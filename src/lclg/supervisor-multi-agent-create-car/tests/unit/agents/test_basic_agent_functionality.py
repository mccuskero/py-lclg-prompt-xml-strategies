"""Basic unit tests for agent functionality to boost coverage."""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock

from agents.base_agent import BaseAgent, AgentMessage, HandoffPayload
from agents.engine_agent import EngineAgent
from agents.body_agent import BodyAgent
from agents.tire_agent import TireAgent
from agents.electrical_agent import ElectricalAgent


class TestAgentMessage:
    """Test AgentMessage class."""

    def test_agent_message_creation(self):
        """Test creating an agent message."""
        message = AgentMessage(content="test content", sender="TestAgent")
        assert message.content == "test content"
        assert message.sender == "TestAgent"
        assert message.timestamp is not None

    def test_agent_message_with_metadata(self):
        """Test creating an agent message with metadata."""
        metadata = {"key": "value", "type": "info"}
        message = AgentMessage(
            content="test content",
            sender="TestAgent",
            metadata=metadata
        )
        assert message.metadata == metadata

    def test_agent_message_string_representation(self):
        """Test agent message string representation."""
        message = AgentMessage(content="test", sender="Agent")
        str_repr = str(message)
        assert "test" in str_repr
        assert "Agent" in str_repr


class TestHandoffPayload:
    """Test HandoffPayload class."""

    def test_handoff_payload_creation(self):
        """Test creating a handoff payload."""
        payload = HandoffPayload(
            from_agent="EngineAgent",
            to_agent="BodyAgent",
            data={"key": "value"}
        )
        assert payload.from_agent == "EngineAgent"
        assert payload.to_agent == "BodyAgent"
        assert payload.data == {"key": "value"}

    def test_handoff_payload_with_constraints(self):
        """Test handoff payload with constraints."""
        constraints = {"material": "steel", "size": "large"}
        payload = HandoffPayload(
            from_agent="EngineAgent",
            to_agent="BodyAgent",
            data={"engine_size": "V6"},
            constraints=constraints
        )
        assert payload.constraints == constraints

    def test_handoff_payload_with_context(self):
        """Test handoff payload with context."""
        payload = HandoffPayload(
            from_agent="EngineAgent",
            to_agent="BodyAgent",
            data={"engine_size": "V6"},
            context="Engine configuration completed"
        )
        assert payload.context == "Engine configuration completed"


