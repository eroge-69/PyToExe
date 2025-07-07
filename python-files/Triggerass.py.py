from random import uniform
import cv2
import numpy as np
import time
import threading
import keyboard
import ctypes
import os
import sys
import logging
import json
import hashlib
import platform
import uuid
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, 
                            QMessageBox, QSizePolicy, QGraphicsDropShadowEffect, 
                            QCheckBox, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QPoint, QRectF
from PyQt5.QtGui import (QFont, QPixmap, QIcon, QColor, QLinearGradient, QPainter, 
                        QPainterPath, QBrush, QPen, QFontMetrics, QImage, QPalette)
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import pyautogui

CONFIG_FILE = Path(os.getenv('APPDATA', '/tmp')) / 'triggerbot_config.json'
SHOW_CLICKS = True
click_count = 0

VALID_KEY = "Lennox"

class FiveMTriggerBot:
    def __init__(self):
        self.stop_script = False
        self.DEBUG_MODE = False
        self.VSYNC_ENABLED = True
        self.TARGET_FPS = 144
        self.last_click_time = 0
        self.last_frame_time = time.time()
        self.enabled = True

        self.LOWER_RED1 = np.array([0, 150, 100])
        self.UPPER_RED1 = np.array([8, 255, 255])
        self.LOWER_RED2 = np.array([172, 150, 100])
        self.UPPER_RED2 = np.array([180, 255, 255])

        self.REGION_SIZE = 60
        screen_width, screen_height = pyautogui.size()
        self.center_x, self.center_y = (screen_width // 2, screen_height // 2)
        self.region_left = self.center_x - self.REGION_SIZE // 2
        self.region_top = self.center_y - self.REGION_SIZE // 2

        pyautogui.FAILSAFE = False

    def left_click(self):
        global click_count
        pyautogui.click()
        click_count += 1
        if SHOW_CLICKS:
            print(f"Click #{click_count} performed")

    def listen_for_exit(self):
        keyboard.wait('#')
        self.stop_script = True
        print('🛑 Exit key pressed. Stopping...')

    def listen_for_toggle(self):
        while not self.stop_script:
            if keyboard.is_pressed('f9'):
                self.enabled = not self.enabled
                status = "ENABLED" if self.enabled else "DISABLED"
                print(f"🔧 TriggerBot {status} (F9 pressed)")
                time.sleep(0.5)
            time.sleep(0.01)

    def frame_pacing(self):
        if self.VSYNC_ENABLED:
            frame_time = 1.0 / self.TARGET_FPS
            elapsed = time.time() - self.last_frame_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
            self.last_frame_time = time.time()

    def process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.LOWER_RED1, self.UPPER_RED1)
        mask2 = cv2.inRange(hsv, self.LOWER_RED2, self.UPPER_RED2)
        mask = cv2.bitwise_or(mask1, mask2)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    def is_right_mouse_down(self):
        try:
            return ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000 != 0
        except:
            return keyboard.is_pressed('shift')

    def run(self):
        threading.Thread(target=self.listen_for_exit, daemon=True).start()
        threading.Thread(target=self.listen_for_toggle, daemon=True).start()
        
        print('🔥 FiveM TriggerBot active. Press # to stop.')
        print('🔴 TriggerBot will only work when right mouse button is held down')
        print('🔧 Press F9 to toggle TriggerBot on/off')
        
        try:
            while not self.stop_script:
                self.frame_pacing()
                
                if self.enabled and self.is_right_mouse_down():
                    screenshot = pyautogui.screenshot(
                        region=(self.region_left, self.region_top, 
                               self.REGION_SIZE, self.REGION_SIZE)
                    )
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    mask = self.process_frame(frame)
                    
                    center_patch = mask[
                        self.REGION_SIZE // 2 - 3:self.REGION_SIZE // 2 + 3,
                        self.REGION_SIZE // 2 - 3:self.REGION_SIZE // 2 + 3
                    ]
                    
                    if cv2.countNonZero(center_patch) > 8:
                        self.left_click()
                
                time.sleep(0.005)
                
        except KeyboardInterrupt:
            pass
        finally:
            print('🛑 TriggerBot stopped.')


class FrostedGlassWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.background_color = QColor(40, 42, 54)
        self.opacity = 0.92

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.background_color)
        
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, QColor(40, 42, 54, int(230 * self.opacity)))
        painter.strokePath(path, QPen(QColor(80, 82, 94, 150), 1.5))


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.logo = QLabel("🎯")
        self.logo.setFont(QFont("Segoe UI", 14))
        self.logo.setStyleSheet("color: #50fa7b;")
        
        self.title = QLabel("Cracked by .gg/cocuk-community")
        self.title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title.setStyleSheet("color: white; margin-left: 10px;")
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        
        self.min_button = QPushButton("−")
        self.min_button.setFixedSize(30, 30)
        self.min_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.8);
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)
        self.min_button.clicked.connect(self.parent.showMinimized)
        
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.8);
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E81123;
            }
        """)
        self.close_button.clicked.connect(self.parent.close)
        
        control_layout.addWidget(self.min_button)
        control_layout.addWidget(self.close_button)
        
        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addLayout(control_layout)
        self.setLayout(layout)
        
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None and event.buttons() == Qt.LeftButton:
            self.parent.move(self.parent.pos() + (event.pos() - self.start_pos))


class HWIDManager:
    @staticmethod
    def get_hwid():
        try:
            info = {
                'machine': platform.machine(),
                'node': platform.node(),
                'processor': platform.processor(),
                'system': platform.system(),
                'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0, 2*6, 2)][::-1])
            }
            return hashlib.sha256(str(info).encode()).hexdigest()
        except Exception as e:
            logging.error(f"Error generating HWID: {e}")
            return "default_hwid_error"


class LicenseClient:
    def __init__(self):
        self.hwid = HWIDManager.get_hwid()
        
    def validate_key(self, key):
        if key.upper() == VALID_KEY.upper():
            return True, "License activated successfully!"
        else:
            return False, "Invalid license key"


class ModernProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._maximum = 100
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(1200)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.glow_pos = 0
        self.glow_animation = QPropertyAnimation(self, b"glowPos")
        self.glow_animation.setDuration(1500)
        self.glow_animation.setStartValue(0)
        self.glow_animation.setEndValue(100)
        self.glow_animation.setLoopCount(-1)
        self.setFixedHeight(6)
        self.setMinimumWidth(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_path = QPainterPath()
        bg_rect = QRectF(0, 0, self.width(), self.height())
        bg_path.addRoundedRect(bg_rect, 3, 3)
        painter.fillPath(bg_path, QColor(60, 62, 74))

        if self._value > 0:
            progress_width = (self._value / self._maximum) * self.width()
            progress_path = QPainterPath()
            progress_rect = QRectF(0, 0, progress_width, self.height())
            progress_path.addRoundedRect(progress_rect, 3, 3)
            
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor("#667eea"))
            gradient.setColorAt(1, QColor("#764ba2"))
            painter.fillPath(progress_path, gradient)

    @pyqtProperty(int)
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.update()

    @pyqtProperty(int)
    def glowPos(self):
        return self.glow_pos

    @glowPos.setter
    def glowPos(self, pos):
        self.glow_pos = pos
        self.update()

    def startAnimation(self):
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.start()
        self.glow_animation.start()

    def stopAnimation(self):
        self.animation.stop()
        self.glow_animation.stop()


class GradientButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self._shadow_blur = 5
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self.normal_color1 = QColor("#667eea")
        self.normal_color2 = QColor("#764ba2")
        self.hover_color1 = QColor("#5a67d8")
        self.hover_color2 = QColor("#6b46c1")
        self.is_hovered = False
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.shadow_animation = QPropertyAnimation(self, b"shadowBlurRadius")
        self.shadow_animation.setDuration(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        if self.is_hovered:
            gradient.setColorAt(0, self.hover_color1)
            gradient.setColorAt(1, self.hover_color2)
        else:
            gradient.setColorAt(0, self.normal_color1)
            gradient.setColorAt(1, self.normal_color2)

        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 8, 8)
        shadow = QPainterPath()
        shadow_rect = QRectF(self.rect().translated(0, 3))
        shadow.addRoundedRect(shadow_rect, 8, 8)
        painter.fillPath(shadow, QColor(0, 0, 0, 50))
        painter.fillPath(path, gradient)
        painter.setPen(Qt.white)
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(self.text())
        text_x = int((self.width() - text_width) / 2)
        text_y = int((self.height() + font_metrics.ascent() - font_metrics.descent()) / 2)
        painter.drawText(text_x, text_y, self.text())

    @pyqtProperty(int)
    def shadowBlurRadius(self):
        return self._shadow_blur

    @shadowBlurRadius.setter
    def shadowBlurRadius(self, radius):
        self._shadow_blur = radius
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()


class FloatingInputField(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(60, 62, 74, 0.7);
                color: white;
                border: 1px solid rgba(80, 82, 94, 0.5);
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI';
                font-size: 14px;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border: 1px solid rgba(102, 126, 234, 0.8);
                background-color: rgba(60, 62, 74, 0.9);
            }
        """)


