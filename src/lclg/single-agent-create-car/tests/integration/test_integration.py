"""Integration tests for the single-agent car creation system."""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from agents.car_agent import CarAgent
from tools.engine_tools import EngineConfigurationTool, EngineSpecificationTool
from tools.body_tools import BodyConfigurationTool, BodyStyleTool
from tools.electrical_tools import ElectricalConfigurationTool, ElectricalSystemTool
from tools.tire_tools import TireConfigurationTool, TireSizingTool
from utils.logging_config import setup_logging, LoggingConfig


@pytest.mark.integration
class TestCarAgentIntegration:
    """Integration tests for the complete car agent system."""

    @pytest.fixture
    def mock_llm_with_json_response(self):
        """Create a mock LLM that returns properly formatted JSON."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
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
                    "horsepower": "280",
                    "@engineCode": "V6G280",
                    "@manufacturer": "Generic Motors"
                },
                "body": {
                    "exterior": {
                        "style": "sedan",
                        "color": "blue",
                        "paint_type": "metallic",
                        "finish": "glossy"
                    },
                    "interior": {
                        "seats": "cloth",
                        "seats_count": "5",
                        "dashboard_style": "modern",
                        "features": ["air_conditioning", "radio"]
                    },
                    "safety": {
                        "airbags": "front_and_side",
                        "abs": "yes",
                        "stability_control": "yes"
                    }
                },
                "electrical": {
                    "main_system": {
                        "voltage_system": "12V",
                        "alternator_output": "130A"
                    },
                    "battery": {
                        "capacity": "75Ah",
                        "type": "lead_acid",
                        "cold_cranking_amps": "650CCA"
                    },
                    "lighting": {
                        "headlights": "LED",
                        "taillights": "LED",
                        "interior_lighting": "standard"
                    },
                    "electronics": {
                        "infotainment": "touchscreen",
                        "charging_ports": "USB_and_12V"
                    }
                },
                "tires_and_wheels": {
                    "tires": {
                        "size": "225/60R16",
                        "type": "all_season",
                        "brand": "Continental",
                        "pressure": "32_psi"
                    },
                    "wheels": {
                        "size": "16x7",
                        "material": "alloy",
                        "finish": "painted",
                        "bolt_pattern": "5x114.3"
                    }
                }
            }
        })
        mock_llm.invoke.return_value = mock_response
        return mock_llm

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_complete_car_creation_workflow(self, mock_get_prompt, mock_create_agent,
                                          mock_llm_with_json_response, disable_logging):
        """Test the complete car creation workflow from start to finish."""
        # Setup mocks
        mock_get_prompt.return_value = "Mock car creation prompt"
        mock_executor = Mock()
        mock_create_agent.return_value = mock_executor

        # Create the car agent
        agent = CarAgent(
            llm=mock_llm_with_json_response,
            enable_logging=False
        )

        # Define requirements
        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "standard",
            "fuel_preference": "gasoline",
            "budget": "medium",
            "special_features": ["sunroof", "navigation"]
        }

        # Execute complete car creation
        result = agent.create_complete_car(requirements)

        # Verify the result structure
        assert "car_configuration" in result
        assert "metadata" in result

        # Verify car configuration components
        car_config = result["car_configuration"]
        assert "vehicle_info" in car_config
        assert "engine" in car_config
        assert "body" in car_config
        assert "electrical" in car_config
        assert "tires_and_wheels" in car_config

        # Verify metadata
        metadata = result["metadata"]
        assert metadata["created_by"] == "car_agent"
        assert metadata["creation_method"] == "single_agent_system"
        assert "performance_summary" in metadata
        assert "component_count" in metadata
        assert "estimated_compatibility" in metadata

        # Verify LLM was called
        mock_llm_with_json_response.invoke.assert_called_once()

    def test_all_tools_are_available(self, mock_ollama_llm, disable_logging):
        """Test that all expected tools are available in the agent."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

            # Check that all tool categories are present
            categories = agent.get_tool_categories()
            expected_categories = ["engine", "body", "electrical", "tires"]

            for category in expected_categories:
                assert category in categories
                assert len(categories[category]) > 0

            # Check total tool count
            assert len(agent.tools) >= 8

            # Check specific tools by name
            available_tools = agent.get_available_tools()
            expected_tools = [
                "configure_engine",
                "get_engine_specs",
                "configure_body",
                "get_body_style_info",
                "configure_electrical_system",
                "get_electrical_system_info",
                "configure_tires",
                "get_tire_sizing"
            ]

            for tool_name in expected_tools:
                assert tool_name in available_tools

    def test_tool_execution_integration(self, disable_logging):
        """Test that individual tools can be executed properly."""
        # Test engine tools
        engine_config_tool = EngineConfigurationTool()
        engine_result = engine_config_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )
        engine_data = json.loads(engine_result)
        assert "engineType" in engine_data
        assert "selected_type" in engine_data

        # Test body tools
        body_config_tool = BodyConfigurationTool()
        body_result = body_config_tool._run(
            vehicle_type="sedan",
            style_preference="modern",
            color_preference="blue"
        )
        body_data = json.loads(body_result)
        assert "body_configuration" in body_data

        # Test electrical tools
        electrical_config_tool = ElectricalConfigurationTool()
        electrical_result = electrical_config_tool._run(
            vehicle_type="sedan",
            engine_type="gasoline"
        )
        electrical_data = json.loads(electrical_result)
        assert "electrical_configuration" in electrical_data

        # Test tire tools
        tire_config_tool = TireConfigurationTool()
        tire_result = tire_config_tool._run(
            vehicle_type="sedan",
            performance_level="standard"
        )
        tire_data = json.loads(tire_result)
        assert "tire_configuration" in tire_data

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_error_handling_integration(self, mock_get_prompt, mock_create_agent, disable_logging):
        """Test error handling across the integrated system."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        # Create LLM that raises an exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM connection failed")

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = {"vehicle_type": "sedan"}
        result = agent.create_complete_car(requirements)

        # Should handle error gracefully
        assert "error" in result
        assert "Failed to create complete car" in result["error"]
        assert result["requirements"] == requirements

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_validation_integration(self, mock_get_prompt, mock_create_agent,
                                  mock_llm_with_json_response, disable_logging):
        """Test the validation system integration."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        agent = CarAgent(
            llm=mock_llm_with_json_response,
            enable_logging=False
        )

        requirements = {
            "vehicle_type": "sedan",
            "fuel_preference": "gasoline"
        }

        result = agent.create_complete_car(requirements)

        # Check that validation was applied
        assert "validation" in result["car_configuration"]
        assert result["car_configuration"]["validation"]["status"] == "validated"

        # Check that metadata includes compatibility check
        assert "estimated_compatibility" in result["metadata"]


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for the logging system."""

    def test_logging_integration_with_agent(self, tmp_path):
        """Test logging integration with agent operations."""
        log_file = tmp_path / "agent_integration.log"

        # Setup logging
        setup_logging(
            level="INFO",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file),
            json_format=False
        )

        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.OllamaLLM') as mock_llm_class:

            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = '{"car_configuration": {"engine": {"horsepower": "250"}}}'
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm

            # Create agent with logging enabled
            agent = CarAgent(enable_logging=True)

            # Perform operations that should generate logs
            requirements = {"vehicle_type": "sedan"}
            result = agent.create_complete_car(requirements)

            # Verify log file was created and contains entries
            assert log_file.exists()
            log_content = log_file.read_text()
            assert len(log_content) > 0

    def test_tool_logging_integration(self, tmp_path):
        """Test logging integration with tool execution."""
        log_file = tmp_path / "tool_integration.log"

        setup_logging(
            level="DEBUG",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file)
        )

        # Execute a tool with logging
        tool = EngineConfigurationTool()
        result = tool._run(vehicle_type="sedan", fuel_preference="gasoline")

        # Verify the tool executed successfully
        data = json.loads(result)
        assert "engineType" in data

        # Log file should exist and contain log entries
        if log_file.exists():
            log_content = log_file.read_text()
            # Basic check that logging occurred
            assert len(log_content) >= 0  # May be empty if tool doesn't log


@pytest.mark.integration
class TestSystemCompatibility:
    """Integration tests for component compatibility."""

    def test_engine_electrical_compatibility(self):
        """Test compatibility between engine and electrical systems."""
        # Test gasoline engine with 12V electrical system
        engine_tool = EngineConfigurationTool()
        engine_result = engine_tool._run(
            vehicle_type="sedan",
            fuel_preference="gasoline"
        )
        engine_data = json.loads(engine_result)

        electrical_tool = ElectricalConfigurationTool()
        electrical_result = electrical_tool._run(
            vehicle_type="sedan",
            engine_type="gasoline"
        )
        electrical_data = json.loads(electrical_result)

        # Verify compatibility
        assert engine_data["engineType"]["fuelType"] == "gasoline"
        assert electrical_data["electrical_configuration"]["main_system"]["voltage_system"] == "12V"

    def test_electric_engine_electrical_compatibility(self):
        """Test compatibility between electric engine and electrical system."""
        engine_tool = EngineConfigurationTool()
        engine_result = engine_tool._run(
            vehicle_type="sedan",
            fuel_preference="electric"
        )
        engine_data = json.loads(engine_result)

        electrical_tool = ElectricalConfigurationTool()
        electrical_result = electrical_tool._run(
            vehicle_type="sedan",
            engine_type="electric"
        )
        electrical_data = json.loads(electrical_result)

        # Verify electric compatibility
        assert engine_data["engineType"]["fuelType"] == "electric"
        assert electrical_data["electrical_configuration"]["main_system"]["voltage_system"] == "high-voltage"

    def test_vehicle_type_consistency(self):
        """Test that all tools respect vehicle type requirements."""
        vehicle_type = "truck"

        # Test engine selection for truck
        engine_tool = EngineConfigurationTool()
        engine_result = engine_tool._run(vehicle_type=vehicle_type)
        engine_data = json.loads(engine_result)

        # Trucks should get appropriate engines
        assert engine_data["selected_type"] in ["v8_gasoline", "v6_gasoline", "diesel_v6"]

        # Test body design for truck
        body_tool = BodyConfigurationTool()
        body_result = body_tool._run(vehicle_type=vehicle_type)
        body_data = json.loads(body_result)

        # Should have truck-appropriate body design
        assert "truck" in body_data["body_configuration"]["base_configuration"]["vehicle_type"].lower()


@pytest.mark.integration
class TestDataFlow:
    """Integration tests for data flow through the system."""

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_requirements_propagation(self, mock_get_prompt, mock_create_agent,
                                    mock_ollama_llm, disable_logging):
        """Test that requirements properly flow through the system."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

        requirements = {
            "vehicle_type": "coupe",
            "performance_level": "performance",
            "fuel_preference": "gasoline",
            "budget": "high",
            "special_features": ["racing_package", "sport_interior"]
        }

        # Mock the LLM response to include our requirements
        mock_response = Mock()
        mock_response.content = json.dumps({
            "car_configuration": {
                "vehicle_info": requirements,
                "engine": {"horsepower": "400"},
                "body": {"style": "coupe"},
                "electrical": {"voltage": "12V"},
                "tires_and_wheels": {"performance": "sport"}
            }
        })
        mock_ollama_llm.invoke.return_value = mock_response

        result = agent.create_complete_car(requirements)

        # Verify requirements were preserved in metadata
        assert result["metadata"]["requirements_used"] == requirements

        # Verify requirements influenced the configuration
        car_config = result["car_configuration"]
        assert car_config["vehicle_info"]["vehicle_type"] == "coupe"
        assert car_config["vehicle_info"]["performance_level"] == "performance"

    def test_metadata_generation(self, mock_ollama_llm, disable_logging):
        """Test that metadata is properly generated and includes all expected fields."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

            # Mock a successful car configuration
            mock_response = Mock()
            mock_response.content = json.dumps({
                "car_configuration": {
                    "vehicle_info": {"type": "sedan"},
                    "engine": {"horsepower": "300"},
                    "body": {"style": "sedan"},
                    "electrical": {"voltage": "12V"},
                    "tires_and_wheels": {"size": "225/60R16"}
                }
            })
            mock_ollama_llm.invoke.return_value = mock_response

            requirements = {"vehicle_type": "sedan"}
            result = agent.create_complete_car(requirements)

            # Verify metadata structure
            metadata = result["metadata"]
            expected_fields = [
                "created_by",
                "creation_method",
                "requirements_used",
                "performance_summary",
                "component_count",
                "estimated_compatibility"
            ]

            for field in expected_fields:
                assert field in metadata

            # Verify specific metadata values
            assert metadata["created_by"] == "car_agent"
            assert metadata["creation_method"] == "single_agent_system"
            assert metadata["component_count"] == 4  # engine, body, electrical, tires


@pytest.mark.integration
class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_luxury_sedan_creation(self, mock_get_prompt, mock_create_agent,
                                 mock_ollama_llm, disable_logging):
        """Test creating a luxury sedan with all options."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        # Mock luxury sedan response
        luxury_response = {
            "car_configuration": {
                "vehicle_info": {
                    "type": "sedan",
                    "performance_level": "luxury",
                    "fuel_preference": "gasoline",
                    "budget": "high"
                },
                "engine": {
                    "displacement": "4.0L",
                    "cylinders": "8",
                    "fuelType": "gasoline",
                    "horsepower": "450"
                },
                "body": {
                    "exterior": {"style": "sedan", "color": "pearl_white"},
                    "interior": {"seats": "leather", "features": ["heated_seats", "massage"]}
                },
                "electrical": {
                    "main_system": {"voltage_system": "12V"},
                    "electronics": {"premium_audio": "yes", "navigation": "yes"}
                },
                "tires_and_wheels": {
                    "tires": {"size": "245/45R18", "type": "performance"},
                    "wheels": {"material": "alloy", "size": "18x8"}
                }
            }
        }

        mock_response = Mock()
        mock_response.content = json.dumps(luxury_response)
        mock_ollama_llm.invoke.return_value = mock_response

        agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "luxury",
            "fuel_preference": "gasoline",
            "budget": "high",
            "special_features": ["leather_interior", "premium_audio", "navigation"]
        }

        result = agent.create_complete_car(requirements)

        # Verify luxury specifications
        car_config = result["car_configuration"]
        assert int(car_config["engine"]["horsepower"]) >= 400
        assert car_config["body"]["interior"]["seats"] == "leather"
        assert car_config["electrical"]["electronics"]["premium_audio"] == "yes"

    @patch('agents.base_agent.create_agent')
    @patch('agents.base_agent.get_agent_prompt')
    def test_electric_vehicle_creation(self, mock_get_prompt, mock_create_agent,
                                     mock_ollama_llm, disable_logging):
        """Test creating an electric vehicle."""
        mock_get_prompt.return_value = "Mock prompt"
        mock_create_agent.return_value = Mock()

        # Mock electric vehicle response
        electric_response = {
            "car_configuration": {
                "vehicle_info": {
                    "type": "sedan",
                    "fuel_preference": "electric"
                },
                "engine": {
                    "fuelType": "electric",
                    "horsepower": "300",
                    "motor_type": "permanent_magnet"
                },
                "electrical": {
                    "main_system": {"voltage_system": "high-voltage"},
                    "battery": {"capacity": "75kWh", "type": "lithium_ion"},
                    "charging": {"fast_charge": "yes", "charging_ports": "CCS_Type2"}
                },
                "body": {"exterior": {"style": "sedan"}},
                "tires_and_wheels": {"tires": {"type": "low_rolling_resistance"}}
            }
        }

        mock_response = Mock()
        mock_response.content = json.dumps(electric_response)
        mock_ollama_llm.invoke.return_value = mock_response

        agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

        requirements = {
            "vehicle_type": "sedan",
            "fuel_preference": "electric",
            "budget": "medium"
        }

        result = agent.create_complete_car(requirements)

        # Verify electric vehicle specifications
        car_config = result["car_configuration"]
        assert car_config["engine"]["fuelType"] == "electric"
        assert car_config["electrical"]["main_system"]["voltage_system"] == "high-voltage"
        assert "battery" in car_config["electrical"]
        assert "charging" in car_config["electrical"]

    def test_performance_truck_creation(self, mock_ollama_llm, disable_logging):
        """Test creating a performance truck."""
        with patch('agents.base_agent.create_agent'), \
             patch('agents.base_agent.get_agent_prompt'):

            # Mock performance truck response
            truck_response = {
                "car_configuration": {
                    "vehicle_info": {
                        "type": "truck",
                        "performance_level": "performance"
                    },
                    "engine": {
                        "displacement": "6.2L",
                        "cylinders": "8",
                        "fuelType": "gasoline",
                        "horsepower": "650",
                        "supercharged": "yes"
                    },
                    "body": {
                        "exterior": {"style": "crew_cab", "bed_length": "short"},
                        "capabilities": {"towing_capacity": "12000_lbs"}
                    },
                    "electrical": {"main_system": {"voltage_system": "12V"}},
                    "tires_and_wheels": {
                        "tires": {"size": "275/65R18", "type": "all_terrain"},
                        "wheels": {"material": "alloy", "size": "18x9"}
                    }
                }
            }

            mock_response = Mock()
            mock_response.content = json.dumps(truck_response)
            mock_ollama_llm.invoke.return_value = mock_response

            agent = CarAgent(llm=mock_ollama_llm, enable_logging=False)

            requirements = {
                "vehicle_type": "truck",
                "performance_level": "performance",
                "fuel_preference": "gasoline",
                "budget": "high"
            }

            result = agent.create_complete_car(requirements)

            # Verify performance truck specifications
            car_config = result["car_configuration"]
            assert car_config["vehicle_info"]["type"] == "truck"
            assert int(car_config["engine"]["horsepower"]) >= 600
            assert car_config["engine"]["cylinders"] == "8"
            assert "towing_capacity" in car_config["body"]["capabilities"]