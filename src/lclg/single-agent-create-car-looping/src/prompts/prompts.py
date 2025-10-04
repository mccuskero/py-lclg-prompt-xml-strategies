"""Prompt templates for the car creation system using LangChain prompt templates."""

from typing import Any, Dict
from langchain_core.prompts import PromptTemplate


# System prompt template for CarAgent (LangChain agent pattern)
# Note: {input} placeholder is required for LangChain agent framework
# Note: {tools} placeholder is auto-populated by create_agent
CAR_AGENT_SYSTEM_PROMPT = PromptTemplate.from_template(
    """You are a comprehensive car creation agent with access to all the tools needed to design and configure a complete vehicle.

Your capabilities include:
- Engine configuration and specifications (gasoline, diesel, electric, hybrid)
- Body design and customization (exterior, interior, styling)
- Electrical system setup (battery, charging, lighting, wiring)
- Tire and wheel configuration (performance, size, design)

Available Tools:
{tools}

When creating a car:
1. Start by understanding the requirements (vehicle type, performance level, budget, preferences)
2. Use the engine tools to select and configure the appropriate engine
3. Use the body tools to design the exterior and interior
4. Use the electrical tools to set up the electrical systems (especially important for electric/hybrid vehicles)
5. Use the tire tools to select appropriate tires and wheels
6. Ensure all components are compatible and integrated properly

CRITICAL JSON FORMATTING RULES:
- You MUST respond with ONLY valid JSON
- Do not include any explanatory text, markdown formatting, or additional commentary
- Start your response with {{ and end with }}
- ALL values must be properly quoted strings (e.g., "2.5L", "180 HP", "silver")
- NO unquoted numbers with units
- ALL field names must be in double quotes
- Use proper JSON syntax with commas and colons
- NO trailing commas

Always provide detailed JSON responses with all component specifications.
Consider dependencies between components (e.g., engine type affects electrical requirements, vehicle type affects tire selection).

Current task: {input}
"""
)


# Human prompt template for component requests with context (used in car_agent.py)
CAR_AGENT_HUMAN_PROMPT = PromptTemplate.from_template(
    """Create a complete car configuration based on these requirements:

Requirements:
{requirements}

Context from Previous Interactions:
{context}

Please use the available tools to:

1. Configure the engine system appropriate for the vehicle type and performance level
2. Design the body (exterior and interior) suitable for the vehicle type and budget
3. Set up the electrical system compatible with the engine choice
4. Select tires and wheels appropriate for the vehicle and performance requirements

Ensure all components are compatible and integrated. Return a comprehensive JSON response with all component specifications in this format:

{{
  "car_configuration": {{
    "vehicle_info": {{
      "type": "string",
      "performance_level": "string",
      "fuel_preference": "string",
      "budget": "string"
    }},
    "engine": {{
      "displacement": "string",
      "cylinders": "string",
      "fuelType": "string",
      "horsepower": "string",
      "@engineCode": "string",
      "@manufacturer": "string"
    }},
    "body": {{
      "exterior": {{
        "style": "string",
        "color": "string",
        "doors": number,
        "material": "string"
      }},
      "interior": {{
        "seating": "string",
        "upholstery": "string",
        "dashboard": "string"
      }}
    }},
    "electrical": {{
      "main_system": {{
        "voltage_system": "string",
        "battery_capacity": "string"
      }},
      "battery": {{
        "voltage": "string",
        "capacity": "string"
      }},
      "lighting": {{
        "headlights": "string",
        "taillights": "string"
      }}
    }},
    "tires_and_wheels": {{
      "tires": {{
        "brand": "string",
        "size": "string",
        "pressure": "string"
      }},
      "wheels": {{
        "size": "string",
        "material": "string",
        "design": "string"
      }}
    }},
    "integration_notes": {{
      "compatibility": "string",
      "notes": "string"
    }}
  }}
}}

Use the tools in sequence and ensure compatibility between all components.
RESPOND ONLY WITH VALID JSON - NO ADDITIONAL TEXT.
"""
)


# Interactive session prompt template
INTERACTIVE_SESSION_PROMPT = PromptTemplate.from_template(
    """Interactive Car Creation Session

Current Context:
{context}

User Request:
{user_input}

Based on the accumulated context and the current request, determine what action to take:
1. If you need to call a tool, provide the tool name and parameters
2. If you need more information from the user, ask a specific question
3. If the task is complete, provide the final result

Respond in JSON format:
{{
  "action": "tool_call" | "user_input" | "complete",
  "tool_name": "string (if action is tool_call)",
  "tool_params": {{}},
  "question": "string (if action is user_input)",
  "result": {{}} (if action is complete)
}}
"""
)


# User input follow-up prompt template
USER_FOLLOWUP_PROMPT = PromptTemplate.from_template(
    """Continue with car configuration.

Previous Context:
{context}

Previous Question: {previous_question}
User Answer: {user_answer}

Update the car configuration based on the user's answer and continue with the next step.
"""
)


def get_car_agent_system_prompt(tools_list: str) -> str:
    """Get the formatted system prompt for the car agent."""
    return CAR_AGENT_SYSTEM_PROMPT.format(tools=tools_list)


def get_car_agent_request_prompt(requirements: Dict[str, Any], context: str = "") -> str:
    """Get the formatted request prompt for the car agent."""
    # Format requirements as a readable string
    requirements_str = "\n".join([f"- {k}: {v}" for k, v in requirements.items()])

    return CAR_AGENT_REQUEST_PROMPT.format(
        requirements=requirements_str,
        context=context if context else "No previous context."
    )


def get_interactive_session_prompt(context: str, user_input: str) -> str:
    """Get the formatted interactive session prompt."""
    return INTERACTIVE_SESSION_PROMPT.format(
        context=context,
        user_input=user_input
    )


def get_user_followup_prompt(context: str, previous_question: str, user_answer: str) -> str:
    """Get the formatted user follow-up prompt."""
    return USER_FOLLOWUP_PROMPT.format(
        context=context,
        previous_question=previous_question,
        user_answer=user_answer
    )
