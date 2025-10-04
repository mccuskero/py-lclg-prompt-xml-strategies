"""Unit tests for SingleAgentSystem class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from single_agent_system import SingleAgentSystem


class TestSingleAgentSystem:
    """Test the SingleAgentSystem class."""

    def test_initialization(self, mock_llm):
        """Test SingleAgentSystem initialization."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            assert system.llm == mock_llm
            assert system.agent is not None
            assert system.session_active == False
            assert system.iteration_count == 0

    def test_initialization_with_custom_params(self, mock_llm):
        """Test initialization with custom parameters."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(
                model_name="llama3.2",
                base_url="http://test:11434",
                temperature=0.5,
                enable_logging=False
            )

            assert system.llm == mock_llm
            assert system.agent is not None

    def test_run_single_request(self, mock_llm, sample_requirements):
        """Test running a single request."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            # Mock the agent's create_complete_car method
            system.agent.create_complete_car = Mock(return_value={
                "car_configuration": {"vehicle_info": {"type": "sedan"}},
                "metadata": {}
            })

            result = system.run_single_request(sample_requirements)

            assert "car_configuration" in result
            system.agent.create_complete_car.assert_called_once_with(sample_requirements)

    def test_process_iteration(self, mock_llm):
        """Test processing a single iteration."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.iteration_count = 1

            # Mock process_user_request
            system.agent.process_user_request = Mock(return_value={
                "car_configuration": {"vehicle_info": {"type": "sedan"}}
            })

            result = system._process_iteration("I want a sedan")

            assert "car_configuration" in result
            system.agent.process_user_request.assert_called_once_with("I want a sedan")

    def test_process_iteration_error(self, mock_llm):
        """Test iteration processing with error."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            # Mock to raise exception
            system.agent.process_user_request = Mock(side_effect=Exception("Test error"))

            result = system._process_iteration("test")

            assert "error" in result
            assert "Test error" in result["error"]

    def test_handle_quit(self, mock_llm):
        """Test quit command handler."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.session_active = True

            system._handle_quit()

            assert system.session_active == False

    def test_handle_reset(self, mock_llm):
        """Test reset command handler."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.iteration_count = 5

            # Add some memory
            system.agent.memory.add_context("test", "value")
            system.agent.memory.add_message("user", "test message")

            system._handle_reset()

            assert system.iteration_count == 0
            assert len(system.agent.memory.context_data) == 0
            assert len(system.agent.memory.messages) == 0

    def test_handle_status(self, mock_llm, capsys):
        """Test status command handler."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.iteration_count = 3

            # Add some context
            system.agent.memory.add_context("vehicle_type", "sedan")
            system.agent.memory.add_message("user", "test")

            system._handle_status()

            captured = capsys.readouterr()
            assert "Iteration Count: 3" in captured.out
            assert "Context Items: 1" in captured.out
            assert "Message History: 1" in captured.out
            assert "vehicle_type" in captured.out

    def test_handle_save_success(self, mock_llm, tmp_path):
        """Test save command handler success."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.iteration_count = 2

            # Add context
            system.agent.memory.add_context("vehicle_type", "sedan")

            # Save to temp file
            save_file = tmp_path / "test_save.json"
            system._handle_save(str(save_file))

            assert save_file.exists()

            # Verify content
            import json
            with open(save_file, 'r') as f:
                data = json.load(f)

            assert data["iteration_count"] == 2
            assert "vehicle_type" in data["context"]

    def test_handle_save_no_config(self, mock_llm, capsys):
        """Test save with no configuration."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            system._handle_save("test.json")

            captured = capsys.readouterr()
            assert "No configuration to save" in captured.out

    def test_handle_save_error(self, mock_llm, capsys):
        """Test save with error."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)
            system.agent.memory.add_context("test", "value")

            # Try to save to invalid path
            system._handle_save("/invalid/path/test.json")

            captured = capsys.readouterr()
            assert "Failed to save" in captured.out

    def test_display_result_success(self, mock_llm, capsys, sample_car_config):
        """Test displaying a successful result."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            system._display_result(sample_car_config)

            captured = capsys.readouterr()
            assert "Car configuration created successfully" in captured.out
            assert "Vehicle Information" in captured.out
            assert "sedan" in captured.out

    def test_display_result_error(self, mock_llm, capsys):
        """Test displaying an error result."""
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(enable_logging=False)

            error_result = {
                "error": "Test error message",
                "raw_response": "Some raw response data"
            }

            system._display_result(error_result)

            captured = capsys.readouterr()
            assert "Error: Test error message" in captured.out
            assert "Raw response preview" in captured.out
