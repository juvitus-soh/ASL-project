#!/usr/bin/env python3
"""
Home Screen for ASL Mobile App
Main navigation and status screen
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
from kivy.metrics import dp


class HomeScreen(Screen):
    """Home screen with navigation and model status"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()

    def build_ui(self):
        """Build the home screen UI"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title
        title = Label(
            text="ASL Recognition",
            font_size='32sp',
            bold=True,
            size_hint_y=0.15,
            color=(0.2, 0.6, 1, 1)  # Blue
        )
        main_layout.add_widget(title)

        # Subtitle
        subtitle = Label(
            text="Real-time American Sign Language Recognition",
            font_size='16sp',
            size_hint_y=0.1,
            color=(0.6, 0.6, 0.6, 1)
        )
        main_layout.add_widget(subtitle)

        # Model status
        self.status_label = Label(
            text="🔄 Loading ASL Model...",
            font_size='18sp',
            size_hint_y=0.1,
            color=(1, 1, 0, 1)  # Yellow
        )
        main_layout.add_widget(self.status_label)

        # Model info
        self.model_info_label = Label(
            text="",
            font_size='14sp',
            size_hint_y=0.1,
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(self.model_info_label)

        # Navigation buttons
        nav_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.55)

        # Start ASL Recognition button
        self.start_button = Button(
            text="📹 Start ASL Recognition",
            font_size='20sp',
            size_hint_y=0.25,
            background_color=(0, 0.7, 0, 1),  # Green
            disabled=True  # Will enable when model loads
        )
        self.start_button.bind(on_press=self.start_camera)
        nav_layout.add_widget(self.start_button)

        # Tutorial button
        tutorial_button = Button(
            text="📚 How to Use",
            font_size='18sp',
            size_hint_y=0.2,
            background_color=(0, 0.5, 1, 1)  # Blue
        )
        tutorial_button.bind(on_press=self.open_tutorial)
        nav_layout.add_widget(tutorial_button)

        # History button
        history_button = Button(
            text="📜 Recognition History",
            font_size='18sp',
            size_hint_y=0.2,
            background_color=(0.7, 0, 0.7, 1)  # Purple
        )
        history_button.bind(on_press=self.open_history)
        nav_layout.add_widget(history_button)

        # Settings button
        settings_button = Button(
            text="⚙️ Settings",
            font_size='18sp',
            size_hint_y=0.2,
            background_color=(0.5, 0.5, 0.5, 1)  # Gray
        )
        settings_button.bind(on_press=self.open_settings)
        nav_layout.add_widget(settings_button)

        # About button
        about_button = Button(
            text="ℹ️ About",
            font_size='18sp',
            size_hint_y=0.15,
            background_color=(0.3, 0.3, 0.3, 1)  # Dark gray
        )
        about_button.bind(on_press=self.open_about)
        nav_layout.add_widget(about_button)

        main_layout.add_widget(nav_layout)

        self.add_widget(main_layout)

    def on_enter(self):
        """Called when entering this screen"""
        self.app = App.get_running_app()

        # Schedule model status check
        Clock.schedule_once(self.check_model_status, 0.5)
        Clock.schedule_interval(self.update_model_status, 2.0)

        print("🏠 Home screen opened")

    def check_model_status(self, dt):
        """Check initial model status"""
        if not self.app:
            return

        if hasattr(self.app, 'asl_engine') and self.app.asl_engine:
            model_info = self.app.asl_engine.get_model_info()
            self.update_status_display(model_info)
        else:
            self.status_label.text = "❌ ASL Engine not initialized"
            self.status_label.color = (1, 0, 0, 1)

    def update_model_status(self, dt):
        """Periodically update model status"""
        if not self.app or not hasattr(self.app, 'asl_engine'):
            return

        if self.app.asl_engine:
            model_info = self.app.asl_engine.get_model_info()
            self.update_status_display(model_info)

    def update_status_display(self, model_info):
        """Update the status display based on model info"""
        if model_info['loaded']:
            # Model is loaded
            self.status_label.text = "✅ ASL Model Ready"
            self.status_label.color = (0, 1, 0, 1)  # Green

            # Enable start button
            self.start_button.disabled = False
            self.start_button.text = "📹 Start ASL Recognition"

            # Show model details
            model_type = model_info.get('type', 'unknown').upper()
            num_classes = model_info.get('num_classes', 'unknown')
            self.model_info_label.text = f"Model: {model_type} ({num_classes} classes)"

            # Update app model loaded status
            self.app.is_model_loaded = True

        else:
            # Model not loaded
            self.status_label.text = "⚠️ No ASL Model Found"
            self.status_label.color = (1, 0.5, 0, 1)  # Orange

            # Disable start button
            self.start_button.disabled = True
            self.start_button.text = "❌ Model Required"

            # Show instructions
            self.model_info_label.text = "Place your model in assets/models/"

            # Update app model loaded status
            self.app.is_model_loaded = False

    def start_camera(self, instance):
        """Start the camera screen"""
        if self.app and self.app.is_model_loaded:
            print("🎥 Starting camera screen...")
            self.app.switch_screen('camera')
        else:
            print("⚠️ Cannot start camera - model not loaded")

    def open_tutorial(self, instance):
        """Open tutorial screen"""
        if self.app:
            self.app.switch_screen('tutorial')

    def open_history(self, instance):
        """Open history screen"""
        if self.app:
            self.app.switch_screen('history')

    def open_settings(self, instance):
        """Open settings screen"""
        if self.app:
            self.app.switch_screen('settings')

    def open_about(self, instance):
        """Open about screen"""
        if self.app:
            self.app.switch_screen('about')

    def on_leave(self):
        """Called when leaving this screen"""
        print("🏠 Left home screen")