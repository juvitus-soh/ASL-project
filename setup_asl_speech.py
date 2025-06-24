#!/usr/bin/env python3
"""
Complete ASL Mobile App Setup Script
Copies model files, fixes imports, and sets up the app
"""

import shutil
import os
from pathlib import Path


def main():
    print("🚀 Setting up ASL Mobile App with trained model...")

    # 1. Copy model files
    copy_model_files()

    # 2. Fix screen imports
    fix_screen_imports()

    # 3. Install dependencies
    install_dependencies()

    # 4. Test setup
    test_setup()

    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. python main.py  # Test the app")
    print("2. If working: buildozer android debug  # Build APK")


def copy_model_files():
    """Copy trained model files"""
    print("\n📁 Copying model files...")

    asl_project_path = Path("C:/Users/user/PycharmProjects/asl_project")
    assets_models_path = Path("assets/models")

    # Create directory
    assets_models_path.mkdir(parents=True, exist_ok=True)

    # Copy model files
    model_files = [
        ("results/checkpoints/best_model.h5", "best_model.h5"),
        ("results/models/best_model.tflite", "best_model.tflite")
    ]

    for src_rel, dst_name in model_files:
        src = asl_project_path / src_rel
        dst = assets_models_path / dst_name

        if src.exists():
            try:
                shutil.copy2(src, dst)
                size_mb = dst.stat().st_size / (1024 * 1024)
                print(f"✅ Copied {dst_name} ({size_mb:.1f}MB)")
            except Exception as e:
                print(f"❌ Error copying {dst_name}: {e}")
        else:
            print(f"❌ Source not found: {src}")


def fix_screen_imports():
    """Fix import statements in screen files"""
    print("\n🔧 Fixing screen imports...")

    screen_files = [
        "app/screens/home_screen.py",
        "app/screens/camera_screen.py",
        "app/screens/settings_screen.py",
        "app/screens/history_screen.py",
        "app/screens/tutorial_screen.py",
        "app/screens/about_screen.py"
    ]

    old_import = "from kivy.uix.screen import Screen"
    new_import = "from kivy.uix.screenmanager import Screen"

    for file_path in screen_files:
        path = Path(file_path)
        if path.exists():
            try:
                content = path.read_text()
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    path.write_text(content)
                    print(f"✅ Fixed imports in {path.name}")
                else:
                    print(f"📄 {path.name} already correct")
            except Exception as e:
                print(f"❌ Error fixing {path.name}: {e}")
        else:
            print(f"❌ File not found: {file_path}")


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Checking dependencies...")

    dependencies = [
        ("tensorflow", "pip install tensorflow"),
        ("pyttsx3", "pip install pyttsx3"),
        ("opencv-python", "pip install opencv-python"),
        ("numpy", "pip install numpy")
    ]

    for module, install_cmd in dependencies:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            print(f"❌ {module} missing - run: {install_cmd}")


def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")

    # Check if model files exist
    model_files = [
        "assets/models/best_model.h5",
        "assets/models/best_model.tflite"
    ]

    model_found = False
    for model_file in model_files:
        if Path(model_file).exists():
            print(f"✅ Found: {model_file}")
            model_found = True
        else:
            print(f"❌ Missing: {model_file}")

    if model_found:
        print("✅ At least one model file found!")
    else:
        print("❌ No model files found!")

    # Test core imports
    print("\n🔍 Testing imports...")
    try:
        import sys
        sys.path.insert(0, 'app')

        from app.core.asl_engine import ASLEngine
        print("✅ ASLEngine import successful")

        # Test engine initialization
        engine = ASLEngine()
        stats = engine.get_statistics()
        print(f"✅ Engine initialized - Model loaded: {stats['model_loaded']}")

    except Exception as e:
        print(f"❌ Import test failed: {e}")


if __name__ == "__main__":
    main()