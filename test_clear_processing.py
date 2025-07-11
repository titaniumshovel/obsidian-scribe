"""
Test script to clear a file from the processing set.
This allows retrying a failed file without restarting the application.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The file we want to clear
file_path = r"audio_input\CECP Day 4 - First Half.webm"

print(f"Attempting to clear file from processing set: {file_path}")

# Create a marker file to trigger reprocessing
# We'll rename the file and rename it back to trigger the file watcher
try:
    full_path = os.path.join(os.getcwd(), file_path)
    temp_path = full_path + ".tmp"
    
    if os.path.exists(full_path):
        print(f"File exists at: {full_path}")
        print("Renaming file temporarily...")
        os.rename(full_path, temp_path)
        print("Waiting 2 seconds...")
        import time
        time.sleep(2)
        print("Renaming back to original...")
        os.rename(temp_path, full_path)
        print("Done! The file should be detected as new by the watcher.")
    else:
        print(f"File not found at: {full_path}")
        
except Exception as e:
    print(f"Error: {e}")