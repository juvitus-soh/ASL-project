#!/usr/bin/env python3
"""
ASL Mobile App - Main Application Entry Point
Fixed version that properly uses your original screen classes and fixes model loading
UPDATED: Added missing methods for camera screen integration
"""

import os
import sys
import logging
from pathlib import Path

# !/usr/bin/env python3
"""
Logging Configuration - Reduce debug spam
Place this at the top of main.py to reduce COM debug messages
"""

import logging
import sys
import os


def configure_logging():
    """Configure logging to reduce spam and improve performance"""

    # Set root logging level
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

    # ✅ CRITICAL: Reduce COM spam that causes crashes
    # These are the specific loggers causing issues
    spam_loggers = [
        'comtypes',
        'comtypes.client',
        'comtypes.client._managing',
        'comtypes.client._generate',
        'comtypes._comobject',
        'comtypes._vtbl',
        'comtypes._post_coinit',
        'comtypes._post_coinit.unknwn'
    ]

    # Set all COM loggers to WARNING level (reduces spam significantly)
    for logger_name in spam_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
        # Disable propagation to prevent spam in parent loggers
        logger.propagate = False

    # Keep important loggers at INFO level
    important_loggers = [
        '__main__',
        'app.core.asl_engine',
        'app.core.speech_engine',
        'app.screens.camera_screen',
        'kivy'
    ]

    for logger_name in important_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

    # Reduce Kivy debug spam too
    kivy_spam_loggers = [
        'kivy.graphics',
        'kivy.graphics.opengl',
        'kivy.graphics.texture',
        'kivy.core',
        'kivy.core.camera'
    ]

    for logger_name in kivy_spam_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)

    print("🔧 Logging configured - reduced debug spam")


# Call this function at the start of your main.py
if __name__ == "__main__":
    configure_logging()
    print("✅ Logging configuration applied")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Core Kivy imports
try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.clock import Clock
    from kivy.metrics import dp

    logger.info("✅ Core modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import core modules: {e}")
    sys.exit(1)

# Import your core classes
try:
    from app.core.settings_manager import SettingsManager
    from app.core.asl_engine import ASLEngine
    from app.core.speech_engine import SpeechEngine

    logger.info("✅ Core classes imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import core classes: {e}")
    sys.exit(1)

# Try to import your original screen classes
SCREENS_AVAILABLE = False
try:
    from app.screens.home_screen import HomeScreen
    from app.screens.camera_screen import CameraScreen
    from app.screens.about_screen import AboutScreen
    from app.screens.history_screen import HistoryScreen
    from app.screens.tutorial_screen import TutorialScreen
    from app.screens.settings_screen import SettingsScreen

    SCREENS_AVAILABLE = True
    logger.info("✅ Original screen classes imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import original screens: {e}")
    logger.info("🔄 Will create fallback screens")


