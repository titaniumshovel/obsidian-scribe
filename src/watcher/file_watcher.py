"""
Main file watching logic for Obsidian Scribe.

Monitors a directory for new audio files and queues them for processing.
"""

import logging
import time
from pathlib import Path
from threading import Thread, Event
from typing import Dict, Optional, Any

from watchdog.observers import Observer

from .event_handler import AudioFileHandler
from .queue_manager import QueueManager


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
        
        # Set back-reference so processor can clear files from processing set
        if hasattr(processor, 'file_watcher'):
            processor.file_watcher = self
        
        # Create queue manager
        self.queue_manager = QueueManager()
        
        # Threading components
        self._observer: Optional[Any] = None  # Observer instance
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
        self._handler = AudioFileHandler(self.queue_manager, self.config)
        self._observer.schedule(self._handler, str(self.watch_folder), recursive=False)
        self._observer.start()
        
        # Start queue processing thread
        self._queue_thread = Thread(target=self._process_queue, daemon=True)
        self._queue_thread.start()
        
        # Scan existing files
        self._scan_existing_files(self._handler)
        
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
                    if handler._is_valid_audio_file(full_path):
                        # For existing files, assume they are ready
                        # Mark the file size as stable by setting it twice
                        file_size = file_path.stat().st_size
                        handler._file_sizes[full_path] = file_size
                        
                        self.logger.info(f"Found existing audio file: {full_path}")
                        self.queue_manager.add_file(full_path)
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
                    file_path = self.queue_manager.get_next_file(timeout=1.0)
                    
                    if file_path:
                        self.logger.info(f"Processing file from queue: {file_path}")
                        try:
                            # Add file to processor queue
                            self.processor.add_file(file_path)
                        except Exception as e:
                            self.logger.error(f"Error adding file to processor: {e}")
                            # Mark as failed for potential retry
                            self.queue_manager.mark_failed(file_path)
                            
            except Exception as e:
                self.logger.error(f"Error in queue processing: {e}")
                time.sleep(1)
                
    def get_queue_size(self) -> int:
        """Get the current size of the file queue."""
        return self.queue_manager.get_queue_size()
        
    def get_stats(self) -> Dict:
        """Get watcher statistics."""
        return {
            'queue_size': self.get_queue_size(),
            'running': self._running,
            'watch_folder': str(self.watch_folder)
        }
        
    def clear_processing_file(self, file_path: str):
        """Clear a file from the processing set."""
        if hasattr(self, '_handler') and self._handler:
            self._handler.clear_processing_file(file_path)