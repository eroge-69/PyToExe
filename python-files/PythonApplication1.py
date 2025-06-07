import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QDialog, QDesktopWidget, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QMessageBox, QFileDialog, QHBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon


class QuizPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quiz Player - SuperNova Studios")
        self.setWindowIcon(QIcon('C:/Users/User/Desktop/SuperNova Studios/novaquiz.png'))

        # Show maximized
        self.showMaximized()

        # Get current screen size
        screen_rect = QDesktopWidget().availableGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        self.setMinimumSize(screen_width, screen_height)
        self.setFixedSize(screen_width, screen_height)



        self.questions = []
        self.current_question_index = 0
        self.score = 0

        self.selected_answer = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(60, 40, 60, 40)
        self.main_layout.setSpacing(30)
        self.setLayout(self.main_layout)

        # Header label with background color
        self.header = QLabel("Quiz Player")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFixedHeight(70)
        header_font = QFont("Segoe UI", 24, QFont.Bold)
        self.header.setFont(header_font)
        self.header.setStyleSheet("background-color: #6f42c1; color: white; border-radius: 10px;")
        self.main_layout.addWidget(self.header)

        # Load quiz button centered horizontally
        btn_layout = QHBoxLayout()
        self.load_quiz_btn = QPushButton("Load Quiz")
        self.load_quiz_btn.setFixedSize(140, 45)
        self.load_quiz_btn.setStyleSheet(
            "background-color: #d6336c; color: white; font-weight: bold; border-radius: 8px;"
            "font-size: 16px;"
            "padding: 8px;"
        )
        self.load_quiz_btn.clicked.connect(self.load_quiz)
        btn_layout.addStretch()
        btn_layout.addWidget(self.load_quiz_btn)
        btn_layout.addStretch()
        self.main_layout.addLayout(btn_layout)

        # Spacer before question
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Question label
        self.question_label = QLabel("")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.question_label.setStyleSheet("color: #e9ecef;")
        self.main_layout.addWidget(self.question_label)

        # Answers buttons layout
        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(20)
        self.main_layout.addLayout(self.answers_layout)

        self.answer_buttons = []
        for i in range(4):
            btn = QPushButton("")
            btn.setFont(QFont("Segoe UI", 16))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self.answer_button_style())
            btn.setMinimumHeight(60)
            btn.clicked.connect(self.make_answer_handler(i))
            self.answers_layout.addWidget(btn)
            self.answer_buttons.append(btn)

        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("Segoe UI", 14))
        self.progress_label.setStyleSheet("color: #adb5bd;")
        self.main_layout.addWidget(self.progress_label)

        # Spacer at bottom
        self.main_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.set_answers_enabled(False)

    def answer_button_style(self, selected=False, correct=False, wrong=False):
        base = "border-radius: 10px; font-weight: bold; padding: 12px;"
        if selected:
            return base + "background-color: #fd7e14; color: white;"  # Orange for selected
        if correct:
            return base + "background-color: #198754; color: white;"  # Green for correct
        if wrong:
            return base + "background-color: #dc3545; color: white;"  # Red for wrong
        return base + "background-color: #343a40; color: #e9ecef;"  # Default dark button

    def make_answer_handler(self, index):
        def handler():
            self.process_answer(index)
        return handler

    def load_quiz(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Quiz", "", "NovaQuiz files (*.nqz)")
        if filename:
            try:
                with open(filename, "r") as f:
                    self.questions = json.load(f)
                if not self.questions:
                    QMessageBox.warning(self, "Error", "Loaded quiz is empty.")
                    return
                self.current_question_index = 0
                self.score = 0
                self.show_question()
                self.set_answers_enabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load quiz:\n{e}")


    def show_question(self):
        if self.current_question_index >= len(self.questions):
            if self.current_question_index >= len(self.questions):
                dlg = ScoreDialog(self.score, len(self.questions), self)
                dlg.exec_()
                self.question_label.setText("Quiz finished. Load another quiz or close.")
                self.set_answers_enabled(False)
                for btn in self.answer_buttons:
                    btn.hide()
                self.progress_label.setText("")
                return
            self.question_label.setText("Quiz finished. Load another quiz or close.")
            self.set_answers_enabled(False)
            for btn in self.answer_buttons:
                btn.hide()
            self.progress_label.setText("")
            return

        q = self.questions[self.current_question_index]
        self.question_label.setText(q["question"])
        for i, answer in enumerate(q["answers"]):
            self.answer_buttons[i].setText(answer)
            self.answer_buttons[i].setStyleSheet(self.answer_button_style())
            self.answer_buttons[i].show()

        self.progress_label.setText(f"Question {self.current_question_index + 1} of {len(self.questions)}")
        self.selected_answer = None
        self.set_answers_enabled(True)

    def set_answers_enabled(self, enabled: bool):
        for btn in self.answer_buttons:
            btn.setEnabled(enabled)

    def process_answer(self, selected_index):
        self.set_answers_enabled(False)
        q = self.questions[self.current_question_index]
        correct_index = q["correct"]

        # Highlight correct and wrong answers
        for i, btn in enumerate(self.answer_buttons):
            if i == correct_index:
                btn.setStyleSheet(self.answer_button_style(correct=True))
            elif i == selected_index:
                btn.setStyleSheet(self.answer_button_style(wrong=True))
            else:
                btn.setStyleSheet(self.answer_button_style())

        if selected_index == correct_index:
            self.score += 1

        # Move to next question after short delay
        QTimer.singleShot(1200, self.next_question)

    def next_question(self):
        self.current_question_index += 1
        self.show_question()

class ScoreDialog(QDialog):
    def __init__(self, score, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quiz Finished")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            background-color: #121212;
            color: #e9ecef;
            font-family: 'Segoe UI';
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        score_label = QLabel(f"Your score: {score} / {total}")
        score_label.setAlignment(Qt.AlignCenter)
        score_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(score_label)

        close_btn = QPushButton("Close Quiz")
        close_btn.setFixedHeight(50)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #d6336c;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #fd7e14;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, QColor("#e9ecef"))
    palette.setColor(QPalette.Base, QColor("#212529"))
    palette.setColor(QPalette.AlternateBase, QColor("#343a40"))
    palette.setColor(QPalette.ToolTipBase, QColor("#e9ecef"))
    palette.setColor(QPalette.ToolTipText, QColor("#e9ecef"))
    palette.setColor(QPalette.Text, QColor("#e9ecef"))
    palette.setColor(QPalette.Button, QColor("#343a40"))
    palette.setColor(QPalette.ButtonText, QColor("#e9ecef"))
    palette.setColor(QPalette.Highlight, QColor("#6f42c1"))
    palette.setColor(QPalette.HighlightedText, QColor("#e9ecef"))
    app.setPalette(palette)

    window = QuizPlayer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    from PyQt5.QtCore import QTimer
    main()
