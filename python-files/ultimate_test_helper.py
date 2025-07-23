import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QScrollArea, QGridLayout, QLineEdit, QRadioButton, QButtonGroup,
    QSpinBox
)
from PySide6.QtCore import Qt, QTimer


class TestHelperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Helper")
        self.setGeometry(100, 100, 700, 610)

        self.numbers = list(range(1, 11))
        self.number_inputs = []
        self.my_answer_groups = []
        self.correct_answer_groups = []
        self.answer_labels = []
        self.previous_answers = {}

        self.timer_running = False
        self.time_remaining = 600

        self.init_ui()
        self.update_timer_display()
        self.setStyleSheet(self.get_dark_stylesheet())

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Timer Layout
        timer_frame = QFrame(self)
        timer_layout = QHBoxLayout()
        timer_frame.setLayout(timer_layout)
        main_layout.addWidget(timer_frame)

        self.hour_input = QSpinBox()
        self.hour_input.setRange(0, 99)
        self.hour_input.setValue(0)

        self.minute_input = QSpinBox()
        self.minute_input.setRange(0, 59)
        self.minute_input.setValue(10)

        self.second_input = QSpinBox()
        self.second_input.setRange(0, 59)
        self.second_input.setValue(0)

        for input_widget in [self.hour_input, self.minute_input, self.second_input]:
            input_widget.editingFinished.connect(self.update_timer_from_input)

        timer_layout.addWidget(QLabel("H:"))
        timer_layout.addWidget(self.hour_input)
        timer_layout.addWidget(QLabel("M:"))
        timer_layout.addWidget(self.minute_input)
        timer_layout.addWidget(QLabel("S:"))
        timer_layout.addWidget(self.second_input)

        self.timer_label = QLabel("00:10:00", self)
        self.timer_label.setStyleSheet("font-size: 24pt;")
        timer_layout.addWidget(self.timer_label)

        start_button = QPushButton("Start")
        stop_button = QPushButton("Stop")
        reset_button = QPushButton("Reset")
        start_button.clicked.connect(self.start_timer)
        stop_button.clicked.connect(self.stop_timer)
        reset_button.clicked.connect(self.reset_timer)

        timer_layout.addWidget(start_button)
        timer_layout.addWidget(stop_button)
        timer_layout.addWidget(reset_button)

        # Scrollable Questions Section
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(15)

        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        self.create_question_widgets()

        # Add/Delete Layout
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        add_combined_widget = QWidget()
        add_combined_layout = QHBoxLayout(add_combined_widget)
        add_combined_layout.setContentsMargins(0, 0, 0, 0)
        add_combined_layout.setSpacing(4)

        self.add_button = QPushButton("Add")
        self.add_button.setFixedHeight(34)

        self.add_spinbox = QSpinBox()
        self.add_spinbox.setRange(1, 100)
        self.add_spinbox.setValue(1)
        self.add_spinbox.setFixedHeight(34)

        self.add_button.clicked.connect(self.add_question)

        add_combined_layout.addWidget(self.add_button)
        add_combined_layout.addWidget(self.add_spinbox)

        delete_button = QPushButton("Delete Question")
        delete_button.setFixedHeight(34)
        delete_button.clicked.connect(self.delete_question)

        button_layout.addWidget(add_combined_widget)
        button_layout.addWidget(delete_button)

        # Clear All Button
        clear_layout = QHBoxLayout()
        main_layout.addLayout(clear_layout)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("QPushButton { background-color: #f08080; }")
        clear_button.clicked.connect(self.clear_all)
        clear_layout.addWidget(clear_button)

    def create_question_widgets(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.number_inputs = []
        self.answer_labels = []
        self.my_answer_groups = []
        self.correct_answer_groups = []
        self.previous_answers = {}

        for i in range(len(self.numbers)):
            num_input = QLineEdit(str(self.numbers[i]))
            num_input.setFixedWidth(40)
            num_input.setAlignment(Qt.AlignCenter)
            num_input.editingFinished.connect(lambda index=i: self.update_numbers(index))
            self.scroll_layout.addWidget(num_input, i, 0)
            self.number_inputs.append(num_input)

            answer_label = QLabel(f"Q{i+1}")
            answer_label.setFixedSize(40, 30)
            answer_label.setStyleSheet("background-color: yellow; color: black; border: 1px solid black;")
            answer_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(answer_label, i, 1)
            self.answer_labels.append(answer_label)

            separator1 = QFrame()
            separator1.setFrameShape(QFrame.VLine)
            separator1.setFrameShadow(QFrame.Sunken)
            self.scroll_layout.addWidget(separator1, i, 2)

            my_group = QButtonGroup(self)
            correct_group = QButtonGroup(self)

            for j, choice in enumerate(['1', '2', '3', '4']):
                my_radio = QRadioButton(choice)
                correct_radio = QRadioButton(choice)

                my_group.addButton(my_radio, j+1)
                correct_group.addButton(correct_radio, j+1)

                self.connect_radio_button(my_radio, i)
                correct_radio.clicked.connect(lambda checked, index=i: self.update_label_color(index))

                self.scroll_layout.addWidget(my_radio, i, j+3)
                self.scroll_layout.addWidget(correct_radio, i, j+8)

            separator2 = QFrame()
            separator2.setFrameShape(QFrame.VLine)
            separator2.setFrameShadow(QFrame.Sunken)
            self.scroll_layout.addWidget(separator2, i, 7)

            self.my_answer_groups.append(my_group)
            self.correct_answer_groups.append(correct_group)
            self.previous_answers[i] = 0

    def connect_radio_button(self, radio, index):
        radio.clicked.connect(lambda: self.toggle_answer(index))

    def update_numbers(self, index):
        try:
            new_number = int(self.number_inputs[index].text())
            for i in range(len(self.numbers)):
                updated_value = new_number + (i - index)
                self.numbers[i] = updated_value
                self.number_inputs[i].setText(str(updated_value))
        except ValueError:
            self.number_inputs[index].setText(str(self.numbers[index]))

    def toggle_answer(self, index):
        selected = self.my_answer_groups[index].checkedId()
        if selected == self.previous_answers[index]:
            button = self.my_answer_groups[index].checkedButton()
            if button is not None:
                self.my_answer_groups[index].setExclusive(False)
                button.setChecked(False)
                self.my_answer_groups[index].setExclusive(True)
                self.previous_answers[index] = 0
        else:
            self.previous_answers[index] = selected
        self.update_label_color(index)

    def update_label_color(self, index):
        selected = self.my_answer_groups[index].checkedId()
        correct = self.correct_answer_groups[index].checkedId()

        if selected == -1:
            self.answer_labels[index].setStyleSheet("background-color: yellow; color: black; border: 1px solid black;")
        elif selected == correct:
            self.answer_labels[index].setStyleSheet("background-color: lightgreen; color: black; border: 1px solid black;")
        else:
            self.answer_labels[index].setStyleSheet("background-color: red; color: black; border: 1px solid black;")

    # ✅ This method was missing before
    def update_timer_from_input(self):
        self.time_remaining = (
            self.hour_input.value() * 3600 +
            self.minute_input.value() * 60 +
            self.second_input.value()
        )
        self.update_timer_display()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.countdown()

    def stop_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.stop_timer()
        hours = self.hour_input.value()
        minutes = self.minute_input.value()
        seconds = self.second_input.value()
        self.time_remaining = (hours * 3600 + minutes * 60 + seconds)
        self.update_timer_display()

    def countdown(self):
        if self.timer_running and self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer_display()
            QTimer.singleShot(1000, self.countdown)
        else:
            self.stop_timer()

    def update_timer_display(self):
        hours = self.time_remaining // 3600
        minutes = (self.time_remaining % 3600) // 60
        seconds = self.time_remaining % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_label.setText(time_str)

    def save_answer_state(self):
        saved_state = {}
        for i in range(len(self.numbers)):
            my_selected_id = self.my_answer_groups[i].checkedId()
            correct_selected_id = self.correct_answer_groups[i].checkedId()
            saved_state[i] = {'my_answer': my_selected_id, 'correct_answer': correct_selected_id}
        return saved_state

    def restore_answer_state(self, saved_state):
        for i in range(len(self.numbers)):
            state = saved_state.get(i, {})
            my_answer_id = state.get('my_answer')
            correct_answer_id = state.get('correct_answer')

            if my_answer_id is not None and my_answer_id != -1:
                button_to_check = self.my_answer_groups[i].button(my_answer_id)
                if button_to_check:
                    button_to_check.setChecked(True)

            if correct_answer_id is not None and correct_answer_id != -1:
                button_to_check = self.correct_answer_groups[i].button(correct_answer_id)
                if button_to_check:
                    button_to_check.setChecked(True)
        self.update_label_colors()

    def update_label_colors(self):
        for i in range(len(self.numbers)):
            self.update_label_color(i)

    def add_question(self):
        saved_answers = self.save_answer_state()
        count = self.add_spinbox.value()
        for _ in range(count):
            next_number = self.numbers[-1] + 1 if self.numbers else 1
            self.numbers.append(next_number)
        self.create_question_widgets()
        self.restore_answer_state(saved_answers)

    def delete_question(self):
        saved_answers = self.save_answer_state()
        if len(self.numbers) > 1:
            self.numbers.pop()
            self.create_question_widgets()
            self.restore_answer_state(saved_answers)

    def clear_all(self):
        self.stop_timer()
        self.time_remaining = 600
        self.hour_input.setValue(0)
        self.minute_input.setValue(10)
        self.second_input.setValue(0)
        self.update_timer_display()

        for group in self.my_answer_groups:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)
        self.previous_answers = {}

        for group in self.correct_answer_groups:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)

        for i in range(len(self.answer_labels)):
            self.update_label_color(i)

        self.numbers = list(range(1, 11))
        self.create_question_widgets()

    def get_dark_stylesheet(self):
        return """
        QWidget {
            background-color: #2b2b2b;
            color: #f0f0f0;
            font-family: Segoe UI, sans-serif;
            font-size: 12pt;
        }

        QLabel {
            color: #e0e0e0;
        }

        QLineEdit, QSpinBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555;
            padding: 4px;
            border-radius: 4px;
        }

        QPushButton {
            background-color: #444;
            color: #fff;
            border: 1px solid #666;
            padding: 6px 12px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #555;
        }

        QPushButton:pressed {
            background-color: #666;
        }

        QRadioButton {
            color: #ccc;
            spacing: 10px;
        }

        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }

        QRadioButton::indicator:checked {
            background-color: #00bc8c;
            border: 1px solid #00bc8c;
            border-radius: 8px;
        }

        QRadioButton::indicator:unchecked {
            background-color: #555;
            border: 1px solid #888;
            border-radius: 8px;
        }

        QScrollArea {
            background-color: #2b2b2b;
            border: none;
        }

        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
        }

        QScrollBar::handle:vertical {
            background-color: #555;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_helper_app = TestHelperApp()
    test_helper_app.show()
    sys.exit(app.exec())
