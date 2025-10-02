"""Unit tests for the CarAgent class."""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from agents.car_agent import CarAgent
from agents.base_agent import AgentMessage


class TestCarAgent:
    """Test cases for CarAgent functionality."""

    @pytest.fixture
    def car_agent(self, mock_ollama_llm, disable_logging):
        """Create a CarAgent instance for testing."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):
            return CarAgent(
                model_name="test_model",
                base_url="http://localhost:11434",
                temperature=0.1,
                enable_logging=False
            )

    def test_agent_initialization(self, car_agent):
        """Test that the CarAgent initializes correctly."""
        assert car_agent.name == "car_agent"
        assert car_agent._get_agent_type() == "car"
        assert len(car_agent.tools) > 0

    def test_agent_has_all_tool_categories(self, car_agent):
        """Test that the agent has tools from all categories."""
        tool_categories = car_agent.get_tool_categories()
        expected_categories = ["engine", "body", "electrical", "tires"]

        for category in expected_categories:
            assert category in tool_categories
            assert len(tool_categories[category]) > 0

    def test_get_system_prompt(self, car_agent):
        """Test getting system prompt."""
        prompt = car_agent._get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "car creation agent" in prompt.lower()
        assert "engine" in prompt.lower()
        assert "body" in prompt.lower()
        assert "electrical" in prompt.lower()
        assert "tire" in prompt.lower()

    def test_build_component_request(self, car_agent):
        """Test building component request."""
        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "standard",
            "fuel_preference": "gasoline",
            "budget": "medium",
            "special_features": ["sunroof"]
        }

        request = car_agent._build_component_request(requirements)

        assert isinstance(request, str)
        assert "sedan" in request
        assert "standard" in request
        assert "gasoline" in request
        assert "medium" in request
        assert "sunroof" in request
        assert "JSON" in request

    def test_agent_info(self, car_agent):
        """Test getting agent information."""
        info = car_agent.get_agent_info()

        assert info["name"] == "car_agent"
        assert info["type"] == "car"
        assert "tools" in info
        assert len(info["tools"]) > 0

    def test_create_complete_car_success(self, car_agent, sample_car_requirements):
        """Test successful complete car creation."""
        with patch.object(car_agent, 'create_component_json') as mock_create:
            mock_create.return_value = {
                "car_configuration": {
                    "engine": {"horsepower": "280"},
                    "body": {"style": "sedan"}
                }
            }

            result = car_agent.create_complete_car(sample_car_requirements)

            assert "car_configuration" in result
            assert "metadata" in result
            assert result["metadata"]["created_by"] == "car_agent"
            mock_create.assert_called_once_with(sample_car_requirements)

    def test_create_complete_car_with_error(self, car_agent, sample_car_requirements):
        """Test complete car creation with error."""
        with patch.object(car_agent, 'create_component_json') as mock_create:
            mock_create.return_value = {
                "error": "Component creation failed"
            }

            result = car_agent.create_complete_car(sample_car_requirements)

            assert "error" in result
            # Should not add metadata when there's an error
            assert "metadata" not in result

    def test_create_complete_car_exception(self, car_agent, sample_car_requirements):
        """Test complete car creation with exception."""
        with patch.object(car_agent, 'create_component_json', side_effect=Exception("Test exception")):
            result = car_agent.create_complete_car(sample_car_requirements)

            assert "error" in result
            assert "Failed to create complete car" in result["error"]
            assert result["requirements"] == sample_car_requirements

    def test_validate_component_data_success(self, car_agent):
        """Test component data validation with valid data."""
        valid_data = {
            "car_configuration": {
                "engine": {"horsepower": "300"},
                "body": {"style": "sedan"},
                "electrical": {"voltage": "12V"},
                "tires_and_wheels": {"size": "225/60R16"}
            }
        }

        validated = car_agent._validate_component_data(valid_data)
        assert "validation" in validated
        assert validated["validation"]["status"] == "validated"
        assert "components_checked" in validated["validation"]

    def test_validate_component_data_with_error(self, car_agent):
        """Test component data validation with error data."""
        error_data = {
            "error": "Component creation failed",
            "details": "LLM connection failed"
        }

        validated = car_agent._validate_component_data(error_data)
        assert validated == error_data  # Should return unchanged

    def test_validate_component_data_missing_sections(self, car_agent):
        """Test component data validation with missing sections."""
        incomplete_data = {
            "car_configuration": {
                "engine": {"horsepower": "300"},
                # Missing body, electrical, tires_and_wheels
            }
        }

        validated = car_agent._validate_component_data(incomplete_data)
        car_config = validated["car_configuration"]

        # Should add missing sections with error status
        assert "body" in car_config
        assert car_config["body"]["status"] == "not_configured"
        assert "electrical" in car_config
        assert "tires_and_wheels" in car_config

    def test_calculate_performance_summary(self, car_agent):
        """Test performance summary calculation."""
        # Test with valid horsepower
        car_config = {"engine": {"horsepower": "250"}}
        summary = car_agent._calculate_performance_summary(car_config)
        assert summary["power_rating"] == "250 HP"
        assert summary["performance_category"] == "standard"

        # Test different performance categories
        test_cases = [
            (150, "economy"),
            (250, "standard"),
            (350, "performance"),
            (450, "high_performance")
        ]

        for hp, expected_category in test_cases:
            config = {"engine": {"horsepower": str(hp)}}
            summary = car_agent._calculate_performance_summary(config)
            assert summary["performance_category"] == expected_category

    def test_calculate_performance_summary_missing_data(self, car_agent):
        """Test performance summary with missing data."""
        # Test with missing engine
        car_config = {}
        summary = car_agent._calculate_performance_summary(car_config)
        assert summary["power_rating"] == "unknown"
        assert summary["performance_category"] == "unknown"

        # Test with missing horsepower
        car_config = {"engine": {}}
        summary = car_agent._calculate_performance_summary(car_config)
        assert summary["power_rating"] == "unknown"

    def test_check_component_compatibility_compatible(self, car_agent):
        """Test component compatibility checking with compatible configuration."""
        compatible_config = {
            "engine": {"fuelType": "gasoline"},
            "electrical": {"main_system": {"voltage_system": "12V"}}
        }

        compatibility = car_agent._check_component_compatibility(compatible_config)
        assert compatibility == "compatible"

    def test_check_component_compatibility_electric_mismatch(self, car_agent):
        """Test compatibility check with electric engine and wrong electrical system."""
        incompatible_config = {
            "engine": {"fuelType": "electric"},
            "electrical": {"main_system": {"voltage_system": "12V"}}
        }

        compatibility = car_agent._check_component_compatibility(incompatible_config)
        assert "Issues found" in compatibility
        assert "Electric engine requires high-voltage" in compatibility

    def test_check_component_compatibility_hybrid_mismatch(self, car_agent):
        """Test compatibility check with hybrid engine and wrong electrical system."""
        incompatible_config = {
            "engine": {"fuelType": "hybrid"},
            "electrical": {"main_system": {"voltage_system": "12V"}}
        }

        compatibility = car_agent._check_component_compatibility(incompatible_config)
        assert "Issues found" in compatibility
        assert "Hybrid engine requires hybrid" in compatibility

    def test_check_component_compatibility_missing_data(self, car_agent):
        """Test compatibility check with missing data."""
        # Missing electrical system
        config = {"engine": {"fuelType": "gasoline"}}
        compatibility = car_agent._check_component_compatibility(config)
        assert compatibility == "compatible"  # No issues found with missing data

        # Missing engine
        config = {"electrical": {"main_system": {"voltage_system": "12V"}}}
        compatibility = car_agent._check_component_compatibility(config)
        assert compatibility == "compatible"

    def test_add_car_metadata(self, car_agent, sample_car_requirements):
        """Test adding car metadata."""
        car_data = {
            "car_configuration": {
                "engine": {"horsepower": "280"},
                "body": {"style": "sedan"},
                "electrical": {"voltage": "12V"},
                "tires_and_wheels": {"size": "225/60R16"}
            }
        }

        result = car_agent._add_car_metadata(car_data, sample_car_requirements)

        assert "metadata" in result
        metadata = result["metadata"]
        assert metadata["created_by"] == "car_agent"
        assert metadata["creation_method"] == "single_agent_system"
        assert metadata["requirements_used"] == sample_car_requirements
        assert "performance_summary" in metadata
        assert "component_count" in metadata
        assert "estimated_compatibility" in metadata

    def test_add_car_metadata_with_performance_data(self, car_agent):
        """Test adding car metadata with performance calculation."""
        car_data = {
            "car_configuration": {
                "engine": {"horsepower": "350"},
                "body": {"style": "coupe"}
            }
        }

        requirements = {"vehicle_type": "coupe"}
        result = car_agent._add_car_metadata(car_data, requirements)

        performance_summary = result["metadata"]["performance_summary"]
        assert performance_summary["power_rating"] == "350 HP"
        assert performance_summary["performance_category"] == "performance"

@pytest.mark.tools
class TestCarAgentTools:
    """Test cases for CarAgent tool functionality."""

    def test_tool_availability(self, car_agent):
        """Test that all expected tools are available."""
        available_tools = car_agent.get_available_tools()

        # Should have tools from all categories
        assert len(available_tools) >= 16  # Expected minimum number of tools

        # Check for key tools from each category
        expected_tools = [
            "configure_engine",
            "get_engine_specs",
            "design_body",
            "configure_electrical",
            "configure_tires"
        ]

        for tool in expected_tools:
            assert tool in available_tools

    def test_get_tool_categories(self, car_agent):
        """Test getting tool categories."""
        categories = car_agent.get_tool_categories()

        expected_categories = ["engine", "body", "electrical", "tires"]
        for category in expected_categories:
            assert category in categories
            assert isinstance(categories[category], list)
            assert len(categories[category]) > 0

        # Check specific tool counts
        assert len(categories["engine"]) == 2  # configure_engine, get_engine_specs
        assert len(categories["body"]) == 2    # configure_body, get_body_style_info
        assert len(categories["electrical"]) == 2  # configure_electrical_system, etc.
        assert len(categories["tires"]) == 2   # configure_tires, get_tire_sizing

@pytest.mark.integration
class TestCarAgentIntegration:
    """Integration tests for CarAgent."""

    def test_full_car_creation_workflow(self, mock_ollama_llm, sample_car_requirements, disable_logging):
        """Test complete car creation workflow."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'), \
             patch.object(mock_ollama_llm, 'invoke') as mock_invoke:

            # Mock LLM response with complete car configuration
            mock_response = Mock()
            mock_response.content = json.dumps({
                "car_configuration": {
                    "vehicle_info": sample_car_requirements,
                    "engine": {
                        "displacement": "3.5L",
                        "cylinders": "6",
                        "fuelType": "gasoline",
                        "horsepower": "280"
                    },
                    "body": {
                        "exterior": {"style": "sedan", "color": "blue"},
                        "interior": {"seats": "cloth"}
                    },
                    "electrical": {
                        "main_system": {"voltage_system": "12V"},
                        "battery": {"capacity": "75Ah"}
                    },
                    "tires_and_wheels": {
                        "tires": {"size": "225/60R16"},
                        "wheels": {"material": "alloy"}
                    }
                }
            })
            mock_invoke.return_value = mock_response

            agent = CarAgent(enable_logging=False)
            result = agent.create_complete_car(sample_car_requirements)

            # Verify the complete workflow
            assert "car_configuration" in result
            assert "metadata" in result
            assert result["metadata"]["created_by"] == "car_agent"
            assert "performance_summary" in result["metadata"]

            # Verify car configuration structure
            car_config = result["car_configuration"]
            assert "engine" in car_config
            assert "body" in car_config
            assert "electrical" in car_config
            assert "tires_and_wheels" in car_config

    def test_car_creation_with_tool_integration(self, mock_ollama_llm, disable_logging):
        """Test car creation with actual tool setup."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

            # Verify all tool categories are set up
            categories = agent.get_tool_categories()
            assert len(categories) == 4
            assert all(len(tools) > 0 for tools in categories.values())

            # Verify agent has the expected number of tools
            assert len(agent.tools) >= 8

    def test_error_handling_integration(self, mock_ollama_llm_with_error, sample_car_requirements, disable_logging):
        """Test error handling in complete workflow."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = CarAgent(llm=mock_ollama_llm_with_error, enable_logging=False)
            result = agent.create_complete_car(sample_car_requirements)

            assert "error" in result
            assert "Failed to create complete car" in result["error"]
            assert result["requirements"] == sample_car_requirements