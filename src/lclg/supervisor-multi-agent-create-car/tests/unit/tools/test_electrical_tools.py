"""Unit tests for electrical tools."""

import pytest
import json
from unittest.mock import Mock, patch

from tools.electrical_tools import (
    ElectricalConfigurationTool,
    ElectricalSystemTool,
    ELECTRICAL_CONFIGURATIONS,
    ECU_CAPABILITIES,
    WIRING_HARNESS_SPECS
)


class TestElectricalConfigurations:
    """Test electrical configuration data."""

    def test_electrical_configurations_exist(self):
        """Test that electrical configurations are defined."""
        assert len(ELECTRICAL_CONFIGURATIONS) > 0

    def test_electrical_configurations_structure(self):
        """Test that electrical configurations have required fields."""
        required_fields = ["batteryVoltage", "alternatorOutput", "wiringHarness", "ecuVersion", "@systemType"]

        for config_name, config in ELECTRICAL_CONFIGURATIONS.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {config_name}"

    def test_electrical_configurations_specific_entries(self):
        """Test specific electrical configurations."""
        # Just test that we have some configurations
        assert len(ELECTRICAL_CONFIGURATIONS) > 0

        # Test first configuration has expected structure
        first_config = list(ELECTRICAL_CONFIGURATIONS.values())[0]
        assert "batteryVoltage" in first_config
        assert "@systemType" in first_config

    def test_ecu_capabilities(self):
        """Test ECU capabilities database."""
        assert len(ECU_CAPABILITIES) > 0

        for version_name, version_info in ECU_CAPABILITIES.items():
            assert isinstance(version_info, dict)
            # Check basic structure
            assert len(version_info) > 0

    def test_wiring_harness_specs(self):
        """Test wiring harness specifications."""
        assert len(WIRING_HARNESS_SPECS) > 0

        for harness_name, harness_info in WIRING_HARNESS_SPECS.items():
            assert isinstance(harness_info, dict)
            # Check basic structure
            assert len(harness_info) > 0


