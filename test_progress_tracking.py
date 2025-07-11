"""Test script to verify diarization progress tracking."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.audio.diarizer import SpeakerDiarizer
from src.config.manager import ConfigManager

def progress_callback(message: str, percentage: float):
    """Print progress updates."""
    print(f"[{percentage:3.0f}%] {message}")

def main():
    # Load config
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Create diarizer
    diarizer = SpeakerDiarizer(config)
    
    # Test file path
    test_file = "archive/2025/07/11/test_audio.wav"
    
    if not Path(test_file).exists():
        print(f"Test file not found: {test_file}")
        return
    
    # Get file size
    file_size_mb = Path(test_file).stat().st_size / (1024 * 1024)
    print(f"Test file size: {file_size_mb:.2f} MB")
    
    # Estimate time
    estimated_time = diarizer._estimate_diarization_time(file_size_mb)
    print(f"Estimated diarization time: {estimated_time:.1f} seconds")
    
    # Run diarization with progress tracking
    print("\nStarting diarization with progress tracking...")
    start_time = time.time()
    
    result = diarizer.diarize(test_file, progress_callback=progress_callback)
    
    actual_time = time.time() - start_time
    print(f"\nActual time: {actual_time:.1f} seconds")
    print(f"Found {len(result['speakers'])} speakers")
    print(f"Found {len(result['segments'])} segments")

if __name__ == "__main__":
    main()