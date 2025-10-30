# Quick Start: Interactive User Querying

## TL;DR

The LLM can now ask you questions during car creation!

When the LLM needs clarification, it responds with:
```json
{ "user_question": "What color would you like?" }
```

The system detects this, prompts you for an answer, and continues the configuration.

## How to Use

### 1. Start Interactive Session

```bash
cd src/lclg/single-agent-create-car-looping
python cli.py interactive --model llama3.2
```

### 2. Provide Your Request

```
[Iteration 1] Your request: I want a sports car
```

### 3. Answer Questions

```
🤔 Agent Question: What color would you like for the car's exterior?
Your answer: red

🤔 Agent Question: Do you prefer manual or automatic transmission?
Your answer: automatic
```

### 4. Get Your Configuration

```
✅ Car configuration created successfully!

📋 Vehicle Information:
  - type: sports car
  - color: red
  - transmission: automatic
  ...
```

## Commands

During the session:

- **Type your requirements** - Natural language input
- **Answer questions** - When agent asks for clarification
- **`skip`** - Skip a question and use defaults
- **`status`** - View accumulated context and Q&A history
- **`reset`** - Clear context and start fresh
- **`save <filename>`** - Save current configuration
- **`quit`** or **`exit`** - End session

## LLM Instructions

If you're implementing a custom agent, instruct your LLM:

```
To ask the user a question, respond ONLY with:
{ "user_question": "Your question here?" }

Do NOT mix this with other JSON data.
After receiving the answer, it will be available in the context.
```

## Code Example

### Extract Questions in Your Agent

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    # ... your agent code ...

    def process_request(self, user_input):
        # Invoke LLM
        result = self.invoke_llm(requirements)

        # Check for questions
        if result.get("requires_user_input"):
            question = result["user_question"]
            # Display to user and get answer
            answer = input(f"{question}\nYour answer: ")
            # Continue with answer...
```

### Detect Questions in LLM Response

```python
# The method is already in BaseAgent
question = self._extract_question_json_from_response(llm_response)

if question:
    # Handle the question
    print(f"LLM asks: {question}")
else:
    # Process normal response
    pass
```

## Files to Reference

- **INTERACTIVE_FEATURE.md** - Full documentation
- **REFACTORING_SUMMARY.md** - Technical details of changes
- **tests/unit/test_interactive_feature.py** - Test examples
- **src/agents/base_agent.py:505** - Question extraction method
- **src/single_agent_system.py:133** - Q&A loop implementation

## Troubleshooting

### Questions Not Detected?

1. Check LLM response format: `{"user_question": "text"}`
2. Enable debug logging: `--log-llm-comms`
3. Verify JSON is valid (no trailing commas, proper quotes)

### Too Many Questions?

1. Type `skip` to use defaults
2. Provide more detailed initial requirements
3. Adjust system prompt to limit questions

### Answers Not Remembered?

1. Use `status` command to check context
2. Verify answers are being stored in memory
3. Don't use `reset` unless you want to clear context

## Best Practices

### For Users

- Provide detailed initial requirements to minimize questions
- Answer questions clearly and specifically
- Use `skip` sparingly - answers improve configuration quality

### For Developers

- Ask questions only when necessary
- Make questions specific and actionable
- Store Q&A in context for future reference
- Limit number of questions per session

## Example Sessions

### Example 1: Minimal Input

```
Request: I want a car
Question: What type of vehicle? (sedan, SUV, truck)
Answer: SUV
Question: What's your budget range?
Answer: $40,000
Question: Fuel preference? (gasoline, electric, hybrid)
Answer: hybrid
Result: Hybrid SUV configured with $40k budget
```

### Example 2: Detailed Input

```
Request: I want a red sports coupe with manual transmission and high performance
(No questions needed - all details provided)
Result: Sports coupe configured exactly as specified
```

### Example 3: Using Skip

```
Question: What color for the interior?
Answer: skip
Result: Uses default interior color (continues configuration)
```

## Running Tests

To test the interactive feature extraction method:

```bash
cd src/lclg/single-agent-create-car-looping
python tests/unit/test_interactive_feature.py
```

Or run all tests:

```bash
pytest tests/unit/test_interactive_feature.py
```

## What's Next?

1. Try the interactive session
2. Experiment with vague vs detailed requirements
3. Check the accumulated context with `status`
4. Save your favorite configurations
5. Review INTERACTIVE_FEATURE.md for advanced usage

## Quick Reference

| Feature | Command/Format |
|---------|----------------|
| Ask question | `{"user_question": "..."}` |
| Answer question | Type your answer |
| Skip question | `skip` |
| View context | `status` |
| Clear context | `reset` |
| Save config | `save <file>` |
| Exit | `quit` or `exit` |

---

**Ready to start?**

```bash
python cli.py interactive
```

Happy car building! 🚗
