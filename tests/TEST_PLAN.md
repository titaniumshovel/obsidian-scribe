# Obsidian Scribe Test Plan

## 1. Test Strategy and Objectives

### 1.1 Strategy Overview

The testing strategy for Obsidian Scribe follows a multi-layered approach to ensure comprehensive coverage of all components, integrations, and edge cases. The strategy emphasizes:

- **Unit Testing**: Individual component validation with mocked dependencies
- **Integration Testing**: End-to-end workflow validation with real API interactions
- **Performance Testing**: Resource usage and processing time optimization
- **Security Testing**: API key handling and data protection validation
- **Edge Case Testing**: Handling of large files, multiple speakers, and error conditions

### 1.2 Primary Objectives

1. Ensure reliable audio file processing from detection to markdown generation
2. Validate proper handling of files exceeding 25MB API limit through chunking
3. Verify speaker diarization accuracy with 1-10+ speakers
4. Confirm error recovery mechanisms with exponential backoff
5. Validate security measures for API key handling and file access
6. Ensure performance meets requirements for concurrent processing

## 2. Test Scope and Coverage Requirements

### 2.1 In Scope

- **Core Modules**: All modules in `src/` directory
  - Configuration management (`config/`)
  - File watching and event handling (`watcher/`)
  - Audio processing pipeline (`audio/`)
  - Transcript generation (`transcript/`)
  - Storage and archiving (`storage/`)
  - Utilities and helpers (`utils/`)
- **Integration Points**:
  - Obsidian Whisper plugin integration
  - OpenAI Whisper API (via custom endpoint)
  - pyannote.audio speaker diarization
  - File system operations
- **File Formats**: .wav and .mp3 audio files
- **File Sizes**: 0KB to 100MB+ files
- **Error Scenarios**: Network failures, API errors, file system issues

### 2.2 Out of Scope

- Obsidian plugin internals
- Third-party library internals (pyannote, whisper)
- Non-audio file formats
- Operating system specific behaviors (focus on cross-platform compatibility)

### 2.3 Coverage Requirements

- **Code Coverage Target**: 85% overall, 90% for critical paths
- **Branch Coverage**: 80% minimum
- **Integration Coverage**: 100% of documented workflows
- **Error Path Coverage**: 100% of defined error scenarios

## 3. Test Categories and Test Cases

### 3.1 Unit Tests

#### 3.1.1 Configuration Management

- **test_config_loading**: Validate YAML configuration loading
- **test_config_validation**: Schema validation for all config parameters
- **test_config_defaults**: Default value application
- **test_config_override**: Environment variable overrides
- **test_invalid_config**: Error handling for malformed configs

#### 3.1.2 File Watcher

- **test_file_detection**: New audio file detection
- **test_file_filtering**: Correct file type filtering (.wav, .mp3)
- **test_event_queuing**: Queue management for multiple files
- **test_watcher_lifecycle**: Start/stop/restart operations
- **test_directory_monitoring**: Multiple directory support

#### 3.1.3 Audio Processing

- **test_audio_validation**: File format and integrity checks
- **test_audio_conversion**: WAV/MP3 format handling
- **test_chunk_calculation**: Proper chunk size calculation for >25MB files
- **test_chunk_splitting**: Audio splitting with overlap
- **test_chunk_metadata**: Metadata preservation across chunks

#### 3.1.4 Speaker Diarization

- **test_single_speaker**: Single speaker detection
- **test_multiple_speakers**: 2-5 speaker scenarios
- **test_many_speakers**: 5+ speaker scenarios
- **test_speaker_labeling**: Consistent speaker ID assignment
- **test_diarization_failure**: Graceful degradation

#### 3.1.5 Transcription

- **test_api_request_format**: Request payload validation
- **test_api_response_parsing**: Response handling
- **test_retry_mechanism**: Exponential backoff (1s, 2s, 4s... up to 60s)
- **test_chunk_transcription**: Multi-chunk file handling
- **test_transcription_merging**: Chunk result combination

#### 3.1.6 Markdown Generation

- **test_markdown_formatting**: Proper markdown syntax
- **test_speaker_sections**: Speaker-based content organization
- **test_timestamp_formatting**: Time format consistency
- **test_metadata_inclusion**: File info in markdown
- **test_template_rendering**: Custom template support

#### 3.1.7 Storage Management

