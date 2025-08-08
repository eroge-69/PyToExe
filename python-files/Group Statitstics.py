import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout,
    QScrollArea, QSizePolicy, QHBoxLayout
)
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QFont, QColor

class StatsWindow(QWidget):
    """A window to display total back-to-back hit counts for each group."""
    def __init__(self, streams, groups):
        super().__init__()
        self.setWindowTitle("Live Statistics")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #17313E;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 10pt;
                font-weight: bold;
            }
            QLabel.stat {
                font-size: 10pt;
                font-weight: normal;
                border-radius: 5px;
                padding: 2px;
                margin: 0px;
            }
        """)
        self.streams = streams
        self.groups = groups

        # Main layout
        layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.grid_layout.setVerticalSpacing(2)
        self.grid_layout.setHorizontalSpacing(5)
        layout.addLayout(self.grid_layout)
        layout.addStretch()
        self.setLayout(layout)

        self.update_stats_display()

    def update_stats_display(self):
        """Update the grid with total back-to-back hit counts for each group."""
        # Clear existing widgets
        for row in range(self.grid_layout.rowCount()):
            for col in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(row, col)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

        # Calculate total back-to-back hits
        back_to_back_counts = {}
        for group in self.groups[1:]:  # Skip Results
            stream = self.streams[group]
            counts = {}
            for i in range(1, len(stream)):
                if stream[i] == stream[i-1] and stream[i] != "-":
                    value = stream[i]
                    counts[value] = counts.get(value, 0) + 1
            back_to_back_counts[group] = counts

        # Display headers
        for col, group in enumerate(self.groups[1:]):  # Skip Results
            label = QLabel(group)
            label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(label, 0, col)

        # Display stats
        max_rows = max(len(counts) for counts in back_to_back_counts.values()) or 1
        for row in range(max_rows):
            for col, group in enumerate(self.groups[1:]):  # Skip Results
                counts = back_to_back_counts.get(group, {})
                if row < len(counts):
                    value, count = list(counts.items())[row]
                    label = QLabel(f"{value}/{count}")
                    label.setObjectName("stat")
                    label.setAlignment(Qt.AlignCenter)
                    self.grid_layout.addWidget(label, row + 1, col)

class GroupStreamsWindow(QWidget):
    """A window to display live results categorized by groups in vertical columns with a main grid for input."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group Streams")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #17313E;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 10pt;
                font-weight: bold;
            }
            QLabel.result {
                font-size: 10pt;
                font-weight: normal;
                border-radius: 5px;
                padding: 2px;
                margin: 0px;
            }
            QPushButton {
                background-color: #333333;
                border: 0px solid #444444;
                border-radius: 15px;
                padding: 3px;
                min-width: 20px;
                min-height: 20px;
                color: white;
                font-size: 9pt;
            }
            QPushButton#reset, QPushButton#stats {
                min-width: 60px;
                min-height: 30px;
            }
            QPushButton#reset {
                background-color: #FF5555;
            }
            QPushButton#stats {
                background-color: #5555FF;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton#reset:hover {
                background-color: #FF7777;
            }
            QPushButton#stats:hover {
                background-color: #7777FF;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()

        # Header with Input Grid label, Reset button, and Stats button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Input Grid:"))
        reset_button = QPushButton("Reset")
        reset_button.setObjectName("reset")
        reset_button.clicked.connect(self.reset_streams)
        header_layout.addWidget(reset_button)
        stats_button = QPushButton("Stats")
        stats_button.setObjectName("stats")
        stats_button.clicked.connect(self.show_stats_window)
        header_layout.addWidget(stats_button)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main grid for input
        self.buttons = {}
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        self.black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
        main_grid = self.create_main_grid()
        main_layout.addLayout(main_grid)

        # Static headers layout
        self.header_layout = QGridLayout()
        self.header_layout.setVerticalSpacing(2)
        self.header_layout.setHorizontalSpacing(5)
        self.groups = ["Results", "Straight", "Split", "Street", "Six Line", "Dozen", "RB", "OE", "HL"]
        self.display_groups = ["Results", "Split", "Street", "Six Line", "Dozen", "RB", "OE", "HL"]  # Exclude Straight from display
        for col, group in enumerate(self.display_groups):
            label = QLabel(group)
            label.setAlignment(Qt.AlignCenter)
            self.header_layout.addWidget(label, 0, col)
        main_layout.addLayout(self.header_layout)

        # Scroll area for group streams results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setVerticalSpacing(2)
        self.grid_layout.setHorizontalSpacing(5)
        self.container.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.container)

        # Initialize group streams
        self.streams = {group: [] for group in self.groups}
        self.splits = {
            1: ["1-4"], 4: ["1-4"], 2: ["2-5"], 5: ["2-5"], 3: ["3-6"], 6: ["3-6"],
            7: ["7-10"], 10: ["7-10"], 8: ["8-11"], 11: ["8-11"], 9: ["9-12"], 12: ["9-12"],
            13: ["13-16"], 16: ["13-16"], 14: ["14-17"], 17: ["14-17"], 15: ["15-18"], 18: ["15-18"],
            19: ["19-22"], 22: ["19-22"], 20: ["20-23"], 23: ["20-23"], 21: ["21-24"], 24: ["21-24"],
            25: ["25-28"], 28: ["25-28"], 26: ["26-29"], 29: ["26-29"], 27: ["27-30"], 30: ["27-30"],
            31: ["31-34"], 34: ["31-34"], 32: ["32-35"], 35: ["32-35"], 33: ["33-36"], 36: ["33-36"],
        }
        self.streets = {
            1: ["1-3"], 2: ["1-3"], 3: ["1-3"], 4: ["4-6"], 5: ["4-6"], 6: ["4-6"],
            7: ["7-9"], 8: ["7-9"], 9: ["7-9"], 10: ["10-12"], 11: ["10-12"], 12: ["10-12"],
            13: ["13-15"], 14: ["13-15"], 15: ["13-15"], 16: ["16-18"], 17: ["16-18"], 18: ["16-18"],
            19: ["19-21"], 20: ["19-21"], 21: ["19-21"], 22: ["22-24"], 23: ["22-24"], 24: ["22-24"],
            25: ["25-27"], 26: ["25-27"], 27: ["25-27"], 28: ["28-30"], 29: ["28-30"], 30: ["28-30"],
            31: ["31-33"], 32: ["31-33"], 33: ["31-33"], 34: ["34-36"], 35: ["34-36"], 36: ["34-36"],
        }
        self.lines = {
            1: ["1-6"], 2: ["1-6"], 3: ["1-6"], 4: ["1-6"], 5: ["1-6"], 6: ["1-6"],
            7: ["7-12"], 8: ["7-12"], 9: ["7-12"], 10: ["7-12"], 11: ["7-12"], 12: ["7-12"],
            13: ["13-18"], 14: ["13-18"], 15: ["13-18"], 16: ["13-18"], 17: ["13-18"], 18: ["13-18"],
            19: ["19-24"], 20: ["19-24"], 21: ["19-24"], 22: ["19-24"], 23: ["19-24"], 24: ["19-24"],
            25: ["25-30"], 26: ["25-30"], 27: ["25-30"], 28: ["25-30"], 29: ["25-30"], 30: ["25-30"],
            31: ["31-36"], 32: ["31-36"], 33: ["31-36"], 34: ["31-36"], 35: ["31-36"], 36: ["31-36"],
        }

        # Stats window reference
        self.stats_window = None

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
        self.update_streams_display()

    def create_main_grid(self):
        """Create a number grid for inputting results."""
        grid = QGridLayout()
        grid.setSpacing(3)
        number_layout = [
            [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        ]

        for row_idx, row in enumerate(number_layout):
            for col_idx, number in enumerate(row):
                btn = QPushButton(str(number))
                btn.setFixedSize(QSize(50, 40))
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setFont(QFont("Calibri Light", 9))
                self.set_button_color(btn, number)
                btn.clicked.connect(lambda checked, n=number: self.add_result(n))
                self.buttons[number] = btn
                grid.addWidget(btn, row_idx, col_idx + 1)

        zero_btn = QPushButton("0")
        zero_btn.setFixedSize(QSize(40, 120))
        zero_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        zero_btn.setFont(QFont("Calibri Light", 9))
        zero_btn.setStyleSheet("background-color: #328E6E; color: white; border-radius: 15px; font-size: 9pt;")
        zero_btn.clicked.connect(lambda: self.add_result(0))
        self.buttons[0] = zero_btn
        grid.addWidget(zero_btn, 0, 0, 3, 1)
        return grid

    def set_button_color(self, btn, number):
        """Set button color based on number (red, black, or green for zero)."""
        base_style = "border-radius: 15px; font-size: 9pt;"
        if number in self.red_numbers:
            btn.setStyleSheet(f"background-color: #FF3300; color: white; {base_style}")
        elif number in self.black_numbers:
            btn.setStyleSheet(f"background-color: #000000; color: white; {base_style}")
        else:
            btn.setStyleSheet(f"background-color: #328E6E; color: white; {base_style}")

    def reset_streams(self):
        """Clear all streams and update the display."""
        self.streams = {group: [] for group in self.groups}
        self.update_streams_display()
        if self.stats_window is not None and self.stats_window.isVisible():
            self.stats_window.update_stats_display()

    def show_stats_window(self):
        """Open or update the stats window."""
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsWindow(self.streams, self.groups)
            self.stats_window.show()
        else:
            self.stats_window.update_stats_display()
            self.stats_window.raise_()
            self.stats_window.activateWindow()

    def add_result(self, number):
        """Add a new result to the streams and update the display."""
        # Determine group values
        result_entry = str(number)
        straight = str(number)
        
        split = self.splits.get(number, [None])[0] or "-"
        street = self.streets.get(number, [None])[0] or "-"
        six_line = self.lines.get(number, [None])[0] or "-"
        
        # Dozen
        if number == 0:
            dozen = "-"
        elif 1 <= number <= 12:
            dozen = "1-12"
        elif 13 <= number <= 24:
            dozen = "13-24"
        else:
            dozen = "25-36"
        
        # RB (Red/Black)
        rb = "R" if number in self.red_numbers else "B" if number in self.black_numbers else "-"
        
        # OE (Odd/Even)
        oe = "O" if number % 2 == 1 and number != 0 else "E" if number % 2 == 0 else "-"
        
        # HL (High/Low)
        hl = "H" if 19 <= number <= 36 else "L" if 1 <= number <= 18 else "-"
        
        # Append to streams
        self.streams["Results"].append(result_entry)
        self.streams["Straight"].append(straight)
        self.streams["Split"].append(split)
        self.streams["Street"].append(street)
        self.streams["Six Line"].append(six_line)
        self.streams["Dozen"].append(dozen)
        self.streams["RB"].append(rb)
        self.streams["OE"].append(oe)
        self.streams["HL"].append(hl)
        
        self.update_streams_display()
        self.scroll_to_bottom()
        if self.stats_window is not None and self.stats_window.isVisible():
            self.stats_window.update_stats_display()

    def scroll_to_bottom(self):
        """Scroll the QScrollArea to the bottom with a slight delay to ensure layout updates."""
        self.container.adjustSize()
        QTimer.singleShot(0, self._perform_scroll)

    def _perform_scroll(self):
        """Helper method to perform the actual scroll to bottom."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_streams_display(self):
        """Update the grid display with the current streams, highlighting back-to-back repeats."""
        # Clear existing widgets
        for row in range(self.grid_layout.rowCount()):
            for col in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(row, col)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
        
        # Add stream data
        max_rows = max(len(stream) for stream in self.streams.values())
        for row in range(max_rows):
            for col, group in enumerate(self.display_groups):
                if row < len(self.streams[group]):
                    value = self.streams[group][row]
                    label = QLabel(value)
                    label.setAlignment(Qt.AlignCenter)
                    label.setObjectName("result")
                    
                    # Check for back-to-back repeat
                    if row > 0 and value == self.streams[group][row - 1]:
                        label.setStyleSheet("""
                            QLabel#result {
                                background-color: #00FF00;
                                color: black;
                                font-size: 10pt;
                                border-radius: 5px;
                                padding: 2px;
                                margin: 0px;
                            }
                        """)
                    else:
                        label.setStyleSheet("""
                            QLabel#result {
                                background-color: transparent;
                                color: white;
                                font-size: 10pt;
                                border-radius: 5px;
                                padding: 2px;
                                margin: 0px;
                            }
                        """)
                    
                    self.grid_layout.addWidget(label, row, col)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GroupStreamsWindow()
    window.show()
    sys.exit(app.exec_())