"""
Audio processing orchestration for Obsidian Scribe.

Manages the processing pipeline for audio files including diarization,
transcription, and output generation.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from threading import Thread, Event, Lock
from typing import Dict, List, Optional, Tuple

from ..storage.file_manager import FileManager
from ..storage.archive import ArchiveManager
from ..transcript.generator import TranscriptGenerator
from .diarizer import SpeakerDiarizer
from .transcriber import WhisperTranscriber
from .converter import AudioConverter
from .chunker import AudioChunker


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
        self.file_watcher = None  # Will be set by FileWatcher
        
        # Extract configuration
        self.paths = config.get('paths', {})
        self.processing_config = config.get('processing', {})
        self.audio_config = config.get('audio', {})
        
        # Initialize components
        self.file_manager = FileManager(config)
        self.archive_manager = ArchiveManager(config, self.file_manager)
        self.diarizer = SpeakerDiarizer(config)
        self.transcriber = WhisperTranscriber(config)
        self.converter = AudioConverter(config)
        self.chunker = AudioChunker(config)
        self.transcript_generator = TranscriptGenerator(config)
        
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
        if not Path(file_path).exists():
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
                    
                if file_path and Path(file_path).exists():
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
                if not Path(file_path).exists():
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
            if not self.file_manager.validate_audio_file(file_path):
                raise ValueError("Invalid audio file format")
                
            # Get file info
            file_info = self.file_manager.get_file_info(file_path)
            self.logger.info(f"File: {file_info['name']}, Size: {file_info['size_mb']:.2f} MB")
            
            # Convert audio if needed
            converted_path = self._prepare_audio(file_path)
            
            # Check if file needs chunking
            chunks = self._chunk_if_needed(converted_path, file_info)
            
            # Check if diarization is enabled
            diarization_enabled = self.config.get('diarization', {}).get('enabled', True)
            
            if diarization_enabled:
                self.logger.info("Performing speaker diarization...")
                
                def diarization_progress(message: str, percentage: float):
                    self.logger.info(f"Diarization progress: {message} ({percentage:.0f}%)")
                
                result.diarization_result = self.diarizer.diarize(converted_path, progress_callback=diarization_progress)
            else:
                # Calculate time savings
                file_size_mb = file_info.get('size_mb', 0)
                estimated_time_saved = file_size_mb * 75  # seconds (75s/MB baseline)
                
                self.logger.info("Skipping speaker diarization (disabled)")
                self.logger.info(f"Estimated time saved: {estimated_time_saved:.0f}s ({estimated_time_saved/60:.1f}m)")
                result.diarization_result = None
            
            # Perform transcription
            self.logger.info("Performing transcription...")
            if chunks:
                # Transcribe chunks and combine
                result.transcription_result = self._transcribe_chunks(chunks)
            else:
                # Transcribe whole file
                result.transcription_result = self.transcriber.transcribe(converted_path)
            
            # Generate transcript
            self.logger.info("Generating transcript...")
            transcript_path = self.transcript_generator.generate(
                file_path,
                result.diarization_result,
                result.transcription_result
            )
            result.transcript_path = transcript_path
            
            # Archive the original file
            self.logger.info("Archiving processed file...")
            self.archive_manager.archive_file(file_path)
            
            # Clean up temporary files
            if converted_path != file_path:
                self.file_manager.delete_file(converted_path)
            if chunks:
                for chunk in chunks:
                    self.file_manager.delete_file(chunk)
            
            # Mark as successful
            result.success = True
            self.logger.info(f"Successfully processed: {file_info['name']}")
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            result.error_message = str(e)
            result.success = False
            
            # Clear the file from processing set if file watcher is available
            if hasattr(self, 'file_watcher') and self.file_watcher:
                self.file_watcher.clear_processing_file(file_path)
                self.logger.debug(f"Cleared {file_path} from processing set")
            
        # Record processing time
        result.processing_time = time.time() - start_time
        self.logger.info(f"Processing time: {result.processing_time:.2f} seconds")
        
        return result
        
    def _prepare_audio(self, file_path: str) -> str:
        """
        Prepare audio file for processing (convert if needed).
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Path to prepared audio file
        """
        # Check if conversion is needed
        if self.converter.needs_conversion(file_path):
            self.logger.info("Converting audio format...")
            return self.converter.convert(file_path)
        return file_path
        
    def _chunk_if_needed(self, file_path: str, file_info: Dict) -> Optional[List[str]]:
        """
        Check if file needs chunking and chunk if necessary.
        
        Args:
            file_path: Path to the audio file
            file_info: File information dictionary
            
        Returns:
            List of chunk paths if chunked, None otherwise
        """
        max_size_mb = self.config.get('transcription', {}).get('chunk_size_mb', 24)
        
        if file_info['size_mb'] > max_size_mb:
            self.logger.info(f"File size ({file_info['size_mb']:.2f} MB) exceeds limit ({max_size_mb} MB), chunking...")
            return self.chunker.chunk_audio(file_path)
            
        return None
        
    def _transcribe_chunks(self, chunks: List[str]) -> Dict:
        """
        Transcribe multiple audio chunks and combine results.
        
        Args:
            chunks: List of chunk file paths
            
        Returns:
            Combined transcription result
        """
        self.logger.info(f"Transcribing {len(chunks)} chunks...")
        
        all_segments = []
        full_text = []
        
        for i, chunk in enumerate(chunks):
            self.logger.info(f"Transcribing chunk {i+1}/{len(chunks)}...")
            chunk_result = self.transcriber.transcribe(chunk)
            
            if chunk_result and 'segments' in chunk_result:
                all_segments.extend(chunk_result['segments'])
                full_text.append(chunk_result.get('text', ''))
                
        return {
            'text': ' '.join(full_text),
            'segments': all_segments,
            'language': chunk_result.get('language', 'en') if chunks else 'en'
        }
        
    def _move_to_failed(self, file_path: str):
        """
        Move a file to the failed folder.
        
        Args:
            file_path: Path to the audio file
        """
        failed_folder = Path(self.paths.get('audio_folder', './Audio')) / 'Failed'
        self.file_manager.ensure_directory(failed_folder)
        
        try:
            dest = failed_folder / Path(file_path).name
            self.file_manager.move_file(file_path, dest)
            self.logger.error(f"Moved failed file to: {dest}")
        except Exception as e:
            self.logger.error(f"Could not move failed file: {e}")
            
    def get_stats(self) -> Dict:
        """Get processing statistics."""
        with self._processing_lock:
            return self.stats.copy()
            
    def get_queue_size(self) -> int:
        """Get the current size of the processing queue."""
        return self.process_queue.qsize()