class ASLMobileApp(App):
    """Main ASL Mobile Application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ASL Mobile App"
        self.icon = "assets/icon.png"  # If you have an icon

        # Core managers
        self.settings_manager = None
        self.asl_engine = None
        self.speech_engine = None
        self.screen_manager = None

        # App state
        self.is_initialized = False

        # ✅ Word/sentence building state (for camera screen)
        self.current_word = ""
        self.current_sentence = ""
        self.recognition_history = []

    def build(self):
        """Build the application"""
        logger.info("🚀 Starting ASL Mobile App...")

        try:
            # Initialize core components
            if not self.initialize_core_components():
                return self.build_error_screen("Failed to initialize core components")

            # Build main screen manager
            sm = self.build_screen_manager()
            if not sm:
                return self.build_error_screen("Failed to build screen manager")

            self.screen_manager = sm
            self.is_initialized = True

            logger.info("🎯 ASL Mobile App started successfully")

            # Try to log status, but don't crash if it fails
            try:
                self.log_status()
            except Exception as e:
                logger.warning(f"⚠️ Could not log status: {e}")

            return sm

        except Exception as e:
            logger.error(f"❌ Error building app: {e}")
            return self.build_error_screen(str(e))

    def initialize_core_components(self):
        """Initialize all core components"""
        try:
            logger.info("🚀 ASL Mobile App initializing...")

            # Initialize settings manager
            self.settings_manager = SettingsManager()
            logger.info("⚙️ Settings manager initialized")

            # Initialize ASL engine
            self.asl_engine = ASLEngine()

            # Try to load lite model if it exists
            model_path = self.settings_manager.get_setting('model_path', 'assets/models/best_model.tflite')
            if os.path.exists(model_path):
                logger.info(f"🔄 Loading TensorFlow Lite model from {model_path}")
                success = self.asl_engine.load_model(model_path)
                if success:
                    logger.info("✅ TensorFlow Lite model loaded successfully")
                else:
                    logger.warning("⚠️ TensorFlow Lite model failed to load")
            else:
                logger.info(f"📁 TensorFlow Lite model not found at {model_path}")
                logger.info("💡 Place your .tflite model at: assets/models/best_model.tflite")

            logger.info(f"🤖 ASL engine initialized (model_loaded: {self.asl_engine.model_loaded})")
            logger.info(f"   Model type: {self.asl_engine.model_type}")
            logger.info(f"   Demo mode: {self.asl_engine.demo_mode}")

            # Initialize speech engine (async)
            logger.info("🔊 Initializing Speech Engine (non-blocking)...")
            self.speech_engine = SpeechEngine()
            logger.info("🔊 Speech engine initialized")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize core components: {e}")
            return False

    def build_screen_manager(self):
        """Build the screen manager with all screens"""
        try:
            sm = ScreenManager()

            if SCREENS_AVAILABLE:
                # Use your original sophisticated screen classes
                logger.info("✅ Using original screen classes")

                # Create and add your original screens with proper names
                home_screen = HomeScreen()
                home_screen.name = 'home'
                sm.add_widget(home_screen)

                camera_screen = CameraScreen()
                camera_screen.name = 'camera'
                sm.add_widget(camera_screen)

                tutorial_screen = TutorialScreen()
                tutorial_screen.name = 'tutorial'
                sm.add_widget(tutorial_screen)

                history_screen = HistoryScreen()
                history_screen.name = 'history'
                sm.add_widget(history_screen)

                settings_screen = SettingsScreen()
                settings_screen.name = 'settings'
                sm.add_widget(settings_screen)

                about_screen = AboutScreen()
                about_screen.name = 'about'
                sm.add_widget(about_screen)

            else:
                # Fallback to simple screens if imports failed
                logger.info("🔄 Using fallback screen classes")
                sm.add_widget(self.create_fallback_home_screen())
                sm.add_widget(self.create_fallback_camera_screen())
                sm.add_widget(self.create_fallback_tutorial_screen())
                sm.add_widget(self.create_fallback_history_screen())
                sm.add_widget(self.create_fallback_settings_screen())
                sm.add_widget(self.create_fallback_about_screen())

            # Set starting screen
            sm.current = 'home'

            # Debug: List all available screens
            screen_names = [screen.name for screen in sm.screens]
            logger.info(f"🖥️ Available screens: {screen_names}")

            return sm

        except Exception as e:
            logger.error(f"❌ Error building screen manager: {e}")
            return None

    # ✅ CAMERA SCREEN INTEGRATION METHODS
    def add_letter(self, letter: str, confidence: float = 0.0):
        """Add a letter to the current word (called by camera screen)"""
        if letter and letter.isalpha():
            # Convert to uppercase for consistency
            letter = letter.upper()

            # Only add if it's different from the last letter (prevent duplicates)
            if not self.current_word or self.current_word[-1] != letter:
                self.current_word += letter

                # Add to history
                self.recognition_history.append({
                    'type': 'letter',
                    'content': letter,
                    'confidence': confidence,
                    'timestamp': Clock.get_time()
                })

                logger.info(f"📝 Added letter: {letter}, word: {self.current_word}")

                # Speak letter if enabled
                try:
                    if self.speech_engine:
                        self.speech_engine.speak(letter)
                except Exception as e:
                    logger.warning(f"Speech failed: {e}")

    def complete_word(self):
        """Complete current word and add to sentence (called by camera screen)"""
        if self.current_word:
            # Add word to sentence
            if self.current_sentence:
                self.current_sentence += " " + self.current_word
            else:
                self.current_sentence = self.current_word

            completed_word = self.current_word

            # Add to history
            self.recognition_history.append({
                'type': 'word',
                'content': completed_word,
                'timestamp': Clock.get_time()
            })

            logger.info(f"✅ Word completed: {completed_word}")
            logger.info(f"📄 Sentence: {self.current_sentence}")

            # Clear current word
            self.current_word = ""

            # Speak word completion if enabled
            try:
                if self.speech_engine:
                    self.speech_engine.speak(f"Word: {completed_word}")
            except Exception as e:
                logger.warning(f"Speech failed: {e}")

            return completed_word

        return ""

    def delete_last_letter(self):
        """Delete the last letter from current word (called by camera screen)"""
        if self.current_word:
            deleted_letter = self.current_word[-1]
            self.current_word = self.current_word[:-1]

            logger.info(f"⬅️ Deleted letter: {deleted_letter}, word: {self.current_word}")

            # Add to history
            self.recognition_history.append({
                'type': 'delete',
                'content': deleted_letter,
                'timestamp': Clock.get_time()
            })

        elif self.current_sentence:
            # If no current word, move last word back to editing
            words = self.current_sentence.split()
            if words:
                self.current_word = words[-1]
                self.current_sentence = " ".join(words[:-1])
                logger.info(f"⬅️ Moved last word back to editing: {self.current_word}")

    def speak_current_sentence(self):
        """Speak the current sentence (called by camera screen)"""
        # Build full text
        text_to_speak = self.current_sentence
        if self.current_word:
            text_to_speak = text_to_speak + " " + self.current_word if text_to_speak else self.current_word

        if text_to_speak:
            logger.info(f"🔊 Speaking: {text_to_speak}")
            try:
                if self.speech_engine:
                    self.speech_engine.speak(text_to_speak)
            except Exception as e:
                logger.warning(f"Speech failed: {e}")
        else:
            logger.info("🔇 Nothing to speak")

    def clear_current_text(self):
        """Clear current word and sentence"""
        self.current_word = ""
        self.current_sentence = ""
        logger.info("🗑️ Cleared current text")

    def get_recognition_history(self, limit: int = 50):
        """Get recent recognition history"""
        return self.recognition_history[-limit:] if self.recognition_history else []

    def switch_screen(self, screen_name):
        """Switch to a specific screen (called by your original screens)"""
        if self.screen_manager and hasattr(self.screen_manager, 'current'):
            self.screen_manager.current = screen_name
            logger.info(f"🖥️ Switched to screen: {screen_name}")
        else:
            logger.error(f"❌ Cannot switch to screen {screen_name}: no screen manager")

    def create_fallback_home_screen(self):
        """Create a fallback home screen"""

        class FallbackHomeScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='home', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                # Title
                layout.add_widget(Label(
                    text='ASL Mobile App\n(Fallback Mode)',
                    font_size='24sp',
                    size_hint=(1, 0.3),
                    halign='center'
                ))

                # Start button
                start_btn = Button(
                    text='Start Camera',
                    size_hint=(1, 0.2),
                    font_size='18sp',
                    background_color=(0, 0.8, 0, 1)
                )
                start_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'camera'))
                layout.add_widget(start_btn)

                # Other buttons
                for screen_name, text in [('tutorial', '📚 Tutorial'), ('history', '📊 History'),
                                          ('settings', '⚙️ Settings'), ('about', 'ℹ️ About')]:
                    btn = Button(text=text, size_hint=(1, 0.15), font_size='16sp')
                    btn.bind(on_press=lambda x, screen=screen_name: setattr(self.manager, 'current', screen))
                    layout.add_widget(btn)

                self.add_widget(layout)

        return FallbackHomeScreen()

    def create_fallback_camera_screen(self):
        """Create a fallback camera screen"""

        class FallbackCameraScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='camera', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                layout.add_widget(Label(
                    text='ASL Camera\n(Fallback Mode)',
                    font_size='20sp',
                    size_hint=(1, 0.3)
                ))

                layout.add_widget(Label(
                    text='Camera functionality would be here',
                    size_hint=(1, 0.5)
                ))

                back_btn = Button(
                    text='← Back to Home',
                    size_hint=(1, 0.2),
                    font_size='18sp'
                )
                back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
                layout.add_widget(back_btn)

                self.add_widget(layout)

        return FallbackCameraScreen()

    def create_fallback_tutorial_screen(self):
        """Create a fallback tutorial screen"""

        class FallbackTutorialScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='tutorial', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                layout.add_widget(Label(
                    text='Tutorial',
                    font_size='24sp',
                    size_hint=(1, 0.2)
                ))

                layout.add_widget(Label(
                    text='Tutorial content would be here',
                    size_hint=(1, 0.6)
                ))

                back_btn = Button(
                    text='← Back',
                    size_hint=(1, 0.2)
                )
                back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
                layout.add_widget(back_btn)

                self.add_widget(layout)

        return FallbackTutorialScreen()

    def create_fallback_history_screen(self):
        """Create a fallback history screen"""

        class FallbackHistoryScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='history', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                layout.add_widget(Label(
                    text='Recognition History',
                    font_size='24sp',
                    size_hint=(1, 0.2)
                ))

                layout.add_widget(Label(
                    text='History would be shown here',
                    size_hint=(1, 0.6)
                ))

                back_btn = Button(
                    text='← Back',
                    size_hint=(1, 0.2)
                )
                back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
                layout.add_widget(back_btn)

                self.add_widget(layout)

        return FallbackHistoryScreen()

    def create_fallback_settings_screen(self):
        """Create a fallback settings screen"""

        class FallbackSettingsScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='settings', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                layout.add_widget(Label(
                    text='Settings',
                    font_size='24sp',
                    size_hint=(1, 0.2)
                ))

                layout.add_widget(Label(
                    text='Settings would be here',
                    size_hint=(1, 0.6)
                ))

                back_btn = Button(
                    text='← Back',
                    size_hint=(1, 0.2)
                )
                back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
                layout.add_widget(back_btn)

                self.add_widget(layout)

        return FallbackSettingsScreen()

    def create_fallback_about_screen(self):
        """Create a fallback about screen"""

        class FallbackAboutScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(name='about', **kwargs)
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

                layout.add_widget(Label(
                    text='About ASL Recognition',
                    font_size='24sp',
                    size_hint=(1, 0.2)
                ))

                layout.add_widget(Label(
                    text='About information would be here',
                    size_hint=(1, 0.6)
                ))

                back_btn = Button(
                    text='← Back',
                    size_hint=(1, 0.2)
                )
                back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
                layout.add_widget(back_btn)

                self.add_widget(layout)

        return FallbackAboutScreen()

    def build_error_screen(self, error_msg):
        """Build error screen when app fails to start"""
        logger.error(f"❌ Building error screen: {error_msg}")

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(
            text='ASL Mobile App\nError',
            font_size='24sp',
            size_hint=(1, 0.3),
            halign='center',
            text_size=(None, None)
        ))

        layout.add_widget(Label(
            text=f'App failed to start:\n{error_msg}\n\nPlease check logs.',
            font_size='16sp',
            size_hint=(1, 0.7),
            halign='center',
            text_size=(None, None)
        ))

        return layout

    def log_status(self):
        """Log current app status"""
        if self.asl_engine:
            # Use getattr with defaults for attributes that might not exist
            model_status = {
                'loaded': getattr(self.asl_engine, 'model_loaded', False),
                'path': getattr(self.asl_engine, 'model_path', None),
                'type': getattr(self.asl_engine, 'model_type', 'unknown'),
                'input_shape': getattr(self.asl_engine, 'input_shape', None),
                'classes': getattr(self.asl_engine, 'num_classes', 0),
                'class_names': getattr(self.asl_engine, 'class_names', [])[:10],  # Show first 10
                'demo_mode': getattr(self.asl_engine, 'demo_mode', True),
                'last_prediction': getattr(self.asl_engine, 'last_prediction', None),
                'last_confidence': getattr(self.asl_engine, 'last_confidence', 0.0),
                'prediction_count': len(getattr(self.asl_engine, 'prediction_history', []))
            }
            logger.info(f"📊 Model status: {model_status}")

        if self.speech_engine:
            logger.info("🔊 Speech engine ready")

        # Log current text state
        logger.info(f"📝 Current word: '{self.current_word}'")
        logger.info(f"📄 Current sentence: '{self.current_sentence}'")

    def on_stop(self):
        """Clean up when app stops"""
        logger.info("🛑 ASL Mobile App stopping...")

        # Clean up ASL engine
        if self.asl_engine:
            self.asl_engine.cleanup()
            logger.info("🔧 ASL Engine cleaned up")

        # Clean up speech engine
        if self.speech_engine:
            self.speech_engine.cleanup()
            logger.info("🔊 Speech Engine cleaned up")

        logger.info("🛑 ASL Mobile App stopped")


def main():
    """Main entry point"""
    logger.info("🚀 Starting ASL Mobile App...")

    # Create and run the app
    app = ASLMobileApp()
    app.run()


if __name__ == "__main__":
    main()