"""
Validation utilities for Obsidian Scribe.

Provides functions to validate various inputs like file paths, URLs,
configuration values, and audio files.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
import json
import yaml

from .exceptions import ValidationError, AudioFormatError, ConfigurationError


def validate_audio_file(file_path: Union[str, Path], 
                       check_exists: bool = True,
                       check_size: bool = True,
                       max_size_mb: float = 500.0,
                       supported_formats: Optional[List[str]] = None) -> Path:
    """
    Validate an audio file.
    
    Args:
        file_path: Path to the audio file
        check_exists: Whether to check if file exists
        check_size: Whether to check file size
        max_size_mb: Maximum file size in MB
        supported_formats: List of supported formats (extensions)
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
        AudioFormatError: If audio format is unsupported
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if check_exists and not file_path.exists():
        raise ValidationError(
            f"Audio file does not exist: {file_path}",
            field='file_path',
            value=str(file_path)
        )
        
    # Check if it's a file (not directory)
    if check_exists and not file_path.is_file():
        raise ValidationError(
            f"Path is not a file: {file_path}",
            field='file_path',
            value=str(file_path)
        )
        
    # Check file extension
    if supported_formats is None:
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', 
                           '.wma', '.aac', '.opus']
                           
    if file_path.suffix.lower() not in supported_formats:
        raise AudioFormatError(
            str(file_path),
            format=file_path.suffix,
            supported_formats=supported_formats
        )
        
    # Check file size
    if check_exists and check_size:
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            raise ValidationError(
                f"Audio file too large: {file_size_mb:.2f} MB (max: {max_size_mb} MB)",
                field='file_size',
                value=file_size_mb,
                expected=f"<= {max_size_mb} MB"
            )
            
        if file_size_mb < 0.001:  # Less than 1KB
            raise ValidationError(
                f"Audio file too small: {file_size_mb:.6f} MB",
                field='file_size',
                value=file_size_mb,
                expected=">= 0.001 MB"
            )
            
    return file_path


