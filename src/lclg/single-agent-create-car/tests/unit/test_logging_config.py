"""Unit tests for logging configuration module."""

import pytest
import logging
import json
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.logging_config import (
    LoggingConfig, ColoredFormatter, JSONFormatter,
    AgentLogger, ToolLogger, setup_logging
)


class TestColoredFormatter:
    """Test cases for ColoredFormatter."""

    def test_format_with_colors(self):
        """Test that formatter adds colors to log records."""
        formatter = ColoredFormatter('%(levelname)s %(message)s')
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert '\033[32m' in formatted  # Green color for INFO
        assert '\033[0m' in formatted   # Reset color

    def test_format_without_colors(self):
        """Test that formatter respects no_color attribute."""
        formatter = ColoredFormatter('%(levelname)s %(message)s')
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        record.no_color = True

        formatted = formatter.format(record)
        assert '\033[' not in formatted  # No ANSI codes

    def test_different_log_levels_colors(self):
        """Test that different log levels get different colors."""
        formatter = ColoredFormatter('%(levelname)s %(message)s')

        levels_and_colors = [
            (logging.DEBUG, '\033[36m'),    # Cyan
            (logging.INFO, '\033[32m'),     # Green
            (logging.WARNING, '\033[33m'),  # Yellow
            (logging.ERROR, '\033[31m'),    # Red
            (logging.CRITICAL, '\033[35m'), # Magenta
        ]

        for level, expected_color in levels_and_colors:
            record = logging.LogRecord(
                name="test", level=level, pathname="", lineno=0,
                msg="Test message", args=(), exc_info=None
            )
            formatted = formatter.format(record)
            assert expected_color in formatted


class TestJSONFormatter:
    """Test cases for JSONFormatter."""

    def test_basic_json_format(self):
        """Test basic JSON formatting."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger", level=logging.INFO, pathname="test.py",
            lineno=42, msg="Test message", args=(), exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data['level'] == 'INFO'
        assert data['logger'] == 'test_logger'
        assert data['message'] == 'Test message'
        assert data['module'] == 'test_module'
        assert data['function'] == 'test_function'
        assert data['line'] == 42
        assert 'timestamp' in data

    def test_json_format_with_extra_fields(self):
        """Test JSON formatting with additional fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        record.agent_name = "test_agent"
        record.tool_name = "test_tool"
        record.request_id = "req_123"
        record.execution_time = 1.5

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data['agent_name'] == 'test_agent'
        assert data['tool_name'] == 'test_tool'
        assert data['request_id'] == 'req_123'
        assert data['execution_time'] == 1.5


