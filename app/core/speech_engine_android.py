#!/usr/bin/env python3
"""
Speech Engine - Android Compatible Version
Text-to-speech synthesis for Android devices
"""

import logging
from typing import Optional, List, Dict, Any
import threading
import time
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Check if we're running on Android
def is_android():
    try:
        import jnius
        return True
    except ImportError:
        return False


# Android TTS implementation with proper error handling
ANDROID_TTS_AVAILABLE = False
PythonActivity = None
TextToSpeech = None
Locale = None
run_on_ui_thread = None

if is_android():
    try:
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread

        # Android classes
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')

        ANDROID_TTS_AVAILABLE = True
        print("✅ Android TTS available")
    except ImportError as e:
        print(f"ℹ️ Android modules not available during development: {e}")
        # This is expected during desktop development
    except Exception as e:
        print(f"❌ Android TTS initialization error: {e}")
else:
    print("ℹ️ Not running on Android - using desktop fallback")

# Fallback TTS for desktop testing
try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class AndroidTTSEngine:
    """Android Text-to-Speech Engine"""

    def __init__(self):
        self.tts = None
        self.initialized = False
        self.is_speaking = False

        if ANDROID_TTS_AVAILABLE:
            self.init_android_tts()

    @run_on_ui_thread
    def init_android_tts(self):
        """Initialize Android TTS on UI thread"""
        try:
            context = PythonActivity.mActivity
            self.tts = TextToSpeech(context, None)

            # Set default language to English
            result = self.tts.setLanguage(Locale.ENGLISH)
            if result == TextToSpeech.LANG_MISSING_DATA or result == TextToSpeech.LANG_NOT_SUPPORTED:
                print("⚠️ English language not supported by TTS")
            else:
                print("✅ Android TTS initialized successfully")
                self.initialized = True

        except Exception as e:
            print(f"❌ Failed to initialize Android TTS: {e}")

    def speak(self, text: str) -> bool:
        """Speak text using Android TTS"""
        if not self.initialized or not self.tts:
            return False

        try:
            self.is_speaking = True
            # Use QUEUE_FLUSH to replace any pending speech
            result = self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "utterance_id")

            if result == TextToSpeech.SUCCESS:
                print(f"🔊 Android TTS speaking: {text}")
                return True
            else:
                print(f"❌ Android TTS failed to speak: {result}")
                return False

        except Exception as e:
            print(f"❌ Android TTS error: {e}")
            return False
        finally:
            # Reset speaking flag after a delay
            def reset_speaking():
                time.sleep(2)
                self.is_speaking = False

            thread = threading.Thread(target=reset_speaking, daemon=True)
            thread.start()

    def stop(self):
        """Stop current speech"""
        if self.tts:
            try:
                self.tts.stop()
                self.is_speaking = False
                print("⏹️ Android TTS stopped")
            except Exception as e:
                print(f"⚠️ Error stopping Android TTS: {e}")

    def cleanup(self):
        """Clean up Android TTS"""
        if self.tts:
            try:
                self.tts.shutdown()
                print("🔧 Android TTS cleaned up")
            except Exception as e:
                print(f"⚠️ Error cleaning up Android TTS: {e}")


