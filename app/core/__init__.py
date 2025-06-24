"""
Core module for ASL Mobile App
Contains the main engine and utility classes
"""

# Core module initialization
__version__ = "1.0.0"
__author__ = "ASL Mobile App Team"

# Make imports available at package level
try:
    from .asl_engine import ASLEngine
    from .settings_manager import SettingsManager
    from .speech_engine import speech_engine
except ImportError as e:
    print(f"⚠️ Core module import warning: {e}")
    # These will be available when the full project is set up
    pass