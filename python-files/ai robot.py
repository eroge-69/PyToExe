import sys
import openai
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QMessageBox, QInputDialog, QCheckBox, QDialog, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QSettings, QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor

# Set your OpenAI API key here or use environment variable
openai.api_key = "YOUR_OPENAI_API_KEY"

# --- Emoji Picker Dialog ---
class EmojiPicker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emoji Picker 😊")
        self.setFixedSize(300, 200)
        layout = QGridLayout(self)

        self.emojis = [
            '😀','😂','😎','😍','😭','😡','👍','🙏','🎉','💯',
            '🔥','🤖','🐍','😴','🧠','🍕','🎮','❤️','👀','🧩',
            '📚','😇','🙃','😜','🤔','🌍','👋','😅','😱','🌟'
        ]

        for i, emoji in enumerate(self.emojis):
            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda _, e=emoji: self.select(e))
            layout.addWidget(btn, i // 8, i % 8)

        self.selected = None

    def select(self, emoji):
        self.selected = emoji
        self.accept()

# --- Worker for OpenAI API call ---
class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class OpenAIWorker(QRunnable):
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self.signals = WorkerSignals()

    def run(self):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # or use "gpt-4" or "gpt-3.5-turbo"
                messages=self.messages,
                max_tokens=600,
                temperature=0.7,
            )
            answer = response.choices[0].message['content'].strip()
            self.signals.finished.emit(answer)
        except Exception as e:
            self.signals.error.emit(str(e))

# --- Main Chat Window ---
class AIChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 Advanced AI Chatbot")
        self.resize(720, 550)

        self.settings = QSettings("AdvancedAIChat", "UserSettings")
        self.nickname = None
        self.conversation_history = []

        self.threadpool = QThreadPool()

        self.setup_ui()
        self.load_settings()
        self.show_login()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        self.lbl_nickname = QLabel("")
        top_bar.addWidget(self.lbl_nickname)
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.clicked.connect(self.logout)
        top_bar.addWidget(self.btn_logout)

        self.chk_darkmode = QCheckBox("Dark Mode")
        self.chk_darkmode.stateChanged.connect(self.toggle_theme)
        top_bar.addWidget(self.chk_darkmode)

        self.layout.addLayout(top_bar)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display, 8)

        self.typing_label = QLabel("")
        self.layout.addWidget(self.typing_label)

        bottom_bar = QHBoxLayout()
        self.input_message = QLineEdit()
        self.input_message.returnPressed.connect(self.on_send)
        bottom_bar.addWidget(self.input_message, 8)

        self.btn_emoji = QPushButton("😊")
        self.btn_emoji.clicked.connect(self.open_emoji_picker)
        bottom_bar.addWidget(self.btn_emoji, 1)

        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.on_send)
        bottom_bar.addWidget(self.btn_send, 2)

        self.layout.addLayout(bottom_bar)

        self.typing_timer = QTimer()
        self.typing_timer.setInterval(3000)
        self.typing_timer.timeout.connect(self.clear_typing_label)

    def load_settings(self):
        dark = self.settings.value("dark_mode", False, type=bool)
        self.chk_darkmode.setChecked(dark)
        self.apply_theme(dark)

    def save_settings(self):
        self.settings.setValue("dark_mode", self.chk_darkmode.isChecked())

    def show_login(self):
        nickname, ok = QInputDialog.getText(self, "Login", "Enter your nickname:")
        if ok and nickname.strip():
            self.nickname = nickname.strip()
            self.lbl_nickname.setText(f"Logged in as: <b>{self.nickname}</b>")
            self.append_chat(f"👋 Welcome, {self.nickname}! Ask me anything.")
            self.conversation_history = []
        else:
            QMessageBox.warning(self, "Login Required", "You must enter a nickname to continue.")
            self.show_login()

    def logout(self):
        self.nickname = None
        self.lbl_nickname.setText("")
        self.chat_display.clear()
        self.show_login()

    def append_chat(self, message, sender="bot"):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        if sender == "user":
            self.chat_display.append(f'<p style="color:#4caf50;"><b>You:</b> {message}</p>')
        else:
            self.chat_display.append(f'<p style="color:#2196f3;"><b>Bot:</b> {message}</p>')

        self.chat_display.moveCursor(QTextCursor.End)
        self.typing_label.clear()

    def open_emoji_picker(self):
        dlg = EmojiPicker(self)
        if dlg.exec_():
            emoji = dlg.selected
            if emoji:
                self.input_message.insert(emoji)

    def toggle_theme(self):
        dark = self.chk_darkmode.isChecked()
        self.apply_theme(dark)
        self.save_settings()

    def apply_theme(self, dark):
        if dark:
            self.setStyleSheet("""
                QWidget { background-color: #121212; color: #eeeeee; }
                QTextEdit { background-color: #1e1e1e; color: #eeeeee; }
                QLineEdit { background-color: #2c2c2c; color: #eeeeee; }
                QPushButton { background-color: #3a3a3a; color: #eeeeee; }
                QLabel { color: #eeeeee; }
            """)
        else:
            self.setStyleSheet("")

    def on_send(self):
        prompt = self.input_message.text().strip()
        if not prompt:
            return
        self.append_chat(prompt, sender="user")
        self.input_message.clear()
        self.typing_label.setText("🤖 Bot is typing...")
        self.typing_timer.start()

        self.conversation_history.append({"role": "user", "content": prompt})

        messages = [{"role": "system", "content": "You are a helpful assistant."}] + self.conversation_history

        worker = OpenAIWorker(messages)
        worker.signals.finished.connect(self.receive_answer)
        worker.signals.error.connect(self.receive_error)
        self.threadpool.start(worker)

    def receive_answer(self, answer):
        self.typing_timer.stop()
        self.typing_label.clear()
        self.append_chat(answer, sender="bot")
        self.conversation_history.append({"role": "assistant", "content": answer})

    def receive_error(self, error):
        self.typing_timer.stop()
        self.typing_label.clear()
        self.append_chat(f"Error: {error}", sender="bot")

    def clear_typing_label(self):
        self.typing_label.clear()
        self.typing_timer.stop()

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIChatApp()
    window.show()
    sys.exit(app.exec())
