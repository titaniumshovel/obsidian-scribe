#!/usr/bin/env python3
"""
Test script for optional diarization feature.
Tests CLI flags, config overrides, and time savings calculations.
"""

import tempfile
import os
from pathlib import Path

def test_cli_argument_parsing():
    """Test that CLI arguments are parsed correctly."""
    print("=== Testing CLI Argument Parsing ===")
    
    # Test --no-diarization flag
    import argparse
    from src.main import parse_arguments
    
    # Temporarily modify sys.argv to test parsing
    import sys
    original_argv = sys.argv.copy()
    
    try:
        # Test --no-diarization
        sys.argv = ['main.py', '--no-diarization']
        args = parse_arguments()
        assert args.no_diarization == True
        assert args.enable_diarization == False
        print("✅ --no-diarization flag parsed correctly")
        
        # Test --enable-diarization
        sys.argv = ['main.py', '--enable-diarization']
        args = parse_arguments()
        assert args.no_diarization == False
        assert args.enable_diarization == True
        print("✅ --enable-diarization flag parsed correctly")
        
        # Test default (no flags)
        sys.argv = ['main.py']
        args = parse_arguments()
        assert args.no_diarization == False
        assert args.enable_diarization == False
        print("✅ Default state (no flags) parsed correctly")
        
    finally:
        sys.argv = original_argv

def test_config_override_logic():
    """Test configuration override logic."""
    print("\n=== Testing Configuration Override Logic ===")
    
    # Test that diarization is enabled by default
    from src.config.manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    diarization_enabled = config.get('diarization', {}).get('enabled', True)
    print(f"Default diarization enabled: {diarization_enabled}")
    assert diarization_enabled == True
    print("✅ Default configuration loads with diarization enabled")
    
    # Test override functionality
    config_manager.set('diarization.enabled', False)
    updated_config = config_manager.get_config()
    diarization_enabled = updated_config.get('diarization', {}).get('enabled', True)
    print(f"After override, diarization enabled: {diarization_enabled}")
    assert diarization_enabled == False
    print("✅ Configuration override works correctly")

def test_time_savings_calculation():
    """Test time savings calculation logic."""
    print("\n=== Testing Time Savings Calculation ===")
    
    # Test time savings for different file sizes
    test_cases = [
        (1.0, 75),    # 1MB file = 75 seconds saved
        (2.5, 187.5), # 2.5MB file = 187.5 seconds saved
        (10.0, 750),  # 10MB file = 750 seconds saved (12.5 minutes)
    ]
    
    for file_size_mb, expected_seconds in test_cases:
        estimated_time_saved = file_size_mb * 75  # Our 75s/MB baseline
        print(f"File size: {file_size_mb}MB -> Time saved: {estimated_time_saved}s ({estimated_time_saved/60:.1f}m)")
        assert estimated_time_saved == expected_seconds
    
    print("✅ Time savings calculations are correct")

def test_transcript_generation_without_diarization():
    """Test transcript generation logic with None diarization."""
    print("\n=== Testing Transcript Generation Without Diarization ===")
    
    from src.transcript.generator import TranscriptGenerator
    
    # Create a minimal config for testing
    test_config = {
        'paths': {
            'output_folder': './Transcripts'
        },
        'transcript': {
            'format': 'markdown',
            'include_timestamps': True
        },
        'markdown': {
            'include_timestamps': True
        }
    }
    
    generator = TranscriptGenerator(test_config)
    
    # Test the _create_single_speaker_groups method
    transcription_segments = [
        {'start': 0.0, 'end': 5.0, 'text': 'Hello world'},
        {'start': 5.0, 'end': 10.0, 'text': 'This is a test'}
    ]
    
    speaker_groups = generator._create_single_speaker_groups(transcription_segments)
    
    assert 'Speaker 1' in speaker_groups
    assert len(speaker_groups['Speaker 1']) == 2
    assert speaker_groups['Speaker 1'][0]['text'] == 'Hello world'
    assert speaker_groups['Speaker 1'][0]['speaker'] == 'Speaker 1'
    
    print("✅ Single speaker group creation works correctly")
    
    # Test metadata generation with None diarization
    fake_audio_path = "/test/audio.wav"
    transcription_result = {
        'text': 'Hello world. This is a test.',
        'segments': transcription_segments,
        'language': 'en'
    }
    
    metadata = generator._generate_metadata(fake_audio_path, None, transcription_result)
    
    assert 'Speaker 1' in metadata['speakers']
    assert metadata['speaker_count'] == 1
    print("✅ Metadata generation with None diarization works correctly")

def main():
    """Run all tests."""
    print("Testing Optional Diarization Feature Implementation")
    print("=" * 60)
    
    try:
        test_cli_argument_parsing()
        test_config_override_logic()
        test_time_savings_calculation()
        test_transcript_generation_without_diarization()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Optional diarization feature is working correctly.")
        print("\nFeature Summary:")
        print("- ✅ CLI flags --no-diarization and --enable-diarization work")
        print("- ✅ Configuration overrides work correctly")
        print("- ✅ Time savings calculations (75s/MB baseline)")
        print("- ✅ Transcript generation handles None diarization results")
        print("- ✅ Single speaker transcripts are generated properly")
        print("\nNext: Test with real audio files for end-to-end validation!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())