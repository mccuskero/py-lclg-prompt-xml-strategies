"""Unit tests for base agent functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from agents.base_agent import (
    BaseAgent,
    AgentMessage,
    HandoffPayload,
)


class TestAgentMessage:
    """Test the AgentMessage model."""

    def test_agent_message_creation(self):
        """Test creating an agent message."""
        message = AgentMessage(
            content="Test message",
            sender="TestAgent",
            recipient="OtherAgent",
            metadata={"key": "value"}
        )

        assert message.content == "Test message"
        assert message.sender == "TestAgent"
        assert message.recipient == "OtherAgent"
        assert message.metadata == {"key": "value"}

    def test_agent_message_defaults(self):
        """Test agent message with defaults."""
        message = AgentMessage(
            content="Test message",
            sender="TestAgent"
        )

        assert message.content == "Test message"
        assert message.sender == "TestAgent"
        assert message.recipient is None
        assert message.metadata == {}


class TestHandoffPayload:
    """Test the HandoffPayload model."""

    def test_handoff_payload_creation(self):
        """Test creating a handoff payload."""
        payload = HandoffPayload(
            from_agent="SourceAgent",
            to_agent="TargetAgent",
            data={"key": "value"},
            constraints={"constraint": "value"},
            context="Test context"
        )

        assert payload.from_agent == "SourceAgent"
        assert payload.to_agent == "TargetAgent"
        assert payload.data == {"key": "value"}
        assert payload.constraints == {"constraint": "value"}
        assert payload.context == "Test context"

    def test_handoff_payload_defaults(self):
        """Test handoff payload with defaults."""
        payload = HandoffPayload(
            from_agent="SourceAgent",
            to_agent="TargetAgent",
            data={"key": "value"}
        )

        assert payload.from_agent == "SourceAgent"
        assert payload.to_agent == "TargetAgent"
        assert payload.data == {"key": "value"}
        assert payload.constraints == {}
        assert payload.context == ""


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def _setup_tools(self):
        """Mock tool setup."""
        self.tools = [Mock(name="test_tool")]

    def _get_system_prompt(self):
        """Mock system prompt."""
        return "Test system prompt"

    def _get_agent_type(self):
        """Mock agent type."""
        return "test"


class TestBaseAgent:
    """Test the BaseAgent class."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock_llm = Mock()
        mock_llm._call.return_value = "Mock response"
        return mock_llm

    @patch('agents.base_agent.get_agent_prompt')
    @patch('agents.base_agent.get_schema_agent_prompt')
    @patch('agents.base_agent.create_agent')
    def test_base_agent_init_default_prompts(self, mock_create_agent, mock_schema_prompt, mock_agent_prompt, mock_llm):
        """Test BaseAgent initialization with default prompts."""
        mock_agent_prompt.return_value = "Agent prompt"
        mock_create_agent.return_value = Mock()

        agent = ConcreteAgent(
            name="TestAgent",
            llm=mock_llm,
            use_json_subtypes_in_prompts_creation=False
        )

        assert agent.name == "TestAgent"
        assert agent.llm == mock_llm
        assert agent.use_json_subtypes_in_prompts_creation is False
        mock_agent_prompt.assert_called_once()
        mock_schema_prompt.assert_not_called()

    @patch('agents.base_agent.get_agent_prompt')
    @patch('agents.base_agent.get_schema_agent_prompt')
    @patch('agents.base_agent.create_agent')
    def test_base_agent_init_schema_prompts(self, mock_create_agent, mock_schema_prompt, mock_agent_prompt, mock_llm):
        """Test BaseAgent initialization with schema prompts."""
        mock_schema_prompt.return_value = "Schema prompt"
        mock_create_agent.return_value = Mock()

        agent = ConcreteAgent(
            name="TestAgent",
            llm=mock_llm,
            use_json_subtypes_in_prompts_creation=True
        )

        assert agent.name == "TestAgent"
        assert agent.llm == mock_llm
        assert agent.use_json_subtypes_in_prompts_creation is True
        mock_schema_prompt.assert_called_once()
        mock_agent_prompt.assert_not_called()

    @patch('agents.base_agent.OllamaLLM')
    @patch('agents.base_agent.get_agent_prompt')
    @patch('agents.base_agent.create_agent')
    def test_base_agent_init_default_llm(self, mock_create_agent, mock_agent_prompt, mock_ollama_llm):
        """Test BaseAgent initialization with default LLM."""
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        mock_agent_prompt.return_value = "Agent prompt"
        mock_create_agent.return_value = Mock()

        agent = ConcreteAgent(
            name="TestAgent",
            model_name="test_model",
            temperature=0.5,
            base_url="http://test:11434"
        )

        assert agent.name == "TestAgent"
        assert agent.llm == mock_llm_instance
        mock_ollama_llm.assert_called_once_with(
            model="test_model",
            temperature=0.5,
            base_url="http://test:11434"
        )

    @patch('agents.base_agent.get_agent_prompt')
    @patch('agents.base_agent.create_agent')
    def test_setup_agent_called(self, mock_create_agent, mock_agent_prompt, mock_llm):
        """Test that _setup_agent is called during initialization."""
        mock_agent_prompt.return_value = "Agent prompt"
        mock_executor = Mock()
        mock_create_agent.return_value = mock_executor

        agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

        assert agent.agent_executor == mock_executor
        mock_create_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message(self, mock_llm):
        """Test processing a message."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent') as mock_create_agent:

            mock_executor = AsyncMock()
            mock_executor.ainvoke.return_value = {
                "messages": [Mock(content="Response from agent")]
            }
            mock_create_agent.return_value = mock_executor

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            message = AgentMessage(
                content="Test message",
                sender="User"
            )

            response = await agent.process_message(message)

            assert isinstance(response, AgentMessage)
            assert response.sender == "TestAgent"
            assert response.recipient == "User"
            assert "Response from agent" in response.content

    @pytest.mark.asyncio
    async def test_process_message_error(self, mock_llm):
        """Test processing a message with error."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent') as mock_create_agent:

            mock_executor = AsyncMock()
            mock_executor.ainvoke.side_effect = Exception("Test error")
            mock_create_agent.return_value = mock_executor

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            message = AgentMessage(
                content="Test message",
                sender="User"
            )

            response = await agent.process_message(message)

            assert isinstance(response, AgentMessage)
            assert response.sender == "TestAgent"
            assert "Error processing message" in response.content
            assert "Test error" in response.content

    def test_create_handoff_payload(self, mock_llm):
        """Test creating a handoff payload."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload = agent.create_handoff_payload(
                to_agent="TargetAgent",
                data={"key": "value"},
                constraints={"constraint": "value"},
                context="Test context"
            )

            assert isinstance(payload, HandoffPayload)
            assert payload.from_agent == "TestAgent"
            assert payload.to_agent == "TargetAgent"
            assert payload.data == {"key": "value"}
            assert payload.constraints == {"constraint": "value"}
            assert payload.context == "Test context"

    def test_receive_handoff_payload(self, mock_llm):
        """Test receiving a handoff payload."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload = HandoffPayload(
                from_agent="SourceAgent",
                to_agent="TestAgent",
                data={"key": "value"}
            )

            result = agent.receive_handoff_payload(payload)

            assert result is True
            assert payload in agent.handoff_payloads

    def test_receive_handoff_payload_wrong_recipient(self, mock_llm):
        """Test receiving a handoff payload for wrong recipient."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload = HandoffPayload(
                from_agent="SourceAgent",
                to_agent="OtherAgent",
                data={"key": "value"}
            )

            result = agent.receive_handoff_payload(payload)

            assert result is False
            assert payload not in agent.handoff_payloads

    def test_get_pending_handoffs(self, mock_llm):
        """Test getting pending handoffs."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload1 = HandoffPayload(
                from_agent="Source1",
                to_agent="TestAgent",
                data={"key1": "value1"}
            )
            payload2 = HandoffPayload(
                from_agent="Source2",
                to_agent="TestAgent",
                data={"key2": "value2"}
            )

            agent.receive_handoff_payload(payload1)
            agent.receive_handoff_payload(payload2)

            pending = agent.get_pending_handoffs()

            assert len(pending) == 2
            assert payload1 in pending
            assert payload2 in pending

    def test_get_pending_handoffs_from_agent(self, mock_llm):
        """Test getting pending handoffs from specific agent."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload1 = HandoffPayload(
                from_agent="Source1",
                to_agent="TestAgent",
                data={"key1": "value1"}
            )
            payload2 = HandoffPayload(
                from_agent="Source2",
                to_agent="TestAgent",
                data={"key2": "value2"}
            )

            agent.receive_handoff_payload(payload1)
            agent.receive_handoff_payload(payload2)

            pending = agent.get_pending_handoffs(from_agent="Source1")

            assert len(pending) == 1
            assert payload1 in pending
            assert payload2 not in pending

    def test_clear_handoff_payloads(self, mock_llm):
        """Test clearing handoff payloads."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            payload = HandoffPayload(
                from_agent="SourceAgent",
                to_agent="TestAgent",
                data={"key": "value"}
            )

            agent.receive_handoff_payload(payload)
            assert len(agent.handoff_payloads) == 1

            agent.clear_handoff_payloads()
            assert len(agent.handoff_payloads) == 0

    def test_get_agent_info(self, mock_llm):
        """Test getting agent information."""
        with patch('agents.base_agent.get_agent_prompt'), \
             patch('agents.base_agent.create_agent'):

            agent = ConcreteAgent(name="TestAgent", llm=mock_llm)

            info = agent.get_agent_info()

            assert info["name"] == "TestAgent"
            assert info["type"] == "test"
            assert "tools" in info
            assert info["tools"] == ["test_tool"]
            assert "handoff_payloads_count" in info

    def test_abstract_methods_enforcement(self):
        """Test that abstract methods are enforced."""
        with pytest.raises(TypeError):
            # This should fail because BaseAgent is abstract
            BaseAgent(name="TestAgent")