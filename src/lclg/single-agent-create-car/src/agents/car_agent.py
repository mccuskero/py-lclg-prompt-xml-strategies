"""CarAgent that combines all car creation tools into a single agent."""

from typing import Dict, Any, List
import json
import sys
import time
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from tools.engine_tools import EngineConfigurationTool, EngineSpecificationTool
from tools.body_tools import BodyConfigurationTool, BodyStyleTool
from tools.electrical_tools import ElectricalConfigurationTool, ElectricalSystemTool
from tools.tire_tools import TireConfigurationTool, TireSizingTool


class CarAgent(BaseAgent):
    """Single agent that handles all aspects of car creation using multiple tools."""

    def __init__(self, **kwargs):
        super().__init__(name="car_agent", **kwargs)

    def _get_agent_type(self) -> str:
        """Return the agent type for prompt selection."""
        return "car"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the car agent."""
        return """You are a comprehensive car creation agent with access to all the tools needed to design and configure a complete vehicle.

Your capabilities include:
- Engine configuration and specifications (gasoline, diesel, electric, hybrid)
- Body design and customization (exterior, interior, styling)
- Electrical system setup (battery, charging, lighting, wiring)
- Tire and wheel configuration (performance, size, design)

When creating a car:
1. Start by understanding the requirements (vehicle type, performance level, budget, preferences)
2. Use the engine tools to select and configure the appropriate engine
3. Use the body tools to design the exterior and interior
4. Use the electrical tools to set up the electrical systems (especially important for electric/hybrid vehicles)
5. Use the tire tools to select appropriate tires and wheels
6. Ensure all components are compatible and integrated properly

