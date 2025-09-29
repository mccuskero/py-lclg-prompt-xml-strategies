"""Enhanced base agent class for the car creation multi-agent system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field
import json
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.base import BaseLanguageModel

# Add prompts module to path
sys.path.append(str(Path(__file__).parent.parent))
from prompts.prompts import get_agent_prompt
from prompts.prompts_from_json_schema import get_schema_agent_prompt
from llm.ollama_llm import OllamaLLM


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    content: str = Field(description="The message content")
    sender: str = Field(description="The agent that sent the message")
    recipient: Optional[str] = Field(default=None, description="The intended recipient")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class HandoffPayload(BaseModel):
    """Payload structure for agent handoffs."""
    from_agent: str = Field(description="Source agent name")
    to_agent: str = Field(description="Target agent name")
    data: Dict[str, Any] = Field(description="Data being passed")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints or requirements")
    context: str = Field(default="", description="Additional context information")


class BaseAgent(ABC):
    """Enhanced base class for all agents in the car creation multi-agent system."""

    def __init__(
        self,
        name: str,
        llm: Optional[BaseLanguageModel] = None,
        temperature: float = 0.1,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        use_json_subtypes_in_prompts_creation: bool = False
    ):
        self.name = name
        self.llm = llm or OllamaLLM(
            model=model_name,
            temperature=temperature,
            base_url=base_url
        )
        self.use_json_subtypes_in_prompts_creation = use_json_subtypes_in_prompts_creation
        self.tools: List[BaseTool] = []
        self.agent_executor = None
        self.handoff_payloads: List[HandoffPayload] = []
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

    @abstractmethod
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection. Must be implemented by subclasses."""
        pass

    def _setup_agent(self) -> None:
        """Set up the agent with tools using create_agent API."""
        # Get the appropriate prompt for this agent type
        if self.use_json_subtypes_in_prompts_creation:
            # Use schema-driven prompts
            formatted_prompt = get_schema_agent_prompt(
                agent_type=self._get_agent_type(),
                agent_name=self.name,
                system_prompt=self._get_system_prompt(),
                tool_names=", ".join([tool.name for tool in self.tools]) if self.tools else "None"
            )
        else:
            # Use original markdown-based prompts
            formatted_prompt = get_agent_prompt(
                agent_type=self._get_agent_type(),
                agent_name=self.name,
                system_prompt=self._get_system_prompt(),
                tool_names=", ".join([tool.name for tool in self.tools]) if self.tools else "None"
            )

        # Create the agent using LangChain v1.0.0a9 API
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            prompt=formatted_prompt
        )

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process a message and return a response."""
        try:
            from langchain_core.messages import HumanMessage

            # Create the input for the agent
            inputs = {
                "messages": [HumanMessage(content=message.content)]
            }

            # Stream the response and collect the final result
            final_state = None
            async for chunk in self.agent_executor.astream(inputs):
                final_state = chunk

            # Extract the response from the final state
            response_content = self._extract_response_content(final_state)

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
                metadata={"error": True, "error_type": type(e).__name__}
            )

    def _extract_response_content(self, final_state: Any) -> str:
        """Extract response content from the final agent state."""
        if final_state and "messages" in final_state:
            messages = final_state["messages"]
            if messages:
                last_message = messages[-1]
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
        return "No response generated"

    def process_handoff(self, payload: HandoffPayload) -> Dict[str, Any]:
        """Process a handoff payload from another agent."""
        self.handoff_payloads.append(payload)

        # Extract relevant data for this agent's processing
        handoff_data = {
            "source": payload.from_agent,
            "data": payload.data,
            "constraints": payload.constraints,
            "context": payload.context
        }

        return self._process_handoff_data(handoff_data)

    @abstractmethod
    def _process_handoff_data(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handoff data specific to this agent type."""
        pass

    def create_component_json(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON component data for this agent's specialization."""
        try:
            print(f"🤖 DEBUG: {self.name} creating component with requirements: {requirements}")

            # Use the agent to process the requirements
            message = AgentMessage(
                content=self._build_component_request(requirements),
                sender="system",
                recipient=self.name
            )

            print(f"🤖 DEBUG: {self.name} sending request to LLM: {message.content[:100]}...")

            # For synchronous processing, we'll use the LLM directly
            # ChatOllama uses invoke() instead of _call()
            from langchain_core.messages import HumanMessage

            # Configure generation parameters to avoid truncation
            config = {
                "max_tokens": 1000,  # Increase max_tokens to allow longer responses
                "temperature": 0.1,  # Lower temperature for more consistent JSON
            }

            response_message = self.llm.invoke(
                [HumanMessage(content=message.content)],
                config=config
            )

            # Extract content from the response message
            response = response_message.content if hasattr(response_message, 'content') else str(response_message)

            print(f"🤖 DEBUG: {self.name} received LLM response: {response[:100]}...")

            # Extract JSON from the response
            component_data = self._extract_json_from_response(response)

            print(f"🤖 DEBUG: {self.name} extracted component data: {type(component_data)}")

            # Validate against schema requirements
            validated_data = self._validate_component_data(component_data)

            print(f"✅ DEBUG: {self.name} component creation successful")
            return validated_data

        except Exception as e:
            print(f"❌ DEBUG: {self.name} component creation failed: {str(e)}")
            return {
                "error": f"Failed to create component: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    @abstractmethod
    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build a component creation request prompt."""
        pass

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON data from agent response."""
        try:
            print(f"🔍 DEBUG: {self.name} extracting JSON from response (length: {len(response)})")
            print(f"🔍 DEBUG: {self.name} response preview: {response[:200]}...")

            # First, try to parse the entire response as JSON
            try:
                result = json.loads(response.strip())
                print(f"✅ DEBUG: {self.name} successfully parsed entire response as JSON")
                return result
            except json.JSONDecodeError:
                print(f"🔍 DEBUG: {self.name} entire response is not valid JSON, trying other methods...")

            # Look for JSON blocks marked with ```json
            import re
            json_block_pattern = r'```json\s*(\{.*?\})\s*```'
            json_match = re.search(json_block_pattern, response, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                print(f"🔍 DEBUG: {self.name} found JSON block: {json_text[:100]}...")
                try:
                    result = json.loads(json_text)
                    print(f"✅ DEBUG: {self.name} successfully parsed JSON block")
                    return result
                except json.JSONDecodeError:
                    print(f"🔍 DEBUG: {self.name} JSON block is not valid, continuing...")

            # Look for any JSON object in the response using regex (simplified pattern for incomplete JSON)
            json_pattern = r'\{.*'
            json_matches = re.findall(json_pattern, response, re.DOTALL)

            for i, match in enumerate(json_matches):
                try:
                    # Try to balance braces properly
                    balanced_json = self._balance_json_braces(match.strip())
                    print(f"🔍 DEBUG: {self.name} balanced JSON attempt {i+1}: {balanced_json[:100]}...")
                    result = json.loads(balanced_json)
                    print(f"✅ DEBUG: {self.name} successfully parsed JSON object from regex match {i+1}")
                    return result
                except json.JSONDecodeError as e:
                    print(f"🔍 DEBUG: {self.name} regex match {i+1} is not valid JSON ({str(e)}), continuing...")
                    continue

            # Look for JSON blocks in the response line by line
            lines = response.split('\n')
            json_lines = []
            in_json = False
            brace_count = 0

            for line in lines:
                line = line.strip()
                if line.startswith('{') or in_json:
                    in_json = True
                    json_lines.append(line)
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0 and in_json:
                        break

            if json_lines:
                json_text = '\n'.join(json_lines)
                print(f"🔍 DEBUG: {self.name} trying line-by-line extraction: {json_text[:100]}...")
                try:
                    result = json.loads(json_text)
                    print(f"✅ DEBUG: {self.name} successfully parsed JSON from line-by-line extraction")
                    return result
                except json.JSONDecodeError:
                    print(f"🔍 DEBUG: {self.name} line-by-line extraction failed")

            print(f"❌ DEBUG: {self.name} could not extract valid JSON from response")
            # Return a structured error response
            return {
                "error": "Could not extract valid JSON from response",
                "raw_response": response,
                "agent": self.name
            }

        except Exception as e:
            print(f"❌ DEBUG: {self.name} JSON extraction failed with exception: {str(e)}")
            return {
                "error": f"JSON extraction failed: {str(e)}",
                "raw_response": response,
                "agent": self.name
            }

    def _balance_json_braces(self, text: str) -> str:
        """Attempt to balance JSON braces in a text string."""
        open_count = text.count('{')
        close_count = text.count('}')

        if open_count > close_count:
            # Add missing closing braces
            text += '}' * (open_count - close_count)
        elif close_count > open_count:
            # Remove extra closing braces from the end
            extra_closes = close_count - open_count
            for _ in range(extra_closes):
                text = text.rstrip().rstrip('}')

        return text

    @abstractmethod
    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component data against schema requirements."""
        pass

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]

    def add_tool(self, tool: BaseTool) -> None:
        """Add a new tool to the agent."""
        self.tools.append(tool)
        # Recreate the agent with the new tool
        self._setup_agent()

    def get_handoff_history(self) -> List[HandoffPayload]:
        """Get the history of handoff payloads received."""
        return self.handoff_payloads.copy()

    def create_handoff_payload(
        self,
        to_agent: str,
        data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
        context: str = ""
    ) -> HandoffPayload:
        """Create a handoff payload to send to another agent."""
        return HandoffPayload(
            from_agent=self.name,
            to_agent=to_agent,
            data=data,
            constraints=constraints or {},
            context=context
        )

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "type": self._get_agent_type(),
            "tools": self.get_available_tools(),
            "handoffs_received": len(self.handoff_payloads),
            "llm_type": type(self.llm).__name__,
            "model": getattr(self.llm, 'model', 'unknown') if hasattr(self.llm, 'model') else 'unknown'
        }