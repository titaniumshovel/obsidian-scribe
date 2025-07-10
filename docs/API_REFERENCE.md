# API Reference

This document provides a comprehensive reference for the Obsidian Scribe Python API.

## Core Classes

### ObsidianScribe

The main application class that orchestrates all components.

```python
from src.main import ObsidianScribe

class ObsidianScribe:
    """Main application class for Obsidian Scribe."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Obsidian Scribe application.
        
        Args:
            config_path: Path to configuration file (optional)
        """
    
    def setup(self) -> None:
        """Set up the application components."""
    
    def start(self) -> None:
        """Start the application."""
    
    def stop(self) -> None:
        """Stop the application gracefully."""
    
    def run(self) -> None:
        """Run the application (setup + start)."""
```

**Example Usage:**

```python
# Basic usage
app = ObsidianScribe()
app.run()

# With custom config
app = ObsidianScribe(config_path=Path("custom-config.yaml"))
app.run()

# Manual control
app = ObsidianScribe()
app.setup()
app.start()
# ... do something ...
app.stop()
```

## Configuration Management

### ConfigManager

Manages application configuration with support for YAML files and environment variables.

```python
from src.config.manager import ConfigManager

class ConfigManager:
    """Singleton configuration manager."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional config file path."""
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key."""
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key."""
    
    def reload(self) -> None:
        """Reload configuration from file."""
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save current configuration to file."""
    
    def validate(self) -> bool:
        """Validate current configuration."""
```

**Example Usage:**

```python
# Get configuration manager
config = ConfigManager()

# Access values
api_key = config.get("transcription.api_key")
chunk_size = config.get("audio.chunk_duration", default=300)

# Set values
config.set("processing.concurrent_files", 4)

# Save changes
config.save()
```

## File Watching

### FileWatcher

Monitors directories for new audio files.

```python
from src.watcher.file_watcher import FileWatcher

class FileWatcher:
    """Watches for new audio files in specified directory."""
    
    def __init__(self, watch_folder: str, processor: AudioProcessor, 
                 config: Dict[str, Any]):
        """Initialize file watcher."""
    
    def start(self) -> None:
        """Start watching for files."""
    
    def stop(self) -> None:
        """Stop watching for files."""
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
```

### QueueManager

Manages processing queue with priority support.

```python
from src.watcher.queue_manager import QueueManager

class QueueManager:
    """Manages file processing queue with priorities."""
    
    def add_file(self, file_path: Path, priority: int = 5) -> str:
        """Add file to processing queue."""
    
    def get_next(self) -> Optional[QueueItem]:
        """Get next file to process."""
    
    def mark_completed(self, item_id: str) -> None:
        """Mark item as completed."""
    
    def mark_failed(self, item_id: str, error: str) -> None:
        """Mark item as failed."""
    
    def get_status(self) -> Dict[str, int]:
        """Get queue statistics."""
```

## Audio Processing

### AudioProcessor

Main audio processing orchestrator.

```python
from src.audio.processor import AudioProcessor

class AudioProcessor:
    """Orchestrates audio file processing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize processor with configuration."""
    
    def process(self, file_path: Path) -> ProcessingResult:
        """Process a single audio file."""
    
    def process_async(self, file_path: Path) -> asyncio.Future:
        """Process file asynchronously."""
    
    def start(self) -> None:
        """Start processing worker threads."""
    
    def stop(self) -> None:
        """Stop processing gracefully."""
```

### Transcriber

Handles transcription using Whisper API.

```python
from src.audio.transcriber import Transcriber

class Transcriber:
    """Handles audio transcription using Whisper API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with API configuration."""
    
    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """Transcribe an audio file."""
    
    def transcribe_chunk(self, chunk_path: Path, 
                        prompt: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe a single audio chunk."""
```

### Diarizer

Performs speaker diarization.

```python
from src.audio.diarizer import Diarizer

class Diarizer:
    """Performs speaker diarization on audio files."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with diarization configuration."""
    
    def diarize(self, audio_path: Path) -> List[DiarizationSegment]:
        """Perform speaker diarization."""
    
    def merge_segments(self, segments: List[DiarizationSegment], 
                      threshold: float = 0.5) -> List[DiarizationSegment]:
        """Merge similar speaker segments."""
```

