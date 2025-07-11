#!/usr/bin/env python3
"""
Simple test to verify speaker diarization works.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_diarization():
    """Test if diarization pipeline can be loaded and used."""
    try:
        # Import pyannote
        from pyannote.audio import Pipeline
        logger.info("✅ pyannote.audio imported successfully")
        
        # Try to load the pipeline without explicit token
        logger.info("Attempting to load speaker-diarization pipeline...")
        
        # First, let's try without any token
        try:
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
            logger.info("✅ Pipeline loaded without token!")
        except Exception as e1:
            logger.warning(f"Failed without token: {e1}")
            
            # Try with empty token
            try:
                pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=True)
                logger.info("✅ Pipeline loaded with use_auth_token=True!")
            except Exception as e2:
                logger.error(f"Failed with use_auth_token=True: {e2}")
                
                # Try reading token from config
                try:
                    import yaml
                    with open('config.yaml', 'r') as f:
                        config = yaml.safe_load(f)
                        token = config.get('diarization', {}).get('hf_token', '')
                    
                    if token:
                        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)
                        logger.info("✅ Pipeline loaded with config token!")
                    else:
                        raise Exception("No token in config")
                except Exception as e3:
                    logger.error(f"Failed with config token: {e3}")
                    raise
        
        # If we got here, pipeline is loaded
        logger.info("Pipeline loaded successfully!")
        
        # Test on a dummy audio file if it exists
        test_audio = Path("audio_input/test_audio.wav")
        if test_audio.exists():
            logger.info(f"Testing diarization on {test_audio}...")
            try:
                diarization = pipeline(str(test_audio))
                
                # Count speakers
                speakers = set()
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    speakers.add(speaker)
                
                logger.info(f"✅ Diarization successful! Found {len(speakers)} speaker(s)")
                
                # Show first few segments
                logger.info("\nFirst few segments:")
                count = 0
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    logger.info(f"  {speaker}: {turn.start:.2f}s - {turn.end:.2f}s")
                    count += 1
                    if count >= 5:
                        break
                        
            except Exception as e:
                logger.error(f"Diarization failed: {e}")
        else:
            logger.info("No test audio file found. Pipeline loaded successfully though!")
            
    except ImportError:
        logger.error("❌ pyannote.audio not installed")
        logger.error("Install with: pip install pyannote.audio")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variable to disable symlink warning
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    
    logger.info("=== Testing Speaker Diarization ===")
    logger.info("Note: This test will work better if run as Administrator on Windows")
    logger.info("")
    
    test_diarization()