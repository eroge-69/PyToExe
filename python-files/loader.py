# loader.py
# SwiftDLC launcher (PyQt5) — полный файл с изменениями:
# - args.txt теперь содержит --enable-native-access=ALL-UNNAMED
# - тема по умолчанию светло-зелёно-черная + опция light
# - тема применятся сразу после сохранения в настройках
# - логирование classpath, фильтрация guava (оставляем последнюю)
# - screenshot загружается по URL
# - настройка RAM (GB), Java path сохраняются

from __future__ import annotations
import sys
import os
import json
import time
import shutil
import logging
import threading
import subprocess
from zipfile import ZipFile
from typing import List, Optional, Tuple
import requests

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QLineEdit, QDialog, QTextEdit,
    QFileDialog, QMessageBox, QSpinBox, QFormLayout, QGroupBox, QFrame, QComboBox
)
from PyQt5.QtGui import QPixmap, QFont, QDesktopServices
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QUrl

# -----------------------
# Configuration - edit if needed
# -----------------------
CLIENT_DIR = r"C:\penjs"
CLIENT_ZIP_URL = "https://dl.dropboxusercontent.com/scl/fi/6fmf6u1dm1gyst0cnadxq/SwiftDLC.zip?rlkey=cs2yi2lti95kw2ukbwzwin3t1"
CLIENT_ZIP_PATH = r"C:\penjs\SwiftDlc.zip"
GAME_DIR = r"C:\penjs"
GAME_VERSION = "1.16.5"
CONFIG_PATH = "config.json"
LOG_FILE = "launcher.log"
EXTRACTION_MARKER = ".extracted_ok"

# Screenshot image URL (replace with your Imgur or other link)
IMAGE_URL = "https://get.wallhere.com/photo/Minecraft-water-Sky-game-2223480.jpg"

# Required artifacts relative to game dir
REQUIRED_PATHS = [
    os.path.join("swiftdlc", "game", "versions", GAME_VERSION, f"{GAME_VERSION}.jar"),
    os.path.join("swiftdlc", "libraries")  # должен содержать jars
]

# -----------------------
# Logging
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SwiftDLCLauncher")

# -----------------------
# Utilities
# -----------------------
def is_windows() -> bool:
    return sys.platform.startswith("win")

def abspath(p: str) -> str:
    try:
        return os.path.abspath(p)
    except Exception:
        return p

def add_long_path_prefix(path: str) -> str:
    """
    On Windows prefix \\?\ to avoid MAX_PATH issues when writing files.
    Note: Not all Windows API calls accept \\?\ for command invocation.
    Here it's used for file IO (open, mkdir, remove).
    """
    if not is_windows():
        return path
    p = abspath(path)
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p.lstrip("\\")
    return "\\\\?\\" + p

def safe_makedirs(path: str):
    try:
        if is_windows():
            os.makedirs(add_long_path_prefix(path), exist_ok=True)
        else:
            os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.debug(f"safe_makedirs fallback: {e}")
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e2:
            logger.error(f"safe_makedirs failed: {e2}")

def safe_remove_dir(path: str):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.error(f"safe_remove_dir error: {e}")

def count_files_in_archive(zip_path: str) -> int:
    try:
        with ZipFile(zip_path, "r") as z:
            return sum(1 for n in z.namelist() if not n.endswith("/"))
    except Exception as e:
        logger.error(f"count_files_in_archive: {e}")
        return 0

def count_files_in_folder(root_dir: str) -> int:
    total = 0
    for _, _, files in os.walk(root_dir):
        total += len(files)
    return total

def find_java_executable(client_dir: str = CLIENT_DIR) -> Optional[str]:
    """Try to find java in bundled jre, JAVA_HOME, or PATH."""
    try:
        if os.path.isdir(client_dir):
            for entry in os.listdir(client_dir):
                if entry.lower().startswith("jre") or entry.lower().startswith("jdk"):
                    candidate = os.path.join(client_dir, entry, "bin", "java.exe" if is_windows() else "java")
                    if os.path.exists(candidate):
                        logger.info(f"Found bundled java: {candidate}")
                        return candidate
    except Exception:
        pass
    java_home = os.environ.get("JAVA_HOME") or os.environ.get("JDK_HOME")
    if java_home:
        candidate = os.path.join(java_home, "bin", "java.exe" if is_windows() else "java")
        if os.path.exists(candidate):
            logger.info(f"Found java in JAVA_HOME: {candidate}")
            return candidate
    from shutil import which
    w = which("java")
    if w:
        logger.info(f"Found java in PATH: {w}")
        return w
    logger.warning("Java not found")
    return None

