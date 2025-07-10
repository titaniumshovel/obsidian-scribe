"""
Utility functions for Obsidian Scribe.

Provides common functionality for file operations, audio validation,
timestamp formatting, and logging setup.
"""

import logging
import logging.handlers
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union


def setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None):
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Path to log file (optional)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
    # Set specific logger levels to reduce noise
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    

def ensure_directories(paths: Dict[str, str]):
    """
    Ensure all required directories exist.
    
    Args:
        paths: Dictionary of path configurations
    """
    for key, path in paths.items():
        if path:
            Path(path).mkdir(parents=True, exist_ok=True)
            

def ensure_directory_exists(directory: Union[str, Path]):
    """
    Ensure a single directory exists.
    
    Args:
        directory: Path to directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    

def validate_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file is a valid audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        True if file is valid audio file
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        return False
        
    # Check file extension
    valid_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma'}
    if file_path.suffix.lower() not in valid_extensions:
        return False
        
    # Check file size (minimum 1KB)
    if file_path.stat().st_size < 1024:
        return False
        
    # TODO: Add more sophisticated audio validation (e.g., check file headers)
    
    return True
    

def move_file_safely(source: Union[str, Path], destination: Union[str, Path]) -> Path:
    """
    Safely move a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        Path to the moved file
        
    Raises:
        OSError: If file cannot be moved
    """
    source = Path(source)
    destination = Path(destination)
    
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle case where destination already exists
    if destination.exists():
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stem = destination.stem
        suffix = destination.suffix
        destination = destination.parent / f"{stem}_{timestamp}{suffix}"
    
    # Try to move the file
    try:
        shutil.move(str(source), str(destination))
        return destination
    except Exception as e:
        # If move fails, try copy and delete
        try:
            shutil.copy2(str(source), str(destination))
            source.unlink()
            return destination
        except Exception:
            raise OSError(f"Failed to move file from {source} to {destination}: {e}")
            

def copy_file_safely(source: Union[str, Path], destination: Union[str, Path]) -> Path:
    """
    Safely copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        Path to the copied file
        
    Raises:
        OSError: If file cannot be copied
    """
    source = Path(source)
    destination = Path(destination)
    
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle case where destination already exists
    if destination.exists():
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stem = destination.stem
        suffix = destination.suffix
        destination = destination.parent / f"{stem}_{timestamp}{suffix}"
    
    # Copy the file
    try:
        shutil.copy2(str(source), str(destination))
        return destination
    except Exception as e:
        raise OSError(f"Failed to copy file from {source} to {destination}: {e}")
        

def format_timestamp(seconds: float) -> str:
    """
    Format seconds into a readable timestamp.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS)
    """
    if seconds < 0:
        return "00:00:00"
        
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    

def format_duration(seconds: float) -> str:
    """
    Format duration in a human-readable way.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human-readable duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
        

def get_file_info(file_path: Union[str, Path]) -> Dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {}
        
    stat = file_path.stat()
    
    return {
        'name': file_path.name,
        'path': str(file_path),
        'size': stat.st_size,
        'size_mb': stat.st_size / (1024 * 1024),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': file_path.suffix.lower()
    }
    

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for Windows/Unix
    invalid_chars = '<>:"|?*\x00'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
        
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        # Keep extension if present
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            max_name_length = max_length - len(ext) - 1
            filename = f"{name[:max_name_length]}.{ext}"
        else:
            filename = filename[:max_length]
            
    return filename
    

def wait_for_file_ready(file_path: Union[str, Path], timeout: float = 30.0, check_interval: float = 0.5) -> bool:
    """
    Wait for a file to be fully written and ready.
    
    Args:
        file_path: Path to the file
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        True if file is ready, False if timeout reached
    """
    file_path = Path(file_path)
    start_time = time.time()
    last_size = -1
    
    while time.time() - start_time < timeout:
        if not file_path.exists():
            time.sleep(check_interval)
            continue
            
        try:
            current_size = file_path.stat().st_size
            
            # Check if size is stable
            if current_size == last_size and current_size > 0:
                # Try to open the file to ensure it's not locked
                with open(file_path, 'rb') as f:
                    # File is accessible
                    return True
                    
            last_size = current_size
            
        except (OSError, IOError):
            # File might be locked or in use
            pass
            
        time.sleep(check_interval)
        
    return False
    

def get_audio_duration(file_path: Union[str, Path]) -> Optional[float]:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Duration in seconds, or None if unable to determine
    """
    # TODO: Implement actual audio duration detection
    # This would require an audio library like pydub or mutagen
    # For now, return None as a placeholder
    return None
    

def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks
    

def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry a function on exception with exponential backoff.
    
    Args:
        func: Function to call
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
        
    Returns:
        Result of the function
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                raise
                
    raise last_exception