"""Comprehensive logging configuration for the single-agent car creation system."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console logging."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        """Format log record with colors for console output."""
        if hasattr(record, 'no_color') and record.no_color:
            return super().format(record)

        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"

        # Format the message
        formatted = super().format(record)

        return formatted


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'agent_name'):
            log_entry['agent_name'] = record.agent_name
        if hasattr(record, 'tool_name'):
            log_entry['tool_name'] = record.tool_name
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time

        return json.dumps(log_entry)


class LoggingConfig:
    """Centralized logging configuration manager."""

    DEFAULT_FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s'
    DETAILED_FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(funcName)s() %(message)s'

    @classmethod
    def setup_logging(
        cls,
        level: str = "INFO",
        log_to_console: bool = True,
        log_to_file: bool = False,
        log_file_path: Optional[str] = None,
        log_format: str = "standard",
        enable_colors: bool = True,
        json_format: bool = False,  # Default to text format
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        logger_configs: Optional[Dict[str, str]] = None
    ) -> logging.Logger:
        """
        Set up comprehensive logging configuration.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_console: Enable console logging
            log_to_file: Enable file logging
            log_file_path: Path to log file (auto-generated if None)
            log_format: Format style ('standard', 'detailed')
            enable_colors: Enable colored console output
            json_format: Use JSON formatting for file logs
            max_file_size: Maximum size for log files before rotation
            backup_count: Number of backup files to keep
            logger_configs: Custom logger configurations

        Returns:
            Configured root logger
        """
        # Convert string level to logging constant
        numeric_level = getattr(logging, level.upper(), logging.INFO)

        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(numeric_level)

        # Configure console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)

            # Always use text format for console, apply colors if enabled
            if enable_colors:
                console_formatter = ColoredFormatter(
                    cls.DETAILED_FORMAT if log_format == 'detailed' else cls.DEFAULT_FORMAT
                )
            else:
                console_formatter = logging.Formatter(
                    cls.DETAILED_FORMAT if log_format == 'detailed' else cls.DEFAULT_FORMAT
                )

            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # Configure file handler
        if log_to_file:
            if log_file_path is None:
                # Auto-generate log file path
                log_dir = Path("logs")
                log_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file_path = log_dir / f"car_agent_{timestamp}.log"

            log_file_path = Path(log_file_path)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)

            # Use JSON format only if explicitly requested, otherwise use text
            if json_format:
                file_formatter = JSONFormatter()
            else:
                file_formatter = logging.Formatter(cls.DETAILED_FORMAT)

            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Configure specific loggers if provided
        if logger_configs:
            for logger_name, logger_level in logger_configs.items():
                specific_logger = logging.getLogger(logger_name)
                specific_logger.setLevel(getattr(logging, logger_level.upper(), logging.INFO))

        # Set third-party library log levels to reduce noise
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('langchain').setLevel(logging.INFO)

        return root_logger

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance with the given name."""
        return logging.getLogger(name)

    @classmethod
    def log_execution_time(cls, logger: logging.Logger, operation: str, start_time: float, end_time: float):
        """Log execution time for operations."""
        execution_time = end_time - start_time
        logger.info(f"{operation} completed", extra={'execution_time': execution_time})

    @classmethod
    def log_agent_activity(cls, logger: logging.Logger, agent_name: str, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log agent-specific activities."""
        extra = {'agent_name': agent_name}
        if details:
            extra.update(details)
        logger.info(f"Agent activity: {activity}", extra=extra)

    @classmethod
    def log_tool_execution(cls, logger: logging.Logger, tool_name: str, action: str, result: Optional[str] = None):
        """Log tool execution activities."""
        extra = {'tool_name': tool_name}
        message = f"Tool {action}: {tool_name}"
        if result:
            message += f" -> {result[:100]}..."
        logger.info(message, extra=extra)

    @classmethod
    def create_request_logger(cls, request_id: str) -> logging.Logger:
        """Create a logger with request ID context."""
        logger = logging.getLogger(f"request.{request_id}")

        # Add request ID to all log records
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record

        logging.setLogRecordFactory(record_factory)
        return logger


class AgentLogger:
    """Specialized logger for agent operations."""

    # Reserved parameter names that conflict with logging methods
    RESERVED_PARAMS = {
        'msg', 'args', 'exc_info', 'extra', 'stack_info', 'stackLevel',
        'stacklevel', 'pathname', 'lineno', 'funcName', 'created',
        'msecs', 'relativeCreated', 'thread', 'threadName', 'processName',
        'process', 'module', 'filename', 'levelno', 'levelname', 'name',
        'getMessage', 'record', 'model', 'model_name', 'temperature', 'base_url'  # LLM params that conflict
    }

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")

    def _safe_extra(self, **kwargs):
        """Create safe extra dict by filtering out reserved parameter names."""
        safe_kwargs = {k: v for k, v in kwargs.items() if k not in self.RESERVED_PARAMS}
        return {'agent_name': self.agent_name, **safe_kwargs}

    def debug(self, message: str, **kwargs):
        """Log debug message with agent context."""
        self.logger.debug(message, extra=self._safe_extra(**kwargs))

    def info(self, message: str, **kwargs):
        """Log info message with agent context."""
        self.logger.info(message, extra=self._safe_extra(**kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with agent context."""
        self.logger.warning(message, extra=self._safe_extra(**kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with agent context."""
        self.logger.error(message, extra=self._safe_extra(**kwargs))

    def critical(self, message: str, **kwargs):
        """Log critical message with agent context."""
        self.logger.critical(message, extra=self._safe_extra(**kwargs))

    def log_component_creation(self, component_type: str, requirements: Dict[str, Any], success: bool = True):
        """Log component creation activities."""
        status = "success" if success else "failure"
        self.info(
            f"Component creation {status}: {component_type}",
            component_type=component_type,
            requirements=requirements,
            success=success
        )

    def log_tool_usage(self, tool_name: str, parameters: Dict[str, Any], result_summary: str):
        """Log tool usage with parameters and results."""
        self.info(
            f"Tool executed: {tool_name}",
            tool_name=tool_name,
            parameters=parameters,
            result_summary=result_summary
        )

    def log_validation(self, validation_type: str, success: bool, errors: Optional[list] = None):
        """Log validation activities."""
        status = "passed" if success else "failed"
        extra = {
            'validation_type': validation_type,
            'success': success
        }
        if errors:
            extra['errors'] = errors

        if success:
            self.info(f"Validation {status}: {validation_type}", **extra)
        else:
            self.warning(f"Validation {status}: {validation_type}", **extra)


class ToolLogger:
    """Specialized logger for tool operations."""

    # Reserved parameter names that conflict with logging methods
    RESERVED_PARAMS = {
        'msg', 'args', 'exc_info', 'extra', 'stack_info', 'stackLevel',
        'stacklevel', 'pathname', 'lineno', 'funcName', 'created',
        'msecs', 'relativeCreated', 'thread', 'threadName', 'processName',
        'process', 'module', 'filename', 'levelno', 'levelname', 'name',
        'getMessage', 'record', 'model', 'model_name', 'temperature', 'base_url'  # LLM params that conflict
    }

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.logger = logging.getLogger(f"tool.{tool_name}")

    def _safe_extra(self, **kwargs):
        """Create safe extra dict by filtering out reserved parameter names."""
        safe_kwargs = {k: v for k, v in kwargs.items() if k not in self.RESERVED_PARAMS}
        return {'tool_name': self.tool_name, **safe_kwargs}

    def debug(self, message: str, **kwargs):
        """Log debug message with tool context."""
        self.logger.debug(message, extra=self._safe_extra(**kwargs))

    def info(self, message: str, **kwargs):
        """Log info message with tool context."""
        self.logger.info(message, extra=self._safe_extra(**kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with tool context."""
        self.logger.warning(message, extra=self._safe_extra(**kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with tool context."""
        self.logger.error(message, extra=self._safe_extra(**kwargs))

    def log_execution(self, parameters: Dict[str, Any], result: Any, execution_time: float):
        """Log tool execution with timing."""
        self.info(
            f"Tool execution completed",
            parameters=parameters,
            result_type=type(result).__name__,
            execution_time=execution_time
        )

    def log_error_with_fallback(self, error: Exception, fallback_used: bool = False):
        """Log errors with fallback information."""
        self.error(
            f"Tool execution error: {str(error)}",
            error_type=type(error).__name__,
            fallback_used=fallback_used
        )


# Convenience function for quick setup
def setup_logging(level: str = "INFO", log_to_file: bool = False, **kwargs) -> logging.Logger:
    """Quick setup function for logging configuration."""
    return LoggingConfig.setup_logging(level=level, log_to_file=log_to_file, **kwargs)