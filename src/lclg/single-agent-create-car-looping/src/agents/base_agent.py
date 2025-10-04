"""Base agent class for the single-agent car creation system with interactive looping."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import json
import logging
import time
from pathlib import Path

from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models.base import BaseLanguageModel
from langgraph.prebuilt import create_react_agent



logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    content: str = Field(description="The message content")
    sender: str = Field(description="The agent that sent the message")
    recipient: Optional[str] = Field(default=None, description="The intended recipient")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationMemory:
    """Manages short-term conversation memory for context accumulation."""

    def __init__(self, max_history: int = 10):
        self.messages: List[Dict[str, str]] = []
        self.max_history = max_history
        self.context_data: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_history:
            self.messages.pop(0)

    def add_context(self, key: str, value: Any):
        """Add contextual data to memory."""
        self.context_data[key] = value

    def get_context_summary(self) -> str:
        """Get a formatted summary of accumulated context."""
        if not self.context_data:
            return "No context accumulated yet."

        summary = "Accumulated Context:\n"
        for key, value in self.context_data.items():
            summary += f"- {key}: {value}\n"
        return summary

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all conversation messages."""
        return self.messages.copy()

    def clear(self):
        """Clear all memory."""
        self.messages.clear()
        self.context_data.clear()


class BaseAgent(ABC):
    """Base class for single-agent car creation system with interactive capabilities."""

    def __init__(
        self,
        name: str,
        llm: BaseLanguageModel,
        temperature: float = 0.1,
        enable_logging: bool = True
    ):
        self.name = name
        self.enable_logging = enable_logging
        self.llm = llm
        self.tools: List[BaseTool] = []
        self.memory = ConversationMemory()

        # System and human prompt templates
        self.system_prompt_template = None
        self.human_prompt_template = None

        if self.enable_logging:
            logger.info(f"Initializing agent: {name}")

        try:
            start_time = time.time()
            self._setup_tools()
            self._setup_prompts()
            setup_time = time.time() - start_time

            if self.enable_logging:
                logger.info(
                    f"Agent setup completed successfully",
                    extra={
                        "setup_time": setup_time,
                        "tool_count": len(self.tools)
                    }
                )
        except Exception as e:
            if self.enable_logging:
                logger.error(f"Agent setup failed: {str(e)}", exc_info=True)
            raise

    @abstractmethod
    def _setup_tools(self) -> None:
        """Set up the tools for this agent. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _setup_prompts(self) -> None:
        """Set up prompt templates. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection. Must be implemented by subclasses."""
        pass

    def invoke_llm(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the LLM with system and human messages, including context memory.

        Args:
            requirements: The current request requirements

        Returns:
            Dict containing the response or error information
        """
        try:
            if self.enable_logging:
                logger.info(f"Invoking LLM with requirements", extra={"requirements": requirements})
                logger.debug(f"Requirements dict: {requirements}")

            # Format requirements as a readable string
            requirements_str = "\n".join([f"- {k}: {v}" for k, v in requirements.items()])
            if self.enable_logging:
                logger.debug(f"Formatted requirements string ({len(requirements_str)} chars)")

            # Build the human message with context
            context_summary = self.memory.get_context_summary()
            if self.enable_logging:
                logger.debug(f"Context summary: {context_summary[:200]}..." if len(context_summary) > 200 else f"Context summary: {context_summary}")

            human_content = self.human_prompt_template.format(
                requirements=requirements_str,
                context=context_summary
            )
            if self.enable_logging:
                logger.debug(f"Built human message ({len(human_content)} chars)")

            # Get system message content
            tools_list = self._format_tools_list()
            if self.enable_logging:
                logger.debug(f"Tools list: {tools_list[:200]}..." if len(tools_list) > 200 else f"Tools list: {tools_list}")

            system_content = self.system_prompt_template.format(
                tools=tools_list,
                input="{input}"  # Not used in direct invoke, but keeps template compatible
            )
            if self.enable_logging:
                logger.debug(f"Built system message ({len(system_content)} chars)")

            # Add to memory
            self.memory.add_message("human", human_content)
            if self.enable_logging:
                logger.debug(f"Added human message to memory (total messages: {len(self.memory.messages)})")

            # Configure generation parameters
            config = {
                "max_tokens": 1000,
                "temperature": 0.1,
                "format": "json",
            }
            if self.enable_logging:
                logger.debug(f"LLM config: {config}")

            # Invoke with both system and human messages
            if self.enable_logging:
                logger.debug(f"Invoking LLM with SystemMessage + HumanMessage")
                logger.debug(f"SystemMessage preview: {system_content[:150]}...")
                logger.debug(f"HumanMessage preview: {human_content[:150]}...")

            # The core `create_react_agent` function from LangChain 1.0.0a9
            self.agent_graph = create_react_agent(self.llm, 
                                                  self.tools)
            
            inputs = {
                "messages": [
                    SystemMessage(content=system_content),
                    HumanMessage(content=human_content)
                ]
            }
            
            response_message = self.agent_graph.invoke(
                inputs,
                config=config
            )

            if self.enable_logging:
                logger.debug(f"LLM invocation completed")

            # Extract response content
            response_content = response_message.content if hasattr(response_message, 'content') else str(response_message)

            if self.enable_logging:
                logger.debug(f"Extracted response content ({len(response_content)} chars)")
                logger.debug(f"Response preview: {response_content[:200]}...")

            # Add to memory
            self.memory.add_message("assistant", response_content)

            if self.enable_logging:
                logger.debug(f"Added assistant response to memory")
                logger.debug(f"Received LLM response", extra={"response_length": len(response_content)})

            # Extract JSON from response
            if self.enable_logging:
                logger.debug(f"Extracting JSON from response")

            component_data = self._extract_json_from_response(response_content)

            if self.enable_logging:
                logger.debug(f"JSON extraction completed, has_error={'error' in component_data}")

            # Validate the data
            if self.enable_logging:
                logger.debug(f"Validating component data")

            validated_data = self._validate_component_data(component_data)

            if self.enable_logging:
                logger.debug(f"Validation completed")

            # Update context memory
            if self.enable_logging:
                logger.debug(f"Updating context memory")

            self._update_context_memory(requirements, validated_data)

            if self.enable_logging:
                logger.debug(f"Context memory updated, context_items={len(self.memory.context_data)}")

            return validated_data

        except Exception as e:
            if self.enable_logging:
                logger.error(f"LLM invocation failed: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to invoke LLM: {str(e)}",
                "agent": self.name,
                "requirements": requirements
            }

    def _format_tools_list(self) -> str:
        """Format the list of available tools for the prompt."""
        if not self.tools:
            return "No tools available"

        tools_list = []
        for tool in self.tools:
            tools_list.append(f"- {tool.name}: {tool.description}")

        return "\n".join(tools_list)

    def _update_context_memory(self, requirements: Dict[str, Any], result: Dict[str, Any]):
        """Update context memory with new information."""
        # Store requirements
        for key, value in requirements.items():
            self.memory.add_context(f"req_{key}", value)

        # Store result summary if no error
        if "error" not in result:
            self.memory.add_context("last_result", "success")
            if "car_configuration" in result:
                config = result["car_configuration"]
                if "engine" in config:
                    self.memory.add_context("configured_engine", True)
                if "body" in config:
                    self.memory.add_context("configured_body", True)
                if "electrical" in config:
                    self.memory.add_context("configured_electrical", True)
                if "tires_and_wheels" in config:
                    self.memory.add_context("configured_tires", True)

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON data from agent response."""
        try:
            if self.enable_logging:
                logger.debug(f"Extracting JSON from response (length: {len(response)})")

            # First, try to parse the entire response as JSON
            try:
                result = json.loads(response.strip())
                logger.debug("Successfully parsed entire response as JSON")
                return result
            except json.JSONDecodeError:
                logger.debug("Entire response is not valid JSON, trying other methods...")

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
                    try:
                        result = json.loads(json_text)
                        logger.debug("Successfully parsed JSON block")
                        return result
                    except json.JSONDecodeError:
                        continue

            # Look for JSON object that starts after common prefixes
            json_prefixes = [
                r'(?:Here is|Here\'s|The configuration is|Configuration:|JSON:)?\s*(\{.*)',
                r'(?:Based on.*requirements:?)?\s*(\{.*)',
                r'(?:.*configuration.*:)?\s*(\{.*)',
                r'\{.*'
            ]

            for prefix_pattern in json_prefixes:
                json_matches = re.findall(prefix_pattern, response, re.DOTALL | re.IGNORECASE)

                for match in json_matches:
                    try:
                        balanced_json = self._balance_json_braces(match.strip())
                        result = json.loads(balanced_json)
                        logger.debug("Successfully parsed JSON from prefix pattern")
                        return result
                    except json.JSONDecodeError:
                        continue

            logger.warning("Could not extract valid JSON from response")

            # Return structured error response
            return {
                "error": "Could not extract valid JSON from response",
                "raw_response": response[:500],  # Truncate for safety
                "agent": self.name
            }

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}", exc_info=True)
            return {
                "error": f"JSON extraction failed: {str(e)}",
                "agent": self.name
            }

    def _balance_json_braces(self, text: str) -> str:
        """Attempt to balance JSON braces in a text string."""
        open_count = text.count('{')
        close_count = text.count('}')

        if open_count > close_count:
            text += '}' * (open_count - close_count)
        elif close_count > open_count:
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

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "type": self._get_agent_type(),
            "tools": self.get_available_tools(),
            "llm_type": type(self.llm).__name__,
            "context_items": len(self.memory.context_data),
            "message_history": len(self.memory.messages)
        }

    def reset_memory(self):
        """Reset the conversation memory."""
        self.memory.clear()
        if self.enable_logging:
            logger.info("Agent memory reset")
