"""
Transcript generator module for Obsidian Scribe.

Combines speaker diarization and transcription results to create
structured transcripts with speaker identification.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .markdown_writer import MarkdownWriter
from .formatter import TranscriptFormatter


class TranscriptGenerator:
    """Generates transcripts by combining diarization and transcription results."""
    
    def __init__(self, config: Dict):
        """
        Initialize the transcript generator.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.markdown_writer = MarkdownWriter(config)
        self.formatter = TranscriptFormatter(config)
        
        # Configuration
        self.paths = config.get('paths', {})
        self.markdown_config = config.get('markdown', {})
        self.include_timestamps = self.markdown_config.get('include_timestamps', True)
        
    def generate(self, audio_path: str, diarization_result: Dict, 
                transcription_result: Dict) -> str:
        """
        Generate a transcript from diarization and transcription results.
        
        Args:
            audio_path: Path to the original audio file
            diarization_result: Speaker diarization results
            transcription_result: Transcription results
            
        Returns:
            Path to the generated transcript file
        """
        try:
            self.logger.info(f"Generating transcript for: {audio_path}")
            
            # Extract data from results
            speaker_segments = diarization_result.get('segments', [])
            transcription_segments = transcription_result.get('segments', [])
            full_text = transcription_result.get('text', '')
            
            # Align speaker segments with transcription
            aligned_segments = self._align_segments(speaker_segments, transcription_segments)
            
            # Group segments by speaker
            speaker_groups = self._group_by_speaker(aligned_segments)
            
            # Generate metadata
            metadata = self._generate_metadata(audio_path, diarization_result, transcription_result)
            
            # Format transcript content
            content = self.formatter.format_transcript(
                speaker_groups,
                metadata,
                full_text
            )
            
            # Write to file
            transcript_path = self.markdown_writer.write_transcript(
                content,
                metadata,
                audio_path
            )
            
            self.logger.info(f"Transcript generated: {transcript_path}")
            return transcript_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate transcript: {e}")
            raise
            
    def _align_segments(self, speaker_segments: List[Dict], 
                       transcription_segments: List[Dict]) -> List[Dict]:
        """
        Align speaker segments with transcription segments.
        
        Args:
            speaker_segments: List of speaker diarization segments
            transcription_segments: List of transcription segments
            
        Returns:
            List of aligned segments with both speaker and text information
        """
        aligned = []
        
        # If no speaker segments, treat as single speaker
        if not speaker_segments:
            self.logger.warning("No speaker segments found, treating as single speaker")
            for trans_seg in transcription_segments:
                aligned.append({
                    'speaker': 'SPEAKER_0',
                    'start': trans_seg.get('start', 0),
                    'end': trans_seg.get('end', 0),
                    'text': trans_seg.get('text', ''),
                    'confidence': 1.0
                })
            return aligned
            
        # Match transcription segments to speaker segments
        for trans_seg in transcription_segments:
            trans_start = trans_seg.get('start', 0)
            trans_end = trans_seg.get('end', 0)
            trans_mid = (trans_start + trans_end) / 2
            
            # Find the speaker segment that contains this transcription
            best_speaker = None
            best_overlap = 0
            
            for speaker_seg in speaker_segments:
                speaker_start = speaker_seg.get('start', 0)
                speaker_end = speaker_seg.get('end', 0)
                
                # Calculate overlap
                overlap_start = max(trans_start, speaker_start)
                overlap_end = min(trans_end, speaker_end)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                # Check if this is the best match
                if overlap_duration > best_overlap:
                    best_overlap = overlap_duration
                    best_speaker = speaker_seg.get('speaker', 'UNKNOWN')
                    
            # Create aligned segment
            aligned.append({
                'speaker': best_speaker or 'UNKNOWN',
                'start': trans_start,
                'end': trans_end,
                'text': trans_seg.get('text', '').strip(),
                'confidence': trans_seg.get('avg_logprob', 0),
                'no_speech_prob': trans_seg.get('no_speech_prob', 0)
            })
            
        return aligned
        
    def _group_by_speaker(self, segments: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group segments by speaker for organized output.
        
        Args:
            segments: List of aligned segments
            
        Returns:
            Dictionary mapping speaker IDs to their segments
        """
        groups = {}
        current_speaker = None
        current_group = []
        
        for segment in segments:
            speaker = segment['speaker']
            
            if speaker != current_speaker:
                # Save previous group
                if current_speaker and current_group:
                    if current_speaker not in groups:
                        groups[current_speaker] = []
                    groups[current_speaker].append({
                        'segments': current_group,
                        'start': current_group[0]['start'],
                        'end': current_group[-1]['end']
                    })
                    
                # Start new group
                current_speaker = speaker
                current_group = [segment]
            else:
                # Continue current group
                current_group.append(segment)
                
        # Don't forget the last group
        if current_speaker and current_group:
            if current_speaker not in groups:
                groups[current_speaker] = []
            groups[current_speaker].append({
                'segments': current_group,
                'start': current_group[0]['start'],
                'end': current_group[-1]['end']
            })
            
        return groups
        
    def _generate_metadata(self, audio_path: str, diarization_result: Dict,
                          transcription_result: Dict) -> Dict:
        """
        Generate metadata for the transcript.
        
        Args:
            audio_path: Path to the audio file
            diarization_result: Diarization results
            transcription_result: Transcription results
            
        Returns:
            Metadata dictionary
        """
        audio_file = Path(audio_path)
        
        # Calculate statistics
        speakers = diarization_result.get('speakers', [])
        segments = diarization_result.get('segments', [])
        
        # Get speaker statistics
        speaker_stats = {}
        if 'segments' in diarization_result:
            for segment in segments:
                speaker = segment.get('speaker', 'UNKNOWN')
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {
                        'duration': 0,
                        'segment_count': 0
                    }
                speaker_stats[speaker]['duration'] += segment.get('duration', 0)
                speaker_stats[speaker]['segment_count'] += 1
                
        metadata = {
            'title': f"Transcript: {audio_file.stem}",
            'audio_file': audio_file.name,
            'date': datetime.now().isoformat(),
            'duration': transcription_result.get('duration', 0),
            'language': transcription_result.get('language', 'en'),
            'speakers': speakers,
            'speaker_count': len(speakers),
            'segment_count': len(segments),
            'speaker_stats': speaker_stats,
            'word_count': len(transcription_result.get('text', '').split()),
            'is_chunked': transcription_result.get('is_chunked', False),
            'chunk_count': transcription_result.get('chunk_count', 1)
        }
        
        return metadata
        
    def generate_summary(self, transcript_path: str) -> Optional[str]:
        """
        Generate a summary of the transcript (placeholder for future enhancement).
        
        Args:
            transcript_path: Path to the transcript file
            
        Returns:
            Path to summary file, or None
        """
        # This is a placeholder for future AI-powered summarization
        self.logger.info("Summary generation not yet implemented")
        return None
        
    def export_to_format(self, transcript_path: str, format: str) -> Optional[str]:
        """
        Export transcript to different formats (placeholder for future enhancement).
        
        Args:
            transcript_path: Path to the transcript file
            format: Target format (e.g., 'pdf', 'docx', 'srt')
            
        Returns:
            Path to exported file, or None
        """
        # This is a placeholder for future export functionality
        self.logger.info(f"Export to {format} not yet implemented")
        return None