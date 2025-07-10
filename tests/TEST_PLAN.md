# Obsidian Scribe Test Plan

## Completed Tests

### Configuration Tests (`test_config.py`)

- ✅ ConfigManager singleton pattern
- ✅ Configuration loading from file and defaults
- ✅ Environment variable overrides
- ✅ Configuration validation
- ✅ Nested configuration access and modification

### Utility Tests (`test_utils.py`)

- ✅ Logger setup and formatting
- ✅ Exception handling and custom exceptions
- ✅ Input validators (audio files, URLs, paths, etc.)
- ✅ Helper functions (formatting, sanitization, retry logic)

### Test Infrastructure (`conftest.py`)

- ✅ Pytest fixtures for common test scenarios
- ✅ Mock objects for external dependencies
- ✅ Temporary directory management
- ✅ Sample file generation

## Tests to Add Later

### Storage Module Tests

1. **FileManager Tests** (`test_file_manager.py`)
   - Atomic write operations
   - Safe file moves and copies with collision handling
   - File validation and metadata extraction
   - Temporary file management
   - Wait for file ready functionality

2. **Archive Tests** (`test_archive.py`)
   - Archive creation with different compression formats
   - Retention policy enforcement
   - Archive search functionality
   - Session archiving with all artifacts

3. **StateManager Tests** (`test_state_manager.py`)
   - SQLite database operations
   - Processing state tracking
   - Recovery from interrupted processing
   - Statistics calculation
   - State export/import

4. **Cache Tests** (`test_cache.py`)
   - LRU memory cache behavior
   - Disk cache with TTL
   - Cache decorators
   - Cache invalidation

### Watcher Module Tests

1. **FileWatcher Tests** (`test_file_watcher.py`)
   - File system event detection
   - Pattern matching for audio files
   - Observer start/stop lifecycle

2. **EventHandler Tests** (`test_event_handler.py`)
   - Audio file event processing
   - File readiness checks
   - Event filtering

3. **QueueManager Tests** (`test_queue_manager.py`)
   - Priority queue operations
   - Retry logic with backoff
   - Queue persistence
   - Concurrent processing limits

### Audio Processing Tests

1. **AudioProcessor Tests** (`test_audio_processor.py`)
   - End-to-end processing pipeline
   - Chunking integration
   - Error handling and recovery

2. **Transcriber Tests** (`test_transcriber.py`)
   - Whisper API mocking
   - Chunk transcription
   - Response parsing
   - Error handling

3. **Diarizer Tests** (`test_diarizer.py`)
   - Pyannote integration mocking
   - Speaker detection
   - Segment merging

4. **Converter Tests** (`test_converter.py`)
   - FFmpeg command generation
   - Format conversion validation
   - Temporary file cleanup

5. **Chunker Tests** (`test_chunker.py`)
   - Audio chunking with overlap
   - Silence detection
   - Chunk size validation

### Transcript Generation Tests

1. **Generator Tests** (`test_generator.py`)
   - Transcript assembly from chunks
   - Diarization integration
   - Metadata generation

2. **MarkdownWriter Tests** (`test_markdown_writer.py`)
   - Markdown formatting
   - Template application
   - File writing

3. **Formatter Tests** (`test_formatter.py`)
   - Text formatting utilities
   - Speaker labeling
   - Timestamp formatting

### Integration Tests

1. **End-to-End Tests** (`test_integration.py`)
   - Complete processing pipeline
   - File watching to transcript generation
   - Error recovery scenarios
   - Performance benchmarks

2. **API Integration Tests** (`test_api_integration.py`)
   - Real Whisper API calls (with test account)
   - Network error handling
   - Rate limiting

### Performance Tests

1. **Load Tests** (`test_performance.py`)
   - Multiple file processing
   - Memory usage monitoring
   - Processing speed benchmarks
   - Cache effectiveness

## Testing Best Practices

1. **Mocking External Dependencies**
   - Mock Whisper API responses
   - Mock Pyannote models
   - Mock file system operations where appropriate

2. **Test Data**
   - Create sample audio files of various formats
   - Generate test transcripts
   - Prepare edge case scenarios

3. **Coverage Goals**
   - Aim for >90% code coverage
   - Focus on critical paths
   - Test error conditions thoroughly

4. **Continuous Integration**
   - Run tests on multiple Python versions (3.8+)
   - Test on different operating systems
   - Automated test runs on pull requests

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "not slow"
```

## Future Improvements

1. Add property-based testing with Hypothesis
2. Implement mutation testing
3. Add visual regression tests for transcript output
4. Create performance regression tests
5. Add security testing for file operations
