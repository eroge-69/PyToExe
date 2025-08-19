from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
import os
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from pystray import Icon, MenuItem, Menu
from PIL import Image

# =====================
# Config bestand
# =====================
CONFIG_FILE = "config.json"
default_config = {
    "GAME_VOLUME_NORMAL": 1.0,
    "GAME_VOLUME_FLASHED": 0.0,
    "FLASH_HOLD_TIME": 0.5,
    "flash_sound_enabled": True,
    "round_sound_enabled": True,
    "ICON_PATH": r"C:\Users\Fjern\Documents\Fjern\CS2 sound fix pogin\Icon.ico",
    "FLASH_MODE": 2
}

# Eerste keer opstarten: config aanmaken als die nog niet bestaat
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

# Config laden
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# =====================
# Config variabelen
# =====================
PORT = 3202
PROC_NAME = "cs2.exe"
GAME_VOLUME_NORMAL = config.get("GAME_VOLUME_NORMAL", 1.0)
GAME_VOLUME_FLASHED = config.get("GAME_VOLUME_FLASHED", 0.0)
FLASH_HOLD_TIME = config.get("FLASH_HOLD_TIME", 0.5)
flash_sound_enabled = config.get("flash_sound_enabled", True)
round_sound_enabled = config.get("round_sound_enabled", True)
ICON_PATH = config.get("ICON_PATH", r"C:\Users\Fjern\Documents\Fjern\CS2 sound fix pogin\Icon.ico")
FLASH_MODE = config.get("FLASH_MODE", 1)
CHECK_INTERVAL = 0.02  # 20 ms polling

# =====================
# Functie om alleen CS2-volume aan te passen
# =====================
def set_volume(level: float) -> bool:
    level = max(0.0, min(1.0, float(level)))
    sessions = AudioUtilities.GetAllSessions()
    found = False
    for session in sessions:
        try:
            if session.Process and session.Process.name().lower() == PROC_NAME:
                s = session._ctl.QueryInterface(ISimpleAudioVolume)
                s.SetMute(0, None)
                s.SetMasterVolume(level, None)
                found = True
        except Exception:
            pass
    return found

# =====================
# Globale status
# =====================
player_state = {'flashed': 0, 'health': 100}
round_state = {'phase': ''}
last_flash_time = 0.0
current_volume = GAME_VOLUME_NORMAL
lock = threading.Lock()

# =====================
# Smooth fade functie naar normaal
# =====================
def fade_to_normal():
    global current_volume
    target = GAME_VOLUME_NORMAL
    step = 0.01
    interval = 0.01
    while current_volume < target:
        current_volume = min(current_volume + step, target)
        set_volume(current_volume)
        time.sleep(interval)

# =====================
# Flash volume functie met twee modes en directe demping
# =====================
def set_volume_based_on_flash():
    global current_volume
    flashed = player_state.get('flashed', 0)  # 0-255
    if flashed > 0 and flash_sound_enabled:
        if FLASH_MODE == 1:
            # directe vaste demping
            if current_volume != GAME_VOLUME_FLASHED:
                current_volume = GAME_VOLUME_FLASHED
                set_volume(current_volume)
        elif FLASH_MODE == 2:
            # dynamische demping op basis van witpunt
            target_volume = GAME_VOLUME_NORMAL - (flashed / 255) * (GAME_VOLUME_NORMAL - GAME_VOLUME_FLASHED)
            if abs(current_volume - target_volume) > 0.01:
                current_volume = target_volume
                set_volume(current_volume)

# =====================
# HTTP-handler voor GSI
# =====================
class GSIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global player_state, round_state
        content_length = int(self.headers.get('Content-Length', '0') or 0)
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            with lock:
                player_state = data.get('player', {}).get('state', {}) or {}
                round_state = data.get('round', {}) or {}
        except json.JSONDecodeError:
            pass
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

# =====================
# Continu monitoren en volume aanpassen
# =====================
def monitor_flash():
    global last_flash_time, current_volume
    while True:
        with lock:
            flashed = player_state.get('flashed', 0)
            health = player_state.get('health', 100)
            phase = round_state.get('phase', "")
        now = time.time()

        # Round start of respawn: volume reset
        if round_sound_enabled and phase == "live" and health > 0:
            if current_volume != GAME_VOLUME_NORMAL:
                fade_to_normal()

        # Flash logica
        if flash_sound_enabled and flashed > 0:
            last_flash_time = now
            set_volume_based_on_flash()
        else:
            if now - last_flash_time >= FLASH_HOLD_TIME:
                if current_volume < GAME_VOLUME_NORMAL:
                    fade_to_normal()

        time.sleep(CHECK_INTERVAL)

# =====================
# Server starten met error popup als poort in gebruik
# =====================
def run_server():
    server_address = ('', PORT)
    try:
        httpd = HTTPServer(server_address, GSIHandler)
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # WSAEADDRINUSE
            ctypes.windll.user32.MessageBoxW(0,
                f"Poort {PORT} is al in gebruik!\nSluit andere instantie van CS2 Sound Fix.",
                "CS2 Sound Fix Error",
                0x10)  # MB_ICONERROR
        else:
            raise

# =====================
# Tray-menu functies
# =====================
def toggle_flash_sound(icon, item):
    global flash_sound_enabled
    flash_sound_enabled = not flash_sound_enabled

def toggle_round_sound(icon, item):
    global round_sound_enabled
    round_sound_enabled = not round_sound_enabled

def on_quit(icon, item):
    icon.stop()

# =====================
# Tray-app starten
# =====================
def start_monitoring():
    threading.Thread(target=monitor_flash, daemon=True).start()
    run_server()

# Icon laden
image = Image.open(ICON_PATH)

menu = Menu(
    MenuItem("Flash Sound", toggle_flash_sound, checked=lambda item: flash_sound_enabled),
    MenuItem("Round Sound", toggle_round_sound, checked=lambda item: round_sound_enabled),
    MenuItem("Quit", on_quit)
)
icon = Icon("CS2 Flash Volume", image, "CS2 Flash Volume", menu)

threading.Thread(target=start_monitoring, daemon=True).start()
icon.run()
