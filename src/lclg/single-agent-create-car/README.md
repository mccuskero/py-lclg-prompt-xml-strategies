# Single-Agent Car Creation System

A comprehensive Python-based system that creates complete car configurations using a single intelligent agent powered by LangChain v1.0.0a9 and OLLAMA. This system consolidates all car creation capabilities—engine configuration, body design, electrical systems, and tire specification—into one unified agent with access to all necessary tools.

## 🎯 Overview

This project represents a refactored approach to the multi-agent car creation system, consolidating multiple specialized agents into a single, comprehensive agent. The system leverages the Strategy Pattern to provide flexible car creation capabilities while maintaining the object-oriented design principles and comprehensive tooling of the original multi-agent system.

### Key Advantages of Single-Agent Architecture

- **Simplified Orchestration**: No complex inter-agent communication or handoff protocols
- **Unified Context**: Single agent maintains complete context throughout the car creation process
- **Reduced Complexity**: Easier debugging, monitoring, and maintenance
- **Consistent Output**: Unified response format and validation across all components
- **Better Performance**: Elimination of agent coordination overhead

### Comparison with Multi-Agent System

| Aspect | Multi-Agent | Single-Agent |
|--------|-------------|--------------|
| **Complexity** | High (coordination required) | Low (single execution flow) |
| **Debugging** | Complex (multiple agents) | Simple (single agent trace) |
| **Performance** | Overhead from handoffs | Direct tool execution |
| **Consistency** | Variable (agent-dependent) | Uniform (single agent logic) |
| **Maintenance** | Multiple agent codebases | Single agent codebase |

## Features

- **Single Agent Architecture**: One agent with access to all car creation tools
- **Comprehensive Tool Set**: Engine, body, electrical, and tire configuration tools
- **LangChain Integration**: Built on LangChain v1.0.0a9 for robust agent orchestration
- **OLLAMA Support**: Direct integration with OLLAMA for local LLM deployment
- **Flexible Prompt System**: Support for both markdown and JSON schema-based prompts
- **CLI Interface**: Complete command-line interface for easy interaction
- **Testing Framework**: Comprehensive pytest-based testing suite

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.8+**: Required for running the application
- **UV Package Manager**: Fast Python package installer and resolver
- **OLLAMA Server**: Local or remote LLM server

### Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd src/lclg/single-agent-create-car
   ```

2. **Install dependencies using UV:**
   ```bash
   uv sync
   ```

3. **Set up OLLAMA (if not already installed):**
   ```bash
   # Install OLLAMA
   curl -fsSL https://ollama.ai/install.sh | sh

   # Start OLLAMA server (run in background)
   ollama serve &

   # Pull required model
   ollama pull llama3.2

   # Verify installation
   ollama list
   ```

4. **Verify system setup:**
   ```bash
   # Test agent connectivity
   uv run python cli.py validate-agent

   # Check available CLI commands
   uv run python cli.py --help
   ```

### Quick Test Run

Create your first car configuration:

```bash
# Create a basic sedan
uv run python cli.py create-car \
  --vehicle-type sedan \
  --performance-level standard \
  --fuel-preference gasoline \
  --budget medium \
  --format summary

# Expected output: Detailed car configuration with engine, body, electrical, and tire specs
```

## 💻 Usage Guide

### Command Line Interface

The system provides a comprehensive CLI with multiple commands for different use cases:

#### **Car Creation Commands**

```bash
# Basic car creation with summary output
uv run python cli.py create-car \
  --vehicle-type sedan \
  --performance-level standard \
  --fuel-preference gasoline \
  --budget medium \
  --format summary

# Advanced car with custom features and JSON output
uv run python cli.py create-car \
  --vehicle-type suv \
  --performance-level performance \
  --fuel-preference hybrid \
  --budget high \
  --special-features sunroof \
  --special-features leather_seats \
  --output my_car.json \
  --format json

# Electric vehicle configuration
uv run python cli.py create-car \
  --vehicle-type coupe \
  --performance-level sport \
  --fuel-preference electric \
  --budget luxury \
  --special-features fast_charging \
  --special-features premium_interior
```

#### **System Management Commands**

```bash
# Validate agent and LLM connectivity
uv run python cli.py validate-agent

# Get comprehensive agent information
uv run python cli.py agent-info

