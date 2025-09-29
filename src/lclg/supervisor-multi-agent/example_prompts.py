"""Example prompts and demonstrations for the multi-agent system."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_math_agent_prompts():
    """Demonstrate MathAgent with various mathematical prompts."""
    print("🧮 MathAgent Example Prompts")
    print("=" * 50)
    
    from src.agents.math_agent import MathAgent
    
    # Create MathAgent
    math_agent = MathAgent(api_key="demo-key")
    
    # Calculator Operations
    print("\n📊 Calculator Operations:")
    calculator_prompts = [
        "Calculate 15 * 23 + 45",
        "What is 2^8 + 3^4?",
        "Compute the square root of 144",
        "Calculate (10 + 5) * 3 / 2"
    ]
    
    for prompt in calculator_prompts:
        print(f"\nPrompt: {prompt}")
        result = math_agent.tools[0].invoke(prompt)
        print(f"Result: {result}")
    
    # Statistics & Data Analysis
    print("\n📈 Statistics & Data Analysis:")
    stats_prompts = [
        "1, 2, 3, 4, 5",
        "10, 20, 30, 40, 50",
        "5, 10, 15, 20, 25"
    ]
    
    for prompt in stats_prompts:
        print(f"\nDataset: {prompt}")
        result = math_agent.tools[2].invoke(prompt)
        print(f"Statistics:\n{result}")
    
    # Geometry Calculations
    print("\n📐 Geometry Calculations:")
    geometry_prompts = [
        "circle radius 5",
        "rectangle length 10 width 5",
        "triangle base 8 height 6"
    ]
    
    for prompt in geometry_prompts:
        print(f"\nShape: {prompt}")
        result = math_agent.tools[3].invoke(prompt)
        print(f"Calculation:\n{result}")

async def demo_research_agent_prompts():
    """Demonstrate ResearchAgent with various research prompts."""
    print("\n🔍 ResearchAgent Example Prompts")
    print("=" * 50)
    
    from src.agents.research_agent import ResearchAgent
    
    # Create ResearchAgent
    research_agent = ResearchAgent(api_key="demo-key")
    
    # Web Search & Information Gathering
    print("\n🌐 Web Search & Information Gathering:")
    search_prompts = [
        "artificial intelligence",
        "renewable energy technologies",
        "machine learning trends",
        "climate change solutions"
    ]
    
    for prompt in search_prompts:
        print(f"\nSearch Query: {prompt}")
        result = research_agent.tools[0].invoke(prompt)
        print(f"Search Results:\n{result[:200]}...")
    
    # Fact Checking & Verification
    print("\n✅ Fact Checking & Verification:")
    fact_check_prompts = [
        "Water boils at 100 degrees Celsius",
        "Earth is round",
        "Vaccines cause autism",
        "Climate change is caused by human activities"
    ]
    
    for prompt in fact_check_prompts:
        print(f"\nStatement: {prompt}")
        result = research_agent.tools[1].invoke(prompt)
        print(f"Verification: {result}")
    
    # Text Summarization
    print("\n📝 Text Summarization:")
    long_text = """
    Artificial Intelligence (AI) is a rapidly evolving field that combines computer science, 
    mathematics, and cognitive science to create systems that can perform tasks typically 
    requiring human intelligence. Machine learning is a subset of AI that focuses on 
    algorithms that can learn from data without being explicitly programmed. Deep learning 
    uses neural networks with multiple layers to process complex patterns in data. 
    AI applications include natural language processing, computer vision, robotics, and 
    autonomous systems. The field is advancing rapidly with new breakthroughs in areas 
    like large language models, computer vision, and reinforcement learning.
    """
    
    print(f"\nOriginal Text ({len(long_text)} characters):")
    print(f"{long_text[:100]}...")
    
    result = research_agent.tools[2].invoke(long_text)
    print(f"\nSummary:\n{result}")
    
    # Knowledge Analysis
    print("\n🧠 Knowledge Analysis:")
    knowledge_prompts = [
        "artificial intelligence",
        "renewable energy",
        "machine learning",
        "data science"
    ]
    
    for prompt in knowledge_prompts:
        print(f"\nTopic: {prompt}")
        result = research_agent.tools[3].invoke(prompt)
        print(f"Analysis:\n{result}")

async def demo_supervisor_agent_prompts():
    """Demonstrate SupervisorAgent with complex multi-agent prompts."""
    print("\n👑 SupervisorAgent Example Prompts")
    print("=" * 50)
    
    from src.agents.supervisor_agent import SupervisorAgent
    
    # Create SupervisorAgent
    supervisor = SupervisorAgent(api_key="demo-key")
    
    # Task Analysis Examples
    print("\n🎯 Task Analysis Examples:")
    task_analysis_prompts = [
        "Calculate the area of a circle with radius 5",
        "Research the latest developments in artificial intelligence",
        "Find information about climate change and calculate carbon footprint",
        "Research machine learning algorithms and analyze their complexity",
        "Calculate statistics for climate data and summarize findings"
    ]
    
    for prompt in task_analysis_prompts:
        print(f"\nTask: {prompt}")
        result = supervisor.tools[1].invoke(prompt)
        print(f"Analysis:\n{result}")
    
    # Coordination Examples
    print("\n🔄 Coordination Examples:")
    coordination_prompts = [
        "Research renewable energy and calculate cost savings",
        "Find climate data and perform statistical analysis",
        "Research AI ethics and analyze bias probability",
        "Investigate solar panel efficiency and calculate payback period"
    ]
    
    for prompt in coordination_prompts:
        print(f"\nWorkflow: {prompt}")
        result = supervisor.tools[2].invoke(prompt)
        print(f"Coordination Plan:\n{result}")
    
    # Result Synthesis Examples
    print("\n🔗 Result Synthesis Examples:")
    synthesis_examples = [
        """Research Results: Solar energy costs have decreased by 80% over the past decade.
