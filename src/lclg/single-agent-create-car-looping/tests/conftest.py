"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


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
