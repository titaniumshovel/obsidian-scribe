#!/usr/bin/env python3
"""
Diagnostic script to test Obsidian Scribe setup
"""
import sys
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

print("=== Obsidian Scribe Diagnostic Test ===\n")

# 1. Check Python version
print(f"1. Python Version: {sys.version}")
if sys.version_info < (3, 8):
    print("   ❌ ERROR: Python 3.8+ required")
else:
    print("   ✅ Python version OK")

# 2. Check required dependencies
print("\n2. Checking Dependencies:")
missing_deps = []
required_deps = {
    'watchdog': 'watchdog',
    'pyannote.audio': 'pyannote',
    'pydub': 'pydub',
    'yaml': 'PyYAML',
    'openai': 'openai',
    'requests': 'requests',
    'torch': 'torch',
    'torchaudio': 'torchaudio'
}

for module, package in required_deps.items():
    try:
        __import__(module)
        print(f"   ✅ {package} installed")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        missing_deps.append(package)

# 3. Check configuration
print("\n3. Checking Configuration:")
config_path = Path("config.yaml")
if config_path.exists():
    print("   ✅ config.yaml found")
    
    # Check API key
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key_in_config = config.get('transcription', {}).get('api_key', '')
    api_key_in_env = os.environ.get('OPENAI_API_KEY', '')
    
    if api_key_in_config or api_key_in_env:
        print("   ✅ API key configured")
    else:
        print("   ❌ API key NOT configured (neither in config.yaml nor OPENAI_API_KEY env var)")
else:
    print("   ❌ config.yaml NOT found")

# 4. Check required directories
print("\n4. Checking Directories:")
if config_path.exists():
    dirs_to_check = [
        config['paths']['watch_folder'],
        config['paths']['output_folder'],
        config['paths']['temp_folder'],
        config['paths']['archive_folder'],
        config['paths']['state_folder'],
        config['paths']['cache_folder']
    ]
    
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path} exists")
        else:
            print(f"   ⚠️  {dir_path} does not exist (will be created on first run)")

# 5. Test imports from src
print("\n5. Testing Module Imports:")
sys.path.insert(0, str(Path(__file__).parent))

modules_to_test = [
    'src.config.manager',
    'src.watcher.file_watcher',
    'src.audio.processor',
    'src.transcript.generator',
    'src.utils.logger'
]

import_errors = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f"   ✅ {module} imported successfully")
    except Exception as e:
        print(f"   ❌ {module} import failed: {str(e)}")
        import_errors.append((module, str(e)))

# 6. Summary
print("\n=== DIAGNOSTIC SUMMARY ===")
issues_found = []

if missing_deps:
    issues_found.append(f"Missing dependencies: {', '.join(missing_deps)}")
    
if not (api_key_in_config or api_key_in_env):
    issues_found.append("API key not configured")
    
if import_errors:
    issues_found.append(f"Import errors in {len(import_errors)} modules")

if issues_found:
    print("\n❌ Issues Found:")
    for i, issue in enumerate(issues_found, 1):
        print(f"   {i}. {issue}")
    
    print("\n📋 Recommended Actions:")
    if missing_deps:
        print(f"   1. Install missing dependencies: pip install {' '.join(missing_deps)}")
    if not (api_key_in_config or api_key_in_env):
        print("   2. Set your API key either:")
        print("      - In config.yaml under transcription.api_key")
        print("      - As environment variable: set OPENAI_API_KEY=your-key-here")
    if import_errors:
        print("   3. Fix import errors (see details above)")
else:
    print("\n✅ All checks passed! The application should be ready to run.")
    print("\nTo run a test:")
    print("   1. Place an audio file in ./audio_input/")
    print("   2. Run: python src/main.py")