Math Results: Cost savings calculation shows $2,500 annual savings for a 5kW system.
Recommendations: Consider installing solar panels for maximum cost benefit.""",
        
        """Research Results: Machine learning algorithms show varying complexity levels.
Math Results: Time complexity analysis shows O(n²) for some algorithms.
Recommendations: Choose algorithms based on dataset size and complexity requirements."""
    ]
    
    for i, example in enumerate(synthesis_examples, 1):
        print(f"\nSynthesis Example {i}:")
        result = supervisor.tools[3].invoke(example)
        print(f"Synthesized Results:\n{result}")

async def demo_complex_multi_agent_prompts():
    """Demonstrate complex prompts that require multiple agents."""
    print("\n🤖 Complex Multi-Agent Prompts")
    print("=" * 50)
    
    print("\nThese are examples of prompts that would require coordination between multiple agents:")
    
    complex_prompts = [
        {
            "prompt": "Research the carbon footprint of air travel and calculate emissions for a 1000km flight",
            "agents": ["ResearchAgent", "MathAgent"],
            "description": "Research flight emissions data, then calculate specific emissions for 1000km"
        },
        {
            "prompt": "Find information about solar panel efficiency and calculate cost savings",
            "agents": ["ResearchAgent", "MathAgent"],
            "description": "Research solar panel specs, then calculate financial savings"
        },
        {
            "prompt": "Research renewable energy costs and calculate payback period for a 5kW system",
            "agents": ["ResearchAgent", "MathAgent"],
            "description": "Research current costs, then calculate return on investment"
        },
        {
            "prompt": "Research machine learning algorithms and analyze their mathematical complexity",
            "agents": ["ResearchAgent", "MathAgent"],
            "description": "Research algorithms, then perform complexity analysis"
        },
        {
            "prompt": "Find information about climate data and perform statistical analysis",
            "agents": ["ResearchAgent", "MathAgent"],
            "description": "Research climate data, then perform statistical calculations"
        }
    ]
    
    for i, example in enumerate(complex_prompts, 1):
        print(f"\n{i}. Complex Prompt:")
        print(f"   Prompt: {example['prompt']}")
        print(f"   Required Agents: {', '.join(example['agents'])}")
        print(f"   Description: {example['description']}")

async def main():
    """Run all example prompt demonstrations."""
    print("🚀 Multi-Agent System Example Prompts")
    print("=" * 60)
    print("This demo shows example prompts for each agent type.")
    print("=" * 60)
    
    try:
        await demo_math_agent_prompts()
        await demo_research_agent_prompts()
        await demo_supervisor_agent_prompts()
        await demo_complex_multi_agent_prompts()
        
        print("\n" + "=" * 60)
        print("🎉 Example prompts demonstration completed!")
        print("\n💡 To test these prompts with full API integration:")
        print("   1. Set your OPENAI_API_KEY in .env file")
        print("   2. Run: uv run python src/main.py")
        print("   3. Try these prompts in the interactive session")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    asyncio.run(main())
