# Obsidian Scribe Implementation Plan
*Detailed technical implementation guide for next development phase*

## Overview

This document provides a detailed, code-specific implementation plan based on analysis of the current codebase. It serves as the tactical execution guide for the strategic objectives outlined in the PROJECT_ROADMAP.md.

## Current State Analysis

### ✅ **Completed Features**
- **Progress Tracking System**: Real-time diarization progress with time estimation (75s/MB CPU, 20s/MB GPU)
- **WebM Processing**: Full support for Obsidian Whisper plugin audio files
- **End-to-End Testing**: Validated with real audio files up to 32.6MB
- **Error Handling**: Robust file detection and processing error recovery

### 🔍 **Key Code Discoveries**

#### Configuration Structure
- **File**: [`config.yaml`](config.yaml:84-85)
- **Finding**: `diarization.enabled: true` exists but is ignored by processor
- **Opportunity**: Leverage existing config structure for optional diarization

#### Processing Pipeline
- **File**: [`src/audio/processor.py`](src/audio/processor.py:257)
- **Finding**: Diarization called unconditionally in `_process_file()`
- **Issue**: No respect for configuration setting

#### File Naming System
- **File**: [`src/transcript/markdown_writer.py`](src/transcript/markdown_writer.py:58)
- **Finding**: Fixed pattern `{filename}_transcript.md`
- **Limitation**: No user control or template system

#### CLI Foundation
- **File**: [`src/main.py`](src/main.py:150-201)
- **Finding**: Strong argument parsing foundation
- **Opportunity**: Easy to extend with new flags

## Phase 1: Optional Diarization Implementation

### 🎯 **Objective**
Enable users to skip speaker diarization for faster processing (reduce 75s/MB to <30s for typical files).

### 📋 **Technical Implementation**

#### 1. Update Audio Processor Logic
**File**: [`src/audio/processor.py`](src/audio/processor.py:252-257)

**Current Code** (lines 252-257):
```python
# Perform diarization with progress tracking
self.logger.info("Performing speaker diarization...")

def diarization_progress(message: str, percentage: float):
    self.logger.info(f"Diarization progress: {message} ({percentage:.0f}%)")

result.diarization_result = self.diarizer.diarize(converted_path, progress_callback=diarization_progress)
```

**Proposed Change**:
```python
# Check if diarization is enabled
diarization_enabled = self.config.get('diarization', {}).get('enabled', True)

if diarization_enabled:
    self.logger.info("Performing speaker diarization...")
    
    def diarization_progress(message: str, percentage: float):
        self.logger.info(f"Diarization progress: {message} ({percentage:.0f}%)")
    
    result.diarization_result = self.diarizer.diarize(converted_path, progress_callback=diarization_progress)
else:
    # Calculate time savings
    file_size_mb = file_info.get('size_mb', 0)
    estimated_time_saved = file_size_mb * 75  # seconds
    
    self.logger.info("Skipping speaker diarization (disabled)")
    self.logger.info(f"Estimated time saved: {estimated_time_saved:.0f}s ({estimated_time_saved/60:.1f}m)")
    result.diarization_result = None
```

#### 2. Add CLI Flag Support
**File**: [`src/main.py`](src/main.py:188-199)

**Add after line 199**:
```python
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
```

**Update config override handling** (after line 231):
```python
# Handle diarization overrides
if args.no_diarization:
    config_overrides['diarization.enabled'] = False
    logger.info("Diarization disabled via command line")
elif args.enable_diarization:
    config_overrides['diarization.enabled'] = True
    logger.info("Diarization enabled via command line")
```

#### 3. Update Transcript Generation
**File**: [`src/transcript/generator.py`](src/transcript/generator.py) (needs investigation)

**Required Changes**:
- Handle `None` diarization_result gracefully
- Generate transcript without speaker labels when diarization is disabled
- Maintain metadata accuracy

#### 4. Configuration Schema Updates
**File**: [`src/config/schema.py`](src/config/schema.py:113-149)

