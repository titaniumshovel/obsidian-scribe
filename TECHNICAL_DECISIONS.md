# Technical Decisions for Obsidian Scribe

## Overview

This document outlines the key technical decisions made for the Obsidian Scribe project, including library selections, architectural patterns, and implementation strategies.

## Core Technology Stack

### Python 3.8+
**Decision**: Use Python 3.8 as the minimum version
**Rationale**:
- Mature async/await support
- Type hints and typing improvements
- Walrus operator for cleaner code
- Wide library ecosystem for audio processing
- Good balance between modern features and compatibility

### Audio Processing Libraries

#### pyannote.audio (Speaker Diarization)
**Decision**: Use pyannote.audio over whisper-diarization
**Rationale**:
- **Accuracy**: State-of-the-art performance on speaker diarization benchmarks
- **Flexibility**: Supports 5+ speakers as required
- **Customization**: Fine-tunable parameters for different audio scenarios
- **Active Development**: Regular updates and improvements
- **Pre-trained Models**: Ready-to-use models for immediate deployment

**Trade-offs**:
- Requires more setup and model downloads
- Higher memory requirements
- Needs PyTorch dependency

#### OpenAI Whisper API (Transcription)
**Decision**: Use Whisper API with custom endpoint over local whisper model
**Rationale**:
- **No GPU Required**: Cloud-based processing
- **Consistent Performance**: No local resource constraints
- **Maintenance**: No model management needed
- **Custom Endpoint**: Company-provided endpoint reduces costs
- **Scalability**: Can handle multiple concurrent requests

**Configuration**:
```python
API_ENDPOINT = "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/audio/transcriptions"
MODEL = "whisper-1"
```

### File System Monitoring

#### watchdog
**Decision**: Use watchdog for file system monitoring
**Rationale**:
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Native Events**: Uses OS-specific APIs for efficiency
- **Mature**: Well-tested in production environments
- **Pythonic API**: Easy to integrate and extend

**Alternative Considered**: 
- `inotify` (Linux only) - rejected due to platform limitations
- Polling-based solutions - rejected due to inefficiency

### Audio File Handling

#### pydub
**Decision**: Use pydub for audio format conversion
**Rationale**:
- **Format Support**: Handles WAV, MP3, and many other formats
- **Simple API**: Easy to use for basic operations
- **FFmpeg Integration**: Leverages FFmpeg for robust conversion
- **Lightweight**: Minimal overhead for simple operations

### Configuration Management

#### PyYAML
**Decision**: Use YAML for configuration files
**Rationale**:
- **Human Readable**: Easy for users to edit
- **Hierarchical**: Supports complex nested configurations
- **Comments**: Allows inline documentation
- **Obsidian Compatible**: YAML front matter familiarity

### Logging

#### Python logging module with rotating handlers
**Decision**: Use built-in logging with rotation
**Rationale**:
- **Standard**: No additional dependencies
- **Flexible**: Configurable levels and formats
- **Rotation**: Prevents log files from growing too large
- **Integration**: Works well with other Python libraries

## Architectural Patterns

### Event-Driven Architecture
**Decision**: Use event-driven pattern for file processing
**Rationale**:
- **Decoupling**: Components can evolve independently
- **Scalability**: Easy to add new event handlers
- **Reliability**: Failed events can be retried
- **Real-time**: Immediate response to file changes

### Pipeline Pattern
**Decision**: Use pipeline for audio processing workflow
**Rationale**:
- **Modularity**: Each stage is independent
- **Testability**: Stages can be tested in isolation
- **Flexibility**: Easy to add or modify stages
- **Error Handling**: Failures isolated to specific stages

### Repository Pattern
**Decision**: Use repository pattern for file operations
**Rationale**:
- **Abstraction**: Hides file system complexity
- **Testability**: Easy to mock for testing
- **Consistency**: Uniform interface for all file operations
- **Safety**: Centralized validation and error handling

## Data Flow Decisions

### Streaming vs. Loading
**Decision**: Stream large audio files, load small ones
**Threshold**: 100MB
**Rationale**:
- **Memory Efficiency**: Prevents OOM errors on large files
- **Performance**: Faster processing for small files
- **Flexibility**: Adaptive to system resources

### Async vs. Sync Processing
**Decision**: Use synchronous processing with threading for I/O
**Rationale**:
- **Simplicity**: Easier to debug and maintain
- **Library Compatibility**: Many audio libraries are sync-only
- **Threading**: Handles I/O-bound operations efficiently
- **Future-proof**: Can migrate to async if needed

## Error Handling Strategy

