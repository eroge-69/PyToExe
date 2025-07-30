from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer, Qt, QPoint
import sys, random, pyautogui

COLOR_PALETTES = [
    ("#A7C7E7", "#FFD6E0", "#2D3142"),
    ("#FFE5B4", "#B5EAD7", "#2D3142"),
    ("#B5EAD7", "#FFDAC1", "#2D3142"),
    ("#E2F0CB", "#FFB7B2", "#2D3142"),
    ("#C7CEEA", "#FFDAC1", "#2D3142"),
]

class CounterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.mouse_hacked = False
        self.block_close = False

        self.bg_color, self.btn_color, self.label_color = random.choice(COLOR_PALETTES)

        self.label = QLabel("Count: 0", self)
        self.label.setFont(QFont("Segoe UI", 64, QFont.Weight.Bold))
        self.label.setStyleSheet(f"color: {self.label_color}; background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("DONT Click Me!", self)
        self.button.setFont(QFont("Segoe UI", 40, QFont.Weight.Bold))
        self.button.setStyleSheet(self.button_style(self.btn_color))
        self.button.resize(400, 120)
        self.button.clicked.connect(self.increment_and_move)

        self.setWindowTitle("Do Not Play")
        self.setStyleSheet(f"background-color: {self.bg_color};")
        self.showFullScreen()

        self.label.resize(self.width(), 150)
        self.label.move(0, 30)
        QTimer.singleShot(100, self.place_button_randomly)

        # Mouse tracking for run-away logic
        self.setMouseTracking(True)
        self.button.setMouseTracking(True)

    def button_style(self, btn_color):
        return f"""
            QPushButton {{
                background-color: {btn_color};
                color: #2D3142;
                border: 4px solid #ffffff;
                border-radius: 30px;
                padding: 30px 60px;
            }}
            QPushButton:hover {{
                background-color: #fffbe7;
            }}
            QPushButton:pressed {{
                background-color: #f7cac9;
            }}
        """

    def increment_and_move(self):
        self.count += 1
        self.label.setText(f"Count: {self.count}")

        if self.count == 10 and not self.mouse_hacked:
            QMessageBox.warning(self, "Warning", "I told you not to.")
            self.mouse_hacked = True

        elif self.count == 15:
            QMessageBox.warning(self, "Stop", "No seriously stop it. OH WAIT YOU CAN'T CLOSE IT")
            self.block_close = True

        elif self.count == 50:
            QMessageBox.information(self, "Congrats", "Congrats! You can now close the window.")
            self.block_close = False
            QTimer.singleShot(1500, self.close)  # 👈 Auto-close after 1.5 sec
            return  # Stop everything after closing begins

        # Color shift every 5
        if self.count % 5 == 0:
            self.bg_color, self.btn_color, self.label_color = random.choice(COLOR_PALETTES)
            self.setStyleSheet(f"background-color: {self.bg_color};")
            self.button.setStyleSheet(self.button_style(self.btn_color))
            self.label.setStyleSheet(f"color: {self.label_color}; background: transparent;")

        # Mouse hijack after 10
        if self.mouse_hacked:
            screen_width, screen_height = pyautogui.size()
            rand_x = random.randint(0, screen_width - 1)
            rand_y = random.randint(0, screen_height - 1)
            pyautogui.moveTo(rand_x, rand_y, duration=0.3)

        # Tease before 50
        if self.count < 50 and self.count > 10:
            QMessageBox.information(self, "Keep Going", "Congrats but start making...")

        self.place_button_randomly()

    def place_button_randomly(self):
        w, h = self.width(), self.height()
        bw, bh = self.button.width(), self.button.height()
        rand_x = random.randint(40, w - bw - 40)
        rand_y = random.randint(180, h - bh - 40)
        self.button.move(rand_x, rand_y)

    def mouseMoveEvent(self, event):
        if 15 < self.count < 50:
            cursor_pos = event.position().toPoint()
            btn_pos = self.button.pos()
            btn_center = btn_pos + QPoint(self.button.width() // 2, self.button.height() // 2)

            dist = ((cursor_pos.x() - btn_center.x())**2 + (cursor_pos.y() - btn_center.y())**2)**0.5

            if dist < 150:
                self.run_away_from_cursor(cursor_pos, btn_center)

        super().mouseMoveEvent(event)

    def run_away_from_cursor(self, cursor_pos, btn_center):
        w, h = self.width(), self.height()
        bw, bh = self.button.width(), self.button.height()

        dx = btn_center.x() - cursor_pos.x()
        dy = btn_center.y() - cursor_pos.y()
        dist = max((dx**2 + dy**2)**0.5, 0.01)
        nx, ny = dx / dist, dy / dist

        move_x = btn_center.x() + int(nx * 200)
        move_y = btn_center.y() + int(ny * 200)

        move_x = max(40, min(move_x - bw // 2, w - bw - 40))
        move_y = max(180, min(move_y - bh // 2, h - bh - 40))

        self.button.move(move_x, move_y)

    def closeEvent(self, event):
        if self.block_close:
            QMessageBox.critical(self, "Nope!", "You can't close this window yet!")
            event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CounterApp()
    window.show()
    sys.exit(app.exec())
