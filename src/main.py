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

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports during development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.watcher.file_watcher import FileWatcher
from src.audio.processor import AudioProcessor
from src.utils.logger import setup_logging
from src.config.manager import ConfigManager
from src.storage.file_manager import FileManager


class ObsidianScribe:
    """Main application class for Obsidian Scribe."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Obsidian Scribe application.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.logger = logging.getLogger(__name__)
        self.file_watcher: Optional[FileWatcher] = None
        self.processor: Optional[AudioProcessor] = None
        self.file_manager: Optional[FileManager] = None
        self._running = False
        
    def setup(self):
        """Set up the application components."""
        self.logger.info("Setting up Obsidian Scribe...")
        
        # Initialize file manager
        self.file_manager = FileManager(self.config)
        
        # Ensure required directories exist
        for path_key, path_value in self.config['paths'].items():
            if path_value:
                self.file_manager.ensure_directory(path_value)
        
        # Initialize components
        self.processor = AudioProcessor(self.config)
        
        # Prepare watcher config with audio formats
        watcher_config = self.config['watcher'].copy()
        watcher_config['file_extensions'] = self.config['audio']['formats']
        
        self.file_watcher = FileWatcher(
            watch_folder=self.config['paths']['watch_folder'],
            processor=self.processor,
            config=watcher_config
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
        
        # Main event loop with status monitoring
        last_status_time = time.time()
        status_interval = 30  # Show status every 30 seconds
        
        try:
            while self._running:
                time.sleep(1)
                
                # Show periodic status updates
                current_time = time.time()
                if current_time - last_status_time >= status_interval:
                    self._show_status()
                    last_status_time = current_time
                    
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
        
    def _show_status(self):
        """Show current application status."""
        # Get queue sizes
        watcher_queue = self.file_watcher.get_queue_size() if self.file_watcher else 0
        processor_queue = self.processor.get_queue_size() if self.processor else 0
        
        # Get processor stats
        processor_stats = self.processor.get_stats() if self.processor else {}
        
        # Log status
        self.logger.info("=" * 50)
        self.logger.info("STATUS UPDATE:")
        self.logger.info(f"  Watching: {self.config['paths']['watch_folder']}")
        self.logger.info(f"  Watcher queue: {watcher_queue} files")
        self.logger.info(f"  Processor queue: {processor_queue} files")
        self.logger.info(f"  Files processed: {processor_stats.get('processed', 0)}")
        self.logger.info(f"  Files failed: {processor_stats.get('failed', 0)}")
        self.logger.info(f"  Total processing time: {processor_stats.get('total_time', 0):.1f}s")
        self.logger.info("  System is running normally...")
        self.logger.info("=" * 50)
        
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
  python -m src.main                    # Run with default configuration
  python -m src.main -c config.yaml     # Run with custom configuration
  python -m src.main --log-level DEBUG  # Run with debug logging
  python -m src.main --watch ./MyAudio  # Watch a specific folder
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
    
    parser.add_argument(
        '--no-diarization',
        action='store_true',
        help='Skip speaker diarization for faster processing'
    )
    
    parser.add_argument(
        '--enable-diarization',
        action='store_true',
        help='Force enable speaker diarization (overrides config)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set up logging
    log_config = {
        'logging': {
            'console_level': args.log_level,
            'file_level': 'DEBUG',
            'log_dir': './logs',
            'use_colors': True
        }
    }
    setup_logging(log_config)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Obsidian Scribe starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    # Handle command-line overrides
    config_overrides = {}
    if args.watch:
        config_overrides['paths.audio_folder'] = str(args.watch)
    if args.output:
        config_overrides['paths.transcript_folder'] = str(args.output)
    
    # Handle diarization overrides
    if args.no_diarization:
        config_overrides['diarization.enabled'] = False
        logger.info("Diarization disabled via command line")
    elif args.enable_diarization:
        config_overrides['diarization.enabled'] = True
        logger.info("Diarization enabled via command line")
    
    # Create and run the application
    app = ObsidianScribe(config_path=args.config)
    
    # Apply overrides if any
    if config_overrides:
        logger.info(f"Applying command-line overrides: {config_overrides}")
        app.config_manager.apply_overrides(config_overrides)
    
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