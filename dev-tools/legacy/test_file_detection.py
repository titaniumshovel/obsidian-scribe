"""
Diagnostic script to test file detection logic.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.watcher.event_handler import AudioFileHandler
from src.watcher.queue_manager import QueueManager

# Test configuration
config = {
    'file_extensions': ['.wav', '.mp3', '.webm'],
    'ignore_patterns': ['.*', '~*']
}

# Create handler
queue_manager = QueueManager()
handler = AudioFileHandler(queue_manager, config)

# Test file path
file_path = r"audio_input\CECP Day 4 - First Half.webm"
full_path = os.path.join(os.getcwd(), file_path)

print(f"Testing file detection for: {full_path}")
print(f"File exists: {os.path.exists(full_path)}")
print(f"Is file: {os.path.isfile(full_path)}")

# Test validation
is_valid = handler._is_valid_audio_file(full_path)
print(f"Is valid audio file: {is_valid}")

# Check extension
file_ext = os.path.splitext(full_path)[1].lower()
print(f"File extension: {file_ext}")
print(f"Valid extensions: {handler.file_extensions}")
print(f"Extension in valid list: {file_ext in handler.file_extensions}")

# Check if file is in processing set
print(f"File in processing set: {full_path in handler._processing_files}")

# Check ignore patterns
should_ignore = handler._should_ignore(full_path)
print(f"Should ignore: {should_ignore}")

# Test file readiness
is_ready = handler._is_file_ready(full_path)
print(f"Is file ready: {is_ready}")

# Check file size
try:
    size = os.path.getsize(full_path)
    print(f"File size: {size} bytes ({size / (1024*1024):.2f} MB)")
except Exception as e:
    print(f"Error getting file size: {e}")