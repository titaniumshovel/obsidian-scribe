"""
Tests for configuration management.
"""

import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config.manager import ConfigManager
from src.config.schema import validate_config
from src.config.defaults import DEFAULT_CONFIG


class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_singleton_pattern(self):
        """Test that ConfigManager follows singleton pattern."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        manager = ConfigManager()
        config = manager.get_config()
        
        assert config is not None
        assert 'paths' in config
        assert 'watcher' in config
        assert 'processing' in config
    
    def test_load_config_from_file(self, config_file):
        """Test loading configuration from file."""
        manager = ConfigManager(config_file)
        config = manager.get_config()
        
        assert config['paths']['audio_folder'].endswith('audio')
        assert config['watcher']['poll_interval'] == 0.1
    
    def test_environment_variable_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv('OBSIDIAN_SCRIBE_WATCHER_POLL_INTERVAL', '5.0')
        monkeypatch.setenv('OBSIDIAN_SCRIBE_PATHS_AUDIO_FOLDER', '/custom/audio')
        
        manager = ConfigManager()
        config = manager.get_config()
        
        assert config['watcher']['poll_interval'] == 5.0
        assert config['paths']['audio_folder'] == '/custom/audio'
    
    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        manager = ConfigManager()
        
        # Test with dots
        value = manager.get('watcher.poll_interval')
        assert value is not None
        
        # Test with default
        value = manager.get('nonexistent.key', 'default')
        assert value == 'default'
    
    def test_set_nested_config(self):
        """Test setting nested configuration values."""
        manager = ConfigManager()
        
        manager.set('watcher.poll_interval', 10.0)
        assert manager.get('watcher.poll_interval') == 10.0
        
        # Test creating new nested keys
        manager.set('new.nested.key', 'value')
        assert manager.get('new.nested.key') == 'value'
    
    def test_apply_overrides(self):
        """Test applying configuration overrides."""
        manager = ConfigManager()
        
        overrides = {
            'watcher.poll_interval': 2.0,
            'paths.audio_folder': '/override/audio'
        }
        
        manager.apply_overrides(overrides)
        
        assert manager.get('watcher.poll_interval') == 2.0
        assert manager.get('paths.audio_folder') == '/override/audio'
    
    def test_reload_config(self, config_file, temp_dir):
        """Test reloading configuration."""
        manager = ConfigManager(config_file)
        original_value = manager.get('watcher.poll_interval')
        
        # Modify the config file
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        config['watcher']['poll_interval'] = 99.0
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Reload
        manager.reload()
        
        assert manager.get('watcher.poll_interval') == 99.0
        assert manager.get('watcher.poll_interval') != original_value
    
    def test_validate_config(self):
        """Test configuration validation."""
        manager = ConfigManager()
        assert manager.validate() is True
        
        # Test with invalid config
        manager.set('watcher.poll_interval', -1)
        assert manager.validate() is False
    
    def test_save_config(self, temp_dir):
        """Test saving configuration to file."""
        config_path = temp_dir / 'saved_config.yaml'
        manager = ConfigManager()
        
        manager.set('test.value', 'saved')
        manager.save(config_path)
        
        assert config_path.exists()
        
        # Load and verify
        with open(config_path, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['test']['value'] == 'saved'


class TestConfigSchema:
    """Test configuration schema validation."""
    
    def test_validate_valid_config(self, test_config):
        """Test validation of valid configuration."""
        errors = validate_config(test_config)
        assert len(errors) == 0
    
    def test_validate_missing_required(self):
        """Test validation with missing required fields."""
        config = {'paths': {}}  # Missing required fields
        errors = validate_config(config)
        assert len(errors) > 0
        assert any('audio_folder' in str(e) for e in errors)
    
    def test_validate_invalid_types(self, test_config):
        """Test validation with invalid types."""
        test_config['watcher']['poll_interval'] = 'not a number'
        errors = validate_config(test_config)
        assert len(errors) > 0
        assert any('poll_interval' in str(e) for e in errors)
    
    def test_validate_invalid_values(self, test_config):
        """Test validation with invalid values."""
        # Negative poll interval
        test_config['watcher']['poll_interval'] = -1
        errors = validate_config(test_config)
        assert len(errors) > 0
        
        # Invalid file extension
        test_config['watcher']['file_extensions'] = ['invalid']
        errors = validate_config(test_config)
        assert len(errors) > 0
    
    def test_validate_path_existence(self, test_config, temp_dir):
        """Test path validation."""
        # Non-existent path should be valid (will be created)
        test_config['paths']['audio_folder'] = str(temp_dir / 'nonexistent')
        errors = validate_config(test_config)
        assert len(errors) == 0
    
    def test_validate_api_configuration(self, test_config):
        """Test API configuration validation."""
        # Missing API key should be valid (can be set via env)
        test_config['transcription']['api_key'] = ''
        errors = validate_config(test_config)
        assert len(errors) == 0
        
        # Invalid URL
        test_config['transcription']['api_base'] = 'not a url'
        errors = validate_config(test_config)
        assert len(errors) > 0


class TestConfigDefaults:
    """Test default configuration values."""
    
    def test_default_config_structure(self):
        """Test that default config has all required sections."""
        required_sections = [
            'paths', 'watcher', 'processing', 'audio',
            'transcription', 'diarization', 'output',
            'archive', 'cache', 'logging'
        ]
        
        for section in required_sections:
            assert section in DEFAULT_CONFIG
    
    def test_default_paths(self):
        """Test default path configuration."""
        paths = DEFAULT_CONFIG['paths']
        assert paths['audio_folder'] == './Audio'
        assert paths['transcript_folder'] == './Transcripts'
        assert paths['archive_folder'] == './Audio/Archive'
    
    def test_default_file_extensions(self):
        """Test default file extensions."""
        extensions = DEFAULT_CONFIG['watcher']['file_extensions']
        assert '.wav' in extensions
        assert '.mp3' in extensions
        assert all(ext.startswith('.') for ext in extensions)
    
    def test_default_audio_settings(self):
        """Test default audio settings."""
        audio = DEFAULT_CONFIG['audio']
        assert audio['sample_rate'] == 16000
        assert audio['channels'] == 1
        assert audio['chunk_duration'] == 300  # 5 minutes
    
    def test_environment_variable_mapping(self):
        """Test environment variable name generation."""
        # Test nested key to env var conversion
        from src.config.manager import ConfigManager
        
        manager = ConfigManager()
        env_var = manager._get_env_var_name('watcher.poll_interval')
        assert env_var == 'OBSIDIAN_SCRIBE_WATCHER_POLL_INTERVAL'
        
        env_var = manager._get_env_var_name('paths.audio_folder')
        assert env_var == 'OBSIDIAN_SCRIBE_PATHS_AUDIO_FOLDER'


class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_full_config_lifecycle(self, temp_dir):
        """Test complete configuration lifecycle."""
        # Create config file
        config_path = temp_dir / 'test_config.yaml'
        test_config = {
            'paths': {
                'audio_folder': str(temp_dir / 'audio'),
                'transcript_folder': str(temp_dir / 'transcripts')
            },
            'watcher': {
                'poll_interval': 2.0,
                'file_extensions': ['.wav']
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Load config
        manager = ConfigManager(config_path)
        
        # Verify loaded values
        assert manager.get('paths.audio_folder') == str(temp_dir / 'audio')
        assert manager.get('watcher.poll_interval') == 2.0
        
        # Modify config
        manager.set('watcher.poll_interval', 3.0)
        manager.set('new.setting', 'value')
        
        # Save modified config
        manager.save()
        
        # Create new manager and verify persistence
        manager2 = ConfigManager(config_path)
        assert manager2.get('watcher.poll_interval') == 3.0
        assert manager2.get('new.setting') == 'value'
    
    @patch.dict(os.environ, {
        'OBSIDIAN_SCRIBE_TRANSCRIPTION_API_KEY': 'env-api-key',
        'OBSIDIAN_SCRIBE_LOGGING_LEVEL': 'WARNING'
    })
    def test_environment_override_priority(self, config_file):
        """Test that environment variables override file config."""
        manager = ConfigManager(config_file)
        
        # Environment should override file
        assert manager.get('transcription.api_key') == 'env-api-key'
        assert manager.get('logging.level') == 'WARNING'
        
        # Programmatic set should override environment
        manager.set('logging.level', 'ERROR')
        assert manager.get('logging.level') == 'ERROR'