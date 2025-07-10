"""
Configuration manager for Obsidian Scribe.

Handles loading configuration from YAML files and environment variables,
with validation and override support.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml

from .defaults import DEFAULT_CONFIG
from .schema import ConfigSchema


class ConfigManager:
    """Manages application configuration with validation and overrides."""
    
    _instance = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        """Implement singleton pattern for configuration manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        if self._initialized:
            return
            
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._find_config_file()
        self.config: Dict[str, Any] = {}
        self.schema = ConfigSchema()
        self._load_config()
        self._initialized = True
        
    def _find_config_file(self) -> Optional[Path]:
        """
        Find the configuration file in standard locations.
        
        Returns:
            Path to config file if found, None otherwise
        """
        search_paths = [
            Path('config/config.yaml'),
            Path('config.yaml'),
            Path.home() / '.obsidian-scribe' / 'config.yaml',
            Path('/etc/obsidian-scribe/config.yaml'),
        ]
        
        for path in search_paths:
            if path.exists():
                self.logger.info(f"Found configuration file: {path}")
                return path
                
        self.logger.info("No configuration file found, using defaults")
        return None
        
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Start with default configuration
        self.config = DEFAULT_CONFIG.copy()
        
        # Load from file if available
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                    self._merge_config(self.config, file_config)
                    self.logger.info(f"Loaded configuration from: {self.config_path}")
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Validate configuration
        self.schema.validate(self.config)
        
    def _merge_config(self, base: Dict, override: Dict):
        """
        Recursively merge override configuration into base configuration.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
                
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'OBSIDIAN_AUDIO_PATH': 'paths.audio_folder',
            'OBSIDIAN_TRANSCRIPT_PATH': 'paths.transcript_folder',
            'OBSIDIAN_ARCHIVE_PATH': 'paths.archive_folder',
            'OBSIDIAN_TEMP_PATH': 'paths.temp_folder',
            'OPENAI_API_KEY': 'transcription.api_key',
            'WHISPER_API_ENDPOINT': 'transcription.api_endpoint',
            'LOG_LEVEL': 'logging.level',
            'LOG_FILE': 'logging.file',
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                self._set_nested_value(self.config, config_path, value)
                self.logger.debug(f"Applied environment override: {env_var} -> {config_path}")
                
    def _set_nested_value(self, config: Dict, path: str, value: Any):
        """
        Set a nested configuration value using dot notation.
        
        Args:
            config: Configuration dictionary
            path: Dot-separated path to the value
            value: Value to set
        """
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
        
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated path.
        
        Args:
            path: Dot-separated path to the value
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
                
        return current
        
    def set(self, path: str, value: Any):
        """
        Set a configuration value by dot-separated path.
        
        Args:
            path: Dot-separated path to the value
            value: Value to set
        """
        self._set_nested_value(self.config, path, value)
        
    def apply_overrides(self, overrides: Dict[str, Any]):
        """
        Apply configuration overrides.
        
        Args:
            overrides: Dictionary of overrides with dot-separated paths as keys
        """
        for path, value in overrides.items():
            self.set(path, value)
            
        # Re-validate configuration
        self.schema.validate(self.config)
        
    def save(self, path: Optional[Path] = None):
        """
        Save current configuration to file.
        
        Args:
            path: Path to save configuration (uses current path if not provided)
        """
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No configuration file path specified")
            
        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
        self.logger.info(f"Saved configuration to: {save_path}")
        
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        self.logger.info("Configuration reloaded")