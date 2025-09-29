"""Unit tests for schema-driven prompt functionality."""

import pytest
from unittest.mock import patch, Mock

from prompts.prompts_from_json_schema import (
    SchemaCarCreationPrompts,
    get_schema_agent_prompt,
    get_schema_car_creation_task_prompt,
    get_schema_validation_prompt,
    get_schema_agent_handoff_prompt,
    get_schema_summary_for_agent,
    validate_schema_availability
)


class TestSchemaCarCreationPrompts:
    """Test the SchemaCarCreationPrompts class."""

    def test_get_engine_schema(self):
        """Test engine schema retrieval."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object", "properties": {"displacement": {"type": "string"}}}'
            result = SchemaCarCreationPrompts._get_engine_schema()
            mock_get.assert_called_once_with("engine")
            assert "displacement" in result

    def test_get_body_schema(self):
        """Test body schema retrieval."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object", "properties": {"style": {"type": "string"}}}'
            result = SchemaCarCreationPrompts._get_body_schema()
            mock_get.assert_called_once_with("body")
            assert "style" in result

    def test_get_tire_schema(self):
        """Test tire schema retrieval."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object", "properties": {"brand": {"type": "string"}}}'
            result = SchemaCarCreationPrompts._get_tire_schema()
            mock_get.assert_called_once_with("tire")
            assert "brand" in result

    def test_get_electrical_schema(self):
        """Test electrical schema retrieval."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object", "properties": {"batteryVoltage": {"type": "string"}}}'
            result = SchemaCarCreationPrompts._get_electrical_schema()
            mock_get.assert_called_once_with("electrical")
            assert "batteryVoltage" in result

    def test_get_car_schema(self):
        """Test car schema retrieval."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object", "properties": {"Engine": {"$ref": "#/$defs/engineType"}}}'
            result = SchemaCarCreationPrompts._get_car_schema()
            mock_get.assert_called_once_with("supervisor")
            assert "Engine" in result

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_supervisor_formatted_prompt')
    def test_get_supervisor_formatted_prompt(self, mock_formatted_prompt):
        """Test supervisor formatted prompt generation."""
        mock_formatted_prompt.return_value = "Formatted supervisor prompt"

        result = SchemaCarCreationPrompts._get_supervisor_formatted_prompt(
            "SupervisorAgent", "System prompt", "tool1, tool2"
        )

        mock_formatted_prompt.assert_called_once_with(
            "SupervisorAgent", "System prompt", "tool1, tool2"
        )
        assert result == "Formatted supervisor prompt"

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_engine_schema')
    def test_get_engine_formatted_prompt(self, mock_engine_schema):
        """Test engine formatted prompt generation."""
        mock_engine_schema.return_value = '{"type": "object"}'

        result = SchemaCarCreationPrompts._get_engine_formatted_prompt(
            "EngineAgent", "System prompt", "tool1, tool2"
        )

        assert "EngineAgent" in result
        assert "System prompt" in result
        assert "tool1, tool2" in result
        assert "engineType" in result
        assert "{input}" in result

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_body_schema')
    def test_get_body_formatted_prompt(self, mock_body_schema):
        """Test body formatted prompt generation."""
        mock_body_schema.return_value = '{"type": "object"}'

        result = SchemaCarCreationPrompts._get_body_formatted_prompt(
            "BodyAgent", "System prompt", "tool1, tool2"
        )

        assert "BodyAgent" in result
        assert "System prompt" in result
        assert "tool1, tool2" in result
        assert "bodyType" in result
        assert "{input}" in result

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_tire_schema')
    def test_get_tire_formatted_prompt(self, mock_tire_schema):
        """Test tire formatted prompt generation."""
        mock_tire_schema.return_value = '{"type": "object"}'

        result = SchemaCarCreationPrompts._get_tire_formatted_prompt(
            "TireAgent", "System prompt", "tool1, tool2"
        )

        assert "TireAgent" in result
        assert "System prompt" in result
        assert "tool1, tool2" in result
        assert "tireType" in result
        assert "{input}" in result

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_electrical_schema')
    def test_get_electrical_formatted_prompt(self, mock_electrical_schema):
        """Test electrical formatted prompt generation."""
        mock_electrical_schema.return_value = '{"type": "object"}'

        result = SchemaCarCreationPrompts._get_electrical_formatted_prompt(
            "ElectricalAgent", "System prompt", "tool1, tool2"
        )

        assert "ElectricalAgent" in result
        assert "System prompt" in result
        assert "tool1, tool2" in result
        assert "electricalType" in result
        assert "{input}" in result

    def test_get_schema_validation_template(self):
        """Test schema validation template generation."""
        with patch('prompts.prompts_from_json_schema.get_agent_schema_for_prompt') as mock_get:
            mock_get.return_value = '{"type": "object"}'

            template = SchemaCarCreationPrompts.get_schema_validation_template("engine")
            formatted = template.format(component_data={"test": "data"})

            assert "engine" in formatted
            assert "Validation Tasks" in formatted
            assert "test" in formatted


class TestModuleFunctions:
    """Test module-level functions."""

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_supervisor_formatted_prompt')
    def test_get_schema_agent_prompt_supervisor(self, mock_formatted):
        """Test schema agent prompt for supervisor."""
        mock_formatted.return_value = "Supervisor prompt"

        result = get_schema_agent_prompt("supervisor", "SupervisorAgent", "System", "tools")

        mock_formatted.assert_called_once_with("SupervisorAgent", "System", "tools")
        assert result == "Supervisor prompt"

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_engine_formatted_prompt')
    def test_get_schema_agent_prompt_engine(self, mock_formatted):
        """Test schema agent prompt for engine."""
        mock_formatted.return_value = "Engine prompt"

        result = get_schema_agent_prompt("engine", "EngineAgent", "System", "tools")

        mock_formatted.assert_called_once_with("EngineAgent", "System", "tools")
        assert result == "Engine prompt"

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_body_formatted_prompt')
    def test_get_schema_agent_prompt_body(self, mock_formatted):
        """Test schema agent prompt for body."""
        mock_formatted.return_value = "Body prompt"

        result = get_schema_agent_prompt("body", "BodyAgent", "System", "tools")

        mock_formatted.assert_called_once_with("BodyAgent", "System", "tools")
        assert result == "Body prompt"

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_tire_formatted_prompt')
    def test_get_schema_agent_prompt_tire(self, mock_formatted):
        """Test schema agent prompt for tire."""
        mock_formatted.return_value = "Tire prompt"

        result = get_schema_agent_prompt("tire", "TireAgent", "System", "tools")

        mock_formatted.assert_called_once_with("TireAgent", "System", "tools")
        assert result == "Tire prompt"

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts._get_electrical_formatted_prompt')
    def test_get_schema_agent_prompt_electrical(self, mock_formatted):
        """Test schema agent prompt for electrical."""
        mock_formatted.return_value = "Electrical prompt"

        result = get_schema_agent_prompt("electrical", "ElectricalAgent", "System", "tools")

        mock_formatted.assert_called_once_with("ElectricalAgent", "System", "tools")
        assert result == "Electrical prompt"

    def test_get_schema_agent_prompt_unknown(self):
        """Test schema agent prompt for unknown agent type."""
        result = get_schema_agent_prompt("unknown", "UnknownAgent", "System", "tools")

        # Should fall back to base template
        assert "UnknownAgent" in result
        assert "System" in result
        assert "tools" in result

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts.get_car_creation_task_template')
    def test_get_schema_car_creation_task_prompt(self, mock_template):
        """Test schema car creation task prompt."""
        mock_template_obj = Mock()
        mock_template_obj.format.return_value = "Formatted task prompt"
        mock_template.return_value = mock_template_obj

        result = get_schema_car_creation_task_prompt(
            task_description="Create a car",
            vin="TEST123",
            year="2024",
            make="Test",
            model="Model"
        )

        assert result == "Formatted task prompt"
        mock_template_obj.format.assert_called_once()

    @patch('prompts.prompts_from_json_schema.SchemaCarCreationPrompts.get_schema_validation_template')
    def test_get_schema_validation_prompt(self, mock_template):
        """Test schema validation prompt."""
        mock_template_obj = Mock()
        mock_template_obj.format.return_value = "Formatted validation prompt"
        mock_template.return_value = mock_template_obj

        result = get_schema_validation_prompt("engine", {"test": "data"})

        assert result == "Formatted validation prompt"
        mock_template_obj.format.assert_called_once_with(component_data={"test": "data"})

    def test_get_schema_agent_handoff_prompt(self):
        """Test schema agent handoff prompt."""
        result = get_schema_agent_handoff_prompt(
            from_agent="EngineAgent",
            to_agent="BodyAgent",
            handoff_type="constraint",
            payload_data={"test": "data"},
            context_info="Test context",
            handoff_instructions="Test instructions"
        )

        assert "EngineAgent" in result
        assert "BodyAgent" in result
        assert "constraint" in result
        assert "test" in result

    @patch('prompts.prompts_from_json_schema.get_schema_loader')
    def test_get_schema_summary_for_agent(self, mock_get_loader):
        """Test schema summary for agent."""
        mock_loader = Mock()
        mock_loader.get_schema_summary.return_value = {"summary": "data"}
        mock_get_loader.return_value = mock_loader

        result = get_schema_summary_for_agent("engine")

        assert result == {"summary": "data"}
        mock_loader.get_schema_summary.assert_called_once_with("engineType")

    @patch('prompts.prompts_from_json_schema.get_schema_loader')
    def test_get_schema_summary_for_agent_unknown(self, mock_get_loader):
        """Test schema summary for unknown agent."""
        mock_loader = Mock()
        mock_get_loader.return_value = mock_loader

        result = get_schema_summary_for_agent("unknown")

        assert "error" in result
        assert "No schema mapping found" in result["error"]

    @patch('prompts.prompts_from_json_schema.get_schema_loader')
    def test_validate_schema_availability(self, mock_get_loader):
        """Test schema availability validation."""
        mock_loader = Mock()
        mock_loader.validate_definition_exists.side_effect = [True, True, True, True, True]
        mock_loader.get_definition_names.return_value = ["engineType", "bodyType", "tireType", "electricalType", "carType"]
        mock_get_loader.return_value = mock_loader

        result = validate_schema_availability()

        assert result["all_available"] is True
        assert result["missing_schemas"] == []
        assert len(result["available_schemas"]) == 5

    @patch('prompts.prompts_from_json_schema.get_schema_loader')
    def test_validate_schema_availability_missing(self, mock_get_loader):
        """Test schema availability validation with missing schemas."""
        mock_loader = Mock()
        mock_loader.validate_definition_exists.side_effect = [True, False, True, False, True]
        mock_loader.get_definition_names.return_value = ["engineType", "tireType", "carType"]
        mock_get_loader.return_value = mock_loader

        result = validate_schema_availability()

        assert result["all_available"] is False
        assert "bodyType" in result["missing_schemas"]
        assert "electricalType" in result["missing_schemas"]
        assert len(result["available_schemas"]) == 3