class SpeechEngine:
    """Cross-platform speech engine with Android support"""

    def __init__(self):
        self.enabled = True
        self.rate = 150  # Words per minute
        self.volume = 0.8  # Volume (0.0 to 1.0)

        # Speech engines
        self.android_engine = None
        self.pyttsx3_engine = None
        self.current_engine = None
        self.initialized = False

        # Thread safety
        self.speaking_lock = threading.Lock()
        self.is_speaking = False

        print("🔊 Initializing Cross-Platform Speech Engine...")
        self.initialize_engines()

    def initialize_engines(self):
        """Initialize speech engines based on platform"""
        if is_android() and ANDROID_TTS_AVAILABLE:
            # Use Android TTS
            try:
                print("🤖 Initializing Android TTS...")
                self.android_engine = AndroidTTSEngine()
                if self.android_engine.initialized:
                    self.current_engine = 'android'
                    self.initialized = True
                    print("✅ Android TTS ready")
                else:
                    print("❌ Android TTS initialization failed")
            except Exception as e:
                print(f"❌ Android TTS error: {e}")

        # Fallback to pyttsx3 for desktop/testing
        if not self.initialized and PYTTSX3_AVAILABLE:
            try:
                print("🔊 Initializing pyttsx3 fallback...")
                self.pyttsx3_engine = pyttsx3.init()
                if self.pyttsx3_engine:
                    self.pyttsx3_engine.setProperty('rate', self.rate)
                    self.pyttsx3_engine.setProperty('volume', self.volume)
                    self.current_engine = 'pyttsx3'
                    self.initialized = True
                    print("✅ pyttsx3 fallback ready")
            except Exception as e:
                print(f"❌ pyttsx3 fallback failed: {e}")

        if not self.initialized:
            print("❌ No speech engines available")
            self.enabled = False
        else:
            print(f"🎯 Using speech engine: {self.current_engine}")

    def speak(self, text: str, blocking: bool = False, test_mode: bool = False) -> bool:
        """
        Speak text using the best available engine

        Args:
            text: Text to speak
            blocking: Whether to block until speech is complete (Android TTS doesn't support this)
            test_mode: Whether this is a test (reduces output)

        Returns:
            bool: True if speech was initiated successfully
        """
        if not self.enabled or not text or not self.initialized:
            return False

        if not test_mode:
            print(f"🔊 Speaking: {text}")
            logger.info(f"Speaking: {text}")

        try:
            with self.speaking_lock:
                self.is_speaking = True

                if self.current_engine == 'android' and self.android_engine:
                    return self.android_engine.speak(text)

                elif self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                    self.pyttsx3_engine.say(text)
                    if blocking:
                        self.pyttsx3_engine.runAndWait()
                        self.is_speaking = False
                    else:
                        def speak_thread():
                            try:
                                self.pyttsx3_engine.runAndWait()
                            except Exception as e:
                                if not test_mode:
                                    print(f"⚠️ pyttsx3 error: {e}")
                            finally:
                                self.is_speaking = False

                        thread = threading.Thread(target=speak_thread, daemon=True)
                        thread.start()
                    return True

                else:
                    if not test_mode:
                        print("❌ No speech engine available")
                    return False

        except Exception as e:
            if not test_mode:
                print(f"❌ Speech failed: {e}")
            logger.error(f"Speech error: {e}")
            self.is_speaking = False
            return False

    def stop_speaking(self):
        """Stop current speech"""
        try:
            if self.current_engine == 'android' and self.android_engine:
                self.android_engine.stop()
            elif self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                self.pyttsx3_engine.stop()

            print("⏹️ Speech stopped")

        except Exception as e:
            print(f"⚠️ Error stopping speech: {e}")
        finally:
            self.is_speaking = False

    def set_rate(self, rate: int):
        """Set speech rate (Android TTS doesn't support runtime rate changes)"""
        self.rate = max(50, min(300, rate))

        try:
            if self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                self.pyttsx3_engine.setProperty('rate', self.rate)
                print(f"🔧 Speech rate set to {self.rate} WPM")
            elif self.current_engine == 'android':
                print("ℹ️ Android TTS rate adjustment not supported at runtime")

        except Exception as e:
            print(f"⚠️ Error setting speech rate: {e}")

    def set_volume(self, volume: float):
        """Set speech volume (Android TTS uses system volume)"""
        self.volume = max(0.0, min(1.0, volume))

        try:
            if self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                self.pyttsx3_engine.setProperty('volume', self.volume)
                print(f"🔧 Speech volume set to {self.volume}")
            elif self.current_engine == 'android':
                print("ℹ️ Android TTS uses system volume")

        except Exception as e:
            print(f"⚠️ Error setting speech volume: {e}")

    def set_enabled(self, enabled: bool):
        """Enable or disable speech"""
        self.enabled = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🔧 Speech {status}")

    def get_status(self) -> Dict[str, Any]:
        """Get current speech engine status"""
        return {
            'enabled': self.enabled,
            'initialized': self.initialized,
            'rate': self.rate,
            'volume': self.volume,
            'current_engine': self.current_engine,
            'is_speaking': self.is_speaking,
            'platform': 'android' if is_android() else platform.system(),
            'engines_available': {
                'android': self.android_engine is not None,
                'pyttsx3': self.pyttsx3_engine is not None
            }
        }

    def cleanup(self):
        """Clean up speech engines"""
        try:
            if self.is_speaking:
                self.stop_speaking()

            if self.android_engine:
                self.android_engine.cleanup()

            if self.pyttsx3_engine:
                self.pyttsx3_engine.stop()

            print("🔧 Speech engine cleaned up")

        except Exception as e:
            print(f"⚠️ Error cleaning up speech engine: {e}")


# Create global instance
speech_engine = SpeechEngine()


# Convenience functions
def speak(text: str, blocking: bool = False) -> bool:
    """Speak text using global speech engine"""
    return speech_engine.speak(text, blocking)


def set_speech_rate(rate: int):
    """Set global speech rate"""
    speech_engine.set_rate(rate)


def set_speech_volume(volume: float):
    """Set global speech volume"""
    speech_engine.set_volume(volume)


def enable_speech(enabled: bool = True):
    """Enable/disable global speech"""
    speech_engine.set_enabled(enabled)


def stop_speech():
    """Stop current speech"""
    speech_engine.stop_speaking()


def get_speech_status() -> Dict[str, Any]:
    """Get speech engine status"""
    return speech_engine.get_status()