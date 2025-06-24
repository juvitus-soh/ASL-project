# app/utils/logger.py
"""
Fixed Logger for ASL Mobile App - Windows Unicode Safe
"""

import logging
import sys
from pathlib import Path


class ASLLogger:
    """Custom logger for ASL Mobile App with Windows Unicode handling"""

    def __init__(self, name="ASLMobileApp", log_file="logs/asl_app.log"):
        """Initialize the logger"""
        self.name = name
        self.log_file = log_file

        # Create logs directory
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers with proper encoding"""

        # File handler with UTF-8 encoding
        try:
            file_handler = logging.FileHandler(
                self.log_file,
                mode='a',
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")

        # Console handler with safe encoding
        try:
            console_handler = logging.StreamHandler(sys.stdout)

            # Simple formatter without Unicode symbols
            console_formatter = logging.Formatter(
                '[%(levelname)s] %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)

        except Exception as e:
            print(f"Warning: Could not setup console logging: {e}")

    def _safe_message(self, message):
        """Make message safe for Windows console"""
        if isinstance(message, str):
            # Replace Unicode symbols with ASCII equivalents
            safe_msg = message.replace('✅', '[OK]')
            safe_msg = safe_msg.replace('❌', '[ERROR]')
            safe_msg = safe_msg.replace('⚠️', '[WARNING]')
            safe_msg = safe_msg.replace('🚀', '[START]')
            safe_msg = safe_msg.replace('🎯', '[TARGET]')
            safe_msg = safe_msg.replace('🔧', '[FIX]')
            safe_msg = safe_msg.replace('📝', '[NOTE]')
            safe_msg = safe_msg.replace('🔊', '[AUDIO]')
            return safe_msg
        return str(message)

    def debug(self, message):
        """Log debug message"""
        safe_msg = self._safe_message(message)
        self.logger.debug(safe_msg)

    def info(self, message):
        """Log info message"""
        safe_msg = self._safe_message(message)
        self.logger.info(safe_msg)

    def warning(self, message):
        """Log warning message"""
        safe_msg = self._safe_message(message)
        self.logger.warning(safe_msg)

    def error(self, message):
        """Log error message"""
        safe_msg = self._safe_message(message)
        self.logger.error(safe_msg)

    def critical(self, message):
        """Log critical message"""
        safe_msg = self._safe_message(message)
        self.logger.critical(safe_msg)


# Create default logger instance
logger = ASLLogger()


# Convenience functions
def debug(msg):
    logger.debug(msg)


def info(msg):
    logger.info(msg)


def warning(msg):
    logger.warning(msg)


def error(msg):
    logger.error(msg)


def critical(msg):
    logger.critical(msg)