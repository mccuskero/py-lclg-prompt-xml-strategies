#!/usr/bin/env python3
"""
Demonstration script for the new LangChain-based memory system.
Shows memory operations with detailed logging.
"""

import sys
import logging
from pathlib import Path
from unittest.mock import Mock
from langchain_core.messages import HumanMessage, AIMessage

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory.memory_manager import (
    MemoryBackendConfig,
    InMemoryManager,
    create_memory_manager
)
from agents.car_agent import CarAgent

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('memory_demo.log')
    ]
)

logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_basic_memory_operations():
    """Demonstrate basic memory manager operations."""
    print_section("1. Basic Memory Manager Operations")

    # Create in-memory manager
    config = MemoryBackendConfig(backend_type="memory")
    memory = create_memory_manager(config, max_messages=5)

    logger.info("Created InMemoryManager with max_messages=5")
    print(f"✓ Memory manager created: {type(memory).__name__}")
    print(f"✓ Max messages: {memory.max_messages}")

    # Add messages
    print("\n📝 Adding messages to memory...")
    memory.add_message(HumanMessage(content="I want to create a sports car"))
    logger.debug("Added HumanMessage: 'I want to create a sports car'")

    memory.add_message(AIMessage(content="Great! I'll help you configure a sports car."))
    logger.debug("Added AIMessage: 'Great! I'll help you configure a sports car.'")

    memory.add_message(HumanMessage(content="What color options do I have?"))
    logger.debug("Added HumanMessage: 'What color options do I have?'")

    # Display messages
    messages = memory.get_messages()
    print(f"\n✓ Total messages in memory: {len(messages)}")
    for idx, msg in enumerate(messages, 1):
        msg_type = type(msg).__name__
        print(f"  [{idx}] {msg_type}: {msg.content[:60]}...")

    # Add context
    print("\n🔑 Adding context data...")
    memory.add_context("vehicle_type", "sports")
    memory.add_context("performance_level", "high")
    memory.add_context("fuel_preference", "gasoline")
    logger.debug("Added context: vehicle_type=sports, performance_level=high, fuel_preference=gasoline")

    # Display context
    context = memory.get_all_context()
    print(f"✓ Total context items: {len(context)}")
    for key, value in context.items():
        print(f"  • {key}: {value}")

    # Get context summary
    print("\n📊 Context Summary:")
    summary = memory.get_context_summary()
    print(summary)

    return memory


def demo_sliding_window():
    """Demonstrate sliding window memory management."""
    print_section("2. Sliding Window Memory Management")

    config = MemoryBackendConfig(backend_type="memory")
    memory = create_memory_manager(config, max_messages=3)

    print(f"✓ Created memory with max_messages=3")
    logger.info("Demonstrating sliding window with max_messages=3")

    # Add 5 messages
    print("\n📝 Adding 5 messages (exceeding limit)...")
    for i in range(5):
        msg = HumanMessage(content=f"Message {i+1}")
        memory.add_message(msg)
        logger.debug(f"Added message {i+1}/5")
        print(f"  Added: Message {i+1}")

    # Show that only last 3 are kept
    messages = memory.get_messages()
    print(f"\n✓ Messages after sliding window:")
    print(f"  Expected: 3 messages (last 3 added)")
    print(f"  Actual: {len(messages)} messages")

    for idx, msg in enumerate(messages, 1):
        print(f"  [{idx}] {msg.content}")

    assert len(messages) == 3, "Sliding window should keep only 3 messages"
    assert messages[0].content == "Message 3", "Should have Message 3 as first"
    assert messages[2].content == "Message 5", "Should have Message 5 as last"

    logger.info("✓ Sliding window working correctly")
    print("\n✅ Sliding window test passed!")


