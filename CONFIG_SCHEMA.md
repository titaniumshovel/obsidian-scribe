# Obsidian Scribe Configuration Schema

## Overview

This document provides a comprehensive reference for configuring Obsidian Scribe. The application uses a YAML configuration file with sensible defaults and environment variable overrides.

## Configuration File Location

The configuration file is loaded in the following order of precedence:
1. Path specified via `--config` command-line argument
2. `OBSIDIAN_SCRIBE_CONFIG` environment variable
3. `./config.yaml` in the current directory
4. `~/.obsidian-scribe/config.yaml` in user home directory
5. Default configuration (built-in)

## Complete Configuration Schema

```yaml
# Obsidian Scribe Configuration
# All paths can use environment variables: ${HOME}, ${OBSIDIAN_VAULT}, etc.

obsidian_scribe:
  # General application settings
  general:
    # Enable/disable the application
    enabled: true
    
    # Run in daemon mode (background)
    daemon: false
    
    # Process existing files on startup
    process_existing: false
    
    # Dry run mode (no files written)
    dry_run: false

  # Path configuration
  paths:
    # Audio folder to monitor (required)
    # Can be absolute or relative to Obsidian vault
    audio_folder: "${OBSIDIAN_VAULT}/Audio"
    
    # Output folder for transcripts (required)
    transcript_folder: "${OBSIDIAN_VAULT}/Transcripts"
    
    # Archive folder for processed audio files
    # Set to null to disable archiving
    archive_folder: "${OBSIDIAN_VAULT}/Audio/Archive"
    
    # Temporary file storage
    temp_folder: "${TEMP}/obsidian-scribe"
    
    # Failed files folder
    failed_folder: "${OBSIDIAN_VAULT}/Audio/Failed"

  # File watching configuration
  watcher:
    # File extensions to monitor (case-insensitive)
    file_extensions: 
      - ".wav"
      - ".mp3"
      - ".m4a"
      - ".flac"
      - ".ogg"
    
    # Polling interval in seconds (for systems without native events)
    poll_interval: 1.0
    
    # Patterns to ignore (glob patterns)
    ignore_patterns: 
      - ".*"          # Hidden files
      - "~*"          # Temporary files
      - "*.tmp"       # Temp extensions
      - "*.partial"   # Partial downloads
    
    # Minimum file age in seconds before processing
    # Prevents processing files still being written
    min_file_age: 5
    
    # Use polling instead of native events
    force_polling: false

  # Audio processing configuration
  audio:
    # Maximum file size in MB
    max_file_size_mb: 500
    
    # Minimum file size in KB
    min_file_size_kb: 10
    
    # Target sample rate for processing
    sample_rate: 16000
    
    # Audio channels (1=mono, 2=stereo)
    # Mono recommended for speech
    channels: 1
    
    # Audio format for processing
    format: "wav"
    
    # Enable audio normalization
    normalize: true
    
    # Silence threshold (dB)
    silence_threshold: -40
    
    # Minimum audio duration in seconds
    min_duration: 1.0

  # Speaker diarization configuration
  diarization:
    # Enable speaker diarization
    enabled: true
    
    # Pyannote model to use
    model: "pyannote/speaker-diarization"
    
    # Model cache directory
    model_cache: "${HOME}/.cache/pyannote"
    
    # Minimum number of speakers
    min_speakers: 1
    
    # Maximum number of speakers
    max_speakers: 10
    
    # Minimum segment duration in seconds
    min_segment_duration: 0.5
    
    # Speaker embedding window size
    embedding_window: 1.5
    
    # Clustering algorithm: "AgglomerativeClustering" or "SpectralClustering"
    clustering: "AgglomerativeClustering"
    
    # Confidence threshold (0.0-1.0)
    confidence_threshold: 0.5
    
    # Use GPU if available
    use_gpu: true
    
    # Device selection: "cuda", "cpu", or "auto"
    device: "auto"

  # Transcription configuration
  transcription:
    # API endpoint (required)
    api_endpoint: "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/audio/transcriptions"
    
    # Model name
    model: "whisper-1"
    
    # API key environment variable name
    api_key_env: "OPENAI_API_KEY"
    
    # Language code (ISO 639-1)
    # Set to null for auto-detection
    language: "en"
    
    # Temperature for sampling (0.0-1.0)
    # Lower = more deterministic
    temperature: 0.0
    
    # API timeout in seconds
    timeout: 300
    
    # Maximum retries for failed requests
    max_retries: 3
    
    # Retry delay in seconds (exponential backoff)
    retry_delay: 1.0
    
    # Maximum retry delay
    max_retry_delay: 60.0
    
    # Chunk size for large files (in seconds)
    # Set to null to disable chunking
    chunk_size: 600  # 10 minutes
    
    # Overlap between chunks (in seconds)
    chunk_overlap: 5
    
    # Include word-level timestamps
    word_timestamps: false
    
    # Response format: "json", "text", "srt", "verbose_json", "vtt"
    response_format: "verbose_json"
    
    # Custom headers for API requests
    custom_headers:
      # "X-Custom-Header": "value"

  # Markdown generation configuration
  markdown:
    # Include timestamps in transcript
    include_timestamps: true
    
    # Timestamp format (strftime format)
    timestamp_format: "[%H:%M:%S]"
    
    # Alternative formats:
    # timestamp_format: "[%M:%S]"      # Minutes and seconds only
    # timestamp_format: "(%H:%M:%S)"   # Parentheses
    # timestamp_format: "%H:%M:%S -"   # Dash separator
    
    # Speaker label format
    # Variables: {number}, {name}, {emoji}
    speaker_format: "## {emoji} Speaker {number}"
    
    # Speaker emoji
    speaker_emoji: "🗣"
    
    # Use speaker names if available
    use_speaker_names: true
    
    # Default speaker names mapping
    speaker_names:
      # "Speaker 1": "John Doe"
      # "Speaker 2": "Jane Smith"
    
    # Default title if none provided
    default_title: "Audio Transcript"
    
    # Title format
    # Variables: {filename}, {date}, {time}
    title_format: "{filename} - {date}"
    
    # Default tags
    tags: 
      - "transcript"
      - "audio"
      - "meeting"
    
    # Additional front matter fields
    extra_front_matter:
      # "project": "Default Project"
      # "type": "meeting"
    
    # Include audio file link
    include_audio_link: true
    
    # Audio link format
    audio_link_format: "[[{path}]]"
    
    # Include summary section
    include_summary: false
    
    # Summary prompt (if using AI summary)
    summary_prompt: "Summarize the key points from this transcript"
    
    # Line width for text wrapping (0 = no wrapping)
    line_width: 0
    
    # Section separator
    section_separator: "\n---\n"

  # Logging configuration
  logging:
    # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    level: "INFO"
    
    # Log file path
    file: "obsidian_scribe.log"
    
    # Log to console
    console: true
    
    # Console log level (can be different from file)
    console_level: "INFO"
    
    # Maximum log file size in MB
    max_size_mb: 10
    
    # Number of backup log files to keep
    backup_count: 5
    
    # Log format
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Date format for logs
    date_format: "%Y-%m-%d %H:%M:%S"
    
    # Include thread name in logs
    include_thread: false
    
    # Log performance metrics
    log_performance: true

  # Processing configuration
  processing:
    # Number of files to process concurrently
    concurrent_files: 1
    
    # Maximum workers for parallel processing
    max_workers: 4
    
    # Queue size for pending files
    queue_size: 100
    
    # Retry failed files
    retry_failed: true
    
    # Retry delay in seconds
    retry_delay: 60
    
    # Maximum retry attempts
    max_retry_attempts: 3
    
    # Delete original files after processing
    # WARNING: Only enable if archiving is configured
    delete_original: false
    
    # Skip files older than X days (0 = no limit)
    skip_older_than_days: 0
    
    # Process files in order: "created", "modified", "name", "size"
    processing_order: "created"
    
    # Reverse processing order
    reverse_order: false

  # Performance tuning
  performance:
    # Memory limit in MB (0 = no limit)
    memory_limit_mb: 0
    
    # CPU cores to use (0 = all cores)
    cpu_cores: 0
    
    # Enable memory profiling
    profile_memory: false
    
    # Cache size for models in MB
    model_cache_size_mb: 1000
    
    # Preload models on startup
    preload_models: true
    
    # Batch size for API requests
    api_batch_size: 1

  # Notification configuration
  notifications:
    # Enable notifications
    enabled: false
    
    # Notification on completion
    on_completion: true
    
    # Notification on error
    on_error: true
    
    # Notification method: "desktop", "email", "webhook"
    method: "desktop"
    
    # Email configuration (if method = "email")
    email:
      smtp_host: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password_env: "EMAIL_PASSWORD"
      from_address: "obsidian-scribe@example.com"
      to_addresses:
        - "user@example.com"
    
    # Webhook configuration (if method = "webhook")
    webhook:
      url: "https://hooks.example.com/obsidian-scribe"
      method: "POST"
      headers:
        "Content-Type": "application/json"

  # Advanced configuration
  advanced:
    # Enable debug mode
    debug: false
    
    # Validate configuration on startup
    validate_config: true
    
    # Health check interval in seconds
    health_check_interval: 300
    
    # Enable metrics collection
    collect_metrics: false
    
    # Metrics export format: "prometheus", "json"
    metrics_format: "json"
    
    # Metrics export path
    metrics_path: "metrics.json"
    
    # Plugin directory
    plugin_directory: "plugins"
    
    # Enable plugins
    enable_plugins: false
```