# Test specific tool categories
uv run python cli.py test-tools --tool-category engine
uv run python cli.py test-tools --tool-category all

# Check available CLI options
uv run python cli.py --help
uv run python cli.py create-car --help
```

#### **Batch Processing**

```bash
# Process multiple car requirements from file
uv run python cli.py batch-create \
  --requirements-file batch_requirements.json \
  --output-dir ./batch_results

# Example batch_requirements.json format:
# [
#   {
#     "vehicle_type": "sedan",
#     "performance_level": "standard",
#     "fuel_preference": "gasoline",
#     "budget": "medium"
#   },
#   {
#     "vehicle_type": "suv",
#     "performance_level": "performance",
#     "fuel_preference": "hybrid",
#     "budget": "high"
#   }
# ]
```

### **CLI Parameters Reference**

| Parameter | Options | Description |
|-----------|---------|-------------|
| `--vehicle-type` | sedan, suv, truck, coupe, convertible | Type of vehicle to create |
| `--performance-level` | economy, standard, performance, sport | Performance characteristics |
| `--fuel-preference` | gasoline, diesel, electric, hybrid | Preferred power source |
| `--budget` | low, medium, high, luxury | Budget constraints |
| `--format` | summary, json, compact | Output format |
| `--model` | llama3.2, codellama, etc. | OLLAMA model to use |
| `--base-url` | URL | OLLAMA server URL |
| `--log-level` | DEBUG, INFO, WARNING, ERROR, CRITICAL | Set logging level |
| `--log-to-file` / `--no-log-to-file` | - | Enable/disable file logging |
| `--log-file` | file path | Custom log file path |
| `--log-format` | standard, detailed | Log format style |
| `--disable-colors` / `--enable-colors` | - | Control colored console output |
| `--json-logs` / `--text-logs` | - | JSON vs text format for file logs |

### Python API

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents.car_agent import CarAgent

# Initialize the agent
agent = CarAgent(
    model_name="llama3.2",
    base_url="http://localhost:11434",
    temperature=0.1
)

# Create a car
requirements = {
    "vehicle_type": "sedan",
    "performance_level": "standard",
    "fuel_preference": "gasoline",
    "budget": "medium",
    "special_features": ["sunroof"]
}

car_config = agent.create_complete_car(requirements)
print(car_config)
```

## Architecture

### Single Agent Design

The system uses a single `CarAgent` that has access to all car creation tools:

- **Engine Tools**: Configure engines, get specifications
- **Body Tools**: Design exterior/interior, customize features
- **Electrical Tools**: Set up electrical systems, batteries, lighting
- **Tire Tools**: Configure tires and wheels, analyze performance

### Tool Categories

#### Engine Tools
- `configure_engine`: Select and configure engines based on requirements
- `get_engine_specs`: Get detailed engine specifications and constraints

#### Body Tools
- `design_body`: Design basic body structure and style
- `get_body_specs`: Get body specifications and constraints
- `customize_exterior`: Customize exterior features
- `customize_interior`: Customize interior features

#### Electrical Tools
- `configure_electrical`: Set up main electrical system
- `configure_battery`: Configure battery systems
- `configure_charging`: Set up charging systems (for electric/hybrid)
- `configure_lighting`: Configure lighting systems

#### Tire Tools
- `configure_tires`: Select and configure tires
- `get_tire_specs`: Get tire specifications
- `design_wheels`: Design wheel specifications
- `analyze_tire_performance`: Analyze tire performance characteristics

## 📁 Project Structure

The project is organized into clear, modular components following object-oriented design principles:

