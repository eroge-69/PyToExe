import sys, psutil, datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

class GalaxyTaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 Galaxy Task Manager")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(self.get_stylesheet())

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_header()
        self.create_task_input()
        self.create_task_list()
        self.create_footer()

        self.tasks = []
        self.update_progress()

    def create_header(self):
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Consolas", 24))
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cpu_label = QLabel()
        self.cpu_label.setFont(QFont("Consolas", 14))
        self.cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.clock_label)
        self.layout.addWidget(self.cpu_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_header)
        self.timer.start(1000)
        self.update_header()

    def update_header(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.setText(f"🕒 {now}")
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU: {cpu}%   RAM: {mem}%")

    def create_task_input(self):
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a task...")
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)
        self.layout.addLayout(input_layout)

    def create_task_list(self):
        self.task_list = QListWidget()
        self.layout.addWidget(self.task_list)

    def create_footer(self):
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

    def add_task(self):
        text = self.task_input.text()
        if text:
            item = QListWidgetItem(f"[ ] {text}")
            item.setFont(QFont("Courier New", 14))
            self.task_list.addItem(item)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable)
            self.task_input.clear()
            item.setData(Qt.ItemDataRole.UserRole, False)
            self.tasks.append(item)
            self.update_progress()

    def mouseDoubleClickEvent(self, event):
        item = self.task_list.currentItem()
        if item:
            done = not item.data(Qt.ItemDataRole.UserRole)
            label = item.text().split(" ", 1)[1]
            item.setText(f"[✓] {label}" if done else f"[ ] {label}")
            item.setData(Qt.ItemDataRole.UserRole, done)
            self.update_progress()

    def update_progress(self):
        if not self.tasks:
            self.progress.setValue(0)
            return
        done = sum(1 for i in self.tasks if i.data(Qt.ItemDataRole.UserRole))
        pct = int(100 * done / len(self.tasks))
        self.progress.setValue(pct)

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #0d0d1a;
            color: #00ffff;
        }
        QLineEdit, QPushButton {
            background-color: #1a1a2e;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            padding: 6px;
            border-radius: 5px;
        }
        QLineEdit:hover, QPushButton:hover {
            background-color: #33334d;
        }
        QListWidget {
            background-color: #141430;
            border: 1px solid #00ffcc;
            border-radius: 5px;
        }
        QProgressBar {
            background-color: #1a1a2e;
            border: 1px solid #00ffcc;
            height: 20px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #00ffcc;
            width: 20px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GalaxyTaskManager()
    win.show()
    sys.exit(app.exec())
