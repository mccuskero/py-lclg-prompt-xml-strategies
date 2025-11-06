"""Memory manager using LangChain's memory framework for agent conversations."""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class MemoryBackendConfig(BaseModel):
    """Configuration for memory backend."""
    backend_type: str = Field(default="memory", description="Type of backend: 'memory' or 'postgres'")
    connection_string: Optional[str] = Field(default=None, description="PostgreSQL connection string")
    session_id: str = Field(default="default", description="Session identifier for memory isolation")
    table_name: str = Field(default="chat_message_history", description="Table name for PostgreSQL backend")


class MemoryManager(ABC):
    """Abstract base class for memory management."""

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


class InMemoryManager(MemoryManager):
    """In-memory implementation of MemoryManager using LangChain's InMemoryChatMessageHistory."""

    def __init__(self, max_messages: int = 10):
        """
        Initialize in-memory manager.

        Args:
            max_messages: Maximum number of messages to keep in history (window size)
        """
        self.chat_history: BaseChatMessageHistory = InMemoryChatMessageHistory()
        self.max_messages = max_messages
        self.context_data: Dict[str, Any] = {}
        logger.info(f"Initialized InMemoryManager with max_messages={max_messages}")

    def add_message(self, message: BaseMessage):
        """Add a message to memory with window management."""
        self.chat_history.add_message(message)

        # Implement sliding window
        messages = self.chat_history.messages
        if len(messages) > self.max_messages:
            # Keep only the last max_messages
            self.chat_history.clear()
            for msg in messages[-self.max_messages:]:
                self.chat_history.add_message(msg)

        logger.debug(f"Added message to memory. Total messages: {len(self.chat_history.messages)}")

    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from memory."""
        return self.chat_history.messages

    def clear(self):
        """Clear all messages and context from memory."""
        self.chat_history.clear()
        self.context_data.clear()
        logger.info("Cleared in-memory storage")

    def add_context(self, key: str, value: Any):
        """Add contextual data to memory."""
        self.context_data[key] = value
        logger.debug(f"Added context: {key}={value}")

    def get_context(self, key: str) -> Optional[Any]:
        """Get contextual data from memory."""
        return self.context_data.get(key)

    def get_context_summary(self) -> str:
        """Get a formatted summary of accumulated context."""
        if not self.context_data:
            return "No context accumulated yet."

        summary = "Accumulated Context:\n"
        for key, value in self.context_data.items():
            summary += f"- {key}: {value}\n"
        return summary

    def get_all_context(self) -> Dict[str, Any]:
        """Get all contextual data."""
        return self.context_data.copy()


class PostgresMemoryManager(MemoryManager):
    """PostgreSQL implementation of MemoryManager using LangChain's PostgresChatMessageHistory."""

    def __init__(
        self,
        connection_string: str,
        session_id: str = "default",
        table_name: str = "chat_message_history",
        max_messages: int = 10
    ):
        """
        Initialize PostgreSQL memory manager.

        Args:
            connection_string: PostgreSQL connection string
            session_id: Session identifier for memory isolation
            table_name: Table name for storing messages
            max_messages: Maximum number of messages to keep in history (window size)
        """
        try:
            from langchain_community.chat_message_histories import PostgresChatMessageHistory

            self.chat_history = PostgresChatMessageHistory(
                connection_string=connection_string,
                session_id=session_id,
                table_name=table_name
            )
            self.max_messages = max_messages
            self.session_id = session_id

            # Context data stored separately in a dict (could be extended to use Postgres)
            self.context_data: Dict[str, Any] = {}

            logger.info(
                f"Initialized PostgresMemoryManager",
                extra={
                    "session_id": session_id,
                    "table_name": table_name,
                    "max_messages": max_messages
                }
            )
        except ImportError as e:
            logger.error("langchain-community not installed. Install with: pip install langchain-community")
            raise ImportError(
                "PostgresMemoryManager requires langchain-community. "
                "Install with: pip install langchain-community psycopg2-binary"
            ) from e

    def add_message(self, message: BaseMessage):
        """Add a message to PostgreSQL storage with window management."""
        self.chat_history.add_message(message)

        # Implement sliding window
        messages = self.chat_history.messages
        if len(messages) > self.max_messages:
            # Clear and re-add only the last max_messages
            self.chat_history.clear()
            for msg in messages[-self.max_messages:]:
                self.chat_history.add_message(msg)

        logger.debug(f"Added message to PostgreSQL. Session: {self.session_id}, Total messages: {len(messages)}")

    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from PostgreSQL storage."""
        return self.chat_history.messages

    def clear(self):
        """Clear all messages from PostgreSQL storage and context."""
        self.chat_history.clear()
        self.context_data.clear()
        logger.info(f"Cleared PostgreSQL storage for session: {self.session_id}")

    def add_context(self, key: str, value: Any):
        """Add contextual data to memory (stored in-memory, could be extended to Postgres)."""
        self.context_data[key] = value
        logger.debug(f"Added context to session {self.session_id}: {key}={value}")

    def get_context(self, key: str) -> Optional[Any]:
        """Get contextual data from memory."""
        return self.context_data.get(key)

    def get_context_summary(self) -> str:
        """Get a formatted summary of accumulated context."""
        if not self.context_data:
            return "No context accumulated yet."

        summary = "Accumulated Context:\n"
        for key, value in self.context_data.items():
            summary += f"- {key}: {value}\n"
        return summary

    def get_all_context(self) -> Dict[str, Any]:
        """Get all contextual data."""
        return self.context_data.copy()


def create_memory_manager(config: MemoryBackendConfig, max_messages: int = 10) -> MemoryManager:
    """
    Factory function to create a memory manager based on configuration.

    Args:
        config: Memory backend configuration
        max_messages: Maximum number of messages to keep in history

    Returns:
        MemoryManager instance (InMemoryManager or PostgresMemoryManager)

    Raises:
        ValueError: If backend_type is not supported
    """
    if config.backend_type == "memory":
        logger.info("Creating in-memory manager")
        return InMemoryManager(max_messages=max_messages)

    elif config.backend_type == "postgres":
        if not config.connection_string:
            raise ValueError("PostgreSQL connection string is required for 'postgres' backend")

        logger.info("Creating PostgreSQL memory manager")
        return PostgresMemoryManager(
            connection_string=config.connection_string,
            session_id=config.session_id,
            table_name=config.table_name,
            max_messages=max_messages
        )

    else:
        raise ValueError(f"Unsupported backend_type: {config.backend_type}. Use 'memory' or 'postgres'")
