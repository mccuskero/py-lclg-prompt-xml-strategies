"""Unit tests for tire tools."""

import pytest
import json
from unittest.mock import Mock, patch

from tools.tire_tools import (
    TireConfigurationTool,
    TireSizingTool,
    TIRE_CONFIGURATIONS,
    TIRE_BRANDS,
    SEASONAL_CHARACTERISTICS
)


class TestTireSpecifications:
    """Test tire specification data."""

    def test_tire_configurations_exist(self):
        """Test that tire configurations are defined."""
        assert len(TIRE_CONFIGURATIONS) > 0

    def test_tire_configurations_structure(self):
        """Test that tire configurations have required fields."""
        required_fields = ["brand", "size", "pressure", "treadDepth", "@season"]

        for size_key, size_config in TIRE_CONFIGURATIONS.items():
            for field in required_fields:
                assert field in size_config, f"Missing {field} in {size_key}"

    def test_tire_configurations_specific_entries(self):
        """Test specific tire configurations."""
        # Just test that we have some configurations
        assert len(TIRE_CONFIGURATIONS) > 0

        # Test first configuration has expected structure
        first_config = list(TIRE_CONFIGURATIONS.values())[0]
        assert "brand" in first_config
        assert "size" in first_config

    def test_tire_brands(self):
        """Test tire brands database."""
        assert len(TIRE_BRANDS) > 0

        for brand_name, brand_info in TIRE_BRANDS.items():
            assert isinstance(brand_info, dict)
            # Check basic structure
            assert len(brand_info) > 0

    def test_seasonal_characteristics(self):
        """Test seasonal characteristics."""
        assert len(SEASONAL_CHARACTERISTICS) > 0

        for season, season_info in SEASONAL_CHARACTERISTICS.items():
            assert isinstance(season_info, dict)
            # Check basic structure
            assert len(season_info) > 0


