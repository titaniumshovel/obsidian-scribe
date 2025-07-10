"""
Transcript formatting module for Obsidian Scribe.

Provides utilities for formatting transcript text, handling timestamps,
and organizing speaker sections.
"""

import logging
import re
from datetime import timedelta
from typing import Dict, List, Optional, Tuple


class TranscriptFormatter:
    """Handles formatting of transcript text and segments."""
    
    def __init__(self, config: Dict):
        """
        Initialize the transcript formatter.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract configuration
        self.markdown_config = config.get('markdown', {})
        self.include_timestamps = self.markdown_config.get('include_timestamps', True)
        self.timestamp_format = self.markdown_config.get('timestamp_format', '[%H:%M:%S]')
        self.speaker_emoji = self.markdown_config.get('speaker_emoji', '🗣')
        
        # Formatting options
        self.max_line_length = 80  # For readability
        self.paragraph_break_seconds = 4.0  # Time gap for paragraph breaks
        
    def format_transcript(self, speaker_groups: Dict[str, List[Dict]], 
                         metadata: Dict, full_text: str) -> str:
        """
        Format the complete transcript with speaker sections.
        
        Args:
            speaker_groups: Dictionary mapping speakers to their segments
            metadata: Transcript metadata
            full_text: Full transcript text (fallback)
            
        Returns:
            Formatted transcript content
        """
        try:
            # If no speaker groups, format as single block
            if not speaker_groups:
                return self._format_single_speaker(full_text)
                
            # Format with speaker sections
            sections = ["## Transcript\n"]
            
            # Get all speaker turns in chronological order
            all_turns = []
            for speaker, groups in speaker_groups.items():
                for group in groups:
                    all_turns.append({
                        'speaker': speaker,
                        'start': group['start'],
                        'end': group['end'],
                        'segments': group['segments']
                    })
                    
            # Sort by start time
            all_turns.sort(key=lambda x: x['start'])
            
            # Format each turn
            for turn in all_turns:
                section = self._format_speaker_turn(turn)
                sections.append(section)
                
            return '\n\n'.join(sections)
            
        except Exception as e:
            self.logger.error(f"Error formatting transcript: {e}")
            # Fallback to simple formatting
            return self._format_single_speaker(full_text)
            
    def _format_speaker_turn(self, turn: Dict) -> str:
        """
        Format a single speaker turn.
        
        Args:
            turn: Speaker turn dictionary
            
        Returns:
            Formatted speaker section
        """
        lines = []
        
        # Create speaker header
        speaker = turn['speaker']
        timestamp = self._format_timestamp(turn['start'])
        
        if self.include_timestamps:
            header = f"### {self.speaker_emoji} {speaker} {timestamp}"
        else:
            header = f"### {self.speaker_emoji} {speaker}"
            
        lines.append(header)
        
        # Format segments
        segments = turn.get('segments', [])
        current_paragraph = []
        last_end_time = None
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
                
            # Check if we should start a new paragraph
            start_time = segment.get('start', 0)
            if (last_end_time is not None and 
                start_time - last_end_time > self.paragraph_break_seconds):
                # Add current paragraph
                if current_paragraph:
                    lines.append(self._format_paragraph(' '.join(current_paragraph)))
                    current_paragraph = []
                    
            # Add text to current paragraph
            current_paragraph.append(text)
            last_end_time = segment.get('end', start_time)
            
        # Add final paragraph
        if current_paragraph:
            lines.append(self._format_paragraph(' '.join(current_paragraph)))
            
        return '\n\n'.join(lines)
        
    def _format_paragraph(self, text: str) -> str:
        """
        Format a paragraph with proper line breaks.
        
        Args:
            text: Paragraph text
            
        Returns:
            Formatted paragraph
        """
        # Clean up the text
        text = self._clean_text(text)
        
        # Apply smart formatting
        text = self._apply_smart_formatting(text)
        
        # Wrap long lines if needed
        if len(text) > self.max_line_length * 2:
            return self._wrap_text(text, self.max_line_length)
            
        return text
        
    def _clean_text(self, text: str) -> str:
        """
        Clean up transcript text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common transcription artifacts
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1\2', text)  # Remove duplicate punctuation
        
        # Capitalize first letter after sentence end
        text = re.sub(r'([.!?])\s+([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
        
        # Ensure first letter is capitalized
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return text.strip()
        
    def _apply_smart_formatting(self, text: str) -> str:
        """
        Apply smart formatting rules to improve readability.
        
        Args:
            text: Text to format
            
        Returns:
            Formatted text
        """
        # Add proper spacing around dashes
        text = re.sub(r'\s*-\s*', ' - ', text)
        
        # Format common abbreviations
        abbreviations = {
            r'\bi\.e\.': 'i.e.',
            r'\be\.g\.': 'e.g.',
            r'\betc\.': 'etc.',
            r'\bvs\.': 'vs.',
            r'\bDr\.': 'Dr.',
            r'\bMr\.': 'Mr.',
            r'\bMs\.': 'Ms.',
            r'\bMrs\.': 'Mrs.',
        }
        
        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        # Format numbers with commas
        text = re.sub(r'\b(\d{4,})\b', lambda m: f"{int(m.group(1)):,}", text)
        
        return text
        
    def _wrap_text(self, text: str, width: int) -> str:
        """
        Wrap text to specified width.
        
        Args:
            text: Text to wrap
            width: Maximum line width
            
        Returns:
            Wrapped text
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            # Check if adding this word would exceed the width
            if current_length + word_length + len(current_line) > width:
                # Start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    # Word is too long for a single line
                    lines.append(word)
                    current_length = 0
            else:
                current_line.append(word)
                current_length += word_length
                
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines)
        
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds into timestamp string.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp
        """
        # Convert to timedelta for easy formatting
        td = timedelta(seconds=int(seconds))
        
        # Extract components
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        
        # Format according to configuration
        timestamp = self.timestamp_format
        timestamp = timestamp.replace('%H', f'{hours:02d}')
        timestamp = timestamp.replace('%M', f'{minutes:02d}')
        timestamp = timestamp.replace('%S', f'{secs:02d}')
        
        return timestamp
        
    def _format_single_speaker(self, text: str) -> str:
        """
        Format transcript with no speaker identification.
        
        Args:
            text: Full transcript text
            
        Returns:
            Formatted transcript
        """
        lines = ["## Transcript\n"]
        
        # Clean and format the text
        text = self._clean_text(text)
        text = self._apply_smart_formatting(text)
        
        # Split into paragraphs based on sentence endings
        sentences = re.split(r'([.!?]+\s+)', text)
        
        current_paragraph = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
                
            sentence = sentence.strip()
            if not sentence:
                continue
                
            current_paragraph.append(sentence)
            
            # Create paragraph breaks at natural points
            if len(' '.join(current_paragraph)) > 300:  # Approximate paragraph length
                lines.append(' '.join(current_paragraph))
                current_paragraph = []
                
        # Add final paragraph
        if current_paragraph:
            lines.append(' '.join(current_paragraph))
            
        return '\n\n'.join(lines)
        
    def format_speaker_name(self, speaker_id: str) -> str:
        """
        Format speaker ID into a readable name.
        
        Args:
            speaker_id: Raw speaker ID (e.g., 'SPEAKER_0')
            
        Returns:
            Formatted speaker name
        """
        # Extract number from speaker ID
        match = re.match(r'SPEAKER_(\d+)', speaker_id)
        if match:
            number = int(match.group(1)) + 1  # Make 1-indexed
            return f"Speaker {number}"
            
        # Return as-is if not in expected format
        return speaker_id
        
    def create_timestamp_link(self, seconds: float, text: str) -> str:
        """
        Create a clickable timestamp link (for future audio player integration).
        
        Args:
            seconds: Time in seconds
            text: Link text
            
        Returns:
            Markdown link
        """
        timestamp = self._format_timestamp(seconds)
        # This could be enhanced to link to specific audio positions
        return f"[{text}](#{int(seconds)}s)"