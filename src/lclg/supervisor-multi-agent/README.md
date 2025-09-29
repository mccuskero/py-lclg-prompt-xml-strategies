# Supervisor Multi-Agent System

A LangChain LangGraph-based multi-agent system with supervisor orchestration, built with object-oriented Python design.

## Overview

This project implements a sophisticated multi-agent system with three specialized agents:

- **MathAgent** → Handles numerical problem-solving, calculations, and mathematical analysis
- **ResearchAgent** → Handles information gathering, fact-checking, and research tasks  
- **SupervisorAgent** → Orchestrates tasks by delegating work to specialized agents using handoff mechanisms

## Features

- **Object-Oriented Design**: Clean, maintainable code structure
- **Modern Agent API**: Uses LangChain v1.0.0a9's new `create_agent` API for improved performance
- **PromptTemplate Integration**: Structured prompt templates for consistent agent behavior
- **Handoff System**: Supervisor can delegate tasks to specialized agents using destination and payload
- **Tool Integration**: Each agent has specialized tools for their domain
- **Async Support**: Full asynchronous operation for better performance
- **Interactive Session**: Command-line interface for testing and demonstration

## Project Structure

```
supervisor-multi-agent/
├── pyproject.toml
├── README.md
├── .env.example
├── main.py                   # Main entry point
├── demo.py                   # Demo without API key
├── example_prompts.py        # Example prompts for each agent
├── test_basic.py            # Basic system tests
├── test_complex_coordination.py  # Multi-agent coordination tests
├── examples.py              # Full examples with API
├── uv_setup.py             # UV setup script
├── Makefile                # Development commands
└── src/
    ├── agents/
    │   ├── __init__.py
    │   ├── base_agent.py
    │   ├── math_agent.py
    │   ├── research_agent.py
    │   ├── supervisor_agent.py
    │   └── multi_agent_system.py  # MultiAgentSystem class
    ├── prompts/
    │   ├── __init__.py
    │   └── prompts.py
    └── main.py              # Entry point functions
```

## PromptTemplate System

The project uses a structured prompt template system for consistent agent behavior:

### **Agent-Specific Templates**
- **MathAgent**: Specialized for mathematical problem-solving with step-by-step reasoning
- **ResearchAgent**: Optimized for information gathering and fact-checking
- **SupervisorAgent**: Designed for multi-agent coordination and task delegation

### **Template Features**
- **Consistent Formatting**: All agents use standardized prompt structures
- **Tool Integration**: Templates include available tools and usage instructions
- **Context Awareness**: Prompts adapt to agent capabilities and responsibilities
- **Error Handling**: Built-in guidance for tool usage and response formatting

### **Complex Task Coordination**
- **Multi-Phase Prompts**: Specialized templates for research + math coordination
- **Synthesis Templates**: Structured prompts for combining agent results
- **Task Analysis**: Dedicated templates for determining agent assignments

## Requirements

- **Python**: 3.10+ (required for LangChain v1.0.0a9)
- **Dependencies**: Managed via `uv` package manager

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd supervisor-multi-agent

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Test the system (no API key needed)
uv run python demo.py

# For full functionality, set up API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the interactive system
uv run python main.py
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd supervisor-multi-agent
   ```

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies with uv**:
   ```bash
   uv sync
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Usage

### Demo (No API Key Required)

Test the system tools without needing an API key:

```bash
uv run python demo.py
```

### Example Prompts Demo

See comprehensive example prompts for each agent:

```bash
uv run python example_prompts.py
```

### Multi-Agent Coordination Test

Test the full multi-agent coordination system:

```bash
uv run python test_complex_coordination.py
```

### Interactive Session

Run the interactive session to test the multi-agent system:

```bash
uv run python main.py
```

### Example Queries

Run example queries to see the system in action:

```bash
uv run python main.py examples
```

### Programmatic Usage

```python
import asyncio
from src.agents.multi_agent_system import MultiAgentSystem

async def main():
    system = MultiAgentSystem(allow_no_api_key=True)
    response = await system.process_query("Calculate the area of a circle with radius 5")
    print(response)

asyncio.run(main())
```

### Development Commands

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run black --check .

# Format code
uv run black .
uv run isort .

