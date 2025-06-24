# app/utils/constants.py
"""
Application constants and configuration
"""

# App Configuration
APP_NAME = "ASL Recognition"
APP_VERSION = "1.0.0"

# ASL Classes (29 classes including space, del, nothing)
ASL_CLASSES = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'space', 'del', 'nothing'
]

# Model Configuration
MODEL_PATH = "assets/models/best_model.h5"
INPUT_SIZE = 224
CONFIDENCE_THRESHOLD = 0.75
PREDICTION_BUFFER_SIZE = 10
SMOOTHING_FRAMES = 8

# UI Configuration
CAMERA_RESOLUTION = (640, 480)
ROI_SIZE = 300
ROI_COLOR = (0, 255, 0, 255)  # Green RGBA

# Colors (RGBA)
PRIMARY_COLOR = (33, 150, 243, 255)      # Blue
SECONDARY_COLOR = (255, 193, 7, 255)     # Amber
SUCCESS_COLOR = (76, 175, 80, 255)       # Green
ERROR_COLOR = (244, 67, 54, 255)         # Red
TEXT_COLOR = (33, 33, 33, 255)           # Dark Gray

# Storage Keys
SETTINGS_KEY = "app_settings"
HISTORY_KEY = "recognition_history"

# Default Settings
DEFAULT_SETTINGS = {
    'confidence_threshold': 0.75,
    'speech_enabled': True,
    'speech_rate': 150,
    'auto_word_completion': True,
    'prediction_smoothing': True,
    'camera_resolution': '640x480'
}