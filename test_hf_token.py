"""Test script to check Hugging Face token configuration."""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging to capture INFO messages
logging.basicConfig(level=logging.INFO, format='%(message)s')

from src.config.manager import ConfigManager
from src.audio.diarizer import SpeakerDiarizer

def test_hf_token():
    """Test Hugging Face token detection."""
    print("=== Testing Hugging Face Token Configuration ===\n")
    
    # Load config
    config_manager = ConfigManager()
    config = config_manager.get_config()
    diarization_config = config.get('diarization', {})
    
    # Check config file
    config_token = diarization_config.get('hf_token', '').strip()
    print(f"1. Token in config.yaml: {'Yes' if config_token else 'No'}")
    if config_token:
        print(f"   Token value: {config_token[:10]}..." if len(config_token) > 10 else config_token)
    
    # Check environment variables
    env_vars = ['HUGGING_FACE_TOKEN', 'HF_TOKEN', 'HUGGINGFACE_TOKEN']
    for var in env_vars:
        token = os.environ.get(var, '').strip()
        print(f"2. {var}: {'Yes' if token else 'No'}")
        if token:
            print(f"   Token value: {token[:10]}..." if len(token) > 10 else token)
    
    # Test diarizer initialization
    print("\n3. Testing SpeakerDiarizer initialization...")
    try:
        diarizer = SpeakerDiarizer(config)
        print(f"   Pipeline initialized: {'Yes' if diarizer.pipeline else 'No'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Test complete")

if __name__ == "__main__":
    test_hf_token()