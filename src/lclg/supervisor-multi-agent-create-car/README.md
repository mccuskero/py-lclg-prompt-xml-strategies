# Car Creation Multi-Agent System

A supervisor-based multi-agent system for creating complete car JSON build descriptions using LangChain v1.0.0a9 and LangGraph. The system employs specialized AI agents that coordinate through handoffs and tool patterns to generate schema-compliant car configurations.

## Features

### Multi-Agent Architecture
- **SupervisorAgent**: Orchestrates workflow using LangGraph coordination
- **EngineAgent**: Handoff pattern - configures engine specifications
- **BodyAgent**: Tool pattern - processes engine constraints for body design
- **TireAgent**: Handoff pattern - considers body style for tire sizing
- **ElectricalAgent**: Tool pattern - processes engine requirements for electrical systems

### Advanced Capabilities
- **Hybrid Execution**: Sequential dependencies with parallel execution where possible
- **Schema Compliance**: All components validate against car.json schema
- **Schema-Driven Prompts**: Choose between markdown descriptions or actual JSON schema definitions in agent prompts
- **Handoff Coordination**: Inter-agent communication with constraint passing
- **Custom Ollama Integration**: Leverages prompt-xml-strategies OllamaClient
- **Robust JSON Processing**: Advanced JSON extraction with automatic brace balancing and multiple parsing strategies
- **Optimized LLM Configuration**: Configured with appropriate token limits and temperature settings for reliable JSON generation
- **CLI Interface**: Comprehensive command-line interface for car creation
- **Debug Logging**: Configurable log levels with detailed JSON processing debugging

## Installation

### Prerequisites
- Python 3.10+
- OLLAMA server running locally or remotely
- UV package manager

### Setup
```bash
# Navigate to the project directory
cd src/lclg/supervisor-multi-agent-create-car

# Install dependencies
uv sync

# Verify installation
uv run python -c "import src.agents.multi_agent_system; print('Installation successful')"
```

### OLLAMA Setup
```bash
# Install OLLAMA (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start OLLAMA server
ollama serve

# Pull required model
ollama pull llama3.2
```

## LLM Configuration & JSON Processing

### Optimized Settings
The system has been optimized for reliable JSON generation with the following configuration:

- **Max Tokens**: Set to 1000 tokens to prevent response truncation
- **Temperature**: Set to 0.1 for consistent, structured JSON output
- **JSON-Only Prompts**: All agents use explicit JSON-only response instructions
- **Automatic Brace Balancing**: Handles incomplete JSON responses from LLM

### JSON Extraction Features
- **Multi-Strategy Parsing**: Attempts direct parsing, regex extraction, and line-by-line reconstruction
- **Brace Balancing**: Automatically fixes missing closing braces in JSON responses
- **Debug Logging**: Comprehensive logging of JSON extraction attempts and results
- **Fallback Mechanisms**: Multiple parsing strategies ensure reliable JSON extraction

### Debug Output
Enable debug logging to see detailed JSON processing information:

```bash
# Enable DEBUG level logging
uv run python cli.py --log-level DEBUG create-car \
  --vin "ABC123" \
  --year "2024" \
  --make "Toyota" \
  --model-name "Camry"

# Other log levels: INFO (default), WARNING, ERROR
uv run python cli.py --log-level INFO create-car [options]
```

### LLM Response Handling
The system handles various LLM response formats:
- **Clean JSON**: Direct JSON parsing for well-formatted responses
- **JSON Blocks**: Extraction from ```json code blocks
- **Incomplete JSON**: Automatic brace balancing for truncated responses
- **Mixed Content**: Regex-based JSON object detection in mixed content

## Quick Start

### Basic Car Creation
```bash

cd ./src/lclg/supervisor-multi-agent-create-car

# Create a single car using default markdown prompts
uv run python cli.py create-car \
  --vin "1HGBH41JXMN109186" \
  --year "2024" \
  --make "Honda" \
  --model-name "Civic" \
  --output "my_car.json"

# Use schema-driven prompts (recommended for better JSON compliance)
uv run python cli.py --use-json-subtypes-in-prompts-creation create-car \
  --vin "1HGBH41JXMN109186" \
  --year "2024" \
  --make "Honda" \
  --model-name "Civic" \
  --output "my_car.json"

# Use different execution mode with schema-driven prompts
uv run python cli.py --use-json-subtypes-in-prompts-creation create-car \
  --vin "1HGBH41JXMN109186" \
  --year "2024" \
  --make "Honda" \
  --model-name "Civic" \
  --execution-mode "sequential" \
  --format "summary"
