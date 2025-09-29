"""Unit tests for body tools."""

import pytest
import json
from unittest.mock import Mock, patch

from tools.body_tools import (
    BodyConfigurationTool,
    BODY_STYLE_CONFIGURATIONS,
    COLOR_DATABASE,
    MATERIAL_PROPERTIES
)


class TestBodyConfigurations:
    """Test body configuration data."""

    def test_body_style_configurations_exist(self):
        """Test that body style configurations are defined."""
        assert len(BODY_STYLE_CONFIGURATIONS) > 0

    def test_body_style_configurations_structure(self):
        """Test that body configurations have required fields."""
        required_fields = ["style", "doors", "material", "color"]

        for style_name, style_config in BODY_STYLE_CONFIGURATIONS.items():
            for field in required_fields:
                assert field in style_config, f"Missing {field} in {style_name}"

    def test_body_style_configurations_specific_entries(self):
        """Test specific body style configurations."""
        # Test sedan
        assert "sedan" in BODY_STYLE_CONFIGURATIONS
        sedan_config = BODY_STYLE_CONFIGURATIONS["sedan"]
        assert sedan_config["style"] == "sedan"
        assert sedan_config["doors"] == "4"

        # Test suv
        assert "suv" in BODY_STYLE_CONFIGURATIONS
        suv_config = BODY_STYLE_CONFIGURATIONS["suv"]
        assert suv_config["style"] == "suv"

    def test_color_database(self):
        """Test color database."""
        assert len(COLOR_DATABASE) > 0

        for color_name, color_info in COLOR_DATABASE.items():
            assert isinstance(color_info, dict)
            # Check basic structure
            assert len(color_info) > 0

    def test_material_properties(self):
        """Test material properties."""
        assert len(MATERIAL_PROPERTIES) > 0

        for material_name, material_info in MATERIAL_PROPERTIES.items():
            assert isinstance(material_info, dict)
            # Check basic structure
            assert len(material_info) > 0


