"""
Transcript generation module for Obsidian Scribe.

This module handles the generation of transcripts by combining speaker
diarization and transcription results into formatted Markdown documents.
"""

from .generator import TranscriptGenerator
from .markdown_writer import MarkdownWriter
from .formatter import TranscriptFormatter
from .templates import TranscriptTemplates

__all__ = [
    'TranscriptGenerator',
    'MarkdownWriter', 
    'TranscriptFormatter',
    'TranscriptTemplates'
]

# Module version
__version__ = '1.0.0'