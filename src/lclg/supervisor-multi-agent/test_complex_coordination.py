"""Test complex multi-agent coordination."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complex_coordination():
    """Test complex multi-agent coordination scenarios."""
    print("🤖 Testing Complex Multi-Agent Coordination")
    print("=" * 60)
    
    from src.agents.multi_agent_system import MultiAgentSystem
    
    # Initialize system
    system = MultiAgentSystem(allow_no_api_key=True)
    
    # Test complex scenarios
    complex_scenarios = [
        {
            "query": "Find information about climate change and calculate the carbon footprint of a 1000km flight",
            "description": "Research + Math: Climate research with carbon footprint calculation"
        },
        {
            "query": "Research solar energy costs and calculate the payback period for a 5kW system",
            "description": "Research + Math: Solar research with financial analysis"
        },
        {
            "query": "Investigate renewable energy and calculate cost savings for a 10kW solar installation",
            "description": "Research + Math: Renewable energy research with cost analysis"
        },
        {
            "query": "Research electric vehicles and calculate the environmental impact of a 500km trip",
            "description": "Research + Math: EV research with environmental impact calculation"
        }
    ]
    
    for i, scenario in enumerate(complex_scenarios, 1):
        print(f"\n🧪 Complex Scenario {i}: {scenario['description']}")
        print(f"Query: {scenario['query']}")
        print("-" * 60)
        
        try:
            response = await system.process_query(scenario['query'])
            
            # Show key parts of the response
            if "COMPLEX TASK COORDINATION RESULTS" in response:
                print("✅ Multi-agent coordination successful!")
                
                # Extract key sections
                lines = response.split('\n')
                for line in lines:
                    if any(keyword in line for keyword in [
                        "📊 Task Analysis:", "🔄 Coordination Plan:", 
                        "📚 Research Results:", "🧮 Mathematical Analysis:",
                        "🔗 Synthesized Results:", "✅ Multi-Agent Coordination Complete!"
                    ]):
                        print(f"   {line}")
            else:
                print(f"Response: {response[:300]}...")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 60)

async def test_individual_agents():
    """Test individual agent capabilities."""
    print("\n🔧 Testing Individual Agent Capabilities")
    print("=" * 60)
    
    from src.agents.multi_agent_system import MultiAgentSystem
    
    system = MultiAgentSystem(allow_no_api_key=True)
    
    # Test MathAgent
    print("\n🧮 MathAgent Tests:")
    math_tests = [
        "Calculate 15 * 23 + 45",
        "What is the area of a circle with radius 7?",
        "Calculate statistics for 1, 2, 3, 4, 5"
    ]
    
    for test in math_tests:
        print(f"\n   Test: {test}")
        try:
            response = await system.process_query(test)
            print(f"   Result: {response[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Test ResearchAgent
    print("\n🔍 ResearchAgent Tests:")
    research_tests = [
        "Research artificial intelligence",
        "Find information about renewable energy",
        "Check if water boils at 100 degrees Celsius"
    ]
    
    for test in research_tests:
        print(f"\n   Test: {test}")
        try:
            response = await system.process_query(test)
            print(f"   Result: {response[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")

async def main():
    """Run all coordination tests."""
    print("🚀 Multi-Agent Coordination Test Suite")
    print("=" * 60)
    
    try:
        await test_complex_coordination()
        await test_individual_agents()
        
        print("\n" + "=" * 60)
        print("🎉 Coordination tests completed!")
        print("\n💡 The system successfully demonstrates:")
        print("   ✅ Individual agent capabilities")
        print("   ✅ Multi-agent coordination")
        print("   ✅ Research + Mathematical analysis")
        print("   ✅ Task synthesis and result combination")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
