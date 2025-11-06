"""Base agent class for the single-agent car creation system with interactive looping."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import json
import logging
import time
from pathlib import Path

from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models.base import BaseLanguageModel
from langchain.agents import create_agent

from memory.memory_manager import MemoryManager, MemoryBackendConfig, create_memory_manager


logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    content: str = Field(description="The message content")
    sender: str = Field(description="The agent that sent the message")
    recipient: Optional[str] = Field(default=None, description="The intended recipient")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseAgent(ABC):
    """Base class for single-agent car creation system with interactive capabilities."""

    def __init__(
        self,
        name: str,
        llm: BaseLanguageModel,
        temperature: float = 0.1,
        enable_logging: bool = True,
        log_llm_comms: bool = False,
        memory_config: Optional[MemoryBackendConfig] = None,
        max_memory_messages: int = 10
    ):
        self.name = name
        self.enable_logging = enable_logging
        self.log_llm_comms = log_llm_comms
        self.llm = llm
        self.tools: List[BaseTool] = []

        # Initialize memory manager with LangChain framework
        if memory_config is None:
            memory_config = MemoryBackendConfig(backend_type="memory")
        self.memory: MemoryManager = create_memory_manager(memory_config, max_messages=max_memory_messages)

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

            # Add to memory using LangChain message types
            self.memory.add_message(HumanMessage(content=human_content))
            if self.enable_logging:
                logger.debug(f"Added human message to memory (total messages: {len(self.memory.get_messages())})")

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

            # Log full LLM request if flag is enabled
            if self.log_llm_comms:
                logger.debug("=" * 80)
                logger.debug("LLM REQUEST - FULL SYSTEM MESSAGE:")
                logger.debug("=" * 80)
                logger.debug(system_content)
                logger.debug("=" * 80)
                logger.debug("LLM REQUEST - FULL HUMAN MESSAGE:")
                logger.debug("=" * 80)
                logger.debug(human_content)
                logger.debug("=" * 80)

            # ================================================
            # Run the Agent
            self.agent = create_agent(self.llm, self.tools)

            inputs = {
                "messages": [
                    SystemMessage(content=system_content),
                    HumanMessage(content=human_content)
                ]
            }

            response_message = self.agent.invoke(
                inputs,
                config=config
            )

            # ================================================

            if self.enable_logging:
                logger.debug(f"LLM invocation completed")
                logger.debug(f"Response type: {type(response_message)}")

            # Extract response content from agent response
            # The agent returns a dict with 'messages' key containing the conversation
            if isinstance(response_message, dict) and 'messages' in response_message:
                # Get the last message from the agent (the final AI response)
                messages = response_message['messages']
                if self.enable_logging:
                    logger.debug(f"Found {len(messages)} messages in response")
                    logger.debug(f"Message types: {[type(m).__name__ for m in messages]}")

                    # Log tool calls summary even without --log-llm-comms
                    tool_calls_found = []
                    for msg in messages:
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get('name', 'unknown')
                                tool_args = tc.get('args', {})
                                tool_calls_found.append({
                                    'name': tool_name,
                                    'args': tool_args
                                })

                    if tool_calls_found:
                        logger.info(f"🔧 LLM requested {len(tool_calls_found)} tool(s): {', '.join([t['name'] for t in tool_calls_found])}")
                        for tc in tool_calls_found:
                            logger.debug(f"   → {tc['name']}({', '.join([f'{k}={v}' for k, v in tc['args'].items()])})")

                # Log all messages in the conversation if flag is enabled
                if self.log_llm_comms:
                    logger.debug("=" * 80)
                    logger.debug("LLM RESPONSE - ALL MESSAGES IN CONVERSATION:")
                    logger.debug("=" * 80)
                    for idx, msg in enumerate(messages):
                        msg_type = type(msg).__name__
                        logger.debug(f"\n--- Message {idx + 1}/{len(messages)} ({msg_type}) ---")

                        # Handle AIMessage with tool calls
                        if msg_type == 'AIMessage' and hasattr(msg, 'tool_calls') and msg.tool_calls:
                            logger.debug(f"\n🔧 TOOL CALLS REQUESTED BY LLM:")
                            for tool_idx, tool_call in enumerate(msg.tool_calls):
                                logger.debug(f"\n  Tool Call {tool_idx + 1}:")
                                logger.debug(f"    Tool Name: {tool_call.get('name', 'N/A')}")
                                logger.debug(f"    Tool ID: {tool_call.get('id', 'N/A')}")
                                logger.debug(f"    Arguments: {json.dumps(tool_call.get('args', {}), indent=6)}")

                        # Handle ToolMessage with results
                        elif msg_type == 'ToolMessage':
                            tool_name = getattr(msg, 'name', 'unknown')
                            logger.debug(f"\n✅ TOOL RESULT (from {tool_name}):")
                            if hasattr(msg, 'content'):
                                # Try to pretty-print JSON content
                                try:
                                    result_json = json.loads(msg.content)
                                    logger.debug(f"    Result: {json.dumps(result_json, indent=6)}")
                                except:
                                    logger.debug(f"    Result: {msg.content}")

                        # Handle regular content
                        elif hasattr(msg, 'content') and msg.content:
                            logger.debug(f"Content: {msg.content}")

                        # Additional kwargs
                        if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                            logger.debug(f"Additional kwargs: {msg.additional_kwargs}")
                    logger.debug("=" * 80)

                # Find the last AIMessage in the list
                # AIMessage is the final response from the agent after tool calls
                last_ai_message = None
                for msg in reversed(messages):
                    msg_type = type(msg).__name__
                    if hasattr(msg, 'content'):
                        if msg_type == 'AIMessage':
                            last_ai_message = msg
                            break
                        elif last_ai_message is None:
                            # Fallback to any message with content if no AIMessage found
                            last_ai_message = msg

                if last_ai_message:
                    response_content = last_ai_message.content
                    if self.enable_logging:
                        logger.debug(f"Extracted content from {type(last_ai_message).__name__}")
                else:
                    if self.enable_logging:
                        logger.warning("No message with content found in response")
                    response_content = str(response_message)
            else:
                # Fallback for direct message responses
                response_content = response_message.content if hasattr(response_message, 'content') else str(response_message)

            if self.enable_logging:
                logger.debug(f"Extracted response content ({len(response_content)} chars)")
                logger.debug(f"Response preview: {response_content[:500]}...")
                # Log to a separate file for full response analysis
                try:
                    with open("full_response_debug.log", "w") as f:
                        f.write(response_content)
                    logger.debug("Full response written to full_response_debug.log")
                except Exception as e:
                    logger.debug(f"Could not write full response: {e}")

            # Add to memory using LangChain message types
            self.memory.add_message(AIMessage(content=response_content))

            if self.enable_logging:
                logger.debug(f"Added assistant response to memory")
                logger.debug(f"Received LLM response", extra={"response_length": len(response_content)})

            # Check if LLM is asking a question to the user
            if self.enable_logging:
                logger.debug(f"Checking for user_question in response")

            user_question = self._extract_question_json_from_response(response_content)

            if user_question:
                # LLM needs more information from the user
                if self.enable_logging:
                    logger.info(f"LLM requesting user input: {user_question}")
                return {
                    "user_question": user_question,
                    "requires_user_input": True,
                    "agent": self.name
                }

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
                logger.debug(f"Context memory updated, context_items={len(self.memory.get_all_context())}")

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

            # Try to handle multiple JSON objects separated by commas
            # This is a common pattern when LLMs return multiple tool results
            try:
                # Wrap in array brackets and parse
                array_wrapped = f"[{response.strip()}]"
                results = json.loads(array_wrapped)
                if isinstance(results, list) and len(results) > 0:
                    logger.debug(f"Successfully parsed {len(results)} JSON objects from comma-separated list")
                    # Merge all objects into one
                    merged = {}
                    for obj in results:
                        if isinstance(obj, dict):
                            merged.update(obj)
                    if merged:
                        logger.debug(f"Merged {len(results)} objects into single result with keys: {list(merged.keys())}")
                        return merged
            except json.JSONDecodeError:
                logger.debug("Response is not a comma-separated list of JSON objects")

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

    def _extract_question_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract user_question JSON from LLM response.

        The LLM can request information from the user by including JSON in this format:
        { "user_question" : "LLM question goes here" }

        Args:
            response: The LLM response text

        Returns:
            The question string if found, None otherwise
        """
        try:
            if self.enable_logging:
                logger.debug("Checking response for user_question")

            import re

            # First try to parse the entire response as JSON
            try:
                result = json.loads(response.strip())
                if isinstance(result, dict) and "user_question" in result:
                    question = result["user_question"]
                    if self.enable_logging:
                        logger.info(f"Found user_question in response: {question}")
                    return question
            except json.JSONDecodeError:
                pass

            # Look for user_question pattern in the text
            patterns = [
                r'\{\s*["\']user_question["\']\s*:\s*["\']([^"\']+)["\']\s*\}',
                r'user_question\s*:\s*["\']([^"\']+)["\']',
                r'"user_question"\s*:\s*"([^"]+)"',
            ]

            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    question = match.group(1)
                    if self.enable_logging:
                        logger.info(f"Found user_question via pattern: {question}")
                    return question

            # Look for JSON blocks that might contain user_question
            json_block_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
            ]

            for pattern in json_block_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    json_text = match.group(1)
                    try:
                        result = json.loads(json_text)
                        if isinstance(result, dict) and "user_question" in result:
                            question = result["user_question"]
                            if self.enable_logging:
                                logger.info(f"Found user_question in JSON block: {question}")
                            return question
                    except json.JSONDecodeError:
                        continue

            if self.enable_logging:
                logger.debug("No user_question found in response")
            return None

        except Exception as e:
            if self.enable_logging:
                logger.error(f"Error extracting user_question: {str(e)}", exc_info=True)
            return None

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
            "context_items": len(self.memory.get_all_context()),
            "message_history": len(self.memory.get_messages())
        }

    def reset_memory(self):
        """Reset the conversation memory."""
        self.memory.clear()
        if self.enable_logging:
            logger.info("Agent memory reset")
