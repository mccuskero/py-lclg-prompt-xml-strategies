"""Unit tests for BaseAgent class."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage
from agents.base_agent import BaseAgent, AgentMessage
from memory.memory_manager import MemoryBackendConfig


class TestAgentMessage:
    """Test the AgentMessage class."""

    def test_create_basic_message(self):
        """Test creating a basic message."""
        msg = AgentMessage(
            content="Test content",
            sender="user",
            recipient="agent"
        )

        assert msg.content == "Test content"
        assert msg.sender == "user"
        assert msg.recipient == "agent"
        assert msg.metadata == {}

    def test_create_message_with_metadata(self):
        """Test creating a message with metadata."""
        msg = AgentMessage(
            content="Test",
            sender="user",
            recipient="agent",
            metadata={"key": "value"}
        )

        assert msg.metadata["key"] == "value"


class TestBaseAgentExtended:
    """Extended tests for BaseAgent functionality."""

    def test_format_tools_list_empty(self, mock_llm):
        """Test formatting tools list when empty."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)
        agent.tools = []

        result = agent._format_tools_list()

        assert result == "No tools available"

    def test_format_tools_list_with_tools(self, mock_llm):
        """Test formatting tools list with tools."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        result = agent._format_tools_list()

        assert "configure_engine" in result
        assert "configure_body" in result
        assert "-" in result

    def test_update_context_memory(self, mock_llm):
        """Test updating context memory."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = {"vehicle_type": "sedan", "performance_level": "standard"}
        result = {
            "car_configuration": {
                "engine": {"displacement": "2.5L"},
                "body": {"style": "sedan"}
            }
        }

        agent._update_context_memory(requirements, result)

        # Use new memory manager API
        context = agent.memory.get_all_context()
        assert context["req_vehicle_type"] == "sedan"
        assert context["req_performance_level"] == "standard"
        assert context["configured_engine"] == True
        assert context["configured_body"] == True

    def test_extract_json_from_response_with_code_block(self, mock_llm):
        """Test extracting JSON from markdown code block."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        response = '''Here is the configuration:
```json
{
  "car_configuration": {
    "vehicle_info": {"type": "sedan"}
  }
}
```
'''

        result = agent._extract_json_from_response(response)

        assert "car_configuration" in result
        assert result["car_configuration"]["vehicle_info"]["type"] == "sedan"

    def test_extract_json_from_response_with_prefix(self, mock_llm):
        """Test extracting JSON with text prefix."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        response = 'Based on your requirements: {"car_configuration": {"vehicle_info": {"type": "suv"}}}'

        result = agent._extract_json_from_response(response)

        assert "car_configuration" in result
        assert result["car_configuration"]["vehicle_info"]["type"] == "suv"

    def test_balance_json_braces_add_closing(self, mock_llm):
        """Test balancing JSON braces - adding closing braces."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        text = '{"key": "value", "nested": {"inner": "data"'
        result = agent._balance_json_braces(text)

        assert result.count('{') == result.count('}')

    def test_balance_json_braces_remove_extra(self, mock_llm):
        """Test balancing JSON braces - removing extra closing braces."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        text = '{"key": "value"}}}'
        result = agent._balance_json_braces(text)

        assert result.count('{') == result.count('}')

    def test_get_agent_info(self, mock_llm):
        """Test getting agent information."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        info = agent.get_agent_info()

        assert info["name"] == "car_agent"
        assert info["type"] == "car"
        assert "tools" in info
        assert len(info["tools"]) == 8  # 8 tools total

    def test_reset_memory(self, mock_llm):
        """Test resetting agent memory."""
        from agents.car_agent import CarAgent

        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Add some memory using new API
        agent.memory.add_message(HumanMessage(content="test message"))
        agent.memory.add_context("test_key", "test_value")

        assert len(agent.memory.get_messages()) > 0
        assert len(agent.memory.get_all_context()) > 0

        # Reset
        agent.reset_memory()

        assert len(agent.memory.get_messages()) == 0
        assert len(agent.memory.get_all_context()) == 0