class TestBaseAgentFunctionality:
    """Test basic agent functionality that doesn't require LLM integration."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = Mock()
        mock._call.return_value = "Mock response"
        return mock

    def test_agent_initialization_properties(self, mock_llm):
        """Test agent initialization and basic properties."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            # Test different agent types
            agent_classes = [EngineAgent, BodyAgent, TireAgent, ElectricalAgent]

            for AgentClass in agent_classes:
                agent = AgentClass(
                    llm=mock_llm,
                    use_json_subtypes_in_prompts_creation=False
                )

                # Check basic properties
                assert agent.llm == mock_llm
                assert agent.use_json_subtypes_in_prompts_creation is False
                assert hasattr(agent, 'tools')
                assert hasattr(agent, 'handoff_payloads')
                assert isinstance(agent.handoff_payloads, list)

    def test_agent_name_properties(self, mock_llm):
        """Test agent name properties."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            engine_agent = EngineAgent(llm=mock_llm)
            assert engine_agent.name == "EngineAgent"

            body_agent = BodyAgent(llm=mock_llm)
            assert body_agent.name == "BodyAgent"

            tire_agent = TireAgent(llm=mock_llm)
            assert tire_agent.name == "TireAgent"

            electrical_agent = ElectricalAgent(llm=mock_llm)
            assert electrical_agent.name == "ElectricalAgent"

    def test_agent_type_methods(self, mock_llm):
        """Test agent type methods."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            engine_agent = EngineAgent(llm=mock_llm)
            assert engine_agent._get_agent_type() == "engine"

            body_agent = BodyAgent(llm=mock_llm)
            assert body_agent._get_agent_type() == "body"

            tire_agent = TireAgent(llm=mock_llm)
            assert tire_agent._get_agent_type() == "tire"

            electrical_agent = ElectricalAgent(llm=mock_llm)
            assert electrical_agent._get_agent_type() == "electrical"

    def test_handoff_payload_management(self, mock_llm):
        """Test handoff payload management."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            agent = EngineAgent(llm=mock_llm)

            # Test adding handoff payloads
            payload1 = HandoffPayload("EngineAgent", "BodyAgent", {"data": "test1"})
            payload2 = HandoffPayload("EngineAgent", "TireAgent", {"data": "test2"})

            agent.add_handoff_payload(payload1)
            agent.add_handoff_payload(payload2)

            assert len(agent.handoff_payloads) == 2
            assert payload1 in agent.handoff_payloads
            assert payload2 in agent.handoff_payloads

    def test_get_handoff_payloads_for_agent(self, mock_llm):
        """Test getting handoff payloads for specific agents."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            agent = EngineAgent(llm=mock_llm)

            # Add payloads for different target agents
            payload1 = HandoffPayload("EngineAgent", "BodyAgent", {"data": "for_body"})
            payload2 = HandoffPayload("EngineAgent", "TireAgent", {"data": "for_tire"})
            payload3 = HandoffPayload("EngineAgent", "BodyAgent", {"data": "also_for_body"})

            agent.add_handoff_payload(payload1)
            agent.add_handoff_payload(payload2)
            agent.add_handoff_payload(payload3)

            # Get payloads for BodyAgent
            body_payloads = agent.get_handoff_payloads_for_agent("BodyAgent")
            assert len(body_payloads) == 2
            assert payload1 in body_payloads
            assert payload3 in body_payloads

            # Get payloads for TireAgent
            tire_payloads = agent.get_handoff_payloads_for_agent("TireAgent")
            assert len(tire_payloads) == 1
            assert payload2 in tire_payloads

    def test_clear_handoff_payloads(self, mock_llm):
        """Test clearing handoff payloads."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            agent = EngineAgent(llm=mock_llm)

            # Add some payloads
            payload1 = HandoffPayload("EngineAgent", "BodyAgent", {"data": "test1"})
            payload2 = HandoffPayload("EngineAgent", "TireAgent", {"data": "test2"})

            agent.add_handoff_payload(payload1)
            agent.add_handoff_payload(payload2)
            assert len(agent.handoff_payloads) == 2

            # Clear payloads
            agent.clear_handoff_payloads()
            assert len(agent.handoff_payloads) == 0

    def test_agent_system_prompt_generation(self, mock_llm):
        """Test system prompt generation."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            agent_classes = [EngineAgent, BodyAgent, TireAgent, ElectricalAgent]

            for AgentClass in agent_classes:
                agent = AgentClass(llm=mock_llm)
                system_prompt = agent._get_system_prompt()

                # System prompt should be a string
                assert isinstance(system_prompt, str)
                assert len(system_prompt) > 0

    def test_agent_tools_initialization(self, mock_llm):
        """Test that agents initialize their tools."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools') as mock_setup_tools:

            agent = EngineAgent(llm=mock_llm)

            # Verify tools setup was called
            mock_setup_tools.assert_called_once()

    def test_agent_with_json_subtypes_flag(self, mock_llm):
        """Test agent initialization with JSON subtypes flag."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            # Test with JSON subtypes enabled
            agent = EngineAgent(
                llm=mock_llm,
                use_json_subtypes_in_prompts_creation=True
            )
            assert agent.use_json_subtypes_in_prompts_creation is True

            # Test with JSON subtypes disabled
            agent = EngineAgent(
                llm=mock_llm,
                use_json_subtypes_in_prompts_creation=False
            )
            assert agent.use_json_subtypes_in_prompts_creation is False

    def test_multiple_agents_isolation(self, mock_llm):
        """Test that multiple agents are properly isolated."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            # Create multiple agents
            engine_agent = EngineAgent(llm=mock_llm)
            body_agent = BodyAgent(llm=mock_llm)

            # Add different payloads to each
            engine_payload = HandoffPayload("EngineAgent", "BodyAgent", {"engine_data": "test"})
            body_payload = HandoffPayload("BodyAgent", "TireAgent", {"body_data": "test"})

            engine_agent.add_handoff_payload(engine_payload)
            body_agent.add_handoff_payload(body_payload)

            # Verify isolation
            assert len(engine_agent.handoff_payloads) == 1
            assert len(body_agent.handoff_payloads) == 1
            assert engine_payload in engine_agent.handoff_payloads
            assert body_payload in body_agent.handoff_payloads
            assert engine_payload not in body_agent.handoff_payloads
            assert body_payload not in engine_agent.handoff_payloads

    def test_agent_string_representation(self, mock_llm):
        """Test agent string representation."""
        with patch('agents.base_agent.BaseAgent._setup_agent'), \
             patch('agents.base_agent.BaseAgent._setup_tools'):

            agent = EngineAgent(llm=mock_llm)
            str_repr = str(agent)

            # Should contain agent name
            assert "EngineAgent" in str_repr