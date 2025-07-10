# Usage Guide

This guide covers how to use Obsidian Scribe for audio transcription and processing.

## Basic Usage

### Starting Obsidian Scribe

Run Obsidian Scribe with default settings:

```bash
python -m src.main
```

With custom configuration:

```bash
python -m src.main --config my-config.yaml
```

With command-line overrides:

```bash
python -m src.main --watch /path/to/audio --output /path/to/transcripts
```

### Stopping Obsidian Scribe

Press `Ctrl+C` to gracefully stop the application. It will:

- Complete any in-progress transcriptions
- Save the current state
- Clean up temporary files

## Processing Audio Files

### Supported Audio Formats

Obsidian Scribe supports the following audio formats:

- WAV (.wav)
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- OGG (.ogg)
- WMA (.wma)
- AAC (.aac)
- OPUS (.opus)

### File Processing Workflow

1. **Place audio files** in the configured audio folder
2. **Obsidian Scribe detects** new files automatically
3. **Processing begins** based on priority rules
4. **Transcripts are generated** in the output folder
5. **Original files are archived** (if configured)

### Priority Processing

Files are processed based on:

- **Size**: Smaller files first (configurable)
- **Age**: Older files first (configurable)
- **Name patterns**: Custom priority rules

Example priority configuration:

```yaml
processing:
  priority_rules:
    size_based: true
    age_based: true
    name_patterns:
      - pattern: "urgent_*"
        priority: 10
      - pattern: "meeting_*"
        priority: 5
```

## Output Formats

### Markdown Output

Default output format with speaker identification:

```markdown
# Transcript: meeting_2024-01-10.wav

**Date**: 2024-01-10 14:30:00
**Duration**: 45:23
**Speakers**: 3

---

[00:00:00] **SPEAKER_00:** Good afternoon, everyone. Let's begin today's meeting.

[00:00:15] **SPEAKER_01:** Thank you for joining. I'd like to start with...

[00:00:45] **SPEAKER_02:** Before we continue, I have a quick question...
```

### Output Templates

Choose from available templates:

1. **Detailed** (default): Full metadata and formatting
2. **Simple**: Minimal formatting
3. **Timestamped**: Emphasis on timing
4. **Speaker-focused**: Organized by speaker

Set template in configuration:

```yaml
output:
  template: "detailed"
```

## Advanced Features

### Speaker Diarization

Enable speaker identification:

```yaml
diarization:
  enabled: true
  min_speakers: 2
  max_speakers: 5
```

### Custom Prompts

Improve transcription accuracy with context:

```yaml
transcription:
  prompt: "Medical consultation between doctor and patient discussing symptoms and treatment options."
```

### Batch Processing

Process existing files:

1. Place all files in the audio folder
2. Start Obsidian Scribe
3. Files will be queued and processed

### Monitoring Progress

Watch the console output for:

- File detection notifications
- Processing progress
- Completion status
- Error messages

Enable debug logging for detailed information:

```bash
python -m src.main --log-level DEBUG
```

## Working with Obsidian

### Transcript Organization

Transcripts are saved with a structure compatible with Obsidian:

```
Transcripts/
├── 2024/
│   ├── 01/
│   │   ├── meeting_2024-01-10.md
│   │   └── interview_2024-01-15.md
│   └── 02/
│       └── conference_2024-02-01.md
```

### Obsidian Integration

1. **Add transcript folder** to your Obsidian vault
2. **Enable automatic reload** in Obsidian settings
3. **Use Obsidian search** to find content across transcripts
4. **Create links** between transcripts and notes

### Metadata and Tags

Transcripts include YAML frontmatter for Obsidian:

```yaml
---
title: "Meeting Transcript"
date: 2024-01-10
duration: "45:23"
speakers: 3
tags: [meeting, project-alpha, q1-2024]
---
```

## Performance Optimization

### Processing Speed

Improve processing speed:

1. **Increase concurrent processing**:

   ```yaml
   processing:
     concurrent_files: 4
   ```

2. **Optimize chunk size**:

   ```yaml
   audio:
     chunk_duration: 600  # 10 minutes
   ```

3. **Enable caching**:

   ```yaml
   cache:
     enabled: true
     cache_transcripts: true
   ```

### Memory Usage

