#!/usr/bin/env python3
"""
Android Build Preparation Script
Prepares your ASL Mobile App for Android APK building
"""

import os
import shutil
from pathlib import Path


def create_buildozer_spec():
    """Create buildozer.spec file"""
    buildozer_content = '''[app]
title = ASL Mobile App
package.name = aslmobileapp
package.domain = org.aslmobile

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,tflite,txt,md
source.exclude_dirs = tests, bin, .git, .github, __pycache__, .pytest_cache, .venv, buildenv

version = 1.0
requirements = python3,kivy==2.1.0,numpy,pillow,plyer,android

source.main = main.py
orientation = portrait

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS
android.private_storage = False
android.ndk = 25b
android.sdk = 33
android.api = 33
android.minapi = 21
android.enable_androidx = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
'''

    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.write(buildozer_content)
    print("Created buildozer.spec")


def create_android_main():
    """Create Android-optimized main entry point"""
    android_main_content = '''#!/usr/bin/env python3
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
                return Label(text="ASL Mobile App\\n\\nLoading...")

        SimpleApp().run()

if __name__ == "__main__":
    main()
'''

    with open('main_android.py', 'w', encoding='utf-8') as f:
        f.write(android_main_content)
    print("Created main_android.py")


def setup_directory_structure():
    """Setup proper directory structure for Android build"""

    # Create necessary directories
    directories = [
        'assets/models',
        'assets/images',
        'android_src/main/java/org/aslmobile/aslmobileapp',
        'android_src/main/res/values',
        'android_src/main/res/mipmap-hdpi',
        'android_src/main/res/mipmap-mdpi',
        'android_src/main/res/mipmap-xhdpi',
        'android_src/main/res/mipmap-xxhdpi',
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


def create_android_manifest():
    """Create Android manifest additions"""
    manifest_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Camera permissions -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera" android:required="true" />
    <uses-feature android:name="android.hardware.camera.front" android:required="false" />

    <!-- Storage permissions -->
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

    <!-- Audio permissions -->
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />

    <!-- Network -->
    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:label="ASL Mobile App"
        android:icon="@mipmap/ic_launcher"
        android:theme="@style/Theme.AppCompat.Light"
        android:hardwareAccelerated="true">

        <activity android:name=".MainActivity"
                  android:screenOrientation="portrait"
                  android:configChanges="orientation|screenSize|keyboardHidden">
        </activity>
    </application>
</manifest>
'''

    manifest_path = Path('android_src/main/AndroidManifest.xml')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    print(f"Created {manifest_path}")


def create_main_activity():
    """Create MainActivity.java for camera permissions"""
    java_content = '''package org.aslmobile.aslmobileapp;

import android.content.pm.PackageManager;
import android.Manifest;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import org.kivy.android.PythonActivity;

public class MainActivity extends PythonActivity {
    private static final int CAMERA_PERMISSION_REQUEST = 1;
    private static final int STORAGE_PERMISSION_REQUEST = 2;

    @Override
    protected void onStart() {
        super.onStart();

        // Request camera permission
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                new String[]{Manifest.permission.CAMERA}, 
                CAMERA_PERMISSION_REQUEST);
        }

        // Request storage permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                new String[]{
                    Manifest.permission.WRITE_EXTERNAL_STORAGE,
                    Manifest.permission.READ_EXTERNAL_STORAGE
                }, 
                STORAGE_PERMISSION_REQUEST);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        switch (requestCode) {
            case CAMERA_PERMISSION_REQUEST:
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // Camera permission granted
                }
                break;
            case STORAGE_PERMISSION_REQUEST:
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // Storage permission granted
                }
                break;
        }
    }
}
'''

    java_path = Path('android_src/main/java/org/aslmobile/aslmobileapp/MainActivity.java')
    with open(java_path, 'w', encoding='utf-8') as f:
        f.write(java_content)
    print(f"Created {java_path}")


def create_app_icon():
    """Create a simple app icon placeholder"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a simple icon
        img = Image.new('RGB', (192, 192), color='#2196F3')
        draw = ImageDraw.Draw(img)

        # Draw ASL text
        try:
            # Try to use a font
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()

        # Draw text
        text = "ASL"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (192 - text_width) // 2
        y = (192 - text_height) // 2

        draw.text((x, y), text, fill='white', font=font)

        # Save different sizes
        sizes = [
            ('android_src/main/res/mipmap-mdpi/ic_launcher.png', 48),
            ('android_src/main/res/mipmap-hdpi/ic_launcher.png', 72),
            ('android_src/main/res/mipmap-xhdpi/ic_launcher.png', 96),
            ('android_src/main/res/mipmap-xxhdpi/ic_launcher.png', 144),
        ]

        for path, size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(path)
            print(f"Created icon: {path}")

    except ImportError:
        print("PIL not available, skipping icon creation")
    except Exception as e:
        print(f"Icon creation failed: {e}")


def copy_model_files():
    """Copy model files to assets"""
    model_src = Path('assets/models/best_model.tflite')

    if model_src.exists():
        print(f"Model file found: {model_src}")
    else:
        print(f"Model file not found: {model_src}")
        print("   You'll need to add your .tflite model file to assets/models/")


def create_requirements_txt():
    """Create requirements.txt for reference"""
    requirements = '''# Android APK Requirements
# These are handled by buildozer.spec, but listed here for reference

kivy==2.1.0
numpy
pillow
plyer
android

# Desktop development requirements (not needed for APK)
# opencv-python-headless
# tensorflow
# pyttsx3
# pywin32
'''

    with open('requirements_android.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    print("Created requirements_android.txt")


def create_gitignore():
    """Create .gitignore for Android build files"""
    gitignore_content = '''# Buildozer files
.buildozer/
bin/
*.apk
*.aab

# Android build files
local.properties
*.keystore

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
.venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''

    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("Created/updated .gitignore")


def main():
    """Setup Android build environment"""
    print("Setting up Android build environment...")
    print("=" * 50)

    # Check current directory
    current_dir = Path.cwd()
    print(f"Working directory: {current_dir}")

    # Setup steps
    setup_directory_structure()
    create_buildozer_spec()
    create_android_main()
    create_android_manifest()
    create_main_activity()
    create_app_icon()
    copy_model_files()
    create_requirements_txt()
    create_gitignore()

    print("\n" + "=" * 50)
    print("Android build setup complete!")
    print("\nNext steps:")
    print("1. Install WSL2 (if on Windows)")
    print("2. Setup buildozer in WSL2:")
    print("   sudo apt update && sudo apt install -y python3-pip")
    print("   pip3 install buildozer cython==0.29.33")
    print("3. Copy project to WSL2:")
    print("   cp -r /mnt/c/path/to/your/project ~/asl_app")
    print("4. Build APK:")
    print("   cd ~/asl_app")
    print("   buildozer android debug")
    print("5. Find APK in bin/ folder")
    print("\nYour APK will be: bin/aslmobileapp-1.0-arm64-v8a-debug.apk")
    print("\nInstall on phone:")
    print("   adb install bin/aslmobileapp-1.0-arm64-v8a-debug.apk")
    print("   Or transfer APK to phone and install manually")


if __name__ == "__main__":
    main()