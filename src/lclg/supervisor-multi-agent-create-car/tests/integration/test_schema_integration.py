"""Integration tests for schema-driven functionality."""

import pytest
import asyncio
from pathlib import Path

from prompts.schema_loader import CarSchemaLoader, validate_schema_availability
from prompts.prompts_from_json_schema import get_schema_agent_prompt


@pytest.mark.integration
class TestSchemaIntegration:
    """Integration tests for schema functionality."""

    @pytest.fixture
    def schema_file_path(self):
        """Get the path to the actual schema file."""
        return Path(__file__).parent.parent.parent / "schema" / "single" / "car.json"

    def test_real_schema_file_exists(self, schema_file_path):
        """Test that the actual schema file exists."""
        assert schema_file_path.exists(), f"Schema file not found at {schema_file_path}"

    def test_real_schema_loading(self, schema_file_path):
        """Test loading the real schema file."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        loader = CarSchemaLoader(str(schema_file_path))

        # Test that basic definitions exist
        definitions = loader.get_definition_names()
        expected_definitions = ["engineType", "bodyType", "tireType", "electricalType", "carType"]

        for expected_def in expected_definitions:
            assert expected_def in definitions, f"Missing definition: {expected_def}"

    def test_schema_availability_with_real_file(self, schema_file_path):
        """Test schema availability validation with real file."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        # This will use the real schema file if available
        result = validate_schema_availability()

        # Should find all required schemas if file is properly formatted
        if result["all_available"]:
            assert len(result["missing_schemas"]) == 0
            assert "engineType" in result["available_schemas"]
            assert "carType" in result["available_schemas"]

    def test_schema_driven_prompt_generation_with_real_schemas(self, schema_file_path):
        """Test generating schema-driven prompts with real schemas."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        agent_types = ["supervisor", "engine", "body", "tire", "electrical"]

        for agent_type in agent_types:
            try:
                prompt = get_schema_agent_prompt(
                    agent_type=agent_type,
                    agent_name=f"{agent_type.title()}Agent",
                    system_prompt="Integration test system prompt",
                    tool_names="integration_tool1, integration_tool2"
                )

                # Basic validation that prompt was generated
                assert len(prompt) > 100  # Should be substantial
                assert agent_type.title() + "Agent" in prompt
                assert "integration_tool1" in prompt

                # Should contain schema information
                schema_indicators = ["{", "}", "type", "properties"]
                schema_present = any(indicator in prompt for indicator in schema_indicators)
                assert schema_present, f"Schema not found in {agent_type} prompt"

            except Exception as e:
                pytest.fail(f"Failed to generate schema prompt for {agent_type}: {str(e)}")

    def test_schema_prompt_vs_markdown_prompt_differences(self, schema_file_path):
        """Test that schema prompts differ from markdown prompts."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        from prompts.prompts import get_agent_prompt

        # Compare schema-driven vs markdown prompts
        agent_type = "engine"
        agent_name = "EngineAgent"
        system_prompt = "Test system prompt"
        tool_names = "test_tool"

        # Get markdown prompt
        try:
            markdown_prompt = get_agent_prompt(agent_type, agent_name, system_prompt, tool_names)
        except Exception:
            pytest.skip("Markdown prompts not available")

        # Get schema prompt
        schema_prompt = get_schema_agent_prompt(agent_type, agent_name, system_prompt, tool_names)

        # They should be different
        assert markdown_prompt != schema_prompt

        # Schema prompt should contain JSON-like structures
        json_indicators = ["{", "}", '"type":', '"properties":']
        schema_has_json = any(indicator in schema_prompt for indicator in json_indicators)
        assert schema_has_json, "Schema prompt should contain JSON schema structures"

    def test_all_agent_types_have_schema_mappings(self, schema_file_path):
        """Test that all agent types have proper schema mappings."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        from prompts.prompts_from_json_schema import get_schema_summary_for_agent

        agent_types = ["supervisor", "engine", "body", "tire", "electrical"]

        for agent_type in agent_types:
            summary = get_schema_summary_for_agent(agent_type)

            if "error" in summary:
                pytest.fail(f"No schema mapping for agent type: {agent_type}")

            # Should have basic schema information
            assert "definition_name" in summary
            assert summary["definition_name"] is not None

    def test_schema_validation_with_real_schemas(self, schema_file_path):
        """Test schema validation functionality with real schemas."""
        if not schema_file_path.exists():
            pytest.skip("Schema file not available for integration testing")

        from prompts.prompts_from_json_schema import get_schema_validation_prompt

        # Test validation prompt generation
        component_data = {
            "displacement": "3.5L",
            "cylinders": "6",
            "fuelType": "gasoline",
            "horsepower": "280",
            "@engineCode": "V6_350_GAS"
        }

        validation_prompt = get_schema_validation_prompt("engine", component_data)

        # Should contain validation instructions
        validation_keywords = ["validation", "required", "schema", "fields"]
        validation_present = any(keyword in validation_prompt.lower() for keyword in validation_keywords)
        assert validation_present, "Validation prompt should contain validation instructions"

        # Should contain the component data
        assert "3.5L" in validation_prompt
        assert "gasoline" in validation_prompt