"""Basic test to check if the system works."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test if we can import the modules."""
    print("🧪 Testing imports...")
    
    try:
        from src.agents import MathAgent, ResearchAgent, SupervisorAgent
        print("✅ All agent imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_math_agent_tools():
    """Test MathAgent tools directly."""
    print("\n🧮 Testing MathAgent tools...")
    
    try:
        from src.agents.math_agent import MathAgent
        
        # Create agent without API key for tool testing
        math_agent = MathAgent(api_key="test-key")
        
        # Test calculator tool
        result = math_agent.tools[0].invoke("2 + 3 * 4")
        print(f"Calculator test: {result}")
        
        # Test statistics tool
        result = math_agent.tools[2].invoke("1, 2, 3, 4, 5")
        print(f"Statistics test: {result}")
        
        print("✅ MathAgent tools working")
        return True
    except Exception as e:
        print(f"❌ MathAgent tools failed: {e}")
        return False

def test_research_agent_tools():
    """Test ResearchAgent tools directly."""
    print("\n🔍 Testing ResearchAgent tools...")
    
    try:
        from src.agents.research_agent import ResearchAgent
        
        # Create agent without API key for tool testing
        research_agent = ResearchAgent(api_key="test-key")
        
        # Test web search tool
        result = research_agent.tools[0].invoke("artificial intelligence")
        print(f"Web search test: {result[:100]}...")
        
        # Test fact checker tool
        result = research_agent.tools[1].invoke("Earth is round")
        print(f"Fact checker test: {result}")
        
        print("✅ ResearchAgent tools working")
        return True
    except Exception as e:
        print(f"❌ ResearchAgent tools failed: {e}")
        return False

def test_supervisor_agent_tools():
    """Test SupervisorAgent tools directly."""
    print("\n👑 Testing SupervisorAgent tools...")
    
    try:
        from src.agents.supervisor_agent import SupervisorAgent
        
        # Create agent without API key for tool testing
        supervisor = SupervisorAgent(api_key="test-key")
        
        # Test task analyzer tool
        result = supervisor.tools[1].invoke("Calculate the area of a circle with radius 5")
        print(f"Task analyzer test: {result}")
        
        print("✅ SupervisorAgent tools working")
        return True
    except Exception as e:
        print(f"❌ SupervisorAgent tools failed: {e}")
        return False

def main():
    """Run basic tests."""
    print("🚀 Basic System Tests")
    print("=" * 40)
    
    # Test imports
    import_success = test_imports()
    
    # Test individual agent tools
    math_success = test_math_agent_tools()
    research_success = test_research_agent_tools()
    supervisor_success = test_supervisor_agent_tools()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   MathAgent Tools: {'✅ PASS' if math_success else '❌ FAIL'}")
    print(f"   ResearchAgent Tools: {'✅ PASS' if research_success else '❌ FAIL'}")
    print(f"   SupervisorAgent: {'✅ PASS' if supervisor_success else '❌ FAIL'}")
    
    if all([import_success, math_success, research_success, supervisor_success]):
        print("\n🎉 Basic tests passed! The system structure is working.")
        print("\n💡 To test with API calls, set your OPENAI_API_KEY and run:")
        print("   uv run python test_system.py")
    else:
        print("\n⚠️  Some basic tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
