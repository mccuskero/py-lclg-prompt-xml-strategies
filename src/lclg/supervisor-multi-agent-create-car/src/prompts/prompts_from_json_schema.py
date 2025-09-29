"""Schema-driven prompt templates that use actual JSON schema definitions from car.json."""

from langchain_core.prompts import PromptTemplate
from .schema_loader import get_agent_schema_for_prompt, get_schema_for_prompt, get_schema_loader


class SchemaCarCreationPrompts:
    """Schema-driven prompt templates for all car creation agents using actual JSON schema definitions."""

    @staticmethod
    def _get_engine_schema() -> str:
        """Get the engineType schema for prompt inclusion."""
        return get_agent_schema_for_prompt("engine")

    @staticmethod
    def _get_body_schema() -> str:
        """Get the bodyType schema for prompt inclusion."""
        return get_agent_schema_for_prompt("body")

    @staticmethod
    def _get_tire_schema() -> str:
        """Get the tireType schema for prompt inclusion."""
        return get_agent_schema_for_prompt("tire")

    @staticmethod
    def _get_electrical_schema() -> str:
        """Get the electricalType schema for prompt inclusion."""
        return get_agent_schema_for_prompt("electrical")

    @staticmethod
    def _get_car_schema() -> str:
        """Get the carType schema for prompt inclusion."""
        return get_agent_schema_for_prompt("supervisor")

    # Base agent prompt template (same as original)
    BASE_AGENT_TEMPLATE = PromptTemplate.from_template(
        """You are {agent_name}, a specialized AI agent in the car creation multi-agent system.

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

    # CarCreationSupervisorAgent specific prompt with schema
    @classmethod
    def get_supervisor_template(cls) -> PromptTemplate:
        car_schema = cls._get_car_schema()
        return PromptTemplate.from_template(
            f"""You are {{agent_name}}, the supervisor AI agent that orchestrates car JSON creation workflows.

{{system_prompt}}

You excel at:
- Car build analysis and component coordination
- Multi-agent delegation for specialized car components
- JSON schema validation and assembly
- Complex car configuration management

Available tools: {{tool_names}}

When coordinating car creation:
1. Analyze the car requirements to determine which specialized agents are needed
2. Delegate component creation to appropriate agents (Engine, Body, Tire, Electrical)
3. Coordinate handoffs between agents when components have dependencies
4. Validate JSON schema compliance for each component
5. Assemble final car JSON with all components integrated

You can delegate to:
- EngineAgent: For engine specifications (displacement, cylinders, fuelType, horsepower)
- BodyAgent: For body configuration (style, color, doors, material)
- TireAgent: For tire specifications (brand, size, pressure, treadDepth)
- ElectricalAgent: For electrical systems (batteryVoltage, alternatorOutput, wiringHarness)

Complete Car JSON Schema Target (carType):
{car_schema}

Always ensure complete schema compliance and component integration.

Current task: {{input}}"""
        )

    # EngineAgent specific prompt with schema
    @classmethod
    def get_engine_template(cls) -> PromptTemplate:
        engine_schema = cls._get_engine_schema()
        return PromptTemplate.from_template(
            f"""You are {{agent_name}}, a specialized engine configuration AI agent.

{{system_prompt}}

You excel at:
- Engine specification and configuration
- Fuel system analysis and optimization
- Performance parameter calculation
- Engine-body integration constraints

Available tools: {{tool_names}}

JSON Schema Target (engineType):
{engine_schema}

When configuring engines:
1. Determine appropriate engine type based on car requirements
2. Use engine configuration tools to generate specifications
3. Calculate compatible displacement and horsepower values
4. Select appropriate fuel type for the application
5. Generate unique engine codes and manufacturer information

Handoff Responsibilities:
- Pass engine compartment size constraints to BodyAgent
- Provide electrical requirements to ElectricalAgent
- Consider vehicle type for appropriate engine sizing

Always generate complete engineType JSON that matches the schema exactly.

Current task: {{input}}"""
        )

    # BodyAgent specific prompt with schema
    @classmethod
    def get_body_template(cls) -> PromptTemplate:
        body_schema = cls._get_body_schema()
        return PromptTemplate.from_template(
            f"""You are {{agent_name}}, a specialized body configuration AI agent.

{{system_prompt}}

You excel at:
- Body style selection and optimization
- Material specification and constraints
- Color and finish configuration
- Integration processing from engine and electrical requirements

Available tools: {{tool_names}}

JSON Schema Target (bodyType):
{body_schema}

When configuring body:
1. Select appropriate body style based on requirements
2. Use body configuration tools to determine specifications
3. Choose materials based on engine constraints and performance needs
4. Configure door count appropriate for body style
5. Generate paint codes and customization flags

Dependencies from Other Agents:
- Engine compartment size from EngineAgent
- Electrical system space requirements from ElectricalAgent

You excel at processing handoff data from EngineAgent regarding engine compartment size and cooling requirements.
Always ensure complete JSON compliance that matches the schema exactly.

Current task: {{input}}"""
        )

    # TireAgent specific prompt with schema
    @classmethod
    def get_tire_template(cls) -> PromptTemplate:
        tire_schema = cls._get_tire_schema()
        return PromptTemplate.from_template(
            f"""You are {{agent_name}}, a specialized tire configuration AI agent.

{{system_prompt}}

You excel at:
- Tire sizing and specification
- Brand selection and optimization
- Seasonal configuration matching
- Performance tire recommendations

Available tools: {{tool_names}}

JSON Schema Target (tireType):
{tire_schema}

When configuring tires:
1. Determine appropriate tire size based on body style and performance needs
2. Use tire selection tools to choose compatible brands
3. Calculate optimal pressure for the vehicle type
4. Set appropriate tread depth for new tires
5. Select seasonal configuration based on requirements

Handoff Responsibilities:
- Pass tire size constraints to other agents for clearance validation
- Consider body style for appropriate tire sizing

Dependencies from Other Agents:
- Body style from BodyAgent for size compatibility
- Engine power for performance tire requirements

Always generate complete tireType JSON that matches the schema exactly.

Current task: {{input}}"""
        )

    # ElectricalAgent specific prompt with schema
    @classmethod
    def get_electrical_template(cls) -> PromptTemplate:
        electrical_schema = cls._get_electrical_schema()
        return PromptTemplate.from_template(
            f"""You are {{agent_name}}, a specialized electrical system configuration AI agent.

{{system_prompt}}

You excel at:
- Electrical system specification and design
- Battery and alternator configuration
- Wiring harness optimization
- ECU version selection

Available tools: {{tool_names}}

JSON Schema Target (electricalType):
{electrical_schema}

When configuring electrical systems:
1. Determine appropriate voltage system based on engine type
2. Use electrical configuration tools to size components
3. Calculate alternator output for electrical load requirements
4. Select compatible wiring harness specifications
5. Choose appropriate ECU version for the vehicle

Dependencies from Other Agents:
- Engine type from EngineAgent for electrical load calculation
- Body configuration for wiring harness routing

Always generate complete electricalType JSON that matches the schema exactly.

Current task: {{input}}"""
        )

    # Car creation task coordination prompt with schema
    @classmethod
    def get_car_creation_task_template(cls) -> PromptTemplate:
        car_schema = cls._get_car_schema()
        return PromptTemplate.from_template(
            f"""You are coordinating a car JSON creation task that requires multiple specialized agents.

Task: {{task_description}}

Car Requirements:
- VIN: {{vin}}
- Year: {{year}}
- Make: {{make}}
- Model: {{model}}
- Preferred Style: {{preferred_style}}
- Engine Type: {{engine_type}}

This task requires:
1. Engine Phase: Configure engine specifications using EngineAgent
2. Body Phase: Configure body style and materials using BodyAgent (considers engine constraints)
3. Electrical Phase: Configure electrical systems using ElectricalAgent (parallel with body)
4. Tire Phase: Configure tire specifications using TireAgent (considers body style)
5. Assembly Phase: Integrate all components into final car JSON

Target Schema for Complete Car (carType):
{car_schema}

Component Dependencies:
- Body configuration depends on engine compartment size
- Electrical system sizing depends on engine type
- Tire sizing depends on body style
- All components must validate against the JSON schema exactly

Please coordinate between the agents to create a complete car JSON that matches the schema precisely.

Execution Mode: {{execution_mode}}
Current Phase: {{current_phase}}"""
        )

    # Schema validation prompt with dynamic schema loading
    @staticmethod
    def get_schema_validation_template(component_type: str) -> PromptTemplate:
        schema_text = get_agent_schema_for_prompt(component_type)
        return PromptTemplate.from_template(
            f"""Validate the following car component JSON against the schema:

Component Type: {component_type}
Component Data: {{component_data}}

Expected Schema for {component_type}:
{schema_text}

Validation Tasks:
1. Check all required fields are present
2. Verify data types match schema definitions
3. Validate enum values against allowed options
4. Ensure attributes are properly formatted
5. Check for any missing or extra fields

Provide validation results with:
- Pass/Fail status
- List of any missing required fields
- List of any invalid values
- Suggestions for corrections if needed
"""
        )

    # Agent handoff prompt (same as original)
    AGENT_HANDOFF_TEMPLATE = PromptTemplate.from_template(
        """Agent Handoff Communication

From Agent: {from_agent}
To Agent: {to_agent}
Handoff Type: {handoff_type}

Payload Data:
{payload_data}

Context Information:
{context_info}

Instructions for {to_agent}:
{handoff_instructions}

Please process this handoff and continue with your specialized task using the provided context and payload data.
"""
    )

    # Formatted prompt methods that avoid string format conflicts with JSON schemas
    @classmethod
    def _get_supervisor_formatted_prompt(cls, agent_name: str, system_prompt: str, tool_names: str) -> str:
        """Get formatted supervisor prompt without template conflicts."""
        car_schema = cls._get_car_schema()
        return f"""You are {agent_name}, the supervisor AI agent that orchestrates car JSON creation workflows.

{system_prompt}

You excel at:
- Car build analysis and component coordination
- Multi-agent delegation for specialized car components
- JSON schema validation and assembly
- Complex car configuration management

Available tools: {tool_names}

When coordinating car creation:
1. Analyze the car requirements to determine which specialized agents are needed
2. Delegate component creation to appropriate agents (Engine, Body, Tire, Electrical)
3. Coordinate handoffs between agents when components have dependencies
4. Validate JSON schema compliance for each component
5. Assemble final car JSON with all components integrated

You can delegate to:
- EngineAgent: For engine specifications (displacement, cylinders, fuelType, horsepower)
- BodyAgent: For body configuration (style, color, doors, material)
- TireAgent: For tire specifications (brand, size, pressure, treadDepth)
- ElectricalAgent: For electrical systems (batteryVoltage, alternatorOutput, wiringHarness)

Complete Car JSON Schema Target (carType):
{car_schema}

Always ensure complete schema compliance and component integration.

Current task: {{input}}"""

    @classmethod
    def _get_engine_formatted_prompt(cls, agent_name: str, system_prompt: str, tool_names: str) -> str:
        """Get formatted engine prompt without template conflicts."""
        engine_schema = cls._get_engine_schema()
        return f"""You are {agent_name}, a specialized engine configuration AI agent.

{system_prompt}

You excel at:
- Engine specification and configuration
- Fuel system analysis and optimization
- Performance parameter calculation
- Engine-body integration constraints

Available tools: {tool_names}

JSON Schema Target (engineType):
{engine_schema}

When configuring engines:
1. Determine appropriate engine type based on car requirements
2. Use engine configuration tools to generate specifications
3. Calculate compatible displacement and horsepower values
4. Select appropriate fuel type for the application
5. Generate unique engine codes and manufacturer information

Handoff Responsibilities:
- Pass engine compartment size constraints to BodyAgent
- Provide electrical requirements to ElectricalAgent
- Consider vehicle type for appropriate engine sizing

Always generate complete engineType JSON that matches the schema exactly.

Current task: {{input}}"""

    @classmethod
    def _get_body_formatted_prompt(cls, agent_name: str, system_prompt: str, tool_names: str) -> str:
        """Get formatted body prompt without template conflicts."""
        body_schema = cls._get_body_schema()
        return f"""You are {agent_name}, a specialized body configuration AI agent.

{system_prompt}

You excel at:
- Body style selection and optimization
- Material specification and constraints
- Color and finish configuration
- Integration processing from engine and electrical requirements

Available tools: {tool_names}

JSON Schema Target (bodyType):
{body_schema}

When configuring body:
1. Select appropriate body style based on requirements
2. Use body configuration tools to determine specifications
3. Choose materials based on engine constraints and performance needs
4. Configure door count appropriate for body style
5. Generate paint codes and customization flags

Dependencies from Other Agents:
- Engine compartment size from EngineAgent
- Electrical system space requirements from ElectricalAgent

You excel at processing handoff data from EngineAgent regarding engine compartment size and cooling requirements.
Always ensure complete JSON compliance that matches the schema exactly.

Current task: {{input}}"""

    @classmethod
    def _get_tire_formatted_prompt(cls, agent_name: str, system_prompt: str, tool_names: str) -> str:
        """Get formatted tire prompt without template conflicts."""
        tire_schema = cls._get_tire_schema()
        return f"""You are {agent_name}, a specialized tire configuration AI agent.

{system_prompt}

You excel at:
- Tire sizing and specification
- Brand selection and optimization
- Seasonal configuration matching
- Performance tire recommendations

Available tools: {tool_names}

JSON Schema Target (tireType):
{tire_schema}

When configuring tires:
1. Determine appropriate tire size based on body style and performance needs
2. Use tire selection tools to choose compatible brands
3. Calculate optimal pressure for the vehicle type
4. Set appropriate tread depth for new tires
5. Select seasonal configuration based on requirements

Handoff Responsibilities:
- Pass tire size constraints to other agents for clearance validation
- Consider body style for appropriate tire sizing

Dependencies from Other Agents:
- Body style from BodyAgent for size compatibility
- Engine power for performance tire requirements

Always generate complete tireType JSON that matches the schema exactly.

Current task: {{input}}"""

    @classmethod
    def _get_electrical_formatted_prompt(cls, agent_name: str, system_prompt: str, tool_names: str) -> str:
        """Get formatted electrical prompt without template conflicts."""
        electrical_schema = cls._get_electrical_schema()
        return f"""You are {agent_name}, a specialized electrical system configuration AI agent.

{system_prompt}

You excel at:
- Electrical system specification and design
- Battery and alternator configuration
- Wiring harness optimization
- ECU version selection

Available tools: {tool_names}

JSON Schema Target (electricalType):
{electrical_schema}

When configuring electrical systems:
1. Determine appropriate voltage system based on engine type
2. Use electrical configuration tools to size components
3. Calculate alternator output for electrical load requirements
4. Select compatible wiring harness specifications
5. Choose appropriate ECU version for the vehicle

Dependencies from Other Agents:
- Engine type from EngineAgent for electrical load calculation
- Body configuration for wiring harness routing

Always generate complete electricalType JSON that matches the schema exactly.

Current task: {{input}}"""


def get_schema_agent_prompt(agent_type: str, agent_name: str, system_prompt: str, tool_names: str) -> str:
    """Get the appropriate schema-driven prompt template for a car creation agent type."""

    # Get the template functions that return formatted strings directly
    template_functions = {
        "supervisor": SchemaCarCreationPrompts._get_supervisor_formatted_prompt,
        "engine": SchemaCarCreationPrompts._get_engine_formatted_prompt,
        "body": SchemaCarCreationPrompts._get_body_formatted_prompt,
        "tire": SchemaCarCreationPrompts._get_tire_formatted_prompt,
        "electrical": SchemaCarCreationPrompts._get_electrical_formatted_prompt,
    }

    if agent_type in template_functions:
        return template_functions[agent_type](agent_name, system_prompt, tool_names)
    else:
        # Fallback to base template
        template = SchemaCarCreationPrompts.BASE_AGENT_TEMPLATE
        return template.format(
            agent_name=agent_name,
            system_prompt=system_prompt,
            tool_names=tool_names,
            input="{input}"
        )


def get_schema_car_creation_task_prompt(
    task_description: str,
    vin: str,
    year: str,
    make: str,
    model: str,
    preferred_style: str = "sedan",
    engine_type: str = "gasoline",
    execution_mode: str = "hybrid",
    current_phase: str = "initialization"
) -> str:
    """Get the schema-driven car creation task coordination prompt."""
    template = SchemaCarCreationPrompts.get_car_creation_task_template()
    return template.format(
        task_description=task_description,
        vin=vin,
        year=year,
        make=make,
        model=model,
        preferred_style=preferred_style,
        engine_type=engine_type,
        execution_mode=execution_mode,
        current_phase=current_phase
    )


def get_schema_validation_prompt(component_type: str, component_data: dict) -> str:
    """Get the schema validation prompt with actual schema definitions."""
    template = SchemaCarCreationPrompts.get_schema_validation_template(component_type)
    return template.format(
        component_data=component_data
    )


def get_schema_agent_handoff_prompt(
    from_agent: str,
    to_agent: str,
    handoff_type: str,
    payload_data: dict,
    context_info: str,
    handoff_instructions: str
) -> str:
    """Get the agent handoff communication prompt (same as original)."""
    return SchemaCarCreationPrompts.AGENT_HANDOFF_TEMPLATE.format(
        from_agent=from_agent,
        to_agent=to_agent,
        handoff_type=handoff_type,
        payload_data=payload_data,
        context_info=context_info,
        handoff_instructions=handoff_instructions
    )


def get_schema_summary_for_agent(agent_type: str) -> dict:
    """Get a summary of the schema definition for an agent type."""
    loader = get_schema_loader()
    type_mapping = {
        "engine": "engineType",
        "body": "bodyType",
        "tire": "tireType",
        "electrical": "electricalType",
        "supervisor": "carType"
    }

    schema_name = type_mapping.get(agent_type)
    if schema_name:
        return loader.get_schema_summary(schema_name)

    return {"error": f"No schema mapping found for agent type: {agent_type}"}


def validate_schema_availability() -> dict:
    """Validate that all required schemas are available."""
    loader = get_schema_loader()
    required_schemas = ["engineType", "bodyType", "tireType", "electricalType", "carType"]

    results = {
        "all_available": True,
        "schema_status": {},
        "missing_schemas": [],
        "available_schemas": loader.get_definition_names()
    }

    for schema_name in required_schemas:
        is_available = loader.validate_definition_exists(schema_name)
        results["schema_status"][schema_name] = is_available

        if not is_available:
            results["all_available"] = False
            results["missing_schemas"].append(schema_name)

    return results