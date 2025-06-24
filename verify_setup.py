#!/usr/bin/env python3
"""
Quick Mobile App Verification Script
Checks if all essential files have proper content
"""

import os
from pathlib import Path


def verify_mobile_app_setup():
    """Verify the mobile app setup is complete"""
    print("🔍 ASL Mobile App Setup Verification")
    print("=" * 50)

    # Check essential files
    essential_files = {
        'main.py': 'Main app entry point',
        'app/core/asl_engine.py': 'ASL recognition engine',
        'app/screens/camera_screen.py': 'Camera screen',
        'app/screens/home_screen.py': 'Home screen',
        'requirements.txt': 'Dependencies',
        'buildozer.spec': 'Android build config'
    }

    missing_files = []
    empty_files = []

    for file_path, description in essential_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 100:  # File has some content
                print(f"✅ {file_path} - {description} ({file_size} bytes)")
            else:
                print(f"⚠️  {file_path} - {description} (EMPTY - {file_size} bytes)")
                empty_files.append(file_path)
        else:
            print(f"❌ {file_path} - {description} (MISSING)")
            missing_files.append(file_path)

    # Check for ASL model
    model_path = "assets/models/best_model.h5"
    if os.path.exists(model_path):
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"✅ {model_path} - ASL Model ({model_size:.1f} MB)")
    else:
        print(f"❌ {model_path} - ASL Model (MISSING)")
        missing_files.append(model_path)

    # Check Python packages
    print("\n📦 Checking Python Packages:")
    required_packages = ['kivy', 'tensorflow', 'opencv-python', 'numpy']

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (NOT INSTALLED)")

    # Summary
    print("\n📋 SUMMARY:")
    if missing_files:
        print(f"❌ Missing files: {len(missing_files)}")
        for f in missing_files:
            print(f"   - {f}")

    if empty_files:
        print(f"⚠️  Empty files: {len(empty_files)}")
        for f in empty_files:
            print(f"   - {f}")

    if not missing_files and not empty_files:
        print("🎉 All essential files present and have content!")
        print("🚀 Ready to test the mobile app!")
        return True
    else:
        print("🔧 Some files need attention before proceeding.")
        return False


if __name__ == "__main__":
    verify_mobile_app_setup()