"""Unit tests for the multi-agent system."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agents.multi_agent_system import MultiAgentSystem


class TestMultiAgentSystem:
    """Test the MultiAgentSystem class."""

    @pytest.fixture
    def mock_ollama_llm(self):
        """Create a mock OllamaLLM."""
        mock_llm = Mock()
        mock_llm.validate_connection.return_value = True
        mock_llm.get_available_models.return_value = ["llama3.2", "codellama"]
        return mock_llm

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_initialization_default_params(self, mock_supervisor, mock_ollama_llm, mock_ollama_llm_instance=None):
        """Test initialization with default parameters."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        mock_supervisor_instance.engine_agent = Mock()
        mock_supervisor_instance.body_agent = Mock()
        mock_supervisor_instance.tire_agent = Mock()
        mock_supervisor_instance.electrical_agent = Mock()

        system = MultiAgentSystem()

        assert system.model == "llama3.2"
        assert system.base_url == "http://localhost:11434"
        assert system.temperature == 0.1
        assert system.execution_mode == "hybrid"
        assert system.enable_logging is True
        assert system.use_json_subtypes_in_prompts_creation is False

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_initialization_custom_params(self, mock_supervisor, mock_ollama_llm):
        """Test initialization with custom parameters."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        mock_supervisor_instance.engine_agent = Mock()
        mock_supervisor_instance.body_agent = Mock()
        mock_supervisor_instance.tire_agent = Mock()
        mock_supervisor_instance.electrical_agent = Mock()

        system = MultiAgentSystem(
            model="custom_model",
            base_url="http://custom:11434",
            temperature=0.5,
            execution_mode="sequential",
            enable_logging=False,
            use_json_subtypes_in_prompts_creation=True
        )

        assert system.model == "custom_model"
        assert system.base_url == "http://custom:11434"
        assert system.temperature == 0.5
        assert system.execution_mode == "sequential"
        assert system.enable_logging is False
        assert system.use_json_subtypes_in_prompts_creation is True

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_agent_initialization(self, mock_supervisor, mock_ollama_llm):
        """Test that agents are properly initialized."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        engine_agent = Mock()
        body_agent = Mock()
        tire_agent = Mock()
        electrical_agent = Mock()

        mock_supervisor_instance.engine_agent = engine_agent
        mock_supervisor_instance.body_agent = body_agent
        mock_supervisor_instance.tire_agent = tire_agent
        mock_supervisor_instance.electrical_agent = electrical_agent

        system = MultiAgentSystem()

        # Check supervisor initialization
        mock_supervisor.assert_called_once_with(
            name="CarCreationSupervisor",
            llm=mock_llm_instance,
            execution_mode="hybrid",
            use_json_subtypes_in_prompts_creation=False
        )

        # Check agent registry
        assert system.supervisor == mock_supervisor_instance
        assert system.engine_agent == engine_agent
        assert system.body_agent == body_agent
        assert system.tire_agent == tire_agent
        assert system.electrical_agent == electrical_agent

        expected_agents = ["supervisor", "engine", "body", "tire", "electrical"]
        assert all(agent in system.agents for agent in expected_agents)

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_system_status_ready(self, mock_supervisor, mock_ollama_llm):
        """Test system status when everything is ready."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        mock_supervisor_instance.engine_agent = Mock()
        mock_supervisor_instance.body_agent = Mock()
        mock_supervisor_instance.tire_agent = Mock()
        mock_supervisor_instance.electrical_agent = Mock()

        system = MultiAgentSystem()

        assert system.system_status["initialized"] is True
        assert system.system_status["agents_ready"] is True

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_validate_system_success(self, mock_supervisor, mock_ollama_llm):
        """Test successful system validation."""
        mock_llm_instance = Mock()
        mock_llm_instance.validate_connection.return_value = True
        mock_llm_instance.get_available_models.return_value = ["llama3.2", "codellama"]
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock agents with get_agent_info method
        engine_agent = Mock()
        engine_agent.get_agent_info.return_value = {"name": "EngineAgent", "type": "engine"}
        body_agent = Mock()
        body_agent.get_agent_info.return_value = {"name": "BodyAgent", "type": "body"}
        tire_agent = Mock()
        tire_agent.get_agent_info.return_value = {"name": "TireAgent", "type": "tire"}
        electrical_agent = Mock()
        electrical_agent.get_agent_info.return_value = {"name": "ElectricalAgent", "type": "electrical"}

        mock_supervisor_instance.engine_agent = engine_agent
        mock_supervisor_instance.body_agent = body_agent
        mock_supervisor_instance.tire_agent = tire_agent
        mock_supervisor_instance.electrical_agent = electrical_agent
        mock_supervisor_instance.get_agent_info.return_value = {"name": "SupervisorAgent", "type": "supervisor"}

        system = MultiAgentSystem(model="llama3.2")

        validation_results = await system.validate_system()

        assert validation_results["overall_status"] == "ready"
        assert validation_results["components"]["ollama"]["status"] == "connected"
        assert validation_results["components"]["ollama"]["model"] == "llama3.2"
        assert validation_results["components"]["ollama"]["model_available"] is True

        # Check all agents are ready
        agents_info = validation_results["components"]["agents"]
        for agent_name in ["supervisor", "engine", "body", "tire", "electrical"]:
            assert agents_info[agent_name]["status"] == "ready"

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_validate_system_ollama_issue(self, mock_supervisor, mock_ollama_llm):
        """Test system validation with Ollama connectivity issues."""
        mock_llm_instance = Mock()
        mock_llm_instance.validate_connection.return_value = False
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agent.get_agent_info.return_value = {"name": agent_name, "type": agent_name.replace("_agent", "")}
            setattr(mock_supervisor_instance, agent_name, agent)

        mock_supervisor_instance.get_agent_info.return_value = {"name": "SupervisorAgent", "type": "supervisor"}

        system = MultiAgentSystem()

        validation_results = await system.validate_system()

        assert validation_results["overall_status"] == "agents_ready_ollama_issue"
        assert validation_results["components"]["ollama"]["status"] == "disconnected"

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_create_car_success(self, mock_supervisor, mock_ollama_llm):
        """Test successful car creation."""
        mock_llm_instance = Mock()
        mock_llm_instance.validate_connection.return_value = True
        mock_llm_instance.get_available_models.return_value = ["llama3.2"]
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = AsyncMock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agent.get_agent_info.return_value = {"name": agent_name, "type": agent_name.replace("_agent", "")}
            setattr(mock_supervisor_instance, agent_name, agent)

        mock_supervisor_instance.get_agent_info.return_value = {"name": "SupervisorAgent", "type": "supervisor"}

        # Mock car creation result
        mock_car_result = {
            "car_json": {
                "@vin": "TEST123",
                "@year": "2024",
                "@make": "Test",
                "@model": "Car"
            },
            "workflow_status": "completed",
            "completed_agents": ["engine", "body", "tire", "electrical"],
            "validation_results": {"schema_compliance": True}
        }
        mock_supervisor_instance.create_car_json.return_value = mock_car_result

        system = MultiAgentSystem()

        result = await system.create_car(
            vin="TEST123",
            year="2024",
            make="Test",
            model="Car"
        )

        assert "car_json" in result
        assert "system_info" in result
        assert result["workflow_status"] == "completed"
        assert result["system_info"]["model_used"] == "llama3.2"
        assert "execution_time_seconds" in result["system_info"]

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_create_car_system_not_ready(self, mock_supervisor, mock_ollama_llm):
        """Test car creation when system is not ready."""
        mock_llm_instance = Mock()
        mock_llm_instance.validate_connection.return_value = False
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock agents that fail
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agent.get_agent_info.side_effect = Exception("Agent not ready")
            setattr(mock_supervisor_instance, agent_name, agent)

        mock_supervisor_instance.get_agent_info.side_effect = Exception("Supervisor not ready")

        system = MultiAgentSystem()

        result = await system.create_car(
            vin="TEST123",
            year="2024",
            make="Test",
            model="Car"
        )

        assert "error" in result
        assert "System not ready" in result["error"]

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_test_individual_agent(self, mock_supervisor, mock_ollama_llm):
        """Test individual agent testing functionality."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock engine agent
        engine_agent = Mock()
        engine_agent.create_component_json.return_value = {
            "engineType": {
                "displacement": "3.5L",
                "cylinders": "6",
                "fuelType": "gasoline"
            }
        }
        mock_supervisor_instance.engine_agent = engine_agent

        # Mock other agents
        for agent_name in ["body_agent", "tire_agent", "electrical_agent"]:
            setattr(mock_supervisor_instance, agent_name, Mock())

        system = MultiAgentSystem()

        result = await system.test_individual_agent("engine")

        assert result["agent"] == "engine"
        assert result["test_status"] == "success"
        assert "engineType" in result["result"]

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_test_individual_agent_unknown(self, mock_supervisor, mock_ollama_llm):
        """Test individual agent testing with unknown agent."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            setattr(mock_supervisor_instance, agent_name, Mock())

        system = MultiAgentSystem()

        result = await system.test_individual_agent("unknown")

        assert "error" in result
        assert "Unknown agent" in result["error"]
        assert "available_agents" in result

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_get_system_status(self, mock_supervisor, mock_ollama_llm):
        """Test getting system status."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agent.get_agent_info.return_value = {"name": agent_name, "type": agent_name.replace("_agent", "")}
            setattr(mock_supervisor_instance, agent_name, agent)

        mock_supervisor_instance.get_agent_info.return_value = {"name": "SupervisorAgent", "type": "supervisor"}

        system = MultiAgentSystem(
            model="test_model",
            execution_mode="test_mode",
            enable_logging=False
        )

        status = system.get_system_status()

        assert "system_status" in status
        assert "configuration" in status
        assert "agents" in status
        assert "timestamp" in status

        config = status["configuration"]
        assert config["model"] == "test_model"
        assert config["execution_mode"] == "test_mode"
        assert config["logging_enabled"] is False

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_execution_history(self, mock_supervisor, mock_ollama_llm):
        """Test execution history functionality."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            setattr(mock_supervisor_instance, agent_name, Mock())

        system = MultiAgentSystem()

        # Initially empty
        assert len(system.get_execution_history()) == 0

        # Add test execution
        test_execution = {"test": "data", "timestamp": "2024-01-01"}
        system._save_to_history(test_execution)

        # Should have one entry
        history = system.get_execution_history()
        assert len(history) == 1
        assert history[0]["test"] == "data"

        # Clear history
        assert system.clear_execution_history() is True
        assert len(system.get_execution_history()) == 0

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_get_available_models(self, mock_supervisor, mock_ollama_llm):
        """Test getting available models."""
        mock_llm_instance = Mock()
        mock_llm_instance.get_available_models.return_value = ["llama3.2", "codellama", "mistral"]
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            setattr(mock_supervisor_instance, agent_name, Mock())

        system = MultiAgentSystem()

        models = system.get_available_models()

        assert "llama3.2" in models
        assert "codellama" in models
        assert "mistral" in models

    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    def test_switch_model(self, mock_supervisor, mock_ollama_llm):
        """Test switching models."""
        # Mock original LLM
        mock_original_llm = Mock()
        mock_original_llm.validate_connection.return_value = True

        # Mock new LLM
        mock_new_llm = Mock()
        mock_new_llm.validate_connection.return_value = True

        mock_ollama_llm.side_effect = [mock_original_llm, mock_new_llm]

        mock_supervisor_instance = Mock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock agents
        agents = {}
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agents[agent_name] = agent
            setattr(mock_supervisor_instance, agent_name, agent)

        system = MultiAgentSystem(model="original_model")

        # Switch model
        result = system.switch_model("new_model")

        assert result is True
        assert system.model == "new_model"
        assert system.llm == mock_new_llm

        # Check that all agents got the new LLM
        for agent in system.agents.values():
            assert agent.llm == mock_new_llm

    @pytest.mark.asyncio
    @patch('agents.multi_agent_system.OllamaLLM')
    @patch('agents.multi_agent_system.CarCreationSupervisorAgent')
    async def test_batch_create_cars(self, mock_supervisor, mock_ollama_llm):
        """Test batch car creation."""
        mock_llm_instance = Mock()
        mock_llm_instance.validate_connection.return_value = True
        mock_llm_instance.get_available_models.return_value = ["llama3.2"]
        mock_ollama_llm.return_value = mock_llm_instance

        mock_supervisor_instance = AsyncMock()
        mock_supervisor.return_value = mock_supervisor_instance

        # Mock the supervisor's agents
        for agent_name in ["engine_agent", "body_agent", "tire_agent", "electrical_agent"]:
            agent = Mock()
            agent.get_agent_info.return_value = {"name": agent_name, "type": agent_name.replace("_agent", "")}
            setattr(mock_supervisor_instance, agent_name, agent)

        mock_supervisor_instance.get_agent_info.return_value = {"name": "SupervisorAgent", "type": "supervisor"}

        # Mock car creation to return different results for each car
        def mock_create_car_json(**kwargs):
            return {
                "car_json": {
                    "@vin": kwargs["vin"],
                    "@year": kwargs["year"],
                    "@make": kwargs["make"],
                    "@model": kwargs["model"]
                },
                "workflow_status": "completed"
            }

        mock_supervisor_instance.create_car_json.side_effect = mock_create_car_json

        system = MultiAgentSystem()

        car_specs = [
            {"vin": "VIN1", "year": "2024", "make": "Make1", "model": "Model1"},
            {"vin": "VIN2", "year": "2024", "make": "Make2", "model": "Model2"}
        ]

        results = await system.batch_create_cars(car_specs, max_concurrent=2)

        assert len(results) == 2
        assert results[0]["car_json"]["@vin"] == "VIN1"
        assert results[1]["car_json"]["@vin"] == "VIN2"