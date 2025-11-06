# Memory Refactoring Guide

## Overview

This document describes the refactoring of the single-agent-create-car-looping-memory project to use LangChain's short-term memory management framework instead of the custom `ConversationMemory` class.

## What Changed

### 1. Dependencies (pyproject.toml)

**Added:**
- `langchain-community` - LangChain community integrations including PostgreSQL support
- `psycopg2-binary>=2.9.0` - PostgreSQL database adapter
- `sqlalchemy>=2.0.0` - SQL toolkit for PostgreSQL backend

### 2. New Memory Manager Module

**Created:** `src/memory/memory_manager.py`

This module provides:

- **MemoryBackendConfig**: Pydantic model for memory configuration
- **MemoryManager**: Abstract base class for memory management
- **InMemoryManager**: In-memory implementation using LangChain's `InMemoryChatMessageHistory`
- **PostgresMemoryManager**: PostgreSQL implementation using LangChain's `PostgresChatMessageHistory`
- **create_memory_manager()**: Factory function for creating memory managers

**Key Features:**
- Sliding window memory management (configurable message limit)
- Context data storage (key-value pairs)
- Unified interface for both in-memory and PostgreSQL backends
- Compatible with LangChain v1.0.0 message types (`HumanMessage`, `AIMessage`, etc.)

### 3. BaseAgent Refactoring

**Changes in `src/agents/base_agent.py`:**

1. **Removed** the custom `ConversationMemory` class
2. **Added** `MemoryManager` integration:
   - New constructor parameters: `memory_config`, `max_memory_messages`
   - Uses `create_memory_manager()` factory to initialize memory
3. **Updated** all memory operations to use `MemoryManager` interface:
   - `self.memory.add_message()` now takes LangChain `BaseMessage` objects
   - `self.memory.get_messages()` returns list of LangChain messages
   - `self.memory.get_all_context()` returns context dictionary
   - `self.memory.get_context_summary()` returns formatted context string

### 4. CarAgent Updates

**Changes in `src/agents/car_agent.py`:**

- Updated references from `self.memory.context_data` to `self.memory.get_all_context()`
- Updated references from `self.memory.messages` to `self.memory.get_messages()`
- No changes to business logic - all functionality preserved

### 5. SingleAgentSystem Enhancements

**Changes in `src/single_agent_system.py`:**

1. **New constructor parameters:**
   - `memory_backend`: "memory" (default) or "postgres"
   - `memory_connection_string`: PostgreSQL connection string
   - `memory_session_id`: Session identifier for memory isolation
   - `max_memory_messages`: Sliding window size (default: 10)

2. **Memory configuration:**
   - Creates `MemoryBackendConfig` based on parameters
   - Passes configuration to `CarAgent` constructor

3. **Updated methods:**
   - `_handle_status()`: Shows memory backend and uses `get_all_context()`
   - `_handle_save()`: Converts LangChain messages to serializable format

### 6. CLI Enhancements

**Changes in `cli.py`:**

**New global arguments:**
```bash
--memory-backend {memory,postgres}  # Memory backend type (default: memory)
--memory-connection-string STRING   # PostgreSQL connection string
--memory-session-id STRING          # Session ID (default: "default")
--max-memory-messages INT           # Message window size (default: 10)
```

**Updated examples:**
- In-memory usage (default)
- PostgreSQL usage with connection string
- Custom memory window sizes

## Usage Examples

### 1. In-Memory Backend (Default)

```bash
# Run interactive session with default in-memory backend
python cli.py interactive

# With custom message window
python cli.py interactive --max-memory-messages 20
```

### 2. PostgreSQL Backend

**Prerequisites:**
- PostgreSQL server running
- Database created
- Connection credentials available

**Connection string format:**
```
postgresql://username:password@hostname:port/database_name
```

**Example usage:**
```bash
# Interactive session with PostgreSQL
python cli.py interactive \
  --memory-backend postgres \
  --memory-connection-string "postgresql://user:pass@localhost:5432/car_agent" \
  --memory-session-id "user123"

# Single request with PostgreSQL
python cli.py single \
  --vehicle-type suv \
  --performance-level performance \
  --memory-backend postgres \
  --memory-connection-string "postgresql://user:pass@localhost:5432/car_agent" \
  --memory-session-id "session_001"
```

### 3. Programmatic Usage

```python
from memory.memory_manager import MemoryBackendConfig, create_memory_manager
from langchain_core.messages import HumanMessage, AIMessage

# In-memory backend
config = MemoryBackendConfig(backend_type="memory")
memory = create_memory_manager(config, max_messages=10)

# Add messages
memory.add_message(HumanMessage(content="Hello"))
memory.add_message(AIMessage(content="Hi there!"))

# Add context
memory.add_context("user_preference", "sports_car")

# Get messages and context
messages = memory.get_messages()
context = memory.get_all_context()
summary = memory.get_context_summary()

# PostgreSQL backend
pg_config = MemoryBackendConfig(
    backend_type="postgres",
    connection_string="postgresql://user:pass@localhost:5432/mydb",
    session_id="user_session_123"
)
pg_memory = create_memory_manager(pg_config, max_messages=10)
```

