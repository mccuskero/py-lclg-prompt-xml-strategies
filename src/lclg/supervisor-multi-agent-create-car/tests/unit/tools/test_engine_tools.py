"""Unit tests for engine tools."""

import pytest
import json
from unittest.mock import Mock, patch

from tools.engine_tools import (
    EngineConfigurationTool,
    ENGINE_CONFIGURATIONS,
    ENGINE_COMPARTMENT_DATA
)


class TestEngineConfigurations:
    """Test engine configuration data."""

    def test_engine_configurations_exist(self):
        """Test that engine configurations are defined."""
        assert len(ENGINE_CONFIGURATIONS) > 0

    def test_engine_configurations_structure(self):
        """Test that engine configurations have required fields."""
        required_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode"]

        for config_name, config in ENGINE_CONFIGURATIONS.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {config_name}"

    def test_engine_configurations_specific_entries(self):
        """Test specific engine configurations."""
        # Test v6_gasoline
        assert "v6_gasoline" in ENGINE_CONFIGURATIONS
        v6_config = ENGINE_CONFIGURATIONS["v6_gasoline"]
        assert v6_config["cylinders"] == "6"
        assert v6_config["fuelType"] == "gasoline"

        # Test electric
        assert "electric" in ENGINE_CONFIGURATIONS
        electric_config = ENGINE_CONFIGURATIONS["electric"]
        assert electric_config["fuelType"] == "electric"

    def test_engine_compartment_data(self):
        """Test engine compartment data."""
        assert len(ENGINE_COMPARTMENT_DATA) > 0

        for engine_type, compartment_info in ENGINE_COMPARTMENT_DATA.items():
            assert isinstance(compartment_info, dict)
            # Check basic structure
            assert len(compartment_info) > 0