```

### System Validation
```bash
# Validate system components
uv run python cli.py validate-system

# Check available models
uv run python cli.py list-models

# Test individual agents with default prompts
uv run python cli.py test-agent --agent engine

# Test individual agents with schema-driven prompts
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent engine

# Test schema-driven prompt functionality
uv run python test_schema_prompts.py
```

### Prompt System Options

The system supports two prompt generation strategies:

#### Markdown Prompts (Default)
- Uses human-readable markdown descriptions of JSON schema requirements
- Backward compatible with existing implementations
- Easier for humans to read and understand

#### Schema-Driven Prompts (Recommended)
- Embeds actual JSON schema definitions directly into agent prompts
- Provides precise structure and validation requirements to agents
- Improves JSON compliance and reduces validation errors
- Better for complex nested structures and constraints

```bash
# Enable schema-driven prompts globally
uv run python cli.py --use-json-subtypes-in-prompts-creation [command]

# Use traditional markdown prompts (default)
uv run python cli.py --use-markdown-prompts [command]
```

**Schema Mapping:**
- `supervisor` → `carType` (complete car structure)
- `engine` → `engineType` (engine specifications)
- `body` → `bodyType` (body configuration)
- `tire` → `tireType` (tire specifications)
- `electrical` → `electricalType` (electrical systems)

### Batch Operations
```bash
# Create multiple cars from specification file
uv run python cli.py --use-json-subtypes-in-prompts-creation batch-create \
  --cars-file "car_specs.json" \
  --output-dir "./batch_output" \
  --max-concurrent 3
```

## Architecture

### Workflow Execution Patterns

#### Hybrid Mode (Default)
```
Engine Agent -> Body Agent (handoff)
             -> Electrical Agent (parallel)
             |
           Tire Agent -> Supervisor (assembly)
```

The system generates car JSON that complies with the car.json schema located at `schema/single/car.json`.

#### Sequential Mode
```
Engine Agent -> Body Agent -> Tire Agent -> Electrical Agent -> Supervisor
```

#### Parallel Mode
```
All agents execute simultaneously with supervisor coordination
```

## Complete CLI Reference

### System Management
```bash
# Validate entire system functionality
uv run python cli.py validate-system

# List available OLLAMA models
uv run python cli.py list-models

# Check agent status and configuration with debug logging
uv run python cli.py --log-level DEBUG --use-json-subtypes-in-prompts-creation validate-system

# Validate system with different log levels
uv run python cli.py --log-level INFO validate-system
uv run python cli.py --log-level WARNING validate-system
uv run python cli.py --log-level ERROR validate-system
```

### Global CLI Options
All commands support these global options:

```bash
# Logging configuration
--log-level [DEBUG|INFO|WARNING|ERROR]    # Set logging verbosity (default: INFO)
--enable-logging / --disable-logging      # Enable/disable system logging (default: enabled)

# Model configuration
--model TEXT                              # Ollama model name (default: llama3.2)
--base-url TEXT                          # Ollama server URL (default: http://localhost:11434)
--temperature FLOAT                      # LLM temperature (default: 0.1)

# Execution configuration
--execution-mode [hybrid|sequential|parallel]  # Workflow execution mode (default: hybrid)

# Prompt configuration
--use-json-subtypes-in-prompts-creation   # Use schema-driven prompts (recommended)
--use-markdown-prompts                    # Use traditional markdown prompts (default)

# Example with multiple global options
uv run python cli.py --log-level DEBUG --temperature 0.2 --use-json-subtypes-in-prompts-creation create-car [options]
```

### Car Creation Commands

#### Single Car Creation
```bash
# Basic car creation with markdown prompts (default)
uv run python cli.py create-car \
  --vin "1HGBH41JXMN109186" \
  --year "2024" \
  --make "Honda" \
  --model-name "Civic" \
  --output "honda_civic.json"

# Enhanced car creation with schema-driven prompts and debug logging
uv run python cli.py --log-level DEBUG --use-json-subtypes-in-prompts-creation create-car \
  --vin "1HGBH41JXMN109186" \
  --year "2024" \
  --make "Honda" \
  --model-name "Civic" \
  --execution-mode "hybrid" \
  --format "json" \
  --output "honda_civic_enhanced.json"

# Sequential execution mode
uv run python cli.py --use-json-subtypes-in-prompts-creation create-car \
  --vin "2T1BURHE0JC014965" \
  --year "2023" \
  --make "Toyota" \
  --model-name "Camry" \
  --execution-mode "sequential" \
  --format "summary" \
  --output "toyota_camry.json"

