#!/usr/bin/env python3
"""
Simple test script to verify Obsidian Scribe is working.
Creates a test audio file and runs the application.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=== Obsidian Scribe Test Run ===\n")

# Check if we have ffmpeg
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    print("✅ FFmpeg is available")
except:
    print("❌ FFmpeg not found. Please install FFmpeg first.")
    print("   Download from: https://ffmpeg.org/download.html")
    sys.exit(1)

# Create test audio file using ffmpeg (5 seconds of silence)
print("\n1. Creating test audio file...")
test_audio_path = Path("audio_input/test_audio.wav")
test_audio_path.parent.mkdir(exist_ok=True)

# Generate a 5-second test tone
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi',
    '-i', 'sine=frequency=440:duration=5',
    '-ar', '16000',
    '-ac', '1',
    str(test_audio_path)
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Created test audio file: {test_audio_path}")
    else:
        print(f"❌ Failed to create test audio: {result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error creating test audio: {e}")
    sys.exit(1)

# Update config to use correct API endpoint
print("\n2. Checking API configuration...")
api_key = os.environ.get('OPENAI_API_KEY', '')
if api_key and api_key != 'your-api-key-here':
    print("✅ API key is configured")
else:
    print("⚠️  API key not properly configured")
    print("   Please update the OPENAI_API_KEY in .env file with your actual API key")
    print("   The test will continue but transcription may fail")

# Run the application
print("\n3. Starting Obsidian Scribe...")
print("   The application will watch for audio files in ./audio_input/")
print("   Transcripts will be saved to ./transcripts/")
print("   Status updates will be shown every 30 seconds")
print("   Press Ctrl+C to stop\n")

try:
    # Run the main application
    subprocess.run([sys.executable, '-m', 'src.main', '--log-level', 'INFO'])
except KeyboardInterrupt:
    print("\n\n✅ Test completed. Check ./transcripts/ for the output.")
except Exception as e:
    print(f"\n❌ Error running application: {e}")
    sys.exit(1)