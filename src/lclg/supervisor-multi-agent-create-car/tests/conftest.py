"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock modules that may not be available or have import issues in test environment
mock_ollama_client = Mock()
mock_llm_error = Exception

sys.modules['prompt_xml_strategies'] = Mock()
sys.modules['prompt_xml_strategies.llm_clients'] = Mock()
sys.modules['prompt_xml_strategies.llm_clients.ollama_client'] = Mock(
    OllamaClient=mock_ollama_client,
    LLMError=mock_llm_error
)

# Mock LangGraph components that might have import issues
mock_langgraph_prebuilt = Mock()
mock_langgraph_prebuilt.create_agent_executor = Mock()
sys.modules['langgraph.prebuilt'] = mock_langgraph_prebuilt

from llm.ollama_llm import OllamaLLM
from agents.base_agent import BaseAgent, HandoffPayload
from agents.multi_agent_system import MultiAgentSystem


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ollama_llm():
    """Create a mock OllamaLLM for testing."""
    mock_llm = Mock(spec=OllamaLLM)
    mock_llm._call.return_value = "Mock LLM response"
    mock_llm.validate_connection.return_value = True
    mock_llm.get_available_models.return_value = ["llama3.2", "codellama", "mistral"]
    return mock_llm


@pytest.fixture
def sample_car_requirements():
    """Sample car requirements for testing."""
    return {
        "vin": "TEST123456789ABCD",
        "year": "2024",
        "make": "TestMake",
        "model": "TestModel"
    }


@pytest.fixture
def sample_engine_data():
    """Sample engine data for testing."""
    return {
        "displacement": "3.5L",
        "cylinders": "6",
        "fuelType": "gasoline",
        "horsepower": "280",
        "@engineCode": "V6_350_GAS"
    }


@pytest.fixture
def sample_body_data():
    """Sample body data for testing."""
    return {
        "style": "sedan",
        "doors": "4",
        "material": "steel",
        "color": "blue",
        "@paintCode": "BLUE_METALLIC_001"
    }


@pytest.fixture
def sample_tire_data():
    """Sample tire data for testing."""
    return {
        "brand": "Michelin",
        "size": "225/60R17",
        "pressure": "32",
        "treadDepth": "10",
        "@season": "all-season"
    }


@pytest.fixture
def sample_electrical_data():
    """Sample electrical data for testing."""
    return {
        "batteryVoltage": "12",
        "alternatorOutput": "120",
        "wiringHarness": "standard",
        "ecuVersion": "v2.1",
        "@systemType": "standard"
    }


@pytest.fixture
def sample_handoff_payload():
    """Sample handoff payload for testing."""
    return HandoffPayload(
        from_agent="EngineAgent",
        to_agent="BodyAgent",
        data={"engine_compartment_size": "large"},
        constraints={"material_requirements": "steel"},
        context="Test handoff context"
    )


@pytest.fixture
def mock_multi_agent_system(mock_ollama_llm):
    """Create a mock multi-agent system for testing."""
    with pytest.MonkeyPatch.context() as m:
        # Mock the MultiAgentSystem initialization to avoid LLM dependencies
        mock_system = Mock(spec=MultiAgentSystem)
        mock_system.model = "llama3.2"
        mock_system.execution_mode = "hybrid"
        mock_system.system_status = {
            "initialized": True,
            "agents_ready": True,
            "ollama_connection": True,
            "last_check": "2024-01-01T00:00:00"
        }
        mock_system.agents = {
            "supervisor": Mock(),
            "engine": Mock(),
            "body": Mock(),
            "tire": Mock(),
            "electrical": Mock()
        }
        mock_system.get_available_models.return_value = ["llama3.2", "codellama"]
        mock_system.get_system_status.return_value = {
            "system_status": mock_system.system_status,
            "configuration": {"model": "llama3.2", "execution_mode": "hybrid"},
            "agents": {},
            "execution_history_count": 0,
            "timestamp": "2024-01-01T00:00:00"
        }
        return mock_system


@pytest.fixture
def json_schema_path():
    """Path to the car.json schema file."""
    return Path(__file__).parent.parent / "schema" / "single" / "car.json"


@pytest.fixture
def sample_car_json():
    """Sample complete car JSON for testing."""
    return {
        "@vin": "TEST123456789ABCD",
        "@year": "2024",
        "@make": "TestMake",
        "@model": "TestModel",
        "Engine": {
            "displacement": "3.5L",
            "cylinders": "6",
            "fuelType": "gasoline",
            "horsepower": "280",
            "@engineCode": "V6_350_GAS"
        },
        "Body": {
            "style": "sedan",
            "doors": "4",
            "material": "steel",
            "color": "blue",
            "@paintCode": "BLUE_METALLIC_001"
        },
        "Tire": {
            "brand": "Michelin",
            "size": "225/60R17",
            "pressure": "32",
            "treadDepth": "10",
            "@season": "all-season"
        },
        "Electrical": {
            "batteryVoltage": "12",
            "alternatorOutput": "120",
            "wiringHarness": "standard",
            "ecuVersion": "v2.1",
            "@systemType": "standard"
        }
    }


class MockAgent(BaseAgent):
    """Mock agent implementation for testing."""

    def __init__(self, name: str = "MockAgent", **kwargs):
        # Skip BaseAgent initialization for testing
        self.name = name
        self.tools = []
        self.agent_executor = Mock()
        self.handoff_payloads = []
        self.use_json_subtypes_in_prompts_creation = kwargs.get(
            'use_json_subtypes_in_prompts_creation', False
        )

    def _setup_tools(self):
        """Mock tool setup."""
        pass

    def _get_system_prompt(self) -> str:
        """Mock system prompt."""
        return "Mock system prompt"

    def _get_agent_type(self) -> str:
        """Mock agent type."""
        return "mock"


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    return MockAgent()


# Test markers for different types of tests
pytestmark = [
    pytest.mark.unit,  # Default marker for unit tests
]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM API access"
    )
    config.addinivalue_line(
        "markers", "ollama: marks tests that require Ollama server"
    )