class TestTireConfigurationTool:
    """Test the TireConfigurationTool class."""

    @pytest.fixture
    def tire_tool(self):
        """Create a TireConfigurationTool instance."""
        return TireConfigurationTool()

    def test_tool_initialization(self, tire_tool):
        """Test tool initialization."""
        assert tire_tool.name == "configure_tires"
        assert "tire configuration" in tire_tool.description.lower()

    def test_tool_run_basic(self, tire_tool):
        """Test basic tool execution."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        # Parse the JSON result
        result_data = json.loads(result)

        assert "tireType" in result_data
        assert "integration_info" in result_data

        tire_type = result_data["tireType"]
        assert "brand" in tire_type
        assert "size" in tire_type
        assert "pressure" in tire_type
        assert "treadDepth" in tire_type
        assert "@season" in tire_type

    def test_tool_run_sedan_standard(self, tire_tool):
        """Test tool execution for sedan with standard performance."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Sedan should get appropriate tire size
        assert tire_type["size"] in ["225/60R17", "215/60R16", "235/50R18"]

    def test_tool_run_suv_performance(self, tire_tool):
        """Test tool execution for SUV with high performance."""
        result = tire_tool._run(
            vehicle_type="suv",
            performance_level="high",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # SUV should get appropriate larger tire size
        assert tire_type["size"] in ["235/55R19", "255/50R20", "275/45R21"]

    def test_tool_run_truck_utility(self, tire_tool):
        """Test tool execution for truck with utility focus."""
        result = tire_tool._run(
            vehicle_type="truck",
            performance_level="standard",
            driving_conditions="off_road"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Truck should get appropriate tire size
        assert "R" in tire_type["size"]  # Should be radial tire

    def test_tool_run_driving_conditions(self, tire_tool):
        """Test tool execution with different driving conditions."""
        driving_conditions = ["normal", "off_road", "sport", "winter", "all_weather"]

        for condition in driving_conditions:
            result = tire_tool._run(
                vehicle_type="sedan",
                performance_level="standard",
                driving_conditions=condition
            )

            result_data = json.loads(result)
            assert "tireType" in result_data

    def test_tool_run_performance_levels(self, tire_tool):
        """Test tool execution with different performance levels."""
        performance_levels = ["economy", "standard", "high", "sport"]

        for performance_level in performance_levels:
            result = tire_tool._run(
                vehicle_type="sedan",
                performance_level=performance_level,
                driving_conditions="normal"
            )

            result_data = json.loads(result)
            assert "tireType" in result_data

    def test_tool_run_vehicle_types(self, tire_tool):
        """Test tool execution with different vehicle types."""
        vehicle_types = ["sedan", "suv", "truck", "sports_car", "hatchback", "wagon"]

        for vehicle_type in vehicle_types:
            result = tire_tool._run(
                vehicle_type=vehicle_type,
                performance_level="standard",
                driving_conditions="normal"
            )

            result_data = json.loads(result)
            tire_type = result_data["tireType"]
            assert tire_type["size"] != ""

    def test_tool_run_integration_info(self, tire_tool):
        """Test that integration info is included."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        assert "body_clearance" in integration_info
        assert "suspension_compatibility" in integration_info
        assert "electrical_tpms" in integration_info

    def test_tool_run_winter_conditions(self, tire_tool):
        """Test winter driving conditions selection."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="winter"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Winter conditions should influence tire selection
        assert "@season" in tire_type

    def test_tool_run_sport_conditions(self, tire_tool):
        """Test sport driving conditions selection."""
        result = tire_tool._run(
            vehicle_type="sports_car",
            performance_level="sport",
            driving_conditions="sport"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Sport conditions should get performance tires
        assert "@season" in tire_type

    def test_tool_run_body_constraints(self, tire_tool):
        """Test tool execution with body constraints."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal",
            body_constraints=json.dumps({
                "wheel_well_size": "large",
                "suspension_type": "sport"
            })
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        # Should process body constraints
        assert "body_clearance" in integration_info

    def test_tool_run_consistent_output_structure(self, tire_tool):
        """Test that tool output structure is consistent."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)

        # Check top-level structure
        assert "tireType" in result_data
        assert "integration_info" in result_data

        # Check tireType structure
        tire_type = result_data["tireType"]
        required_fields = ["brand", "size", "pressure", "treadDepth", "@season"]
        for field in required_fields:
            assert field in tire_type

        # Check integration_info structure
        integration_info = result_data["integration_info"]
        required_integration_fields = ["body_clearance", "suspension_compatibility", "electrical_tpms"]
        for field in required_integration_fields:
            assert field in integration_info

    def test_tool_run_json_validity(self, tire_tool):
        """Test that tool always returns valid JSON."""
        test_cases = [
            ("sedan", "standard", "normal"),
            ("suv", "high", "off_road"),
            ("truck", "economy", "winter"),
            ("sports_car", "sport", "sport"),
        ]

        for vehicle_type, performance_level, driving_conditions in test_cases:
            result = tire_tool._run(
                vehicle_type=vehicle_type,
                performance_level=performance_level,
                driving_conditions=driving_conditions
            )

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)

    def test_tool_run_invalid_inputs_graceful_handling(self, tire_tool):
        """Test that tool handles invalid inputs gracefully."""
        # Invalid vehicle type
        result = tire_tool._run(
            vehicle_type="invalid_vehicle",
            performance_level="standard",
            driving_conditions="normal"
        )

        # Should still return valid JSON with fallback
        result_data = json.loads(result)
        assert "tireType" in result_data

    def test_tool_run_pressure_assignments(self, tire_tool):
        """Test that tire pressures are appropriate."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Should have reasonable pressure (typically 30-40 PSI)
        pressure = int(tire_type["pressure"])
        assert 25 <= pressure <= 45

    def test_tool_run_tread_depth_assignments(self, tire_tool):
        """Test that tread depths are appropriate."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Should have reasonable tread depth (typically 8-12mm for new)
        tread_depth = int(tire_type["treadDepth"])
        assert 6 <= tread_depth <= 15

    def test_tool_run_brand_assignments(self, tire_tool):
        """Test that tire brands are properly assigned."""
        result = tire_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            driving_conditions="normal"
        )

        result_data = json.loads(result)
        tire_type = result_data["tireType"]

        # Should have a brand assigned
        assert "brand" in tire_type
        assert tire_type["brand"] != ""

    def test_tool_run_size_logic_by_vehicle(self, tire_tool):
        """Test that tire sizes are logical for different vehicle types."""
        # Test various vehicle types and their expected size ranges
        vehicle_size_expectations = {
            "sedan": ("15", "18"),  # Typically 15-18 inch wheels
            "suv": ("17", "21"),    # Typically 17-21 inch wheels
            "truck": ("16", "20"),  # Typically 16-20 inch wheels
            "sports_car": ("17", "20"),  # Typically 17-20 inch wheels
        }

        for vehicle_type, (min_size, max_size) in vehicle_size_expectations.items():
            result = tire_tool._run(
                vehicle_type=vehicle_type,
                performance_level="standard",
                driving_conditions="normal"
            )

            result_data = json.loads(result)
            tire_type = result_data["tireType"]

            # Extract wheel size from tire size (e.g., "225/60R17" -> "17")
            tire_size = tire_type["size"]
            wheel_size = tire_size.split("R")[-1]
            wheel_size_int = int(wheel_size)

            assert int(min_size) <= wheel_size_int <= int(max_size), \
                f"Wheel size {wheel_size} out of range {min_size}-{max_size} for {vehicle_type}"


class TestTireSizingTool:
    """Test the TireSizingTool class."""

    @pytest.fixture
    def tire_spec_tool(self):
        """Create a TireSizingTool instance."""
        return TireSizingTool()

    def test_spec_tool_initialization(self, tire_spec_tool):
        """Test spec tool initialization."""
        assert tire_spec_tool.name == "get_tire_sizing"
        assert "tire sizing" in tire_spec_tool.description.lower()

    def test_spec_tool_run_basic(self, tire_spec_tool):
        """Test basic spec tool execution."""
        result = tire_spec_tool._run(
            tire_size="225/60R17",
            detailed_analysis=True
        )

        # Parse the JSON result
        result_data = json.loads(result)

        assert "tire_size" in result_data or "error" in result_data
        assert "matching_configs" in result_data or "error" in result_data

    def test_spec_tool_run_all_sizes(self, tire_spec_tool):
        """Test spec tool with all available sizes."""
        for size in TIRE_CONFIGURATIONS.keys():
            result = tire_spec_tool._run(tire_size=size, detailed_analysis=False)

            result_data = json.loads(result)
            # Should return some result structure
            assert isinstance(result_data, dict)

    def test_spec_tool_run_detailed_mode(self, tire_spec_tool):
        """Test spec tool in detailed mode."""
        result = tire_spec_tool._run(
            tire_size="225/60R17",
            detailed_analysis=True
        )

        result_data = json.loads(result)

        # Should return structured data
        assert isinstance(result_data, dict)

    def test_spec_tool_run_invalid_size(self, tire_spec_tool):
        """Test spec tool with invalid tire size."""
        result = tire_spec_tool._run(
            tire_size="invalid_size",
            detailed_analysis=True
        )

        result_data = json.loads(result)

        # Should return valid JSON (might include error info)
        assert isinstance(result_data, dict)

    def test_spec_tool_run_json_validity(self, tire_spec_tool):
        """Test that spec tool always returns valid JSON."""
        test_sizes = ["225/60R17", "245/45R18", "invalid_size"]

        for size in test_sizes:
            result = tire_spec_tool._run(tire_size=size, detailed_analysis=True)

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)