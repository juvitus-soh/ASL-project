"""
Image processing utilities for ASL recognition
"""

import cv2
import numpy as np


class ImageProcessor:
    """Handles image preprocessing for ASL recognition"""

    @staticmethod
    def preprocess_image(image, target_size=224):
        """Preprocess image for model input"""
        # Resize image
        image = cv2.resize(image, (target_size, target_size))

        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0

        # Add batch dimension
        image = np.expand_dims(image, axis=0)

        return image

    @staticmethod
    def extract_roi(image, roi_coords, roi_size=300):
        """Extract region of interest from image"""
        h, w = image.shape[:2]
        x, y = roi_coords

        # Ensure ROI is within image bounds
        x = max(0, min(x, w - roi_size))
        y = max(0, min(y, h - roi_size))
        x2 = min(w, x + roi_size)
        y2 = min(h, y + roi_size)

        return image[y:y2, x:x2]

    @staticmethod
    def enhance_image(image):
        """Enhance image quality for better recognition"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[..., 0] = clahe.apply(lab[..., 0])

        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return enhanced