"""Hardcoded tools for tire configuration and sizing."""

from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import Field
import json


# Hardcoded tire configurations by vehicle type and size
TIRE_CONFIGURATIONS = {
    "sedan_standard": {
        "brand": "Michelin",
        "size": "225/60R16",
        "pressure": "32 PSI",
        "treadDepth": "10/32\"",
        "@season": "all-season",
        "@runFlat": False
    },
    "sedan_performance": {
        "brand": "Pirelli",
        "size": "245/40R18",
        "pressure": "36 PSI",
        "treadDepth": "9/32\"",
        "@season": "summer",
        "@runFlat": True
    },
    "coupe_sport": {
        "brand": "Bridgestone",
        "size": "255/35R19",
        "pressure": "38 PSI",
        "treadDepth": "8/32\"",
        "@season": "performance",
        "@runFlat": True
    },
    "coupe_standard": {
        "brand": "Continental",
        "size": "225/55R17",
        "pressure": "34 PSI",
        "treadDepth": "10/32\"",
        "@season": "all-season",
        "@runFlat": False
    },
    "suv_standard": {
        "brand": "Goodyear",
        "size": "265/70R17",
        "pressure": "35 PSI",
        "treadDepth": "12/32\"",
        "@season": "all-season",
        "@runFlat": False
    },
    "suv_performance": {
        "brand": "Michelin",
        "size": "275/45R20",
        "pressure": "38 PSI",
        "treadDepth": "10/32\"",
        "@season": "summer",
        "@runFlat": True
    },
    "truck_work": {
        "brand": "BFGoodrich",
        "size": "265/75R16",
        "pressure": "40 PSI",
        "treadDepth": "14/32\"",
        "@season": "all-season",
        "@runFlat": False
    },
    "truck_performance": {
        "brand": "Nitto",
        "size": "285/55R20",
        "pressure": "42 PSI",
        "treadDepth": "12/32\"",
        "@season": "summer",
        "@runFlat": False
    },
    "hatchback_eco": {
        "brand": "Ecopia",
        "size": "195/65R15",
        "pressure": "30 PSI",
        "treadDepth": "11/32\"",
        "@season": "all-season",
        "@runFlat": False
    },
    "hatchback_sport": {
        "brand": "Yokohama",
        "size": "215/45R17",
        "pressure": "35 PSI",
        "treadDepth": "9/32\"",
        "@season": "performance",
        "@runFlat": True
    },
    "convertible_luxury": {
        "brand": "Pirelli",
        "size": "245/40R19",
        "pressure": "36 PSI",
        "treadDepth": "9/32\"",
        "@season": "summer",
        "@runFlat": True
    },
    "wagon_utility": {
        "brand": "Michelin",
        "size": "235/60R18",
        "pressure": "34 PSI",
        "treadDepth": "11/32\"",
        "@season": "all-season",
        "@runFlat": False
    }
}

# Tire brand characteristics
TIRE_BRANDS = {
    "Michelin": {"focus": "premium", "specialty": "longevity", "price_range": "high"},
    "Pirelli": {"focus": "performance", "specialty": "sport_handling", "price_range": "high"},
    "Bridgestone": {"focus": "technology", "specialty": "innovation", "price_range": "medium-high"},
    "Continental": {"focus": "safety", "specialty": "wet_weather", "price_range": "medium-high"},
    "Goodyear": {"focus": "versatility", "specialty": "all_terrain", "price_range": "medium"},
    "BFGoodrich": {"focus": "durability", "specialty": "off_road", "price_range": "medium"},
    "Yokohama": {"focus": "performance", "specialty": "racing", "price_range": "medium"},
    "Nitto": {"focus": "custom", "specialty": "truck_sport", "price_range": "medium"},
    "Ecopia": {"focus": "efficiency", "specialty": "fuel_economy", "price_range": "low-medium"}
}

