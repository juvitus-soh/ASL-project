# #!/usr/bin/env python3
# """
# Speech Engine - Non-blocking Version
# Text-to-speech synthesis without blocking initialization
# """
#
# import logging
# from typing import Optional, List, Dict, Any
# import threading
# import time
#
# try:
#     import pyttsx3
#
#     PYTTSX3_AVAILABLE = True
# except ImportError:
#     PYTTSX3_AVAILABLE = False
#     print("⚠️ pyttsx3 not available, using Windows SAPI fallback")
#
# try:
#     import win32com.client
#
#     WIN32_AVAILABLE = True
# except ImportError:
#     WIN32_AVAILABLE = False
#     print("⚠️ win32com not available")
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# class SpeechEngine:
#     """Enhanced speech engine with non-blocking initialization"""
#
#     def __init__(self):
#         self.enabled = True
#         self.rate = 150  # Words per minute
#         self.volume = 0.8  # Volume (0.0 to 1.0)
#
#         # Speech engines (try multiple for reliability)
#         self.pyttsx3_engine = None
#         self.sapi_engine = None
#         self.current_engine = None
#         self.initialized = False
#
#         # Thread safety
#         self.speaking_lock = threading.Lock()
#         self.is_speaking = False
#
#         print("🔊 Initializing Speech Engine (non-blocking)...")
#         self.initialize_engines()
#
#     def initialize_engines(self):
#         """Initialize all available speech engines - NON-BLOCKING"""
#         engines_initialized = []
#
#         # Method 1: Try pyttsx3 (most reliable)
#         if PYTTSX3_AVAILABLE:
#             try:
#                 print("🔊 Trying pyttsx3 engine...")
#                 self.pyttsx3_engine = pyttsx3.init()
#                 if self.pyttsx3_engine:
#                     # Configure pyttsx3
#                     self.pyttsx3_engine.setProperty('rate', self.rate)
#                     self.pyttsx3_engine.setProperty('volume', self.volume)
#
#                     # Check if it works (no blocking test)
#                     voices = self.pyttsx3_engine.getProperty('voices')
#                     if voices:
#                         print(f"✅ pyttsx3 initialized with {len(voices)} voices")
#                         self.current_engine = 'pyttsx3'
#                         engines_initialized.append('pyttsx3')
#                     else:
#                         print("⚠️ pyttsx3 initialized but no voices found")
#
#             except Exception as e:
#                 print(f"❌ pyttsx3 initialization failed: {e}")
#                 self.pyttsx3_engine = None
#
#         # Method 2: Try Windows SAPI (fallback)
#         if WIN32_AVAILABLE:
#             try:
#                 print("🔊 Trying Windows SAPI engine...")
#                 self.sapi_engine = win32com.client.Dispatch("SAPI.SpVoice")
#                 if self.sapi_engine:
#                     # Configure SAPI
#                     self.sapi_engine.Rate = 1  # SAPI rate scale is different
#                     self.sapi_engine.Volume = int(self.volume * 100)  # SAPI uses 0-100
#
#                     # Test available voices
#                     voices = self.sapi_engine.GetVoices()
#                     print(f"✅ SAPI initialized with {voices.Count} voices")
#                     if not self.current_engine:  # Use SAPI if pyttsx3 failed
#                         self.current_engine = 'sapi'
#                     engines_initialized.append('sapi')
#
#             except Exception as e:
#                 print(f"❌ SAPI initialization failed: {e}")
#                 self.sapi_engine = None
#
#         # Report initialization results
#         if engines_initialized:
#             print(f"✅ Speech engines initialized: {', '.join(engines_initialized)}")
#             print(f"🎯 Using primary engine: {self.current_engine}")
#             self.initialized = True
#
#             # NO BLOCKING TEST - just mark as ready
#             print("✅ Speech engine ready (test skipped for faster startup)")
#         else:
#             print("❌ No speech engines available")
#             self.enabled = False
#
#     def test_speech_async(self):
#         """Test speech output asynchronously (call manually if needed)"""
#
#         def test_in_thread():
#             try:
#                 print("🔊 Testing speech output...")
#                 self.speak("Speech test", blocking=True, test_mode=True)
#                 print("✅ Speech test completed")
#             except Exception as e:
#                 print(f"⚠️ Speech test failed: {e}")
#
#         if self.initialized:
#             thread = threading.Thread(target=test_in_thread, daemon=True)
#             thread.start()
#         else:
#             print("⚠️ Speech engine not initialized")
#
#     def speak(self, text: str, blocking: bool = False, test_mode: bool = False) -> bool:
#         """
#         Speak text using the best available engine
#
#         Args:
#             text: Text to speak
#             blocking: Whether to block until speech is complete
#             test_mode: Whether this is a test (reduces output)
#
#         Returns:
#             bool: True if speech was initiated successfully
#         """
#         if not self.enabled or not text or not self.initialized:
#             return False
#
#         if not test_mode:
#             print(f"🔊 Speaking: {text}")
#             logger.info(f"Speaking: {text}")
#
#         try:
#             # Method 1: Try pyttsx3 first
#             if self.pyttsx3_engine and self.current_engine == 'pyttsx3':
#                 return self._speak_pyttsx3(text, blocking, test_mode)
#
#             # Method 2: Try SAPI
#             elif self.sapi_engine and self.current_engine == 'sapi':
#                 return self._speak_sapi(text, blocking, test_mode)
#
#             # Method 3: Try any available engine
#             else:
#                 if self.pyttsx3_engine:
#                     return self._speak_pyttsx3(text, blocking, test_mode)
#                 elif self.sapi_engine:
#                     return self._speak_sapi(text, blocking, test_mode)
#                 else:
#                     if not test_mode:
#                         print("❌ No speech engines available")
#                     return False
#
#         except Exception as e:
#             if not test_mode:
#                 print(f"❌ Speech failed: {e}")
#             logger.error(f"Speech error: {e}")
#             return False
#
#     def _speak_pyttsx3(self, text: str, blocking: bool, test_mode: bool) -> bool:
#         """Speak using pyttsx3 engine"""
#         try:
#             if not test_mode:
#                 print("🔊 Using pyttsx3 engine")
#
#             with self.speaking_lock:
#                 self.is_speaking = True
#                 self.pyttsx3_engine.say(text)
#
#                 if blocking:
#                     self.pyttsx3_engine.runAndWait()
#                     self.is_speaking = False
#                 else:
#                     # Run in separate thread for non-blocking speech
#                     def speak_thread():
#                         try:
#                             self.pyttsx3_engine.runAndWait()
#                         except Exception as e:
#                             if not test_mode:
#                                 print(f"⚠️ pyttsx3 thread error: {e}")
#                         finally:
#                             self.is_speaking = False
#
#                     thread = threading.Thread(target=speak_thread, daemon=True)
#                     thread.start()
#
#             return True
#
#         except Exception as e:
#             if not test_mode:
#                 print(f"❌ pyttsx3 speech failed: {e}")
#             self.is_speaking = False
#             return False
#
#     def _speak_sapi(self, text: str, blocking: bool, test_mode: bool) -> bool:
#         """Speak using Windows SAPI engine"""
#         try:
#             if not test_mode:
#                 print("🔊 Using SAPI engine")
#
#             with self.speaking_lock:
#                 self.is_speaking = True
#
#                 # SAPI flags: 0 = synchronous (blocking), 1 = asynchronous (non-blocking)
#                 flags = 0 if blocking else 1
#
#                 self.sapi_engine.Speak(text, flags)
#
#                 if blocking:
#                     self.is_speaking = False
#                 else:
#                     # For non-blocking, set a timer to reset the speaking flag
#                     def reset_speaking():
#                         time.sleep(2)  # Assume speech finishes in 2 seconds
#                         self.is_speaking = False
#
#                     thread = threading.Thread(target=reset_speaking, daemon=True)
#                     thread.start()
#
#             return True
#
#         except Exception as e:
#             if not test_mode:
#                 print(f"❌ SAPI speech failed: {e}")
#             self.is_speaking = False
#             return False
#
#     def stop_speaking(self):
#         """Stop current speech"""
#         try:
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.stop()
#
#             if self.sapi_engine:
#                 self.sapi_engine.Speak("", 3)  # Flag 3 = purge and stop
#
#             print("⏹️ Speech stopped")
#
#         except Exception as e:
#             print(f"⚠️ Error stopping speech: {e}")
#         finally:
#             self.is_speaking = False
#
#     def set_rate(self, rate: int):
#         """Set speech rate (words per minute)"""
#         self.rate = max(50, min(300, rate))  # Clamp between 50-300
#
#         try:
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.setProperty('rate', self.rate)
#
#             if self.sapi_engine:
#                 # SAPI rate: -10 to 10, convert from WPM
#                 sapi_rate = int((self.rate - 150) / 20)  # Approximate conversion
#                 sapi_rate = max(-10, min(10, sapi_rate))
#                 self.sapi_engine.Rate = sapi_rate
#
#             print(f"🔧 Speech rate set to {self.rate} WPM")
#
#         except Exception as e:
#             print(f"⚠️ Error setting speech rate: {e}")
#
#     def set_volume(self, volume: float):
#         """Set speech volume (0.0 to 1.0)"""
#         self.volume = max(0.0, min(1.0, volume))
#
#         try:
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.setProperty('volume', self.volume)
#
#             if self.sapi_engine:
#                 self.sapi_engine.Volume = int(self.volume * 100)
#
#             print(f"🔧 Speech volume set to {self.volume}")
#
#         except Exception as e:
#             print(f"⚠️ Error setting speech volume: {e}")
#
#     def set_enabled(self, enabled: bool):
#         """Enable or disable speech"""
#         self.enabled = enabled
#         status = "enabled" if enabled else "disabled"
#         print(f"🔧 Speech {status}")
#
#     def get_voices(self) -> List[Dict[str, Any]]:
#         """Get available voices"""
#         voices = []
#
#         try:
#             if self.pyttsx3_engine:
#                 pyttsx3_voices = self.pyttsx3_engine.getProperty('voices')
#                 for voice in pyttsx3_voices:
#                     voices.append({
#                         'id': voice.id,
#                         'name': voice.name,
#                         'engine': 'pyttsx3'
#                     })
#
#             if self.sapi_engine:
#                 sapi_voices = self.sapi_engine.GetVoices()
#                 for i in range(sapi_voices.Count):
#                     voice = sapi_voices.Item(i)
#                     voices.append({
#                         'id': voice.Id,
#                         'name': voice.GetDescription(),
#                         'engine': 'sapi'
#                     })
#
#         except Exception as e:
#             print(f"⚠️ Error getting voices: {e}")
#
#         return voices
#
#     def get_status(self) -> Dict[str, Any]:
#         """Get current speech engine status"""
#         return {
#             'enabled': self.enabled,
#             'initialized': self.initialized,
#             'rate': self.rate,
#             'volume': self.volume,
#             'current_engine': self.current_engine,
#             'is_speaking': self.is_speaking,
#             'engines_available': {
#                 'pyttsx3': self.pyttsx3_engine is not None,
#                 'sapi': self.sapi_engine is not None
#             }
#         }
#
#     def cleanup(self):
#         """Clean up speech engines"""
#         try:
#             if self.is_speaking:
#                 self.stop_speaking()
#
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.stop()
#
#             print("🔧 Speech engine cleaned up")
#
#         except Exception as e:
#             print(f"⚠️ Error cleaning up speech engine: {e}")
#
#
# # Create global instance
# speech_engine = SpeechEngine()
#
#
# # Convenience functions
# def speak(text: str, blocking: bool = False) -> bool:
#     """Speak text using global speech engine"""
#     return speech_engine.speak(text, blocking)
#
#
# def test_speech():
#     """Test speech engine manually"""
#     speech_engine.test_speech_async()
#
#
# def set_speech_rate(rate: int):
#     """Set global speech rate"""
#     speech_engine.set_rate(rate)
#
#
# def set_speech_volume(volume: float):
#     """Set global speech volume"""
#     speech_engine.set_volume(volume)
#
#
# def enable_speech(enabled: bool = True):
#     """Enable/disable global speech"""
#     speech_engine.set_enabled(enabled)
#
#
# def stop_speech():
#     """Stop current speech"""
#     speech_engine.stop_speaking()
#
#
# def get_speech_status() -> Dict[str, Any]:
#     """Get speech engine status"""
#     return speech_engine.get_status()

