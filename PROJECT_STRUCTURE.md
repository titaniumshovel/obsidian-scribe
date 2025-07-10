# Obsidian Scribe Project Structure

## Directory Layout

```
obsidian-scribe/
├── src/                           # Source code directory
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Application entry point and CLI
│   │
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── manager.py            # Config loading and validation
│   │   ├── schema.py             # Configuration schema definitions
│   │   └── defaults.py           # Default configuration values
│   │
│   ├── watcher/                  # File system monitoring
│   │   ├── __init__.py
│   │   ├── file_watcher.py       # Main file watching logic
│   │   ├── event_handler.py      # File event processing
│   │   └── queue_manager.py      # Processing queue management
│   │
│   ├── audio/                    # Audio processing components
│   │   ├── __init__.py
│   │   ├── processor.py          # Audio processing orchestration
│   │   ├── diarizer.py           # Pyannote speaker diarization
│   │   ├── transcriber.py        # Whisper API integration
│   │   ├── converter.py          # Audio format conversion
│   │   └── chunker.py            # Audio file splitting for API limits
│   │
│   ├── transcript/               # Transcript generation
│   │   ├── __init__.py
│   │   ├── generator.py          # Transcript assembly logic
│   │   ├── markdown_writer.py    # Markdown formatting
│   │   ├── formatter.py          # Text formatting utilities
│   │   └── templates.py          # Markdown templates
│   │
│   ├── storage/                  # File and data management
│   │   ├── __init__.py
│   │   ├── file_manager.py       # File operations
│   │   ├── archive.py            # Archive management
│   │   ├── state_manager.py      # Processing state persistence
│   │   └── cache.py              # Caching functionality
│   │
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       ├── exceptions.py         # Custom exception classes
│       ├── validators.py         # Input validation
│       └── helpers.py            # General helper functions
│
├── config/                       # Configuration files
│   ├── config.yaml              # Default configuration
│   └── config.example.yaml      # Example configuration
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── fixtures/               # Test fixtures
│   │   ├── audio_files/        # Sample audio files
│   │   └── config_files/       # Test configurations
│   ├── unit/                   # Unit tests
│   │   ├── test_config.py
│   │   ├── test_watcher.py
│   │   ├── test_audio.py
│   │   ├── test_transcript.py
│   │   └── test_storage.py
│   └── integration/            # Integration tests
│       ├── test_pipeline.py
│       └── test_api.py
│
├── docs/                       # Documentation
│   ├── setup.md               # Installation guide
│   ├── configuration.md       # Configuration reference
│   ├── usage.md               # Usage instructions
│   ├── api.md                 # API documentation
│   └── troubleshooting.md     # Common issues and solutions
│
├── scripts/                    # Utility scripts
│   ├── setup_models.py        # Download required models
│   ├── validate_config.py     # Configuration validator
│   └── test_api.py           # API connectivity test
│
├── docker/                    # Docker configuration
│   ├── Dockerfile            # Container definition
│   └── docker-compose.yml    # Compose configuration
│
├── .github/                   # GitHub configuration
│   └── workflows/
│       ├── tests.yml         # CI test workflow
│       └── release.yml       # Release workflow
│
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── setup.py                  # Package setup script
├── setup.cfg                 # Setup configuration
├── pyproject.toml           # Modern Python project config
├── README.md                # Project overview
├── LICENSE                  # License file
├── CHANGELOG.md            # Version history
├── .gitignore              # Git ignore rules
├── .env.example            # Environment variables example
└── Makefile                # Common tasks automation
```

## Module Descriptions

### Core Modules

#### `src/main.py`
Entry point for the application. Handles:
- Command-line argument parsing
- Application initialization
- Main event loop
- Graceful shutdown

#### `src/config/`
Configuration management system:
- **manager.py**: Loads config from YAML, environment variables
- **schema.py**: Defines and validates configuration structure
- **defaults.py**: Provides sensible default values

