"""SupervisorAgent for orchestrating multi-agent tasks."""

from typing import Any, Dict, List, Optional, Union
from langchain.tools import BaseTool, tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from .base_agent import BaseAgent, AgentMessage
from .math_agent import MathAgent
from .research_agent import ResearchAgent


class HandoffInput(BaseModel):
    """Input for handoff tool."""
    destination: str = Field(description="The agent to handoff to (math_agent or research_agent)")
    payload: str = Field(description="The task or message to send to the destination agent")


class SupervisorAgent(BaseAgent):
    """Supervisor agent that orchestrates tasks between specialized agents."""
    
    def __init__(
        self,
        math_agent: Optional[MathAgent] = None,
        research_agent: Optional[ResearchAgent] = None,
        llm: Optional[ChatOpenAI] = None,
        temperature: float = 0.1,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        super().__init__(
            name="SupervisorAgent",
            llm=llm,
            temperature=temperature,
            model_name=model_name,
            api_key=api_key
        )
        
        # Initialize specialized agents
        self.math_agent = math_agent or MathAgent(llm=llm, temperature=temperature, model_name=model_name, api_key=api_key)
        self.research_agent = research_agent or ResearchAgent(llm=llm, temperature=temperature, model_name=model_name, api_key=api_key)
        
        # Agent registry for easy lookup
        self.agent_registry = {
            "math_agent": self.math_agent,
            "research_agent": self.research_agent
        }
    
    def _setup_tools(self) -> None:
        """Set up supervisor tools including handoff tools."""
        self.tools = [
            self._create_handoff_tool(),
            self._create_task_analyzer_tool(),
            self._create_coordination_tool(),
            self._create_result_synthesizer_tool()
        ]
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor agent."""
        return """You are a supervisor agent responsible for orchestrating a multi-agent system. You coordinate between:

- MathAgent: Handles mathematical problems, calculations, and numerical analysis
- ResearchAgent: Handles information gathering, fact-checking, and research tasks

Your responsibilities:
1. Analyze incoming tasks to determine which specialized agent should handle them
2. Delegate tasks to appropriate agents using handoff tools
3. Coordinate multi-step tasks that require multiple agents
4. Synthesize results from multiple agents
5. Provide high-level oversight and quality control

Available agents:
- math_agent: For mathematical calculations, equations, statistics, geometry
- research_agent: For web search, fact-checking, summarization, knowledge analysis

When delegating tasks:
- Use the handoff tool with appropriate destination and payload
- Be specific about what you need from each agent
- Consider if a task requires multiple agents working together
- Always provide clear instructions in the payload

You should be the primary interface for complex tasks that require coordination between agents."""
    
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "supervisor"
    
    def _create_handoff_tool(self) -> BaseTool:
        """Create a handoff tool for delegating tasks to specialized agents."""
        
        @tool("handoff")
        def handoff_task(destination: str, payload: str) -> str:
            """Handoff a task to a specialized agent."""
            try:
                if destination not in self.agent_registry:
                    return f"Error: Unknown destination '{destination}'. Available agents: {list(self.agent_registry.keys())}"
                
                target_agent = self.agent_registry[destination]
                
                # For now, just return a simple response since we can't do async here
                return f"Handoff to {destination} would process: {payload}"
                
            except Exception as e:
                return f"Error during handoff to {destination}: {str(e)}"
        
        return handoff_task
    
    def _create_task_analyzer_tool(self) -> BaseTool:
        """Create a tool for analyzing and categorizing tasks."""
        
        @tool("task_analyzer")
        def analyze_task(task: str) -> str:
            """Analyze a task to determine the best agent(s) to handle it."""
            task_lower = task.lower()
            
            # Mathematical keywords
            math_keywords = [
                'calculate', 'solve', 'equation', 'formula', 'math', 'mathematical',
                'statistics', 'probability', 'geometry', 'algebra', 'calculus',
                'number', 'numeric', 'computation', 'arithmetic'
            ]
            
            # Research keywords
            research_keywords = [
                'research', 'find', 'search', 'information', 'fact', 'verify',
                'summarize', 'analyze', 'investigate', 'look up', 'gather',
                'knowledge', 'data', 'source', 'reference'
            ]
            
            math_score = sum(1 for keyword in math_keywords if keyword in task_lower)
            research_score = sum(1 for keyword in research_keywords if keyword in task_lower)
            
            recommendations = []
            
            if math_score > 0:
                recommendations.append(f"MathAgent (score: {math_score}) - for mathematical calculations")
            
            if research_score > 0:
                recommendations.append(f"ResearchAgent (score: {research_score}) - for information gathering")
            
            if math_score > 0 and research_score > 0:
                recommendations.append("Both agents - this task may require mathematical analysis and research")
            
            if not recommendations:
                recommendations.append("SupervisorAgent - general task that doesn't require specialized agents")
            
            return f"""Task Analysis for: "{task}"

Recommended Agent(s):
{chr(10).join(f"- {rec}" for rec in recommendations)}

Task Complexity: {'High' if math_score + research_score > 3 else 'Medium' if math_score + research_score > 0 else 'Low'}
Estimated Processing Time: {'5-10 minutes' if math_score + research_score > 3 else '2-5 minutes' if math_score + research_score > 0 else '1-2 minutes'}"""
        
        return analyze_task
    
    def _create_coordination_tool(self) -> BaseTool:
        """Create a tool for coordinating multi-agent workflows."""
        
        @tool("coordination")
        def coordinate_workflow(workflow: str) -> str:
            """Coordinate a multi-step workflow across agents."""
            workflow_lower = workflow.lower()
            
            # Identify workflow steps
            steps = []
            
            if 'research' in workflow_lower or 'find' in workflow_lower:
                steps.append("1. ResearchAgent: Gather relevant information")
            
            if 'calculate' in workflow_lower or 'analyze' in workflow_lower:
                steps.append("2. MathAgent: Perform calculations and analysis")
            
            if 'synthesize' in workflow_lower or 'summarize' in workflow_lower:
                steps.append("3. SupervisorAgent: Synthesize results from all agents")
            
            if not steps:
                steps = [
                    "1. Analyze task requirements",
                    "2. Delegate to appropriate agents",
                    "3. Collect and synthesize results"
                ]
            
            return f"""Multi-Agent Workflow for: "{workflow}"

Proposed Steps:
{chr(10).join(steps)}

Coordination Strategy:
- Sequential execution for dependent tasks
- Parallel execution for independent tasks
- Result aggregation and synthesis
- Quality control and validation

Estimated Total Time: {len(steps) * 2}-{len(steps) * 5} minutes"""
        
        return coordinate_workflow
    
    def _create_result_synthesizer_tool(self) -> BaseTool:
        """Create a tool for synthesizing results from multiple agents."""
        
        @tool("result_synthesizer")
        def synthesize_results(results: str) -> str:
            """Synthesize results from multiple agents into a coherent response."""
            # This is a simplified synthesizer
            # In production, you would use more sophisticated NLP techniques
            
            lines = results.split('\n')
            synthesized = []
            
            # Extract key information
            key_findings = []
            calculations = []
            recommendations = []
            
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in ['result', 'answer', 'solution']):
                    key_findings.append(line.strip())
                elif any(word in line_lower for word in ['calculate', 'compute', 'formula']):
                    calculations.append(line.strip())
                elif any(word in line_lower for word in ['recommend', 'suggest', 'advise']):
                    recommendations.append(line.strip())
            
            synthesized.append("=== SYNTHESIZED RESULTS ===")
            synthesized.append("")
            
            if key_findings:
                synthesized.append("Key Findings:")
                for finding in key_findings:
                    synthesized.append(f"• {finding}")
                synthesized.append("")
            
            if calculations:
                synthesized.append("Calculations:")
                for calc in calculations:
                    synthesized.append(f"• {calc}")
                synthesized.append("")
            
            if recommendations:
                synthesized.append("Recommendations:")
                for rec in recommendations:
                    synthesized.append(f"• {rec}")
                synthesized.append("")
            
            synthesized.append("=== END SYNTHESIS ===")
            
            return '\n'.join(synthesized)
        
        return synthesize_results
    
    async def process_complex_task(self, task: str) -> str:
        """Process a complex task that may require multiple agents."""
        try:
            # First, analyze the task
            analysis = self.tools[1].func(task)  # task_analyzer
            
            # Determine if we need multiple agents
            if "Both agents" in analysis or "math_agent" in analysis and "research_agent" in analysis:
                # Multi-agent workflow
                workflow = self.tools[2].func(task)  # coordination
                
                # Execute research first (if needed)
                research_result = ""
                if "research" in task.lower() or "find" in task.lower():
                    research_message = AgentMessage(
                        content=f"Research task: {task}",
                        sender=self.name,
                        recipient=self.research_agent.name
                    )
                    research_response = await self.research_agent.process_message(research_message)
                    research_result = research_response.content
                
                # Execute math tasks (if needed)
                math_result = ""
                if "calculate" in task.lower() or "math" in task.lower():
                    math_message = AgentMessage(
                        content=f"Mathematical task: {task}",
                        sender=self.name,
                        recipient=self.math_agent.name
                    )
                    math_response = await self.math_agent.process_message(math_message)
                    math_result = math_response.content
                
                # Synthesize results
                combined_results = f"Research Results:\n{research_result}\n\nMath Results:\n{math_result}"
                final_result = self.tools[3].func(combined_results)  # result_synthesizer
                
                return f"Complex Task Analysis:\n{analysis}\n\nWorkflow:\n{workflow}\n\nFinal Results:\n{final_result}"
            
            else:
                # Single agent task - use handoff
                if "math_agent" in analysis:
                    destination = "math_agent"
                elif "research_agent" in analysis:
                    destination = "research_agent"
                else:
                    # Handle directly
                    return f"Task Analysis:\n{analysis}\n\nHandling directly as supervisor task."
                
                handoff_result = await self.tools[0].func(destination, task)  # handoff
                return f"Task Analysis:\n{analysis}\n\nHandoff Result:\n{handoff_result}"
                
        except Exception as e:
            return f"Error processing complex task: {str(e)}"
