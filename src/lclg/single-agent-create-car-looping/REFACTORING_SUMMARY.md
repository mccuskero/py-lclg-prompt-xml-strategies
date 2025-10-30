# Refactoring Summary: Interactive User Querying Feature

## Overview

The single-agent-create-car-looping project has been successfully refactored to support interactive user querying. The LLM can now ask clarifying questions during the car creation process, enabling more personalized and accurate configurations.

## Requirements Implemented

✅ **Requirement 1**: LLM uses JSON format to query/prompt the user
- Format: `{ "user_question" : "LLM question goes here" }`

✅ **Requirement 2**: Created `_extract_question_json_from_response()` in BaseAgent class
- Location: `src/agents/base_agent.py:505`
- Supports multiple JSON formats and patterns

✅ **Requirement 3**: Response is used to display/prompt the user
- Implemented in `SingleAgentSystem._process_iteration()`
- Interactive loop continues until configuration is complete

## Files Modified

### 1. `src/agents/base_agent.py`

#### Added Method: `_extract_question_json_from_response()` (Line 505)

```python
def _extract_question_json_from_response(self, response: str) -> Optional[str]:
    """
    Extract user_question JSON from LLM response.

    Supports formats:
    - Pure JSON: { "user_question": "text" }
    - JSON blocks: ```json ... ```
    - Inline patterns: user_question: "text"

    Returns:
        The question string if found, None otherwise
    """
```

**Features**:
- Parses multiple JSON formats
- Uses regex patterns for flexible extraction
- Handles malformed JSON gracefully
- Logs extraction attempts and results
- Returns None if no question found

#### Modified Method: `invoke_llm()` (Line 334-348)

Added question detection logic:
```python
# Check if LLM is asking a question to the user
user_question = self._extract_question_json_from_response(response_content)

if user_question:
    # LLM needs more information from the user
    return {
        "user_question": user_question,
        "requires_user_input": True,
        "agent": self.name
    }
```

**Impact**:
- Intercepts user questions before JSON extraction
- Returns special response format for questions
- Prevents normal processing when question is detected

### 2. `src/prompts/prompts.py`

#### Updated: `CAR_AGENT_SYSTEM_PROMPT` (Line 10-58)

Added instructions for user questions:

```
2. **IMPORTANT**: If you need more information from the user to create
   the best car configuration, you can ask questions using this format:
   { "user_question": "Your question here?" }

   - Ask ONLY when critical information is missing
   - Keep questions clear, specific, and relevant
   - After receiving the user's answer, continue with car creation
```

Added formatting rules:

```
USER QUESTION FORMAT:
- To request information from the user, respond ONLY with:
  { "user_question": "Your question?" }
- Do NOT mix user_question with other JSON data
- After receiving the user's answer, you can access it in the context
```

#### Updated: `CAR_AGENT_HUMAN_PROMPT` (Line 62-88)

Added interactive feature section:

```
INTERACTIVE FEATURE:
If you need clarification or additional information from the user,
you can ask a question using:
{ "user_question": "Your specific question here?" }

For example:
- Color preference: { "user_question": "What color would you like?" }
- Budget clarification: { "user_question": "What is your target budget?" }
- Performance vs efficiency: { "user_question": "Do you prefer fuel efficiency or high performance?" }
```

### 3. `src/single_agent_system.py`

#### Modified: `interactive_session()` (Line 74-88)

Updated welcome message:

```python
print("\n✨ NEW: The agent can now ask you questions to better understand")
print("        your preferences and create a personalized car configuration!")
```

#### Enhanced: `_process_iteration()` (Line 133-205)

Implemented interactive Q&A loop:

```python
# Check if the LLM is asking a question to the user
while result.get("requires_user_input", False) and "user_question" in result:
    question = result["user_question"]

    # Display the question to the user
    print(f"\n🤔 Agent Question: {question}")

    # Get user's answer
    user_answer = input("Your answer: ").strip()

    # Handle skip option
    if user_answer.lower() == "skip":
        user_answer = "User chose to skip. Use reasonable defaults."

    # Add Q&A to context
    self.agent.memory.add_context(f"question_{iteration}", question)
    self.agent.memory.add_context(f"answer_{iteration}", user_answer)

    # Continue processing with the answer
    follow_up_input = f"Based on my previous answer: {user_answer}. Continue..."
    result = self.agent.process_user_request(follow_up_input)
```

