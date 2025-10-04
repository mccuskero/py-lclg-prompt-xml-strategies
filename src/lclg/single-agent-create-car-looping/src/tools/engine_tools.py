"""Hardcoded tools for engine configuration and specifications."""

from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import Field
import json
import time
import sys
from pathlib import Path

# Add utils module to path for logging
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import ToolLogger


# Hardcoded engine configurations
ENGINE_CONFIGURATIONS = {
    "v6_gasoline": {
        "displacement": "3.5L",
        "cylinders": "6",
        "fuelType": "gasoline",
        "horsepower": "280",
        "@engineCode": "V6-350",
        "@manufacturer": "Generic Motors"
    },
    "v8_gasoline": {
        "displacement": "5.0L",
        "cylinders": "8",
        "fuelType": "gasoline",
        "horsepower": "420",
        "@engineCode": "V8-500",
        "@manufacturer": "Performance Motors"
    },
    "v4_turbo": {
        "displacement": "2.0L",
        "cylinders": "4",
        "fuelType": "gasoline",
        "horsepower": "250",
        "@engineCode": "T4-200",
        "@manufacturer": "Turbo Dynamics"
    },
    "electric": {
        "displacement": "N/A",
        "cylinders": "0",
        "fuelType": "electric",
        "horsepower": "300",
        "@engineCode": "EV-300",
        "@manufacturer": "Electric Dynamics"
    },
    "hybrid": {
        "displacement": "2.5L",
        "cylinders": "4",
        "fuelType": "hybrid",
        "horsepower": "200",
        "@engineCode": "HYB-250",
        "@manufacturer": "Hybrid Systems"
    },
    "diesel_v6": {
        "displacement": "3.0L",
        "cylinders": "6",
        "fuelType": "diesel",
        "horsepower": "240",
        "@engineCode": "D6-300",
        "@manufacturer": "Diesel Power"
    }
}

# Engine sizing and compartment data
ENGINE_COMPARTMENT_DATA = {
    "v6_gasoline": {"size": "medium", "cooling_requirements": "standard"},
    "v8_gasoline": {"size": "large", "cooling_requirements": "enhanced"},
    "v4_turbo": {"size": "small", "cooling_requirements": "enhanced"},
    "electric": {"size": "small", "cooling_requirements": "minimal"},
    "hybrid": {"size": "medium", "cooling_requirements": "dual"},
    "diesel_v6": {"size": "medium", "cooling_requirements": "heavy_duty"}
}


