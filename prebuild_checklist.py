#!/usr/bin/env python3
"""
Pre-Build Checklist for ASL Mobile App
Ensures everything is ready for Android APK build
"""

import os
import sys
import platform
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def check_project_structure():
    """Check if all required files and directories exist"""
    print("📁 Checking project structure...")

    required_items = {
        'files': [
            'main.py',
            'buildozer.spec',
            'app/__init__.py',
            'app/core/__init__.py',
            'app/screens/__init__.py',
        ],
        'directories': [
            'app/',
            'app/core/',
            'app/screens/',
            'app/utils/',
            'app/widgets/',
            'assets/',
            'assets/models/',
        ]
    }

    missing = []
    present = []

    # Check files
    for file_path in required_items['files']:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            present.append(file_path)
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)

    # Check directories
    for dir_path in required_items['directories']:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
            present.append(dir_path)
        else:
            print(f"❌ {dir_path}")
            missing.append(dir_path)

    return len(missing) == 0, missing


def check_assets():
    """Check if assets are properly organized"""
    print("🎨 Checking assets...")

    assets_to_check = [
        'assets/models/best_model.tflite',
        'assets/models/best_model.h5',
        'assets/images/',
    ]

    found_assets = []
    missing_assets = []

    for asset in assets_to_check:
        if os.path.exists(asset):
            print(f"✅ {asset}")
            found_assets.append(asset)
        else:
            print(f"⚠️ {asset} (optional)")
            missing_assets.append(asset)

    # Check model files specifically
    has_tflite = os.path.exists('assets/models/best_model.tflite')
    has_h5 = os.path.exists('assets/models/best_model.h5')

    if has_tflite:
        print("🤖 TensorFlow Lite model found - Perfect for Android!")
    elif has_h5:
        print("🤖 TensorFlow model found - Will work but TFLite is better for mobile")
    else:
        print("⚠️ No ML models found - App will run in demo mode")

    return True, missing_assets


def check_buildozer_config():
    """Check buildozer.spec configuration"""
    print("⚙️ Checking buildozer configuration...")

    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec not found")
        return False, ["buildozer.spec missing"]

    try:
        with open('buildozer.spec', 'r') as f:
            content = f.read()

        required_settings = {
            'title = ASL Mobile App': 'App title',
            'package.name = aslmobileapp': 'Package name',
            'requirements = python3,kivy': 'Basic requirements',
            'android.permissions = CAMERA': 'Camera permission',
            'android.api = 33': 'Target API (should be 30+)',
        }

        issues = []
        for setting, description in required_settings.items():
            if setting in content:
                print(f"✅ {description}")
            else:
                print(f"⚠️ {description} - check manually")
                issues.append(description)

        return len(issues) == 0, issues

    except Exception as e:
        print(f"❌ Error reading buildozer.spec: {e}")
        return False, [str(e)]


def check_python_environment():
    """Check Python environment and dependencies"""
    print("🐍 Checking Python environment...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python {python_version.major}.{python_version.minor} (recommend 3.8+)")

    # Check critical imports
    critical_packages = [
        ('kivy', 'Kivy UI framework'),
        ('numpy', 'NumPy for numerical operations'),
        ('PIL', 'Pillow for image processing'),
    ]

    missing_packages = []
    for package, description in critical_packages:
        try:
            __import__(package)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description}")
            missing_packages.append(package)

    # Check buildozer
    try:
        import buildozer
        print("✅ Buildozer available")
    except ImportError:
        print("❌ Buildozer not installed")
        missing_packages.append('buildozer')

    return len(missing_packages) == 0, missing_packages


def check_system_requirements():
    """Check system requirements for building"""
    print("💻 Checking system requirements...")

    system = platform.system()
    print(f"✅ Platform: {system}")

    recommendations = []

    if system == "Windows":
        print("ℹ️ Windows detected - Consider using WSL2 for better buildozer support")
        recommendations.append("Consider WSL2 for buildozer")

    elif system == "Darwin":  # macOS
        print("ℹ️ macOS detected - Buildozer should work well")

    elif system == "Linux":
        print("✅ Linux detected - Optimal for buildozer")

    # Check available disk space (rough estimate)
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024 ** 3)  # GB
        if free_space > 10:
            print(f"✅ Available disk space: {free_space:.1f} GB")
        else:
            print(f"⚠️ Available disk space: {free_space:.1f} GB (recommend 10+ GB)")
            recommendations.append("Free up disk space (10+ GB recommended)")
    except:
        print("⚠️ Could not check disk space")

    return True, recommendations


def create_missing_files():
    """Create any missing essential files"""
    print("🔧 Creating missing essential files...")

    # Create basic icon if missing
    icon_path = Path('assets/images/icons/app_icon.png')
    if not icon_path.exists():
        icon_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {icon_path.parent}")
        print(f"⚠️ Add your app icon at: {icon_path}")

    # Create presplash directory if missing
    presplash_path = Path('assets/images/presplash.png')
    if not presplash_path.exists():
        presplash_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"⚠️ Add your presplash image at: {presplash_path}")

    return True


def main():
    """Run all pre-build checks"""
    print("🚀 ASL Mobile App - Pre-Build Checklist")
    print("📋 Ensuring your app is ready for Android APK build")

    checks = [
        ("Project Structure", check_project_structure),
        ("Assets", check_assets),
        ("Buildozer Config", check_buildozer_config),
        ("Python Environment", check_python_environment),
        ("System Requirements", check_system_requirements),
    ]

    all_passed = True
    issues = []

    for check_name, check_func in checks:
        print_header(check_name)
        try:
            passed, problems = check_func()
            if passed:
                print(f"✅ {check_name}: PASSED")
            else:
                print(f"⚠️ {check_name}: ISSUES FOUND")
                all_passed = False
                issues.extend(problems)
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}")
            all_passed = False
            issues.append(f"{check_name}: {e}")

    # Create missing files
    print_header("Creating Missing Files")
    create_missing_files()

    # Final report
    print_header("BUILD READINESS REPORT")

    if all_passed:
        print("🎉 Your app is ready for Android build!")
        print("\n📱 Next steps:")
        print("   1. Install buildozer: pip install buildozer")
        print("   2. Run: buildozer android debug")
        print("   3. Wait for build (30-60 minutes first time)")
        print("   4. Install APK: adb install bin/*.apk")
        print("\n⏰ Build time estimates:")
        print("   • First build: 30-60 minutes (downloads Android SDK/NDK)")
        print("   • Subsequent builds: 5-15 minutes")
    else:
        print("⚠️ Issues found that should be addressed:")
        for issue in issues:
            print(f"   • {issue}")

        print("\n🔧 Recommended fixes:")
        print("   • Install missing packages: pip install -r requirements.txt")
        print("   • Create missing files/directories")
        print("   • Update buildozer.spec if needed")
        print("   • Ensure you have 10+ GB free disk space")

    print("\n📋 Build command when ready:")
    print("   buildozer android debug")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)