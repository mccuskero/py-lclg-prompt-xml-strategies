"""Hardcoded tools for electrical system configuration."""

from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import Field
import json


# Hardcoded electrical system configurations
ELECTRICAL_CONFIGURATIONS = {
    "standard_12v": {
        "batteryVoltage": "12V",
        "alternatorOutput": "120A",
        "wiringHarness": "standard_copper",
        "ecuVersion": "ECU-2024-STD",
        "@systemType": "12V",
        "@hybridCapable": False
    },
    "performance_12v": {
        "batteryVoltage": "12V",
        "alternatorOutput": "180A",
        "wiringHarness": "heavy_duty_copper",
        "ecuVersion": "ECU-2024-PERF",
        "@systemType": "12V",
        "@hybridCapable": False
    },
    "hybrid_system": {
        "batteryVoltage": "12V/320V",
        "alternatorOutput": "150A",
        "wiringHarness": "hybrid_shielded",
        "ecuVersion": "ECU-2024-HYB",
        "@systemType": "hybrid",
        "@hybridCapable": True
    },
    "electric_system": {
        "batteryVoltage": "400V",
        "alternatorOutput": "N/A",
        "wiringHarness": "high_voltage_shielded",
        "ecuVersion": "ECU-2024-EV",
        "@systemType": "high-voltage",
        "@hybridCapable": False
    },
    "truck_24v": {
        "batteryVoltage": "24V",
        "alternatorOutput": "200A",
        "wiringHarness": "heavy_duty_copper",
        "ecuVersion": "ECU-2024-TRUCK",
        "@systemType": "24V",
        "@hybridCapable": False
    },
    "luxury_12v": {
        "batteryVoltage": "12V",
        "alternatorOutput": "160A",
        "wiringHarness": "premium_copper",
        "ecuVersion": "ECU-2024-LUX",
        "@systemType": "12V",
        "@hybridCapable": False
    }
}

# Electrical load requirements by component
ELECTRICAL_LOADS = {
    "engine_types": {
        "v6_gasoline": {"starter_load": "2.5kW", "ignition_load": "300W", "fuel_system": "200W"},
        "v8_gasoline": {"starter_load": "3.5kW", "ignition_load": "400W", "fuel_system": "250W"},
        "v4_turbo": {"starter_load": "2.0kW", "ignition_load": "250W", "fuel_system": "300W"},
        "electric": {"motor_controller": "200kW", "charging_system": "11kW", "dc_converter": "3kW"},
        "hybrid": {"motor_controller": "60kW", "charging_system": "3.3kW", "dc_converter": "1.5kW"},
        "diesel_v6": {"starter_load": "4.0kW", "glow_plugs": "1.2kW", "fuel_system": "400W"}
    },
    "body_features": {
        "basic": {"lighting": "500W", "climate": "2kW", "infotainment": "200W"},
        "premium": {"lighting": "800W", "climate": "3kW", "infotainment": "500W"},
        "luxury": {"lighting": "1200W", "climate": "4kW", "infotainment": "800W"}
    },
    "safety_systems": {
        "standard": {"abs_esp": "200W", "airbags": "100W", "sensors": "150W"},
        "advanced": {"abs_esp": "300W", "airbags": "200W", "sensors": "400W", "autonomous": "600W"}
    }
}

# Wiring harness specifications
WIRING_HARNESS_SPECS = {
    "standard_copper": {
        "gauge_range": "10-22 AWG",
        "insulation": "PVC",
        "temperature_rating": "105°C",
        "suitable_for": ["standard", "economy"]
    },
    "heavy_duty_copper": {
        "gauge_range": "8-20 AWG",
        "insulation": "XLPE",
        "temperature_rating": "125°C",
        "suitable_for": ["performance", "truck"]
    },
    "premium_copper": {
        "gauge_range": "10-24 AWG",
        "insulation": "XLPE_premium",
        "temperature_rating": "125°C",
        "suitable_for": ["luxury", "high_end"]
    },
    "hybrid_shielded": {
        "gauge_range": "6-22 AWG",
        "insulation": "XLPE_shielded",
        "temperature_rating": "150°C",
        "suitable_for": ["hybrid", "electric_assist"]
    },
    "high_voltage_shielded": {
        "gauge_range": "2-16 AWG",
        "insulation": "high_voltage_XLPE",
        "temperature_rating": "200°C",
        "suitable_for": ["electric", "high_voltage"]
    }
}

