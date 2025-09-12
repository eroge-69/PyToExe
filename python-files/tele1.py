import os, sys, threading, time, ctypes, json, random, psutil, winsound
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSystemTrayIcon, QMenu, QGridLayout, QCheckBox, QComboBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QPointF
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QPen, QLinearGradient
from PyQt6.QtWidgets import QProxyStyle, QStyle, QStyleOptionButton
import pydivert
import keyboard
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Set, List

FILTER_BASE = "outbound and udp.PayloadLength >= 24 and udp.PayloadLength <= 68"
HOTKEY_FILE = "teleport_hotkey.json"

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

class AppState(Enum):
    IDLE = "idle"
    CAPTURING_PACKETS = "capturing"
    WAITING_FOR_HOTKEY = "waiting_hotkey"
    SETTING_HOTKEY = "setting_hotkey"

@dataclass
class HotkeyConfig:
    key: str = ""
    display_name: str = ""
    is_valid: bool = False

@dataclass
class AppConfig:
    hotkey: HotkeyConfig
    audio_enabled: bool = True

@dataclass
class NetworkStats:
    packets_held: int = 0
    packets_sent: int = 0
    total_processed: int = 0
    bytes_held: int = 0
    bytes_sent: int = 0
    network_usage: float = 0.0
    ping: int = 0
    upload_speed: float = 0.0
    download_speed: float = 0.0
    cpu_percent: float = 0.0

class StatusSignals(QObject):
    update_status = pyqtSignal(str, str)
    update_packet_count = pyqtSignal(int)
    update_hotkey = pyqtSignal(str)
    update_button_state = pyqtSignal(bool)
    update_overlay_status = pyqtSignal(dict)
    update_network_stats = pyqtSignal(object)
    update_signal_wave = pyqtSignal(float, float, float)

class SignalWaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(82)
        self.setMaximumHeight(110)
        self.setStyleSheet("background:transparent;")
        self.samples_up: List[float] = [0.0] * 200
        self.samples_down: List[float] = [0.0] * 200
        self.samples_cpu: List[float] = [0.0] * 200

    def update_wave(self, up: float, down: float, cpu: float):
        self.samples_up = self.samples_up[1:] + [up]
        self.samples_down = self.samples_down[1:] + [down]
        self.samples_cpu = self.samples_cpu[1:] + [cpu]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        painter.fillRect(self.rect(), QColor(28, 30, 34, 72))
        max_up = max(self.samples_up) if max(self.samples_up) > 0.15 else 0.15
        max_down = max(self.samples_down) if max(self.samples_down) > 0.15 else 0.15
        max_cpu = max(self.samples_cpu) if max(self.samples_cpu) > 10 else 10
        max_val = max(max_up, max_down, max_cpu)
        grad_up = QLinearGradient(0, 0, 0, h)
        grad_up.setColorAt(0, QColor(0, 255, 140, 180))
        grad_up.setColorAt(1, QColor(0, 90, 70, 60))
        grad_down = QLinearGradient(0, 0, 0, h)
        grad_down.setColorAt(0, QColor(50, 110, 255, 180))
        grad_down.setColorAt(1, QColor(55, 52, 100, 60))
        grad_cpu = QLinearGradient(0, 0, 0, h)
        grad_cpu.setColorAt(0, QColor(255, 200, 45, 170))
        grad_cpu.setColorAt(1, QColor(110, 74, 0, 60))
        pen_up = QPen(QColor(0, 255, 140), 2)
        pen_down = QPen(QColor(50, 110, 255), 2)
        pen_cpu = QPen(QColor(255, 210, 60), 2)
        painter.setPen(QColor(120, 120, 120, 25))
        for i in range(0, w, max(1, w // 12)):
            painter.drawLine(i, 0, i, h)
        for i in range(0, h, max(1, h // 6)):
            painter.drawLine(0, i, w, i)
        path_up = []
        for i, v in enumerate(self.samples_up):
            x = int(i * w / len(self.samples_up))
            y = int(h - (v / max_val) * (h - 15) - 7)
            path_up.append(QPointF(x, y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad_up)
        polygon_up = path_up + [QPointF(w, h), QPointF(0, h)]
        painter.drawPolygon(*polygon_up)
        path_down = []
        for i, v in enumerate(self.samples_down):
            x = int(i * w / len(self.samples_down))
            y = int(h - (v / max_val) * (h - 15) - 7)
            path_down.append(QPointF(x, y))
        painter.setBrush(grad_down)
        polygon_down = path_down + [QPointF(w, h), QPointF(0, h)]
        painter.drawPolygon(*polygon_down)
        path_cpu = []
        for i, v in enumerate(self.samples_cpu):
            x = int(i * w / len(self.samples_cpu))
            y = int(h - (v / max_val) * (h - 15) - 7)
            path_cpu.append(QPointF(x, y))
        painter.setBrush(grad_cpu)
        polygon_cpu = path_cpu + [QPointF(w, h), QPointF(0, h)]
        painter.drawPolygon(*polygon_cpu)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen_up)
        for i in range(1, len(path_up)):
            painter.drawLine(path_up[i-1], path_up[i])
        painter.setPen(pen_down)
        for i in range(1, len(path_down)):
            painter.drawLine(path_down[i-1], path_down[i])
        painter.setPen(pen_cpu)
        for i in range(1, len(path_cpu)):
            painter.drawLine(path_cpu[i-1], path_cpu[i])

class ESPOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.mode_statuses = {
            "Teleport": False
        }
        self.dragging = False
        self.drag_position = None
        self.setFixedWidth(110)
        self.setFixedHeight(26)
        self.init_ui()

    def init_ui(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        height = 26
        width = 110
        self.setGeometry(screen_geometry.width() - width - 20, 12, width, height)

    def update_statuses(self, mode_states):
        self.mode_statuses = mode_states
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 160))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 6, 6)
        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)
        y_pos = self.height() // 2 + 4
        for mode, status in self.mode_statuses.items():
            text = f"{mode}: {'ON' if status else 'OFF'}"
            color = QColor(50, 255, 50) if status else QColor(255, 80, 80)
            text_width = painter.fontMetrics().horizontalAdvance(text)
            x_pos = self.width() / 2 - (text_width / 2)
            painter.setPen(color)
            painter.drawText(int(x_pos), y_pos, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = self.mapToParent(event.position().toPoint() - self.drag_position)
            screen_geo = QApplication.primaryScreen().geometry()
            new_x = max(0, min(new_pos.x(), screen_geo.width() - self.width()))
            new_y = max(0, min(new_pos.y(), screen_geo.height() - self.height()))
            self.move(new_x, new_y)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def leaveEvent(self, event):
        if not self.dragging:
            self.setCursor(Qt.CursorShape.ArrowCursor)

class AudioManager:
    def __init__(self, config):
        self.config = config

    def play_beep(self, frequency=500, duration=300):
        if not self.config.audio_enabled:
            return
        def beep_thread():
            try:
                winsound.Beep(frequency, duration)
            except Exception:
                pass
        threading.Thread(target=beep_thread, daemon=True).start()

    def play_toggle_on(self):
        self.play_beep(600, 200)

    def play_toggle_off(self):
        self.play_beep(400, 300)

class ModernHotkeyManager:
    ALLOWED_KEYS = {
        **{f"f{i}": f"F{i}" for i in range(1, 13) if i != 10},
        **{str(i): str(i) for i in range(0, 10)},
        **{chr(i): chr(i).upper() for i in range(ord('a'), ord('z') + 1)},
        'space': 'SPACE', 'tab': 'TAB', 'enter': 'ENTER', 'shift': 'SHIFT',
        'ctrl': 'CTRL', 'alt': 'ALT', 'insert': 'INSERT', 'delete': 'DELETE',
        'home': 'HOME', 'end': 'END', 'page up': 'PAGE UP', 'page down': 'PAGE DOWN',
        'up': '↑', 'down': '↓', 'left': '←', 'right': '→'
    }
    FORBIDDEN_KEYS = {'f10', 'esc', 'windows', 'menu'}

    def __init__(self, signals, config):
        self.signals = signals
        self.config = config
        self.capture_active = False
        self.capture_timeout = None
        self.registered_hooks: Set[str] = set()

    def is_key_allowed(self, key: str) -> bool:
        key_lower = key.lower()
        return (key_lower in self.ALLOWED_KEYS and key_lower not in self.FORBIDDEN_KEYS)

    def normalize_key(self, key: str) -> str:
        key_lower = key.lower()
        return self.ALLOWED_KEYS.get(key_lower, key.upper())

    def start_capture(self, timeout: float = 10.0) -> bool:
        if self.capture_active:
            return False
        self.capture_active = True
        def auto_stop():
            time.sleep(timeout)
            if self.capture_active:
                self.stop_capture()
                self.signals.update_status.emit("⏰ Timeout - Không nhận được hotkey", "warning")
        self.capture_timeout = threading.Thread(target=auto_stop, daemon=True)
        self.capture_timeout.start()
        return True

    def stop_capture(self):
        self.capture_active = False

    def try_set_hotkey(self, key: str) -> bool:
        if not self.capture_active:
            return False
        if not self.is_key_allowed(key):
            forbidden_msg = {
                'f10': "❌ F10 dành cho thoát chương trình",
                'esc': "❌ ESC không được phép",
                'windows': "❌ Windows key không được phép",
                'menu': "❌ Menu key không được phép"
            }
            self.signals.update_status.emit(forbidden_msg.get(key.lower(), "❌ Phím không được phép"), "error")
            return False
        self.unregister_current_hotkey()
        self.config.hotkey.key = key.lower()
        self.config.hotkey.display_name = self.normalize_key(key)
        self.config.hotkey.is_valid = True
        self.register_hotkey()
        self._update_ui_after_set()
        self.save_config()
        self.stop_capture()
        return True

    def _update_ui_after_set(self):
        self.signals.update_hotkey.emit(self.config.hotkey.display_name)
        self.signals.update_status.emit(f"✅ Hotkey: {self.config.hotkey.display_name}", "success")

    def register_hotkey(self):
        if not self.config.hotkey.is_valid:
            return
        try:
            keyboard.add_hotkey(self.config.hotkey.key, toggle_tele, suppress=True)
            self.registered_hooks.add(self.config.hotkey.key)
        except Exception:
            pass

    def unregister_current_hotkey(self):
        for hotkey in self.registered_hooks.copy():
            try:
                keyboard.remove_hotkey(hotkey)
                self.registered_hooks.remove(hotkey)
            except:
                pass

    def save_config(self):
        try:
            config_data = {
                "hotkey": self.config.hotkey.key,
                "display_name": self.config.hotkey.display_name,
                "audio_enabled": self.config.audio_enabled,
                "version": "2.1"
            }
            with open(HOTKEY_FILE, "w", encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def load_config(self) -> bool:
        if not os.path.exists(HOTKEY_FILE):
            return False
        try:
            with open(HOTKEY_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
            key = data.get("hotkey", "")
            if key and self.is_key_allowed(key):
                self.config.hotkey.key = key
                self.config.hotkey.display_name = data.get("display_name", self.normalize_key(key))
                self.config.hotkey.is_valid = True
                self.config.audio_enabled = data.get("audio_enabled", True)
                self._update_ui_after_set()
                self.register_hotkey()
                return True
        except Exception:
            pass
        return False

class GreenCheckStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PrimitiveElement.PE_IndicatorCheckBox:
            opt = QStyleOptionButton(option)
            rect = opt.rect
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor("#404040"), 2)
            if opt.state & QStyle.StateFlag.State_MouseOver:
                pen.setColor(QColor("#00dd77") if opt.state & QStyle.StateFlag.State_On else QColor("#606060"))
            if opt.state & QStyle.StateFlag.State_On:
                pen.setColor(QColor("#00ff88"))
            painter.setPen(pen)
            painter.setBrush(QColor("#2b2b2b"))
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 3, 3)
            if opt.state & QStyle.StateFlag.State_On:
                painter.setPen(QPen(QColor("#00ff88"), 2))
                x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                painter.drawLine(int(x + w*0.25), int(y + h*0.55), int(x + w*0.45), int(y + h*0.75))
                painter.drawLine(int(x + w*0.45), int(y + h*0.75), int(x + w*0.75), int(y + h*0.33))
            painter.restore()
        else:
            super().drawPrimitive(element, option, painter, widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = StatusSignals()
        self.network_stats = NetworkStats()
        self.app_config = AppConfig(hotkey=HotkeyConfig(), audio_enabled=True)
        self.audio_manager = AudioManager(self.app_config)
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_network_stats)
        self.stats_timer.start(800)
        self.selected_pid = None
        self.pid_items = []
        self.current_filter = None
        self.filter_dirty = True
        self.init_ui()
        self.init_globals()
        self.connect_signals()
        self.init_overlay()
        self.start_backend()
        self.session_packets_sent = 0
        self.session_bytes_sent = 0
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()
        self.last_recv = self.last_net.bytes_recv
        self.last_sent = self.last_net.bytes_sent

    def init_ui(self):
        self.setWindowTitle("⚡ Teleport v2.1 Pro")
        self.setFixedSize(480, 360)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #141622, stop:0.5 #1a1f2b, stop:1 #0f111a);
                color: white;
                border: 1px solid #2b2e3b;
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: bold;
                font-size: 11px;
                color: #eafef7;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e2b2a, stop:1 #17333a);
                box-shadow: 0px 0px 10px rgba(0,255,160,0.15);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #244240, stop:1 #1d4650);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #143332, stop:1 #14323a);
            }
            QCheckBox {
                color: white;
                background: transparent;
                font-size: 10px;
                spacing: 8px;
            }
            QComboBox {
                background: rgba(255,255,255,0.04);
                border: 1px solid #2f3442;
                border-radius: 8px;
                padding: 6px 8px;
                color: #e6f4ff;
                selection-background-color: #0ea57a;
            }
            QComboBox QAbstractItemView {
                background: #151826;
                color: #e6f4ff;
                selection-background-color: #0ea57a;
                selection-color: #0b0d13;
                border: 1px solid #2f3442;
            }
        """)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(6)
        title_label = QLabel("⚡ Teleport v2.1 Pro")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #00f2a6; margin-bottom: 4px;")
        main_layout.addWidget(title_label)
        proc_row = QHBoxLayout()
        proc_label = QLabel("Process:")
        proc_label.setStyleSheet("color:#9bb0c9")
        self.process_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.populate_process_list)
        self.process_combo.currentIndexChanged.connect(self.on_process_selected)
        proc_row.addWidget(proc_label)
        proc_row.addWidget(self.process_combo, 1)
        proc_row.addWidget(self.refresh_btn)
        main_layout.addLayout(proc_row)
        self.hotkey_btn = QPushButton("Click để set hotkey")
        self.hotkey_btn.clicked.connect(self.start_hotkey_capture)
        main_layout.addWidget(self.hotkey_btn)
        self.audio_checkbox = QCheckBox("🔊 Bật tắt tiếng beep")
        self.audio_checkbox.setChecked(self.app_config.audio_enabled)
        self.audio_checkbox.stateChanged.connect(self.on_audio_checkbox_changed)
        main_layout.addWidget(self.audio_checkbox)
        self.signal_wave = SignalWaveWidget()
        main_layout.addWidget(self.signal_wave)
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: rgba(14, 20, 30, 0.45);
                border: 1px solid #2b2e3b;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(3)
        stats_layout.setContentsMargins(6, 4, 6, 4)
        self.packet_held_label = QLabel("Held: 0")
        self.packet_held_label.setFont(QFont("Consolas", 8))
        self.packet_held_label.setStyleSheet("color: #ff6b6b;")
        self.packet_sent_label = QLabel("Sent: 0")
        self.packet_sent_label.setFont(QFont("Consolas", 8))
        self.packet_sent_label.setStyleSheet("color: #51cf66;")
        self.total_processed_label = QLabel("Total: 0")
        self.total_processed_label.setFont(QFont("Consolas", 8))
        self.total_processed_label.setStyleSheet("color: #74c0fc;")
        self.bytes_held_label = QLabel("B.Held: 0")
        self.bytes_held_label.setFont(QFont("Consolas", 8))
        self.bytes_held_label.setStyleSheet("color: #ffd43b;")
        self.bytes_sent_label = QLabel("B.Sent: 0")
        self.bytes_sent_label.setFont(QFont("Consolas", 8))
        self.bytes_sent_label.setStyleSheet("color: #ff922b;")
        self.network_usage_label = QLabel("Net: 0 KB/s")
        self.network_usage_label.setFont(QFont("Consolas", 8))
        self.network_usage_label.setStyleSheet("color: #d0bfff;")
        self.speed_up_label = QLabel("Up: 0 KB/s")
        self.speed_up_label.setFont(QFont("Consolas", 8))
        self.speed_up_label.setStyleSheet("color: #7cffd9;")
        self.speed_down_label = QLabel("Down: 0 KB/s")
        self.speed_down_label.setFont(QFont("Consolas", 8))
        self.speed_down_label.setStyleSheet("color: #b197fc;")
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setFont(QFont("Consolas", 8))
        self.cpu_label.setStyleSheet("color: #fab005;")
        row = 0
        stats_layout.addWidget(self.packet_held_label, row, 0)
        stats_layout.addWidget(self.packet_sent_label, row, 1)
        stats_layout.addWidget(self.total_processed_label, row, 2)
        row += 1
        stats_layout.addWidget(self.bytes_held_label, row, 0)
        stats_layout.addWidget(self.bytes_sent_label, row, 1)
        stats_layout.addWidget(self.network_usage_label, row, 2)
        row += 1
        stats_layout.addWidget(self.speed_up_label, row, 0)
        stats_layout.addWidget(self.speed_down_label, row, 1)
        stats_layout.addWidget(self.cpu_label, row, 2)
        main_layout.addWidget(stats_frame)
        self.status_label = QLabel("Status: Ready — No process selected")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setStyleSheet("color: #93a0b4; padding: 4px;")
        main_layout.addWidget(self.status_label)
        self.populate_process_list()

    def init_globals(self):
        global tele_mode, packet_tele, lock, running, app_state, hotkey_manager
        tele_mode = False
        packet_tele = []
        lock = threading.Lock()
        running = True
        app_state = AppState.IDLE
        hotkey_manager = ModernHotkeyManager(self.signals, self.app_config)

    def init_overlay(self):
        self.overlay = ESPOverlay()
        self.overlay.show()

    def connect_signals(self):
        self.signals.update_packet_count.connect(self.update_packet_count)
        self.signals.update_hotkey.connect(self.update_hotkey_display)
        self.signals.update_button_state.connect(self.update_button_state)
        self.signals.update_overlay_status.connect(self.update_overlay_status)
        self.signals.update_network_stats.connect(self.update_network_stats_display)
        self.signals.update_signal_wave.connect(self.signal_wave.update_wave)
        self.signals.update_status.connect(self.update_status)

    def start_backend(self):
        keyboard.hook(self.handle_global_key)
        keyboard.add_hotkey('f10', self.force_exit, suppress=True)
        hotkey_manager.load_config()
        self.audio_checkbox.setChecked(self.app_config.audio_enabled)
        threading.Thread(target=self.divert_tele, daemon=True).start()

    def on_audio_checkbox_changed(self, state):
        self.app_config.audio_enabled = state == Qt.CheckState.Checked.value
        hotkey_manager.save_config()
        if self.app_config.audio_enabled:
            self.audio_manager.play_beep(800, 150)

    def update_status(self, message, status_type):
        self.status_label.setText(f"Status: {message}")

    def populate_process_list(self):
        try:
            current_pid = self.selected_pid
            self.process_combo.blockSignals(True)
            self.process_combo.clear()
            items = []
            for proc in psutil.process_iter(["pid", "name"]):
                name = proc.info.get("name") or "unknown.exe"
                pid = proc.info.get("pid")
                items.append((name.lower(), f"{name} (PID {pid})", pid))
            items.sort(key=lambda t: t[0])
            self.pid_items = [(label, pid) for _, label, pid in items]
            for label, _pid in self.pid_items:
                self.process_combo.addItem(label)
            if current_pid:
                # Try to reselect previous pid
                for i, (_, pid) in enumerate(self.pid_items):
                    if pid == current_pid:
                        self.process_combo.setCurrentIndex(i)
                        break
            self.process_combo.blockSignals(False)
            self.on_process_selected(self.process_combo.currentIndex())
        except Exception:
            pass

    def on_process_selected(self, idx):
        try:
            if idx < 0 or idx >= len(self.pid_items):
                self.selected_pid = None
                self.status_label.setText("Status: Ready — No process selected")
            else:
                label, pid = self.pid_items[idx]
                self.selected_pid = pid
                self.status_label.setText(f"Status: Ready — Target: {label}")
            # Mark filter to be rebuilt
            self.filter_dirty = True
        except Exception:
            pass

    def update_packet_count(self, count):
        self.network_stats.packets_held = count
        with lock:
            self.network_stats.bytes_held = sum(len(pkt.raw) for pkt in packet_tele)
        self.signals.update_network_stats.emit(self.network_stats)

    def update_hotkey_display(self, hotkey_name):
        self.hotkey_btn.setText(f"Hotkey: {hotkey_name}")

    def update_button_state(self, is_on):
        self.signals.update_overlay_status.emit({"Teleport": is_on})

    def update_overlay_status(self, status_dict):
        self.overlay.update_statuses(status_dict)

    def update_network_stats(self):
        try:
            net_io = psutil.net_io_counters()
            now = time.time()
            elapsed = now - self.last_time if hasattr(self, "last_time") else 1.0
            up_speed = (net_io.bytes_sent - self.last_sent) / elapsed
            down_speed = (net_io.bytes_recv - self.last_recv) / elapsed
            up_kb = up_speed / 1024
            down_kb = down_speed / 1024
            self.last_sent = net_io.bytes_sent
            self.last_recv = net_io.bytes_recv
            self.last_time = now
            self.network_stats.upload_speed = up_kb
            self.network_stats.download_speed = down_kb
            self.network_stats.network_usage = up_kb + down_kb
            self.network_stats.cpu_percent = psutil.cpu_percent(interval=None)
            self.signals.update_network_stats.emit(self.network_stats)
            self.signals.update_signal_wave.emit(self.network_stats.upload_speed, self.network_stats.download_speed, self.network_stats.cpu_percent)
        except:
            pass

    def update_network_stats_display(self, stats):
        self.packet_held_label.setText(f"Held: {stats.packets_held}")
        self.packet_sent_label.setText(f"Sent: {self.session_packets_sent}")
        self.total_processed_label.setText(f"Total: {stats.total_processed}")
        self.bytes_held_label.setText(f"B.Held: {self.format_bytes(stats.bytes_held)}")
        self.bytes_sent_label.setText(f"B.Sent: {self.format_bytes(self.session_bytes_sent)}")
        self.network_usage_label.setText(f"Net: {stats.network_usage:.2f} KB/s")
        self.speed_up_label.setText(f"Up: {stats.upload_speed:.2f} KB/s")
        self.speed_down_label.setText(f"Down: {stats.download_speed:.2f} KB/s")
        self.cpu_label.setText(f"CPU: {stats.cpu_percent:.1f}%")

    def format_bytes(self, bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val}B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val/1024:.1f}K"
        else:
            return f"{bytes_val/(1024*1024):.1f}M"

    def toggle_tele(self):
        global tele_mode, app_state, packet_tele
        if not hotkey_manager.config.hotkey.is_valid:
            return
        if app_state == AppState.WAITING_FOR_HOTKEY:
            return
        if tele_mode:
            with lock:
                tele_mode = False
                to_send = list(packet_tele)
                packet_tele.clear()
                app_state = AppState.IDLE
            self.signals.update_button_state.emit(False)
            self.audio_manager.play_toggle_off()
            def send_bursts():
                try:
                    sent_count = 0
                    bytes_sent = 0
                    with pydivert.WinDivert("outbound", layer=pydivert.Layer.NETWORK) as sender:
                        for pkt in to_send:
                            try:
                                pkt_size = len(pkt.raw)
                                pkt_rebuilt = pydivert.Packet(pkt.raw, pkt.interface, pkt.direction)
                                sender.send(pkt_rebuilt)
                                sent_count += 1
                                bytes_sent += pkt_size
                                time.sleep(random.uniform(0.00508, 0.00525))
                            except:
                                pass
                    self.session_packets_sent = sent_count
                    self.session_bytes_sent = bytes_sent
                    self.network_stats.packets_sent = sent_count
                    self.network_stats.bytes_sent = bytes_sent
                    self.network_stats.total_processed += sent_count
                    self.signals.update_packet_count.emit(0)
                    self.signals.update_network_stats.emit(self.network_stats)
                except Exception:
                    pass
            if to_send:
                threading.Thread(target=send_bursts, daemon=True).start()
            else:
                self.session_packets_sent = 0
                self.session_bytes_sent = 0
                self.signals.update_packet_count.emit(0)
        else:
            with lock:
                tele_mode = True
                packet_tele.clear()
                app_state = AppState.CAPTURING_PACKETS
            self.session_packets_sent = 0
            self.session_bytes_sent = 0
            self.signals.update_button_state.emit(True)
            self.audio_manager.play_toggle_on()
            self.signals.update_network_stats.emit(self.network_stats)

    def start_hotkey_capture(self):
        global app_state
        if app_state == AppState.WAITING_FOR_HOTKEY:
            return
        app_state = AppState.WAITING_FOR_HOTKEY
        self.hotkey_btn.setText("Nhấn phím...")
        if hotkey_manager.start_capture(timeout=15.0):
            pass
        else:
            app_state = AppState.IDLE

    def handle_global_key(self, event):
        global app_state
        if not running:
            return
        key = event.name.lower()
        if app_state == AppState.WAITING_FOR_HOTKEY and event.event_type == keyboard.KEY_DOWN:
            if hotkey_manager.try_set_hotkey(key):
                app_state = AppState.IDLE
            return
        if key == "f10" and event.event_type == keyboard.KEY_DOWN:
            self.force_exit()

    def build_filter(self):
        base = FILTER_BASE
        if self.selected_pid:
            return f"{base} and processId == {int(self.selected_pid)}"
        return base

    def divert_tele(self):
        global tele_mode, packet_tele, running
        try:
            while running:
                try:
                    self.current_filter = self.build_filter()
                    self.filter_dirty = False
                    with pydivert.WinDivert(self.current_filter) as w:
                        for packet in w:
                            if not running:
                                break
                            if self.filter_dirty:
                                # Rebuild handle with new filter
                                break
                            with lock:
                                if tele_mode:
                                    packet_tele.append(packet)
                                    self.network_stats.total_processed += 1
                                    self.signals.update_packet_count.emit(len(packet_tele))
                                    continue
                            try:
                                w.send(packet)
                            except:
                                pass
                except Exception:
                    time.sleep(0.1)
                    continue
        except Exception:
            pass

    def force_exit(self):
        global running
        running = False
        hotkey_manager.unregister_current_hotkey()
        if hasattr(self, 'overlay'):
            self.overlay.close()
        if hasattr(self, 'stats_timer'):
            self.stats_timer.stop()
        QApplication.quit()

    def closeEvent(self, event):
        self.force_exit()
        event.accept()

def toggle_tele():
    if hasattr(window, 'toggle_tele'):
        window.toggle_tele()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(GreenCheckStyle())
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        window.force_exit()
    except Exception:
        window.force_exit()