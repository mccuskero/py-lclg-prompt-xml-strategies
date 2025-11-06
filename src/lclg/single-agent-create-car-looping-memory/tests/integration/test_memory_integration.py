"""Integration tests for memory manager with agents."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from agents.car_agent import CarAgent
from memory.memory_manager import (
    MemoryBackendConfig,
    InMemoryManager,
    create_memory_manager
)


class TestMemoryWithAgent:
    """Test memory manager integration with CarAgent."""

    def test_agent_uses_memory_manager(self, mock_llm):
        """Test that agent is initialized with memory manager."""
        config = MemoryBackendConfig(backend_type="memory")
        agent = CarAgent(
            llm=mock_llm,
            enable_logging=False,
            memory_config=config,
            max_memory_messages=5
        )

        assert hasattr(agent, 'memory')
        assert isinstance(agent.memory, InMemoryManager)
        assert agent.memory.max_messages == 5

    def test_agent_default_memory_config(self, mock_llm):
        """Test agent with default memory configuration."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Should default to in-memory
        assert hasattr(agent, 'memory')
        assert isinstance(agent.memory, InMemoryManager)

    def test_agent_memory_persistence_across_calls(self, mock_llm):
        """Test that memory persists across multiple agent calls."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Add context in first interaction
        agent.memory.add_context("vehicle_type", "sedan")
        agent.memory.add_message(HumanMessage(content="First interaction"))

        # Verify it persists
        assert agent.memory.get_context("vehicle_type") == "sedan"
        assert len(agent.memory.get_messages()) == 1

        # Add more context
        agent.memory.add_context("fuel_type", "gasoline")
        agent.memory.add_message(AIMessage(content="Second interaction"))

        # Verify both persist
        assert agent.memory.get_context("vehicle_type") == "sedan"
        assert agent.memory.get_context("fuel_type") == "gasoline"
        assert len(agent.memory.get_messages()) == 2

    def test_agent_memory_sliding_window(self, mock_llm):
        """Test that agent respects sliding window in memory."""
        agent = CarAgent(
            llm=mock_llm,
            enable_logging=False,
            max_memory_messages=3
        )

        # Add 5 messages
        for i in range(5):
            agent.memory.add_message(HumanMessage(content=f"Message {i}"))

        messages = agent.memory.get_messages()
        assert len(messages) == 3
        # Should keep last 3 messages
        assert messages[0].content == "Message 2"
        assert messages[2].content == "Message 4"

    def test_agent_reset_memory_integration(self, mock_llm):
        """Test resetting agent memory."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Add data
        agent.memory.add_message(HumanMessage(content="Test"))
        agent.memory.add_context("key", "value")

        # Reset
        agent.reset_memory()

        # Verify cleared
        assert len(agent.memory.get_messages()) == 0
        assert len(agent.memory.get_all_context()) == 0

    def test_agent_context_summary_integration(self, mock_llm):
        """Test context summary generation in agent."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        agent.memory.add_context("vehicle_type", "sports")
        agent.memory.add_context("performance", "high")

        summary = agent.memory.get_context_summary()
        assert "vehicle_type" in summary
        assert "sports" in summary
        assert "performance" in summary
        assert "high" in summary

    @patch('langchain_community.chat_message_histories.PostgresChatMessageHistory')
    def test_agent_with_postgres_config(self, mock_postgres, mock_llm):
        """Test agent with PostgreSQL memory configuration."""
        mock_history_instance = MagicMock()
        mock_history_instance.messages = []
        mock_postgres.return_value = mock_history_instance

        config = MemoryBackendConfig(
            backend_type="postgres",
            connection_string="postgresql://localhost/test",
            session_id="test_session"
        )

        agent = CarAgent(
            llm=mock_llm,
            enable_logging=False,
            memory_config=config,
            max_memory_messages=10
        )

        # Should have PostgreSQL memory manager
        assert hasattr(agent, 'memory')
        assert hasattr(agent.memory, 'session_id')
        assert agent.memory.session_id == "test_session"

    def test_agent_info_includes_memory_stats(self, mock_llm):
        """Test that agent info includes memory statistics."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        agent.memory.add_message(HumanMessage(content="Test"))
        agent.memory.add_context("key", "value")

        info = agent.get_agent_info()
        assert "context_items" in info
        assert "message_history" in info
        assert info["context_items"] == 1
        assert info["message_history"] == 1


class TestMemoryInMultipleAgents:
    """Test memory isolation between multiple agents."""

    def test_separate_memory_for_each_agent(self, mock_llm):
        """Test that each agent has its own memory."""
        agent1 = CarAgent(llm=mock_llm, enable_logging=False)
        agent2 = CarAgent(llm=mock_llm, enable_logging=False)

        # Add data to agent1
        agent1.memory.add_context("vehicle_type", "sedan")
        agent1.memory.add_message(HumanMessage(content="Agent 1 message"))

        # Add different data to agent2
        agent2.memory.add_context("vehicle_type", "suv")
        agent2.memory.add_message(HumanMessage(content="Agent 2 message"))

        # Verify isolation
        assert agent1.memory.get_context("vehicle_type") == "sedan"
        assert agent2.memory.get_context("vehicle_type") == "suv"

        assert agent1.memory.get_messages()[0].content == "Agent 1 message"
        assert agent2.memory.get_messages()[0].content == "Agent 2 message"

    @patch('langchain_community.chat_message_histories.PostgresChatMessageHistory')
    def test_postgres_session_isolation(self, mock_postgres, mock_llm):
        """Test that PostgreSQL sessions are isolated."""
        mock_history_instance_1 = MagicMock()
        mock_history_instance_1.messages = []
        mock_history_instance_2 = MagicMock()
        mock_history_instance_2.messages = []

        # Return different instances for different sessions
        def side_effect(*args, **kwargs):
            session_id = kwargs.get('session_id')
            if session_id == "session_1":
                return mock_history_instance_1
            else:
                return mock_history_instance_2

        mock_postgres.side_effect = side_effect

        config1 = MemoryBackendConfig(
            backend_type="postgres",
            connection_string="postgresql://localhost/test",
            session_id="session_1"
        )

        config2 = MemoryBackendConfig(
            backend_type="postgres",
            connection_string="postgresql://localhost/test",
            session_id="session_2"
        )

        agent1 = CarAgent(llm=mock_llm, enable_logging=False, memory_config=config1)
        agent2 = CarAgent(llm=mock_llm, enable_logging=False, memory_config=config2)

        # Verify different sessions
        assert agent1.memory.session_id == "session_1"
        assert agent2.memory.session_id == "session_2"


