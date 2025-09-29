"""Basic functionality tests for the car creation multi-agent system."""

import pytest
import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.multi_agent_system import MultiAgentSystem
from agents.engine_agent import EngineAgent
from agents.body_agent import BodyAgent
from agents.tire_agent import TireAgent
from agents.electrical_agent import ElectricalAgent
from llm.ollama_llm import OllamaLLM


class TestBasicFunctionality:
    """Test basic functionality of the car creation system."""

    @pytest.fixture
    def mock_system(self):
        """Create a multi-agent system for testing (may not connect to actual Ollama)."""
        try:
            system = MultiAgentSystem(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.1,
                execution_mode="hybrid",
                enable_logging=False
            )
            return system
        except Exception:
            # Return None if Ollama is not available
            return None

    def test_system_initialization(self, mock_system):
        """Test that the system initializes correctly."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        assert mock_system is not None
        assert mock_system.model == "llama3.2"
        assert mock_system.execution_mode == "hybrid"
        assert mock_system.system_status["agents_ready"] is True

    def test_agent_registry(self, mock_system):
        """Test that all agents are properly registered."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        expected_agents = ["supervisor", "engine", "body", "tire", "electrical"]
        assert all(agent in mock_system.agents for agent in expected_agents)

        # Test agent types
        assert isinstance(mock_system.engine_agent, EngineAgent)
        assert isinstance(mock_system.body_agent, BodyAgent)
        assert isinstance(mock_system.tire_agent, TireAgent)
        assert isinstance(mock_system.electrical_agent, ElectricalAgent)

    def test_agent_info_methods(self, mock_system):
        """Test that agents provide correct information."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        for agent_name, agent in mock_system.agents.items():
            info = agent.get_agent_info()

            assert "name" in info
            assert "type" in info
            assert "tools" in info
            assert info["name"] == agent.name

    def test_engine_configurations(self):
        """Test that engine configurations are available."""
        from tools.engine_tools import ENGINE_CONFIGURATIONS

        assert len(ENGINE_CONFIGURATIONS) > 0

        # Test specific configurations
        assert "v6_gasoline" in ENGINE_CONFIGURATIONS
        assert "electric" in ENGINE_CONFIGURATIONS

        # Test required fields in configurations
        for config_name, config in ENGINE_CONFIGURATIONS.items():
            required_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode"]
            for field in required_fields:
                assert field in config, f"Missing {field} in {config_name}"

    def test_body_configurations(self):
        """Test that body configurations are available."""
        from tools.body_tools import BODY_STYLE_CONFIGURATIONS

        assert len(BODY_STYLE_CONFIGURATIONS) > 0

        # Test specific styles
        assert "sedan" in BODY_STYLE_CONFIGURATIONS
        assert "suv" in BODY_STYLE_CONFIGURATIONS

        # Test required fields
        for style_name, style in BODY_STYLE_CONFIGURATIONS.items():
            required_fields = ["style", "doors", "material", "color"]
            for field in required_fields:
                assert field in style, f"Missing {field} in {style_name}"

    def test_tire_configurations(self):
        """Test that tire configurations are available."""
        from tools.tire_tools import TIRE_CONFIGURATIONS

        assert len(TIRE_CONFIGURATIONS) > 0

        # Test required fields
        for config_name, config in TIRE_CONFIGURATIONS.items():
            required_fields = ["brand", "size", "pressure", "treadDepth", "@season"]
            for field in required_fields:
                assert field in config, f"Missing {field} in {config_name}"

    def test_electrical_configurations(self):
        """Test that electrical configurations are available."""
        from tools.electrical_tools import ELECTRICAL_CONFIGURATIONS

        assert len(ELECTRICAL_CONFIGURATIONS) > 0

        # Test specific systems
        assert "standard_12v" in ELECTRICAL_CONFIGURATIONS
        assert "electric_system" in ELECTRICAL_CONFIGURATIONS

        # Test required fields
        for config_name, config in ELECTRICAL_CONFIGURATIONS.items():
            required_fields = ["batteryVoltage", "alternatorOutput", "wiringHarness", "ecuVersion", "@systemType"]
            for field in required_fields:
                assert field in config, f"Missing {field} in {config_name}"

    def test_handoff_payload_creation(self, mock_system):
        """Test handoff payload creation."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        engine_agent = mock_system.engine_agent

        payload = engine_agent.create_handoff_payload(
            to_agent="body",
            data={"engine_compartment_size": "large"},
            constraints={"material_requirements": "steel"},
            context="Test handoff"
        )

        assert payload.from_agent == "EngineAgent"
        assert payload.to_agent == "body"
        assert payload.data["engine_compartment_size"] == "large"
        assert payload.constraints["material_requirements"] == "steel"

    def test_json_schema_compliance(self):
        """Test that generated components comply with expected JSON structure."""
        # Test engine component structure
        from tools.engine_tools import ENGINE_CONFIGURATIONS

        config = ENGINE_CONFIGURATIONS["v6_gasoline"]

        # Should have all required fields for engineType
        required_engine_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode"]
        for field in required_engine_fields:
            assert field in config

        # Should have valid fuel type
        valid_fuel_types = ["gasoline", "diesel", "electric", "hybrid", "hydrogen"]
        assert config["fuelType"] in valid_fuel_types

    def test_system_status_method(self, mock_system):
        """Test system status retrieval."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        status = mock_system.get_system_status()

        assert "system_status" in status
        assert "configuration" in status
        assert "agents" in status
        assert "timestamp" in status

        # Check configuration
        config = status["configuration"]
        assert config["model"] == "llama3.2"
        assert config["execution_mode"] == "hybrid"

    @pytest.mark.asyncio
    async def test_system_validation(self, mock_system):
        """Test system validation functionality."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        try:
            validation_results = await mock_system.validate_system()

            assert "overall_status" in validation_results
            assert "components" in validation_results
            assert "timestamp" in validation_results

            # Should have ollama and agents components
            assert "ollama" in validation_results["components"]
            assert "agents" in validation_results["components"]

        except Exception as e:
            # Validation may fail if Ollama is not running, which is OK for testing
            assert "connect" in str(e).lower() or "timeout" in str(e).lower()

    def test_execution_history_management(self, mock_system):
        """Test execution history functionality."""
        if mock_system is None:
            pytest.skip("Ollama not available for testing")

        # Initially empty
        assert len(mock_system.get_execution_history()) == 0

        # Add mock execution
        mock_system._save_to_history({"test": "data", "timestamp": "2024-01-01"})

        # Should have one entry
        history = mock_system.get_execution_history()
        assert len(history) == 1
        assert history[0]["test"] == "data"

        # Clear history
        assert mock_system.clear_execution_history() is True
        assert len(mock_system.get_execution_history()) == 0


