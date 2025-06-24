# app/widgets/word_builder.py
"""
Word building widget for ASL recognition
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex


class WordBuilder(BoxLayout):
    """Widget for building words from ASL letters"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.current_word = ""
        self.sentence = ""

        # Current word display
        self.word_display = Label(
            text="Current Word: ",
            font_size='20sp',
            size_hint_y=0.3,
            color=get_color_from_hex('#2196F3')
        )
        self.add_widget(self.word_display)

        # Sentence display
        self.sentence_display = Label(
            text="Sentence: ",
            font_size='16sp',
            size_hint_y=0.4,
            color=get_color_from_hex('#4CAF50'),
            text_size=(None, None),
            halign='left'
        )
        self.add_widget(self.sentence_display)

        # Control buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)

        self.space_btn = Button(
            text="Space",
            size_hint_x=0.3,
            background_color=get_color_from_hex('#FF9800')
        )
        self.space_btn.bind(on_press=self.add_space)

        self.backspace_btn = Button(
            text="⌫",
            size_hint_x=0.2,
            background_color=get_color_from_hex('#F44336')
        )
        self.backspace_btn.bind(on_press=self.backspace)

        self.clear_btn = Button(
            text="Clear",
            size_hint_x=0.25,
            background_color=get_color_from_hex('#9E9E9E')
        )
        self.clear_btn.bind(on_press=self.clear_all)

        self.speak_btn = Button(
            text="🔊",
            size_hint_x=0.25,
            background_color=get_color_from_hex('#4CAF50')
        )
        self.speak_btn.bind(on_press=self.speak_sentence)

        button_layout.add_widget(self.space_btn)
        button_layout.add_widget(self.backspace_btn)
        button_layout.add_widget(self.clear_btn)
        button_layout.add_widget(self.speak_btn)

        self.add_widget(button_layout)

        self.update_display()

    def add_letter(self, letter):
        """Add a letter to the current word"""
        if letter not in ['space', 'del', 'nothing']:
            self.current_word += letter.upper()
            self.update_display()

    def add_space(self, instance=None):
        """Add current word to sentence and start new word"""
        if self.current_word:
            if self.sentence:
                self.sentence += " " + self.current_word
            else:
                self.sentence = self.current_word
            self.current_word = ""
            self.update_display()

    def backspace(self, instance=None):
        """Remove last letter from current word"""
        if self.current_word:
            self.current_word = self.current_word[:-1]
            self.update_display()

    def clear_all(self, instance=None):
        """Clear everything"""
        self.current_word = ""
        self.sentence = ""
        self.update_display()

    def speak_sentence(self, instance=None):
        """Speak the current sentence"""
        text_to_speak = self.sentence
        if self.current_word:
            if text_to_speak:
                text_to_speak += " " + self.current_word
            else:
                text_to_speak = self.current_word

        if text_to_speak:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text_to_speak)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

    def update_display(self):
        """Update the display labels"""
        self.word_display.text = f"Current Word: {self.current_word}"
        self.sentence_display.text = f"Sentence: {self.sentence}"

        # Update text_size for proper text wrapping
        self.sentence_display.text_size = (self.width * 0.95, None)
