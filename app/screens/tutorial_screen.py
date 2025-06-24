# app/screens/tutorial_screen.py
"""
Tutorial screen for learning how to use the app
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


class TutorialScreen(Screen):
    """Tutorial screen implementation"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tutorial'
        self.build_ui()

    def build_ui(self):
        """Build the tutorial interface"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        back_btn = Button(
            text='← Back',
            size_hint_x=0.2,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text='Tutorial - How to Use ASL Recognition',
            font_size='20sp',
            color=(0.13, 0.59, 0.95, 1)
        )

        header.add_widget(back_btn)
        header.add_widget(title)

        # Tutorial content
        scroll = ScrollView(size_hint_y=0.9)
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=20
        )
        content.bind(minimum_height=content.setter('height'))

        # Tutorial steps
        steps = [
            "1. Position Your Hand",
            "Place your hand clearly in the green square on the camera screen. Ensure good lighting and a plain background.",

            "2. Make Clear Signs",
            "Form ASL letters clearly and hold them steady for 2-3 seconds. The app needs time to recognize the sign.",

            "3. Watch the Predictions",
            "Look at the prediction panel on the right. The confidence level shows how sure the app is about the recognition.",

            "4. Build Words",
            "Letters automatically build into words. Use the 'Space' button to complete a word, or wait for auto-completion.",

            "5. Form Sentences",
            "Complete words are added to your sentence. Use the speak button to hear your sentence out loud.",

            "6. Adjust Settings",
            "Go to Settings to adjust confidence thresholds, enable/disable speech, and customize other preferences."
        ]

        for i, step in enumerate(steps):
            if i % 2 == 0:  # Headers
                label = Label(
                    text=step,
                    font_size='18sp',
                    size_hint_y=None,
                    height=40,
                    color=(0.13, 0.59, 0.95, 1),
                    text_size=(None, None),
                    halign='left'
                )
            else:  # Content
                label = Label(
                    text=step,
                    font_size='14sp',
                    size_hint_y=None,
                    height=60,
                    color=(0.3, 0.3, 0.3, 1),
                    text_size=(600, None),
                    halign='left',
                    valign='top'
                )

            content.add_widget(label)

        scroll.add_widget(content)
        layout.add_widget(header)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def go_back(self, instance):
        """Go back to home screen"""
        self.manager.current = 'home'