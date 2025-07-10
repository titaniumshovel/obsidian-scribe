"""
File watching module for Obsidian Scribe.

Monitors a directory for new audio files and queues them for processing.
Uses the watchdog library for efficient file system monitoring.
"""

import logging
import os
import time
from pathlib import Path
from queue import Queue
from threading import Thread, Event
from typing import Dict, List, Optional, Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent


class AudioFileHandler(FileSystemEventHandler):
    """Handler for audio file system events."""
    
    def __init__(self, queue: Queue, config: Dict):
        """
        Initialize the audio file handler.
        
        Args:
            queue: Queue to add detected files to
            config: Watcher configuration
        """
        self.queue = queue
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
        self.queue.put(file_path)
        
        # Clean up file size tracking
        if file_path in self._file_sizes:
            del self._file_sizes[file_path]


class FileWatcher:
    """Main file watcher class that monitors directories for audio files."""
    
    def __init__(self, watch_folder: str, processor, config: Dict):
        """
        Initialize the file watcher.
        
        Args:
            watch_folder: Directory to watch for audio files
            processor: AudioProcessor instance to handle files
            config: Watcher configuration
        """
        self.watch_folder = Path(watch_folder)
        self.processor = processor
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create queue for files
        self.file_queue: Queue = Queue()
        
        # Threading components
        self._observer: Optional[Observer] = None
        self._queue_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._running = False
        
        # Validate watch folder
        if not self.watch_folder.exists():
            self.logger.warning(f"Watch folder does not exist, creating: {self.watch_folder}")
            self.watch_folder.mkdir(parents=True, exist_ok=True)
            
    def start(self):
        """Start the file watcher."""
        if self._running:
            self.logger.warning("File watcher is already running")
            return
            
        self.logger.info(f"Starting file watcher on: {self.watch_folder}")
        self._running = True
        self._stop_event.clear()
        
        # Start the observer
        self._observer = Observer()
        handler = AudioFileHandler(self.file_queue, self.config)
        self._observer.schedule(handler, str(self.watch_folder), recursive=False)
        self._observer.start()
        
        # Start queue processing thread
        self._queue_thread = Thread(target=self._process_queue, daemon=True)
        self._queue_thread.start()
        
        # Scan existing files
        self._scan_existing_files(handler)
        
        self.logger.info("File watcher started successfully")
        
    def stop(self):
        """Stop the file watcher."""
        if not self._running:
            return
            
        self.logger.info("Stopping file watcher...")
        self._running = False
        self._stop_event.set()
        
        # Stop the observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
            
        # Stop queue thread
        if self._queue_thread:
            self._queue_thread.join(timeout=5)
            self._queue_thread = None
            
        self.logger.info("File watcher stopped")
        
    def _scan_existing_files(self, handler: AudioFileHandler):
        """
        Scan for existing audio files in the watch folder.
        
        Args:
            handler: File handler to use for validation
        """
        self.logger.info("Scanning for existing audio files...")
        count = 0
        
        try:
            for file_path in self.watch_folder.iterdir():
                if file_path.is_file():
                    full_path = str(file_path)
                    if handler._is_valid_audio_file(full_path) and handler._is_file_ready(full_path):
                        self.logger.info(f"Found existing audio file: {full_path}")
                        self.file_queue.put(full_path)
                        handler._processing_files.add(full_path)
                        count += 1
                        
        except Exception as e:
            self.logger.error(f"Error scanning existing files: {e}")
            
        if count > 0:
            self.logger.info(f"Found {count} existing audio files to process")
            
    def _process_queue(self):
        """Process files from the queue."""
        while self._running:
            try:
                # Wait for a file with timeout
                if not self._stop_event.is_set():
                    try:
                        file_path = self.file_queue.get(timeout=1.0)
                    except:
                        continue
                        
                    if file_path:
                        self.logger.info(f"Processing file from queue: {file_path}")
                        try:
                            # Add file to processor queue
                            self.processor.add_file(file_path)
                        except Exception as e:
                            self.logger.error(f"Error adding file to processor: {e}")
                            
            except Exception as e:
                self.logger.error(f"Error in queue processing: {e}")
                time.sleep(1)
                
    def get_queue_size(self) -> int:
        """Get the current size of the file queue."""
        return self.file_queue.qsize()