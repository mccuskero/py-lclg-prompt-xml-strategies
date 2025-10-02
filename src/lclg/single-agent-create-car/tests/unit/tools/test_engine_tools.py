"""Unit tests for engine tools module."""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from tools.engine_tools import (
    EngineConfigurationTool, EngineSpecificationTool,
    ENGINE_CONFIGURATIONS, ENGINE_COMPARTMENT_DATA
)


class TestEngineConfigurationTool:
    """Test cases for EngineConfigurationTool."""

    @pytest.fixture
    def engine_tool(self):
        """Create an EngineConfigurationTool instance for testing."""
        return EngineConfigurationTool()

    def test_tool_initialization(self, engine_tool):
        """Test tool initialization."""
        assert engine_tool.name == "configure_engine"
        assert "Configure engine specifications" in engine_tool.description
        assert hasattr(engine_tool, 'logger')

    def test_basic_engine_configuration(self, engine_tool):
        """Test basic engine configuration."""
        result = engine_tool._run()
        data = json.loads(result)

        assert "engineType" in data
        assert "compartment_info" in data
        assert "selected_type" in data
        assert "requirements_met" in data

        # Default should be v6_gasoline
        assert data["selected_type"] in ENGINE_CONFIGURATIONS
        assert data["engineType"]["fuelType"] == "gasoline"

    def test_gasoline_engine_selection(self, engine_tool):
        """Test gasoline engine selection."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )
        data = json.loads(result)

        assert data["selected_type"] == "v6_gasoline"
        assert data["engineType"]["fuelType"] == "gasoline"
        assert data["requirements_met"]["fuel_preference"] == "gasoline"

    def test_electric_engine_selection(self, engine_tool):
        """Test electric engine selection."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="electric"
        )
        data = json.loads(result)

        assert data["selected_type"] == "electric"
        assert data["engineType"]["fuelType"] == "electric"

    def test_hybrid_engine_selection(self, engine_tool):
        """Test hybrid engine selection."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="hybrid"
        )
        data = json.loads(result)

        assert data["selected_type"] == "hybrid"
        assert data["engineType"]["fuelType"] == "hybrid"

    def test_diesel_engine_selection(self, engine_tool):
        """Test diesel engine selection."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="diesel"
        )
        data = json.loads(result)

        assert data["selected_type"] == "diesel_v6"
        assert data["engineType"]["fuelType"] == "diesel"

    def test_performance_engine_selection(self, engine_tool):
        """Test performance engine selection."""
        # Performance sedan should get turbo
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="performance",
            fuel_preference="gasoline"
        )
        data = json.loads(result)
        assert data["selected_type"] == "v4_turbo"

        # Performance SUV should get V8
        result = engine_tool._run(
            vehicle_type="suv",
            performance_level="performance",
            fuel_preference="gasoline"
        )
        data = json.loads(result)
        assert data["selected_type"] == "v8_gasoline"

    def test_vehicle_type_engine_selection(self, engine_tool):
        """Test engine selection based on vehicle type."""
        # Truck should get V8 or V6
        result = engine_tool._run(
            vehicle_type="truck",
            performance_level="standard",
            fuel_preference="gasoline"
        )
        data = json.loads(result)
        assert data["selected_type"] in ["v8_gasoline", "v6_gasoline"]

        # Coupe should get turbo
        result = engine_tool._run(
            vehicle_type="coupe",
            performance_level="standard",
            fuel_preference="gasoline"
        )
        data = json.loads(result)
        assert data["selected_type"] == "v4_turbo"

    def test_electric_capable_override(self, engine_tool):
        """Test electric_capable parameter override."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline",
            electric_capable=True
        )
        data = json.loads(result)

        assert data["selected_type"] == "electric"
        assert data["engineType"]["fuelType"] == "electric"

    def test_compartment_info_inclusion(self, engine_tool):
        """Test that compartment info is included."""
        result = engine_tool._run()
        data = json.loads(result)

        assert "compartment_info" in data
        compartment = data["compartment_info"]
        assert "size" in compartment
        assert "cooling_requirements" in compartment

    def test_requirements_tracking(self, engine_tool):
        """Test that requirements are tracked in output."""
        vehicle_type = "coupe"
        performance_level = "sport"
        fuel_preference = "gasoline"
        electric_capable = False

        result = engine_tool._run(
            vehicle_type=vehicle_type,
            performance_level=performance_level,
            fuel_preference=fuel_preference,
            electric_capable=electric_capable
        )
        data = json.loads(result)

        requirements = data["requirements_met"]
        assert requirements["vehicle_type"] == vehicle_type
        assert requirements["performance_level"] == performance_level
        assert requirements["fuel_preference"] == fuel_preference
        assert requirements["electric_capable"] == electric_capable

    def test_error_handling(self, engine_tool):
        """Test error handling in engine configuration."""
        with patch.object(engine_tool, '_select_engine_type', side_effect=Exception("Test error")):
            result = engine_tool._run()
            data = json.loads(result)

            assert "error" in data
            assert "Engine configuration failed" in data["error"]
            assert "fallback" in data

    def test_select_engine_type_method(self, engine_tool):
        """Test the _select_engine_type method directly."""
        # Test electric preference
        engine_type = engine_tool._select_engine_type(
            "sedan", "standard", "electric", False
        )
        assert engine_type == "electric"

        # Test hybrid preference
        engine_type = engine_tool._select_engine_type(
            "sedan", "standard", "hybrid", False
        )
        assert engine_type == "hybrid"

        # Test diesel preference
        engine_type = engine_tool._select_engine_type(
            "sedan", "standard", "diesel", False
        )
        assert engine_type == "diesel_v6"

        # Test performance gasoline
        engine_type = engine_tool._select_engine_type(
            "sedan", "performance", "gasoline", False
        )
        assert engine_type == "v4_turbo"

        # Test truck standard
        engine_type = engine_tool._select_engine_type(
            "truck", "standard", "gasoline", False
        )
        assert engine_type == "v6_gasoline"


class TestEngineSpecificationTool:
    """Test cases for EngineSpecificationTool."""

    @pytest.fixture
    def spec_tool(self):
        """Create an EngineSpecificationTool instance for testing."""
        return EngineSpecificationTool()

    def test_tool_initialization(self, spec_tool):
        """Test tool initialization."""
        assert spec_tool.name == "get_engine_specs"
        assert "detailed engine specifications" in spec_tool.description.lower()

    def test_basic_engine_specs(self, spec_tool):
        """Test basic engine specifications retrieval."""
        result = spec_tool._run()
        data = json.loads(result)

        assert "engine_specifications" in data
        assert "electrical_requirements" in data
        assert "cooling_specifications" in data
        assert "compartment_constraints" in data
        assert "integration_notes" in data

    def test_engine_specs_with_specific_type(self, spec_tool):
        """Test engine specs for specific engine type."""
        result = spec_tool._run(engine_type="electric")
        data = json.loads(result)

        specs = data["engine_specifications"]
        assert specs["fuelType"] == "electric"

        electrical = data["electrical_requirements"]
        assert electrical["voltage_system"] == "high-voltage"
        assert electrical["battery_capacity"] == "75kWh"

    def test_electrical_requirements_gasoline(self, spec_tool):
        """Test electrical requirements for gasoline engine."""
        result = spec_tool._run(engine_type="v6_gasoline")
        data = json.loads(result)

        electrical = data["electrical_requirements"]
        assert electrical["voltage_system"] == "12V"
        assert electrical["battery_capacity"] == "75Ah"
        assert "alternator_output" in electrical

    def test_electrical_requirements_hybrid(self, spec_tool):
        """Test electrical requirements for hybrid engine."""
        result = spec_tool._run(engine_type="hybrid")
        data = json.loads(result)

        electrical = data["electrical_requirements"]
        assert electrical["voltage_system"] == "hybrid"
        assert electrical["charging_capability"] == "regenerative"

    def test_electrical_requirements_electric(self, spec_tool):
        """Test electrical requirements for electric engine."""
        result = spec_tool._run(engine_type="electric")
        data = json.loads(result)

        electrical = data["electrical_requirements"]
        assert electrical["voltage_system"] == "high-voltage"
        assert electrical["charging_capability"] == "DC_fast"
        assert electrical["alternator_needed"] is False

    def test_cooling_specifications_standard(self, spec_tool):
        """Test cooling specifications for standard engine."""
        result = spec_tool._run(engine_type="v6_gasoline")
        data = json.loads(result)

        cooling = data["cooling_specifications"]
        assert cooling["radiator_size"] == "standard"
        assert cooling["fan_type"] == "electric"
        assert "coolant_capacity" in cooling

    def test_cooling_specifications_enhanced(self, spec_tool):
        """Test cooling specifications for enhanced cooling engine."""
        result = spec_tool._run(engine_type="v4_turbo")  # Has enhanced cooling
        data = json.loads(result)

        cooling = data["cooling_specifications"]
        assert cooling["radiator_size"] == "oversized"
        assert cooling["fan_type"] == "dual_electric"
        assert "intercooler" in cooling

    def test_cooling_specifications_electric(self, spec_tool):
        """Test cooling specifications for electric engine."""
        result = spec_tool._run(engine_type="electric")
        data = json.loads(result)

        cooling = data["cooling_specifications"]
        assert "battery_cooling" in cooling
        assert cooling["thermal_management"] == "active"

    def test_cooling_specifications_heavy_duty(self, spec_tool):
        """Test cooling specifications for heavy duty engine."""
        result = spec_tool._run(engine_type="diesel_v6")  # Has heavy duty cooling
        data = json.loads(result)

        cooling = data["cooling_specifications"]
        assert cooling["radiator_size"] == "heavy_duty"
        assert cooling["fan_type"] == "clutch_driven"

    def test_integration_notes(self, spec_tool):
        """Test integration notes generation."""
        result = spec_tool._run(engine_type="v8_gasoline")
        data = json.loads(result)

        notes = data["integration_notes"]
        assert "body_agent" in notes
        assert "electrical_agent" in notes
        assert "general" in notes
        assert "larger hood" in notes["body_agent"]  # V8 specific note

    def test_integration_notes_electric(self, spec_tool):
        """Test integration notes for electric engine."""
        result = spec_tool._run(engine_type="electric")
        data = json.loads(result)

        notes = data["integration_notes"]
        assert "No traditional grille needed" in notes["body_agent"]
        assert "High-voltage battery system" in notes["electrical_agent"]

    def test_invalid_engine_type_fallback(self, spec_tool):
        """Test fallback for invalid engine type."""
        result = spec_tool._run(engine_type="invalid_engine")
        data = json.loads(result)

        # Should fallback to v6_gasoline
        specs = data["engine_specifications"]
        assert specs["fuelType"] == "gasoline"
        assert specs["cylinders"] == "6"

    def test_error_handling(self, spec_tool):
        """Test error handling in spec tool."""
        with patch.object(spec_tool, '_calculate_electrical_requirements', side_effect=Exception("Test error")):
            result = spec_tool._run()
            data = json.loads(result)

            assert "error" in data
            assert "Failed to get engine specifications" in data["error"]

    def test_calculate_electrical_requirements_method(self, spec_tool):
        """Test the _calculate_electrical_requirements method directly."""
        # Test gasoline engine
        engine_config = {"fuelType": "gasoline", "horsepower": "300"}
        electrical = spec_tool._calculate_electrical_requirements(engine_config)

        assert electrical["voltage_system"] == "12V"
        assert int(electrical["alternator_output"].replace("A", "")) >= 120

        # Test electric engine
        engine_config = {"fuelType": "electric", "horsepower": "300"}
        electrical = spec_tool._calculate_electrical_requirements(engine_config)

        assert electrical["voltage_system"] == "high-voltage"
        assert electrical["alternator_needed"] is False

    def test_get_cooling_specifications_method(self, spec_tool):
        """Test the _get_cooling_specifications method directly."""
        engine_config = {"fuelType": "gasoline"}
        compartment_info = {"cooling_requirements": "standard"}

        cooling = spec_tool._get_cooling_specifications(engine_config, compartment_info)

        assert cooling["radiator_size"] == "standard"
        assert cooling["fan_type"] == "electric"

    def test_get_integration_notes_method(self, spec_tool):
        """Test the _get_integration_notes method directly."""
        notes = spec_tool._get_integration_notes("v6_gasoline")

        assert "body_agent" in notes
        assert "electrical_agent" in notes
        assert "general" in notes
        assert "v6_gasoline" in notes["general"]


class TestEngineConfigurationsData:
    """Test cases for engine configuration data."""

    def test_engine_configurations_completeness(self):
        """Test that all engine configurations have required fields."""
        required_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode", "@manufacturer"]

        for engine_type, config in ENGINE_CONFIGURATIONS.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {engine_type}"
                assert config[field] is not None, f"None value for {field} in {engine_type}"

    def test_engine_compartment_data_completeness(self):
        """Test that all engine types have compartment data."""
        for engine_type in ENGINE_CONFIGURATIONS.keys():
            assert engine_type in ENGINE_COMPARTMENT_DATA, f"Missing compartment data for {engine_type}"

            compartment = ENGINE_COMPARTMENT_DATA[engine_type]
            assert "size" in compartment
            assert "cooling_requirements" in compartment

    def test_engine_configuration_values(self):
        """Test that engine configuration values are reasonable."""
        for engine_type, config in ENGINE_CONFIGURATIONS.items():
            # Test horsepower is numeric
            hp = int(config["horsepower"])
            assert 100 <= hp <= 1000, f"Unreasonable horsepower {hp} for {engine_type}"

            # Test cylinders is numeric
            cylinders = int(config["cylinders"]) if config["cylinders"] != "0" else 0
            assert 0 <= cylinders <= 12, f"Unreasonable cylinder count {cylinders} for {engine_type}"

            # Test fuel type is valid
            assert config["fuelType"] in ["gasoline", "diesel", "electric", "hybrid"], f"Invalid fuel type for {engine_type}"

    def test_compartment_data_values(self):
        """Test that compartment data values are valid."""
        valid_sizes = ["small", "medium", "large"]
        valid_cooling = ["minimal", "standard", "enhanced", "heavy_duty", "dual"]

        for engine_type, compartment in ENGINE_COMPARTMENT_DATA.items():
            assert compartment["size"] in valid_sizes, f"Invalid size for {engine_type}"
            assert compartment["cooling_requirements"] in valid_cooling, f"Invalid cooling for {engine_type}"


@pytest.mark.integration
class TestEngineToolsIntegration:
    """Integration tests for engine tools."""

    def test_configuration_to_specification_workflow(self):
        """Test workflow from configuration to specification."""
        config_tool = EngineConfigurationTool()
        spec_tool = EngineSpecificationTool()

        # Configure an engine
        config_result = config_tool._run(
            vehicle_type="sedan",
            performance_level="performance",
            fuel_preference="gasoline"
        )
        config_data = json.loads(config_result)

        # Get specifications for the configured engine
        engine_type = config_data["selected_type"]
        spec_result = spec_tool._run(engine_type=engine_type)
        spec_data = json.loads(spec_result)

        # Verify consistency
        assert config_data["engineType"]["fuelType"] == spec_data["engine_specifications"]["fuelType"]
        assert config_data["compartment_info"]["size"] == spec_data["compartment_constraints"]["size"]

    def test_all_engine_types_have_specs(self):
        """Test that all engine types can generate specifications."""
        spec_tool = EngineSpecificationTool()

        for engine_type in ENGINE_CONFIGURATIONS.keys():
            result = spec_tool._run(engine_type=engine_type)
            data = json.loads(result)

            # Should not have errors
            assert "error" not in data, f"Error getting specs for {engine_type}"

            # Should have all required sections
            required_sections = ["engine_specifications", "electrical_requirements",
                               "cooling_specifications", "compartment_constraints", "integration_notes"]
            for section in required_sections:
                assert section in data, f"Missing {section} for {engine_type}"