Always provide detailed JSON responses with all component specifications.
Consider dependencies between components (e.g., engine type affects electrical requirements, vehicle type affects tire selection).
"""

    def _setup_tools(self) -> None:
        """Set up all the tools for comprehensive car creation."""
        self.tools = [
            # Engine tools
            EngineConfigurationTool(),
            EngineSpecificationTool(),

            # Body tools
            BodyConfigurationTool(),
            BodyStyleTool(),

            # Electrical tools
            ElectricalConfigurationTool(),
            ElectricalSystemTool(),

            # Tire tools
            TireConfigurationTool(),
            TireSizingTool(),
        ]

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build a comprehensive car creation request."""
        vehicle_type = requirements.get("vehicle_type", "sedan")
        performance_level = requirements.get("performance_level", "standard")
        fuel_preference = requirements.get("fuel_preference", "gasoline")
        budget = requirements.get("budget", "medium")
        special_features = requirements.get("special_features", [])

        request = f"""
Create a complete car configuration based on these requirements:

Vehicle Type: {vehicle_type}
Performance Level: {performance_level}
Fuel Preference: {fuel_preference}
Budget: {budget}
Special Features: {', '.join(special_features) if special_features else 'None specified'}

Please use the available tools to:

1. Configure the engine system appropriate for the vehicle type and performance level
2. Design the body (exterior and interior) suitable for the vehicle type and budget
3. Set up the electrical system compatible with the engine choice
4. Select tires and wheels appropriate for the vehicle and performance requirements

Ensure all components are compatible and integrated. Return a comprehensive JSON response with all component specifications in this format:

{{
  "car_configuration": {{
    "vehicle_info": {{
      "type": "{vehicle_type}",
      "performance_level": "{performance_level}",
      "fuel_preference": "{fuel_preference}",
      "budget": "{budget}"
    }},
    "engine": {{
      // Engine configuration details
    }},
    "body": {{
      "exterior": {{
        // Exterior design details
      }},
      "interior": {{
        // Interior design details
      }}
    }},
    "electrical": {{
      "main_system": {{
        // Main electrical system details
      }},
      "battery": {{
        // Battery configuration details
      }},
      "lighting": {{
        // Lighting system details
      }}
    }},
    "tires_and_wheels": {{
      "tires": {{
        // Tire configuration details
      }},
      "wheels": {{
        // Wheel design details
      }}
    }},
    "integration_notes": {{
      // Notes about component compatibility and integration
    }}
  }}
}}

Use the tools in sequence and ensure compatibility between all components.
"""
        return request

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete car configuration data."""
        if "error" in component_data:
            return component_data

        # Basic validation - ensure we have the main components
        required_sections = ["engine", "body", "electrical", "tires_and_wheels"]
        car_config = component_data.get("car_configuration", {})

        validated_data = component_data.copy()

        # Check for missing sections and add defaults if needed
        for section in required_sections:
            if section not in car_config:
                validated_data["car_configuration"][section] = {
                    "status": "not_configured",
                    "error": f"Missing {section} configuration"
                }

        # Add validation timestamp
        validated_data["validation"] = {
            "timestamp": "auto-generated",
            "status": "validated",
            "components_checked": required_sections
        }

        return validated_data

    def create_complete_car(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete car configuration using all available tools."""
        start_time = time.time()
        if self.enable_logging:
            self.logger.info(
                f"Starting complete car creation",
                vehicle_type=requirements.get('vehicle_type'),
                performance_level=requirements.get('performance_level'),
                fuel_preference=requirements.get('fuel_preference'),
                budget=requirements.get('budget')
            )

        try:
            # Use the base class method to create the complete component
            car_data = self.create_component_json(requirements)

            # Additional post-processing for car-specific validation
            if "error" not in car_data:
                if self.enable_logging:
                    self.logger.debug("Adding car-specific metadata")
                car_data = self._add_car_metadata(car_data, requirements)

            creation_time = time.time() - start_time
            if self.enable_logging:
                success = "error" not in car_data
                self.logger.info(
                    f"Complete car creation {'completed' if success else 'failed'}",
                    success=success,
                    creation_time=creation_time,
                    has_metadata="metadata" in car_data
                )

            return car_data

        except Exception as e:
            creation_time = time.time() - start_time
            if self.enable_logging:
                self.logger.error(
                    f"Failed to create complete car: {str(e)}",
                    error_type=type(e).__name__,
                    creation_time=creation_time,
                    requirements=requirements
                )
            return {
                "error": f"Failed to create complete car: {str(e)}",
                "requirements": requirements
            }

    def _add_car_metadata(self, car_data: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata and summary information to the car configuration."""
        car_config = car_data.get("car_configuration", {})

        # Calculate estimated performance metrics
        performance_summary = self._calculate_performance_summary(car_config)

        # Add metadata
        car_data["metadata"] = {
            "created_by": self.name,
            "creation_method": "single_agent_system",
            "requirements_used": requirements,
            "performance_summary": performance_summary,
            "component_count": len([k for k in car_config.keys() if k != "vehicle_info"]),
            "estimated_compatibility": self._check_component_compatibility(car_config)
        }

        return car_data

    def _calculate_performance_summary(self, car_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated performance metrics from the configuration."""
        summary = {
            "power_rating": "unknown",
            "fuel_efficiency": "unknown",
            "performance_category": "unknown"
        }

        # Extract engine info if available
        engine = car_config.get("engine", {})
        if isinstance(engine, dict) and "horsepower" in engine:
            try:
                hp = int(engine["horsepower"])
                if hp < 200:
                    summary["performance_category"] = "economy"
                elif hp < 300:
                    summary["performance_category"] = "standard"
                elif hp < 400:
                    summary["performance_category"] = "performance"
                else:
                    summary["performance_category"] = "high_performance"

                summary["power_rating"] = f"{hp} HP"
            except (ValueError, KeyError):
                pass

        return summary

    def _check_component_compatibility(self, car_config: Dict[str, Any]) -> str:
        """Check basic compatibility between components."""
        issues = []

        # Check engine-electrical compatibility
        engine = car_config.get("engine", {})
        electrical = car_config.get("electrical", {})

        if isinstance(engine, dict) and isinstance(electrical, dict):
            engine_fuel = engine.get("fuelType", "gasoline")
            electrical_type = electrical.get("main_system", {}).get("voltage_system", "12V")

            if engine_fuel == "electric" and electrical_type != "high-voltage":
                issues.append("Electric engine requires high-voltage electrical system")
            elif engine_fuel == "hybrid" and electrical_type != "hybrid":
                issues.append("Hybrid engine requires hybrid electrical system")

        if issues:
            return f"Issues found: {'; '.join(issues)}"
        else:
            return "compatible"

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Get tools organized by category."""
        return {
            "engine": ["configure_engine", "get_engine_specs"],
            "body": ["configure_body", "get_body_style_info"],
            "electrical": ["configure_electrical_system", "get_electrical_system_info"],
            "tires": ["configure_tires", "get_tire_sizing"]
        }