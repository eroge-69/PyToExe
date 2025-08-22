
import sys
import os
import time
import threading
import socket
import configparser
import base64
import ctypes
import ctypes.wintypes as wintypes

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDialog,
    QSpinBox, QColorDialog, QFormLayout,
    QGroupBox, QMessageBox, QMenu, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QClipboard

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# ----------------------------
# Security helpers (Windows DPAPI)
# ----------------------------

def _is_windows():
    return os.name == "nt"

def _dpapi_protect(data: bytes) -> bytes:
    if not _is_windows():
        return data
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
    CryptProtectData = ctypes.windll.crypt32.CryptProtectData
    CryptProtectData.argtypes = [ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR, ctypes.POINTER(DATA_BLOB),
                                 ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    CryptProtectData.restype = wintypes.BOOL

    in_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_char)))
    out_blob = DATA_BLOB()
    if not CryptProtectData(ctypes.byref(in_blob), "binance_api", None, None, None, 0, ctypes.byref(out_blob)):
        raise OSError("DPAPI protect failed")
    try:
        protected = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return protected
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)

def _dpapi_unprotect(data: bytes) -> bytes:
    if not _is_windows():
        return data
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.POINTER(wintypes.LPWSTR), ctypes.POINTER(DATA_BLOB),
                                   ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
    CryptUnprotectData.restype = wintypes.BOOL

    in_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_char)))
    out_blob = DATA_BLOB()
    if not CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        raise OSError("DPAPI unprotect failed")
    try:
        unprotected = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return unprotected
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)

def protect_text(text: str) -> str:
    try:
        enc = _dpapi_protect(text.encode("utf-8"))
        return "DPAPI:" + base64.b64encode(enc).decode("ascii")
    except Exception:
        # Fallback to base64 (not secure, but avoids crashes on non-Windows)
        return "PLAIN:" + base64.b64encode(text.encode("utf-8")).decode("ascii")

def unprotect_text(text: str) -> str:
    try:
        if text.startswith("DPAPI:"):
            raw = base64.b64decode(text[6:])
            return _dpapi_unprotect(raw).decode("utf-8")
        if text.startswith("PLAIN:"):
            return base64.b64decode(text[6:]).decode("utf-8")
        return text
    except Exception:
        return ""

# ----------------------------
# Network helpers
# ----------------------------

