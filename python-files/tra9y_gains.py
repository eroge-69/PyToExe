#!/usr/bin/env python3
"""
TrayGains — cute tray app with glowy splash, first-run wizard, secure donation handshake,
auto-update from GitHub, per-service status, calc button, sounds, and persistent config.

This file implements the core GUI and logic for the TrayGains application. It features
a dark-themed, glowy splash screen with a water-fill animation, a first-run wizard to
download and install the necessary repository, persistent configuration, automatic
updates from a specified GitHub repository, and secure donation links using a local
helper for obfuscated referral links. The app runs in the system tray, showing
earnings over different time windows and projecting monthly income. Users can also
customize settings, import sound packs, and check for updates manually.
"""

import os
import sys
import json
import time
import io
import zipfile
import shutil
import subprocess
import tempfile
import threading
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Tuple
import datetime as _dt

try:
    # Optional import; GUI code only available if PySide6 is installed
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QLabel,
        QLineEdit,
        QPushButton,
        QFileDialog,
        QVBoxLayout,
        QHBoxLayout,
        QCheckBox,
        QTextEdit,
        QSpinBox,
        QSystemTrayIcon,
        QMenu,
        QMessageBox,
        QColorDialog,
        QSlider,
        QFrame,
        QGridLayout,
    )
    from PySide6.QtGui import (
        QAction,
        QIcon,
        QColor,
        QPixmap,
        QPainter,
        QFont,
        QLinearGradient,
        QBrush,
    )
    from PySide6.QtCore import Qt, QTimer, QRect, QPointF, QSize, Slot
    try:
        from PySide6.QtSvg import QSvgRenderer
    except Exception:
        QSvgRenderer = None
    try:
        from PySide6.QtMultimedia import QSoundEffect
        HAVE_SOUND = True
    except Exception:
        HAVE_SOUND = False
except ImportError:
    # If PySide6 is not available, define dummy classes for type checking
    QApplication = object  # type: ignore
    QWidget = object  # type: ignore
    QLabel = object  # type: ignore
    QLineEdit = object  # type: ignore
    QPushButton = object  # type: ignore
    QFileDialog = object  # type: ignore
    QVBoxLayout = object  # type: ignore
    QHBoxLayout = object  # type: ignore
    QCheckBox = object  # type: ignore
    QTextEdit = object  # type: ignore
    QSpinBox = object  # type: ignore
    QSystemTrayIcon = object  # type: ignore
    QMenu = object  # type: ignore
    QMessageBox = object  # type: ignore
    QColorDialog = object  # type: ignore
    QSlider = object  # type: ignore
    QFrame = object  # type: ignore
    QGridLayout = object  # type: ignore
    QAction = object  # type: ignore
    QIcon = object  # type: ignore
    QColor = object  # type: ignore
    QPixmap = object  # type: ignore
    QPainter = object  # type: ignore
    QFont = object  # type: ignore
    QLinearGradient = object  # type: ignore
    QBrush = object  # type: ignore
    Qt = object  # type: ignore
    QTimer = object  # type: ignore
    QRect = object  # type: ignore
    QPointF = object  # type: ignore
    QSize = object  # type: ignore
    Slot = lambda x: x  # type: ignore
    QSvgRenderer = None  # type: ignore
    HAVE_SOUND = False

__all__ = [
    "TrayApp",
    "load_config",
    "save_config",
    "backup_user_data",
    "check_for_update_and_launch",
]

# -----------------------------------------------------------------------------
# Application configuration constants
# -----------------------------------------------------------------------------

APP_NAME = "TrayGains"
"""The name of the application."""

CURRENCY = "$"
"""The currency symbol used in the application."""

# Directories for storing user data and configuration
CONFIG_DIR = Path.home() / f".{APP_NAME.lower()}"
CONFIG_PATH = CONFIG_DIR / "config.json"
SOUNDS_DIR = CONFIG_DIR / "sounds"
PACKS_DIR = SOUNDS_DIR / "packs"
ACTIVE_DIR = SOUNDS_DIR / "active"
BACKUP_DIR = CONFIG_DIR / "backups"

