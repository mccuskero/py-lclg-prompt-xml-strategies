"""Engine Agent - Specialized agent for engine configuration with handoff capabilities."""

from typing import Dict, Any, Optional
import json
import sys
from pathlib import Path

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent))
from tools.engine_tools import EngineConfigurationTool, EngineSpecificationTool
from .base_agent import BaseAgent


class EngineAgent(BaseAgent):
    """Specialized agent for engine configuration with handoff capabilities to BodyAgent."""

    def _setup_tools(self) -> None:
        """Set up engine-specific tools."""
        self.tools = [
            EngineConfigurationTool(),
            EngineSpecificationTool()
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the engine agent."""
        return """You are a specialized engine configuration expert. Your primary responsibilities include:

1. Engine Specification: Configure engine displacement, cylinders, fuel type, and horsepower based on vehicle requirements
2. Performance Analysis: Determine appropriate engine type for the vehicle class and performance needs
3. Integration Planning: Calculate engine compartment size and constraints for other components
4. Handoff Coordination: Pass critical engine constraints to BodyAgent for proper integration

Key JSON Schema Target (engineType):
- displacement: Engine displacement volume (e.g., "3.5L", "2.0L")
- cylinders: Number of cylinders (e.g., "6", "8", "4")
- fuelType: Must be one of [gasoline, diesel, electric, hybrid, hydrogen]
- horsepower: Engine power output (e.g., "280", "420")
- @engineCode: Unique engine identifier (required attribute)
- @manufacturer: Engine manufacturer (optional attribute)

Always ensure complete JSON compliance and provide handoff data for engine compartment sizing to the BodyAgent."""

    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "engine"

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build an engine component creation request prompt."""
        vehicle_type = requirements.get("vehicle_type", "sedan")
        performance_level = requirements.get("performance_level", "standard")
        fuel_preference = requirements.get("fuel_preference", "gasoline")
        electric_capable = requirements.get("electric_capable", False)

        request = f"""Create a complete engine configuration for the following requirements:

Vehicle Type: {vehicle_type}
Performance Level: {performance_level}
Fuel Preference: {fuel_preference}
Electric Capable: {electric_capable}

IMPORTANT: You MUST respond with a valid JSON object only. Do not include any explanatory text before or after the JSON.

The response must be a JSON object with this exact structure:
{{
  "displacement": "string (e.g. '3.5L', '2.0L')",
  "cylinders": "string (e.g. '6', '8', '4')",
  "fuelType": "one of [gasoline, diesel, electric, hybrid, hydrogen]",
  "horsepower": "string (e.g. '280', '420')",
  "@engineCode": "string (unique engine identifier)",
  "@manufacturer": "string (optional)"
}}

Example valid response:
{{
  "displacement": "3.5L",
  "cylinders": "6",
  "fuelType": "gasoline",
  "horsepower": "280",
  "@engineCode": "ENG-V6-350",
  "@manufacturer": "AutoCorp"
}}

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

        return request

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate engine component data against schema requirements."""
        if "error" in component_data:
            return component_data

        # Extract engineType if nested
        engine_type = component_data.get("engineType", component_data)

        # Required fields for engineType
        required_fields = ["displacement", "cylinders", "fuelType", "horsepower", "@engineCode"]

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if field not in engine_type:
                missing_fields.append(field)

        if missing_fields:
            return {
                "error": f"Missing required fields: {missing_fields}",
                "provided_data": engine_type,
                "agent": self.name
            }

        # Validate fuelType enum
        valid_fuel_types = ["gasoline", "diesel", "electric", "hybrid", "hydrogen"]
        if engine_type["fuelType"] not in valid_fuel_types:
            return {
                "error": f"Invalid fuelType: {engine_type['fuelType']}. Must be one of {valid_fuel_types}",
                "provided_data": engine_type,
                "agent": self.name
            }

        # Return validated data with handoff information
        return {
            "engineType": engine_type,
            "validation_status": "passed",
            "agent": self.name,
            "handoff_data": component_data.get("compartment_info", {}),
            "integration_notes": component_data.get("integration_notes", {})
        }

    def _process_handoff_data(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handoff data from other agents."""
        # EngineAgent typically initiates workflows, so minimal handoff processing needed
        return {
            "processed": True,
            "source": handoff_data.get("source", "unknown"),
            "data_received": list(handoff_data.get("data", {}).keys()),
            "notes": "Engine agent typically initiates the workflow"
        }

    def create_engine_with_handoff(
        self,
        requirements: Dict[str, Any],
        target_agent: str = "body"
    ) -> Dict[str, Any]:
        """Create engine configuration and prepare handoff to another agent.

        Args:
            requirements: Engine configuration requirements
            target_agent: Target agent for handoff (usually "body")

        Returns:
            Dictionary with engine data and handoff payload
        """
        try:
            # Create the engine component
            engine_result = self.create_component_json(requirements)

            if "error" in engine_result:
                return engine_result

            # Extract engine data and compartment info
            engine_data = engine_result.get("engineType", {})
            compartment_info = engine_result.get("handoff_data", {})
            integration_notes = engine_result.get("integration_notes", {})

            # Create handoff payload for BodyAgent
            handoff_payload = self.create_handoff_payload(
                to_agent=target_agent,
                data={
                    "engine_compartment_size": compartment_info.get("size", "medium"),
                    "cooling_requirements": compartment_info.get("cooling_requirements", "standard"),
                    "engine_type": engine_data.get("fuelType", "gasoline"),
                    "horsepower": engine_data.get("horsepower", "280")
                },
                constraints={
                    "material_requirements": self._get_material_constraints(engine_data),
                    "space_requirements": compartment_info
                },
                context=f"Engine configured: {engine_data.get('@engineCode', 'Unknown')} - {engine_data.get('displacement', 'Unknown')} {engine_data.get('fuelType', 'Unknown')}"
            )

            return {
                "engine_configuration": engine_data,
                "handoff_payload": handoff_payload.dict(),
                "integration_notes": integration_notes,
                "status": "success",
                "agent": self.name
            }

        except Exception as e:
            return {
                "error": f"Failed to create engine with handoff: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    def _get_material_constraints(self, engine_data: Dict[str, Any]) -> Dict[str, str]:
        """Get material constraints based on engine configuration."""
        fuel_type = engine_data.get("fuelType", "gasoline")
        horsepower = int(engine_data.get("horsepower", "0"))

        constraints = {}

        # High-power engines need stronger materials
        if horsepower >= 400:
            constraints["minimum_strength"] = "high"
            constraints["recommended_materials"] = "steel,composite"
        elif horsepower >= 300:
            constraints["minimum_strength"] = "medium"
            constraints["recommended_materials"] = "steel,aluminum,composite"
        else:
            constraints["minimum_strength"] = "standard"
            constraints["recommended_materials"] = "any"

        # Electric engines have different requirements
        if fuel_type == "electric":
            constraints["thermal_management"] = "minimal"
            constraints["vibration_dampening"] = "low"
        elif fuel_type in ["v8_gasoline", "diesel_v6"]:
            constraints["thermal_management"] = "high"
            constraints["vibration_dampening"] = "high"
        else:
            constraints["thermal_management"] = "standard"
            constraints["vibration_dampening"] = "standard"

        return constraints

    def get_engine_specifications(self, engine_type: str) -> Dict[str, Any]:
        """Get detailed engine specifications using the EngineSpecificationTool.

        Args:
            engine_type: Type of engine to analyze

        Returns:
            Dictionary with detailed engine specifications
        """
        try:
            # Use the tool directly for detailed specs
            spec_tool = EngineSpecificationTool()
            result_json = spec_tool._run(engine_type)

            return json.loads(result_json)

        except Exception as e:
            return {
                "error": f"Failed to get engine specifications: {str(e)}",
                "engine_type": engine_type,
                "agent": self.name
            }

    def get_available_engine_types(self) -> Dict[str, Any]:
        """Get list of available engine configurations.

        Returns:
            Dictionary with available engine types and their characteristics
        """
        from tools.engine_tools import ENGINE_CONFIGURATIONS

        return {
            "available_engines": list(ENGINE_CONFIGURATIONS.keys()),
            "engine_details": ENGINE_CONFIGURATIONS,
            "agent": self.name
        }