def has_internet(host="8.8.8.8", port=53, timeout=2.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

# ----------------------------
# Settings Dialog
# ----------------------------

class SettingsDialog(QDialog):
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки оверлея")
        self.setGeometry(200, 200, 460, 820)

        layout = QVBoxLayout()

        # API group
        api_group = QGroupBox("API Настройки")
        api_layout = QFormLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Введите ваш API ключ")
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setPlaceholderText("Введите ваш секретный ключ")
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        api_layout.addRow("API Ключ:", self.api_key_input)
        api_layout.addRow("Секретный ключ:", self.api_secret_input)

        # Info label and wallet copy button
        self.info_label = QLabel("ℹ️ Программа полностью бесплатная, но я с радостью приму подарок.")
        self.info_label.setWordWrap(True)
        api_layout.addRow(self.info_label)

        wallet = "0x1ea179e669e2347d43d53a79aba4e8b539d478ce"
        wallet_layout = QHBoxLayout()
        self.wallet_label = QLabel(wallet)
        self.wallet_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_btn = QPushButton("🎁 Копировать")
        self.copy_btn.clicked.connect(lambda: self.copy_to_clipboard(wallet))
        wallet_layout.addWidget(self.wallet_label, 1)
        wallet_layout.addWidget(self.copy_btn, 0)
        api_layout.addRow("Кошелёк:", wallet_layout)

        # Telegram contact (below wallet)
        tg_layout = QHBoxLayout()
        self.tg_label = QLabel("@TinoAyato1")
        self.tg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_tg_btn = QPushButton("📨 Копировать")
        self.copy_tg_btn.clicked.connect(lambda: self.copy_to_clipboard("@TinoAyato1"))
        tg_layout.addWidget(self.tg_label, 1)
        tg_layout.addWidget(self.copy_tg_btn, 0)
        api_layout.addRow("Telegram:", tg_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Display group
        display_group = QGroupBox("Настройки отображения")
        display_layout = QFormLayout()

        self.show_balance_chk = QCheckBox()
        self.show_balance_chk.setChecked(True)
        display_layout.addRow("Показывать баланс:", self.show_balance_chk)

        self.click_through_chk = QCheckBox()
        self.click_through_chk.setChecked(True)
        display_layout.addRow("Прозрачность для кликов (поверх игр):", self.click_through_chk)

        self.balance_font_size = QSpinBox()
        self.balance_font_size.setRange(8, 72)
        self.balance_font_size.setValue(24)
        display_layout.addRow("Размер шрифта баланса:", self.balance_font_size)

        self.balance_color_btn = QPushButton("Выбрать цвет")
        self.balance_color_btn.clicked.connect(lambda: self.choose_color("balance"))
        display_layout.addRow("Цвет баланса:", self.balance_color_btn)
        self.balance_color = QColor("#00FF00")

        self.positions_font_size = QSpinBox()
        self.positions_font_size.setRange(8, 36)
        self.positions_font_size.setValue(16)
        display_layout.addRow("Размер шрифта позиций:", self.positions_font_size)

        self.profit_color_btn = QPushButton("Выбрать цвет")
        self.profit_color_btn.clicked.connect(lambda: self.choose_color("profit"))
        display_layout.addRow("Цвет прибыли:", self.profit_color_btn)
        self.profit_color = QColor("#00FF00")

        self.loss_color_btn = QPushButton("Выбрать цвет")
        self.loss_color_btn.clicked.connect(lambda: self.choose_color("loss"))
        display_layout.addRow("Цвет убытка:", self.loss_color_btn)
        self.loss_color = QColor("#FF0000")

        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 60)
        self.refresh_interval.setValue(15)
        self.refresh_interval.setSuffix(" сек")
        display_layout.addRow("Частота обновления:", self.refresh_interval)

        self.transparency = QSpinBox()
        self.transparency.setRange(10, 100)
        self.transparency.setValue(100)
        self.transparency.setSuffix("%")
        display_layout.addRow("Прозрачность окна:", self.transparency)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить и применить")
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Load existing settings if provided
        if existing:
            self.api_key_input.setText(existing.get("api_key", ""))
            self.api_secret_input.setText(existing.get("api_secret", ""))
            self.show_balance_chk.setChecked(existing.get("show_balance", True))
            self.click_through_chk.setChecked(existing.get("click_through", True))
            self.balance_font_size.setValue(existing.get("balance_font_size", 24))
            self.positions_font_size.setValue(existing.get("positions_font_size", 16))
            self.refresh_interval.setValue(existing.get("refresh_interval", 15))
            self.transparency.setValue(existing.get("transparency", 100))
            self.balance_color = QColor(existing.get("balance_color", "#00FF00"))
            self.profit_color = QColor(existing.get("profit_color", "#00FF00"))
            self.loss_color = QColor(existing.get("loss_color", "#FF0000"))

    def choose_color(self, color_type):
        color_dialog = QColorDialog(self)
        if color_type == "balance":
            color = color_dialog.getColor(self.balance_color)
            if color.isValid():
                self.balance_color = color
        elif color_type == "profit":
            color = color_dialog.getColor(self.profit_color)
            if color.isValid():
                self.profit_color = color
        elif color_type == "loss":
            color = color_dialog.getColor(self.loss_color)
            if color.isValid():
                self.loss_color = color

    def copy_to_clipboard(self, text):
        cb: QClipboard = QApplication.clipboard()
        cb.setText(text)
        QMessageBox.information(self, "Скопировано", f"«{text}» скопирован в буфер обмена!")

    def get_settings(self):
        return {
            "api_key": self.api_key_input.text().strip(),
            "api_secret": self.api_secret_input.text().strip(),
            "show_balance": self.show_balance_chk.isChecked(),
            "click_through": self.click_through_chk.isChecked(),
            "balance_font_size": self.balance_font_size.value(),
            "positions_font_size": self.positions_font_size.value(),
            "balance_color": self.balance_color.name(),
            "profit_color": self.profit_color.name(),
            "loss_color": self.loss_color.name(),
            "refresh_interval": self.refresh_interval.value(),
            "transparency": self.transparency.value(),
        }

# ----------------------------
# Overlay Window
# ----------------------------

class TransparentOverlay(QMainWindow):
    safe_update_signal = pyqtSignal()

    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon
        self.client = None
        self.balance = "0.00"
        self.positions = []
        self.settings = {}
        self.refresh_interval = 15
        self.stop_event = threading.Event()
        self.last_display_snapshot = ""

        self.init_ui()
        self.load_config()

        # Background data thread
        self.update_thread = threading.Thread(target=self.update_data_loop, daemon=True)
        self.update_thread.start()

        # UI update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display_if_changed)
        self.timer.start(500)

        self.safe_update_signal.connect(self.update_display_if_changed)

    def init_ui(self):
        self.setWindowTitle("Binance Overlay")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.SplashScreen  # helps stay over some full-screen contexts
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Center widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Balance label
        self.balance_label = QLabel("Загрузка...")
        self.balance_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.balance_label)

        # Positions container
        self.positions_container = QWidget()
        self.positions_layout = QVBoxLayout(self.positions_container)
        self.positions_layout.setAlignment(Qt.AlignTop)
        self.positions_layout.setContentsMargins(0, 5, 0, 0)
        self.positions_layout.setSpacing(3)
        self.layout.addWidget(self.positions_container)

        self.setGeometry(50, 50, 320, 160)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Text shadow effect
        self.text_shadow = QGraphicsDropShadowEffect()
        self.text_shadow.setBlurRadius(3)
        self.text_shadow.setColor(QColor(0, 0, 0, 180))
        self.text_shadow.setOffset(1, 1)

        # Force topmost over (most) full-screen apps/games on Windows
        if _is_windows():
            QTimer.singleShot(1000, self._force_topmost)
            self.topmost_timer = QTimer(self)
            self.topmost_timer.timeout.connect(self._force_topmost)
            self.topmost_timer.start(2000)

    def _force_topmost(self):
        if not _is_windows():
            return
        try:
            import win32con, win32gui
            hwnd = int(self.winId())
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        except Exception:
            # Fallback via ctypes
            try:
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                ctypes.windll.user32.SetWindowPos(int(self.winId()), HWND_TOPMOST, 0, 0, 0, 0,
                                                  SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
            except Exception:
                pass

    def _make_click_through(self):
        if not _is_windows():
            return
        try:
            import win32con, win32gui
            hwnd = int(self.winId())
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        except Exception:
            # Fallback via ctypes
            try:
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_LAYERED = 0x00080000
                hwnd = int(self.winId())
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ex_style |= WS_EX_TRANSPARENT | WS_EX_LAYERED
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
            except Exception:
                pass

    def _remove_click_through(self):
        if not _is_windows():
            return
        try:
            import win32con, win32gui
            hwnd = int(self.winId())
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style &= ~win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        except Exception:
            try:
                GWL_EXSTYLE = -20
                WS_EX_TRANSPARENT = 0x00000020
                hwnd = int(self.winId())
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ex_style &= ~WS_EX_TRANSPARENT
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
            except Exception:
                pass

    def show_context_menu(self, pos):
        menu = QMenu(self)
        settings_action = menu.addAction("Настройки")
        toggle_balance_action = menu.addAction("Показывать баланс" if not self.settings.get("show_balance", True) else "Скрыть баланс")
        toggle_click_action = menu.addAction("Отключить click-through" if self.settings.get("click_through", True) else "Включить click-through")
        hide_action = menu.addAction("Свернуть в трей")
        exit_action = menu.addAction("Выход")

        action = menu.exec_(self.mapToGlobal(pos))
        if action == settings_action:
            self.open_settings()
        elif action == toggle_balance_action:
            self.settings["show_balance"] = not self.settings.get("show_balance", True)
            self.save_config_settings()
            self.apply_settings()
        elif action == toggle_click_action:
            self.settings["click_through"] = not self.settings.get("click_through", True)
            self.save_config_settings()
            self.apply_settings()
        elif action == hide_action:
            self.hide_to_tray()
        elif action == exit_action:
            QApplication.quit()

    def hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage("Losь", "Программа свернута в системный трей",
                                   QSystemTrayIcon.Information, 2000)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    # --------------- Config ---------------

    def _config_path(self):
        # Store config next to executable if frozen, otherwise cwd
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.getcwd()
        return os.path.join(base, "overlay_config.ini")

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self._config_path()):
            config.read(self._config_path(), encoding="utf-8")
            # API
            api_key_enc = config.get("API", "key", fallback="")
            api_secret_enc = config.get("API", "secret", fallback="")
            api_key = unprotect_text(api_key_enc) if api_key_enc else ""
            api_secret = unprotect_text(api_secret_enc) if api_secret_enc else ""
            # Display
            self.settings = {
                "show_balance": config.getboolean("Display", "show_balance", fallback=True),
                "click_through": config.getboolean("Display", "click_through", fallback=True),
                "balance_font_size": config.getint("Display", "balance_font_size", fallback=24),
                "positions_font_size": config.getint("Display", "positions_font_size", fallback=16),
                "balance_color": config.get("Display", "balance_color", fallback="#00FF00"),
                "profit_color": config.get("Display", "profit_color", fallback="#00FF00"),
                "loss_color": config.get("Display", "loss_color", fallback="#FF0000"),
                "refresh_interval": config.getint("Display", "refresh_interval", fallback=15),
                "transparency": config.getint("Display", "transparency", fallback=100),
                "api_key": api_key,
                "api_secret": api_secret,
            }
            self.refresh_interval = self.settings["refresh_interval"]
            self.apply_settings()
            if api_key and api_secret:
                self._init_client(api_key, api_secret)

    def save_config_settings(self, new_api=None):
        config = configparser.ConfigParser()
        cfg_path = self._config_path()
        if os.path.exists(cfg_path):
            config.read(cfg_path, encoding="utf-8")

        api_key = self.settings.get("api_key", "")
        api_secret = self.settings.get("api_secret", "")
        if new_api:
            api_key = new_api.get("api_key", api_key)
            api_secret = new_api.get("api_secret", api_secret)
        config["API"] = {
            "key": protect_text(api_key) if api_key else "",
            "secret": protect_text(api_secret) if api_secret else "",
        }

        disp = {
            "show_balance": str(self.settings.get("show_balance", True)),
            "click_through": str(self.settings.get("click_through", True)),
            "balance_font_size": str(self.settings.get("balance_font_size", 24)),
            "positions_font_size": str(self.settings.get("positions_font_size", 16)),
            "balance_color": self.settings.get("balance_color", "#00FF00"),
            "profit_color": self.settings.get("profit_color", "#00FF00"),
            "loss_color": self.settings.get("loss_color", "#FF0000"),
            "refresh_interval": str(self.settings.get("refresh_interval", 15)),
            "transparency": str(self.settings.get("transparency", 100)),
        }
        config["Display"] = disp

        with open(cfg_path, "w", encoding="utf-8") as f:
            config.write(f)

    def apply_settings(self):
        if not self.settings:
            return
        self.setWindowOpacity(self.settings.get("transparency", 100) / 100.0)
        self.refresh_interval = int(self.settings.get("refresh_interval", 15))

        balance_font = QFont()
        balance_font.setPointSize(self.settings.get("balance_font_size", 24))
        balance_font.setBold(True)
        self.balance_label.setFont(balance_font)
        self.balance_label.setStyleSheet(f"color: {self.settings.get('balance_color', '#00FF00')}; background-color: transparent;")
        self.balance_label.setGraphicsEffect(self.text_shadow)
        self.balance_label.setVisible(self.settings.get("show_balance", True))

        # Apply click-through
        if self.settings.get("click_through", True):
            self._make_click_through()
        else:
            self._remove_click_through()

        self.update_display_if_changed()

    def open_settings(self):
        existing = {
            "api_key": self.settings.get("api_key", ""),
            "api_secret": self.settings.get("api_secret", ""),
            "show_balance": self.settings.get("show_balance", True),
            "click_through": self.settings.get("click_through", True),
            "balance_font_size": self.settings.get("balance_font_size", 24),
            "positions_font_size": self.settings.get("positions_font_size", 16),
            "refresh_interval": self.settings.get("refresh_interval", 15),
            "transparency": self.settings.get("transparency", 100),
            "balance_color": self.settings.get("balance_color", "#00FF00"),
            "profit_color": self.settings.get("profit_color", "#00FF00"),
            "loss_color": self.settings.get("loss_color", "#FF0000"),
        }
        dialog = SettingsDialog(self, existing=existing)
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update({
                "show_balance": new_settings["show_balance"],
                "click_through": new_settings["click_through"],
                "balance_font_size": new_settings["balance_font_size"],
                "positions_font_size": new_settings["positions_font_size"],
                "balance_color": new_settings["balance_color"],
                "profit_color": new_settings["profit_color"],
                "loss_color": new_settings["loss_color"],
                "refresh_interval": new_settings["refresh_interval"],
                "transparency": new_settings["transparency"],
                "api_key": new_settings["api_key"] or self.settings.get("api_key", ""),
                "api_secret": new_settings["api_secret"] or self.settings.get("api_secret", ""),
            })
            self.save_config_settings(new_api={"api_key": new_settings["api_key"], "api_secret": new_settings["api_secret"]})
            if new_settings["api_key"] and new_settings["api_secret"]:
                self._init_client(new_settings["api_key"], new_settings["api_secret"])
            self.apply_settings()

    # --------------- Binance / Data ---------------

    def _init_client(self, api_key, api_secret):
        try:
            self.client = Client(api_key, api_secret)
            # Test quick call
            _ = self.client.futures_account_balance()
        except Exception as e:
            self.client = None
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к Binance: {e}")

    def update_data_loop(self):
        backoff = 1
        while not self.stop_event.is_set():
            if not self.client:
                time.sleep(min(backoff, 60))
                backoff = min(backoff * 2, 60)
                api_key = self.settings.get("api_key", "")
                api_secret = self.settings.get("api_secret", "")
                if api_key and api_secret and has_internet():
                    self._init_client(api_key, api_secret)
                continue

            try:
                if not has_internet():
                    raise ConnectionError("Нет соединения с интернетом")

                # Balance
                balances = self.client.futures_account_balance()
                bal_val = None
                for asset in balances:
                    if asset.get("asset") == "USDT":
                        bal_val = float(asset.get("balance", 0.0))
                        break
                self.balance = f"{bal_val:.2f}" if bal_val is not None else "0.00"

                # Positions
                positions = self.client.futures_position_information()
                new_positions = []
                for pos in positions:
                    try:
                        amount = float(pos.get("positionAmt", 0.0))
                        if amount == 0:
                            continue
                        symbol = pos.get("symbol", "?")
                        entry_price = float(pos.get("entryPrice", 0.0))
                        mark_price = float(pos.get("markPrice", 0.0))

                        pnl_usd = (mark_price - entry_price) * abs(amount) if amount > 0 else (entry_price - mark_price) * abs(amount)
                        pnl_percent = ((mark_price - entry_price) / entry_price * 100.0) if entry_price > 0 else 0.0
                        if amount < 0:
                            pnl_percent = -pnl_percent

                        new_positions.append({
                            "symbol": symbol,
                            "pnl_usd": pnl_usd,
                            "pnl_percent": pnl_percent
                        })
                    except Exception:
                        continue
                self.positions = new_positions

                backoff = 1

            except (ConnectionError, BinanceAPIException, BinanceRequestException, OSError) as e:
                self.balance = "Error"
                self.positions = []
                if not isinstance(e, (ConnectionError, OSError)):
                    self.client = None
                time.sleep(min(backoff, 60))
                backoff = min(backoff * 2, 60)
            except Exception:
                time.sleep(2)

            time.sleep(max(1, int(self.refresh_interval)))
            self.safe_update_signal.emit()

    def _build_snapshot_text(self):
        parts = []
        if self.settings.get("show_balance", True):
            parts.append(f"Баланс: {self.balance} USDT")
        for pos in self.positions:
            symbol = pos["symbol"]
            pnl_usd = pos["pnl_usd"]
            pnl_percent = pos["pnl_percent"]
            sign = "+" if pnl_usd >= 0 else ""
            parts.append(f"{symbol}: {sign}{pnl_usd:.2f} USDT ({sign}{pnl_percent:.2f}%)")
        return "\n".join(parts)

    def update_display_if_changed(self):
        snapshot = self._build_snapshot_text()
        if snapshot == self.last_display_snapshot:
            return
        self.last_display_snapshot = snapshot
        self.update_display()

    def update_display(self):
        # Balance
        if self.settings.get("show_balance", True):
            self.balance_label.setText(f"Баланс: {self.balance} USDT")
            self.balance_label.setVisible(True)
        else:
            self.balance_label.setVisible(False)

        # Clear previous position labels
        for i in reversed(range(self.positions_layout.count())):
            widget = self.positions_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        for pos in self.positions:
            symbol = pos["symbol"]
            pnl_usd = pos["pnl_usd"]
            pnl_percent = pos["pnl_percent"]
            color = self.settings.get("profit_color", "#00FF00") if pnl_usd >= 0 else self.settings.get("loss_color", "#FF0000")
            sign = "+" if pnl_usd >= 0 else ""

            lbl = QLabel(f"{symbol}: {sign}{pnl_usd:.2f} USDT ({sign}{pnl_percent:.2f}%)")
            lbl.setAlignment(Qt.AlignCenter)

            f = QFont()
            f.setPointSize(self.settings.get("positions_font_size", 16))
            lbl.setFont(f)
            lbl.setStyleSheet(f"color: {color}; background-color: transparent;")
            lbl.setGraphicsEffect(self.text_shadow)
            self.positions_layout.addWidget(lbl)

        self.adjustSize()

    # --------------- Cleanup ---------------

    def closeEvent(self, event):
        self.stop_event.set()
        return super().closeEvent(event)