def demo_agent_with_memory():
    """Demonstrate agent integration with memory."""
    print_section("3. Agent Integration with Memory")

    # Create mock LLM
    mock_llm = Mock()
    mock_response = {
        'messages': [
            AIMessage(content='''{
                "car_configuration": {
                    "vehicle_info": {"type": "sports", "category": "performance"},
                    "engine": {
                        "displacement": "5.0L",
                        "cylinders": "8",
                        "fuelType": "gasoline",
                        "horsepower": "450",
                        "@engineCode": "V8-500",
                        "@manufacturer": "Performance Motors"
                    },
                    "body": {
                        "exterior": {
                            "style": "coupe",
                            "color": "red",
                            "doors": 2,
                            "material": "aluminum"
                        }
                    },
                    "electrical": {
                        "main_system": {
                            "voltage_system": "12V",
                            "battery_capacity": "90Ah"
                        }
                    },
                    "tires_and_wheels": {
                        "tires": {
                            "brand": "Performance",
                            "size": "255/35R20",
                            "pressure": "35 PSI"
                        }
                    }
                }
            }''')
        ]
    }
    mock_llm.invoke = Mock(return_value=mock_response)

    # Create agent with memory configuration
    config = MemoryBackendConfig(backend_type="memory")
    agent = CarAgent(
        llm=mock_llm,
        enable_logging=True,
        log_llm_comms=False,
        memory_config=config,
        max_memory_messages=10
    )

    logger.info("Created CarAgent with LangChain memory manager")
    print(f"✓ Agent created: {agent.name}")
    print(f"✓ Memory type: {type(agent.memory).__name__}")
    print(f"✓ Max messages: {agent.memory.max_messages}")

    # Check agent info
    info = agent.get_agent_info()
    print(f"\n📋 Agent Info:")
    print(f"  • Name: {info['name']}")
    print(f"  • Type: {info['type']}")
    print(f"  • Tools: {len(info['tools'])} available")
    print(f"  • Context items: {info['context_items']}")
    print(f"  • Message history: {info['message_history']}")

    # Simulate interaction
    print("\n🚗 Creating car configuration...")
    requirements = {
        "vehicle_type": "sports",
        "performance_level": "high",
        "fuel_preference": "gasoline",
        "budget": "high"
    }

    logger.info(f"Processing requirements: {requirements}")
    result = agent.create_complete_car(requirements)

    if "error" not in result:
        print("✅ Car configuration created successfully!")

        # Check memory after operation
        print(f"\n🧠 Memory State After Operation:")
        context = agent.memory.get_all_context()
        messages = agent.memory.get_messages()

        print(f"  • Context items: {len(context)}")
        print(f"  • Messages: {len(messages)}")

        print("\n  Context data:")
        for key, value in list(context.items())[:5]:  # Show first 5
            print(f"    - {key}: {value}")

        if len(context) > 5:
            print(f"    ... and {len(context) - 5} more items")
    else:
        print(f"❌ Error: {result['error']}")

    return agent


def demo_memory_persistence():
    """Demonstrate memory persistence across multiple operations."""
    print_section("4. Memory Persistence Across Operations")

    # Create mock LLM
    mock_llm = Mock()
    mock_llm.invoke = Mock(return_value={
        'messages': [AIMessage(content='{"car_configuration": {"engine": {}}}')]
    })

    # Create agent
    agent = CarAgent(llm=mock_llm, enable_logging=False)

    print("🔄 Simulating multiple interactions...")

    # First interaction
    print("\n  [1] First interaction: Adding color preference")
    agent.memory.add_context("color_preference", "red")
    agent.memory.add_message(HumanMessage(content="I want a red car"))
    logger.debug("First interaction: color_preference=red")

    # Second interaction
    print("  [2] Second interaction: Adding engine preference")
    agent.memory.add_context("engine_type", "V8")
    agent.memory.add_message(AIMessage(content="Great! I'll configure a V8 engine"))
    logger.debug("Second interaction: engine_type=V8")

    # Third interaction
    print("  [3] Third interaction: Adding budget")
    agent.memory.add_context("budget", "high")
    agent.memory.add_message(HumanMessage(content="I have a high budget"))
    logger.debug("Third interaction: budget=high")

    # Check persistence
    print("\n✓ Memory persistence check:")
    context = agent.memory.get_all_context()
    messages = agent.memory.get_messages()

    print(f"  • Total context items: {len(context)}")
    print(f"  • Total messages: {len(messages)}")

    # Verify all data is present
    assert agent.memory.get_context("color_preference") == "red"
    assert agent.memory.get_context("engine_type") == "V8"
    assert agent.memory.get_context("budget") == "high"

    print("\n  All context preserved:")
    for key, value in context.items():
        print(f"    ✓ {key}: {value}")

    print("\n  Message history:")
    for idx, msg in enumerate(messages, 1):
        msg_type = type(msg).__name__
        print(f"    [{idx}] {msg_type}: {msg.content[:50]}...")

    logger.info("✓ Memory persistence verified")
    print("\n✅ Persistence test passed!")


