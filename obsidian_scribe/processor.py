"""
Audio processing orchestrator for Obsidian Scribe.

Manages the processing pipeline for audio files including diarization,
transcription, and output generation.
"""

import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from threading import Thread, Event, Lock
from typing import Dict, List, Optional, Tuple

from .utils import (
    validate_audio_file,
    move_file_safely,
    format_timestamp,
    ensure_directory_exists
)


class ProcessingResult:
    """Container for processing results."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.success = False
        self.error_message: Optional[str] = None
        self.transcript_path: Optional[str] = None
        self.processing_time: float = 0.0
        self.diarization_result: Optional[Dict] = None
        self.transcription_result: Optional[Dict] = None


class AudioProcessor:
    """Core audio processing orchestrator."""
    
    def __init__(self, config: Dict):
        """
        Initialize the audio processor.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract configuration
        self.paths = config.get('paths', {})
        self.processing_config = config.get('processing', {})
        
        # Processing queue
        self.process_queue: Queue = Queue()
        self.failed_queue: Queue = Queue()
        
        # Threading components
        self._processing_thread: Optional[Thread] = None
        self._retry_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._running = False
        self._processing_lock = Lock()
        
        # Statistics
        self.stats = {
            'processed': 0,
            'failed': 0,
            'retried': 0,
            'total_time': 0.0
        }
        
    def start(self):
        """Start the audio processor."""
        if self._running:
            self.logger.warning("Audio processor is already running")
            return
            
        self.logger.info("Starting audio processor...")
        self._running = True
        self._stop_event.clear()
        
        # Start processing thread
        self._processing_thread = Thread(target=self._process_loop, daemon=True)
        self._processing_thread.start()
        
        # Start retry thread if enabled
        if self.processing_config.get('retry_failed', True):
            self._retry_thread = Thread(target=self._retry_loop, daemon=True)
            self._retry_thread.start()
            
        self.logger.info("Audio processor started successfully")
        
    def stop(self):
        """Stop the audio processor."""
        if not self._running:
            return
            
        self.logger.info("Stopping audio processor...")
        self._running = False
        self._stop_event.set()
        
        # Wait for threads to finish
        if self._processing_thread:
            self._processing_thread.join(timeout=5)
            self._processing_thread = None
            
        if self._retry_thread:
            self._retry_thread.join(timeout=5)
            self._retry_thread = None
            
        self.logger.info("Audio processor stopped")
        self.logger.info(f"Processing statistics: {self.stats}")
        
    def add_file(self, file_path: str):
        """
        Add a file to the processing queue.
        
        Args:
            file_path: Path to the audio file
        """
        # Validate file exists
        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return
            
        # Add to queue
        self.logger.info(f"Adding file to processing queue: {file_path}")
        self.process_queue.put(file_path)
        
    def _process_loop(self):
        """Main processing loop."""
        while self._running:
            try:
                # Get file from queue with timeout
                try:
                    file_path = self.process_queue.get(timeout=1.0)
                except Empty:
                    continue
                    
                if file_path and os.path.exists(file_path):
                    # Process the file
                    result = self._process_file(file_path)
                    
                    # Update statistics
                    with self._processing_lock:
                        if result.success:
                            self.stats['processed'] += 1
                        else:
                            self.stats['failed'] += 1
                            # Add to failed queue for retry
                            if self.processing_config.get('retry_failed', True):
                                self.failed_queue.put((file_path, 1, time.time()))
                                
                        self.stats['total_time'] += result.processing_time
                        
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}", exc_info=True)
                time.sleep(1)
                
    def _retry_loop(self):
        """Retry loop for failed files."""
        retry_delay = self.processing_config.get('retry_delay', 60)
        max_retries = self.processing_config.get('max_retries', 3)
        
        while self._running:
            try:
                # Check failed queue
                try:
                    file_path, retry_count, last_attempt = self.failed_queue.get(timeout=5.0)
                except Empty:
                    continue
                    
                # Check if enough time has passed
                if time.time() - last_attempt < retry_delay:
                    # Put it back in the queue
                    self.failed_queue.put((file_path, retry_count, last_attempt))
                    time.sleep(1)
                    continue
                    
                # Check if file still exists
                if not os.path.exists(file_path):
                    self.logger.warning(f"File no longer exists for retry: {file_path}")
                    continue
                    
                # Retry processing
                self.logger.info(f"Retrying file (attempt {retry_count + 1}): {file_path}")
                result = self._process_file(file_path)
                
                with self._processing_lock:
                    self.stats['retried'] += 1
                    
                if result.success:
                    self.stats['processed'] += 1
                    self.logger.info(f"Retry successful: {file_path}")
                else:
                    # Check if we should retry again
                    if retry_count < max_retries:
                        self.failed_queue.put((file_path, retry_count + 1, time.time()))
                    else:
                        self.logger.error(f"Max retries reached for: {file_path}")
                        # Move to failed folder
                        self._move_to_failed(file_path)
                        
            except Exception as e:
                self.logger.error(f"Error in retry loop: {e}", exc_info=True)
                time.sleep(5)
                
    def _process_file(self, file_path: str) -> ProcessingResult:
        """
        Process a single audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            ProcessingResult object
        """
        start_time = time.time()
        result = ProcessingResult(file_path)
        
        try:
            self.logger.info(f"Processing file: {file_path}")
            
            # Validate audio file
            if not validate_audio_file(file_path):
                raise ValueError("Invalid audio file format")
                
            # Get file info
            file_name = os.path.basename(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.logger.info(f"File: {file_name}, Size: {file_size_mb:.2f} MB")
            
            # TODO: Implement actual diarization
            # For now, create placeholder diarization result
            self.logger.info("Performing speaker diarization (placeholder)...")
            result.diarization_result = self._diarize_audio(file_path)
            
            # TODO: Implement actual transcription
            # For now, create placeholder transcription result
            self.logger.info("Performing transcription (placeholder)...")
            result.transcription_result = self._transcribe_audio(file_path)
            
            # Generate transcript
            self.logger.info("Generating transcript...")
            transcript_path = self._generate_transcript(file_path, result)
            result.transcript_path = transcript_path
            
            # Archive the original file
            self.logger.info("Archiving processed file...")
            self._archive_file(file_path)
            
            # Mark as successful
            result.success = True
            self.logger.info(f"Successfully processed: {file_name}")
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            result.error_message = str(e)
            result.success = False
            
        # Record processing time
        result.processing_time = time.time() - start_time
        self.logger.info(f"Processing time: {result.processing_time:.2f} seconds")
        
        return result
        
    def _diarize_audio(self, file_path: str) -> Dict:
        """
        Perform speaker diarization on audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Diarization results
        """
        # TODO: Implement actual diarization using pyannote.audio
        # This is a placeholder implementation
        return {
            'speakers': [
                {
                    'id': 'SPEAKER_00',
                    'segments': [
                        {'start': 0.0, 'end': 10.5},
                        {'start': 15.2, 'end': 25.8}
                    ]
                },
                {
                    'id': 'SPEAKER_01',
                    'segments': [
                        {'start': 10.5, 'end': 15.2},
                        {'start': 25.8, 'end': 35.0}
                    ]
                }
            ],
            'total_speakers': 2,
            'duration': 35.0
        }
        
    def _transcribe_audio(self, file_path: str) -> Dict:
        """
        Transcribe audio file using Whisper API.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcription results
        """
        # TODO: Implement actual transcription using OpenAI Whisper API
        # This is a placeholder implementation
        return {
            'text': 'This is a placeholder transcription. Actual implementation will use the Whisper API.',
            'segments': [
                {
                    'start': 0.0,
                    'end': 10.5,
                    'text': 'Hello, this is speaker one talking.'
                },
                {
                    'start': 10.5,
                    'end': 15.2,
                    'text': 'And this is speaker two responding.'
                },
                {
                    'start': 15.2,
                    'end': 25.8,
                    'text': 'Speaker one continues the conversation here.'
                },
                {
                    'start': 25.8,
                    'end': 35.0,
                    'text': 'Speaker two concludes the discussion.'
                }
            ],
            'language': 'en'
        }
        
    def _generate_transcript(self, file_path: str, result: ProcessingResult) -> str:
        """
        Generate the final transcript file.
        
        Args:
            file_path: Original audio file path
            result: Processing result with diarization and transcription
            
        Returns:
            Path to the generated transcript
        """
        # Create transcript filename
        base_name = Path(file_path).stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        transcript_name = f"{base_name}_{timestamp}.md"
        transcript_path = os.path.join(self.paths.get('transcript_folder', './Transcripts'), transcript_name)
        
        # Ensure transcript directory exists
        ensure_directory_exists(os.path.dirname(transcript_path))
        
        # Generate markdown content
        content = self._format_transcript_markdown(file_path, result)
        
        # Write transcript file
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.logger.info(f"Transcript saved to: {transcript_path}")
        return transcript_path
        
    def _format_transcript_markdown(self, file_path: str, result: ProcessingResult) -> str:
        """
        Format the transcript as Markdown.
        
        Args:
            file_path: Original audio file path
            result: Processing result
            
        Returns:
            Formatted Markdown content
        """
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        # Create YAML front matter
        front_matter = f"""---
title: Audio Transcript - {Path(file_path).stem}
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [transcript, audio]
audio_file: "{file_name}"
file_size_mb: {file_size:.2f}
duration_seconds: {result.diarization_result.get('duration', 0):.1f}
speakers: {result.diarization_result.get('total_speakers', 0)}
processing_time: {result.processing_time:.2f}
---

# Audio Transcript

**Original File**: [[{file_name}]]
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration**: {format_timestamp(result.diarization_result.get('duration', 0))}
**Speakers**: {result.diarization_result.get('total_speakers', 0)}

---

## Transcript

"""
        
        # Add placeholder content for now
        # TODO: Implement actual transcript formatting with speaker segments
        content = front_matter
        content += "🗣 **SPEAKER_00** [00:00:00]\n\n"
        content += "This is a placeholder transcript. The actual implementation will combine diarization and transcription results.\n\n"
        content += "🗣 **SPEAKER_01** [00:00:10]\n\n"
        content += "Each speaker section will be clearly marked with timestamps.\n\n"
        
        return content
        
    def _archive_file(self, file_path: str):
        """
        Archive a processed audio file.
        
        Args:
            file_path: Path to the audio file
        """
        archive_folder = self.paths.get('archive_folder', './Audio/Archive')
        ensure_directory_exists(archive_folder)
        
        # Create archive path with date subfolder
        date_folder = datetime.now().strftime('%Y-%m-%d')
        archive_subfolder = os.path.join(archive_folder, date_folder)
        ensure_directory_exists(archive_subfolder)
        
        # Move file to archive
        file_name = os.path.basename(file_path)
        archive_path = os.path.join(archive_subfolder, file_name)
        
        move_file_safely(file_path, archive_path)
        self.logger.info(f"Archived file to: {archive_path}")
        
    def _move_to_failed(self, file_path: str):
        """
        Move a file to the failed folder.
        
        Args:
            file_path: Path to the audio file
        """
        failed_folder = os.path.join(self.paths.get('audio_folder', './Audio'), 'Failed')
        ensure_directory_exists(failed_folder)
        
        # Move file to failed folder
        file_name = os.path.basename(file_path)
        failed_path = os.path.join(failed_folder, file_name)
        
        try:
            move_file_safely(file_path, failed_path)
            self.logger.error(f"Moved failed file to: {failed_path}")
        except Exception as e:
            self.logger.error(f"Could not move failed file: {e}")
            
    def get_stats(self) -> Dict:
        """Get processing statistics."""
        with self._processing_lock:
            return self.stats.copy()
            
    def get_queue_size(self) -> int:
        """Get the current size of the processing queue."""
        return self.process_queue.qsize()