## Environment Variables

All configuration values can be overridden using environment variables with the prefix `OBSIDIAN_SCRIBE_`:

```bash
# Examples
export OBSIDIAN_SCRIBE_PATHS_AUDIO_FOLDER="/path/to/audio"
export OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY_ENV="MY_API_KEY"
export OBSIDIAN_SCRIBE_LOGGING_LEVEL="DEBUG"
export OBSIDIAN_SCRIBE_DIARIZATION_MAX_SPEAKERS=20
```

## Configuration Profiles

You can use different configuration profiles for different scenarios:

### Minimal Configuration (config.minimal.yaml)
```yaml
obsidian_scribe:
  paths:
    audio_folder: "./Audio"
    transcript_folder: "./Transcripts"
  transcription:
    api_endpoint: "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/audio/transcriptions"
    api_key_env: "OPENAI_API_KEY"
```

### Development Configuration (config.dev.yaml)
```yaml
obsidian_scribe:
  general:
    dry_run: true
  logging:
    level: "DEBUG"
    console_level: "DEBUG"
  processing:
    concurrent_files: 1
  advanced:
    debug: true
```

### Production Configuration (config.prod.yaml)
```yaml
obsidian_scribe:
  general:
    daemon: true
  logging:
    level: "WARNING"
    console: false
  processing:
    concurrent_files: 4
    retry_failed: true
  notifications:
    enabled: true
    on_error: true
```

