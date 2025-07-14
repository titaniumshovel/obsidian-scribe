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
├── obsidian_scribe/              # Legacy module (to be migrated)
│   ├── __init__.py
│   ├── file_watcher.py
│   ├── processor.py
│   └── utils.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_config.py           # Configuration tests
│   ├── test_utils.py            # Utility tests
│   └── TEST_PLAN.md             # Test planning documentation
│
├── docs/                         # Documentation
│   ├── README.md                # Documentation overview
│   ├── API_REFERENCE.md         # API documentation
│   ├── CONFIGURATION.md         # Configuration reference
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── INSTALLATION.md          # Installation guide
│   ├── TROUBLESHOOTING.md       # Common issues and solutions  
│   ├── USAGE.md                 # Usage instructions
│   ├── IMPLEMENTATION_PLAN.md   # Development roadmap
│   ├── PROGRESS_TRACKING.md     # Progress tracking docs
│   ├── RESTRUCTURING_PROGRESS.md# Project restructuring log
│   ├── WEBM_DETECTION_FIX.md    # Technical debugging notes
│   ├── technical/               # Technical documentation
│   │   ├── ARCHITECTURE.md      # System architecture
│   │   ├── TECHNICAL_DECISIONS.md# Technology choices
│   │   ├── CONFIG_SCHEMA.md     # Configuration schema
│   │   ├── AUDIO_CHUNKING.md    # Audio processing strategy
│   │   ├── VOICEMEETER_SETUP.md # Audio routing setup
│   │   └── WHISPER_INTEGRATION.md# Integration guide
│   └── project/                 # Project management docs
│       ├── PROJECT_ROADMAP.md   # Strategic roadmap
│       └── PROJECT_STRUCTURE.md # This file
│
├── config.example.yaml          # Example configuration
├── requirements.txt             # Production dependencies
├── setup.py                     # Package setup script
├── setup.cfg                    # Setup configuration
├── pyproject.toml              # Modern Python project config
├── README.md                   # Project overview
├── LICENSE                     # License file
├── CHANGELOG.md               # Version history
├── .gitignore                 # Git ignore rules
├── .env.example               # Environment variables example
├── Makefile                   # Common tasks automation
├── obsidian_scribe.py         # Legacy entry point
├── test_pipeline.py           # Pipeline testing script
│
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

### `config.example.yaml`
Example configuration showing all available settings with sensible defaults.

### `.env.example`
Example environment variables:
```bash
OPENAI_API_KEY=your-api-key-here
OBSIDIAN_AUDIO_PATH=/path/to/obsidian/Audio
OBSIDIAN_TRANSCRIPT_PATH=/path/to/obsidian/Transcripts
LOG_LEVEL=INFO
```

## Testing Structure

### Current Tests
- **test_config.py**: Configuration management tests
- **test_utils.py**: Utility function tests
- **TEST_PLAN.md**: Comprehensive test planning documentation

### Planned Test Structure
- Unit tests for individual components
- Integration tests for complete workflows
- Test fixtures with sample audio files and mock API responses

## Documentation

### User Documentation (in `docs/`)
- **INSTALLATION.md**: Step-by-step installation guide
- **CONFIGURATION.md**: Detailed configuration reference
- **USAGE.md**: Common usage scenarios and examples
- **TROUBLESHOOTING.md**: FAQ and problem solutions

### Developer Documentation
- **API_REFERENCE.md**: Internal API documentation
- **ARCHITECTURE_OVERVIEW.md**: System architecture guide
- **CONTRIBUTING.md**: Contribution guidelines
- Inline code documentation with docstrings
- Type hints throughout the codebase

### Project Documentation (root directory)
- **ARCHITECTURE.md**: Detailed architecture decisions
- **TECHNICAL_DECISIONS.md**: Log of technical choices
- **CONFIG_SCHEMA.md**: Configuration schema details
- **AUDIO_CHUNKING.md**: Audio processing documentation
- **WHISPER_INTEGRATION.md**: Whisper API integration guide
- **VOICEMEETER_SETUP.md**: VoiceMeeter configuration guide
- **RESTRUCTURING_PROGRESS.md**: Project restructuring tracker

## Build and Deployment

### Package Distribution
- **setup.py**: Package setup script for pip installation
- **pyproject.toml**: Modern Python packaging configuration
- **setup.cfg**: Additional setup configuration
- **requirements.txt**: Production dependencies

## Development Workflow

### Makefile Commands
The project includes a Makefile for common development tasks. Planned commands include:
- `install`: Install dependencies
- `test`: Run all tests
- `lint`: Run linting checks
- `format`: Format code with black
- `type-check`: Run mypy type checking
- `clean`: Clean build artifacts

### Development Best Practices
- Use type hints throughout the codebase
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Include unit tests for new functionality
- Update documentation when adding features

## Current Status

The project is currently undergoing restructuring from a monolithic script to a modular architecture. Key components are being migrated from the `obsidian_scribe/` directory to the new `src/` structure. See `RESTRUCTURING_PROGRESS.md` for detailed progress tracking.

### Legacy Components
- **obsidian_scribe.py**: Original entry point (to be replaced by src/main.py)
- **obsidian_scribe/**: Legacy module directory (being migrated to src/)
- **test_pipeline.py**: Pipeline testing script

This structure provides a clean, maintainable foundation for the Obsidian Scribe project with clear separation of concerns and room for future growth.