# Interactive User Querying Feature

## Overview

The single-agent-create-car-looping project now supports **interactive user querying**, allowing the LLM to ask clarifying questions during the car creation process. This enables more personalized and accurate car configurations based on user preferences.

## How It Works

### 1. LLM Asks Questions

When the LLM needs additional information, it can respond with a special JSON format:

```json
{ "user_question": "What color would you like for the car's exterior?" }
```

### 2. User Provides Answers

The system detects the question, displays it to the user, and waits for their response. The answer is then stored in the conversation context and used to continue the car configuration process.

### 3. Context Management

All questions and answers are automatically stored in the agent's memory, allowing the LLM to reference them in subsequent interactions.

## Architecture

### Components Modified

1. **BaseAgent Class** (`src/agents/base_agent.py`)
   - Added `_extract_question_json_from_response()` method to detect user questions in LLM responses
   - Updated `invoke_llm()` to check for user_question and return it appropriately

2. **System Prompts** (`src/prompts/prompts.py`)
   - Updated `CAR_AGENT_SYSTEM_PROMPT` to instruct the LLM about the user_question format
   - Updated `CAR_AGENT_HUMAN_PROMPT` with examples of when to ask questions

3. **SingleAgentSystem** (`src/single_agent_system.py`)
   - Enhanced `_process_iteration()` to handle interactive Q&A loops
   - Added visual indicators for agent questions

## Usage Examples

### Running the Interactive Session

```bash
cd src/lclg/single-agent-create-car-looping
python cli.py interactive --model llama3.2
```

### Example Session Flow

```
[Iteration 1] Your request: I want a sports car

🤔 Agent Question: What color would you like for the car's exterior?
Your answer: red

🤔 Agent Question: Do you prefer manual or automatic transmission?
Your answer: automatic

✅ Car configuration created successfully!
```

### Programmatic Usage

```python
from single_agent_system import SingleAgentSystem

# Initialize the system
system = SingleAgentSystem(
    model_name="llama3.2",
    base_url="http://localhost:11434"
)

# Run interactive session
system.interactive_session()
```

## JSON Format Specification

### User Question Format

The LLM responds with:
```json
{
  "user_question": "Your specific question here?"
}
```

### Response Detection

The `_extract_question_json_from_response()` method supports multiple formats:

1. **Pure JSON**: `{ "user_question": "question" }`
2. **JSON blocks**: ` ```json\n{ "user_question": "question" }\n``` `
3. **Inline patterns**: `user_question: "question"`

### Context Storage

Questions and answers are stored as:
```python
{
  "question_1": "What color would you like?",
  "answer_1": "red",
  "question_2": "Manual or automatic?",
  "answer_2": "automatic"
}
```

## Implementation Details

### BaseAgent._extract_question_json_from_response()

```python
def _extract_question_json_from_response(self, response: str) -> Optional[str]:
    """
    Extract user_question JSON from LLM response.

    Returns:
        The question string if found, None otherwise
    """
    # 1. Try parsing entire response as JSON
    # 2. Search for user_question patterns
    # 3. Look in JSON code blocks
    # 4. Return question or None
```

### SingleAgentSystem._process_iteration()

```python
def _process_iteration(self, user_input: str) -> Dict[str, Any]:
    """
    Process iteration with Q&A support.

    Flow:
    1. Process user request through agent
    2. While result contains user_question:
       a. Display question to user
       b. Get user's answer
       c. Add Q&A to context
       d. Continue processing with answer
    3. Return final result
    """
```

## Best Practices

### When to Ask Questions

The LLM should ask questions when:
- Critical information is missing (color, specific features)
- Budget constraints are unclear
- Performance preferences are vague
- User requirements conflict

### When NOT to Ask

Avoid asking questions when:
- Reasonable defaults exist
- Information can be inferred from context
- Too many questions have already been asked
- User explicitly provided "skip" as an answer

### Question Quality

Good questions are:
- **Specific**: "What color?" vs "Tell me about preferences"
- **Relevant**: Directly related to car configuration
- **Clear**: Easy to understand and answer
- **Actionable**: Answers directly influence the configuration

## Testing

### Manual Testing

1. Start the interactive session
2. Provide vague requirements: "I want a car"
3. Observe if the agent asks clarifying questions
4. Answer the questions
5. Verify the final configuration reflects your answers

### Automated Testing

```python
# Test the extraction method directly
from agents.base_agent import BaseAgent

response = '{ "user_question": "What color do you prefer?" }'
question = agent._extract_question_json_from_response(response)
assert question == "What color do you prefer?"
```

## Troubleshooting

### Question Not Detected

- **Issue**: LLM asks a question but system doesn't detect it
- **Solution**: Check LLM response format in logs (`--log-llm-comms`)
- **Verify**: Ensure JSON format is exactly `{"user_question": "text"}`

### Infinite Question Loop

- **Issue**: Agent keeps asking questions without providing configuration
- **Solution**: Improve prompt instructions or use skip option
- **Workaround**: Type 'skip' to use defaults

### Context Not Preserved

- **Issue**: Agent doesn't remember previous answers
- **Solution**: Check memory context in logs
- **Debug**: Use 'status' command to view stored context

## Future Enhancements

Potential improvements:
1. Support for multiple-choice questions
2. Question priority/importance levels
3. Maximum questions per session limit
4. Question history export
5. Pre-configured question templates
6. Validation of user answers

## API Reference

### BaseAgent Methods

```python
def _extract_question_json_from_response(response: str) -> Optional[str]
    """Extract user_question from LLM response."""
```

### SingleAgentSystem Methods

```python
def _process_iteration(user_input: str) -> Dict[str, Any]
    """Process iteration with Q&A support."""
```

### Response Format

```python
{
    "user_question": str,           # The question to ask
    "requires_user_input": bool,    # Always True when user_question present
    "agent": str                     # Agent name
}
```

## Examples

### Example 1: Color Preference

**User**: "I want a luxury sedan"

**Agent**: `{ "user_question": "What color would you like for the exterior?" }`

**User**: "Deep blue"

**Agent**: Creates configuration with deep blue exterior

### Example 2: Performance vs Efficiency

**User**: "I need a family car"

**Agent**: `{ "user_question": "Do you prefer fuel efficiency or higher performance?" }`

**User**: "Fuel efficiency is more important"

**Agent**: Configures with economy engine and efficient components

### Example 3: Budget Clarification

**User**: "Create a car for me"

**Agent**: `{ "user_question": "What is your budget range for this vehicle?" }`

**User**: "$30,000 to $40,000"

**Agent**: Configures within the specified budget range

## Conclusion

The interactive querying feature enhances the car creation system by enabling dynamic, context-aware conversations between the user and the LLM. This results in more accurate and personalized car configurations that truly match user preferences.
