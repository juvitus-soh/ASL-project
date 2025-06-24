# app/widgets/letter_history.py
"""
Letter recognition history widget
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from collections import defaultdict


class LetterHistory(ScrollView):
    """Display recognition history and statistics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid = GridLayout(cols=2, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.add_widget(self.grid)

        self.letter_counts = defaultdict(int)
        self.total_predictions = 0

        self.update_display()

    def add_prediction(self, letter, confidence):
        """Add a new prediction to history"""
        if letter not in ['nothing', 'del'] and confidence > 0.5:
            self.letter_counts[letter] += 1
            self.total_predictions += 1
            self.update_display()

    def update_display(self):
        """Update the history display"""
        self.grid.clear_widgets()

        # Title
        title = Label(
            text="Recognition Statistics",
            font_size='18sp',
            size_hint_y=None,
            height=40,
            color=get_color_from_hex('#2196F3')
        )
        self.grid.add_widget(title)
        self.grid.add_widget(Label())  # Empty cell

        # Total predictions
        total_label = Label(
            text="Total Predictions:",
            size_hint_y=None,
            height=30
        )
        total_count = Label(
            text=str(self.total_predictions),
            size_hint_y=None,
            height=30,
            color=get_color_from_hex('#4CAF50')
        )
        self.grid.add_widget(total_label)
        self.grid.add_widget(total_count)

        # Letter breakdown
        if self.letter_counts:
            # Sort by frequency
            sorted_letters = sorted(
                self.letter_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for letter, count in sorted_letters:
                letter_label = Label(
                    text=f"Letter {letter}:",
                    size_hint_y=None,
                    height=25
                )
                count_label = Label(
                    text=f"{count} times",
                    size_hint_y=None,
                    height=25,
                    color=get_color_from_hex('#666666')
                )
                self.grid.add_widget(letter_label)
                self.grid.add_widget(count_label)

    def clear_history(self):
        """Clear all history"""
        self.letter_counts.clear()
        self.total_predictions = 0
        self.update_display()