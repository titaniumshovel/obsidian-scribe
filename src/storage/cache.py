"""
Caching functionality for Obsidian Scribe.

Provides in-memory and disk-based caching for transcripts, diarization results,
and other frequently accessed data.
"""

import json
import logging
import pickle
import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable
from functools import wraps
from collections import OrderedDict
import hashlib
import threading


class CacheManager:
    """Manages caching for the application."""
    
    def __init__(self, config: Dict, file_manager):
        """
        Initialize the cache manager.
        
        Args:
            config: Application configuration
            file_manager: FileManager instance
        """
        self.config = config
        self.file_manager = file_manager
        self.logger = logging.getLogger(__name__)
        
        # Cache configuration
        cache_config = config.get('cache', {})
        self.cache_dir = Path(cache_config.get('directory', './cache'))
        self.max_memory_items = cache_config.get('max_memory_items', 100)
        self.max_memory_size_mb = cache_config.get('max_memory_size_mb', 100)
        self.ttl_seconds = cache_config.get('ttl_seconds', 3600)  # 1 hour default
        self.enable_disk_cache = cache_config.get('enable_disk_cache', True)
        
        # Ensure cache directory exists
        if self.enable_disk_cache:
            self.file_manager.ensure_directory(self.cache_dir)
            
        # In-memory cache
        self._memory_cache = OrderedDict()
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_hits': 0,
            'disk_misses': 0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a string representation of all arguments
        key_parts = []
        
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, Path):
                key_parts.append(str(arg.absolute()))
            else:
                key_parts.append(repr(arg))
                
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
            
        key_string = "|".join(key_parts)
        
        # Hash for consistent length and avoid filesystem issues
        return hashlib.sha256(key_string.encode()).hexdigest()
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                
                # Check if expired
                if time.time() - entry['timestamp'] > self.ttl_seconds:
                    del self._memory_cache[key]
                    self._cache_stats['misses'] += 1
                    return self._get_from_disk(key, default)
                    
                # Move to end (LRU)
                self._memory_cache.move_to_end(key)
                self._cache_stats['hits'] += 1
                return entry['value']
                
            # Check disk cache
            self._cache_stats['misses'] += 1
            return self._get_from_disk(key, default)
            
    def _get_from_disk(self, key: str, default: Any = None) -> Any:
        """Get value from disk cache."""
        if not self.enable_disk_cache:
            return default
            
        cache_file = self.cache_dir / f"{key}.cache"
        
        if cache_file.exists():
            try:
                # Check if expired
                mtime = cache_file.stat().st_mtime
                if time.time() - mtime > self.ttl_seconds:
                    cache_file.unlink()
                    self._cache_stats['disk_misses'] += 1
                    return default
                    
                # Load from disk
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                # Add to memory cache
                self._add_to_memory_cache(key, data)
                
                self._cache_stats['disk_hits'] += 1
                return data
                
            except Exception as e:
                self.logger.warning(f"Error loading cache file {cache_file}: {e}")
                try:
                    cache_file.unlink()
                except:
                    pass
                    
        self._cache_stats['disk_misses'] += 1
        return default
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds (overrides default)
        """
        with self._lock:
            # Add to memory cache
            self._add_to_memory_cache(key, value)
            
            # Save to disk if enabled
            if self.enable_disk_cache:
                self._save_to_disk(key, value)
                
    def _add_to_memory_cache(self, key: str, value: Any):
        """Add item to memory cache with LRU eviction."""
        # Evict if at capacity
        while len(self._memory_cache) >= self.max_memory_items:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            self._cache_stats['evictions'] += 1
            
        self._memory_cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
    def _save_to_disk(self, key: str, value: Any):
        """Save value to disk cache."""
        cache_file = self.cache_dir / f"{key}.cache"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            self.logger.warning(f"Error saving to cache file {cache_file}: {e}")
            
    def delete(self, key: str):
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
        """
        with self._lock:
            # Remove from memory
            if key in self._memory_cache:
                del self._memory_cache[key]
                
            # Remove from disk
            if self.enable_disk_cache:
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Error deleting cache file: {e}")
                        
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._memory_cache.clear()
            
            if self.enable_disk_cache:
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Error deleting cache file: {e}")
                        
        self.logger.info("Cache cleared")
        
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        
        with self._lock:
            # Clean memory cache
            expired_keys = []
            for key, entry in self._memory_cache.items():
                if current_time - entry['timestamp'] > self.ttl_seconds:
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self._memory_cache[key]
                
            # Clean disk cache
            if self.enable_disk_cache:
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        mtime = cache_file.stat().st_mtime
                        if current_time - mtime > self.ttl_seconds:
                            cache_file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Error cleaning cache file: {e}")
                        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        with self._lock:
            memory_size = sum(
                len(pickle.dumps(entry['value']))
                for entry in self._memory_cache.values()
            ) / (1024 * 1024)  # MB
            
            disk_size = 0
            disk_files = 0
            if self.enable_disk_cache:
                for cache_file in self.cache_dir.glob("*.cache"):
                    disk_size += cache_file.stat().st_size
                    disk_files += 1
                disk_size = disk_size / (1024 * 1024)  # MB
                
            total_requests = (
                self._cache_stats['hits'] + 
                self._cache_stats['misses']
            )
            
            hit_rate = (
                self._cache_stats['hits'] / total_requests * 100
                if total_requests > 0 else 0
            )
            
            return {
                'memory_items': len(self._memory_cache),
                'memory_size_mb': round(memory_size, 2),
                'disk_files': disk_files,
                'disk_size_mb': round(disk_size, 2),
                'hits': self._cache_stats['hits'],
                'misses': self._cache_stats['misses'],
                'disk_hits': self._cache_stats['disk_hits'],
                'disk_misses': self._cache_stats['disk_misses'],
                'evictions': self._cache_stats['evictions'],
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
            
    def cache_result(self, ttl: Optional[int] = None):
        """
        Decorator to cache function results.
        
        Args:
            ttl: Optional TTL in seconds
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func.__module__}.{func.__name__}:{self._generate_key(*args, **kwargs)}"
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                    
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
                
            return wrapper
        return decorator
        
    def cache_transcript(self, audio_file: Union[str, Path], 
                        transcript_data: Dict) -> str:
        """
        Cache transcript data for an audio file.
        
        Args:
            audio_file: Path to audio file
            transcript_data: Transcript data to cache
            
        Returns:
            Cache key
        """
        audio_path = Path(audio_file).absolute()
        
        # Include file modification time in key for invalidation
        mtime = audio_path.stat().st_mtime
        cache_key = self._generate_key(
            'transcript',
            str(audio_path),
            mtime
        )
        
        self.set(cache_key, transcript_data)
        return cache_key
        
    def get_transcript(self, audio_file: Union[str, Path]) -> Optional[Dict]:
        """
        Get cached transcript for an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Cached transcript data or None
        """
        audio_path = Path(audio_file).absolute()
        
        # Include file modification time in key
        try:
            mtime = audio_path.stat().st_mtime
        except:
            return None
            
        cache_key = self._generate_key(
            'transcript',
            str(audio_path),
            mtime
        )
        
        return self.get(cache_key)
        
    def cache_diarization(self, audio_file: Union[str, Path], 
                         diarization_data: Dict) -> str:
        """
        Cache diarization results for an audio file.
        
        Args:
            audio_file: Path to audio file
            diarization_data: Diarization data to cache
            
        Returns:
            Cache key
        """
        audio_path = Path(audio_file).absolute()
        
        # Include file modification time in key
        mtime = audio_path.stat().st_mtime
        cache_key = self._generate_key(
            'diarization',
            str(audio_path),
            mtime
        )
        
        self.set(cache_key, diarization_data)
        return cache_key
        
    def get_diarization(self, audio_file: Union[str, Path]) -> Optional[Dict]:
        """
        Get cached diarization for an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Cached diarization data or None
        """
        audio_path = Path(audio_file).absolute()
        
        # Include file modification time in key
        try:
            mtime = audio_path.stat().st_mtime
        except:
            return None
            
        cache_key = self._generate_key(
            'diarization',
            str(audio_path),
            mtime
        )
        
        return self.get(cache_key)