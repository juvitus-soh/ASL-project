# app/utils/storage.py
"""
Local data storage management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class AppStorage:
    """Manages local app data storage"""

    def __init__(self):
        # Create app data directory
        self.app_dir = Path.home() / ".asl_mobile_app"
        self.app_dir.mkdir(exist_ok=True)

        self.settings_file = self.app_dir / "settings.json"
        self.history_file = self.app_dir / "history.json"

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save app settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def load_settings(self) -> Dict[str, Any]:
        """Load app settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")

        # Return default settings if file doesn't exist or error occurred
        from .constants import DEFAULT_SETTINGS
        return DEFAULT_SETTINGS.copy()

    def save_history(self, history: Dict[str, Any]) -> bool:
        """Save recognition history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False

    def load_history(self) -> Dict[str, Any]:
        """Load recognition history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")

        # Return empty history if file doesn't exist or error occurred
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'words_formed': 0,
            'letters_recognized': {},
            'session_history': []
        }

    def clear_data(self) -> bool:
        """Clear all stored data"""
        try:
            if self.settings_file.exists():
                os.remove(self.settings_file)
            if self.history_file.exists():
                os.remove(self.history_file)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False