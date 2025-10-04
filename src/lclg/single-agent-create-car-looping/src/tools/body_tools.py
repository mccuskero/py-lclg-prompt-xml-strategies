"""Hardcoded tools for body configuration and styling."""

from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import Field
import json
import sys
from pathlib import Path

# Add utils module to path for logging
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_config import ToolLogger


# Hardcoded body style configurations
BODY_STYLE_CONFIGURATIONS = {
    "sedan": {
        "style": "sedan",
        "doors": "4",
        "material": "steel",
        "color": "silver",
        "@paintCode": "SLV-2024",
        "@customized": False
    },
    "coupe": {
        "style": "coupe",
        "doors": "2",
        "material": "aluminum",
        "color": "red",
        "@paintCode": "RED-SPORT",
        "@customized": True
    },
    "hatchback": {
        "style": "hatchback",
        "doors": "4",
        "material": "steel",
        "color": "blue",
        "@paintCode": "BLU-ECO",
        "@customized": False
    },
    "suv": {
        "style": "suv",
        "doors": "4",
        "material": "composite",
        "color": "black",
        "@paintCode": "BLK-PREM",
        "@customized": True
    },
    "truck": {
        "style": "truck",
        "doors": "4",
        "material": "steel",
        "color": "white",
        "@paintCode": "WHT-WORK",
        "@customized": False
    },
    "convertible": {
        "style": "convertible",
        "doors": "2",
        "material": "carbon-fiber",
        "color": "yellow",
        "@paintCode": "YEL-PERF",
        "@customized": True
    },
    "wagon": {
        "style": "wagon",
        "doors": "4",
        "material": "aluminum",
        "color": "green",
        "@paintCode": "GRN-UTIL",
        "@customized": False
    }
}

# Color options database
COLOR_DATABASE = {
    "performance": ["red", "yellow", "orange", "black"],
    "luxury": ["black", "white", "silver", "pearl"],
    "economy": ["blue", "silver", "white", "gray"],
    "utility": ["white", "black", "green", "blue"],
    "custom": ["purple", "orange", "lime", "gold"]
}

# Material properties and constraints
MATERIAL_PROPERTIES = {
    "steel": {
        "weight": "heavy",
        "cost": "low",
        "durability": "high",
        "suitable_for": ["sedan", "truck", "suv"],
        "engine_compatibility": ["v6_gasoline", "v8_gasoline", "diesel_v6"]
    },
    "aluminum": {
        "weight": "light",
        "cost": "medium",
        "durability": "medium",
        "suitable_for": ["coupe", "wagon", "convertible"],
        "engine_compatibility": ["v4_turbo", "v6_gasoline", "hybrid"]
    },
    "carbon-fiber": {
        "weight": "very_light",
        "cost": "high",
        "durability": "high",
        "suitable_for": ["coupe", "convertible"],
        "engine_compatibility": ["v4_turbo", "electric"]
    },
    "composite": {
        "weight": "medium",
        "cost": "medium",
        "durability": "high",
        "suitable_for": ["suv", "hatchback"],
        "engine_compatibility": ["v6_gasoline", "hybrid", "electric"]
    },
    "fiberglass": {
        "weight": "light",
        "cost": "low",
        "durability": "medium",
        "suitable_for": ["convertible", "coupe"],
        "engine_compatibility": ["v4_turbo", "electric"]
    }
}