# Parallel execution mode
uv run python cli.py --use-json-subtypes-in-prompts-creation create-car \
  --vin "WBANE53544CT18942" \
  --year "2024" \
  --make "BMW" \
  --model-name "X5" \
  --execution-mode "parallel" \
  --format "full" \
  --output "bmw_x5.json"
```

#### Batch Car Creation
```bash
# Create multiple cars from specification file
uv run python cli.py --use-json-subtypes-in-prompts-creation batch-create \
  --cars-file "car_specifications.json" \
  --output-dir "./batch_results" \
  --max-concurrent 3 \
  --execution-mode "hybrid"

# Batch creation with sequential processing
uv run python cli.py batch-create \
  --cars-file "luxury_cars.json" \
  --output-dir "./luxury_output" \
  --max-concurrent 1 \
  --execution-mode "sequential"
```

### Agent Testing
```bash
# Test individual agents with default prompts
uv run python cli.py test-agent --agent engine
uv run python cli.py test-agent --agent body
uv run python cli.py test-agent --agent tire
uv run python cli.py test-agent --agent electrical
uv run python cli.py test-agent --agent supervisor

# Test agents with schema-driven prompts (recommended)
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent engine
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent body
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent tire
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent electrical
uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --supervisor

# Test all agents in sequence
for agent in engine body tire electrical supervisor; do
  uv run python cli.py --use-json-subtypes-in-prompts-creation test-agent --agent $agent
done
```

### Schema and Prompt Testing
```bash
# Test schema-driven prompt functionality
uv run python test_schema_prompts.py

# Test schema functionality and validation
uv run python tests/test_schema_functionality.py

# Validate JSON schema compliance
uv run python -c "from src.utils.schema_loader import SchemaLoader; SchemaLoader.validate_car_schema('output/my_car.json')"
```

## Testing

The project includes comprehensive test suites with multiple categories and execution modes.

### Test Setup
```bash
# Install test dependencies
uv sync --dev

# Install with test-only dependencies
uv sync --group test
```

### Running Tests

#### Basic Test Execution
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src

# Run tests with HTML coverage report
uv run pytest --cov=src --cov-report=html
```

#### Test Categories

The project uses pytest markers to organize tests:

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run tests that don't require LLM access
uv run pytest -m "not llm"

# Run tests that don't require OLLAMA server
uv run pytest -m "not ollama"

# Run multi-agent system tests
uv run pytest -m multi_agent

# Run fast tests only (exclude slow tests)
uv run pytest -m "not slow"
```

#### Specific Test Files and Directories
```bash
# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only
uv run pytest tests/integration/

# Run specific test file
uv run pytest tests/unit/test_multi_agent_system.py

# Run specific test class
uv run pytest tests/unit/test_base_agent.py::TestBaseAgent

# Run specific test method
uv run pytest tests/unit/test_schema_loader.py::TestSchemaLoader::test_load_car_schema

# Run agent-specific tests
uv run pytest tests/unit/agents/
uv run pytest tests/unit/tools/

# Run LLM integration tests
uv run pytest tests/unit/llm/test_ollama_llm.py
```

#### Parallel Test Execution
```bash
# Run tests in parallel using all CPU cores
uv run pytest -n auto

# Run tests using 4 CPU cores
uv run pytest -n 4

# Run specific test category in parallel
uv run pytest -m unit -n auto
```

#### Coverage Requirements
```bash
# Run tests with 80% coverage requirement (configured default)
uv run pytest --cov=src --cov-fail-under=80

# Run with stricter coverage requirement
uv run pytest --cov=src --cov-fail-under=90

# Generate coverage reports in multiple formats
uv run pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

#### Development Testing Workflows
```bash
# Quick test during development (unit tests only, parallel)
uv run pytest -m unit -n auto

# Full test suite with coverage
uv run pytest --cov=src --cov-report=html

# Test specific agent functionality
uv run pytest tests/unit/agents/ -v

# Test tool functionality
uv run pytest tests/unit/tools/ -v

# Integration testing (requires OLLAMA server)
uv run pytest -m integration --ollama

# Schema validation testing
uv run pytest tests/unit/test_schema_loader.py tests/integration/test_schema_integration.py
```

### Code Quality Checks
```bash
# Format code with Black
uv run black src/ tests/

# Check code formatting without changing files
uv run black --check src/ tests/

# Lint code with flake8
uv run flake8 src/ tests/

# Type checking with mypy
uv run mypy src/

# Run all quality checks together
uv run black src/ tests/ && uv run flake8 src/ tests/ && uv run mypy src/
```

