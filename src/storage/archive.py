"""
Archive management for Obsidian Scribe.

Handles archiving of processed audio files and transcripts with configurable
retention policies and compression options.
"""

import os
import shutil
import logging
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import json


class ArchiveManager:
    """Manages archiving of processed files."""
    
    def __init__(self, config: Dict, file_manager):
        """
        Initialize the archive manager.
        
        Args:
            config: Application configuration
            file_manager: FileManager instance
        """
        self.config = config
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
        
        # Archive settings
        archive_config = config.get('archive', {})
        self.archive_dir = Path(archive_config.get('directory', './archive'))
        self.compression_type = archive_config.get('compression', 'zip')
        self.retention_days = archive_config.get('retention_days', 30)
        self.group_by = archive_config.get('group_by', 'date')  # date, speaker, project
        
        # Ensure archive directory exists
        self.file_manager.ensure_directory(self.archive_dir)
        
    def archive_file(self, file_path: Union[str, Path], 
                    metadata: Optional[Dict] = None) -> Path:
        """
        Archive a single file.
        
        Args:
            file_path: Path to file to archive
            metadata: Optional metadata to store with the file
            
        Returns:
            Path to archived file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Determine archive location
        archive_subdir = self._get_archive_subdir(file_path, metadata)
        archive_dest = archive_subdir / file_path.name
        
        # Copy file to archive
        archived_path = self.file_manager.copy_file(file_path, archive_dest)
        
        # Save metadata if provided
        if metadata:
            metadata_path = archive_dest.with_suffix('.metadata.json')
            self.file_manager.save_json(metadata_path, metadata)
            
        self.logger.info(f"Archived {file_path} to {archived_path}")
        return archived_path
        
    def archive_session(self, audio_file: Union[str, Path], 
                       transcript_file: Union[str, Path],
                       additional_files: Optional[List[Path]] = None,
                       metadata: Optional[Dict] = None) -> Path:
        """
        Archive a complete transcription session.
        
        Args:
            audio_file: Path to audio file
            transcript_file: Path to transcript file
            additional_files: List of additional files to include
            metadata: Session metadata
            
        Returns:
            Path to archive directory or archive file
        """
        audio_file = Path(audio_file)
        transcript_file = Path(transcript_file)
        
        # Create session directory
        session_name = f"{audio_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_dir = self._get_archive_subdir(audio_file, metadata) / session_name
        self.file_manager.ensure_directory(session_dir)
        
        # Copy files
        files_archived = []
        
        # Archive audio file
        audio_dest = session_dir / audio_file.name
        self.file_manager.copy_file(audio_file, audio_dest)
        files_archived.append(audio_dest)
        
        # Archive transcript
        transcript_dest = session_dir / transcript_file.name
        self.file_manager.copy_file(transcript_file, transcript_dest)
        files_archived.append(transcript_dest)
        
        # Archive additional files
        if additional_files:
            for file in additional_files:
                if file.exists():
                    dest = session_dir / file.name
                    self.file_manager.copy_file(file, dest)
                    files_archived.append(dest)
                    
        # Save metadata
        session_metadata = {
            'session_name': session_name,
            'archived_at': datetime.now().isoformat(),
            'audio_file': audio_file.name,
            'transcript_file': transcript_file.name,
            'files': [str(f.relative_to(session_dir)) for f in files_archived],
            'original_metadata': metadata or {}
        }
        
        metadata_path = session_dir / 'session_metadata.json'
        self.file_manager.save_json(metadata_path, session_metadata)
        
        # Optionally compress the session
        if self.config.get('archive', {}).get('compress_sessions', True):
            archive_path = self._compress_directory(session_dir)
            # Remove uncompressed directory
            shutil.rmtree(session_dir)
            return archive_path
        else:
            return session_dir
            
    def _get_archive_subdir(self, file_path: Path, metadata: Optional[Dict] = None) -> Path:
        """
        Determine the archive subdirectory based on grouping strategy.
        
        Args:
            file_path: File being archived
            metadata: File metadata
            
        Returns:
            Path to archive subdirectory
        """
        if self.group_by == 'date':
            subdir = datetime.now().strftime('%Y/%m/%d')
        elif self.group_by == 'speaker' and metadata and 'primary_speaker' in metadata:
            speaker = metadata['primary_speaker'].replace(' ', '_')
            subdir = f"speakers/{speaker}"
        elif self.group_by == 'project' and metadata and 'project' in metadata:
            project = metadata['project'].replace(' ', '_')
            subdir = f"projects/{project}"
        else:
            # Default to year/month
            subdir = datetime.now().strftime('%Y/%m')
            
        full_path = self.archive_dir / subdir
        self.file_manager.ensure_directory(full_path)
        return full_path
        
    def _compress_directory(self, directory: Path) -> Path:
        """
        Compress a directory into an archive.
        
        Args:
            directory: Directory to compress
            
        Returns:
            Path to compressed archive
        """
        if self.compression_type == 'zip':
            archive_path = directory.with_suffix('.zip')
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in directory.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(directory.parent)
                        zf.write(file, arcname)
                        
        elif self.compression_type == 'tar':
            archive_path = directory.with_suffix('.tar.gz')
            with tarfile.open(archive_path, 'w:gz') as tf:
                tf.add(directory, arcname=directory.name)
                
        else:
            raise ValueError(f"Unsupported compression type: {self.compression_type}")
            
        self.logger.debug(f"Compressed {directory} to {archive_path}")
        return archive_path
        
    def clean_old_archives(self, dry_run: bool = False) -> List[Path]:
        """
        Clean archives older than retention period.
        
        Args:
            dry_run: If True, only report what would be deleted
            
        Returns:
            List of deleted (or would-be deleted) paths
        """
        if self.retention_days <= 0:
            return []  # No retention policy
            
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_paths = []
        
        for archive_file in self.archive_dir.rglob('*'):
            if archive_file.is_file():
                # Check file age
                mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if mtime < cutoff_date:
                    deleted_paths.append(archive_file)
                    if not dry_run:
                        try:
                            archive_file.unlink()
                            self.logger.info(f"Deleted old archive: {archive_file}")
                        except Exception as e:
                            self.logger.error(f"Error deleting {archive_file}: {e}")
                            
        # Clean empty directories
        if not dry_run:
            self._clean_empty_directories()
            
        return deleted_paths
        
    def _clean_empty_directories(self):
        """Remove empty directories in the archive."""
        for dirpath, dirnames, filenames in os.walk(self.archive_dir, topdown=False):
            if not dirnames and not filenames and dirpath != str(self.archive_dir):
                try:
                    os.rmdir(dirpath)
                    self.logger.debug(f"Removed empty directory: {dirpath}")
                except Exception as e:
                    self.logger.warning(f"Could not remove directory {dirpath}: {e}")
                    
    def search_archives(self, query: str, search_in: List[str] = None) -> List[Dict]:
        """
        Search archives for files matching query.
        
        Args:
            query: Search query (matches filename or metadata)
            search_in: List of fields to search in ['filename', 'metadata', 'content']
            
        Returns:
            List of matching archive entries
        """
        if search_in is None:
            search_in = ['filename', 'metadata']
            
        results = []
        query_lower = query.lower()
        
        for archive_file in self.archive_dir.rglob('*'):
            if archive_file.is_file():
                match_info = {'path': str(archive_file), 'matches': []}
                
                # Search in filename
                if 'filename' in search_in and query_lower in archive_file.name.lower():
                    match_info['matches'].append('filename')
                    
                # Search in metadata
                if 'metadata' in search_in:
                    metadata_files = [
                        archive_file.with_suffix('.metadata.json'),
                        archive_file.parent / 'session_metadata.json'
                    ]
                    
                    for metadata_file in metadata_files:
                        if metadata_file.exists():
                            try:
                                metadata = self.file_manager.load_json(metadata_file)
                                if self._search_in_dict(metadata, query_lower):
                                    match_info['matches'].append('metadata')
                                    match_info['metadata'] = metadata
                                    break
                            except Exception as e:
                                self.logger.warning(f"Error reading metadata {metadata_file}: {e}")
                                
                if match_info['matches']:
                    results.append(match_info)
                    
        return results
        
    def _search_in_dict(self, data: Dict, query: str) -> bool:
        """
        Recursively search for query in dictionary values.
        
        Args:
            data: Dictionary to search
            query: Query string (lowercase)
            
        Returns:
            True if query found in any value
        """
        for value in data.values():
            if isinstance(value, str) and query in value.lower():
                return True
            elif isinstance(value, dict):
                if self._search_in_dict(value, query):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and query in item.lower():
                        return True
                    elif isinstance(item, dict) and self._search_in_dict(item, query):
                        return True
                        
        return False
        
    def get_archive_stats(self) -> Dict:
        """
        Get statistics about the archive.
        
        Returns:
            Dictionary with archive statistics
        """
        total_files = 0
        total_size = 0
        file_types = {}
        oldest_file = None
        newest_file = None
        
        for archive_file in self.archive_dir.rglob('*'):
            if archive_file.is_file():
                total_files += 1
                file_size = archive_file.stat().st_size
                total_size += file_size
                
                # Track file types
                ext = archive_file.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Track oldest/newest
                mtime = archive_file.stat().st_mtime
                if oldest_file is None or mtime < oldest_file[1]:
                    oldest_file = (archive_file, mtime)
                if newest_file is None or mtime > newest_file[1]:
                    newest_file = (archive_file, mtime)
                    
        stats = {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': total_size / (1024 * 1024 * 1024),
            'file_types': file_types,
            'archive_directory': str(self.archive_dir)
        }
        
        if oldest_file:
            stats['oldest_file'] = {
                'path': str(oldest_file[0]),
                'date': datetime.fromtimestamp(oldest_file[1]).isoformat()
            }
            
        if newest_file:
            stats['newest_file'] = {
                'path': str(newest_file[0]),
                'date': datetime.fromtimestamp(newest_file[1]).isoformat()
            }
            
        return stats
        
    def restore_from_archive(self, archive_path: Union[str, Path], 
                           destination: Union[str, Path]) -> List[Path]:
        """
        Restore files from archive.
        
        Args:
            archive_path: Path to archive file or directory
            destination: Where to restore files
            
        Returns:
            List of restored file paths
        """
        archive_path = Path(archive_path)
        destination = Path(destination)
        
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
            
        self.file_manager.ensure_directory(destination)
        restored_files = []
        
        if archive_path.is_file():
            # Handle compressed archives
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(destination)
                    restored_files = [destination / name for name in zf.namelist()]
                    
            elif archive_path.suffix in ['.tar', '.gz']:
                with tarfile.open(archive_path, 'r:*') as tf:
                    tf.extractall(destination)
                    restored_files = [destination / member.name for member in tf.getmembers()]
                    
        elif archive_path.is_dir():
            # Copy directory contents
            shutil.copytree(archive_path, destination / archive_path.name)
            restored_files = list((destination / archive_path.name).rglob('*'))
            
        self.logger.info(f"Restored {len(restored_files)} files from {archive_path}")
        return restored_files