```
src/lclg/single-agent-create-car/
├── 📂 src/                        # Main source code
│   ├── 📂 agents/                 # Agent implementations
│   │   ├── base_agent.py          # Abstract base agent class
│   │   ├── car_agent.py           # Main car creation agent
│   │   └── __init__.py
│   ├── 📂 tools/                  # Car creation tools (copied from multi-agent)
│   │   ├── engine_tools.py        # Engine configuration & specs
│   │   ├── body_tools.py          # Body design & customization
│   │   ├── electrical_tools.py    # Electrical systems & battery
│   │   ├── tire_tools.py          # Tire & wheel configuration
│   │   └── __init__.py
│   ├── 📂 prompts/                # Prompt management system
│   │   ├── prompts.py             # Markdown-based prompts
│   │   ├── prompts_from_json_schema.py  # JSON schema-driven prompts
│   │   ├── schema_loader.py       # Schema loading utilities
│   │   └── __init__.py
│   ├── 📂 llm/                    # LLM client integration
│   │   ├── ollama_llm.py          # OLLAMA client implementation
│   │   └── __init__.py
│   ├── 📂 utils/                  # Utility modules
│   │   └── __init__.py
│   └── __init__.py
├── 📂 schema/                     # JSON schema definitions
│   ├── 📂 single/                 # Single-file schemas
│   │   └── car.json
│   └── 📂 multi/                  # Multi-file schema definitions
├── 📂 tests/                      # Comprehensive test suite
│   ├── 📂 unit/                   # Unit tests
│   │   ├── test_car_agent.py      # Car agent functionality tests
│   │   └── __init__.py
│   ├── 📂 integration/            # Integration tests
│   │   └── __init__.py
│   ├── conftest.py                # Pytest configuration & fixtures
│   └── __init__.py
├── 📄 cli.py                      # Command-line interface
├── 📄 pyproject.toml              # UV/Python project configuration
├── 📄 pytest.ini                 # Pytest configuration
└── 📄 README.md                   # This documentation
```

### 🔧 Core Components

#### **CarAgent** (`src/agents/car_agent.py`)
- **Purpose**: Single agent that orchestrates all car creation activities
- **Capabilities**: Engine, body, electrical, and tire configuration
- **Tools**: 16 specialized tools for comprehensive car creation
- **Integration**: All tools accessible within single agent context

#### **BaseAgent** (`src/agents/base_agent.py`)
- **Purpose**: Abstract base class providing common agent functionality
- **Features**: LLM integration, tool management, JSON processing, validation
- **Benefits**: Consistent interface and shared functionality for all agents

#### **Tool Categories**
- **Engine Tools** (2 tools): Engine configuration and specifications
- **Body Tools** (4 tools): Body design, exterior/interior customization
- **Electrical Tools** (4 tools): Main system, battery, charging, lighting
- **Tire Tools** (4 tools): Tire configuration, wheel design, performance analysis

#### **Prompt System**
- **Dual Support**: Both markdown and JSON schema-based prompts
- **Flexibility**: Choose prompt style based on use case requirements
- **Schema Integration**: JSON schemas drive prompt generation and validation

## 🧪 Testing

The project includes a comprehensive testing framework using pytest with multiple test categories and configurations.

### **Running Tests**

#### **Basic Test Commands**

```bash
# Run all unit tests
uv run pytest tests/unit/ -v

# Run tests with detailed output
uv run pytest tests/unit/ -v -s

# Run specific test file
uv run pytest tests/unit/test_car_agent.py -v

# Run tests with coverage report
uv run pytest --cov=src tests/ --cov-report=html

# Run tests and generate coverage report
uv run pytest --cov=src --cov-report=term-missing tests/
```

#### **Test Categories and Markers**

```bash
# Run only car agent tests
uv run pytest -m "car_agent" -v

# Run only tool tests
uv run pytest -m "tools" -v

# Run only unit tests (excludes integration)
uv run pytest -m "unit" -v

# Skip slow tests
uv run pytest -m "not slow" -v

# Run integration tests (requires OLLAMA server)
uv run pytest --integration tests/integration/ -v
```

#### **Test Configuration Examples**

```bash
# Test with specific OLLAMA model
uv run pytest tests/unit/ --model llama3.2

# Test with custom OLLAMA server
uv run pytest tests/unit/ --base-url http://remote-ollama:11434

# Run tests in parallel (requires pytest-xdist)
uv run pytest tests/unit/ -n auto

# Generate XML test report
uv run pytest tests/unit/ --junitxml=test-results.xml
```

### **Test Structure and Organization**

#### **Test Categories**

| Category | Location | Purpose | Dependencies |
|----------|----------|---------|--------------|
| **Unit Tests** | `tests/unit/` | Component isolation testing | None (mocked) |
| **Integration Tests** | `tests/integration/` | End-to-end system testing | OLLAMA server |
| **Tool Tests** | `tests/unit/` | Individual tool functionality | Mocked LLM |
| **Agent Tests** | `tests/unit/` | Agent behavior and responses | Mocked LLM |

