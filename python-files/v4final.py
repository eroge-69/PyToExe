import sys
import asyncio
import threading
import pyperclip
import discord
import re
import json
import os
import websockets

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

# =========================
# WebSocket server (background thread)
# =========================
WS_HOST = "127.0.0.1"
WS_PORT = 8765

_server_loop = None
_connected_clients = set()
_server_lock = threading.Lock()


async def _ws_handler(ws):
    addr = getattr(ws, "remote_address", ("local", 0))
    print(f"[WS] Client connected: {addr}")
    _connected_clients.add(ws)
    try:
        async for _ in ws:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        _connected_clients.discard(ws)
        print(f"[WS] Client disconnected: {addr}")


async def _ws_send_coroutine(job_id: str):
    if not _connected_clients:
        return
    to_remove = []
    for ws in list(_connected_clients):
        try:
            await ws.send(job_id)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        _connected_clients.discard(ws)


def send_job_to_ws(job_id: str):
    global _server_loop
    if not job_id:
        return
    with _server_lock:
        loop = _server_loop
    if loop is None:
        return
    try:
        fut = asyncio.run_coroutine_threadsafe(_ws_send_coroutine(job_id), loop)
        try:
            fut.result(timeout=2)
        except Exception:
            pass
    except Exception as e:
        print(f"[WS] Failed to schedule send: {e}")


async def _start_ws_server():
    server = await websockets.serve(_ws_handler, WS_HOST, WS_PORT)
    print(f"[WS] Server listening on ws://{WS_HOST}:{WS_PORT}")
    await asyncio.Future()


def _ws_thread_entry():
    global _server_loop
    try:
        loop = asyncio.new_event_loop()
        with _server_lock:
            _server_loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_start_ws_server())
    except Exception as e:
        print(f"[WS] Server thread error: {e}")
    finally:
        with _server_lock:
            _server_loop = None


def start_ws_background():
    with _server_lock:
        if _server_loop is not None:
            return
    t = threading.Thread(target=_ws_thread_entry, name="ws-server-thread", daemon=True)
    t.start()


# ================= Config File =================
CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


if not os.path.exists(CONFIG_FILE):
    save_config({})


# ================= Discord Config =================
POLL_INTERVAL = 0
intents = discord.Intents.all()

CHANNELS = {
    "Under 500k Notify 1": 1401774723246854204,
    "Under 500k Notify 2": 1401774863974268959,
    "500k to 1m Notify 1": 1401774956404277378,
    "500k to 1m Notify 2": 1401775012083404931,
    "1m to 10m Notify 1": 1401775061706346536,
    "1m to 10m Notify 2": 1401775125765947442,
    "10m+ Notify": 1401775181025775738
}

BRAINROT_NAMES = [
    "Garama and Madundung", "Dragon Cannelloni", "Nuclearo Dinossauro",
    "La Suprema Combinasion", "Los Hotspotsitos", "Esok Sekolah",
    "Ketupat Kepat", "Sammyni Spyderini", "La Grande Combinasion"
]

EXCLUDE_BRAINROTS = [
    "Job Job Job Sahur",
    "La Cucaracha",
    "Mariachi Corazoni"
]


