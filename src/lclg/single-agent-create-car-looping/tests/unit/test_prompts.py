"""Unit tests for prompts module."""

import pytest
from prompts.prompts import (
    CAR_AGENT_SYSTEM_PROMPT,
    CAR_AGENT_HUMAN_PROMPT,
    get_car_agent_system_prompt,
    get_car_agent_request_prompt,
    get_interactive_session_prompt,
    get_user_followup_prompt
)


class TestPromptTemplates:
    """Test prompt template functionality."""

    def test_car_agent_system_prompt_exists(self):
        """Test that system prompt template exists."""
        assert CAR_AGENT_SYSTEM_PROMPT is not None
        assert hasattr(CAR_AGENT_SYSTEM_PROMPT, 'format')

    def test_car_agent_human_prompt_exists(self):
        """Test that human prompt template exists."""
        assert CAR_AGENT_HUMAN_PROMPT is not None
        assert hasattr(CAR_AGENT_HUMAN_PROMPT, 'format')

    def test_system_prompt_format(self):
        """Test formatting system prompt."""
        tools_list = "- tool1\n- tool2\n- tool3"
        result = CAR_AGENT_SYSTEM_PROMPT.format(tools=tools_list)

        assert "tool1" in result
        assert "tool2" in result
        assert "comprehensive car creation agent" in result
        assert "Engine configuration" in result

    def test_human_prompt_format(self):
        """Test formatting human prompt."""
        requirements = "- vehicle_type: sedan\n- performance: standard"
        context = "No context"

        result = CAR_AGENT_HUMAN_PROMPT.format(
            requirements=requirements,
            context=context
        )

        assert "sedan" in result
        assert "No context" in result
        assert "car_configuration" in result

    def test_get_car_agent_system_prompt(self):
        """Test get_car_agent_system_prompt function."""
        tools_list = "- configure_engine\n- configure_body"
        result = get_car_agent_system_prompt(tools_list)

        assert isinstance(result, str)
        assert "configure_engine" in result
        assert "configure_body" in result

    def test_get_car_agent_request_prompt(self):
        """Test get_car_agent_request_prompt function."""
        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "standard",
            "fuel_preference": "gasoline"
        }
        context = "Previous iteration configured engine"

        result = get_car_agent_request_prompt(requirements, context)

        assert isinstance(result, str)
        assert "sedan" in result
        assert "standard" in result
        assert "gasoline" in result
        assert "Previous iteration" in result

    def test_get_car_agent_request_prompt_no_context(self):
        """Test request prompt without context."""
        requirements = {"vehicle_type": "suv"}

        result = get_car_agent_request_prompt(requirements)

        assert isinstance(result, str)
        assert "suv" in result
        assert "No previous context" in result

    def test_get_interactive_session_prompt(self):
        """Test get_interactive_session_prompt function."""
        context = "User requested sedan"
        user_input = "Make it electric"

        result = get_interactive_session_prompt(context, user_input)

        assert isinstance(result, str)
        assert "sedan" in result
        assert "electric" in result
        assert "action" in result

    def test_get_user_followup_prompt(self):
        """Test get_user_followup_prompt function."""
        context = "Engine configured"
        previous_question = "What color do you want?"
        user_answer = "Blue"

        result = get_user_followup_prompt(context, previous_question, user_answer)

        assert isinstance(result, str)
        assert "Engine configured" in result
        assert "What color" in result
        assert "Blue" in result