class EngineConfigurationTool(BaseTool):
    """Tool for configuring engine specifications based on requirements."""

    name: str = "configure_engine"
    description: str = ("Configure engine specifications based on vehicle type, "
                       "performance requirements, and fuel preferences. "
                       "Returns complete engineType JSON with all required fields.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = ToolLogger(self.name)

    @property
    def logger(self):
        """Get the logger instance."""
        return self._logger

    def _run(
        self,
        vehicle_type: str = "sedan",
        performance_level: str = "standard",
        fuel_preference: str = "gasoline",
        electric_capable: bool = False,
        **kwargs
    ) -> str:
        """Configure engine based on requirements.

        Args:
            vehicle_type: Type of vehicle (sedan, suv, truck, coupe, etc.)
            performance_level: Performance level (economy, standard, performance, sport)
            fuel_preference: Preferred fuel type (gasoline, diesel, electric, hybrid)
            electric_capable: Whether electric/hybrid capability is required

        Returns:
            JSON string with engine configuration
        """
        start_time = time.time()
        parameters = {
            "vehicle_type": vehicle_type,
            "performance_level": performance_level,
            "fuel_preference": fuel_preference,
            "electric_capable": electric_capable
        }

        self.logger.info(f"Engine configuration requested", **parameters)
        self.logger.debug(f"Starting engine configuration with parameters: {parameters}")

        try:
            # Determine engine type based on requirements
            self.logger.debug(f"Selecting engine type for vehicle_type={vehicle_type}, performance={performance_level}, fuel={fuel_preference}")
            engine_key = self._select_engine_type(
                vehicle_type, performance_level, fuel_preference, electric_capable
            )
            self.logger.debug(f"Selected engine key: {engine_key}")

            # Get the base configuration
            engine_config = ENGINE_CONFIGURATIONS.get(engine_key, ENGINE_CONFIGURATIONS["v6_gasoline"])
            self.logger.debug(f"Retrieved engine configuration: {engine_config}")

            # Add compartment sizing information for handoffs
            compartment_info = ENGINE_COMPARTMENT_DATA.get(engine_key, {"size": "medium", "cooling_requirements": "standard"})
            self.logger.debug(f"Compartment info: {compartment_info}")

            # Build complete configuration
            result = {
                "engineType": engine_config.copy(),
                "compartment_info": compartment_info,
                "selected_type": engine_key,
                "requirements_met": {
                    "vehicle_type": vehicle_type,
                    "performance_level": performance_level,
                    "fuel_preference": fuel_preference,
                    "electric_capable": electric_capable
                }
            }
            self.logger.debug(f"Built complete engine configuration result")

            execution_time = time.time() - start_time
            self.logger.log_execution(parameters, result, execution_time)
            self.logger.debug(f"Engine configuration completed in {execution_time:.3f}s")

            return json.dumps(result, indent=2)

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error_with_fallback(e, fallback_used=True)

            return json.dumps({
                "error": f"Engine configuration failed: {str(e)}",
                "fallback": ENGINE_CONFIGURATIONS["v6_gasoline"]
            })

    def _select_engine_type(
        self,
        vehicle_type: str,
        performance_level: str,
        fuel_preference: str,
        electric_capable: bool
    ) -> str:
        """Select appropriate engine type based on requirements."""

        # Electric/hybrid preference
        if electric_capable or fuel_preference == "electric":
            return "electric"
        if fuel_preference == "hybrid":
            return "hybrid"

        # Diesel preference
        if fuel_preference == "diesel":
            return "diesel_v6"

        # Performance-based selection for gasoline
        if performance_level in ["performance", "sport"]:
            if vehicle_type in ["truck", "suv"]:
                return "v8_gasoline"
            else:
                return "v4_turbo"

        # Vehicle type based selection
        if vehicle_type in ["truck", "suv"]:
            return "v8_gasoline" if performance_level == "performance" else "v6_gasoline"
        elif vehicle_type in ["coupe", "convertible"]:
            return "v4_turbo"
        else:  # sedan, hatchback, wagon
            return "v6_gasoline"


class EngineSpecificationTool(BaseTool):
    """Tool for getting detailed engine specifications and constraints."""

    name: str = "get_engine_specs"
    description: str = ("Get detailed engine specifications including electrical requirements, "
                       "compartment constraints, and cooling needs for integration with other components.")

    def _run(self, engine_type: str = "v6_gasoline", **kwargs) -> str:
        """Get detailed engine specifications.

        Args:
            engine_type: Type of engine configuration to analyze

        Returns:
            JSON string with detailed specifications
        """
        try:
            if engine_type not in ENGINE_CONFIGURATIONS:
                engine_type = "v6_gasoline"  # Default fallback

            engine_config = ENGINE_CONFIGURATIONS[engine_type]
            compartment_info = ENGINE_COMPARTMENT_DATA[engine_type]

            # Calculate electrical requirements
            electrical_reqs = self._calculate_electrical_requirements(engine_config)

            # Determine cooling requirements
            cooling_specs = self._get_cooling_specifications(engine_config, compartment_info)

            result = {
                "engine_specifications": engine_config,
                "electrical_requirements": electrical_reqs,
                "cooling_specifications": cooling_specs,
                "compartment_constraints": compartment_info,
                "integration_notes": self._get_integration_notes(engine_type)
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to get engine specifications: {str(e)}",
                "engine_type": engine_type
            })

    def _calculate_electrical_requirements(self, engine_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate electrical system requirements based on engine type."""
        fuel_type = engine_config.get("fuelType", "gasoline")
        horsepower = int(engine_config.get("horsepower", "200"))

        if fuel_type == "electric":
            return {
                "voltage_system": "high-voltage",
                "battery_capacity": "75kWh",
                "charging_capability": "DC_fast",
                "alternator_needed": False
            }
        elif fuel_type == "hybrid":
            return {
                "voltage_system": "hybrid",
                "battery_capacity": "1.8kWh",
                "charging_capability": "regenerative",
                "alternator_output": "150A"
            }
        else:
            # Calculate alternator size based on horsepower
            alternator_output = max(120, int(horsepower * 0.3))
            return {
                "voltage_system": "12V",
                "battery_capacity": "75Ah",
                "charging_capability": "standard",
                "alternator_output": f"{alternator_output}A"
            }

    def _get_cooling_specifications(self, engine_config: Dict[str, Any], compartment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get cooling system specifications."""
        fuel_type = engine_config.get("fuelType", "gasoline")
        cooling_req = compartment_info.get("cooling_requirements", "standard")

        cooling_specs = {
            "radiator_size": "standard",
            "fan_type": "electric",
            "coolant_capacity": "5L"
        }

        if fuel_type == "electric":
            cooling_specs.update({
                "battery_cooling": "liquid",
                "thermal_management": "active",
                "coolant_capacity": "3L"
            })
        elif cooling_req == "enhanced":
            cooling_specs.update({
                "radiator_size": "oversized",
                "fan_type": "dual_electric",
                "intercooler": "air_to_air"
            })
        elif cooling_req == "heavy_duty":
            cooling_specs.update({
                "radiator_size": "heavy_duty",
                "fan_type": "clutch_driven",
                "coolant_capacity": "8L"
            })

        return cooling_specs

    def _get_integration_notes(self, engine_type: str) -> Dict[str, str]:
        """Get integration notes for other agents."""
        notes = {
            "body_agent": f"Engine compartment size: {ENGINE_COMPARTMENT_DATA[engine_type]['size']}",
            "electrical_agent": f"Cooling requirements: {ENGINE_COMPARTMENT_DATA[engine_type]['cooling_requirements']}",
            "general": f"Selected engine type: {engine_type}"
        }

        if engine_type == "electric":
            notes["body_agent"] += " - No traditional grille needed"
            notes["electrical_agent"] += " - High-voltage battery system required"
        elif engine_type == "v8_gasoline":
            notes["body_agent"] += " - Requires larger hood and air intake"
            notes["tire_agent"] = "Performance tires recommended for V8 power"

        return notes