#### `src/watcher/`
File system monitoring:
- **file_watcher.py**: Implements watchdog observers
- **event_handler.py**: Processes file system events
- **queue_manager.py**: Manages processing queue with priorities

#### `src/audio/`
Audio processing pipeline:
- **processor.py**: Orchestrates the processing workflow
- **diarizer.py**: Implements pyannote.audio integration
- **transcriber.py**: Handles Whisper API communication
- **converter.py**: Converts between audio formats

#### `src/transcript/`
Transcript generation and formatting:
- **generator.py**: Combines diarization and transcription
- **markdown_writer.py**: Creates Obsidian-compatible Markdown
- **formatter.py**: Handles text formatting and timestamps
- **templates.py**: Markdown template definitions

#### `src/storage/`
File and state management:
- **file_manager.py**: Safe file operations with atomic writes
- **archive.py**: Manages processed file archiving
- **state_manager.py**: Persists processing state for recovery
- **cache.py**: Caches model outputs and API responses

#### `src/utils/`
Shared utilities:
- **logger.py**: Centralized logging configuration
- **exceptions.py**: Custom exception hierarchy
- **validators.py**: Input validation functions
- **helpers.py**: Common helper functions

## File Naming Conventions

- **Python files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Test files**: `test_<module_name>.py`

## Key Design Patterns

### 1. Factory Pattern
Used for creating processors based on configuration:
```python
# audio/processor.py
class AudioProcessorFactory:
    @staticmethod
    def create_processor(config: Config) -> AudioProcessor:
        # Returns appropriate processor instance
```

### 2. Observer Pattern
For file system monitoring:
```python
# watcher/file_watcher.py
class FileWatcher(FileSystemEventHandler):
    def on_created(self, event):
        # Handle new file events
```

### 3. Strategy Pattern
For different transcription backends:
```python
# audio/transcriber.py
class TranscriberStrategy(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> Transcript:
        pass
```

### 4. Singleton Pattern
For configuration and logging:
```python
# config/manager.py
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Configuration Files

### `config/config.yaml`
Default configuration with all available options and sensible defaults.

### `config/config.example.yaml`
Minimal example configuration showing only required settings.

### `.env.example`
Example environment variables:
```bash
OPENAI_API_KEY=your-api-key-here
OBSIDIAN_AUDIO_PATH=/path/to/obsidian/Audio
OBSIDIAN_TRANSCRIPT_PATH=/path/to/obsidian/Transcripts
LOG_LEVEL=INFO
```

## Testing Structure

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on edge cases and error conditions

### Integration Tests
- Test complete workflows
- Use real audio files (small samples)
- Verify end-to-end functionality

### Test Fixtures
- Sample audio files in various formats
- Mock API responses
- Test configuration files

## Documentation

### User Documentation
- **setup.md**: Step-by-step installation guide
- **configuration.md**: Detailed configuration reference
- **usage.md**: Common usage scenarios and examples
- **troubleshooting.md**: FAQ and problem solutions

### Developer Documentation
- **api.md**: Internal API documentation
- Inline code documentation with docstrings
- Type hints throughout the codebase

## Build and Deployment

### Docker Support
- Multi-stage Dockerfile for minimal image size
- docker-compose.yml for easy local development
- Support for both CPU and GPU variants

### Package Distribution
- setup.py for pip installation
- pyproject.toml for modern Python packaging
- Automated release workflow via GitHub Actions

## Development Workflow

### Makefile Commands
```makefile
install:        # Install dependencies
test:           # Run all tests
test-unit:      # Run unit tests only
lint:           # Run linting checks
format:         # Format code with black
type-check:     # Run mypy type checking
docs:           # Generate documentation
clean:          # Clean build artifacts
docker-build:   # Build Docker image
docker-run:     # Run Docker container
```

### Pre-commit Hooks
- Code formatting with black
- Linting with flake8
- Type checking with mypy
- Import sorting with isort

This structure provides a clean, maintainable foundation for the Obsidian Scribe project with clear separation of concerns and room for future growth.