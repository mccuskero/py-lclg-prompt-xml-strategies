"""Main entry point for the multi-agent system."""

import asyncio
from .agents.multi_agent_system import MultiAgentSystem


async def main():
    """Main function to run the multi-agent system."""
    try:
        # Initialize the system (allow no API key for demo mode)
        system = MultiAgentSystem(allow_no_api_key=True)
        
        # Display system information
        info = system.get_system_info()
        print("\n📊 System Information:")
        print(f"   Total Agents: {info['total_agents']}")
        print(f"   Total Tools: {info['total_tools']}")
        
        # Run interactive session
        await system.interactive_session()
        
    except Exception as e:
        print(f"❌ Failed to initialize system: {str(e)}")
        print("\n💡 Make sure you have:")
        print("   1. Set your OPENAI_API_KEY environment variable for full functionality")
        print("   2. Or run in demo mode (limited functionality)")
        print("   3. Installed all dependencies: uv sync")


def run_example_queries():
    """Run some example queries to demonstrate the system."""
    async def examples():
        system = MultiAgentSystem(allow_no_api_key=True)
        
        example_queries = [
            "Calculate the area of a circle with radius 5",
            "Research the latest developments in artificial intelligence",
            "What is the standard deviation of the numbers 1, 2, 3, 4, 5?",
            "Find information about climate change and calculate the carbon footprint of a 1000km flight",
            "Research solar energy costs and calculate the payback period for a 5kW system",
            "Investigate renewable energy and calculate cost savings for a 10kW solar installation"
        ]
        
        print("\n🧪 Running Example Queries:")
        print("="*50)
        
        for i, query in enumerate(example_queries, 1):
            print(f"\n📝 Example {i}: {query}")
            try:
                response = await system.process_query(query)
                if response:
                    print(f"🤖 Response: {response[:200]}..." if len(response) > 200 else f"🤖 Response: {response}")
                else:
                    print("🤖 Response: No response generated")
            except Exception as e:
                print(f"❌ Error processing query: {str(e)}")
            print("-" * 50)
    
    return examples


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "examples":
        # Run example queries
        asyncio.run(run_example_queries()())
    else:
        # Run interactive session
        asyncio.run(main())