# Or use the Makefile for convenience
make install-dev    # Install dev dependencies
make test          # Run tests
make lint          # Run linting
make format        # Format code
make run           # Run interactive session
make examples      # Run examples
make example-prompts # Run example prompts demo
make clean         # Clean up cache files
```

## Agent Capabilities

### MathAgent
- **Calculator**: Safe evaluation of mathematical expressions
- **Equation Solver**: Solve simple linear equations
- **Statistics**: Calculate mean, median, standard deviation
- **Geometry**: Area, perimeter, and geometric calculations

### ResearchAgent  
- **Web Search**: Information retrieval (mock implementation)
- **Fact Checker**: Verify statements and claims
- **Summarizer**: Text summarization and key point extraction
- **Knowledge Analyzer**: Organize and analyze knowledge about topics

### SupervisorAgent
- **Handoff Tool**: Delegate tasks to specialized agents
- **Task Analyzer**: Determine which agent should handle a task
- **Coordination**: Manage multi-step workflows
- **Result Synthesizer**: Combine results from multiple agents

## Example Prompts

### MathAgent Examples

The MathAgent specializes in mathematical problem-solving and calculations. Here are example prompts:

#### **Calculator Operations**
```
"Calculate 15 * 23 + 45"
"What is 2^8 + 3^4?"
"Compute the square root of 144"
"Calculate (10 + 5) * 3 / 2"
```

#### **Statistics & Data Analysis**
```
"Calculate the mean, median, and standard deviation of 1, 2, 3, 4, 5"
"What are the statistics for the numbers 10, 20, 30, 40, 50?"
"Find the variance of the dataset: 5, 10, 15, 20, 25"
```

#### **Geometry Calculations**
```
"Calculate the area of a circle with radius 5"
"What is the area of a rectangle with length 10 and width 5?"
"Find the area of a triangle with base 8 and height 6"
"Calculate the circumference of a circle with radius 3"
```

#### **Equation Solving**
```
"Solve the equation 2x + 3 = 7"
"Find x in the equation 3x - 5 = 10"
"Solve for y: 2y + 4 = 12"
```

### ResearchAgent Examples

The ResearchAgent specializes in information gathering, fact-checking, and research tasks. Here are example prompts:

#### **Web Search & Information Gathering**
```
"Research the latest developments in artificial intelligence"
"Find information about renewable energy technologies"
"Look up current trends in machine learning"
"Search for information about climate change solutions"
```

#### **Fact Checking & Verification**
```
"Check if the statement 'Water boils at 100 degrees Celsius' is true"
"Verify the claim that 'The Earth is round'"
"Fact-check: 'Vaccines cause autism'"
"Verify: 'Climate change is caused by human activities'"
```

#### **Text Summarization**
```
"Summarize this long article about quantum computing"
"Provide a summary of the key points in this research paper"
"Create a brief overview of this technical document"
"Summarize the main findings from this study"
```

#### **Knowledge Analysis**
```
"Analyze the knowledge structure of machine learning"
"Organize information about renewable energy sources"
"Analyze the key concepts in artificial intelligence"
"Break down the components of data science"
```

### Complex Multi-Agent Examples

Tasks that require coordination between multiple agents:

#### **Research + Math Tasks**
```
"Research the carbon footprint of air travel and calculate emissions for a 1000km flight"
"Find information about solar panel efficiency and calculate cost savings"
"Research renewable energy costs and calculate payback period for a 5kW system"
"Investigate renewable energy and calculate cost savings for a 10kW solar installation"
```

#### **Analysis + Research Tasks**
```
"Research machine learning algorithms and analyze their mathematical complexity"
"Find information about climate data and perform statistical analysis"
"Research AI ethics and analyze the probability of bias in AI systems"
"Research electric vehicles and calculate the environmental impact of a 500km trip"
```

#### **Multi-Agent Coordination Process**
The system now implements full coordination between agents:

1. **📊 Task Analysis**: Determines which agents are needed
2. **📚 Research Phase**: ResearchAgent gathers relevant information
3. **🧮 Mathematical Phase**: MathAgent performs calculations and analysis
4. **🔗 Synthesis Phase**: SupervisorAgent combines results
5. **✅ Final Coordination**: Provides comprehensive response

## Example Interactions

### Mathematical Tasks
```
Query: "Calculate the area of a circle with radius 5"
→ MathAgent handles the calculation
→ Returns: Area = 78.54 square units
```

### Research Tasks
```
Query: "Research the latest developments in artificial intelligence"
→ ResearchAgent handles the research
→ Returns: Summarized information with sources
```

### Complex Tasks
```
Query: "Find information about climate change and calculate the carbon footprint"
→ ResearchAgent gathers information
→ MathAgent performs calculations
→ SupervisorAgent synthesizes results
```

## Configuration

The system can be configured through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4)
- `OPENAI_TEMPERATURE`: Temperature setting (default: 0.1)

## Development

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement `_setup_tools()` and `_get_system_prompt()`
3. Add the agent to the supervisor's registry
4. Update the handoff tool to include the new agent

### Adding New Tools

1. Create a tool function with the `@tool` decorator
2. Add it to the agent's `_setup_tools()` method
3. The tool will be automatically available to the agent

## Dependencies

Managed by `uv` package manager:

- **LangChain**: Core framework for agent creation
- **OpenAI**: LLM provider
- **Pydantic**: Data validation and settings
- **Python-dotenv**: Environment variable management
- **Requests**: HTTP requests for web search (mock)

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **ruff**: Fast Python linter


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions or issues, please open an issue on the GitHub repository.
