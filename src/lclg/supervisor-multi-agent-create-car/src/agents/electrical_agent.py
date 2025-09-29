"""Electrical Agent - Specialized agent for electrical system configuration using tool patterns."""

from typing import Dict, Any, Optional
import json
import sys
from pathlib import Path

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent))
from tools.electrical_tools import ElectricalConfigurationTool, ElectricalSystemTool
from .base_agent import BaseAgent


class ElectricalAgent(BaseAgent):
    """Specialized agent for electrical system configuration using traditional LangChain tool patterns."""

    def _setup_tools(self) -> None:
        """Set up electrical-specific tools."""
        self.tools = [
            ElectricalConfigurationTool(),
            ElectricalSystemTool()
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the electrical agent."""
        return """You are a specialized electrical system configuration expert. Your primary responsibilities include:

1. Electrical System Design: Configure voltage systems, alternator output, and ECU versions based on engine requirements
2. Battery Management: Select appropriate battery types and voltages for different powertrains
3. Wiring Harness Selection: Choose suitable wiring harnesses for different voltage systems and environments
4. Load Calculation: Calculate electrical loads and ensure adequate power generation and distribution

Key JSON Schema Target (electricalType):
- batteryVoltage: Battery voltage specification (e.g., "12V", "24V", "400V")
- alternatorOutput: Alternator output capacity (e.g., "120A", "N/A" for electric)
- wiringHarness: Wiring harness type/specification
- ecuVersion: ECU software version identifier
- @systemType: Must be one of [12V, 24V, hybrid, high-voltage] (required attribute)
- @hybridCapable: Hybrid capability flag (optional boolean attribute)

You process dependencies from EngineAgent (engine type affects electrical requirements) and coordinate
with BodyAgent for wiring harness routing considerations. Always ensure complete JSON compliance."""

    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "electrical"

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build an electrical component creation request prompt."""
        engine_type = requirements.get("engine_type", "v6_gasoline")
        vehicle_class = requirements.get("vehicle_class", "standard")
        feature_level = requirements.get("feature_level", "basic")
        climate_requirements = requirements.get("climate_requirements", "standard")

        # Check for engine constraints from handoffs
        engine_constraints = None
        for payload in self.handoff_payloads:
            if payload.from_agent == "engine":
                engine_constraints = {
                    "engine_type": payload.data.get("engine_type", engine_type),
                    "horsepower": payload.data.get("horsepower", "280"),
                    "electrical_requirements": payload.constraints
                }
                break

        request = f"""Create a complete electrical system configuration for the following requirements:

Engine Type: {engine_type}
Vehicle Class: {vehicle_class}
Feature Level: {feature_level}
Climate Requirements: {climate_requirements}
Engine Constraints: {engine_constraints or "No constraints received"}

IMPORTANT: You MUST respond with a valid JSON object only. Do not include any explanatory text before or after the JSON.

The response must be a JSON object with this exact structure:
{{
  "batteryVoltage": "string (voltage specification)",
  "alternatorOutput": "string (alternator capacity or N/A for electric)",
  "wiringHarness": "string (harness type specification)",
  "ecuVersion": "string (ECU version identifier)",
  "@systemType": "one of [12V, 24V, hybrid, high-voltage]",
  "@hybridCapable": "boolean (optional)"
}}

Example valid response:
{{
  "batteryVoltage": "12V",
  "alternatorOutput": "120A",
  "wiringHarness": "standard",
  "ecuVersion": "ECU-2.1",
  "@systemType": "12V",
  "@hybridCapable": "false"
}}

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

        return request

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate electrical component data against schema requirements."""
        if "error" in component_data:
            return component_data

        # Extract electricalType if nested
        electrical_type = component_data.get("electricalType", component_data)

        # Required fields for electricalType
        required_fields = ["batteryVoltage", "alternatorOutput", "wiringHarness", "ecuVersion", "@systemType"]

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if field not in electrical_type:
                missing_fields.append(field)

        if missing_fields:
            return {
                "error": f"Missing required fields: {missing_fields}",
                "provided_data": electrical_type,
                "agent": self.name
            }

        # Validate systemType enum
        valid_system_types = ["12V", "24V", "hybrid", "high-voltage"]
        if electrical_type["@systemType"] not in valid_system_types:
            return {
                "error": f"Invalid systemType: {electrical_type['@systemType']}. Must be one of {valid_system_types}",
                "provided_data": electrical_type,
                "agent": self.name
            }

        # Return validated data
        return {
            "electricalType": electrical_type,
            "validation_status": "passed",
            "agent": self.name,
            "load_analysis": component_data.get("load_analysis", {}),
            "harness_specifications": component_data.get("harness_specifications", {}),
            "ecu_capabilities": component_data.get("ecu_capabilities", {})
        }

    def _process_handoff_data(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handoff data from other agents, particularly EngineAgent."""
        source = handoff_data.get("source", "unknown")
        data = handoff_data.get("data", {})
        constraints = handoff_data.get("constraints", {})

        processed_info = {
            "source_agent": source,
            "processing_status": "completed"
        }

        if source == "engine":
            # Process engine-specific electrical requirements
            engine_type = data.get("engine_type", "gasoline")
            horsepower = data.get("horsepower", "280")
            cooling_requirements = data.get("cooling_requirements", "standard")

            # Calculate electrical load implications
            electrical_requirements = self._calculate_engine_electrical_requirements(
                engine_type, horsepower, cooling_requirements
            )

            processed_info.update({
                "engine_type": engine_type,
                "horsepower": horsepower,
                "cooling_requirements": cooling_requirements,
                "electrical_requirements": electrical_requirements,
                "system_recommendations": self._get_system_recommendations(engine_type),
                "integration_notes": [
                    f"Engine type: {engine_type}",
                    f"Power output: {horsepower} HP",
                    f"Cooling needs: {cooling_requirements}"
                ]
            })

        elif source == "body":
            # Process body-specific wiring requirements
            body_style = data.get("body_style", "sedan")
            material = data.get("material", "steel")
            customization = data.get("customized", False)

            wiring_implications = self._get_wiring_implications(body_style, material, customization)

            processed_info.update({
                "body_style": body_style,
                "material": material,
                "customization": customization,
                "wiring_implications": wiring_implications,
                "integration_notes": [
                    f"Body style: {body_style}",
                    f"Material: {material}",
                    f"Customized: {customization}"
                ]
            })

        return processed_info

    def _calculate_engine_electrical_requirements(
        self,
        engine_type: str,
        horsepower: str,
        cooling_requirements: str
    ) -> Dict[str, Any]:
        """Calculate electrical requirements based on engine specifications."""
        try:
            hp_value = int(horsepower)
            requirements = {}

            if engine_type == "electric":
                requirements = {
                    "system_type": "high-voltage",
                    "alternator_needed": False,
                    "high_voltage_battery": True,
                    "charging_infrastructure": True
                }
            elif engine_type == "hybrid":
                requirements = {
                    "system_type": "hybrid",
                    "alternator_needed": True,
                    "high_voltage_battery": True,
                    "charging_infrastructure": True
                }
            else:
                # ICE engines
                alternator_size = max(120, int(hp_value * 0.25))  # Base calculation

                if cooling_requirements in ["enhanced", "heavy_duty"]:
                    alternator_size += 40  # Additional load for enhanced cooling

                requirements = {
                    "system_type": "12V" if hp_value < 500 else "24V",
                    "alternator_needed": True,
                    "recommended_alternator": f"{alternator_size}A",
                    "high_voltage_battery": False,
                    "charging_infrastructure": False
                }

            return requirements

        except ValueError:
            return {"system_type": "12V", "alternator_needed": True}

    def _get_system_recommendations(self, engine_type: str) -> Dict[str, str]:
        """Get electrical system recommendations based on engine type."""
        recommendations = {
            "v6_gasoline": {"voltage": "12V", "complexity": "standard"},
            "v8_gasoline": {"voltage": "12V", "complexity": "enhanced"},
            "v4_turbo": {"voltage": "12V", "complexity": "performance"},
            "electric": {"voltage": "high-voltage", "complexity": "advanced"},
            "hybrid": {"voltage": "dual-voltage", "complexity": "complex"},
            "diesel_v6": {"voltage": "12V", "complexity": "heavy_duty"}
        }
        return recommendations.get(engine_type, {"voltage": "12V", "complexity": "standard"})

    def _get_wiring_implications(self, body_style: str, material: str, customization: bool) -> Dict[str, str]:
        """Get wiring harness implications based on body configuration."""
        implications = {}

        # Body style implications
        if body_style == "convertible":
            implications["weatherproofing"] = "enhanced"
            implications["flex_zones"] = "critical"
        elif body_style in ["truck", "suv"]:
            implications["durability"] = "heavy_duty"
            implications["routing"] = "utility_focused"
        else:
            implications["routing"] = "standard"

        # Material implications
        if material == "carbon-fiber":
            implications["electromagnetic_shielding"] = "required"
        elif material == "aluminum":
            implications["grounding"] = "special_attention"

        # Customization implications
        if customization:
            implications["accessibility"] = "enhanced"
            implications["upgrade_provisions"] = "included"

        return implications

    def create_electrical_with_dependencies(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create electrical system configuration considering dependencies from other agents.

        Args:
            requirements: Electrical system configuration requirements

        Returns:
            Dictionary with electrical configuration data
        """
        try:
            # Process constraints from handoffs
            engine_constraints = None
            body_constraints = None

            for payload in self.handoff_payloads:
                if payload.from_agent == "engine":
                    engine_data = self._process_handoff_data({
                        "source": payload.from_agent,
                        "data": payload.data,
                        "constraints": payload.constraints
                    })
                    engine_constraints = engine_data
                elif payload.from_agent == "body":
                    body_data = self._process_handoff_data({
                        "source": payload.from_agent,
                        "data": payload.data,
                        "constraints": payload.constraints
                    })
                    body_constraints = body_data

            # Update requirements with constraints
            if engine_constraints:
                requirements["engine_type"] = engine_constraints.get("engine_type", requirements.get("engine_type", "v6_gasoline"))
                electrical_reqs = engine_constraints.get("electrical_requirements", {})
                if "system_type" in electrical_reqs:
                    requirements["system_type_override"] = electrical_reqs["system_type"]

            # Create the electrical component
            electrical_result = self.create_component_json(requirements)

            if "error" in electrical_result:
                return electrical_result

            # Add dependency processing information
            electrical_result["dependencies_processed"] = {
                "engine_constraints": engine_constraints is not None,
                "body_constraints": body_constraints is not None,
                "handoffs_received": len(self.handoff_payloads)
            }

            return electrical_result

        except Exception as e:
            return {
                "error": f"Failed to create electrical system with dependencies: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    def get_electrical_system_analysis(self, system_type: str) -> Dict[str, Any]:
        """Get detailed electrical system analysis.

        Args:
            system_type: System type to analyze

        Returns:
            Dictionary with system analysis
        """
        try:
            # Use the tool directly for system analysis
            system_tool = ElectricalSystemTool()
            result_json = system_tool._run(system_type, detailed_analysis=True)

            return json.loads(result_json)

        except Exception as e:
            return {
                "error": f"Failed to analyze electrical system: {str(e)}",
                "system_type": system_type,
                "agent": self.name
            }

    def get_load_calculation(self, engine_specs: Dict[str, Any], feature_level: str) -> Dict[str, Any]:
        """Calculate electrical load requirements.

        Args:
            engine_specs: Engine specifications
            feature_level: Vehicle feature level

        Returns:
            Dictionary with load calculations
        """
        try:
            engine_type = engine_specs.get("fuelType", "gasoline")
            horsepower = engine_specs.get("horsepower", "280")

            # Use the configuration tool to calculate loads
            config_tool = ElectricalConfigurationTool()
            result_json = config_tool._run(
                engine_type=engine_type,
                vehicle_class="standard",
                feature_level=feature_level,
                climate_requirements="standard"
            )

            result = json.loads(result_json)
            return result.get("load_analysis", {})

        except Exception as e:
            return {
                "error": f"Failed to calculate electrical load: {str(e)}",
                "engine_specs": engine_specs,
                "agent": self.name
            }

    def get_available_electrical_systems(self) -> Dict[str, Any]:
        """Get list of available electrical system configurations.

        Returns:
            Dictionary with available electrical systems
        """
        from tools.electrical_tools import ELECTRICAL_CONFIGURATIONS

        return {
            "available_systems": list(ELECTRICAL_CONFIGURATIONS.keys()),
            "system_details": ELECTRICAL_CONFIGURATIONS,
            "agent": self.name
        }