Reduce memory usage:

1. **Limit concurrent files**:

   ```yaml
   processing:
     concurrent_files: 1
   ```

2. **Reduce cache size**:

   ```yaml
   cache:
     memory_cache_size: 50
   ```

### GPU Acceleration

Enable GPU for diarization:

1. Install CUDA-enabled PyTorch
2. Obsidian Scribe will automatically use GPU if available

## Troubleshooting Common Issues

### Files Not Being Processed

1. **Check file format**: Ensure files are in supported formats
2. **Check file size**: Verify files meet size requirements
3. **Check permissions**: Ensure read access to audio files
4. **Check logs**: Look for error messages

### Poor Transcription Quality

1. **Audio quality**: Ensure clear audio with minimal background noise
2. **Language setting**: Set correct language in configuration
3. **Custom prompts**: Add context-specific prompts
4. **Chunk overlap**: Increase overlap for better continuity

### Processing Errors

1. **API errors**: Check API key and internet connection
2. **File errors**: Ensure files aren't corrupted
3. **Memory errors**: Reduce concurrent processing
4. **Timeout errors**: Increase timeout values

## Command Reference

### Command-Line Arguments

```bash
python -m src.main [OPTIONS]

Options:
  -c, --config PATH         Configuration file path
  -w, --watch PATH         Override audio watch folder
  -o, --output PATH        Override transcript output folder
  --log-level LEVEL        Set logging level (DEBUG, INFO, WARNING, ERROR)
  --log-file PATH          Set log file path
  --version                Show version information
  -h, --help              Show help message
```

### Environment Variables

Key environment variables:

```bash
# API Keys
OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY="your-api-key"
OBSIDIAN_SCRIBE_DIARIZATION_AUTH_TOKEN="your-token"

# Paths
OBSIDIAN_SCRIBE_PATHS_AUDIO_FOLDER="/path/to/audio"
OBSIDIAN_SCRIBE_PATHS_TRANSCRIPT_FOLDER="/path/to/transcripts"

# Processing
OBSIDIAN_SCRIBE_PROCESSING_CONCURRENT_FILES="4"
OBSIDIAN_SCRIBE_AUDIO_CHUNK_DURATION="600"
```

## Best Practices

### Audio File Preparation

1. **Use consistent naming**: Include date and context
2. **Optimize audio quality**: 16kHz sample rate, mono
3. **Remove silence**: Trim long silences before/after
4. **Split long recordings**: Break into manageable segments

### Organization

1. **Folder structure**: Organize by date, project, or type
2. **Naming conventions**: Use descriptive, searchable names
3. **Archive regularly**: Clean up processed files
4. **Backup transcripts**: Keep copies of important transcripts

### Security

1. **Protect API keys**: Use environment variables
2. **Secure storage**: Encrypt sensitive recordings
3. **Access control**: Limit folder permissions
4. **Data retention**: Follow privacy policies

## Examples

### Example 1: Meeting Transcription

```bash
# Configure for meetings
export OBSIDIAN_SCRIBE_TRANSCRIPTION_PROMPT="Business meeting with multiple participants"
export OBSIDIAN_SCRIBE_DIARIZATION_MIN_SPEAKERS="2"

# Run with meeting-specific settings
python -m src.main --watch ./Meetings --output ./Meeting_Transcripts
```

### Example 2: Podcast Processing

```bash
# Configure for podcasts
export OBSIDIAN_SCRIBE_AUDIO_CHUNK_DURATION="900"  # 15-minute chunks
export OBSIDIAN_SCRIBE_OUTPUT_TEMPLATE="timestamped"

# Process podcast episodes
python -m src.main --watch ./Podcasts --output ./Podcast_Transcripts
```

### Example 3: Batch Processing Archive

```bash
# Configure for batch processing
export OBSIDIAN_SCRIBE_PROCESSING_CONCURRENT_FILES="1"
export OBSIDIAN_SCRIBE_ARCHIVE_ENABLED="false"

# Process archived recordings
python -m src.main --watch ./Archive --output ./Archive_Transcripts
```

## Next Steps

- Explore [API Reference](API_REFERENCE.md) for programmatic usage
- Read [Architecture Overview](ARCHITECTURE_OVERVIEW.md) for system understanding
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for problem resolution
