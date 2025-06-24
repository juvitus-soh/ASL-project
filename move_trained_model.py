#!/usr/bin/env python3
"""
Copy trained model from asl_project to ASL Mobile App
"""

import shutil
import os
from pathlib import Path


def copy_model_files():
    """Copy the trained model and related files"""

    # Source paths (your asl_project)
    asl_project_path = Path("C:/Users/user/PycharmProjects/asl_project")

    # Destination paths (current mobile app)
    mobile_app_path = Path(".")
    assets_models_path = mobile_app_path / "assets" / "models"

    # Create destination directory
    assets_models_path.mkdir(parents=True, exist_ok=True)

    print("🚀 Copying trained model files...")

    # Copy the main model file
    model_files_to_copy = [
        {
            'source': asl_project_path / "results" / "checkpoints" / "best_model.h5",
            'dest': assets_models_path / "best_model.h5",
            'description': "Main Keras model file"
        },
        {
            'source': asl_project_path / "results" / "models" / "best_model.tflite",
            'dest': assets_models_path / "best_model.tflite",
            'description': "TensorFlow Lite model (smaller, faster)"
        }
    ]

    for file_info in model_files_to_copy:
        source = file_info['source']
        dest = file_info['dest']
        desc = file_info['description']

        if source.exists():
            try:
                shutil.copy2(source, dest)
                size_mb = dest.stat().st_size / (1024 * 1024)
                print(f"✅ Copied {desc}: {dest.name} ({size_mb:.1f}MB)")
            except Exception as e:
                print(f"❌ Error copying {desc}: {e}")
        else:
            print(f"❌ Source file not found: {source}")

    # Copy important source files for integration
    source_files_to_copy = [
        {
            'source': asl_project_path / "src" / "inference" / "predictor.py",
            'dest': mobile_app_path / "app" / "core" / "predictor.py",
            'description': "Model predictor"
        },
        {
            'source': asl_project_path / "src" / "config.py",
            'dest': mobile_app_path / "app" / "utils" / "model_config.py",
            'description': "Model configuration"
        }
    ]

    for file_info in source_files_to_copy:
        source = file_info['source']
        dest = file_info['dest']
        desc = file_info['description']

        if source.exists():
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                print(f"✅ Copied {desc}: {dest.name}")
            except Exception as e:
                print(f"❌ Error copying {desc}: {e}")
        else:
            print(f"❌ Source file not found: {source}")

    print("\n🎯 Model files copied successfully!")
    print("\n📋 Next steps:")
    print("1. Update the model manager to load the real model")
    print("2. Test the integration")
    print("3. Run the app again")


if __name__ == "__main__":
    copy_model_files()