# -----------------------
# Download & Extract helpers (synchronous functions used in threads)
# -----------------------
def download_file(url: str, dest_path: str, progress_callback=None, status_callback=None, timeout=60) -> bool:
    """Download with streaming; call progress_callback(percent) and status_callback(message)."""
    try:
        safe_makedirs(os.path.dirname(dest_path))
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0) or 0)
            downloaded = 0
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and progress_callback:
                        try:
                            progress_callback(int(downloaded / total * 100))
                        except Exception:
                            pass
        if status_callback:
            status_callback("Download complete")
        logger.info(f"Downloaded: {url} -> {dest_path}")
        return True
    except Exception as e:
        logger.exception(f"download_file error: {e}")
        if status_callback:
            status_callback(f"Download failed: {e}")
        return False

def extract_zip_manual(zip_path: str, target_dir: str, progress_callback=None, status_callback=None) -> bool:
    """Extract zip entry-by-entry, writing with add_long_path_prefix on Windows."""
    try:
        with ZipFile(zip_path, "r") as z:
            members = z.infolist()
            total = len(members) or 1
            extracted = 0
            for idx, member in enumerate(members, start=1):
                name = member.filename
                name_norm = name.replace("/", os.sep).replace("\\", os.sep)
                target_path = os.path.normpath(os.path.join(target_dir, name_norm))
                parent = os.path.dirname(target_path)
                if parent:
                    safe_makedirs(parent)
                if name_norm.endswith(os.sep):
                    # directory
                    continue
                try:
                    with z.open(member, "r") as src, open(add_long_path_prefix(target_path), "wb") as dst:
                        shutil.copyfileobj(src, dst)
                except Exception as e:
                    logger.debug(f"Primary extract failed for {name}: {e}")
                    try:
                        with z.open(member, "r") as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                    except Exception as e2:
                        logger.error(f"Failed to extract {name}: {e2}")
                extracted += 1
                if progress_callback:
                    try:
                        progress_callback(int(extracted / total * 100))
                    except Exception:
                        pass
                if status_callback:
                    try:
                        status_callback(f"Extracting {idx}/{total}")
                    except Exception:
                        pass
        # write marker
        try:
            marker = os.path.join(target_dir, EXTRACTION_MARKER)
            with open(add_long_path_prefix(marker), "w", encoding="utf-8") as m:
                m.write("ok")
        except Exception:
            pass
        logger.info(f"Extracted archive {zip_path} -> {target_dir}")
        return True
    except Exception as e:
        logger.exception(f"extract_zip_manual error: {e}")
        return False

# -----------------------
# Helper: guava version parsing and filtering
# -----------------------
def _extract_version_tuple_from_name(name: str) -> Tuple[int, ...]:
    import re
    m = re.search(r"guava-([0-9]+(?:\.[0-9]+)*)", name, flags=re.IGNORECASE)
    if not m:
        return (0,)
    ver = m.group(1)
    parts = ver.split('.')
    tup = []
    for p in parts:
        try:
            tup.append(int(p))
        except Exception:
            tup.append(0)
    return tuple(tup)

def _filter_guava_keep_latest(jars: List[str]) -> List[str]:
    guavas = [j for j in jars if "guava-" in os.path.basename(j).lower()]
    if not guavas:
        return jars
    
    sorted_guavas = sorted(guavas, 
                          key=lambda p: _extract_version_tuple_from_name(os.path.basename(p)), 
                          reverse=True)
    
    latest = sorted_guavas[0] if sorted_guavas else guavas[0]
    
    jars = [j for j in jars if "guava-" not in os.path.basename(j).lower()]
    jars.append(latest)
    
    logger.info(f"Guava jars found: {len(guavas)} files; using: {os.path.basename(latest)}")
    return jars

# -----------------------
# Signals object for thread->GUI communication
# -----------------------
class Signals(QObject):
    status = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)  # success, message

