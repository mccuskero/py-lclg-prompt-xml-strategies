"""JSON Schema loader utility for extracting subtypes from car.json schema."""

import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path


class CarSchemaLoader:
    """Utility class for loading and extracting JSON schema definitions."""

    def __init__(self, schema_path: Optional[str] = None):
        """Initialize the schema loader.

        Args:
            schema_path: Path to the car.json schema file. If None, uses default location.
        """
        if schema_path is None:
            # Default path relative to this file
            self.schema_path = Path(__file__).parent.parent.parent / "schema" / "single" / "car.json"
        else:
            self.schema_path = Path(schema_path)

        self._schema_data: Optional[Dict[str, Any]] = None
        self._load_schema()

    def _load_schema(self) -> None:
        """Load the JSON schema from file."""
        try:
            with open(self.schema_path, 'r') as f:
                self._schema_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")

    def get_schema_definition(self, definition_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific schema definition from the $defs section.

        Args:
            definition_name: Name of the definition (e.g., 'engineType', 'bodyType')

        Returns:
            Dictionary containing the schema definition, or None if not found
        """
        if not self._schema_data:
            return None

        defs = self._schema_data.get("$defs", {})
        return defs.get(definition_name)

    def get_formatted_schema_for_prompt(self, definition_name: str, indent: int = 2) -> str:
        """Get a formatted schema definition suitable for inclusion in prompts.

        Args:
            definition_name: Name of the definition (e.g., 'engineType', 'bodyType')
            indent: Number of spaces for indentation

        Returns:
            Formatted JSON string for prompt inclusion
        """
        definition = self.get_schema_definition(definition_name)
        if not definition:
            return f"Schema definition '{definition_name}' not found"

        # Create a clean version without $schema and title for prompt clarity
        clean_definition = {k: v for k, v in definition.items()
                          if k not in ["$schema", "title"]}

        return json.dumps(clean_definition, indent=indent)

    def get_enum_values(self, definition_name: str) -> Dict[str, list]:
        """Extract enum values from a schema definition.

        Args:
            definition_name: Name of the definition to analyze

        Returns:
            Dictionary mapping field names to their enum values
        """
        definition = self.get_schema_definition(definition_name)
        if not definition:
            return {}

        enum_values = {}
        properties = definition.get("properties", {})

        for field_name, field_def in properties.items():
            if isinstance(field_def, dict):
                # Check for direct enum
                if "enum" in field_def:
                    enum_values[field_name] = field_def["enum"]
                # Check for $ref to enum definitions
                elif "$ref" in field_def:
                    ref_path = field_def["$ref"]
                    if ref_path.startswith("#/$defs/"):
                        ref_name = ref_path.replace("#/$defs/", "")
                        ref_def = self.get_schema_definition(ref_name)
                        if ref_def and "enum" in ref_def:
                            enum_values[field_name] = ref_def["enum"]

        return enum_values

    def get_required_fields(self, definition_name: str) -> list:
        """Get the list of required fields for a schema definition.

        Args:
            definition_name: Name of the definition

        Returns:
            List of required field names
        """
        definition = self.get_schema_definition(definition_name)
        if not definition:
            return []

        return definition.get("required", [])

    def get_field_descriptions(self, definition_name: str) -> Dict[str, str]:
        """Extract field descriptions from a schema definition.

        Args:
            definition_name: Name of the definition

        Returns:
            Dictionary mapping field names to their descriptions
        """
        definition = self.get_schema_definition(definition_name)
        if not definition:
            return {}

        descriptions = {}
        properties = definition.get("properties", {})

        for field_name, field_def in properties.items():
            if isinstance(field_def, dict) and "description" in field_def:
                descriptions[field_name] = field_def["description"]

        return descriptions

    def get_schema_summary(self, definition_name: str) -> Dict[str, Any]:
        """Get a comprehensive summary of a schema definition.

        Args:
            definition_name: Name of the definition

        Returns:
            Dictionary with schema summary information
        """
        definition = self.get_schema_definition(definition_name)
        if not definition:
            return {"error": f"Definition '{definition_name}' not found"}

        return {
            "definition_name": definition_name,
            "description": definition.get("description", ""),
            "type": definition.get("type", "unknown"),
            "required_fields": self.get_required_fields(definition_name),
            "field_descriptions": self.get_field_descriptions(definition_name),
            "enum_values": self.get_enum_values(definition_name),
            "total_properties": len(definition.get("properties", {})),
            "formatted_schema": self.get_formatted_schema_for_prompt(definition_name)
        }

    def get_all_definitions(self) -> Dict[str, Any]:
        """Get all schema definitions available in the schema.

        Returns:
            Dictionary with all schema definitions
        """
        if not self._schema_data:
            return {}

        return self._schema_data.get("$defs", {})

    def get_definition_names(self) -> list:
        """Get a list of all available definition names.

        Returns:
            List of definition names
        """
        return list(self.get_all_definitions().keys())

    def validate_definition_exists(self, definition_name: str) -> bool:
        """Check if a schema definition exists.

        Args:
            definition_name: Name of the definition to check

        Returns:
            True if the definition exists, False otherwise
        """
        return definition_name in self.get_definition_names()

    def get_schema_for_agent_type(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get the appropriate schema definition for an agent type.

        Args:
            agent_type: Agent type (engine, body, tire, electrical)

        Returns:
            Schema definition dictionary or None if not found
        """
        type_mapping = {
            "engine": "engineType",
            "body": "bodyType",
            "tire": "tireType",
            "electrical": "electricalType",
            "supervisor": "carType"
        }

        schema_name = type_mapping.get(agent_type)
        if schema_name:
            return self.get_schema_definition(schema_name)

        return None

    def get_formatted_schema_for_agent(self, agent_type: str, indent: int = 2) -> str:
        """Get formatted schema for a specific agent type.

        Args:
            agent_type: Agent type (engine, body, tire, electrical)
            indent: Indentation for JSON formatting

        Returns:
            Formatted schema string for prompt inclusion
        """
        type_mapping = {
            "engine": "engineType",
            "body": "bodyType",
            "tire": "tireType",
            "electrical": "electricalType",
            "supervisor": "carType"
        }

        schema_name = type_mapping.get(agent_type)
        if schema_name:
            return self.get_formatted_schema_for_prompt(schema_name, indent)

        return f"No schema mapping found for agent type: {agent_type}"


# Global schema loader instance
_schema_loader_instance: Optional[CarSchemaLoader] = None


def get_schema_loader(schema_path: Optional[str] = None) -> CarSchemaLoader:
    """Get a singleton instance of the schema loader.

    Args:
        schema_path: Optional path to schema file

    Returns:
        CarSchemaLoader instance
    """
    global _schema_loader_instance

    if _schema_loader_instance is None or schema_path is not None:
        _schema_loader_instance = CarSchemaLoader(schema_path)

    return _schema_loader_instance


# Convenience functions
def get_schema_for_prompt(definition_name: str, indent: int = 2) -> str:
    """Convenience function to get formatted schema for prompts."""
    loader = get_schema_loader()
    return loader.get_formatted_schema_for_prompt(definition_name, indent)


def get_agent_schema_for_prompt(agent_type: str, indent: int = 2) -> str:
    """Convenience function to get formatted schema for agent prompts."""
    loader = get_schema_loader()
    return loader.get_formatted_schema_for_agent(agent_type, indent)


def get_schema_summary(definition_name: str) -> Dict[str, Any]:
    """Convenience function to get schema summary."""
    loader = get_schema_loader()
    return loader.get_schema_summary(definition_name)