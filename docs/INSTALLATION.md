# Installation Guide

This guide will walk you through installing Obsidian Scribe on your system.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for diarization)
- **Storage**: At least 2GB free space for dependencies
- **GPU**: Optional but recommended for faster diarization

### Required Software

1. **Python 3.8+**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - macOS: `brew install python3`
   - Linux: `sudo apt-get install python3 python3-pip`

2. **FFmpeg**
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

3. **Git** (for development installation)
   - Windows: Download from [git-scm.com](https://git-scm.com/download/win)
   - macOS: `brew install git`
   - Linux: `sudo apt-get install git`

## Installation Methods

### Method 1: From Source (Recommended for Development)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/obsidian-scribe.git
   cd obsidian-scribe
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install in development mode**:

   ```bash
   pip install -e .
   ```

4. **Install additional dependencies for diarization** (optional):

   ```bash
   pip install -e ".[diarization]"
   ```

### Method 2: Using pip (Coming Soon)

```bash
pip install obsidian-scribe
```

### Method 3: Using Docker (Coming Soon)

```bash
docker pull obsidian-scribe/obsidian-scribe
docker run -v /path/to/audio:/audio obsidian-scribe
```

## Post-Installation Setup

### 1. Configuration

Copy the example configuration file:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your preferred settings. Key configurations:

- **API Keys**: Set your OpenAI API key for transcription
- **Paths**: Configure input/output directories
- **Audio Settings**: Adjust quality and processing parameters

### 2. Environment Variables

For sensitive information, use environment variables:

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
export OBSIDIAN_SCRIBE_API_KEY="your-openai-api-key"
export OBSIDIAN_SCRIBE_HUGGINGFACE_TOKEN="your-hf-token"
```

### 3. Verify Installation

Run the verification script:

```bash
python -m src.main --version
```

Test with a sample audio file:

```bash
python test_pipeline.py
```

## Platform-Specific Notes

### Windows

- Ensure FFmpeg is in your system PATH
- Use PowerShell or Command Prompt as Administrator for installation
- Consider using Windows Terminal for better experience

### macOS

- If using Apple Silicon (M1/M2), some dependencies may require Rosetta 2
- Install Xcode Command Line Tools: `xcode-select --install`

### Linux

- On Ubuntu/Debian, you may need additional packages:

  ```bash
  sudo apt-get install python3-dev portaudio19-dev
  ```

## GPU Setup (Optional)

For faster diarization with GPU support:

### NVIDIA GPUs

1. Install CUDA Toolkit (11.8 or higher)
2. Install PyTorch with CUDA support:

   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Apple Silicon

PyTorch should automatically use Metal Performance Shaders (MPS) on supported devices.

## Troubleshooting Installation

### Common Issues

1. **"pip: command not found"**
   - Ensure Python is installed and added to PATH
   - Try `python -m pip` instead of `pip`

2. **"FFmpeg not found"**
   - Verify FFmpeg installation: `ffmpeg -version`
   - Add FFmpeg to system PATH

3. **Permission errors**
   - Use virtual environment (recommended)
   - Or install with user flag: `pip install --user -e .`

4. **Dependency conflicts**
   - Create a fresh virtual environment
   - Update pip: `pip install --upgrade pip`

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/yourusername/obsidian-scribe/issues)
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [Configuration Guide](CONFIGURATION.md) to customize settings
2. Follow the [Usage Guide](USAGE.md) to start processing audio files
3. Explore the [API Reference](API_REFERENCE.md) for advanced usage

## Updating Obsidian Scribe

To update to the latest version:

```bash
# If installed from source
git pull origin main
pip install -e . --upgrade

# If installed via pip (when available)
pip install --upgrade obsidian-scribe
```

Always check the [CHANGELOG](../CHANGELOG.md) for breaking changes before updating.