# GitHub update defaults
GITHUB_OWNER = "ashesaffective"
"""GitHub user account providing updates."""

GITHUB_REPO = "ashestraymoneygainrrrrrrr"
"""GitHub repository name from which releases are pulled."""

RELEASE_ASSET_FILENAME = "TrayGains.exe"
"""The name of the release asset to download for updates."""

CURRENT_VERSION = "0.0.1"
"""Current version of the application. Bump this when releasing new versions."""


DEFAULT_CONFIG: Dict[str, Any] = {
    "first_run_done": False,
    "repo": {
        "url": "https://github.com/XternA/income-generator",
        "branch": "main",
        "dest": str((Path.cwd() / "income-generator").resolve()),
        "create_venv": True,
        "write_env": True,
        "env_vars": {},
    },
    "poll_seconds": 10 * 60,
    "discord": {
        "enabled": False,
        "webhook_url": "",
        "post_every_minutes": 120,
    },
    "sources": [
        {"name": "EarnApp", "type": "dummy", "enabled": True, "config": {}},
        {"name": "Honeygain", "type": "dummy", "enabled": False, "config": {}},
    ],
    "ui": {
        "splash_image_path": "",
        "splash_overlay_hex": "#89a3ff",
        "sounds_enabled": True,
        "active_pack": "default",
        "volume": 0.15,
    },
    "github_update": {
        "owner": GITHUB_OWNER,
        "repo": GITHUB_REPO,
        "asset": RELEASE_ASSET_FILENAME,
        "auto_check": True,
    },
}


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def ensure_dir(p: Path) -> None:
    """Ensure that a directory exists."""
    p.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load the user configuration from disk, creating defaults if missing."""
    ensure_dir(CONFIG_DIR)
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Create default configuration if loading fails
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg: Dict[str, Any]) -> None:
    """Save the user configuration to disk."""
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def run(cmd: List[str], cwd: str | None = None) -> Tuple[bool, str]:
    """Run a subprocess command and return success status and output."""
    try:
        process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output, _ = process.communicate()
        return process.returncode == 0, output or ""
    except Exception as e:
        return False, str(e)


def git_or_zip_fetch(url: str, branch: str, dest: str) -> Tuple[bool, str]:
    """Clone a GitHub repository using git if available, otherwise download a zip."""
    if shutil.which("git"):
        ok, out = run(["git", "clone", "--depth", "1", "--branch", branch, url, dest])
        if ok:
            return True, out
    # Fallback to downloading the repository as a zip
    try:
        owner, repo = url.rstrip("/").split("/")[-2:]
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        with urllib.request.urlopen(zip_url) as response:
            data = response.read()
        z = zipfile.ZipFile(io.BytesIO(data))
        z.extractall(dest)
        top = z.namelist()[0].split("/")[0]
        root = Path(dest) / top
        for it in root.iterdir():
            tgt = Path(dest) / it.name
            if not tgt.exists():
                shutil.move(str(it), str(tgt))
        shutil.rmtree(root, ignore_errors=True)
        return True, "Zip fetched"
    except Exception as e:
        return False, f"zip fetch failed: {e}"


# -----------------------------------------------------------------------------
# Earnings and adapters
# -----------------------------------------------------------------------------

class EarningEvent:
    """Represents a micro-earning event with a timestamp, amount, and service name."""

    def __init__(self, ts: _dt.datetime, amt: float, service: str) -> None:
        self.timestamp = ts
        self.amount = amt
        self.service = service


class DummyAdapter:
    """A dummy earnings adapter that generates fake micro-earnings for demonstration."""

    def __init__(self, name: str, cfg: Dict[str, Any]):
        self.name = name
        self.cfg = cfg

    def fetch_recent(self) -> List[EarningEvent]:
        now = _dt.datetime.now(_dt.timezone.utc)
        events = []
        for i in range(180):
            events.append(EarningEvent(now - _dt.timedelta(minutes=i * 20), 0.006 + (i % 3) * 0.003, self.name))
        return events


ADAPTERS: Dict[str, Any] = {"dummy": DummyAdapter}


def summarize(events: List[EarningEvent]) -> Dict[str, Any]:
    """Summarize earnings data into totals and projected values."""
    if not events:
        return {
            "sum_24h": 0.0,
            "sum_7d": 0.0,
            "rate_per_hour": 0.0,
            "month_projection": 0.0,
            "per_service": {},
        }
    now = _dt.datetime.now(_dt.timezone.utc)
    cut24 = now - _dt.timedelta(hours=24)
    cut7 = now - _dt.timedelta(days=7)
    s24 = sum(e.amount for e in events if e.timestamp >= cut24)
    s7 = sum(e.amount for e in events if e.timestamp >= cut7)
    base_sum, base_hours = (s24, 24.0) if s24 > 0 else (s7, 168.0)
    r = base_sum / base_hours if base_hours else 0.0
    per: Dict[str, float] = {}
    for e in events:
        per[e.service] = per.get(e.service, 0.0) + e.amount
    return {
        "sum_24h": round(s24, 2),
        "sum_7d": round(s7, 2),
        "rate_per_hour": round(r, 4),
        "month_projection": round(r * 24 * 30, 2),
        "per_service": {k: round(v, 2) for k, v in per.items()},
    }


# -----------------------------------------------------------------------------
# UI components for splash, sound, and earnings
# -----------------------------------------------------------------------------


class Dot(QWidget):
    """A pulsing dot widget representing connection state."""

    def __init__(self, color: str = "#ffdd33") -> None:
        super().__init__()
        self.color = QColor(color)
        self._pulse = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(60)
        self.setFixedSize(QSize(18, 18))

    def _step(self) -> None:
        self._pulse = (self._pulse + 1) % 40
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = 8 + (self._pulse / 40.0) * 3
        p.setBrush(self.color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(self.rect().center(), r, r)


class ServiceCard(QFrame):
    """A widget representing a service's connection status and earnings."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.setObjectName("ServiceCard")
        self.setStyleSheet(
            "#ServiceCard{background:#161425;border:1px solid #2a2745;border-radius:12px;} "
            "QLabel{color:#eceaff;}"
        )
        self.dot = Dot("#ffd84d")
        self.title = QLabel(name)
        self.title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.state = QLabel("Awaiting connection")
        self.metrics = QLabel("$0.00 today • $0.00 this week • $0.00/hr")
        self.metrics.setStyleSheet("color:#bdb9ff;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(10)
        col = QVBoxLayout()
        col.addWidget(self.title)
        col.addWidget(self.state)
        col.addWidget(self.metrics)
        layout.addWidget(self.dot, 0, Qt.AlignTop)
        layout.addLayout(col, 1)

    def set_state(self, state: str) -> None:
        state = state.lower()
        if state == "awaiting":
            self.state.setText("Awaiting connection")
            self.dot.color = QColor("#ffd84d")
        elif state == "connecting":
            self.state.setText("Connecting…")
            self.dot.color = QColor("#8fd3ff")
        elif state == "connected":
            self.state.setText("Connected ✓")
            self.dot.color = QColor("#86e57f")
        else:
            self.state.setText("Error")
            self.dot.color = QColor("#ff6b6b")
        self.dot.update()

    def set_metrics(self, sum24: float, sum7: float, rate: float) -> None:
        self.metrics.setText(f"{CURRENCY}{sum24:.2f} today • {CURRENCY}{sum7:.2f} this week • {CURRENCY}{rate:.2f}/hr")


class SplashScreen(QWidget):
    """A glowy water-effect splash screen used during startup and long operations."""

    def __init__(self, cfg_ui: Dict[str, Any], text: str = "Starting…") -> None:
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.cfg_ui = cfg_ui
        self.text = text
        self.progress = 0
        self.t = 0.0
        self.resize(680, 460)
        scr = QApplication.primaryScreen().geometry()
        self.move(scr.center() - self.rect().center())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self.timer.start(33)
        self.show()

    def step(self) -> None:
        self.t += 0.06
        self.update()

    def set_status(self, text: str, pct: int | None = None) -> None:
        self.text = text
        if pct is not None:
            self.progress = max(self.progress, pct)
        self.update()

    def _wave(self, size: QSize, level: int, t: float, alpha: int = 110, amp: int = 8, wavelength: int = 90) -> QPixmap:
        from math import sin, pi

        w, h = size.width(), size.height()
        pm = QPixmap(w, h)
        pm.fill(Qt.transparent)
        pp = QPainter(pm)
        pp.setPen(Qt.NoPen)
        grad = QLinearGradient(0, level - 40, 0, h)
        base = QColor(255, 255, 255, alpha)
        grad.setColorAt(0, base)
        grad.setColorAt(1, QColor(255, 255, 255, max(0, alpha - 60)))
        pp.setBrush(QBrush(grad))
        pts = []
        for x in range(0, w + 1, 2):
            y = level + int(amp * sin((x + t * 42) * 2 * pi / wavelength))
            pts.append(QPointF(x, y))
        pts += [QPointF(w, h), QPointF(0, h)]
        pp.drawPolygon(pts)
        pp.end()
        return pm

    def _draw_glow(self, p: QPainter, rect: QRect) -> None:
        h = rect.height()
        level = rect.bottom() - int(h * (self.progress / 100.0))
        # Glow tint using difference composition
        p.setCompositionMode(QPainter.CompositionMode_Difference)
        p.fillRect(rect, QColor("#67e8f9"))
        p.setCompositionMode(QPainter.CompositionMode_Plus)
        # Multiple waves for layered glow
        p.drawPixmap(rect.topLeft(), self._wave(rect.size(), level - 2, self.t * 0.98, 60, 12, 100))
        p.drawPixmap(rect.topLeft(), self._wave(rect.size(), level - 5, self.t * 1.05, 40, 18, 110))
        p.drawPixmap(rect.topLeft(), self._wave(rect.size(), level - 8, self.t * 1.09, 25, 24, 125))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        # Base wave
        p.drawPixmap(rect.topLeft(), self._wave(rect.size(), level, self.t, 110, 8, 90))

    def _draw_base(self, p: QPainter, rect: QRect) -> None:
        p.fillRect(self.rect(), QColor(10, 10, 14, 235))
        path = self.cfg_ui.get("splash_image_path", "")
        overlay = qcolor(self.cfg_ui.get("splash_overlay_hex", "#89a3ff"))
        if path and Path(path).is_file():
            if path.lower().endswith(".svg") and QSvgRenderer is not None:
                svg = QSvgRenderer(path)
                tmp = QPixmap(rect.size())
                tmp.fill(Qt.transparent)
                if svg.isValid():
                    q = QPainter(tmp)
                    svg.render(q)
                    q.end()
                    p.drawPixmap(rect, tmp)
            else:
                px = QPixmap(path)
                if not px.isNull():
                    p.drawPixmap(rect, px.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            p.setPen(QColor("#cbd5ff"))
            f = QFont("Comic Sans MS", 28)
            if not f.exactMatch():
                f = QFont("Segoe UI", 28)
            f.setBold(True)
            p.setFont(f)
            p.drawText(rect, Qt.AlignCenter, "✨ TrayGains ✨")
        p.setCompositionMode(QPainter.CompositionMode_Difference)
        p.fillRect(rect, overlay)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        img_rect = QRect(40, 36, self.width() - 80, self.height() - 160)
        self._draw_base(p, img_rect)
        self._draw_glow(p, img_rect)
        # Draw text and percentage
        f = QFont("Comic Sans MS", 14)
        if not f.exactMatch():
            f = QFont("Segoe UI", 14)
        p.setFont(f)
        p.setPen(QColor("#e8e8f2"))
        p.drawText(QRect(0, self.height() - 98, self.width(), 30), Qt.AlignCenter, self.text)
        p.setPen(QColor("#b9b9cc"))
        p.drawText(QRect(0, self.height() - 72, self.width(), 30), Qt.AlignCenter, f"{self.progress}%")
        p.end()


# -----------------------------------------------------------------------------
# Secure donation links handshake
# -----------------------------------------------------------------------------


def _ensure_helper() -> bool:
    """Ensure the verifier helper is running; start it if possible."""
    helper = "verifier.exe"
    root = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    helper_path = root / helper
    # Check if helper is already running
    try:
        socket.create_connection((HOST, PORT), timeout=0.2).close()
        return True
    except Exception:
        if helper_path.exists():
            try:
                subprocess.Popen([str(helper_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.5)
                return True
            except Exception:
                return False
        return False


def _from_helper() -> List[Dict[str, str]]:
    """Retrieve links from the helper via a challenge-response handshake."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((HOST, PORT))
        nonce = os.urandom(8).hex()
        ts = int(time.time())
        s.sendall(json.dumps({"nonce": nonce, "ts": ts}).encode())
        data = s.recv(65536)
        s.close()
        if not data:
            return []
        resp = json.loads(data.decode())
        if "links" not in resp:
            return []
        key = _mk_expected_key()
        msg = f"{resp.get('nonce')}|{resp.get('ts')}".encode()
        mac = hmac.new(key, msg, hashlib.sha256).hexdigest()
        if hmac.compare_digest(mac, resp.get("hmac", "")) and abs(int(time.time()) - int(resp.get("ts", 0))) <= 60:
            return resp["links"]
        return []
    except Exception:
        return []


def get_donation_links() -> List[Dict[str, str]]:
    """Return the donation links after verifying with the helper, or fallback."""
    if _ensure_helper():
        links = _from_helper()
        if links:
            return links
    # Fallback to obfuscated donate module
    try:
        from donate_obf import get_links as _obf
        return _obf()
    except Exception:
        return []


# -----------------------------------------------------------------------------
# Auto-update using GitHub Releases
# -----------------------------------------------------------------------------


def _gh_get(url: str, token: str | None = None) -> Dict[str, Any]:
    """Retrieve JSON data from GitHub API."""
    req = urllib.request.Request(url, headers={"User-Agent": "TrayGains-Updater"})
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)


def check_latest_release(owner: str, repo: str, token: str | None = None) -> Dict[str, Any] | None:
    """Check GitHub for the latest release."""
    try:
        return _gh_get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", token)
    except Exception as e:
        print("release check failed:", e)
        return None


def find_asset(release_json: Dict[str, Any], filename: str) -> Dict[str, Any] | None:
    """Find a release asset matching the specified filename."""
    for asset in release_json.get("assets", []):
        if asset.get("name") == filename:
            return asset
    return None


def backup_user_data() -> Path:
    """Create a zip backup of user settings and sound packs."""
    ensure_dir(BACKUP_DIR)
    ts = time.strftime("%Y%m%d-%H%M%S")
    zip_path = BACKUP_DIR / f"traygains-backup-{ts}.zip"
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as z:
        if CONFIG_PATH.exists():
            z.write(str(CONFIG_PATH), "config.json")
        if SOUNDS_DIR.exists():
            for p in SOUNDS_DIR.rglob("*"):
                if p.is_file():
                    z.write(str(p), str(p.relative_to(CONFIG_DIR)))
    return zip_path


def download_asset(url: str, name: str) -> Path:
    """Download a release asset to a temporary location and return its path."""
    tmp = Path(tempfile.mkdtemp(prefix="tg_update_"))
    out = tmp / name
    req = urllib.request.Request(url, headers={"User-Agent": "TrayGains-Updater"})
    with urllib.request.urlopen(req, timeout=60) as response, open(out, "wb") as f:
        shutil.copyfileobj(response, f)
    return out


def launch_updater(downloaded: Path, backup_zip: Path) -> Tuple[bool, str]:
    """Launch the updater helper to replace the current binary with the downloaded one."""
    exe = Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0]).resolve()
    updater = exe.with_name("updater.exe")
    if not updater.exists():
        return False, "updater-missing"
    cmd = [str(updater), "--old", str(exe), "--new", str(downloaded), "--backup", str(backup_zip)]
    try:
        subprocess.Popen(cmd)
        os._exit(0)
    except Exception as e:
        return False, str(e)


def check_for_update_and_launch(cfg: Dict[str, Any]) -> None:
    """Check for updates and perform update if a new version is available."""
    if not cfg.get("github_update", {}).get("auto_check", True):
        return
    owner = cfg["github_update"].get("owner") or GITHUB_OWNER
    repo = cfg["github_update"].get("repo") or GITHUB_REPO
    asset = cfg["github_update"].get("asset") or RELEASE_ASSET_FILENAME
    release = check_latest_release(owner, repo)
    if not release:
        return
    tag = release.get("tag_name") or release.get("name") or ""
    if tag and tag != CURRENT_VERSION:
        asset_json = find_asset(release, asset)
        if not asset_json:
            return
        download_url = asset_json.get("browser_download_url")
        file_name = asset_json.get("name")
        try:
            backup = backup_user_data()
            downloaded = download_asset(download_url, file_name)
            launch_updater(downloaded, backup)
        except Exception as e:
            print("update failed:", e)


# -----------------------------------------------------------------------------
# UI: Wizard, Dashboard, Settings
# -----------------------------------------------------------------------------

class WizardScreen(QWidget):
    """First-run wizard for cloning the repository, installing dependencies, and writing .env."""

    def __init__(self, cfg: Dict[str, Any], on_done: callable, splash: SplashScreen) -> None:
        super().__init__()
        self.cfg = cfg
        self.on_done = on_done
        self.splash = splash
        self.setWindowTitle(f"{APP_NAME} — First run")
        self.resize(760, 560)
        grid = QGridLayout(self)
        self.repo = QLineEdit(cfg["repo"]["url"])
        self.branch = QLineEdit(cfg["repo"]["branch"])
        self.dest = QLineEdit(cfg["repo"]["dest"])
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.pick_folder)
        self.create_venv_chk = QCheckBox("Create virtualenv + install requirements.txt")
        self.create_venv_chk.setChecked(cfg["repo"]["create_venv"])
        self.write_env_chk = QCheckBox("Write .env with the keys below")
        self.write_env_chk.setChecked(cfg["repo"]["write_env"])
        self.env_edit = QTextEdit()
        self.poll = QSpinBox()
        self.poll.setRange(60, 24 * 3600)
        self.poll.setValue(cfg.get("poll_seconds", 600))
        self.clone_btn = QPushButton("Clone / Download")
        self.clone_btn.clicked.connect(self.clone_repo)
        self.install_btn = QPushButton("Install deps")
        self.install_btn.clicked.connect(self.install_deps)
        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.finish)
        row = 0
        grid.addWidget(QLabel("Repository"), row, 0, 1, 4)
        row += 1
        grid.addWidget(QLabel("URL:"), row, 0)
        grid.addWidget(self.repo, row, 1, 1, 2)
        grid.addWidget(browse_btn, row, 3)
        row += 1
        grid.addWidget(QLabel("Branch:"), row, 0)
        grid.addWidget(self.branch, row, 1)
        row += 1
        grid.addWidget(QLabel("Destination:"), row, 0)
        grid.addWidget(self.dest, row, 1, 1, 3)
        row += 1
        grid.addWidget(self.create_venv_chk, row, 0, 1, 4)
        row += 1
        grid.addWidget(self.write_env_chk, row, 0, 1, 4)
        row += 1
        grid.addWidget(QLabel(".env key=value lines"), row, 0, 1, 4)
        row += 1
        grid.addWidget(self.env_edit, row, 0, 1, 4)
        row += 1
        grid.addWidget(QLabel("Polling interval (sec):"), row, 0)
        grid.addWidget(self.poll, row, 1)
        row += 1
        grid.addWidget(self.clone_btn, row, 0)
        grid.addWidget(self.install_btn, row, 1)
        grid.addWidget(self.finish_btn, row, 2)

    def pick_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Choose folder", str(Path.cwd()))
        if d:
            self.dest.setText(str(Path(d) / "income-generator"))

    def clone_repo(self) -> None:
        self.splash.set_status("Fetching repository…", 20)
        ok, out = git_or_zip_fetch(self.repo.text().strip(), self.branch.text().strip(), self.dest.text().strip())
        QMessageBox.information(self, "Clone", "OK" if ok else out)
        self.splash.set_status("Clone complete" if ok else "Clone failed", 40 if ok else 10)

    def install_deps(self) -> None:
        dest = self.dest.text().strip()
        req = Path(dest) / "requirements.txt"
        if not req.exists():
            QMessageBox.information(self, "Install", "No requirements.txt — skipping")
            return
        self.splash.set_status("Creating venv…", 50)
        if self.create_venv_chk.isChecked():
            venv = Path(dest) / ".venv_tray"
            if not venv.exists():
                run([sys.executable, "-m", "venv", str(venv)])
            pip = venv / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")
            pip = str(pip if pip.exists() else (shutil.which("pip") or "pip"))
            self.splash.set_status("Installing deps…", 70)
            ok, out = run([pip, "install", "-r", str(req)], cwd=dest)
            QMessageBox.information(self, "Install", out[-800:] if out else ("OK" if ok else "fail"))
        else:
            pip = shutil.which("pip") or "pip"
            ok, out = run([pip, "install", "-r", str(req)], cwd=dest)
            QMessageBox.information(self, "Install", out[-800:] if out else ("OK" if ok else "fail"))
        self.splash.set_status("Deps installed", 85)

    def finish(self) -> None:
        self.cfg["repo"].update(
            {
                "url": self.repo.text().strip(),
                "branch": self.branch.text().strip(),
                "dest": self.dest.text().strip(),
                "create_venv": self.create_venv_chk.isChecked(),
                "write_env": self.write_env_chk.isChecked(),
                "env_vars": {},
            }
        )
        # Save polling interval
        self.cfg["poll_seconds"] = int(self.poll.value())
        # Write .env if requested
        if self.write_env_chk.isChecked():
            env_map: Dict[str, str] = {}
            for line in self.env_edit.toPlainText().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env_map[k.strip()] = v.strip().strip('"')
            if env_map:
                dest = Path(self.dest.text().strip())
                (dest / ".env").write_text(
                    "\n".join(f'{k}="{v}"' for k, v in env_map.items()), encoding="utf-8"
                )
        self.cfg["first_run_done"] = True
        save_config(self.cfg)
        self.splash.set_status("Done!", 100)
        self.on_done()
        self.close()


# -----------------------------------------------------------------------------
# Main application class
# -----------------------------------------------------------------------------

class TrayApp:
    """Main class for the TrayGains application."""

    def __init__(self) -> None:
        ensure_dir(CONFIG_DIR)
        ensure_dir(BACKUP_DIR)
        self.cfg = load_config()
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.tray = QSystemTrayIcon(icon_())
        self.tray.setToolTip(APP_NAME)
        self.build_menu()
        self.sound = Sounder(self.cfg)
        self.splash = SplashScreen(self.cfg["ui"], "Starting…")
        self.splash.set_status("Loading config…", 10)
        self.events_lock = threading.Lock()
        self.events: List[EarningEvent] = []
        self.summary: Dict[str, Any] = {}
        self.poll_seconds = int(self.cfg.get("poll_seconds", 600))
        if not self.cfg.get("first_run_done", False):
            self.splash.set_status("First run — opening setup…", 15)
            self.wizard = WizardScreen(self.cfg, on_done=self.after_first_run, splash=self.splash)
            self.wizard.show()
        else:
            self.splash.set_status("Ready", 100)
            self.splash.close()
            self.start_poll_loop()
        threading.Thread(target=lambda: check_for_update_and_launch(self.cfg), daemon=True).start()
        self.dashboard: QWidget | None = None
        self.settings_win: QWidget | None = None

    def build_menu(self) -> None:
        menu = QMenu()
        act_open = QAction("Open Dashboard", self.app)
        act_open.triggered.connect(self.open_dashboard)
        menu.addAction(act_open)
        act_refresh = QAction("Refresh now", self.app)
        act_refresh.triggered.connect(self.poll_once_threaded)
        menu.addAction(act_refresh)
        act_settings = QAction("Settings…", self.app)
        act_settings.triggered.connect(self.open_settings)
        menu.addAction(act_settings)
        # Donation submenu
        donate_menu = QMenu("Support me", menu)
        for item in get_donation_links():
            action = QAction(item["name"], self.app)
            action.triggered.connect(lambda checked=False, url=item["url"]: webbrowser.open(url))
            donate_menu.addAction(action)
        menu.addMenu(donate_menu)
        menu.addSeparator()
        act_quit = QAction("Quit", self.app)
        act_quit.triggered.connect(self.quit)
        menu.addAction(act_quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.open_dashboard() if reason == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def make_adapters(self) -> List[DummyAdapter]:
        adapters = []
        for source in self.cfg.get("sources", []):
            if not source.get("enabled", True):
                continue
            cls = ADAPTERS.get(source["type"])
            if cls:
                adapters.append(cls(source["name"], source.get("config", {})))
        return adapters

    def poll_once(self) -> None:
        adapters = self.make_adapters()
        all_events: List[EarningEvent] = []
        # Fetch data from adapters
        for adapter in adapters:
            try:
                all_events.extend(adapter.fetch_recent())
            except Exception:
                pass
        with self.events_lock:
            self.events = all_events
            self.summary = summarize(all_events)
        s = self.summary
        self.tray.setToolTip(
            f"{APP_NAME}\n24h: {CURRENCY}{s.get('sum_24h', 0)} | "
            f"7d: {CURRENCY}{s.get('sum_7d', 0)} | "
            f"{CURRENCY}{s.get('rate_per_hour', 0)}/h"
        )
        if self.dashboard:
            self.dashboard.update_ui()

    def poll_once_threaded(self) -> None:
        threading.Thread(target=self.poll_once, daemon=True).start()

    def start_poll_loop(self) -> None:
        self.poll_once_threaded()
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_once_threaded)
        self.timer.start(self.poll_seconds * 1000)

    def get_summary(self) -> Dict[str, Any]:
        with self.events_lock:
            return dict(self.summary) if self.summary else summarize([])

    def get_table(self) -> List[Tuple[str, float]]:
        with self.events_lock:
            per: Dict[str, float] = {}
            for e in self.events:
                per[e.service] = per.get(e.service, 0.0) + e.amount
            return sorted(per.items(), key=lambda kv: -kv[1])

    def open_dashboard(self) -> None:
        if self.dashboard is None:
            self.dashboard = Dashboard(self.cfg, self.get_summary, self.get_table, self.poll_once_threaded)
        self.dashboard.update_ui()
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def open_settings(self) -> None:
        def on_save() -> None:
            # Update polling interval in the running app
            self.poll_seconds = int(self.cfg.get("poll_seconds", 600))
            if hasattr(self, "timer"):
                self.timer.setInterval(self.poll_seconds * 1000)

        self.settings_win = Settings(self.cfg, on_save)
        self.settings_win.show()

    def after_first_run(self) -> None:
        # Called after the wizard completes on first run
        self.splash.set_status("Done!", 100)
        time.sleep(0.4)
        self.splash.close()
        self.start_poll_loop()

    def quit(self) -> None:
        self.tray.hide()
        self.app.quit()

    def run(self) -> None:
        sys.exit(self.app.exec())


def main() -> None:
    app = QApplication(sys.argv)
    TrayApp().run()


if __name__ == "__main__":
    main()