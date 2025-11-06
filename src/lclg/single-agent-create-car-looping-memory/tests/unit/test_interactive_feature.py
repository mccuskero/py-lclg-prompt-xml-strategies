"""
Test script to demonstrate the interactive user querying feature.

This script tests the new capability where the LLM can ask questions
to the user during the car creation process.
"""

import sys
from pathlib import Path

# Add src to path (go up two directories from tests/unit to project root, then into src)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for testing the _extract_question_json_from_response method."""

    def _setup_tools(self):
        pass

    def _setup_prompts(self):
        pass

    def _get_agent_type(self):
        return "mock"

    def _validate_component_data(self, data):
        return data


def test_extract_question_json():
    """Test the _extract_question_json_from_response method."""
    print("=" * 70)
    print("Testing _extract_question_json_from_response Method")
    print("=" * 70)

    # Create a mock LLM (we won't actually use it)
    from langchain_ollama import ChatOllama
    mock_llm = ChatOllama(model="llama3.2", temperature=0.1)

    # Create mock agent
    agent = MockAgent(
        name="test_agent",
        llm=mock_llm,
        enable_logging=False
    )

    # Test cases
    test_cases = [
        {
            "name": "Pure JSON format",
            "response": '{ "user_question": "What color would you like for the car?" }',
            "expected": "What color would you like for the car?"
        },
        {
            "name": "JSON with extra whitespace",
            "response": '  { "user_question" : "Do you prefer manual or automatic transmission?" }  ',
            "expected": "Do you prefer manual or automatic transmission?"
        },
        {
            "name": "JSON in code block",
            "response": '''```json
{
  "user_question": "What is your budget range?"
}
```''',
            "expected": "What is your budget range?"
        },
        {
            "name": "Inline pattern",
            "response": 'The answer is user_question: "What engine type do you prefer?"',
            "expected": "What engine type do you prefer?"
        },
        {
            "name": "No question present",
            "response": '{ "car_configuration": { "engine": "V6" } }',
            "expected": None
        },
        {
            "name": "Mixed content with question",
            "response": '''Here is my response:
{ "user_question": "How many seats do you need?" }
Based on your requirements...''',
            "expected": "How many seats do you need?"
        }
    ]

    # Run tests
    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Response: {test['response'][:60]}{'...' if len(test['response']) > 60 else ''}")

        result = agent._extract_question_json_from_response(test['response'])

        if result == test['expected']:
            print(f"✅ PASSED - Extracted: {result}")
            passed += 1
        else:
            print(f"❌ FAILED")
            print(f"   Expected: {test['expected']}")
            print(f"   Got: {result}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"Test Summary: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


def test_integration_flow():
    """Test the complete integration flow (simulated)."""
    print("\n" + "=" * 70)
    print("Integration Flow Simulation")
    print("=" * 70)

    print("""
This demonstrates how the interactive feature works in practice:

1. User starts session:
   $ python cli.py interactive

2. User provides vague requirement:
   [Iteration 1] Your request: I want a car

3. LLM responds with question:
   🤔 Agent Question: What type of vehicle are you looking for? (sedan, SUV, truck, etc.)
   Your answer: SUV

4. LLM asks follow-up:
   🤔 Agent Question: What color would you like for the exterior?
   Your answer: black

5. LLM continues with tools and creates configuration:
   ✅ Car configuration created successfully!

   📋 Vehicle Information:
     - type: suv
     - color: black
     ...

Key Points:
- Questions are stored in context
- Answers influence the configuration
- User can type 'skip' to use defaults
- Multiple questions can be asked in sequence
- All Q&A is preserved in memory for future iterations
""")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Interactive User Querying Feature - Test Suite")
    print("=" * 70)

    # Test 1: Extract question method
    test1_passed = test_extract_question_json()

    # Test 2: Integration flow (demo)
    test_integration_flow()

    # Final summary
    print("\n" + "=" * 70)
    print("All Tests Completed!")
    print("=" * 70)

    if test1_passed:
        print("\n✅ All extraction tests passed!")
        print("\nTo test the full interactive feature, run:")
        print("  python cli.py interactive --model llama3.2")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
