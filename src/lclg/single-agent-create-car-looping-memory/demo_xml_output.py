#!/usr/bin/env python3
"""
Demonstration script for car creation with XML output.
Shows memory operations and generates XML car configuration.
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

from single_agent_system import SingleAgentSystem

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('xml_demo.log')
    ]
)

logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def dict_to_xml(data, root_name="car"):
    """
    Convert dictionary to XML format.

    Args:
        data: Dictionary to convert
        root_name: Name of the root XML element

    Returns:
        XML string (prettified)
    """
    def build_element(parent, key, value):
        """Recursively build XML elements."""
        if isinstance(value, dict):
            # Handle attributes (keys starting with @)
            element = ET.SubElement(parent, key)
            for k, v in value.items():
                if k.startswith('@'):
                    # It's an attribute
                    element.set(k[1:], str(v))
                else:
                    # It's a child element
                    build_element(element, k, v)
        elif isinstance(value, list):
            # Handle lists
            for item in value:
                if isinstance(item, dict):
                    build_element(parent, key, item)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(item)
        else:
            # Simple value
            element = ET.SubElement(parent, key)
            element.text = str(value)

    # Create root element
    root = ET.Element(root_name)

    # Add timestamp attribute
    root.set("timestamp", datetime.now().isoformat())
    root.set("generator", "single-agent-car-creation-system")

    # Build XML tree
    if isinstance(data, dict):
        for key, value in data.items():
            build_element(root, key, value)

    # Convert to string and prettify
    xml_string = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ")


def create_sample_car_config():
    """Create a sample car configuration for demonstration."""
    return {
        "car_configuration": {
            "vehicle_info": {
                "@id": "CAR-2024-001",
                "type": "sports",
                "category": "performance",
                "year": "2024",
                "manufacturer": "Generic Motors"
            },
            "engine": {
                "@engineCode": "V8-500",
                "@manufacturer": "Performance Motors",
                "displacement": "5.0L",
                "cylinders": "8",
                "configuration": "V8",
                "fuelType": "gasoline",
                "horsepower": "450 HP",
                "torque": "400 lb-ft",
                "aspiration": "turbocharged"
            },
            "body": {
                "exterior": {
                    "@paintCode": "RED-2024",
                    "style": "coupe",
                    "color": "red",
                    "doors": "2",
                    "material": "aluminum",
                    "aerodynamics": "high-performance"
                },
                "interior": {
                    "seating": "4-passenger",
                    "upholstery": "leather",
                    "dashboard": "digital",
                    "trim": "carbon-fiber"
                }
            },
            "electrical": {
                "@systemType": "12V",
                "@hybridCapable": "false",
                "main_system": {
                    "voltage_system": "12V",
                    "battery_capacity": "90Ah",
                    "alternator_output": "180A"
                },
                "battery": {
                    "voltage": "12V",
                    "capacity": "90Ah",
                    "type": "AGM",
                    "cold_cranking_amps": "850"
                },
                "lighting": {
                    "headlights": "LED",
                    "taillights": "LED",
                    "fog_lights": "LED",
                    "interior": "ambient-LED"
                }
            },
            "tires_and_wheels": {
                "tires": {
                    "@position": "all",
                    "brand": "Performance Plus",
                    "size": "255/35R20",
                    "pressure": "35 PSI",
                    "type": "summer-performance"
                },
                "wheels": {
                    "size": "20 inch",
                    "material": "forged-aluminum",
                    "design": "multi-spoke",
                    "finish": "gloss-black"
                }
            },
            "performance": {
                "acceleration_0_60": "3.5 seconds",
                "top_speed": "190 mph",
                "horsepower_to_weight": "0.15 HP/lb",
                "fuel_economy_city": "15 mpg",
                "fuel_economy_highway": "22 mpg"
            },
            "features": {
                "safety": [
                    "ABS",
                    "Traction Control",
                    "Stability Control",
                    "Airbags (8)",
                    "Blind Spot Monitoring",
                    "Lane Departure Warning"
                ],
                "technology": [
                    "Adaptive Cruise Control",
                    "Navigation System",
                    "Premium Sound System",
                    "Bluetooth Connectivity",
                    "Wireless Charging"
                ],
                "comfort": [
                    "Climate Control",
                    "Heated Seats",
                    "Power Adjustable Seats",
                    "Keyless Entry",
                    "Push Button Start"
                ]
            }
        },
        "metadata": {
            "created_by": "car_agent",
            "creation_method": "single_agent_interactive_system",
            "requirements_used": {
                "vehicle_type": "sports",
                "performance_level": "high",
                "fuel_preference": "gasoline",
                "budget": "high"
            },
            "performance_summary": {
                "power_rating": "450 HP",
                "fuel_efficiency": "standard",
                "performance_category": "high_performance"
            },
            "estimated_compatibility": "compatible"
        }
    }


def demo_with_ollama():
    """Try to create a car using OLLAMA if available."""
    print_section("Creating Car with OLLAMA")

    try:
        import requests

        # Check if OLLAMA is available
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ OLLAMA server detected")
                logger.info("OLLAMA server is available")

                # Create system with memory configuration
                system = SingleAgentSystem(
                    model_name="llama3.2",
                    base_url="http://localhost:11434",
                    temperature=0.1,
                    enable_logging=True,
                    log_llm_comms=False,
                    memory_backend="memory",
                    max_memory_messages=10
                )

                print("\n🧠 Memory Configuration:")
                print(f"  • Backend: {system.memory_backend}")
                print(f"  • Max messages: 10")
                print(f"  • Context items: {len(system.agent.memory.get_all_context())}")

                # Create car
                print("\n🚗 Creating sports car...")
                requirements = {
                    "vehicle_type": "sports",
                    "performance_level": "high",
                    "fuel_preference": "gasoline",
                    "budget": "high"
                }

                result = system.run_single_request(requirements)

                # Check memory after creation
                print("\n🧠 Memory State After Creation:")
                context = system.agent.memory.get_all_context()
                messages = system.agent.memory.get_messages()
                print(f"  • Context items: {len(context)}")
                print(f"  • Messages: {len(messages)}")

                if len(context) > 0:
                    print("\n  Sample context:")
                    for key, value in list(context.items())[:3]:
                        print(f"    - {key}: {value}")

                return result

            else:
                print("⚠️  OLLAMA server not responding")
                return None

        except requests.exceptions.RequestException:
            print("⚠️  OLLAMA server not running")
            return None

    except ImportError:
        print("⚠️  requests module not available")
        return None


def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print(" " * 15 + "Car Creation System with XML Output")
    print(" " * 20 + "& Memory Management Demo")
    print("=" * 80)

    # Try to create with OLLAMA first
    car_config = demo_with_ollama()

    # If OLLAMA not available, use sample configuration
    if car_config is None or "error" in car_config:
        print_section("Using Sample Car Configuration")
        print("📝 Generating sample high-performance sports car...")
        car_config = create_sample_car_config()

        # Simulate memory operations
        print("\n🧠 Simulated Memory Operations:")
        print("  ✓ Added HumanMessage: 'Create a sports car'")
        print("  ✓ Added AIMessage: 'Creating configuration...'")
        print("  ✓ Context: vehicle_type=sports")
        print("  ✓ Context: performance_level=high")
        print("  ✓ Context: fuel_preference=gasoline")
        logger.info("Using sample configuration with simulated memory")

    # Display JSON configuration
    print_section("JSON Car Configuration")
    print(json.dumps(car_config, indent=2))

    # Convert to XML
    print_section("Converting to XML")
    print("🔄 Converting JSON to XML format...")

    try:
        xml_output = dict_to_xml(car_config, root_name="vehicle")
        logger.info("Successfully converted to XML")

        # Display XML
        print_section("XML Car Configuration")
        print(xml_output)

        # Save to file
        xml_filename = f"car_configuration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        with open(xml_filename, 'w') as f:
            f.write(xml_output)

        print_section("Output Summary")
        print(f"✅ XML file saved: {xml_filename}")
        print(f"✅ Log file saved: xml_demo.log")

        # Display configuration summary
        if "car_configuration" in car_config:
            config = car_config["car_configuration"]

            print("\n📊 Configuration Summary:")
            if "vehicle_info" in config:
                info = config["vehicle_info"]
                print(f"  • Vehicle Type: {info.get('type', 'N/A')}")
                print(f"  • Category: {info.get('category', 'N/A')}")

            if "engine" in config:
                engine = config["engine"]
                print(f"  • Engine: {engine.get('configuration', 'N/A')} {engine.get('displacement', 'N/A')}")
                print(f"  • Power: {engine.get('horsepower', 'N/A')}")

            if "body" in config:
                body = config["body"]
                if "exterior" in body:
                    ext = body["exterior"]
                    print(f"  • Body: {ext.get('color', 'N/A')} {ext.get('style', 'N/A')}")

            if "performance" in config:
                perf = config["performance"]
                print(f"  • 0-60 mph: {perf.get('acceleration_0_60', 'N/A')}")
                print(f"  • Top Speed: {perf.get('top_speed', 'N/A')}")

        # Display metadata
        if "metadata" in car_config:
            metadata = car_config["metadata"]
            print("\n📋 Metadata:")
            print(f"  • Created by: {metadata.get('created_by', 'N/A')}")
            print(f"  • Method: {metadata.get('creation_method', 'N/A')}")
            if "performance_summary" in metadata:
                perf_sum = metadata["performance_summary"]
                print(f"  • Performance: {perf_sum.get('performance_category', 'N/A')}")
                print(f"  • Compatibility: {metadata.get('estimated_compatibility', 'N/A')}")

        print("\n" + "=" * 80)
        print("✅ Demo completed successfully!")
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"XML conversion failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
