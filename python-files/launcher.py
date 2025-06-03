import sys
import os
import json
import time
import threading
import subprocess
import random

import psutil
import GPUtil
import cv2

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QMenu, QGraphicsDropShadowEffect,
    QGraphicsBlurEffect, QLineEdit, QDialog, QDialogButtonBox, QColorDialog, QComboBox, QCheckBox, QInputDialog, QGroupBox, QGridLayout,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QIcon, QPainter, QBrush, QPen, QFontDatabase, QLinearGradient, QAction, QKeySequence, QPainterPath, QImage, QRadialGradient
)
from PyQt6.QtCore import (
    Qt, QUrl, QTimer, QSize, pyqtSignal, QObject, QRectF, QPropertyAnimation, QEasingCurve, QRect, QPoint, QThread
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

import pygame

ICON_PATH = "assets/icons/"
DEFAULT_BG_PATH = "assets/bg_default.jpg"
DEFAULT_AVATAR = "assets/avatar.png"
FONT_PATH = "assets/fonts/Orbitron.ttf"
LAUNCHER_VERSION = "Hosein Launcher v4.0"

def load_settings():
    defaults = {
        "theme": "dark",
        "main_color": "#a020f0",
        "select_sound": "assets/sounds/select.wav",
        "play_sound": "assets/sounds/play.wav",
        "font_family": "Orbitron",
        "card_size": 1,
        "show_monitor": True,
        "show_recent": True,
        "show_glow": True,
        "default_bg": DEFAULT_BG_PATH,
        "card_width": 180,
        "card_height": 240,
        "card_spacing": 8,
        "card_row_top": 0,
        "welcome_pos": "Top",
        "monitor_top": 16,
        "monitor_spacing": 32,
        "monitor_size": 140,
        "perf_top": 16,
        "perf_spacing": 32,
        "perf_size": 90,
        "bg_blur": 0,
        "bg_fade": 0,
        "last_selected": 0
    }
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                data = json.load(f)
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v
                return data
    except Exception:
        pass
    return defaults.copy()

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=2)

def get_screen_size():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    return size.width(), size.height()

SCREEN_W, SCREEN_H = get_screen_size()
CARD_WIDTH = int(SCREEN_W * 0.09)
CARD_HEIGHT = int(SCREEN_H * 0.22)
CARD_RADIUS = 32
CARD_SPACING = 8

def resolve_shortcut(path):
    if not path.lower().endswith('.lnk'):
        return path
    try:
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        return shortcut.Targetpath
    except Exception as e:
        print("Shortcut resolve error:", e)
        return path

class GamepadSignals(QObject):
    move_left = pyqtSignal()
    move_right = pyqtSignal()
    play = pyqtSignal()
    back = pyqtSignal()

class GamepadThread(threading.Thread):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.running = True

    def run(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No gamepad detected.")
            return
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("Gamepad connected:", joystick.get_name())
        while self.running:
            try:
                pygame.event.pump()
            except pygame.error:
                break
            hat = joystick.get_hat(0) if joystick.get_numhats() > 0 else (0, 0)
            if hat[0] == 1:
                self.signals.move_right.emit()
                time.sleep(0.2)
            elif hat[0] == -1:
                self.signals.move_left.emit()
                time.sleep(0.2)
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if joystick.get_button(0):
                        self.signals.play.emit()
                        time.sleep(0.2)
                    if joystick.get_button(1):
                        self.signals.back.emit()
                        time.sleep(0.2)
            time.sleep(0.05)

    def stop(self):
        self.running = False
        try:
            pygame.quit()
        except Exception:
            pass
# --- اسپلش ویدیو فول‌اسکرین واقعی (بدون parent) ---
class VideoThread(QThread):
    frame_signal = pyqtSignal(QPixmap)
    finished_signal = pyqtSignal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 33
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.frame_signal.emit(pix)
            QThread.msleep(delay)
        cap.release()
        self.finished_signal.emit()

    def stop(self):
        self.running = False

class SplashVideoPlayer(QWidget):
    def __init__(self, video_path, on_finish):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # گرفتن سایز نمایشگر
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        # ویجت ویدیو را بدون parent قرار بده تا مستقل باشد
        self.video_widget = QVideoWidget()
        self.video_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Window
        )
        self.video_widget.setGeometry(screen)
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile(os.path.abspath(video_path)))
        self.player.mediaStatusChanged.connect(self._on_status)
        self.on_finish = on_finish

    def start(self):
        self.video_widget.showFullScreen()
        self.video_widget.raise_()
        self.player.play()

    def _on_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.video_widget.hide()
            if self.on_finish:
                self.on_finish()

