"""Unit tests for base_agent module."""

import pytest
import sys
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from agents.base_agent import BaseAgent, AgentMessage
from langchain.tools import BaseTool


class TestAgentMessage:
    """Test cases for AgentMessage class."""

    def test_agent_message_creation(self):
        """Test creating an AgentMessage."""
        message = AgentMessage(
            content="Test content",
            sender="test_sender",
            recipient="test_recipient",
            metadata={"key": "value"}
        )

        assert message.content == "Test content"
        assert message.sender == "test_sender"
        assert message.recipient == "test_recipient"
        assert message.metadata == {"key": "value"}

    def test_agent_message_optional_fields(self):
        """Test AgentMessage with optional fields."""
        message = AgentMessage(
            content="Test content",
            sender="test_sender"
        )

        assert message.content == "Test content"
        assert message.sender == "test_sender"
        assert message.recipient is None
        assert message.metadata == {}

    def test_agent_message_validation(self):
        """Test AgentMessage field validation."""
        # Test required fields
        with pytest.raises(ValueError):
            AgentMessage()

        with pytest.raises(ValueError):
            AgentMessage(content="test")

        # Valid message
        message = AgentMessage(content="test", sender="sender")
        assert message.content == "test"


class MockBaseAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def __init__(self, **kwargs):
        self.setup_tools_called = False
        self.tools_to_setup = kwargs.pop('mock_tools', [])
        super().__init__(**kwargs)

    def _setup_tools(self) -> None:
        """Mock implementation of _setup_tools."""
        self.setup_tools_called = True
        self.tools = self.tools_to_setup

    def _get_system_prompt(self) -> str:
        """Mock implementation of _get_system_prompt."""
        return "Test system prompt for mock agent"

    def _get_agent_type(self) -> str:
        """Mock implementation of _get_agent_type."""
        return "mock"

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Mock implementation of _build_component_request."""
        return f"Mock component request for {requirements}"

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of _validate_component_data."""
        if "error" in component_data:
            return component_data
        return {"validated": True, **component_data}


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_base_agent_initialization(self, mock_get_prompt, mock_create_agent, mock_ollama_llm, disable_logging):
        """Test BaseAgent initialization."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tools = [mock_tool]
        agent = MockBaseAgent(
            name="test_agent",
            llm=mock_ollama_llm,
            mock_tools=mock_tools,
            enable_logging=False
        )

        assert agent.name == "test_agent"
        assert agent.llm == mock_ollama_llm
        assert agent.setup_tools_called is True
        assert agent.tools == mock_tools
        assert agent.agent_executor is not None
        mock_create_agent.assert_called_once()

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_schema_agent_prompt')
    def test_base_agent_with_json_prompts(self, mock_get_schema_prompt, mock_create_agent, mock_ollama_llm, disable_logging):
        """Test BaseAgent initialization with JSON schema prompts."""
        mock_get_schema_prompt.return_value = "Mock schema prompt"
        mock_create_agent.return_value = Mock()

        agent = MockBaseAgent(
            name="test_agent",
            llm=mock_ollama_llm,
            use_json_subtypes_in_prompts_creation=True,
            enable_logging=False
        )

        mock_get_schema_prompt.assert_called_once()
        assert agent.use_json_subtypes_in_prompts_creation is True

    def test_base_agent_with_logging_disabled(self, mock_ollama_llm):
        """Test BaseAgent with logging disabled."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            assert not hasattr(agent, 'logger')

    def test_base_agent_with_logging_enabled(self, mock_ollama_llm):
        """Test BaseAgent with logging enabled."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.AgentLogger') as mock_logger_class:

            mock_logger = Mock()
            mock_logger_class.return_value = mock_logger

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=True
            )

            assert agent.enable_logging is True
            mock_logger_class.assert_called_once_with("test_agent")

    def test_base_agent_setup_failure(self, mock_ollama_llm):
        """Test BaseAgent setup failure handling."""
        with patch('agents.base_agent.create_agent', side_effect=Exception("Setup failed")), \
             patch('agents.base_agent.get_agent_prompt'):

            with pytest.raises(Exception, match="Setup failed"):
                MockBaseAgent(
                    name="test_agent",
                    llm=mock_ollama_llm,
                    enable_logging=False
                )

    @pytest.mark.asyncio
    async def test_process_message_success(self, mock_ollama_llm, mock_agent_message, disable_logging):
        """Test successful message processing."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Mock the agent executor
            mock_final_state = {
                "messages": [Mock(content="Response content")]
            }

            async def mock_astream(inputs):
                yield mock_final_state

            agent.agent_executor.astream = mock_astream

            response = await agent.process_message(mock_agent_message)

            assert isinstance(response, AgentMessage)
            assert response.content == "Response content"
            assert response.sender == "test_agent"
            assert response.recipient == "test_sender"

    @pytest.mark.asyncio
    async def test_process_message_failure(self, mock_ollama_llm, mock_agent_message, disable_logging):
        """Test message processing with failure."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Mock the agent executor to raise an exception
            async def mock_astream_error(inputs):
                raise Exception("Processing failed")

            agent.agent_executor.astream = mock_astream_error

            response = await agent.process_message(mock_agent_message)

            assert isinstance(response, AgentMessage)
            assert "Error processing message" in response.content
            assert response.metadata["error"] is True

    def test_extract_response_content_with_messages(self, mock_ollama_llm, disable_logging):
        """Test extracting response content from final state."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            final_state = {
                "messages": [
                    Mock(content="First message"),
                    Mock(content="Last message")
                ]
            }

            content = agent._extract_response_content(final_state)
            assert content == "Last message"

    def test_extract_response_content_no_messages(self, mock_ollama_llm, disable_logging):
        """Test extracting response content with no messages."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Test with empty state
            content = agent._extract_response_content({})
            assert content == "No response generated"

            # Test with empty messages
            final_state = {"messages": []}
            content = agent._extract_response_content(final_state)
            assert content == "No response generated"

    def test_create_component_json_success(self, mock_ollama_llm, disable_logging):
        """Test successful component JSON creation."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            requirements = {"vehicle_type": "sedan"}
            result = agent.create_component_json(requirements)

            assert result["validated"] is True
            mock_ollama_llm.invoke.assert_called_once()

    def test_create_component_json_failure(self, mock_ollama_llm_with_error, disable_logging):
        """Test component JSON creation failure."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm_with_error,
                enable_logging=False
            )

            requirements = {"vehicle_type": "sedan"}
            result = agent.create_component_json(requirements)

            assert "error" in result
            assert "Failed to create component" in result["error"]

    def test_extract_json_from_response_valid_json(self, mock_ollama_llm, disable_logging):
        """Test extracting JSON from valid JSON response."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            json_response = '{"key": "value", "number": 42}'
            result = agent._extract_json_from_response(json_response)

            assert result == {"key": "value", "number": 42}

    def test_extract_json_from_response_json_block(self, mock_ollama_llm, disable_logging):
        """Test extracting JSON from markdown code block."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            response = '''Here is the JSON:
            ```json
            {"key": "value", "test": true}
            ```
            End of response.'''

            result = agent._extract_json_from_response(response)
            assert result == {"key": "value", "test": True}

    def test_extract_json_from_response_invalid_json(self, mock_ollama_llm, disable_logging):
        """Test extracting JSON from invalid JSON response."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            invalid_response = "This is not JSON at all"
            result = agent._extract_json_from_response(invalid_response)

            assert "error" in result
            assert "Could not extract valid JSON" in result["error"]

    def test_balance_json_braces(self, mock_ollama_llm, disable_logging):
        """Test balancing JSON braces."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Test adding missing closing braces
            unbalanced = '{"key": "value", "nested": {"inner": "value"'
            balanced = agent._balance_json_braces(unbalanced)
            assert balanced.count('{') == balanced.count('}')

            # Test removing extra closing braces
            extra_braces = '{"key": "value"}}}'
            balanced = agent._balance_json_braces(extra_braces)
            # Should at least reduce the extra braces
            assert balanced.count('}') <= extra_braces.count('}')
            # Should try to parse as valid JSON after balancing
            try:
                import json
                json.loads(balanced)
                assert True  # Successfully parsed
            except json.JSONDecodeError:
                # Even if not perfectly balanced, should have fewer extra braces
                assert balanced.count('}') < extra_braces.count('}')

    def test_get_available_tools(self, mock_ollama_llm, disable_logging):
        """Test getting available tools."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            tool1 = Mock()
            tool1.name = "tool1"
            tool2 = Mock()
            tool2.name = "tool2"
            tool3 = Mock()
            tool3.name = "tool3"
            mock_tools = [tool1, tool2, tool3]

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                mock_tools=mock_tools,
                enable_logging=False
            )

            tool_names = agent.get_available_tools()
            assert tool_names == ["tool1", "tool2", "tool3"]

    def test_add_tool(self, mock_ollama_llm, disable_logging):
        """Test adding a new tool."""
        with patch('agents.base_agent.create_agent') as mock_create_agent, \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Reset the mock to count calls after initialization
            mock_create_agent.reset_mock()

            new_tool = Mock()
            new_tool.name = "new_tool"
            initial_tool_count = len(agent.tools)

            agent.add_tool(new_tool)

            assert len(agent.tools) == initial_tool_count + 1
            assert new_tool in agent.tools
            # Should recreate agent with new tool
            mock_create_agent.assert_called_once()

    def test_get_agent_info(self, mock_ollama_llm, disable_logging):
        """Test getting agent information."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            tool1 = Mock()
            tool1.name = "tool1"
            tool2 = Mock()
            tool2.name = "tool2"
            mock_tools = [tool1, tool2]
            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                mock_tools=mock_tools,
                enable_logging=False
            )

            info = agent.get_agent_info()

            assert info["name"] == "test_agent"
            assert info["type"] == "mock"
            assert info["tools"] == ["tool1", "tool2"]
            assert "llm_type" in info
            assert "model" in info

    def test_agent_setup_with_custom_parameters(self, disable_logging):
        """Test agent setup with custom parameters."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.OllamaLLM') as mock_ollama_class:

            mock_llm = Mock()
            mock_ollama_class.return_value = mock_llm

            agent = MockBaseAgent(
                name="test_agent",
                temperature=0.5,
                model_name="custom_model",
                base_url="http://custom:11434",
                enable_logging=False
            )

            mock_ollama_class.assert_called_once_with(
                model="custom_model",
                temperature=0.5,
                base_url="http://custom:11434"
            )
            assert agent.llm == mock_llm