# -----------------------
# Themes (green/dark default + light)
# -----------------------
THEMES = {
    "dark_green": """
        QWidget { background-color: #07140b; color: #e8fdf0; font-family: "Segoe UI", Arial; }
        QLabel#title { font-size: 24px; font-weight: 700; color: #bbf7d0; }
        QLabel#version { color: #86efac; font-weight: 600; }
        QFrame.panel { background-color: #0b1f16; border-radius: 12px; }
        QPushButton.small { background-color: #0f2b20; border-radius: 8px; padding: 6px 10px; }
        QPushButton.small:hover { background-color: #153826; }
        QPushButton.launch { background-color: #22c55e; color: white; border-radius: 12px; font-size: 18px; padding: 12px 20px; }
        QPushButton.launch:hover { background-color: #16a34a; }
        QProgressBar { background-color: #0b1f16; border-radius: 6px; text-align: center; }
        QProgressBar::chunk { background-color: #4ade80; border-radius: 6px; }
        QLabel#small { color: #a7f3d0; }
    """,
    "light": """
        QWidget { background-color: #f7fdf8; color: #072018; font-family: "Segoe UI", Arial; }
        QLabel#title { font-size: 24px; font-weight: 700; color: #065f46; }
        QLabel#version { color: #067f52; font-weight: 600; }
        QFrame.panel { background-color: #eef7ee; border-radius: 12px; }
        QPushButton.small { background-color: #d8f8e0; border-radius: 8px; padding: 6px 10px; }
        QPushButton.small:hover { background-color: #bff1c7; }
        QPushButton.launch { background-color: #10b981; color: white; border-radius: 12px; font-size: 18px; padding: 12px 20px; }
        QPushButton.launch:hover { background-color: #059669; }
        QProgressBar { background-color: #eef7ee; border-radius: 6px; text-align: center; }
        QProgressBar::chunk { background-color: #10b981; border-radius: 6px; }
        QLabel#small { color: #0f766e; }
    """
}

