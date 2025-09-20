import sys
import json
import threading
import pyautogui
import keyboard
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QColorDialog, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QBrush, QCursor
from PyQt5.QtCore import Qt, QTimer, QRect

# --- Configurable Settings ---
settings = {
    "highlight_enabled": True,
    "spotlight_enabled": True,
    "magnifier_enabled": True,
    "highlight_color": (255, 255, 0),
    "highlight_radius": 60,
    "spotlight_opacity": 150,  # 0-255
    "magnifier_zoom": 2,
    "shortcuts": {
        "toggle_highlight": "f3",
        "toggle_spotlight": "f1",
        "toggle_magnifier": "f2",
        "exit_app": "esc"
    }
}

# --- Save/Load Config (optional) ---
def save_settings():
    with open("settings.json", "w") as f:
        json.dump(settings, f)

# --- Main Overlay Window ---
class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, pyautogui.size().width, pyautogui.size().height)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        mouse_x, mouse_y = pyautogui.position()

        # --- Spotlight effect ---
        if settings["spotlight_enabled"]:
            painter.setBrush(QColor(0, 0, 0, settings["spotlight_opacity"]))
            painter.drawRect(0, 0, self.width(), self.height())
            spotlight_radius = settings["highlight_radius"] + 30
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawEllipse(mouse_x - spotlight_radius//2, mouse_y - spotlight_radius//2, spotlight_radius, spotlight_radius)

        # --- Highlight circle ---
        if settings["highlight_enabled"]:
            color = QColor(*settings["highlight_color"])
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.setPen(color)
            r = settings["highlight_radius"]
            painter.drawEllipse(mouse_x - r//2, mouse_y - r//2, r, r)

# --- Magnifier Window ---
def magnifier_loop():
    while True:
        if settings["magnifier_enabled"]:
            x, y = pyautogui.position()
            r = 50
            img = pyautogui.screenshot(region=(x - r, y - r, r*2, r*2))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            zoomed = cv2.resize(frame, (r*2*settings["magnifier_zoom"], r*2*settings["magnifier_zoom"]))
            cv2.imshow("Magnifier", zoomed)
            cv2.moveWindow("Magnifier", 10, 10)
            cv2.waitKey(1)
        else:
            cv2.destroyWindow("Magnifier")

# --- Keyboard Shortcut Listener ---
def listen_shortcuts():
    while True:
        if keyboard.is_pressed(settings["shortcuts"]["toggle_highlight"]):
            settings["highlight_enabled"] = not settings["highlight_enabled"]
            keyboard.wait(settings["shortcuts"]["toggle_highlight"])

        if keyboard.is_pressed(settings["shortcuts"]["toggle_spotlight"]):
            settings["spotlight_enabled"] = not settings["spotlight_enabled"]
            keyboard.wait(settings["shortcuts"]["toggle_spotlight"])

        if keyboard.is_pressed(settings["shortcuts"]["toggle_magnifier"]):
            settings["magnifier_enabled"] = not settings["magnifier_enabled"]
            keyboard.wait(settings["shortcuts"]["toggle_magnifier"])

        if keyboard.is_pressed(settings["shortcuts"]["exit_app"]):
            print("Exiting...")
            save_settings()
            sys.exit()

# --- Run Everything ---
def run_app():
    app = QApplication(sys.argv)
    overlay = Overlay()

    threading.Thread(target=listen_shortcuts, daemon=True).start()
    threading.Thread(target=magnifier_loop, daemon=True).start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