class TestElectricalConfigurationTool:
    """Test the ElectricalConfigurationTool class."""

    @pytest.fixture
    def electrical_tool(self):
        """Create an ElectricalConfigurationTool instance."""
        return ElectricalConfigurationTool()

    def test_tool_initialization(self, electrical_tool):
        """Test tool initialization."""
        assert electrical_tool.name == "configure_electrical"
        assert "electrical configuration" in electrical_tool.description.lower()

    def test_tool_run_basic(self, electrical_tool):
        """Test basic tool execution."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        # Parse the JSON result
        result_data = json.loads(result)

        assert "electricalType" in result_data
        assert "integration_info" in result_data

        electrical_type = result_data["electricalType"]
        assert "batteryVoltage" in electrical_type
        assert "alternatorOutput" in electrical_type
        assert "wiringHarness" in electrical_type
        assert "ecuVersion" in electrical_type
        assert "@systemType" in electrical_type

    def test_tool_run_sedan_standard(self, electrical_tool):
        """Test tool execution for sedan with standard load."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        assert electrical_type["batteryVoltage"] == "12"
        assert int(electrical_type["alternatorOutput"]) >= 100

    def test_tool_run_suv_high_load(self, electrical_tool):
        """Test tool execution for SUV with high electrical load."""
        result = electrical_tool._run(
            vehicle_type="suv",
            electrical_load="high",
            feature_level="premium"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # High load should get more powerful alternator
        alternator_output = int(electrical_type["alternatorOutput"])
        assert alternator_output >= 140

    def test_tool_run_electric_vehicle(self, electrical_tool):
        """Test tool execution for electric vehicle."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="electric",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Electric vehicle should have appropriate system type
        assert electrical_type["@systemType"] in ["electric", "hybrid"]

    def test_tool_run_hybrid_vehicle(self, electrical_tool):
        """Test tool execution for hybrid vehicle."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="hybrid",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        assert electrical_type["@systemType"] == "hybrid"

    def test_tool_run_different_electrical_loads(self, electrical_tool):
        """Test tool execution with different electrical loads."""
        electrical_loads = ["low", "standard", "high", "hybrid", "electric"]

        for load in electrical_loads:
            result = electrical_tool._run(
                vehicle_type="sedan",
                electrical_load=load,
                feature_level="standard"
            )

            result_data = json.loads(result)
            assert "electricalType" in result_data

    def test_tool_run_different_feature_levels(self, electrical_tool):
        """Test tool execution with different feature levels."""
        feature_levels = ["basic", "standard", "premium", "luxury"]

        for feature_level in feature_levels:
            result = electrical_tool._run(
                vehicle_type="sedan",
                electrical_load="standard",
                feature_level=feature_level
            )

            result_data = json.loads(result)
            assert "electricalType" in result_data

    def test_tool_run_different_vehicle_types(self, electrical_tool):
        """Test tool execution with different vehicle types."""
        vehicle_types = ["sedan", "suv", "truck", "sports_car", "hatchback"]

        for vehicle_type in vehicle_types:
            result = electrical_tool._run(
                vehicle_type=vehicle_type,
                electrical_load="standard",
                feature_level="standard"
            )

            result_data = json.loads(result)
            electrical_type = result_data["electricalType"]
            assert electrical_type["batteryVoltage"] in ["12", "24", "48"]

    def test_tool_run_integration_info(self, electrical_tool):
        """Test that integration info is included."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        assert "engine_integration" in integration_info
        assert "body_routing" in integration_info
        assert "tire_sensors" in integration_info

    def test_tool_run_engine_constraints(self, electrical_tool):
        """Test tool execution with engine constraints."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard",
            engine_constraints=json.dumps({
                "alternator_requirements": "high",
                "fuel_type": "gasoline"
            })
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        # Should process engine constraints
        assert "engine_integration" in integration_info

    def test_tool_run_body_constraints(self, electrical_tool):
        """Test tool execution with body constraints."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard",
            body_constraints=json.dumps({
                "wiring_complexity": "standard",
                "material": "steel"
            })
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        # Should process body constraints
        assert "body_routing" in integration_info

    def test_tool_run_premium_features(self, electrical_tool):
        """Test premium feature configurations."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="high",
            feature_level="luxury"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Luxury features might require higher electrical capacity
        alternator_output = int(electrical_type["alternatorOutput"])
        assert alternator_output >= 120

    def test_tool_run_economy_configuration(self, electrical_tool):
        """Test economy electrical configuration."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="low",
            feature_level="basic"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Economy should still have all required fields
        assert "batteryVoltage" in electrical_type
        assert "alternatorOutput" in electrical_type
        assert "wiringHarness" in electrical_type
        assert "ecuVersion" in electrical_type
        assert "@systemType" in electrical_type

    def test_tool_run_consistent_output_structure(self, electrical_tool):
        """Test that tool output structure is consistent."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)

        # Check top-level structure
        assert "electricalType" in result_data
        assert "integration_info" in result_data

        # Check electricalType structure
        electrical_type = result_data["electricalType"]
        required_fields = ["batteryVoltage", "alternatorOutput", "wiringHarness", "ecuVersion", "@systemType"]
        for field in required_fields:
            assert field in electrical_type

        # Check integration_info structure
        integration_info = result_data["integration_info"]
        required_integration_fields = ["engine_integration", "body_routing", "tire_sensors"]
        for field in required_integration_fields:
            assert field in integration_info

    def test_tool_run_json_validity(self, electrical_tool):
        """Test that tool always returns valid JSON."""
        test_cases = [
            ("sedan", "standard", "standard"),
            ("suv", "high", "premium"),
            ("truck", "low", "basic"),
            ("sports_car", "high", "luxury"),
        ]

        for vehicle_type, electrical_load, feature_level in test_cases:
            result = electrical_tool._run(
                vehicle_type=vehicle_type,
                electrical_load=electrical_load,
                feature_level=feature_level
            )

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)

    def test_tool_run_invalid_inputs_graceful_handling(self, electrical_tool):
        """Test that tool handles invalid inputs gracefully."""
        # Invalid vehicle type
        result = electrical_tool._run(
            vehicle_type="invalid_vehicle",
            electrical_load="standard",
            feature_level="standard"
        )

        # Should still return valid JSON with fallback
        result_data = json.loads(result)
        assert "electricalType" in result_data

    def test_tool_run_battery_voltage_logic(self, electrical_tool):
        """Test battery voltage selection logic."""
        # Most vehicles should use 12V system
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Standard vehicles typically use 12V
        assert electrical_type["batteryVoltage"] in ["12", "24", "48"]

    def test_tool_run_alternator_scaling(self, electrical_tool):
        """Test that alternator output scales with electrical load."""
        # Get alternator outputs for different loads
        results = {}
        for load in ["low", "standard", "high"]:
            result = electrical_tool._run(
                vehicle_type="sedan",
                electrical_load=load,
                feature_level="standard"
            )
            result_data = json.loads(result)
            results[load] = int(result_data["electricalType"]["alternatorOutput"])

        # Higher loads should generally have higher alternator output
        if "low" in results and "high" in results:
            assert results["low"] <= results["high"]

    def test_tool_run_ecu_version_assignment(self, electrical_tool):
        """Test ECU version assignment."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Should have an ECU version assigned
        assert "ecuVersion" in electrical_type
        assert electrical_type["ecuVersion"] != ""

    def test_tool_run_wiring_harness_assignment(self, electrical_tool):
        """Test wiring harness assignment."""
        result = electrical_tool._run(
            vehicle_type="sedan",
            electrical_load="standard",
            feature_level="standard"
        )

        result_data = json.loads(result)
        electrical_type = result_data["electricalType"]

        # Should have a wiring harness assigned
        assert "wiringHarness" in electrical_type
        assert electrical_type["wiringHarness"] != ""


class TestElectricalSystemTool:
    """Test the ElectricalSystemTool class."""

    @pytest.fixture
    def electrical_spec_tool(self):
        """Create an ElectricalSystemTool instance."""
        return ElectricalSystemTool()

    def test_spec_tool_initialization(self, electrical_spec_tool):
        """Test spec tool initialization."""
        assert electrical_spec_tool.name == "get_electrical_system_info"
        assert "electrical system" in electrical_spec_tool.description.lower()

    def test_spec_tool_run_basic(self, electrical_spec_tool):
        """Test basic spec tool execution."""
        result = electrical_spec_tool._run(
            system_type="12V",
            detailed_analysis=True
        )

        # Parse the JSON result
        result_data = json.loads(result)

        # Should return structured electrical system data
        assert isinstance(result_data, dict)

    def test_spec_tool_run_all_systems(self, electrical_spec_tool):
        """Test spec tool with all available system types."""
        system_types = ["12V", "24V", "hybrid", "high-voltage"]

        for system_type in system_types:
            result = electrical_spec_tool._run(system_type=system_type, detailed_analysis=False)

            result_data = json.loads(result)
            assert isinstance(result_data, dict)

    def test_spec_tool_run_detailed_mode(self, electrical_spec_tool):
        """Test spec tool in detailed mode."""
        result = electrical_spec_tool._run(
            system_type="12V",
            detailed_analysis=True
        )

        result_data = json.loads(result)

        # Should return structured data
        assert isinstance(result_data, dict)

    def test_spec_tool_run_invalid_system(self, electrical_spec_tool):
        """Test spec tool with invalid system type."""
        result = electrical_spec_tool._run(
            system_type="invalid_system",
            detailed_analysis=True
        )

        result_data = json.loads(result)

        # Should return valid JSON (might include error info)
        assert isinstance(result_data, dict)

    def test_spec_tool_run_json_validity(self, electrical_spec_tool):
        """Test that spec tool always returns valid JSON."""
        test_systems = ["12V", "24V", "hybrid", "invalid_system"]

        for system_type in test_systems:
            result = electrical_spec_tool._run(system_type=system_type, detailed_analysis=True)

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)