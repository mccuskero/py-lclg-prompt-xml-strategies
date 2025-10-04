# Dual Message System Documentation

This document explains how the single-agent-create-car-looping system uses both SystemMessage and HumanMessage when invoking the LLM.

## Overview

The system implements a dual-message pattern where every LLM invocation includes:
1. **SystemMessage**: Defines the agent's role, capabilities, and instructions
2. **HumanMessage**: Contains the specific request with requirements and context

## Implementation

### Location
The dual-message pattern is implemented in `src/agents/base_agent.py` in the `invoke_llm()` method.

### Code Flow

```python
def invoke_llm(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke the LLM with both system and human messages, including context memory.

    Args:
        requirements: The current request requirements

    Returns:
        Dict containing the response or error information
    """
    # 1. Format requirements as readable string
    requirements_str = "\n".join([f"- {k}: {v}" for k, v in requirements.items()])

    # 2. Build human message with context
    human_content = self.human_prompt_template.format(
        requirements=requirements_str,
        context=self.memory.get_context_summary()
    )

    # 3. Build system message with tools
    system_content = self.system_prompt_template.format(
        tools=self._format_tools_list()
    )

    # 4. Add to conversation memory
    self.memory.add_message("human", human_content)

    # 5. Configure generation parameters
    config = {
        "max_tokens": 1000,
        "temperature": 0.1,
        "format": "json",
    }

    # 6. Invoke LLM with BOTH messages
    response_message = self.llm.invoke(
        [
            SystemMessage(content=system_content),  # System role and capabilities
            HumanMessage(content=human_content)      # User request with context
        ],
        config=config
    )

    # 7. Process response
    response_content = response_message.content
    self.memory.add_message("assistant", response_content)
    component_data = self._extract_json_from_response(response_content)
    validated_data = self._validate_component_data(component_data)
    self._update_context_memory(requirements, validated_data)

    return validated_data
```

## Message Contents

### SystemMessage Content

Built from `CAR_AGENT_SYSTEM_PROMPT` template in `src/prompts/prompts.py`:

```
You are a comprehensive car creation agent with access to all the tools needed to design and configure a complete vehicle.

Your capabilities include:
- Engine configuration and specifications (gasoline, diesel, electric, hybrid)
- Body design and customization (exterior, interior, styling)
- Electrical system setup (battery, charging, lighting, wiring)
- Tire and wheel configuration (performance, size, design)

Available Tools:
- configure_engine: Configure engine specifications
- get_engine_specs: Get engine details
- configure_body: Configure body design
... (8 tools total)

When creating a car:
1. Start by understanding the requirements
2. Use the engine tools to configure the engine
3. Use the body tools to design exterior/interior
4. Use electrical tools for electrical systems
5. Use tire tools for tires and wheels
6. Ensure component compatibility

CRITICAL JSON FORMATTING RULES:
- MUST respond with ONLY valid JSON
- No explanatory text or markdown
- Start with { and end with }
- All values properly quoted
- Proper JSON syntax
```

### HumanMessage Content

Built from `CAR_AGENT_HUMAN_PROMPT` template in `src/prompts/prompts.py`:

```
Create a complete car configuration based on these requirements:

Requirements:
- vehicle_type: sedan
- performance_level: standard
- fuel_preference: gasoline
- budget: medium

Context from Previous Interactions:
Accumulated Context:
- req_vehicle_type: sedan
- configured_engine: True
- configured_body: False

Please use the available tools to:
1. Configure the engine system
2. Design the body (exterior and interior)
3. Set up the electrical system
4. Select tires and wheels

Ensure compatibility. Return JSON in this format:
{
  "car_configuration": {
    "vehicle_info": {...},
    "engine": {...},
    "body": {...},
    "electrical": {...},
    "tires_and_wheels": {...}
  }
}

RESPOND ONLY WITH VALID JSON - NO ADDITIONAL TEXT.
```

## Benefits of Dual-Message Pattern

### 1. Role Clarity
- **SystemMessage**: Establishes agent role and capabilities
- **HumanMessage**: Provides specific task and requirements
- Clear separation between "who you are" and "what to do"

### 2. Context Management
- SystemMessage remains consistent across invocations
- HumanMessage changes with each request
- Context accumulates in HumanMessage through memory

### 3. Tool Awareness
- Tools are dynamically listed in SystemMessage
- Agent always aware of available tools
- Format: `{tools}` placeholder filled with `_format_tools_list()`

### 4. Memory Integration
- Previous context passed in HumanMessage
- Growing context across iterations
- Format: `{context}` placeholder filled with `memory.get_context_summary()`