### AudioChunker

Splits audio files into processable chunks.

```python
from src.audio.chunker import AudioChunker

class AudioChunker:
    """Splits audio files into chunks for processing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with chunking configuration."""
    
    def chunk_audio(self, audio_path: Path) -> List[AudioChunk]:
        """Split audio file into chunks."""
    
    def detect_silence(self, audio_path: Path) -> List[Tuple[float, float]]:
        """Detect silence periods in audio."""
```

## Transcript Generation

### TranscriptGenerator

Combines transcription and diarization results.

```python
from src.transcript.generator import TranscriptGenerator

class TranscriptGenerator:
    """Generates final transcripts from processing results."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with output configuration."""
    
    def generate(self, transcription: TranscriptionResult,
                diarization: Optional[DiarizationResult] = None) -> Transcript:
        """Generate complete transcript."""
    
    def merge_chunks(self, chunks: List[TranscriptChunk]) -> Transcript:
        """Merge transcript chunks into single document."""
```

### MarkdownWriter

Writes transcripts in Markdown format.

```python
from src.transcript.markdown_writer import MarkdownWriter

class MarkdownWriter:
    """Writes transcripts to Markdown files."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with formatting configuration."""
    
    def write(self, transcript: Transcript, output_path: Path) -> None:
        """Write transcript to Markdown file."""
    
    def format_segment(self, segment: TranscriptSegment) -> str:
        """Format a single transcript segment."""
```

## Storage Management

### FileManager

Handles safe file operations.

```python
from src.storage.file_manager import FileManager

class FileManager:
    """Manages file operations with safety and atomicity."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with storage configuration."""
    
    @contextmanager
    def atomic_write(self, file_path: Path, mode: str = 'w'):
        """Context manager for atomic file writes."""
    
    def validate_audio_file(self, file_path: Path) -> bool:
        """Validate audio file format and integrity."""
    
    def wait_for_file_ready(self, file_path: Path, 
                           timeout: float = 30.0) -> bool:
        """Wait for file to be fully written."""
```

### ArchiveManager

Manages file archiving and retention.

```python
from src.storage.archive import ArchiveManager

class ArchiveManager:
    """Manages archiving of processed files."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with archive configuration."""
    
    def archive_file(self, file_path: Path, 
                    metadata: Optional[Dict] = None) -> Path:
        """Archive a single file."""
    
    def archive_session(self, session_id: str, 
                       files: List[Path]) -> Path:
        """Archive complete processing session."""
    
    def cleanup_old_archives(self, retention_days: int) -> int:
        """Remove archives older than retention period."""
```

### StateManager

Manages processing state and history.

```python
from src.storage.state_manager import StateManager

class StateManager:
    """Manages processing state and history."""
    
    def __init__(self, db_path: Path):
        """Initialize with database path."""
    
    def add_to_history(self, file_path: Path, 
                      result: ProcessingResult) -> None:
        """Add processing result to history."""
    
    def get_file_status(self, file_path: Path) -> Optional[str]:
        """Get processing status for file."""
    
    def recover_interrupted(self) -> List[Path]:
        """Get list of interrupted files for recovery."""
```

### CacheManager

Provides caching functionality.

```python
from src.storage.cache import CacheManager

class CacheManager:
    """Manages multi-level caching."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with cache configuration."""
    
    def cache_transcript(self, file_hash: str, 
                        transcript: Transcript) -> None:
        """Cache transcription result."""
    
    def get_cached_transcript(self, file_hash: str) -> Optional[Transcript]:
        """Retrieve cached transcript."""
    
    @lru_cache(maxsize=100)
    def memory_cache(self, key: str) -> Any:
        """In-memory LRU cache decorator."""
```

## Utility Functions

### Logging

```python
from src.utils.logger import setup_logging, get_logger

# Setup logging
logger = setup_logging(
    level=logging.INFO,
    log_file=Path("app.log"),
    format="detailed"
)

# Get module logger
module_logger = get_logger(__name__)
module_logger.info("Processing started")
```

