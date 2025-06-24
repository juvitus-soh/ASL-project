#!/bin/bash
# Automated Android Build Script for WSL2
# Run this script in WSL2 to build your ASL Mobile App APK

set -e  # Exit on any error

echo "=========================================="
echo "ASL Mobile App - Android Build Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in WSL2
if [[ ! -f /proc/version ]] || ! grep -q Microsoft /proc/version; then
    print_error "This script should be run in WSL2"
    exit 1
fi

print_success "Running in WSL2 environment"

# Check if project directory exists
PROJECT_DIR="$HOME/asl_mobile_app"
if [[ ! -d "$PROJECT_DIR" ]]; then
    print_error "Project directory $PROJECT_DIR not found"
    print_status "Please copy your project files first:"
    echo "  cp -r /mnt/c/Users/user/PycharmProjects/ASLMobileApp ~/asl_mobile_app"
    exit 1
fi

cd "$PROJECT_DIR"
print_success "Changed to project directory: $PROJECT_DIR"

# Check if buildozer.spec exists
if [[ ! -f "buildozer.spec" ]]; then
    print_error "buildozer.spec not found in project directory"
    print_status "Please run the prepare_android_build.py script first"
    exit 1
fi

print_success "Found buildozer.spec"

# Check if virtual environment exists
VENV_DIR="$HOME/buildenv"
if [[ ! -d "$VENV_DIR" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    print_status "Installing buildozer and dependencies..."
    pip install --upgrade pip
    pip install buildozer
    pip install cython==0.29.33
    pip install kivy[base]
    print_success "Buildozer installed"
else
    print_success "Buildozer already installed"
fi

# Check system dependencies
print_status "Checking system dependencies..."
missing_deps=()

# Check Java
if ! command -v java &> /dev/null; then
    missing_deps+=("openjdk-17-jdk")
fi

# Check build tools
for cmd in gcc g++ make git unzip; do
    if ! command -v "$cmd" &> /dev/null; then
        missing_deps+=("build-essential")
        break
    fi
done

# Install missing dependencies
if [[ ${#missing_deps[@]} -gt 0 ]]; then
    print_status "Installing missing system dependencies..."
    sudo apt update
    sudo apt install -y "${missing_deps[@]}"
    print_success "System dependencies installed"
else
    print_success "All system dependencies found"
fi

# Check disk space
available_space=$(df . | tail -1 | awk '{print $4}')
required_space=5000000  # 5GB in KB

if [[ $available_space -lt $required_space ]]; then
    print_warning "Low disk space detected"
    print_status "Available: $(($available_space / 1024 / 1024))GB"
    print_status "Recommended: 5GB free space"
    echo -n "Continue anyway? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Build cancelled"
        exit 0
    fi
fi

# Check for model file
if [[ ! -f "assets/models/best_model.tflite" ]]; then
    print_warning "TensorFlow Lite model not found"
    print_status "App will run in demo mode"
fi

# Ask for build type
echo ""
echo "Select build type:"
echo "1) Debug APK (for testing)"
echo "2) Release APK (for distribution)"
echo -n "Enter choice (1-2): "
read -r build_type

case $build_type in
    1)
        BUILD_COMMAND="buildozer android debug"
        BUILD_TYPE="debug"
        ;;
    2)
        BUILD_COMMAND="buildozer android release"
        BUILD_TYPE="release"
        ;;
    *)
        print_status "Defaulting to debug build"
        BUILD_COMMAND="buildozer android debug"
        BUILD_TYPE="debug"
        ;;
esac

# Ask about clean build
echo -n "Perform clean build? (removes cache, takes longer) (y/N): "
read -r clean_response
if [[ "$clean_response" =~ ^[Yy]$ ]]; then
    print_status "Performing clean build..."
    buildozer android clean
fi

# Estimate build time
if [[ -d ".buildozer" ]]; then
    print_status "Estimated build time: 5-15 minutes"
else
    print_status "First build - Estimated time: 45-90 minutes"
    print_status "This will download Android SDK, NDK, and dependencies"
fi

echo ""
echo -n "Start build? (Y/n): "
read -r start_response
if [[ "$start_response" =~ ^[Nn]$ ]]; then
    print_status "Build cancelled"
    exit 0
fi

# Start build
print_status "Starting $BUILD_TYPE build..."
echo "=========================================="
echo "Build started at: $(date)"
echo "Command: $BUILD_COMMAND"
echo "=========================================="

start_time=$(date +%s)

# Run build with error handling
if $BUILD_COMMAND; then
    end_time=$(date +%s)
    build_time=$((end_time - start_time))
    minutes=$((build_time / 60))
    seconds=$((build_time % 60))

    print_success "Build completed successfully!"
    print_status "Build time: ${minutes}m ${seconds}s"

    # Find APK file
    APK_FILE=$(find bin -name "*.apk" 2>/dev/null | head -1)
    if [[ -n "$APK_FILE" ]]; then
        APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
        print_success "APK created: $APK_FILE"
        print_status "APK size: $APK_SIZE"

        # Copy APK to Windows
        WINDOWS_DEST="/mnt/c/Users/user/Desktop"
        if [[ -d "$WINDOWS_DEST" ]]; then
            cp "$APK_FILE" "$WINDOWS_DEST/"
            print_success "APK copied to Windows Desktop"
        else
            print_status "Copy APK manually from: $PROJECT_DIR/$APK_FILE"
        fi

        echo ""
        echo "=========================================="
        print_success "BUILD COMPLETE!"
        echo "=========================================="
        echo "APK Location: $APK_FILE"
        echo "Install on phone:"
        echo "1. Copy APK to phone"
        echo "2. Enable 'Install from unknown sources'"
        echo "3. Tap APK file to install"
        echo ""
        echo "Or use ADB:"
        echo "adb install $APK_FILE"
        echo "=========================================="

    else
        print_error "APK file not found after build"
    fi

else
    print_error "Build failed!"
    echo ""
    echo "Common solutions:"
    echo "1. Try clean build: buildozer android clean"
    echo "2. Check disk space"
    echo "3. Update buildozer: pip install --upgrade buildozer"
    echo "4. Check buildozer.spec configuration"
    exit 1
fi

# Deactivate virtual environment
deactivate