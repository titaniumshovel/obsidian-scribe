# Obsidian Whisper Plugin Integration Guide

## Overview

Obsidian Scribe is designed to work alongside the Obsidian Whisper plugin, creating a powerful two-tool workflow for audio recording and processing. This document explains how to configure both tools for optimal integration.

## Tool Responsibilities

### Obsidian Whisper Plugin
- **Primary Role**: Audio recording interface within Obsidian
- **Features Used**:
  - Recording from VoiceMeeter virtual microphone
  - Saving audio files to vault
  - Quick transcription for simple notes (optional)
- **Features to Disable**:
  - Automatic transcription (for files needing diarization)

### Obsidian Scribe
- **Primary Role**: Advanced post-processing
- **Features Provided**:
  - Speaker diarization (identifying who said what)
  - Large file handling (>25MB chunking)
  - Enhanced Markdown formatting
  - Batch processing
  - File archiving

## Configuration Guide

### Step 1: Configure Obsidian Whisper Plugin

In Obsidian settings, configure the Whisper plugin:

```yaml
# Recommended Whisper Plugin Settings
API Key: [Your OpenAI API Key]
API URL: https://api.openai.com/v1  # Keep default
Model: whisper-1
Language: en  # Or your preferred language

# Critical Settings for Integration
Save recording: ON  # Must be enabled
Recordings folder: Audio  # Where Scribe will monitor
Save transcription: OFF  # Let Scribe handle this

# Optional Settings
Audio format: webm  # Recommended for size
Sample rate: 16000  # Good for speech
```

### Step 2: Configure Obsidian Scribe

In your `config.yaml` for Obsidian Scribe:

```yaml
obsidian_scribe:
  paths:
    # Must match Whisper's recordings folder
    audio_folder: "${OBSIDIAN_VAULT}/Audio"
    transcript_folder: "${OBSIDIAN_VAULT}/Transcripts"
    archive_folder: "${OBSIDIAN_VAULT}/Audio/Archive"
  
  # Process files created by Whisper
  watcher:
    file_extensions: [".webm", ".mp3", ".wav"]
    min_file_age: 5  # Wait for Whisper to finish writing
  
  # Skip Whisper's transcriptions if any exist
  processing:
    skip_existing_transcripts: true
```

## Workflow Scenarios

### Scenario 1: Quick Note (Whisper Only)
For quick personal notes without multiple speakers:

1. **Enable transcription** in Whisper temporarily
2. Record your note
3. Whisper creates instant transcription
4. Obsidian Scribe skips the file (transcript exists)

### Scenario 2: Meeting Recording (Both Tools)
For meetings with multiple participants:

1. **Disable transcription** in Whisper
2. Record meeting via VoiceMeeter
3. Whisper saves audio file only
4. Obsidian Scribe automatically:
   - Detects the new audio file
   - Performs speaker diarization
   - Creates enhanced transcript

### Scenario 3: Large Recording (Both Tools)
For recordings over 25MB:

1. Record normally with Whisper
2. Whisper saves the large file
3. Obsidian Scribe automatically:
   - Detects file size >25MB
   - Splits into chunks
   - Processes each chunk
   - Combines results

## File Organization

```
Obsidian Vault/
├── Audio/                    # Whisper saves here
│   ├── Meeting-2024-01-15.webm
│   ├── Quick-Note-2024-01-15.webm
│   └── Archive/             # Scribe moves processed files here
│       └── Meeting-2024-01-15.webm
├── Transcripts/             # Scribe creates transcripts here
│   └── Meeting-2024-01-15.md
└── Quick-Note-2024-01-15.md  # Created by Whisper (if enabled)
```

## Handling Edge Cases

### Both Tools Creating Transcripts
If both tools are configured to create transcripts:
- Whisper creates: `Audio/transcript.md`
- Scribe creates: `Transcripts/transcript.md`
- No conflict, but duplication

**Solution**: Disable Whisper transcription for recordings needing diarization.

### Processing Delays
Obsidian Scribe waits 5 seconds (`min_file_age`) before processing to ensure:
- Whisper has finished writing the file
- File system has flushed all data
- No partial file processing

### Selective Processing
You can configure Scribe to only process certain files:
```yaml
watcher:
  ignore_patterns: 
    - "Quick-Note-*"  # Skip personal notes
    - "Draft-*"       # Skip drafts
```

## Best Practices

1. **Clear Naming Convention**
   - Meeting recordings: `Meeting-YYYY-MM-DD-Topic.webm`
   - Personal notes: `Note-YYYY-MM-DD-Topic.webm`
   - This helps with selective processing

2. **Folder Organization**
   - Keep Whisper recordings in `Audio/`
   - Let Scribe manage `Audio/Archive/`
   - Transcripts go to `Transcripts/`

3. **API Key Management**
   - Whisper: Uses OpenAI API for quick transcription
   - Scribe: Uses company API for advanced processing
   - Different keys prevent quota conflicts

4. **Performance Optimization**
   - Run Scribe as a background service
   - Configure concurrent processing based on system
   - Monitor log files for any issues

## Troubleshooting

### Scribe Not Processing Files
1. Check `audio_folder` path matches Whisper's setting
2. Verify file extensions are in `file_extensions` list
3. Check Scribe logs for errors
4. Ensure Scribe service is running

### Duplicate Transcriptions
1. Disable Whisper's `Save transcription` setting
2. Or configure Scribe to skip existing transcripts
3. Use different output folders if needed

### Missing Speaker Labels
1. Verify audio has multiple speakers
2. Check diarization is enabled in Scribe
3. Review audio quality (VoiceMeeter mixing)

## Migration from Whisper-Only Workflow

If you have existing Whisper transcriptions:

1. **Keep existing transcripts** as-is
2. **Configure Scribe** to process new recordings only
3. **Optionally reprocess** old recordings:
   ```bash
   python obsidian_scribe.py --reprocess --folder "Audio/Old-Recordings"
   ```

This integration approach gives you the best of both worlds: Whisper's convenient recording interface and Scribe's advanced processing capabilities.