def validate_config(config: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        schema: Optional schema to validate against
        
    Returns:
        Validated configuration
        
    Raises:
        ConfigurationError: If validation fails
    """
    if not isinstance(config, dict):
        raise ConfigurationError(
            "Configuration must be a dictionary",
            config_value=type(config).__name__
        )
        
    # Basic validation
    if not config:
        raise ConfigurationError("Configuration is empty")
        
    # Schema validation if provided
    if schema:
        _validate_against_schema(config, schema)
        
    # Validate specific sections
    _validate_paths_config(config.get('paths', {}))
    _validate_audio_config(config.get('audio', {}))
    _validate_transcription_config(config.get('transcription', {}))
    _validate_logging_config(config.get('logging', {}))
    
    return config


def _validate_against_schema(config: Dict, schema: Dict, path: str = ""):
    """Validate configuration against a schema."""
    for key, rules in schema.items():
        current_path = f"{path}.{key}" if path else key
        
        # Check required fields
        if rules.get('required', False) and key not in config:
            raise ConfigurationError(
                f"Missing required configuration: {current_path}",
                config_key=current_path
            )
            
        if key in config:
            value = config[key]
            
            # Type validation
            expected_type = rules.get('type')
            if expected_type:
                if expected_type == 'dict' and isinstance(rules.get('properties'), dict):
                    if not isinstance(value, dict):
                        raise ConfigurationError(
                            f"Configuration {current_path} must be a dictionary",
                            config_key=current_path,
                            config_value=type(value).__name__
                        )
                    # Recursive validation
                    _validate_against_schema(value, rules['properties'], current_path)
                elif not _check_type(value, expected_type):
                    raise ConfigurationError(
                        f"Configuration {current_path} has wrong type",
                        config_key=current_path,
                        config_value=f"{type(value).__name__} (expected {expected_type})"
                    )
                    
            # Value validation
            if 'enum' in rules and value not in rules['enum']:
                raise ConfigurationError(
                    f"Configuration {current_path} has invalid value",
                    config_key=current_path,
                    config_value=f"{value} (allowed: {rules['enum']})"
                )
                
            if 'min' in rules and value < rules['min']:
                raise ConfigurationError(
                    f"Configuration {current_path} below minimum",
                    config_key=current_path,
                    config_value=f"{value} (min: {rules['min']})"
                )
                
            if 'max' in rules and value > rules['max']:
                raise ConfigurationError(
                    f"Configuration {current_path} above maximum",
                    config_key=current_path,
                    config_value=f"{value} (max: {rules['max']})"
                )


def _check_type(value: Any, expected_type: str) -> bool:
    """Check if value matches expected type."""
    type_map = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'dict': dict,
        'null': type(None)
    }
    
    expected = type_map.get(expected_type)
    if expected:
        return isinstance(value, expected)
    return True


def _validate_paths_config(paths: Dict[str, Any]):
    """Validate paths configuration section."""
    for key, path in paths.items():
        if not isinstance(path, str):
            raise ConfigurationError(
                f"Path configuration must be string: paths.{key}",
                config_key=f"paths.{key}",
                config_value=type(path).__name__
            )


def _validate_audio_config(audio: Dict[str, Any]):
    """Validate audio configuration section."""
    # Validate chunk settings
    if 'chunk_duration' in audio:
        duration = audio['chunk_duration']
        if not isinstance(duration, (int, float)) or duration <= 0:
            raise ConfigurationError(
                "audio.chunk_duration must be positive number",
                config_key="audio.chunk_duration",
                config_value=duration
            )
            
    # Validate file size limit
    if 'max_file_size_mb' in audio:
        size = audio['max_file_size_mb']
        if not isinstance(size, (int, float)) or size <= 0:
            raise ConfigurationError(
                "audio.max_file_size_mb must be positive number",
                config_key="audio.max_file_size_mb",
                config_value=size
            )


def _validate_transcription_config(transcription: Dict[str, Any]):
    """Validate transcription configuration section."""
    # Validate API endpoint
    if 'api_endpoint' in transcription:
        endpoint = transcription['api_endpoint']
        if not validate_url(endpoint, allow_localhost=True):
            raise ConfigurationError(
                "Invalid API endpoint URL",
                config_key="transcription.api_endpoint",
                config_value=endpoint
            )
            
    # Validate model
    if 'model' in transcription:
        model = transcription['model']
        valid_models = ['whisper-1', 'whisper-large-v3', 'whisper-large-v2']
        if model not in valid_models:
            raise ConfigurationError(
                f"Invalid transcription model",
                config_key="transcription.model",
                config_value=f"{model} (valid: {valid_models})"
            )


def _validate_logging_config(logging: Dict[str, Any]):
    """Validate logging configuration section."""
    # Validate log levels
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    for key in ['console_level', 'file_level']:
        if key in logging:
            level = logging[key].upper()
            if level not in valid_levels:
                raise ConfigurationError(
                    f"Invalid log level",
                    config_key=f"logging.{key}",
                    config_value=f"{level} (valid: {valid_levels})"
                )


def validate_path(path: Union[str, Path], 
                 must_exist: bool = False,
                 must_be_file: bool = False,
                 must_be_dir: bool = False,
                 create_if_missing: bool = False) -> Path:
    """
    Validate a file system path.
    
    Args:
        path: Path to validate
        must_exist: Whether path must exist
        must_be_file: Whether path must be a file
        must_be_dir: Whether path must be a directory
        create_if_missing: Create directory if missing (only for dirs)
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
    """
    path = Path(path)
    
    # Check existence
    if must_exist and not path.exists():
        if must_be_dir and create_if_missing:
            path.mkdir(parents=True, exist_ok=True)
        else:
            raise ValidationError(
                f"Path does not exist: {path}",
                field='path',
                value=str(path)
            )
            
    # Check type
    if path.exists():
        if must_be_file and not path.is_file():
            raise ValidationError(
                f"Path is not a file: {path}",
                field='path',
                value=str(path),
                expected='file'
            )
            
        if must_be_dir and not path.is_dir():
            raise ValidationError(
                f"Path is not a directory: {path}",
                field='path',
                value=str(path),
                expected='directory'
            )
            
    return path


def validate_url(url: str, 
                allow_localhost: bool = True,
                require_https: bool = False,
                allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate a URL.
    
    Args:
        url: URL to validate
        allow_localhost: Whether to allow localhost URLs
        require_https: Whether to require HTTPS
        allowed_schemes: List of allowed URL schemes
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if allowed_schemes:
            if parsed.scheme not in allowed_schemes:
                return False
        else:
            if parsed.scheme not in ['http', 'https']:
                return False
                
        if require_https and parsed.scheme != 'https':
            return False
            
        # Check host
        if not parsed.netloc:
            return False
            
        if not allow_localhost:
            localhost_names = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
            if any(name in parsed.netloc for name in localhost_names):
                return False
                
        return True
        
    except Exception:
        return False


def validate_json(data: Union[str, Dict]) -> Dict:
    """
    Validate JSON data.
    
    Args:
        data: JSON string or dictionary
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValidationError: If JSON is invalid
    """
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON: {e}",
                field='json',
                value=data[:100] + '...' if len(data) > 100 else data
            )
    elif isinstance(data, dict):
        return data
    else:
        raise ValidationError(
            "Data must be JSON string or dictionary",
            field='json',
            value=type(data).__name__
        )


def validate_yaml(data: Union[str, Dict]) -> Dict:
    """
    Validate YAML data.
    
    Args:
        data: YAML string or dictionary
        
    Returns:
        Parsed YAML as dictionary
        
    Raises:
        ValidationError: If YAML is invalid
    """
    if isinstance(data, str):
        try:
            return yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ValidationError(
                f"Invalid YAML: {e}",
                field='yaml',
                value=data[:100] + '...' if len(data) > 100 else data
            )
    elif isinstance(data, dict):
        return data
    else:
        raise ValidationError(
            "Data must be YAML string or dictionary",
            field='yaml',
            value=type(data).__name__
        )


def validate_timestamp(timestamp: Union[str, float], 
                      format: str = 'seconds') -> float:
    """
    Validate and convert timestamp.
    
    Args:
        timestamp: Timestamp to validate
        format: Format ('seconds', 'milliseconds', 'hh:mm:ss')
        
    Returns:
        Timestamp in seconds
        
    Raises:
        ValidationError: If timestamp is invalid
    """
    try:
        if format == 'seconds':
            return float(timestamp)
        elif format == 'milliseconds':
            return float(timestamp) / 1000
        elif format == 'hh:mm:ss':
            if isinstance(timestamp, str):
                parts = timestamp.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    return int(h) * 3600 + int(m) * 60 + float(s)
                elif len(parts) == 2:
                    m, s = parts
                    return int(m) * 60 + float(s)
                else:
                    return float(parts[0])
            else:
                raise ValueError("Timestamp must be string for hh:mm:ss format")
        else:
            raise ValueError(f"Unknown timestamp format: {format}")
            
    except (ValueError, TypeError) as e:
        raise ValidationError(
            f"Invalid timestamp: {e}",
            field='timestamp',
            value=timestamp,
            expected=format
        )

def validate_email(email: str) -> str:
    """
    Validate email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email
        
    Raises:
        ValidationError: If email is invalid
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not isinstance(email, str):
        raise ValidationError(
            "Email must be a string",
            field='email',
            value=type(email).__name__
        )
        
    if not re.match(pattern, email):
        raise ValidationError(
            f"Invalid email address format",
            field='email',
            value=email,
            expected='user@example.com'
        )
        
    return email.lower()


def validate_speaker_name(name: str) -> str:
    """
    Validate speaker name.
    
    Args:
        name: Speaker name to validate
        
    Returns:
        Validated speaker name
        
    Raises:
        ValidationError: If name is invalid
    """
    if not isinstance(name, str):
        raise ValidationError(
            "Speaker name must be a string",
            field='speaker_name',
            value=type(name).__name__
        )
        
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    if not name:
        raise ValidationError(
            "Speaker name cannot be empty",
            field='speaker_name',
            value=name
        )
        
    # Check length
    if len(name) > 100:
        raise ValidationError(
            f"Speaker name too long: {len(name)} characters (max: 100)",
            field='speaker_name',
            value=name[:50] + '...'
        )
        
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValidationError(
            "Speaker name contains invalid characters",
            field='speaker_name',
            value=name,
            expected="Only letters, spaces, hyphens, and apostrophes"
        )
        
    return name


def validate_language_code(code: str) -> str:
    """
    Validate language code (ISO 639-1).
    
    Args:
        code: Language code to validate
        
    Returns:
        Validated language code
        
    Raises:
        ValidationError: If code is invalid
    """
    # Common ISO 639-1 language codes
    valid_codes = {
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
        'ar', 'hi', 'nl', 'pl', 'tr', 'sv', 'da', 'no', 'fi', 'cs',
        'el', 'he', 'hu', 'id', 'ms', 'th', 'vi', 'uk', 'ro', 'bg'
    }
    
    if not isinstance(code, str):
        raise ValidationError(
            "Language code must be a string",
            field='language_code',
            value=type(code).__name__
        )
        
    code = code.lower()
    
    if len(code) != 2:
        raise ValidationError(
            f"Language code must be 2 characters",
            field='language_code',
            value=code,
            expected='ISO 639-1 format (e.g., "en")'
        )
        
    if code not in valid_codes:
        raise ValidationError(
            f"Unsupported language code",
            field='language_code',
            value=code,
            expected=f"One of: {', '.join(sorted(valid_codes))}"
        )
        
    return code
        