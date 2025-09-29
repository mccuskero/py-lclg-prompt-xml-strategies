"""Multi-agent system orchestrator."""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

from . import SupervisorAgent, MathAgent, ResearchAgent
from .base_agent import AgentMessage
from ..prompts import get_complex_task_prompt, get_task_analysis_prompt


class MultiAgentSystem:
    """Main orchestrator for the multi-agent system."""
    
    def __init__(self, api_key: Optional[str] = None, allow_no_api_key: bool = False):
        """Initialize the multi-agent system."""
        # Load environment variables
        load_dotenv()
        
        # Set up API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key and not allow_no_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize agents
        self.supervisor = None
        self.math_agent = None
        self.research_agent = None
        
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents in the system."""
        print("Initializing multi-agent system...")
        
        try:
            # Initialize specialized agents
            self.math_agent = MathAgent(api_key=self.api_key)
            self.research_agent = ResearchAgent(api_key=self.api_key)
            
            # Initialize supervisor with references to specialized agents
            self.supervisor = SupervisorAgent(
                math_agent=self.math_agent,
                research_agent=self.research_agent,
                api_key=self.api_key
            )
            
            print("✅ Multi-agent system initialized successfully!")
            print(f"   - SupervisorAgent: {self.supervisor.name}")
            print(f"   - MathAgent: {self.math_agent.name}")
            print(f"   - ResearchAgent: {self.research_agent.name}")
            
        except Exception as e:
            print(f"⚠️  Warning: Agent initialization failed: {str(e)}")
            print("   The system will run in limited mode (tools only)")
            # Initialize with demo keys for tool testing
            self.math_agent = MathAgent(api_key="demo-key")
            self.research_agent = ResearchAgent(api_key="demo-key")
            self.supervisor = SupervisorAgent(
                math_agent=self.math_agent,
                research_agent=self.research_agent,
                api_key="demo-key"
            )
            print("✅ Multi-agent system initialized in demo mode!")
    
    async def process_query(self, query: str) -> str:
        """Process a user query through the multi-agent system."""
        print(f"\n🔍 Processing query: {query}")
        
        try:
            # First, try to analyze the task to determine which agent should handle it
            task_analysis = self.supervisor.tools[1].invoke(query)  # task_analyzer
            print(f"📊 Task Analysis: {task_analysis}")
            
            # Determine which agent to use based on the analysis
            query_lower = query.lower()
            
            # Check if it's a math task
            math_keywords = ['calculate', 'solve', 'equation', 'formula', 'math', 'statistics', 'geometry', 'number']
            is_math_task = any(keyword in query_lower for keyword in math_keywords)
            
            # Check if it's a research task
            research_keywords = ['research', 'find', 'search', 'information', 'fact', 'verify', 'summarize', 'analyze', 'investigate']
            is_research_task = any(keyword in query_lower for keyword in research_keywords)
            
            if is_math_task and not is_research_task:
                # Use MathAgent directly
                print("🧮 Using MathAgent for mathematical task")
                
                # Check for specific math operations
                if "circle" in query_lower and "radius" in query_lower:
                    # Extract radius from query
                    import re
                    radius_match = re.search(r'radius\s+(\d+(?:\.\d+)?)', query_lower)
                    if radius_match:
                        radius = radius_match.group(1)
                        result = self.math_agent.tools[3].invoke(f"circle radius {radius}")
                        return f"MathAgent Geometry Result:\n{result}"
                
                elif "statistics" in query_lower or "standard deviation" in query_lower or "mean" in query_lower or "median" in query_lower:
                    # Extract numbers from query
                    import re
                    numbers = re.findall(r'\d+(?:\.\d+)?', query)
                    if numbers:
                        data = ', '.join(numbers)
                        result = self.math_agent.tools[2].invoke(data)  # statistics
                        return f"MathAgent Statistics Result:\n{result}"
                
                elif "calculate" in query_lower or "compute" in query_lower:
                    # Try to extract mathematical expression
                    import re
                    # Look for expressions like "15 * 23 + 45"
                    expr_match = re.search(r'(\d+(?:\.\d+)?\s*[\+\-\*\/\^]\s*\d+(?:\.\d+)?(?:\s*[\+\-\*\/\^]\s*\d+(?:\.\d+)?)*)', query)
                    if expr_match:
                        expression = expr_match.group(1).replace('^', '**')
                        result = self.math_agent.tools[0].invoke(expression)
                        return f"MathAgent Calculator Result:\n{result}"
                
                elif "solve" in query_lower and "equation" in query_lower:
                    result = self.math_agent.tools[1].invoke(query)  # equation solver
                    return f"MathAgent Equation Solver Result:\n{result}"
                
                else:
                    return f"MathAgent: I can help with mathematical calculations. Please be more specific about what you'd like me to calculate."
            
            elif is_research_task and not is_math_task:
                # Use ResearchAgent directly
                print("🔍 Using ResearchAgent for research task")
                if "search" in query_lower or "find" in query_lower or "research" in query_lower:
                    # Extract search terms
                    search_terms = query.replace("research", "").replace("find", "").replace("search", "").strip()
                    result = self.research_agent.tools[0].invoke(search_terms)  # web_search
                    return f"ResearchAgent Search Result:\n{result}"
                elif "fact" in query_lower or "check" in query_lower or "verify" in query_lower:
                    result = self.research_agent.tools[1].invoke(query)  # fact_checker
                    return f"ResearchAgent Fact Check Result:\n{result}"
                else:
                    return f"ResearchAgent: I can help with research and information gathering. Please specify what you'd like me to research."
            
            elif is_math_task and is_research_task:
                # Complex task requiring both agents
                print("🤖 Using both agents for complex task")
                return await self._handle_complex_task(query, task_analysis)
            
            else:
                # General task - use supervisor tools
                print("👑 Using SupervisorAgent for general task")
                return f"SupervisorAgent Task Analysis:\n{task_analysis}\n\nI can help coordinate between specialized agents for complex tasks."
            
        except Exception as e:
            return f"Error processing query: {str(e)}\n\nPlease try a more specific mathematical or research question."
    
    async def _handle_complex_task(self, query: str, task_analysis: str) -> str:
        """Handle complex tasks that require both research and mathematical analysis."""
        print("🔄 Coordinating between ResearchAgent and MathAgent...")
        
        try:
            # Step 1: Research phase
            print("📚 Phase 1: Research")
            research_results = []
            
            # Extract research topics from the query
            query_lower = query.lower()
            research_topics = []
            
            if "climate change" in query_lower:
                research_topics.append("climate change")
            if "carbon footprint" in query_lower:
                research_topics.append("carbon footprint")
            if "emissions" in query_lower:
                research_topics.append("carbon emissions")
            if "renewable energy" in query_lower:
                research_topics.append("renewable energy")
            if "solar" in query_lower:
                research_topics.append("solar energy")
            if "wind" in query_lower:
                research_topics.append("wind energy")
            
            # If no specific topics found, use general research
            if not research_topics:
                research_topics = ["environmental impact", "sustainability"]
            
            # Conduct research for each topic
            for topic in research_topics[:2]:  # Limit to 2 topics to avoid too much output
                print(f"   Researching: {topic}")
                research_result = self.research_agent.tools[0].invoke(topic)  # web_search
                research_results.append(f"Research on {topic}:\n{research_result}")
            
            # Step 2: Mathematical analysis phase
            print("🧮 Phase 2: Mathematical Analysis")
            math_results = []
            
            # Extract mathematical components
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', query)
            
            if "carbon footprint" in query_lower or "emissions" in query_lower:
                # Calculate carbon footprint
                if numbers:
                    # Use the first number as distance or amount
                    amount = float(numbers[0])
                    
                    # Example calculations for carbon footprint
                    if "flight" in query_lower or "km" in query_lower:
                        # Flight emissions: ~0.255 kg CO2 per km
                        co2_per_km = 0.255
                        total_emissions = amount * co2_per_km
                        math_results.append(f"Flight Carbon Footprint Calculation:\n- Distance: {amount} km\n- CO2 per km: {co2_per_km} kg\n- Total emissions: {total_emissions:.2f} kg CO2")
                    
                    elif "car" in query_lower or "driving" in query_lower:
                        # Car emissions: ~0.192 kg CO2 per km
                        co2_per_km = 0.192
                        total_emissions = amount * co2_per_km
                        math_results.append(f"Car Carbon Footprint Calculation:\n- Distance: {amount} km\n- CO2 per km: {co2_per_km} kg\n- Total emissions: {total_emissions:.2f} kg CO2")
                    
                    else:
                        # General carbon calculation
                        co2_per_unit = 0.5  # Example rate
                        total_emissions = amount * co2_per_unit
                        math_results.append(f"Carbon Footprint Calculation:\n- Amount: {amount} units\n- CO2 per unit: {co2_per_unit} kg\n- Total emissions: {total_emissions:.2f} kg CO2")
                else:
                    math_results.append("No specific numbers found for calculation. Please provide quantities for accurate carbon footprint calculation.")
            
            elif "cost" in query_lower or "savings" in query_lower:
                # Calculate cost savings
                if numbers:
                    amount = float(numbers[0])
                    # Example: Solar panel cost savings
                    if "solar" in query_lower:
                        cost_per_kw = 3000  # $3000 per kW
                        annual_savings = amount * 0.12  # $0.12 per kWh
                        payback_years = (amount * cost_per_kw) / (annual_savings * 365)
                        math_results.append(f"Solar Panel Cost Analysis:\n- System size: {amount} kW\n- Cost: ${amount * cost_per_kw:,.0f}\n- Annual savings: ${annual_savings * 365:,.0f}\n- Payback period: {payback_years:.1f} years")
                    else:
                        math_results.append(f"Cost analysis requires more specific parameters. Found amount: {amount}")
                else:
                    math_results.append("No specific numbers found for cost calculation.")
            
            else:
                # General mathematical analysis
                if numbers:
                    data = ', '.join(numbers)
                    stats_result = self.math_agent.tools[2].invoke(data)  # statistics
                    math_results.append(f"Statistical Analysis:\n{stats_result}")
                else:
                    math_results.append("No numerical data found for mathematical analysis.")
            
            # Step 3: Synthesis phase
            print("🔗 Phase 3: Synthesis")
            synthesis_prompt = get_complex_task_prompt(
                task_description=query,
                research_topics=research_topics,
                math_components=[f"Numbers found: {numbers}" if numbers else "No specific numbers"],
                current_phase="Synthesis"
            )
            synthesis_result = self.supervisor.tools[3].invoke(synthesis_prompt)
            
            # Step 4: Final coordination
            print("✅ Phase 4: Final Coordination")
            coordination_plan = self.supervisor.tools[2].invoke(query)  # coordination
            
            # Combine all results
            final_response = f"""🤖 COMPLEX TASK COORDINATION RESULTS