class TestLoggingConfig:
    """Test cases for LoggingConfig class."""

    def setup_method(self):
        """Reset logging configuration before each test."""
        # Clear all handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.WARNING)

    def test_setup_logging_console_only(self):
        """Test setting up console-only logging."""
        logger = LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=True,
            log_to_file=False
        )

        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_file_only(self, temporary_log_dir):
        """Test setting up file-only logging."""
        log_file = temporary_log_dir / "test.log"

        logger = LoggingConfig.setup_logging(
            level="DEBUG",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file)
        )

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert log_file.exists()

    def test_setup_logging_both_outputs(self, temporary_log_dir):
        """Test setting up both console and file logging."""
        log_file = temporary_log_dir / "test.log"

        logger = LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=True,
            log_to_file=True,
            log_file_path=str(log_file)
        )

        assert len(logger.handlers) == 2
        handler_types = [type(h) for h in logger.handlers]
        assert logging.StreamHandler in handler_types
        assert logging.handlers.RotatingFileHandler in handler_types

    def test_setup_logging_with_json_format(self, temporary_log_dir):
        """Test setting up logging with JSON format."""
        log_file = temporary_log_dir / "test.log"

        LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file),
            json_format=True
        )

        # Find the file handler
        root_logger = logging.getLogger()
        file_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert isinstance(file_handler.formatter, JSONFormatter)

    def test_setup_logging_with_colors(self):
        """Test setting up logging with colored output."""
        LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=True,
            log_to_file=False,
            enable_colors=True
        )

        root_logger = logging.getLogger()
        console_handler = root_logger.handlers[0]
        assert isinstance(console_handler.formatter, ColoredFormatter)

    def test_setup_logging_different_levels(self):
        """Test setting up logging with different levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        expected_levels = [logging.DEBUG, logging.INFO, logging.WARNING,
                          logging.ERROR, logging.CRITICAL]

        for level_str, expected_level in zip(levels, expected_levels):
            self.setup_method()  # Reset
            logger = LoggingConfig.setup_logging(level=level_str)
            assert logger.level == expected_level

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = LoggingConfig.get_logger("test_logger")
        assert logger.name == "test_logger"
        assert isinstance(logger, logging.Logger)

    def test_log_execution_time(self):
        """Test logging execution time."""
        with patch('logging.Logger.info') as mock_info:
            logger = logging.getLogger("test")
            LoggingConfig.log_execution_time(logger, "test_operation", 1.0, 3.5)

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "test_operation completed" in args[0]
            assert 'extra' in kwargs
            assert 'execution_time' in kwargs['extra']

    def test_log_agent_activity(self):
        """Test logging agent activity."""
        with patch('logging.Logger.info') as mock_info:
            logger = logging.getLogger("test")
            LoggingConfig.log_agent_activity(
                logger, "test_agent", "test_activity", {"key": "value"}
            )

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Agent activity: test_activity" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['agent_name'] == 'test_agent'
            assert kwargs['extra']['key'] == 'value'

    def test_log_tool_execution(self):
        """Test logging tool execution."""
        with patch('logging.Logger.info') as mock_info:
            logger = logging.getLogger("test")
            LoggingConfig.log_tool_execution(
                logger, "test_tool", "executed", "result_data"
            )

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Tool executed: test_tool" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['tool_name'] == 'test_tool'


class TestAgentLogger:
    """Test cases for AgentLogger."""

    def test_agent_logger_initialization(self):
        """Test AgentLogger initialization."""
        agent_logger = AgentLogger("test_agent")
        assert agent_logger.agent_name == "test_agent"
        assert agent_logger.logger.name == "agent.test_agent"

    def test_agent_logger_methods(self):
        """Test AgentLogger logging methods."""
        agent_logger = AgentLogger("test_agent")

        with patch.object(agent_logger.logger, 'info') as mock_info:
            agent_logger.info("Test message", custom_key="custom_value")

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert args[0] == "Test message"
            assert 'extra' in kwargs
            assert kwargs['extra']['agent_name'] == 'test_agent'
            assert kwargs['extra']['custom_key'] == 'custom_value'

    def test_log_component_creation(self):
        """Test logging component creation."""
        agent_logger = AgentLogger("test_agent")
        requirements = {"vehicle_type": "sedan"}

        with patch.object(agent_logger.logger, 'info') as mock_info:
            agent_logger.log_component_creation("engine", requirements, success=True)

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Component creation success: engine" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['component_type'] == 'engine'
            assert kwargs['extra']['requirements'] == requirements
            assert kwargs['extra']['success'] is True

    def test_log_tool_usage(self):
        """Test logging tool usage."""
        agent_logger = AgentLogger("test_agent")
        parameters = {"param1": "value1"}

        with patch.object(agent_logger.logger, 'info') as mock_info:
            agent_logger.log_tool_usage("test_tool", parameters, "success")

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Tool executed: test_tool" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['tool_name'] == 'test_tool'
            assert kwargs['extra']['parameters'] == parameters

    def test_log_validation(self):
        """Test logging validation results."""
        agent_logger = AgentLogger("test_agent")

        # Test successful validation
        with patch.object(agent_logger.logger, 'info') as mock_info:
            agent_logger.log_validation("schema", success=True)
            mock_info.assert_called_once()

        # Test failed validation
        with patch.object(agent_logger.logger, 'warning') as mock_warning:
            agent_logger.log_validation("schema", success=False, errors=["error1"])
            mock_warning.assert_called_once()


class TestToolLogger:
    """Test cases for ToolLogger."""

    def test_tool_logger_initialization(self):
        """Test ToolLogger initialization."""
        tool_logger = ToolLogger("test_tool")
        assert tool_logger.tool_name == "test_tool"
        assert tool_logger.logger.name == "tool.test_tool"

    def test_tool_logger_methods(self):
        """Test ToolLogger logging methods."""
        tool_logger = ToolLogger("test_tool")

        with patch.object(tool_logger.logger, 'debug') as mock_debug:
            tool_logger.debug("Debug message", extra_param="value")

            mock_debug.assert_called_once()
            args, kwargs = mock_debug.call_args
            assert args[0] == "Debug message"
            assert 'extra' in kwargs
            assert kwargs['extra']['tool_name'] == 'test_tool'
            assert kwargs['extra']['extra_param'] == 'value'

    def test_log_execution(self):
        """Test logging tool execution."""
        tool_logger = ToolLogger("test_tool")
        parameters = {"input": "value"}
        result = {"output": "result"}

        with patch.object(tool_logger.logger, 'info') as mock_info:
            tool_logger.log_execution(parameters, result, 1.5)

            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Tool execution completed" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['parameters'] == parameters
            assert kwargs['extra']['execution_time'] == 1.5

    def test_log_error_with_fallback(self):
        """Test logging errors with fallback information."""
        tool_logger = ToolLogger("test_tool")
        error = ValueError("Test error")

        with patch.object(tool_logger.logger, 'error') as mock_error:
            tool_logger.log_error_with_fallback(error, fallback_used=True)

            mock_error.assert_called_once()
            args, kwargs = mock_error.call_args
            assert "Tool execution error: Test error" in args[0]
            assert 'extra' in kwargs
            assert kwargs['extra']['error_type'] == 'ValueError'
            assert kwargs['extra']['fallback_used'] is True


class TestSetupLogging:
    """Test cases for setup_logging convenience function."""

    def setup_method(self):
        """Reset logging configuration before each test."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_setup_logging_convenience_function(self):
        """Test the convenience setup_logging function."""
        logger = setup_logging(level="DEBUG", log_to_file=False)

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1  # Console only

    def test_setup_logging_with_file(self, temporary_log_dir):
        """Test setup_logging with file output."""
        log_file = temporary_log_dir / "convenience.log"

        logger = setup_logging(
            level="INFO",
            log_to_file=True,
            log_file_path=str(log_file)
        )

        assert len(logger.handlers) == 2  # Console + file
        assert log_file.exists()


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_logging_integration_with_file_output(self, temporary_log_dir):
        """Test complete logging integration with file output."""
        log_file = temporary_log_dir / "integration.log"

        # Setup logging
        LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file),
            json_format=False
        )

        # Create logger and log messages
        logger = logging.getLogger("integration_test")
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Verify file content
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test info message" in content
        assert "Test warning message" in content
        assert "Test error message" in content
        assert "integration_test" in content

    def test_logging_integration_with_json_output(self, temporary_log_dir):
        """Test logging integration with JSON format."""
        log_file = temporary_log_dir / "json_integration.log"

        # Setup JSON logging
        LoggingConfig.setup_logging(
            level="INFO",
            log_to_console=False,
            log_to_file=True,
            log_file_path=str(log_file),
            json_format=True
        )

        # Log with extra fields
        logger = logging.getLogger("json_test")
        logger.info("JSON test message", extra={
            'agent_name': 'test_agent',
            'custom_field': 'custom_value'
        })

        # Verify JSON format
        assert log_file.exists()
        content = log_file.read_text().strip()
        data = json.loads(content)

        assert data['message'] == "JSON test message"
        assert data['logger'] == "json_test"
        assert 'timestamp' in data