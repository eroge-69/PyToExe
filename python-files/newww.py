import sys
import ctypes
import threading
import time
import numpy as np
import cv2
import pyautogui
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QColorDialog
)
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from PyQt6.QtCore import Qt, QTimer

# Windows constants
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
GWL_EXSTYLE = -20

def make_window_click_through(hwnd):
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

def send_relative_mouse_move(dx, dy):
    dx = int(np.clip(dx, -30, 30))
    dy = int(np.clip(dy, -30, 30))
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0)

def send_left_click():
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)

def send_jump():
    ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)  # Space down
    ctypes.windll.user32.keybd_event(0x20, 0, 2, 0)  # Space up

def get_async_key_state(key_code):
    return ctypes.windll.user32.GetAsyncKeyState(key_code) & 0x8000

class Overlay(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # Make overlay click-through and transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        hwnd = int(self.winId())
        make_window_click_through(hwnd)

        # Store screen size
        self.screen_width, self.screen_height = pyautogui.size()
        self.center_x, self.center_y = self.screen_width // 2, self.screen_height // 2

        # Load YOLO model
        import torch
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', source='github', force_reload=True)

        self.detections = []
        self.detections_lock = threading.Lock()

        # Start detection thread
        threading.Thread(target=self.detection_loop, daemon=True).start()

        # Initialize mouse button states
        self.right_mouse_held = False
        self.left_mouse_held = False

        # Mouse listener
        from pynput import mouse
        self.mouse_listener = mouse.Listener(on_click=self.mouse_click)
        self.mouse_listener.start()

        # Start behavior threads
        self.target_lock = TargetLock()
        threading.Thread(target=self.aimbot_loop, daemon=True).start()
        threading.Thread(target=self.triggerbot_loop, daemon=True).start()
        threading.Thread(target=self.anti_recoil_loop, daemon=True).start()
        threading.Thread(target=self.bhop_loop, daemon=True).start()

        # Timer for visuals
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def mouse_click(self, x, y, button, pressed):
        from pynput import mouse
        if button == mouse.Button.right:
            self.right_mouse_held = pressed
            if not pressed:
                self.target_lock.clear()
        elif button == mouse.Button.left:
            self.left_mouse_held = pressed

    def detection_loop(self):
        while True:
            # Capture screenshot and run detection
            img = pyautogui.screenshot().resize((416, 234))
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            results = self.model(img_bgr)
            detections = []
            scale_x = self.screen_width / 416
            scale_y = self.screen_height / 234
            for *box, conf, cls in results.xyxy[0]:
                if float(conf) >= 0.4:
                    x1, y1, x2, y2 = map(int, [box[0]*scale_x, box[1]*scale_y, box[2]*scale_x, box[3]*scale_y])
                    detections.append([x1, y1, x2, y2, float(conf)])
            with self.detections_lock:
                self.detections = detections
            time.sleep(0.03)

    def aimbot_loop(self):
        while True:
            if self.state['aimbot'] and self.right_mouse_held:
                with self.detections_lock:
                    if self.target_lock.target is None and self.target_lock.can_lock():
                        closest = None
                        closest_dist = self.state['fov_radius']
                        for box in self.detections:
                            x1, y1, x2, y2, _ = box
                            cx = (x1 + x2) / 2
                            cy = y1 + (y2 - y1) * 0.20
                            dist = ((cx - self.center_x) ** 2 + (cy - self.center_y) ** 2) ** 0.5
                            if dist <= closest_dist:
                                closest = (cx, cy)
                                closest_dist = dist
                        if closest:
                            self.target_lock.lock(closest)
                            dx = closest[0] - self.center_x
                            dy = closest[1] - self.center_y
                            send_relative_mouse_move(dx, dy)
                            send_left_click()
            time.sleep(0.001)

    def triggerbot_loop(self):
        while True:
            if self.state['triggerbot']:
                with self.detections_lock:
                    for box in self.detections:
                        x1, y1, x2, y2, _ = box
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2
                        dist = ((cx - self.center_x) ** 2 + (cy - self.center_y) ** 2) ** 0.5
                        if dist < self.state['trigger_radius']:
                            send_left_click()
                            break
            time.sleep(0.001)

    def anti_recoil_loop(self):
        while True:
            if self.left_mouse_held and self.state['anti_recoil']:
                send_relative_mouse_move(0, 3)
            time.sleep(0.01)

    def bhop_loop(self):
        while True:
            if self.state['bhop'] and get_async_key_state(0x20):
                send_jump()
                time.sleep(0.2)
            time.sleep(0.01)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw FOV circle
        if self.state['fov']:
            pen = QPen(self.state['fov_color'])
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(
                int(self.center_x - self.state['fov_radius']),
                int(self.center_y - self.state['fov_radius']),
                int(self.state['fov_radius'] * 2),
                int(self.state['fov_radius'] * 2)
            )

        # Draw ESP boxes
        if self.state['esp']:
            pen = QPen(self.state['esp_color'])
            pen.setWidth(2)
            painter.setPen(pen)
            with self.detections_lock:
                for box in self.detections:
                    x1, y1, x2, y2, _ = box
                    painter.drawRect(x1, y1, x2 - x1, y2 - y1)

        # Draw crosshair
        if self.state['crosshair']:
            pen = QPen(self.state['crosshair_color'])
            pen.setWidth(2)
            painter.setPen(pen)
            size = 10
            painter.drawLine(self.center_x - size, self.center_y, self.center_x + size, self.center_y)
            painter.drawLine(self.center_x, self.center_y - size, self.center_x, self.center_y + size)

        painter.end()

class TargetLock:
    def __init__(self):
        self.target = None
        self.locked_time = 0
        self.cooldown = 1.0
    def can_lock(self):
        return time.time() - self.locked_time > self.cooldown
    def lock(self, target):
        self.target = target
        self.locked_time = time.time()
    def clear(self):
        self.target = None

class ControlPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(50, 50, 500, 400)
        self.old_pos = None

        # Make background solid black instead of transparent
        self.bg_widget = QWidget(self)
        self.bg_widget.setGeometry(0, 0, 500, 400)
        self.bg_widget.setStyleSheet("""
            background-color: rgb(0, 0, 0);
        """)

        # Logo label
        self.logo_label = QLabel("Aorist", self.bg_widget)
        font = QFont("Arial", 20)
        font.setWeight(QFont.Weight.Bold)
        self.logo_label.setFont(font)
        self.logo_label.setStyleSheet("color: white;")
        self.logo_label.move(20, 10)

        # Layout for toggle buttons
        self.layout = QVBoxLayout(self.bg_widget)
        self.layout.setContentsMargins(20, 50, 20, 20)
        self.layout.setSpacing(10)

        toggle_layout = QHBoxLayout()
        toggle_layout.setSpacing(8)

        self.toggle_buttons = {}
        for key in ['aimbot', 'triggerbot', 'anti_recoil', 'fov', 'crosshair', 'esp', 'bhop']:
            btn = QPushButton(key.replace('_', ' ').title())
            btn.setCheckable(True)
            btn.setChecked(self.state[key])
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4B0082;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background-color: #8A2BE2;
                }
                QPushButton:hover {
                    background-color: #6A0DAD;
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self.toggle_feature(k, checked))
            self.toggle_buttons[key] = btn
            toggle_layout.addWidget(btn)
        self.layout.addLayout(toggle_layout)

        # Sliders
        def create_slider(label_text, key, min_v, max_v, default):
            lbl = QLabel(f"{label_text}: {default:.2f}")
            lbl.setStyleSheet("color: white; font-weight: bold;")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(int(min_v * 100))
            slider.setMaximum(int(max_v * 100))
            slider.setValue(int(default * 100))
            slider.valueChanged.connect(lambda val, lbl=lbl, k=key: self.slider_change(val, lbl, k))
            # Style slider
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 8px;
                    background: #444;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #8A2BE2;
                    border: none;
                    border-radius: 4px;
                    width: 20px;
                    margin: -6px 0;
                }
                QSlider::sub-page:horizontal {
                    background: #8A2BE2;
                    border-radius: 4px;
                }
            """)
            self.layout.addWidget(lbl)
            self.layout.addWidget(slider)
            return slider

        self.sensitivity_slider = create_slider('Sensitivity', 'sensitivity', 1, 5, self.state['sensitivity'])
        self.smoothing_slider = create_slider('Smoothing', 'smoothing', 0, 1, self.state['smoothing'])
        self.fov_radius_slider = create_slider('FOV Radius', 'fov_radius', 10, 300, self.state['fov_radius'])
        self.ai_confidence_slider = create_slider('AI Confidence', 'ai_confidence', 0.1, 1.0, self.state['ai_confidence'])

        # Color buttons
        color_layout = QHBoxLayout()
        def create_color_btn(label, key):
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4B0082;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #6A0DAD;
                }
            """)
            btn.clicked.connect(lambda _, k=key: self.change_color(k))
            color_layout.addWidget(btn)

        create_color_btn('FOV Color', 'fov_color')
        create_color_btn('ESP Color', 'esp_color')
        create_color_btn('Crosshair Color', 'crosshair_color')
        self.layout.addLayout(color_layout)

    def toggle_feature(self, key, checked):
        self.state[key] = checked

    def slider_change(self, val, lbl, key):
        value = val / 100.0
        lbl.setText(f"{lbl.text().split(':')[0]}: {value:.2f}")
        if key == 'sensitivity':
            self.state['sensitivity'] = value
        elif key == 'smoothing':
            self.state['smoothing'] = value
        elif key == 'fov_radius':
            self.state['fov_radius'] = int(value)
        elif key == 'ai_confidence':
            self.state['ai_confidence'] = value

    def change_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.state[key] = color

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

# Main code
if __name__ == "__main__":
    import torch
    from pynput import mouse

    app = QApplication(sys.argv)

    # Initial state
    state = {
        'aimbot': False,
        'triggerbot': False,
        'anti_recoil': False,
        'fov': False,
        'crosshair': False,
        'esp': False,
        'bhop': False,
        'fov_radius': 80,
        'sensitivity': 2.11,
        'smoothing': 0.170,
        'ai_confidence': 0.7,
        'fov_color': QColor(255, 255, 0, 100),
        'esp_color': QColor(255, 0, 0, 200),
        'crosshair_color': QColor(0, 255, 255, 200),
        'trigger_radius': 50,
    }

    # Create control panel window
    control_panel = ControlPanel(state)
    control_panel.show()

    # Create overlay window
    overlay = Overlay(state)
    overlay.showFullScreen()

    # Toggle control panel with Insert key
    def check_insert_press():
        if ctypes.windll.user32.GetAsyncKeyState(0x2D) & 0x8000:
            if control_panel.isVisible():
                control_panel.hide()
            else:
                control_panel.show()
            time.sleep(0.3)

    toggle_timer = QTimer()
    toggle_timer.timeout.connect(check_insert_press)
    toggle_timer.start(200)

    sys.exit(app.exec())