# ----------------------------
# Tray wrapper
# ----------------------------

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.tray_icon = QSystemTrayIcon()
        # Use icon.ico if present
        icon_path = "icon.ico"
        self.tray_icon.setIcon(QIcon(icon_path) if os.path.exists(icon_path) else QIcon())
        self.tray_menu = QMenu()
        self.show_action = self.tray_menu.addAction("Показать оверлей")
        self.show_action.triggered.connect(self.show_overlay)
        self.settings_action = self.tray_menu.addAction("Настройки")
        self.settings_action.triggered.connect(self.show_settings)
        self.toggle_balance_action = self.tray_menu.addAction("Скрыть баланс")
        self.toggle_balance_action.triggered.connect(self.toggle_balance)
        self.toggle_click_action = self.tray_menu.addAction("Отключить click-through")
        self.toggle_click_action.triggered.connect(self.toggle_click_through)
        self.exit_action = self.tray_menu.addAction("Выход")
        self.exit_action.triggered.connect(self.exit_app)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.overlay = TransparentOverlay(self.tray_icon)
        self.overlay.show()
        if self.overlay.settings.get("click_through", True):
            self.overlay._make_click_through()
        self.tray_icon.show()

        self._sync_tray_texts()

    def _sync_tray_texts(self):
        show = self.overlay.settings.get("show_balance", True)
        self.toggle_balance_action.setText("Скрыть баланс" if show else "Показывать баланс")
        ct = self.overlay.settings.get("click_through", True)
        self.toggle_click_action.setText("Отключить click-through" if ct else "Включить click-through")

    def toggle_balance(self):
        cur = self.overlay.settings.get("show_balance", True)
        self.overlay.settings["show_balance"] = not cur
        self.overlay.save_config_settings()
        self.overlay.apply_settings()
        self._sync_tray_texts()

    def toggle_click_through(self):
        cur = self.overlay.settings.get("click_through", True)
        self.overlay.settings["click_through"] = not cur
        self.overlay.save_config_settings()
        self.overlay.apply_settings()
        self._sync_tray_texts()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_overlay()

    def show_overlay(self):
        self.overlay.show()
        self.overlay.activateWindow()

    def show_settings(self):
        self.overlay.open_settings()
        self._sync_tray_texts()

    def exit_app(self):
        self.tray_icon.hide()
        self.overlay.stop_event.set()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

# ----------------------------
# Entry point
# ----------------------------

if __name__ == "__main__":
    cfg = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), "overlay_config.ini")
    if not os.path.exists(cfg):
        app = QApplication(sys.argv)
        dialog = SettingsDialog()
        if dialog.exec_() == QDialog.Accepted:
            s = dialog.get_settings()
            config = configparser.ConfigParser()
            config["API"] = {
                "key": protect_text(s["api_key"]) if s["api_key"] else "",
                "secret": protect_text(s["api_secret"]) if s["api_secret"] else "",
            }
            config["Display"] = {
                "show_balance": str(s["show_balance"]),
                "click_through": str(s["click_through"]),
                "balance_font_size": str(s["balance_font_size"]),
                "positions_font_size": str(s["positions_font_size"]),
                "balance_color": s["balance_color"],
                "profit_color": s["profit_color"],
                "loss_color": s["loss_color"],
                "refresh_interval": str(s["refresh_interval"]),
                "transparency": str(s["transparency"]),
            }
            with open(cfg, "w", encoding="utf-8") as f:
                config.write(f)
        else:
            sys.exit(0)

    tray_app = TrayApp()
    tray_app.run()
