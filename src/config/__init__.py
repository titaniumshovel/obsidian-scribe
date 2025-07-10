"""Configuration management module for Obsidian Scribe."""

from .manager import ConfigManager
from .schema import ConfigSchema
from .defaults import DEFAULT_CONFIG

__all__ = ['ConfigManager', 'ConfigSchema', 'DEFAULT_CONFIG']