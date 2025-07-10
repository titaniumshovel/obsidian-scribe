"""
Custom exceptions for Obsidian Scribe.

Provides a hierarchy of exceptions for different error scenarios.
"""

from typing import Optional, Dict, Any


class ObsidianScribeError(Exception):
    """Base exception for all Obsidian Scribe errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
    def __str__(self):
        """String representation of the error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(ObsidianScribeError):
    """Raised when there's an error in configuration."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 config_value: Any = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Invalid configuration value
        """
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = config_value
            
        super().__init__(message, details)


class ProcessingError(ObsidianScribeError):
    """Raised when there's an error during file processing."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 stage: Optional[str] = None, error_type: Optional[str] = None):
        """
        Initialize processing error.
        
        Args:
            message: Error message
            file_path: Path to the file being processed
            stage: Processing stage where error occurred
            error_type: Type of processing error
        """
        details = {}
        if file_path:
            details['file_path'] = file_path
        if stage:
            details['stage'] = stage
        if error_type:
            details['error_type'] = error_type
            
        super().__init__(message, details)


class TranscriptionError(ProcessingError):
    """Raised when there's an error during transcription."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 api_error: Optional[str] = None, status_code: Optional[int] = None):
        """
        Initialize transcription error.
        
        Args:
            message: Error message
            file_path: Path to the audio file
            api_error: API error message if applicable
            status_code: HTTP status code if applicable
        """
        super().__init__(message, file_path, stage='transcription')
        
        if api_error:
            self.details['api_error'] = api_error
        if status_code:
            self.details['status_code'] = status_code


class DiarizationError(ProcessingError):
    """Raised when there's an error during speaker diarization."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 model_error: Optional[str] = None):
        """
        Initialize diarization error.
        
        Args:
            message: Error message
            file_path: Path to the audio file
            model_error: Model-specific error message
        """
        super().__init__(message, file_path, stage='diarization')
        
        if model_error:
            self.details['model_error'] = model_error


class FileNotFoundError(ObsidianScribeError):
    """Raised when a required file is not found."""
    
    def __init__(self, file_path: str, file_type: Optional[str] = None):
        """
        Initialize file not found error.
        
        Args:
            file_path: Path to the missing file
            file_type: Type of file (e.g., 'audio', 'config', 'template')
        """
        message = f"File not found: {file_path}"
        details = {'file_path': file_path}
        
        if file_type:
            details['file_type'] = file_type
            message = f"{file_type.capitalize()} file not found: {file_path}"
            
        super().__init__(message, details)


class ValidationError(ObsidianScribeError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Any = None, expected: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            expected: Expected value or format
        """
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
        if expected:
            details['expected'] = expected
            
        super().__init__(message, details)


class AudioFormatError(ValidationError):
    """Raised when audio format is invalid or unsupported."""
    
    def __init__(self, file_path: str, format: Optional[str] = None,
                 supported_formats: Optional[list] = None):
        """
        Initialize audio format error.
        
        Args:
            file_path: Path to the audio file
            format: Detected format
            supported_formats: List of supported formats
        """
        message = f"Unsupported audio format: {file_path}"
        
        super().__init__(message, field='audio_format', value=format)
        
        self.details['file_path'] = file_path
        if supported_formats:
            self.details['supported_formats'] = supported_formats


class StorageError(ObsidianScribeError):
    """Raised when there's an error with storage operations."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 path: Optional[str] = None):
        """
        Initialize storage error.
        
        Args:
            message: Error message
            operation: Storage operation that failed
            path: Path involved in the operation
        """
        details = {}
        if operation:
            details['operation'] = operation
        if path:
            details['path'] = path
            
        super().__init__(message, details)


class CacheError(StorageError):
    """Raised when there's an error with cache operations."""
    
    def __init__(self, message: str, cache_key: Optional[str] = None):
        """
        Initialize cache error.
        
        Args:
            message: Error message
            cache_key: Cache key involved
        """
        super().__init__(message, operation='cache')
        
        if cache_key:
            self.details['cache_key'] = cache_key


class ArchiveError(StorageError):
    """Raised when there's an error with archive operations."""
    
    def __init__(self, message: str, archive_path: Optional[str] = None):
        """
        Initialize archive error.
        
        Args:
            message: Error message
            archive_path: Archive path involved
        """
        super().__init__(message, operation='archive', path=archive_path)


class StateError(ObsidianScribeError):
    """Raised when there's an error with state management."""
    
    def __init__(self, message: str, state: Optional[str] = None,
                 file_path: Optional[str] = None):
        """
        Initialize state error.
        
        Args:
            message: Error message
            state: Current state
            file_path: File path involved
        """
        details = {}
        if state:
            details['state'] = state
        if file_path:
            details['file_path'] = file_path
            
        super().__init__(message, details)


class QueueError(ObsidianScribeError):
    """Raised when there's an error with queue operations."""
    
    def __init__(self, message: str, queue_size: Optional[int] = None):
        """
        Initialize queue error.
        
        Args:
            message: Error message
            queue_size: Current queue size
        """
        details = {}
        if queue_size is not None:
            details['queue_size'] = queue_size
            
        super().__init__(message, details)


class NetworkError(ObsidianScribeError):
    """Raised when there's a network-related error."""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 status_code: Optional[int] = None, timeout: Optional[float] = None):
        """
        Initialize network error.
        
        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code
            timeout: Timeout value if timeout occurred
        """
        details = {}
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        if timeout:
            details['timeout'] = timeout
            
        super().__init__(message, details)


class APIError(NetworkError):
    """Raised when there's an API-related error."""
    
    def __init__(self, message: str, api_name: str, endpoint: Optional[str] = None,
                 response: Optional[Dict] = None, **kwargs):
        """
        Initialize API error.
        
        Args:
            message: Error message
            api_name: Name of the API (e.g., 'whisper', 'openai')
            endpoint: API endpoint
            response: API response if available
            **kwargs: Additional details
        """
        super().__init__(message, url=endpoint, **kwargs)
        
        self.details['api_name'] = api_name
        if response:
            self.details['api_response'] = response


class AuthenticationError(APIError):
    """Raised when there's an authentication error with an API."""
    
    def __init__(self, api_name: str, message: Optional[str] = None):
        """
        Initialize authentication error.
        
        Args:
            api_name: Name of the API
            message: Optional custom message
        """
        if not message:
            message = f"Authentication failed for {api_name} API"
            
        super().__init__(message, api_name, status_code=401)


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, api_name: str, retry_after: Optional[int] = None,
                 message: Optional[str] = None):
        """
        Initialize rate limit error.
        
        Args:
            api_name: Name of the API
            retry_after: Seconds to wait before retry
            message: Optional custom message
        """
        if not message:
            message = f"Rate limit exceeded for {api_name} API"
            
        super().__init__(message, api_name, status_code=429)
        
        if retry_after:
            self.details['retry_after'] = retry_after


# Exception handler utility
def handle_exception(exception: Exception, logger=None, reraise: bool = True):
    """
    Handle an exception with logging and optional re-raising.
    
    Args:
        exception: The exception to handle
        logger: Optional logger instance
        reraise: Whether to re-raise the exception
    """
    if logger:
        if isinstance(exception, ObsidianScribeError):
            logger.error(f"{exception.__class__.__name__}: {exception}")
            if exception.details:
                logger.debug(f"Error details: {exception.details}")
        else:
            logger.error(f"Unexpected error: {exception}", exc_info=True)
            
    if reraise:
        raise