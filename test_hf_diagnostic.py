#!/usr/bin/env python3
"""
Diagnostic script to test Hugging Face token and pyannote model access.
"""

import os
import sys
import requests
from pathlib import Path

def test_hf_token():
    """Test if Hugging Face token is valid and has proper permissions."""
    print("=== Hugging Face Token Diagnostic ===\n")
    
    # Check for token in environment and config
    token_sources = []
    
    # Check environment variables
    for env_var in ['HUGGING_FACE_TOKEN', 'HF_TOKEN', 'HUGGINGFACE_TOKEN']:
        token = os.environ.get(env_var, '').strip()
        if token:
            token_sources.append((env_var, token))
    
    # Check config file
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            config_token = config.get('diarization', {}).get('hf_token', '').strip()
            if config_token:
                token_sources.append(('config.yaml', config_token))
    except Exception as e:
        print(f"Could not read config.yaml: {e}")
    
    if not token_sources:
        print("❌ No Hugging Face token found!")
        print("   Please set HUGGING_FACE_TOKEN environment variable or add to config.yaml")
        return False
    
    print(f"✅ Found {len(token_sources)} token source(s):")
    for source, token in token_sources:
        print(f"   - {source}: {token[:10]}...")
    
    # Test the first token
    source, token = token_sources[0]
    print(f"\nTesting token from {source}...")
    
    # Test token validity
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test basic token validity
    print("\n1. Testing token validity...")
    try:
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ Token is valid! User: {user_info.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Token validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to validate token: {e}")
        return False
    
    # 2. Test access to pyannote models
    models_to_check = [
        ("pyannote/speaker-diarization", "https://huggingface.co/api/models/pyannote/speaker-diarization"),
        ("pyannote/segmentation", "https://huggingface.co/api/models/pyannote/segmentation")
    ]
    
    all_models_accessible = True
    
    for model_name, model_url in models_to_check:
        print(f"\n2. Testing access to {model_name}...")
        try:
            response = requests.get(model_url, headers=headers, timeout=10)
            if response.status_code == 200:
                model_info = response.json()
                if model_info.get('gated', False):
                    print(f"   ⚠️  Model is gated (requires accepting conditions)")
                    
                    # Check if user has access
                    if 'gated' in model_info and model_info['gated'] == 'auto':
                        print(f"   ✅ You have access to {model_name}")
                    else:
                        print(f"   ❌ You need to accept the model conditions at:")
                        print(f"      https://hf.co/{model_name}")
                        all_models_accessible = False
                else:
                    print(f"   ✅ {model_name} is accessible")
            else:
                print(f"   ❌ Cannot access {model_name}: {response.status_code}")
                all_models_accessible = False
        except Exception as e:
            print(f"   ❌ Failed to check {model_name} access: {e}")
            all_models_accessible = False
    
    if not all_models_accessible:
        return False
    
    # 3. Test model file download for both models
    print("\n3. Testing model file downloads...")
    test_files = [
        ("pyannote/speaker-diarization", "https://huggingface.co/pyannote/speaker-diarization/resolve/main/config.yaml"),
        ("pyannote/segmentation", "https://huggingface.co/pyannote/segmentation/resolve/main/config.yaml")
    ]
    
    for model_name, test_file_url in test_files:
        print(f"   Testing {model_name}...")
        try:
            response = requests.head(test_file_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Can download {model_name} files")
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed for {model_name} - invalid token")
                return False
            elif response.status_code == 403:
                print(f"   ❌ Access denied for {model_name} - you need to accept model conditions at:")
                print(f"      https://hf.co/{model_name}")
                return False
            else:
                print(f"   ❌ Cannot download {model_name} files: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Failed to test {model_name} file download: {e}")
            return False
    
    # 4. Check cache directory
    print("\n4. Checking cache directory...")
    try:
        import huggingface_hub
        cache_dir = Path(huggingface_hub.constants.HUGGINGFACE_HUB_CACHE)
        print(f"   Cache directory: {cache_dir}")
        if cache_dir.exists():
            print(f"   ✅ Cache directory exists")
            # Check for pyannote models in cache
            pyannote_models = list(cache_dir.glob("**/pyannote*"))
            if pyannote_models:
                print(f"   ✅ Found {len(pyannote_models)} pyannote model(s) in cache")
            else:
                print("   ℹ️  No pyannote models in cache (will download on first use)")
        else:
            print("   ⚠️  Cache directory doesn't exist (will be created on first use)")
    except Exception as e:
        print(f"   ❌ Failed to check cache: {e}")
    
    print("\n" + "="*50)
    print("✅ All checks passed! Your Hugging Face token should work.")
    print("\nIf you still have issues, make sure you:")
    print("1. Have accepted the conditions for BOTH models:")
    print("   - https://hf.co/pyannote/speaker-diarization")
    print("   - https://hf.co/pyannote/segmentation")
    print("2. Have a stable internet connection")
    print("3. Are not behind a restrictive firewall/proxy")
    
    return True

def test_pyannote_import():
    """Test if pyannote.audio can be imported."""
    print("\n=== Testing pyannote.audio Import ===\n")
    try:
        import pyannote.audio
        print("✅ pyannote.audio imported successfully")
        print(f"   Version: {pyannote.audio.__version__}")
        
        # Try importing Pipeline
        from pyannote.audio import Pipeline
        print("✅ Pipeline imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import pyannote.audio: {e}")
        print("\nTry installing with: pip install pyannote.audio")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("Obsidian Scribe - Hugging Face Diagnostic Tool")
    print("=" * 50)
    
    # Test pyannote import
    if not test_pyannote_import():
        sys.exit(1)
    
    # Test HF token
    if not test_hf_token():
        print("\n❌ Diagnostic failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ All diagnostics passed!")

if __name__ == "__main__":
    main()