#### **Test Fixtures Available**

```python
# Available in conftest.py
mock_ollama_llm           # Mocked OLLAMA client
sample_car_requirements   # Standard car requirements
sample_engine_config      # Engine configuration data
sample_car_config         # Complete car configuration
mock_tools               # Mocked tools for testing
temporary_output_dir     # Temp directory for test outputs
```

#### **Writing New Tests**

```python
# Example test structure
import pytest
from agents.car_agent import CarAgent

class TestCarAgent:
    @pytest.mark.car_agent
    def test_agent_initialization(self, mock_ollama_llm):
        agent = CarAgent()
        assert agent.name == "car_agent"

    @pytest.mark.tools
    def test_tool_execution(self, sample_car_requirements):
        agent = CarAgent()
        result = agent.create_complete_car(sample_car_requirements)
        assert "car_configuration" in result
```

### **Test Coverage Goals**

- **Unit Tests**: >90% code coverage
- **Integration Tests**: End-to-end workflow validation
- **Tool Tests**: All 16 tools individually tested
- **Error Handling**: Exception scenarios covered

### **Continuous Testing**

```bash
# Watch mode for development
uv run pytest tests/unit/ --watch

# Pre-commit testing
uv run pytest tests/unit/ --quick

# Full test suite (CI/CD)
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_TEMPERATURE=0.1
USE_JSON_PROMPTS=false
```

### CLI Options

