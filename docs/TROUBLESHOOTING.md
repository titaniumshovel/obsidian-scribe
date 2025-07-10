# Troubleshooting Guide

This guide helps you resolve common issues with Obsidian Scribe.

## Quick Diagnostics

Run the diagnostic command to check your setup:

```bash
python -m src.main --diagnose
```

This checks:

- Python version compatibility
- Required dependencies
- FFmpeg availability
- Configuration validity
- API connectivity
- File permissions

## Common Issues

### Installation Issues

#### "Module not found" Errors

**Problem**: Python can't find Obsidian Scribe modules.

**Solutions**:

1. Ensure you're in the virtual environment:

   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. Reinstall in development mode:

   ```bash
   pip install -e .
   ```

3. Check Python path:

   ```python
   import sys
   print(sys.path)
   ```

#### FFmpeg Not Found

**Problem**: "FFmpeg not found" error during audio processing.

**Solutions**:

1. Verify FFmpeg installation:

   ```bash
   ffmpeg -version
   ```

2. Add FFmpeg to PATH:
   - **Windows**: Add FFmpeg bin directory to System PATH
   - **macOS**: `export PATH="/usr/local/bin:$PATH"`
   - **Linux**: `export PATH="/usr/bin:$PATH"`

3. Specify FFmpeg path in config:

   ```yaml
   audio:
     ffmpeg_path: "/path/to/ffmpeg"
   ```

### Configuration Issues

#### Invalid Configuration Error

**Problem**: "Configuration validation failed" on startup.

**Solutions**:

1. Check error message for specific field
2. Verify YAML syntax:

   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

3. Common YAML issues:
   - Use spaces, not tabs
   - Proper indentation (2 spaces)
   - Quote strings with special characters

#### API Key Not Working

**Problem**: "Authentication failed" or "Invalid API key".

**Solutions**:

1. Verify API key format:

   ```bash
   echo $OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY
   ```

2. Check API key permissions
3. Test API directly:

   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY"
   ```

### File Processing Issues

#### Files Not Being Detected

**Problem**: Audio files aren't being processed.

**Checklist**:

1. ✓ File in correct folder?
2. ✓ File extension supported?
3. ✓ File size within limits?
4. ✓ File not hidden (starting with .)?
5. ✓ File permissions readable?

**Debug steps**:

```bash
# Check file detection
python -m src.main --log-level DEBUG

# List watched files
ls -la ./Audio/