# --- گیج مدرن برای مانیتورینگ ---
class ModernGauge(QWidget):
    def __init__(self, label, color, max_value=100, unit="%", show_temp=False, size=140):
        super().__init__()
        self.value = 0
        self.temp = 0
        self.label = label
        self.color = color
        self.max_value = max_value
        self.unit = unit
        self.show_temp = show_temp
        self.setFixedSize(size, size)
        self.font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        self.font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0] if self.font_id != -1 else "Arial"

    def set_value(self, value, temp=None):
        self.value = value
        if temp is not None:
            self.temp = temp
        self.update()

    def paintEvent(self, event):
        s = self.width()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(10, 10, s-20, s-20)
        painter.setBrush(QColor(24,28,36,220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        painter.setPen(QPen(QColor("#232a36"), 18, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 45*16, 270*16)
        angle = 45 + 270 * (self.value / self.max_value)
        painter.setPen(QPen(QColor(self.color), 18, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 45*16, int((angle-45)*16))
        painter.setBrush(QBrush(QColor("#181c24")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(s//4, s//4, s//2, s//2)
        painter.setPen(QColor(self.color))
        painter.setFont(QFont(self.font_family, int(s*0.18), QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}{self.unit}")
        painter.setPen(QColor("#fff"))
        painter.setFont(QFont(self.font_family, int(s*0.09), QFont.Weight.Bold))
        painter.drawText(0, int(s*0.78), s, int(s*0.13), Qt.AlignmentFlag.AlignCenter, self.label)
        if self.show_temp and self.temp:
            painter.setPen(QColor("#ff6a00"))
            painter.setFont(QFont(self.font_family, int(s*0.08), QFont.Weight.Bold))
            painter.drawText(0, int(s*0.68), s, int(s*0.13), Qt.AlignmentFlag.AlignCenter, f"{int(self.temp)}°C")

# --- کارت افزودن بازی ---
class AddGameCard(QWidget):
    def __init__(self, callback, main_color):
        super().__init__()
        self.callback = callback
        self.main_color = main_color
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT + 48)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn = QPushButton("+")
        self.btn.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232a36, stop:1 {self.main_color});
                color: #fff;
                border: 3px dashed {self.main_color};
                border-radius: 28px;
                font-size: 64px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.main_color};
                color: #fff;
            }}
        """)
        self.btn.clicked.connect(self.callback)
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Add Game")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {self.main_color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

# --- کارت بازی با انیمیشن نرم‌تر ---
class GameCard(QWidget):
    def __init__(self, game, callback_select, callback_update, callback_remove, launcher, main_color, font_family, card_size, show_glow):
        super().__init__()
        self.game = game
        self.callback_update = callback_update
        self.callback_remove = callback_remove
        self.launcher = launcher
        self.main_color = main_color
        self.font_family = font_family
        self.card_size = card_size
        self.show_glow = show_glow
        self.selected = False

        self.normal_w = int(CARD_WIDTH * 0.85)
        self.normal_h = int(CARD_HEIGHT * 0.85)
        self.selected_w = int(CARD_WIDTH * 1.15)
        self.selected_h = int(CARD_HEIGHT * 1.15)
        self.setFixedSize(self.normal_w, self.normal_h + 48)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(self.normal_w, self.normal_h)
        self.cover_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_cover(self.game["cover"], selected=False)
        self.layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(self.game["name"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(self.font_family, 15, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {self.main_color}; background: transparent;")
        self.title_label.setFixedHeight(28)
        self.title_label.setWordWrap(True)
        self.title_label.setVisible(False)
        self.layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # سه نقطه فقط روی کارت انتخاب‌شده و گوشه کاور
        self.menu_button = QPushButton("⋮", self.cover_label)
        self.menu_button.setFixedSize(32, 32)
        self.menu_button.move(self.cover_label.width() - 40, 8)
        self.menu_button.setStyleSheet("""
            QPushButton {
                color: #fff; background: rgba(0,0,0,0.5); border: none; border-radius: 16px; font-size: 18px;
            }
            QPushButton:hover { background: #a020f0; color: #fff; }
        """)
        self.menu = QMenu()
        self.menu.addAction("🖼 Change Cover", self.change_cover)
        self.menu.addAction("🌄 Change Background", self.change_bg)
        self.menu.addAction("🗑 Remove Game", self.remove_game)
        self.menu_button.setMenu(self.menu)
        self.menu_button.hide()

        self.setLayout(self.layout)

        self.cover_label.mousePressEvent = self._cover_click
        self.cover_label.enterEvent = self._cover_hover

        self.anim = None

    def _cover_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.launcher and hasattr(self.launcher, "selected_card") and self.launcher.selected_card == self:
                self.start_game()
            else:
                if self.launcher and hasattr(self.launcher, "select_card"):
                    self.launcher.select_card(self, animate=True)
                    self.launcher.play_select_sound()

    def _cover_hover(self, event):
        if self.launcher and hasattr(self.launcher, "select_card"):
            self.launcher.select_card(self, animate=True)
            self.launcher.play_select_sound()

    def keyPressEvent(self, event):
        if self.selected and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.start_game()

    def set_cover(self, path, selected=False):
        w = self.selected_w if selected else self.normal_w
        h = self.selected_h if selected else self.normal_h
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            rounded = QPixmap(w, h)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path_ = QPainterPath()
            path_.addRoundedRect(0, 0, w, h, 28, 28)
            painter.setClipPath(path_)
            painter.drawPixmap(0, 0, pix)
            painter.end()
            self.cover_label.setPixmap(rounded)
        self.cover_label.setFixedSize(w, h)

    def set_selected(self, selected, animate=True):
        if selected == self.selected:
            return
        self.selected = selected
        start_w = self.selected_w if not selected else self.normal_w
        start_h = self.selected_h if not selected else self.normal_h
        end_w = self.selected_w if selected else self.normal_w
        end_h = self.selected_h if selected else self.normal_h

        if animate:
            self.anim = QPropertyAnimation(self.cover_label, b"size")
            self.anim.setDuration(400)  # نرم‌تر از قبل
            self.anim.setStartValue(QSize(start_w, start_h))
            self.anim.setEndValue(QSize(end_w, end_h))
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)  # منحنی نرم‌تر
            self.anim.start()
        self.set_cover(self.game["cover"], selected=selected)
        self.cover_label.setFixedSize(end_w, end_h)
        self.setFixedSize(end_w, end_h + 48)

        if selected:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(60)
            shadow.setOffset(0, 10)
            shadow.setColor(QColor(self.main_color))
            self.cover_label.setGraphicsEffect(shadow)
            self.cover_label.setStyleSheet(f"border: 4px solid {self.main_color}; border-radius: 28px;")
            self.title_label.setVisible(True)
            self.title_label.setWindowOpacity(0.0)
            anim = QPropertyAnimation(self.title_label, b"windowOpacity")
            anim.setDuration(350)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            anim.start()
            self.setFocus()
            self.menu_button.show()
        else:
            self.cover_label.setGraphicsEffect(None)
            self.cover_label.setStyleSheet("border: none; border-radius: 28px;")
            self.title_label.setVisible(False)
            self.menu_button.hide()

    def resizeEvent(self, event):
        self.menu_button.move(self.cover_label.width() - 40, 8)
        super().resizeEvent(event)

    def start_game(self):
        try:
            exec_path = self.game.get("real_exec", self.game["exec"])
            if sys.platform == "win32":
                params = f'"{exec_path}"'
                subprocess.Popen(['powershell', '-Command', f'Start-Process {params} -Verb runAs'])
            else:
                subprocess.Popen([exec_path])
            self.launcher.add_recent(self.game)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot start game:\n{e}")

    def change_cover(self):
        new_cover, _ = QFileDialog.getOpenFileName(self, "Select New Cover", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if new_cover:
            self.game["cover"] = new_cover
            self.set_cover(new_cover)
            self.callback_update(self.game["name"], "cover", new_cover)

    def change_bg(self):
        new_bg, _ = QFileDialog.getOpenFileName(self, "Select New Background", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if new_bg:
            self.game["bg"] = new_bg
            self.callback_update(self.game["name"], "bg", new_bg)

    def remove_game(self):
        confirm = QMessageBox.question(self, "Remove Game", f"Are you sure to remove '{self.game['name']}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.callback_remove(self.game["name"])
class PerformanceModeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(340, 90)
        self.modes = [
            {"name": "Windows", "icon": "windows.svg", "color": "#fff", "halo": "#a0eaff", "power": "SCHEME_BALANCED", "armoury": "Windows"},
            {"name": "Silent", "icon": "silent.svg", "color": "#a0eaff", "halo": "#a0eaff", "power": "SCHEME_MAX", "armoury": "Silent"},
            {"name": "Performance", "icon": "performance.svg", "color": "#ffb300", "halo": "#ffb300", "power": "SCHEME_MIN", "armoury": "Performance"},
            {"name": "Turbo", "icon": "turbo.svg", "color": "#ff6a00", "halo": "#ff6a00", "power": "SCHEME_MIN", "armoury": "Turbo"},
        ]
        self.current_mode = 2
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_power_mode(self.modes[self.current_mode])

    def set_power_mode(self, mode):
        try:
            subprocess.Popen([r"C:\Program Files\ASUS\ARMOURY CRATE Service\ArmouryCrateControl.exe", "-performance", mode["armoury"]])
        except Exception:
            pass
        try:
            os.system(f'powercfg /setactive {mode["power"]}')
        except Exception as e:
            print("Power mode change error:", e)

    def mousePressEvent(self, event):
        self.current_mode = (self.current_mode + 1) % len(self.modes)
        self.set_power_mode(self.modes[self.current_mode])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(24,28,36,180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)
        w = self.width() // 4
        for i, mode in enumerate(self.modes):
            x = i * w
            if i == self.current_mode:
                grad = QLinearGradient(x, 0, x+w, 0)
                grad.setColorAt(0, QColor(mode["halo"]))
                grad.setColorAt(1, QColor("#232a36"))
                painter.setBrush(grad)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(x+6, 10, w-12, 70, 16, 16)
                painter.setPen(QPen(QColor(mode["color"]), 3))
                painter.drawLine(x+16, 80, x+w-16, 80)
            icon = QPixmap(ICON_PATH + mode["icon"])
            painter.drawPixmap(x+w//2-18, 18, 36, 36, icon)
            painter.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            painter.setPen(QColor(mode["color"] if i == self.current_mode else "#fff"))
            painter.drawText(x, 60, w, 24, Qt.AlignmentFlag.AlignCenter, mode["name"])

    def get_mode(self):
        return self.modes[self.current_mode]["name"]

class GlassStatusBar(QWidget):
    def __init__(self, parent, profile, font_family, open_settings_callback, edit_profile_callback):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setFixedWidth(440)
        self.setStyleSheet("background: transparent;")
        self.font_family = font_family
        self.profile = profile
        self.battery = 100
        self.wifi = 100
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        self.update_status()
        self.clock = time.strftime("%H:%M")
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        self.settings_btn = QPushButton(self)
        self.settings_btn.setIcon(QIcon(ICON_PATH + "settings.svg"))
        self.settings_btn.setIconSize(QSize(28, 28))
        self.settings_btn.setStyleSheet("background: transparent; border: none;")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(open_settings_callback)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.avatar_label = QLabel(self)
        self.avatar_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.avatar_label.mousePressEvent = edit_profile_callback

    def update_status(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                self.battery = int(battery.percent)
            else:
                self.battery = random.randint(60, 100)
        except Exception:
            self.battery = random.randint(60, 100)
        try:
            self.wifi = min(100, max(0, int(psutil.net_if_stats().get('Wi-Fi', psutil.net_if_stats().get('wlan0', type('', (), {'speed':0})())).speed / 10)))
        except Exception:
            self.wifi = random.randint(70, 100)
        self.update()

    def update_clock(self):
        self.clock = time.strftime("%H:%M")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor(24,28,36,220))
        grad.setColorAt(1, QColor(32,36,56,240))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)
        wifi_icon = QPixmap(ICON_PATH + "wifi.png")
        painter.drawPixmap(20, 16, 28, 28, wifi_icon)
        painter.setFont(QFont(self.font_family, 13, QFont.Weight.Bold))
        painter.setPen(QColor("#ffe600"))
        painter.drawText(54, 36, f"{self.wifi}%")
        battery_icon = QPixmap(ICON_PATH + "battery.png")
        painter.drawPixmap(110, 16, 28, 28, battery_icon)
        painter.setPen(QColor("#00ff00"))
        painter.drawText(144, 36, f"{self.battery}%")
        painter.setFont(QFont(self.font_family, 16, QFont.Weight.Bold))
        painter.setPen(QColor("#a020f0"))
        painter.drawText(200, 38, self.clock)
        avatar = QPixmap(self.profile["avatar"]).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.avatar_label.setPixmap(avatar)
        self.avatar_label.setGeometry(320, 14, 32, 32)
        painter.setFont(QFont(self.font_family, 12, QFont.Weight.Bold))
        painter.setPen(QColor("#fff"))
        painter.drawText(360, 36, self.profile["name"])
        self.settings_btn.move(self.width()-48, 12)
        self.settings_btn.raise_()

class ProfileDialog(QDialog):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile")
        self.setFixedSize(420, 260)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232a36, stop:1 #181c24);
                border-radius: 18px;
            }
            QLabel, QLineEdit {
                color: #fff;
                font-size: 15px;
            }
            QPushButton {
                background: #a020f0;
                color: #fff;
                border-radius: 8px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background: #ff00c8;
            }
        """)
        self.profile = dict(profile)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_avatar(self.profile.get("avatar", DEFAULT_AVATAR))
        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.avatar_btn = QPushButton("Change Avatar")
        self.avatar_btn.clicked.connect(self.pick_avatar)
        layout.addWidget(self.avatar_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(self.profile.get("name", "Player"))
        name_row.addWidget(self.name_edit)
        layout.addLayout(name_row)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def set_avatar(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            pix = QPixmap(DEFAULT_AVATAR)
        pix = pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        rounded = QPixmap(80, 80)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path_ = QPainterPath()
        path_.addEllipse(0, 0, 80, 80)
        painter.setClipPath(path_)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        self.avatar_label.setPixmap(rounded)
        self.profile["avatar"] = path

    def pick_avatar(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Avatar", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file:
            self.set_avatar(file)

    def get_profile(self):
        return {
            "name": self.name_edit.text().strip() or "Player",
            "avatar": self.profile.get("avatar", DEFAULT_AVATAR)
        }

# SettingsDialog 
class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(1200, 480)
        # بک‌گراند خاص
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232a36, stop:1 #181c24);
                border-radius: 24px;
            }
            QGroupBox {
                background: rgba(24,28,36,180);
                border-radius: 16px;
                font-weight: bold;
                color: #a020f0;
            }
            QLabel, QCheckBox, QComboBox, QLineEdit {
                color: #fff;
                font-size: 15px;
            }
            QPushButton {
                background: #a020f0;
                color: #fff;
                border-radius: 8px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background: #ff00c8;
            }
        """)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {background: transparent; border: none;}
            QScrollBar:horizontal {height: 16px;}
        """)
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # --- گروه تم و رنگ ---
        group_theme = QGroupBox("Theme & Color")
        grid_theme = QGridLayout()
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Dark", "Light"])
        self.theme_box.setCurrentText("Dark" if settings["theme"] == "dark" else "Light")
        grid_theme.addWidget(QLabel("Theme:"), 0, 0)
        grid_theme.addWidget(self.theme_box, 0, 1)
        self.color_btn = QPushButton("Change Main Color")
        self.color_btn.clicked.connect(self.pick_color)
        grid_theme.addWidget(self.color_btn, 1, 0, 1, 2)
        group_theme.setLayout(grid_theme)
        layout.addWidget(group_theme)

        # --- گروه فونت و سایز ---
        group_font = QGroupBox("Font & Card Size")
        grid_font = QGridLayout()
        self.font_box = QComboBox()
        self.font_box.addItems(["Orbitron", "Arial", "Segoe UI"])
        self.font_box.setCurrentText(settings["font_family"])
        grid_font.addWidget(QLabel("Font:"), 0, 0)
        grid_font.addWidget(self.font_box, 0, 1)
        self.size_box = QComboBox()
        self.size_box.addItems(["Small", "Medium", "Large"])
        self.size_box.setCurrentIndex(settings["card_size"])
        grid_font.addWidget(QLabel("Card Size:"), 1, 0)
        grid_font.addWidget(self.size_box, 1, 1)
        group_font.setLayout(grid_font)
        layout.addWidget(group_font)

        # --- گروه مانیتورینگ و پرفورمنس با کنترل فاصله و سایز ---
        group_monitor = QGroupBox("Monitoring & Performance Panel")
        grid_monitor = QGridLayout()
        self.monitor_check = QCheckBox("Show Monitoring Panel")
        self.monitor_check.setChecked(settings["show_monitor"])
        grid_monitor.addWidget(self.monitor_check, 0, 0, 1, 2)
        grid_monitor.addWidget(QLabel("Monitor Top Margin:"), 1, 0)
        self.monitor_top_edit = QLineEdit(str(settings["monitor_top"]))
        grid_monitor.addWidget(self.monitor_top_edit, 1, 1)
        grid_monitor.addWidget(QLabel("Monitor Spacing:"), 2, 0)
        self.monitor_spacing_edit = QLineEdit(str(settings["monitor_spacing"]))
        grid_monitor.addWidget(self.monitor_spacing_edit, 2, 1)
        grid_monitor.addWidget(QLabel("Monitor Size:"), 3, 0)
        self.monitor_size_edit = QLineEdit(str(settings["monitor_size"]))
        grid_monitor.addWidget(self.monitor_size_edit, 3, 1)
        self.performance_check = QCheckBox("Show Performance Panel")
        self.performance_check.setChecked(settings.get("show_performance", True))
        grid_monitor.addWidget(self.performance_check, 4, 0, 1, 2)
        grid_monitor.addWidget(QLabel("Performance Top Margin:"), 5, 0)
        self.perf_top_edit = QLineEdit(str(settings["perf_top"]))
        grid_monitor.addWidget(self.perf_top_edit, 5, 1)
        grid_monitor.addWidget(QLabel("Performance Spacing:"), 6, 0)
        self.perf_spacing_edit = QLineEdit(str(settings["perf_spacing"]))
        grid_monitor.addWidget(self.perf_spacing_edit, 6, 1)
        grid_monitor.addWidget(QLabel("Performance Size:"), 7, 0)
        self.perf_size_edit = QLineEdit(str(settings["perf_size"]))
        grid_monitor.addWidget(self.perf_size_edit, 7, 1)
        group_monitor.setLayout(grid_monitor)
        layout.addWidget(group_monitor)

        # --- گروه سایر تنظیمات ---
        group_other = QGroupBox("Other Settings")
        grid_other = QGridLayout()
        self.recent_check = QCheckBox("Show Recently Played")
        self.recent_check.setChecked(settings["show_recent"])
        grid_other.addWidget(self.recent_check, 0, 0, 1, 2)
        self.glow_check = QCheckBox("Glow Effect on Selected Card")
        self.glow_check.setChecked(settings["show_glow"])
        grid_other.addWidget(self.glow_check, 1, 0, 1, 2)
        self.select_sound_btn = QPushButton("Change Select Sound")
        self.select_sound_btn.clicked.connect(self.pick_select_sound)
        grid_other.addWidget(self.select_sound_btn, 2, 0, 1, 2)
        self.play_sound_btn = QPushButton("Change Play Sound")
        self.play_sound_btn.clicked.connect(self.pick_play_sound)
        grid_other.addWidget(self.play_sound_btn, 3, 0, 1, 2)
        self.bg_btn = QPushButton("Change Default Background")
        self.bg_btn.clicked.connect(self.pick_bg)
        grid_other.addWidget(self.bg_btn, 4, 0, 1, 2)
        self.blur_edit = QLineEdit(str(settings.get("bg_blur", 0)))
        grid_other.addWidget(QLabel("Background Blur:"), 5, 0)
        grid_other.addWidget(self.blur_edit, 5, 1)
        self.fade_edit = QLineEdit(str(settings.get("bg_fade", 0)))
        grid_other.addWidget(QLabel("Background Dark Fade:"), 6, 0)
        grid_other.addWidget(self.fade_edit, 6, 1)
        group_other.setLayout(grid_other)
        layout.addWidget(group_other)

        # --- گروه تنظیمات کارت ---
        group_card = QGroupBox("Card Layout")
        grid_card = QGridLayout()
        self.card_width_edit = QLineEdit(str(settings["card_width"]))
        self.card_height_edit = QLineEdit(str(settings["card_height"]))
        self.card_spacing_edit = QLineEdit(str(settings.get("card_spacing", 0)))  # مقدار پیش‌فرض 0
        self.card_row_top_edit = QLineEdit(str(settings["card_row_top"]))
        grid_card.addWidget(QLabel("Card Width:"), 0, 0)
        grid_card.addWidget(self.card_width_edit, 0, 1)
        grid_card.addWidget(QLabel("Card Height:"), 1, 0)
        grid_card.addWidget(self.card_height_edit, 1, 1)
        grid_card.addWidget(QLabel("Card Spacing:"), 2, 0)
        grid_card.addWidget(self.card_spacing_edit, 2, 1)
        grid_card.addWidget(QLabel("Card Row Top Margin:"), 3, 0)
        grid_card.addWidget(self.card_row_top_edit, 3, 1)
        group_card.setLayout(grid_card)
        layout.addWidget(group_card)

        # --- گروه موقعیت متن خوش‌آمدگویی ---
        group_welcome = QGroupBox("Welcome Text Position")
        grid_welcome = QGridLayout()
        self.welcome_pos_box = QComboBox()
        self.welcome_pos_box.addItems(["Top", "Center", "Bottom", "Left", "Right"])
        self.welcome_pos_box.setCurrentText(settings["welcome_pos"])
        grid_welcome.addWidget(QLabel("Position:"), 0, 0)
        grid_welcome.addWidget(self.welcome_pos_box, 0, 1)
        group_welcome.setLayout(grid_welcome)
        layout.addWidget(group_welcome)

        # --- دکمه‌های خروجی ---
        group_export = QGroupBox("Export / Import / Reset")
        grid_export = QGridLayout()
        self.export_btn = QPushButton("Export Games List")
        self.export_btn.clicked.connect(self.export_games)
        self.import_btn = QPushButton("Import Games List")
        self.import_btn.clicked.connect(self.import_games)
        self.reset_btn = QPushButton("Reset All Settings")
        self.reset_btn.clicked.connect(self.reset_settings)
        grid_export.addWidget(self.export_btn, 0, 0)
        grid_export.addWidget(self.import_btn, 1, 0)
        grid_export.addWidget(self.reset_btn, 2, 0)
        group_export.setLayout(grid_export)
        layout.addWidget(group_export)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        scroll.setWidget(main_widget)
        vbox = QVBoxLayout(self)
        vbox.addWidget(scroll)
        self.setLayout(vbox)

        self.main_color = settings["main_color"]
        self.select_sound = settings["select_sound"]
        self.play_sound = settings["play_sound"]
        self.default_bg = settings["default_bg"]

    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.main_color), self, "Pick Main Color")
        if color.isValid():
            self.main_color = color.name()

    def pick_select_sound(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Select Sound", "", "Audio (*.wav *.mp3 *.ogg)")
        if file:
            self.select_sound = file

    def pick_play_sound(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Play Sound", "", "Audio (*.wav *.mp3 *.ogg)")
        if file:
            self.play_sound = file

    def pick_bg(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Default Background", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file:
            self.default_bg = file

    def export_games(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export Games List", "", "JSON (*.json)")
        if file:
            try:
                with open("games.json", "r") as f:
                    games = json.load(f)
                with open(file, "w") as f2:
                    json.dump(games, f2, indent=2)
                QMessageBox.information(self, "Export", "Games exported successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def import_games(self):
        file, _ = QFileDialog.getOpenFileName(self, "Import Games List", "", "JSON (*.json)")
        if file:
            try:
                with open(file, "r") as f:
                    games = json.load(f)
                with open("games.json", "w") as f2:
                    json.dump(games, f2, indent=2)
                QMessageBox.information(self, "Import", "Games imported successfully. Please refresh (F5).")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", str(e))

    def reset_settings(self):
        self.theme_box.setCurrentText("Dark")
        self.main_color = "#a020f0"
        self.font_box.setCurrentText("Orbitron")
        self.size_box.setCurrentIndex(1)
        self.monitor_check.setChecked(True)
        self.performance_check.setChecked(True)
        self.recent_check.setChecked(True)
        self.glow_check.setChecked(True)
        self.select_sound = "assets/sounds/select.wav"
        self.play_sound = "assets/sounds/play.wav"
        self.default_bg = DEFAULT_BG_PATH
        self.card_width_edit.setText("180")
        self.card_height_edit.setText("240")
        self.card_spacing_edit.setText("0")
        self.card_row_top_edit.setText("0")
        self.monitor_top_edit.setText("16")
        self.monitor_spacing_edit.setText("32")
        self.monitor_size_edit.setText("140")
        self.perf_top_edit.setText("16")
        self.perf_spacing_edit.setText("32")
        self.perf_size_edit.setText("90")
        self.blur_edit.setText("0")
        self.fade_edit.setText("0")
        self.welcome_pos_box.setCurrentText("Top")

    def get_settings(self):
        return {
            "theme": "dark" if self.theme_box.currentText() == "Dark" else "light",
            "main_color": self.main_color,
            "select_sound": self.select_sound,
            "play_sound": self.play_sound,
            "font_family": self.font_box.currentText(),
            "card_size": self.size_box.currentIndex(),
            "show_monitor": self.monitor_check.isChecked(),
            "show_performance": self.performance_check.isChecked(),
            "show_recent": self.recent_check.isChecked(),
            "show_glow": self.glow_check.isChecked(),
            "default_bg": self.default_bg,
            "card_width": int(self.card_width_edit.text()),
            "card_height": int(self.card_height_edit.text()),
            "card_spacing": int(self.card_spacing_edit.text()),
            "card_row_top": int(self.card_row_top_edit.text()),
            "welcome_pos": self.welcome_pos_box.currentText(),
            "monitor_top": int(self.monitor_top_edit.text()),
            "monitor_spacing": int(self.monitor_spacing_edit.text()),
            "monitor_size": int(self.monitor_size_edit.text()),
            "perf_top": int(self.perf_top_edit.text()),
            "perf_spacing": int(self.perf_spacing_edit.text()),
            "perf_size": int(self.perf_size_edit.text()),
            "bg_blur": int(self.blur_edit.text()),
            "bg_fade": int(self.fade_edit.text())
        }

class PS5Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.profile = self.load_profile()
        self.games = self.load_games()
        self.selected_card = None
        settings = load_settings()
        self.theme = settings["theme"]
        self.main_color = settings["main_color"]
        self.select_sound = settings["select_sound"]
        self.play_sound = settings["play_sound"]
        self.font_family = settings["font_family"]
        self.card_size = settings["card_size"]
        self.show_monitor = settings["show_monitor"]
        self.show_performance = settings.get("show_performance", True)
        self.show_recent = settings["show_recent"]
        self.show_glow = settings["show_glow"]
        self.default_bg = settings["default_bg"]
        self.card_width = settings["card_width"]
        self.card_height = settings["card_height"]
        self.card_spacing = settings.get("card_spacing", 8)
        self.card_row_top = settings["card_row_top"]
        self.welcome_pos = settings["welcome_pos"]
        self.monitor_top = settings["monitor_top"]
        self.monitor_spacing = settings["monitor_spacing"]
        self.monitor_size = settings["monitor_size"]
        self.perf_top = settings["perf_top"]
        self.perf_spacing = settings["perf_spacing"]
        self.perf_size = settings["perf_size"]
        self.bg_blur_value = settings.get("bg_blur", 0)
        self.bg_fade_value = settings.get("bg_fade", 0)
        self.language = "en"
        self.locked = False

        self.current_index = settings.get("last_selected", 0)
        self.recent_games = self.load_recent()

        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, SCREEN_W, SCREEN_H)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg.lower()
        self.bg_blur = QGraphicsBlurEffect()
        self.bg_blur.setBlurRadius(self.bg_blur_value)
        self.bg.setGraphicsEffect(self.bg_blur)
        self.setWindowTitle("Hosein Launcher v4.0")
        self.setStyleSheet("background: transparent;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.showMaximized()

        self.bg_opacity = 0.85
        self.bg_fade_anim = QPropertyAnimation(self.bg, b"windowOpacity")
        self.bg_fade_anim.setDuration(600)
        self.bg_fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.select_player = QMediaPlayer()
        self.select_audio = QAudioOutput()
        self.select_player.setAudioOutput(self.select_audio)
        self.select_player.setSource(QUrl.fromLocalFile(os.path.abspath(self.select_sound)))
        self.select_audio.setVolume(1.0)
        self.play_player = QMediaPlayer()
        self.play_audio = QAudioOutput()
        self.play_player.setAudioOutput(self.play_audio)
        self.play_player.setSource(QUrl.fromLocalFile(os.path.abspath(self.play_sound)))
        self.play_audio.setVolume(1.0)
        self.startup_player = QMediaPlayer()
        self.startup_audio = QAudioOutput()
        self.startup_player.setAudioOutput(self.startup_audio)
        self.startup_player.setSource(QUrl.fromLocalFile(os.path.abspath("assets/sounds/startup.wav")))
        self.startup_audio.setVolume(1.0)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # ردیف کارت‌ها (بالای صفحه)
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cards_scroll.setStyleSheet("""
            QScrollArea {background: transparent; border: none;}
            QScrollBar:horizontal, QScrollBar:vertical {height: 0px; width: 0px;}
        """)
        self.cards_widget = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(32, 16, 32, 0)
        self.cards_layout.setSpacing(self.card_spacing)
        self.cards_scroll.setWidget(self.cards_widget)
        self.main_layout.addWidget(self.cards_scroll, alignment=Qt.AlignmentFlag.AlignTop)

        # --- ویجت خوش‌آمدگویی و شمارش بازی‌ها (قبل از مانیتورینگ) ---
        self.welcome_panel = QWidget()
        self.welcome_panel.setFixedHeight(60)
        welcome_layout = QVBoxLayout(self.welcome_panel)
        welcome_layout.setContentsMargins(32, 24, 0, 0)
        welcome_layout.setSpacing(0)

        self.welcome_label = QLabel(f"Welcome, {self.profile['name']}! Ready to Play?")
        self.welcome_label.setFont(QFont(self.font_family, 22, QFont.Weight.Bold))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.welcome_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a020f0, stop:1 #00eaff);
            }
        """)
        welcome_layout.addWidget(self.welcome_label)

        self.games_count_label = QLabel()
        self.games_count_label.setFont(QFont(self.font_family, 13))
        self.games_count_label.setStyleSheet("color: #b0eaff; padding-top: 2px;")
        self.games_count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        welcome_layout.addWidget(self.games_count_label)

        self.main_layout.addWidget(self.welcome_panel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # استاتوس بار گوشه بالا راست
        self.status_bar = GlassStatusBar(self, self.profile, self.font_family, self.open_settings, self.edit_profile)
        self.status_bar.setParent(self)
        self.status_bar.show()
        self.status_bar.move(self.width() - self.status_bar.width() - 24, 16)

        # --- پنل مانیتورینگ و پرفورمنس پایین صفحه (جمع و نزدیک) ---
        self.bottom_panel = QWidget(self)
        self.bottom_panel.setFixedHeight(140)
        self.bottom_panel.setStyleSheet("background: transparent;")
        self.bottom_layout = QHBoxLayout(self.bottom_panel)
        self.bottom_layout.setContentsMargins(16, 4, 16, 4)
        self.bottom_layout.setSpacing(2)
        self.gauge_cpu = ModernGauge("CPU", "#00eaff", 100, "%", True, size=self.monitor_size)
        self.gauge_gpu = ModernGauge("GPU", "#ff00c8", 100, "%", True, size=self.monitor_size)
        self.gauge_ram = ModernGauge("RAM", "#ffe600", 100, "%", False, size=self.monitor_size)
        self.gauge_fan = ModernGauge("FAN", "#ff6a00", 100, "%", False, size=self.monitor_size)
        self.performance_mode = PerformanceModeWidget()
        self.performance_mode.setFixedHeight(90)
        self.performance_mode.setFixedWidth(340)
        self.bottom_layout.addWidget(self.gauge_cpu)
        self.bottom_layout.addWidget(self.gauge_gpu)
        self.bottom_layout.addWidget(self.gauge_ram)
        self.bottom_layout.addWidget(self.gauge_fan)
        self.bottom_layout.addWidget(self.performance_mode)
        self.bottom_panel.setVisible(self.show_monitor or self.show_performance)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.bottom_panel, alignment=Qt.AlignmentFlag.AlignBottom)

        self.version_label = QLabel(f"{LAUNCHER_VERSION}")
        self.version_label.setStyleSheet("color: #888; font-size: 12px; margin: 8px;")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.version_label)

        self.shortcut_search = QAction(self)
        self.shortcut_search.setShortcut(QKeySequence("Ctrl+F"))
        self.shortcut_search.triggered.connect(self.quick_search)
        self.addAction(self.shortcut_search)

        self.shortcut_lock = QAction(self)
        self.shortcut_lock.setShortcut(QKeySequence("Ctrl+L"))
        self.shortcut_lock.triggered.connect(self.lock_launcher)
        self.addAction(self.shortcut_lock)

        self.shortcut_theme = QAction(self)
        self.shortcut_theme.setShortcut(QKeySequence("Alt+T"))
        self.shortcut_theme.triggered.connect(self.toggle_theme)
        self.addAction(self.shortcut_theme)

        self.shortcut_lang = QAction(self)
        self.shortcut_lang.setShortcut(QKeySequence("Alt+L"))
        self.shortcut_lang.triggered.connect(self.toggle_language)
        self.addAction(self.shortcut_lang)

        self.shortcut_help = QAction(self)
        self.shortcut_help.setShortcut(QKeySequence("F1"))
        self.shortcut_help.triggered.connect(self.show_help)
        self.addAction(self.shortcut_help)

        self.populate()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()
        self.set_default_bg()
        self.gamepad_signals = GamepadSignals()
        self.gamepad_signals.move_left.connect(self.move_left)
        self.gamepad_signals.move_right.connect(self.move_right)
        self.gamepad_signals.play.connect(self.play_selected)
        self.gamepad_signals.back.connect(self.close_launcher)
        self.gamepad_thread = GamepadThread(self.gamepad_signals)
        self.gamepad_thread.daemon = True
        self.gamepad_thread.start()

        if self.show_monitor or self.show_performance:
            self.monitor_timer = QTimer()
            self.monitor_timer.timeout.connect(self.update_monitor)
            self.monitor_timer.start(1200)
            self.update_monitor()

        # --- اسپلش ویدیو Overlay (بدون parent) ---
        self.splash = SplashVideoPlayer("assets/intro.mp4", self.after_splash)
        self.splash.start()
        self.setWindowOpacity(0.0)

    def set_default_bg(self):
        self.set_bg(self.default_bg)

    def set_bg(self, path):
        if not hasattr(self, "bg"):
            return
        if not os.path.exists(path):
            self.bg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #181c24, stop:1 #232a36);")
            return
        pix = QPixmap(path)
        if not pix.isNull():
            w, h = self.width(), self.height()
            img_w, img_h = pix.width(), pix.height()
            scale = max(w / img_w, h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            pix = pix.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (pix.width() - w) // 2
            y = (pix.height() - h) // 2
            cropped = pix.copy(x, y, w, h)
            vignette = QPixmap(w, h)
            vignette.fill(Qt.GlobalColor.transparent)
            painter = QPainter(vignette)
            painter.drawPixmap(0, 0, cropped)
            vignette_strength = getattr(self, "bg_fade_value", 0)
            if vignette_strength > 0:
                vignette_mask = QPixmap(w, h)
                vignette_mask.fill(Qt.GlobalColor.transparent)
                mask_painter = QPainter(vignette_mask)
                mask_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                grad = QRadialGradient(w//2, h//2, max(w, h)//1.1)
                grad.setColorAt(0.0, QColor(0, 0, 0, 0))
                grad.setColorAt(0.7, QColor(0, 0, 0, 0))
                grad.setColorAt(1.0, QColor(0, 0, 0, min(255, vignette_strength)))
                mask_painter.setBrush(QBrush(grad))
                mask_painter.setPen(Qt.PenStyle.NoPen)
                mask_painter.drawRect(0, 0, w, h)
                mask_painter.end()
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.drawPixmap(0, 0, vignette_mask)
            painter.end()
            self.bg.setPixmap(vignette)
            self.bg.setGeometry(0, 0, w, h)
            self.bg_blur.setBlurRadius(self.bg_blur_value)
            self.bg_fade_anim.stop()
            self.bg.setWindowOpacity(0.0)
            self.bg_fade_anim.setStartValue(0.0)
            self.bg_fade_anim.setEndValue(self.bg_opacity)
            self.bg_fade_anim.start()
        else:
            self.bg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #181c24, stop:1 #232a36);")

    def populate(self):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.cards_layout.setSpacing(self.card_spacing)
        self.cards = []
        for game in self.games:
            global CARD_WIDTH, CARD_HEIGHT, CARD_SPACING
            CARD_WIDTH = self.card_width
            CARD_HEIGHT = self.card_height
            CARD_SPACING = self.card_spacing
            card = GameCard(
                game, self.select_card, self.update_game_data, self.remove_game_data, self, self.main_color, self.font_family, self.card_size, self.show_glow
            )
            self.cards_layout.addWidget(card)
            self.cards.append(card)
        add_btn = AddGameCard(self.add_game, self.main_color)
        self.cards_layout.addWidget(add_btn)
        if self.cards:
            self.current_index = min(self.current_index, len(self.cards)-1)
            self.select_card(self.cards[self.current_index], animate=False)
        else:
            self.selected_card = None
            self.current_index = 0
            self.set_default_bg()

    def update_monitor(self):
        cpu = psutil.cpu_percent()
        temp = None
        try:
            temp = psutil.sensors_temperatures()
            cpu_temp = None
            for name, entries in temp.items():
                for entry in entries:
                    if "cpu" in entry.label.lower() or "core" in entry.label.lower():
                        cpu_temp = entry.current
                        break
                if cpu_temp: break
        except Exception: cpu_temp = None
        if self.show_monitor:
            self.gauge_cpu.set_value(cpu, cpu_temp)
        gpu = 0
        gpu_temp = None
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0].load * 100
                gpu_temp = gpus[0].temperature
        except Exception:
            pass
        if self.show_monitor:
            self.gauge_gpu.set_value(gpu, gpu_temp)
        ram = psutil.virtual_memory().percent
        if self.show_monitor:
            self.gauge_ram.set_value(ram)
        fan_speed = random.randint(30, 80)
        if self.show_monitor:
            self.gauge_fan.set_value(fan_speed)
        self.bottom_panel.setVisible(self.show_monitor or self.show_performance)

    def add_game(self):
        exe, _ = QFileDialog.getOpenFileName(
            self, "Select Executable or Shortcut",
            "", "Executables (*.exe *.lnk);;All Files (*)"
        )
        if not exe:
            return
        real_exe = resolve_shortcut(exe)
        cover, _ = QFileDialog.getOpenFileName(self, "Select Cover Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if not cover:
            return
        bg, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if not bg:
            return
        name = os.path.basename(real_exe).replace(".exe", "")
        if any(g['name'].lower() == name.lower() for g in self.games):
            QMessageBox.warning(self, "Duplicate Game", "A game with this name already exists.")
            return
        new_game = {"name": name, "exec": exe, "real_exec": real_exe, "cover": cover, "bg": bg, "favorite": False}
        self.games.append(new_game)
        self.save_games()
        self.populate()

    def select_card(self, selected_card, animate=True):
        if selected_card not in self.cards:
            return
        self.play_select_sound()
        for card in self.cards:
            card.set_selected(False, animate=True)
        selected_card.set_selected(True, animate=animate)
        self.selected_card = selected_card
        self.current_index = self.cards.index(selected_card)
        bg = selected_card.game.get("bg", selected_card.game["cover"])
        self.set_bg(bg)
        settings = load_settings()
        settings["last_selected"] = self.current_index
        save_settings(settings)
        # اسکرول خودکار کارت انتخاب شده به وسط
        scroll = self.cards_scroll.horizontalScrollBar()
        card_widget = self.cards[self.current_index]
        card_x = card_widget.pos().x()
        card_w = card_widget.width()
        scroll_center = card_x + card_w // 2 - self.cards_scroll.viewport().width() // 2
        scroll.setValue(max(0, scroll_center))

    def play_select_sound(self):
        self.select_player.stop()
        self.select_player.play()

    def keyPressEvent(self, event):
        if self.selected_card and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.selected_card.start_game()
        else:
            super().keyPressEvent(event)

    def load_profile(self):
        try:
            if os.path.exists("profile.json"):
                with open("profile.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"name": "Player", "avatar": DEFAULT_AVATAR}

    def save_profile(self):
        with open("profile.json", "w") as f:
            json.dump(self.profile, f, indent=2)

    def edit_profile(self, event):
        dlg = ProfileDialog(self, self.profile)
        if dlg.exec():
            self.profile = dlg.get_profile()
            self.save_profile()
            self.status_bar.profile = self.profile
            self.status_bar.update()
            self.welcome_label.setText(f"Welcome, {self.profile['name']}! Ready to Play?")

    def load_games(self):
        try:
            if os.path.exists("games.json"):
                with open("games.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def save_games(self):
        with open("games.json", "w") as f:
            json.dump(self.games, f, indent=2)

    def load_recent(self):
        try:
            if os.path.exists("recent.json"):
                with open("recent.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def save_recent(self):
        with open("recent.json", "w") as f:
            json.dump(self.recent_games, f, indent=2)

    def add_recent(self, game):
        self.recent_games = [g for g in self.recent_games if g["name"] != game["name"]]
        self.recent_games.insert(0, game)
        self.recent_games = self.recent_games[:6]
        self.save_recent()

    def update_game_data(self, name, field, value):
        for g in self.games:
            if g["name"] == name:
                g[field] = value
        self.save_games()
        self.populate()

    def remove_game_data(self, name):
        self.games = [g for g in self.games if g["name"] != name]
        self.save_games()
        self.populate()

    def move_left(self):
        if self.current_index > 0:
            self.select_card(self.cards[self.current_index - 1])

    def move_right(self):
        if self.current_index < len(self.cards) - 1:
            self.select_card(self.cards[self.current_index + 1])

    def play_selected(self):
        if self.selected_card:
            self.selected_card.start_game()

    def close_launcher(self):
        self.close()

    def closeEvent(self, event):
        if hasattr(self, "gamepad_thread"):
            self.gamepad_thread.stop()
        if hasattr(self, "monitor_timer"):
            self.monitor_timer.stop()
        event.accept()

    def quick_search(self):
        text, ok = QInputDialog.getText(self, "Quick Search", "Enter game name:")
        if ok and text:
            for i, card in enumerate(self.cards):
                if text.lower() in card.game["name"].lower():
                    self.select_card(card)
                    break

    def lock_launcher(self):
        self.locked = True
        QMessageBox.information(self, "Locked", "Launcher is locked. Press ESC to exit.")

    def open_settings(self):
        dlg = SettingsDialog(self, load_settings())
        if dlg.exec():
            new_settings = dlg.get_settings()
            save_settings(new_settings)
            self.theme = new_settings["theme"]
            self.main_color = new_settings["main_color"]
            self.font_family = new_settings["font_family"]
            self.card_size = new_settings["card_size"]
            self.show_monitor = new_settings.get("show_monitor", True)
            self.show_performance = new_settings.get("show_performance", True)
            self.card_width = new_settings["card_width"]
            self.card_height = new_settings["card_height"]
            self.card_spacing = new_settings["card_spacing"]
            self.monitor_size = new_settings.get("monitor_size", 140)
            self.default_bg = new_settings["default_bg"]
            self.bg_blur_value = new_settings.get("bg_blur", 0)
            self.bg_fade_value = new_settings.get("bg_fade", 0)
            self.set_default_bg()
            self.populate()
            self.bottom_panel.setVisible(self.show_monitor or self.show_performance)

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            self.setStyleSheet("background: #fff;")
        else:
            self.theme = "dark"
            self.setStyleSheet("background: transparent;")
        self.populate()

    def toggle_language(self):
        if self.language == "en":
            self.language = "fa"
            self.welcome_label.setText(f"سلام {self.profile['name']} عزیز! به Hosein Launcher خوش آمدید.")
            self.games_count_label.setText(f"تعداد بازی‌ها: {len(self.games)}")
        else:
            self.language = "en"
            self.welcome_label.setText(f"Welcome, {self.profile['name']}! Ready to Play?")
            self.games_count_label.setText(f"Games count: {len(self.games)}")

    def show_help(self):
        QMessageBox.information(self, "Help", 
            "F1: Help\nCtrl+F: Quick Search\nCtrl+L: Lock Launcher\nAlt+T: Switch Theme\nAlt+L: Switch Language\nEsc: Exit")

    def update_clock(self):
        if self.language == "fa":
            self.games_count_label.setText(f"تعداد بازی‌ها: {len(self.games)}")
        else:
            self.games_count_label.setText(f"Games count: {len(self.games)}")

    def after_splash(self):
        self.splash.hide()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowOpacity(1.0)
        self.fadein_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fadein_anim.setDuration(700)
        self.fadein_anim.setStartValue(0.0)
        self.fadein_anim.setEndValue(1.0)
        self.fadein_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fadein_anim.start()
        self.startup_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists(FONT_PATH):
        QFontDatabase.addApplicationFont(FONT_PATH)
    win = PS5Launcher()
    win.show()
    sys.exit(app.exec())