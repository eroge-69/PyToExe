import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt
from Chatbot import ChatBot  # <- tumhara chatbot function yahan se aata hai

class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShinchanAI - Copilot Chat")
        self.setGeometry(100, 100, 600, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🧠 ShinchanAI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Chat History Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background-color: #f0f0f0; padding: 10px; font-size: 14px;")
        layout.addWidget(self.chat_area)

        # Input + Send layout
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Send Anything But Khuch bhi Mat Bhej Dena...")
        self.input_box.setStyleSheet("padding: 10px; font-size: 14px;")
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("padding: 10px;")

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def send_message(self):
        user_input = self.input_box.text().strip()
        if not user_input:
            return

        # Show user message
        self.chat_area.append(f"🧑 You: {user_input}")
        self.input_box.clear()

        # Get response from ChatBot backend
        try:
            bot_response = ChatBot(user_input)
            self.chat_area.append(f"🤖 ShinchanAI: {bot_response}\n")
        except Exception as e:
            self.chat_area.append(f"⚠️ Error: {str(e)}\n")

# Run GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatUI()
    window.show()
    sys.exit(app.exec_())
