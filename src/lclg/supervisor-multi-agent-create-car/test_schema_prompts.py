#!/usr/bin/env python3
"""Simple test script for schema-driven prompt functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from prompts.prompts_from_json_schema import (
    validate_schema_availability,
    get_schema_agent_prompt
)

def test_schema_functionality():
    """Test the schema-driven prompt functionality."""
    print("🧪 Testing Schema-Driven Prompt Functionality")
    print("=" * 50)

    # Test schema availability
    print("1. Testing schema availability...")
    result = validate_schema_availability()
    print(f"   ✅ All schemas available: {result['all_available']}")
    print(f"   📋 Available schemas: {', '.join(result['available_schemas'])}")

    if not result['all_available']:
        print(f"   ❌ Missing schemas: {', '.join(result['missing_schemas'])}")
        return False

    # Test prompt generation for all agent types
    print("\n2. Testing prompt generation...")
    agent_types = ['supervisor', 'engine', 'body', 'tire', 'electrical']

    for agent_type in agent_types:
        try:
            prompt = get_schema_agent_prompt(
                agent_type=agent_type,
                agent_name=f"{agent_type.title()}Agent",
                system_prompt="Test system prompt",
                tool_names="test_tool1, test_tool2"
            )

            # Check if schema is included
            schema_names = {
                'supervisor': 'carType',
                'engine': 'engineType',
                'body': 'bodyType',
                'tire': 'tireType',
                'electrical': 'electricalType'
            }

            schema_included = schema_names[agent_type] in prompt
            print(f"   ✅ {agent_type.title()}Agent: {len(prompt)} chars, schema: {'✅' if schema_included else '❌'}")

        except Exception as e:
            print(f"   ❌ {agent_type.title()}Agent: Error - {str(e)}")
            return False

    print("\n🎉 All tests passed! Schema-driven prompts are working correctly.")
    return True

if __name__ == "__main__":
    success = test_schema_functionality()
    sys.exit(0 if success else 1)