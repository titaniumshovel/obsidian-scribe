"""
Tests for utility modules.
"""

import pytest
import logging
import time
from pathlib import Path
from unittest.mock import patch, Mock, call
from datetime import datetime, timedelta

from src.utils.logger import setup_logging, get_logger, ColoredFormatter, log_progress
from src.utils.exceptions import (
    ObsidianScribeError, ConfigurationError, FileWatcherError,
    AudioProcessingError, TranscriptionError, DiarizationError,
    handle_exception, format_exception_details
)
from src.utils.validators import (
    validate_audio_file, validate_config_value, validate_path,
    validate_url, validate_email, validate_language_code
)
from src.utils.helpers import (
    format_duration, format_timestamp, sanitize_filename,
    get_file_hash, retry_with_backoff, parse_time_string,
    generate_unique_id, truncate_text, merge_dicts,
    chunk_list, format_file_size, safe_divide, clamp
)


class TestLogger:
    """Test logging utilities."""
    
    def test_setup_logging_console(self, capsys):
        """Test basic console logging setup."""
        logger = setup_logging(level=logging.INFO)
        
        logger.info("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.err
    
    def test_setup_logging_file(self, temp_dir):
        """Test file logging setup."""
        log_file = temp_dir / "test.log"
        logger = setup_logging(
            level=logging.DEBUG,
            log_file=log_file
        )
        
        logger.debug("Debug message")
        logger.info("Info message")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Debug message" in content
        assert "Info message" in content
    
    def test_colored_formatter(self):
        """Test colored log formatting."""
        formatter = ColoredFormatter(
            '%(levelname)s - %(message)s',
            use_colors=True
        )
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        # Should contain ANSI color codes
        assert '\033[' in formatted
        assert 'Error message' in formatted
    
    def test_get_logger(self):
        """Test getting named loggers."""
        logger1 = get_logger("test.module1")
        logger2 = get_logger("test.module2")
        logger3 = get_logger("test.module1")
        
        assert logger1.name == "test.module1"
        assert logger2.name == "test.module2"
        assert logger1 is logger3  # Same logger instance
    
    def test_log_progress(self, capsys):
        """Test progress logging."""
        logger = setup_logging(level=logging.INFO)
        
        # Test percentage progress
        log_progress(logger, 50, 100, "Processing")
        captured = capsys.readouterr()
        assert "50%" in captured.err
        assert "Processing" in captured.err
        
        # Test with prefix
        log_progress(logger, 75, 100, prefix="Files: ")
        captured = capsys.readouterr()
        assert "Files:" in captured.err
        assert "75%" in captured.err


class TestExceptions:
    """Test exception handling."""
    
    def test_base_exception(self):
        """Test base ObsidianScribeError."""
        error = ObsidianScribeError(
            "Test error",
            details={'key': 'value'}
        )
        
        assert str(error) == "Test error"
        assert error.details == {'key': 'value'}
    
    def test_specific_exceptions(self):
        """Test specific exception types."""
        config_error = ConfigurationError("Invalid config")
        assert isinstance(config_error, ObsidianScribeError)
        
        watcher_error = FileWatcherError("Watch failed")
        assert isinstance(watcher_error, ObsidianScribeError)
        
        audio_error = AudioProcessingError("Processing failed")
        assert isinstance(audio_error, ObsidianScribeError)
    
    def test_exception_with_details(self):
        """Test exceptions with detailed information."""
        error = TranscriptionError(
            "API request failed",
            details={
                'status_code': 401,
                'api_response': 'Unauthorized',
                'file': 'test.wav'
            }
        )
        
        assert error.details['status_code'] == 401
        assert error.details['file'] == 'test.wav'
    
    def test_handle_exception_decorator(self):
        """Test exception handling decorator."""
        @handle_exception(default_return="default")
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "default"
        
        # Test with logger
        mock_logger = Mock()
        
        @handle_exception(logger=mock_logger, default_return=None)
        def another_failing_function():
            raise RuntimeError("Another error")
        
        result = another_failing_function()
        assert result is None
        mock_logger.error.assert_called()
    
    def test_format_exception_details(self):
        """Test exception detail formatting."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            details = format_exception_details(e)
            
            assert details['type'] == 'ValueError'
            assert details['message'] == 'Test error'
            assert 'traceback' in details
            assert 'timestamp' in details


class TestValidators:
    """Test validation functions."""
    
    def test_validate_audio_file(self, sample_audio_file):
        """Test audio file validation."""
        # Valid audio file
        assert validate_audio_file(sample_audio_file) is True
        
        # Non-existent file
        assert validate_audio_file("nonexistent.wav") is False
        
        # Invalid extension
        invalid_file = sample_audio_file.parent / "test.txt"
        invalid_file.write_text("not audio")
        assert validate_audio_file(invalid_file) is False
    
    def test_validate_config_value(self):
        """Test configuration value validation."""
        # Valid values
        assert validate_config_value('string', str) is True
        assert validate_config_value(123, int) is True
        assert validate_config_value(1.5, float) is True
        assert validate_config_value([1, 2, 3], list) is True
        
        # Invalid types
        assert validate_config_value('string', int) is False
        assert validate_config_value(123, str) is False
        
        # Range validation
        assert validate_config_value(5, int, min_value=0, max_value=10) is True
        assert validate_config_value(15, int, min_value=0, max_value=10) is False
        
        # Choices validation
        assert validate_config_value('debug', str, choices=['debug', 'info']) is True
        assert validate_config_value('invalid', str, choices=['debug', 'info']) is False
    
    def test_validate_path(self, temp_dir):
        """Test path validation."""
        # Existing directory
        assert validate_path(temp_dir, must_exist=True) is True
        
        # Non-existent path (should be valid if must_exist=False)
        assert validate_path(temp_dir / "new_dir", must_exist=False) is True
        
        # Non-existent path (invalid if must_exist=True)
        assert validate_path(temp_dir / "missing", must_exist=True) is False
        
        # File vs directory check
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        assert validate_path(test_file, is_file=True) is True
        assert validate_path(test_file, is_file=False) is False
    
    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("http://example.com") is True
        assert validate_url("https://api.example.com/v1") is True
        assert validate_url("http://localhost:8000") is True
        
        # Invalid URLs
        assert validate_url("not a url") is False
        assert validate_url("ftp://example.com") is False  # Not http/https
        assert validate_url("") is False
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
    
    def test_validate_language_code(self):
        """Test language code validation."""
        # Valid codes
        assert validate_language_code("en") is True
        assert validate_language_code("en-US") is True
        assert validate_language_code("zh-CN") is True
        
        # Invalid codes
        assert validate_language_code("english") is False
        assert validate_language_code("e") is False
        assert validate_language_code("en_US") is False  # Wrong separator


class TestHelpers:
    """Test helper functions."""
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Human format
        assert format_duration(0) == "0s"
        assert format_duration(45) == "45s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3661) == "1h 1m 1s"
        
        # HMS format
        assert format_duration(45, format='hms') == "00:45"
        assert format_duration(3661, format='hms') == "01:01:01"
        
        # MS format
        assert format_duration(65.123, format='ms') == "01:05.123"
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Unix timestamp
        ts = 1704067200  # 2024-01-01 00:00:00 UTC
        formatted = format_timestamp(ts, '%Y-%m-%d')
        assert '2024' in formatted
        
        # Datetime object
        dt = datetime(2024, 1, 1, 12, 30, 45)
        formatted = format_timestamp(dt, '%H:%M:%S')
        assert formatted == "12:30:45"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Remove invalid characters
        assert sanitize_filename('file<>:"|?*.txt') == 'file_______.txt'
        
        # Remove leading/trailing dots and spaces
        assert sanitize_filename('  .file.  ') == 'file'
        
        # Handle reserved names
        assert sanitize_filename('CON') == '_CON'
        assert sanitize_filename('con.txt') == '_con.txt'
        
        # Truncate long names
        long_name = 'a' * 300 + '.txt'
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith('.txt')
    
    def test_get_file_hash(self, temp_dir):
        """Test file hash calculation."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Calculate hashes
        sha256_hash = get_file_hash(test_file, 'sha256')
        md5_hash = get_file_hash(test_file, 'md5')
        
        assert len(sha256_hash) == 64  # SHA256 hex length
        assert len(md5_hash) == 32  # MD5 hex length
        
        # Same content should give same hash
        assert get_file_hash(test_file, 'sha256') == sha256_hash
    
    def test_retry_with_backoff(self):
        """Test retry decorator."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
        
        # Test permanent failure
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            raise RuntimeError("Permanent error")
        
        with pytest.raises(RuntimeError):
            always_fails()
    
    def test_parse_time_string(self):
        """Test time string parsing."""
        # Seconds
        assert parse_time_string("30s") == 30
        assert parse_time_string("30 seconds") == 30
        
        # Minutes
        assert parse_time_string("5m") == 300
        assert parse_time_string("5 minutes") == 300
        
        # Hours
        assert parse_time_string("2h") == 7200
        assert parse_time_string("2 hours") == 7200
        
        # Combined
        assert parse_time_string("1h 30m 45s") == 5445
        
        # HH:MM:SS format
        assert parse_time_string("01:30:45") == 5445
        assert parse_time_string("02:30") == 150
        
        # Plain number
        assert parse_time_string("123") == 123
    
    def test_generate_unique_id(self):
        """Test unique ID generation."""
        # Basic ID
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        assert id1 != id2
        assert len(id1) > 8
        
        # With prefix
        id_with_prefix = generate_unique_id(prefix="test")
        assert id_with_prefix.startswith("test_")
        
        # Custom length
        custom_id = generate_unique_id(length=16)
        parts = custom_id.split('_')
        assert len(parts[-1]) == 16
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs truncation"
        
        # Basic truncation
        truncated = truncate_text(text, 20)
        assert len(truncated) <= 20
        assert truncated.endswith("...")
        
        # Custom suffix
        truncated = truncate_text(text, 20, suffix=" [...]")
        assert truncated.endswith(" [...]")
        
        # No truncation needed
        short_text = "Short"
        assert truncate_text(short_text, 20) == short_text
    
    def test_merge_dicts(self):
        """Test dictionary merging."""
        dict1 = {'a': 1, 'b': {'c': 2}}
        dict2 = {'b': {'d': 3}, 'e': 4}
        
        # Shallow merge
        result = merge_dicts(dict1, dict2, deep=False)
        assert result == {'a': 1, 'b': {'d': 3}, 'e': 4}
        
        # Deep merge
        result = merge_dicts(dict1, dict2, deep=True)
        assert result == {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
    
    def test_chunk_list(self):
        """Test list chunking."""
        lst = list(range(10))
        
        # Chunk into groups of 3
        chunks = chunk_list(lst, 3)
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[-1] == [9]
        
        # Exact division
        chunks = chunk_list(list(range(6)), 2)
        assert len(chunks) == 3
        assert all(len(chunk) == 2 for chunk in chunks)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0.00 B"
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1024 * 1024) == "1.00 MB"
        assert format_file_size(1536 * 1024) == "1.50 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"
    
    def test_safe_divide(self):
        """Test safe division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=float('inf')) == float('inf')
    
    def test_clamp(self):
        """Test value clamping."""
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10
        assert clamp(0.5, 0.0, 1.0) == 0.5