- **test_file_archiving**: Processed file movement
- **test_cache_operations**: Temporary file management
- **test_state_persistence**: Processing state tracking
- **test_cleanup_operations**: Resource cleanup
- **test_concurrent_access**: Thread-safe operations

### 3.2 Integration Tests

#### 3.2.1 End-to-End Workflows

- **test_simple_audio_workflow**: Single small file processing
- **test_large_file_workflow**: >25MB file with chunking
- **test_multi_speaker_workflow**: Complex diarization scenario
- **test_batch_processing**: Multiple files queued
- **test_concurrent_processing**: Parallel file handling

#### 3.2.2 API Integration

- **test_api_authentication**: API key validation
- **test_api_rate_limiting**: Rate limit handling
- **test_api_timeout**: Timeout and retry behavior
- **test_api_error_responses**: 4xx/5xx error handling
- **test_network_interruption**: Connection failure recovery

#### 3.2.3 File System Integration

- **test_cross_platform_paths**: Windows/Linux/Mac compatibility
- **test_permission_errors**: Read/write permission handling
- **test_disk_space**: Low disk space scenarios
- **test_file_locking**: Concurrent file access
- **test_symbolic_links**: Symlink handling

### 3.3 Edge Case Tests

#### 3.3.1 File Size Boundaries

- **test_empty_file**: 0KB file handling
- **test_tiny_file**: <1MB files
- **test_boundary_25mb**: Files at 25MB boundary
- **test_large_file_50mb**: 50MB file processing
- **test_huge_file_100mb**: 100MB+ streaming mode

#### 3.3.2 Audio Content Edge Cases

- **test_silence_only**: Files with only silence
- **test_noise_only**: Files with only background noise
- **test_mixed_languages**: Multi-language content
- **test_overlapping_speech**: Simultaneous speakers
- **test_corrupted_audio**: Partial file corruption

#### 3.3.3 System Resource Limits

- **test_memory_pressure**: Low memory conditions
- **test_cpu_throttling**: High CPU usage scenarios
- **test_many_concurrent_files**: 10+ simultaneous files
- **test_long_running_process**: Hours-long processing
- **test_system_shutdown**: Graceful shutdown handling

### 3.4 Performance Tests

#### 3.4.1 Processing Time

- **test_small_file_performance**: <5MB file target time
- **test_medium_file_performance**: 5-25MB file target time
- **test_large_file_performance**: >25MB file target time
- **test_throughput**: Files processed per minute
- **test_latency**: Time from detection to completion

#### 3.4.2 Resource Usage

- **test_memory_usage**: Peak memory consumption
- **test_memory_leaks**: Long-running memory stability
- **test_cpu_usage**: CPU utilization patterns
- **test_disk_io**: I/O operations efficiency
- **test_network_bandwidth**: API communication efficiency

### 3.5 Security Tests

#### 3.5.1 API Security

- **test_api_key_storage**: Secure key storage validation
- **test_api_key_exposure**: Log sanitization verification
- **test_api_key_rotation**: Key update handling
- **test_invalid_api_key**: Unauthorized access handling
- **test_api_injection**: Request parameter sanitization

#### 3.5.2 File System Security

- **test_path_traversal**: Directory traversal prevention
- **test_file_permissions**: Secure file creation
- **test_temp_file_security**: Temporary file protection
- **test_sensitive_data_handling**: PII in transcripts
- **test_log_sanitization**: Sensitive data in logs

## 4. Test Environment Setup Requirements

### 4.1 Development Environment

- **Python Version**: 3.8, 3.9, 3.10, 3.11
- **Operating Systems**: Windows 10/11, Ubuntu 20.04/22.04, macOS 12+
- **Dependencies**: All requirements.txt packages
- **Test Framework**: pytest 7.x with plugins
  - pytest-cov for coverage
  - pytest-mock for mocking
  - pytest-asyncio for async tests
  - pytest-timeout for time limits

### 4.2 Test Infrastructure

- **Mock API Server**: Local mock of custom Whisper endpoint
- **Test Audio Files**: Standardized test audio library
- **Docker Containers**: Isolated test environments
- **CI/CD Pipeline**: GitHub Actions or similar
- **Resource Monitoring**: Memory/CPU profiling tools

### 4.3 Configuration

```yaml
test_config:
  api_endpoint: "http://localhost:8080/mock/whisper"
  test_data_dir: "./tests/test_data"
  temp_dir: "./tests/temp"
  log_level: "DEBUG"
  parallel_workers: 2
  test_timeout: 300  # 5 minutes default
```

