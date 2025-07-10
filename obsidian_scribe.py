#!/usr/bin/env python3
"""
Obsidian Scribe - Advanced audio processing for Obsidian
Main entry point for the application.
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

from obsidian_scribe.file_watcher import FileWatcher
from obsidian_scribe.processor import AudioProcessor
from obsidian_scribe.utils import setup_logging, ensure_directories


class ObsidianScribe:
    """Main application class for Obsidian Scribe."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Obsidian Scribe application.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.file_watcher: Optional[FileWatcher] = None
        self.processor: Optional[AudioProcessor] = None
        self._running = False
        
    def setup(self):
        """Set up the application components."""
        self.logger.info("Setting up Obsidian Scribe...")
        
        # For now, use default configuration
        # TODO: Load configuration from YAML file
        config = {
            'paths': {
                'audio_folder': './Audio',
                'transcript_folder': './Transcripts',
                'archive_folder': './Audio/Archive',
                'temp_folder': './temp'
            },
            'watcher': {
                'file_extensions': ['.wav', '.mp3'],
                'poll_interval': 1.0,
                'ignore_patterns': ['.*', '~*']
            },
            'processing': {
                'concurrent_files': 1,
                'retry_failed': True,
                'retry_delay': 60
            }
        }
        
        # Ensure required directories exist
        ensure_directories(config['paths'])
        
        # Initialize components
        self.processor = AudioProcessor(config)
        self.file_watcher = FileWatcher(
            watch_folder=config['paths']['audio_folder'],
            processor=self.processor,
            config=config['watcher']
        )
        
        self.logger.info("Setup complete")
        
    def start(self):
        """Start the application."""
        self.logger.info("Starting Obsidian Scribe...")
        self._running = True
        
        # Start the file watcher
        self.file_watcher.start()
        
        # Start the processor
        self.processor.start()
        
        self.logger.info("Obsidian Scribe is running. Press Ctrl+C to stop.")
        
        # Main event loop
        try:
            while self._running:
                time.sleep(1)
                # TODO: Add health checks and status monitoring
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
            self.stop()
            
    def stop(self):
        """Stop the application gracefully."""
        self.logger.info("Stopping Obsidian Scribe...")
        self._running = False
        
        # Stop components
        if self.file_watcher:
            self.file_watcher.stop()
        if self.processor:
            self.processor.stop()
            
        self.logger.info("Obsidian Scribe stopped")
        
    def run(self):
        """Run the application."""
        try:
            self.setup()
            self.start()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Obsidian Scribe - Advanced audio processing for Obsidian",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  obsidian_scribe.py                    # Run with default configuration
  obsidian_scribe.py -c config.yaml     # Run with custom configuration
  obsidian_scribe.py --log-level DEBUG  # Run with debug logging
  obsidian_scribe.py --watch ./MyAudio  # Watch a specific folder
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '-w', '--watch',
        type=Path,
        help='Override the audio folder to watch'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Override the transcript output folder'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=Path,
        help='Path to log file (default: obsidian_scribe.log)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Obsidian Scribe 0.1.0'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set up logging
    log_file = args.log_file or Path('obsidian_scribe.log')
    setup_logging(
        level=getattr(logging, args.log_level),
        log_file=log_file
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Obsidian Scribe starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    # Handle command-line overrides
    if args.watch or args.output:
        logger.info("Command-line overrides detected")
        # TODO: Implement configuration override logic
    
    # Create and run the application
    app = ObsidianScribe(config_path=args.config)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    app.run()


if __name__ == '__main__':
    main()