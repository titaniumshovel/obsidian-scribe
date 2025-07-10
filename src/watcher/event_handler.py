"""
File system event handler for audio files.

Handles file creation and modification events for audio files.
"""

import logging
import os
from typing import Dict, Set

from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from .queue_manager import QueueManager


class AudioFileHandler(FileSystemEventHandler):
    """Handler for audio file system events."""
    
    def __init__(self, queue_manager: QueueManager, config: Dict):
        """
        Initialize the audio file handler.
        
        Args:
            queue_manager: Queue manager instance
            config: Watcher configuration
        """
        self.queue_manager = queue_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.file_extensions = [ext.lower() for ext in config.get('file_extensions', ['.wav', '.mp3'])]
        self.ignore_patterns = config.get('ignore_patterns', ['.*', '~*'])
        self._processing_files: Set[str] = set()
        self._file_sizes: Dict[str, int] = {}
        
    def _should_ignore(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be ignored
        """
        filename = os.path.basename(file_path)
        
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern.startswith('*') and filename.endswith(pattern[1:]):
                return True
            elif pattern.endswith('*') and filename.startswith(pattern[:-1]):
                return True
            elif pattern in filename:
                return True
                
        return False
        
    def _is_valid_audio_file(self, file_path: str) -> bool:
        """
        Check if a file is a valid audio file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid audio file
        """
        if not os.path.isfile(file_path):
            return False
            
        if self._should_ignore(file_path):
            return False
            
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.file_extensions
        
    def _is_file_ready(self, file_path: str) -> bool:
        """
        Check if a file is fully written and ready for processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is ready
        """
        try:
            # Check if file size is stable
            current_size = os.path.getsize(file_path)
            
            if file_path in self._file_sizes:
                if self._file_sizes[file_path] == current_size:
                    # Size hasn't changed, file is likely ready
                    return True
                    
            self._file_sizes[file_path] = current_size
            return False
            
        except (OSError, IOError):
            return False
            
    def on_created(self, event):
        """Handle file creation events."""
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            self._handle_file(event.src_path)
            
    def on_modified(self, event):
        """Handle file modification events."""
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            self._handle_file(event.src_path)
            
    def _handle_file(self, file_path: str):
        """
        Handle a potential audio file.
        
        Args:
            file_path: Path to the file
        """
        if not self._is_valid_audio_file(file_path):
            return
            
        # Skip if already processing
        if file_path in self._processing_files:
            return
            
        # Check if file is ready (fully written)
        if not self._is_file_ready(file_path):
            self.logger.debug(f"File not ready yet: {file_path}")
            return
            
        # Add to processing set and queue
        self._processing_files.add(file_path)
        self.logger.info(f"New audio file detected: {file_path}")
        
        # Add to queue with priority based on file age
        try:
            file_stat = os.stat(file_path)
            priority = -file_stat.st_mtime  # Negative so older files have higher priority
            self.queue_manager.add_file(file_path, priority=priority)
        except Exception as e:
            self.logger.error(f"Error adding file to queue: {e}")
            self._processing_files.discard(file_path)
        
        # Clean up file size tracking
        if file_path in self._file_sizes:
            del self._file_sizes[file_path]
            
    def clear_processing_file(self, file_path: str):
        """
        Remove a file from the processing set.
        
        Args:
            file_path: Path to the file
        """
        self._processing_files.discard(file_path)