"""
Helper utilities for Obsidian Scribe.

Provides various utility functions for formatting, file operations,
retry logic, and other common tasks.
"""

import hashlib
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, Callable, Any, Optional, Dict, List
from functools import wraps
import unicodedata
import random
import string


def format_duration(seconds: float, format: str = 'human') -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        format: Format type ('human', 'hms', 'ms')
        
    Returns:
        Formatted duration string
    """
    if format == 'human':
        # Human-readable format (e.g., "1h 23m 45s")
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
            
        return " ".join(parts)
        
    elif format == 'hms':
        # HH:MM:SS format
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
            
    elif format == 'ms':
        # MM:SS.mmm format (with milliseconds)
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
        
    else:
        return str(seconds)


def format_timestamp(timestamp: Union[float, datetime], 
                    format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format timestamp to string.
    
    Args:
        timestamp: Unix timestamp or datetime object
        format: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        raise ValueError(f"Invalid timestamp type: {type(timestamp)}")
        
    return dt.strftime(format)


def sanitize_filename(filename: str, 
                     replacement: str = '_',
                     max_length: int = 255) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace('/', replacement).replace('\\', replacement)
    
    # Remove invalid characters for Windows
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, replacement)
        
    # Remove control characters
    filename = ''.join(
        char if ord(char) >= 32 else replacement 
        for char in filename
    )
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Handle reserved names (Windows)
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
        'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5',
        'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_part = filename.split('.')[0].upper()
    if name_part in reserved_names:
        filename = replacement + filename
        
    # Normalize unicode
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Replace multiple consecutive replacements with single
    while replacement * 2 in filename:
        filename = filename.replace(replacement * 2, replacement)
        
    # Truncate if too long
    if len(filename) > max_length:
        # Try to preserve extension
        parts = filename.rsplit('.', 1)
        if len(parts) == 2 and len(parts[1]) < 10:
            name_part = parts[0][:max_length - len(parts[1]) - 1]
            filename = f"{name_part}.{parts[1]}"
        else:
            filename = filename[:max_length]
            
    # Ensure filename is not empty
    if not filename or filename == replacement:
        filename = 'unnamed'
        
    return filename


def get_file_hash(file_path: Union[str, Path], 
                 algorithm: str = 'sha256',
                 chunk_size: int = 8192) -> str:
    """
    Calculate file hash.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256', etc.)
        chunk_size: Size of chunks to read
        
    Returns:
        Hex digest of file hash
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
            
    return hash_obj.hexdigest()


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise
                        
                    if on_retry:
                        on_retry(attempt + 1, delay, e)
                        
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def parse_time_string(time_str: str) -> float:
    """
    Parse time string to seconds.
    
    Supports formats like:
    - "30s" or "30 seconds"
    - "5m" or "5 minutes"  
    - "2h" or "2 hours"
    - "1h 30m 45s"
    - "01:30:45"
    
    Args:
        time_str: Time string to parse
        
    Returns:
        Time in seconds
    """
    time_str = time_str.strip().lower()
    
    # Try HH:MM:SS format first
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
            
    # Parse unit-based format
    total_seconds = 0
    
    # Pattern for number followed by unit
    pattern = r'(\d+(?:\.\d+)?)\s*([a-z]+)'
    matches = re.findall(pattern, time_str)
    
    unit_multipliers = {
        's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
        'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
        'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400
    }
    
    for value, unit in matches:
        value = float(value)
        
        # Find matching unit
        multiplier = None
        for unit_key, mult in unit_multipliers.items():
            if unit.startswith(unit_key):
                multiplier = mult
                break
                
        if multiplier:
            total_seconds += value * multiplier
            
    # If no matches found, try to parse as plain number (assume seconds)
    if not matches and time_str.replace('.', '').isdigit():
        total_seconds = float(time_str)
        
    return total_seconds


def generate_unique_id(prefix: str = '', length: int = 8) -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part
        
    Returns:
        Unique identifier string
    """
    # Use timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Add random characters
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_part}"
    else:
        return f"{timestamp}_{random_part}"


def truncate_text(text: str, max_length: int, 
                 suffix: str = '...') -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    if max_length <= len(suffix):
        return text[:max_length]
        
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(dict1: Dict, dict2: Dict, 
                deep: bool = True) -> Dict:
    """
    Merge two dictionaries.
    
    Args:
        dict1: First dictionary (base)
        dict2: Second dictionary (updates)
        deep: Whether to do deep merge
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    if not deep:
        result.update(dict2)
        return result
        
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
            
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
        
    return f"{size_bytes:.2f} PB"


def extract_audio_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract basic metadata from audio file path.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with metadata
    """
    file_path = Path(file_path)
    
    metadata = {
        'filename': file_path.name,
        'stem': file_path.stem,
        'extension': file_path.suffix.lower(),
        'size_bytes': file_path.stat().st_size if file_path.exists() else 0,
        'modified_time': file_path.stat().st_mtime if file_path.exists() else None,
        'absolute_path': str(file_path.absolute())
    }
    
    # Try to extract date from filename
    date_patterns = [
        r'(\d{4}[-_]\d{2}[-_]\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
        r'(\d{8})',  # YYYYMMDD
        r'(\d{2}[-_]\d{2}[-_]\d{4})',  # DD-MM-YYYY or DD_MM_YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, file_path.stem)
        if match:
            metadata['extracted_date'] = match.group(1)
            break
            
    return metadata


def safe_divide(numerator: float, denominator: float, 
                default: float = 0.0) -> float:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a file path.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized Path object
    """
    path = Path(path)
    
    # Resolve symlinks and relative paths
    try:
        path = path.resolve()
    except:
        # If resolve fails, at least make it absolute
        path = path.absolute()
        
    return path