class TestBaseAgentAbstractMethods:
    """Test cases for abstract method requirements."""

    def test_cannot_instantiate_base_agent_directly(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent(name="test")

    def test_mock_agent_implements_required_methods(self, mock_ollama_llm, disable_logging):
        """Test that MockBaseAgent implements all required abstract methods."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = MockBaseAgent(
                name="test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Test all abstract methods are implemented
            assert agent._get_agent_type() == "mock"
            assert agent._get_system_prompt() == "Test system prompt for mock agent"
            assert "Mock component request" in agent._build_component_request({"test": "data"})

            validated = agent._validate_component_data({"test": "data"})
            assert validated["validated"] is True


@pytest.mark.integration
class TestBaseAgentIntegration:
    """Integration tests for BaseAgent."""

    def test_full_agent_workflow(self, mock_ollama_llm, disable_logging):
        """Test complete agent workflow from initialization to response."""
        with patch('agents.base_agent.create_agent') as mock_create_agent, \
             patch('agents.base_agent.get_agent_prompt'):

            # Setup mock agent executor
            mock_executor = Mock()
            mock_create_agent.return_value = mock_executor

            # Create agent
            agent = MockBaseAgent(
                name="integration_test_agent",
                llm=mock_ollama_llm,
                enable_logging=False
            )

            # Test component creation
            requirements = {
                "vehicle_type": "sedan",
                "performance_level": "standard"
            }

            result = agent.create_component_json(requirements)

            # Verify the workflow
            assert agent.setup_tools_called is True
            assert agent.agent_executor is not None
            assert result["validated"] is True
            mock_ollama_llm.invoke.assert_called_once()