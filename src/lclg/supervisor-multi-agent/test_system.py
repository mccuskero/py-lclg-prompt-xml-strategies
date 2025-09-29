"""Test script for the multi-agent system."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_math_agent():
    """Test the MathAgent functionality."""
    print("🧮 Testing MathAgent...")
    
    try:
        from src.agents.math_agent import MathAgent
        from src.agents.base_agent import AgentMessage
        
        # Initialize MathAgent
        math_agent = MathAgent(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test calculator tool
        print("Testing calculator tool...")
        result = math_agent.tools[0].func("2 + 3 * 4")
        print(f"Calculator result: {result}")
        
        # Test statistics tool
        print("Testing statistics tool...")
        result = math_agent.tools[2].func("1, 2, 3, 4, 5")
        print(f"Statistics result: {result}")
        
        print("✅ MathAgent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MathAgent test failed: {str(e)}")
        return False

async def test_research_agent():
    """Test the ResearchAgent functionality."""
    print("\n🔍 Testing ResearchAgent...")
    
    try:
        from src.agents.research_agent import ResearchAgent
        
        # Initialize ResearchAgent
        research_agent = ResearchAgent(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test web search tool
        print("Testing web search tool...")
        result = research_agent.tools[0].func("artificial intelligence")
        print(f"Web search result: {result[:200]}...")
        
        # Test fact checker tool
        print("Testing fact checker tool...")
        result = research_agent.tools[1].func("Earth is round")
        print(f"Fact checker result: {result}")
        
        print("✅ ResearchAgent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ResearchAgent test failed: {str(e)}")
        return False

async def test_supervisor_agent():
    """Test the SupervisorAgent functionality."""
    print("\n👑 Testing SupervisorAgent...")
    
    try:
        from src.agents.supervisor_agent import SupervisorAgent
        
        # Initialize SupervisorAgent
        supervisor = SupervisorAgent(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test task analyzer tool
        print("Testing task analyzer tool...")
        result = supervisor.tools[1].func("Calculate the area of a circle with radius 5")
        print(f"Task analyzer result: {result}")
        
        # Test coordination tool
        print("Testing coordination tool...")
        result = supervisor.tools[2].func("Research climate change and calculate carbon footprint")
        print(f"Coordination result: {result}")
        
        print("✅ SupervisorAgent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ SupervisorAgent test failed: {str(e)}")
        return False

async def test_full_system():
    """Test the complete multi-agent system."""
    print("\n🤖 Testing Full Multi-Agent System...")
    
    try:
        from src.main import MultiAgentSystem
        
        # Initialize the system
        system = MultiAgentSystem()
        
        # Test simple math query
        print("Testing math query...")
        response = await system.process_query("Calculate 2 + 2")
        print(f"Math query response: {response[:200]}...")
        
        # Test research query
        print("Testing research query...")
        response = await system.process_query("What is artificial intelligence?")
        print(f"Research query response: {response[:200]}...")
        
        print("✅ Full system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Full system test failed: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Multi-Agent System Tests")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        print("\n💡 To run with uv:")
        print("   uv run python test_system.py")
        return
    
    # Run individual agent tests
    math_success = await test_math_agent()
    research_success = await test_research_agent()
    supervisor_success = await test_supervisor_agent()
    
    # Run full system test
    system_success = await test_full_system()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   MathAgent: {'✅ PASS' if math_success else '❌ FAIL'}")
    print(f"   ResearchAgent: {'✅ PASS' if research_success else '❌ FAIL'}")
    print(f"   SupervisorAgent: {'✅ PASS' if supervisor_success else '❌ FAIL'}")
    print(f"   Full System: {'✅ PASS' if system_success else '❌ FAIL'}")
    
    if all([math_success, research_success, supervisor_success, system_success]):
        print("\n🎉 All tests passed! The multi-agent system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
