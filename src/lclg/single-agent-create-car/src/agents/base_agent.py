"""Base agent class for the single-agent car creation system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field
import json
import sys
import time
from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.base import BaseLanguageModel

# Add prompts module to path
sys.path.append(str(Path(__file__).parent.parent))
from prompts.prompts import get_agent_prompt
from prompts.prompts_from_json_schema import get_schema_agent_prompt
from langchain_ollama import ChatOllama
from utils.logging_config import AgentLogger


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    content: str = Field(description="The message content")
    sender: str = Field(description="The agent that sent the message")
    recipient: Optional[str] = Field(default=None, description="The intended recipient")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseAgent(ABC):
    """Base class for single-agent car creation system."""

    def __init__(
        self,
        name: str,
        llm: Optional[BaseLanguageModel] = None,
        temperature: float = 0.1,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        use_json_subtypes_in_prompts_creation: bool = False,
        enable_logging: bool = True
    ):
        self.name = name
        self.enable_logging = enable_logging

        # Initialize logging
        if self.enable_logging:
            self.logger = AgentLogger(name)
            self.logger.info(f"Initializing agent: {name}", model_name=model_name, base_url=base_url)

        self.llm = llm or ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=base_url
        )
        self.use_json_subtypes_in_prompts_creation = use_json_subtypes_in_prompts_creation
        self.tools: List[BaseTool] = []
        self.agent_executor = None

        try:
            start_time = time.time()
            self._setup_tools()
            self._setup_agent()
            setup_time = time.time() - start_time

            if self.enable_logging:
                self.logger.info(
                    f"Agent setup completed successfully",
                    setup_time=setup_time,
                    tool_count=len(self.tools),
                    prompt_type="json_schema" if use_json_subtypes_in_prompts_creation else "markdown"
                )
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Agent setup failed: {str(e)}", error_type=type(e).__name__)
            raise

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
        if self.enable_logging:
            self.logger.debug("Setting up agent with tools", tool_count=len(self.tools))

        try:
            # Get the appropriate prompt for this agent type
            if self.use_json_subtypes_in_prompts_creation:
                # Use schema-driven prompts
                formatted_prompt = get_schema_agent_prompt(
                    agent_type=self._get_agent_type(),
                    agent_name=self.name,
                    system_prompt=self._get_system_prompt(),
                    tool_names=", ".join([tool.name for tool in self.tools]) if self.tools else "None"
                )
                if self.enable_logging:
                    self.logger.debug("Using JSON schema-driven prompts")
            else:
                # Use original markdown-based prompts
                formatted_prompt = get_agent_prompt(
                    agent_type=self._get_agent_type(),
                    agent_name=self.name,
                    system_prompt=self._get_system_prompt(),
                    tool_names=", ".join([tool.name for tool in self.tools]) if self.tools else "None"
                )
                if self.enable_logging:
                    self.logger.debug("Using markdown-based prompts")

            # Create the agent using LangChain v1.0.0a9 API
            self.agent_executor = create_agent(
                model=self.llm,
                tools=self.tools,
                prompt=formatted_prompt
            )

            if self.enable_logging:
                self.logger.debug("Agent executor created successfully")

        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Failed to setup agent: {str(e)}", error_type=type(e).__name__)
            raise

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process a message and return a response."""
        start_time = time.time()
        if self.enable_logging:
            self.logger.info(f"Processing message from {message.sender}", message_length=len(message.content))

        try:
            from langchain_core.messages import HumanMessage

            # Create the input for the agent
            inputs = {
                "messages": [HumanMessage(content=message.content)]
            }

            if self.enable_logging:
                self.logger.debug("Created input for agent executor")

            # Stream the response and collect the final result
            final_state = None
            async for chunk in self.agent_executor.astream(inputs):
                final_state = chunk

            # Extract the response from the final state
            response_content = self._extract_response_content(final_state)
            processing_time = time.time() - start_time

            if self.enable_logging:
                self.logger.info(
                    f"Message processed successfully",
                    processing_time=processing_time,
                    response_length=len(response_content)
                )

            return AgentMessage(
                content=response_content,
                sender=self.name,
                recipient=message.sender,
                metadata={"processing_time": processing_time}
            )
        except Exception as e:
            processing_time = time.time() - start_time
            if self.enable_logging:
                self.logger.error(
                    f"Error processing message: {str(e)}",
                    error_type=type(e).__name__,
                    processing_time=processing_time
                )
            return AgentMessage(
                content=f"Error processing message: {str(e)}",
                sender=self.name,
                recipient=message.sender,
                metadata={"error": True, "error_type": type(e).__name__, "processing_time": processing_time}
            )

    def _extract_response_content(self, final_state: Any) -> str:
        """Extract response content from the final agent state."""
        if final_state and "messages" in final_state:
            messages = final_state["messages"]
            if messages:
                last_message = messages[-1]
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
        return "No response generated"

    def create_component_json(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON component data for this agent's specialization."""
        start_time = time.time()
        if self.enable_logging:
            self.logger.log_component_creation("json_component", requirements, success=False)

        try:
            if self.enable_logging:
                self.logger.info(f"Creating component with requirements", requirements=requirements)

            # Use the agent to process the requirements
            message = AgentMessage(
                content=self._build_component_request(requirements),
                sender="system",
                recipient=self.name
            )

            if self.enable_logging:
                self.logger.debug(f"Sending request to LLM", message_length=len(message.content))

            # For synchronous processing, we'll use the LLM directly
            from langchain_core.messages import HumanMessage

            # Configure generation parameters to avoid truncation and force JSON format
            config = {
                "max_tokens": 1000,
                "temperature": 0.1,
                "format": "json",  # Force JSON output format in compatible LLMs
            }

            response_message = self.llm.invoke(
                [HumanMessage(content=message.content)],
                config=config
            )

            # Extract content from the response message
            response = response_message.content if hasattr(response_message, 'content') else str(response_message)

            if self.enable_logging:
                self.logger.debug(f"Received LLM response", response_length=len(response))

            # Extract JSON from the response
            component_data = self._extract_json_from_response(response)

            if self.enable_logging:
                self.logger.debug(f"Extracted component data", data_type=type(component_data).__name__)

            # Validate against schema requirements
            validated_data = self._validate_component_data(component_data)

            creation_time = time.time() - start_time
            if self.enable_logging:
                self.logger.log_component_creation("json_component", requirements, success=True)
                self.logger.info(f"Component creation successful", creation_time=creation_time)

            return validated_data

        except Exception as e:
            creation_time = time.time() - start_time
            if self.enable_logging:
                self.logger.error(
                    f"Component creation failed: {str(e)}",
                    error_type=type(e).__name__,
                    creation_time=creation_time,
                    requirements=requirements
                )
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

            # Look for JSON blocks marked with ```json or ```
            import re
            json_block_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'json\s*(\{.*?\})',
            ]

            for pattern in json_block_patterns:
                json_match = re.search(pattern, response, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                    print(f"🔍 DEBUG: {self.name} found JSON block: {json_text[:100]}...")
                    try:
                        result = json.loads(json_text)
                        print(f"✅ DEBUG: {self.name} successfully parsed JSON block")
                        return result
                    except json.JSONDecodeError:
                        print(f"🔍 DEBUG: {self.name} JSON block is not valid, continuing...")

            # Look for JSON object that starts after common prefixes
            json_prefixes = [
                r'(?:Here is|Here\'s|The configuration is|Configuration:|JSON:)?\s*(\{.*)',
                r'(?:Based on.*requirements:?)?\s*(\{.*)',
                r'(?:.*configuration.*:)?\s*(\{.*)',
                r'\{.*'  # fallback: any JSON starting with {
            ]

            for prefix_pattern in json_prefixes:
                json_matches = re.findall(prefix_pattern, response, re.DOTALL | re.IGNORECASE)

                for i, match in enumerate(json_matches):
                    try:
                        # Try to balance braces properly
                        balanced_json = self._balance_json_braces(match.strip())
                        print(f"🔍 DEBUG: {self.name} balanced JSON attempt from prefix {prefix_pattern[:20]}...: {balanced_json[:100]}...")

                        # Try to repair common JSON formatting issues
                        repaired_json = self._repair_json_formatting(balanced_json)
                        print(f"🔧 DEBUG: {self.name} after repair: {repaired_json[:200]}...")
                        result = json.loads(repaired_json)
                        print(f"✅ DEBUG: {self.name} successfully parsed JSON object from prefix pattern")
                        return result
                    except json.JSONDecodeError as e:
                        print(f"🔍 DEBUG: {self.name} prefix pattern match is not valid JSON ({str(e)}), continuing...")
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

            # Try to create a fallback response using basic parsing
            fallback_response = self._create_fallback_response(response)
            if fallback_response:
                print(f"🔄 DEBUG: {self.name} using fallback response generation")
                return fallback_response

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

    def _repair_json_formatting(self, json_text: str) -> str:
        """Repair common JSON formatting issues from LLM responses."""
        import re

        # Common patterns that LLMs generate incorrectly
        repairs = [
            # Fix unquoted numbers with units (e.g., 2.5L -> "2.5L")
            (r':\s*(\d+\.?\d*[A-Za-z]+)', r': "\1"'),
            # Fix unquoted numbers followed by space and units (e.g., 170 lb-ft -> "170 lb-ft")
            (r':\s*(\d+\.?\d*\s+[A-Za-z-]+)', r': "\1"'),
            # Fix unquoted numbers with decimal and units including periods (e.g., 184.5 in -> "184.5 in")
            (r':\s*(\d+\.?\d*\s+[A-Za-z\.]+)', r': "\1"'),
            # Fix malformed quoted strings (e.g., "170lb"-ft -> "170 lb-ft")
            (r'"(\d+[A-Za-z]+)"-([A-Za-z]+)', r'"\1-\2"'),
            # Fix unquoted numbers with no units but in string context (e.g., horsepower: 180 -> "180")
            (r'("(?:horsepower|torque|width|height|length|doors)":\s*)(\d+\.?\d*)(?=,|\s*})', r'\1"\2"'),
            # Fix multi-word unquoted strings (e.g., sedan body style -> "sedan body style")
            (r':\s*([a-zA-Z]+\s+[a-zA-Z]+\s+[a-zA-Z]+)(?=,|\s*})', r': "\1"'),
            # Fix unquoted units after values (e.g., "180" HP -> "180 HP")
            (r'("(?:\d+\.?\d*)")\s+([A-Za-z-]+)', r'"\1 \2"'),
            # Remove trailing commas before closing braces/brackets
            (r',(\s*[}\]])', r'\1'),
        ]

        repaired = json_text
        for pattern, replacement in repairs:
            repaired = re.sub(pattern, replacement, repaired)

        # Find the end of the main JSON object and strip everything after it
        repaired = self._trim_to_valid_json(repaired)

        return repaired

    def _trim_to_valid_json(self, json_text: str) -> str:
        """Trim text to contain only the main JSON object."""
        lines = json_text.split('\n')
        json_lines = []
        brace_count = 0
        started = False

        for line in lines:
            if not started and '{' in line:
                started = True

            if started:
                json_lines.append(line)
                brace_count += line.count('{') - line.count('}')

                # If we've closed the main object, stop
                if brace_count == 0 and started:
                    break

        return '\n'.join(json_lines)

    def _create_fallback_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Create a fallback response when JSON parsing fails."""
        try:
            # Extract key information from the response text using basic parsing
            import re

            # Basic car configuration structure
            fallback = {
                "car_configuration": {
                    "vehicle_info": {
                        "type": "sedan",
                        "performance_level": "standard",
                        "fuel_preference": "gasoline",
                        "budget": "medium"
                    },
                    "engine": {
                        "displacement": "2.5L",
                        "cylinders": "4",
                        "fuelType": "gasoline",
                        "horsepower": "180",
                        "@engineCode": "ECO-250",
                        "@manufacturer": "Generic Motors"
                    },
                    "body": {
                        "exterior": {
                            "style": "sedan",
                            "color": "silver",
                            "doors": 4,
                            "material": "steel"
                        },
                        "interior": {
                            "seating": "5-passenger",
                            "upholstery": "cloth",
                            "dashboard": "standard"
                        }
                    },
                    "electrical": {
                        "main_system": {
                            "voltage_system": "12V",
                            "battery_capacity": "75Ah"
                        },
                        "battery": {
                            "voltage": "12V",
                            "capacity": "75Ah"
                        },
                        "lighting": {
                            "headlights": "LED",
                            "taillights": "LED"
                        }
                    },
                    "tires_and_wheels": {
                        "tires": {
                            "brand": "Goodyear",
                            "size": "225/60R16",
                            "pressure": "32 PSI"
                        },
                        "wheels": {
                            "size": "16 inch",
                            "material": "alloy",
                            "design": "5-spoke"
                        }
                    }
                },
                "fallback_generated": True,
                "original_response_length": len(response)
            }

            # Try to extract specific values from the response if available
            horsepower_match = re.search(r'(?:horsepower|hp).*?(\d+)', response, re.IGNORECASE)
            if horsepower_match:
                fallback["car_configuration"]["engine"]["horsepower"] = horsepower_match.group(1)

            displacement_match = re.search(r'(?:displacement).*?(\d+\.?\d*\s*L)', response, re.IGNORECASE)
            if displacement_match:
                fallback["car_configuration"]["engine"]["displacement"] = displacement_match.group(1)

            color_match = re.search(r'(?:color).*?(silver|black|white|blue|red|gray)', response, re.IGNORECASE)
            if color_match:
                fallback["car_configuration"]["body"]["exterior"]["color"] = color_match.group(1).lower()

            return fallback

        except Exception as e:
            print(f"🔄 DEBUG: Fallback generation failed: {str(e)}")
            return None

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

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "type": self._get_agent_type(),
            "tools": self.get_available_tools(),
            "llm_type": type(self.llm).__name__,
            "model": getattr(self.llm, 'model', 'unknown') if hasattr(self.llm, 'model') else 'unknown'
        }