class TestEngineConfigurationTool:
    """Test the EngineConfigurationTool class."""

    @pytest.fixture
    def engine_tool(self):
        """Create an EngineConfigurationTool instance."""
        return EngineConfigurationTool()

    def test_tool_initialization(self, engine_tool):
        """Test tool initialization."""
        assert engine_tool.name == "configure_engine"
        assert "engine configuration" in engine_tool.description.lower()

    def test_tool_run_basic(self, engine_tool):
        """Test basic tool execution."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        # Parse the JSON result
        result_data = json.loads(result)

        assert "engineType" in result_data
        assert "compartment_info" in result_data

        engine_type = result_data["engineType"]
        assert "displacement" in engine_type
        assert "cylinders" in engine_type
        assert "fuelType" in engine_type
        assert "horsepower" in engine_type
        assert "@engineCode" in engine_type

    def test_tool_run_sedan_gasoline(self, engine_tool):
        """Test tool execution for sedan with gasoline preference."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)
        engine_type = result_data["engineType"]

        assert engine_type["fuelType"] == "gasoline"
        # Should get a reasonable engine for sedan
        assert engine_type["cylinders"] in ["4", "6", "8"]

    def test_tool_run_suv_performance(self, engine_tool):
        """Test tool execution for SUV with high performance."""
        result = engine_tool._run(
            vehicle_type="suv",
            performance_level="high",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)
        engine_type = result_data["engineType"]

        assert engine_type["fuelType"] == "gasoline"
        # High performance SUV should get more powerful engine
        horsepower = int(engine_type["horsepower"])
        assert horsepower > 200

    def test_tool_run_electric_preference(self, engine_tool):
        """Test tool execution with electric preference."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="electric"
        )

        result_data = json.loads(result)
        engine_type = result_data["engineType"]

        assert engine_type["fuelType"] == "electric"

    def test_tool_run_hybrid_preference(self, engine_tool):
        """Test tool execution with hybrid preference."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="hybrid"
        )

        result_data = json.loads(result)
        engine_type = result_data["engineType"]

        assert engine_type["fuelType"] == "hybrid"

    def test_tool_run_truck_high_performance(self, engine_tool):
        """Test tool execution for truck with high performance."""
        result = engine_tool._run(
            vehicle_type="truck",
            performance_level="high",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)
        engine_type = result_data["engineType"]

        # Truck should get powerful engine
        cylinders = int(engine_type["cylinders"])
        assert cylinders >= 6

        horsepower = int(engine_type["horsepower"])
        assert horsepower > 250

    def test_tool_run_compartment_info(self, engine_tool):
        """Test that compartment info is included."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)
        compartment_info = result_data["compartment_info"]

        assert "size" in compartment_info
        assert "cooling_requirements" in compartment_info
        assert "constraints" in compartment_info

    def test_tool_run_different_vehicle_types(self, engine_tool):
        """Test tool execution with different vehicle types."""
        vehicle_types = ["sedan", "suv", "truck", "sports_car", "hatchback"]

        for vehicle_type in vehicle_types:
            result = engine_tool._run(
                vehicle_type=vehicle_type,
                performance_level="standard",
                fuel_preference="gasoline"
            )

            result_data = json.loads(result)
            assert "engineType" in result_data
            assert "compartment_info" in result_data

    def test_tool_run_different_performance_levels(self, engine_tool):
        """Test tool execution with different performance levels."""
        performance_levels = ["economy", "standard", "high", "sport"]

        for performance_level in performance_levels:
            result = engine_tool._run(
                vehicle_type="sedan",
                performance_level=performance_level,
                fuel_preference="gasoline"
            )

            result_data = json.loads(result)
            assert "engineType" in result_data

    def test_tool_run_all_fuel_preferences(self, engine_tool):
        """Test tool execution with all fuel preferences."""
        fuel_preferences = ["gasoline", "diesel", "electric", "hybrid", "hydrogen"]

        for fuel_preference in fuel_preferences:
            result = engine_tool._run(
                vehicle_type="sedan",
                performance_level="standard",
                fuel_preference=fuel_preference
            )

            result_data = json.loads(result)
            engine_type = result_data["engineType"]

            # Should respect fuel preference
            assert engine_type["fuelType"] == fuel_preference

    def test_tool_run_invalid_inputs_graceful_handling(self, engine_tool):
        """Test that tool handles invalid inputs gracefully."""
        # Invalid vehicle type
        result = engine_tool._run(
            vehicle_type="invalid_vehicle",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        # Should still return valid JSON
        result_data = json.loads(result)
        assert "engineType" in result_data

    def test_tool_run_json_validity(self, engine_tool):
        """Test that tool always returns valid JSON."""
        test_cases = [
            ("sedan", "standard", "gasoline"),
            ("suv", "high", "electric"),
            ("truck", "economy", "diesel"),
            ("sports_car", "sport", "hybrid"),
        ]

        for vehicle_type, performance_level, fuel_preference in test_cases:
            result = engine_tool._run(
                vehicle_type=vehicle_type,
                performance_level=performance_level,
                fuel_preference=fuel_preference
            )

            # Should be valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, dict)

    def test_tool_run_consistent_output_structure(self, engine_tool):
        """Test that tool output structure is consistent."""
        result = engine_tool._run(
            vehicle_type="sedan",
            performance_level="standard",
            fuel_preference="gasoline"
        )

        result_data = json.loads(result)

        # Check top-level structure
        assert "engineType" in result_data
        assert "compartment_info" in result_data

        # Check engineType structure
        engine_type = result_data["engineType"]
        required_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode"]
        for field in required_fields:
            assert field in engine_type

        # Check compartment_info structure
        compartment_info = result_data["compartment_info"]
        required_compartment_fields = ["size", "cooling_requirements", "constraints"]
        for field in required_compartment_fields:
            assert field in compartment_info

    def test_tool_run_performance_scaling(self, engine_tool):
        """Test that performance levels affect engine power appropriately."""
        # Get engines for different performance levels
        results = {}
        for performance_level in ["economy", "standard", "high", "sport"]:
            result = engine_tool._run(
                vehicle_type="sedan",
                performance_level=performance_level,
                fuel_preference="gasoline"
            )
            result_data = json.loads(result)
            results[performance_level] = int(result_data["engineType"]["horsepower"])

        # Economy should have less power than sport
        if "economy" in results and "sport" in results:
            assert results["economy"] <= results["sport"]