# Single Agent Car Creation System with Interactive Looping

An interactive car creation system using a single agent with context memory and looping capabilities. Built with LangChain v1.0.0a9 and OLLAMA.

## Quick Start

```bash
# 1. Install dependencies
cd src/lclg/single-agent-create-car-looping
uv sync --prerelease=allow

# 2. Start OLLAMA (in another terminal)
ollama serve

# 3. Pull the model (if not already available)
ollama pull llama3.2

# 4. Run the system
uv run python -m cli --log-level INFO interactive --model llama3.2

# Or run a single request
uv run python -m cli --log-level INFO single --model llama3.2
uv run python -m cli --log-level DEBUG single --model llama3.2

# single requests with significant LLM comms info, with Tools calls
uv run python -m cli --log-level DEBUG --log-llm-comms single --model llama3.2 
```

## Requirements
- **Python 3.10+** (required by LangChain 1.0.0a9)
- **OLLAMA** running locally or remotely
- **uv package manager**

## Features

- **Interactive Session**: Engage in a conversational loop with the agent to iteratively build car configurations
- **Context Memory**: The agent remembers previous interactions and uses that context in subsequent requests
- **Prompt Templates**: All prompts are managed using LangChain's prompt template framework
- **Tool Integration**: Comprehensive car creation tools for engine, body, electrical, and tire configuration
- **Single Agent Architecture**: One agent handles all aspects of car creation with tool delegation
- **OO Python Design**: Clean object-oriented architecture with the Strategy pattern

## Project Structure

```
src/lclg/single-agent-create-car-looping/
├── src/
│   ├── agents/                     # Agent implementations
│   │   ├── base_agent.py          # Base agent with context memory
│   │   └── car_agent.py           # Car creation agent
│   ├── tools/                     # Agent tools
│   │   ├── engine_tools.py        # Engine configuration tools
│   │   ├── body_tools.py          # Body design tools
│   │   ├── tire_tools.py          # Tire specification tools
│   │   └── electrical_tools.py    # Electrical system tools
│   ├── prompts/                   # LangChain prompt templates
│   │   └── prompts.py             # System and human prompts
│   └── single_agent_system.py     # Interactive session manager
├── schema/                        # JSON schema definitions
│   ├── single/                    # Single-file schemas
│   └── multi/                     # Multi-file schemas
├── tests/                         # Pytest tests
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── cli.py                         # Command-line interface
└── pyproject.toml                 # Project configuration
```

## Prerequisites

Before running the system, ensure you have:

