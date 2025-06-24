# app/widgets/confidence_bar.py
"""
Confidence level visualization bar
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation


class ConfidenceBar(Widget):
    """Visual confidence level bar"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confidence = 0.0
        self.size_hint_y = None
        self.height = 30

        with self.canvas:
            # Background
            Color(0.9, 0.9, 0.9, 1)  # Light gray
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

            # Confidence bar
            Color(0.2, 0.6, 1.0, 1)  # Blue
            self.conf_rect = Rectangle(pos=self.pos, size=(0, self.height))

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        """Update bar graphics"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        # Update confidence bar
        conf_width = self.width * self.confidence
        self.conf_rect.pos = self.pos
        self.conf_rect.size = (conf_width, self.height)

    def set_confidence(self, confidence):
        """Set confidence level (0.0 to 1.0)"""
        self.confidence = max(0.0, min(1.0, confidence))

        # Update color based on confidence
        with self.canvas:
            if confidence >= 0.8:
                Color(0.3, 0.7, 0.3, 1)  # Green
            elif confidence >= 0.5:
                Color(1.0, 0.6, 0.2, 1)  # Orange
            else:
                Color(0.8, 0.3, 0.3, 1)  # Red

            self.conf_rect = Rectangle(
                pos=self.pos,
                size=(self.width * self.confidence, self.height)
            )