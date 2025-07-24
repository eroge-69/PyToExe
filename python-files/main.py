import random
import os
import sys
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QLineEdit, QVBoxLayout, QWidget,
    QMessageBox, QMenuBar, QAction, QMainWindow, QDialog, QRadioButton, QHBoxLayout, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QCloseEvent
from pygame import mixer

mixer.init()

def play_audio(file_name):
    try:
        if os.path.exists(file_name):
            mixer.music.load(file_name)
            mixer.music.play()
            print(f"Playing audio file: {file_name}")
        else:
            print(f"فایل صوتی '{file_name}' وجود ندارد.")
            QMessageBox.critical(None, "خطا", f"فایل صوتی '{file_name}' یافت نشد.")
    except Exception as e:
        print(f"خطا در پخش صوت: {e}")
        QMessageBox.critical(None, "خطا", "مشکلی در پخش صوت رخ داده است.")

def get_question_audio_file(num1, num2):
    return f"question_{num1}_{num2}.mp3"

class ModeSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("انتخاب حالت")
        self.setGeometry(200, 200, 300, 150)
        self.selected_mode = None
        layout = QVBoxLayout()
        self.blind_mode_radio = QRadioButton("حالت نابینا")
        self.visually_impaired_mode_radio = QRadioButton("حالت کم‌بینا")
        layout.addWidget(self.blind_mode_radio)
        layout.addWidget(self.visually_impaired_mode_radio)
        self.confirm_button = QPushButton("تایید")
        self.confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

    def confirm_selection(self):
        if self.blind_mode_radio.isChecked():
            self.selected_mode = "blind"
        elif self.visually_impaired_mode_radio.isChecked():
            self.selected_mode = "visually_impaired"
        self.accept()

class AboutUsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ارتباط با ما")
        self.setGeometry(250, 250, 350, 150)
        layout = QVBoxLayout()
        about_label = QLabel(
            "برنامه آموزش ضرب برای دانش آموزان با آسیب بینایی\n"
            "توسعه دهندگان: یوسف خواجه و امیر احمدی\n"
            "تلفن تماس:\n"
            "09212052825\n"
            "+98 913 543 4018", self)
        about_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(about_label)
        close_button = QPushButton("بستن", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.setLayout(layout)

class BlindModeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.correct_answer = None
        self.current_mode = None
        self.init_ui()

    def init_ui(self):
        mode_dialog = ModeSelectionDialog()
        if mode_dialog.exec_() == QDialog.Accepted:
            self.current_mode = mode_dialog.selected_mode
            self.open_guide()
        else:
            exit()

        self.setWindowTitle("آموزش ضرب")
        self.setGeometry(100, 100, 400, 300)

        menubar = self.menuBar()
        mode_menu = menubar.addMenu("حالت")

        blind_mode_action = QAction("حالت نابینا", self)
        blind_mode_action.triggered.connect(self.set_blind_mode)
        mode_menu.addAction(blind_mode_action)

        visually_impaired_mode_action = QAction("حالت کم‌بینا", self)
        visually_impaired_mode_action.triggered.connect(self.set_visually_impaired_mode)
        mode_menu.addAction(visually_impaired_mode_action)

        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)

        help_menu = menubar.addMenu("راهنما")
        open_guide_action = QAction("باز کردن راهنما", self)
        open_guide_action.triggered.connect(self.open_guide)
        help_menu.addAction(open_guide_action)

        about_us_action = QAction("ارتباط با ما", self)
        about_us_action.triggered.connect(self.show_about_us_dialog)
        menubar.addAction(about_us_action)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        if self.current_mode == "blind":
            self.set_blind_mode()
        elif self.current_mode == "visually_impaired":
            self.set_visually_impaired_mode()

        self.set_keyboard_shortcuts()

    def closeEvent(self, event: QCloseEvent):
        mixer.music.stop()
        event.accept()

    def show_about_us_dialog(self):
        about_dialog = AboutUsDialog()
        about_dialog.exec_()

    def set_keyboard_shortcuts(self):
        self.next_question_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.next_question_shortcut.activated.connect(self.ask_question)

        self.repeat_question_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.repeat_question_shortcut.activated.connect(self.repeat_current_question)

        self.exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.exit_shortcut.activated.connect(self.close)

    def open_guide(self):
        audio_guide_file = "guide.mp3"
        if os.path.exists(audio_guide_file):
            play_audio(audio_guide_file)
            QMessageBox.information(self, "راهنما", "فایل راهنمای صوتی در حال پخش است.")
        else:
            QMessageBox.warning(self, "خطا", "فایل راهنمای صوتی یافت نشد.")

    def repeat_current_question(self):
        if hasattr(self, "current_question_text"):
            question_parts = self.current_question_text.split()
            if len(question_parts) >= 5 and question_parts[2].isdigit() and question_parts[4].isdigit():
                num1 = int(question_parts[2])
                num2 = int(question_parts[4])
                question_file = get_question_audio_file(num1, num2)
                play_audio(question_file)
                QMessageBox.information(self, "تکرار سوال", "سوال فعلی دوباره پخش شد.")

    def set_blind_mode(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.label = QLabel("برای شروع، پاسخ را وارد کرده و Enter بزنید.", self)
        self.label.setAccessibleName("راهنمایی: برای شروع، پاسخ را وارد کرده و Enter بزنید.")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.entry = QLineEdit(self)
        self.entry.setAccessibleName("ورودی پاسخ")
        self.entry.setPlaceholderText("پاسخ خود را اینجا وارد کنید.")
        self.layout.addWidget(self.entry)
        self.entry.returnPressed.connect(self.submit_answer)
        self.entry.setFocus()
        self.ask_button = QPushButton("پرسیدن سوال مجدد", self)
        self.ask_button.setAccessibleName("پرسیدن سوال مجدد (برای نابینایان)")
        self.ask_button.clicked.connect(self.ask_question)
        self.layout.addWidget(self.ask_button)
        self.current_mode = "blind"
        self.ask_question()

    def set_visually_impaired_mode(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.question_entry = QLineEdit(self)
        self.question_entry.setReadOnly(True)
        self.question_entry.setAccessibleName("سوال (برای کم‌بینایان)")
        self.question_entry.setStyleSheet("font-size: 24px; padding: 10px;")
        self.layout.addWidget(self.question_entry)
        self.entry = QLineEdit(self)
        self.entry.setAccessibleName("ورودی پاسخ")
        self.entry.setPlaceholderText("پاسخ خود را اینجا وارد کنید.")
        self.entry.setStyleSheet("font-size: 20px; padding: 8px;")
        self.layout.addWidget(self.entry)
        self.submit_button = QPushButton("بررسی پاسخ", self)
        self.submit_button.setAccessibleName("بررسی پاسخ (برای کم‌بینایان)")
        self.submit_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_button)
        self.current_mode = "visually_impaired"
        self.generate_new_question()

    def generate_new_question(self):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        self.correct_answer = num1 * num2
        self.current_question_text = f"حاصل ضرب {num1} در {num2} چیست؟"
        if self.current_mode == "visually_impaired" and hasattr(self, "question_entry"):
            self.question_entry.setText(self.current_question_text)
            self.question_entry.setAccessibleName(f"سوال: {self.current_question_text} (برای کم‌بینایان)")

    def check_answer(self):
        try:
            user_answer = self.entry.text().strip()
            if not user_answer.isdigit():
                QMessageBox.warning(self, "خطا", "لطفاً یک عدد وارد کنید.")
                return
            user_answer = int(user_answer)
            if user_answer == self.correct_answer:
                play_audio("positive_feedback.mp3")
                while mixer.music.get_busy():
                    QApplication.processEvents()
                self.generate_new_question()
                self.entry.clear()
            else:
                play_audio("negative_feedback.mp3")
                QMessageBox.information(self, "نتیجه", f"متاسفانه پاسخ شما اشتباه است. پاسخ صحیح: {self.correct_answer}")
                self.entry.clear()
        except Exception as e:
            print(f"خطا در ورودی کاربر: {e}")
            QMessageBox.critical(self, "خطا", "خطایی رخ داده است.")

    def ask_question(self):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        self.correct_answer = num1 * num2
        self.current_question_text = f"حاصل ضرب {num1} در {num2} چیست؟"
        question_file = get_question_audio_file(num1, num2)
        play_audio(question_file)
        if self.current_mode == "blind" and hasattr(self, "entry"):
            self.entry.clear()
            self.entry.setFocus()

    def submit_answer(self):
        try:
            user_answer = self.entry.text().strip()
            if not user_answer.isdigit():
                QMessageBox.warning(self, "خطا", "لطفاً یک عدد وارد کنید.")
                return
            user_answer = int(user_answer)
            if user_answer == self.correct_answer:
                play_audio("positive_feedback.mp3")
                while mixer.music.get_busy():
                    QApplication.processEvents()
                self.ask_question()
            else:
                play_audio("negative_feedback.mp3")
                QMessageBox.information(self, "پاسخ صحیح", f"پاسخ صحیح: {self.correct_answer}")
                self.ask_question()
            self.entry.clear()
        except Exception as e:
            print(f"خطا در ورودی کاربر: {e}")
            QMessageBox.critical(self, "خطا", "خطایی رخ داده است.")

if __name__ == "__main__":
    app = QApplication([])
    window = BlindModeApp()
    window.showFullScreen()  # Optional: Run in full screen
    app.exec_()