# ================= Discord Monitor =================
class DiscordMonitor(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(bool)
    job_signal = pyqtSignal(str, str, str)  # job_id, name_val, full_message

    def __init__(self, token, channel_id):
        super().__init__()
        self.token = token
        self.channel_id = int(channel_id)
        self.loop = asyncio.new_event_loop()
        self.client = discord.Client(intents=intents, loop=self.loop)
        self.last_seen_id = None
        self.running = True

        @self.client.event
        async def on_ready():
            self.log_signal.emit(f"✅ Logged in as {self.client.user}")
            self.log_signal.emit(f"📡 Monitoring Channel ID: {self.channel_id}")
            self.status_signal.emit(True)
            self.loop.create_task(self.poll_messages())

    async def poll_messages(self):
        await self.client.wait_until_ready()
        channel = self.client.get_channel(self.channel_id)
        if not channel:
            self.log_signal.emit("❌ Could not get target channel.")
            self.status_signal.emit(False)
            return

        while self.running and not self.client.is_closed():
            try:
                last_message = await channel.history(limit=1).flatten()
                if last_message:
                    message = last_message[0]
                    if self.last_seen_id != message.id:
                        self.last_seen_id = message.id
                        self.process_message(message)
            except Exception as e:
                self.log_signal.emit(f"❌ Error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    @staticmethod
    def parse_money(money_str: str) -> float:
        if not money_str:
            return 0.0
        match = re.search(r"\$([\d\.]+)([KkMmBb]?)/s", money_str.replace(",", ""))
        if not match:
            return 0.0
        value = float(match.group(1))
        suffix = (match.group(2) or "").lower()
        if suffix == "k":
            value /= 1000
        elif suffix == "m":
            value *= 1
        elif suffix == "b":
            value *= 1000
        return value

    def process_message(self, message):
        content = message.content
        name_val, money_val, job_val = None, None, None

        if content:
            for line in content.splitlines():
                clean_line = line.replace("```", "").strip()
                if "Name" in line and not name_val:
                    name_val = clean_line.split(":", 1)[-1].strip()
                elif "Money per sec" in line and not money_val:
                    money_val = clean_line.split(":", 1)[-1].strip()
                elif "Job ID" in line and "(PC)" in line and not job_val:
                    job_val = clean_line.split(":", 1)[-1].strip()

        for embed in message.embeds:
            for field in embed.to_dict().get("fields", []):
                name_field = field.get("name", "").replace("```", "").strip()
                value_field = field.get("value", "").replace("```", "").strip()
                if "Name" in name_field and not name_val:
                    name_val = value_field
                if "Money per sec" in name_field and not money_val:
                    money_val = value_field
                if "Job ID" in name_field and "(PC)" in name_field and not job_val:
                    job_val = value_field

        if name_val or money_val or job_val:
            log_msg = "\n📨 New Job Notification:\n------------------------"
            if name_val:
                log_msg += f"\n🏷️ Name: {name_val}"
            if money_val:
                log_msg += f"\n💰 Money/s: {money_val}"
            if job_val:
                log_msg += f"\n🆔 Job ID (PC): {job_val}"
            log_msg += "\n------------------------\n"

            self.log_signal.emit(log_msg)
            if job_val:
                self.job_signal.emit(job_val, name_val or "", log_msg)

    def run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.client.start(self.token, bot=False))
        except Exception as e:
            self.log_signal.emit(f"❌ Discord client stopped: {e}")

    def stop(self):
        self.running = False
        try:
            asyncio.run_coroutine_threadsafe(self.client.close(), self.loop)
        except Exception:
            pass
        self.status_signal.emit(False)


# ================= Main GUI =================
class MonitorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("V4 AUTOJOINER")
        self.setMinimumSize(950, 650)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #0b0b1f, stop:1 #1a1a40);
                color: #f0f0ff; font-family: Poppins;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        header = QLabel("🚀 EX Hub Monitor")
        header.setFont(QFont("Poppins", 28, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff79c6, stop:1 #ff2e63);")
        main_layout.addWidget(header)

        cfg = load_config()

        input_frame = QFrame()
        input_frame.setStyleSheet("QFrame { background: rgba(27,27,58,0.6); border-radius: 12px; }")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)

        self.token_input = QLineEdit(cfg.get("token", ""))
        self.token_input.setPlaceholderText("Discord User Token")
        self.channel_dropdown = QComboBox()
        self.channel_dropdown.addItems(CHANNELS.keys())
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter Name or Min Money/s (e.g., 60, Los Bombinitos)")

        input_layout.addWidget(self.token_input)
        input_layout.addWidget(self.channel_dropdown)
        input_layout.addWidget(self.filter_input)

        self.brainrot_btn = QPushButton("⚙️")
        self.brainrot_btn.setStyleSheet("""
            QPushButton { background: rgba(255,121,198,0.3); border:1px solid #ff79c6;
            color:#f0f0ff; border-radius:8px; min-height:32px; padding:4px 12px; }
            QPushButton:hover { background: rgba(255,121,198,0.6); }
        """)
        input_layout.addWidget(self.brainrot_btn)

        self.brainrot_dropdown = QComboBox()
        self.brainrot_dropdown.addItem("All Brainrot Names")
        self.brainrot_dropdown.addItems(BRAINROT_NAMES)
        self.brainrot_dropdown.setVisible(False)
        self.brainrot_dropdown.setStyleSheet("""
            QComboBox { background: rgba(27,27,58,0.7); color: #f0f0ff; border: 1px solid #ff79c6; border-radius: 8px; padding: 4px;}
            QComboBox QAbstractItemView { background: #1b1b3a; color: #f0f0ff; selection-background-color: #ff79c6; }
        """)
        input_layout.addWidget(self.brainrot_dropdown)

        self.exclude_dropdown = QComboBox()
        self.exclude_dropdown.addItem("No Exclude")
        self.exclude_dropdown.addItems(EXCLUDE_BRAINROTS)
        self.exclude_dropdown.setStyleSheet("""
            QComboBox { background: rgba(27,27,58,0.7); color: #f0f0ff; border: 1px solid #ff2e63; border-radius: 8px; padding: 4px;}
        """)
        input_layout.addWidget(self.exclude_dropdown)

        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("Custom Exclude (e.g., Bombinitos)")
        input_layout.addWidget(self.exclude_input)

        self.brainrot_btn.clicked.connect(lambda: self.brainrot_dropdown.setVisible(not self.brainrot_dropdown.isVisible()))

        self.toggle_btn = QPushButton("Start Monitor")
        self.clear_btn = QPushButton("Clear Logs")
        for btn in [self.toggle_btn, self.clear_btn]:
            btn.setStyleSheet("""
                QPushButton { background: rgba(255, 121, 198,0.3); border: 1px solid #ff79c6;
                color: #f0f0ff; border-radius: 10px; min-height: 36px; padding: 6px 14px; }
                QPushButton:hover { background: rgba(255, 121, 198,0.6); }
            """)
        input_layout.addWidget(self.toggle_btn)
        input_layout.addWidget(self.clear_btn)

        main_layout.addWidget(input_frame)

        self.status_label = QLabel("Stopped")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background-color:#ff2e63; color:white; border-radius:12px; padding:6px;")
        main_layout.addWidget(self.status_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background: rgba(27,27,58,0.6);
                color:#f0f0ff;
                border-radius:12px;
                padding:10px;
            }
            QScrollBar:vertical {
                background: #1b1b3a;
                width: 10px;
                margin: 4px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #ff79c6;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff2e63;
            }
        """)
        main_layout.addWidget(self.log_area)

        self.toggle_btn.clicked.connect(self.toggle_monitor)
        self.clear_btn.clicked.connect(lambda: self.log_area.clear())

        self.monitor_thread = None
        self.monitor_running = False

    # ========= Shared Filter Function =========
    def passes_filter(self, message: str, job_id: str = None, name_val: str = None) -> bool:
        filter_text = self.filter_input.text().strip().lower()
        passed = False

        if not filter_text:
            passed = True
        else:
            if filter_text.replace(".", "", 1).isdigit():
                try:
                    min_val = float(filter_text)
                    match = re.search(r"💰 Money/s: ([^\n]+)", message)
                    if match:
                        money_val = DiscordMonitor.parse_money(match.group(1).strip())
                        if money_val >= min_val:
                            passed = True
                except:
                    pass
            else:
                if filter_text in message.lower():
                    passed = True

        selected_brainrot = self.brainrot_dropdown.currentText()
        if selected_brainrot != "All Brainrot Names":
            if selected_brainrot.lower() not in (message or "").lower():
                passed = False

        exclude_choice = self.exclude_dropdown.currentText()
        if exclude_choice != "No Exclude" and exclude_choice.lower() in (message or "").lower():
            passed = False

        custom_ex = self.exclude_input.text().strip().lower()
        if custom_ex and custom_ex in (message or "").lower():
            passed = False

        return passed

    def append_log(self, text):
        self.log_area.append(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def update_status(self, running: bool):
        self.monitor_running = running
        if running:
            self.status_label.setText("Running")
            self.status_label.setStyleSheet("background-color:#10d27a; color:black; border-radius:12px; padding:6px;")
            self.toggle_btn.setText("Stop Monitor")
        else:
            self.status_label.setText("Stopped")
            self.status_label.setStyleSheet("background-color:#ff2e63; color:white; border-radius:12px; padding:6px;")
            self.toggle_btn.setText("Start Monitor")

    def toggle_monitor(self):
        if not self.monitor_running:
            token = self.token_input.text().strip()
            if not token:
                self.append_log("❌ Please enter your Discord token.")
                return
            save_config({"token": token})
            channel_name = self.channel_dropdown.currentText()
            channel_id = CHANNELS[channel_name]
            self.append_log(f"✅ Starting monitor on {channel_name}...")
            self.monitor_thread = DiscordMonitor(token, channel_id)
            self.monitor_thread.log_signal.connect(self.filtered_log)
            self.monitor_thread.status_signal.connect(self.update_status)
            self.monitor_thread.job_signal.connect(self.copy_job_if_passes)
            self.monitor_thread.start()
        else:
            if self.monitor_thread:
                self.monitor_thread.stop()
                self.append_log("🛑 Monitor stopped.")

    def filtered_log(self, message):
        if self.passes_filter(message):
            self.append_log(message)

    def copy_job_if_passes(self, job_id, name_val, full_message):
        if self.passes_filter(full_message, job_id, name_val):
            try:
                pyperclip.copy(job_id)
                send_job_to_ws(job_id)  # <-- Only send if passes filters
                self.append_log(f"📋 Copied Job ID: {job_id}")
            except Exception as e:
                self.append_log(f"⚠️ Failed to copy job id: {e}")


# ================= Run =================
if __name__ == "__main__":
    start_ws_background()
    app = QApplication(sys.argv)
    window = MonitorUI()
    window.show()
    sys.exit(app.exec())