class BodyConfigurationTool(BaseTool):
    """Tool for configuring body style and materials based on requirements and engine constraints."""

    name: str = "configure_body"
    description: str = ("Configure body style, materials, doors, and color based on vehicle requirements "
                       "and engine compartment constraints. Returns complete bodyType JSON.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = ToolLogger(self.name)

    @property
    def logger(self):
        """Get the logger instance."""
        return self._logger

    def _run(
        self,
        style: str = "sedan",
        engine_constraints: Optional[str] = None,
        performance_level: str = "standard",
        customization_level: str = "standard",
        color_preference: str = "auto",
        **kwargs
    ) -> str:
        """Configure body based on requirements and constraints.

        Args:
            style: Body style (sedan, coupe, hatchback, suv, truck, convertible, wagon)
            engine_constraints: Engine compartment size constraints (small, medium, large)
            performance_level: Performance category (economy, standard, performance, luxury)
            customization_level: Level of customization (basic, standard, premium, custom)
            color_preference: Color preference or "auto" for automatic selection

        Returns:
            JSON string with body configuration
        """
        self.logger.debug(f"Starting body configuration: style={style}, engine_constraints={engine_constraints}, performance={performance_level}")

        try:
            # Get base configuration for the style
            if style not in BODY_STYLE_CONFIGURATIONS:
                self.logger.debug(f"Style '{style}' not found, defaulting to 'sedan'")
                style = "sedan"  # Default fallback

            body_config = BODY_STYLE_CONFIGURATIONS[style].copy()
            self.logger.debug(f"Retrieved base body configuration for style '{style}'")

            # Apply engine constraints to material selection
            if engine_constraints:
                self.logger.debug(f"Applying engine constraints: {engine_constraints}")
                material = self._select_material_for_engine(style, engine_constraints, performance_level)
                body_config["material"] = material
                self.logger.debug(f"Selected material: {material}")

            # Apply color selection
            if color_preference != "auto":
                self.logger.debug(f"Using custom color preference: {color_preference}")
                body_config["color"] = color_preference
            else:
                body_config["color"] = self._select_color(performance_level, customization_level)
                self.logger.debug(f"Auto-selected color: {body_config['color']}")

            # Apply customization
            body_config["@customized"] = customization_level in ["premium", "custom"]
            self.logger.debug(f"Customization level: {customization_level}, customized={body_config['@customized']}")

            # Generate appropriate paint code
            body_config["@paintCode"] = self._generate_paint_code(body_config["color"], customization_level)

            # Add material properties for other agents
            material_props = MATERIAL_PROPERTIES.get(body_config["material"], {})

            result = {
                "bodyType": body_config,
                "material_properties": material_props,
                "constraints_applied": {
                    "engine_constraints": engine_constraints,
                    "performance_level": performance_level,
                    "customization_level": customization_level
                },
                "integration_notes": self._get_body_integration_notes(body_config, material_props)
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Body configuration failed: {str(e)}",
                "fallback": BODY_STYLE_CONFIGURATIONS["sedan"]
            })

    def _select_material_for_engine(self, style: str, engine_constraint: str, performance_level: str) -> str:
        """Select appropriate material based on engine constraints."""
        # Filter materials suitable for this body style
        suitable_materials = []
        for material, props in MATERIAL_PROPERTIES.items():
            if style in props["suitable_for"]:
                suitable_materials.append(material)

        if not suitable_materials:
            return "steel"  # Default fallback

        # Apply engine constraint logic
        if engine_constraint == "large":
            # Large engines need stronger materials
            if "steel" in suitable_materials:
                return "steel"
            elif "composite" in suitable_materials:
                return "composite"
        elif engine_constraint == "small":
            # Small engines can use lighter materials
            if performance_level == "performance" and "carbon-fiber" in suitable_materials:
                return "carbon-fiber"
            elif "aluminum" in suitable_materials:
                return "aluminum"

        # Default to first suitable material
        return suitable_materials[0]

    def _select_color(self, performance_level: str, customization_level: str) -> str:
        """Select appropriate color based on performance and customization level."""
        if customization_level == "custom":
            colors = COLOR_DATABASE.get("custom", ["purple"])
        else:
            colors = COLOR_DATABASE.get(performance_level, COLOR_DATABASE["economy"])

        # Return first color from the appropriate category
        return colors[0]

    def _generate_paint_code(self, color: str, customization_level: str) -> str:
        """Generate paint code based on color and customization."""
        color_codes = {
            "red": "RED", "blue": "BLU", "green": "GRN", "yellow": "YEL",
            "black": "BLK", "white": "WHT", "silver": "SLV", "gray": "GRY",
            "purple": "PRP", "orange": "ORG", "lime": "LIM", "gold": "GLD", "pearl": "PRL"
        }

        color_code = color_codes.get(color, "UNK")

        if customization_level == "custom":
            suffix = "CUST"
        elif customization_level == "premium":
            suffix = "PREM"
        else:
            suffix = "STD"

        return f"{color_code}-{suffix}"

    def _get_body_integration_notes(self, body_config: Dict[str, Any], material_props: Dict[str, Any]) -> Dict[str, str]:
        """Get integration notes for other agents."""
        notes = {
            "tire_agent": f"Body style: {body_config['style']} - affects tire sizing",
            "electrical_agent": f"Material: {body_config['material']} - affects wiring routing"
        }

        # Add material-specific notes
        if material_props.get("weight") == "very_light":
            notes["tire_agent"] += " - Consider performance tires for light body"
        elif material_props.get("weight") == "heavy":
            notes["tire_agent"] += " - May need larger tire size for weight support"

        if body_config["style"] in ["convertible", "coupe"]:
            notes["electrical_agent"] += " - Special attention to weatherproofing"

        return notes


