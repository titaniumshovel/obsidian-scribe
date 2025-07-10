"""
Markdown writer module for Obsidian Scribe.

Creates Obsidian-compatible Markdown files with YAML front matter,
formatted transcripts, and proper structure.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class MarkdownWriter:
    """Handles writing transcripts to Obsidian-compatible Markdown files."""
    
    def __init__(self, config: Dict):
        """
        Initialize the Markdown writer.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract configuration
        self.paths = config.get('paths', {})
        self.markdown_config = config.get('markdown', {})
        
        # Markdown settings
        self.include_timestamps = self.markdown_config.get('include_timestamps', True)
        self.timestamp_format = self.markdown_config.get('timestamp_format', '[%H:%M:%S]')
        self.speaker_emoji = self.markdown_config.get('speaker_emoji', '🗣')
        self.default_title = self.markdown_config.get('default_title', 'Audio Transcript')
        self.default_tags = self.markdown_config.get('tags', ['transcript', 'audio'])
        
        # Output folder
        self.transcript_folder = Path(self.paths.get('transcript_folder', './Transcripts'))
        self.transcript_folder.mkdir(parents=True, exist_ok=True)
        
    def write_transcript(self, content: str, metadata: Dict, audio_path: str) -> str:
        """
        Write transcript content to a Markdown file.
        
        Args:
            content: Formatted transcript content
            metadata: Transcript metadata
            audio_path: Path to the original audio file
            
        Returns:
            Path to the created transcript file
        """
        try:
            # Generate filename
            audio_file = Path(audio_path)
            transcript_filename = f"{audio_file.stem}_transcript.md"
            transcript_path = self.transcript_folder / transcript_filename
            
            # Create full document
            document = self._create_document(content, metadata, audio_file.name)
            
            # Write to file
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(document)
                
            self.logger.info(f"Transcript written to: {transcript_path}")
            return str(transcript_path)
            
        except Exception as e:
            self.logger.error(f"Failed to write transcript: {e}")
            raise
            
    def _create_document(self, content: str, metadata: Dict, audio_filename: str) -> str:
        """
        Create the full Markdown document with front matter.
        
        Args:
            content: Transcript content
            metadata: Metadata dictionary
            audio_filename: Name of the audio file
            
        Returns:
            Complete Markdown document
        """
        # Create YAML front matter
        front_matter = self._create_front_matter(metadata, audio_filename)
        
        # Create document sections
        sections = [
            front_matter,
            self._create_header(metadata),
            self._create_summary_section(metadata),
            content,
            self._create_footer(audio_filename)
        ]
        
        # Join sections with double newlines
        return '\n\n'.join(filter(None, sections))
        
    def _create_front_matter(self, metadata: Dict, audio_filename: str) -> str:
        """
        Create YAML front matter for Obsidian.
        
        Args:
            metadata: Metadata dictionary
            audio_filename: Name of the audio file
            
        Returns:
            YAML front matter string
        """
        # Build front matter data
        front_matter_data = {
            'title': metadata.get('title', self.default_title),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'tags': self.default_tags.copy(),
            'audio_file': audio_filename,
            'duration': self._format_duration(metadata.get('duration', 0)),
            'speakers': metadata.get('speaker_count', 0),
            'language': metadata.get('language', 'en'),
            'word_count': metadata.get('word_count', 0)
        }
        
        # Add custom tags if provided
        if 'tags' in metadata:
            front_matter_data['tags'].extend(metadata['tags'])
            
        # Add speaker list if available
        if metadata.get('speakers'):
            front_matter_data['speaker_list'] = metadata['speakers']
            
        # Convert to YAML
        yaml_content = yaml.dump(
            front_matter_data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        
        return f"---\n{yaml_content}---"
        
    def _create_header(self, metadata: Dict) -> str:
        """
        Create the document header.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Header string
        """
        title = metadata.get('title', self.default_title)
        date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        header_lines = [
            f"# {title}",
            f"*Transcribed on {date}*"
        ]
        
        return '\n'.join(header_lines)
        
    def _create_summary_section(self, metadata: Dict) -> str:
        """
        Create a summary section with key information.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Summary section string
        """
        lines = ["## Summary"]
        
        # Basic information
        duration = self._format_duration(metadata.get('duration', 0))
        lines.append(f"- **Duration**: {duration}")
        lines.append(f"- **Speakers**: {metadata.get('speaker_count', 0)}")
        lines.append(f"- **Language**: {metadata.get('language', 'en').upper()}")
        lines.append(f"- **Words**: {metadata.get('word_count', 0):,}")
        
        # Speaker breakdown if available
        if metadata.get('speaker_stats'):
            lines.append("\n### Speaker Breakdown")
            for speaker, stats in metadata['speaker_stats'].items():
                speaker_duration = self._format_duration(stats.get('duration', 0))
                segments = stats.get('segment_count', 0)
                lines.append(f"- **{speaker}**: {speaker_duration} ({segments} segments)")
                
        # Chunking information if applicable
        if metadata.get('is_chunked'):
            lines.append(f"\n*Note: This transcript was processed in {metadata.get('chunk_count', 1)} chunks due to file size.*")
            
        return '\n'.join(lines)
        
    def _create_footer(self, audio_filename: str) -> str:
        """
        Create the document footer with links and metadata.
        
        Args:
            audio_filename: Name of the audio file
            
        Returns:
            Footer string
        """
        lines = [
            "---",
            "## Links",
            f"- Audio file: [[{audio_filename}]]",
            "",
            f"*Generated by Obsidian Scribe v1.0*"
        ]
        
        return '\n'.join(lines)
        
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds == 0:
            return "Unknown"
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
            
    def create_index_file(self, transcript_files: List[str]) -> str:
        """
        Create an index file linking to all transcripts.
        
        Args:
            transcript_files: List of transcript file paths
            
        Returns:
            Path to the index file
        """
        try:
            index_path = self.transcript_folder / "Transcript_Index.md"
            
            # Create index content
            lines = [
                "# Transcript Index",
                f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
                "",
                f"Total transcripts: {len(transcript_files)}",
                "",
                "## Transcripts"
            ]
            
            # Add links to transcripts
            for transcript_path in sorted(transcript_files):
                transcript_file = Path(transcript_path)
                # Extract date from filename if possible
                lines.append(f"- [[{transcript_file.stem}]]")
                
            # Write index file
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
            self.logger.info(f"Index file created: {index_path}")
            return str(index_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create index file: {e}")
            raise
            
    def update_daily_note(self, transcript_path: str, daily_note_path: Optional[str] = None):
        """
        Add a link to the transcript in the daily note (placeholder for future enhancement).
        
        Args:
            transcript_path: Path to the transcript file
            daily_note_path: Optional path to daily note
        """
        # This is a placeholder for future Obsidian daily note integration
        self.logger.debug("Daily note integration not yet implemented")