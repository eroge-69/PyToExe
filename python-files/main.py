import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt


class ShutdownTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutdown Timer")
        self.setGeometry(200, 200, 500, 300)
        self.setStyleSheet("background-color: #121212; color: white; font-size: 18px;")

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Ліва панель з кнопками
        left_layout = QVBoxLayout()
        btn_times = [
            (30, "30 хв"),
            (45, "45 хв"),
            (60, "1 год"),
            (75, "1 год 15 хв"),
            (90, "1 год 30 хв"),
            (105, "1 год 45 хв"),
            (120, "2 год")
        ]
        for minutes, label in btn_times:
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setStyleSheet("background-color: #2e2e2e; border-radius: 8px;")
            btn.clicked.connect(lambda checked, m=minutes: self.start_timer(m))
            left_layout.addWidget(btn)

        main_layout.addLayout(left_layout)

        # Права панель з селектом
        right_layout = QVBoxLayout()
        self.combo = QComboBox()
        for m in range(30, 181, 5):
            self.combo.addItem(f"{m} хв", m)
        self.combo.setStyleSheet("background-color: #2e2e2e;")
        right_layout.addWidget(self.combo)

        confirm_btn = QPushButton("Підтвердити")
        confirm_btn.setFixedHeight(50)
        confirm_btn.setStyleSheet("background-color: #444444; border-radius: 8px;")
        confirm_btn.clicked.connect(self.confirm_selection)
        right_layout.addWidget(confirm_btn)

        self.status_label = QLabel("Таймер не запущено")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.status_label)

        main_layout.addLayout(right_layout)

        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0

    def confirm_selection(self):
        minutes = self.combo.currentData()
        self.start_timer(minutes)

    def start_timer(self, minutes):
        self.remaining_seconds = minutes * 60
        self.status_label.setText(f"Вимкнення через {minutes} хв")
        self.timer.start(1000)

    def update_countdown(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 60:
            mins = self.remaining_seconds // 60
            self.status_label.setText(f"Вимкнення через {mins} хв")
        elif self.remaining_seconds == 60:
            self.show_warning()
        elif self.remaining_seconds <= 0:
            self.timer.stop()
            subprocess.run("shutdown -s -t 0", shell=True)

    def show_warning(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Попередження")
        msg.setText("Компʼютер вимкнеться через 1 хвилину!")
        msg.setStyleSheet("background-color: #1e1e1e; color: white; font-size: 16px;")
        cancel_btn = msg.addButton("Відмінити", QMessageBox.ButtonRole.RejectRole)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.exec()

        if msg.clickedButton() == cancel_btn:
            self.timer.stop()
            self.status_label.setText("Таймер скасовано")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShutdownTimer()
    window.show()
    sys.exit(app.exec())
