"""Body Agent - Specialized agent for body configuration using tool patterns."""

from typing import Dict, Any, Optional
import json
import sys
from pathlib import Path

# Add tools to path
sys.path.append(str(Path(__file__).parent.parent))
from tools.body_tools import BodyConfigurationTool, BodyStyleTool
from .base_agent import BaseAgent


class BodyAgent(BaseAgent):
    """Specialized agent for body configuration using traditional LangChain tool patterns."""

    def _setup_tools(self) -> None:
        """Set up body-specific tools."""
        self.tools = [
            BodyConfigurationTool(),
            BodyStyleTool()
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the body agent."""
        return """You are a specialized body configuration expert. Your primary responsibilities include:

1. Body Style Configuration: Select and configure vehicle body style based on requirements
2. Material Selection: Choose appropriate materials considering engine constraints and performance needs
3. Color and Finish: Configure paint colors, codes, and customization options
4. Integration Processing: Process engine compartment constraints and electrical system requirements

Key JSON Schema Target (bodyType):
- style: Must be one of [sedan, coupe, hatchback, suv, truck, convertible, wagon]
- color: Body color specification
- doors: Number of doors (as string)
- material: Must be one of [steel, aluminum, carbon-fiber, composite, fiberglass]
- @paintCode: Paint code identifier (optional attribute)
- @customized: Customization flag (optional boolean attribute)

You excel at processing handoff data from EngineAgent regarding engine compartment size and cooling requirements.
Always ensure complete JSON compliance and consider integration constraints from other agents."""

    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "body"

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build a body component creation request prompt."""
        style = requirements.get("style", "sedan")
        performance_level = requirements.get("performance_level", "standard")
        customization_level = requirements.get("customization_level", "standard")
        color_preference = requirements.get("color_preference", "auto")

        # Check for engine constraints from handoffs
        engine_constraints = None
        for payload in self.handoff_payloads:
            if payload.from_agent == "engine":
                engine_constraints = payload.constraints.get("space_requirements", {}).get("size", "medium")
                break

        request = f"""Create a complete body configuration for the following requirements:

Body Style: {style}
Performance Level: {performance_level}
Customization Level: {customization_level}
Color Preference: {color_preference}
Engine Constraints: {engine_constraints or "No constraints received"}

IMPORTANT: You MUST respond with a valid JSON object only. Do not include any explanatory text before or after the JSON.

The response must be a JSON object with this exact structure:
{{
  "style": "one of [sedan, coupe, hatchback, suv, truck, convertible, wagon]",
  "color": "string (body color specification)",
  "doors": "string (number of doors)",
  "material": "one of [steel, aluminum, carbon-fiber, composite, fiberglass]",
  "@paintCode": "string (optional paint code)",
  "@customized": "boolean (optional customization flag)"
}}

Example valid response:
{{
  "style": "sedan",
  "color": "blue",
  "doors": "4",
  "material": "steel",
  "@paintCode": "BLU-001",
  "@customized": "false"
}}

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

        return request

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate body component data against schema requirements."""
        if "error" in component_data:
            return component_data

        # Extract bodyType if nested
        body_type = component_data.get("bodyType", component_data)

        # Required fields for bodyType
        required_fields = ["style", "color", "doors", "material"]

        # Validate required fields
        missing_fields = []
        for field in required_fields:
            if field not in body_type:
                missing_fields.append(field)

        if missing_fields:
            return {
                "error": f"Missing required fields: {missing_fields}",
                "provided_data": body_type,
                "agent": self.name
            }

        # Validate style enum
        valid_styles = ["sedan", "coupe", "hatchback", "suv", "truck", "convertible", "wagon"]
        if body_type["style"] not in valid_styles:
            return {
                "error": f"Invalid style: {body_type['style']}. Must be one of {valid_styles}",
                "provided_data": body_type,
                "agent": self.name
            }

        # Validate material enum
        valid_materials = ["steel", "aluminum", "carbon-fiber", "composite", "fiberglass"]
        if body_type["material"] not in valid_materials:
            return {
                "error": f"Invalid material: {body_type['material']}. Must be one of {valid_materials}",
                "provided_data": body_type,
                "agent": self.name
            }

        # Return validated data
        return {
            "bodyType": body_type,
            "validation_status": "passed",
            "agent": self.name,
            "material_properties": component_data.get("material_properties", {}),
            "integration_notes": component_data.get("integration_notes", {})
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
            # Process engine-specific constraints
            engine_compartment_size = data.get("engine_compartment_size", "medium")
            cooling_requirements = data.get("cooling_requirements", "standard")
            engine_type = data.get("engine_type", "gasoline")

            processed_info.update({
                "engine_compartment_size": engine_compartment_size,
                "cooling_requirements": cooling_requirements,
                "engine_type": engine_type,
                "material_constraints": constraints.get("material_requirements", {}),
                "space_constraints": constraints.get("space_requirements", {}),
                "integration_notes": [
                    f"Engine compartment: {engine_compartment_size}",
                    f"Cooling needs: {cooling_requirements}",
                    f"Engine type: {engine_type}"
                ]
            })

            # Apply constraints to material selection logic
            if cooling_requirements in ["enhanced", "heavy_duty"]:
                processed_info["recommended_materials"] = ["steel", "composite"]
            elif engine_type == "electric":
                processed_info["recommended_materials"] = ["aluminum", "carbon-fiber", "composite"]
            else:
                processed_info["recommended_materials"] = ["any"]

        return processed_info

    def create_body_with_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create body configuration considering engine constraints from handoffs.

        Args:
            requirements: Body configuration requirements

        Returns:
            Dictionary with body configuration data
        """
        try:
            # Process any engine constraints from handoffs
            engine_constraints = None
            for payload in self.handoff_payloads:
                if payload.from_agent == "engine":
                    constraint_data = self._process_handoff_data({
                        "source": payload.from_agent,
                        "data": payload.data,
                        "constraints": payload.constraints
                    })
                    engine_constraints = constraint_data.get("engine_compartment_size", "medium")
                    break

            # Update requirements with engine constraints
            if engine_constraints:
                requirements["engine_constraints"] = engine_constraints

            # Create the body component
            body_result = self.create_component_json(requirements)

            if "error" in body_result:
                return body_result

            # Add constraint processing information
            body_result["constraints_processed"] = {
                "engine_constraints": engine_constraints,
                "handoffs_received": len(self.handoff_payloads)
            }

            return body_result

        except Exception as e:
            return {
                "error": f"Failed to create body with constraints: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    def get_body_style_compatibility(self, style: str) -> Dict[str, Any]:
        """Get compatibility information for a specific body style.

        Args:
            style: Body style to analyze

        Returns:
            Dictionary with compatibility information
        """
        try:
            # Use the tool directly for style information
            style_tool = BodyStyleTool()
            result_json = style_tool._run(style, detailed=True)

            return json.loads(result_json)

        except Exception as e:
            return {
                "error": f"Failed to get body style compatibility: {str(e)}",
                "style": style,
                "agent": self.name
            }

    def get_material_recommendations(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Get material recommendations based on constraints.

        Args:
            constraints: Constraints including engine requirements, performance needs

        Returns:
            Dictionary with material recommendations
        """
        try:
            from tools.body_tools import MATERIAL_PROPERTIES

            engine_constraint = constraints.get("engine_constraint", "medium")
            performance_level = constraints.get("performance_level", "standard")
            style = constraints.get("style", "sedan")

            # Filter materials based on constraints
            suitable_materials = []
            for material, props in MATERIAL_PROPERTIES.items():
                if style in props["suitable_for"]:
                    # Check engine compatibility if provided
                    if "engine_compatibility" in constraints:
                        engine_type = constraints["engine_compatibility"]
                        if engine_type in props.get("engine_compatibility", []):
                            suitable_materials.append({
                                "material": material,
                                "properties": props,
                                "compatibility_score": self._calculate_compatibility_score(
                                    props, engine_constraint, performance_level
                                )
                            })
                    else:
                        suitable_materials.append({
                            "material": material,
                            "properties": props,
                            "compatibility_score": self._calculate_compatibility_score(
                                props, engine_constraint, performance_level
                            )
                        })

            # Sort by compatibility score
            suitable_materials.sort(key=lambda x: x["compatibility_score"], reverse=True)

            return {
                "recommended_materials": suitable_materials,
                "constraints_applied": constraints,
                "agent": self.name
            }

        except Exception as e:
            return {
                "error": f"Failed to get material recommendations: {str(e)}",
                "constraints": constraints,
                "agent": self.name
            }

    def _calculate_compatibility_score(
        self,
        material_props: Dict[str, Any],
        engine_constraint: str,
        performance_level: str
    ) -> float:
        """Calculate a compatibility score for material selection."""
        score = 5.0  # Base score

        # Engine constraint scoring
        if engine_constraint == "large":
            if material_props.get("durability") == "high":
                score += 2.0
            if material_props.get("weight") == "heavy":
                score += 1.0
        elif engine_constraint == "small":
            if material_props.get("weight") in ["light", "very_light"]:
                score += 2.0

        # Performance level scoring
        if performance_level in ["performance", "sport"]:
            if material_props.get("weight") in ["light", "very_light"]:
                score += 1.5
            if material_props.get("durability") == "high":
                score += 1.0
        elif performance_level == "economy":
            if material_props.get("cost") == "low":
                score += 1.5

        return score

    def get_available_body_styles(self) -> Dict[str, Any]:
        """Get list of available body styles and their characteristics.

        Returns:
            Dictionary with available body styles
        """
        from tools.body_tools import BODY_STYLE_CONFIGURATIONS

        return {
            "available_styles": list(BODY_STYLE_CONFIGURATIONS.keys()),
            "style_details": BODY_STYLE_CONFIGURATIONS,
            "agent": self.name
        }