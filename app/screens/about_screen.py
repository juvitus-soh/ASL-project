# app/screens/about_screen.py
"""
About screen with app information
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class AboutScreen(Screen):
    """About screen implementation"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'about'
        self.build_ui()

    def build_ui(self):
        """Build the about interface"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        back_btn = Button(
            text='← Back',
            size_hint_x=0.2,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text='About ASL Recognition App',
            font_size='20sp',
            color=(0.13, 0.59, 0.95, 1)
        )

        header.add_widget(back_btn)
        header.add_widget(title)

        # About content
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.9)

        app_info = Label(
            text='ASL Recognition Mobile App\nVersion 1.0.0',
            font_size='18sp',
            size_hint_y=0.2,
            color=(0.13, 0.59, 0.95, 1)
        )

        description = Label(
            text='This app uses deep learning to recognize American Sign Language (ASL) letters in real-time through your device camera. Built with TensorFlow and Kivy for cross-platform mobile deployment.',
            font_size='14sp',
            size_hint_y=0.3,
            text_size=(500, None),
            halign='center',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )

        features = Label(
            text='Features:\n• Real-time ASL letter recognition\n• Word and sentence building\n• Text-to-speech output\n• Confidence visualization\n• Recognition statistics\n• Customizable settings',
            font_size='14sp',
            size_hint_y=0.4,
            text_size=(400, None),
            halign='left',
            valign='top',
            color=(0.2, 0.2, 0.2, 1)
        )

        tech_info = Label(
            text='Technology: TensorFlow • Kivy • OpenCV • Python',
            font_size='12sp',
            size_hint_y=0.1,
            color=(0.6, 0.6, 0.6, 1)
        )

        content.add_widget(app_info)
        content.add_widget(description)
        content.add_widget(features)
        content.add_widget(tech_info)

        layout.add_widget(header)
        layout.add_widget(content)

        self.add_widget(layout)

    def go_back(self, instance):
        """Go back to home screen"""
        self.manager.current = 'home'