"""Test configuration and fixtures for the single-agent car creation system."""

import pytest
import sys
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_ollama_llm():
    """Mock OLLAMA LLM for testing without actual LLM calls."""
    mock_llm = Mock()
    mock_llm.model = "test_model"
    mock_llm.temperature = 0.1
    mock_llm.base_url = "http://localhost:11434"

    # Mock successful JSON response
    mock_response = Mock()
    mock_response.content = '{"engineType": {"displacement": "3.5L", "horsepower": "280"}}'
    mock_llm.invoke = Mock(return_value=mock_response)

    return mock_llm


@pytest.fixture
def mock_ollama_llm_with_error():
    """Mock OLLAMA LLM that raises errors for testing error handling."""
    mock_llm = Mock()
    mock_llm.model = "test_model"
    mock_llm.invoke = Mock(side_effect=Exception("LLM connection failed"))
    return mock_llm


@pytest.fixture
def sample_car_requirements():
    """Sample car requirements for testing."""
    return {
        "vehicle_type": "sedan",
        "performance_level": "standard",
        "fuel_preference": "gasoline",
        "budget": "medium",
        "special_features": ["sunroof", "leather_seats"]
    }


@pytest.fixture
def sample_engine_config():
    """Sample engine configuration for testing."""
    return {
        "displacement": "3.5L",
        "cylinders": "6",
        "fuelType": "gasoline",
        "horsepower": "280",
        "@engineCode": "V6-350",
        "@manufacturer": "Generic Motors"
    }


@pytest.fixture
def sample_car_config():
    """Sample complete car configuration for testing."""
    return {
        "car_configuration": {
            "vehicle_info": {
                "type": "sedan",
                "performance_level": "standard",
                "fuel_preference": "gasoline",
                "budget": "medium"
            },
            "engine": {
                "displacement": "3.5L",
                "cylinders": "6",
                "fuelType": "gasoline",
                "horsepower": "280"
            },
            "body": {
                "exterior": {
                    "style": "sedan",
                    "color": "blue",
                    "material": "steel"
                },
                "interior": {
                    "seats": "cloth",
                    "dashboard": "standard"
                }
            },
            "electrical": {
                "main_system": {
                    "voltage_system": "12V"
                },
                "battery": {
                    "capacity": "75Ah"
                }
            },
            "tires_and_wheels": {
                "tires": {
                    "size": "225/60R16",
                    "type": "all_season"
                },
                "wheels": {
                    "material": "alloy",
                    "size": "16"
                }
            }
        }
    }


@pytest.fixture
def mock_tools():
    """Mock tools for testing without actual tool execution."""
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "Test tool for testing"
    return [mock_tool]


@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temporary_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temporary_log_dir(tmp_path):
    """Temporary directory for test logs."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def mock_tools_list():
    """Mock list of tools for agent testing."""
    tools = []
    for tool_name in ["configure_engine", "design_body", "configure_electrical", "configure_tires"]:
        mock_tool = Mock()
        mock_tool.name = tool_name
        mock_tool.description = f"Mock {tool_name} tool"
        tools.append(mock_tool)
    return tools


@pytest.fixture
def disable_logging():
    """Disable logging during tests to reduce noise."""
    # Store original level
    original_level = logging.getLogger().level

    # Disable logging
    logging.getLogger().setLevel(logging.CRITICAL + 1)

    yield

    # Restore original level
    logging.getLogger().setLevel(original_level)


@pytest.fixture
def mock_agent_message():
    """Mock agent message for testing."""
    from agents.base_agent import AgentMessage
    return AgentMessage(
        content="Test message content",
        sender="test_sender",
        recipient="test_recipient",
        metadata={"test": "data"}
    )


@pytest.fixture
def mock_langchain_create_agent():
    """Mock langchain create_agent function."""
    with patch('agents.base_agent.create_agent') as mock_create:
        mock_agent = Mock()
        mock_agent.astream = Mock()
        mock_create.return_value = mock_agent
        yield mock_create


@pytest.fixture
def environment_variables():
    """Mock environment variables for testing."""
    return {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "LLM_TEMPERATURE": "0.1",
        "LOG_LEVEL": "INFO",
        "LOG_TO_FILE": "false"
    }


# Skip integration tests by default unless explicitly requested
def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires OLLAMA server)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--integration"):
        # Don't skip integration tests if explicitly requested
        return

    # Skip integration tests by default
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)