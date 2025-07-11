# Progress Tracking in Obsidian Scribe

## Overview

Obsidian Scribe now includes real-time progress tracking for speaker diarization, providing users with visibility into the processing status and estimated completion times.

## Features

### 1. Real-Time Progress Updates
- Progress updates every 2 seconds during diarization
- Shows elapsed time and estimated total time
- Displays percentage completion
- Clear status messages at each stage

### 2. Time Estimation
The system estimates diarization time based on file size:
- **CPU Processing**: ~75 seconds per MB of WAV audio
- **GPU Processing**: ~20 seconds per MB of WAV audio (if available)
- Includes a 15% buffer for variability

### 3. Progress Display Format
Progress updates appear in the logs as:
```
Diarization progress: Diarizing... (30s / ~233s) (13%)
```

Where:
- `30s` = elapsed time
- `~233s` = estimated total time
- `13%` = percentage complete

## Implementation Details

### Progress Callback
The diarization module accepts an optional progress callback:

```python
def diarize(self, audio_path: str, progress_callback: Optional[Callable[[str, float], None]] = None) -> Dict:
    """
    Perform speaker diarization on an audio file.
    
    Args:
        audio_path: Path to the audio file
        progress_callback: Optional callback for progress updates (message, percentage)
    """
```

### Time Estimation Algorithm
Based on empirical data:
- Small files (0.35 MB WebM → 0.70 MB WAV): ~60 seconds
- Medium files (1.34 MB WebM → 2.64 MB WAV): ~190 seconds

The estimation formula:
```python
estimated_time = base_time + (file_size_mb * time_per_mb) * buffer
```

Where:
- `base_time` = 5 seconds (initialization overhead)
- `time_per_mb` = 75 seconds for CPU, 20 seconds for GPU
- `buffer` = 1.15 (15% safety margin)

## Example Output

```
2025-07-11 12:03:08,710 - INFO - Estimated diarization time: 233.5 seconds for 2.64 MB file
2025-07-11 12:03:08,711 - INFO - Diarization progress: Starting diarization (estimated 233s)... (0%)
2025-07-11 12:03:10,718 - INFO - Diarization progress: Diarizing... (2s / ~233s) (1%)
2025-07-11 12:03:12,746 - INFO - Diarization progress: Diarizing... (4s / ~233s) (2%)
...
2025-07-11 12:09:40,654 - INFO - Diarization progress: Processing diarization results... (98%)
2025-07-11 12:09:40,656 - INFO - Diarization progress: Diarization complete (1 speakers) (100%)
2025-07-11 12:09:40,655 - INFO - Actual diarization time: 191.7 seconds (estimated was 233.5s)
```

## Benefits

1. **User Awareness**: Users know the system is working and approximately how long to wait
2. **Better UX**: No more wondering if the process is stuck
3. **Accurate Estimates**: Based on real performance data
4. **Debugging Aid**: Helps identify performance issues

## Future Enhancements

1. **Progress Bar UI**: Add visual progress bar for GUI implementations
2. **Adaptive Estimation**: Learn from actual processing times to improve estimates
3. **Cancellation Support**: Allow users to cancel long-running operations
4. **Resource Monitoring**: Show CPU/GPU usage during processing