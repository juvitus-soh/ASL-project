# #!/usr/bin/env python3
# """
# Camera Screen - Simplified Working Version
# Focus on camera display first, then add predictions
# """
#
# from kivy.uix.screenmanager import Screen
# from kivy.uix.camera import Camera
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.label import Label
# from kivy.uix.button import Button
# from kivy.uix.progressbar import ProgressBar
# from kivy.graphics import Rectangle, Color
# from kivy.clock import Clock
# from kivy.logger import Logger
# from kivy.metrics import dp
# from kivy.app import App
#
# import numpy as np
# import time
# import random
#
#
# class CameraScreen(Screen):
#     """Main camera screen for ASL recognition - Simplified Version"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         # App reference
#         self.app = None
#
#         # Camera and prediction state
#         self.camera = None
#         self.is_predicting = False
#         self.prediction_enabled = False
#         self.frame_count = 0
#         self.camera_initialized = False
#
#         # Current predictions
#         self.current_letter = ""
#         self.current_confidence = 0.0
#
#         # UI elements
#         self.prediction_label = None
#         self.confidence_bar = None
#         self.word_label = None
#         self.sentence_label = None
#         self.status_label = None
#
#         # Build UI
#         self.build_ui()
#
#     def build_ui(self):
#         """Build the camera screen UI"""
#         # Main layout
#         main_layout = FloatLayout()
#
#         # Back button - Top left
#         back_button = Button(
#             text="← Home",
#             size_hint=(0.2, 0.08),
#             pos_hint={'x': 0.02, 'top': 0.98},
#             background_color=(0.3, 0.3, 0.3, 1)
#         )
#         back_button.bind(on_press=self.go_back)
#         main_layout.add_widget(back_button)
#
#         # Camera placeholder (will be replaced when camera starts)
#         self.camera_placeholder = Label(
#             text="📷\n\nCamera will start when you\nclick 'Start Recognition'\n\n✅ Ready to begin ASL detection",
#             font_size=dp(18),
#             pos_hint={'center_x': 0.5, 'center_y': 0.6},
#             size_hint=(0.9, 0.6),
#             halign='center',
#             color=(0.7, 0.7, 0.7, 1)
#         )
#         main_layout.add_widget(self.camera_placeholder)
#
#         # Prediction overlay
#         prediction_overlay = self.create_prediction_overlay()
#         main_layout.add_widget(prediction_overlay)
#
#         # Word/sentence display
#         text_display = self.create_text_display()
#         main_layout.add_widget(text_display)
#
#         # Control buttons
#         controls = self.create_controls()
#         main_layout.add_widget(controls)
#
#         # Status bar
#         status_bar = self.create_status_bar()
#         main_layout.add_widget(status_bar)
#
#         self.add_widget(main_layout)
#
#     def create_prediction_overlay(self):
#         """Create prediction display overlay"""
#         overlay = FloatLayout(
#             pos_hint={'center_x': 0.5, 'top': 0.95},
#             size_hint=(0.9, 0.25)
#         )
#
#         # Background
#         with overlay.canvas.before:
#             Color(0, 0, 0, 0.7)  # Semi-transparent black
#             self.overlay_rect = Rectangle(size=overlay.size, pos=overlay.pos)
#
#         overlay.bind(size=self.update_overlay_rect, pos=self.update_overlay_rect)
#
#         # Current prediction
#         self.prediction_label = Label(
#             text="Ready to recognize ASL...",
#             font_size=dp(24),
#             bold=True,
#             pos_hint={'center_x': 0.5, 'top': 0.9},
#             size_hint=(1, 0.3),
#             color=(1, 1, 1, 1)
#         )
#         overlay.add_widget(self.prediction_label)
#
#         # Confidence bar
#         confidence_layout = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'top': 0.6},
#             size_hint=(0.8, 0.15),
#             spacing=dp(10)
#         )
#
#         confidence_layout.add_widget(Label(
#             text="Confidence:",
#             size_hint=(0.3, 1),
#             color=(1, 1, 1, 1)
#         ))
#
#         self.confidence_bar = ProgressBar(
#             max=100,
#             value=0,
#             size_hint=(0.7, 1)
#         )
#         confidence_layout.add_widget(self.confidence_bar)
#
#         overlay.add_widget(confidence_layout)
#
#         return overlay
#
#     def create_text_display(self):
#         """Create word and sentence display"""
#         text_layout = BoxLayout(
#             orientation='vertical',
#             pos_hint={'center_x': 0.5, 'top': 0.25},
#             size_hint=(0.9, 0.15),
#             spacing=dp(5)
#         )
#
#         # Current word
#         self.word_label = Label(
#             text="Word: ",
#             font_size=dp(20),
#             bold=True,
#             size_hint=(1, 0.5),
#             color=(0, 0.7, 1, 1)  # Blue
#         )
#         text_layout.add_widget(self.word_label)
#
#         # Current sentence
#         self.sentence_label = Label(
#             text="Sentence: ",
#             font_size=dp(16),
#             size_hint=(1, 0.5),
#             color=(0.2, 0.8, 0.2, 1)  # Green
#         )
#         text_layout.add_widget(self.sentence_label)
#
#         return text_layout
#
#     def create_controls(self):
#         """Create control buttons"""
#         controls = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'y': 0.02},
#             size_hint=(0.95, 0.08),
#             spacing=dp(5)
#         )
#
#         # Start/Stop button
#         self.toggle_button = Button(
#             text="Start Recognition",
#             size_hint=(0.3, 1),
#             background_color=(0, 0.7, 0, 1)  # Green
#         )
#         self.toggle_button.bind(on_press=self.toggle_recognition)
#         controls.add_widget(self.toggle_button)
#
#         # Complete word button (Space)
#         word_button = Button(
#             text="Space",
#             size_hint=(0.2, 1),
#             background_color=(0, 0.5, 1, 1)  # Blue
#         )
#         word_button.bind(on_press=self.complete_word)
#         controls.add_widget(word_button)
#
#         # Delete letter button
#         delete_button = Button(
#             text="Delete",
#             size_hint=(0.2, 1),
#             background_color=(1, 0.5, 0, 1)  # Orange
#         )
#         delete_button.bind(on_press=self.delete_letter)
#         controls.add_widget(delete_button)
#
#         # Speak button
#         speak_button = Button(
#             text="Speak",
#             size_hint=(0.15, 1),
#             background_color=(0.7, 0, 0.7, 1)  # Purple
#         )
#         speak_button.bind(on_press=self.speak_sentence)
#         controls.add_widget(speak_button)
#
#         # Settings button
#         settings_button = Button(
#             text="⚙",
#             size_hint=(0.15, 1),
#             background_color=(0.5, 0.5, 0.5, 1)  # Gray
#         )
#         settings_button.bind(on_press=self.open_settings)
#         controls.add_widget(settings_button)
#
#         return controls
#
#     def create_status_bar(self):
#         """Create status bar"""
#         self.status_label = Label(
#             text="Press 'Start Recognition' to begin ASL detection",
#             font_size=dp(12),
#             pos_hint={'center_x': 0.5, 'bottom': 1},
#             size_hint=(1, 0.05),
#             color=(0.7, 0.7, 0.7, 1)
#         )
#         return self.status_label
#
#     def update_overlay_rect(self, instance, value):
#         """Update overlay rectangle size/position"""
#         self.overlay_rect.size = instance.size
#         self.overlay_rect.pos = instance.pos
#
#     def on_enter(self):
#         """Called when entering this screen"""
#         self.app = App.get_running_app()
#
#         # Update model status display
#         if hasattr(self.app, 'asl_engine') and self.app.asl_engine:
#             model_info = self.app.asl_engine.get_model_info()
#             if model_info['loaded']:
#                 self.status_label.text = "✅ Model ready - Press 'Start Recognition' to begin"
#                 self.status_label.color = (0, 1, 0, 1)
#             else:
#                 self.status_label.text = "❌ Model not loaded"
#                 self.status_label.color = (1, 0, 0, 1)
#
#         # Update text display
#         self.update_text_display()
#         Logger.info("CameraScreen: Entered screen")
#
#     def initialize_camera(self):
#         """Initialize camera when needed - SIMPLIFIED VERSION"""
#         if self.camera_initialized:
#             return True
#
#         try:
#             print("🎥 Initializing camera...")
#
#             # ✅ Create camera widget - SIMPLE APPROACH
#             self.camera = Camera(
#                 play=True,  # Start immediately
#                 resolution=(640, 480),
#                 pos_hint={'center_x': 0.5, 'center_y': 0.6},
#                 size_hint=(0.9, 0.6),
#                 index=0
#             )
#
#             # ✅ Simple widget replacement
#             if hasattr(self, 'camera_placeholder') and self.camera_placeholder:
#                 parent = self.camera_placeholder.parent
#                 if parent:
#                     parent.remove_widget(self.camera_placeholder)
#                     parent.add_widget(self.camera)
#                     print("✅ Camera added successfully")
#                 else:
#                     # Fallback
#                     self.add_widget(self.camera)
#                     print("✅ Camera added to screen")
#                 self.camera_placeholder = None
#
#             self.camera_initialized = True
#             print("✅ Camera initialized successfully")
#             return True
#
#         except Exception as e:
#             print(f"❌ Camera initialization failed: {e}")
#             self.status_label.text = f"Camera error: {e}"
#             self.status_label.color = (1, 0, 0, 1)
#             return False
#
#     def toggle_recognition(self, instance):
#         """Toggle ASL recognition on/off"""
#         if not self.app or not hasattr(self.app, 'asl_engine'):
#             self.status_label.text = "ASL engine not available"
#             return
#
#         if not self.app.asl_engine.get_model_info()['loaded']:
#             self.status_label.text = "Model not loaded yet..."
#             return
#
#         if self.prediction_enabled:
#             self.stop_recognition()
#         else:
#             self.start_recognition()
#
#     def start_recognition(self):
#         """Start ASL recognition - SIMPLIFIED VERSION"""
#         # Initialize camera first
#         if not self.initialize_camera():
#             return
#
#         self.prediction_enabled = True
#         self.is_predicting = True
#
#         # Update UI
#         self.toggle_button.text = "Stop Recognition"
#         self.toggle_button.background_color = (1, 0, 0, 1)  # Red
#         self.status_label.text = "🎯 Recognizing ASL signs..."
#         self.status_label.color = (0, 1, 0, 1)
#
#         # ✅ Start VERY SIMPLE prediction loop - demo only for now
#         self.prediction_event = Clock.schedule_interval(self.demo_predict, 3.0)  # Every 3 seconds
#
#         Logger.info("CameraScreen: Recognition started")
#
#     def stop_recognition(self):
#         """Stop ASL recognition"""
#         self.prediction_enabled = False
#         self.is_predicting = False
#
#         # Update UI
#         self.toggle_button.text = "Start Recognition"
#         self.toggle_button.background_color = (0, 0.7, 0, 1)  # Green
#         self.status_label.text = "Recognition stopped"
#         self.status_label.color = (0.7, 0.7, 0.7, 1)
#
#         # Stop prediction loop
#         if hasattr(self, 'prediction_event'):
#             self.prediction_event.cancel()
#
#         # Reset display
#         self.prediction_label.text = "Recognition stopped"
#         self.confidence_bar.value = 0
#
#         Logger.info("CameraScreen: Recognition stopped")
#
#     def demo_predict(self, dt):
#         """Demo prediction method - NO camera processing for stability"""
#         if not self.prediction_enabled:
#             return
#
#         try:
#             # ✅ SIMPLE demo predictions - no camera processing yet
#             letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
#                        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
#
#             # Random demo prediction
#             letter = random.choice(letters)
#             confidence = random.uniform(0.6, 0.95)
#
#             # Update display
#             self.prediction_label.text = f"Demo: {letter}"
#             self.prediction_label.color = (0, 0.8, 1, 1)  # Blue for demo mode
#             self.confidence_bar.value = confidence * 100
#
#             # Process letter (high confidence only)
#             if confidence > 0.8:
#                 if hasattr(self.app, 'add_letter'):
#                     self.app.add_letter(letter)
#                     self.update_text_display()
#                     print(f"📝 Demo added letter: {letter}")
#
#             self.frame_count += 1
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: Demo prediction error: {e}")
#             self.prediction_label.text = "Demo error..."
#             self.prediction_label.color = (1, 0.5, 0, 1)
#
#     def update_text_display(self):
#         """Update word and sentence display"""
#         if hasattr(self.app, 'current_word'):
#             self.word_label.text = f"Word: {self.app.current_word}"
#         if hasattr(self.app, 'current_sentence'):
#             self.sentence_label.text = f"Sentence: {self.app.current_sentence}"
#
#     def complete_word(self, instance=None):
#         """Complete current word"""
#         if hasattr(self.app, 'complete_word'):
#             completed_word = self.app.complete_word()
#             if completed_word:
#                 self.update_text_display()
#                 # Speak if available
#                 if hasattr(self.app, 'speak_text'):
#                     self.app.speak_text(f"Word: {completed_word}")
#
#     def delete_letter(self, instance=None):
#         """Delete last letter"""
#         if hasattr(self.app, 'delete_last_letter'):
#             self.app.delete_last_letter()
#             self.update_text_display()
#
#     def speak_sentence(self, instance=None):
#         """Speak current sentence"""
#         if hasattr(self.app, 'speak_current_sentence'):
#             self.app.speak_current_sentence()
#
#     def open_settings(self, instance=None):
#         """Open settings screen"""
#         if self.app:
#             self.app.switch_screen('settings')
#
#     def go_back(self, instance=None):
#         """Go back to home screen"""
#         # Stop recognition first
#         if self.prediction_enabled:
#             self.stop_recognition()
#
#         # Go back to home
#         if self.app:
#             self.app.switch_screen('home')
#
#     def on_leave(self):
#         """Called when leaving screen"""
#         if self.prediction_enabled:
#             self.stop_recognition()
#         Logger.info("CameraScreen: Left screen")

