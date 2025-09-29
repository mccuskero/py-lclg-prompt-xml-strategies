"""Example usage of the multi-agent system."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def example_math_problems():
    """Example mathematical problems."""
    print("🧮 Mathematical Problems Examples")
    print("=" * 40)
    
    from src.main import MultiAgentSystem
    system = MultiAgentSystem()
    
    math_queries = [
        "Calculate the area of a circle with radius 5",
        "What is the standard deviation of the numbers 1, 2, 3, 4, 5?",
        "Solve the equation 2x + 3 = 7",
        "Calculate the area of a rectangle with length 10 and width 5",
        "What is the mean of the numbers 10, 20, 30, 40, 50?"
    ]
    
    for i, query in enumerate(math_queries, 1):
        print(f"\n📝 Example {i}: {query}")
        try:
            response = await system.process_query(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 40)

async def example_research_tasks():
    """Example research tasks."""
    print("\n🔍 Research Tasks Examples")
    print("=" * 40)
    
    from src.main import MultiAgentSystem
    system = MultiAgentSystem()
    
    research_queries = [
        "Research the latest developments in artificial intelligence",
        "What are the key facts about climate change?",
        "Summarize the benefits of renewable energy",
        "Find information about machine learning applications",
        "What is the current state of quantum computing?"
    ]
    
    for i, query in enumerate(research_queries, 1):
        print(f"\n📝 Example {i}: {query}")
        try:
            response = await system.process_query(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 40)

async def example_complex_tasks():
    """Example complex tasks requiring multiple agents."""
    print("\n🤖 Complex Multi-Agent Tasks Examples")
    print("=" * 40)
    
    from src.main import MultiAgentSystem
    system = MultiAgentSystem()
    
    complex_queries = [
        "Research the carbon footprint of air travel and calculate the emissions for a 1000km flight",
        "Find information about renewable energy and calculate the cost savings of solar panels",
        "Research machine learning algorithms and calculate the accuracy improvement of a new model",
        "Investigate climate change data and perform statistical analysis on temperature trends",
        "Research AI ethics and analyze the mathematical probability of bias in AI systems"
    ]
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n📝 Example {i}: {query}")
        try:
            response = await system.process_query(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 40)

async def example_agent_specific_tasks():
    """Example tasks that demonstrate specific agent capabilities."""
    print("\n🎯 Agent-Specific Capabilities Examples")
    print("=" * 40)
    
    from src.main import MultiAgentSystem
    system = MultiAgentSystem()
    
    # Test MathAgent directly
    print("\n🧮 MathAgent Direct Tests:")
    math_tasks = [
        "Calculate 15 * 23 + 45",
        "What is the area of a triangle with base 8 and height 6?",
        "Calculate the statistics for the numbers 5, 10, 15, 20, 25"
    ]
    
    for task in math_tasks:
        print(f"\n📝 Math Task: {task}")
        try:
            response = await system.process_query(task)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test ResearchAgent directly
    print("\n🔍 ResearchAgent Direct Tests:")
    research_tasks = [
        "Summarize the key points about artificial intelligence",
        "Check if the statement 'Water boils at 100 degrees Celsius' is true",
        "Analyze the knowledge structure of machine learning"
    ]
    
    for task in research_tasks:
        print(f"\n📝 Research Task: {task}")
        try:
            response = await system.process_query(task)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    """Run all examples."""
    print("🚀 Multi-Agent System Examples")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file")
        print("\n💡 To run with uv:")
        print("   uv run python examples.py")
        return
    
    try:
        # Run different types of examples
        await example_math_problems()
        await example_research_tasks()
        await example_complex_tasks()
        await example_agent_specific_tasks()
        
        print("\n🎉 All examples completed successfully!")
        print("\n💡 To run the interactive session, use:")
        print("   uv run python src/main.py")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
