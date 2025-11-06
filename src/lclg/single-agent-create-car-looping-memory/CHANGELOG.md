# Changelog

All notable changes to the single-agent-create-car-looping project.

## [Unreleased]

### Added - 2025-10-03

#### Documentation
- **Added comprehensive dual-message system documentation**
  - Created `docs/DUAL_MESSAGE_SYSTEM.md` explaining how SystemMessage and HumanMessage work together
  - Documents the complete message flow in `base_agent.py`
  - Includes examples, benefits, and troubleshooting
  - Shows how prompts are formatted and sent to LLM

### Changed - 2025-10-03

#### Requirements Formatting in BaseAgent
- **Improved requirements formatting in `invoke_llm()` method**
  - Now formats requirements dict as readable bullet points
  - Changed from passing raw dict to formatted string
  - Format: `"- key: value"` for each requirement
  - Makes human message more readable for LLM

#### Prompt Template Refactoring
- **Moved human prompt template from `car_agent.py` to `src/prompts/prompts.py`**
  - Extracted the inline `human_prompt_template` definition from `CarAgent._setup_prompts()` method
  - Created `CAR_AGENT_HUMAN_PROMPT` constant in `src/prompts/prompts.py`
  - Updated `car_agent.py` to import and use `CAR_AGENT_HUMAN_PROMPT` instead of inline definition
  - Simplified `_setup_prompts()` method from ~95 lines to 5 lines

- **Benefits:**
  - All prompts now centralized in `src/prompts/prompts.py`
  - Easier to maintain and modify prompts
  - Better separation of concerns
  - Consistent with system prompt handling
  - Prompts can be reused across multiple agents if needed

- **Files Modified:**
  - `src/prompts/prompts.py`: Added `CAR_AGENT_HUMAN_PROMPT` template
  - `src/prompts/__init__.py`: Exported `CAR_AGENT_HUMAN_PROMPT`
  - `src/agents/car_agent.py`: Removed inline template, now imports from prompts module

- **Migration:**
  - No breaking changes
  - Functionality remains identical
  - Template content unchanged

## [0.1.0] - 2025-10-03

### Added
- Initial release of single-agent-create-car-looping
- Interactive session management with context memory
- LangChain prompt template integration
- Dual message system (SystemMessage + HumanMessage)
- ConversationMemory for short-term context
- CarAgent with all car creation tools
- CLI with interactive and single-request modes
- Comprehensive unit tests (20 tests)
- Complete documentation (README, QUICKSTART)
- Example requirement files

### Features
- Interactive looping with commands (reset, status, save, quit)
- Growing context passed through iterations
- Natural language input parsing
- Component validation and compatibility checking
- Performance metrics calculation
- Tool integration (8 tools for engine, body, electrical, tire)
- Logging with configurable levels
- Support for local and remote OLLAMA servers
