#!/usr/bin/env python3
"""
Quick fix script to correct import errors in screen files
"""

import os
import re


def fix_screen_imports():
    """Fix incorrect Kivy imports in screen files"""

    screen_files = [
        'app/screens/home_screen.py',
        'app/screens/camera_screen.py',
        'app/screens/settings_screen.py',
        'app/screens/history_screen.py',
        'app/screens/tutorial_screen.py',
        'app/screens/about_screen.py'
    ]

    # Pattern to find incorrect import
    wrong_import = r'from kivy\.uix\.screen import Screen'
    correct_import = 'from kivy.uix.screenmanager import Screen'

    fixed_count = 0

    for file_path in screen_files:
        if os.path.exists(file_path):
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if it has the wrong import
                if re.search(wrong_import, content):
                    # Fix the import
                    fixed_content = re.sub(wrong_import, correct_import, content)

                    # Write back the fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

                    print(f"✅ Fixed imports in: {file_path}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  No import issues in: {file_path}")

            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")

    print(f"\n📊 Summary: Fixed imports in {fixed_count} files")
    return fixed_count > 0


if __name__ == "__main__":
    print("🔧 Fixing Kivy import errors...")
    print("=" * 40)

    success = fix_screen_imports()

    if success:
        print("\n🎉 Import errors fixed!")
        print("Now try running: python main.py")
    else:
        print("\n⚠️  No files needed fixing or errors occurred")