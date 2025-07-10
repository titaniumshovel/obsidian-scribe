# Contributing to Obsidian Scribe

Thank you for your interest in contributing to Obsidian Scribe! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Issues

1. **Check existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Complete error messages
   - Steps to reproduce
   - Expected vs actual behavior

### Suggesting Features

1. **Open a discussion** first for major features
2. **Explain the use case** and benefits
3. **Consider implementation complexity**
4. **Be open to feedback** and alternatives

### Contributing Code

#### Setup Development Environment

1. **Fork the repository**:

   ```bash
   git clone https://github.com/yourusername/obsidian-scribe.git
   cd obsidian-scribe
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:

   ```bash
   pre-commit install
   ```

#### Development Workflow

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, readable code
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**:

   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=src --cov-report=html

   # Run specific tests
   pytest tests/test_config.py
   ```

4. **Check code quality**:

   ```bash
   # Run linters
   make lint

   # Format code
   make format

   # Type checking
   mypy src
   ```

5. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR**:

   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style Guide

We follow PEP 8 with these additions:

- **Line length**: 88 characters (Black default)
- **Imports**: Sorted with `isort`
- **Docstrings**: Google style
- **Type hints**: Required for public APIs

### Code Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import numpy as np
import requests

# Local imports
from src.config import ConfigManager
from src.utils import logger
```

### Docstring Example

```python
def process_audio(file_path: Path, config: Dict[str, Any]) -> TranscriptResult:
    """
    Process an audio file and return transcript.
    
    Args:
        file_path: Path to the audio file
        config: Processing configuration dictionary
        
    Returns:
        TranscriptResult object containing transcript and metadata
        
    Raises:
        AudioProcessingError: If audio processing fails
        TranscriptionError: If transcription fails
    """
```

### Error Handling

```python
try:
    result = process_file(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise AudioProcessingError(f"Failed to process {file_path}") from e
```

## Testing Guidelines

### Test Structure

```text
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py    # Shared pytest configuration
```

### Writing Tests

```python
import pytest
from src.audio.processor import AudioProcessor

class TestAudioProcessor:
    """Test AudioProcessor functionality."""
    
    def test_process_valid_file(self, sample_audio_file, mock_config):
        """Test processing a valid audio file."""
        processor = AudioProcessor(mock_config)
        result = processor.process(sample_audio_file)
        
        assert result.status == "completed"
        assert result.transcript is not None
        
    def test_process_invalid_file(self, mock_config):
        """Test handling of invalid file."""
        processor = AudioProcessor(mock_config)
        
        with pytest.raises(AudioProcessingError):
            processor.process("nonexistent.wav")
```

### Test Coverage

- Aim for >90% code coverage
- Test edge cases and error conditions
- Include integration tests for critical paths
- Add performance tests for bottlenecks

## Documentation

### Documentation Standards

- **Clear and concise**: Avoid jargon
- **Examples**: Include practical examples
- **Up-to-date**: Update docs with code changes
- **Accessible**: Consider different skill levels

### Documentation Types

1. **Code documentation**: Docstrings and comments
2. **User documentation**: Guides and tutorials
3. **API documentation**: Reference and examples
4. **Architecture documentation**: Design decisions

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in CI/CD pipeline
4. **Documentation review** if applicable
5. **Final approval** and merge

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test package
5. Create release tag
6. Deploy to PyPI

## Development Tips

### Debugging

```python
# Use logging instead of print
logger.debug(f"Processing file: {file_path}")

# Use debugger when needed
import pdb; pdb.set_trace()

# Profile performance
from cProfile import Profile
profiler = Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()
profiler.print_stats()
```

### Performance

- Profile before optimizing
- Use caching appropriately
- Consider memory usage
- Test with large files

### Security

- Never commit secrets
- Validate all inputs
- Use secure defaults
- Follow OWASP guidelines

## Getting Help

### Resources

- **Documentation**: Read existing docs first
- **Issues**: Search closed issues
- **Discussions**: Ask questions
- **Discord/Slack**: Real-time help (if available)

### Maintainer Contact

- Create an issue for public discussions
- Email for security issues: <security@example.com>

## Recognition

Contributors are recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Obsidian Scribe! Your efforts help make this project better for everyone.