class TestToolFunctionality:
    """Test individual tool functionality without requiring Ollama."""

    def test_engine_configuration_tool(self):
        """Test engine configuration tool."""
        from tools.engine_tools import EngineConfigurationTool

        tool = EngineConfigurationTool()

        # Test basic configuration
        result = tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)
        assert "engineType" in result_data
        assert "compartment_info" in result_data

        engine_type = result_data["engineType"]
        assert "displacement" in engine_type
        assert "fuelType" in engine_type
        assert engine_type["fuelType"] == "gasoline"

    def test_body_configuration_tool(self):
        """Test body configuration tool."""
        from tools.body_tools import BodyConfigurationTool

        tool = BodyConfigurationTool()

        result = tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        assert "bodyType" in result_data

        body_type = result_data["bodyType"]
        assert "style" in body_type
        assert "doors" in body_type
        assert body_type["style"] == "sedan"

    def test_tire_configuration_tool(self):
        """Test tire configuration tool."""
        from tools.tire_tools import TireConfigurationTool

        tool = TireConfigurationTool()

        result = tool._run(
            body_style="sedan",
            performance_level="standard",
            climate_preference="all-season"
        )

        result_data = json.loads(result)
        assert "tireType" in result_data

        tire_type = result_data["tireType"]
        assert "brand" in tire_type
        assert "size" in tire_type
        assert "@season" in tire_type
        assert tire_type["@season"] == "all-season"

    def test_electrical_configuration_tool(self):
        """Test electrical configuration tool."""
        from tools.electrical_tools import ElectricalConfigurationTool

        tool = ElectricalConfigurationTool()

        result = tool._run(
            engine_type="v6_gasoline",
            vehicle_class="standard",
            feature_level="basic"
        )

        result_data = json.loads(result)
        assert "electricalType" in result_data

        electrical_type = result_data["electricalType"]
        assert "batteryVoltage" in electrical_type
        assert "@systemType" in electrical_type


if __name__ == "__main__":
    pytest.main([__file__])