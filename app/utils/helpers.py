# app/utils/helpers.py
"""
Helper utility functions
"""

import time
from typing import List, Tuple, Optional
import numpy as np


def format_confidence(confidence: float) -> str:
    """Format confidence value as percentage"""
    return f"{confidence * 100:.1f}%"


def get_color_for_confidence(confidence: float) -> Tuple[float, float, float, float]:
    """Get color based on confidence level"""
    from .constants import SUCCESS_COLOR, ERROR_COLOR, SECONDARY_COLOR

    if confidence >= 0.8:
        return [c / 255.0 for c in SUCCESS_COLOR]  # Green
    elif confidence >= 0.5:
        return [c / 255.0 for c in SECONDARY_COLOR]  # Amber
    else:
        return [c / 255.0 for c in ERROR_COLOR]  # Red


def smooth_predictions(predictions: List[str], buffer_size: int = 10) -> Optional[str]:
    """Smooth predictions using majority voting"""
    if not predictions:
        return None

    # Take the most recent predictions
    recent = predictions[-buffer_size:]

    # Count occurrences
    counts = {}
    for pred in recent:
        counts[pred] = counts.get(pred, 0) + 1

    # Return most common prediction
    if counts:
        return max(counts, key=counts.get)
    return None


def calculate_fps(frame_times: List[float], window_size: int = 30) -> float:
    """Calculate FPS from frame timestamps"""
    if len(frame_times) < 2:
        return 0.0

    recent_times = frame_times[-window_size:]
    if len(recent_times) < 2:
        return 0.0

    time_diff = recent_times[-1] - recent_times[0]
    if time_diff <= 0:
        return 0.0

    return (len(recent_times) - 1) / time_diff


def preprocess_for_model(image: np.ndarray, target_size: int = 224) -> np.ndarray:
    """Preprocess image for model input"""
    import cv2

    # Resize to target size
    image = cv2.resize(image, (target_size, target_size))

    # Normalize to [0, 1]
    image = image.astype(np.float32) / 255.0

    # Add batch dimension
    image = np.expand_dims(image, axis=0)

    return image


def format_time_elapsed(seconds: int) -> str:
    """Format elapsed time in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"