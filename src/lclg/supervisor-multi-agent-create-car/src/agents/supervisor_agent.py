"""Car Creation Supervisor Agent - Orchestrates multi-agent car creation workflow using LangGraph."""

from typing import Dict, Any, Optional, List, Literal
import json
import asyncio
import sys
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict

# Add project modules to path
sys.path.append(str(Path(__file__).parent.parent))
from .base_agent import BaseAgent, HandoffPayload
from .engine_agent import EngineAgent
from .body_agent import BodyAgent
from .tire_agent import TireAgent
from .electrical_agent import ElectricalAgent
from prompts.prompts import get_car_creation_task_prompt, get_schema_validation_prompt


class CarCreationState(BaseModel):
    """State management for car creation workflow."""

    # Car build requirements
    vin: str = Field(description="Vehicle Identification Number")
    year: str = Field(description="Car year")
    make: str = Field(description="Car make")
    model: str = Field(description="Car model")

    # Component data
    engine_data: Optional[Dict[str, Any]] = Field(default=None, description="Engine component data")
    body_data: Optional[Dict[str, Any]] = Field(default=None, description="Body component data")
    tire_data: Optional[Dict[str, Any]] = Field(default=None, description="Tire component data")
    electrical_data: Optional[Dict[str, Any]] = Field(default=None, description="Electrical component data")

    # Workflow state
    current_agent: Optional[str] = Field(default=None, description="Currently active agent")
    completed_agents: List[str] = Field(default_factory=list, description="Completed agents")
    workflow_status: str = Field(default="initialized", description="Overall workflow status")

    # Handoff coordination
    pending_handoffs: List[HandoffPayload] = Field(default_factory=list, description="Pending handoff payloads")

    # Final results
    car_json: Optional[Dict[str, Any]] = Field(default=None, description="Final assembled car JSON")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")

    # Error handling
    errors: List[str] = Field(default_factory=list, description="Workflow errors")


