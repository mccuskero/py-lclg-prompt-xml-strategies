"""Unit tests for CarAgent class."""

import pytest
from unittest.mock import Mock, patch
from agents.car_agent import CarAgent


class TestCarAgent:
    """Test the CarAgent class."""

    def test_initialization(self, mock_llm):
        """Test CarAgent initialization."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        assert agent.name == "car_agent"
        assert len(agent.tools) == 8  # 2 engine + 2 body + 2 electrical + 2 tire
        assert agent.memory is not None

    def test_get_agent_type(self, mock_llm):
        """Test getting agent type."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        assert agent._get_agent_type() == "car"

    def test_get_tool_categories(self, mock_llm):
        """Test getting tool categories."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        categories = agent.get_tool_categories()

        assert "engine" in categories
        assert "body" in categories
        assert "electrical" in categories
        assert "tires" in categories

    def test_parse_user_input_sedan(self, mock_llm):
        """Test parsing user input for sedan."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = agent._parse_user_input("I want a sedan")

        assert requirements["vehicle_type"] == "sedan"
        assert requirements["user_input"] == "I want a sedan"

    def test_parse_user_input_suv(self, mock_llm):
        """Test parsing user input for SUV."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = agent._parse_user_input("I need a performance SUV")

        assert requirements["vehicle_type"] == "suv"
        assert requirements["performance_level"] == "performance"

    def test_parse_user_input_electric(self, mock_llm):
        """Test parsing user input for electric vehicle."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = agent._parse_user_input("I want an electric car")

        assert requirements["fuel_preference"] == "electric"

    def test_parse_user_input_hybrid(self, mock_llm):
        """Test parsing user input for hybrid vehicle."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = agent._parse_user_input("Give me a hybrid vehicle")

        assert requirements["fuel_preference"] == "hybrid"

    def test_parse_user_input_luxury(self, mock_llm):
        """Test parsing user input for luxury vehicle."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = agent._parse_user_input("I want a luxury sedan")

        assert requirements["budget"] == "high"
        assert requirements["vehicle_type"] == "sedan"

    def test_validate_component_data_complete(self, mock_llm, sample_car_config):
        """Test validating complete car configuration."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        validated = agent._validate_component_data(sample_car_config)

        assert "validation" in validated
        assert validated["validation"]["status"] == "validated"
        assert len(validated["validation"]["missing_sections"]) == 0

    def test_validate_component_data_missing_engine(self, mock_llm):
        """Test validating car configuration with missing engine."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        incomplete_config = {
            "car_configuration": {
                "body": {},
                "electrical": {},
                "tires_and_wheels": {}
            }
        }

        validated = agent._validate_component_data(incomplete_config)

        assert validated["validation"]["status"] == "incomplete"
        assert "engine" in validated["validation"]["missing_sections"]

    def test_validate_component_data_error(self, mock_llm):
        """Test validating car configuration with error."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        error_config = {
            "error": "Some error occurred"
        }

        validated = agent._validate_component_data(error_config)

        assert "error" in validated
        assert validated["error"] == "Some error occurred"

    def test_calculate_performance_summary_economy(self, mock_llm):
        """Test calculating performance summary for economy car."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        config = {
            "engine": {
                "horsepower": "150"
            }
        }

        summary = agent._calculate_performance_summary(config)

        assert summary["performance_category"] == "economy"
        assert "150" in summary["power_rating"]

    def test_calculate_performance_summary_performance(self, mock_llm):
        """Test calculating performance summary for performance car."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        config = {
            "engine": {
                "horsepower": "350 HP"
            }
        }

        summary = agent._calculate_performance_summary(config)

        assert summary["performance_category"] == "performance"

    def test_check_component_compatibility_compatible(self, mock_llm):
        """Test checking component compatibility for compatible configuration."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        config = {
            "engine": {
                "fuelType": "gasoline"
            },
            "electrical": {
                "main_system": {
                    "voltage_system": "12V"
                }
            }
        }

        compatibility = agent._check_component_compatibility(config)

        assert compatibility == "compatible"

    def test_check_component_compatibility_electric_incompatible(self, mock_llm):
        """Test checking component compatibility for electric with wrong voltage."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        config = {
            "engine": {
                "fuelType": "electric"
            },
            "electrical": {
                "main_system": {
                    "voltage_system": "12V"
                }
            }
        }

        compatibility = agent._check_component_compatibility(config)

        assert "Issues found" in compatibility
        assert "high-voltage" in compatibility
