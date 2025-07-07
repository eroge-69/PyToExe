import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QPushButton, QLineEdit, QListWidget, QMessageBox
)
from PyQt5.QtGui import QFont
import pyttsx3

DATA_FILE = "crash_data.json"

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history[-200:], f)

def analyze_strategy(history):
    if len(history) < 5:
        return "Waiting for more data...", "gray"
    last5 = history[-5:]
    lows = sum(1 for x in last5 if x < 1.5)
    highs = sum(1 for x in last5 if x > 10)
    if lows >= 4:
        return "🟢 BET NOW — Suggest cashout at 1.85x", "green"
    elif highs > 0:
        return "🛑 WAIT (recent spike)", "red"
    else:
        return "⏳ WAIT", "orange"

class AviatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Aviator Predictor - All-in-One")
        self.setGeometry(100, 100, 400, 500)
        self.history = load_history()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Enter crash multiplier (e.g., 1.87):")
        self.label.setFont(QFont("Arial", 12))
        layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g., 1.87")
        layout.addWidget(self.input)

        self.btn_add = QPushButton("Add Multiplier")
        self.btn_add.clicked.connect(self.add_multiplier)
        layout.addWidget(self.btn_add)

        self.status = QLabel("Status: Waiting...")
        self.status.setFont(QFont("Arial", 14))
        self.status.setStyleSheet("color: gray")
        layout.addWidget(self.status)

        self.history_list = QListWidget()
        for val in self.history[-50:]:
            self.history_list.addItem(f"{val}x")
        layout.addWidget(self.history_list)

        self.setLayout(layout)

    def add_multiplier(self):
        try:
            value = float(self.input.text())
            self.history.append(value)
            save_history(self.history)
            self.history_list.addItem(f"{value}x")
            strategy, color = analyze_strategy(self.history)
            self.status.setText(f"Status: {strategy}")
            self.status.setStyleSheet(f"color: {color}")
            self.input.clear()
            if "BET NOW" in strategy:
                self.speak("Bet now. Cash out at one point eight five")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number.")

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AviatorApp()
    win.show()
    sys.exit(app.exec_())