class CoordinationTool(BaseTool):
    """Tool for coordinating between agents in the supervisor workflow."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "coordinate_agents"
    description: str = ("Coordinate workflow between specialized car creation agents, "
                       "manage handoffs, and track completion status.")
    supervisor: Any = Field(description="Reference to the supervisor agent")

    def __init__(self, supervisor_agent, **kwargs):
        super().__init__(supervisor=supervisor_agent, **kwargs)

    def _run(self, action: str, agent_name: str = "", data: str = "") -> str:
        """Coordinate agent actions.

        Args:
            action: Action to perform (start_agent, complete_agent, handoff, validate)
            agent_name: Name of the agent to coordinate
            data: Additional data for the action

        Returns:
            JSON string with coordination result
        """
        try:
            if action == "start_agent":
                return self.supervisor._start_agent_coordination(agent_name)
            elif action == "complete_agent":
                return self.supervisor._complete_agent_coordination(agent_name, data)
            elif action == "handoff":
                return self.supervisor._process_handoff_coordination(agent_name, data)
            elif action == "validate":
                return self.supervisor._validate_component_coordination(agent_name, data)
            else:
                return json.dumps({"error": f"Unknown coordination action: {action}"})

        except Exception as e:
            return json.dumps({"error": f"Coordination failed: {str(e)}"})


class CarCreationSupervisorAgent(BaseAgent):
    """Supervisor agent that orchestrates the car creation multi-agent workflow using LangGraph."""

    def __init__(self, **kwargs):
        # Initialize workflow execution mode
        self.execution_mode = kwargs.pop("execution_mode", "hybrid")  # hybrid, sequential, parallel
        # Initialize prompt creation mode
        self.use_json_subtypes_in_prompts_creation = kwargs.pop("use_json_subtypes_in_prompts_creation", False)

        super().__init__(**kwargs)

        # Initialize specialized agents
        self.engine_agent = EngineAgent(
            name="EngineAgent",
            llm=self.llm,
            use_json_subtypes_in_prompts_creation=self.use_json_subtypes_in_prompts_creation
        )
        self.body_agent = BodyAgent(
            name="BodyAgent",
            llm=self.llm,
            use_json_subtypes_in_prompts_creation=self.use_json_subtypes_in_prompts_creation
        )
        self.tire_agent = TireAgent(
            name="TireAgent",
            llm=self.llm,
            use_json_subtypes_in_prompts_creation=self.use_json_subtypes_in_prompts_creation
        )
        self.electrical_agent = ElectricalAgent(
            name="ElectricalAgent",
            llm=self.llm,
            use_json_subtypes_in_prompts_creation=self.use_json_subtypes_in_prompts_creation
        )

        # Create LangGraph workflow
        self.workflow_graph = self._create_workflow_graph()

    def _setup_tools(self) -> None:
        """Set up supervisor-specific tools."""
        self.tools = [
            CoordinationTool(self)
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor agent."""
        return """You are the Car Creation Supervisor Agent, responsible for orchestrating a complex multi-agent workflow to create complete car JSON descriptions.

Your responsibilities include:

1. Workflow Orchestration: Coordinate sequential and parallel execution of specialized agents
2. Handoff Management: Process and route handoff payloads between agents
3. State Management: Track workflow progress and component completion
4. Validation Coordination: Ensure all components meet car.json schema requirements
5. Final Assembly: Combine all component data into a complete car JSON

Available Specialized Agents:
- EngineAgent: Creates engineType JSON with handoff to BodyAgent
- BodyAgent: Creates bodyType JSON, processes engine constraints
- TireAgent: Creates tireType JSON, considers body style dependencies
- ElectricalAgent: Creates electricalType JSON, processes engine requirements

Workflow Execution Modes:
- hybrid: Sequential dependencies (Engine→Body), parallel where possible (Body+Electrical)
- sequential: One agent at a time with full handoff processing
- parallel: Maximum parallel execution with post-processing coordination

Always ensure complete car.json schema compliance and successful component integration."""

    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "supervisor"

    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow for car creation."""

        # Define the workflow graph with dictionary state
        workflow = StateGraph(dict)

        # Add nodes for each phase
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("engine_phase", self._execute_engine_phase)
        workflow.add_node("body_electrical_phase", self._execute_body_electrical_phase)
        workflow.add_node("tire_phase", self._execute_tire_phase)
        workflow.add_node("assembly_phase", self._assemble_car_json)
        workflow.add_node("validation_phase", self._validate_final_json)

        # Define workflow edges
        workflow.add_edge("initialize", "engine_phase")
        workflow.add_edge("engine_phase", "body_electrical_phase")
        workflow.add_edge("body_electrical_phase", "tire_phase")
        workflow.add_edge("tire_phase", "assembly_phase")
        workflow.add_edge("assembly_phase", "validation_phase")
        workflow.add_edge("validation_phase", END)

        # Set entry point
        workflow.set_entry_point("initialize")

        return workflow.compile()

    async def _initialize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the car creation workflow."""
        print(f"🔧 DEBUG: Initializing workflow for {state.get('year')} {state.get('make')} {state.get('model')}")

        # LangGraph passes state as dictionary, update directly
        state["workflow_status"] = "initialized"
        state["current_agent"] = "supervisor"
        state["completed_agents"] = []

        # Ensure errors list exists
        if "errors" not in state:
            state["errors"] = []

        # Validate required car information
        required_fields = ["vin", "year", "make", "model"]
        for field in required_fields:
            if not state.get(field):
                state["errors"].append(f"Missing required field: {field}")

        if not state["errors"]:
            state["workflow_status"] = "ready"
            print(f"✅ DEBUG: Workflow initialized successfully")
        else:
            print(f"❌ DEBUG: Workflow initialization failed with errors: {state['errors']}")

        return state

    async def _execute_engine_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the engine configuration phase."""
        print(f"🚗 DEBUG: Starting engine phase")
        state["current_agent"] = "engine"

        try:
            # Build engine requirements
            engine_requirements = {
                "vehicle_type": self._infer_vehicle_type(state["make"], state["model"]),
                "performance_level": "standard",  # Could be derived from model
                "fuel_preference": "gasoline",
                "electric_capable": False
            }

            print(f"🔧 DEBUG: Executing engine agent with requirements: {engine_requirements}")

            # Execute engine agent
            engine_result = self.engine_agent.create_engine_with_handoff(
                requirements=engine_requirements,
                target_agent="body"
            )

            print(f"🔧 DEBUG: Engine agent returned: {type(engine_result)} with keys: {list(engine_result.keys()) if isinstance(engine_result, dict) else 'not dict'}")

            if "error" in engine_result:
                print(f"❌ DEBUG: Engine phase failed: {engine_result['error']}")
                state["errors"].append(f"Engine phase failed: {engine_result['error']}")
                state["workflow_status"] = "error"
            else:
                print(f"✅ DEBUG: Engine phase completed successfully")
                state["engine_data"] = engine_result["engine_configuration"]

                # Queue handoff payload for body agent
                if "pending_handoffs" not in state:
                    state["pending_handoffs"] = []

                # Store handoff payload as dict (LangGraph works with serializable data)
                handoff_payload = engine_result["handoff_payload"]
                state["pending_handoffs"].append(handoff_payload)

                state["completed_agents"].append("engine")
                state["workflow_status"] = "engine_completed"

        except Exception as e:
            state["errors"].append(f"Engine phase exception: {str(e)}")
            state["workflow_status"] = "error"

        return state

    async def _execute_body_electrical_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute body and electrical phases in parallel."""
        state["current_agent"] = "body_electrical"

        try:
            # Process engine handoff for body agent
            engine_handoff = None
            for handoff in state.get("pending_handoffs", []):
                if handoff and handoff.get("to_agent") == "body":
                    # Convert dict back to HandoffPayload for agent processing
                    handoff_payload = HandoffPayload(**handoff)
                    self.body_agent.process_handoff(handoff_payload)
                    engine_handoff = handoff
                    break

            # Build requirements for both agents
            body_requirements = {
                "style": self._infer_body_style(state["make"], state["model"]),
                "performance_level": "standard",
                "customization_level": "standard",
                "color_preference": "auto"
            }

            # Get engine data safely
            engine_data = state.get("engine_data") or {}
            electrical_requirements = {
                "engine_type": engine_data.get("fuelType", "gasoline"),
                "vehicle_class": "standard",
                "feature_level": "basic",
                "climate_requirements": "standard"
            }

            # Create handoff for electrical agent from engine data
            if engine_data and engine_handoff:
                electrical_handoff = HandoffPayload(
                    from_agent="engine",
                    to_agent="electrical",
                    data={
                        "engine_type": engine_data.get("fuelType", "gasoline"),
                        "horsepower": engine_data.get("horsepower", "280"),
                        "cooling_requirements": engine_handoff.get("data", {}).get("cooling_requirements", "standard") if engine_handoff else "standard"
                    },
                    constraints=engine_handoff.get("constraints", {}) if engine_handoff else {},
                    context="Engine data forwarded for electrical system design"
                )
                self.electrical_agent.process_handoff(electrical_handoff)

            # Execute both agents in parallel
            body_task = asyncio.create_task(
                self._execute_body_agent(body_requirements)
            )
            electrical_task = asyncio.create_task(
                self._execute_electrical_agent(electrical_requirements)
            )

            # Wait for both to complete
            body_result, electrical_result = await asyncio.gather(body_task, electrical_task)

            # Process results
            if body_result and "error" in body_result:
                state["errors"].append(f"Body phase failed: {body_result['error']}")
            elif body_result:
                state["body_data"] = body_result.get("bodyType")
                state["completed_agents"].append("body")
            else:
                state["errors"].append("Body agent returned no result")

            if electrical_result and "error" in electrical_result:
                state["errors"].append(f"Electrical phase failed: {electrical_result['error']}")
            elif electrical_result:
                state["electrical_data"] = electrical_result.get("electricalType")
                state["completed_agents"].append("electrical")
            else:
                state["errors"].append("Electrical agent returned no result")

            if not state["errors"]:
                state["workflow_status"] = "body_electrical_completed"
            else:
                state["workflow_status"] = "error"

        except Exception as e:
            state["errors"].append(f"Body/Electrical phase exception: {str(e)}")
            state["workflow_status"] = "error"

        return state

    async def _execute_tire_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tire configuration phase."""
        state["current_agent"] = "tire"

        try:
            # Create handoff from body data
            body_data = state.get("body_data")
            if body_data:
                body_handoff = HandoffPayload(
                    from_agent="body",
                    to_agent="tire",
                    data={
                        "body_style": body_data.get("style", "sedan"),
                        "material": body_data.get("material", "steel"),
                        "customized": body_data.get("@customized", False)
                    },
                    constraints={},
                    context="Body configuration completed for tire sizing"
                )
                self.tire_agent.process_handoff(body_handoff)

            # Build tire requirements
            tire_requirements = {
                "body_style": body_data.get("style", "sedan") if body_data else "sedan",
                "performance_level": "standard",
                "climate_preference": "all-season",
                "weight_class": "medium",
                "run_flat_required": False
            }

            # Execute tire agent
            tire_result = self.tire_agent.create_tire_with_constraints(tire_requirements)

            if "error" in tire_result:
                state["errors"].append(f"Tire phase failed: {tire_result['error']}")
                state["workflow_status"] = "error"
            else:
                state["tire_data"] = tire_result["tireType"]
                state["completed_agents"].append("tire")
                state["workflow_status"] = "tire_completed"

        except Exception as e:
            state["errors"].append(f"Tire phase exception: {str(e)}")
            state["workflow_status"] = "error"

        return state

    async def _assemble_car_json(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble the final car JSON from all components."""
        state["current_agent"] = "supervisor"

        try:
            # Validate all components are present
            required_components = ["engine_data", "body_data", "tire_data", "electrical_data"]
            missing_components = []

            for component in required_components:
                if not state.get(component):
                    missing_components.append(component)

            if missing_components:
                state["errors"].append(f"Missing components for assembly: {missing_components}")
                state["workflow_status"] = "assembly_error"
                return state

            # Assemble complete car JSON according to car.json schema
            state["car_json"] = {
                "Engine": state["engine_data"],
                "Body": state["body_data"],
                "Tire": state["tire_data"],
                "Electrical": state["electrical_data"],
                "@vin": state["vin"],
                "@year": state["year"],
                "@make": state["make"],
                "@model": state["model"]
            }

            state["workflow_status"] = "assembled"

        except Exception as e:
            state["errors"].append(f"Assembly phase exception: {str(e)}")
            state["workflow_status"] = "assembly_error"

        return state

    async def _validate_final_json(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the final car JSON against the schema."""
        state["current_agent"] = "supervisor"

        try:
            if not state["car_json"]:
                state["errors"].append("No car JSON to validate")
                state["workflow_status"] = "validation_error"
                return state

            # Perform basic validation
            validation_results = {
                "schema_compliance": True,
                "required_fields": [],
                "warnings": []
            }

            # Check required top-level attributes
            required_attrs = ["@vin", "@year", "@make", "@model"]
            for attr in required_attrs:
                if attr not in state["car_json"]:
                    validation_results["required_fields"].append(attr)
                    validation_results["schema_compliance"] = False

            # Check required components
            required_components = ["Engine", "Body", "Tire", "Electrical"]
            for component in required_components:
                if component not in state["car_json"]:
                    validation_results["required_fields"].append(component)
                    validation_results["schema_compliance"] = False

            state["validation_results"] = validation_results

            if validation_results["schema_compliance"]:
                state["workflow_status"] = "completed"
            else:
                state["workflow_status"] = "validation_error"
                state["errors"].append(f"Schema validation failed: {validation_results['required_fields']}")

        except Exception as e:
            state["errors"].append(f"Validation phase exception: {str(e)}")
            state["workflow_status"] = "validation_error"

        return state

    async def _execute_body_agent(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute body agent asynchronously."""
        try:
            return self.body_agent.create_body_with_constraints(requirements)
        except Exception as e:
            return {"error": f"Body agent execution failed: {str(e)}"}

    async def _execute_electrical_agent(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Execute electrical agent asynchronously."""
        try:
            return self.electrical_agent.create_electrical_with_dependencies(requirements)
        except Exception as e:
            return {"error": f"Electrical agent execution failed: {str(e)}"}

    def _infer_vehicle_type(self, make: str, model: str) -> str:
        """Infer vehicle type from make and model."""
        model_lower = model.lower()

        if any(keyword in model_lower for keyword in ["truck", "f-150", "silverado", "ram"]):
            return "truck"
        elif any(keyword in model_lower for keyword in ["suv", "explorer", "tahoe", "suburban"]):
            return "suv"
        elif any(keyword in model_lower for keyword in ["coupe", "corvette", "mustang", "camaro"]):
            return "coupe"
        elif any(keyword in model_lower for keyword in ["hatchback", "civic", "focus"]):
            return "hatchback"
        elif any(keyword in model_lower for keyword in ["wagon", "outback", "forester"]):
            return "wagon"
        elif any(keyword in model_lower for keyword in ["convertible", "roadster"]):
            return "convertible"
        else:
            return "sedan"  # Default

    def _infer_body_style(self, make: str, model: str) -> str:
        """Infer body style from make and model."""
        return self._infer_vehicle_type(make, model)  # Same logic for now

    # Coordination methods
    def _start_agent_coordination(self, agent_name: str) -> str:
        """Start coordination for a specific agent."""
        return json.dumps({
            "status": "started",
            "agent": agent_name,
            "message": f"Started coordination for {agent_name}"
        })

    def _complete_agent_coordination(self, agent_name: str, data: str) -> str:
        """Complete coordination for a specific agent."""
        return json.dumps({
            "status": "completed",
            "agent": agent_name,
            "data": data,
            "message": f"Completed coordination for {agent_name}"
        })

    def _process_handoff_coordination(self, agent_name: str, data: str) -> str:
        """Process handoff coordination."""
        return json.dumps({
            "status": "handoff_processed",
            "agent": agent_name,
            "data": data,
            "message": f"Processed handoff for {agent_name}"
        })

    def _validate_component_coordination(self, agent_name: str, data: str) -> str:
        """Validate component coordination."""
        return json.dumps({
            "status": "validated",
            "agent": agent_name,
            "data": data,
            "message": f"Validated component for {agent_name}"
        })

    # Main execution methods
    async def create_car_json(
        self,
        vin: str,
        year: str,
        make: str,
        model: str,
        execution_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a complete car JSON using the multi-agent workflow.

        Args:
            vin: Vehicle Identification Number
            year: Car year
            make: Car make
            model: Car model
            execution_mode: Workflow execution mode (hybrid, sequential, parallel)

        Returns:
            Dictionary with complete car JSON and workflow results
        """
        try:
            # Initialize state - convert Pydantic model to dict for LangGraph
            initial_state = CarCreationState(
                vin=vin,
                year=year,
                make=make,
                model=model
            )

            # Convert to dictionary for LangGraph
            state_dict = initial_state.model_dump()

            # Execute workflow
            final_state = await self.workflow_graph.ainvoke(state_dict)

            # Handle the final state (LangGraph returns a dictionary)
            if isinstance(final_state, dict):
                # Extract values from dictionary
                car_json = final_state.get("car_json")
                workflow_status = final_state.get("workflow_status", "unknown")
                completed_agents = final_state.get("completed_agents", [])
                validation_results = final_state.get("validation_results", {})
                errors = final_state.get("errors", [])
            else:
                # Handle CarCreationState object (fallback)
                car_json = final_state["car_json"]
                workflow_status = final_state["workflow_status"]
                completed_agents = final_state["completed_agents"]
                validation_results = final_state["validation_results"]
                errors = final_state["errors"]

            # Return results
            return {
                "car_json": car_json,
                "workflow_status": workflow_status,
                "completed_agents": completed_agents,
                "validation_results": validation_results,
                "errors": errors,
                "execution_mode": execution_mode or self.execution_mode
            }

        except Exception as e:
            return {
                "error": f"Car creation workflow failed: {str(e)}",
                "workflow_status": "error",
                "vin": vin,
                "make": make,
                "model": model
            }

    def _build_component_request(self, requirements: Dict[str, Any]) -> str:
        """Build a car creation request prompt."""
        return get_car_creation_task_prompt(
            task_description="Create complete car JSON with all components",
            vin=requirements.get("vin", ""),
            year=requirements.get("year", ""),
            make=requirements.get("make", ""),
            model=requirements.get("model", ""),
            preferred_style=requirements.get("preferred_style", "sedan"),
            engine_type=requirements.get("engine_type", "gasoline"),
            execution_mode=self.execution_mode,
            current_phase="initialization"
        )

    def _validate_component_data(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the complete car JSON."""
        # This would implement full car.json schema validation
        return {
            "validation_status": "passed",
            "car_json": component_data,
            "agent": self.name
        }

    def _process_handoff_data(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handoff data (supervisor typically doesn't receive handoffs)."""
        return {
            "processed": True,
            "note": "Supervisor agent coordinates handoffs between other agents"
        }