class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.client = LicenseClient()
        self.triggerbot = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Triggerbot Login")
        self.resize(700, 800)
        self.setMinimumSize(400, 500)
        
        self.main_widget = FrostedGlassWidget()
        self.setCentralWidget(self.main_widget)
        
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(25)
        main_layout.addWidget(content_widget)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignCenter)
        
        self.logo = QLabel("🔑")
        self.logo.setStyleSheet("font-size: 48px;")
        self.logo.setAlignment(Qt.AlignCenter)
        
        header = QLabel("Triggerbot Login")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("""
            color: white; 
            letter-spacing: 2px;
            padding-bottom: 10px;
            margin-bottom: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.logo)
        header_layout.addWidget(header)
        content_layout.addLayout(header_layout)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 42, 54, 0.8);
                border-radius: 12px;
                padding: 25px;
                border: 1px solid rgba(80, 82, 94, 0.3);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(25)
        content_layout.addWidget(card)
        
        title = QLabel("Login with License")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: white;
                padding: 5px 0 15px 0;
                letter-spacing: 1px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        self.key_entry = FloatingInputField("Enter your license key...")
        self.key_entry.returnPressed.connect(self.activate)
        card_layout.addWidget(self.key_entry)
        
        self.remember_me = QCheckBox("Remember Me")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                color: rgba(255,255,255,0.8);
                font-family: 'Segoe UI';
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid rgba(80, 82, 94, 0.5);
                border-radius: 4px;
                background-color: rgba(60, 62, 74, 0.7);
            }
            QCheckBox::indicator:checked {
                border: 1px solid rgba(102, 126, 234, 0.8);
                border-radius: 4px;
                background-color: rgba(102, 126, 234, 0.8);
            }
        """)
        
        self.activate_btn = GradientButton("Login With License")
        self.activate_btn.clicked.connect(self.activate)
        card_layout.addWidget(self.activate_btn)
        
        self.progress_bar = ModernProgressBar()
        self.progress_bar.hide()
        card_layout.addWidget(self.progress_bar, 0, Qt.AlignHCenter)
        
        self.status_label = QLabel("Enter your license key to continue")
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
        self.status_label.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            padding-top: 5px;
            letter-spacing: 0.5px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.status_label)
        
        device_frame = QFrame()
        device_frame.setStyleSheet("""
            background-color: rgba(30, 32, 44, 0.6); 
            border-radius: 8px;
            border: 1px solid rgba(60, 62, 74, 0.3);
        """)
        device_layout = QHBoxLayout(device_frame)
        device_layout.setContentsMargins(15, 10, 15, 10)
        
        device_icon = QLabel("🖥️")
        device_icon.setStyleSheet("font-size: 16px;")
        
        device_label = QLabel("Device ID:")
        device_label.setFont(QFont("Segoe UI", 9))
        device_label.setStyleSheet("color: rgba(200,200,200,0.7);")
        
        self.hwid_label = QLabel(f"{self.client.hwid[:8]}...{self.client.hwid[-4:]}")
        self.hwid_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.hwid_label.setStyleSheet("color: rgba(255,255,255,0.9); letter-spacing: 0.5px;")
        
        device_layout.addWidget(device_icon)
        device_layout.addSpacing(5)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.hwid_label)
        device_layout.addStretch()
        
        card_layout.addWidget(device_frame)
        
        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        help_label = QLabel("© 2025 cracked by .gg/cocuk-community | Version 1.0.3")
        help_label.setFont(QFont("Segoe UI", 9))
        help_label.setStyleSheet("""
            color: rgba(180,180,180,0.8);
            letter-spacing: 0.5px;
        """)
        footer_layout.addWidget(help_label)
        footer_layout.addStretch()
        
        content_layout.addWidget(footer)
        
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)
        self.main_widget.setGraphicsEffect(self.shadow)
        
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, 
                 (screen.height() - self.height()) // 2)

    def activate(self):
        key = self.key_entry.text().strip().upper()
        if not key:
            self.show_error("Error", "Please enter a license key")
            return
            
        self.status_label.setText("Verifying license with server...")
        self.activate_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.startAnimation()
        QApplication.processEvents()
        
        QTimer.singleShot(1500, lambda: self.finish_activation(key))

    def finish_activation(self, key):
        valid, msg = self.client.validate_key(key)
        self.progress_bar.stopAnimation()
        self.progress_bar.hide()
        self.activate_btn.setEnabled(True)
        
        if valid:
            self.status_label.setText("License activated successfully!")
            self.hide()  
            triggerbot = FiveMTriggerBot()
            triggerbot.run()  
            self.close()  
        else:
            self.status_label.setText("Activation failed")
            self.show_error("Activation Failed", msg)

    def show_error(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #282a36;
                color: white;
                border: 1px solid #44475a;
                border-radius: 8px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #ff5555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #ff6e6e;
            }
        """)
        msg.exec_()

    def closeEvent(self, event):
        if hasattr(self, 'triggerbot') and self.triggerbot:
            self.triggerbot.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(40, 42, 54))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 32, 44))
    palette.setColor(QPalette.AlternateBase, QColor(50, 52, 64))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(50, 52, 64))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(102, 126, 234))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    window = ClientApp()
    window.show()
    
    sys.exit(app.exec_())