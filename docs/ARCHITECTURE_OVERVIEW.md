# Architecture Overview

This document provides a high-level overview of Obsidian Scribe's architecture, design decisions, and component interactions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Obsidian Scribe                          │
├─────────────────────────────────────────────────────────────────┤
│                      Configuration Layer                         │
│                    (YAML + Environment Vars)                    │
├─────────────────────────────────────────────────────────────────┤
│   File Watcher    │    Audio Processor    │  Transcript Gen     │
│   ┌──────────┐   │   ┌──────────────┐   │  ┌──────────────┐  │
│   │ Observer │   │   │  Chunker     │   │  │  Generator   │  │
│   │ Handler  │   │   │  Converter   │   │  │  Formatter   │  │
│   │ Queue    │   │   │  Transcriber │   │  │  Writer      │  │
│   └──────────┘   │   │  Diarizer    │   │  └──────────────┘  │
│                   │   └──────────────┘   │                     │
├─────────────────────────────────────────────────────────────────┤
│                       Storage Layer                             │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│   │  Files   │   │ Archive  │   │  State   │   │  Cache   │  │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Utility Layer                            │
│     Logger    │    Validators    │    Helpers    │ Exceptions  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration Management

**Purpose**: Centralized configuration with validation and environment override support.

**Key Classes**:

- `ConfigManager`: Singleton pattern for global configuration access
- `ConfigSchema`: Validation rules and constraints
- `ConfigDefaults`: Default values for all settings

**Design Decisions**:

- YAML format for human readability
- Environment variables for sensitive data
- Dot notation for nested access
- Runtime validation for safety

### 2. File Watching System

**Purpose**: Monitor directories for new audio files and queue them for processing.

**Key Classes**:

- `FileWatcher`: Uses Observer pattern with watchdog library
- `EventHandler`: Filters and validates file events
- `QueueManager`: Priority-based processing queue

**Design Decisions**:

- Event-driven architecture for efficiency
- Configurable file filters and patterns
- Priority queue for processing order
- File readiness checks to avoid partial files

### 3. Audio Processing Pipeline

**Purpose**: Convert, chunk, transcribe, and diarize audio files.

**Key Classes**:

- `AudioProcessor`: Orchestrates the processing pipeline
- `AudioChunker`: Splits long audio into manageable chunks
- `AudioConverter`: Normalizes audio format using FFmpeg
- `Transcriber`: Interfaces with Whisper API
- `Diarizer`: Identifies speakers using pyannote

**Design Decisions**:

- Modular pipeline for flexibility
- Chunking for long audio files
- Overlap to maintain context
- Parallel processing support
- Retry logic for resilience

### 4. Transcript Generation

**Purpose**: Combine processing results into formatted output.

**Key Classes**:

- `TranscriptGenerator`: Assembles final transcript
- `MarkdownWriter`: Formats output for Obsidian
- `Formatter`: Text formatting utilities
- `Templates`: Customizable output templates

**Design Decisions**:

- Markdown format for Obsidian compatibility
- Multiple template options
- Metadata in YAML frontmatter
- Speaker-aware formatting

### 5. Storage Management

**Purpose**: Handle file operations, archiving, state persistence, and caching.

**Key Classes**:

- `FileManager`: Safe file operations with atomic writes
- `ArchiveManager`: Compression and retention policies
- `StateManager`: SQLite-based state tracking
- `CacheManager`: Multi-level caching system

**Design Decisions**:

- Atomic writes for data integrity
- Automatic archiving with retention
- State persistence for recovery
- LRU caching for performance

### 6. Utility Layer

**Purpose**: Common functionality used across components.

**Key Classes**:

- `Logger`: Centralized logging with color support
- `Validators`: Input validation functions
- `Helpers`: Common utility functions
- `Exceptions`: Custom exception hierarchy

**Design Decisions**:

- Structured logging for debugging
- Comprehensive validation
- Reusable utility functions
- Detailed error information

## Data Flow

### Processing Pipeline

```
1. Audio File Detected
   └─> File Watcher
       └─> Event Handler (validation)
           └─> Queue Manager (prioritization)

2. File Processing
   └─> Audio Processor
       ├─> Converter (format normalization)
       ├─> Chunker (split if needed)
       ├─> Transcriber (speech to text)
       └─> Diarizer (speaker identification)

3. Transcript Generation
   └─> Generator (combine results)
       └─> Formatter (apply template)
           └─> Writer (save to disk)

4. Post-Processing
   ├─> Archive Manager (compress and store)
   ├─> State Manager (update history)
   └─> Cache Manager (store results)
```

### Error Handling Flow

