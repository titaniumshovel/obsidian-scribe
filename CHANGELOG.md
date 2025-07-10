# Changelog

All notable changes to Obsidian Scribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release of Obsidian Scribe
- Core file watching functionality with watchdog library
- Audio processing pipeline with chunking support
- Whisper API integration for transcription
- Pyannote.audio integration for speaker diarization
- Markdown output formatting for Obsidian
- Configuration management with YAML and environment variables
- Multi-level caching system (memory and disk)
- Archive management with compression and retention policies
- SQLite-based state tracking and recovery
- Comprehensive error handling and retry logic
- Atomic file operations for data integrity
- Priority queue for processing order
- Extensive logging with color support
- Command-line interface with argument parsing
- Docker support for containerized deployment
- Comprehensive test suite infrastructure
- Full documentation suite

### Configuration

- YAML-based configuration with schema validation
- Environment variable overrides for sensitive data
- Dot notation for nested configuration access
- Runtime validation of configuration values

### Audio Processing

- Support for multiple audio formats (mp3, wav, m4a, flac, ogg, wma, aac)
- Automatic format conversion using FFmpeg
- Configurable chunk size and overlap
- Silence-based splitting option
- GPU acceleration support for diarization

### Output Features

- Customizable Markdown templates
- YAML frontmatter with metadata
- Speaker-aware formatting
- Timestamp preservation
- Confidence scores in output

### Storage Features

- Automatic archiving of processed files
- Configurable retention policies
- Compression support (ZIP and TAR.GZ)
- Safe file operations with atomic writes
- Automatic directory creation

### Performance

- Multi-threaded processing support
- Connection pooling for API calls
- LRU caching with TTL support
- Lazy loading of heavy dependencies
- Memory-mapped file support for large audio

### Security

- API key management via environment variables
- Path traversal prevention
- Input validation and sanitization
- No telemetry or data collection

## [0.1.0] - TBD

### Added This Version

- First public release
- Basic functionality for audio transcription
- Obsidian integration support
- Documentation and examples

### Known Issues

- Large audio files (>1GB) may require significant memory
- GPU support requires manual CUDA setup
- Some audio formats may require additional codecs

### Future Plans

- Real-time transcription support
- Web interface for monitoring
- Cloud storage integration
- Additional transcription providers
- Batch processing improvements
- Plugin system for extensibility

---

## Version History Format

### [Version] - Date

#### Added Features

- New features

#### Changed

- Changes in existing functionality

#### Deprecated

- Soon-to-be removed features

#### Removed

- Removed features

#### Fixed

- Bug fixes

#### Security Updates

- Security updates