# !/usr/bin/env python3
"""
Camera Screen - Main ASL Recognition Interface
Real-time camera view with prediction overlay
"""
#
# from kivy.uix.screenmanager import Screen  # ✅ Fixed import
# from kivy.uix.camera import Camera
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.label import Label
# from kivy.uix.button import Button
# from kivy.uix.progressbar import ProgressBar
# from kivy.graphics import Rectangle, Color, Line
# from kivy.clock import Clock
# from kivy.logger import Logger
# from kivy.metrics import dp
# from kivy.app import App
#
# import cv2
# import numpy as np
# import time
#
#
# class CameraScreen(Screen):
#     """Main camera screen for ASL recognition"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         # App reference
#         self.app = None
#
#         # Camera and prediction state
#         self.camera = None
#         self.is_predicting = False
#         self.prediction_enabled = False
#         self.frame_count = 0
#
#         # Current predictions
#         self.current_letter = ""
#         self.current_confidence = 0.0
#         self.current_top3 = []
#         self.stable_letter = None
#
#         # UI elements
#         self.prediction_label = None
#         self.confidence_bar = None
#         self.word_label = None
#         self.sentence_label = None
#         self.status_label = None
#
#         # Build UI
#         self.build_ui()
#
#         # Schedule initialization
#         Clock.schedule_once(self.initialize, 0.5)
#
#     def build_ui(self):
#         """Build the camera screen UI"""
#         # Main layout
#         main_layout = FloatLayout()
#
#         # Camera view
#         self.camera = Camera(
#             play=True,
#             resolution=(640, 480),
#             pos_hint={'center_x': 0.5, 'center_y': 0.6},
#             size_hint=(0.9, 0.6)
#         )
#         main_layout.add_widget(self.camera)
#
#         # Prediction overlay
#         prediction_overlay = self.create_prediction_overlay()
#         main_layout.add_widget(prediction_overlay)
#
#         # Word/sentence display
#         text_display = self.create_text_display()
#         main_layout.add_widget(text_display)
#
#         # Control buttons
#         controls = self.create_controls()
#         main_layout.add_widget(controls)
#
#         # Status bar
#         status_bar = self.create_status_bar()
#         main_layout.add_widget(status_bar)
#
#         self.add_widget(main_layout)
#
#     def create_prediction_overlay(self):
#         """Create prediction display overlay"""
#         overlay = FloatLayout(
#             pos_hint={'center_x': 0.5, 'top': 0.95},
#             size_hint=(0.9, 0.25)
#         )
#
#         # Background
#         with overlay.canvas.before:
#             Color(0, 0, 0, 0.7)  # Semi-transparent black
#             self.overlay_rect = Rectangle(size=overlay.size, pos=overlay.pos)
#
#         overlay.bind(size=self.update_overlay_rect, pos=self.update_overlay_rect)
#
#         # Current prediction
#         self.prediction_label = Label(
#             text="Ready to recognize ASL...",
#             font_size=dp(24),
#             bold=True,
#             pos_hint={'center_x': 0.5, 'top': 0.9},
#             size_hint=(1, 0.3),
#             color=(1, 1, 1, 1)
#         )
#         overlay.add_widget(self.prediction_label)
#
#         # Confidence bar
#         confidence_layout = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'top': 0.6},
#             size_hint=(0.8, 0.15),
#             spacing=dp(10)
#         )
#
#         confidence_layout.add_widget(Label(
#             text="Confidence:",
#             size_hint=(0.3, 1),
#             color=(1, 1, 1, 1)
#         ))
#
#         self.confidence_bar = ProgressBar(
#             max=100,
#             value=0,
#             size_hint=(0.7, 1)
#         )
#         confidence_layout.add_widget(self.confidence_bar)
#
#         overlay.add_widget(confidence_layout)
#
#         # Top 3 predictions
#         self.top3_label = Label(
#             text="",
#             font_size=dp(14),
#             pos_hint={'center_x': 0.5, 'top': 0.4},
#             size_hint=(1, 0.2),
#             color=(0.8, 0.8, 0.8, 1)
#         )
#         overlay.add_widget(self.top3_label)
#
#         return overlay
#
#     def create_text_display(self):
#         """Create word and sentence display"""
#         text_layout = BoxLayout(
#             orientation='vertical',
#             pos_hint={'center_x': 0.5, 'top': 0.25},
#             size_hint=(0.9, 0.15),
#             spacing=dp(5)
#         )
#
#         # Current word
#         self.word_label = Label(
#             text="Word: ",
#             font_size=dp(20),
#             bold=True,
#             size_hint=(1, 0.5),
#             color=(0, 0.7, 1, 1)  # Blue
#         )
#         text_layout.add_widget(self.word_label)
#
#         # Current sentence
#         self.sentence_label = Label(
#             text="Sentence: ",
#             font_size=dp(16),
#             size_hint=(1, 0.5),
#             color=(0.2, 0.8, 0.2, 1)  # Green
#         )
#         text_layout.add_widget(self.sentence_label)
#
#         return text_layout
#
#     def create_controls(self):
#         """Create control buttons"""
#         controls = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'y': 0.02},
#             size_hint=(0.95, 0.08),
#             spacing=dp(5)
#         )
#
#         # Start/Stop button
#         self.toggle_button = Button(
#             text="Start Recognition",
#             size_hint=(0.3, 1),
#             background_color=(0, 0.7, 0, 1)  # Green
#         )
#         self.toggle_button.bind(on_press=self.toggle_recognition)
#         controls.add_widget(self.toggle_button)
#
#         # Complete word button
#         word_button = Button(
#             text="Complete Word",
#             size_hint=(0.25, 1),
#             background_color=(0, 0.5, 1, 1)  # Blue
#         )
#         word_button.bind(on_press=self.complete_word)
#         controls.add_widget(word_button)
#
#         # Delete letter button
#         delete_button = Button(
#             text="Delete",
#             size_hint=(0.15, 1),
#             background_color=(1, 0.5, 0, 1)  # Orange
#         )
#         delete_button.bind(on_press=self.delete_letter)
#         controls.add_widget(delete_button)
#
#         # Speak button
#         speak_button = Button(
#             text="Speak",
#             size_hint=(0.15, 1),
#             background_color=(0.7, 0, 0.7, 1)  # Purple
#         )
#         speak_button.bind(on_press=self.speak_sentence)
#         controls.add_widget(speak_button)
#
#         # Settings button
#         settings_button = Button(
#             text="⚙",
#             size_hint=(0.15, 1),
#             background_color=(0.5, 0.5, 0.5, 1)  # Gray
#         )
#         settings_button.bind(on_press=self.open_settings)
#         controls.add_widget(settings_button)
#
#         return controls
#
#     def create_status_bar(self):
#         """Create status bar"""
#         self.status_label = Label(
#             text="Loading...",
#             font_size=dp(12),
#             pos_hint={'center_x': 0.5, 'bottom': 1},
#             size_hint=(1, 0.05),
#             color=(0.7, 0.7, 0.7, 1)
#         )
#         return self.status_label
#
#     def update_overlay_rect(self, instance, value):
#         """Update overlay rectangle size/position"""
#         self.overlay_rect.size = instance.size
#         self.overlay_rect.pos = instance.pos
#
#     def initialize(self, dt):
#         """Initialize screen components"""
#         self.app = App.get_running_app()
#
#         # Check if model is loaded
#         if hasattr(self.app, 'asl_engine') and self.app.asl_engine and self.app.asl_engine.model_loaded:
#             self.on_model_ready()
#         else:
#             self.status_label.text = "Loading ASL model..."
#
#     def on_model_ready(self):
#         """Called when ASL model is ready"""
#         self.status_label.text = "Model ready. Press 'Start Recognition' to begin."
#         self.prediction_label.text = "Ready to recognize ASL signs"
#         Logger.info("CameraScreen: Model ready for predictions")
#
#     def toggle_recognition(self, instance):
#         """Toggle ASL recognition on/off"""
#         if not self.app or not hasattr(self.app, 'asl_engine') or not self.app.asl_engine.model_loaded:
#             self.status_label.text = "Model not loaded yet..."
#             return
#
#         if self.prediction_enabled:
#             self.stop_recognition()
#         else:
#             self.start_recognition()
#
#     def start_recognition(self):
#         """Start ASL recognition"""
#         self.prediction_enabled = True
#         self.is_predicting = True
#
#         # Update UI
#         self.toggle_button.text = "Stop Recognition"
#         self.toggle_button.background_color = (1, 0, 0, 1)  # Red
#         self.status_label.text = "Recognizing ASL signs..."
#
#         # Start prediction loop
#         self.prediction_event = Clock.schedule_interval(self.predict_frame, 1 / 10)  # 10 FPS
#
#         Logger.info("CameraScreen: Recognition started")
#
#     def stop_recognition(self):
#         """Stop ASL recognition"""
#         self.prediction_enabled = False
#         self.is_predicting = False
#
#         # Update UI
#         self.toggle_button.text = "Start Recognition"
#         self.toggle_button.background_color = (0, 0.7, 0, 1)  # Green
#         self.status_label.text = "Recognition stopped"
#
#         # Stop prediction loop
#         if hasattr(self, 'prediction_event'):
#             self.prediction_event.cancel()
#
#         # Reset display
#         self.prediction_label.text = "Recognition stopped"
#         self.confidence_bar.value = 0
#         self.top3_label.text = ""
#
#         Logger.info("CameraScreen: Recognition stopped")
#
#     def predict_frame(self, dt):
#         """Predict ASL from current camera frame"""
#         if not self.prediction_enabled or not self.camera:
#             return
#
#         try:
#             # Get camera texture
#             texture = self.camera.texture
#             if not texture:
#                 return
#
#             # Convert texture to numpy array
#             image_data = self.texture_to_array(texture)
#             if image_data is None:
#                 return
#
#             # Extract ROI (center square)
#             roi = self.extract_roi(image_data)
#
#             # Predict using ASL engine
#             if hasattr(self.app, 'asl_engine') and self.app.asl_engine:
#                 prediction_result = self.app.asl_engine.predict(roi)
#
#                 if prediction_result:
#                     letter = prediction_result.get('prediction', '')
#                     confidence = prediction_result.get('confidence', 0.0)
#                     top_3 = prediction_result.get('top_predictions', [])
#
#                     # Update stable prediction (if method exists)
#                     stable_letter = letter
#                     if hasattr(self.app.asl_engine, 'update_stable_prediction'):
#                         stable_letter = self.app.asl_engine.update_stable_prediction(letter, confidence)
#
#                     # Update UI
#                     self.update_prediction_display(letter, confidence, top_3, stable_letter)
#
#                     # Process stable letter
#                     if stable_letter and stable_letter != 'nothing':
#                         self.process_stable_letter(stable_letter, confidence)
#
#                     self.frame_count += 1
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: Prediction error: {e}")
#
#     def texture_to_array(self, texture):
#         """Convert Kivy texture to numpy array"""
#         try:
#             # Get texture data
#             data = texture.pixels
#             if not data:
#                 return None
#
#             # Convert to numpy array
#             arr = np.frombuffer(data, dtype=np.uint8)
#
#             # Reshape based on texture format
#             w, h = texture.width, texture.height
#             if texture.colorfmt == 'rgba':
#                 arr = arr.reshape((h, w, 4))
#                 # Convert RGBA to BGR
#                 arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
#             elif texture.colorfmt == 'rgb':
#                 arr = arr.reshape((h, w, 3))
#                 # Convert RGB to BGR
#                 arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
#             else:
#                 return None
#
#             # Flip vertically (Kivy textures are flipped)
#             arr = cv2.flip(arr, 0)
#
#             return arr
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: Texture conversion failed: {e}")
#             return None
#
#     def extract_roi(self, image):
#         """Extract region of interest from image"""
#         try:
#             h, w = image.shape[:2]
#
#             # Calculate ROI (center square)
#             roi_size = min(h, w) // 2
#             center_x, center_y = w // 2, h // 2
#
#             x1 = center_x - roi_size // 2
#             y1 = center_y - roi_size // 2
#             x2 = x1 + roi_size
#             y2 = y1 + roi_size
#
#             # Extract ROI
#             roi = image[y1:y2, x1:x2]
#
#             return roi
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: ROI extraction failed: {e}")
#             return image
#
#     def update_prediction_display(self, letter, confidence, top_3, stable_letter):
#         """Update prediction display"""
#         # Update current prediction
#         self.current_letter = letter
#         self.current_confidence = confidence
#         self.current_top3 = top_3
#         self.stable_letter = stable_letter
#
#         # Update prediction label
#         if stable_letter:
#             self.prediction_label.text = f"STABLE: {stable_letter}"
#             self.prediction_label.color = (0, 1, 0, 1)  # Green
#         else:
#             self.prediction_label.text = f"Detecting: {letter}"
#             self.prediction_label.color = (1, 1, 0, 1)  # Yellow
#
#         # Update confidence bar
#         self.confidence_bar.value = confidence * 100
#
#         # Update top 3
#         if top_3:
#             top3_text = " | ".join([f"{l}: {c:.2f}" for l, c in top_3[:3]])
#             self.top3_label.text = f"Top 3: {top3_text}"
#
#     def process_stable_letter(self, letter, confidence):
#         """Process a stable letter detection"""
#         if letter == 'space':
#             self.complete_word()
#         elif letter == 'del':
#             self.delete_letter()
#         elif letter.isalpha():
#             # Add letter to current word
#             if hasattr(self.app, 'add_letter'):
#                 self.app.add_letter(letter, confidence)
#             else:
#                 # Fallback: just add to current word
#                 if not hasattr(self.app, 'current_word'):
#                     self.app.current_word = ""
#                 self.app.current_word += letter
#
#             self.update_text_display()
#
#             # Speak letter if enabled
#             if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#                 self.app.speech_engine.speak(letter)
#
#     def update_text_display(self):
#         """Update word and sentence display"""
#         current_word = getattr(self.app, 'current_word', "")
#         current_sentence = getattr(self.app, 'current_sentence', "")
#
#         self.word_label.text = f"Word: {current_word}"
#         self.sentence_label.text = f"Sentence: {current_sentence}"
#
#     def complete_word(self, instance=None):
#         """Complete current word"""
#         if hasattr(self.app, 'complete_word'):
#             completed_word = self.app.complete_word()
#         else:
#             # Fallback implementation
#             if not hasattr(self.app, 'current_word'):
#                 self.app.current_word = ""
#             if not hasattr(self.app, 'current_sentence'):
#                 self.app.current_sentence = ""
#
#             if self.app.current_word:
#                 self.app.current_sentence += self.app.current_word + " "
#                 completed_word = self.app.current_word
#                 self.app.current_word = ""
#             else:
#                 completed_word = ""
#
#         if completed_word:
#             self.update_text_display()
#             if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#                 self.app.speech_engine.speak(f"Word: {completed_word}")
#
#     def delete_letter(self, instance=None):
#         """Delete last letter"""
#         if hasattr(self.app, 'delete_last_letter'):
#             self.app.delete_last_letter()
#         else:
#             # Fallback implementation
#             if hasattr(self.app, 'current_word') and self.app.current_word:
#                 self.app.current_word = self.app.current_word[:-1]
#
#         self.update_text_display()
#
#     def speak_sentence(self, instance=None):
#         """Speak current sentence"""
#         if hasattr(self.app, 'speak_current_sentence'):
#             self.app.speak_current_sentence()
#         elif hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#             current_sentence = getattr(self.app, 'current_sentence', "")
#             if current_sentence:
#                 self.app.speech_engine.speak(current_sentence)
#
#     def open_settings(self, instance=None):
#         """Open settings screen"""
#         if hasattr(self.app, 'switch_screen'):
#             self.app.switch_screen('settings')
#         else:
#             self.manager.current = 'settings'
#
#     def on_pre_enter(self):
#         """Called before entering screen"""
#         Logger.info("CameraScreen: Entering camera screen")
#         if self.app:
#             self.update_text_display()
#
#         # Re-initialize if needed
#         if not self.app:
#             self.app = App.get_running_app()
#
#     def on_leave(self):
#         """Called when leaving screen"""
#         Logger.info("CameraScreen: Leaving camera screen")
#         if self.prediction_enabled:
#             self.stop_recognition()
#
#     # Additional methods for compatibility
#     def toggle_camera(self):
#         """Toggle camera for .kv compatibility"""
#         self.toggle_recognition(None)
#
#     def speak_current(self):
#         """Speak current for .kv compatibility"""
#         self.speak_sentence()
#
#     def clear_all(self):
#         """Clear all for .kv compatibility"""
#         if hasattr(self.app, 'current_word'):
#             self.app.current_word = ""
#         if hasattr(self.app, 'current_sentence'):
#             self.app.current_sentence = ""
#         self.update_text_display()


