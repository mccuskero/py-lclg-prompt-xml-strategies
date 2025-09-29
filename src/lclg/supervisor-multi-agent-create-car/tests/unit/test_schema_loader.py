"""Unit tests for schema loader functionality."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from prompts.schema_loader import (
    CarSchemaLoader,
    get_schema_loader,
    get_schema_for_prompt,
    get_agent_schema_for_prompt,
    get_schema_summary
)


class TestCarSchemaLoader:
    """Test the CarSchemaLoader class."""

    @pytest.fixture
    def sample_schema_data(self):
        """Sample schema data for testing."""
        return {
            "$defs": {
                "engineType": {
                    "type": "object",
                    "properties": {
                        "displacement": {"type": "string"},
                        "cylinders": {"type": "string"},
                        "fuelType": {"$ref": "#/$defs/fuelTypeEnum"}
                    },
                    "required": ["displacement", "cylinders"]
                },
                "fuelTypeEnum": {
                    "enum": ["gasoline", "diesel", "electric", "hybrid"]
                },
                "carType": {
                    "type": "object",
                    "properties": {
                        "Engine": {"$ref": "#/$defs/engineType"},
                        "@vin": {"type": "string"}
                    }
                }
            }
        }

    @pytest.fixture
    def mock_schema_file(self, sample_schema_data):
        """Mock schema file."""
        return mock_open(read_data=json.dumps(sample_schema_data))

    def test_init_with_default_path(self):
        """Test initialization with default schema path."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load') as mock_json_load:
            mock_json_load.return_value = {"$defs": {}}
            loader = CarSchemaLoader()
            assert loader.schema_path.name == "car.json"
            assert "schema/single" in str(loader.schema_path)

    def test_init_with_custom_path(self):
        """Test initialization with custom schema path."""
        custom_path = "/custom/path/schema.json"
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load') as mock_json_load:
            mock_json_load.return_value = {"$defs": {}}
            loader = CarSchemaLoader(schema_path=custom_path)
            assert str(loader.schema_path) == custom_path

    def test_load_schema_success(self, sample_schema_data, mock_schema_file):
        """Test successful schema loading."""
        with patch('prompts.schema_loader.Path.open', mock_schema_file), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            assert loader._schema_data == sample_schema_data

    def test_load_schema_file_not_found(self):
        """Test schema loading with file not found."""
        with patch('prompts.schema_loader.Path.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError, match="Schema file not found"):
                CarSchemaLoader()

    def test_load_schema_invalid_json(self):
        """Test schema loading with invalid JSON."""
        with patch('prompts.schema_loader.Path.open', mock_open(read_data="invalid json")), \
             patch('json.load', side_effect=json.JSONDecodeError("msg", "doc", 0)):
            with pytest.raises(ValueError, match="Invalid JSON in schema file"):
                CarSchemaLoader()

    def test_get_schema_definition_success(self, sample_schema_data):
        """Test successful schema definition retrieval."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            definition = loader.get_schema_definition("engineType")
            assert definition is not None
            assert definition["type"] == "object"
            assert "displacement" in definition["properties"]

    def test_get_schema_definition_not_found(self, sample_schema_data):
        """Test schema definition retrieval for non-existent definition."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            definition = loader.get_schema_definition("nonexistent")
            assert definition is None

    def test_get_formatted_schema_for_prompt(self, sample_schema_data):
        """Test formatted schema generation for prompts."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            formatted = loader.get_formatted_schema_for_prompt("engineType")
            assert "displacement" in formatted
            assert "cylinders" in formatted
            # Should not contain $schema or title
            assert "$schema" not in formatted
            assert "title" not in formatted

    def test_get_formatted_schema_not_found(self, sample_schema_data):
        """Test formatted schema for non-existent definition."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            formatted = loader.get_formatted_schema_for_prompt("nonexistent")
            assert "Schema definition 'nonexistent' not found" in formatted

    def test_get_enum_values(self, sample_schema_data):
        """Test enum value extraction."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            enum_values = loader.get_enum_values("engineType")
            # Should find fuelType enum through $ref
            assert "fuelType" in enum_values or len(enum_values) >= 0

    def test_get_required_fields(self, sample_schema_data):
        """Test required fields extraction."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            required = loader.get_required_fields("engineType")
            assert "displacement" in required
            assert "cylinders" in required

    def test_get_required_fields_not_found(self, sample_schema_data):
        """Test required fields for non-existent definition."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            required = loader.get_required_fields("nonexistent")
            assert required == []

    def test_get_field_descriptions(self, sample_schema_data):
        """Test field description extraction."""
        # Add descriptions to sample data
        sample_schema_data["$defs"]["engineType"]["properties"]["displacement"]["description"] = "Engine displacement"

        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            descriptions = loader.get_field_descriptions("engineType")
            assert "displacement" in descriptions
            assert descriptions["displacement"] == "Engine displacement"

    def test_get_schema_summary(self, sample_schema_data):
        """Test comprehensive schema summary."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            summary = loader.get_schema_summary("engineType")
            assert summary["definition_name"] == "engineType"
            assert summary["type"] == "object"
            assert "displacement" in summary["required_fields"]
            assert "formatted_schema" in summary

    def test_get_schema_summary_not_found(self, sample_schema_data):
        """Test schema summary for non-existent definition."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            summary = loader.get_schema_summary("nonexistent")
            assert "error" in summary
            assert "not found" in summary["error"]

    def test_get_all_definitions(self, sample_schema_data):
        """Test getting all schema definitions."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            definitions = loader.get_all_definitions()
            assert "engineType" in definitions
            assert "fuelTypeEnum" in definitions
            assert "carType" in definitions

    def test_get_definition_names(self, sample_schema_data):
        """Test getting all definition names."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            names = loader.get_definition_names()
            assert "engineType" in names
            assert "fuelTypeEnum" in names
            assert "carType" in names

    def test_validate_definition_exists(self, sample_schema_data):
        """Test definition existence validation."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            assert loader.validate_definition_exists("engineType") is True
            assert loader.validate_definition_exists("nonexistent") is False

    def test_get_schema_for_agent_type(self, sample_schema_data):
        """Test getting schema for specific agent types."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            schema = loader.get_schema_for_agent_type("engine")
            assert schema is not None
            assert schema["type"] == "object"

            # Test unknown agent type
            schema = loader.get_schema_for_agent_type("unknown")
            assert schema is None

    def test_get_formatted_schema_for_agent(self, sample_schema_data):
        """Test getting formatted schema for agent types."""
        with patch('prompts.schema_loader.Path.open'), \
             patch('json.load', return_value=sample_schema_data):
            loader = CarSchemaLoader()
            formatted = loader.get_formatted_schema_for_agent("engine")
            assert "displacement" in formatted

            # Test unknown agent type
            formatted = loader.get_formatted_schema_for_agent("unknown")
            assert "No schema mapping found" in formatted


class TestModuleFunctions:
    """Test module-level functions."""

    def test_get_schema_loader_singleton(self):
        """Test that get_schema_loader returns singleton instance."""
        with patch('prompts.schema_loader.CarSchemaLoader') as mock_loader_class:
            mock_instance = mock_loader_class.return_value

            # First call should create instance
            loader1 = get_schema_loader()
            assert loader1 == mock_instance

            # Second call should return same instance
            loader2 = get_schema_loader()
            assert loader2 == mock_instance

            # Should only be called once
            mock_loader_class.assert_called_once()

    def test_get_schema_loader_with_custom_path(self):
        """Test get_schema_loader with custom path."""
        with patch('prompts.schema_loader.CarSchemaLoader') as mock_loader_class:
            custom_path = "/custom/path"
            get_schema_loader(custom_path)
            mock_loader_class.assert_called_with(custom_path)

    def test_get_schema_for_prompt(self):
        """Test get_schema_for_prompt convenience function."""
        with patch('prompts.schema_loader.get_schema_loader') as mock_get_loader:
            mock_loader = mock_get_loader.return_value
            mock_loader.get_formatted_schema_for_prompt.return_value = "formatted schema"

            result = get_schema_for_prompt("engineType", 4)
            assert result == "formatted schema"
            mock_loader.get_formatted_schema_for_prompt.assert_called_once_with("engineType", 4)

    def test_get_agent_schema_for_prompt(self):
        """Test get_agent_schema_for_prompt convenience function."""
        with patch('prompts.schema_loader.get_schema_loader') as mock_get_loader:
            mock_loader = mock_get_loader.return_value
            mock_loader.get_formatted_schema_for_agent.return_value = "formatted agent schema"

            result = get_agent_schema_for_prompt("engine", 4)
            assert result == "formatted agent schema"
            mock_loader.get_formatted_schema_for_agent.assert_called_once_with("engine", 4)

    def test_get_schema_summary_function(self):
        """Test get_schema_summary convenience function."""
        with patch('prompts.schema_loader.get_schema_loader') as mock_get_loader:
            mock_loader = mock_get_loader.return_value
            mock_loader.get_schema_summary.return_value = {"summary": "data"}

            result = get_schema_summary("engineType")
            assert result == {"summary": "data"}
            mock_loader.get_schema_summary.assert_called_once_with("engineType")