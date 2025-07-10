"""
Pytest configuration and fixtures for Obsidian Scribe tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import yaml
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config = {
        'paths': {
            'audio_folder': str(temp_dir / 'audio'),
            'transcript_folder': str(temp_dir / 'transcripts'),
            'archive_folder': str(temp_dir / 'archive'),
            'temp_folder': str(temp_dir / 'temp'),
            'cache_folder': str(temp_dir / 'cache'),
            'state_file': str(temp_dir / 'state.db')
        },
        'watcher': {
            'file_extensions': ['.wav', '.mp3'],
            'poll_interval': 0.1,
            'ignore_patterns': ['.*', '~*'],
            'min_file_size_mb': 0.001,
            'max_file_size_mb': 100,
            'file_ready_timeout': 1.0
        },
        'processing': {
            'concurrent_files': 1,
            'retry_failed': True,
            'retry_delay': 1,
            'max_retries': 2,
            'priority_rules': {
                'size_based': True,
                'age_based': True,
                'name_patterns': []
            }
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'format': 'wav',
            'chunk_duration': 30,
            'overlap_duration': 2,
            'silence_threshold': -40,
            'min_silence_duration': 0.5
        },
        'transcription': {
            'api_key': 'test-api-key',
            'api_base': 'http://localhost:8000',
            'model': 'whisper-1',
            'language': 'en',
            'temperature': 0.0,
            'prompt': '',
            'response_format': 'verbose_json',
            'timeout': 30,
            'max_retries': 2
        },
        'diarization': {
            'enabled': True,
            'model': 'pyannote/speaker-diarization',
            'auth_token': 'test-token',
            'min_speakers': 1,
            'max_speakers': 10,
            'min_segment_duration': 1.0,
            'merge_threshold': 0.5
        },
        'output': {
            'format': 'markdown',
            'template': 'detailed',
            'include_metadata': True,
            'include_timestamps': True,
            'timestamp_format': '[{timestamp}]',
            'speaker_format': '**{speaker}:**',
            'save_intermediate': False
        },
        'archive': {
            'enabled': True,
            'compress': True,
            'compression_format': 'zip',
            'retention_days': 30,
            'include_audio': True,
            'include_intermediate': False
        },
        'cache': {
            'enabled': True,
            'memory_cache_size': 100,
            'disk_cache_size_mb': 500,
            'ttl_hours': 24,
            'cache_transcripts': True,
            'cache_diarization': True
        },
        'logging': {
            'level': 'DEBUG',
            'format': 'detailed',
            'file': str(temp_dir / 'test.log'),
            'max_size_mb': 10,
            'backup_count': 3,
            'console_colors': False
        }
    }
    
    # Create directories
    for key, path in config['paths'].items():
        if key != 'state_file':
            Path(path).mkdir(parents=True, exist_ok=True)
    
    return config


@pytest.fixture
def config_file(temp_dir, test_config):
    """Create a temporary config file."""
    config_path = temp_dir / 'config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f)
    return config_path


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing."""
    audio_dir = temp_dir / 'audio'
    audio_dir.mkdir(exist_ok=True)
    
    # Create a dummy WAV file with minimal header
    audio_file = audio_dir / 'test_audio.wav'
    
    # WAV header for 1 second of silence at 16kHz, mono, 16-bit
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x80, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size (16)
        0x01, 0x00,              # AudioFormat (PCM)
        0x01, 0x00,              # NumChannels (1)
        0x80, 0x3E, 0x00, 0x00,  # SampleRate (16000)
        0x00, 0x7D, 0x00, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x80, 0x00, 0x00   # Subchunk2Size
    ])
    
    # Write header and 1 second of silence
    with open(audio_file, 'wb') as f:
        f.write(wav_header)
        f.write(b'\x00' * 32000)  # 16000 samples * 2 bytes per sample
    
    return audio_file


@pytest.fixture
def mock_whisper_response():
    """Create a mock Whisper API response."""
    return {
        "task": "transcribe",
        "language": "english",
        "duration": 30.0,
        "segments": [
            {
                "id": 0,
                "seek": 0,
                "start": 0.0,
                "end": 5.0,
                "text": " Hello, this is a test transcription.",
                "tokens": [50364, 2425, 11, 341, 307, 257, 1500, 35839, 13, 50614],
                "temperature": 0.0,
                "avg_logprob": -0.2,
                "compression_ratio": 1.2,
                "no_speech_prob": 0.01
            },
            {
                "id": 1,
                "seek": 500,
                "start": 5.0,
                "end": 10.0,
                "text": " This is the second segment.",
                "tokens": [50614, 639, 307, 264, 1150, 9469, 13, 50864],
                "temperature": 0.0,
                "avg_logprob": -0.25,
                "compression_ratio": 1.1,
                "no_speech_prob": 0.02
            }
        ],
        "text": "Hello, this is a test transcription. This is the second segment."
    }


@pytest.fixture
def mock_diarization_response():
    """Create a mock diarization response."""
    return [
        {
            'start': 0.0,
            'end': 5.0,
            'speaker': 'SPEAKER_00',
            'confidence': 0.95
        },
        {
            'start': 5.0,
            'end': 10.0,
            'speaker': 'SPEAKER_01',
            'confidence': 0.92
        }
    ]


@pytest.fixture
def mock_config_manager(test_config):
    """Create a mock ConfigManager."""
    mock = Mock()
    mock.get_config.return_value = test_config
    mock.get.side_effect = lambda key, default=None: test_config.get(key, default)
    mock.validate.return_value = True
    return mock


@pytest.fixture
def mock_file_manager(test_config):
    """Create a mock FileManager."""
    mock = Mock()
    mock.config = test_config
    mock.ensure_directory = Mock(return_value=Path('.'))
    mock.validate_audio_file = Mock(return_value=True)
    mock.get_file_info = Mock(return_value={
        'name': 'test.wav',
        'size': 1024,
        'size_mb': 0.001,
        'extension': '.wav'
    })
    return mock


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset ConfigManager singleton
    from src.config.manager import ConfigManager
    ConfigManager._instance = None
    
    yield
    
    # Clean up after test
    ConfigManager._instance = None


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


# Environment variable fixtures
@pytest.fixture
def env_vars(monkeypatch):
    """Set up test environment variables."""
    test_env = {
        'OBSIDIAN_SCRIBE_API_KEY': 'test-api-key',
        'OBSIDIAN_SCRIBE_LOG_LEVEL': 'DEBUG',
        'OBSIDIAN_SCRIBE_AUDIO_FOLDER': '/test/audio'
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env


# Async fixtures for testing async components
@pytest.fixture
async def async_mock_processor():
    """Create an async mock processor."""
    mock = MagicMock()
    mock.process = MagicMock(return_value={'status': 'completed'})
    return mock