**Features**:
- While loop handles multiple questions in sequence
- Visual indicators (🤔) for better UX
- Skip option for optional questions
- Stores Q&A in context for future reference
- Continues processing after each answer

## New Files Created

### 1. `INTERACTIVE_FEATURE.md`

Comprehensive documentation including:
- Overview and architecture
- Usage examples
- JSON format specification
- Implementation details
- Best practices
- Troubleshooting guide
- API reference
- Future enhancements

### 2. `tests/unit/test_interactive_feature.py`

Test suite demonstrating:
- `_extract_question_json_from_response()` test cases
- Integration flow simulation
- Example usage patterns
- Expected behaviors

### 3. `REFACTORING_SUMMARY.md`

This document - complete summary of all changes.

## Usage

### Starting an Interactive Session

```bash
cd src/lclg/single-agent-create-car-looping
python cli.py interactive --model llama3.2
```

### Example Interaction

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

system = SingleAgentSystem(model_name="llama3.2")
system.interactive_session()
```

## Technical Details

### Question Detection Flow

1. User submits request
2. LLM processes request
3. `invoke_llm()` receives response
4. `_extract_question_json_from_response()` checks for user_question
5. If found:
   - Return `{"user_question": "...", "requires_user_input": True}`
6. If not found:
   - Continue with normal JSON extraction and validation

### Context Management

Questions and answers are stored as:

```python
{
  "question_1": "What color would you like?",
  "answer_1": "red",
  "question_2": "Manual or automatic?",
  "answer_2": "automatic",
  ...
}
```

This allows:
- LLM to reference previous answers
- User to see accumulated context with 'status' command
- Configuration to be saved with full Q&A history

### Response Format

When user_question is detected:

```python
{
    "user_question": str,           # The question to ask
    "requires_user_input": bool,    # Always True
    "agent": str                     # Agent name
}
```

Normal response (no question):

```python
{
    "car_configuration": {
        "engine": {...},
        "body": {...},
        ...
    },
    "metadata": {...},
    "validation": {...}
}
```

## Benefits

1. **Personalization**: LLM can gather specific user preferences
2. **Accuracy**: Reduces guesswork and improper defaults
3. **Flexibility**: Handles vague or incomplete requirements
4. **User Experience**: More conversational and interactive
5. **Context Awareness**: Remembers all Q&A for better decisions

## Backwards Compatibility

✅ Fully backwards compatible:
- Existing code works without modification
- Questions are optional - LLM can choose not to ask
- Normal processing continues if no questions are detected
- All existing tests should pass

## Testing Recommendations

### Unit Tests

```python
# Test question extraction
def test_extract_question():
    response = '{ "user_question": "What color?" }'
    question = agent._extract_question_json_from_response(response)
    assert question == "What color?"
```

### Integration Tests

```python
# Test full Q&A flow
def test_qa_flow():
    system = SingleAgentSystem(...)
    # Simulate user input with questions
    # Verify answers are stored in context
    # Verify configuration reflects answers
```

### Manual Tests

1. Vague requirements → Verify questions asked
2. Complete requirements → Verify no questions needed
3. Skip functionality → Verify defaults used
4. Multiple questions → Verify sequential handling
5. Context preservation → Verify answers remembered

## Future Enhancements

Potential improvements identified:

1. **Multiple Choice Questions**
   - Format: `{"user_question": "...", "options": [...]}`
   - Allows constrained choices

2. **Question Priority**
   - Critical vs optional questions
   - Max questions limit per session

3. **Answer Validation**
   - Validate user responses before continuing
   - Request clarification if answer is unclear

4. **Question Templates**
   - Pre-configured common questions
   - Consistent phrasing across sessions

5. **Export Q&A History**
   - Save conversation transcripts
   - Analyze common questions for improvement

## Conclusion

The refactoring successfully implements interactive user querying in the single-agent-create-car-looping project. The implementation is:

- ✅ Clean and maintainable
- ✅ Well-documented
- ✅ Backwards compatible
- ✅ Extensible for future enhancements
- ✅ User-friendly with visual indicators

All three requirements have been met:
1. ✅ JSON format for user questions
2. ✅ `_extract_question_json_from_response()` method created
3. ✅ Response used to prompt user interactively

The feature is ready for use and testing!