**Current validation is sufficient** - `diarization.enabled` boolean validation already exists.

### 🧪 **Testing Strategy**

#### Unit Tests
```python
# test_optional_diarization.py
def test_diarization_disabled_in_config():
    """Test that diarization is skipped when disabled in config."""
    
def test_diarization_cli_override():
    """Test CLI flags override config settings."""
    
def test_transcript_generation_without_diarization():
    """Test transcript generation works without speaker data."""
```

#### Integration Tests
- Process same file with/without diarization
- Verify time savings (should be 60-90% faster)
- Ensure transcript quality without speaker labels

#### Performance Benchmarks
- **Target**: <30 seconds for 1MB file without diarization
- **Baseline**: 75 seconds for 1MB file with diarization
- **Expected Improvement**: 60-75% time reduction

## Phase 2: Enhanced File Naming System

### 🎯 **Objective**
Provide users full control over output file naming with template system.

### 📋 **Technical Implementation**

#### 1. Configuration Extension
**File**: [`config.yaml`](config.yaml:108-137)

**Add to transcript section**:
```yaml
# Transcript generation configuration
transcript:
  # ... existing config ...
  
  # File naming configuration
  naming:
    # Template variables: {date}, {time}, {source_name}, {duration}, {speakers}
    template: "{date}_{time}_{source_name}_transcript"
    date_format: "%Y%m%d"
    time_format: "%H%M%S"
    include_speaker_count: false
    include_duration: false
    custom_prefix: ""
    custom_suffix: ""
    # Fallback for conflicts
    conflict_resolution: "append_number"  # append_number, timestamp, overwrite
```

#### 2. Markdown Writer Updates
**File**: [`src/transcript/markdown_writer.py`](src/transcript/markdown_writer.py:56-59)

**Replace current filename generation**:
```python
def _generate_filename(self, audio_path: str, metadata: Dict) -> str:
    """Generate filename based on template configuration."""
    audio_file = Path(audio_path)
    naming_config = self.config.get('transcript', {}).get('naming', {})
    
    # Get template
    template = naming_config.get('template', '{source_name}_transcript')
    
    # Build template variables
    now = datetime.now()
    variables = {
        'date': now.strftime(naming_config.get('date_format', '%Y%m%d')),
        'time': now.strftime(naming_config.get('time_format', '%H%M%S')),
        'source_name': audio_file.stem,
        'duration': self._format_duration_short(metadata.get('duration', 0)),
        'speakers': str(metadata.get('speaker_count', 0)),
        'language': metadata.get('language', 'en').upper()
    }
    
    # Apply template
    filename = template.format(**variables)
    
    # Add prefix/suffix
    prefix = naming_config.get('custom_prefix', '')
    suffix = naming_config.get('custom_suffix', '')
    
    if prefix:
        filename = f"{prefix}_{filename}"
    if suffix:
        filename = f"{filename}_{suffix}"
    
    # Handle conflicts
    return self._resolve_filename_conflict(f"{filename}.md")

def _resolve_filename_conflict(self, filename: str) -> str:
    """Handle filename conflicts based on configuration."""
    # Implementation for conflict resolution
```

#### 3. CLI Override Support
**File**: [`src/main.py`](src/main.py)

**Add arguments**:
```python
parser.add_argument(
    '--output-name',
    type=str,
    help='Custom name for output transcript (without extension)'
)

parser.add_argument(
    '--naming-template',
    type=str,
    help='Custom naming template (e.g., "{date}_{source_name}")'
)
```

### 🧪 **Testing Strategy**

#### Template Tests
- Default template behavior
- Custom template variables
- Prefix/suffix handling
- Conflict resolution

#### CLI Integration Tests
- Custom output names
- Template overrides
- Error handling for invalid templates

## Phase 3: User Experience Enhancements

### 📋 **Implementation Tasks**

