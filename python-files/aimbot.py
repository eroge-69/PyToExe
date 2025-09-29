import sys
import threading
import time
import random
import numpy as np
import pyautogui
import mss, cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from pynput import mouse
import os
import json
import platform
if platform.system().lower().startswith("win"):
    import ctypes

selected_color = None
pick_color_mode = False
fov_visible = True
fov_radius = 200
color_tolerance = 20
tracking_active = True
anti_ban_mode = False
anti_lag_mode = False
auto_headshot_mode = False
running = True

pyautogui.FAILSAFE = True

def on_click(x, y, button, pressed):
    global selected_color, pick_color_mode
    if pick_color_mode and pressed:
        screenshot = pyautogui.screenshot(region=(x, y, 1, 1))
        color_bgr = np.array(screenshot)[0, 0]
        selected_color = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        pick_color_mode = False
        if 'window' in globals():
            window.update_chosen_color()
        return False

def start_pipette():
    global pick_color_mode
    pick_color_mode = True
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    if 'window' in globals():
        window.raise_()
        window.activateWindow()

def hsv_to_rgb_display(hsv):
    h, s, v = hsv
    rgb = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2RGB)[0][0]
    return int(rgb[0]), int(rgb[1]), int(rgb[2])

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.show()
    def paintEvent(self, event):
        if not fov_visible:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(180, 0, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        center = QtCore.QPoint(self.width() // 2, self.height() // 2)
        painter.drawEllipse(center, fov_radius, fov_radius)
        painter.end()

class ColorButton(QtWidgets.QPushButton):
    def __init__(self, color_hsv, parent=None):
        super().__init__(parent)
        self.color_hsv = color_hsv
        self.setFixedSize(40, 40)
        r, g, b = hsv_to_rgb_display(color_hsv)
        self.setStyleSheet(f"background-color: rgb({r},{g},{b}); border:1px solid #cba6f7;")
        self.clicked.connect(self.on_click)
    def on_click(self):
        global selected_color
        selected_color = self.color_hsv
        if 'window' in globals():
            window.update_chosen_color()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User HUB")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #2b2b2b; color: #cba6f7;")
        self.setGeometry(100, 100, 520, 780)
        self._drag_pos = None
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("User HUB")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        self.min_btn = QtWidgets.QPushButton("—")
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.clicked.connect(self.hide)
        title_layout.addWidget(self.min_btn)
        layout.addLayout(title_layout)
        layout.addWidget(QtWidgets.QLabel("Color Tolerance"))
        tol_layout = QtWidgets.QVBoxLayout()
        self.slider_tol = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_tol.setRange(1, 60)
        self.slider_tol.setValue(color_tolerance)
        self.slider_tol.setToolTip("Left = Low tolerance, Right = High tolerance")
        lowhigh_layout = QtWidgets.QHBoxLayout()
        low_label = QtWidgets.QLabel("Low")
        low_label.setStyleSheet("color:#aaaaaa;")
        high_label = QtWidgets.QLabel("High")
        high_label.setStyleSheet("color:#aaaaaa;")
        lowhigh_layout.addWidget(low_label)
        lowhigh_layout.addStretch()
        lowhigh_layout.addWidget(QtWidgets.QLabel("Tolerance"))
        lowhigh_layout.addStretch()
        lowhigh_layout.addWidget(high_label)
        tol_layout.addWidget(self.slider_tol)
        tol_layout.addLayout(lowhigh_layout)
        layout.addLayout(tol_layout)
        layout.addWidget(QtWidgets.QLabel("FOV Radius"))
        self.slider_fov = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_fov.setRange(10, 1200)
        self.slider_fov.setValue(fov_radius)
        layout.addWidget(self.slider_fov)
        self.btn_fov = QtWidgets.QPushButton("FOV Circle: ON")
        self.btn_fov.setCheckable(True)
        self.btn_fov.setChecked(fov_visible)
        self.btn_fov.clicked.connect(self.toggle_fov)
        layout.addWidget(self.btn_fov)
        self.btn_anti_ban = QtWidgets.QPushButton("Anti-Ban: OFF")
        self.btn_anti_ban.setCheckable(True)
        self.btn_anti_ban.clicked.connect(self.toggle_anti_ban)
        layout.addWidget(self.btn_anti_ban)
        self.btn_anti_lag = QtWidgets.QPushButton("Anti-Lag: OFF")
        self.btn_anti_lag.setCheckable(True)
        self.btn_anti_lag.clicked.connect(self.toggle_anti_lag)
        layout.addWidget(self.btn_anti_lag)
        headshot_layout = QtWidgets.QHBoxLayout()
        self.btn_auto_headshot = QtWidgets.QPushButton("Auto Headshot: OFF")
        self.btn_auto_headshot.setCheckable(True)
        self.btn_auto_headshot.clicked.connect(self.toggle_auto_headshot)
        headshot_label = QtWidgets.QLabel("Risk")
        headshot_label.setStyleSheet("color:#cba6f7; font-weight:bold; margin-left:6px;")
        headshot_layout.addWidget(self.btn_auto_headshot)
        headshot_layout.addWidget(headshot_label)
        headshot_layout.addStretch()
        layout.addLayout(headshot_layout)
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_pipette = QtWidgets.QPushButton("Pipette")
        btn_layout.addWidget(self.btn_pipette)
        self.btn_stop = QtWidgets.QPushButton("STOP Tracking")
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)
        color_layout = QtWidgets.QHBoxLayout()
        presets = [np.array([0, 255, 255]), np.array([60, 255, 255]), np.array([120, 255, 255]), np.array([30, 255, 255])]
        for hsv in presets:
            color_layout.addWidget(ColorButton(hsv))
        layout.addLayout(color_layout)
        self.chosen_label = QtWidgets.QLabel("Chosen Color")
        self.chosen_label.setAlignment(QtCore.Qt.AlignCenter)
        self.chosen_label.setFixedHeight(56)
        self.chosen_label.setStyleSheet("background-color: rgb(0,0,0); border:1px solid #cba6f7;")
        layout.addWidget(self.chosen_label)
        layout.addStretch()
        preset_layout = QtWidgets.QHBoxLayout()
        self.btn_save_preset = QtWidgets.QPushButton("Save Preset")
        self.btn_import_preset = QtWidgets.QPushButton("Import Preset")
        preset_layout.addWidget(self.btn_save_preset)
        preset_layout.addWidget(self.btn_import_preset)
        layout.addLayout(preset_layout)
        footer = QtWidgets.QLabel("credits : piwiii2.0")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("color:#8f8f8f; font-size:10px;")
        layout.addWidget(footer)
        self.setLayout(layout)
        self.btn_pipette.clicked.connect(start_pipette)
        self.btn_stop.clicked.connect(self.toggle_tracking)
        self.btn_save_preset.clicked.connect(self.save_preset)
        self.btn_import_preset.clicked.connect(self.import_preset)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if getattr(self, "_drag_pos", None) is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()
    def update_chosen_color(self):
        if selected_color is not None:
            r, g, b = hsv_to_rgb_display(selected_color)
            self.chosen_label.setStyleSheet(f"background-color: rgb({r},{g},{b}); border:1px solid #cba6f7;")
    def toggle_tracking(self):
        global tracking_active
        tracking_active = not tracking_active
        self.btn_stop.setText("STOP Tracking" if tracking_active else "START Tracking")
    def toggle_anti_ban(self):
        global anti_ban_mode
        anti_ban_mode = self.btn_anti_ban.isChecked()
        self.btn_anti_ban.setText(f"Anti-Ban: {'ON' if anti_ban_mode else 'OFF'}")
        self.raise_()
        self.activateWindow()
    def toggle_anti_lag(self):
        global anti_lag_mode
        anti_lag_mode = self.btn_anti_lag.isChecked()
        self.btn_anti_lag.setText(f"Anti-Lag: {'ON' if anti_lag_mode else 'OFF'}")
        self.raise_()
        self.activateWindow()
    def toggle_auto_headshot(self):
        global auto_headshot_mode
        auto_headshot_mode = self.btn_auto_headshot.isChecked()
        self.btn_auto_headshot.setText(f"Auto Headshot: {'ON' if auto_headshot_mode else 'OFF'}")
    def toggle_fov(self):
        global fov_visible
        fov_visible = self.btn_fov.isChecked()
        self.btn_fov.setText(f"FOV Circle: {'ON' if fov_visible else 'OFF'}")
    def save_preset(self):
        preset = {
            "fov_radius": self.slider_fov.value(),
            "color_tolerance": self.slider_tol.value(),
            "selected_color": selected_color.tolist() if selected_color is not None else None,
            "anti_ban_mode": anti_ban_mode,
            "anti_lag_mode": anti_lag_mode,
            "auto_headshot_mode": auto_headshot_mode
        }
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preset.json")
        with open(file_path, "w") as f:
            json.dump(preset, f, indent=4)
    def import_preset(self):
        folder = os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Preset", folder, "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    preset = json.load(f)
                self.slider_fov.setValue(preset.get("fov_radius", fov_radius))
                self.slider_tol.setValue(preset.get("color_tolerance", color_tolerance))
                global selected_color, anti_ban_mode, anti_lag_mode, auto_headshot_mode
                sc = preset.get("selected_color")
                if sc:
                    selected_color = np.array(sc)
                    self.update_chosen_color()
                anti_ban_mode = preset.get("anti_ban_mode", False)
                self.btn_anti_ban.setChecked(anti_ban_mode)
                self.btn_anti_ban.setText(f"Anti-Ban: {'ON' if anti_ban_mode else 'OFF'}")
                anti_lag_mode = preset.get("anti_lag_mode", False)
                self.btn_anti_lag.setChecked(anti_lag_mode)
                self.btn_anti_lag.setText(f"Anti-Lag: {'ON' if anti_lag_mode else 'OFF'}")
                auto_headshot_mode = preset.get("auto_headshot_mode", False)
                self.btn_auto_headshot.setChecked(auto_headshot_mode)
                self.btn_auto_headshot.setText(f"Auto Headshot: {'ON' if auto_headshot_mode else 'OFF'}")
            except Exception as e:
                print("Erreur lors de l'import preset:", e)