# Check file size
du -h ./Audio/myfile.wav
```

#### Processing Stuck

**Problem**: File processing doesn't complete.

**Solutions**:

1. Check log file for errors:

   ```bash
   tail -f obsidian_scribe.log
   ```

2. Monitor system resources:

   ```bash
   # CPU and memory usage
   top
   
   # Disk space
   df -h
   ```

3. Reduce concurrent processing:

   ```yaml
   processing:
     concurrent_files: 1
   ```

### Transcription Issues

#### Poor Transcription Quality

**Problem**: Transcripts have errors or missing content.

**Solutions**:

1. **Audio quality check**:
   - Ensure clear audio (no background noise)
   - Check audio format compatibility
   - Verify sample rate (16kHz recommended)

2. **Language settings**:

   ```yaml
   transcription:
     language: "en"  # Set specific language
   ```

3. **Add context prompt**:

   ```yaml
   transcription:
     prompt: "Technical discussion about software development"
   ```

4. **Adjust chunk settings**:

   ```yaml
   audio:
     chunk_duration: 180  # Smaller chunks
     overlap_duration: 5  # More overlap
   ```

#### Transcription Timeouts

**Problem**: "Request timeout" errors.

**Solutions**:

1. Increase timeout:

   ```yaml
   transcription:
     timeout: 600  # 10 minutes
   ```

2. Reduce chunk size:

   ```yaml
   audio:
     chunk_duration: 120  # 2 minutes
   ```

3. Check internet connection speed

### Speaker Diarization Issues

#### Speakers Not Identified

**Problem**: All text attributed to "SPEAKER_00".

**Solutions**:

1. Verify diarization is enabled:

   ```yaml
   diarization:
     enabled: true
   ```

2. Check Hugging Face token:

   ```bash
   echo $OBSIDIAN_SCRIBE_DIARIZATION_AUTH_TOKEN
   ```

3. Adjust speaker settings:

   ```yaml
   diarization:
     min_speakers: 2
     max_speakers: 5
     min_segment_duration: 0.5
   ```

#### Wrong Speaker Count

**Problem**: Incorrect number of speakers detected.

**Solutions**:

1. Set expected speaker range:

   ```yaml
   diarization:
     min_speakers: 3
     max_speakers: 3  # Force exact count
   ```

2. Adjust merge threshold:

   ```yaml
   diarization:
     merge_threshold: 0.7  # Higher = fewer speakers
   ```

### Performance Issues

#### High Memory Usage

**Problem**: Obsidian Scribe uses too much RAM.

**Solutions**:

1. Reduce concurrent processing:

   ```yaml
   processing:
     concurrent_files: 1
   ```

2. Limit cache size:

   ```yaml
   cache:
     memory_cache_size: 50
     disk_cache_size_mb: 200
   ```

3. Process smaller chunks:

   ```yaml
   audio:
     chunk_duration: 60
   ```

#### Slow Processing

**Problem**: Transcription takes too long.

**Solutions**:

1. Enable GPU acceleration (if available)
2. Increase concurrent processing:

   ```yaml
   processing:
     concurrent_files: 4
   ```

3. Use caching:

   ```yaml
   cache:
     enabled: true
     cache_transcripts: true
   ```

### Archive Issues

#### Files Not Archived

**Problem**: Processed files remain in audio folder.

**Solutions**:

1. Check archive settings:

   ```yaml
   archive:
     enabled: true
   ```

2. Verify archive folder permissions:

   ```bash
   ls -la ./Audio/Archive/
   ```

3. Check disk space:

   ```bash
   df -h
   ```

## Error Messages

### Common Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| `E001` | Configuration invalid | Check config.yaml syntax |
| `E002` | API authentication failed | Verify API key |
| `E003` | File not found | Check file path |
| `E004` | FFmpeg error | Verify FFmpeg installation |
| `E005` | Network timeout | Check internet connection |
| `E006` | Insufficient memory | Reduce concurrent processing |
| `E007` | Disk space full | Free up disk space |
| `E008` | Permission denied | Check file permissions |

### API Error Responses

#### OpenAI API Errors

- **401 Unauthorized**: Invalid API key
- **429 Rate Limited**: Too many requests
- **500 Server Error**: OpenAI service issue
- **503 Service Unavailable**: Temporary outage

#### Hugging Face Errors

- **401 Invalid Token**: Check auth token
- **403 Forbidden**: Token lacks permissions
- **413 Payload Too Large**: Audio file too big

## Debug Mode

Enable comprehensive debugging:

```bash
# Maximum verbosity
python -m src.main --log-level DEBUG

# Debug specific module
export OBSIDIAN_SCRIBE_DEBUG_MODULE="transcriber"

# Save debug logs
python -m src.main --log-level DEBUG --log-file debug.log
```

## Getting Help

### Collect Diagnostic Information

When reporting issues, include:

1. **System information**:

   ```bash
   python --version
   pip list | grep obsidian
   ffmpeg -version
   ```

2. **Configuration** (remove sensitive data):

   ```bash
   cat config.yaml | grep -v api_key
   ```

3. **Error logs**:

   ```bash
   tail -n 100 obsidian_scribe.log
   ```

4. **Sample file information**:

   ```bash
   ffprobe -v error -show_format -show_streams audio_file.wav
   ```

### Support Channels

1. **GitHub Issues**: For bugs and feature requests
2. **Discussions**: For questions and help
3. **Wiki**: For detailed documentation
4. **Discord**: For real-time support (if available)

## Recovery Procedures

### Recover from Interrupted Processing

```bash
# Check processing state
sqlite3 state.db "SELECT * FROM processing_queue WHERE status='processing';"

# Reset stuck files
python -m src.utils.reset_queue

# Resume processing
python -m src.main
```

### Restore from Backup

```bash
# Restore configuration
cp config.yaml.backup config.yaml

# Restore state database
cp state.db.backup state.db

# Verify and restart
python -m src.main --diagnose
```

## Preventive Measures

1. **Regular backups**: Back up config and state database
2. **Monitor disk space**: Keep 20% free space
3. **Update regularly**: Check for updates monthly
4. **Test configuration**: Validate after changes
5. **Archive old files**: Prevent folder bloat

## Advanced Debugging

### Enable Python Debugging

```python
# Add to your config
import pdb; pdb.set_trace()
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Run with profiling
python -m memory_profiler src.main
```

### Performance Profiling

```bash
# Install profiler
pip install py-spy

# Profile running process
py-spy record -o profile.svg --pid <PID>
```

Remember: Most issues can be resolved by checking logs, validating configuration, and ensuring all dependencies are properly installed.
