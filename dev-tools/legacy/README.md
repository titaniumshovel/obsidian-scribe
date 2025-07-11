# Legacy Development Tools

This directory contains deprecated testing scripts from earlier development phases. These tools were used during the project restructuring but are no longer needed for normal development.

## Historical Context

These scripts were created during the transition from the monolithic `obsidian_scribe.py` structure to the modular `src/` architecture. They test various components and integration points from that development phase.

## Files

### Pipeline and Integration Tests
- **`test_pipeline.py`**: Tests the basic file watching and processing pipeline using legacy structure
- **`test_run.py`**: Basic application run test
- **`test_clear_processing.py`**: Tests processing cleanup functionality

### Component-Specific Tests  
- **`test_diarization_simple.py`**: Basic speaker diarization functionality test
- **`test_progress_tracking.py`**: Validates real-time progress tracking implementation
- **`test_file_detection.py`**: Tests file detection and monitoring

### Authentication Tests
- **`test_hf_token.py`**: Basic Hugging Face token validation (superseded by `../test_hf_diagnostic.py`)

## Status

❌ **DEPRECATED**: These scripts may not work with the current codebase structure.

⚠️ **NOT MAINTAINED**: These files are kept for historical reference only.

## Migration Path

If you need functionality from these scripts:

1. **Check current test suite**: Look in `tests/` directory for modern equivalents
2. **Use development tools**: Check `../` for updated diagnostic scripts
3. **Adapt for new structure**: Update imports to use `src/` module structure

## When to Use

- **Historical reference**: Understanding how features were originally implemented
- **Migration debugging**: If modernizing old functionality
- **Learning**: Understanding the evolution of the codebase

## Cleanup Note

These files can be safely deleted if historical reference is not needed. They are retained to understand the development progression and assist with any potential rollback scenarios.