"""
Markdown templates module for Obsidian Scribe.

Provides customizable templates for different transcript formats and use cases.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional


class TranscriptTemplates:
    """Manages Markdown templates for transcript generation."""
    
    def __init__(self, config: Dict):
        """
        Initialize the template manager.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Template configuration
        self.markdown_config = config.get('markdown', {})
        self.template_config = self.markdown_config.get('templates', {})
        
        # Load default templates
        self._load_default_templates()
        
    def _load_default_templates(self):
        """Load default template definitions."""
        self.templates = {
            'default': self._default_template(),
            'meeting': self._meeting_template(),
            'interview': self._interview_template(),
            'lecture': self._lecture_template(),
            'podcast': self._podcast_template(),
            'simple': self._simple_template()
        }
        
    def get_template(self, template_name: str = 'default') -> Dict:
        """
        Get a specific template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary
        """
        if template_name not in self.templates:
            self.logger.warning(f"Template '{template_name}' not found, using default")
            template_name = 'default'
            
        return self.templates[template_name]
        
    def _default_template(self) -> Dict:
        """Default transcript template."""
        return {
            'name': 'default',
            'description': 'Standard transcript template',
            'front_matter': {
                'type': 'transcript',
                'template': 'default',
                'created': '{{date}}',
                'tags': ['transcript', 'audio'],
                'audio_file': '{{audio_file}}',
                'duration': '{{duration}}',
                'speakers': '{{speaker_count}}',
                'language': '{{language}}'
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': '{{title}}'
                },
                {
                    'type': 'metadata',
                    'content': '*Transcribed on {{date_long}}*'
                },
                {
                    'type': 'summary',
                    'title': 'Summary',
                    'include_stats': True
                },
                {
                    'type': 'transcript',
                    'title': 'Transcript',
                    'speaker_format': 'emoji_name_timestamp',
                    'include_timestamps': True
                },
                {
                    'type': 'footer',
                    'include_links': True,
                    'include_generator': True
                }
            ]
        }
        
    def _meeting_template(self) -> Dict:
        """Template optimized for meeting transcripts."""
        return {
            'name': 'meeting',
            'description': 'Meeting transcript with action items',
            'front_matter': {
                'type': 'meeting-transcript',
                'template': 'meeting',
                'meeting_date': '{{date}}',
                'attendees': '{{speakers}}',
                'tags': ['meeting', 'transcript'],
                'audio_file': '{{audio_file}}',
                'duration': '{{duration}}'
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': 'Meeting: {{title}}'
                },
                {
                    'type': 'metadata',
                    'content': '*Date: {{date_long}} | Duration: {{duration}}*'
                },
                {
                    'type': 'custom',
                    'title': 'Attendees',
                    'content': '{{speaker_list}}'
                },
                {
                    'type': 'custom',
                    'title': 'Action Items',
                    'content': '- [ ] Review transcript and add action items\n- [ ] Share with attendees'
                },
                {
                    'type': 'custom',
                    'title': 'Key Decisions',
                    'content': '*To be filled after review*'
                },
                {
                    'type': 'transcript',
                    'title': 'Discussion',
                    'speaker_format': 'name_only',
                    'include_timestamps': False
                },
                {
                    'type': 'custom',
                    'title': 'Next Steps',
                    'content': '*To be added*'
                }
            ]
        }
        
    def _interview_template(self) -> Dict:
        """Template for interview transcripts."""
        return {
            'name': 'interview',
            'description': 'Interview transcript with Q&A format',
            'front_matter': {
                'type': 'interview-transcript',
                'template': 'interview',
                'interview_date': '{{date}}',
                'interviewer': 'Speaker 1',
                'interviewee': 'Speaker 2',
                'tags': ['interview', 'transcript'],
                'audio_file': '{{audio_file}}',
                'duration': '{{duration}}'
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': 'Interview: {{title}}'
                },
                {
                    'type': 'metadata',
                    'content': '*Conducted on {{date_long}}*'
                },
                {
                    'type': 'custom',
                    'title': 'Participants',
                    'content': '- **Interviewer**: {{interviewer}}\n- **Interviewee**: {{interviewee}}'
                },
                {
                    'type': 'custom',
                    'title': 'Key Topics',
                    'content': '*To be added after review*'
                },
                {
                    'type': 'transcript',
                    'title': 'Interview Transcript',
                    'speaker_format': 'bold_name',
                    'include_timestamps': True,
                    'qa_format': True
                },
                {
                    'type': 'custom',
                    'title': 'Follow-up Questions',
                    'content': '*To be added*'
                }
            ]
        }
        
    def _lecture_template(self) -> Dict:
        """Template for lecture/presentation transcripts."""
        return {
            'name': 'lecture',
            'description': 'Lecture transcript with sections',
            'front_matter': {
                'type': 'lecture-transcript',
                'template': 'lecture',
                'lecture_date': '{{date}}',
                'speaker': '{{primary_speaker}}',
                'topic': '{{title}}',
                'tags': ['lecture', 'transcript', 'education'],
                'audio_file': '{{audio_file}}',
                'duration': '{{duration}}'
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': '{{title}}'
                },
                {
                    'type': 'metadata',
                    'content': '*Lecture by {{primary_speaker}} on {{date_long}}*'
                },
                {
                    'type': 'custom',
                    'title': 'Overview',
                    'content': '*Add lecture overview here*'
                },
                {
                    'type': 'custom',
                    'title': 'Key Points',
                    'content': '1. *To be added*\n2. *To be added*\n3. *To be added*'
                },
                {
                    'type': 'transcript',
                    'title': 'Full Transcript',
                    'speaker_format': 'hidden',  # Hide speaker labels for single speaker
                    'include_timestamps': True,
                    'section_breaks': True  # Add section breaks based on pauses
                },
                {
                    'type': 'custom',
                    'title': 'References',
                    'content': '*Add any references mentioned*'
                },
                {
                    'type': 'custom',
                    'title': 'Questions & Answers',
                    'content': '*If Q&A session included*'
                }
            ]
        }
        
    def _podcast_template(self) -> Dict:
        """Template for podcast transcripts."""
        return {
            'name': 'podcast',
            'description': 'Podcast transcript with episode info',
            'front_matter': {
                'type': 'podcast-transcript',
                'template': 'podcast',
                'episode_date': '{{date}}',
                'episode_number': '',
                'hosts': '{{speakers}}',
                'guests': '',
                'tags': ['podcast', 'transcript'],
                'audio_file': '{{audio_file}}',
                'duration': '{{duration}}'
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': '{{title}}'
                },
                {
                    'type': 'metadata',
                    'content': '*Episode recorded on {{date_long}} | Duration: {{duration}}*'
                },
                {
                    'type': 'custom',
                    'title': 'Episode Information',
                    'content': '- **Hosts**: {{hosts}}\n- **Guests**: {{guests}}\n- **Topics**: *To be added*'
                },
                {
                    'type': 'custom',
                    'title': 'Episode Summary',
                    'content': '*Add episode summary here*'
                },
                {
                    'type': 'custom',
                    'title': 'Timestamps',
                    'content': '- [00:00] Introduction\n- *Add more timestamps*'
                },
                {
                    'type': 'transcript',
                    'title': 'Full Transcript',
                    'speaker_format': 'emoji_name',
                    'include_timestamps': True
                },
                {
                    'type': 'custom',
                    'title': 'Links & Resources',
                    'content': '*Add any mentioned links or resources*'
                }
            ]
        }
        
    def _simple_template(self) -> Dict:
        """Minimal template for simple transcripts."""
        return {
            'name': 'simple',
            'description': 'Simple transcript without extras',
            'front_matter': {
                'title': '{{title}}',
                'date': '{{date}}',
                'tags': ['transcript']
            },
            'sections': [
                {
                    'type': 'header',
                    'level': 1,
                    'content': '{{title}}'
                },
                {
                    'type': 'transcript',
                    'speaker_format': 'name_only',
                    'include_timestamps': False
                }
            ]
        }
        
    def render_template(self, template_name: str, data: Dict) -> str:
        """
        Render a template with provided data.
        
        Args:
            template_name: Name of the template to use
            data: Data dictionary for template variables
            
        Returns:
            Rendered template string
        """
        template = self.get_template(template_name)
        
        # This is a placeholder for a full template rendering system
        # In a production system, you might use Jinja2 or similar
        self.logger.debug(f"Rendering template: {template_name}")
        
        # For now, return template structure
        # The actual rendering would be done by the MarkdownWriter
        return template
        
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates.
        
        Returns:
            List of template info dictionaries
        """
        return [
            {
                'name': name,
                'description': template.get('description', 'No description')
            }
            for name, template in self.templates.items()
        ]
        
    def add_custom_template(self, name: str, template: Dict):
        """
        Add a custom template.
        
        Args:
            name: Template name
            template: Template dictionary
        """
        if name in self.templates:
            self.logger.warning(f"Overwriting existing template: {name}")
            
        self.templates[name] = template
        self.logger.info(f"Added custom template: {name}")