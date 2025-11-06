#!/usr/bin/env python3
"""
Quick demonstration of car creation with XML output and memory tracking.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory.memory_manager import MemoryBackendConfig, create_memory_manager
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def dict_to_xml(data, root_name="car"):
    """Convert dictionary to XML format."""
    def build_element(parent, key, value):
        """Recursively build XML elements."""
        if isinstance(value, dict):
            element = ET.SubElement(parent, key)
            for k, v in value.items():
                if k.startswith('@'):
                    element.set(k[1:], str(v))
                else:
                    build_element(element, k, v)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    build_element(parent, key, item)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(item)
        else:
            element = ET.SubElement(parent, key)
            element.text = str(value)

    root = ET.Element(root_name)
    root.set("timestamp", datetime.now().isoformat())
    root.set("generator", "single-agent-car-creation-system")
    root.set("memory_backend", "langchain-in-memory")

    if isinstance(data, dict):
        for key, value in data.items():
            build_element(root, key, value)

    xml_string = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ")


def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print(" " * 15 + "Car Creation System with XML Output")
    print(" " * 18 + "Memory Management Demonstration")
    print("=" * 80)

    # Step 1: Initialize Memory Manager
    print_section("Step 1: Initialize LangChain Memory Manager")

    config = MemoryBackendConfig(backend_type="memory")
    memory = create_memory_manager(config, max_messages=10)

    print("✓ Memory manager initialized")
    print(f"  • Type: {type(memory).__name__}")
    print(f"  • Backend: In-Memory (LangChain)")
    print(f"  • Max messages: {memory.max_messages}")

    logger.info("Memory manager initialized with LangChain InMemoryChatMessageHistory")

    # Step 2: Simulate Car Creation Process
    print_section("Step 2: Car Creation with Memory Tracking")

    print("\n🚗 Creating sports car configuration...")

    # Simulate user request
    user_request = "Create a high-performance sports car with V8 engine, red exterior, and premium features"
    memory.add_message(HumanMessage(content=user_request))
    print(f"\n[User Request]")
    print(f"  {user_request}")

    # Store requirements in context
    requirements = {
        "vehicle_type": "sports",
        "performance_level": "high",
        "fuel_preference": "gasoline",
        "budget": "high"
    }

    for key, value in requirements.items():
        memory.add_context(key, value)

    print(f"\n✓ Stored requirements in memory context:")
    for key, value in requirements.items():
        print(f"  • {key}: {value}")

    logger.info(f"Added {len(requirements)} context items to memory")

    # Simulate agent response
    agent_response = "I'll create a high-performance sports car configuration for you."
    memory.add_message(AIMessage(content=agent_response))
    print(f"\n[Agent Response]")
    print(f"  {agent_response}")

    # Create configuration
    car_config = {
        "car_configuration": {
            "vehicle_info": {
                "@id": "CAR-2024-SPORTS-001",
                "type": "sports",
                "category": "performance",
                "year": "2024",
                "manufacturer": "Generic Motors"
            },
            "engine": {
                "@engineCode": "V8-500-TURBO",
                "@manufacturer": "Performance Motors",
                "displacement": "5.0L",
                "cylinders": "8",
                "configuration": "V8",
                "fuelType": "gasoline",
                "horsepower": "500 HP",
                "torque": "450 lb-ft",
                "aspiration": "twin-turbocharged",
                "redline": "7000 RPM"
            },
            "body": {
                "exterior": {
                    "@paintCode": "PERFORMANCE-RED-2024",
                    "@customized": "true",
                    "style": "coupe",
                    "color": "red",
                    "doors": "2",
                    "material": "carbon-fiber-aluminum",
                    "aerodynamics": "active-aero",
                    "drag_coefficient": "0.28"
                },
                "interior": {
                    "seating": "4-passenger",
                    "upholstery": "premium-leather",
                    "dashboard": "digital-cockpit",
                    "trim": "carbon-fiber",
                    "steering_wheel": "alcantara-wrapped"
                }
            },
            "electrical": {
                "@systemType": "12V",
                "@hybridCapable": "false",
                "main_system": {
                    "voltage_system": "12V",
                    "battery_capacity": "100Ah",
                    "alternator_output": "200A"
                },
                "battery": {
                    "voltage": "12V",
                    "capacity": "100Ah",
                    "type": "AGM-performance",
                    "cold_cranking_amps": "950"
                },
                "lighting": {
                    "headlights": "matrix-LED",
                    "taillights": "OLED",
                    "fog_lights": "LED",
                    "interior": "ambient-RGB-LED"
                }
            },
            "tires_and_wheels": {
                "tires": {
                    "@position": "all-corners",
                    "brand": "Performance Plus Pro",
                    "size_front": "255/35R20",
                    "size_rear": "295/30R20",
                    "pressure": "36 PSI",
                    "type": "summer-performance-compound"
                },
                "wheels": {
                    "size_front": "20x9 inch",
                    "size_rear": "20x11 inch",
                    "material": "forged-aluminum",
                    "design": "multi-spoke-performance",
                    "finish": "gloss-black"
                }
            },
            "performance_specs": {
                "acceleration_0_60": "3.2 seconds",
                "acceleration_0_100": "7.5 seconds",
                "quarter_mile": "11.3 seconds",
                "top_speed": "198 mph",
                "horsepower_to_weight": "0.17 HP/lb",
                "braking_60_0": "95 feet"
            },
            "fuel_economy": {
                "city": "14 mpg",
                "highway": "21 mpg",
                "combined": "17 mpg",
                "tank_capacity": "18.5 gallons"
            },
            "features": {
                "safety": {
                    "item": [
                        "ABS with EBD",
                        "Electronic Stability Control",
                        "Traction Control",
                        "Airbags (10 total)",
                        "Blind Spot Monitoring",
                        "Lane Departure Warning",
                        "Forward Collision Warning",
                        "Automatic Emergency Braking"
                    ]
                },
                "technology": {
                    "item": [
                        "Adaptive Cruise Control",
                        "GPS Navigation with Real-Time Traffic",
                        "Premium 12-Speaker Sound System",
                        "Apple CarPlay & Android Auto",
                        "Wireless Phone Charging",
                        "Head-Up Display",
                        "360-Degree Camera System"
                    ]
                },
                "comfort": {
                    "item": [
                        "Dual-Zone Climate Control",
                        "Heated & Ventilated Seats",
                        "Power Adjustable Sport Seats",
                        "Keyless Entry & Start",
                        "Auto-Dimming Mirrors",
                        "Rain-Sensing Wipers"
                    ]
                }
            }
        },
        "metadata": {
            "created_by": "car_agent",
            "creation_method": "single_agent_system_with_langchain_memory",
            "memory_backend": "langchain_in_memory",
            "requirements_used": requirements,
            "performance_category": "high_performance",
            "estimated_compatibility": "compatible",
            "configuration_complete": "true"
        }
    }

    # Store configuration in context
    memory.add_context("configuration_complete", True)
    memory.add_context("car_type_created", "sports")
    memory.add_context("power_output", "500 HP")

    print(f"\n✓ Car configuration created")

    # Step 3: Show Memory State
    print_section("Step 3: Memory State After Car Creation")

    messages = memory.get_messages()
    context = memory.get_all_context()

    print(f"\n🧠 Memory Statistics:")
    print(f"  • Total messages: {len(messages)}")
    print(f"  • Total context items: {len(context)}")

    print(f"\n📝 Message History:")
    for idx, msg in enumerate(messages, 1):
        msg_type = type(msg).__name__
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"  [{idx}] {msg_type}: {content_preview}")

    print(f"\n🔑 Context Data:")
    for key, value in context.items():
        print(f"  • {key}: {value}")

    print(f"\n📊 Context Summary:")
    summary = memory.get_context_summary()
    for line in summary.split('\n')[:10]:  # First 10 lines
        print(f"  {line}")

    logger.info(f"Memory state: {len(messages)} messages, {len(context)} context items")

    # Step 4: Convert to XML
    print_section("Step 4: Convert Configuration to XML")

    print("🔄 Converting JSON to XML format...")
    xml_output = dict_to_xml(car_config, root_name="vehicle")

    print("✓ Conversion complete")

    # Step 5: Display XML
    print_section("Step 5: XML Car Configuration")
    print(xml_output)

    # Step 6: Save files
    print_section("Step 6: Save Output Files")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save XML
    xml_filename = f"car_configuration_{timestamp}.xml"
    with open(xml_filename, 'w') as f:
        f.write(xml_output)
    print(f"✓ XML saved: {xml_filename}")

    # Save JSON
    json_filename = f"car_configuration_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(car_config, f, indent=2)
    print(f"✓ JSON saved: {json_filename}")

    # Save memory state
    memory_state = {
        "messages": [
            {"type": type(msg).__name__, "content": msg.content}
            for msg in messages
        ],
        "context": context,
        "summary": summary
    }
    memory_filename = f"memory_state_{timestamp}.json"
    with open(memory_filename, 'w') as f:
        json.dump(memory_state, f, indent=2)
    print(f"✓ Memory state saved: {memory_filename}")

    # Summary
    print_section("Summary")

    print("✅ Car creation demonstration completed successfully!\n")

    print("📊 Configuration Details:")
    print(f"  • Vehicle: High-Performance Sports Car")
    print(f"  • Engine: V8 Twin-Turbo 5.0L (500 HP)")
    print(f"  • Exterior: Performance Red Coupe")
    print(f"  • 0-60 mph: 3.2 seconds")
    print(f"  • Top Speed: 198 mph")

    print(f"\n🧠 Memory Management:")
    print(f"  • Backend: LangChain InMemoryManager")
    print(f"  • Messages tracked: {len(messages)}")
    print(f"  • Context items stored: {len(context)}")
    print(f"  • Sliding window: {memory.max_messages} messages max")

    print(f"\n💾 Output Files:")
    print(f"  • {xml_filename} - XML car configuration")
    print(f"  • {json_filename} - JSON car configuration")
    print(f"  • {memory_filename} - Memory state snapshot")

    print("\n" + "=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
