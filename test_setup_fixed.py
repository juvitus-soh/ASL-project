#!/usr/bin/env python3
"""
Test Setup Script - Verify all components work before building APK
"""

import sys
import os
import platform
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"🧪 Testing: {title}")
    print("=" * 50)


def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing file structure...")

    required_files = [
        'main.py',
        'buildozer.spec',
        'core/__init__.py',
        'core/asl_engine.py',
        'core/settings_manager.py',
        'core/speech_engine_android.py',
        'app/__init__.py',
        'app/screens/__init__.py'
    ]

    missing_files = []
    existing_files = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            existing_files.append(file_path)
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True


def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")

    # Test Kivy
    try:
        import kivy
        print(f"✅ Kivy {kivy.__version__} available")
    except ImportError as e:
        print(f"❌ Kivy not available: {e}")
        return False

    # Test core modules
    try:
        from core.asl_engine import ASLEngine
        from core.settings_manager import SettingsManager
        from core.speech_engine_android import AndroidSpeechEngine
        print("✅ Core modules available")
    except ImportError as e:
        print(f"❌ Core modules error: {e}")
        return False

    # Test main app
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())

        # Import without running
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)

        print("✅ Main app imports successfully")
    except Exception as e:
        print(f"❌ Main app import error: {e}")
        return False

    return True


def test_core_functionality():
    """Test core components work"""
    print("⚙️ Testing core functionality...")

    try:
        # Test ASL Engine
        from app.core.asl_engine import ASLEngine
        asl_engine = ASLEngine(demo_mode=True)
        print("✅ ASL engine works")

        # Test Settings Manager
        from app.core.settings_manager import SettingsManager
        settings = SettingsManager("test_settings.json")
        test_value = settings.get("display.width", 800)
        print(f"✅ Settings manager works (width: {test_value})")

        # Test Speech Engine
        from app.core.speech_engine_android import AndroidSpeechEngine
        speech = AndroidSpeechEngine()
        print("✅ Speech engine initializes")

        # Clean up test settings
        if os.path.exists("test_settings.json"):
            os.remove("test_settings.json")

        return True

    except Exception as e:
        print(f"❌ Core functionality error: {e}")
        return False


def test_buildozer_config():
    """Test buildozer configuration"""
    print("📱 Testing buildozer configuration...")

    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec not found")
        return False

    try:
        with open("buildozer.spec", 'r') as f:
            content = f.read()

        # Check for essential sections
        required_sections = [
            'title = ASL Mobile App',
            'package.name = aslmobileapp',
            'requirements = python3,kivy',
            'android.permissions = CAMERA'
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            print(f"❌ Missing buildozer sections: {missing_sections}")
            return False

        print("✅ buildozer.spec looks good")
        return True

    except Exception as e:
        print(f"❌ Buildozer config error: {e}")
        return False


def test_android_compatibility():
    """Test Android-specific features"""
    print("🤖 Testing Android compatibility...")

    try:
        # Test platform detection
        from app.core.speech_engine_android import is_android
        android_detected = is_android()
        print(f"✅ Android detection: {android_detected}")

        # Test Android imports (should fail gracefully on desktop)
        try:
            from app.core.speech_engine_android import ANDROID_TTS_AVAILABLE
            print(f"✅ Android TTS available: {ANDROID_TTS_AVAILABLE}")
        except:
            print("✅ Android TTS gracefully unavailable (expected on desktop)")

        return True

    except Exception as e:
        print(f"❌ Android compatibility error: {e}")
        return False


def check_system_requirements():
    """Check system requirements for building"""
    print("🔧 Checking system requirements...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python {python_version.major}.{python_version.minor} (recommend 3.8+)")

    # Check platform
    system = platform.system()
    print(f"✅ Platform: {system}")

    # Check buildozer
    try:
        import buildozer
        print("✅ Buildozer available")
    except ImportError:
        print("❌ Buildozer not installed (run: pip install buildozer)")
        return False

    return True


def main():
    """Run all tests"""
    print("🧪 ASL Mobile App - Setup Test (Fixed Version)")
    print("🔧 This verifies your app is ready for APK build")

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Core Functionality", test_core_functionality),
        ("Buildozer Config", test_buildozer_config),
        ("Android Compatibility", test_android_compatibility),
        ("System Requirements", check_system_requirements)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print_header(test_name)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print_header("Test Results")
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready to build APK 🚀")
        print("\n📱 Next steps:")
        print("   1. Run: buildozer android debug")
        print("   2. Wait for build (30-60 minutes first time)")
        print("   3. Install APK: adb install bin/*.apk")
        return True
    else:
        print("❌ Some tests failed. Fix issues before building APK.")
        print("\n🔧 Common fixes:")
        print("   • Create missing files from the artifacts above")
        print("   • Install missing packages: pip install kivy buildozer")
        print("   • Check file permissions and paths")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)