## 5. Test Data Requirements

### 5.1 Audio Test Files

- **small_single_speaker.wav**: 2MB, 1 speaker, 2 minutes
- **medium_two_speakers.mp3**: 10MB, 2 speakers, 10 minutes
- **large_multi_speaker.wav**: 30MB, 5 speakers, 30 minutes
- **huge_conference.mp3**: 75MB, 8 speakers, 1 hour
- **edge_silence.wav**: 5MB, mostly silence
- **edge_noise.mp3**: 5MB, background noise only
- **edge_corrupted.wav**: 10MB, partially corrupted

### 5.2 Configuration Test Files

- **valid_config.yaml**: Complete valid configuration
- **minimal_config.yaml**: Minimum required settings
- **invalid_schema.yaml**: Schema validation failures
- **missing_required.yaml**: Missing required fields

### 5.3 Expected Output Files

- **expected_markdown/**: Reference markdown outputs
- **expected_chunks/**: Reference audio chunks
- **expected_diarization/**: Reference speaker segments

### 5.4 Mock API Responses

- **success_response.json**: Successful transcription
- **error_rate_limit.json**: Rate limit error
- **error_invalid_audio.json**: Invalid audio error
- **partial_success.json**: Partial transcription

## 6. Test Execution Approach

### 6.1 Test Execution Phases

#### Phase 1: Unit Test Suite (Daily)

```bash
pytest tests/unit/ -v --cov=src --cov-report=html
```

#### Phase 2: Integration Tests (Daily)

```bash
pytest tests/integration/ -v --timeout=600
```

#### Phase 3: Performance Tests (Weekly)

```bash
pytest tests/performance/ -v --benchmark-only
```

#### Phase 4: Security Tests (Weekly)

```bash
pytest tests/security/ -v --security-audit
```

#### Phase 5: End-to-End Tests (Per Release)

```bash
pytest tests/e2e/ -v --e2e-full
```

### 6.2 Continuous Integration

- **Pre-commit**: Linting and unit tests
- **Pull Request**: Unit + integration tests
- **Main Branch**: Full test suite
- **Release**: Full suite + manual validation

### 6.3 Test Reporting

- **Coverage Reports**: HTML and XML formats
- **Test Results**: JUnit XML format
- **Performance Metrics**: JSON benchmark results
- **Security Scan**: SARIF format results

## 7. Success Criteria and Metrics

### 7.1 Quality Gates

- **Unit Test Pass Rate**: 100% required
- **Integration Test Pass Rate**: 95% minimum
- **Code Coverage**: 85% overall, 90% critical paths
- **Performance Regression**: <10% degradation allowed
- **Security Vulnerabilities**: Zero high/critical issues

### 7.2 Key Performance Indicators

- **Processing Speed**: <1 minute per 10MB of audio
- **Memory Usage**: <500MB for files up to 25MB
- **API Success Rate**: >99% with retry mechanism
- **Chunk Accuracy**: 100% content preservation
- **Diarization Accuracy**: >85% speaker identification

### 7.3 Reliability Metrics

- **Mean Time Between Failures**: >100 hours
- **Error Recovery Rate**: 95% automatic recovery
- **Data Loss Rate**: 0% under normal operations
- **Concurrent Processing**: 5+ files without degradation

### 7.4 User Experience Metrics

- **File Detection Latency**: <1 second
- **Processing Start Time**: <5 seconds from detection
- **Progress Visibility**: Updates every 10 seconds
- **Error Message Clarity**: 100% actionable errors

## 8. Test Maintenance and Evolution

### 8.1 Test Review Schedule

- **Weekly**: Review failing tests and flaky tests
- **Monthly**: Update test data and mock responses
- **Quarterly**: Review coverage gaps and add tests
- **Annually**: Major test refactoring and optimization

### 8.2 Test Documentation

- **Test Case Documentation**: Docstrings for all tests
- **Test Data Documentation**: README in test_data/
- **Troubleshooting Guide**: Common test failures
- **Best Practices**: Testing guidelines for contributors

### 8.3 Future Considerations

- **AI Model Updates**: Test suite for model version changes
- **New Audio Formats**: Extensible format testing
- **Scalability Testing**: Cloud deployment scenarios
- **Accessibility Testing**: Output format accessibility

---

This test plan is a living document and should be updated as the project evolves. All team members are encouraged to contribute test cases and improvements to ensure comprehensive coverage of the Obsidian Scribe audio processing pipeline.