# -----------------------
# Main Window
# -----------------------
class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SwiftDLC Launcher")
        # load config
        self.config = self._load_config()
        self.username = self.config.get("username", "Player")
        self.memory_gb = int(self.config.get("memory_gb", 4))
        self.auth_key = self.config.get("auth_key", "")
        self.java_path = self.config.get("java_path", None) or find_java_executable()
        self.theme = self.config.get("theme", "dark_green")

        # subscription active flag (active if key applied at least once)
        self.sub_active = bool(self.auth_key)

        # signals
        self.signals = Signals()
        self.signals.status.connect(self.on_status)
        self.signals.progress.connect(self.on_progress)
        self.signals.finished.connect(self.on_finished_task)

        # UI
        self._init_ui()

        # background lock
        self._bg_lock = threading.Lock()

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Load config failed: {e}")
                return {}
        return {}

    def _save_config(self):
        try:
            cfg = {
                "username": self.username,
                "memory_gb": self.memory_gb,
                "auth_key": self.auth_key,
                "java_path": self.java_path,
                "theme": self.theme
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            logger.info("Config saved")
        except Exception as e:
            logger.error(f"Save config error: {e}")

    def apply_theme(self):
        # apply stylesheet for selected theme
        style = THEMES.get(self.theme, THEMES["dark_green"])
        try:
            self.setStyleSheet(style)
        except Exception as e:
            logger.error(f"apply_theme failed: {e}")

    def _init_ui(self):
        """
        Новый UI: фиксированное окно 960x600, светло-зелено-черная тема по умолчанию.
        """
        # window size & base style
        self.setFixedSize(960, 600)
        self.apply_theme()

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(18)
        central.setLayout(root)

        # ---------- LEFT COLUMN ----------
        left_col = QVBoxLayout()
        left_col.setSpacing(14)
        root.addLayout(left_col, 1)

        # Header block (title + version)
        header = QVBoxLayout()
        title_lbl = QLabel("SwiftDLC")
        title_lbl.setObjectName("title")
        title_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.addWidget(title_lbl)

        version_lbl = QLabel(f"Minecraft <span style='color:#86efac; font-weight:600;'>{GAME_VERSION}</span>")
        version_lbl.setObjectName("version")
        version_lbl.setFont(QFont("Segoe UI", 11))
        header.addWidget(version_lbl)

        left_col.addLayout(header)

        # Description (panel)
        desc_frame = QFrame()
        desc_frame.setObjectName("panel")
        desc_layout = QVBoxLayout()
        desc_layout.setContentsMargins(12, 12, 12, 12)
        desc_frame.setLayout(desc_layout)
        desc = QLabel("Modern client with asset manager. Use Launch to start the client (access key required). "
                      "Includes verify/reinstall, settings and logging. The launcher handles downloads and extraction.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        desc_layout.addWidget(desc)
        left_col.addWidget(desc_frame)

        # Inline controls: progress + status
        prog_frame = QFrame()
        prog_frame.setObjectName("panel")
        prog_layout = QVBoxLayout()
        prog_layout.setContentsMargins(12, 10, 12, 10)
        prog_frame.setLayout(prog_layout)

        # progress bar & label
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        prog_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("0%")
        self.progress_label.setObjectName("small")
        self.progress_label.setStyleSheet("font-size: 12px;")
        prog_layout.addWidget(self.progress_label)

        # status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setObjectName("small")
        self.status_label.setStyleSheet("font-size: 12px;")
        prog_layout.addWidget(self.status_label)

        left_col.addWidget(prog_frame)

        # Buttons area (Verify / Logs / Settings)
        btns_frame = QFrame()
        btns_frame.setObjectName("panel")
        btns_layout = QHBoxLayout()
        btns_layout.setContentsMargins(10, 10, 10, 10)
        btns_layout.setSpacing(8)
        btns_frame.setLayout(btns_layout)

        self.btn_verify = QPushButton("Verify / Reinstall")
        self.btn_verify.setProperty("class", "small")
        self.btn_verify.setFixedHeight(36)
        self.btn_verify.clicked.connect(self.on_verify_clicked)
        btns_layout.addWidget(self.btn_verify)

        self.btn_logs = QPushButton("Open Logs")
        self.btn_logs.setProperty("class", "small")
        self.btn_logs.setFixedHeight(36)
        self.btn_logs.clicked.connect(self.on_open_logs)
        btns_layout.addWidget(self.btn_logs)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setProperty("class", "small")
        self.btn_settings.setFixedHeight(36)
        self.btn_settings.clicked.connect(self.on_open_settings)
        btns_layout.addWidget(self.btn_settings)

        left_col.addWidget(btns_frame)

        # Account / Subscription block
        acc_frame = QFrame()
        acc_frame.setObjectName("panel")
        acc_layout = QHBoxLayout()
        acc_layout.setContentsMargins(12, 10, 12, 10)
        acc_frame.setLayout(acc_layout)

        self.user_display = QLabel(f"👤 <b>{self.username}</b>")
        self.user_display.setStyleSheet("font-size: 13px;")
        acc_layout.addWidget(self.user_display)

        acc_layout.addStretch(1)

        # subscription active/inactive
        self.sub_display = QLabel()
        self._update_subscription_label()
        self.sub_display.setStyleSheet("font-size: 13px;")
        acc_layout.addWidget(self.sub_display)

        left_col.addWidget(acc_frame)

        # Socials block - only Telegram
        socials_frame = QFrame()
        socials_frame.setObjectName("panel")
        socials_layout = QHBoxLayout()
        socials_layout.setContentsMargins(12, 8, 12, 8)
        socials_layout.setSpacing(8)
        socials_frame.setLayout(socials_layout)

        btn_tg = QPushButton("Telegram @swiftdlc")
        btn_tg.setFixedHeight(34)
        btn_tg.setProperty("class", "small")
        btn_tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/swiftdlc")))
        socials_layout.addWidget(btn_tg)

        left_col.addWidget(socials_frame)

        # spacer to push left column items to top
        left_col.addStretch(1)

        # ---------- RIGHT COLUMN ----------
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        root.addLayout(right_col, 1)

        # Large image panel - load from IMAGE_URL
        img_frame = QFrame()
        img_frame.setObjectName("panel")
        img_layout = QVBoxLayout()
        img_layout.setContentsMargins(12, 12, 12, 12)
        img_frame.setLayout(img_layout)

        self.img_label = QLabel()
        self.img_label.setFixedSize(520, 300)
        # background color adjusted by theme stylesheet
        self.img_label.setStyleSheet("border-radius: 12px; background-color: rgba(0,0,0,0.12);")
        self.img_label.setAlignment(Qt.AlignCenter)

        # Try load from URL
        try:
            resp = requests.get(IMAGE_URL, timeout=8)
            if resp.status_code == 200:
                pix = QPixmap()
                if pix.loadFromData(resp.content):
                    pix = pix.scaled(self.img_label.width(), self.img_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.img_label.setPixmap(pix)
                else:
                    self.img_label.setText("Screenshot\n(520x300)")
            else:
                self.img_label.setText("Screenshot\n(520x300)")
        except Exception as e:
            logger.info(f"Failed to load image from URL: {e}")
            # fallback to local screenshot.jpg or placeholder
            if os.path.exists("screenshot.jpg"):
                try:
                    pix = QPixmap("screenshot.jpg").scaled(self.img_label.width(), self.img_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.img_label.setPixmap(pix)
                except Exception:
                    self.img_label.setText("Screenshot\n(520x300)")
            else:
                self.img_label.setText("Screenshot\n(520x300)")

        img_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        right_col.addWidget(img_frame)

        # Middle info row (news)
        info_frame = QFrame()
        info_frame.setObjectName("panel")
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_frame.setLayout(info_layout)

        news_lbl = QLabel("Latest: Launcher UI redesigned — fixed-size modern look.")
        news_lbl.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(news_lbl)

        right_col.addWidget(info_frame)

        right_col.addStretch(1)

        # Launch button area (centered horizontally)
        launch_hbox = QHBoxLayout()
        launch_hbox.addStretch(1)
        self.btn_launch = QPushButton("▶ Launch")
        self.btn_launch.setObjectName("btn_launch")
        self.btn_launch.setProperty("class", "launch")
        self.btn_launch.setFixedSize(300, 64)
        self.btn_launch.clicked.connect(self.on_launch_clicked)
        launch_hbox.addWidget(self.btn_launch)
        launch_hbox.addStretch(1)
        right_col.addLayout(launch_hbox)

        # Bottom status bar (small)
        bottom_frame = QFrame()
        bottom_frame.setObjectName("panel")
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(10, 8, 10, 8)
        bottom_frame.setLayout(bottom_layout)

        bottom_left = QLabel(f"User: <b>{self.username}</b>")
        bottom_left.setStyleSheet("font-size: 12px;")
        bottom_layout.addWidget(bottom_left)

        bottom_layout.addStretch(1)
        self.statusBar().showMessage("Ready")

    # -----------------------
    # Helpers / UI updates
    # -----------------------
    def _update_subscription_label(self):
        txt = "Subscription: <span style='color:#34d399; font-weight:600;'>Active</span>" if self.sub_active else "Subscription: <span style='color:#f87171; font-weight:600;'>Inactive</span>"
        self.sub_display.setText(txt)

    # -----------------------
    # UI slots
    # -----------------------
    def on_status(self, message: str):
        logger.info(message)
        try:
            self.status_label.setText(f"Status: {message}")
        except Exception:
            pass
        self.statusBar().showMessage(message)

    def on_progress(self, percent: int):
        try:
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"{percent}%")
        except Exception:
            pass

    def on_finished_task(self, success: bool, message: str):
        if success:
            QMessageBox.information(self, "Task Finished", message)
        else:
            QMessageBox.critical(self, "Task Error", message)
        try:
            self.progress_bar.setValue(0)
            self.progress_label.setText("0%")
        except Exception:
            pass

    # -----------------------
    # Buttons handlers
    # -----------------------
    def on_open_logs(self):
        if is_windows():
            try:
                subprocess.Popen(["notepad.exe", LOG_FILE])
            except Exception as e:
                QMessageBox.warning(self, "Open Logs", f"Cannot open logs: {e}")
        else:
            QMessageBox.information(self, "Open Logs", f"Log file: {os.path.abspath(LOG_FILE)}")

    def on_open_settings(self):
        dlg = SettingsDialog(self, self.username, self.memory_gb, self.java_path, self.theme)
        if dlg.exec_():
            # apply settings
            self.username, self.memory_gb, self.java_path, self.theme = dlg.get_values()
            self._save_config()
            self.on_status_emit("Settings saved")
            # update bottom display and user display
            try:
                self.user_display.setText(f"👤 <b>{self.username}</b>")
            except Exception:
                pass
            # apply theme immediately
            try:
                self.apply_theme()
            except Exception as e:
                logger.error(f"Failed to apply theme: {e}")

    def on_verify_clicked(self):
        # show modal with options
        dlg = VerifyDialog(self)
        if dlg.exec_():
            if dlg.action == "verify":
                self._background(self.verify_client)
            elif dlg.action == "reinstall":
                self._background(self.reinstall_client)

    def on_launch_clicked(self):
        if not self.auth_key:
            # prompt for key
            dlg = KeyDialog(self)
            if dlg.exec_():
                self.auth_key = dlg.get_key()
                # save
                self.config["auth_key"] = self.auth_key
                self._save_config()
                self.sub_active = bool(self.auth_key)
                self._update_subscription_label()
        self._background(self.launch_procedure)

    # -----------------------
    # Background wrappers and status helpers
    # -----------------------
    def on_status_emit(self, text: str):
        self.signals.status.emit(text)

    def on_progress_emit(self, value: int):
        self.signals.progress.emit(value)

    def on_finished_emit(self, ok: bool, msg: str):
        self.signals.finished.emit(ok, msg)

    def _background(self, target, *args, **kwargs):
        """Run target in a daemon thread and catch exceptions."""
        def wrapper():
            try:
                target(*args, **kwargs)
            except Exception as e:
                logger.exception("Background task exception")
                self.on_status_emit(f"Error: {e}")
                self.on_finished_emit(False, str(e))
        t = threading.Thread(target=wrapper, daemon=True)
        t.start()

    # -----------------------
    # Verification and reinstall flows
    # -----------------------
    def verify_client(self):
        self.on_status_emit("Verifying client...")
        if os.path.exists(CLIENT_ZIP_PATH):
            archive_count = count_files_in_archive(CLIENT_ZIP_PATH)
            folder_count = count_files_in_folder(CLIENT_DIR) if os.path.isdir(CLIENT_DIR) else 0
            self.on_status_emit(f"Archive files: {archive_count}, installed: {folder_count}")
            if folder_count >= archive_count:
                self.on_finished_emit(True, "Verification OK")
            else:
                self.on_finished_emit(False, "Client incomplete vs archive")
        else:
            self.on_finished_emit(False, "No archive available for verification")

    def reinstall_client(self):
        self.on_status_emit("Reinstall: removing old client and downloading archive...")
        safe_remove_dir(CLIENT_DIR)
        try:
            if os.path.exists(CLIENT_ZIP_PATH):
                os.remove(CLIENT_ZIP_PATH)
        except Exception:
            pass
        # download and extract
        ok = download_file(CLIENT_ZIP_URL, CLIENT_ZIP_PATH, progress_callback=self.on_progress_emit, status_callback=self.on_status_emit)
        if not ok:
            self.on_finished_emit(False, "Download failed")
            return
        ok = extract_zip_manual(CLIENT_ZIP_PATH, CLIENT_DIR, progress_callback=self.on_progress_emit, status_callback=self.on_status_emit)
        if not ok:
            self.on_finished_emit(False, "Extraction failed")
            return
        self.on_finished_emit(True, "Reinstall complete")

    # -----------------------
    # Launch flow: check files -> restore from zip or download -> build args & launch
    # -----------------------
    def _check_required_files(self) -> List[str]:
        missing = []
        details = []
        for rel in REQUIRED_PATHS:
            # if the required path mentions "libraries", check libraries presence under GAME_DIR
            if rel.endswith(("swiftdlc", "game", "libraries")):
                # build the path as it's expected relative to GAME_DIR
                p = os.path.join(GAME_DIR, "swiftdlc", "game", "libraries")
                if not os.path.isdir(p):
                    missing.append(p)
                    details.append(f"Missing directory: {p}")
                else:
                    # check that at least one .jar exists inside libraries
                    found = False
                    for root, _, files in os.walk(p):
                        for fn in files:
                            if fn.endswith(".jar"):
                                found = True
                                break
                        if found:
                            break
                    if not found:
                        missing.append(p + " (no jars)")
                        details.append(f"No .jar files found under: {p}")
            else:
                # general file existence check relative to GAME_DIR
                p = os.path.join(GAME_DIR, rel)
                if not os.path.exists(p):
                    missing.append(p)
                    details.append(f"Missing path: {p}")

        # always ensure version jar exists (explicit check to be safe)
        version_jar = os.path.join(GAME_DIR, "swiftdlc", "game", "versions", GAME_VERSION, f"{GAME_VERSION}.jar")
        if not os.path.exists(version_jar):
            missing.append(version_jar)
            details.append(f"Missing version jar: {version_jar}")

        if missing:
            logger.error(f"Missing files: {missing}")
            # log detail lines as well
            for d in details:
                logger.error(d)
        return missing

    def launch_procedure(self):
        with self._bg_lock:
            self.on_status_emit("Preparing launch...")
            missing = self._check_required_files()
            if missing:
                self.on_status_emit(f"Missing {len(missing)} items. Trying to restore...")
                # try extract from local zip if present
                if os.path.exists(CLIENT_ZIP_PATH):
                    ok = extract_zip_manual(CLIENT_ZIP_PATH, CLIENT_DIR, progress_callback=self.on_progress_emit, status_callback=self.on_status_emit)
                    if not ok:
                        self.on_finished_emit(False, "Extraction from local archive failed")
                        return
                else:
                    # download archive
                    ok = download_file(CLIENT_ZIP_URL, CLIENT_ZIP_PATH, progress_callback=self.on_progress_emit, status_callback=self.on_status_emit)
                    if not ok:
                        self.on_finished_emit(False, "Download failed")
                        return
                    ok = extract_zip_manual(CLIENT_ZIP_PATH, CLIENT_DIR, progress_callback=self.on_progress_emit, status_callback=self.on_status_emit)
                    if not ok:
                        self.on_finished_emit(False, "Extraction failed")
                        return
                # re-check after extraction
                missing2 = self._check_required_files()
                if missing2:
                    # include the list of missing files in the error message so user sees what exactly is missing
                    msg = f"Still missing {len(missing2)} items after extraction:\n" + "\n".join(missing2)
                    logger.error(msg)
                    self.on_finished_emit(False, msg)
                    return
            else:
                self.on_status_emit("All required files present")

            # Build classpath list
            jars = []
            libraries_dir = os.path.join(GAME_DIR, "swiftdlc", "game", "libraries")
            if os.path.isdir(libraries_dir):
                for root, _, files in os.walk(libraries_dir):
                    for fn in files:
                        if fn.endswith(".jar"):
                            jars.append(os.path.join(root, fn))
            version_jar = os.path.join(GAME_DIR, "swiftdlc", "game", "versions", GAME_VERSION, f"{GAME_VERSION}.jar")
            if os.path.exists(version_jar):
                jars.append(version_jar)
            # include client jars too
            if os.path.isdir(CLIENT_DIR):
                for root, _, files in os.walk(CLIENT_DIR):
                    for fn in files:
                        if fn.endswith(".jar"):
                            jars.append(os.path.join(root, fn))

            # Log all jars found
            logger.info("Collected classpath jars:")
            for j in jars:
                logger.info(f"  {j}")

            # Show guava jars and keep latest one only
            jars = _filter_guava_keep_latest(jars)

            classpath = os.pathsep.join(jars)
            # write args file
            args_path = os.path.join(GAME_DIR, "args.txt")
            safe_makedirs(os.path.dirname(args_path))
            try:
                with open(args_path, "w", encoding="utf-8") as af:
                    # memory
                    af.write(f"-Xmx{int(self.memory_gb)*1024}m\n")
                    # enable native access for newer JDKs (removes restricted method warnings)
                    af.write("--enable-native-access=ALL-UNNAMED\n")
                    af.write("-cp\n")
                    af.write(classpath + "\n")
                    af.write("net.minecraft.client.main.Main\n")
                    af.write(f"--version {GAME_VERSION}\n")
                    af.write(f"--gameDir {GAME_DIR}\n")
                    af.write(f"--assetsDir {os.path.join(GAME_DIR, 'swiftdlc', 'game', 'assets')}\n")
                    af.write("--assetIndex 1.16\n")
                    af.write(f"--username {self.username}\n")
                    af.write("--accessToken 0\n")
                self.on_status_emit("args.txt written")
            except Exception as e:
                logger.exception("Failed to write args.txt")
                self.on_finished_emit(False, f"Failed to write args.txt: {e}")
                return

            # find java
            java_exec = self.java_path or find_java_executable()
            if not java_exec or not os.path.exists(java_exec):
                self.on_finished_emit(False, "Java not found. Set path in Settings.")
                return

            # Логируем команду запуска
            logger.info(f"Launch command: {cmd}")
            logger.info(f"Java executable: {java_exec}")
            logger.info(f"Args file: {args_path}")

            # Проверяем существование args.txt
            if os.path.exists(args_path):
                with open(args_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Args file content:\n{f.read()}")
            else:
                logger.error("Args file not found!")

            # launch java @args.txt
            cmd = [java_exec, f"@{args_path}"]
            self.on_status_emit("Launching Java process...")
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                out, err = proc.communicate()
                
                # Логируем вывод
                if out:
                    logger.info(f"Java stdout: {out[:1000]}")
                if err:
                    logger.error(f"Java stderr: {err[:2000]}")
                    
                if proc.returncode == 0:
                    self.on_finished_emit(True, "Client finished successfully.")
                else:
                    logger.error(f"Java process exited with code: {proc.returncode}")
                    self.on_finished_emit(False, f"Launch failed with exit code {proc.returncode}")
            except Exception as e:
                logger.exception("Launch exception")
                self.on_finished_emit(False, f"Launch failed: {e}")

# -----------------------
# Dialogs
# -----------------------
class KeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter access key")
        self.setModal(True)
        v = QVBoxLayout()
        self.setLayout(v)
        self.field = QLineEdit()
        self.field.setPlaceholderText("Enter key (any text works for now)")
        v.addWidget(self.field)
        hb = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        hb.addWidget(cancel)
        hb.addWidget(ok)
        v.addLayout(hb)

    def get_key(self):
        return self.field.text().strip()

class SettingsDialog(QDialog):
    def __init__(self, parent, username: str, memory_gb: int, java_path: Optional[str], theme: Optional[str] = "dark_green"):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.username = username
        self.memory_gb = memory_gb
        self.java_path = java_path or ""
        self.theme = theme or "dark_green"

        form = QFormLayout()
        self.user_edit = QLineEdit(self.username)
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(1, 64)  # allow up to 64 GB if user wants
        self.ram_spin.setValue(self.memory_gb)
        self.java_edit = QLineEdit(self.java_path)
        browse = QPushButton("Browse")
        browse.clicked.connect(self.browse_java)
        hb = QHBoxLayout()
        hb.addWidget(self.java_edit)
        hb.addWidget(browse)

        # Theme selector
        self.theme_combo = QComboBox()
        # available themes based on THEMES dict keys
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.theme)

        form.addRow("Username:", self.user_edit)
        form.addRow("RAM (GB):", self.ram_spin)
        form.addRow("Java path:", hb)
        form.addRow("Theme:", self.theme_combo)
        btns = QHBoxLayout()
        ok = QPushButton("Save")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(btns)
        self.setLayout(layout)

    def browse_java(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Java executable", "", "Executables (*.exe);;All files (*)")
        if f:
            self.java_edit.setText(f)

    def get_values(self):
        return self.user_edit.text().strip(), int(self.ram_spin.value()), self.java_edit.text().strip(), self.theme_combo.currentText()

class VerifyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verify / Reinstall")
        self.setModal(True)
        self.action = None
        v = QVBoxLayout()
        self.setLayout(v)
        v.addWidget(QLabel("Choose action:"))
        btn_verify = QPushButton("Verify")
        btn_reinstall = QPushButton("Reinstall")
        btn_cancel = QPushButton("Cancel")
        btn_verify.clicked.connect(self.do_verify)
        btn_reinstall.clicked.connect(self.do_reinstall)
        btn_cancel.clicked.connect(self.reject)
        hb = QHBoxLayout()
        hb.addWidget(btn_verify)
        hb.addWidget(btn_reinstall)
        hb.addWidget(btn_cancel)
        v.addLayout(hb)

    def do_verify(self):
        self.action = "verify"
        self.accept()

    def do_reinstall(self):
        self.action = "reinstall"
        self.accept()

# -----------------------
# Entrypoint
# -----------------------
def main():
    app = QApplication(sys.argv)
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()