## LangChain Message Types

The system uses LangChain's core message types:

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# SystemMessage - Defines agent role
SystemMessage(content="You are a helpful assistant...")

# HumanMessage - User/system request
HumanMessage(content="Create a car with these specs...")

# AIMessage - Stored in memory (not used in invoke)
AIMessage(content="Response from LLM...")
```

## Message Order

The messages are sent in this order:
1. **SystemMessage** first - Establishes context
2. **HumanMessage** second - Provides specific request

This order is important for LLM comprehension.

## Configuration Parameters

```python
config = {
    "max_tokens": 1000,        # Maximum response length
    "temperature": 0.1,        # Low for consistent JSON output
    "format": "json",          # Force JSON format (OLLAMA specific)
}
```

## Example Invocation

### Input
```python
requirements = {
    "vehicle_type": "sedan",
    "performance_level": "standard",
    "fuel_preference": "gasoline",
    "budget": "medium"
}

result = agent.invoke_llm(requirements)
```

### Messages Sent to LLM
```python
[
    SystemMessage(content="You are a comprehensive car creation agent...Available Tools:\n- configure_engine...\n..."),
    HumanMessage(content="Create a complete car...Requirements:\n- vehicle_type: sedan\n...Context from Previous Interactions:\n...")
]
```

### Response Processing
1. LLM generates JSON response
2. Response stored in memory
3. JSON extracted and validated
4. Context memory updated
5. Validated data returned

## Memory Updates

After each invocation:

1. **Human message stored**:
   ```python
   self.memory.add_message("human", human_content)
   ```

2. **Assistant response stored**:
   ```python
   self.memory.add_message("assistant", response_content)
   ```

3. **Context data updated**:
   ```python
   self._update_context_memory(requirements, validated_data)
   ```

## Usage in CarAgent

The `CarAgent` class uses this through inheritance:

```python
class CarAgent(BaseAgent):
    def create_complete_car(self, requirements: Dict[str, Any]):
        # Uses BaseAgent.invoke_llm() with dual messages
        car_data = self.invoke_llm(requirements)
        return car_data
```

## Comparison with Original Pattern

### Original (from specification)
```python
# System message
system_message = AgentMessage(
    content=self._get_system_prompt(),
    sender="system",
    recipient=self.name
)

# Human message
human_message = AgentMessage(
    content=self._build_component_request(requirements),
    sender="user",
    recipient=self.name
)

# Invoke
response_message = self.llm.invoke(
    [
        HumanMessage(content=human_message.content),
        SystemMessage(content=system_message.content)
    ],
    config=config
)
```

### Current Implementation
```python
# Build messages directly from templates
system_content = self.system_prompt_template.format(tools=...)
human_content = self.human_prompt_template.format(requirements=..., context=...)

# Invoke with both messages
response_message = self.llm.invoke(
    [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content)
    ],
    config=config
)
```

**Key Improvements:**
- Uses LangChain PromptTemplates instead of string methods
- Integrates context memory automatically
- No need for intermediate AgentMessage objects
- Message order: SystemMessage first, HumanMessage second

## Testing

The dual-message pattern can be tested using mocks:

```python
def test_invoke_llm_uses_both_messages(mock_llm):
    agent = CarAgent(llm=mock_llm, enable_logging=False)

    requirements = {"vehicle_type": "sedan"}
    agent.invoke_llm(requirements)

    # Verify both messages sent
    call_args = mock_llm.invoke.call_args
    messages = call_args[0][0]

    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert "comprehensive car creation agent" in messages[0].content
    assert "sedan" in messages[1].content
```

## Troubleshooting

### Issue: LLM not following system instructions

**Solution**: Check that SystemMessage is first in the list:
```python
[
    SystemMessage(content=...),  # Must be first
    HumanMessage(content=...)    # Then human message
]
```

### Issue: Context not included in responses

**Solution**: Verify context is in HumanMessage:
```python
human_content = self.human_prompt_template.format(
    requirements=requirements_str,
    context=self.memory.get_context_summary()  # Must be included
)
```

### Issue: JSON format not enforced

**Solution**: Ensure config includes format parameter:
```python
config = {
    "format": "json",  # Required for OLLAMA
    ...
}
```

## References

- Base implementation: `src/agents/base_agent.py:117-190`
- System prompt: `src/prompts/prompts.py:8-41`
- Human prompt: `src/prompts/prompts.py:44-127`
- CarAgent usage: `src/agents/car_agent.py:194-220`
- Memory management: `src/agents/base_agent.py:26-52`
