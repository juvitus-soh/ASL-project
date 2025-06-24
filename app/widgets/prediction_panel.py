# app/widgets/prediction_panel.py
"""
Prediction display panel
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex


class PredictionPanel(BoxLayout):
    """Panel to display ASL predictions"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 200

        # Current prediction label
        self.current_prediction = Label(
            text="Ready to recognize...",
            font_size='24sp',
            size_hint_y=0.4,
            color=get_color_from_hex('#2196F3')
        )
        self.add_widget(self.current_prediction)

        # Confidence label
        self.confidence_label = Label(
            text="Confidence: --",
            font_size='16sp',
            size_hint_y=0.3,
            color=get_color_from_hex('#666666')
        )
        self.add_widget(self.confidence_label)

        # Current word label
        self.word_label = Label(
            text="Word: ",
            font_size='18sp',
            size_hint_y=0.3,
            color=get_color_from_hex('#4CAF50')
        )
        self.add_widget(self.word_label)

    def update_prediction(self, letter, confidence):
        """Update the displayed prediction"""
        self.current_prediction.text = f"Letter: {letter}"
        self.confidence_label.text = f"Confidence: {confidence:.1%}"

        # Update color based on confidence
        if confidence >= 0.8:
            self.current_prediction.color = get_color_from_hex('#4CAF50')  # Green
        elif confidence >= 0.5:
            self.current_prediction.color = get_color_from_hex('#FF9800')  # Orange
        else:
            self.current_prediction.color = get_color_from_hex('#F44336')  # Red

    def update_word(self, word):
        """Update the current word being built"""
        self.word_label.text = f"Word: {word}"