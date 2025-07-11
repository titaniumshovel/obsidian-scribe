#!/usr/bin/env python3
"""
Debug script to test Hugging Face token format and authentication.
"""

import os
import sys
import yaml
import requests

def debug_token():
    """Debug token issues with detailed output."""
    print("=== Hugging Face Token Debug ===\n")
    
    # Check for tokens
    tokens = []
    
    # Check config.yaml
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            config_token = config.get('diarization', {}).get('hf_token', '').strip()
            if config_token:
                tokens.append(('config.yaml', config_token))
    except Exception as e:
        print(f"Error reading config.yaml: {e}")
    
    # Check environment variables
    for env_var in ['HUGGING_FACE_TOKEN', 'HF_TOKEN', 'HUGGINGFACE_TOKEN']:
        env_token = os.environ.get(env_var, '').strip()
        if env_token:
            tokens.append((env_var, env_token))
    
    if not tokens:
        print("❌ No tokens found!")
        return
    
    print(f"Found {len(tokens)} token(s):\n")
    
    for source, token in tokens:
        print(f"Source: {source}")
        print(f"Token preview: {token[:10]}...")
        print(f"Token length: {len(token)} characters")
        
        # Check token format
        if not token.startswith('hf_'):
            print("⚠️  Warning: Token should start with 'hf_'")
        
        # Test the token
        print("\nTesting token authentication...")
        
        # Method 1: Direct API test
        print("1. Testing with whoami endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(
                "https://huggingface.co/api/whoami",
                headers=headers,
                timeout=10
            )
            print(f"   Status code: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token is valid!")
                print(f"   User: {data.get('name', 'Unknown')}")
                print(f"   Type: {data.get('type', 'Unknown')}")
            else:
                print(f"   ❌ Authentication failed")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        # Method 2: Test with different auth format
        print("\n2. Testing alternative auth format...")
        alt_headers = {"Authorization": token}  # Without "Bearer"
        try:
            response = requests.get(
                "https://huggingface.co/api/whoami",
                headers=alt_headers,
                timeout=10
            )
            if response.status_code == 200:
                print("   ✅ Works without 'Bearer' prefix")
            else:
                print(f"   ❌ Also fails: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        # Method 3: Test as query parameter
        print("\n3. Testing as query parameter...")
        try:
            response = requests.get(
                f"https://huggingface.co/api/whoami?token={token}",
                timeout=10
            )
            if response.status_code == 200:
                print("   ✅ Works as query parameter")
            else:
                print(f"   ❌ Also fails: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        print("\n" + "-"*50 + "\n")
    
    # Test with pyannote
    print("\n=== Testing with pyannote.audio ===")
    try:
        from pyannote.audio import Pipeline
        print("✅ pyannote.audio imported")
        
        # Try to load pipeline with token
        source, token = tokens[0]
        print(f"\nTrying to load pipeline with token from {source}...")
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization",
                use_auth_token=token
            )
            print("✅ Pipeline loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load pipeline: {e}")
            
            # Try without Bearer prefix
            print("\nTrying without Bearer prefix...")
            try:
                pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization",
                    use_auth_token=token.replace("Bearer ", "")
                )
                print("✅ Works without Bearer prefix!")
            except Exception as e2:
                print(f"❌ Still fails: {e2}")
                
    except ImportError:
        print("❌ pyannote.audio not installed")

if __name__ == "__main__":
    debug_token()