# ECU capabilities by version
ECU_CAPABILITIES = {
    "ECU-2024-STD": {
        "processor": "32-bit ARM",
        "memory": "2MB Flash, 512KB RAM",
        "can_bus": "CAN 2.0B",
        "features": ["engine_control", "emission_control", "basic_diagnostics"]
    },
    "ECU-2024-PERF": {
        "processor": "64-bit ARM",
        "memory": "4MB Flash, 1MB RAM",
        "can_bus": "CAN-FD",
        "features": ["engine_control", "performance_tuning", "advanced_diagnostics", "data_logging"]
    },
    "ECU-2024-HYB": {
        "processor": "64-bit ARM Dual-Core",
        "memory": "8MB Flash, 2MB RAM",
        "can_bus": "CAN-FD + LIN",
        "features": ["engine_control", "motor_control", "battery_management", "energy_optimization"]
    },
    "ECU-2024-EV": {
        "processor": "64-bit ARM Quad-Core",
        "memory": "16MB Flash, 4MB RAM",
        "can_bus": "CAN-FD + Ethernet",
        "features": ["motor_control", "battery_management", "charging_control", "thermal_management"]
    },
    "ECU-2024-TRUCK": {
        "processor": "32-bit ARM",
        "memory": "4MB Flash, 1MB RAM",
        "can_bus": "CAN 2.0B + J1939",
        "features": ["engine_control", "transmission_control", "trailer_interface", "fleet_management"]
    },
    "ECU-2024-LUX": {
        "processor": "64-bit ARM",
        "memory": "8MB Flash, 2MB RAM",
        "can_bus": "CAN-FD + MOST",
        "features": ["engine_control", "comfort_systems", "advanced_diagnostics", "security_features"]
    }
}


