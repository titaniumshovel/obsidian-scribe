"""
Configuration schema and validation for Obsidian Scribe.

Defines the structure and validation rules for configuration.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path


class ConfigSchema:
    """Configuration schema validator."""
    
    def __init__(self):
        """Initialize the configuration schema."""
        self.logger = logging.getLogger(__name__)
        
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            # Validate paths section
            self._validate_paths(config.get('paths', {}))
            
            # Validate watcher section
            self._validate_watcher(config.get('watcher', {}))
            
            # Validate audio section
            self._validate_audio(config.get('audio', {}))
            
            # Validate diarization section
            self._validate_diarization(config.get('diarization', {}))
            
            # Validate transcription section
            self._validate_transcription(config.get('transcription', {}))
            
            # Validate markdown section
            self._validate_markdown(config.get('markdown', {}))
            
            # Validate logging section
            self._validate_logging(config.get('logging', {}))
            
            # Validate processing section
            self._validate_processing(config.get('processing', {}))
            
            self.logger.debug("Configuration validation successful")
            return True
            
        except ValueError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
            
    def _validate_paths(self, paths: Dict[str, Any]):
        """Validate paths configuration."""
        required_paths = ['audio_folder', 'transcript_folder', 'archive_folder', 'temp_folder']
        
        for path_key in required_paths:
            if path_key not in paths:
                raise ValueError(f"Missing required path: {path_key}")
                
            path_value = paths[path_key]
            if not isinstance(path_value, str):
                raise ValueError(f"Path {path_key} must be a string")
                
    def _validate_watcher(self, watcher: Dict[str, Any]):
        """Validate watcher configuration."""
        # Validate file extensions
        if 'file_extensions' in watcher:
            extensions = watcher['file_extensions']
            if not isinstance(extensions, list):
                raise ValueError("file_extensions must be a list")
            for ext in extensions:
                if not isinstance(ext, str) or not ext.startswith('.'):
                    raise ValueError(f"Invalid file extension: {ext}")
                    
        # Validate poll interval
        if 'poll_interval' in watcher:
            interval = watcher['poll_interval']
            if not isinstance(interval, (int, float)) or interval <= 0:
                raise ValueError("poll_interval must be a positive number")
                
        # Validate ignore patterns
        if 'ignore_patterns' in watcher:
            patterns = watcher['ignore_patterns']
            if not isinstance(patterns, list):
                raise ValueError("ignore_patterns must be a list")
                
    def _validate_audio(self, audio: Dict[str, Any]):
        """Validate audio configuration."""
        # Validate max file size
        if 'max_file_size_mb' in audio:
            size = audio['max_file_size_mb']
            if not isinstance(size, (int, float)) or size <= 0:
                raise ValueError("max_file_size_mb must be a positive number")
                
        # Validate sample rate
        if 'sample_rate' in audio:
            rate = audio['sample_rate']
            if not isinstance(rate, int) or rate <= 0:
                raise ValueError("sample_rate must be a positive integer")
                
    def _validate_diarization(self, diarization: Dict[str, Any]):
        """Validate diarization configuration."""
        # Validate model
        if 'model' in diarization:
            model = diarization['model']
            if not isinstance(model, str):
                raise ValueError("diarization model must be a string")
                
        # Validate hf_token
        if 'hf_token' in diarization:
            token = diarization['hf_token']
            # Allow empty string (will check environment variable)
            if not isinstance(token, str):
                raise ValueError("hf_token must be a string")
                
        # Validate speaker counts
        if 'min_speakers' in diarization:
            min_speakers = diarization['min_speakers']
            if not isinstance(min_speakers, int) or min_speakers < 1:
                raise ValueError("min_speakers must be a positive integer")
                
        if 'max_speakers' in diarization:
            max_speakers = diarization['max_speakers']
            if not isinstance(max_speakers, int) or max_speakers < 0:
                raise ValueError("max_speakers must be a non-negative integer (0 for automatic)")
                
        # Validate min/max relationship
        if 'min_speakers' in diarization and 'max_speakers' in diarization:
            # Skip validation if max_speakers is 0 (automatic detection)
            if diarization['max_speakers'] > 0 and diarization['min_speakers'] > diarization['max_speakers']:
                raise ValueError("min_speakers cannot be greater than max_speakers")
                
        # Validate min segment duration
        if 'min_segment_duration' in diarization:
            duration = diarization['min_segment_duration']
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError("min_segment_duration must be a positive number")
                
    def _validate_transcription(self, transcription: Dict[str, Any]):
        """Validate transcription configuration."""
        # Validate API endpoint
        if 'api_endpoint' in transcription:
            endpoint = transcription['api_endpoint']
            if not isinstance(endpoint, str) or not endpoint.startswith(('http://', 'https://')):
                raise ValueError("api_endpoint must be a valid HTTP(S) URL")
                
        # Validate model
        if 'model' in transcription:
            model = transcription['model']
            if not isinstance(model, str):
                raise ValueError("transcription model must be a string")
                
        # Validate language
        if 'language' in transcription:
            language = transcription['language']
            # Allow empty string for auto-detection
            if language and (not isinstance(language, str) or len(language) != 2):
                raise ValueError("language must be a 2-letter language code or empty for auto-detection")
                
        # Validate temperature
        if 'temperature' in transcription:
            temp = transcription['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
                raise ValueError("temperature must be between 0 and 1")
                
        # Validate timeout
        if 'timeout' in transcription:
            timeout = transcription['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValueError("timeout must be a positive number")
                
        # Validate max retries
        if 'max_retries' in transcription:
            retries = transcription['max_retries']
            if not isinstance(retries, int) or retries < 0:
                raise ValueError("max_retries must be a non-negative integer")
                
    def _validate_markdown(self, markdown: Dict[str, Any]):
        """Validate markdown configuration."""
        # Validate boolean flags
        bool_fields = ['include_timestamps']
        for field in bool_fields:
            if field in markdown and not isinstance(markdown[field], bool):
                raise ValueError(f"{field} must be a boolean")
                
        # Validate timestamp format
        if 'timestamp_format' in markdown:
            format_str = markdown['timestamp_format']
            if not isinstance(format_str, str):
                raise ValueError("timestamp_format must be a string")
                
        # Validate tags
        if 'tags' in markdown:
            tags = markdown['tags']
            if not isinstance(tags, list):
                raise ValueError("tags must be a list")
            for tag in tags:
                if not isinstance(tag, str):
                    raise ValueError("All tags must be strings")
                    
    def _validate_logging(self, logging_config: Dict[str, Any]):
        """Validate logging configuration."""
        # Validate log level
        if 'level' in logging_config:
            level = logging_config['level']
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level not in valid_levels:
                raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
                
        # Validate log file
        if 'file' in logging_config:
            file_path = logging_config['file']
            if not isinstance(file_path, str):
                raise ValueError("log file must be a string")
                
        # Validate max size
        if 'max_size_mb' in logging_config:
            size = logging_config['max_size_mb']
            if not isinstance(size, (int, float)) or size <= 0:
                raise ValueError("max_size_mb must be a positive number")
                
        # Validate backup count
        if 'backup_count' in logging_config:
            count = logging_config['backup_count']
            if not isinstance(count, int) or count < 0:
                raise ValueError("backup_count must be a non-negative integer")
                
    def _validate_processing(self, processing: Dict[str, Any]):
        """Validate processing configuration."""
        # Validate concurrent files
        if 'concurrent_files' in processing:
            concurrent = processing['concurrent_files']
            if not isinstance(concurrent, int) or concurrent < 1:
                raise ValueError("concurrent_files must be a positive integer")
                
        # Validate retry settings
        if 'retry_failed' in processing:
            retry = processing['retry_failed']
            if not isinstance(retry, bool):
                raise ValueError("retry_failed must be a boolean")
                
        if 'retry_delay' in processing:
            delay = processing['retry_delay']
            if not isinstance(delay, (int, float)) or delay < 0:
                raise ValueError("retry_delay must be a non-negative number")
                
        if 'max_retries' in processing:
            retries = processing['max_retries']
            if not isinstance(retries, int) or retries < 0:
                raise ValueError("max_retries must be a non-negative integer")