# app/widgets/camera_widget.py
"""
Custom camera widget for ASL recognition
"""

from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.clock import Clock
import cv2
import numpy as np


class CameraWidget(Camera):
    """Custom camera widget with ROI overlay"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roi_size = 300
        self.roi_color = (0, 1, 0, 1)  # Green

        # Bind to draw ROI when size changes
        self.bind(size=self.update_roi)
        self.bind(pos=self.update_roi)

        # Schedule ROI drawing
        Clock.schedule_once(self.update_roi, 0.1)

    def update_roi(self, *args):
        """Update ROI overlay"""
        self.canvas.after.clear()

        with self.canvas.after:
            # Draw ROI rectangle
            Color(*self.roi_color)

            # Calculate ROI position (center of camera)
            roi_x = self.center_x - self.roi_size / 2
            roi_y = self.center_y - self.roi_size / 2

            # Draw rectangle outline
            Line(rectangle=(roi_x, roi_y, self.roi_size, self.roi_size), width=3)

    def get_roi_frame(self):
        """Extract ROI from camera frame"""
        try:
            # Get current frame
            if hasattr(self, '_camera') and self._camera:
                # This is a simplified version - actual implementation
                # would need to capture the camera frame properly
                pass
        except Exception as e:
            print(f"Error getting ROI frame: {e}")

        return None