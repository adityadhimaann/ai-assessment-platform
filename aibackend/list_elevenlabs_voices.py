#!/usr/bin/env python3
"""
List all available ElevenLabs voices in your account
"""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings


def list_voices():
    """List all voices available in the ElevenLabs account"""
    
    print("\n" + "=" * 70)
    print("  ELEVENLABS VOICE FINDER")
    print("=" * 70 + "\n")
    
    # Load settings
    try:
        settings = get_settings()
        api_key = settings.tts_api_key
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return False
    
    print("🔍 Fetching voices from your ElevenLabs account...\n")
    
    # Call ElevenLabs API to list voices
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        voices = data.get("voices", [])
        
        if not voices:
            print("⚠️  No voices found in your account")
            return False
        
        print(f"✅ Found {len(voices)} voice(s) in your account:\n")
        print("=" * 70)
        
        # Look for Devi voice specifically
        devi_voice = None
        
        for i, voice in enumerate(voices, 1):
            voice_id = voice.get("voice_id", "N/A")
            name = voice.get("name", "N/A")
            category = voice.get("category", "N/A")
            description = voice.get("description", "")
            
            # Check if this is the Devi voice
            is_devi = "devi" in name.lower()
            
            if is_devi:
                devi_voice = voice
                print(f"\n🎯 FOUND YOUR DEVI VOICE! 🎯")
            
            print(f"\n{i}. {name}")
            print(f"   Voice ID: {voice_id}")
            print(f"   Category: {category}")
            if description:
                print(f"   Description: {description[:100]}...")
            
            if is_devi:
                print(f"\n   ✅ This is your Devi voice!")
                print(f"   📋 Copy this ID to your .env file:")
                print(f"   ELEVENLABS_VOICE_ID={voice_id}")
        
        print("\n" + "=" * 70)
        
        if devi_voice:
            print("\n✅ SUCCESS! Found your Devi voice!")
            print(f"\n📝 Next steps:")
            print(f"1. Copy the voice ID above")
            print(f"2. Edit backend/.env")
            print(f"3. Replace 'your_devi_voice_id_here' with: {devi_voice['voice_id']}")
            print(f"4. Save the file")
            print(f"5. Run: python3 test_devi_voice.py")
            return True
        else:
            print("\n⚠️  Devi voice not found in the list above")
            print("\nPossible reasons:")
            print("1. Voice name might be different (check the list above)")
            print("2. Voice might be in a different ElevenLabs account")
            print("3. Voice might not be created yet")
            print("\n💡 To use any voice above, copy its Voice ID to your .env file")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = list_voices()
    print("\n" + "=" * 70 + "\n")
    sys.exit(0 if success else 1)