class BodyStyleTool(BaseTool):
    """Tool for getting detailed body style specifications and compatibility information."""

    name: str = "get_body_style_info"
    description: str = ("Get detailed information about body styles, material properties, "
                       "and compatibility with different engine types and performance requirements.")

    def _run(self, style: str = "sedan", detailed: bool = True, **kwargs) -> str:
        """Get detailed body style information.

        Args:
            style: Body style to analyze
            detailed: Whether to include detailed compatibility information

        Returns:
            JSON string with body style information
        """
        try:
            if style not in BODY_STYLE_CONFIGURATIONS:
                available_styles = list(BODY_STYLE_CONFIGURATIONS.keys())
                return json.dumps({
                    "error": f"Unknown style: {style}",
                    "available_styles": available_styles
                })

            style_config = BODY_STYLE_CONFIGURATIONS[style]

            result = {
                "style_configuration": style_config,
                "style_name": style
            }

            if detailed:
                # Add material compatibility
                compatible_materials = []
                for material, props in MATERIAL_PROPERTIES.items():
                    if style in props["suitable_for"]:
                        compatible_materials.append({
                            "material": material,
                            "properties": props
                        })

                # Add performance characteristics
                performance_notes = self._get_style_performance_notes(style)

                result.update({
                    "compatible_materials": compatible_materials,
                    "performance_characteristics": performance_notes,
                    "typical_use_cases": self._get_use_cases(style),
                    "customization_options": self._get_customization_options(style)
                })

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to get body style info: {str(e)}",
                "style": style
            })

    def _get_style_performance_notes(self, style: str) -> Dict[str, Any]:
        """Get performance characteristics for a body style."""
        characteristics = {
            "sedan": {"aerodynamics": "good", "cargo_space": "medium", "passenger_capacity": "5"},
            "coupe": {"aerodynamics": "excellent", "cargo_space": "small", "passenger_capacity": "4"},
            "hatchback": {"aerodynamics": "good", "cargo_space": "flexible", "passenger_capacity": "5"},
            "suv": {"aerodynamics": "fair", "cargo_space": "large", "passenger_capacity": "7"},
            "truck": {"aerodynamics": "poor", "cargo_space": "bed", "passenger_capacity": "5"},
            "convertible": {"aerodynamics": "variable", "cargo_space": "small", "passenger_capacity": "4"},
            "wagon": {"aerodynamics": "good", "cargo_space": "large", "passenger_capacity": "7"}
        }

        return characteristics.get(style, {"aerodynamics": "unknown", "cargo_space": "unknown", "passenger_capacity": "unknown"})

    def _get_use_cases(self, style: str) -> List[str]:
        """Get typical use cases for a body style."""
        use_cases = {
            "sedan": ["daily commuting", "family transport", "business use"],
            "coupe": ["performance driving", "weekend recreation", "style statement"],
            "hatchback": ["urban driving", "cargo flexibility", "fuel efficiency"],
            "suv": ["family transport", "off-road capability", "cargo hauling"],
            "truck": ["work vehicle", "towing", "cargo transport"],
            "convertible": ["recreational driving", "fair weather", "luxury"],
            "wagon": ["family transport", "cargo capacity", "versatility"]
        }

        return use_cases.get(style, ["general purpose"])

    def _get_customization_options(self, style: str) -> Dict[str, List[str]]:
        """Get customization options available for a body style."""
        return {
            "color_categories": list(COLOR_DATABASE.keys()),
            "material_options": [m for m, props in MATERIAL_PROPERTIES.items() if style in props["suitable_for"]],
            "typical_upgrades": self._get_typical_upgrades(style)
        }

    def _get_typical_upgrades(self, style: str) -> List[str]:
        """Get typical upgrade options for a body style."""
        upgrades = {
            "sedan": ["sunroof", "premium paint", "chrome trim"],
            "coupe": ["sport package", "performance stripes", "custom wheels"],
            "hatchback": ["roof rails", "sport suspension", "fog lights"],
            "suv": ["running boards", "roof rack", "tow package"],
            "truck": ["bed liner", "tonneau cover", "lift kit"],
            "convertible": ["premium top", "heated seats", "performance package"],
            "wagon": ["roof rails", "cargo organizer", "all-weather package"]
        }

        return upgrades.get(style, ["basic upgrades"])