class TestBodyConfigurationTool:
    """Test the BodyConfigurationTool class."""

    @pytest.fixture
    def body_tool(self):
        """Create a BodyConfigurationTool instance."""
        return BodyConfigurationTool()

    def test_tool_initialization(self, body_tool):
        """Test tool initialization."""
        assert body_tool.name == "configure_body"
        assert "body configuration" in body_tool.description.lower()

    def test_tool_run_basic(self, body_tool):
        """Test basic tool execution."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        # Parse the JSON result
        result_data = json.loads(result)

        assert "bodyType" in result_data
        assert "integration_info" in result_data

        body_type = result_data["bodyType"]
        assert "style" in body_type
        assert "doors" in body_type
        assert "material" in body_type
        assert "color" in body_type

    def test_tool_run_sedan_style(self, body_tool):
        """Test tool execution for sedan style."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        assert body_type["style"] == "sedan"
        assert body_type["doors"] == "4"

    def test_tool_run_suv_style(self, body_tool):
        """Test tool execution for SUV style."""
        result = body_tool._run(
            style="suv",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        assert body_type["style"] == "suv"

    def test_tool_run_sports_car_style(self, body_tool):
        """Test tool execution for sports car style."""
        result = body_tool._run(
            style="sports_car",
            performance_level="high",
            customization_level="premium"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        assert body_type["style"] == "sports_car"
        assert body_type["doors"] == "2"  # Sports cars typically have 2 doors

    def test_tool_run_performance_levels(self, body_tool):
        """Test tool execution with different performance levels."""
        performance_levels = ["economy", "standard", "high", "sport"]

        for performance_level in performance_levels:
            result = body_tool._run(
                style="sedan",
                performance_level=performance_level,
                customization_level="standard"
            )

            result_data = json.loads(result)
            assert "bodyType" in result_data

    def test_tool_run_customization_levels(self, body_tool):
        """Test tool execution with different customization levels."""
        customization_levels = ["basic", "standard", "premium", "luxury"]

        for customization_level in customization_levels:
            result = body_tool._run(
                style="sedan",
                performance_level="standard",
                customization_level=customization_level
            )

            result_data = json.loads(result)
            assert "bodyType" in result_data

    def test_tool_run_integration_info(self, body_tool):
        """Test that integration info is included."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        assert "engine_accommodation" in integration_info
        assert "electrical_routing" in integration_info
        assert "aerodynamics" in integration_info

    def test_tool_run_all_styles(self, body_tool):
        """Test tool execution with all available styles."""
        styles = ["sedan", "suv", "truck", "sports_car", "hatchback", "convertible", "wagon"]

        for style in styles:
            result = body_tool._run(
                style=style,
                performance_level="standard",
                customization_level="standard"
            )

            result_data = json.loads(result)
            body_type = result_data["bodyType"]
            assert body_type["style"] == style

    def test_tool_run_color_assignment(self, body_tool):
        """Test that colors are properly assigned."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        # Should have a color assigned
        assert "color" in body_type
        assert body_type["color"] != ""

        # Should have paint code
        if "@paintCode" in body_type:
            assert body_type["@paintCode"] != ""

    def test_tool_run_material_assignment(self, body_tool):
        """Test that materials are properly assigned."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        # Should have a material assigned
        assert "material" in body_type
        assert body_type["material"] != ""

    def test_tool_run_luxury_customization(self, body_tool):
        """Test luxury customization features."""
        result = body_tool._run(
            style="sedan",
            performance_level="high",
            customization_level="luxury"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        # Luxury customization might include special features
        # The tool should handle this appropriately
        assert "style" in body_type
        assert "material" in body_type

    def test_tool_run_economy_performance(self, body_tool):
        """Test economy performance configuration."""
        result = body_tool._run(
            style="sedan",
            performance_level="economy",
            customization_level="basic"
        )

        result_data = json.loads(result)
        body_type = result_data["bodyType"]

        # Economy should still have all required fields
        assert "style" in body_type
        assert "doors" in body_type
        assert "material" in body_type
        assert "color" in body_type

    def test_tool_run_with_engine_constraints(self, body_tool):
        """Test tool execution with engine constraints."""
        # This would simulate receiving constraints from EngineAgent
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard",
            engine_constraints=json.dumps({
                "compartment_size": "large",
                "cooling_requirements": "high"
            })
        )

        result_data = json.loads(result)
        integration_info = result_data["integration_info"]

        # Should process engine constraints
        assert "engine_accommodation" in integration_info

    def test_tool_run_json_validity(self, body_tool):
        """Test that tool always returns valid JSON."""
        test_cases = [
            ("sedan", "standard", "standard"),
            ("suv", "high", "premium"),
            ("truck", "economy", "basic"),
            ("sports_car", "sport", "luxury"),
        ]

        for style, performance_level, customization_level in test_cases:
            result = body_tool._run(
                style=style,
                performance_level=performance_level,
                customization_level=customization_level
            )

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)

    def test_tool_run_consistent_output_structure(self, body_tool):
        """Test that tool output structure is consistent."""
        result = body_tool._run(
            style="sedan",
            performance_level="standard",
            customization_level="standard"
        )

        result_data = json.loads(result)

        # Check top-level structure
        assert "bodyType" in result_data
        assert "integration_info" in result_data

        # Check bodyType structure
        body_type = result_data["bodyType"]
        required_fields = ["style", "doors", "material", "color"]
        for field in required_fields:
            assert field in body_type

        # Check integration_info structure
        integration_info = result_data["integration_info"]
        required_integration_fields = ["engine_accommodation", "electrical_routing", "aerodynamics"]
        for field in required_integration_fields:
            assert field in integration_info

    def test_tool_run_door_count_logic(self, body_tool):
        """Test that door count is logical for different styles."""
        # Test specific styles with expected door counts
        style_door_mapping = {
            "sedan": "4",
            "sports_car": "2",
            "suv": ["4", "5"],  # SUVs can vary
            "truck": ["2", "4"],  # Trucks can vary
        }

        for style, expected_doors in style_door_mapping.items():
            result = body_tool._run(
                style=style,
                performance_level="standard",
                customization_level="standard"
            )

            result_data = json.loads(result)
            body_type = result_data["bodyType"]

            if isinstance(expected_doors, list):
                assert body_type["doors"] in expected_doors
            else:
                assert body_type["doors"] == expected_doors

    def test_tool_run_invalid_style_handling(self, body_tool):
        """Test handling of invalid style input."""
        result = body_tool._run(
            style="invalid_style",
            performance_level="standard",
            customization_level="standard"
        )

        # Should still return valid JSON with fallback
        result_data = json.loads(result)
        assert "bodyType" in result_data