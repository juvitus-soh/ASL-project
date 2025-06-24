#!/usr/bin/env python3
"""
ASL Mobile App - Android Entry Point
"""

import os
import sys
import platform
from pathlib import Path

# Detect platform
IS_ANDROID = platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ

if IS_ANDROID:
    print("Running on Android")

    # Request permissions
    try:
        from android.permissions import request_permissions, Permission
        permissions = [Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
        request_permissions(permissions)
        print("Permissions requested")
    except ImportError:
        print("Android permissions not available")

# Add paths
base_path = Path(__file__).parent
sys.path.insert(0, str(base_path))

def main():
    """Main entry point"""
    print("Starting ASL Mobile App...")

    try:
        # Import your existing app
        import main as app_main

        # Create and run app
        app = app_main.ASLMobileApp()

        # Android-specific settings
        if IS_ANDROID:
            # Disable speech on Android initially
            if hasattr(app, 'speech_engine'):
                app.speech_engine.set_enabled(False)
            print("Android mode enabled")

        app.run()

    except Exception as e:
        print(f"Error: {e}")

        # Fallback basic app
        from kivy.app import App
        from kivy.uix.label import Label

        class SimpleApp(App):
            def build(self):
                return Label(text="ASL Mobile App\n\nLoading...")

        SimpleApp().run()

if __name__ == "__main__":
    main()
