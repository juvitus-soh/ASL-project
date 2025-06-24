#!/usr/bin/env python3
"""
History Screen - Display recognition and word history with statistics
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.app import App
from kivy.metrics import dp
from datetime import datetime


class HistoryScreen(Screen):
    """History screen showing recognition statistics and history"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_manager = None
        self.build_ui()

    def build_ui(self):
        """Build the history screen UI"""
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )

        # Header
        header = self.create_header()
        main_layout.add_widget(header)

        # Tabbed content
        tabbed_content = self.create_tabbed_content()
        main_layout.add_widget(tabbed_content)

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
            text="Recognition History",
            font_size=dp(24),
            bold=True,
            size_hint=(0.6, 1)
        )
        header_layout.add_widget(title)

        # Refresh button
        refresh_btn = Button(
            text="🔄",
            size_hint=(0.2, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_data)
        header_layout.add_widget(refresh_btn)

        return header_layout

    def create_tabbed_content(self):
        """Create tabbed content area"""
        self.tab_panel = TabbedPanel(
            size_hint=(1, 0.9),
            do_default_tab=False
        )

        # Statistics tab
        stats_tab = TabbedPanelItem(text='📊 Stats')
        stats_tab.content = self.create_stats_content()
        self.tab_panel.add_widget(stats_tab)

        # Recent predictions tab
        predictions_tab = TabbedPanelItem(text='🔤 Letters')
        predictions_tab.content = self.create_predictions_content()
        self.tab_panel.add_widget(predictions_tab)

        # Words history tab
        words_tab = TabbedPanelItem(text='📝 Words')
        words_tab.content = self.create_words_content()
        self.tab_panel.add_widget(words_tab)

        # Set default tab
        self.tab_panel.default_tab = stats_tab

        return self.tab_panel

    def create_stats_content(self):
        """Create statistics content"""
        scroll = ScrollView()

        self.stats_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))

        # Will be populated in refresh_stats()
        self.refresh_stats()

        scroll.add_widget(self.stats_layout)
        return scroll

    def create_predictions_content(self):
        """Create predictions history content"""
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )

        # Controls
        controls = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10),
            padding=dp(10)
        )

        controls.add_widget(Label(
            text="Recent Letter Predictions:",
            font_size=dp(16),
            bold=True,
            size_hint=(0.7, 1)
        ))

        clear_btn = Button(
            text="Clear History",
            size_hint=(0.3, 1),
            background_color=(1, 0.3, 0.3, 1)
        )
        clear_btn.bind(on_press=self.clear_prediction_history)
        controls.add_widget(clear_btn)

        layout.add_widget(controls)

        # Scrollable predictions list
        scroll = ScrollView(size_hint=(1, 0.9))

        self.predictions_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(10)
        )
        self.predictions_layout.bind(minimum_height=self.predictions_layout.setter('height'))

        scroll.add_widget(self.predictions_layout)
        layout.add_widget(scroll)

        return layout

    def create_words_content(self):
        """Create words history content"""
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )

        # Controls
        controls = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10),
            padding=dp(10)
        )

        controls.add_widget(Label(
            text="Completed Words:",
            font_size=dp(16),
            bold=True,
            size_hint=(0.7, 1)
        ))

        export_btn = Button(
            text="Export Data",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        export_btn.bind(on_press=self.export_data)
        controls.add_widget(export_btn)

        layout.add_widget(controls)

        # Scrollable words list
        scroll = ScrollView(size_hint=(1, 0.9))

        self.words_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(10)
        )
        self.words_layout.bind(minimum_height=self.words_layout.setter('height'))

        scroll.add_widget(self.words_layout)
        layout.add_widget(scroll)

        return layout

    def refresh_stats(self):
        """Refresh statistics display"""
        if not self.storage_manager:
            app = App.get_running_app()
            self.storage_manager = getattr(app, 'storage_manager', None)

        if not self.storage_manager:
            return

        self.stats_layout.clear_widgets()

        # Get statistics
        pred_stats = self.storage_manager.get_prediction_stats()
        word_stats = self.storage_manager.get_word_stats()
        app_stats = self.storage_manager.get_app_stats()

        # Overall stats section
        overall_section = self.create_stat_section(
            "📊 Overall Statistics",
            [
                ("Total Predictions", f"{pred_stats.get('total_predictions', 0):,}"),
                ("Average Confidence", f"{pred_stats.get('average_confidence', 0):.1%}"),
                ("Today's Predictions", f"{pred_stats.get('today_predictions', 0)}"),
                ("Total Words Completed", f"{word_stats.get('total_words', 0):,}"),
                ("Today's Words", f"{word_stats.get('today_words', 0)}"),
                ("App Sessions", f"{app_stats.get('total_sessions', 0)}")
            ]
        )
        self.stats_layout.add_widget(overall_section)

        # Letter frequency section
        letter_counts = pred_stats.get('prediction_count_by_letter', {})
        if letter_counts:
            # Get top 10 most frequent letters
            top_letters = sorted(letter_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            letter_section = self.create_stat_section(
                "🔤 Most Frequent Letters",
                [(letter, f"{count} times") for letter, count in top_letters]
            )
            self.stats_layout.add_widget(letter_section)

        # Word stats section
        if word_stats.get('total_words', 0) > 0:
            most_common_words = word_stats.get('most_common_words', [])[:5]

            word_items = [
                ("Average Word Length", f"{word_stats.get('average_word_length', 0):.1f} letters"),
                ("Longest Word", word_stats.get('longest_word', 'None'))
            ]

            if most_common_words:
                word_items.extend([
                    ("", ""),  # Spacer
                    ("Most Common Words:", "")
                ])
                word_items.extend([(word, f"{count} times") for word, count in most_common_words])

            word_section = self.create_stat_section("📝 Word Statistics", word_items)
            self.stats_layout.add_widget(word_section)

    def create_stat_section(self, title, items):
        """Create a statistics section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )

        # Section title
        title_label = Label(
            text=title,
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.6, 1, 1)
        )
        section.add_widget(title_label)

        # Stats grid
        stats_grid = GridLayout(
            cols=2,
            size_hint_y=None,
            spacing=dp(5)
        )
        stats_grid.bind(minimum_height=stats_grid.setter('height'))

        for label, value in items:
            if label == "":  # Spacer
                stats_grid.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                stats_grid.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                continue

            label_widget = Label(
                text=label,
                size_hint_y=None,
                height=dp(30),
                text_size=(dp(150), None),
                halign='left',
                valign='middle'
            )

            value_widget = Label(
                text=str(value),
                size_hint_y=None,
                height=dp(30),
                bold=True,
                color=(0.2, 0.8, 0.2, 1) if isinstance(value, str) and value.isdigit() else (1, 1, 1, 1)
            )

            stats_grid.add_widget(label_widget)
            stats_grid.add_widget(value_widget)

        section.add_widget(stats_grid)

        # Calculate section height
        section.height = dp(40) + len(items) * dp(30) + dp(20)

        return section

    def refresh_predictions(self):
        """Refresh predictions history"""
        if not self.storage_manager:
            return

        self.predictions_layout.clear_widgets()

        # Get recent predictions
        predictions = self.storage_manager.get_prediction_history(limit=50)

        if not predictions:
            no_data = Label(
                text="No prediction history available",
                size_hint_y=None,
                height=dp(40),
                color=(0.7, 0.7, 0.7, 1)
            )
            self.predictions_layout.add_widget(no_data)
            return

        # Display predictions (most recent first)
        for pred in reversed(predictions[-20:]):  # Show last 20
            pred_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=dp(10)
            )

            # Letter
            letter_label = Label(
                text=pred['letter'],
                font_size=dp(20),
                bold=True,
                size_hint_x=0.15,
                color=(0.2, 0.8, 1, 1)
            )
            pred_layout.add_widget(letter_label)

            # Confidence
            confidence = pred['confidence']
            conf_color = (0, 0.8, 0, 1) if confidence > 0.8 else (1, 0.8, 0, 1) if confidence > 0.6 else (1, 0.4, 0, 1)

            conf_label = Label(
                text=f"{confidence:.1%}",
                size_hint_x=0.2,
                color=conf_color
            )
            pred_layout.add_widget(conf_label)

            # Timestamp
            try:
                timestamp = datetime.fromisoformat(pred['timestamp'])
                time_str = timestamp.strftime("%H:%M:%S")
            except:
                time_str = "Unknown"

            time_label = Label(
                text=time_str,
                size_hint_x=0.65,
                color=(0.7, 0.7, 0.7, 1)
            )
            pred_layout.add_widget(time_label)

            self.predictions_layout.add_widget(pred_layout)

    def refresh_words(self):
        """Refresh words history"""
        if not self.storage_manager:
            return

        self.words_layout.clear_widgets()

        # Get recent words
        words = self.storage_manager.get_word_history(limit=30)

        if not words:
            no_data = Label(
                text="No completed words yet",
                size_hint_y=None,
                height=dp(40),
                color=(0.7, 0.7, 0.7, 1)
            )
            self.words_layout.add_widget(no_data)
            return

        # Display words (most recent first)
        for word_entry in reversed(words):
            word_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )

            # Word
            word_label = Label(
                text=word_entry['word'],
                font_size=dp(18),
                bold=True,
                size_hint_x=0.4,
                color=(0.2, 0.8, 0.2, 1)
            )
            word_layout.add_widget(word_label)

            # Length
            length_label = Label(
                text=f"{word_entry['length']} letters",
                size_hint_x=0.3,
                color=(0.8, 0.8, 0.8, 1)
            )
            word_layout.add_widget(length_label)

            # Timestamp
            try:
                timestamp = datetime.fromisoformat(word_entry['timestamp'])
                time_str = timestamp.strftime("%m/%d %H:%M")
            except:
                time_str = "Unknown"

            time_label = Label(
                text=time_str,
                size_hint_x=0.3,
                color=(0.7, 0.7, 0.7, 1)
            )
            word_layout.add_widget(time_label)

            self.words_layout.add_widget(word_layout)

    def refresh_data(self, instance=None):
        """Refresh all data"""
        self.refresh_stats()
        self.refresh_predictions()
        self.refresh_words()

    def clear_prediction_history(self, instance):
        """Clear prediction history"""
        if self.storage_manager:
            success = self.storage_manager.clear_prediction_history()
            if success:
                self.refresh_data()

    def export_data(self, instance):
        """Export app data"""
        if self.storage_manager:
            export_file = self.storage_manager.export_all_data()
            if export_file:
                # TODO: Show success popup with file location
                print(f"Data exported to: {export_file}")

    def go_back(self, instance=None):
        """Go back to home screen"""
        App.get_running_app().switch_screen('home')

    def on_pre_enter(self):
        """Called before entering the screen"""
        app = App.get_running_app()
        self.storage_manager = getattr(app, 'storage_manager', None)
        self.refresh_data()