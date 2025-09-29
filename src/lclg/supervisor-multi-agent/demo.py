"""Simple demo of the multi-agent system."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_math_agent():
    """Demo the MathAgent tools."""
    print("🧮 MathAgent Demo")
    print("=" * 40)
    
    from src.agents.math_agent import MathAgent
    
    # Create MathAgent
    math_agent = MathAgent(api_key="demo-key")
    
    # Demo calculator
    print("Calculator Demo:")
    result = math_agent.tools[0].invoke("15 * 23 + 45")
    print(f"  15 * 23 + 45 = {result}")
    
    # Demo statistics
    print("\nStatistics Demo:")
    result = math_agent.tools[2].invoke("10, 20, 30, 40, 50")
    print(f"  Stats for [10, 20, 30, 40, 50]:\n{result}")
    
    # Demo geometry
    print("\nGeometry Demo:")
    result = math_agent.tools[3].invoke("circle radius 5")
    print(f"  Circle with radius 5:\n{result}")

async def demo_research_agent():
    """Demo the ResearchAgent tools."""
    print("\n🔍 ResearchAgent Demo")
    print("=" * 40)
    
    from src.agents.research_agent import ResearchAgent
    
    # Create ResearchAgent
    research_agent = ResearchAgent(api_key="demo-key")
    
    # Demo web search
    print("Web Search Demo:")
    result = research_agent.tools[0].invoke("machine learning")
    print(f"  Search results for 'machine learning':\n{result[:200]}...")
    
    # Demo fact checker
    print("\nFact Checker Demo:")
    result = research_agent.tools[1].invoke("Water boils at 100 degrees Celsius")
    print(f"  Fact check: {result}")
    
    # Demo summarizer
    print("\nSummarizer Demo:")
    long_text = "Artificial Intelligence is a rapidly evolving field that combines computer science, mathematics, and cognitive science. It involves creating systems that can perform tasks typically requiring human intelligence. Machine learning is a subset of AI that focuses on algorithms that can learn from data. Deep learning uses neural networks with multiple layers to process complex patterns. AI applications include natural language processing, computer vision, robotics, and autonomous systems."
    result = research_agent.tools[2].invoke(long_text)
    print(f"  Summary:\n{result}")

async def demo_supervisor_agent():
    """Demo the SupervisorAgent tools."""
    print("\n👑 SupervisorAgent Demo")
    print("=" * 40)
    
    from src.agents.supervisor_agent import SupervisorAgent
    
    # Create SupervisorAgent
    supervisor = SupervisorAgent(api_key="demo-key")
    
    # Demo task analyzer
    print("Task Analyzer Demo:")
    result = supervisor.tools[1].invoke("Research climate change and calculate carbon footprint")
    print(f"  Task analysis:\n{result}")
    
    # Demo coordination
    print("\nCoordination Demo:")
    result = supervisor.tools[2].invoke("Find information about renewable energy and calculate cost savings")
    print(f"  Workflow coordination:\n{result}")
    
    # Demo result synthesizer
    print("\nResult Synthesizer Demo:")
    results = """Research Results: Solar energy costs have decreased by 80% over the past decade.
Math Results: Cost savings calculation shows $2,500 annual savings for a 5kW system.
Recommendations: Consider installing solar panels for maximum cost benefit."""
    result = supervisor.tools[3].invoke(results)
    print(f"  Synthesized results:\n{result}")

async def main():
    """Run all demos."""
    print("🚀 Multi-Agent System Demo")
    print("=" * 50)
    print("This demo shows the individual agent tools working without API calls.")
    print("=" * 50)
    
    try:
        await demo_math_agent()
        await demo_research_agent()
        await demo_supervisor_agent()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n💡 To test with full API integration:")
        print("   1. Set your OPENAI_API_KEY in .env file")
        print("   2. Run: uv run python src/main.py")
        print("   3. Or run: uv run python examples.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    asyncio.run(main())
