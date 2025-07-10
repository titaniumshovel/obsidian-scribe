"""
Default configuration values for Obsidian Scribe.

This module defines the default configuration structure and values
that are used when no configuration file is provided.
"""

DEFAULT_CONFIG = {
    'obsidian_scribe': {
        # Paths configuration
        'paths': {
            'audio_folder': './Audio',              # Folder to monitor for audio files
            'transcript_folder': './Transcripts',   # Output folder for transcripts
            'archive_folder': './Audio/Archive',    # Archive for processed files
            'temp_folder': './temp'                 # Temporary file storage
        },
        
        # File watching configuration
        'watcher': {
            'file_extensions': ['.wav', '.mp3'],    # Supported audio formats
            'poll_interval': 1.0,                   # Seconds between folder checks
            'ignore_patterns': ['.*', '~*']         # Patterns to ignore
        },
        
        # Audio processing configuration
        'audio': {
            'max_file_size_mb': 500,                # Maximum file size to process
            'sample_rate': 16000                    # Target sample rate for processing
        },
        
        # Speaker diarization configuration
        'diarization': {
            'model': 'pyannote/speaker-diarization',  # Pyannote model to use
            'min_speakers': 1,                      # Minimum expected speakers
            'max_speakers': 10,                     # Maximum expected speakers
            'min_segment_duration': 0.5             # Minimum segment duration in seconds
        },
        
        # Transcription configuration
        'transcription': {
            'api_endpoint': 'https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/audio/transcriptions',
            'model': 'whisper-1',
            'api_key_env': 'OPENAI_API_KEY',        # Environment variable for API key
            'language': 'en',                       # Default language
            'temperature': 0.0,                     # Model temperature
            'timeout': 300,                         # API timeout in seconds
            'max_retries': 3,                       # Maximum retry attempts
            'chunk_size_mb': 24,                    # Maximum chunk size for API
            'chunk_overlap_seconds': 0.5            # Overlap between chunks
        },
        
        # Markdown generation configuration
        'markdown': {
            'include_timestamps': True,             # Include timestamps in transcript
            'timestamp_format': '[%H:%M:%S]',       # Timestamp format
            'speaker_emoji': '🗣',                  # Emoji for speaker headings
            'default_title': 'Audio Transcript',    # Default title if none provided
            'tags': ['transcript', 'audio'],        # Default tags
            'template': 'default'                   # Markdown template to use
        },
        
        # Logging configuration
        'logging': {
            'level': 'INFO',                        # Log level (DEBUG, INFO, WARNING, ERROR)
            'file': 'obsidian_scribe.log',          # Log file name
            'max_size_mb': 10,                      # Maximum log file size
            'backup_count': 5,                      # Number of backup logs to keep
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        
        # Processing configuration
        'processing': {
            'concurrent_files': 1,                  # Number of files to process simultaneously
            'retry_failed': True,                   # Retry failed files
            'retry_delay': 60,                      # Seconds to wait before retry
            'max_retries': 3,                       # Maximum retry attempts
            'state_file': '.obsidian_scribe_state.json'  # Processing state file
        },
        
        # Cache configuration
        'cache': {
            'enabled': True,                        # Enable caching
            'directory': '.cache',                  # Cache directory
            'max_size_mb': 500,                     # Maximum cache size
            'ttl_hours': 24                         # Cache time-to-live in hours
        }
    }
}

# Flatten the configuration for easier access
DEFAULT_CONFIG = DEFAULT_CONFIG['obsidian_scribe']