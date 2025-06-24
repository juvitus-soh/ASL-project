#!/usr/bin/env python3
"""
Settings Manager - Configuration and preferences management
Updated to use TensorFlow Lite model by default
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages application settings and user preferences"""

    def __init__(self, settings_file: Optional[str] = None):
        """
        Initialize settings manager

        Args:
            settings_file: Path to settings file (default: settings.json)
        """
        # Default settings file
        if settings_file is None:
            settings_file = "settings.json"

        self.settings_file = Path(settings_file)

        # Default settings
        self.default_settings = {
            # Speech settings
            'speech_enabled': True,
            'speech_rate': 150,
            'speech_volume': 0.8,
            'speech_voice': 'default',

            # Recognition settings
            'recognition_confidence_threshold': 0.7,
            'auto_speak_words': True,
            'auto_speak_interval': 9,  # Speak every N letters

            # Camera settings
            'camera_resolution': 'medium',  # low, medium, high
            'camera_fps': 30,
            'show_camera_preview': True,

            # UI settings
            'theme': 'light',  # light, dark
            'font_size': 'medium',  # small, medium, large
            'show_confidence': True,
            'show_fps': False,

            # Tutorial settings
            'tutorial_completed': False,
            'show_hints': True,

            # Data settings
            'save_history': True,
            'max_history_items': 100,
            'clear_history_on_exit': False,

            # Advanced settings
            'debug_mode': False,
            'log_predictions': False,
            'model_path': 'assets/models/best_model.tflite'  # ✅ Updated to use best_model.tflite
        }

        # Current settings (loaded from file or defaults)
        self.settings = self.default_settings.copy()

        # Load existing settings
        self.load_settings()

    def load_settings(self) -> bool:
        """
        Load settings from file

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Merge with defaults (in case new settings were added)
                self.settings.update(loaded_settings)

                print(f"✅ Settings loaded from {self.settings_file}")
                return True
            else:
                print(f"📁 Settings file not found, using defaults")
                return False

        except Exception as e:
            print(f"⚠️ Failed to load settings: {e}")
            return False

    def save_settings(self) -> bool:
        """
        Save current settings to file

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, sort_keys=True)

            print(f"💾 Settings saved to {self.settings_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to save settings: {e}")
            return False

    def get_settings(self) -> Dict[str, Any]:
        """
        Get all current settings

        Returns:
            Dict containing all settings
        """
        return self.settings.copy()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a specific setting value

        Args:
            key: Setting key
            value: Setting value

        Returns:
            bool: True if set successfully
        """
        try:
            self.settings[key] = value
            print(f"⚙️ Setting updated: {key} = {value}")
            return True
        except Exception as e:
            print(f"❌ Failed to set setting {key}: {e}")
            return False

    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """
        Update multiple settings

        Args:
            new_settings: Dictionary of settings to update

        Returns:
            bool: True if updated successfully
        """
        try:
            self.settings.update(new_settings)
            print(f"⚙️ Updated {len(new_settings)} settings")
            return True
        except Exception as e:
            print(f"❌ Failed to update settings: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults

        Returns:
            bool: True if reset successfully
        """
        try:
            self.settings = self.default_settings.copy()
            print("🔄 Settings reset to defaults")
            return True
        except Exception as e:
            print(f"❌ Failed to reset settings: {e}")
            return False

    def export_settings(self, export_path: str) -> bool:
        """
        Export settings to a file

        Args:
            export_path: Path to export file

        Returns:
            bool: True if exported successfully
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, sort_keys=True)

            print(f"📤 Settings exported to {export_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to export settings: {e}")
            return False

    def import_settings(self, import_path: str) -> bool:
        """
        Import settings from a file

        Args:
            import_path: Path to import file

        Returns:
            bool: True if imported successfully
        """
        try:
            import_file = Path(import_path)

            if not import_file.exists():
                print(f"❌ Import file not found: {import_file}")
                return False

            with open(import_file, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)

            # Validate imported settings (only update known keys)
            valid_settings = {}
            for key, value in imported_settings.items():
                if key in self.default_settings:
                    valid_settings[key] = value
                else:
                    print(f"⚠️ Skipping unknown setting: {key}")

            self.settings.update(valid_settings)
            print(f"📥 Settings imported from {import_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to import settings: {e}")
            return False

    def get_category_settings(self, category: str) -> Dict[str, Any]:
        """
        Get all settings for a specific category

        Args:
            category: Category prefix (e.g., 'speech', 'camera')

        Returns:
            Dict containing category settings
        """
        category_settings = {}
        prefix = f"{category}_"

        for key, value in self.settings.items():
            if key.startswith(prefix):
                # Remove prefix from key
                clean_key = key[len(prefix):]
                category_settings[clean_key] = value

        return category_settings

    def update_category_settings(self, category: str, category_settings: Dict[str, Any]) -> bool:
        """
        Update all settings for a specific category

        Args:
            category: Category prefix
            category_settings: Dict of category settings (without prefix)

        Returns:
            bool: True if updated successfully
        """
        try:
            prefix = f"{category}_"

            for key, value in category_settings.items():
                full_key = f"{prefix}{key}"
                if full_key in self.default_settings:
                    self.settings[full_key] = value
                else:
                    print(f"⚠️ Unknown setting: {full_key}")

            print(f"⚙️ Updated {category} settings")
            return True

        except Exception as e:
            print(f"❌ Failed to update {category} settings: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get settings manager information

        Returns:
            Dict containing manager info
        """
        return {
            'settings_file': str(self.settings_file),
            'settings_exist': self.settings_file.exists(),
            'total_settings': len(self.settings),
            'default_settings': len(self.default_settings),
            'custom_settings': len([k for k in self.settings if k not in self.default_settings])
        }