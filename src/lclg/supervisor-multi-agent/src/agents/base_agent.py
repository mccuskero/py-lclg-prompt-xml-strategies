"""Base agent class for the multi-agent system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
        


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    content: str = Field(description="The message content")
    sender: str = Field(description="The agent that sent the message")
    recipient: Optional[str] = Field(default=None, description="The intended recipient")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(
        self,
        name: str,
        llm: Optional[ChatOpenAI] = None,
        temperature: float = 0.1,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        self.name = name
        self.llm = llm or ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        self.tools: List[BaseTool] = []
        self.agent_executor: Optional[AgentExecutor] = None
        self._setup_tools()
        self._setup_agent()
    
    @abstractmethod
    def _setup_tools(self) -> None:
        """Set up the tools for this agent. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent. Must be implemented by subclasses."""
        pass
    
    def _setup_agent(self) -> None:
        """Set up the agent with tools using the new create_agent API."""
        # Create a comprehensive prompt template
        prompt_template = PromptTemplate.from_template(
            """You are {agent_name}, a specialized AI agent.

{system_prompt}

You have access to the following tools: {tool_names}

When using tools:
1. Think about what you need to do
2. Use the appropriate tool with the correct input
3. Analyze the tool's output
4. Provide a clear, helpful response

Always be helpful, accurate, and provide clear explanations.

Current task: {input}"""
        )
        
        # Format the prompt with agent-specific information
        formatted_prompt = prompt_template.format(
            agent_name=self.name,
            system_prompt=self._get_system_prompt(),
            tool_names=", ".join([tool.name for tool in self.tools]),
            input="{input}"
        )
        
        # Create the agent using the new API
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            prompt=formatted_prompt
        )
    
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection. Override in subclasses."""
        return "base"
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process a message and return a response."""
        try:
            # Use the new agent API
            from langchain_core.messages import HumanMessage
            
            # Create the input for the new agent API
            inputs = {
                "messages": [HumanMessage(content=message.content)]
            }
            
            # Stream the response and collect the final result
            final_state = None
            async for chunk in self.agent_executor.astream(inputs):
                final_state = chunk
            
            # Extract the response from the final state
            if final_state and "messages" in final_state:
                # Get the last message from the agent
                messages = final_state["messages"]
                if messages:
                    last_message = messages[-1]
                    response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                else:
                    response_content = "No response generated"
            else:
                response_content = "No response generated"
            
            return AgentMessage(
                content=response_content,
                sender=self.name,
                recipient=message.sender,
                metadata={"processing_time": "calculated_if_needed"}
            )
        except Exception as e:
            return AgentMessage(
                content=f"Error processing message: {str(e)}",
                sender=self.name,
                recipient=message.sender,
                metadata={"error": True}
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a new tool to the agent."""
        self.tools.append(tool)
        # Recreate the agent with the new tool
        self._setup_agent()