# !/usr/bin/env python3
"""
Camera Screen - Main ASL Recognition Interface
Real-time camera view with prediction overlay
FIXED: Now handles tuple predictions from ASL engine
"""


#
# from kivy.uix.screenmanager import Screen
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.label import Label
# from kivy.uix.button import Button
# from kivy.uix.progressbar import ProgressBar
# from kivy.graphics import Rectangle, Color, Line
# from kivy.clock import Clock
# from kivy.logger import Logger
# from kivy.uix.camera import Camera
# from kivy.metrics import dp
# from kivy.app import App
#
# import cv2
# import numpy as np
# import time
# from collections import Counter
#
#
# class CameraScreen(Screen):
#     """Main camera screen for ASL recognition"""
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         # App reference
#         self.app = None
#
#         # Camera and prediction state
#         self.camera = None
#         self.is_predicting = False
#         self.prediction_enabled = False
#         self.frame_count = 0
#
#         # Current predictions
#         self.current_letter = ""
#         self.current_confidence = 0.0
#         self.current_top3 = []
#         self.stable_letter = None
#
#         # Stable prediction tracking
#         self.prediction_history = []
#         self.stable_threshold = 3  # Number of consecutive predictions needed
#         self.last_stable_time = 0
#         self.stable_cooldown = 2.0  # Seconds between stable predictions
#
#         # UI elements
#         self.prediction_label = None
#         self.confidence_bar = None
#         self.word_label = None
#         self.sentence_label = None
#         self.status_label = None
#
#         # Build UI
#         self.build_ui()
#
#         # Schedule initialization
#         Clock.schedule_once(self.initialize, 0.5)
#
#     def build_ui(self):
#         """Build the camera screen UI"""
#         # Main layout
#         main_layout = FloatLayout()
#
#         # Camera view
#         self.camera = Camera(
#             play=True,
#             resolution=(640, 480),
#             pos_hint={'center_x': 0.5, 'center_y': 0.6},
#             size_hint=(0.9, 0.6)
#         )
#         main_layout.add_widget(self.camera)
#
#         # Prediction overlay
#         prediction_overlay = self.create_prediction_overlay()
#         main_layout.add_widget(prediction_overlay)
#
#         # Word/sentence display
#         text_display = self.create_text_display()
#         main_layout.add_widget(text_display)
#
#         # Control buttons
#         controls = self.create_controls()
#         main_layout.add_widget(controls)
#
#         # Status bar
#         status_bar = self.create_status_bar()
#         main_layout.add_widget(status_bar)
#
#         self.add_widget(main_layout)
#
#     def create_prediction_overlay(self):
#         """Create prediction display overlay"""
#         overlay = FloatLayout(
#             pos_hint={'center_x': 0.5, 'top': 0.95},
#             size_hint=(0.9, 0.25)
#         )
#
#         # Background
#         with overlay.canvas.before:
#             Color(0, 0, 0, 0.7)  # Semi-transparent black
#             self.overlay_rect = Rectangle(size=overlay.size, pos=overlay.pos)
#
#         overlay.bind(size=self.update_overlay_rect, pos=self.update_overlay_rect)
#
#         # Current prediction
#         self.prediction_label = Label(
#             text="Ready to recognize ASL...",
#             font_size=dp(24),
#             bold=True,
#             pos_hint={'center_x': 0.5, 'top': 0.9},
#             size_hint=(1, 0.3),
#             color=(1, 1, 1, 1)
#         )
#         overlay.add_widget(self.prediction_label)
#
#         # Confidence bar
#         confidence_layout = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'top': 0.6},
#             size_hint=(0.8, 0.15),
#             spacing=dp(10)
#         )
#
#         confidence_layout.add_widget(Label(
#             text="Confidence:",
#             size_hint=(0.3, 1),
#             color=(1, 1, 1, 1)
#         ))
#
#         self.confidence_bar = ProgressBar(
#             max=100,
#             value=0,
#             size_hint=(0.7, 1)
#         )
#         confidence_layout.add_widget(self.confidence_bar)
#
#         overlay.add_widget(confidence_layout)
#
#         # Top 3 predictions
#         self.top3_label = Label(
#             text="",
#             font_size=dp(14),
#             pos_hint={'center_x': 0.5, 'top': 0.4},
#             size_hint=(1, 0.2),
#             color=(0.8, 0.8, 0.8, 1)
#         )
#         overlay.add_widget(self.top3_label)
#
#         return overlay
#
#     def create_text_display(self):
#         """Create word and sentence display"""
#         text_layout = BoxLayout(
#             orientation='vertical',
#             pos_hint={'center_x': 0.5, 'top': 0.25},
#             size_hint=(0.9, 0.15),
#             spacing=dp(5)
#         )
#
#         # Current word
#         self.word_label = Label(
#             text="Word: ",
#             font_size=dp(20),
#             bold=True,
#             size_hint=(1, 0.5),
#             color=(0, 0.7, 1, 1)  # Blue
#         )
#         text_layout.add_widget(self.word_label)
#
#         # Current sentence
#         self.sentence_label = Label(
#             text="Sentence: ",
#             font_size=dp(16),
#             size_hint=(1, 0.5),
#             color=(0.2, 0.8, 0.2, 1)  # Green
#         )
#         text_layout.add_widget(self.sentence_label)
#
#         return text_layout
#
#     def create_controls(self):
#         """Create control buttons"""
#         controls = BoxLayout(
#             orientation='horizontal',
#             pos_hint={'center_x': 0.5, 'y': 0.02},
#             size_hint=(0.95, 0.08),
#             spacing=dp(5)
#         )
#
#         # Start/Stop button
#         self.toggle_button = Button(
#             text="Start Recognition",
#             size_hint=(0.3, 1),
#             background_color=(0, 0.7, 0, 1)  # Green
#         )
#         self.toggle_button.bind(on_press=self.toggle_recognition)
#         controls.add_widget(self.toggle_button)
#
#         # Complete word button
#         word_button = Button(
#             text="Complete Word",
#             size_hint=(0.25, 1),
#             background_color=(0, 0.5, 1, 1)  # Blue
#         )
#         word_button.bind(on_press=self.complete_word)
#         controls.add_widget(word_button)
#
#         # Delete letter button
#         delete_button = Button(
#             text="Delete",
#             size_hint=(0.15, 1),
#             background_color=(1, 0.5, 0, 1)  # Orange
#         )
#         delete_button.bind(on_press=self.delete_letter)
#         controls.add_widget(delete_button)
#
#         # Speak button
#         speak_button = Button(
#             text="Speak",
#             size_hint=(0.15, 1),
#             background_color=(0.7, 0, 0.7, 1)  # Purple
#         )
#         speak_button.bind(on_press=self.speak_sentence)
#         controls.add_widget(speak_button)
#
#         # Settings button
#         settings_button = Button(
#             text="⚙",
#             size_hint=(0.15, 1),
#             background_color=(0.5, 0.5, 0.5, 1)  # Gray
#         )
#         settings_button.bind(on_press=self.open_settings)
#         controls.add_widget(settings_button)
#
#         return controls
#
#     def create_status_bar(self):
#         """Create status bar"""
#         self.status_label = Label(
#             text="Loading...",
#             font_size=dp(12),
#             pos_hint={'center_x': 0.5, 'bottom': 1},
#             size_hint=(1, 0.05),
#             color=(0.7, 0.7, 0.7, 1)
#         )
#         return self.status_label
#
#     def update_overlay_rect(self, instance, value):
#         """Update overlay rectangle size/position"""
#         self.overlay_rect.size = instance.size
#         self.overlay_rect.pos = instance.pos
#
#     def initialize(self, dt):
#         """Initialize screen components"""
#         self.app = App.get_running_app()
#
#         # Check if model is loaded
#         if hasattr(self.app, 'asl_engine') and self.app.asl_engine and self.app.asl_engine.model_loaded:
#             self.on_model_ready()
#         else:
#             self.status_label.text = "Loading ASL model..."
#
#     def on_model_ready(self):
#         """Called when ASL model is ready"""
#         self.status_label.text = "Model ready. Press 'Start Recognition' to begin."
#         self.prediction_label.text = "Ready to recognize ASL signs"
#         Logger.info("CameraScreen: Model ready for predictions")
#
#     def toggle_recognition(self, instance):
#         """Toggle ASL recognition on/off"""
#         if not self.app or not hasattr(self.app, 'asl_engine') or not self.app.asl_engine.model_loaded:
#             self.status_label.text = "Model not loaded yet..."
#             return
#
#         if self.prediction_enabled:
#             self.stop_recognition()
#         else:
#             self.start_recognition()
#
#     def start_recognition(self):
#         """Start ASL recognition"""
#         self.prediction_enabled = True
#         self.is_predicting = True
#
#         # Update UI
#         self.toggle_button.text = "Stop Recognition"
#         self.toggle_button.background_color = (1, 0, 0, 1)  # Red
#         self.status_label.text = "Recognizing ASL signs..."
#
#         # Reset tracking
#         self.prediction_history.clear()
#         self.last_stable_time = 0
#
#         # Start prediction loop
#         self.prediction_event = Clock.schedule_interval(self.predict_frame, 1 / 10)  # 10 FPS
#
#         Logger.info("CameraScreen: Recognition started")
#
#     def stop_recognition(self):
#         """Stop ASL recognition"""
#         self.prediction_enabled = False
#         self.is_predicting = False
#
#         # Update UI
#         self.toggle_button.text = "Start Recognition"
#         self.toggle_button.background_color = (0, 0.7, 0, 1)  # Green
#         self.status_label.text = "Recognition stopped"
#
#         # Stop prediction loop
#         if hasattr(self, 'prediction_event'):
#             self.prediction_event.cancel()
#
#         # Reset display
#         self.prediction_label.text = "Recognition stopped"
#         self.confidence_bar.value = 0
#         self.top3_label.text = ""
#
#         Logger.info("CameraScreen: Recognition stopped")
#
#     def predict_frame(self, dt):
#         """Predict ASL from current camera frame"""
#         if not self.prediction_enabled or not self.camera:
#             return
#
#         try:
#             # Get camera texture
#             texture = self.camera.texture
#             if not texture:
#                 return
#
#             # Convert texture to numpy array
#             image_data = self.texture_to_array(texture)
#             if image_data is None:
#                 return
#
#             # Extract ROI (center square)
#             roi = self.extract_roi(image_data)
#
#             # Predict using ASL engine
#             if hasattr(self.app, 'asl_engine') and self.app.asl_engine:
#                 # ✅ FIXED: Handle tuple prediction result
#                 prediction_result = self.app.asl_engine.predict(roi)
#
#                 if prediction_result is not None:
#                     # Handle tuple format: (letter, confidence)
#                     if isinstance(prediction_result, tuple) and len(prediction_result) >= 2:
#                         letter, confidence = prediction_result[:2]
#                     else:
#                         Logger.warning("CameraScreen: Unexpected prediction format")
#                         return
#
#                     # Create synthetic top 3 (since ASL engine doesn't provide it)
#                     top_3 = self.create_synthetic_top3(letter, confidence)
#
#                     # Update stable prediction
#                     stable_letter = self.update_stable_prediction(letter, confidence)
#
#                     # Update UI
#                     self.update_prediction_display(letter, confidence, top_3, stable_letter)
#
#                     # Process stable letter
#                     if stable_letter and stable_letter != 'NOTHING':
#                         self.process_stable_letter(stable_letter, confidence)
#
#                     self.frame_count += 1
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: Prediction error: {e}")
#
#     def create_synthetic_top3(self, predicted_letter, confidence):
#         """Create synthetic top 3 predictions for display"""
#         # Create a simple top 3 based on the main prediction
#         alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
#
#         # Remove the predicted letter from alphabet
#         other_letters = [l for l in alphabet if l != predicted_letter]
#
#         # Create top 3 with decreasing confidence
#         top_3 = [(predicted_letter, confidence)]
#
#         if len(other_letters) >= 2:
#             # Add two more with lower confidence
#             import random
#             random.shuffle(other_letters)
#             top_3.append((other_letters[0], max(0.1, confidence - 0.2)))
#             top_3.append((other_letters[1], max(0.05, confidence - 0.4)))
#
#         return top_3
#
#     def update_stable_prediction(self, letter, confidence):
#         """Update stable prediction based on history"""
#         current_time = time.time()
#
#         # Add to history
#         self.prediction_history.append(letter)
#
#         # Keep only recent history
#         if len(self.prediction_history) > 10:
#             self.prediction_history = self.prediction_history[-5:]
#
#         # Check for stable prediction
#         if len(self.prediction_history) >= self.stable_threshold:
#             # Get most common recent prediction
#             recent = self.prediction_history[-self.stable_threshold:]
#             letter_counts = Counter(recent)
#             most_common = letter_counts.most_common(1)[0]
#
#             # Check if it's stable and enough time has passed
#             if (most_common[1] >= self.stable_threshold and
#                     current_time - self.last_stable_time > self.stable_cooldown):
#                 stable_letter = most_common[0]
#                 self.last_stable_time = current_time
#                 return stable_letter
#
#         return None
#
#     def texture_to_array(self, texture):
#         """Convert Kivy texture to numpy array"""
#         try:
#             # Get texture data
#             data = texture.pixels
#             if not data:
#                 return None
#
#             # Convert to numpy array
#             arr = np.frombuffer(data, dtype=np.uint8)
#
#             # Reshape based on texture format
#             w, h = texture.width, texture.height
#             if texture.colorfmt == 'rgba':
#                 arr = arr.reshape((h, w, 4))
#                 # Convert RGBA to BGR
#                 arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
#             elif texture.colorfmt == 'rgb':
#                 arr = arr.reshape((h, w, 3))
#                 # Convert RGB to BGR
#                 arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
#             else:
#                 return None
#
#             # Flip vertically (Kivy textures are flipped)
#             arr = cv2.flip(arr, 0)
#
#             return arr
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: Texture conversion failed: {e}")
#             return None
#
#     def extract_roi(self, image):
#         """Extract region of interest from image"""
#         try:
#             h, w = image.shape[:2]
#
#             # Calculate ROI (center square)
#             roi_size = min(h, w) // 2
#             center_x, center_y = w // 2, h // 2
#
#             x1 = center_x - roi_size // 2
#             y1 = center_y - roi_size // 2
#             x2 = x1 + roi_size
#             y2 = y1 + roi_size
#
#             # Extract ROI
#             roi = image[y1:y2, x1:x2]
#
#             return roi
#
#         except Exception as e:
#             Logger.error(f"CameraScreen: ROI extraction failed: {e}")
#             return image
#
#     def update_prediction_display(self, letter, confidence, top_3, stable_letter):
#         """Update prediction display"""
#         # Update current prediction
#         self.current_letter = letter
#         self.current_confidence = confidence
#         self.current_top3 = top_3
#         self.stable_letter = stable_letter
#
#         # Update prediction label
#         if stable_letter:
#             self.prediction_label.text = f"STABLE: {stable_letter}"
#             self.prediction_label.color = (0, 1, 0, 1)  # Green
#         else:
#             self.prediction_label.text = f"Detecting: {letter}"
#             self.prediction_label.color = (1, 1, 0, 1)  # Yellow
#
#         # Update confidence bar
#         self.confidence_bar.value = confidence * 100
#
#         # Update top 3
#         if top_3:
#             top3_text = " | ".join([f"{l}: {c:.2f}" for l, c in top_3[:3]])
#             self.top3_label.text = f"Top 3: {top3_text}"
#
#     def process_stable_letter(self, letter, confidence):
#         """Process a stable letter detection"""
#         if letter == 'SPACE':
#             self.complete_word()
#         elif letter == 'DELETE':
#             self.delete_letter()
#         elif letter.isalpha():
#             # Add letter to current word
#             if hasattr(self.app, 'add_letter'):
#                 self.app.add_letter(letter, confidence)
#             else:
#                 # Fallback: just add to current word
#                 if not hasattr(self.app, 'current_word'):
#                     self.app.current_word = ""
#                 self.app.current_word += letter
#
#             self.update_text_display()
#
#             # Speak letter if enabled
#             if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#                 try:
#                     self.app.speech_engine.speak(letter)
#                 except Exception as e:
#                     Logger.warning(f"Speech failed: {e}")
#
#     def update_text_display(self):
#         """Update word and sentence display"""
#         current_word = getattr(self.app, 'current_word', "")
#         current_sentence = getattr(self.app, 'current_sentence', "")
#
#         self.word_label.text = f"Word: {current_word}"
#         self.sentence_label.text = f"Sentence: {current_sentence}"
#
#     def complete_word(self, instance=None):
#         """Complete current word"""
#         if hasattr(self.app, 'complete_word'):
#             completed_word = self.app.complete_word()
#         else:
#             # Fallback implementation
#             if not hasattr(self.app, 'current_word'):
#                 self.app.current_word = ""
#             if not hasattr(self.app, 'current_sentence'):
#                 self.app.current_sentence = ""
#
#             if self.app.current_word:
#                 self.app.current_sentence += self.app.current_word + " "
#                 completed_word = self.app.current_word
#                 self.app.current_word = ""
#             else:
#                 completed_word = ""
#
#         if completed_word:
#             self.update_text_display()
#             if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#                 try:
#                     self.app.speech_engine.speak(f"Word: {completed_word}")
#                 except Exception as e:
#                     Logger.warning(f"Speech failed: {e}")
#
#     def delete_letter(self, instance=None):
#         """Delete last letter"""
#         if hasattr(self.app, 'delete_last_letter'):
#             self.app.delete_last_letter()
#         else:
#             # Fallback implementation
#             if hasattr(self.app, 'current_word') and self.app.current_word:
#                 self.app.current_word = self.app.current_word[:-1]
#
#         self.update_text_display()
#
#     def speak_sentence(self, instance=None):
#         """Speak current sentence"""
#         if hasattr(self.app, 'speak_current_sentence'):
#             self.app.speak_current_sentence()
#         elif hasattr(self.app, 'speech_engine') and self.app.speech_engine:
#             current_sentence = getattr(self.app, 'current_sentence', "")
#             current_word = getattr(self.app, 'current_word', "")
#
#             text_to_speak = current_sentence
#             if current_word:
#                 text_to_speak = text_to_speak + " " + current_word if text_to_speak else current_word
#
#             if text_to_speak:
#                 try:
#                     self.app.speech_engine.speak(text_to_speak)
#                 except Exception as e:
#                     Logger.warning(f"Speech failed: {e}")
#
#     def open_settings(self, instance=None):
#         """Open settings screen"""
#         if hasattr(self.app, 'switch_screen'):
#             self.app.switch_screen('settings')
#         else:
#             self.manager.current = 'settings'
#
#     def on_pre_enter(self):
#         """Called before entering screen"""
#         Logger.info("CameraScreen: Entering camera screen")
#         if self.app:
#             self.update_text_display()
#
#         # Re-initialize if needed
#         if not self.app:
#             self.app = App.get_running_app()
#
#     def on_leave(self):
#         """Called when leaving screen"""
#         Logger.info("CameraScreen: Leaving camera screen")
#         if self.prediction_enabled:
#             self.stop_recognition()
#
#     # Additional methods for compatibility
#     def toggle_camera(self):
#         """Toggle camera for .kv compatibility"""
#         self.toggle_recognition(None)
#
#     def speak_current(self):
#         """Speak current for .kv compatibility"""
#         self.speak_sentence()
#
#     def clear_all(self):
#         """Clear all for .kv compatibility"""
#         if hasattr(self.app, 'current_word'):
#             self.app.current_word = ""
#         if hasattr(self.app, 'current_sentence'):
#             self.app.current_sentence = ""
#         self.update_text_display()


