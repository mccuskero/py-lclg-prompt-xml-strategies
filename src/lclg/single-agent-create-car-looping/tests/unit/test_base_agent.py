"""Unit tests for BaseAgent class."""

import pytest
from agents.base_agent import BaseAgent, ConversationMemory, AgentMessage


class TestConversationMemory:
    """Test the ConversationMemory class."""

    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory(max_history=3)

        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there")

        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_max_history_limit(self):
        """Test that memory respects max_history limit."""
        memory = ConversationMemory(max_history=2)

        memory.add_message("user", "Message 1")
        memory.add_message("assistant", "Response 1")
        memory.add_message("user", "Message 2")

        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["content"] == "Response 1"
        assert messages[1]["content"] == "Message 2"

    def test_add_context(self):
        """Test adding context data."""
        memory = ConversationMemory()

        memory.add_context("vehicle_type", "sedan")
        memory.add_context("fuel_type", "gasoline")

        assert memory.context_data["vehicle_type"] == "sedan"
        assert memory.context_data["fuel_type"] == "gasoline"

    def test_get_context_summary(self):
        """Test getting context summary."""
        memory = ConversationMemory()

        memory.add_context("vehicle_type", "sedan")
        memory.add_context("performance", "standard")

        summary = memory.get_context_summary()
        assert "vehicle_type" in summary
        assert "sedan" in summary
        assert "performance" in summary
        assert "standard" in summary

    def test_get_context_summary_empty(self):
        """Test context summary when no context exists."""
        memory = ConversationMemory()

        summary = memory.get_context_summary()
        assert "No context" in summary

    def test_clear(self):
        """Test clearing memory."""
        memory = ConversationMemory()

        memory.add_message("user", "Hello")
        memory.add_context("key", "value")

        memory.clear()

        assert len(memory.get_messages()) == 0
        assert len(memory.context_data) == 0


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

        assert agent.memory.context_data["req_vehicle_type"] == "sedan"
        assert agent.memory.context_data["req_performance_level"] == "standard"
        assert agent.memory.context_data["configured_engine"] == True
        assert agent.memory.context_data["configured_body"] == True

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

        # Add some memory
        agent.memory.add_message("user", "test message")
        agent.memory.add_context("test_key", "test_value")

        assert len(agent.memory.messages) > 0
        assert len(agent.memory.context_data) > 0

        # Reset
        agent.reset_memory()

        assert len(agent.memory.messages) == 0
        assert len(agent.memory.context_data) == 0