# Seasonal characteristics
SEASONAL_CHARACTERISTICS = {
    "all-season": {"temp_range": "-10 to 85°F", "versatility": "high", "specialty": "general_purpose"},
    "summer": {"temp_range": "45 to 100°F", "versatility": "medium", "specialty": "dry_wet_performance"},
    "winter": {"temp_range": "-20 to 45°F", "versatility": "low", "specialty": "snow_ice_traction"},
    "performance": {"temp_range": "50 to 95°F", "versatility": "low", "specialty": "track_sport_driving"}
}


class TireConfigurationTool(BaseTool):
    """Tool for configuring tire specifications based on body style and performance requirements."""

    name: str = "configure_tires"
    description: str = ("Configure tire specifications including brand, size, pressure, and seasonal type "
                       "based on body style, performance level, and climate requirements.")

    def _run(
        self,
        body_style: str = "sedan",
        performance_level: str = "standard",
        climate_preference: str = "all-season",
        weight_class: str = "medium",
        run_flat_required: bool = False,
        **kwargs
    ) -> str:
        """Configure tires based on vehicle and performance requirements.

        Args:
            body_style: Vehicle body style (sedan, coupe, suv, truck, hatchback, convertible, wagon)
            performance_level: Performance category (economy, standard, performance, sport)
            climate_preference: Climate/seasonal preference (all-season, summer, winter, performance)
            weight_class: Vehicle weight class (light, medium, heavy)
            run_flat_required: Whether run-flat capability is required

        Returns:
            JSON string with tire configuration
        """
        try:
            # Determine tire configuration key
            config_key = self._select_tire_configuration(
                body_style, performance_level, climate_preference, weight_class
            )

            # Get base configuration
            tire_config = TIRE_CONFIGURATIONS.get(config_key, TIRE_CONFIGURATIONS["sedan_standard"]).copy()

            # Apply run-flat requirement
            if run_flat_required:
                tire_config["@runFlat"] = True

            # Apply climate preference
            if climate_preference in SEASONAL_CHARACTERISTICS:
                tire_config["@season"] = climate_preference

            # Adjust pressure for weight class
            tire_config["pressure"] = self._adjust_pressure_for_weight(tire_config["pressure"], weight_class)

            # Get additional specifications
            brand_info = TIRE_BRANDS.get(tire_config["brand"], {})
            seasonal_info = SEASONAL_CHARACTERISTICS.get(tire_config["@season"], {})

            # Calculate sizing constraints for other components
            sizing_constraints = self._calculate_sizing_constraints(tire_config["size"])

            result = {
                "tireType": tire_config,
                "brand_characteristics": brand_info,
                "seasonal_characteristics": seasonal_info,
                "sizing_constraints": sizing_constraints,
                "configuration_notes": {
                    "selected_config": config_key,
                    "weight_class": weight_class,
                    "run_flat_applied": run_flat_required
                }
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Tire configuration failed: {str(e)}",
                "fallback": TIRE_CONFIGURATIONS["sedan_standard"]
            })

    def _select_tire_configuration(self, body_style: str, performance_level: str, climate: str, weight: str) -> str:
        """Select appropriate tire configuration based on requirements."""

        # Performance level mapping
        if performance_level in ["performance", "sport"]:
            performance_suffix = "_performance" if body_style in ["sedan", "suv", "truck"] else "_sport"
        elif performance_level == "economy" and body_style == "hatchback":
            performance_suffix = "_eco"
        elif body_style == "convertible":
            performance_suffix = "_luxury"
        elif body_style == "wagon":
            performance_suffix = "_utility"
        elif body_style == "truck" and performance_level == "standard":
            performance_suffix = "_work"
        else:
            performance_suffix = "_standard"

        # Construct configuration key
        config_key = f"{body_style}{performance_suffix}"

        # Validate key exists
        if config_key not in TIRE_CONFIGURATIONS:
            # Fallback logic
            fallback_keys = [k for k in TIRE_CONFIGURATIONS.keys() if k.startswith(body_style)]
            if fallback_keys:
                config_key = fallback_keys[0]
            else:
                config_key = "sedan_standard"

        return config_key

    def _adjust_pressure_for_weight(self, base_pressure: str, weight_class: str) -> str:
        """Adjust tire pressure based on vehicle weight class."""
        try:
            # Extract numeric pressure value
            pressure_value = int(base_pressure.split()[0])

            # Adjust based on weight class
            if weight_class == "heavy":
                pressure_value += 3
            elif weight_class == "light":
                pressure_value -= 2

            # Ensure reasonable range
            pressure_value = max(28, min(45, pressure_value))

            return f"{pressure_value} PSI"

        except (ValueError, IndexError):
            return base_pressure  # Return original if parsing fails

    def _calculate_sizing_constraints(self, tire_size: str) -> Dict[str, Any]:
        """Calculate sizing constraints for integration with other components."""
        try:
            # Parse tire size (e.g., "225/60R16")
            parts = tire_size.split('/')
            width = int(parts[0])

            aspect_ratio_and_diameter = parts[1].split('R')
            aspect_ratio = int(aspect_ratio_and_diameter[0])
            rim_diameter = int(aspect_ratio_and_diameter[1])

            # Calculate overall diameter
            sidewall_height = (width * aspect_ratio) / 100
            overall_diameter = (sidewall_height * 2) + (rim_diameter * 25.4)  # Convert to mm

            return {
                "width_mm": width,
                "aspect_ratio": aspect_ratio,
                "rim_diameter_inches": rim_diameter,
                "overall_diameter_mm": round(overall_diameter, 1),
                "clearance_requirements": {
                    "wheel_well_width": width + 50,  # Add clearance
                    "wheel_well_diameter": round(overall_diameter + 100, 1),  # Add clearance
                    "suspension_clearance": "standard"
                }
            }

        except (ValueError, IndexError):
            return {
                "error": f"Could not parse tire size: {tire_size}",
                "clearance_requirements": {"suspension_clearance": "standard"}
            }