```
Try Operation
 └─> Success: Continue
 └─> Failure: Catch Exception
     ├─> Log Error Details
     ├─> Update State (failed)
     ├─> Retry if Configured
     └─> Archive with Error Metadata
```

## Design Patterns

### 1. Singleton Pattern

- **Used in**: ConfigManager
- **Purpose**: Ensure single configuration instance
- **Benefits**: Global access, consistency

### 2. Observer Pattern

- **Used in**: FileWatcher
- **Purpose**: React to file system events
- **Benefits**: Decoupling, efficiency

### 3. Factory Pattern

- **Used in**: Template selection
- **Purpose**: Create objects based on configuration
- **Benefits**: Flexibility, extensibility

### 4. Strategy Pattern

- **Used in**: Audio processing pipeline
- **Purpose**: Swap algorithms at runtime
- **Benefits**: Modularity, testability

### 5. Context Manager Pattern

- **Used in**: Atomic file writes
- **Purpose**: Resource management
- **Benefits**: Safety, cleanup guarantee

## Concurrency Model

### Thread Usage

1. **Main Thread**: Application lifecycle, coordination
2. **Watcher Thread**: File system monitoring
3. **Worker Threads**: Audio processing (configurable pool)
4. **Background Threads**: Archiving, cleanup

### Synchronization

- **Queue**: Thread-safe priority queue
- **State**: Database transactions
- **Cache**: Thread-safe data structures
- **Config**: Read-write locks

### Async Considerations

- Future support for async/await
- Non-blocking I/O for API calls
- Event-driven architecture ready

## Performance Optimizations

### 1. Caching Strategy

```
Request → Memory Cache → Disk Cache → Process → Store in Cache
```

- LRU eviction policy
- TTL-based expiration
- Separate caches for transcripts and diarization

### 2. Chunking Strategy

- Configurable chunk size (default: 5 minutes)
- Overlap for context (default: 2 seconds)
- Silence-based splitting when possible

### 3. Resource Management

- Connection pooling for API calls
- Temporary file cleanup
- Memory-mapped files for large audio
- Lazy loading of heavy dependencies

## Security Considerations

### 1. API Key Management

- Environment variables for secrets
- Never logged or stored in plain text
- Validation before use

### 2. File System Security

- Path traversal prevention
- Permission checks
- Sanitized filenames

### 3. Input Validation

- File type verification
- Size limits enforcement
- Content validation

### 4. Data Privacy

- Configurable retention policies
- Secure deletion options
- No telemetry by default

## Extensibility Points

### 1. Custom Processors

```python
class CustomProcessor(AudioProcessor):
    def process_audio(self, path: Path) -> Result:
        # Custom implementation
        pass
```

### 2. Output Formats

```python
class CustomWriter(BaseWriter):
    def write(self, transcript: Transcript) -> None:
        # Custom format
        pass
```

### 3. Storage Backends

```python
class S3Storage(StorageBackend):
    def store(self, path: Path, data: bytes) -> None:
        # S3 implementation
        pass
```

### 4. API Providers

```python
class AzureTranscriber(BaseTranscriber):
    def transcribe(self, audio: Path) -> Transcript:
        # Azure Speech Services
        pass
```

## Deployment Considerations

### 1. Docker Support

- Dockerfile for containerization
- Volume mounts for data persistence
- Environment-based configuration

### 2. Scaling Options

- Horizontal scaling with shared storage
- Queue-based work distribution
- Stateless worker nodes

### 3. Monitoring

- Health check endpoints
- Metrics collection hooks
- Structured logging for analysis

## Future Architecture Plans

### 1. Microservices Option

- Separate services for watching, processing, storage
- Message queue for communication
- Independent scaling

### 2. Cloud Native

- Kubernetes deployment
- Cloud storage integration
- Managed queue services

### 3. Real-time Processing

- Streaming audio support
- WebSocket notifications
- Live transcription

## Technology Stack

### Core Dependencies

- **Python 3.8+**: Modern Python features
- **watchdog**: File system monitoring
- **FFmpeg**: Audio processing
- **OpenAI Whisper**: Transcription
- **pyannote**: Speaker diarization

### Storage

- **SQLite**: State management
- **File System**: Primary storage
- **ZIP/TAR**: Archive formats

### Development

- **pytest**: Testing framework
- **mypy**: Type checking
- **black**: Code formatting
- **pre-commit**: Git hooks

## Best Practices

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Components receive dependencies
3. **Interface Segregation**: Small, focused interfaces
4. **Error Propagation**: Exceptions bubble up with context
5. **Logging**: Structured logs at appropriate levels
6. **Testing**: Unit tests for components, integration tests for workflows
7. **Documentation**: Code is self-documenting with clear docstrings

This architecture provides a solid foundation for audio transcription while remaining flexible for future enhancements and different deployment scenarios.
