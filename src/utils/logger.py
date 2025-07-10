"""
Logging configuration and utilities for Obsidian Scribe.

Provides centralized logging setup with file rotation, formatting, and
different log levels for console and file output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            
        # Format the message
        result = super().format(record)
        
        # Reset levelname for other handlers
        record.levelname = levelname
        
        return result


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename',
                          'funcName', 'levelname', 'levelno', 'lineno',
                          'module', 'msecs', 'pathname', 'process',
                          'processName', 'relativeCreated', 'thread',
                          'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
                
        return json.dumps(log_data)


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        config: Optional configuration dictionary
    """
    if config is None:
        config = {}
        
    # Get logging configuration
    log_config = config.get('logging', {})
    
    # Log levels
    console_level = log_config.get('console_level', 'INFO')
    file_level = log_config.get('file_level', 'DEBUG')
    
    # Log directory
    log_dir = Path(log_config.get('log_dir', './logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all, filter in handlers
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper()))
    
    # Use colored formatter for console if not disabled
    if log_config.get('use_colors', True) and sys.stdout.isatty():
        console_format = log_config.get(
            'console_format',
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        console_formatter = ColoredFormatter(console_format)
    else:
        console_format = log_config.get(
            'console_format',
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        console_formatter = logging.Formatter(console_format)
        
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_dir / 'obsidian_scribe.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_config.get('max_bytes', 10 * 1024 * 1024),  # 10MB default
        backupCount=log_config.get('backup_count', 5)
    )
    file_handler.setLevel(getattr(logging, file_level.upper()))
    
    # File format
    file_format = log_config.get(
        'file_format',
        '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # JSON file handler for structured logs (optional)
    if log_config.get('enable_json_logs', False):
        json_file = log_dir / 'obsidian_scribe.json'
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=log_config.get('max_bytes', 10 * 1024 * 1024),
            backupCount=log_config.get('backup_count', 5)
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)
        
    # Error file handler (errors and above)
    error_file = log_dir / 'obsidian_scribe_errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=log_config.get('max_bytes', 10 * 1024 * 1024),
        backupCount=log_config.get('backup_count', 5)
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Set levels for specific loggers
    logger_levels = log_config.get('logger_levels', {})
    for logger_name, level in logger_levels.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))
        
    # Suppress noisy loggers
    for logger_name in log_config.get('suppress_loggers', []):
        logging.getLogger(logger_name).setLevel(logging.WARNING)
        
    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
    logger.debug(f"Log directory: {log_dir}")
    

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, logger: logging.Logger, **kwargs):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            **kwargs: Context variables to add
        """
        self.logger = logger
        self.context = kwargs
        self.old_factory = None
        
    def __enter__(self):
        """Enter context."""
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
            
        logging.setLogRecordFactory(record_factory)
        self.old_factory = old_factory
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)
            

def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {e}", exc_info=True)
                raise
                
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger):
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"{func_name} completed in {elapsed:.2f} seconds")
                return result
            except Exception:
                elapsed = time.time() - start_time
                logger.error(f"{func_name} failed after {elapsed:.2f} seconds")
                raise
                
        return wrapper
    return decorator


class ProgressLogger:
    """Helper class for logging progress of long-running operations."""
    
    def __init__(self, logger: logging.Logger, total: int, 
                 description: str = "Processing"):
        """
        Initialize progress logger.
        
        Args:
            logger: Logger instance
            total: Total number of items
            description: Description of the operation
        """
        self.logger = logger
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = datetime.now()
        
    def update(self, increment: int = 1, message: Optional[str] = None):
        """
        Update progress.
        
        Args:
            increment: Number of items completed
            message: Optional progress message
        """
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / rate if rate > 0 else 0
        
        log_message = (
            f"{self.description}: {self.current}/{self.total} "
            f"({percentage:.1f}%) - Rate: {rate:.1f}/s - ETA: {eta:.1f}s"
        )
        
        if message:
            log_message += f" - {message}"
            
        self.logger.info(log_message)
        
    def complete(self, message: Optional[str] = None):
        """Mark operation as complete."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        log_message = (
            f"{self.description} completed: {self.current} items "
            f"in {elapsed:.1f} seconds"
        )
        
        if message:
            log_message += f" - {message}"
            
        self.logger.info(log_message)