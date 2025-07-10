"""
Setup script for Obsidian Scribe.

This script is used to install Obsidian Scribe as a Python package.
"""

import os
from setuptools import setup, find_packages

# Read the README file
def read_long_description():
    """Read the README file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements(filename='requirements.txt'):
    """Read requirements from file."""
    req_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Package metadata
setup(
    name='obsidian-scribe',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Automated audio transcription tool with speaker diarization for Obsidian',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/obsidian-scribe',
    license='MIT',
    
    # Package structure
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Include package data
    include_package_data=True,
    package_data={
        'obsidian_scribe': [
            'templates/*.j2',
            'templates/*.md',
        ],
    },
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.20.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
            'pre-commit>=2.20.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-autodoc-typehints>=1.19.0',
        ],
    },
    
    # Entry points
    entry_points={
        'console_scripts': [
            'obsidian-scribe=obsidian_scribe.main:main',
            'obs-scribe=obsidian_scribe.main:main',  # Short alias
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    # Keywords
    keywords='audio transcription whisper openai speech-to-text diarization obsidian',
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/obsidian-scribe/issues',
        'Source': 'https://github.com/yourusername/obsidian-scribe',
        'Documentation': 'https://obsidian-scribe.readthedocs.io',
    },
)