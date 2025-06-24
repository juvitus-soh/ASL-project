#!/usr/bin/env python3
"""
Quick Speech Test Script
Run this to verify speech is working before using in the main app
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_speech_simple():
    """Simple speech test"""
    print("🧪 Testing Speech Engines...")

    # Test 1: pyttsx3 direct
    try:
        import pyttsx3
        print("📢 Testing pyttsx3 directly...")
        engine = pyttsx3.init()
        engine.say("pyttsx3 is working")
        engine.runAndWait()
        print("✅ pyttsx3 direct test passed")
    except Exception as e:
        print(f"❌ pyttsx3 direct test failed: {e}")

    time.sleep(1)

    # Test 2: Windows SAPI direct
    try:
        import win32com.client
        print("📢 Testing Windows SAPI directly...")
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        sapi.Speak("Windows SAPI is working", 0)
        print("✅ SAPI direct test passed")
    except Exception as e:
        print(f"❌ SAPI direct test failed: {e}")

    time.sleep(1)

    # Test 3: Our Speech Engine
    try:
        print("📢 Testing our Speech Engine...")

        # Import our fixed speech engine
        from app.core.speech_engine import SpeechEngine

        speech = SpeechEngine()

        if speech.enabled:
            print("✅ Speech Engine initialized")

            # Test immediate speech
            speech.speak_immediate("Speech Engine is working")
            time.sleep(2)

            # Test queued speech
            speech.speak("Testing queue")
            time.sleep(2)

            # Test multiple calls (should be rate limited)
            for i in range(3):
                speech.speak(f"Number {i}")

            time.sleep(3)

            print("✅ Speech Engine test completed")
            speech.cleanup()

        else:
            print("❌ Speech Engine not enabled")

    except Exception as e:
        print(f"❌ Speech Engine test failed: {e}")
        import traceback
        traceback.print_exc()


def test_speech_engines_info():
    """Get info about available speech engines"""
    print("\n🔍 Speech Engine Information:")

    # Check pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ pyttsx3: Available with {len(voices) if voices else 0} voices")

        if voices:
            for i, voice in enumerate(voices[:2]):  # Show first 2 voices
                print(f"   Voice {i}: {voice.name}")

        engine.stop()
    except Exception as e:
        print(f"❌ pyttsx3: Not available - {e}")

    # Check Windows SAPI
    try:
        import win32com.client
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        voices = sapi.GetVoices()
        print(f"✅ Windows SAPI: Available with {voices.Count} voices")

        for i in range(min(2, voices.Count)):  # Show first 2 voices
            voice = voices.Item(i)
            print(f"   Voice {i}: {voice.GetDescription()}")

    except Exception as e:
        print(f"❌ Windows SAPI: Not available - {e}")


if __name__ == "__main__":
    print("🎵 Speech Engine Test")
    print("=" * 50)

    # Show engine info
    test_speech_engines_info()

    print("\n" + "=" * 50)
    print("🧪 Running Speech Tests...")
    print("You should hear audio for each successful test.")
    print("=" * 50)

    # Run tests
    test_speech_simple()

    print("\n✅ Speech tests completed!")
    print("If you heard audio, speech is working correctly.")
    print("If no audio, check your system volume and speakers.")