- `--model`: OLLAMA model name (default: llama3.2)
- `--base-url`: OLLAMA server URL (default: http://localhost:11434)
- `--temperature`: LLM temperature (default: 0.1)
- `--use-json-subtypes-in-prompts-creation`: Use JSON schema prompts instead of markdown

## 🏃‍♂️ How to Run

### **Prerequisites Check**

Before running the system, ensure all components are properly set up:

```bash
# 1. Verify Python and UV installation
python --version  # Should be 3.8+
uv --version     # Should be installed

# 2. Check OLLAMA installation and models
ollama --version
ollama list      # Should show available models

# 3. Verify OLLAMA server is running
curl http://localhost:11434/api/tags  # Should return JSON response
```

### **Step-by-Step Execution**

#### **1. System Validation**
```bash
# Navigate to project directory
cd src/lclg/single-agent-create-car

# Install dependencies
uv sync

# Validate system readiness
uv run python cli.py validate-agent
```

#### **2. Basic Car Creation**
```bash
# Create a standard sedan
uv run python cli.py create-car \
  --vehicle-type sedan \
  --performance-level standard \
  --fuel-preference gasoline \
  --budget medium \
  --format summary

# Save output to file
uv run python cli.py create-car \
  --vehicle-type suv \
  --performance-level performance \
  --fuel-preference hybrid \
  --budget high \
  --output my_car.json \
  --format json
```

#### **3. Advanced Usage**
```bash
# Create electric sports car
uv run python cli.py create-car \
  --vehicle-type coupe \
  --performance-level sport \
  --fuel-preference electric \
  --budget luxury \
  --special-features fast_charging \
  --special-features carbon_fiber \
  --format summary

# Test different tool categories
uv run python cli.py test-tools --tool-category engine
uv run python cli.py test-tools --tool-category electrical
```

#### **4. Batch Processing**
```bash
# Create batch requirements file
cat > batch_cars.json << EOF
[
  {
    "vehicle_type": "sedan",
    "performance_level": "economy",
    "fuel_preference": "gasoline",
    "budget": "low"
  },
  {
    "vehicle_type": "suv",
    "performance_level": "standard",
    "fuel_preference": "hybrid",
    "budget": "medium"
  },
  {
    "vehicle_type": "truck",
    "performance_level": "performance",
    "fuel_preference": "diesel",
    "budget": "high"
  }
]
EOF

# Process batch
uv run python cli.py batch-create \
  --requirements-file batch_cars.json \
  --output-dir ./batch_results
```

### **Expected Output Examples**

#### **Summary Format Output**
```
🚗 Single-Agent Car Creation Summary
============================================================
Vehicle Info:
  Type: sedan
  Performance Level: standard
  Fuel Preference: gasoline
  Budget: medium

Components:
  🔧 Engine: gasoline (280 HP, 3.5L)
  🚙 Body: sedan - blue steel
  ⚡ Electrical: 12V system
  🛞 Tires: 225/60R16 (all_season)

Performance Summary:
  Power Rating: 280 HP
  Performance Category: standard
  Component Compatibility: compatible
```

#### **JSON Format Output**
```json
{
  "car_configuration": {
    "vehicle_info": {
      "type": "sedan",
      "performance_level": "standard"
    },
    "engine": {
      "displacement": "3.5L",
      "cylinders": "6",
      "fuelType": "gasoline",
      "horsepower": "280"
    },
    "body": {
      "exterior": { "style": "sedan", "color": "blue" },
      "interior": { "seats": "cloth" }
    }
  }
}
```

### **Performance Considerations**

- **First Run**: May take 30-60 seconds as OLLAMA loads the model
- **Subsequent Runs**: Typically complete in 10-20 seconds
- **Batch Processing**: Processes 1-3 cars per minute depending on complexity
- **Memory Usage**: Requires ~2-4GB RAM for OLLAMA model

## Development

### Code Quality

```bash
# Format code
uv run black src/

# Lint code
uv run flake8 src/

# Type checking
uv run mypy src/
```

### Adding New Tools

1. Create tool class in appropriate `tools/` file
2. Inherit from `BaseTool`
3. Implement `_run()` method
4. Add tool to `CarAgent._setup_tools()`
5. Update tool categories in `CarAgent.get_tool_categories()`
6. Add tests

### Adding New Features

1. Extend `CarAgent` class
2. Add new methods for feature functionality
3. Update CLI commands as needed
4. Add comprehensive tests
5. Update documentation

## Troubleshooting

### Common Issues

1. **OLLAMA Connection Failed**
   - Ensure OLLAMA server is running: `ollama serve`
   - Check server URL and port
   - Verify model is available: `ollama list`

2. **Import Errors**
   - Ensure all `__init__.py` files are present
   - Check Python path configuration
   - Verify dependencies are installed: `uv sync`

3. **Tool Execution Errors**
   - Check tool implementation and parameters
   - Verify LLM responses are properly formatted
   - Enable debug logging for detailed error information

## 📝 Comprehensive Logging

The system includes comprehensive logging capabilities with multiple output formats, levels, and destinations.

### **Logging Features**

- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Dual Output**: Console and file logging with independent configuration
- **Text Format Default**: Human-readable text logs by default
- **Colored Console Output**: Enhanced readability with color-coded log levels
- **Optional JSON Logs**: Machine-readable JSON format available when needed
- **Log Rotation**: Automatic log file rotation with size limits
- **Component-Specific Logging**: Separate loggers for agents, tools, and CLI
- **Performance Tracking**: Execution time logging for operations
- **Request Tracing**: Request ID tracking for debugging

### **Logging Configuration**

#### **Command Line Options**

```bash
# Basic logging configuration
uv run python cli.py create-car \
  --vehicle-type sedan \
  --log-level DEBUG \
  --log-to-file \
  --log-format detailed

# Advanced logging with custom file and JSON format
uv run python cli.py create-car \
  --vehicle-type suv \
  --log-level INFO \
  --log-to-file \
  --log-file ./custom_logs/car_creation.log \
  --json-logs \
  --disable-colors

# Console-only logging with colors (default text format)
uv run python cli.py create-car \
  --vehicle-type truck \
  --log-level WARNING \
  --no-log-to-file \
  --enable-colors
```

#### **Environment Variables**

Create a `.env` file for persistent configuration:

```env
# Logging Configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_FILE_PATH=logs/car_agent.log
LOG_FORMAT=standard
ENABLE_COLORS=true
JSON_LOGS=false  # Default to human-readable text format
MAX_LOG_FILE_SIZE=10485760
LOG_BACKUP_COUNT=5
```

#### **Programmatic Configuration**

```python
from utils.logging_config import setup_logging, LoggingConfig

# Basic setup (defaults to text format)
setup_logging(level="DEBUG", log_to_file=True)

# Advanced setup (text format is default)
LoggingConfig.setup_logging(
    level="INFO",
    log_to_console=True,
    log_to_file=True,
    log_file_path="./logs/custom.log",
    log_format="detailed",
    enable_colors=True,
    json_format=False,  # Explicit text format (default)
    max_file_size=20*1024*1024,  # 20MB
    backup_count=10
)
```

### **Log Format Examples**

#### **Standard Format (Default Text)**
```
2025-01-15 10:30:45 car_agent.py:187 INFO Starting complete car creation
2025-01-15 10:30:45 engine_tools.py:117 INFO Engine configuration requested
2025-01-15 10:30:46 car_agent.py:212 INFO Complete car creation completed
```

#### **Detailed Format (Text with Function Names)**
```
2025-01-15 10:30:45 car_agent.py:187 INFO create_complete_car() Starting complete car creation
2025-01-15 10:30:45 engine_tools.py:117 INFO _run() Engine configuration requested
2025-01-15 10:30:46 car_agent.py:212 INFO create_complete_car() Complete car creation completed
```

#### **JSON Format (Optional, when --json-logs is used)**
```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "agent.car_agent",
  "message": "Starting complete car creation",
  "module": "car_agent",
  "function": "create_complete_car",
  "line": 187,
  "agent_name": "car_agent",
  "vehicle_type": "sedan",
  "performance_level": "standard"
}
```

### **Component-Specific Logging**

#### **Agent Logging**
```python
# Agents automatically log key activities
# - Agent initialization
# - Tool setup and configuration
# - Message processing
# - Component creation
# - Error handling

# Custom agent logging
if self.enable_logging:
    self.logger.info("Custom agent activity", custom_data="value")
    self.logger.log_component_creation("engine", requirements, success=True)
```

#### **Tool Logging**
```python
# Tools automatically log:
# - Tool execution with parameters
# - Execution time tracking
# - Error handling with fallbacks
# - Result summaries

# Example tool log output
self.logger.log_execution(parameters, result, execution_time)
self.logger.log_error_with_fallback(exception, fallback_used=True)
```

#### **CLI Logging**
```python
# CLI commands log:
# - Command initiation
# - Parameter validation
# - Operation progress
# - Results and completion status

logger.info("Car creation command started", vehicle_type="sedan")
logger.debug("Starting car creation with agent", requirements=requirements)
```

### **Log Analysis and Monitoring**

#### **Log File Locations**
```bash
# Default log files
logs/car_agent_20250115_103045.log  # Timestamped logs
logs/car_agent.log                   # Current log file

# Custom log files (as specified)
./custom_logs/car_creation.log
./debug_logs/detailed.log
```

#### **Log Rotation**
- **Default Size Limit**: 10MB per file
- **Backup Count**: 5 backup files retained
- **Rotation Pattern**: `car_agent.log`, `car_agent.log.1`, `car_agent.log.2`, etc.

#### **Monitoring Commands**
```bash
# Monitor real-time logs
tail -f logs/car_agent.log

# Search for specific events
grep "ERROR" logs/car_agent.log
grep "engine_tools" logs/car_agent.log

# Analyze JSON logs
cat logs/car_agent.log | jq '.level' | sort | uniq -c
```

### **Debug Mode**

Enable comprehensive debug logging:

```bash
# Maximum verbosity with file logging
uv run python cli.py create-car \
  --vehicle-type sedan \
  --log-level DEBUG \
  --log-to-file \
  --log-format detailed \
  --enable-colors

# Debug specific components
export LOG_LEVEL=DEBUG
uv run python cli.py create-car --vehicle-type sedan
```

### **Performance Monitoring**

The logging system tracks execution times for key operations:

```bash
# Example performance log entries
2025-01-15 10:30:45 car_agent.py:252 INFO Component creation successful creation_time=2.34
2025-01-15 10:30:45 engine_tools.py:147 INFO Tool execution completed execution_time=0.45
2025-01-15 10:30:46 cli.py:247 INFO Car creation command completed success=true
```

### **Troubleshooting with Logs**

1. **Agent Initialization Issues**
   ```bash
   grep "Agent setup" logs/car_agent.log
   grep "ERROR.*setup" logs/car_agent.log
   ```

2. **Tool Execution Problems**
   ```bash
   grep "tool.*ERROR" logs/car_agent.log
   grep "fallback" logs/car_agent.log
   ```

3. **LLM Communication Issues**
   ```bash
   grep "LLM" logs/car_agent.log
   grep "invoke" logs/car_agent.log
   ```
