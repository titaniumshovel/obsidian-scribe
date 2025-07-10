# Changelog

All notable changes to Obsidian Scribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-10

### Added

- Complete project restructuring with modular architecture
- Comprehensive documentation suite in `docs/` directory:
  - Installation guide with prerequisites and troubleshooting
  - Usage guide with examples and best practices
  - Configuration reference with all options
  - API reference for all modules
  - Architecture overview with system design
  - Troubleshooting guide for common issues
  - Contributing guidelines
- Modern Python packaging:
  - `setup.py` with entry points and dependencies
  - `setup.cfg` with metadata and tool configuration
  - `pyproject.toml` with Black formatting config
  - `Makefile` for development tasks
- `.gitignore` file with comprehensive exclusions:
  - Sensitive configuration files (config.yaml, .env)
  - Audio files and processing directories
  - Python artifacts and virtual environments
  - IDE and OS-specific files
- `.env.example` with documented environment variables

### Fixed

- Import errors in `src/audio/transcriber.py`:
  - Updated deprecated `requests.packages.urllib3.util.retry` to `urllib3.util.retry`
- Type annotation issues in `src/watcher/file_watcher.py`:
  - Fixed Observer type annotation for Pylance compatibility
- Missing dependencies in `requirements.txt`:
  - Added `urllib3>=2.0.0` for retry functionality
  - Added `ffmpeg-python>=0.2.0` for audio processing
  - Uncommented `pyannote.audio`, `torch`, and `torchaudio` for diarization
- Markdown linting issues in documentation:
  - Added language specifiers to all code blocks

### Changed

- Updated README.md to reflect new structure and installation process
- Enhanced project documentation with complete guides
- Improved error messages and logging throughout

### Project Structure

- Initial release of Obsidian Scribe with complete architecture:
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

## Development Progress

### 2025-01-10 - Major Restructuring Complete

All components have been implemented according to the architecture:

- ✅ Configuration management with YAML and environment variables
- ✅ File watching system with priority queue
- ✅ Audio processing pipeline with chunking
- ✅ Speaker diarization with pyannote.audio
- ✅ Whisper API transcription
- ✅ Transcript generation with templates
- ✅ Storage management with archiving
- ✅ Comprehensive utility modules
- ✅ Complete documentation suite
- ✅ Modern Python packaging

The project is now ready for testing and deployment.

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
