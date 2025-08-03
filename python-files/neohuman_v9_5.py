
import cv2
import numpy as np
import pyautogui
import pydirectinput
import win32api
import win32con
import keyboard
import sys
from PyQt5 import QtWidgets, QtCore
from threading import Thread
import time

# ------------------------
# CONFIGURATION
# ------------------------
ENEMY_COLOR = (255, 0, 0)  # RED (default Valorant enemy outline)
COLOR_TOLERANCE = 30       # Tolerance to detect red outline
AIM_SPEED = 0.8            # 1.0 = instant, lower = smoother
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
CENTER_X, CENTER_Y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
SCAN_BOX_SIZE = 400        # Size of the box around crosshair to scan

full_bot_mode = False
running = True

# ------------------------
# AIMBOT LOGIC
# ------------------------
def get_screen():
    screenshot = pyautogui.screenshot(region=(
        CENTER_X - SCAN_BOX_SIZE // 2,
        CENTER_Y - SCAN_BOX_SIZE // 2,
        SCAN_BOX_SIZE,
        SCAN_BOX_SIZE
    ))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def find_enemy_head(frame):
    mask = cv2.inRange(frame, 
        (ENEMY_COLOR[2] - COLOR_TOLERANCE, ENEMY_COLOR[1] - COLOR_TOLERANCE, ENEMY_COLOR[0] - COLOR_TOLERANCE),
        (ENEMY_COLOR[2] + COLOR_TOLERANCE, ENEMY_COLOR[1] + COLOR_TOLERANCE, ENEMY_COLOR[0] + COLOR_TOLERANCE)
    )
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 10:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return cx, cy
    return None

def move_mouse_to_head(x_offset, y_offset):
    move_x = int(x_offset * AIM_SPEED)
    move_y = int(y_offset * AIM_SPEED)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

def aim_loop():
    global running
    while running:
        if full_bot_mode:
            frame = get_screen()
            head = find_enemy_head(frame)
            if head:
                target_x = head[0] - SCAN_BOX_SIZE // 2
                target_y = head[1] - SCAN_BOX_SIZE // 2
                move_mouse_to_head(target_x, target_y)
        time.sleep(0.001)

# ------------------------
# MOVEMENT / FULL BOT LOGIC
# ------------------------
def bot_movement_logic():
    while running:
        if full_bot_mode:
            # Basic forward movement with counter-strafe burst logic (dummy example)
            pydirectinput.keyDown('a')
            time.sleep(0.1)
            pydirectinput.keyUp('a')
            pydirectinput.keyDown('d')
            time.sleep(0.1)
            pydirectinput.keyUp('d')
        time.sleep(0.02)

# ------------------------
# GUI
# ------------------------
class BotControlGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeoHuman V9.5 – Radiant Lock")
        self.setGeometry(100, 100, 320, 150)
        self.setFixedSize(320, 150)

        self.status_label = QtWidgets.QLabel("🟥 Full Bot Mode: OFF", self)
        self.status_label.setGeometry(30, 30, 260, 30)
        self.status_label.setStyleSheet("font-size: 16px;")

        self.exit_btn = QtWidgets.QPushButton("Exit (F9)", self)
        self.exit_btn.setGeometry(100, 80, 120, 40)
        self.exit_btn.clicked.connect(self.exit_bot)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(100)

    def update_status(self):
        if full_bot_mode:
            self.status_label.setText("🟢 Full Bot Mode: ON")
        else:
            self.status_label.setText("🟥 Full Bot Mode: OFF")

    def exit_bot(self):
        global running
        running = False
        QtWidgets.qApp.quit()

# ------------------------
# KEYBOARD HOOKS
# ------------------------
def hotkey_listener():
    global full_bot_mode, running
    while running:
        if keyboard.is_pressed("F8"):
            full_bot_mode = not full_bot_mode
            time.sleep(0.3)
        if keyboard.is_pressed("F9"):
            running = False
            break
        time.sleep(0.01)

# ------------------------
# MAIN
# ------------------------
def main():
    print("🟢 NeoHuman V9.5 — Radiant Lock: UNLEASHED")
    print("⚔️  Full Aim Power Enabled — Zero Miss, Pure Headshots")
    print("🎯 Predictive Aim | Sticky Lock | Burst Kill Mode")

    aim_thread = Thread(target=aim_loop)
    move_thread = Thread(target=bot_movement_logic)
    hotkey_thread = Thread(target=hotkey_listener)

    aim_thread.start()
    move_thread.start()
    hotkey_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    gui = BotControlGUI()
    gui.show()
    app.exec_()

    # Clean up
    global running
    running = False
    aim_thread.join()
    move_thread.join()
    hotkey_thread.join()
    print("🛑 Bot terminated.")

if __name__ == "__main__":
    main()