#### 1. Enhanced Logging and Feedback
```python
# In processor.py
def _log_processing_summary(self, result: ProcessingResult, file_info: Dict):
    """Provide comprehensive processing summary."""
    self.logger.info("=" * 50)
    self.logger.info("PROCESSING COMPLETE")
    self.logger.info(f"File: {file_info['name']}")
    self.logger.info(f"Size: {file_info['size_mb']:.2f} MB")
    self.logger.info(f"Duration: {result.processing_time:.1f}s")
    
    if result.diarization_result:
        self.logger.info(f"Speakers detected: {len(result.diarization_result.get('speakers', []))}")
    else:
        self.logger.info("Diarization: Skipped")
    
    self.logger.info(f"Transcript: {result.transcript_path}")
    self.logger.info("=" * 50)
```

#### 2. Configuration Validation
**File**: [`src/config/schema.py`](src/config/schema.py)

**Add validation for naming templates**:
```python
def _validate_transcript_naming(self, naming: Dict[str, Any]):
    """Validate transcript naming configuration."""
    if 'template' in naming:
        template = naming['template']
        # Validate template variables
        valid_vars = {'date', 'time', 'source_name', 'duration', 'speakers', 'language'}
        # Implementation for template validation
```

#### 3. Documentation Updates
- Update README.md with new features
- Create usage examples
- Add troubleshooting guide

## Implementation Timeline

### Week 1: Optional Diarization
- **Day 1**: Processor logic updates and CLI flags
- **Day 2**: Transcript generation without diarization
- **Day 3**: Testing and validation
- **Day 4**: Performance benchmarking
- **Day 5**: Documentation and user testing

### Week 2: File Naming System
- **Day 1-2**: Template system implementation
- **Day 3**: CLI integration and conflict resolution
- **Day 4**: Comprehensive testing
- **Day 5**: Documentation and examples

### Week 3: Polish and Documentation
- **Day 1-2**: Enhanced logging and user feedback
- **Day 3**: Configuration validation improvements
- **Day 4**: Documentation updates
- **Day 5**: Final testing and release preparation

## Success Metrics

### Performance Targets
- **Without Diarization**: <30 seconds for 1MB file
- **With Diarization**: Maintain current 75s/MB performance
- **Time Savings**: 60-75% reduction when diarization disabled

### User Experience Targets
- **Setup Complexity**: Zero additional configuration required
- **File Naming**: 100% user control with templates
- **Error Recovery**: Clear messages for all failure modes
- **Documentation**: Complete usage examples and troubleshooting

### Technical Targets
- **Backward Compatibility**: 100% for existing configurations
- **Test Coverage**: >90% for new features
- **Configuration Validation**: Prevent all invalid configurations

## Risk Mitigation

### High Risk Items
1. **Transcript Generation Without Diarization**: Ensure quality maintained
2. **Backward Compatibility**: Existing workflows must continue working
3. **Performance Regression**: New features shouldn't slow down existing paths

### Mitigation Strategies
- Comprehensive testing with real audio files
- Feature flags for gradual rollout
- Performance benchmarking at each step
- User acceptance testing before release

## Long-term Goals

### Model Version Management (Month 4-6)

#### 🎯 **Objective**
Implement a hybrid model versioning system to address version compatibility warnings and provide users with flexibility between stability and latest features.

#### 📋 **Technical Implementation**

##### 1. Configuration Schema Enhancement
**File**: [`config.yaml`](config.yaml)

```yaml
diarization:
  enabled: true
  method: "pyannote"
  
  # Model version management
  model_version: "stable"  # Options: stable, latest, legacy, custom
  models:
    stable:
      name: "pyannote/speaker-diarization@2.1"
      min_pyannote_version: "2.1.0"
      max_pyannote_version: "2.2.0"
      torch_version: "1.13.1"
      verified: true
    latest:
      name: "pyannote/speaker-diarization-3.1"
      min_pyannote_version: "3.1.0"
      max_pyannote_version: "4.0.0"
      torch_version: "2.0.0"
      verified: false
    legacy:
      name: "pyannote/speaker-diarization"
      min_pyannote_version: "0.0.1"
      max_pyannote_version: "1.0.0"
      torch_version: "1.10.0"
      verified: true
    custom:
      name: ""  # User-specified model
      requirements_file: ""  # User-specified requirements
```