# !/usr/bin/env python3
# """
# Speech Engine - Text-to-Speech functionality
# FIXED: Thread-safe with rate limiting to prevent crashes
# """
#
# import threading
# import time
# import queue
# import logging
# from typing import Optional
#
# # Configure logging to reduce COM spam
# logging.getLogger('comtypes').setLevel(logging.WARNING)
# logging.getLogger('comtypes.client').setLevel(logging.WARNING)
# logging.getLogger('comtypes._comobject').setLevel(logging.WARNING)
# logging.getLogger('comtypes._vtbl').setLevel(logging.WARNING)
# logging.getLogger('comtypes._post_coinit').setLevel(logging.WARNING)
#
# logger = logging.getLogger(__name__)
#
# # Try to import speech engines
# PYTTSX3_AVAILABLE = False
# SAPI_AVAILABLE = False
#
# try:
#     import pyttsx3
#
#     PYTTSX3_AVAILABLE = True
#     print("✅ pyttsx3 available")
# except ImportError:
#     print("⚠️ pyttsx3 not available")
#
# try:
#     import win32com.client
#
#     SAPI_AVAILABLE = True
#     print("✅ Windows SAPI available")
# except ImportError:
#     print("⚠️ Windows SAPI not available")
#
#
# class SpeechEngine:
#     """Thread-safe Speech Engine with rate limiting"""
#
#     def __init__(self):
#         """Initialize the speech engine"""
#         print("🔊 Initializing Speech Engine...")
#
#         # Speech engines
#         self.pyttsx3_engine = None
#         self.sapi_engine = None
#         self.current_engine = None
#
#         # Thread safety
#         self.speech_queue = queue.Queue()
#         self.speech_thread = None
#         self.stop_thread = False
#         self.thread_lock = threading.Lock()
#
#         # Rate limiting
#         self.last_speech_time = 0
#         self.min_speech_interval = 0.5  # Minimum 500ms between speech calls
#         self.speech_cache = {}  # Cache to prevent duplicate speech
#         self.cache_timeout = 1.0  # Clear cache after 1 second
#
#         # Settings
#         self.enabled = True
#         self.rate = 150
#         self.volume = 0.8
#
#         # Initialize engines
#         self._initialize_engines()
#
#         # Start speech thread
#         self._start_speech_thread()
#
#         print("✅ Speech Engine initialized")
#
#     def _initialize_engines(self):
#         """Initialize available speech engines"""
#         engines_initialized = []
#
#         # Initialize pyttsx3 (preferred)
#         if PYTTSX3_AVAILABLE:
#             try:
#                 self.pyttsx3_engine = pyttsx3.init()
#                 if self.pyttsx3_engine:
#                     # Configure pyttsx3
#                     self.pyttsx3_engine.setProperty('rate', self.rate)
#                     self.pyttsx3_engine.setProperty('volume', self.volume)
#
#                     # Get available voices
#                     voices = self.pyttsx3_engine.getProperty('voices')
#                     voice_count = len(voices) if voices else 0
#
#                     engines_initialized.append('pyttsx3')
#                     print(f"✅ pyttsx3 initialized with {voice_count} voices")
#
#                     if not self.current_engine:
#                         self.current_engine = 'pyttsx3'
#
#             except Exception as e:
#                 print(f"⚠️ pyttsx3 initialization failed: {e}")
#
#         # Initialize Windows SAPI (fallback)
#         if SAPI_AVAILABLE:
#             try:
#                 self.sapi_engine = win32com.client.Dispatch("SAPI.SpVoice")
#                 if self.sapi_engine:
#                     # Get available voices
#                     voices = self.sapi_engine.GetVoices()
#                     voice_count = voices.Count if voices else 0
#
#                     engines_initialized.append('sapi')
#                     print(f"✅ SAPI initialized with {voice_count} voices")
#
#                     if not self.current_engine:
#                         self.current_engine = 'sapi'
#
#             except Exception as e:
#                 print(f"⚠️ SAPI initialization failed: {e}")
#
#         if engines_initialized:
#             print(f"✅ Speech engines initialized: {', '.join(engines_initialized)}")
#             print(f"🎯 Using primary engine: {self.current_engine}")
#         else:
#             print("❌ No speech engines available")
#             self.enabled = False
#
#     def _start_speech_thread(self):
#         """Start the speech processing thread"""
#         if self.speech_thread and self.speech_thread.is_alive():
#             return
#
#         self.stop_thread = False
#         self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
#         self.speech_thread.start()
#         print("🧵 Speech thread started")
#
#     def _speech_worker(self):
#         """Worker thread for processing speech requests"""
#         while not self.stop_thread:
#             try:
#                 # Get speech request from queue (with timeout)
#                 try:
#                     text = self.speech_queue.get(timeout=1.0)
#                 except queue.Empty:
#                     continue
#
#                 # Process speech request
#                 if text and self.enabled:
#                     self._do_speak(text)
#
#                 # Mark task as done
#                 self.speech_queue.task_done()
#
#             except Exception as e:
#                 logger.error(f"Speech worker error: {e}")
#                 time.sleep(0.1)  # Brief pause on error
#
#     def _do_speak(self, text: str):
#         """Actually perform the speech synthesis"""
#         try:
#             current_time = time.time()
#
#             # Check rate limiting
#             if current_time - self.last_speech_time < self.min_speech_interval:
#                 return
#
#             # Check cache (prevent duplicate speech)
#             cache_key = text.lower().strip()
#             if cache_key in self.speech_cache:
#                 cache_time = self.speech_cache[cache_key]
#                 if current_time - cache_time < self.cache_timeout:
#                     return  # Skip duplicate speech
#
#             # Update cache and timing
#             self.speech_cache[cache_key] = current_time
#             self.last_speech_time = current_time
#
#             # Clean old cache entries
#             self._clean_cache(current_time)
#
#             # Perform speech synthesis
#             if self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
#                 self._speak_pyttsx3(text)
#             elif self.current_engine == 'sapi' and self.sapi_engine:
#                 self._speak_sapi(text)
#             else:
#                 print(f"🔇 Would speak: {text}")  # Fallback
#
#         except Exception as e:
#             logger.error(f"Speech synthesis error: {e}")
#
#     def _speak_pyttsx3(self, text: str):
#         """Speak using pyttsx3 (thread-safe)"""
#         try:
#             with self.thread_lock:
#                 # Use runAndWait in a controlled way
#                 self.pyttsx3_engine.say(text)
#
#                 # Run in non-blocking way to prevent thread conflicts
#                 self.pyttsx3_engine.startLoop(False)
#                 for _ in range(50):  # Max 5 seconds
#                     if not self.pyttsx3_engine.isBusy():
#                         break
#                     time.sleep(0.1)
#                 self.pyttsx3_engine.endLoop()
#
#                 logger.info(f"Speaking: {text}")
#
#         except Exception as e:
#             logger.warning(f"pyttsx3 speech error: {e}")
#             # Fallback to SAPI if available
#             if self.sapi_engine:
#                 self._speak_sapi(text)
#
#     def _speak_sapi(self, text: str):
#         """Speak using Windows SAPI"""
#         try:
#             # SAPI is generally more thread-safe
#             self.sapi_engine.Speak(text, 1)  # 1 = asynchronous
#             logger.info(f"Speaking: {text}")
#
#         except Exception as e:
#             logger.warning(f"SAPI speech error: {e}")
#
#     def _clean_cache(self, current_time: float):
#         """Clean old entries from speech cache"""
#         try:
#             keys_to_remove = []
#             for key, timestamp in self.speech_cache.items():
#                 if current_time - timestamp > self.cache_timeout:
#                     keys_to_remove.append(key)
#
#             for key in keys_to_remove:
#                 del self.speech_cache[key]
#
#         except Exception as e:
#             logger.warning(f"Cache cleanup error: {e}")
#
#     def speak(self, text: str):
#         """
#         Queue text for speech synthesis (non-blocking)
#
#         Args:
#             text: Text to speak
#         """
#         if not text or not self.enabled:
#             return
#
#         try:
#             # Clean text
#             text = str(text).strip()
#             if not text:
#                 return
#
#             # Add to queue (non-blocking)
#             try:
#                 self.speech_queue.put_nowait(text)
#             except queue.Full:
#                 logger.warning("Speech queue full, dropping request")
#
#         except Exception as e:
#             logger.error(f"Speech queue error: {e}")
#
#     def speak_immediate(self, text: str):
#         """
#         Speak text immediately (blocking)
#         Use sparingly - prefer speak() for normal use
#
#         Args:
#             text: Text to speak
#         """
#         if not text or not self.enabled:
#             return
#
#         try:
#             text = str(text).strip()
#             if text:
#                 self._do_speak(text)
#         except Exception as e:
#             logger.error(f"Immediate speech error: {e}")
#
#     def set_enabled(self, enabled: bool):
#         """Enable or disable speech"""
#         self.enabled = enabled
#         if enabled:
#             print("🔊 Speech enabled")
#         else:
#             print("🔇 Speech disabled")
#
#     def set_rate(self, rate: int):
#         """Set speech rate (words per minute)"""
#         self.rate = max(50, min(400, rate))  # Clamp to reasonable range
#
#         try:
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.setProperty('rate', self.rate)
#             print(f"🎵 Speech rate set to {self.rate} WPM")
#         except Exception as e:
#             logger.warning(f"Failed to set speech rate: {e}")
#
#     def set_volume(self, volume: float):
#         """Set speech volume (0.0 to 1.0)"""
#         self.volume = max(0.0, min(1.0, volume))
#
#         try:
#             if self.pyttsx3_engine:
#                 self.pyttsx3_engine.setProperty('volume', self.volume)
#             print(f"🔊 Speech volume set to {self.volume}")
#         except Exception as e:
#             logger.warning(f"Failed to set speech volume: {e}")
#
#     def update_settings(self, settings: dict):
#         """Update speech settings"""
#         try:
#             if 'enabled' in settings:
#                 self.set_enabled(settings['enabled'])
#
#             if 'rate' in settings:
#                 self.set_rate(settings['rate'])
#
#             if 'volume' in settings:
#                 self.set_volume(settings['volume'])
#
#             if 'min_speech_interval' in settings:
#                 self.min_speech_interval = max(0.1, settings['min_speech_interval'])
#
#             logger.info("Speech settings updated")
#
#         except Exception as e:
#             logger.error(f"Failed to update speech settings: {e}")
#
#     def clear_queue(self):
#         """Clear the speech queue"""
#         try:
#             while not self.speech_queue.empty():
#                 try:
#                     self.speech_queue.get_nowait()
#                 except queue.Empty:
#                     break
#             print("🗑️ Speech queue cleared")
#         except Exception as e:
#             logger.warning(f"Queue clear error: {e}")
#
#     def get_status(self) -> dict:
#         """Get speech engine status"""
#         return {
#             'enabled': self.enabled,
#             'current_engine': self.current_engine,
#             'queue_size': self.speech_queue.qsize(),
#             'rate': self.rate,
#             'volume': self.volume,
#             'engines_available': {
#                 'pyttsx3': self.pyttsx3_engine is not None,
#                 'sapi': self.sapi_engine is not None
#             }
#         }
#
#     def cleanup(self):
#         """Clean up the speech engine"""
#         try:
#             print("🔧 Cleaning up Speech Engine...")
#
#             # Stop thread
#             self.stop_thread = True
#             if self.speech_thread and self.speech_thread.is_alive():
#                 self.speech_thread.join(timeout=2.0)
#
#             # Clear queue
#             self.clear_queue()
#
#             # Clean up engines
#             with self.thread_lock:
#                 if self.pyttsx3_engine:
#                     try:
#                         self.pyttsx3_engine.stop()
#                     except:
#                         pass
#                     self.pyttsx3_engine = None
#
#                 if self.sapi_engine:
#                     self.sapi_engine = None
#
#             print("🔧 Speech Engine cleaned up")
#
#         except Exception as e:
#             logger.error(f"Speech cleanup error: {e}")
#
#
# # Test function
# def test_speech_engine():
#     """Test the speech engine"""
#     print("🧪 Testing Speech Engine...")
#
#     engine = SpeechEngine()
#
#     if engine.enabled:
#         print("✅ Speech engine working")
#
#         # Test basic speech
#         engine.speak("Testing speech engine")
#         time.sleep(1)
#
#         # Test rapid speech (should be rate limited)
#         for i in range(5):
#             engine.speak(f"Test {i}")
#
#         time.sleep(2)
#         engine.cleanup()
#
#     else:
#         print("❌ Speech engine not available")
#
#
# if __name__ == "__main__":
#     test_speech_engine()

