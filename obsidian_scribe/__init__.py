"""
Obsidian Scribe - Advanced audio processing for Obsidian

A Python application that monitors audio files, performs speaker diarization,
transcribes speech to text, and generates formatted Markdown files for Obsidian.
"""

__version__ = "0.1.0"
__author__ = "Obsidian Scribe Team"
__license__ = "MIT"

# Import main components for easier access
from .file_watcher import FileWatcher
from .processor import AudioProcessor

__all__ = [
    "FileWatcher",
    "AudioProcessor",
    "__version__",
]