##### 2. Dynamic Model Loading System
**File**: [`src/audio/diarizer.py`](src/audio/diarizer.py)

```python
def _load_pipeline(self):
    """Load the appropriate model based on configuration."""
    model_version = self.config['diarization'].get('model_version', 'stable')
    model_config = self.config['diarization']['models'][model_version]
    
    # Check version compatibility
    if not self._check_version_compatibility(model_config):
        self.logger.warning(f"Version mismatch detected for {model_version} model")
        # Offer to switch to compatible version or continue with warnings
    
    try:
        self.pipeline = Pipeline.from_pretrained(
            model_config['name'],
            use_auth_token=self.hf_token
        )
        self.logger.info(f"Successfully loaded {model_version} model: {model_config['name']}")
    except Exception as e:
        self.logger.error(f"Failed to load {model_version} model: {e}")
        # Fallback logic
```

##### 3. Version Compatibility Checker
**New File**: `src/utils/version_checker.py`

```python
class VersionChecker:
    """Check and manage dependency version compatibility."""
    
    def check_environment(self, model_config: Dict) -> Dict[str, Any]:
        """Check if current environment matches model requirements."""
        import pyannote.audio
        import torch
        
        results = {
            'compatible': True,
            'warnings': [],
            'errors': []
        }
        
        # Check pyannote.audio version
        current_pyannote = pyannote.audio.__version__
        if not self._version_in_range(current_pyannote,
                                     model_config.get('min_pyannote_version'),
                                     model_config.get('max_pyannote_version')):
            results['warnings'].append(
                f"pyannote.audio version {current_pyannote} may not be compatible"
            )
        
        # Similar checks for torch, pytorch-lightning, etc.
        return results
```

##### 4. CLI Enhancement
**File**: [`src/main.py`](src/main.py)

```python
parser.add_argument(
    '--model-version',
    choices=['stable', 'latest', 'legacy', 'custom'],
    help='Select diarization model version (default: stable)'
)

parser.add_argument(
    '--check-compatibility',
    action='store_true',
    help='Check version compatibility and exit'
)
```

##### 5. Environment Management
**New Files**:
- `environments/stable-env.yml` - Stable version environment
- `environments/latest-env.yml` - Latest features environment
- `environments/legacy-env.yml` - Legacy compatibility environment

#### 🧪 **Testing Strategy**

1. **Compatibility Matrix Testing**
   - Test each model version with different dependency versions
   - Document which combinations work best
   - Create automated compatibility tests

2. **Performance Benchmarking**
   - Compare accuracy across model versions
   - Measure processing speed differences
   - Document trade-offs

3. **Migration Testing**
   - Test upgrading from one model version to another
   - Ensure smooth transitions
   - Provide migration guides

#### 📊 **Success Metrics**

- **Version Flexibility**: Users can choose between 3+ model versions
- **Compatibility Warnings**: Clear warnings before issues occur
- **Fallback Success**: 100% graceful fallback when models fail
- **Documentation**: Complete compatibility matrix published
- **User Satisfaction**: Reduced version-related support issues

#### 🗓️ **Implementation Timeline**

**Month 4**: Research and Design
- Survey available models and versions
- Design compatibility checking system
- Create environment specifications

**Month 5**: Implementation
- Implement dynamic model loading
- Create version compatibility checker
- Add CLI enhancements

**Month 6**: Testing and Documentation
- Comprehensive compatibility testing
- Performance benchmarking
- User documentation and guides

---

*This implementation plan serves as the detailed technical guide for executing the strategic objectives outlined in PROJECT_ROADMAP.md. It should be updated as implementation progresses and new requirements are discovered.*