📊 Task Analysis:
{task_analysis}

🔄 Coordination Plan:
{coordination_plan}

📚 Research Results:
{chr(10).join(research_results)}

🧮 Mathematical Analysis:
{chr(10).join(math_results)}

🔗 Synthesized Results:
{synthesis_result}

✅ Multi-Agent Coordination Complete!"""
            
            return final_response
            
        except Exception as e:
            return f"Error in complex task coordination: {str(e)}\n\nFalling back to individual agent responses."
    
    async def interactive_session(self):
        """Run an interactive session with the multi-agent system."""
        print("\n" + "="*60)
        print("🤖 Multi-Agent System Interactive Session")
        print("="*60)
        print("Available agents:")
        print("  - MathAgent: Mathematical problems, calculations, statistics")
        print("  - ResearchAgent: Information gathering, fact-checking, research")
        print("  - SupervisorAgent: Orchestrates complex tasks")
        print("\nType 'quit' or 'exit' to end the session")
        print("="*60)
        
        while True:
            try:
                query = input("\n💬 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not query:
                    print("Please enter a query.")
                    continue
                
                # Process the query
                response = await self.process_query(query)
                print(f"\n🤖 Response:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    def get_system_info(self) -> dict:
        """Get information about the system."""
        return {
            "agents": {
                "supervisor": {
                    "name": self.supervisor.name,
                    "tools": self.supervisor.get_available_tools()
                },
                "math_agent": {
                    "name": self.math_agent.name,
                    "tools": self.math_agent.get_available_tools()
                },
                "research_agent": {
                    "name": self.research_agent.name,
                    "tools": self.research_agent.get_available_tools()
                }
            },
            "total_agents": 3,
            "total_tools": len(self.supervisor.get_available_tools()) + 
                          len(self.math_agent.get_available_tools()) + 
                          len(self.research_agent.get_available_tools())
        }