## Architecture

### Memory Manager Interface

```python
class MemoryManager(ABC):
    @abstractmethod
    def add_message(self, message: BaseMessage):
        """Add a message to memory."""
        pass

    @abstractmethod
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from memory."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all messages from memory."""
        pass

    @abstractmethod
    def add_context(self, key: str, value: Any):
        """Add contextual data to memory."""
        pass

    @abstractmethod
    def get_context(self, key: str) -> Optional[Any]:
        """Get contextual data from memory."""
        pass

    @abstractmethod
    def get_context_summary(self) -> str:
        """Get a formatted summary of accumulated context."""
        pass

    @abstractmethod
    def get_all_context(self) -> Dict[str, Any]:
        """Get all contextual data."""
        pass
```

### Sliding Window Memory

Both in-memory and PostgreSQL implementations support sliding window memory management:

- Configurable maximum message count (default: 10)
- Automatically removes oldest messages when limit is exceeded
- Maintains most recent conversation history
- Improves performance and reduces storage requirements

## PostgreSQL Setup

### 1. Install PostgreSQL

```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql
sudo service postgresql start
```

### 2. Create Database

```sql
CREATE DATABASE car_agent;
CREATE USER car_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE car_agent TO car_user;
```

### 3. Table Creation

The PostgreSQL memory manager automatically creates the required table on first use:
- Table name: `chat_message_history` (configurable)
- Columns: `session_id`, `message` (JSON), `created_at`

## Migration from Old Code

If you have existing code using the old `ConversationMemory` class:

### Before (Old API):
```python
from agents.base_agent import ConversationMemory

memory = ConversationMemory(max_history=10)
memory.add_message("human", "Hello")
memory.add_message("assistant", "Hi there!")
messages = memory.get_messages()  # Returns list of dicts
context = memory.context_data  # Direct attribute access
```

### After (New API):
```python
from memory.memory_manager import MemoryBackendConfig, create_memory_manager
from langchain_core.messages import HumanMessage, AIMessage

config = MemoryBackendConfig(backend_type="memory")
memory = create_memory_manager(config, max_messages=10)
memory.add_message(HumanMessage(content="Hello"))
memory.add_message(AIMessage(content="Hi there!"))
messages = memory.get_messages()  # Returns list of BaseMessage objects
context = memory.get_all_context()  # Method call
```

## Benefits of Refactoring

1. **LangChain Integration**: Native support for LangChain memory framework
2. **Flexibility**: Easy switching between in-memory and PostgreSQL backends
3. **Scalability**: PostgreSQL backend supports multiple sessions and persistence
4. **Compatibility**: Works with LangChain v1.0.0 and `create_agent` API
5. **Maintainability**: Uses standard LangChain patterns and message types
6. **Type Safety**: Better type hints with Pydantic models
7. **Extensibility**: Easy to add new memory backends (Redis, MongoDB, etc.)

## Testing

Run the test suite:

```bash
python test_memory_refactor.py
```

Tests verify:
- ✓ InMemoryManager functionality
- ✓ Sliding window memory management
- ✓ Context data management
- ✓ Memory clearing
- ✓ Integration with BaseAgent
- ✓ PostgreSQL configuration

## Troubleshooting

### Import Errors

**Error:** `ImportError: cannot import name 'PostgresChatMessageHistory'`

**Solution:** Install langchain-community:
```bash
uv sync
# or
pip install langchain-community
```

### PostgreSQL Connection Errors

**Error:** `Could not connect to PostgreSQL`

**Checklist:**
1. PostgreSQL server is running
2. Connection string is correct
3. Database exists
4. User has proper permissions
5. Network/firewall allows connection

**Test connection:**
```bash
psql "postgresql://user:pass@localhost:5432/car_agent"
```

### Memory Not Persisting

**For in-memory backend:** This is expected - memory is cleared when the process ends.

**For PostgreSQL backend:** Check that:
1. Connection string is valid
2. Session ID is consistent across runs
3. Database user has write permissions

## Future Enhancements

Potential improvements:

1. **Redis Backend**: For distributed caching
2. **MongoDB Backend**: For document-based storage
3. **Hybrid Memory**: Short-term (in-memory) + long-term (PostgreSQL)
4. **Memory Summarization**: Compress old messages using LLM
5. **Multi-Session Management**: Session switching and merging
6. **Memory Analytics**: Usage statistics and insights

## References

- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)
- [LangChain Community Chat Message Histories](https://python.langchain.com/docs/integrations/memory/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [LangChain v1.0.0 Migration Guide](https://python.langchain.com/docs/versions/v0_2/)

## Support

For issues or questions:
1. Check this guide first
2. Review test_memory_refactor.py for examples
3. Check LangChain documentation
4. Review PostgreSQL connection settings
