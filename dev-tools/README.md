# Development Tools

This directory contains development and diagnostic tools for Obsidian Scribe.

## Current Tools

### Diagnostic Scripts

#### `test_diagnostic.py`
**Purpose**: System diagnostic script to validate Obsidian Scribe setup
**Usage**: 
```bash
python dev-tools/test_diagnostic.py
```
**What it checks**:
- Python version compatibility
- Required dependencies
- Configuration file validity
- Environment variables
- File permissions

#### `test_hf_diagnostic.py`
**Purpose**: Hugging Face authentication and model access diagnostic
**Usage**:
```bash
python dev-tools/test_hf_diagnostic.py
```
**What it checks**:
- Hugging Face token validity
- Model access permissions
- pyannote.audio model availability
- Authentication flow

#### `test_token_debug.py`
**Purpose**: Token validation and debugging script
**Usage**:
```bash
python dev-tools/test_token_debug.py
```
**What it checks**:
- API token format validation
- Token expiration
- Access permissions
- Token scope validation

### Feature Validation

#### `test_optional_diarization.py`
**Purpose**: Validates the optional diarization feature implementation
**Usage**:
```bash
source venv/bin/activate
python dev-tools/test_optional_diarization.py
```
**What it tests**:
- CLI argument parsing (`--no-diarization`, `--enable-diarization`)
- Configuration override logic
- Time savings calculations (75s/MB baseline)
- Transcript generation without diarization
- Single speaker transcript format

**Test Results**: All tests should pass ✅

## Legacy Tools

See `legacy/README.md` for information about deprecated testing scripts.

## Usage Guidelines

1. **Run diagnostics first** when setting up a new environment
2. **Use feature validation** after implementing new features
3. **Keep tools updated** as the main codebase evolves
4. **Document new tools** added to this directory

## Environment Requirements

Most tools require the virtual environment to be activated:
```bash
source venv/bin/activate
```

Some diagnostic tools can run without dependencies to help with initial setup validation.