"""Single Agent System for interactive car creation with looping and context management."""

import logging
from typing import Dict, Any, Optional
import json

from langchain_ollama import ChatOllama
from agents.car_agent import CarAgent
from memory.memory_manager import MemoryBackendConfig


logger = logging.getLogger(__name__)


class SingleAgentSystem:
    """
    Manages an interactive session with the CarAgent, handling tool calls and user input.
    """

    def __init__(
        self,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        enable_logging: bool = True,
        log_llm_comms: bool = False,
        memory_backend: str = "memory",
        memory_connection_string: Optional[str] = None,
        memory_session_id: str = "default",
        max_memory_messages: int = 10
    ):
        """
        Initialize the Single Agent System.

        Args:
            model_name: The LLM model name to use
            base_url: The base URL for the OLLAMA server
            temperature: Temperature for LLM generation
            enable_logging: Whether to enable logging
            log_llm_comms: Whether to log full LLM communications at DEBUG level
            memory_backend: Memory backend type ('memory' or 'postgres')
            memory_connection_string: PostgreSQL connection string (required if memory_backend='postgres')
            memory_session_id: Session ID for memory isolation (useful for PostgreSQL)
            max_memory_messages: Maximum number of messages to keep in memory (sliding window)
        """
        self.enable_logging = enable_logging
        self.log_llm_comms = log_llm_comms
        self.memory_backend = memory_backend

        # Create memory configuration
        memory_config = MemoryBackendConfig(
            backend_type=memory_backend,
            connection_string=memory_connection_string,
            session_id=memory_session_id
        )

        if self.enable_logging:
            logger.info(
                "Initializing Single Agent System",
                extra={
                    "model_name": model_name,
                    "base_url": base_url,
                    "temperature": temperature,
                    "log_llm_comms": log_llm_comms,
                    "memory_backend": memory_backend,
                    "memory_session_id": memory_session_id,
                    "max_memory_messages": max_memory_messages
                }
            )

        # Initialize LLM
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=base_url
        )

        # Initialize agent with memory configuration
        self.agent = CarAgent(
            llm=self.llm,
            temperature=temperature,
            enable_logging=enable_logging,
            log_llm_comms=log_llm_comms,
            memory_config=memory_config,
            max_memory_messages=max_memory_messages
        )

        self.session_active = False
        self.iteration_count = 0

    def interactive_session(self):
        """
        Run an interactive session where the user can create cars iteratively.
        The session maintains context across interactions.
        """
        self.session_active = True
        print("\n" + "=" * 60)
        print("  Welcome to the Interactive Car Creation System")
        print("=" * 60)
        print("\nThis system will help you design and configure a complete car.")
        print("The agent will remember context from previous interactions.")
        print("\n✨ NEW: The agent can now ask you questions to better understand")
        print("        your preferences and create a personalized car configuration!")
        print("\nCommands:")
        print("  - Type your car requirements naturally")
        print("  - Type 'reset' to clear the context and start fresh")
        print("  - Type 'status' to see current context")
        print("  - Type 'save <filename>' to save the current configuration")
        print("  - Type 'quit' or 'exit' to end the session")
        print("=" * 60 + "\n")

        try:
            while self.session_active:
                self.iteration_count += 1

                # Get user input
                user_input = input(f"\n[Iteration {self.iteration_count}] Your request: ").strip()

                if not user_input:
                    print("Please provide input or type 'quit' to exit.")
                    continue

                # Handle commands
                if user_input.lower() in ["quit", "exit"]:
                    self._handle_quit()
                    break
                elif user_input.lower() == "reset":
                    self._handle_reset()
                    continue
                elif user_input.lower() == "status":
                    self._handle_status()
                    continue
                elif user_input.lower().startswith("save "):
                    filename = user_input[5:].strip()
                    self._handle_save(filename)
                    continue

                # Process the user request
                print("\n" + "-" * 60)
                print(f"Processing your request...")
                print("-" * 60)

                result = self._process_iteration(user_input)

                # Display result
                self._display_result(result)

        except KeyboardInterrupt:
            print("\n\nSession interrupted by user.")
            self._handle_quit()
        except Exception as e:
            logger.error(f"Session error: {str(e)}", exc_info=True)
            print(f"\n❌ Session error: {str(e)}")
        finally:
            print("\nThank you for using the Interactive Car Creation System!")

    def _process_iteration(self, user_input: str) -> Dict[str, Any]:
        """
        Process a single iteration of the interactive session.
        Handles user questions from the LLM and continues the conversation.

        Args:
            user_input: The user's input text

        Returns:
            Dict containing the result of processing
        """
        try:
            if self.enable_logging:
                logger.info(
                    f"Processing iteration {self.iteration_count}",
                    extra={"user_input": user_input}
                )

            # Process user request through the agent
            result = self.agent.process_user_request(user_input)

            # Check if the LLM is asking a question to the user
            while result.get("requires_user_input", False) and "user_question" in result:
                question = result["user_question"]

                if self.enable_logging:
                    logger.info(f"LLM asking user: {question}")

                # Display the question to the user
                print(f"\n🤔 Agent Question: {question}")

                # Get user's answer
                user_answer = input("Your answer: ").strip()

                if not user_answer:
                    print("Please provide an answer or type 'skip' to skip this question.")
                    user_answer = input("Your answer: ").strip()

                if user_answer.lower() == "skip":
                    # Add a default answer to context and continue
                    self.agent.memory.add_context("skipped_question", question)
                    user_answer = "User chose to skip this question. Please use reasonable defaults."

                # Add the Q&A to context
                self.agent.memory.add_context(f"question_{self.iteration_count}", question)
                self.agent.memory.add_context(f"answer_{self.iteration_count}", user_answer)

                if self.enable_logging:
                    logger.info(f"User answered: {user_answer}")

                # Continue processing with the user's answer
                # Add the answer as a new requirement
                follow_up_input = f"Based on my previous answer: {user_answer}. Continue with the car configuration."
                result = self.agent.process_user_request(follow_up_input)

            if self.enable_logging:
                logger.info(
                    f"Iteration {self.iteration_count} completed",
                    extra={"has_error": "error" in result}
                )

            return result

        except Exception as e:
            if self.enable_logging:
                logger.error(
                    f"Iteration {self.iteration_count} failed: {str(e)}",
                    exc_info=True
                )
            return {
                "error": f"Failed to process iteration: {str(e)}",
                "iteration": self.iteration_count
            }

    def _display_result(self, result: Dict[str, Any]):
        """
        Display the result of processing to the user.

        Args:
            result: The result dictionary
        """
        print("\n" + "=" * 60)
        print("  Result")
        print("=" * 60)

        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            if "raw_response" in result:
                print(f"\nRaw response preview: {result['raw_response'][:200]}...")
        else:
            print("\n✅ Car configuration created successfully!")

            # Display car configuration summary
            if "car_configuration" in result:
                config = result["car_configuration"]

                if "vehicle_info" in config:
                    print("\n📋 Vehicle Information:")
                    for key, value in config["vehicle_info"].items():
                        print(f"  - {key}: {value}")

                if "engine" in config:
                    print("\n🔧 Engine Configuration:")
                    engine = config["engine"]
                    if isinstance(engine, dict):
                        for key, value in engine.items():
                            print(f"  - {key}: {value}")

                if "body" in config:
                    print("\n🚗 Body Configuration:")
                    body = config["body"]
                    if isinstance(body, dict) and "exterior" in body:
                        print("  Exterior:")
                        for key, value in body["exterior"].items():
                            print(f"    - {key}: {value}")

                if "electrical" in config:
                    print("\n⚡ Electrical System:")
                    electrical = config["electrical"]
                    if isinstance(electrical, dict) and "main_system" in electrical:
                        for key, value in electrical["main_system"].items():
                            print(f"  - {key}: {value}")

                if "tires_and_wheels" in config:
                    print("\n🛞 Tires and Wheels:")
                    tires = config["tires_and_wheels"]
                    if isinstance(tires, dict) and "tires" in tires:
                        for key, value in tires["tires"].items():
                            print(f"  - {key}: {value}")

            # Display metadata if available
            if "metadata" in result:
                metadata = result["metadata"]
                print("\n📊 Metadata:")
                print(f"  - Performance Category: {metadata.get('performance_summary', {}).get('performance_category', 'unknown')}")
                print(f"  - Compatibility: {metadata.get('estimated_compatibility', 'unknown')}")
                print(f"  - Context Items: {metadata.get('context_items', 0)}")
                print(f"  - Interactions: {metadata.get('interaction_count', 0)}")

        print("=" * 60)

    def _handle_quit(self):
        """Handle quit command."""
        print("\nEnding session...")
        self.session_active = False
        if self.enable_logging:
            logger.info(f"Session ended after {self.iteration_count} iterations")

    def _handle_reset(self):
        """Handle reset command - clear context and start fresh."""
        self.agent.reset_memory()
        self.iteration_count = 0
        print("\n🔄 Context cleared. Starting fresh!")
        if self.enable_logging:
            logger.info("Context reset by user")

    def _handle_status(self):
        """Handle status command - display current context."""
        print("\n" + "=" * 60)
        print("  Current Status")
        print("=" * 60)
        print(f"\nIteration Count: {self.iteration_count}")
        print(f"Memory Backend: {self.memory_backend}")
        print(f"Context Items: {len(self.agent.memory.get_all_context())}")
        print(f"Message History: {len(self.agent.memory.get_messages())}")

        context_data = self.agent.memory.get_all_context()
        if context_data:
            print("\nAccumulated Context:")
            for key, value in context_data.items():
                print(f"  - {key}: {value}")
        else:
            print("\nNo context accumulated yet.")

        print("=" * 60)

    def _handle_save(self, filename: str):
        """
        Handle save command - save current configuration to file.

        Args:
            filename: The filename to save to
        """
        try:
            # Get the last result from agent memory
            context_data = self.agent.memory.get_all_context()
            if not context_data:
                print("\n⚠️  No configuration to save yet.")
                return

            # Convert LangChain messages to serializable format
            messages = self.agent.memory.get_messages()
            serializable_messages = [
                {"type": type(msg).__name__, "content": msg.content}
                for msg in messages
            ]

            # Create a summary of the context
            save_data = {
                "iteration_count": self.iteration_count,
                "memory_backend": self.memory_backend,
                "context": context_data,
                "message_history": serializable_messages
            }

            # Save to file
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            print(f"\n💾 Configuration saved to: {filename}")

            if self.enable_logging:
                logger.info(f"Configuration saved to {filename}")

        except Exception as e:
            print(f"\n❌ Failed to save: {str(e)}")
            if self.enable_logging:
                logger.error(f"Save failed: {str(e)}", exc_info=True)

    def run_single_request(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single car creation request (non-interactive mode).

        Args:
            requirements: The car requirements

        Returns:
            Dict containing the car configuration
        """
        if self.enable_logging:
            logger.info("Running single request", extra={"requirements": requirements})

        result = self.agent.create_complete_car(requirements)

        return result
