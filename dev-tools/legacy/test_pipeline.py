#!/usr/bin/env python3
"""
Test script for Obsidian Scribe pipeline.

This script tests the basic functionality of file watching and processing.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from obsidian_scribe.utils import setup_logging, ensure_directories


def create_test_directories():
    """Create test directories for the pipeline."""
    test_dirs = {
        'audio_folder': './test_audio',
        'transcript_folder': './test_transcripts',
        'archive_folder': './test_audio/archive',
        'temp_folder': './test_temp'
    }
    
    ensure_directories(test_dirs)
    return test_dirs


def create_test_audio_file(directory: str, filename: str = "test_audio.wav"):
    """Create a dummy audio file for testing."""
    file_path = Path(directory) / filename
    
    # Create a small dummy WAV file (just the header for testing)
    # This is a minimal WAV header for a 1-second silent file
    wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    with open(file_path, 'wb') as f:
        f.write(wav_header)
        # Add some dummy data
        f.write(b'\x00' * 1000)
    
    return file_path


def test_basic_pipeline():
    """Test the basic pipeline functionality."""
    print("=" * 60)
    print("Obsidian Scribe Pipeline Test")
    print("=" * 60)
    
    # Set up logging
    setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Create test directories
    logger.info("Creating test directories...")
    test_dirs = create_test_directories()
    
    # Import and initialize components
    from obsidian_scribe.file_watcher import FileWatcher
    from obsidian_scribe.processor import AudioProcessor
    
    # Create test configuration
    config = {
        'paths': test_dirs,
        'watcher': {
            'file_extensions': ['.wav', '.mp3'],
            'poll_interval': 1.0,
            'ignore_patterns': ['.*', '~*']
        },
        'processing': {
            'concurrent_files': 1,
            'retry_failed': True,
            'retry_delay': 5
        }
    }
    
    # Initialize processor
    logger.info("Initializing audio processor...")
    processor = AudioProcessor(config)
    processor.start()
    
    # Initialize file watcher
    logger.info("Initializing file watcher...")
    watcher = FileWatcher(
        watch_folder=config['paths']['audio_folder'],
        processor=processor,
        config=config['watcher']
    )
    watcher.start()
    
    # Give the system time to start
    time.sleep(2)
    
    # Create a test audio file
    logger.info("Creating test audio file...")
    test_file = create_test_audio_file(test_dirs['audio_folder'], "test_recording_001.wav")
    logger.info(f"Created test file: {test_file}")
    
    # Wait for processing
    logger.info("Waiting for file to be processed...")
    max_wait = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # Check if file was archived (moved from audio folder)
        if not test_file.exists():
            logger.info("File has been processed and archived!")
            break
        
        # Check for transcript
        transcript_files = list(Path(test_dirs['transcript_folder']).glob('*.md'))
        if transcript_files:
            logger.info(f"Transcript created: {transcript_files[0]}")
            break
            
        time.sleep(1)
    
    # Check results
    logger.info("\nChecking results...")
    
    # Check archive
    archive_files = list(Path(test_dirs['archive_folder']).rglob('*.wav'))
    if archive_files:
        logger.info(f"✓ File archived: {archive_files[0]}")
    else:
        logger.warning("✗ File not found in archive")
    
    # Check transcripts
    transcript_files = list(Path(test_dirs['transcript_folder']).glob('*.md'))
    if transcript_files:
        logger.info(f"✓ Transcript created: {transcript_files[0]}")
        # Read and display transcript content
        with open(transcript_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"\nTranscript content preview:\n{content[:500]}...")
    else:
        logger.warning("✗ No transcript found")
    
    # Get processing stats
    stats = processor.get_stats()
    logger.info(f"\nProcessing statistics: {stats}")
    
    # Stop components
    logger.info("\nStopping components...")
    watcher.stop()
    processor.stop()
    
    # Clean up test directories (optional)
    # import shutil
    # for path in test_dirs.values():
    #     if Path(path).exists():
    #         shutil.rmtree(path)
    
    logger.info("\nTest completed!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_basic_pipeline()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()