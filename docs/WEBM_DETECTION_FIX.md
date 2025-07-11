# WebM File Detection Issue - Diagnosis and Fix

## Problem Summary
The Obsidian Scribe application was not detecting or processing WebM files that were already present in the audio_input folder when the application started.

## Root Cause Analysis

### Issue 1: File stuck in processing set
When a file fails processing, it remains in the `_processing_files` set forever, preventing reprocessing. The `clear_processing_file` method existed but was never called.

**Fix Applied:**
- Added `file_watcher` reference to AudioProcessor
- Modified AudioProcessor to call `clear_processing_file` when processing fails
- Added method to FileWatcher to expose clearing functionality

### Issue 2: File readiness check failing for existing files
The `_is_file_ready` method requires two consecutive size checks with the same value to confirm a file is stable. For existing files during initial scan, this always fails on first attempt.

**Fix Applied:**
- Modified `_scan_existing_files` to pre-populate the file size in `handler._file_sizes`
- This allows existing files to pass the readiness check immediately

## Code Changes

### src/audio/processor.py
```python
# Added file_watcher reference
self.file_watcher = None  # Will be set by FileWatcher

# Added clearing logic on error
if hasattr(self, 'file_watcher') and self.file_watcher:
    self.file_watcher.clear_processing_file(file_path)
    self.logger.debug(f"Cleared {file_path} from processing set")
```

### src/watcher/file_watcher.py
```python
# Added back-reference setup
if hasattr(processor, 'file_watcher'):
    processor.file_watcher = self

# Added method to clear files
def clear_processing_file(self, file_path: str):
    """Clear a file from the processing set."""
    if hasattr(self, '_handler') and self._handler:
        self._handler.clear_processing_file(file_path)

# Fixed existing file scan
# Mark the file size as stable by setting it twice
file_size = file_path.stat().st_size
handler._file_sizes[full_path] = file_size
```

## Testing Results

### Diagnostic Test Output
```
File exists: True
Is valid audio file: True
File extension: .webm
Valid extensions: ['.wav', '.mp3', '.webm']
Extension in valid list: True
File in processing set: False
Should ignore: False
Is file ready: False  <-- This was the issue
File size: 34284104 bytes (32.70 MB)
```

## Next Steps

1. Restart the application to test the fix
2. Verify the WebM file is detected and processed
3. Monitor for successful audio conversion
4. Check audio chunking (file is 32.7 MB, over 25 MB limit)
5. Verify speaker diarization runs successfully

## Additional Improvements Needed

1. Add better logging for file detection and processing states
2. Implement a manual retry mechanism for failed files
3. Add status endpoint or command to check processing state
4. Consider adding a "force reprocess" option for stuck files