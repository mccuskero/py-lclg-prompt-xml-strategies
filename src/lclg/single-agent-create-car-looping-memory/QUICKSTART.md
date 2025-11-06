# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **uv package manager** installed
3. **OLLAMA** server running locally or accessible remotely

## Setup

1. Navigate to the project directory:
```bash
cd src/lclg/single-agent-create-car-looping
```

2. Install dependencies:
```bash
uv sync
```

3. Verify OLLAMA is running:
```bash
curl http://localhost:11434/api/tags
```

4. Pull the llama3.2 model (if not already available):
```bash
ollama pull llama3.2
```

## Running the Interactive Session

Start an interactive session:

```bash
uv run python cli.py interactive
```

### Example Interaction

```
[Iteration 1] Your request: I need a sedan for daily commuting
... (agent creates basic sedan configuration)

[Iteration 2] Your request: make it more fuel efficient
... (agent updates to hybrid or electric engine)

[Iteration 3] Your request: I want leather seats
... (agent updates interior configuration)

[Iteration 4] Your request: status
... (shows accumulated context)

[Iteration 5] Your request: save my-car.json
... (saves configuration to file)

[Iteration 6] Your request: quit
```

## Running a Single Request

Create a car with command-line options:

```bash
uv run python cli.py single \
  --vehicle-type sedan \
  --performance-level standard \
  --fuel-preference gasoline \
  --output sedan.json
```

Or use a requirements file:

```bash
uv run python cli.py single \
  --requirements-file examples/sample_requirements.json \
  --output result.json
```

## Available Commands (Interactive Mode)

- **Natural language**: Type your car requirements naturally
- **`reset`**: Clear context and start fresh
- **`status`**: Display accumulated context
- **`save <filename>`**: Save current configuration
- **`quit`** or **`exit`**: End the session

## Configuration Options

### Vehicle Types
- sedan
- suv
- truck
- coupe
- hatchback
- convertible
- wagon

### Performance Levels
- economy
- standard
- performance

### Fuel Preferences
- gasoline
- diesel
- electric
- hybrid

### Budget Levels
- low
- medium
- high

## Testing

Run the test suite:

```bash
# All tests
uv run pytest tests/

# Verbose output
uv run pytest tests/ -v

# Specific test
uv run pytest tests/unit/test_car_agent.py -v
```

## Troubleshooting

### OLLAMA Connection Issues

If you get connection errors:

1. Check OLLAMA is running:
```bash
ollama serve
```

2. Verify the model is available:
```bash
ollama list
```

3. Pull the model if needed:
```bash
ollama pull llama3.2
```

### Import Errors

If you get import errors, ensure you're running from the project root:

```bash
cd src/lclg/single-agent-create-car-looping
uv run python cli.py interactive
```

### JSON Parsing Errors

If the LLM response can't be parsed:

1. Try a different model (e.g., codellama):
```bash
uv run python cli.py interactive --model codellama:13b
```

2. Adjust temperature:
```bash
uv run python cli.py interactive --temperature 0.0
```

## Advanced Usage

### Remote OLLAMA Server

Connect to a remote OLLAMA server:

```bash
uv run python cli.py interactive \
  --base-url http://your-server:11434 \
  --model llama3.2
```

### Custom Model

Use a different model:

```bash
uv run python cli.py interactive \
  --model codellama:13b \
  --temperature 0.2
```

### Logging

Enable debug logging:

```bash
uv run python cli.py interactive --log-level DEBUG
```

Disable logging:

```bash
uv run python cli.py interactive --no-logging
```

## Next Steps

1. Review the [README.md](README.md) for detailed documentation
2. Check out example requirements in `examples/`
3. Explore the code structure in `src/`
4. Run the tests to understand the components
5. Customize prompts in `src/prompts/prompts.py`

## Key Features to Try

1. **Context Memory**: Ask for multiple iterations to see how the agent remembers context
2. **Tool Usage**: Watch how the agent uses different tools for different components
3. **Validation**: Try incompatible configurations (e.g., electric engine with 12V electrical)
4. **Status Command**: Check accumulated context at any point
5. **Save/Load**: Save configurations and review them later

## Support

For issues or questions:
1. Check the logs in `car_creation.log`
2. Review the README for detailed documentation
3. Examine the test files for usage examples
