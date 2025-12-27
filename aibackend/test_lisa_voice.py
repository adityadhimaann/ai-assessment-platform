#!/usr/bin/env python3
"""
Quick test script to verify Lisa's voice configuration
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from app.services.voice_service import VoiceService


def test_devi_voice():
    """Test Lisa's voice configuration"""
    
    print("🎤 Testing Lisa's Voice Configuration\n")
    print("=" * 50)
    
    # Load settings
    try:
        settings = get_settings()
        print("✅ Settings loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return False
    
    # Check TTS configuration
    print(f"\n📋 Configuration:")
    print(f"   TTS Service: {settings.tts_service}")
    print(f"   TTS API Key: {'*' * 20}{settings.tts_api_key[-4:] if len(settings.tts_api_key) > 4 else '****'}")
    
    if settings.tts_service == "elevenlabs":
        if settings.elevenlabs_voice_id:
            print(f"   Voice ID: {settings.elevenlabs_voice_id}")
        else:
            print(f"   ⚠️  Voice ID: Not set (will use default)")
        print(f"   Model ID: {settings.elevenlabs_model_id}")
    
    # Create voice service
    try:
        voice_service = VoiceService(settings)
        print("\n✅ Voice service initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize voice service: {e}")
        return False
    
    # Test voice generation
    print("\n🎵 Testing voice generation...")
    test_text = "Hello! This is Lisa speaking. Your voice configuration is working perfectly!"
    
    try:
        audio_data = voice_service.generate_voice_feedback(test_text)
        print(f"✅ Voice generated successfully!")
        print(f"   Audio size: {len(audio_data)} bytes")
        
        # Save test audio
        output_file = Path(__file__).parent / "test_devi_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"   Saved to: {output_file}")
        print(f"\n🎧 Play the file to hear Lisa's voice!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate voice: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  LISA VOICE TEST SCRIPT")
    print("=" * 50 + "\n")
    
    success = test_devi_voice()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Play test_devi_output.mp3 to verify the voice")
        print("2. If it sounds correct, you're all set!")
        print("3. Start the backend and frontend to use in the app")
    else:
        print("❌ Tests failed!")
        print("\nTroubleshooting:")
        print("1. Verify ELEVENLABS_VOICE_ID in backend/.env")
        print("2. Check TTS_API_KEY is correct")
        print("3. Ensure voice exists in your ElevenLabs account")
    print("=" * 50 + "\n")
    
    sys.exit(0 if success else 1)