class TireSizingTool(BaseTool):
    """Tool for getting detailed tire sizing information and compatibility."""

    name: str = "get_tire_sizing"
    description: str = ("Get detailed tire sizing information, compatibility with different body styles, "
                       "and constraints for wheel well design and suspension setup.")

    def _run(self, tire_size: str = "225/60R16", detailed_analysis: bool = True, **kwargs) -> str:
        """Get detailed tire sizing information.

        Args:
            tire_size: Tire size specification (e.g., "225/60R16")
            detailed_analysis: Whether to include detailed compatibility analysis

        Returns:
            JSON string with tire sizing information
        """
        try:
            # Find configurations using this tire size
            matching_configs = {}
            for config_name, config_data in TIRE_CONFIGURATIONS.items():
                if config_data["size"] == tire_size:
                    matching_configs[config_name] = config_data

            # Calculate sizing details
            sizing_details = self._calculate_sizing_constraints(tire_size)

            result = {
                "tire_size": tire_size,
                "sizing_details": sizing_details,
                "matching_configurations": matching_configs
            }

            if detailed_analysis:
                # Add compatibility analysis
                compatibility = self._analyze_compatibility(tire_size)
                performance_impact = self._analyze_performance_impact(tire_size)

                result.update({
                    "compatibility_analysis": compatibility,
                    "performance_impact": performance_impact,
                    "alternative_sizes": self._get_alternative_sizes(tire_size),
                    "installation_notes": self._get_installation_notes(tire_size)
                })

            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to analyze tire sizing: {str(e)}",
                "tire_size": tire_size
            })

    def _analyze_compatibility(self, tire_size: str) -> Dict[str, Any]:
        """Analyze compatibility with different vehicle types."""
        try:
            parts = tire_size.split('/')
            width = int(parts[0])
            rim_diameter = int(parts[1].split('R')[1])

            compatibility = {
                "compact_cars": width <= 215 and rim_diameter <= 17,
                "sedans": 195 <= width <= 245 and 15 <= rim_diameter <= 19,
                "suvs": 235 <= width <= 285 and 16 <= rim_diameter <= 22,
                "trucks": 245 <= width <= 315 and 16 <= rim_diameter <= 22,
                "sports_cars": 225 <= width <= 295 and 17 <= rim_diameter <= 21,
                "performance_applications": rim_diameter >= 18 and width >= 225
            }

            return compatibility

        except (ValueError, IndexError):
            return {"error": f"Could not analyze compatibility for size: {tire_size}"}

    def _analyze_performance_impact(self, tire_size: str) -> Dict[str, str]:
        """Analyze performance characteristics of tire size."""
        try:
            parts = tire_size.split('/')
            width = int(parts[0])
            aspect_ratio = int(parts[1].split('R')[0])
            rim_diameter = int(parts[1].split('R')[1])

            impact = {}

            # Width impact
            if width >= 245:
                impact["traction"] = "high"
                impact["fuel_economy"] = "reduced"
            elif width <= 195:
                impact["traction"] = "standard"
                impact["fuel_economy"] = "improved"
            else:
                impact["traction"] = "good"
                impact["fuel_economy"] = "standard"

            # Aspect ratio impact
            if aspect_ratio <= 45:
                impact["handling"] = "excellent"
                impact["comfort"] = "firm"
            elif aspect_ratio >= 65:
                impact["handling"] = "comfortable"
                impact["comfort"] = "soft"
            else:
                impact["handling"] = "balanced"
                impact["comfort"] = "moderate"

            # Rim diameter impact
            if rim_diameter >= 19:
                impact["appearance"] = "aggressive"
                impact["replacement_cost"] = "high"
            elif rim_diameter <= 16:
                impact["appearance"] = "conservative"
                impact["replacement_cost"] = "low"
            else:
                impact["appearance"] = "balanced"
                impact["replacement_cost"] = "moderate"

            return impact

        except (ValueError, IndexError):
            return {"error": f"Could not analyze performance impact for size: {tire_size}"}

    def _get_alternative_sizes(self, tire_size: str) -> List[str]:
        """Get alternative tire sizes with similar characteristics."""
        try:
            parts = tire_size.split('/')
            width = int(parts[0])
            rim_diameter = int(parts[1].split('R')[1])

            alternatives = []

            # Plus sizing options (larger wheel, lower profile)
            if rim_diameter < 20:
                for new_rim in [rim_diameter + 1, rim_diameter + 2]:
                    # Calculate new aspect ratio to maintain overall diameter
                    # This is a simplified calculation
                    alternatives.append(f"{width}/45R{new_rim}")

            # Width variations
            for width_delta in [-10, -20, 10, 20]:
                new_width = width + width_delta
                if 175 <= new_width <= 315:  # Reasonable width range
                    alternatives.append(f"{new_width}/{parts[1]}")

            # Remove duplicates and the original size
            alternatives = list(set(alternatives))
            if tire_size in alternatives:
                alternatives.remove(tire_size)

            return alternatives[:5]  # Return up to 5 alternatives

        except (ValueError, IndexError):
            return []

    def _get_installation_notes(self, tire_size: str) -> Dict[str, str]:
        """Get installation and compatibility notes."""
        try:
            parts = tire_size.split('/')
            width = int(parts[0])
            rim_diameter = int(parts[1].split('R')[1])

            notes = {}

            if width >= 275:
                notes["wheel_well"] = "Verify adequate wheel well clearance for wide tires"

            if rim_diameter >= 20:
                notes["suspension"] = "Check suspension compatibility with low-profile tires"

            if rim_diameter <= 15:
                notes["brakes"] = "Ensure adequate clearance for brake components"

            notes["balancing"] = "Professional balancing recommended for optimal performance"
            notes["pressure_monitoring"] = "TPMS sensors may need recalibration"

            return notes

        except (ValueError, IndexError):
            return {"general": "Professional installation recommended"}