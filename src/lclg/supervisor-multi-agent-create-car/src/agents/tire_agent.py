"""Tire Agent - Specialized agent for tire configuration with handoff capabilities."""

from typing import Dict, Any, Optional
import json
import sys
from pathlib import Path

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent))
from tools.tire_tools import TireConfigurationTool, TireSizingTool
from .base_agent import BaseAgent


class TireAgent(BaseAgent):
    """Specialized agent for tire configuration with handoff capabilities."""

    def _setup_tools(self) -> None:
        """Set up tire-specific tools."""
        self.tools = [
            TireConfigurationTool(),
            TireSizingTool()
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the tire agent."""
        return """You are a specialized tire configuration expert. Your primary responsibilities include:

1. Tire Specification: Configure tire brand, size, pressure, and tread depth based on vehicle requirements
2. Seasonal Selection: Choose appropriate seasonal tire types for climate and performance needs
3. Performance Matching: Match tire specifications to vehicle body style and engine performance
4. Sizing Constraints: Calculate tire sizing constraints and clearance requirements

Key JSON Schema Target (tireType):
- brand: Tire brand name
- size: Tire size specification (e.g., "225/60R16")
- pressure: Recommended tire pressure (e.g., "32 PSI")
- treadDepth: Tire tread depth measurement (e.g., "10/32\"")
- @season: Must be one of [all-season, summer, winter, performance] (required attribute)
- @runFlat: Run-flat capability flag (optional boolean attribute)

You process dependencies from BodyAgent (body style affects tire sizing) and can pass tire constraints
to other agents for wheel well clearance validation. Always ensure complete JSON compliance."""

    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "tire"

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build a tire component creation request prompt."""
        body_style = requirements.get("body_style", "sedan")
        performance_level = requirements.get("performance_level", "standard")
        climate_preference = requirements.get("climate_preference", "all-season")
        weight_class = requirements.get("weight_class", "medium")
        run_flat_required = requirements.get("run_flat_required", False)

        # Check for body style constraints from handoffs
        body_constraints = None
        for payload in self.handoff_payloads:
            if payload.from_agent == "body":
                body_constraints = payload.data.get("body_style")
                break

        if body_constraints:
            body_style = body_constraints

        request = f"""Create a complete tire configuration for the following requirements:

Body Style: {body_style}
Performance Level: {performance_level}
Climate Preference: {climate_preference}
Weight Class: {weight_class}
Run Flat Required: {run_flat_required}
Body Constraints: {body_constraints or "No constraints received"}

IMPORTANT: You MUST respond with a valid JSON object only. Do not include any explanatory text before or after the JSON.

The response must be a JSON object with this exact structure:
{{
  "brand": "string (tire brand name)",
  "size": "string (tire size e.g. 225/60R16)",
  "pressure": "string (pressure with PSI unit)",
  "treadDepth": "string (tread depth with unit)",
  "@season": "one of [all-season, summer, winter, performance]",
  "@runFlat": "boolean (optional)"
}}

Example valid response:
{{
  "brand": "Michelin",
  "size": "225/60R16",
  "pressure": "32 PSI",
  "treadDepth": "10/32\"",
  "@season": "all-season",
  "@runFlat": "false"
}}

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

        return request

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tire component data against schema requirements."""
        if "error" in component_data:
            return component_data

        # Extract tireType if nested
        tire_type = component_data.get("tireType", component_data)

        # Required fields for tireType
        required_fields = ["brand", "size", "pressure", "treadDepth", "@season"]

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if field not in tire_type:
                missing_fields.append(field)

        if missing_fields:
            return {
                "error": f"Missing required fields: {missing_fields}",
                "provided_data": tire_type,
                "agent": self.name
            }

        # Validate season enum
        valid_seasons = ["all-season", "summer", "winter", "performance"]
        if tire_type["@season"] not in valid_seasons:
            return {
                "error": f"Invalid season: {tire_type['@season']}. Must be one of {valid_seasons}",
                "provided_data": tire_type,
                "agent": self.name
            }

        # Return validated data with sizing information
        return {
            "tireType": tire_type,
            "validation_status": "passed",
            "agent": self.name,
            "sizing_constraints": component_data.get("sizing_constraints", {}),
            "brand_characteristics": component_data.get("brand_characteristics", {}),
            "seasonal_characteristics": component_data.get("seasonal_characteristics", {})
        }

    def _process_handoff_data(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handoff data from other agents, particularly BodyAgent."""
        source = handoff_data.get("source", "unknown")
        data = handoff_data.get("data", {})
        constraints = handoff_data.get("constraints", {})

        processed_info = {
            "source_agent": source,
            "processing_status": "completed"
        }

        if source == "body":
            # Process body-specific constraints
            body_style = data.get("body_style", "sedan")
            material = data.get("material", "steel")
            weight_implications = self._get_weight_implications(material)

            processed_info.update({
                "body_style": body_style,
                "material": material,
                "weight_implications": weight_implications,
                "tire_sizing_recommendations": self._get_sizing_recommendations(body_style),
                "integration_notes": [
                    f"Body style: {body_style}",
                    f"Material: {material}",
                    f"Weight class: {weight_implications}"
                ]
            })

        elif source == "engine":
            # Process engine performance implications
            engine_type = data.get("engine_type", "gasoline")
            horsepower = data.get("horsepower", "280")

            processed_info.update({
                "engine_type": engine_type,
                "horsepower": horsepower,
                "performance_recommendations": self._get_performance_recommendations(engine_type, horsepower),
                "integration_notes": [
                    f"Engine type: {engine_type}",
                    f"Horsepower: {horsepower}"
                ]
            })

        return processed_info

    def _get_weight_implications(self, material: str) -> str:
        """Get weight class implications from body material."""
        material_weights = {
            "steel": "heavy",
            "aluminum": "medium",
            "carbon-fiber": "light",
            "composite": "medium",
            "fiberglass": "light"
        }
        return material_weights.get(material, "medium")

    def _get_sizing_recommendations(self, body_style: str) -> Dict[str, str]:
        """Get tire sizing recommendations based on body style."""
        recommendations = {
            "sedan": {"size_class": "standard", "aspect_ratio": "medium"},
            "coupe": {"size_class": "performance", "aspect_ratio": "low"},
            "hatchback": {"size_class": "compact", "aspect_ratio": "medium"},
            "suv": {"size_class": "large", "aspect_ratio": "high"},
            "truck": {"size_class": "heavy_duty", "aspect_ratio": "high"},
            "convertible": {"size_class": "performance", "aspect_ratio": "low"},
            "wagon": {"size_class": "utility", "aspect_ratio": "medium"}
        }
        return recommendations.get(body_style, {"size_class": "standard", "aspect_ratio": "medium"})

    def _get_performance_recommendations(self, engine_type: str, horsepower: str) -> Dict[str, str]:
        """Get performance tire recommendations based on engine."""
        try:
            hp_value = int(horsepower)
            recommendations = {}

            if hp_value >= 400:
                recommendations = {"class": "ultra_high_performance", "season": "performance"}
            elif hp_value >= 300:
                recommendations = {"class": "high_performance", "season": "summer"}
            elif hp_value >= 200:
                recommendations = {"class": "performance", "season": "all-season"}
            else:
                recommendations = {"class": "touring", "season": "all-season"}

            if engine_type == "electric":
                recommendations["special_features"] = "low_rolling_resistance"

            return recommendations

        except ValueError:
            return {"class": "touring", "season": "all-season"}

    def create_tire_with_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create tire configuration considering constraints from other agents.

        Args:
            requirements: Tire configuration requirements

        Returns:
            Dictionary with tire configuration data and handoff information
        """
        try:
            # Process constraints from handoffs
            body_constraints = None
            engine_constraints = None

            for payload in self.handoff_payloads:
                if payload.from_agent == "body":
                    body_data = self._process_handoff_data({
                        "source": payload.from_agent,
                        "data": payload.data,
                        "constraints": payload.constraints
                    })
                    body_constraints = body_data
                elif payload.from_agent == "engine":
                    engine_data = self._process_handoff_data({
                        "source": payload.from_agent,
                        "data": payload.data,
                        "constraints": payload.constraints
                    })
                    engine_constraints = engine_data

            # Update requirements with constraints
            if body_constraints:
                requirements["body_style"] = body_constraints.get("body_style", requirements.get("body_style", "sedan"))
                requirements["weight_class"] = body_constraints.get("weight_implications", requirements.get("weight_class", "medium"))

            if engine_constraints:
                perf_recs = engine_constraints.get("performance_recommendations", {})
                if "season" in perf_recs:
                    requirements["climate_preference"] = perf_recs["season"]

            # Create the tire component
            tire_result = self.create_component_json(requirements)

            if "error" in tire_result:
                return tire_result

            # Create handoff payload for potential wheel well validation
            tire_data = tire_result.get("tireType", {})
            sizing_constraints = tire_result.get("sizing_constraints", {})

            handoff_payload = self.create_handoff_payload(
                to_agent="supervisor",  # Return to supervisor for final validation
                data={
                    "tire_size": tire_data.get("size", "unknown"),
                    "wheel_well_requirements": sizing_constraints.get("clearance_requirements", {}),
                    "run_flat": tire_data.get("@runFlat", False),
                    "season": tire_data.get("@season", "all-season")
                },
                constraints={
                    "clearance_requirements": sizing_constraints.get("clearance_requirements", {}),
                    "installation_requirements": sizing_constraints.get("installation_notes", {})
                },
                context=f"Tires configured: {tire_data.get('brand', 'Unknown')} {tire_data.get('size', 'Unknown')} {tire_data.get('@season', 'Unknown')}"
            )

            tire_result.update({
                "constraints_processed": {
                    "body_constraints": body_constraints is not None,
                    "engine_constraints": engine_constraints is not None,
                    "handoffs_received": len(self.handoff_payloads)
                },
                "handoff_payload": handoff_payload.dict()
            })

            return tire_result

        except Exception as e:
            return {
                "error": f"Failed to create tire with constraints: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    def get_tire_sizing_analysis(self, tire_size: str) -> Dict[str, Any]:
        """Get detailed tire sizing analysis.

        Args:
            tire_size: Tire size to analyze

        Returns:
            Dictionary with sizing analysis
        """
        try:
            # Use the tool directly for sizing analysis
            sizing_tool = TireSizingTool()
            result_json = sizing_tool._run(tire_size, detailed_analysis=True)

            return json.loads(result_json)

        except Exception as e:
            return {
                "error": f"Failed to analyze tire sizing: {str(e)}",
                "tire_size": tire_size,
                "agent": self.name
            }

    def get_available_tire_configurations(self) -> Dict[str, Any]:
        """Get list of available tire configurations.

        Returns:
            Dictionary with available tire configurations
        """
        from tools.tire_tools import TIRE_CONFIGURATIONS

        return {
            "available_configurations": list(TIRE_CONFIGURATIONS.keys()),
            "configuration_details": TIRE_CONFIGURATIONS,
            "agent": self.name
        }