class TestMemoryContextAccumulation:
    """Test context accumulation across agent operations."""

    def test_context_accumulation_during_car_creation(self, mock_llm):
        """Test that context accumulates during car creation."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        requirements = {
            "vehicle_type": "sedan",
            "performance_level": "standard"
        }

        result = {
            "car_configuration": {
                "engine": {"displacement": "2.5L"},
                "body": {"style": "sedan"}
            }
        }

        # Simulate context update
        agent._update_context_memory(requirements, result)

        # Verify context was accumulated
        context = agent.memory.get_all_context()
        assert "req_vehicle_type" in context
        assert "req_performance_level" in context
        assert context["configured_engine"] == True
        assert context["configured_body"] == True

    def test_context_summary_reflects_accumulation(self, mock_llm):
        """Test that context summary reflects accumulated data."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Simulate multiple interactions
        agent.memory.add_context("req_vehicle_type", "sedan")
        agent.memory.add_context("req_fuel_preference", "gasoline")
        agent.memory.add_context("configured_engine", True)
        agent.memory.add_context("configured_body", True)

        summary = agent.memory.get_context_summary()

        # Should contain all accumulated context
        assert "req_vehicle_type" in summary
        assert "sedan" in summary
        assert "configured_engine" in summary
        assert "True" in summary or "configured_engine" in summary


class TestMemoryWithSystemIntegration:
    """Test memory integration with SingleAgentSystem."""

    def test_system_passes_memory_config_to_agent(self, mock_llm):
        """Test that SingleAgentSystem passes memory config to agent."""
        from single_agent_system import SingleAgentSystem

        # Mock ChatOllama
        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(
                model_name="test",
                enable_logging=False,
                memory_backend="memory",
                max_memory_messages=15
            )

            # Agent should have the configured memory
            assert hasattr(system.agent, 'memory')
            assert system.agent.memory.max_messages == 15

    @patch('langchain_community.chat_message_histories.PostgresChatMessageHistory')
    def test_system_with_postgres_config(self, mock_postgres, mock_llm):
        """Test SingleAgentSystem with PostgreSQL configuration."""
        from single_agent_system import SingleAgentSystem

        mock_history_instance = MagicMock()
        mock_history_instance.messages = []
        mock_postgres.return_value = mock_history_instance

        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(
                model_name="test",
                enable_logging=False,
                memory_backend="postgres",
                memory_connection_string="postgresql://localhost/test",
                memory_session_id="test_session_123"
            )

            # Verify PostgreSQL configuration
            assert hasattr(system.agent.memory, 'session_id')
            assert system.agent.memory.session_id == "test_session_123"

    def test_system_memory_backend_attribute(self, mock_llm):
        """Test that system tracks memory backend type."""
        from single_agent_system import SingleAgentSystem

        with patch('single_agent_system.ChatOllama', return_value=mock_llm):
            system = SingleAgentSystem(
                model_name="test",
                enable_logging=False,
                memory_backend="memory"
            )

            assert system.memory_backend == "memory"


class TestMemoryErrorHandling:
    """Test error handling in memory integration."""

    def test_agent_handles_memory_clear_gracefully(self, mock_llm):
        """Test that agent handles memory clear without errors."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Clear empty memory should not error
        agent.reset_memory()
        assert len(agent.memory.get_messages()) == 0

        # Clear with data should work
        agent.memory.add_message(HumanMessage(content="Test"))
        agent.reset_memory()
        assert len(agent.memory.get_messages()) == 0

    def test_agent_handles_missing_context_gracefully(self, mock_llm):
        """Test that agent handles missing context keys gracefully."""
        agent = CarAgent(llm=mock_llm, enable_logging=False)

        # Getting nonexistent context should return None
        result = agent.memory.get_context("nonexistent")
        assert result is None

    @patch('langchain_community.chat_message_histories.PostgresChatMessageHistory')
    def test_postgres_connection_error_isolation(self, mock_postgres, mock_llm):
        """Test that PostgreSQL connection errors are properly handled."""
        # This tests that errors don't crash the agent
        mock_postgres.side_effect = Exception("Connection failed")

        config = MemoryBackendConfig(
            backend_type="postgres",
            connection_string="postgresql://localhost/test"
        )

        # Should raise exception during initialization
        with pytest.raises(Exception, match="Connection failed"):
            agent = CarAgent(
                llm=mock_llm,
                enable_logging=False,
                memory_config=config
            )
