"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from langchain_core.messages import HumanMessage, AIMessage

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory.memory_manager import (
    MemoryBackendConfig,
    InMemoryManager,
    create_memory_manager
)


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = Mock()
    mock.invoke = Mock(return_value=Mock(
        content='{"car_configuration": {"vehicle_info": {"type": "sedan"}}}'
    ))
    return mock


@pytest.fixture
def sample_requirements():
    """Sample car requirements for testing."""
    return {
        "vehicle_type": "sedan",
        "performance_level": "standard",
        "fuel_preference": "gasoline",
        "budget": "medium"
    }


@pytest.fixture
def sample_car_config():
    """Sample car configuration for testing."""
    return {
        "car_configuration": {
            "vehicle_info": {
                "type": "sedan",
                "performance_level": "standard",
                "fuel_preference": "gasoline",
                "budget": "medium"
            },
            "engine": {
                "displacement": "2.5L",
                "cylinders": "4",
                "fuelType": "gasoline",
                "horsepower": "180",
                "@engineCode": "ECO-250",
                "@manufacturer": "Generic Motors"
            },
            "body": {
                "exterior": {
                    "style": "sedan",
                    "color": "silver",
                    "doors": 4,
                    "material": "steel"
                },
                "interior": {
                    "seating": "5-passenger",
                    "upholstery": "cloth",
                    "dashboard": "standard"
                }
            },
            "electrical": {
                "main_system": {
                    "voltage_system": "12V",
                    "battery_capacity": "75Ah"
                },
                "battery": {
                    "voltage": "12V",
                    "capacity": "75Ah"
                },
                "lighting": {
                    "headlights": "LED",
                    "taillights": "LED"
                }
            },
            "tires_and_wheels": {
                "tires": {
                    "brand": "Goodyear",
                    "size": "225/60R16",
                    "pressure": "32 PSI"
                },
                "wheels": {
                    "size": "16 inch",
                    "material": "alloy",
                    "design": "5-spoke"
                }
            }
        }
    }


# Memory-related fixtures

@pytest.fixture
def memory_config_in_memory():
    """Memory configuration for in-memory backend."""
    return MemoryBackendConfig(backend_type="memory")


@pytest.fixture
def memory_config_postgres():
    """Memory configuration for PostgreSQL backend."""
    return MemoryBackendConfig(
        backend_type="postgres",
        connection_string="postgresql://test:test@localhost:5432/test_db",
        session_id="test_session",
        table_name="test_table"
    )


@pytest.fixture
def in_memory_manager():
    """Create an InMemoryManager instance for testing."""
    return InMemoryManager(max_messages=10)


@pytest.fixture
def memory_manager_with_data():
    """Create an InMemoryManager with some test data."""
    manager = InMemoryManager(max_messages=10)

    # Add messages
    manager.add_message(HumanMessage(content="I want a sports car"))
    manager.add_message(AIMessage(content="I can help you with that!"))

    # Add context
    manager.add_context("vehicle_type", "sports")
    manager.add_context("performance_level", "high")
    manager.add_context("fuel_preference", "gasoline")

    return manager


@pytest.fixture
def mock_postgres_history():
    """Mock PostgresChatMessageHistory for testing."""
    with patch('memory.memory_manager.PostgresChatMessageHistory') as mock:
        mock_instance = MagicMock()
        mock_instance.messages = []
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def sample_messages():
    """Sample LangChain messages for testing."""
    return [
        HumanMessage(content="Hello, I need a car"),
        AIMessage(content="I can help you create a car configuration"),
        HumanMessage(content="I want a sedan"),
        AIMessage(content="Great choice! I'll configure a sedan for you")
    ]


@pytest.fixture
def sample_context_data():
    """Sample context data for testing."""
    return {
        "vehicle_type": "sedan",
        "performance_level": "standard",
        "fuel_preference": "gasoline",
        "budget": "medium",
        "configured_engine": True,
        "configured_body": True
    }