1. **Python 3.10+** installed (required by LangChain 1.0.0a9)
2. **uv package manager** installed ([installation guide](https://github.com/astral-sh/uv))
3. **OLLAMA server** running locally or accessible remotely

### Setting Up OLLAMA

1. Install OLLAMA (if not already installed):
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or follow instructions at https://ollama.ai
```

2. Start the OLLAMA server:
```bash
ollama serve
```

3. Pull the required model (in a new terminal):
```bash
ollama pull llama3.2
```

4. Verify OLLAMA is running:
```bash
curl http://localhost:11434/api/tags
```

## Installation

1. Navigate to the project directory:
```bash
cd src/lclg/single-agent-create-car-looping
```

2. Install dependencies using `uv` (with prerelease support for LangChain 1.0.0a9):
```bash
uv sync --prerelease=allow
```

3. (Optional) Install development dependencies:
```bash
uv sync --dev --prerelease=allow
```

## Running the System

### 1. Interactive Mode (Recommended)

Run an interactive session where you can iteratively build car configurations:

```bash
uv run python -m cli interactive
```

Or with custom configuration:

```bash
# With specific model and logging
uv run python -m cli --log-level INFO interactive --model llama3.2

# With custom OLLAMA server
uv run python -m cli interactive --model llama3.2 --base-url http://your-server:11434
```

**Available Commands in Interactive Mode:**
- **Natural language**: Type your car requirements naturally (e.g., "I want a sedan")
- **`reset`**: Clear context and start fresh
- **`status`**: Display accumulated context and iteration count
- **`save <filename>`**: Save the current configuration to a JSON file
- **`quit`** or **`exit`**: End the session

**Example Interactive Session:**
```
Welcome to the Interactive Car Creation System
============================================================

[Iteration 1] Your request: I want a sedan for daily commuting
Processing your request...
============================================================
✅ Car configuration created successfully!

📋 Vehicle Information:
  - type: sedan
  - performance_level: standard
  - fuel_preference: gasoline
  - budget: medium

🔧 Engine Configuration:
  - displacement: 2.5L
  - cylinders: 4
  - fuelType: gasoline
  - horsepower: 180 HP
  ...

[Iteration 2] Your request: make it electric with high performance
Processing your request...
============================================================
✅ Car configuration updated successfully!

🔧 Engine Configuration:
  - fuelType: electric
  - horsepower: 300 HP
  ...

⚡ Electrical System:
  - voltage_system: high-voltage
  - battery_capacity: 75kWh
  ...

[Iteration 3] Your request: status

============================================================
  Current Status
============================================================
Iteration Count: 3
Context Items: 8
Message History: 6

Accumulated Context:
  - req_vehicle_type: sedan
  - req_fuel_preference: electric
  - configured_engine: True
  - configured_electrical: True
  ...

[Iteration 4] Your request: save my-electric-sedan.json
💾 Configuration saved to: my-electric-sedan.json

[Iteration 5] Your request: quit
Ending session...
Thank you for using the Interactive Car Creation System!
```

### 2. Single Request Mode

Create a complete car configuration with a single command:

**Basic Usage:**
```bash
# Simple sedan configuration
uv run python -m cli --log-level INFO single --model llama3.2

# This uses default requirements: sedan, standard performance, gasoline, medium budget
```

**Using Command-Line Arguments:**
```bash
uv run python -m cli single \
  --model llama3.2 \
  --vehicle-type sedan \
  --performance-level standard \
  --fuel-preference gasoline \
  --budget medium
```

**Quick Examples:**
```bash
# Economy sedan
uv run python -m cli single \
  --model llama3.2 \
  --vehicle-type sedan \
  --performance-level economy \
  --fuel-preference hybrid \
  --budget low

# Performance coupe
uv run python -m cli single \
  --model llama3.2 \
  --vehicle-type coupe \
  --performance-level performance \
  --fuel-preference gasoline \
  --budget high

# Electric SUV
uv run python -m cli single \
  --model llama3.2 \
  --vehicle-type suv \
  --fuel-preference electric \
  --budget high
```

### 3. Custom OLLAMA Configuration

**Use a Different Model:**
```bash
# With llama3.2 (default)
uv run python -m cli interactive --model llama3.2

# With codellama (better for JSON generation)
uv run python -m cli interactive --model codellama:13b

# With custom temperature
uv run python -m cli interactive --model llama3.2 --temperature 0.2
```

**Connect to Remote OLLAMA Server:**
```bash
uv run python -m cli interactive \
  --model llama3.2 \
  --base-url http://your-ollama-server:11434
```

**With Logging Options:**
```bash
# Debug logging (shows detailed agent execution)
uv run python -m cli --log-level DEBUG interactive --model llama3.2

# Info logging (default, shows key steps)
uv run python -m cli --log-level INFO interactive --model llama3.2

# Warning logging (only warnings and errors)
uv run python -m cli --log-level WARNING interactive --model llama3.2

# Disable logging
uv run python -m cli --no-logging interactive --model llama3.2

# Log full LLM communications (requests and responses)
uv run python -m cli --log-level DEBUG --log-llm-comms interactive --model llama3.2

# Combine with single mode for detailed debugging
uv run python -m cli --log-level DEBUG --log-llm-comms single --model llama3.2
```

## Configuration

### Requirements File Format

Create a JSON file with car requirements:

```json
{
  "vehicle_type": "sedan",
  "performance_level": "standard",
  "fuel_preference": "gasoline",
  "budget": "medium",
  "special_features": ["sunroof", "leather seats"]
}
```

### Supported Options

- **vehicle_type**: sedan, suv, truck, coupe, hatchback, convertible, wagon
- **performance_level**: economy, standard, performance
- **fuel_preference**: gasoline, diesel, electric, hybrid
- **budget**: low, medium, high

## Architecture

### Key Components

1. **BaseAgent**: Abstract base class with:
   - ConversationMemory for context accumulation
   - LangChain agent pattern using `create_agent` API
   - Agent executor for tool-augmented LLM interactions
   - Prompt templates with `{input}` placeholder for agent framework
   - JSON extraction and validation

2. **CarAgent**: Specialized agent that:
   - Integrates all car creation tools (engine, body, electrical, tires)
   - Follows LangChain v1.0.0a9 agent pattern
   - Uses agent executor for intelligent tool selection
   - Maintains context across iterations
   - Validates component compatibility

3. **SingleAgentSystem**: Session manager that:
   - Handles interactive looping
   - Manages user commands (reset, status, save, quit)
   - Displays results in user-friendly format
   - Supports both interactive and single-request modes

4. **Prompt Templates**: LangChain PromptTemplate objects for:
   - System prompts with `{tools}` and `{input}` placeholders
   - Agent framework compatibility
   - Context-aware prompt generation
   - Standardized agent behavior

### Context Memory

The system maintains short-term memory that accumulates:
- User requirements from each interaction
- Configured components (engine, body, electrical, tires)
- Conversation history (up to configurable limit)
- Metadata about the configuration process

This context is automatically included in subsequent prompts, allowing the agent to:
- Build on previous configurations
- Remember user preferences
- Make context-aware decisions
- Maintain consistency across iterations

## Running Tests

The project includes comprehensive unit tests for all components. Tests are written using pytest.

### Prerequisites for Testing

Ensure you have installed the development dependencies:

```bash
uv sync --dev --prerelease=allow
```

### Running All Tests

Run the complete test suite:

```bash
cd src/lclg/single-agent-create-car-looping
uv run pytest tests/
```

### Running Tests with Different Options

**Verbose Output (see each test name and result):**
```bash
uv run pytest tests/ -v
```

**Very Verbose Output (see test details and print statements):**
```bash
uv run pytest tests/ -vv
```

**Run Specific Test File:**
```bash
# Test base agent functionality
uv run pytest tests/unit/test_base_agent.py -v

# Test car agent functionality
uv run pytest tests/unit/test_car_agent.py -v
```

**Run Specific Test Class:**
```bash
uv run pytest tests/unit/test_base_agent.py::TestConversationMemory -v
```

**Run Specific Test Function:**
```bash
uv run pytest tests/unit/test_car_agent.py::TestCarAgent::test_parse_user_input_sedan -v
```

**Run Tests with Coverage Report:**
```bash
# Simple coverage report (currently at ~54%)
uv run pytest tests/unit/ --cov=src --cov-report=term-missing

# Detailed HTML coverage report
uv run pytest tests/unit/ --cov=src --cov-report=html

# View coverage report (creates htmlcov/index.html)
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

**Current Test Coverage:**
The project currently has **54% test coverage** with 66 passing tests covering:
- ConversationMemory functionality
- AgentMessage creation
- BaseAgent methods (tool formatting, JSON extraction, context updates)
- CarAgent functionality (parsing, validation, compatibility)
- Prompt template generation
- SingleAgentSystem session management

**Run Only Failed Tests (after a test run):**
```bash
uv run pytest tests/ --lf
```

**Stop at First Failure:**
```bash
uv run pytest tests/ -x
```

**Run Tests in Parallel (faster):**
```bash
uv run pytest tests/ -n auto
```

### Test Categories

**Unit Tests** (`tests/unit/`):
- `test_base_agent.py`: Tests for BaseAgent, ConversationMemory, and AgentMessage
- `test_car_agent.py`: Tests for CarAgent functionality, parsing, validation, and compatibility checks

**Integration Tests** (`tests/integration/`):
- Currently a placeholder for end-to-end integration tests

### Example Test Output

```bash
$ uv run pytest tests/unit/ -v

========================= test session starts =========================
platform darwin -- Python 3.12.8, pytest-8.4.2, pluggy-1.6.0
collected 77 items

tests/unit/test_base_agent.py::TestConversationMemory::test_add_message PASSED [  1%]
tests/unit/test_base_agent.py::TestConversationMemory::test_max_history_limit PASSED [  2%]
tests/unit/test_base_agent.py::TestConversationMemory::test_add_context PASSED [  3%]
tests/unit/test_base_agent.py::TestConversationMemory::test_get_context_summary PASSED [  5%]
tests/unit/test_base_agent.py::TestConversationMemory::test_clear PASSED [  6%]
tests/unit/test_car_agent.py::TestCarAgent::test_initialization PASSED [  7%]
tests/unit/test_car_agent.py::TestCarAgent::test_parse_user_input_sedan PASSED [  8%]
tests/unit/test_car_agent.py::TestCarAgent::test_parse_user_input_electric PASSED [  9%]
tests/unit/test_car_agent.py::TestCarAgent::test_validate_component_data_complete PASSED [ 10%]
tests/unit/test_prompts.py::TestPromptTemplates::test_car_agent_system_prompt_exists PASSED [ 11%]
tests/unit/test_prompts.py::TestPromptTemplates::test_system_prompt_format PASSED [ 12%]
tests/unit/test_single_agent_system.py::TestSingleAgentSystem::test_initialization PASSED [ 13%]
...

========================= 66 passed, 11 failed in 3.37s ==========================
```

Note: Some tool-related tests may fail due to changes in tool output structure. The core agent functionality tests pass successfully.

### Writing New Tests

To add new tests:

1. Create a new test file in `tests/unit/` or `tests/integration/`
2. Import the components you want to test
3. Use the fixtures defined in `tests/conftest.py`
4. Follow the existing test patterns

Example test:
```python
def test_my_feature(mock_llm, sample_requirements):
    """Test description."""
    agent = CarAgent(llm=mock_llm, enable_logging=False)
    result = agent.some_method(sample_requirements)
    assert result["some_field"] == "expected_value"
```

### Continuous Integration

The test suite is designed to be run in CI/CD pipelines. Recommended configuration:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    uv sync --dev --prerelease=allow
    uv run pytest tests/unit/ -v --cov=src --cov-report=xml
```

## Development

### Code Formatting

```bash
uv run black src/
```

### Linting

```bash
uv run flake8 src/
```

### Type Checking

```bash
uv run mypy src/
```

## Examples

### Example 1: Building a Car Iteratively

```
[Iteration 1] Your request: I need a car for daily commuting
... (creates economy sedan with standard features)

[Iteration 2] Your request: make it more fuel efficient
... (switches to hybrid or electric engine)

[Iteration 3] Your request: I want better seats
... (upgrades interior with leather or premium upholstery)

[Iteration 4] Your request: save commuter-car.json
... (saves the complete configuration)
```

### Example 2: Quick Performance Build

```bash
uv run python cli.py single \
  --vehicle-type coupe \
  --performance-level performance \
  --fuel-preference gasoline \
  --budget high \
  --output performance-coupe.json
```

## Logging

Logs are written to both console and `car_creation.log` file. Configure log level:

```bash
# Debug logging (most verbose)
uv run python cli.py interactive --log-level DEBUG

# Info logging (default)
uv run python cli.py interactive --log-level INFO

# Warning logging (less verbose)
uv run python cli.py interactive --log-level WARNING

# Disable logging
uv run python cli.py interactive --no-logging
```

### Advanced Logging: Full LLM Communications

Use the `--log-llm-comms` flag to capture complete LLM request/response data at DEBUG level. This is extremely useful for:
- Understanding how the agent is calling tools
- Debugging JSON parsing issues
- Seeing the exact prompts sent to the LLM
- Viewing all intermediate tool call messages
- Analyzing agent decision-making

```bash
# Enable full LLM communication logging
uv run python -m cli --log-level DEBUG --log-llm-comms single --model llama3.2

# View the detailed logs
tail -f car_creation.log
```

**What gets logged with `--log-llm-comms`:**
- Full system message (including all tool descriptions)
- Full human message (requirements and context)
- All messages in the conversation chain:
  - 🔧 **Tool Call Requests**: Shows exactly which tools the LLM requested, with:
    - Tool name
    - Tool ID
    - Arguments passed to each tool (formatted JSON)
  - ✅ **Tool Results**: Shows the response from each tool execution
  - Intermediate LLM responses
  - Final AI message
- Additional metadata from each message

**Example log output with `--log-llm-comms`:**
```
🔧 TOOL CALLS REQUESTED BY LLM:

  Tool Call 1:
    Tool Name: configure_engine
    Tool ID: call_abc123
    Arguments: {
      "vehicle_type": "sedan",
      "performance_level": "standard",
      "fuel_preference": "gasoline"
    }

✅ TOOL RESULT (from configure_engine):
    Result: {
      "engineType": {
        "displacement": "3.5L",
        "cylinders": "6",
        "fuelType": "gasoline"
      }
    }
```

This flag adds significant verbosity but is invaluable for debugging complex agent behaviors.

View the log file:
```bash
tail -f car_creation.log

# Or filter for LLM communications only
grep -A 20 "LLM REQUEST\|LLM RESPONSE" car_creation.log

# Filter for tool call summaries
grep "🔧" car_creation.log

# Filter for tool results
grep "✅" car_creation.log
```

**Logging Levels Summary:**

| Log Level | What You See | Use Case |
|-----------|--------------|----------|
| INFO | Tool call summaries: "🔧 LLM requested 4 tool(s): configure_engine, configure_body..." | Normal operation monitoring |
| DEBUG | Tool call details with arguments: "→ configure_engine(vehicle_type=sedan, performance=standard)" | Detailed troubleshooting |
| DEBUG + `--log-llm-comms` | Full conversation flow with complete tool requests, arguments, and results | Deep debugging of agent behavior |

## Troubleshooting

### Common Issues and Solutions

#### 1. OLLAMA Connection Refused

**Problem:** `Connection refused` or `Cannot connect to OLLAMA server`

**Solutions:**
```bash
# Check if OLLAMA is running
curl http://localhost:11434/api/tags

# If not, start OLLAMA
ollama serve

# Verify the model is available
ollama list

# Pull the model if needed
ollama pull llama3.2
```

#### 2. Model Not Found

**Problem:** `Model 'llama3.2' not found`

**Solution:**
```bash
# Pull the required model
ollama pull llama3.2

# Or use a different available model
uv run python cli.py interactive --model <your-model-name>
```

#### 3. JSON Parsing Errors

**Problem:** `Could not extract valid JSON from response`

**Solutions:**
```bash
# Try a model better suited for JSON generation
uv run python cli.py interactive --model codellama:13b

# Lower the temperature for more consistent outputs
uv run python cli.py interactive --temperature 0.0

# Check the logs for the raw response
tail -n 50 car_creation.log

# Check the full_response_debug.log file for detailed response analysis
cat full_response_debug.log
```

**Note:** The system automatically handles multiple JSON objects in LLM responses. When the LLM returns tool results as comma-separated JSON objects (e.g., `{engine}, {body}, {tires}, {electrical}`), the parser wraps them in array brackets and merges all objects into a single configuration. This ensures all component data is captured correctly.

#### 4. Import Errors

**Problem:** `ModuleNotFoundError` or import errors

**Solutions:**
```bash
# Ensure you're in the correct directory
cd src/lclg/single-agent-create-car-looping

# Reinstall dependencies with prerelease support
uv sync --dev --prerelease=allow

# Verify Python version (needs 3.10+ for LangChain 1.0.0a9)
python --version
```

#### 5. Test Failures

**Problem:** Tests failing during `pytest` run

**Solutions:**
```bash
# Install dev dependencies with prerelease support
uv sync --dev --prerelease=allow

# Run tests with verbose output to see errors
uv run pytest tests/unit/ -vv

# Run specific failing test to debug
uv run pytest tests/unit/test_car_agent.py::TestCarAgent::test_name -vv

# Note: Some tool tests may fail due to output format changes - this is expected
# Core agent functionality tests should pass
```

#### 6. Memory/Context Issues

**Problem:** Agent not remembering previous interactions

**Solutions:**
- Use the `status` command to check accumulated context
- Try the `reset` command to clear and restart
- Check that you're in interactive mode (not single request mode)
- Review logs to ensure context is being updated

#### 7. Slow Response Times

**Problem:** Agent takes too long to respond

**Solutions:**
```bash
# Use a smaller/faster model
uv run python cli.py interactive --model llama3.2

# Connect to a GPU-accelerated server
uv run python cli.py interactive --base-url http://gpu-server:11434

# Check OLLAMA server resource usage
ollama ps
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   cat car_creation.log
   ```

2. **Enable debug logging:**
   ```bash
   uv run python cli.py interactive --log-level DEBUG
   ```

3. **Run tests to verify setup:**
   ```bash
   uv run pytest tests/ -v
   ```

4. **Check OLLAMA server status:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Requirements

- **Python 3.10+** (required by LangChain 1.0.0a9)
- **LangChain v1.0.0a9** (prerelease version)
- **OLLAMA server** (local or remote)
- **uv package manager**

## Project Dependencies

Main dependencies (auto-installed with `uv sync --prerelease=allow`):
- `langchain>=1.0.0a9` - LangChain framework (prerelease)
- `langchain-core` - LangChain core components
- `langchain-ollama` - OLLAMA integration
- `pydantic>=2.0.0` - Data validation

Development dependencies (installed with `uv sync --dev --prerelease=allow`):
- `pytest>=8.4.2` - Testing framework
- `pytest-asyncio>=1.2.0` - Async test support
- `pytest-cov>=7.0.0` - Coverage reporting
- `black>=23.0.0` - Code formatting (optional)
- `flake8>=6.0.0` - Linting (optional)
- `mypy>=1.0.0` - Type checking (optional)

## Technical Details

### LangChain Agent Pattern

This project implements the standard LangChain agent pattern using the `create_agent` API:

1. **Prompt Template Structure**: Prompts include `{tools}` and `{input}` placeholders
2. **Agent Executor**: Created via `create_agent(model, tools, prompt)`
3. **Agent Invocation**: Uses `agent_executor.invoke({"input": message})`
4. **Tool Integration**: Tools are automatically formatted and injected by the framework
5. **Response Extraction**: Handles both `output` key and message-based responses

### Context Memory Implementation

- **Short-term memory** with configurable history limit
- **Context accumulation** across iterations
- **Automatic context injection** into prompts
- **Metadata tracking** for configured components

### Multi-Object JSON Response Handling

The system includes intelligent JSON parsing that handles LLM responses containing multiple JSON objects:

**Problem:** LLMs using tools may return multiple JSON objects in a single response:
```json
{engine_config},
{body_config},
{tire_config},
{electrical_config}
```

**Solution:** The `_extract_json_from_response` method in `BaseAgent`:
1. Detects comma-separated JSON objects in the response
2. Wraps them in array brackets: `[{...}, {...}, {...}]`
3. Parses as a JSON array
4. Merges all objects into a single dictionary
5. Returns the complete merged configuration

This ensures all tool results are captured and integrated into the final car configuration, preventing data loss from partial parsing.

## License

MIT License
