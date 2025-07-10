# Configuration Guide

Obsidian Scribe uses a flexible configuration system that supports YAML files, environment variables, and programmatic overrides.

## Configuration Hierarchy

Configuration values are loaded in the following order (later sources override earlier ones):

1. Default configuration (built-in)
2. Configuration file (`config.yaml`)
3. Environment variables
4. Command-line arguments
5. Programmatic overrides

## Configuration File

The main configuration file is `config.yaml`. Copy `config.example.yaml` to get started:

```bash
cp config.example.yaml config.yaml
```

## Configuration Sections

### Paths Configuration

```yaml
paths:
  audio_folder: "./Audio"           # Where to watch for new audio files
  transcript_folder: "./Transcripts" # Where to save transcripts
  archive_folder: "./Audio/Archive"  # Where to move processed files
  temp_folder: "./temp"             # Temporary file storage
  cache_folder: "./cache"           # Cache storage location
  state_file: "./state.db"          # Processing state database
```

### File Watcher Settings

```yaml
watcher:
  file_extensions:                  # Audio file types to process
    - ".wav"
    - ".mp3"
    - ".m4a"
    - ".flac"
    - ".ogg"
  poll_interval: 1.0               # How often to check for new files (seconds)
  ignore_patterns:                 # Patterns to ignore
    - ".*"                         # Hidden files
    - "~*"                         # Temporary files
  min_file_size_mb: 0.1           # Minimum file size to process
  max_file_size_mb: 500           # Maximum file size to process
  file_ready_timeout: 30          # Wait time for file to be ready (seconds)
```

### Processing Configuration

```yaml
processing:
  concurrent_files: 2              # Number of files to process simultaneously
  retry_failed: true              # Retry failed transcriptions
  retry_delay: 300                # Delay before retry (seconds)
  max_retries: 3                  # Maximum retry attempts
  priority_rules:
    size_based: true              # Prioritize smaller files
    age_based: true               # Prioritize older files
    name_patterns:                # Custom priority patterns
      - pattern: "urgent_*"
        priority: 10
      - pattern: "meeting_*"
        priority: 5
```

### Audio Processing Settings

```yaml
audio:
  sample_rate: 16000              # Target sample rate for processing
  channels: 1                     # Convert to mono (1) or stereo (2)
  format: "wav"                   # Internal processing format
  chunk_duration: 300             # Chunk size in seconds (5 minutes)
  overlap_duration: 2             # Overlap between chunks (seconds)
  silence_threshold: -40          # Silence detection threshold (dB)
  min_silence_duration: 0.5       # Minimum silence duration (seconds)
```

### Transcription Settings

```yaml
transcription:
  api_key: "${OBSIDIAN_SCRIBE_API_KEY}"  # OpenAI API key (use env var)
  api_base: "https://api.openai.com/v1"  # API endpoint
  model: "whisper-1"                     # Model to use
  language: "en"                         # Language code or "auto"
  temperature: 0.0                       # Sampling temperature (0-1)
  prompt: ""                            # Optional context prompt
  response_format: "verbose_json"        # Response format
  timeout: 300                          # API timeout (seconds)
  max_retries: 3                        # API retry attempts
```

### Speaker Diarization Settings

```yaml
diarization:
  enabled: true                          # Enable speaker identification
  model: "pyannote/speaker-diarization"  # Diarization model
  auth_token: "${HUGGINGFACE_TOKEN}"     # Hugging Face token
  min_speakers: 1                        # Minimum expected speakers
  max_speakers: 10                       # Maximum expected speakers
  min_segment_duration: 1.0              # Minimum speech segment (seconds)
  merge_threshold: 0.5                   # Speaker merge threshold
```

### Output Configuration

```yaml
output:
  format: "markdown"                     # Output format
  template: "detailed"                   # Template to use
  include_metadata: true                 # Include file metadata
  include_timestamps: true               # Include timestamps
  timestamp_format: "[{timestamp}]"      # Timestamp format
  speaker_format: "**{speaker}:**"       # Speaker label format
  save_intermediate: false               # Save intermediate files
```

### Archive Settings