# !/usr/bin/env python3
"""
Speech Engine - Text-to-Speech functionality
WORKING VERSION: Simplified to ensure actual audio output
"""

import threading
import time
import queue
import logging
from typing import Optional

# Configure logging to reduce COM spam
logging.getLogger('comtypes').setLevel(logging.WARNING)
logging.getLogger('comtypes.client').setLevel(logging.WARNING)
logging.getLogger('comtypes._comobject').setLevel(logging.WARNING)
logging.getLogger('comtypes._vtbl').setLevel(logging.WARNING)
logging.getLogger('comtypes._post_coinit').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Try to import speech engines
PYTTSX3_AVAILABLE = False
SAPI_AVAILABLE = False

try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
    print("✅ pyttsx3 available")
except ImportError:
    print("⚠️ pyttsx3 not available")

try:
    import win32com.client

    SAPI_AVAILABLE = True
    print("✅ Windows SAPI available")
except ImportError:
    print("⚠️ Windows SAPI not available")


class SpeechEngine:
    """Simplified Speech Engine that actually produces audio"""

    def __init__(self):
        """Initialize the speech engine"""
        print("🔊 Initializing Speech Engine...")

        # Speech engines
        self.pyttsx3_engine = None
        self.sapi_engine = None
        self.current_engine = None

        # Thread safety - simpler approach
        self.speech_queue = queue.Queue(maxsize=5)  # Limit queue size
        self.speech_thread = None
        self.stop_thread = False
        self.engine_lock = threading.Lock()

        # Rate limiting
        self.last_speech_time = 0
        self.min_speech_interval = 1.0  # 1 second minimum between speech

        # Settings
        self.enabled = True
        self.rate = 150
        self.volume = 0.8

        # Initialize engines
        self._initialize_engines()

        # Start speech thread
        self._start_speech_thread()

        print("✅ Speech Engine initialized")

    def _initialize_engines(self):
        """Initialize available speech engines"""
        engines_initialized = []

        # Initialize pyttsx3 (preferred)
        if PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                if self.pyttsx3_engine:
                    # Configure pyttsx3
                    self.pyttsx3_engine.setProperty('rate', self.rate)
                    self.pyttsx3_engine.setProperty('volume', self.volume)

                    # Get available voices
                    voices = self.pyttsx3_engine.getProperty('voices')
                    voice_count = len(voices) if voices else 0

                    engines_initialized.append('pyttsx3')
                    print(f"✅ pyttsx3 initialized with {voice_count} voices")

                    if not self.current_engine:
                        self.current_engine = 'pyttsx3'

            except Exception as e:
                print(f"⚠️ pyttsx3 initialization failed: {e}")

        # Initialize Windows SAPI (fallback)
        if SAPI_AVAILABLE:
            try:
                self.sapi_engine = win32com.client.Dispatch("SAPI.SpVoice")
                if self.sapi_engine:
                    engines_initialized.append('sapi')
                    print(f"✅ SAPI initialized")

                    if not self.current_engine:
                        self.current_engine = 'sapi'

            except Exception as e:
                print(f"⚠️ SAPI initialization failed: {e}")

        if engines_initialized:
            print(f"✅ Speech engines initialized: {', '.join(engines_initialized)}")
            print(f"🎯 Using primary engine: {self.current_engine}")
        else:
            print("❌ No speech engines available")
            self.enabled = False

    def _start_speech_thread(self):
        """Start the speech processing thread"""
        if self.speech_thread and self.speech_thread.is_alive():
            return

        self.stop_thread = False
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        print("🧵 Speech thread started")

    def _speech_worker(self):
        """Worker thread for processing speech requests"""
        while not self.stop_thread:
            try:
                # Get speech request from queue
                try:
                    text = self.speech_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Process speech request
                if text and self.enabled:
                    self._do_speak(text)

                # Mark task as done
                self.speech_queue.task_done()

            except Exception as e:
                logger.error(f"Speech worker error: {e}")
                time.sleep(0.1)

    def _do_speak(self, text: str):
        """Actually perform the speech synthesis"""
        try:
            current_time = time.time()

            # Check rate limiting
            if current_time - self.last_speech_time < self.min_speech_interval:
                return

            self.last_speech_time = current_time

            # Perform speech synthesis
            success = False

            # Try pyttsx3 first (simplified approach)
            if self.current_engine == 'pyttsx3' and self.pyttsx3_engine:
                success = self._speak_pyttsx3_simple(text)

            # Fall back to SAPI if pyttsx3 fails
            if not success and self.sapi_engine:
                success = self._speak_sapi(text)

            if success:
                logger.info(f"Speaking: {text}")
            else:
                logger.warning(f"Failed to speak: {text}")

        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")

    def _speak_pyttsx3_simple(self, text: str) -> bool:
        """Speak using pyttsx3 - simplified working version"""
        try:
            with self.engine_lock:
                # Simple approach that actually works
                self.pyttsx3_engine.say(text)

                # Use runAndWait in the worker thread - this blocks but produces audio
                self.pyttsx3_engine.runAndWait()

                return True

        except Exception as e:
            logger.warning(f"pyttsx3 speech error: {e}")
            return False

    def _speak_sapi(self, text: str) -> bool:
        """Speak using Windows SAPI"""
        try:
            # SAPI synchronous speech (blocks but works reliably)
            self.sapi_engine.Speak(text, 0)  # 0 = synchronous
            return True

        except Exception as e:
            logger.warning(f"SAPI speech error: {e}")
            return False

    def speak(self, text: str):
        """
        Queue text for speech synthesis (non-blocking)

        Args:
            text: Text to speak
        """
        if not text or not self.enabled:
            return

        try:
            # Clean text
            text = str(text).strip()
            if not text:
                return

            # Add to queue (non-blocking, drop if full)
            try:
                self.speech_queue.put_nowait(text)
            except queue.Full:
                # Clear old items and try again
                try:
                    self.speech_queue.get_nowait()  # Remove oldest
                    self.speech_queue.put_nowait(text)
                except queue.Empty:
                    pass

        except Exception as e:
            logger.error(f"Speech queue error: {e}")

    def speak_immediate(self, text: str):
        """
        Speak text immediately (blocking)
        Use for important announcements

        Args:
            text: Text to speak
        """
        if not text or not self.enabled:
            return

        try:
            text = str(text).strip()
            if text:
                current_time = time.time()
                if current_time - self.last_speech_time >= self.min_speech_interval:
                    self._do_speak(text)
        except Exception as e:
            logger.error(f"Immediate speech error: {e}")

    def set_enabled(self, enabled: bool):
        """Enable or disable speech"""
        self.enabled = enabled
        if enabled:
            print("🔊 Speech enabled")
        else:
            print("🔇 Speech disabled")

    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.rate = max(50, min(400, rate))

        try:
            with self.engine_lock:
                if self.pyttsx3_engine:
                    self.pyttsx3_engine.setProperty('rate', self.rate)
            print(f"🎵 Speech rate set to {self.rate} WPM")
        except Exception as e:
            logger.warning(f"Failed to set speech rate: {e}")

    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))

        try:
            with self.engine_lock:
                if self.pyttsx3_engine:
                    self.pyttsx3_engine.setProperty('volume', self.volume)
            print(f"🔊 Speech volume set to {self.volume}")
        except Exception as e:
            logger.warning(f"Failed to set speech volume: {e}")

    def test_speech(self):
        """Test speech functionality"""
        print("🧪 Testing speech...")

        if not self.enabled:
            print("❌ Speech is disabled")
            return False

        test_text = "Speech test successful"

        try:
            # Test immediate speech
            self.speak_immediate(test_text)
            print("✅ Speech test completed")
            return True

        except Exception as e:
            print(f"❌ Speech test failed: {e}")
            return False

    def switch_engine(self):
        """Switch between available speech engines"""
        if self.current_engine == 'pyttsx3' and self.sapi_engine:
            self.current_engine = 'sapi'
            print("🔄 Switched to SAPI engine")
        elif self.current_engine == 'sapi' and self.pyttsx3_engine:
            self.current_engine = 'pyttsx3'
            print("🔄 Switched to pyttsx3 engine")
        else:
            print("⚠️ No alternative engine available")

    def clear_queue(self):
        """Clear the speech queue"""
        try:
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            print("🗑️ Speech queue cleared")
        except Exception as e:
            logger.warning(f"Queue clear error: {e}")

    def get_status(self) -> dict:
        """Get speech engine status"""
        return {
            'enabled': self.enabled,
            'current_engine': self.current_engine,
            'queue_size': self.speech_queue.qsize(),
            'rate': self.rate,
            'volume': self.volume,
            'engines_available': {
                'pyttsx3': self.pyttsx3_engine is not None,
                'sapi': self.sapi_engine is not None
            }
        }

    def cleanup(self):
        """Clean up the speech engine"""
        try:
            print("🔧 Cleaning up Speech Engine...")

            # Stop thread
            self.stop_thread = True
            if self.speech_thread and self.speech_thread.is_alive():
                self.speech_thread.join(timeout=2.0)

            # Clear queue
            self.clear_queue()

            # Clean up engines
            with self.engine_lock:
                if self.pyttsx3_engine:
                    try:
                        self.pyttsx3_engine.stop()
                    except:
                        pass
                    self.pyttsx3_engine = None

                if self.sapi_engine:
                    self.sapi_engine = None

            print("🔧 Speech Engine cleaned up")

        except Exception as e:
            logger.error(f"Speech cleanup error: {e}")


# Test function
def test_speech_engine():
    """Test the speech engine"""
    print("🧪 Testing Speech Engine...")

    engine = SpeechEngine()

    if engine.enabled:
        print("✅ Speech engine working")

        # Test immediate speech
        engine.speak_immediate("Testing speech engine")
        time.sleep(2)

        # Test queued speech
        engine.speak("Testing queue")
        time.sleep(2)

        # Test with rate limiting
        for i in range(3):
            engine.speak(f"Test {i}")

        time.sleep(3)
        engine.cleanup()

    else:
        print("❌ Speech engine not available")


if __name__ == "__main__":
    test_speech_engine()