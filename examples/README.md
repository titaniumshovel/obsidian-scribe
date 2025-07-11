# Examples and Sample Data

This directory contains example files and sample data for testing and demonstration purposes.

## Directory Structure

### `sample-data/`
Contains real sample files generated during development and testing:

#### `sample-data/audio_input/`
- **Purpose**: Example audio files in various formats
- **Contents**: WebM files from actual Obsidian Whisper recordings
- **Usage**: Test the file detection and processing pipeline

#### `sample-data/archive/`  
- **Purpose**: Processed audio files that have been archived
- **Contents**: Original audio files after successful transcription
- **Usage**: Understand the archival workflow

#### `sample-data/Transcripts/`
- **Purpose**: Generated transcript examples
- **Contents**: Actual transcripts with speaker diarization and timestamps
- **Usage**: See expected output format and quality

## Using Sample Data

### Testing File Processing
```bash
# Copy a sample audio file to your watch folder
cp examples/sample-data/audio_input/test-estimation.webm ./Audio/

# Run Obsidian Scribe to process it
source venv/bin/activate
python -m src.main
```

### Testing Without Diarization
```bash
# Process with faster, single-speaker mode
python -m src.main --no-diarization
```

### Viewing Sample Transcripts
The `sample-data/Transcripts/` directory contains examples of:
- Multi-speaker transcripts with diarization
- Timestamped segments
- Obsidian-compatible Markdown formatting
- YAML front matter with metadata

## File Formats

### Audio Files
- **WebM**: From Obsidian Whisper plugin recordings
- Shows compatibility with real-world usage

### Transcript Files  
- **Markdown format**: Optimized for Obsidian
- **YAML front matter**: Rich metadata
- **Speaker sections**: Clear organization
- **Timestamps**: Precise timing information

## Development Usage

These samples are valuable for:
1. **Testing new features** - Validate against known good data
2. **Performance benchmarking** - Measure processing improvements
3. **Format validation** - Ensure output compatibility
4. **Documentation** - Show expected results to users

## Regenerating Samples

To create new sample data:
1. Record audio using Obsidian Whisper plugin
2. Process with Obsidian Scribe
3. Copy interesting results to this directory
4. Update documentation with new examples

## Privacy Note

⚠️ **Sample data should not contain sensitive information**
- Use test recordings only
- Avoid personal conversations
- Check content before committing to repository