## Validation Rules

The configuration is validated according to these rules:

1. **Required Fields**:
   - `paths.audio_folder`
   - `paths.transcript_folder`
   - `transcription.api_endpoint`

2. **Path Validation**:
   - All paths must be valid and accessible
   - Audio folder must exist
   - Transcript folder will be created if missing

3. **Numeric Ranges**:
   - `diarization.min_speakers` >= 1
   - `diarization.max_speakers` >= `min_speakers`
   - `transcription.temperature` between 0.0 and 1.0
   - `processing.concurrent_files` >= 1

4. **API Configuration**:
   - API key must be available via environment variable
   - API endpoint must be a valid URL

## Best Practices

1. **Security**:
   - Never store API keys in configuration files
   - Use environment variables for sensitive data
   - Restrict file permissions on config files

2. **Performance**:
   - Adjust `concurrent_files` based on system resources
   - Enable GPU for diarization if available
   - Use appropriate chunk sizes for large files

3. **Reliability**:
   - Enable retry logic for production use
   - Configure appropriate timeouts
   - Set up proper logging and monitoring

4. **Organization**:
   - Use consistent folder structures
   - Enable archiving to prevent reprocessing
   - Configure meaningful tags and metadata

This configuration schema provides maximum flexibility while maintaining sensible defaults for most use cases.