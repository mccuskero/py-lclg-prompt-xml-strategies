"""Multi-Agent System orchestrator for car creation workflows."""

from typing import Dict, Any, Optional, List, Union
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project modules to path
sys.path.append(str(Path(__file__).parent.parent))
from .supervisor_agent import CarCreationSupervisorAgent
from .engine_agent import EngineAgent
from .body_agent import BodyAgent
from .tire_agent import TireAgent
from .electrical_agent import ElectricalAgent
from llm.ollama_llm import OllamaLLM
from langchain_ollama import ChatOllama


class MultiAgentSystem:
    """Orchestrator for the car creation multi-agent system."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        execution_mode: str = "hybrid",
        enable_logging: bool = True,
        log_level: str = "INFO",
        use_json_subtypes_in_prompts_creation: bool = False
    ):
        """Initialize the multi-agent system.

        Args:
            model: Ollama model name to use
            base_url: Ollama server URL
            temperature: LLM temperature setting
            execution_mode: Workflow execution mode (hybrid, sequential, parallel)
            enable_logging: Whether to enable detailed logging
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            use_json_subtypes_in_prompts_creation: Whether to use JSON schema subtypes in prompts instead of markdown
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.execution_mode = execution_mode
        self.enable_logging = enable_logging
        self.log_level = log_level
        self.use_json_subtypes_in_prompts_creation = use_json_subtypes_in_prompts_creation

        # Initialize logging
        if self.enable_logging:
            self._setup_logging()

        # Initialize LLM for custom operations (using prompt-xml-strategies)
        self.llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=temperature
        )

        # Initialize ChatOllama for agents (required by create_agent)
        self.chat_llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature
        )

        # System status (must be initialized before agents)
        self.system_status = {
            "initialized": True,
            "agents_ready": False,
            "ollama_connection": False,
            "last_check": None
        }

        # Execution history
        self.execution_history: List[Dict[str, Any]] = []

        # Initialize agents (requires system_status to be available)
        self._initialize_agents()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Convert string log level to logging constant
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        log_level = log_level_map.get(self.log_level.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('car_creation_system.log')
            ]
        )
        self.logger = logging.getLogger('CarCreationSystem')
        self.logger.setLevel(log_level)

    def _initialize_agents(self) -> None:
        """Initialize all agents in the system."""
        try:
            # Initialize supervisor agent
            self.supervisor = CarCreationSupervisorAgent(
                name="CarCreationSupervisor",
                llm=self.chat_llm,
                execution_mode=self.execution_mode,
                use_json_subtypes_in_prompts_creation=self.use_json_subtypes_in_prompts_creation
            )

            # Direct access to specialized agents
            self.engine_agent = self.supervisor.engine_agent
            self.body_agent = self.supervisor.body_agent
            self.tire_agent = self.supervisor.tire_agent
            self.electrical_agent = self.supervisor.electrical_agent

            # Agent registry
            self.agents = {
                "supervisor": self.supervisor,
                "engine": self.engine_agent,
                "body": self.body_agent,
                "tire": self.tire_agent,
                "electrical": self.electrical_agent
            }

            self.system_status["agents_ready"] = True

            if self.enable_logging:
                self.logger.info("All agents initialized successfully")

        except Exception as e:
            self.system_status["agents_ready"] = False
            if self.enable_logging:
                self.logger.error(f"Agent initialization failed: {str(e)}")
            raise

    async def validate_system(self) -> Dict[str, Any]:
        """Validate system components and connectivity.

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {}
        }

        try:
            # Test Ollama connection
            try:
                ollama_status = self.llm.validate_connection()
                available_models = self.llm.get_available_models()

                validation_results["components"]["ollama"] = {
                    "status": "connected" if ollama_status else "disconnected",
                    "base_url": self.base_url,
                    "model": self.model,
                    "available_models": available_models[:5] if available_models else [],
                    "model_available": self.model in available_models if available_models else False
                }

                self.system_status["ollama_connection"] = ollama_status

            except Exception as e:
                validation_results["components"]["ollama"] = {
                    "status": "error",
                    "error": str(e),
                    "base_url": self.base_url
                }

            # Test agent initialization
            agent_status = {}
            for agent_name, agent in self.agents.items():
                try:
                    agent_info = agent.get_agent_info()
                    agent_status[agent_name] = {
                        "status": "ready",
                        "info": agent_info
                    }
                except Exception as e:
                    agent_status[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }

            validation_results["components"]["agents"] = agent_status

            # Determine overall status
            ollama_ok = validation_results["components"]["ollama"]["status"] == "connected"
            agents_ok = all(agent["status"] == "ready" for agent in agent_status.values())

            if ollama_ok and agents_ok:
                validation_results["overall_status"] = "ready"
            elif agents_ok:
                validation_results["overall_status"] = "agents_ready_ollama_issue"
            else:
                validation_results["overall_status"] = "not_ready"

            self.system_status["last_check"] = datetime.now().isoformat()

            if self.enable_logging:
                self.logger.info(f"System validation completed: {validation_results['overall_status']}")

        except Exception as e:
            validation_results["overall_status"] = "validation_error"
            validation_results["error"] = str(e)

            if self.enable_logging:
                self.logger.error(f"System validation failed: {str(e)}")

        return validation_results

    async def create_car(
        self,
        vin: str,
        year: str,
        make: str,
        model: str,
        execution_mode: Optional[str] = None,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """Create a complete car JSON using the multi-agent workflow.

        Args:
            vin: Vehicle Identification Number
            year: Car year
            make: Car make
            model: Car model
            execution_mode: Override execution mode for this request
            save_history: Whether to save execution to history

        Returns:
            Dictionary with car creation results
        """
        execution_start = datetime.now()

        # Validate system before execution
        validation_results = await self.validate_system()
        if validation_results["overall_status"] not in ["ready", "agents_ready_ollama_issue"]:
            return {
                "error": "System not ready for car creation",
                "validation_results": validation_results,
                "timestamp": execution_start.isoformat()
            }

        # Use provided execution mode or default
        exec_mode = execution_mode or self.execution_mode

        if self.enable_logging:
            self.logger.info(f"Starting car creation: {year} {make} {model} (VIN: {vin})")

        try:
            if self.enable_logging:
                self.logger.debug(f"Executing car creation workflow for {year} {make} {model}")
                self.logger.debug(f"VIN: {vin}, Execution mode: {exec_mode}")

            # Execute car creation workflow
            result = await self.supervisor.create_car_json(
                vin=vin,
                year=year,
                make=make,
                model=model,
                execution_mode=exec_mode
            )

            if self.enable_logging:
                self.logger.debug(f"Workflow execution completed with status: {result.get('workflow_status')}")
                self.logger.debug(f"Completed agents: {result.get('completed_agents', [])}")
                if result.get('errors'):
                    self.logger.debug(f"Errors encountered: {len(result['errors'])}")

            execution_end = datetime.now()
            execution_time = (execution_end - execution_start).total_seconds()

            # Enhance result with system information
            enhanced_result = {
                **result,
                "system_info": {
                    "execution_time_seconds": execution_time,
                    "execution_start": execution_start.isoformat(),
                    "execution_end": execution_end.isoformat(),
                    "model_used": self.model,
                    "base_url": self.base_url,
                    "execution_mode": exec_mode,
                    "system_validation": validation_results["overall_status"]
                }
            }

            # Save to history if requested
            if save_history:
                self._save_to_history(enhanced_result)

            if self.enable_logging:
                status = enhanced_result.get("workflow_status", "unknown")
                self.logger.info(f"Car creation completed: {status} ({execution_time:.2f}s)")

            return enhanced_result

        except Exception as e:
            error_result = {
                "error": f"Car creation failed: {str(e)}",
                "vin": vin,
                "make": make,
                "model": model,
                "execution_mode": exec_mode,
                "timestamp": execution_start.isoformat()
            }

            if self.enable_logging:
                self.logger.error(f"Car creation failed: {str(e)}")

            if save_history:
                self._save_to_history(error_result)

            return error_result

    def _save_to_history(self, result: Dict[str, Any]) -> None:
        """Save execution result to history."""
        self.execution_history.append(result)

        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

    async def test_individual_agent(
        self,
        agent_name: str,
        test_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test an individual agent with sample requirements.

        Args:
            agent_name: Name of the agent to test
            test_requirements: Test requirements (will use defaults if not provided)

        Returns:
            Dictionary with test results
        """
        if agent_name not in self.agents:
            return {
                "error": f"Unknown agent: {agent_name}",
                "available_agents": list(self.agents.keys())
            }

        agent = self.agents[agent_name]

        # Default test requirements by agent type
        default_requirements = {
            "engine": {
                "vehicle_type": "sedan",
                "performance_level": "standard",
                "fuel_preference": "gasoline",
                "electric_capable": False
            },
            "body": {
                "style": "sedan",
                "performance_level": "standard",
                "customization_level": "standard",
                "color_preference": "blue"
            },
            "tire": {
                "body_style": "sedan",
                "performance_level": "standard",
                "climate_preference": "all-season",
                "weight_class": "medium"
            },
            "electrical": {
                "engine_type": "v6_gasoline",
                "vehicle_class": "standard",
                "feature_level": "basic",
                "climate_requirements": "standard"
            },
            "supervisor": {
                "vin": "TEST123456789",
                "year": "2024",
                "make": "Test",
                "model": "Vehicle"
            }
        }

        requirements = test_requirements or default_requirements.get(agent_name, {})

        try:
            if agent_name == "supervisor":
                # Test supervisor with full workflow
                result = await self.supervisor.create_car_json(
                    vin=requirements["vin"],
                    year=requirements["year"],
                    make=requirements["make"],
                    model=requirements["model"]
                )
            else:
                # Test individual agent
                result = agent.create_component_json(requirements)

            return {
                "agent": agent_name,
                "test_status": "success",
                "requirements": requirements,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "agent": agent_name,
                "test_status": "error",
                "error": str(e),
                "requirements": requirements,
                "timestamp": datetime.now().isoformat()
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and information.

        Returns:
            Dictionary with system status
        """
        return {
            "system_status": self.system_status,
            "configuration": {
                "model": self.model,
                "base_url": self.base_url,
                "temperature": self.temperature,
                "execution_mode": self.execution_mode,
                "logging_enabled": self.enable_logging
            },
            "agents": {
                name: agent.get_agent_info()
                for name, agent in self.agents.items()
            },
            "execution_history_count": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history.

        Args:
            limit: Maximum number of executions to return

        Returns:
            List of recent execution results
        """
        return self.execution_history[-limit:] if self.execution_history else []

    def clear_execution_history(self) -> bool:
        """Clear the execution history.

        Returns:
            True if cleared successfully
        """
        try:
            self.execution_history.clear()
            if self.enable_logging:
                self.logger.info("Execution history cleared")
            return True
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Failed to clear execution history: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models.

        Returns:
            List of available model names
        """
        try:
            return self.llm.get_available_models()
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Failed to get available models: {str(e)}")
            return []

    def switch_model(self, new_model: str) -> bool:
        """Switch to a different Ollama model.

        Args:
            new_model: Name of the new model to use

        Returns:
            True if switch was successful
        """
        try:
            # Create new LLM instances
            new_llm = OllamaLLM(
                model=new_model,
                base_url=self.base_url,
                temperature=self.temperature
            )

            new_chat_llm = ChatOllama(
                model=new_model,
                base_url=self.base_url,
                temperature=self.temperature
            )

            # Test connection
            if new_llm.validate_connection():
                self.model = new_model
                self.llm = new_llm
                self.chat_llm = new_chat_llm

                # Update agents with new chat LLM
                for agent in self.agents.values():
                    agent.llm = new_chat_llm

                if self.enable_logging:
                    self.logger.info(f"Switched to model: {new_model}")

                return True
            else:
                if self.enable_logging:
                    self.logger.error(f"Failed to connect with model: {new_model}")
                return False

        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Model switch failed: {str(e)}")
            return False

    async def batch_create_cars(
        self,
        car_specifications: List[Dict[str, str]],
        execution_mode: Optional[str] = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Create multiple cars in batch with controlled concurrency.

        Args:
            car_specifications: List of car specs (each with vin, year, make, model)
            execution_mode: Execution mode for all cars
            max_concurrent: Maximum concurrent executions

        Returns:
            List of car creation results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def create_single_car(spec: Dict[str, str]) -> Dict[str, Any]:
            async with semaphore:
                return await self.create_car(
                    vin=spec["vin"],
                    year=spec["year"],
                    make=spec["make"],
                    model=spec["model"],
                    execution_mode=execution_mode,
                    save_history=False  # Don't save individual results to history
                )

        if self.enable_logging:
            self.logger.info(f"Starting batch creation of {len(car_specifications)} cars")

        try:
            # Execute all car creations concurrently
            tasks = [create_single_car(spec) for spec in car_specifications]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "error": f"Batch execution failed: {str(result)}",
                        "specification": car_specifications[i],
                        "index": i
                    })
                else:
                    processed_results.append(result)

            # Save batch result to history
            batch_summary = {
                "batch_execution": True,
                "total_cars": len(car_specifications),
                "successful": len([r for r in processed_results if "error" not in r]),
                "failed": len([r for r in processed_results if "error" in r]),
                "timestamp": datetime.now().isoformat(),
                "execution_mode": execution_mode or self.execution_mode,
                "results": processed_results
            }

            self._save_to_history(batch_summary)

            if self.enable_logging:
                success_count = batch_summary["successful"]
                total_count = batch_summary["total_cars"]
                self.logger.info(f"Batch creation completed: {success_count}/{total_count} successful")

            return processed_results

        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Batch creation failed: {str(e)}")

            return [{
                "error": f"Batch creation failed: {str(e)}",
                "specifications": car_specifications
            }]