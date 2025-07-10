"""
File management utilities for Obsidian Scribe.

Provides safe file operations with atomic writes, validation, and error handling.
"""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, Union, List
from contextlib import contextmanager
import hashlib
import json


class FileManager:
    """Manages file operations with safety and atomicity."""
    
    def __init__(self, config: Dict):
        """
        Initialize the file manager.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(config.get('paths', {}).get('temp_folder', './temp'))
        self.ensure_directory(self.temp_dir)
        
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Path to directory
            
        Returns:
            Path object for the directory
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def validate_audio_file(self, file_path: Union[str, Path]) -> bool:
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
        valid_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.opus'}
        if file_path.suffix.lower() not in valid_extensions:
            return False
            
        # Check file size (minimum 1KB, maximum from config)
        file_size = file_path.stat().st_size
        if file_size < 1024:  # Less than 1KB
            return False
            
        max_size_mb = self.config.get('audio', {}).get('max_file_size_mb', 500)
        if file_size > max_size_mb * 1024 * 1024:
            self.logger.warning(f"File too large: {file_size / 1024 / 1024:.2f} MB")
            return False
            
        return True
        
    def get_file_info(self, file_path: Union[str, Path]) -> Dict:
        """
        Get detailed information about a file.
        
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
            'absolute_path': str(file_path.absolute()),
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'extension': file_path.suffix.lower(),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'parent': str(file_path.parent),
            'stem': file_path.stem
        }
        
    @contextmanager
    def atomic_write(self, file_path: Union[str, Path], mode: str = 'w'):
        """
        Context manager for atomic file writes.
        
        Writes to a temporary file and moves it to the final location
        only if the write completes successfully.
        
        Args:
            file_path: Final destination path
            mode: File open mode
            
        Yields:
            File handle for writing
        """
        file_path = Path(file_path)
        self.ensure_directory(file_path.parent)
        
        # Create temporary file in the same directory for atomic rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f'.{file_path.name}.',
            suffix='.tmp'
        )
        
        try:
            with os.fdopen(temp_fd, mode) as f:
                yield f
                
            # If we get here, write was successful
            # Use atomic rename (on same filesystem)
            Path(temp_path).replace(file_path)
            
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise
            
    def read_file(self, file_path: Union[str, Path], mode: str = 'r') -> Union[str, bytes]:
        """
        Read a file with error handling.
        
        Args:
            file_path: Path to file
            mode: Read mode ('r' for text, 'rb' for binary)
            
        Returns:
            File contents
        """
        file_path = Path(file_path)
        
        try:
            with open(file_path, mode) as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise
            
    def write_file(self, file_path: Union[str, Path], content: Union[str, bytes], mode: str = 'w'):
        """
        Write content to a file atomically.
        
        Args:
            file_path: Path to file
            content: Content to write
            mode: Write mode ('w' for text, 'wb' for binary)
        """
        with self.atomic_write(file_path, mode) as f:
            f.write(content)
            
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Copy a file safely.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the copied file
        """
        source = Path(source)
        destination = Path(destination)
        
        # Ensure destination directory exists
        self.ensure_directory(destination.parent)
        
        # Copy with metadata preservation
        shutil.copy2(str(source), str(destination))
        
        self.logger.debug(f"Copied {source} to {destination}")
        return destination
        
    def copy_file_safely(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Safely copy a file from source to destination with automatic renaming if exists.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the copied file
        """
        from datetime import datetime
        
        source = Path(source)
        destination = Path(destination)
        
        # Ensure destination directory exists
        self.ensure_directory(destination.parent)
        
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
            self.logger.debug(f"Safely copied {source} to {destination}")
            return destination
        except Exception as e:
            raise OSError(f"Failed to copy file from {source} to {destination}: {e}")
        
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Move a file safely.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the moved file
        """
        source = Path(source)
        destination = Path(destination)
        
        # Ensure destination directory exists
        self.ensure_directory(destination.parent)
        
        # Use shutil.move for cross-filesystem support
        shutil.move(str(source), str(destination))
        
        self.logger.debug(f"Moved {source} to {destination}")
        return destination
        
    def move_file_safely(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Safely move a file from source to destination with automatic renaming if exists.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the moved file
        """
        from datetime import datetime
        
        source = Path(source)
        destination = Path(destination)
        
        # Ensure destination directory exists
        self.ensure_directory(destination.parent)
        
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
            self.logger.debug(f"Safely moved {source} to {destination}")
            return destination
        except Exception as e:
            # If move fails, try copy and delete
            try:
                shutil.copy2(str(source), str(destination))
                source.unlink()
                self.logger.debug(f"Safely moved {source} to {destination} (via copy+delete)")
                return destination
            except Exception:
                raise OSError(f"Failed to move file from {source} to {destination}: {e}")
        
    def delete_file(self, file_path: Union[str, Path]):
        """
        Delete a file safely.
        
        Args:
            file_path: Path to file to delete
        """
        file_path = Path(file_path)
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Deleted {file_path}")
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            raise
            
    def get_temp_file(self, prefix: str = 'obsidian_scribe_', suffix: str = '') -> Path:
        """
        Get a temporary file path.
        
        Args:
            prefix: File prefix
            suffix: File suffix
            
        Returns:
            Path to temporary file
        """
        fd, temp_path = tempfile.mkstemp(
            dir=self.temp_dir,
            prefix=prefix,
            suffix=suffix
        )
        os.close(fd)  # Close the file descriptor
        return Path(temp_path)
        
    def clean_temp_files(self, max_age_hours: int = 24):
        """
        Clean old temporary files.
        
        Args:
            max_age_hours: Maximum age of temp files in hours
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleaned = 0
        for temp_file in self.temp_dir.iterdir():
            if temp_file.is_file():
                file_age = current_time - temp_file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        temp_file.unlink()
                        cleaned += 1
                    except Exception as e:
                        self.logger.warning(f"Could not delete temp file {temp_file}: {e}")
                        
        if cleaned > 0:
            self.logger.info(f"Cleaned {cleaned} old temporary files")
            
    def calculate_checksum(self, file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """
        Calculate file checksum.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of the file
        """
        file_path = Path(file_path)
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
                
        return hash_func.hexdigest()
        
    def list_files(self, directory: Union[str, Path], pattern: str = '*', 
                   recursive: bool = False) -> List[Path]:
        """
        List files in a directory.
        
        Args:
            directory: Directory to list
            pattern: Glob pattern for filtering
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        directory = Path(directory)
        
        if not directory.exists():
            return []
            
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
            
    def get_unique_filename(self, directory: Union[str, Path], base_name: str, 
                           extension: str = '') -> Path:
        """
        Get a unique filename in a directory.
        
        Args:
            directory: Target directory
            base_name: Base filename
            extension: File extension
            
        Returns:
            Unique file path
        """
        directory = Path(directory)
        self.ensure_directory(directory)
        
        # Try the base name first
        file_path = directory / f"{base_name}{extension}"
        if not file_path.exists():
            return file_path
            
        # Add numbers until we find a unique name
        counter = 1
        while True:
            file_path = directory / f"{base_name}_{counter}{extension}"
            if not file_path.exists():
                return file_path
            counter += 1
            
    def save_json(self, file_path: Union[str, Path], data: Dict, indent: int = 2):
        """
        Save data as JSON file.
        
        Args:
            file_path: Path to save to
            data: Data to save
            indent: JSON indentation
        """
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        self.write_file(file_path, content)
        
    def load_json(self, file_path: Union[str, Path]) -> Dict:
        """
        Load data from JSON file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            Loaded data
        """
        content = self.read_file(file_path)
        return json.loads(content)
        
    def wait_for_file_ready(self, file_path: Union[str, Path],
                           timeout: float = 30.0,
                           check_interval: float = 0.5) -> bool:
        """
        Wait for a file to be fully written and ready.
        
        Args:
            file_path: Path to the file
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            True if file is ready, False if timeout reached
        """
        import time
        
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
        
    def get_audio_duration(self, file_path: Union[str, Path]) -> Optional[float]:
        """
        Get the duration of an audio file in seconds.
        
        Note: This is a placeholder. Actual implementation would require
        an audio library like pydub or mutagen.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Duration in seconds, or None if unable to determine
        """
        # TODO: Implement actual audio duration detection
        # This would require an audio library like pydub or mutagen
        # For now, return None as a placeholder
        self.logger.debug(f"Audio duration detection not yet implemented for {file_path}")
        return None