def move_mouse(cx, cy):
    if anti_lag_mode:
        start_x, start_y = pyautogui.position()
        steps = max(1, int(np.hypot(cx - start_x, cy - start_y)/160))
        for i in range(1, steps+1):
            t = i/steps
            dx = int(start_x + (cx-start_x)*t + random.randint(-5,5))
            dy = int(start_y + (cy-start_y)*t + random.randint(-5,5))
            pyautogui.moveTo(dx, dy, duration=0.002)
    elif anti_ban_mode:
        start_x, start_y = pyautogui.position()
        steps = max(1, int(np.hypot(cx - start_x, cy - start_y)/180))
        for i in range(1, steps+1):
            t = i/steps
            dx = int(start_x + (cx-start_x)*t + random.randint(-12,12))
            dy = int(start_y + (cy-start_y)*t + random.randint(-12,12))
            if random.random()<0.1:
                dx += random.randint(-3,3)
                dy += random.randint(-3,3)
            pyautogui.moveTo(dx, dy, duration=0.002)
    else:
        pyautogui.moveTo(cx, cy, duration=0.001)

def tracking_loop():
    global color_tolerance, fov_radius
    screen_w, screen_h = pyautogui.size()
    with mss.mss() as sct:
        while running:
            if not tracking_active:
                time.sleep(0.002)
                continue
            center_x, center_y = screen_w // 2, screen_h // 2
            cap_r = int(max(64, min(fov_radius + 40, 800)))
            top = max(0, center_y - cap_r)
            left = max(0, center_x - cap_r)
            width = min(screen_w - left, cap_r*2)
            height = min(screen_h - top, cap_r*2)
            monitor = {"top":top,"left":left,"width":width,"height":height}
            sct_img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(sct_img, cv2.COLOR_BGRA2BGR)
            if selected_color is not None:
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                h = int(selected_color[0])
                lower = np.array([max(0,h-color_tolerance),60,60])
                upper = np.array([min(179,h+color_tolerance),255,255])
                mask = cv2.inRange(hsv_frame, lower, upper)
                contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    c = max(contours,key=cv2.contourArea)
                    x,y,w,hbox = cv2.boundingRect(c)
                    cx = left + x + w//2
                    cy = top + y + hbox//2
                    if auto_headshot_mode:
                        cy = top + y + int(0.12*hbox)
                    if np.hypot(cx - screen_w//2, cy - screen_h//2) <= fov_radius:
                        move_mouse(cx,cy)
            if 'overlay' in globals():
                overlay.update()
            time.sleep(0.002)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
overlay = Overlay()
threading.Thread(target=tracking_loop, daemon=True).start()
QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), window).activated.connect(lambda: setattr(sys.modules[__name__], "running", False))
QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Q"), window).activated.connect(window.toggle_tracking)
sys.exit(app.exec_())