### Validators

```python
from src.utils.validators import (
    validate_audio_file,
    validate_config_value,
    validate_url,
    validate_path
)

# Validate audio file
if validate_audio_file("recording.wav"):
    process_file("recording.wav")

# Validate configuration
if not validate_config_value(api_key, str, min_length=20):
    raise ConfigurationError("Invalid API key")
```

### Helpers

```python
from src.utils.helpers import (
    format_duration,
    sanitize_filename,
    retry_with_backoff,
    parse_time_string
)

# Format duration
duration_str = format_duration(3661)  # "1h 1m 1s"

# Sanitize filename
safe_name = sanitize_filename("my:file*.txt")  # "my_file_.txt"

# Retry decorator
@retry_with_backoff(max_retries=3)
def api_call():
    return requests.get("https://api.example.com")
```

## Custom Exceptions

```python
from src.utils.exceptions import (
    ObsidianScribeError,
    ConfigurationError,
    AudioProcessingError,
    TranscriptionError,
    DiarizationError
)

try:
    result = process_audio(file_path)
except AudioProcessingError as e:
    logger.error(f"Processing failed: {e}")
    logger.debug(f"Error details: {e.details}")
except ObsidianScribeError as e:
    # Handle any Obsidian Scribe error
    handle_error(e)
```

## Data Models

### ProcessingResult

```python
@dataclass
class ProcessingResult:
    """Result of audio file processing."""
    file_path: Path
    status: str  # "completed", "failed", "partial"
    transcript: Optional[Transcript]
    error: Optional[str]
    duration: float
    metadata: Dict[str, Any]
```

### Transcript

```python
@dataclass
class Transcript:
    """Complete transcript with metadata."""
    content: str
    segments: List[TranscriptSegment]
    metadata: TranscriptMetadata
    speakers: List[Speaker]
```

### TranscriptSegment

```python
@dataclass
class TranscriptSegment:
    """Single segment of transcript."""
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str]
    confidence: float
```

## Advanced Usage

### Custom Processing Pipeline

```python
# Create custom processor
class CustomProcessor(AudioProcessor):
    def pre_process(self, file_path: Path) -> Path:
        """Custom pre-processing logic."""
        # Apply noise reduction, normalization, etc.
        return processed_path
    
    def post_process(self, transcript: Transcript) -> Transcript:
        """Custom post-processing logic."""
        # Apply custom formatting, filtering, etc.
        return modified_transcript

# Use custom processor
processor = CustomProcessor(config)
result = processor.process("audio.wav")
```

### Programmatic Control

```python
# Direct API usage without file watching
from src.audio.transcriber import Transcriber
from src.audio.diarizer import Diarizer
from src.transcript.generator import TranscriptGenerator

# Initialize components
transcriber = Transcriber(config)
diarizer = Diarizer(config)
generator = TranscriptGenerator(config)

# Process manually
transcription = transcriber.transcribe("audio.wav")
diarization = diarizer.diarize("audio.wav")
transcript = generator.generate(transcription, diarization)

# Save result
with open("transcript.md", "w") as f:
    f.write(transcript.content)
```

### Event Handling

```python
# Subscribe to processing events
from src.events import EventBus, ProcessingEvent

def on_file_completed(event: ProcessingEvent):
    print(f"Completed: {event.file_path}")
    # Send notification, update database, etc.

EventBus.subscribe("file.completed", on_file_completed)
```

## Performance Considerations

- Use `process_async()` for non-blocking processing
- Enable caching for repeated transcriptions
- Adjust chunk size based on available memory
- Use GPU acceleration when available
- Monitor queue size and adjust concurrent processing

## Thread Safety

Most classes are thread-safe for read operations. For write operations:

- `ConfigManager` uses locks for thread safety
- `QueueManager` is thread-safe by design
- `StateManager` uses database transactions
- `CacheManager` uses thread-safe data structures

## Error Handling

All methods may raise:

- `ConfigurationError`: Invalid configuration
- `AudioProcessingError`: Processing failures
- `TranscriptionError`: API errors
- `IOError`: File system errors

Always wrap API calls in appropriate error handling.
