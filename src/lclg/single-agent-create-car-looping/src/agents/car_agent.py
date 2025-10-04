"""CarAgent that combines all car creation tools into a single agent with interactive looping."""

from typing import Dict, Any, List
import json
import logging
from pathlib import Path

from agents.base_agent import BaseAgent
from tools.engine_tools import EngineConfigurationTool, EngineSpecificationTool
from tools.body_tools import BodyConfigurationTool, BodyStyleTool
from tools.electrical_tools import ElectricalConfigurationTool, ElectricalSystemTool
from tools.tire_tools import TireConfigurationTool, TireSizingTool
from prompts.prompts import (
    CAR_AGENT_SYSTEM_PROMPT,
    CAR_AGENT_HUMAN_PROMPT
)


logger = logging.getLogger(__name__)


class CarAgent(BaseAgent):
    """Single agent that handles all aspects of car creation using multiple tools with context memory."""

    def __init__(self, **kwargs):
        super().__init__(name="car_agent", **kwargs)

    def _get_agent_type(self) -> str:
        """Return the agent type for prompt selection."""
        return "car"

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

    def _setup_prompts(self) -> None:
        """Set up the system and human prompt templates."""
        # System prompt template (imported from prompts module)
        self.system_prompt_template = CAR_AGENT_SYSTEM_PROMPT

        # Human prompt template with context support (imported from prompts module)
        self.human_prompt_template = CAR_AGENT_HUMAN_PROMPT

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete car configuration data."""
        if "error" in component_data:
            return component_data

        # Basic validation - ensure we have the main components
        required_sections = ["engine", "body", "electrical", "tires_and_wheels"]
        car_config = component_data.get("car_configuration", {})

        validated_data = component_data.copy()

        # Check for missing sections and add defaults if needed
        missing_sections = []
        for section in required_sections:
            if section not in car_config:
                missing_sections.append(section)
                validated_data.setdefault("car_configuration", {})[section] = {
                    "status": "not_configured",
                    "error": f"Missing {section} configuration"
                }

        # Add validation metadata
        validated_data["validation"] = {
            "status": "validated" if not missing_sections else "incomplete",
            "components_checked": required_sections,
            "missing_sections": missing_sections
        }

        return validated_data

    def create_complete_car(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete car configuration using all available tools."""
        if self.enable_logging:
            logger.info(
                "Starting complete car creation",
                extra={
                    "vehicle_type": requirements.get('vehicle_type'),
                    "performance_level": requirements.get('performance_level'),
                    "fuel_preference": requirements.get('fuel_preference'),
                    "budget": requirements.get('budget')
                }
            )
            logger.debug(f"Complete requirements: {requirements}")
            logger.debug(f"Current context items: {len(self.memory.context_data)}")
            logger.debug(f"Current message history: {len(self.memory.messages)}")

        try:
            # Use the base class method to invoke LLM with context
            if self.enable_logging:
                logger.debug("Invoking LLM with requirements and context")

            car_data = self.invoke_llm(requirements)

            if self.enable_logging:
                logger.debug(f"LLM invocation completed, received data with keys: {list(car_data.keys())}")

            # Additional post-processing for car-specific validation
            if "error" not in car_data:
                if self.enable_logging:
                    logger.debug("No errors in car data, adding car-specific metadata")
                car_data = self._add_car_metadata(car_data, requirements)
                if self.enable_logging:
                    logger.debug("Car metadata added successfully")
            else:
                if self.enable_logging:
                    logger.warning(f"Error in car data: {car_data.get('error')}")

            if self.enable_logging:
                success = "error" not in car_data
                logger.info(
                    f"Complete car creation {'completed' if success else 'failed'}",
                    extra={
                        "success": success,
                        "has_metadata": "metadata" in car_data
                    }
                )
                logger.debug(f"Final car data structure: {list(car_data.keys())}")

            return car_data

        except Exception as e:
            if self.enable_logging:
                logger.error(
                    f"Failed to create complete car: {str(e)}",
                    exc_info=True,
                    extra={"requirements": requirements}
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
            "creation_method": "single_agent_interactive_system",
            "requirements_used": requirements,
            "performance_summary": performance_summary,
            "component_count": len([k for k in car_config.keys() if k != "vehicle_info"]),
            "estimated_compatibility": self._check_component_compatibility(car_config),
            "context_items": len(self.memory.context_data),
            "interaction_count": len(self.memory.messages)
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
                hp_str = str(engine["horsepower"]).split()[0]  # Handle "180 HP" format
                hp = int(hp_str)
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

            if engine_fuel == "electric" and "high" not in electrical_type.lower():
                issues.append("Electric engine requires high-voltage electrical system")
            elif engine_fuel == "hybrid" and "hybrid" not in electrical_type.lower():
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

    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user request in the interactive session.

        Args:
            user_input: The user's input text

        Returns:
            Dict containing the response or next action
        """
        # Parse user input into requirements
        requirements = self._parse_user_input(user_input)

        # Create car configuration with context
        result = self.create_complete_car(requirements)

        return result

    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input into structured requirements.

        Args:
            user_input: The user's input text

        Returns:
            Dict of parsed requirements
        """
        # Simple keyword-based parsing
        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "standard",
            "fuel_preference": "gasoline",
            "budget": "medium",
            "special_features": []
        }

        user_lower = user_input.lower()

        # Vehicle types
        if "suv" in user_lower:
            requirements["vehicle_type"] = "suv"
        elif "truck" in user_lower:
            requirements["vehicle_type"] = "truck"
        elif "coupe" in user_lower:
            requirements["vehicle_type"] = "coupe"
        elif "sedan" in user_lower:
            requirements["vehicle_type"] = "sedan"

        # Performance levels
        if "sport" in user_lower or "performance" in user_lower or "fast" in user_lower:
            requirements["performance_level"] = "performance"
        elif "economy" in user_lower or "efficient" in user_lower:
            requirements["performance_level"] = "economy"

        # Fuel types
        if "electric" in user_lower or "ev" in user_lower:
            requirements["fuel_preference"] = "electric"
        elif "hybrid" in user_lower:
            requirements["fuel_preference"] = "hybrid"
        elif "diesel" in user_lower:
            requirements["fuel_preference"] = "diesel"

        # Budget
        if "luxury" in user_lower or "premium" in user_lower or "high-end" in user_lower:
            requirements["budget"] = "high"
        elif "budget" in user_lower or "affordable" in user_lower or "cheap" in user_lower:
            requirements["budget"] = "low"

        # Store the original user input
        requirements["user_input"] = user_input

        return requirements