### Graceful Degradation
**Decision**: Continue processing other files on individual failures
**Implementation**:
```python
# Pseudo-code
for file in files:
    try:
        process_file(file)
    except ProcessingError as e:
        log_error(e)
        move_to_failed(file)
        continue
```

### Retry Logic
**Decision**: Exponential backoff with maximum 3 retries
**Parameters**:
- Initial delay: 1 second
- Multiplier: 2
- Maximum delay: 60 seconds
- Maximum attempts: 3

**Rationale**:
- **API Limits**: Respects rate limiting
- **Network Issues**: Handles temporary failures
- **Resource Conservation**: Prevents infinite loops

## Storage Decisions

### File Organization
**Decision**: Mirror Obsidian vault structure
**Structure**:
```
Obsidian Vault/
├── Audio/
│   ├── Meeting-2024-01-15.wav
│   └── Archive/
│       └── Meeting-2024-01-15.wav
└── Transcripts/
    └── Meeting-2024-01-15.md
```

**Rationale**:
- **Intuitive**: Users understand the structure
- **Obsidian Integration**: Works with existing workflows
- **Backup Friendly**: Clear separation of source and output

### State Persistence
**Decision**: Use JSON files for processing state
**Rationale**:
- **Simple**: No database dependency
- **Portable**: Easy to backup and transfer
- **Human Readable**: Debugging friendly
- **Atomic Writes**: Prevents corruption

## Performance Optimizations

### Model Caching
**Decision**: Cache diarization models in memory
**Rationale**:
- **Speed**: Avoid repeated model loading
- **Resource Efficiency**: Single model instance
- **Trade-off**: Higher memory usage accepted

### Batch Processing
**Decision**: Process files individually, not in batches
**Rationale**:
- **User Experience**: Immediate results
- **Error Isolation**: One failure doesn't affect others
- **Memory Management**: Predictable resource usage

### Connection Pooling
**Decision**: Reuse HTTP connections for API calls
**Implementation**: requests.Session() with connection pooling
**Rationale**:
- **Performance**: Reduces connection overhead
- **Reliability**: Better handling of network issues

## Security Considerations

### API Key Management
**Decision**: Environment variables only, no file storage
**Implementation**:
```python
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ConfigurationError("API key not found")
```

### Path Validation
**Decision**: Strict path validation and sandboxing
**Implementation**:
- Resolve all paths to absolute
- Check if within allowed directories
- Reject path traversal attempts

### Sensitive Data
**Decision**: No audio content in logs
**Rationale**:
- **Privacy**: Protects user conversations
- **Compliance**: Meets data protection requirements
- **Storage**: Reduces log size

## Deployment Decisions

### Distribution Method
**Decision**: Primary distribution via pip, secondary via Docker
**Rationale**:
- **Pip**: Native Python experience
- **Docker**: Isolated environment with dependencies
- **Choice**: Users can pick their preference

### Dependency Management
**Decision**: Pin major versions, allow minor updates
**Example**:
```
pyannote.audio>=2.1,<3.0
watchdog>=2.0,<3.0
```
**Rationale**:
- **Stability**: Prevents breaking changes
- **Security**: Allows patch updates
- **Compatibility**: Tested version ranges

## Future-Proofing

### Extensibility Points
1. **Transcription Backends**: Interface allows easy addition
2. **Output Formats**: Template system for new formats
3. **Audio Sources**: Can add streaming, URL support
4. **Post-Processing**: Hook system for plugins

### Migration Paths
1. **Async Migration**: Designed to allow gradual async adoption
2. **Database Support**: Repository pattern enables easy switch
3. **Cloud Storage**: File manager abstraction ready for S3, etc.

## Rejected Alternatives

### whisper-diarization
**Rejected Because**:
- Less accurate for 5+ speakers
- Fewer configuration options
- Less active development

### Local Whisper Model
**Rejected Because**:
- Requires significant local resources
- Slower processing without GPU
- Model management overhead
- Company provides API endpoint

### SQLite for State
**Rejected Because**:
- Overkill for simple state tracking
- Additional dependency
- More complex backup/restore

### Celery for Task Queue
**Rejected Because**:
- Requires message broker (Redis/RabbitMQ)
- Complex setup for simple use case
- Overkill for single-user application

## Conclusion

These technical decisions prioritize:
1. **User Experience**: Easy setup and reliable operation
2. **Maintainability**: Clear code structure and patterns
3. **Performance**: Efficient processing without over-engineering
4. **Flexibility**: Room for growth and customization

The chosen stack balances modern capabilities with proven reliability, ensuring Obsidian Scribe can effectively serve its purpose while remaining maintainable and extensible.