### Testing Best Practices

#### Prerequisites for Testing
- **OLLAMA Server**: Some tests require OLLAMA server running locally
- **Models**: Ensure `llama3.2` model is available for LLM tests
- **Schema Files**: JSON schema files must be present in `schema/` directory

#### Test Environment Setup
```bash
# Start OLLAMA server for integration tests
ollama serve

# Pull required model for LLM tests
ollama pull llama3.2

# Verify OLLAMA connectivity
curl http://localhost:11434/api/tags
```

#### Continuous Integration Testing
```bash
# Run the full CI test suite
uv run pytest -m "not slow" --cov=src --cov-fail-under=80

# Run tests without external dependencies
uv run pytest -m "unit and not llm and not ollama"

# Run tests suitable for CI environment
uv run pytest -m "not slow and not ollama" -n auto
```

## Project Structure

```
src/lclg/supervisor-multi-agent-create-car/
├── src/
│   ├── agents/                     # Agent implementations
│   │   ├── multi_agent_system.py  # Main multi-agent orchestration
│   │   ├── base_agent.py          # Base agent functionality
│   │   ├── engine_agent.py        # Engine configuration agent
│   │   ├── body_agent.py          # Body design agent
│   │   ├── tire_agent.py          # Tire specification agent
│   │   └── electrical_agent.py    # Electrical system agent
│   ├── tools/                     # Agent tools
│   │   ├── engine_tools.py        # Engine configuration tools
│   │   ├── body_tools.py          # Body design tools
│   │   ├── tire_tools.py          # Tire specification tools
│   │   └── electrical_tools.py    # Electrical system tools
│   ├── utils/                     # Utility modules
│   │   ├── schema_loader.py       # JSON schema loading and validation
│   │   ├── prompts_from_json_schema.py  # Schema-driven prompt generation
│   │   └── ollama_llm.py          # OLLAMA client integration
│   └── cli.py                     # Command-line interface
├── tests/
│   ├── unit/                      # Unit tests
│   │   ├── agents/                # Agent unit tests
│   │   ├── tools/                 # Tool unit tests
│   │   ├── llm/                   # LLM integration tests
│   │   └── test_*.py              # Core functionality tests
│   ├── integration/               # Integration tests
│   └── test_*.py                  # Top-level test files
├── schema/                        # JSON schema definitions
│   ├── single/car.json           # Main car schema
│   └── multi/                    # Multi-file schema definitions
├── examples/                      # Example configurations and outputs
├── cli.py                        # CLI entry point
├── test_schema_prompts.py        # Schema prompt testing
└── pyproject.toml               # Project configuration
```

## Troubleshooting

### Common Issues and Solutions

#### JSON Parsing Errors
If you encounter JSON parsing errors, the system includes robust error handling:

```bash
# Enable debug logging to see JSON processing details
uv run python cli.py --log-level DEBUG create-car [options]
```

**Common JSON issues and automatic fixes:**
- **Truncated responses**: Increased max_tokens to 1000 tokens
- **Missing closing braces**: Automatic brace balancing
- **Mixed content**: Regex-based JSON extraction
- **Temperature too high**: Lowered to 0.1 for consistency

#### LLM Response Issues
- **Timeout errors**: Check OLLAMA server connectivity
- **Model not found**: Ensure `llama3.2` model is pulled
- **Connection refused**: Verify OLLAMA server is running

```bash
# Verify OLLAMA connectivity
curl http://localhost:11434/api/tags

# Check system status
uv run python cli.py validate-system
```

#### Agent Failures
If specific agents fail:

```bash
# Test individual agents
uv run python cli.py --log-level DEBUG test-agent --agent engine
uv run python cli.py --log-level DEBUG test-agent --agent electrical

# Use schema-driven prompts for better compliance
uv run python cli.py --use-json-subtypes-in-prompts-creation --log-level DEBUG create-car [options]
```

### Performance Optimization
- **Use hybrid mode**: Balances speed and reliability
- **Enable schema-driven prompts**: Improves JSON compliance
- **Adjust temperature**: Lower values (0.1) for structured output
- **Monitor token usage**: 1000 token limit prevents truncation

### Debugging Tips
1. **Always start with debug logging**: `--log-level DEBUG`
2. **Check individual agents**: Test agents separately before full workflow
3. **Verify OLLAMA status**: Ensure model availability and server connectivity
4. **Use schema-driven prompts**: `--use-json-subtypes-in-prompts-creation` for complex schemas