```yaml
archive:
  enabled: true                          # Enable archiving
  compress: true                         # Compress archives
  compression_format: "zip"              # zip or tar.gz
  retention_days: 30                     # Keep archives for N days
  include_audio: true                    # Include original audio
  include_intermediate: false            # Include intermediate files
```

### Cache Configuration

```yaml
cache:
  enabled: true                          # Enable caching
  memory_cache_size: 100                 # Number of items in memory
  disk_cache_size_mb: 500               # Disk cache size limit
  ttl_hours: 24                         # Cache time-to-live
  cache_transcripts: true               # Cache transcription results
  cache_diarization: true               # Cache diarization results
```

### Logging Settings

```yaml
logging:
  level: "INFO"                         # Log level (DEBUG, INFO, WARNING, ERROR)
  format: "detailed"                    # Log format (simple, detailed, json)
  file: "obsidian_scribe.log"          # Log file path
  max_size_mb: 10                      # Maximum log file size
  backup_count: 5                      # Number of backup files
  console_colors: true                 # Colorize console output
```

## Environment Variables

Any configuration value can be overridden using environment variables. The format is:

```
OBSIDIAN_SCRIBE_<SECTION>_<KEY>
```

Examples:

```bash
# Set API key
export OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY="sk-..."

# Change audio folder
export OBSIDIAN_SCRIBE_PATHS_AUDIO_FOLDER="/home/user/recordings"

# Set log level
export OBSIDIAN_SCRIBE_LOGGING_LEVEL="DEBUG"

# Set concurrent processing
export OBSIDIAN_SCRIBE_PROCESSING_CONCURRENT_FILES="4"
```

## Command-Line Overrides

Common settings can be overridden via command-line arguments:

```bash
# Override audio folder
python -m src.main --watch /path/to/audio

# Override output folder
python -m src.main --output /path/to/transcripts

# Change log level
python -m src.main --log-level DEBUG

# Use custom config file
python -m src.main --config my-config.yaml
```

## Configuration Validation

Obsidian Scribe validates configuration on startup. Common validation rules:

- Paths must be valid directory paths
- Numeric values must be within acceptable ranges
- Required API keys must be provided
- File extensions must start with a dot
- URLs must be valid HTTP/HTTPS endpoints

## Advanced Configuration

### Custom Whisper Endpoints

Use a self-hosted Whisper API:

```yaml
transcription:
  api_base: "http://localhost:8000/v1"
  api_key: "local-key"
```

### Multiple Watch Folders

Watch multiple folders by using symbolic links or running multiple instances:

```bash
# Create symbolic links
ln -s /path/to/folder1 ./Audio/folder1
ln -s /path/to/folder2 ./Audio/folder2
```

### Performance Tuning

For high-volume processing:

```yaml
processing:
  concurrent_files: 4          # Increase based on CPU cores
  
audio:
  chunk_duration: 600         # Larger chunks for long files
  
cache:
  memory_cache_size: 500      # More memory cache
  disk_cache_size_mb: 2000    # Larger disk cache
```

### Security Considerations

1. **API Keys**: Always use environment variables for sensitive data
2. **File Permissions**: Ensure proper permissions on config files
3. **Network Security**: Use HTTPS endpoints when possible
4. **Token Storage**: Never commit tokens to version control

## Configuration Examples

### Minimal Configuration

```yaml
paths:
  audio_folder: "./Audio"
  transcript_folder: "./Transcripts"

transcription:
  api_key: "${OBSIDIAN_SCRIBE_API_KEY}"
```

### High-Performance Configuration

```yaml
processing:
  concurrent_files: 8
  
audio:
  chunk_duration: 600
  
cache:
  memory_cache_size: 1000
  disk_cache_size_mb: 5000
  
diarization:
  enabled: true
  min_speakers: 2
  max_speakers: 5
```

### Development Configuration

```yaml
logging:
  level: "DEBUG"
  console_colors: true
  
output:
  save_intermediate: true
  
processing:
  concurrent_files: 1
```

## Troubleshooting Configuration

1. **Validation Errors**: Check the error message for specific fields
2. **Missing Values**: Ensure all required fields are present
3. **Type Errors**: Verify correct data types (numbers vs strings)
4. **Path Issues**: Use absolute paths if relative paths cause issues

For more help, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
