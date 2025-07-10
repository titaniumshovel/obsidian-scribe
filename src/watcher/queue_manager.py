"""
Queue management for file processing.

Manages the queue of files to be processed with priority support.
"""

import logging
import heapq
from queue import Queue, Empty, PriorityQueue
from threading import Lock
from typing import Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(order=True)
class QueueItem:
    """Item in the processing queue with priority support."""
    priority: float
    file_path: str = field(compare=False)
    added_time: datetime = field(default_factory=datetime.now, compare=False)
    retry_count: int = field(default=0, compare=False)


class QueueManager:
    """Manages the file processing queue with priority and retry support."""
    
    def __init__(self):
        """Initialize the queue manager."""
        self.logger = logging.getLogger(__name__)
        self._queue: PriorityQueue = PriorityQueue()
        self._processing: Set[str] = set()
        self._failed: Dict[str, int] = {}
        self._completed: Set[str] = set()
        self._lock = Lock()
        
    def add_file(self, file_path: str, priority: float = 0.0):
        """
        Add a file to the processing queue.
        
        Args:
            file_path: Path to the file
            priority: Priority value (lower values processed first)
        """
        with self._lock:
            if file_path in self._processing or file_path in self._completed:
                self.logger.debug(f"File already processed or processing: {file_path}")
                return
                
            item = QueueItem(priority=priority, file_path=file_path)
            self._queue.put(item)
            self.logger.debug(f"Added file to queue: {file_path} (priority: {priority})")
            
    def get_next_file(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Get the next file from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            File path or None if queue is empty
        """
        try:
            item = self._queue.get(timeout=timeout)
            with self._lock:
                self._processing.add(item.file_path)
            return item.file_path
        except Empty:
            return None
            
    def mark_completed(self, file_path: str):
        """
        Mark a file as completed.
        
        Args:
            file_path: Path to the file
        """
        with self._lock:
            self._processing.discard(file_path)
            self._completed.add(file_path)
            self._failed.pop(file_path, None)
            self.logger.debug(f"Marked file as completed: {file_path}")
            
    def mark_failed(self, file_path: str, retry: bool = True, max_retries: int = 3):
        """
        Mark a file as failed.
        
        Args:
            file_path: Path to the file
            retry: Whether to retry the file
            max_retries: Maximum number of retries
        """
        with self._lock:
            self._processing.discard(file_path)
            
            # Update retry count
            retry_count = self._failed.get(file_path, 0) + 1
            self._failed[file_path] = retry_count
            
            if retry and retry_count < max_retries:
                # Re-add to queue with lower priority
                priority = 100.0 + retry_count  # Lower priority for retries
                item = QueueItem(
                    priority=priority,
                    file_path=file_path,
                    retry_count=retry_count
                )
                self._queue.put(item)
                self.logger.info(f"Re-queued failed file (attempt {retry_count}): {file_path}")
            else:
                self.logger.error(f"File permanently failed after {retry_count} attempts: {file_path}")
                
    def get_queue_size(self) -> int:
        """Get the current size of the queue."""
        return self._queue.qsize()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            return {
                'queued': self.get_queue_size(),
                'processing': len(self._processing),
                'completed': len(self._completed),
                'failed': len(self._failed),
                'total_processed': len(self._completed) + len(self._failed)
            }
            
    def is_processing(self, file_path: str) -> bool:
        """
        Check if a file is currently being processed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is being processed
        """
        with self._lock:
            return file_path in self._processing
            
    def is_completed(self, file_path: str) -> bool:
        """
        Check if a file has been completed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file has been completed
        """
        with self._lock:
            return file_path in self._completed
            
    def clear_completed(self):
        """Clear the completed files set."""
        with self._lock:
            self._completed.clear()
            self.logger.info("Cleared completed files list")
            
    def get_failed_files(self) -> Dict[str, int]:
        """
        Get the list of failed files with retry counts.
        
        Returns:
            Dictionary of file paths to retry counts
        """
        with self._lock:
            return self._failed.copy()