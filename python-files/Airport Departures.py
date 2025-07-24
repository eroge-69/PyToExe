import sys
import string
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

FLIP_SPEED = 30
ROWS = 10
COL_LAYOUT = [8, 20, 12, 10]
HEADERS = ['Time', 'Destination', 'Flight', 'Status']

# Flight data
flights = [
    {'time': '11:30', 'destination': 'Berlin', 'flight': 'TU4709', 'status': 'On Time'},
    {'time': '12:45', 'destination': 'Kiev', 'flight': 'UA6385', 'status': 'Delayed'},
    {'time': '14:10', 'destination': 'Hong Kong', 'flight': 'JP8290', 'status': 'Boarding'},
    {'time': '15:25', 'destination': 'Tokyo', 'flight': 'NH1234', 'status': 'Cancelled'},
    {'time': '16:40', 'destination': 'New York', 'flight': 'DL5678', 'status': 'On Time'},
] + [{'time': '', 'destination': '', 'flight': '', 'status': ''} for _ in range(ROWS - 5)]


class FlipChar(QLabel):
    def __init__(self, char=' '):
        super().__init__()
        self.char_set = string.ascii_uppercase + string.digits + ':.- '
        self.current_char = char
        self.setFont(QFont('Courier', 24, QFont.Bold))
        self.setStyleSheet('color: white; background-color: black; border: 1px solid #333;')
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(35, 45)
        self.setText(char)

    def flip_to(self, new_char):
        if new_char == self.current_char:
            return
        steps = self._flip_sequence(self.current_char, new_char)
        self._animate_flip(steps)

    def _flip_sequence(self, from_char, to_char):
        if from_char not in self.char_set:
            from_char = ' '
        if to_char not in self.char_set:
            to_char = ' '
        start = self.char_set.index(from_char)
        end = self.char_set.index(to_char)
        if end < start:
            end += len(self.char_set)
        return [self.char_set[i % len(self.char_set)] for i in range(start + 1, end + 1)]

    def _animate_flip(self, sequence):
        def step():
            if sequence:
                self.setText(sequence.pop(0))
                QTimer.singleShot(FLIP_SPEED, step)
            else:
                self.current_char = self.text()
        step()


class DisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Flight Board')
        self.setStyleSheet('background-color: black; color: white;')
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(20, 10, 20, 10)

        # Main Title
        title = QLabel('✈ Welcome to Kuwait International Airport ✈')
        title.setFont(QFont('Courier', 28, QFont.Bold))
        title.setStyleSheet('color: white;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Header row
        header_row = QWidget()
        header_layout = QHBoxLayout()
        for text, width in zip(HEADERS, COL_LAYOUT):
            header = QLabel(text)
            header.setFont(QFont('Courier', 18, QFont.Bold))
            header.setStyleSheet('color: white;')
            header.setAlignment(Qt.AlignCenter)
            header.setFixedWidth(width * 35)
            header_layout.addWidget(header)
        header_row.setLayout(header_layout)
        layout.addWidget(header_row)

        # Flipboard character grid
        self.grid = QGridLayout()
        self.char_cells = []
        for row in range(ROWS):
            row_cells = []
            col = 0
            for width in COL_LAYOUT:
                cell = [FlipChar() for _ in range(width)]
                for c in cell:
                    self.grid.addWidget(c, row, col)
                    col += 1
                row_cells.extend(cell)
            self.char_cells.append(row_cells)
        layout.addLayout(self.grid)

        # Single scrolling marquee (one line)
        self.marquee_text = (
            'Flight JL752 delayed due to weather · Please check gate updates · '
            'Customs closed from 00:00 to 04:00 · Declare all electronics · '
            'Gate C3 now boarding flight LH123 · Priority passengers first · '
            'Use Terminal 2 for domestic departures · Have ID and boarding pass ready · '
            'Smoking is prohibited in all terminals · Baggage carts are available near exits · '
        )
        self.scroll_index = 0
        self.marquee = QLabel()
        self.marquee.setStyleSheet('color: yellow;')
        self.marquee.setFont(QFont('Courier', 14))
        self.marquee.setFixedWidth(sum(COL_LAYOUT) * 35)
        layout.addWidget(self.marquee)

        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_marquee)
        self.scroll_timer.start(120)

        self.setLayout(layout)
        self.update_board()

    def update_board(self):
        for row, data in enumerate(flights[:ROWS]):
            line = f'{data["time"]:<8}{data["destination"]:<20}{data["flight"]:<12}{data["status"]:<10}'.upper()
            for col, char in enumerate(line):
                self.char_cells[row][col].flip_to(char)
        QTimer.singleShot(3000, self.update_board)

    def update_marquee(self):
        text = self.marquee_text
        self.scroll_index = (self.scroll_index + 1) % len(text)
        shifted = text[self.scroll_index:] + text[:self.scroll_index]
        self.marquee.setText(shifted)


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Flight Control Panel')
        self.layout = QVBoxLayout()
        self.inputs = []

        for i in range(ROWS):
            row = QWidget()
            row_layout = QHBoxLayout()
            row_fields = {}
            for key in ['time', 'destination', 'flight', 'status']:
                input_field = QLineEdit()
                input_field.setPlaceholderText(f'{key.capitalize()} {i + 1}')
                input_field.setText(flights[i][key])
                input_field.setFixedWidth(150)
                row_layout.addWidget(input_field)
                row_fields[key] = input_field
            row.setLayout(row_layout)
            self.inputs.append(row_fields)
            self.layout.addWidget(row)

        save_btn = QPushButton('Update Display')
        save_btn.clicked.connect(self.update_flights)
        self.layout.addWidget(save_btn)
        self.setLayout(self.layout)

    def update_flights(self):
        for i, row in enumerate(self.inputs):
            flights[i] = {
                'time': row['time'].text(),
                'destination': row['destination'].text(),
                'flight': row['flight'].text(),
                'status': row['status'].text()
            }


if __name__ == '__main__':
    app = QApplication(sys.argv)
    display = DisplayWindow()
    control = ControlPanel()

    screens = app.screens()
    if len(screens) > 1:
        display.move(screens[1].geometry().topLeft())

    display.showFullScreen()
    control.show()

    sys.exit(app.exec_())
