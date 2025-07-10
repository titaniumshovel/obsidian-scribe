"""
State management for Obsidian Scribe.

Tracks processing state, handles recovery from failures, and maintains
processing history.
"""

import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import sqlite3
from contextlib import contextmanager


class ProcessingState(Enum):
    """Processing state enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DIARIZING = "diarizing"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class StateManager:
    """Manages processing state and history."""
    
    def __init__(self, config: Dict, file_manager):
        """
        Initialize the state manager.
        
        Args:
            config: Application configuration
            file_manager: FileManager instance
        """
        self.config = config
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
        
        # State storage
        state_dir = Path(config.get('paths', {}).get('state_folder', './state'))
        self.file_manager.ensure_directory(state_dir)
        
        self.db_path = state_dir / 'processing_state.db'
        self.state_file = state_dir / 'current_state.json'
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Load current state
        self.current_state = self._load_current_state()
        
    def _init_database(self):
        """Initialize the SQLite database for state tracking."""
        with self._get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    state TEXT NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds REAL,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path 
                ON processing_history(file_path)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_state 
                ON processing_history(state)
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processing_stats (
                    date TEXT PRIMARY KEY,
                    total_processed INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    total_duration_seconds REAL DEFAULT 0,
                    average_duration_seconds REAL DEFAULT 0
                )
            ''')
            
    @contextmanager
    def _get_db(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def _load_current_state(self) -> Dict[str, Dict]:
        """Load current processing state from file."""
        if self.state_file.exists():
            try:
                return self.file_manager.load_json(self.state_file)
            except Exception as e:
                self.logger.error(f"Error loading state file: {e}")
                return {}
        return {}
        
    def _save_current_state(self):
        """Save current processing state to file."""
        with self._lock:
            self.file_manager.save_json(self.state_file, self.current_state)
            
    def start_processing(self, file_path: Union[str, Path], 
                        metadata: Optional[Dict] = None) -> int:
        """
        Mark a file as started processing.
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata
            
        Returns:
            Processing ID
        """
        file_path = str(Path(file_path).absolute())
        
        with self._lock:
            # Update current state
            self.current_state[file_path] = {
                'state': ProcessingState.PROCESSING.value,
                'started_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            self._save_current_state()
            
        # Add to history
        with self._get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO processing_history 
                (file_path, state, started_at, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                file_path,
                ProcessingState.PROCESSING.value,
                datetime.now(),
                json.dumps(metadata or {})
            ))
            
            processing_id = cursor.lastrowid
            
        self.logger.info(f"Started processing {file_path} (ID: {processing_id})")
        return processing_id
        
    def update_state(self, file_path: Union[str, Path], 
                    state: ProcessingState,
                    error_message: Optional[str] = None,
                    metadata_update: Optional[Dict] = None):
        """
        Update the processing state of a file.
        
        Args:
            file_path: Path to the file
            state: New processing state
            error_message: Error message if failed
            metadata_update: Metadata to update/merge
        """
        file_path = str(Path(file_path).absolute())
        
        with self._lock:
            if file_path in self.current_state:
                self.current_state[file_path]['state'] = state.value
                self.current_state[file_path]['updated_at'] = datetime.now().isoformat()
                
                if error_message:
                    self.current_state[file_path]['error'] = error_message
                    
                if metadata_update:
                    self.current_state[file_path]['metadata'].update(metadata_update)
                    
                self._save_current_state()
                
        # Update history
        with self._get_db() as conn:
            conn.execute('''
                UPDATE processing_history
                SET state = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE file_path = ? AND completed_at IS NULL
            ''', (state.value, error_message, file_path))
            
        self.logger.debug(f"Updated state for {file_path}: {state.value}")
        
    def complete_processing(self, file_path: Union[str, Path], 
                          success: bool = True,
                          error_message: Optional[str] = None,
                          metadata_update: Optional[Dict] = None):
        """
        Mark a file as completed processing.
        
        Args:
            file_path: Path to the file
            success: Whether processing was successful
            error_message: Error message if failed
            metadata_update: Final metadata updates
        """
        file_path = str(Path(file_path).absolute())
        
        final_state = ProcessingState.COMPLETED if success else ProcessingState.FAILED
        
        with self._lock:
            if file_path in self.current_state:
                started_at = datetime.fromisoformat(
                    self.current_state[file_path]['started_at']
                )
                duration = (datetime.now() - started_at).total_seconds()
                
                # Remove from current state
                del self.current_state[file_path]
                self._save_current_state()
            else:
                duration = None
                
        # Update history
        with self._get_db() as conn:
            conn.execute('''
                UPDATE processing_history
                SET state = ?, 
                    completed_at = ?,
                    duration_seconds = ?,
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE file_path = ? AND completed_at IS NULL
            ''', (
                final_state.value,
                datetime.now(),
                duration,
                error_message,
                file_path
            ))
            
        # Update daily stats
        self._update_daily_stats(success, duration)
        
        status = "completed" if success else "failed"
        self.logger.info(f"Processing {status} for {file_path}")
        
    def _update_daily_stats(self, success: bool, duration: Optional[float]):
        """Update daily processing statistics."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with self._get_db() as conn:
            # Get current stats
            row = conn.execute(
                'SELECT * FROM processing_stats WHERE date = ?', 
                (today,)
            ).fetchone()
            
            if row:
                # Update existing
                if success:
                    total_processed = row['total_processed'] + 1
                    total_failed = row['total_failed']
                else:
                    total_processed = row['total_processed']
                    total_failed = row['total_failed'] + 1
                    
                total_duration = row['total_duration_seconds'] + (duration or 0)
                avg_duration = total_duration / (total_processed + total_failed)
                
                conn.execute('''
                    UPDATE processing_stats
                    SET total_processed = ?,
                        total_failed = ?,
                        total_duration_seconds = ?,
                        average_duration_seconds = ?
                    WHERE date = ?
                ''', (total_processed, total_failed, total_duration, avg_duration, today))
            else:
                # Insert new
                conn.execute('''
                    INSERT INTO processing_stats 
                    (date, total_processed, total_failed, total_duration_seconds, average_duration_seconds)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    today,
                    1 if success else 0,
                    0 if success else 1,
                    duration or 0,
                    duration or 0
                ))
                
    def get_processing_files(self) -> List[Dict]:
        """
        Get list of currently processing files.
        
        Returns:
            List of processing file info
        """
        with self._lock:
            return [
                {
                    'file_path': file_path,
                    **info
                }
                for file_path, info in self.current_state.items()
            ]
            
    def get_file_history(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Get processing history for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of processing history entries
        """
        file_path = str(Path(file_path).absolute())
        
        with self._get_db() as conn:
            rows = conn.execute('''
                SELECT * FROM processing_history
                WHERE file_path = ?
                ORDER BY created_at DESC
            ''', (file_path,)).fetchall()
            
            return [dict(row) for row in rows]
            
    def get_failed_files(self, limit: int = 100) -> List[Dict]:
        """
        Get list of failed files.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of failed file info
        """
        with self._get_db() as conn:
            rows = conn.execute('''
                SELECT * FROM processing_history
                WHERE state = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (ProcessingState.FAILED.value, limit)).fetchall()
            
            return [dict(row) for row in rows]
            
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get processing statistics.
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary of statistics
        """
        cutoff_date = datetime.now().strftime('%Y-%m-%d')
        
        with self._get_db() as conn:
            # Overall stats
            overall = conn.execute('''
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN state = ? THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN state = ? THEN 1 ELSE 0 END) as failed,
                    AVG(duration_seconds) as avg_duration,
                    MIN(duration_seconds) as min_duration,
                    MAX(duration_seconds) as max_duration
                FROM processing_history
                WHERE created_at >= date('now', '-' || ? || ' days')
            ''', (
                ProcessingState.COMPLETED.value,
                ProcessingState.FAILED.value,
                days
            )).fetchone()
            
            # Daily stats
            daily_stats = conn.execute('''
                SELECT * FROM processing_stats
                WHERE date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            ''', (days,)).fetchall()
            
            # Currently processing
            processing_count = len(self.current_state)
            
        return {
            'period_days': days,
            'total_files': overall['total_files'] or 0,
            'completed': overall['completed'] or 0,
            'failed': overall['failed'] or 0,
            'currently_processing': processing_count,
            'average_duration_seconds': overall['avg_duration'] or 0,
            'min_duration_seconds': overall['min_duration'] or 0,
            'max_duration_seconds': overall['max_duration'] or 0,
            'daily_stats': [dict(row) for row in daily_stats],
            'success_rate': (
                (overall['completed'] / overall['total_files'] * 100)
                if overall['total_files'] > 0 else 0
            )
        }
        
    def cleanup_old_history(self, days: int = 90):
        """
        Clean up old processing history.
        
        Args:
            days: Keep history for this many days
        """
        with self._get_db() as conn:
            deleted = conn.execute('''
                DELETE FROM processing_history
                WHERE created_at < date('now', '-' || ? || ' days')
                AND state IN (?, ?)
            ''', (days, ProcessingState.COMPLETED.value, ProcessingState.ARCHIVED.value))
            
            if deleted.rowcount > 0:
                self.logger.info(f"Cleaned up {deleted.rowcount} old history entries")
                
    def recover_interrupted(self) -> List[str]:
        """
        Recover files that were interrupted during processing.
        
        Returns:
            List of file paths that need reprocessing
        """
        interrupted_files = []
        
        with self._lock:
            for file_path, info in list(self.current_state.items()):
                # Check if processing was started but not completed
                if info['state'] in [
                    ProcessingState.PROCESSING.value,
                    ProcessingState.DIARIZING.value,
                    ProcessingState.TRANSCRIBING.value,
                    ProcessingState.GENERATING.value
                ]:
                    # Mark as failed
                    self.complete_processing(
                        file_path, 
                        success=False,
                        error_message="Processing interrupted - system restart"
                    )
                    interrupted_files.append(file_path)
                    
        if interrupted_files:
            self.logger.warning(
                f"Found {len(interrupted_files)} interrupted files that need reprocessing"
            )
            
        return interrupted_files
        
    def export_history(self, output_path: Union[str, Path],
                      format: str = 'json') -> Path:
        """
        Export processing history.
        
        Args:
            output_path: Where to save the export
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        
        with self._get_db() as conn:
            rows = conn.execute('''
                SELECT * FROM processing_history
                ORDER BY created_at DESC
            ''').fetchall()
            
            data = [dict(row) for row in rows]
            
        if format == 'json':
            self.file_manager.save_json(output_path, data)
        elif format == 'csv':
            import csv
            
            if data:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        self.logger.info(f"Exported {len(data)} history entries to {output_path}")
        return output_path