class ElectricalConfigurationTool(BaseTool):
    """Tool for configuring electrical systems based on engine type and vehicle requirements."""

    name: str = "configure_electrical_system"
    description: str = ("Configure electrical system specifications including battery voltage, "
                       "alternator output, wiring harness, and ECU based on engine type and vehicle features.")

    def _run(
        self,
        engine_type: str = "v6_gasoline",
        vehicle_class: str = "standard",
        feature_level: str = "basic",
        climate_requirements: str = "standard"
    ) -> str:
        """Configure electrical system based on engine and vehicle requirements.

        Args:
            engine_type: Type of engine (v6_gasoline, v8_gasoline, v4_turbo, electric, hybrid, diesel_v6)
            vehicle_class: Vehicle class (standard, performance, luxury, truck)
            feature_level: Feature level (basic, premium, luxury)
            climate_requirements: Climate control requirements (standard, enhanced, premium)

        Returns:
            JSON string with electrical system configuration
        """
        try:
            # Select base electrical configuration
            config_key = self._select_electrical_configuration(engine_type, vehicle_class)
            electrical_config = ELECTRICAL_CONFIGURATIONS.get(config_key, ELECTRICAL_CONFIGURATIONS["standard_12v"]).copy()

            # Calculate total electrical load
            total_load = self._calculate_total_electrical_load(
                engine_type, feature_level, climate_requirements
            )

            # Adjust alternator output if needed
            electrical_config = self._adjust_alternator_output(electrical_config, total_load, engine_type)

            # Select appropriate wiring harness
            electrical_config["wiringHarness"] = self._select_wiring_harness(engine_type, vehicle_class, feature_level)

            # Get detailed specifications
            harness_specs = WIRING_HARNESS_SPECS.get(electrical_config["wiringHarness"], {})
            ecu_specs = ECU_CAPABILITIES.get(electrical_config["ecuVersion"], {})

            result = {
                "electricalType": electrical_config,
                "load_analysis": total_load,
                "harness_specifications": harness_specs,
                "ecu_capabilities": ecu_specs,
                "configuration_notes": {
                    "selected_config": config_key,
                    "engine_type": engine_type,
                    "vehicle_class": vehicle_class,
                    "feature_level": feature_level
                }
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Electrical configuration failed: {str(e)}",
                "fallback": ELECTRICAL_CONFIGURATIONS["standard_12v"]
            })

    def _select_electrical_configuration(self, engine_type: str, vehicle_class: str) -> str:
        """Select appropriate electrical configuration."""

        # Engine type priority
        if engine_type == "electric":
            return "electric_system"
        elif engine_type == "hybrid":
            return "hybrid_system"
        elif vehicle_class == "truck":
            return "truck_24v"
        elif vehicle_class in ["performance", "sport"]:
            return "performance_12v"
        elif vehicle_class == "luxury":
            return "luxury_12v"
        else:
            return "standard_12v"

    def _calculate_total_electrical_load(self, engine_type: str, feature_level: str, climate: str) -> Dict[str, Any]:
        """Calculate total electrical load requirements."""

        # Get engine loads
        engine_loads = ELECTRICAL_LOADS["engine_types"].get(engine_type, {})

        # Get body feature loads
        body_loads = ELECTRICAL_LOADS["body_features"].get(feature_level, ELECTRICAL_LOADS["body_features"]["basic"])

        # Get safety system loads
        safety_level = "advanced" if feature_level in ["premium", "luxury"] else "standard"
        safety_loads = ELECTRICAL_LOADS["safety_systems"][safety_level]

        # Climate adjustment
        climate_multiplier = {"standard": 1.0, "enhanced": 1.3, "premium": 1.6}.get(climate, 1.0)
        adjusted_climate_load = int(float(body_loads["climate"].replace("kW", "")) * climate_multiplier * 1000)

        total_load = {
            "engine_loads": engine_loads,
            "body_loads": body_loads,
            "safety_loads": safety_loads,
            "climate_adjusted": f"{adjusted_climate_load}W",
            "estimated_peak_load": self._calculate_peak_load(engine_loads, body_loads, safety_loads, adjusted_climate_load)
        }

        return total_load

    def _calculate_peak_load(self, engine_loads: Dict, body_loads: Dict, safety_loads: Dict, climate_load: int) -> str:
        """Calculate estimated peak electrical load."""
        try:
            total_watts = 0

            # Sum engine loads (convert kW to W)
            for load in engine_loads.values():
                if "kW" in load:
                    total_watts += float(load.replace("kW", "")) * 1000
                elif "W" in load:
                    total_watts += float(load.replace("W", ""))

            # Sum body loads (excluding climate as it's already adjusted)
            for key, load in body_loads.items():
                if key != "climate":
                    if "kW" in load:
                        total_watts += float(load.replace("kW", "")) * 1000
                    elif "W" in load:
                        total_watts += float(load.replace("W", ""))

            # Add adjusted climate load
            total_watts += climate_load

            # Sum safety loads
            for load in safety_loads.values():
                if "W" in load:
                    total_watts += float(load.replace("W", ""))

            # Convert back to appropriate unit
            if total_watts >= 1000:
                return f"{total_watts/1000:.1f}kW"
            else:
                return f"{int(total_watts)}W"

        except (ValueError, KeyError):
            return "Calculation_Error"

    def _adjust_alternator_output(self, config: Dict, total_load: Dict, engine_type: str) -> Dict:
        """Adjust alternator output based on calculated load."""

        if engine_type == "electric":
            return config  # Electric vehicles don't have alternators

        try:
            # Extract peak load value
            peak_load_str = total_load.get("estimated_peak_load", "0W")
            if "kW" in peak_load_str:
                peak_load_watts = float(peak_load_str.replace("kW", "")) * 1000
            else:
                peak_load_watts = float(peak_load_str.replace("W", ""))

            # Calculate required alternator output (add 30% margin)
            required_amps = (peak_load_watts * 1.3) / 12  # Assume 12V system

            # Current alternator output
            current_output = int(config["alternatorOutput"].replace("A", ""))

            # Upgrade if needed
            if required_amps > current_output:
                new_output = int((required_amps // 20 + 1) * 20)  # Round up to nearest 20A
                config["alternatorOutput"] = f"{new_output}A"

        except (ValueError, KeyError):
            pass  # Keep original alternator output if calculation fails

        return config

    def _select_wiring_harness(self, engine_type: str, vehicle_class: str, feature_level: str) -> str:
        """Select appropriate wiring harness."""

        if engine_type == "electric":
            return "high_voltage_shielded"
        elif engine_type == "hybrid":
            return "hybrid_shielded"
        elif vehicle_class in ["performance", "truck"]:
            return "heavy_duty_copper"
        elif feature_level == "luxury":
            return "premium_copper"
        else:
            return "standard_copper"


class ElectricalSystemTool(BaseTool):
    """Tool for getting detailed electrical system information and integration requirements."""

    name: str = "get_electrical_system_info"
    description: str = ("Get detailed information about electrical systems, compatibility requirements, "
                       "and integration specifications for different engine types and vehicle configurations.")

    def _run(
        self,
        system_type: str = "12V",
        detailed_analysis: bool = True,
        compatibility_check: str = "all"
    ) -> str:
        """Get detailed electrical system information.

        Args:
            system_type: System type to analyze (12V, 24V, hybrid, high-voltage)
            detailed_analysis: Whether to include detailed specifications
            compatibility_check: What to check compatibility with (all, engine, body, specific)

        Returns:
            JSON string with electrical system information
        """
        try:
            # Find configurations with this system type
            matching_configs = {}
            for config_name, config_data in ELECTRICAL_CONFIGURATIONS.items():
                if config_data["@systemType"] == system_type:
                    matching_configs[config_name] = config_data

            if not matching_configs:
                return json.dumps({
                    "error": f"No configurations found for system type: {system_type}",
                    "available_types": list(set(config["@systemType"] for config in ELECTRICAL_CONFIGURATIONS.values()))
                })

            result = {
                "system_type": system_type,
                "matching_configurations": matching_configs
            }

            if detailed_analysis:
                # Add detailed specifications
                detailed_specs = self._get_detailed_specifications(system_type)
                integration_requirements = self._get_integration_requirements(system_type)
                safety_considerations = self._get_safety_considerations(system_type)

                result.update({
                    "detailed_specifications": detailed_specs,
                    "integration_requirements": integration_requirements,
                    "safety_considerations": safety_considerations
                })

            if compatibility_check != "none":
                compatibility = self._analyze_system_compatibility(system_type, compatibility_check)
                result["compatibility_analysis"] = compatibility

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to get electrical system info: {str(e)}",
                "system_type": system_type
            })

    def _get_detailed_specifications(self, system_type: str) -> Dict[str, Any]:
        """Get detailed specifications for a system type."""

        specs = {
            "12V": {
                "nominal_voltage": "12V",
                "operating_range": "10.5V - 14.4V",
                "typical_battery": "12V Lead-Acid or AGM",
                "charging_voltage": "13.8V - 14.4V",
                "applications": ["passenger_cars", "light_trucks", "motorcycles"]
            },
            "24V": {
                "nominal_voltage": "24V",
                "operating_range": "21V - 28.8V",
                "typical_battery": "24V Lead-Acid (2x12V)",
                "charging_voltage": "27.6V - 28.8V",
                "applications": ["heavy_trucks", "commercial_vehicles", "marine"]
            },
            "hybrid": {
                "nominal_voltage": "12V/200V-400V",
                "operating_range": "Variable",
                "typical_battery": "12V + NiMH/Li-ion HV",
                "charging_voltage": "Variable/Regenerative",
                "applications": ["hybrid_vehicles", "mild_hybrid", "plug_in_hybrid"]
            },
            "high-voltage": {
                "nominal_voltage": "200V-800V",
                "operating_range": "150V-900V",
                "typical_battery": "Li-ion HV Pack",
                "charging_voltage": "DC Fast/AC Slow",
                "applications": ["electric_vehicles", "performance_EVs", "commercial_EVs"]
            }
        }

        return specs.get(system_type, {"error": f"Unknown system type: {system_type}"})

    def _get_integration_requirements(self, system_type: str) -> Dict[str, List[str]]:
        """Get integration requirements for different system types."""

        requirements = {
            "12V": [
                "Standard automotive connectors",
                "Basic insulation requirements",
                "Standard grounding practices",
                "Conventional fuse/relay box"
            ],
            "24V": [
                "Heavy-duty connectors",
                "Enhanced insulation",
                "Dual-battery management",
                "Commercial-grade protection"
            ],
            "hybrid": [
                "High-voltage safety interlock",
                "Dual-voltage system management",
                "Electromagnetic shielding",
                "Specialized service procedures"
            ],
            "high-voltage": [
                "High-voltage safety systems",
                "Orange cable identification",
                "Electromagnetic compatibility",
                "Thermal management systems",
                "Service disconnect procedures"
            ]
        }

        return {"requirements": requirements.get(system_type, [])}

    def _get_safety_considerations(self, system_type: str) -> Dict[str, List[str]]:
        """Get safety considerations for system types."""

        safety = {
            "12V": [
                "Standard electrical safety",
                "Short circuit protection",
                "Overcurrent protection"
            ],
            "24V": [
                "Enhanced electrical safety",
                "Arc flash considerations",
                "Ground fault protection"
            ],
            "hybrid": [
                "High-voltage awareness training",
                "Insulated tools required",
                "Emergency disconnect procedures",
                "Battery cooling monitoring"
            ],
            "high-voltage": [
                "Specialized training required",
                "High-voltage PPE mandatory",
                "Lockout/tagout procedures",
                "Arc flash protection",
                "Thermal runaway protection"
            ]
        }

        return {"safety_requirements": safety.get(system_type, [])}

    def _analyze_system_compatibility(self, system_type: str, check_type: str) -> Dict[str, Any]:
        """Analyze compatibility with other vehicle systems."""

        compatibility = {
            "engine_compatibility": self._check_engine_compatibility(system_type),
            "charging_infrastructure": self._check_charging_compatibility(system_type),
            "service_requirements": self._get_service_requirements(system_type)
        }

        return compatibility

    def _check_engine_compatibility(self, system_type: str) -> Dict[str, bool]:
        """Check compatibility with different engine types."""

        compatibility_matrix = {
            "12V": {
                "v6_gasoline": True,
                "v8_gasoline": True,
                "v4_turbo": True,
                "diesel_v6": True,
                "hybrid": False,
                "electric": False
            },
            "24V": {
                "v6_gasoline": True,
                "v8_gasoline": True,
                "v4_turbo": True,
                "diesel_v6": True,
                "hybrid": False,
                "electric": False
            },
            "hybrid": {
                "v6_gasoline": True,
                "v8_gasoline": True,
                "v4_turbo": True,
                "diesel_v6": True,
                "hybrid": True,
                "electric": False
            },
            "high-voltage": {
                "v6_gasoline": False,
                "v8_gasoline": False,
                "v4_turbo": False,
                "diesel_v6": False,
                "hybrid": False,
                "electric": True
            }
        }

        return compatibility_matrix.get(system_type, {})

    def _check_charging_compatibility(self, system_type: str) -> Dict[str, str]:
        """Check charging system compatibility."""

        charging = {
            "12V": {"type": "alternator", "method": "belt_driven", "voltage_regulation": "built_in"},
            "24V": {"type": "alternator", "method": "belt_driven", "voltage_regulation": "external"},
            "hybrid": {"type": "alternator_motor", "method": "integrated", "voltage_regulation": "ECU_controlled"},
            "high-voltage": {"type": "onboard_charger", "method": "AC_DC_conversion", "voltage_regulation": "BMS_controlled"}
        }

        return charging.get(system_type, {"type": "unknown"})

    def _get_service_requirements(self, system_type: str) -> List[str]:
        """Get service and maintenance requirements."""

        service_reqs = {
            "12V": ["Standard electrical tools", "Basic multimeter", "Standard safety"],
            "24V": ["Heavy-duty tools", "Commercial multimeter", "Enhanced safety"],
            "hybrid": ["Insulated tools", "HV-capable multimeter", "HV safety training"],
            "high-voltage": ["Specialized HV tools", "HV test equipment", "Certified technician"]
        }

        return service_reqs.get(system_type, ["Consult manufacturer"])