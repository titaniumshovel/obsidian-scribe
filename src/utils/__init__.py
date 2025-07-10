"""
Utility modules for Obsidian Scribe.

Provides logging, exceptions, validation, and helper functions.
"""

from .logger import setup_logging, get_logger
from .exceptions import (
    ObsidianScribeError,
    ConfigurationError,
    ProcessingError,
    TranscriptionError,
    DiarizationError,
    FileNotFoundError,
    ValidationError
)
from .validators import (
    validate_audio_file,
    validate_config,
    validate_path,
    validate_url
)
from .helpers import (
    format_duration,
    format_timestamp,
    sanitize_filename,
    get_file_hash,
    retry_with_backoff
)

__all__ = [
    # Logger
    'setup_logging',
    'get_logger',
    
    # Exceptions
    'ObsidianScribeError',
    'ConfigurationError',
    'ProcessingError',
    'TranscriptionError',
    'DiarizationError',
    'FileNotFoundError',
    'ValidationError',
    
    # Validators
    'validate_audio_file',
    'validate_config',
    'validate_path',
    'validate_url',
    
    # Helpers
    'format_duration',
    'format_timestamp',
    'sanitize_filename',
    'get_file_hash',
    'retry_with_backoff'
]