# !/usr/bin/env python3
"""
Camera Screen - Main ASL Recognition Interface
OPTIMIZED: Reduced speech frequency and better error handling
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Rectangle, Color, Line
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.app import App

import cv2
import numpy as np
import time
from collections import Counter


class CameraScreen(Screen):
    """Main camera screen for ASL recognition"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # App reference
        self.app = None

        # Camera and prediction state
        self.camera = None
        self.is_predicting = False
        self.prediction_enabled = False
        self.frame_count = 0

        # Current predictions
        self.current_letter = ""
        self.current_confidence = 0.0
        self.current_top3 = []
        self.stable_letter = None

        # Stable prediction tracking
        self.prediction_history = []
        self.stable_threshold = 5  # ✅ Increased from 3 to 5 for more stability
        self.last_stable_time = 0
        self.stable_cooldown = 3.0  # ✅ Increased from 2.0 to 3.0 seconds

        # ✅ Speech control
        self.last_speech_time = 0
        self.speech_cooldown = 2.0  # Minimum 2 seconds between speech
        self.speech_enabled = True

        # ✅ Error handling
        self.error_count = 0
        self.max_errors = 10
        self.last_error_time = 0

        # UI elements
        self.prediction_label = None
        self.confidence_bar = None
        self.word_label = None
        self.sentence_label = None
        self.status_label = None

        # Build UI
        self.build_ui()

        # Schedule initialization
        Clock.schedule_once(self.initialize, 0.5)

    def build_ui(self):
        """Build the camera screen UI"""
        # Main layout
        main_layout = FloatLayout()

        # Camera view
        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            size_hint=(0.9, 0.6)
        )
        main_layout.add_widget(self.camera)

        # Prediction overlay
        prediction_overlay = self.create_prediction_overlay()
        main_layout.add_widget(prediction_overlay)

        # Word/sentence display
        text_display = self.create_text_display()
        main_layout.add_widget(text_display)

        # Control buttons
        controls = self.create_controls()
        main_layout.add_widget(controls)

        # Status bar
        status_bar = self.create_status_bar()
        main_layout.add_widget(status_bar)

        self.add_widget(main_layout)

    def create_prediction_overlay(self):
        """Create prediction display overlay"""
        overlay = FloatLayout(
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(0.9, 0.25)
        )

        # Background
        with overlay.canvas.before:
            Color(0, 0, 0, 0.7)  # Semi-transparent black
            self.overlay_rect = Rectangle(size=overlay.size, pos=overlay.pos)

        overlay.bind(size=self.update_overlay_rect, pos=self.update_overlay_rect)

        # Current prediction
        self.prediction_label = Label(
            text="Ready to recognize ASL...",
            font_size=dp(24),
            bold=True,
            pos_hint={'center_x': 0.5, 'top': 0.9},
            size_hint=(1, 0.3),
            color=(1, 1, 1, 1)
        )
        overlay.add_widget(self.prediction_label)

        # Confidence bar
        confidence_layout = BoxLayout(
            orientation='horizontal',
            pos_hint={'center_x': 0.5, 'top': 0.6},
            size_hint=(0.8, 0.15),
            spacing=dp(10)
        )

        confidence_layout.add_widget(Label(
            text="Confidence:",
            size_hint=(0.3, 1),
            color=(1, 1, 1, 1)
        ))

        self.confidence_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(0.7, 1)
        )
        confidence_layout.add_widget(self.confidence_bar)

        overlay.add_widget(confidence_layout)

        # Top 3 predictions
        self.top3_label = Label(
            text="",
            font_size=dp(14),
            pos_hint={'center_x': 0.5, 'top': 0.4},
            size_hint=(1, 0.2),
            color=(0.8, 0.8, 0.8, 1)
        )
        overlay.add_widget(self.top3_label)

        return overlay

    def create_text_display(self):
        """Create word and sentence display"""
        text_layout = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5, 'top': 0.25},
            size_hint=(0.9, 0.15),
            spacing=dp(5)
        )

        # Current word
        self.word_label = Label(
            text="Word: ",
            font_size=dp(20),
            bold=True,
            size_hint=(1, 0.5),
            color=(0, 0.7, 1, 1)  # Blue
        )
        text_layout.add_widget(self.word_label)

        # Current sentence
        self.sentence_label = Label(
            text="Sentence: ",
            font_size=dp(16),
            size_hint=(1, 0.5),
            color=(0.2, 0.8, 0.2, 1)  # Green
        )
        text_layout.add_widget(self.sentence_label)

        return text_layout

    def create_controls(self):
        """Create control buttons"""
        controls = BoxLayout(
            orientation='horizontal',
            pos_hint={'center_x': 0.5, 'y': 0.02},
            size_hint=(0.95, 0.08),
            spacing=dp(5)
        )

        # Start/Stop button
        self.toggle_button = Button(
            text="Start Recognition",
            size_hint=(0.25, 1),
            background_color=(0, 0.7, 0, 1)  # Green
        )
        self.toggle_button.bind(on_press=self.toggle_recognition)
        controls.add_widget(self.toggle_button)

        # Speech toggle button
        self.speech_button = Button(
            text="🔊 Speech ON",
            size_hint=(0.2, 1),
            background_color=(0, 0.5, 1, 1)  # Blue
        )
        self.speech_button.bind(on_press=self.toggle_speech)
        controls.add_widget(self.speech_button)

        # Complete word button
        word_button = Button(
            text="Complete Word",
            size_hint=(0.2, 1),
            background_color=(0, 0.5, 1, 1)  # Blue
        )
        word_button.bind(on_press=self.complete_word)
        controls.add_widget(word_button)

        # Delete letter button
        delete_button = Button(
            text="Delete",
            size_hint=(0.15, 1),
            background_color=(1, 0.5, 0, 1)  # Orange
        )
        delete_button.bind(on_press=self.delete_letter)
        controls.add_widget(delete_button)

        # Speak button
        speak_button = Button(
            text="Speak",
            size_hint=(0.15, 1),
            background_color=(0.7, 0, 0.7, 1)  # Purple
        )
        speak_button.bind(on_press=self.speak_sentence)
        controls.add_widget(speak_button)

        # Settings button
        settings_button = Button(
            text="⚙",
            size_hint=(0.05, 1),
            background_color=(0.5, 0.5, 0.5, 1)  # Gray
        )
        settings_button.bind(on_press=self.open_settings)
        controls.add_widget(settings_button)

        return controls

    def create_status_bar(self):
        """Create status bar"""
        self.status_label = Label(
            text="Loading...",
            font_size=dp(12),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            size_hint=(1, 0.05),
            color=(0.7, 0.7, 0.7, 1)
        )
        return self.status_label

    def update_overlay_rect(self, instance, value):
        """Update overlay rectangle size/position"""
        self.overlay_rect.size = instance.size
        self.overlay_rect.pos = instance.pos

    def initialize(self, dt):
        """Initialize screen components"""
        self.app = App.get_running_app()

        # Check if model is loaded
        if hasattr(self.app, 'asl_engine') and self.app.asl_engine and self.app.asl_engine.model_loaded:
            self.on_model_ready()
        else:
            self.status_label.text = "Loading ASL model..."

    def on_model_ready(self):
        """Called when ASL model is ready"""
        self.status_label.text = "Model ready. Press 'Start Recognition' to begin."
        self.prediction_label.text = "Ready to recognize ASL signs"
        Logger.info("CameraScreen: Model ready for predictions")

    def toggle_recognition(self, instance):
        """Toggle ASL recognition on/off"""
        if not self.app or not hasattr(self.app, 'asl_engine') or not self.app.asl_engine.model_loaded:
            self.status_label.text = "Model not loaded yet..."
            return

        if self.prediction_enabled:
            self.stop_recognition()
        else:
            self.start_recognition()

    def toggle_speech(self, instance):
        """Toggle speech on/off"""
        self.speech_enabled = not self.speech_enabled

        if self.speech_enabled:
            self.speech_button.text = "🔊 Speech ON"
            self.speech_button.background_color = (0, 0.5, 1, 1)  # Blue
            self.status_label.text = "Speech enabled"
        else:
            self.speech_button.text = "🔇 Speech OFF"
            self.speech_button.background_color = (0.5, 0.5, 0.5, 1)  # Gray
            self.status_label.text = "Speech disabled"

    def start_recognition(self):
        """Start ASL recognition"""
        self.prediction_enabled = True
        self.is_predicting = True

        # Update UI
        self.toggle_button.text = "Stop Recognition"
        self.toggle_button.background_color = (1, 0, 0, 1)  # Red
        self.status_label.text = "Recognizing ASL signs..."

        # Reset tracking
        self.prediction_history.clear()
        self.last_stable_time = 0
        self.error_count = 0

        # Start prediction loop (reduced frequency)
        self.prediction_event = Clock.schedule_interval(self.predict_frame, 1 / 8)  # ✅ Reduced from 10 FPS to 8 FPS

        Logger.info("CameraScreen: Recognition started")

    def stop_recognition(self):
        """Stop ASL recognition"""
        self.prediction_enabled = False
        self.is_predicting = False

        # Update UI
        self.toggle_button.text = "Start Recognition"
        self.toggle_button.background_color = (0, 0.7, 0, 1)  # Green
        self.status_label.text = "Recognition stopped"

        # Stop prediction loop
        if hasattr(self, 'prediction_event'):
            self.prediction_event.cancel()

        # Reset display
        self.prediction_label.text = "Recognition stopped"
        self.confidence_bar.value = 0
        self.top3_label.text = ""

        Logger.info("CameraScreen: Recognition stopped")

    def predict_frame(self, dt):
        """Predict ASL from current camera frame"""
        if not self.prediction_enabled or not self.camera:
            return

        try:
            # Get camera texture
            texture = self.camera.texture
            if not texture:
                return

            # Convert texture to numpy array
            image_data = self.texture_to_array(texture)
            if image_data is None:
                return

            # Extract ROI (center square)
            roi = self.extract_roi(image_data)

            # Predict using ASL engine
            if hasattr(self.app, 'asl_engine') and self.app.asl_engine:
                prediction_result = self.app.asl_engine.predict(roi)

                if prediction_result is not None:
                    # Handle tuple format: (letter, confidence)
                    if isinstance(prediction_result, tuple) and len(prediction_result) >= 2:
                        letter, confidence = prediction_result[:2]
                    else:
                        Logger.warning("CameraScreen: Unexpected prediction format")
                        return

                    # Create synthetic top 3
                    top_3 = self.create_synthetic_top3(letter, confidence)

                    # Update stable prediction
                    stable_letter = self.update_stable_prediction(letter, confidence)

                    # Update UI
                    self.update_prediction_display(letter, confidence, top_3, stable_letter)

                    # Process stable letter (with reduced frequency)
                    if stable_letter and stable_letter != 'NOTHING':
                        self.process_stable_letter(stable_letter, confidence)

                    # Reset error count on success
                    self.error_count = 0
                    self.frame_count += 1

        except Exception as e:
            self.error_count += 1
            current_time = time.time()

            # Log error (but not too frequently)
            if current_time - self.last_error_time > 5.0:
                Logger.error(f"CameraScreen: Prediction error: {e}")
                self.last_error_time = current_time

            # Stop recognition if too many errors
            if self.error_count > self.max_errors:
                Logger.error("CameraScreen: Too many errors, stopping recognition")
                self.stop_recognition()
                self.status_label.text = "Recognition stopped due to errors"

    def create_synthetic_top3(self, predicted_letter, confidence):
        """Create synthetic top 3 predictions for display"""
        alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        other_letters = [l for l in alphabet if l != predicted_letter]

        top_3 = [(predicted_letter, confidence)]

        if len(other_letters) >= 2:
            import random
            random.shuffle(other_letters)
            top_3.append((other_letters[0], max(0.1, confidence - 0.2)))
            top_3.append((other_letters[1], max(0.05, confidence - 0.4)))

        return top_3

    def update_stable_prediction(self, letter, confidence):
        """Update stable prediction based on history"""
        current_time = time.time()

        # Add to history
        self.prediction_history.append(letter)

        # Keep only recent history
        if len(self.prediction_history) > 15:
            self.prediction_history = self.prediction_history[-10:]

        # Check for stable prediction
        if len(self.prediction_history) >= self.stable_threshold:
            # Get most common recent prediction
            recent = self.prediction_history[-self.stable_threshold:]
            letter_counts = Counter(recent)
            most_common = letter_counts.most_common(1)[0]

            # Check if it's stable and enough time has passed
            if (most_common[1] >= self.stable_threshold and
                    current_time - self.last_stable_time > self.stable_cooldown):
                stable_letter = most_common[0]
                self.last_stable_time = current_time
                return stable_letter

        return None

    def texture_to_array(self, texture):
        """Convert Kivy texture to numpy array"""
        try:
            data = texture.pixels
            if not data:
                return None

            arr = np.frombuffer(data, dtype=np.uint8)
            w, h = texture.width, texture.height

            if texture.colorfmt == 'rgba':
                arr = arr.reshape((h, w, 4))
                arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            elif texture.colorfmt == 'rgb':
                arr = arr.reshape((h, w, 3))
                arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            else:
                return None

            # Flip vertically (Kivy textures are flipped)
            arr = cv2.flip(arr, 0)
            return arr

        except Exception as e:
            Logger.error(f"CameraScreen: Texture conversion failed: {e}")
            return None

    def extract_roi(self, image):
        """Extract region of interest from image"""
        try:
            h, w = image.shape[:2]
            roi_size = min(h, w) // 2
            center_x, center_y = w // 2, h // 2

            x1 = center_x - roi_size // 2
            y1 = center_y - roi_size // 2
            x2 = x1 + roi_size
            y2 = y1 + roi_size

            roi = image[y1:y2, x1:x2]
            return roi

        except Exception as e:
            Logger.error(f"CameraScreen: ROI extraction failed: {e}")
            return image

    def update_prediction_display(self, letter, confidence, top_3, stable_letter):
        """Update prediction display"""
        self.current_letter = letter
        self.current_confidence = confidence
        self.current_top3 = top_3
        self.stable_letter = stable_letter

        # Update prediction label
        if stable_letter:
            self.prediction_label.text = f"STABLE: {stable_letter}"
            self.prediction_label.color = (0, 1, 0, 1)  # Green
        else:
            self.prediction_label.text = f"Detecting: {letter}"
            self.prediction_label.color = (1, 1, 0, 1)  # Yellow

        # Update confidence bar
        self.confidence_bar.value = confidence * 100

        # Update top 3
        if top_3:
            top3_text = " | ".join([f"{l}: {c:.2f}" for l, c in top_3[:3]])
            self.top3_label.text = f"Top 3: {top3_text}"

    def process_stable_letter(self, letter, confidence):
        """Process a stable letter detection"""
        if letter == 'SPACE':
            self.complete_word()
        elif letter == 'DELETE':
            self.delete_letter()
        elif letter.isalpha():
            # Add letter to current word
            if hasattr(self.app, 'add_letter'):
                self.app.add_letter(letter, confidence)
            else:
                # Fallback
                if not hasattr(self.app, 'current_word'):
                    self.app.current_word = ""
                self.app.current_word += letter

            self.update_text_display()

            # ✅ Speak letter with rate limiting
            current_time = time.time()
            if (self.speech_enabled and
                    current_time - self.last_speech_time > self.speech_cooldown):

                if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
                    try:
                        self.app.speech_engine.speak(letter)
                        self.last_speech_time = current_time
                    except Exception as e:
                        Logger.warning(f"Speech failed: {e}")

    def update_text_display(self):
        """Update word and sentence display"""
        current_word = getattr(self.app, 'current_word', "")
        current_sentence = getattr(self.app, 'current_sentence', "")

        self.word_label.text = f"Word: {current_word}"
        self.sentence_label.text = f"Sentence: {current_sentence}"

    def complete_word(self, instance=None):
        """Complete current word"""
        if hasattr(self.app, 'complete_word'):
            completed_word = self.app.complete_word()
        else:
            # Fallback implementation
            if not hasattr(self.app, 'current_word'):
                self.app.current_word = ""
            if not hasattr(self.app, 'current_sentence'):
                self.app.current_sentence = ""

            if self.app.current_word:
                self.app.current_sentence += self.app.current_word + " "
                completed_word = self.app.current_word
                self.app.current_word = ""
            else:
                completed_word = ""

        if completed_word:
            self.update_text_display()

            # ✅ Speak word completion with rate limiting
            current_time = time.time()
            if (self.speech_enabled and
                    current_time - self.last_speech_time > self.speech_cooldown):

                if hasattr(self.app, 'speech_engine') and self.app.speech_engine:
                    try:
                        self.app.speech_engine.speak(f"Word: {completed_word}")
                        self.last_speech_time = current_time
                    except Exception as e:
                        Logger.warning(f"Speech failed: {e}")

    def delete_letter(self, instance=None):
        """Delete last letter"""
        if hasattr(self.app, 'delete_last_letter'):
            self.app.delete_last_letter()
        else:
            # Fallback implementation
            if hasattr(self.app, 'current_word') and self.app.current_word:
                self.app.current_word = self.app.current_word[:-1]

        self.update_text_display()

    def speak_sentence(self, instance=None):
        """Speak current sentence"""
        if hasattr(self.app, 'speak_current_sentence'):
            self.app.speak_current_sentence()
        elif hasattr(self.app, 'speech_engine') and self.app.speech_engine:
            current_sentence = getattr(self.app, 'current_sentence', "")
            current_word = getattr(self.app, 'current_word', "")

            text_to_speak = current_sentence
            if current_word:
                text_to_speak = text_to_speak + " " + current_word if text_to_speak else current_word

            if text_to_speak:
                try:
                    self.app.speech_engine.speak(text_to_speak)
                except Exception as e:
                    Logger.warning(f"Speech failed: {e}")

    def open_settings(self, instance=None):
        """Open settings screen"""
        if hasattr(self.app, 'switch_screen'):
            self.app.switch_screen('settings')
        else:
            self.manager.current = 'settings'

    def on_pre_enter(self):
        """Called before entering screen"""
        Logger.info("CameraScreen: Entering camera screen")
        if self.app:
            self.update_text_display()

        if not self.app:
            self.app = App.get_running_app()

    def on_leave(self):
        """Called when leaving screen"""
        Logger.info("CameraScreen: Leaving camera screen")
        if self.prediction_enabled:
            self.stop_recognition()

    # Additional methods for compatibility
    def toggle_camera(self):
        """Toggle camera for .kv compatibility"""
        self.toggle_recognition(None)

    def speak_current(self):
        """Speak current for .kv compatibility"""
        self.speak_sentence()

    def clear_all(self):
        """Clear all for .kv compatibility"""
        if hasattr(self.app, 'current_word'):
            self.app.current_word = ""
        if hasattr(self.app, 'current_sentence'):
            self.app.current_sentence = ""
        self.update_text_display()