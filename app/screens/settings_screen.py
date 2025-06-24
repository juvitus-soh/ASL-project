#!/usr/bin/env python3
"""
Settings Screen - App configuration and preferences
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.app import App
from kivy.metrics import dp


class SettingsScreen(Screen):
    """Settings screen for app configuration"""

    def __init__(self, **kwargs):
        super().__init__(name='settings', **kwargs)
        self.settings_manager = None
        self.build_ui()

    def build_ui(self):
        """Build the settings screen UI"""
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )

        # Header
        header = self.create_header()
        main_layout.add_widget(header)

        # Tabbed settings content
        tabbed_content = self.create_tabbed_content()
        main_layout.add_widget(tabbed_content)

        # Footer
        footer = self.create_footer()
        main_layout.add_widget(footer)

        self.add_widget(main_layout)

    def create_header(self):
        """Create header with back button and title"""
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10)
        )

        # Back button
        back_btn = Button(
            text="← Back",
            size_hint=(0.2, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)

        # Title
        title = Label(
            text="Settings",
            font_size=dp(24),
            bold=True,
            size_hint=(0.6, 1)
        )
        header_layout.add_widget(title)

        # Save button
        save_btn = Button(
            text="💾 Save",
            size_hint=(0.2, 1),
            background_color=(0, 0.8, 0, 1)
        )
        save_btn.bind(on_press=self.save_settings)
        header_layout.add_widget(save_btn)

        return header_layout

    def create_tabbed_content(self):
        """Create tabbed content area"""
        self.tab_panel = TabbedPanel(
            size_hint=(1, 0.8),
            do_default_tab=False
        )

        # Speech settings tab
        speech_tab = TabbedPanelItem(text='🔊 Speech')
        speech_tab.content = self.create_speech_settings()
        self.tab_panel.add_widget(speech_tab)

        # Recognition settings tab
        recognition_tab = TabbedPanelItem(text='🎯 Recognition')
        recognition_tab.content = self.create_recognition_settings()
        self.tab_panel.add_widget(recognition_tab)

        # Camera settings tab
        camera_tab = TabbedPanelItem(text='📹 Camera')
        camera_tab.content = self.create_camera_settings()
        self.tab_panel.add_widget(camera_tab)

        # App settings tab
        app_tab = TabbedPanelItem(text='📱 App')
        app_tab.content = self.create_app_settings()
        self.tab_panel.add_widget(app_tab)

        # Set default tab
        self.tab_panel.default_tab = speech_tab

        return self.tab_panel

    def create_speech_settings(self):
        """Create speech settings content"""
        scroll = ScrollView()

        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        layout.bind(minimum_height=layout.setter('height'))

        # Speech enabled
        speech_layout = self.create_setting_row(
            "Enable Speech",
            "Enable text-to-speech output",
            Switch(active=True)
        )
        layout.add_widget(speech_layout)

        # Speech rate
        rate_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        rate_layout.add_widget(Label(
            text="Speech Rate",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))
        rate_slider = Slider(
            min=50, max=300, value=150, step=10,
            size_hint_y=None, height=dp(30)
        )
        rate_layout.add_widget(rate_slider)
        rate_layout.add_widget(Label(
            text="150 words per minute",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(rate_layout)

        # Speech volume
        volume_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        volume_layout.add_widget(Label(
            text="Speech Volume",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))
        volume_slider = Slider(
            min=0, max=1, value=0.8, step=0.1,
            size_hint_y=None, height=dp(30)
        )
        volume_layout.add_widget(volume_slider)
        volume_layout.add_widget(Label(
            text="80%",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(volume_layout)

        # Auto-speak words
        auto_speak_layout = self.create_setting_row(
            "Auto-speak Words",
            "Automatically speak completed words",
            Switch(active=True)
        )
        layout.add_widget(auto_speak_layout)

        scroll.add_widget(layout)
        return scroll

    def create_recognition_settings(self):
        """Create recognition settings content"""
        scroll = ScrollView()

        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        layout.bind(minimum_height=layout.setter('height'))

        # Confidence threshold
        conf_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        conf_layout.add_widget(Label(
            text="Confidence Threshold",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))
        conf_slider = Slider(
            min=0.3, max=0.95, value=0.7, step=0.05,
            size_hint_y=None, height=dp(30)
        )
        conf_layout.add_widget(conf_slider)
        conf_layout.add_widget(Label(
            text="70% - Higher values require more confident predictions",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(conf_layout)

        # Show confidence
        show_conf_layout = self.create_setting_row(
            "Show Confidence",
            "Display prediction confidence percentages",
            Switch(active=True)
        )
        layout.add_widget(show_conf_layout)

        # Show FPS
        fps_layout = self.create_setting_row(
            "Show FPS",
            "Display frames per second counter",
            Switch(active=False)
        )
        layout.add_widget(fps_layout)

        # Prediction smoothing
        smooth_layout = self.create_setting_row(
            "Prediction Smoothing",
            "Reduce jittery predictions",
            Switch(active=True)
        )
        layout.add_widget(smooth_layout)

        scroll.add_widget(layout)
        return scroll

    def create_camera_settings(self):
        """Create camera settings content"""
        scroll = ScrollView()

        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        layout.bind(minimum_height=layout.setter('height'))

        # Camera resolution
        res_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        res_layout.add_widget(Label(
            text="Camera Resolution",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))

        res_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        for res in ['Low', 'Medium', 'High']:
            btn = Button(
                text=res,
                size_hint_x=0.33,
                background_color=(0.2, 0.6, 1, 1) if res == 'Medium' else (0.5, 0.5, 0.5, 1)
            )
            res_buttons.add_widget(btn)
        res_layout.add_widget(res_buttons)

        res_layout.add_widget(Label(
            text="Medium (640x480) - Balance of quality and performance",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(res_layout)

        # Camera FPS
        fps_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        fps_layout.add_widget(Label(
            text="Camera FPS",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))
        fps_slider = Slider(
            min=15, max=60, value=30, step=5,
            size_hint_y=None, height=dp(30)
        )
        fps_layout.add_widget(fps_slider)
        fps_layout.add_widget(Label(
            text="30 FPS - Higher values use more battery",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(fps_layout)

        # Show camera preview
        preview_layout = self.create_setting_row(
            "Show Camera Preview",
            "Display live camera feed",
            Switch(active=True)
        )
        layout.add_widget(preview_layout)

        scroll.add_widget(layout)
        return scroll

    def create_app_settings(self):
        """Create app settings content"""
        scroll = ScrollView()

        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        layout.bind(minimum_height=layout.setter('height'))

        # Theme
        theme_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        theme_layout.add_widget(Label(
            text="Theme",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))

        theme_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        for theme in ['Light', 'Dark']:
            btn = Button(
                text=theme,
                size_hint_x=0.5,
                background_color=(0.2, 0.6, 1, 1) if theme == 'Light' else (0.5, 0.5, 0.5, 1)
            )
            theme_buttons.add_widget(btn)
        theme_layout.add_widget(theme_buttons)

        theme_layout.add_widget(Label(
            text="Light theme active",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(theme_layout)

        # Save history
        history_layout = self.create_setting_row(
            "Save Recognition History",
            "Keep history of predictions and words",
            Switch(active=True)
        )
        layout.add_widget(history_layout)

        # Debug mode
        debug_layout = self.create_setting_row(
            "Debug Mode",
            "Show additional debugging information",
            Switch(active=False)
        )
        layout.add_widget(debug_layout)

        # Model information
        model_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        model_layout.add_widget(Label(
            text="ASL Model",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30)
        ))

        model_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        model_info.add_widget(Label(
            text="TensorFlow Lite Model",
            font_size=dp(14),
            size_hint_x=0.7,
            halign='left',
            text_size=(dp(180), None)
        ))

        model_btn = Button(
            text="📁 Browse",
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1)
        )
        model_btn.bind(on_press=self.browse_model)
        model_info.add_widget(model_btn)
        model_layout.add_widget(model_info)

        model_layout.add_widget(Label(
            text="Expected: assets/models/best_model.tflite",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30),
            color=(0.7, 0.7, 0.7, 1)
        ))
        layout.add_widget(model_layout)

        # Tutorial completed
        tutorial_layout = self.create_setting_row(
            "Tutorial Completed",
            "Mark tutorial as completed",
            Switch(active=False)
        )
        layout.add_widget(tutorial_layout)

        scroll.add_widget(layout)
        return scroll

    def create_setting_row(self, title, description, control):
        """Create a setting row with title, description and control"""
        row_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        # Text column
        text_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        text_layout.add_widget(Label(
            text=title,
            font_size=dp(16),
            bold=True,
            size_hint_y=0.6,
            halign='left',
            text_size=(dp(200), None)
        ))
        text_layout.add_widget(Label(
            text=description,
            font_size=dp(12),
            size_hint_y=0.4,
            color=(0.7, 0.7, 0.7, 1),
            halign='left',
            text_size=(dp(200), None)
        ))
        row_layout.add_widget(text_layout)

        # Control column
        control_layout = BoxLayout(size_hint_x=0.3)
        control_layout.add_widget(control)
        row_layout.add_widget(control_layout)

        return row_layout

    def create_footer(self):
        """Create footer buttons"""
        footer_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10)
        )

        # Reset button
        reset_btn = Button(
            text="🔄 Reset to Defaults",
            size_hint=(0.5, 1),
            background_color=(1, 0.4, 0, 1)
        )
        reset_btn.bind(on_press=self.reset_settings)
        footer_layout.add_widget(reset_btn)

        # Export button
        export_btn = Button(
            text="📤 Export Settings",
            size_hint=(0.5, 1),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        export_btn.bind(on_press=self.export_settings)
        footer_layout.add_widget(export_btn)

        return footer_layout

    def save_settings(self, instance):
        """Save current settings"""
        if self.settings_manager:
            success = self.settings_manager.save_settings()
            if success:
                # TODO: Show success popup
                print("✅ Settings saved successfully")

    def reset_settings(self, instance):
        """Reset settings to defaults"""
        if self.settings_manager:
            success = self.settings_manager.reset_to_defaults()
            if success:
                # TODO: Refresh UI with new values
                print("🔄 Settings reset to defaults")

    def export_settings(self, instance):
        """Export settings to file"""
        if self.settings_manager:
            export_file = f"asl_settings_export_{self.get_timestamp()}.json"
            success = self.settings_manager.export_settings(export_file)
            if success:
                # TODO: Show success popup with file location
                print(f"📤 Settings exported to: {export_file}")

    def browse_model(self, instance):
        """Browse for model file"""
        # TODO: Implement file browser for model selection
        print("📁 Model browser would open here")
        print("💡 Currently looking for: assets/models/best_model.tflite")

    def get_timestamp(self):
        """Get current timestamp for file naming"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def go_back(self, instance=None):
        """Go back to home screen"""
        App.get_running_app().switch_screen('home')

    def on_pre_enter(self):
        """Called before entering the screen"""
        app = App.get_running_app()
        self.settings_manager = getattr(app, 'settings_manager', None)
        # TODO: Load current settings into UI controls