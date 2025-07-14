# Obsidian Scribe Documentation

Welcome to the Obsidian Scribe documentation! This guide will help you set up, configure, and use Obsidian Scribe for automated audio transcription and processing.

## Table of Contents

### User Guides
1. [Installation Guide](INSTALLATION.md) - How to install and set up Obsidian Scribe
2. [Configuration Guide](CONFIGURATION.md) - Detailed configuration options
3. [Usage Guide](USAGE.md) - How to use Obsidian Scribe effectively
4. [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

### Technical Documentation
5. [API Reference](API_REFERENCE.md) - Detailed API documentation
6. [Architecture Overview](technical/ARCHITECTURE.md) - System design and components
7. [Progress Tracking](PROGRESS_TRACKING.md) - Real-time diarization progress tracking
8. [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed development roadmap and technical specifications
9. [Technical Decisions](technical/TECHNICAL_DECISIONS.md) - Rationale for technology choices
10. [Configuration Schema](technical/CONFIG_SCHEMA.md) - Complete configuration reference
11. [Audio Chunking](technical/AUDIO_CHUNKING.md) - Audio processing strategy
12. [VoiceMeeter Setup](technical/VOICEMEETER_SETUP.md) - Audio routing configuration
13. [Whisper Integration](technical/WHISPER_INTEGRATION.md) - Integration guide

### Project Information
14. [Contributing](CONTRIBUTING.md) - How to contribute to the project
15. [Project Roadmap](project/PROJECT_ROADMAP.md) - Strategic development roadmap
16. [Project Structure](project/PROJECT_STRUCTURE.md) - Detailed project organization

## Quick Start

1. **Install Obsidian Scribe**:

   ```bash
   pip install -e .
   ```

2. **Configure your settings**:

   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your settings
   ```

3. **Run Obsidian Scribe**:

   ```bash
   python -m src.main
   ```

## Features

- **Automatic File Watching**: Monitors specified folders for new audio files
- **Speaker Diarization**: Identifies different speakers in audio recordings
- **Real-Time Progress Tracking**: Shows diarization progress with time estimates
- **High-Quality Transcription**: Uses OpenAI Whisper for accurate transcription
- **Obsidian Integration**: Generates Markdown files compatible with Obsidian
- **Smart Chunking**: Handles long audio files by intelligent chunking
- **Caching**: Improves performance with multi-level caching
- **Archive Management**: Automatically archives processed files
- **Extensible Architecture**: Modular design for easy customization

## System Requirements

- Python 3.8 or higher
- FFmpeg (for audio conversion)
- 4GB RAM minimum (8GB recommended)
- GPU recommended for diarization (optional)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/obsidian-scribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/obsidian-scribe/discussions)
- **Documentation**: You're reading it!

## License

Obsidian Scribe is released under the MIT License. See the LICENSE file for details.
