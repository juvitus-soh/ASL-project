# app/widgets/custom_buttons.py
"""
Custom styled buttons for the app
"""

from kivy.uix.button import Button
from kivy.utils import get_color_from_hex


class PrimaryButton(Button):
    """Primary action button"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#2196F3')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = '16sp'


class SecondaryButton(Button):
    """Secondary action button"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#FF9800')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = '16sp'


class DangerButton(Button):
    """Danger/warning action button"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#F44336')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = '16sp'


class SuccessButton(Button):
    """Success action button"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#4CAF50')
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = '16sp'