def demo_memory_reset():
    """Demonstrate memory reset functionality."""
    print_section("5. Memory Reset Functionality")

    # Create memory with data
    config = MemoryBackendConfig(backend_type="memory")
    memory = create_memory_manager(config, max_messages=10)

    # Add data
    print("📝 Adding data to memory...")
    memory.add_message(HumanMessage(content="Test message 1"))
    memory.add_message(AIMessage(content="Test response 1"))
    memory.add_context("key1", "value1")
    memory.add_context("key2", "value2")

    print(f"  • Messages: {len(memory.get_messages())}")
    print(f"  • Context items: {len(memory.get_all_context())}")

    # Reset
    print("\n🔄 Resetting memory...")
    memory.clear()
    logger.info("Memory cleared")

    # Verify reset
    print("✓ Memory after reset:")
    print(f"  • Messages: {len(memory.get_messages())}")
    print(f"  • Context items: {len(memory.get_all_context())}")

    assert len(memory.get_messages()) == 0
    assert len(memory.get_all_context()) == 0

    print("\n✅ Reset test passed!")


def demo_multiple_agents():
    """Demonstrate memory isolation between multiple agents."""
    print_section("6. Memory Isolation Between Agents")

    # Create mock LLM
    mock_llm = Mock()
    mock_llm.invoke = Mock(return_value={
        'messages': [AIMessage(content='{"car_configuration": {}}')]
    })

    # Create two agents
    print("🤖 Creating two separate agents...")
    agent1 = CarAgent(llm=mock_llm, enable_logging=False)
    agent2 = CarAgent(llm=mock_llm, enable_logging=False)

    print(f"  • Agent 1: {agent1.name}")
    print(f"  • Agent 2: {agent2.name}")

    # Add different data to each
    print("\n📝 Adding different data to each agent...")
    agent1.memory.add_context("vehicle_type", "sports")
    agent1.memory.add_message(HumanMessage(content="Agent 1 message"))
    print("  • Agent 1: vehicle_type=sports")

    agent2.memory.add_context("vehicle_type", "suv")
    agent2.memory.add_message(HumanMessage(content="Agent 2 message"))
    print("  • Agent 2: vehicle_type=suv")

    # Verify isolation
    print("\n✓ Verifying memory isolation:")
    agent1_type = agent1.memory.get_context("vehicle_type")
    agent2_type = agent2.memory.get_context("vehicle_type")

    print(f"  • Agent 1 vehicle_type: {agent1_type}")
    print(f"  • Agent 2 vehicle_type: {agent2_type}")

    assert agent1_type == "sports"
    assert agent2_type == "suv"
    assert agent1_type != agent2_type

    logger.info("✓ Memory isolation verified")
    print("\n✅ Isolation test passed!")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print(" " * 20 + "LangChain Memory System Demonstration")
    print("=" * 80)

    try:
        # Run demonstrations
        demo_basic_memory_operations()
        demo_sliding_window()
        demo_agent_with_memory()
        demo_memory_persistence()
        demo_memory_reset()
        demo_multiple_agents()

        # Summary
        print_section("Summary")
        print("✅ All demonstrations completed successfully!")
        print("\n📊 Features Demonstrated:")
        print("  ✓ Basic memory operations (add, get, clear)")
        print("  ✓ Sliding window memory management")
        print("  ✓ Agent integration with LangChain memory")
        print("  ✓ Memory persistence across operations")
        print("  ✓ Memory reset functionality")
        print("  ✓ Memory isolation between agents")

        print("\n📝 Logs saved to: memory_demo.log")
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Demonstration failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
