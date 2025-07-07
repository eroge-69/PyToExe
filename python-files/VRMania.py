from kivy.core.window import Window

# Make sure fullscreen is enabled:
Window.fullscreen = True

# Then set the size to match the display:
import ctypes
user32 = ctypes.windll.user32
w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
Window.size = (w, h)


import os
import sys
import json
import subprocess
import threading
import time
import random
from datetime import datetime
import serial
import serial.tools.list_ports
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window


# ==== ICON EXTRACTION ====
ICON_EXTRACTION_AVAILABLE = False
try:
    import win32api
    import win32con
    import win32ui
    import win32gui
    from PIL import Image as PILImage
    ICON_EXTRACTION_AVAILABLE = True
except ImportError:
    pass

def extract_icon_to_png(exe_path, out_png):
    if not ICON_EXTRACTION_AVAILABLE:
        return None
    large, small = win32gui.ExtractIconEx(exe_path, 0)
    hicon = None
    if large:
        hicon = large[0]
    elif small:
        hicon = small[0]
    else:
        return None
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
    hdc2 = hdc.CreateCompatibleDC()
    hdc2.SelectObject(hbmp)
    win32gui.DrawIconEx(hdc2.GetHandleOutput(), 0, 0, hicon, ico_x, ico_x, 0, None, win32con.DI_NORMAL)
    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    img = PILImage.frombuffer(
        'RGBA',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRA', 0, 1)
    #img = img.transpose(PILImage.FLIP_TOP_BOTTOM)
    img.save(out_png)
    win32gui.DestroyIcon(hicon)
    hdc2.DeleteDC()
    hbmp.DeleteObject()
    hdc.DeleteDC()
    return out_png

def get_best_icon_for_exe(exe_path):
    base = os.path.splitext(exe_path)[0]
    ico_path = base + ".ico"
    if os.path.isfile(ico_path):
        print("Using existing .ico:", ico_path)
        return ico_path
    # Try pyiress resource extraction (all icons)
    try:
        import pyiress
        out_folder = os.path.dirname(exe_path)
        icons = pyiress.extract_icons(exe_path, out_folder)
        if icons:
            best = max(icons, key=lambda x: x[1][0])
            print("Using extracted icon:", best[0])
            return best[0]
    except Exception as e:
        print("Resource icon extraction failed:", e)
    # Fallback to classic method
    icon_path = os.path.join(os.path.dirname(exe_path), os.path.basename(base) + "_icon.png")
    try:
        icon_file = extract_icon_to_png(exe_path, icon_path)
        if icon_file and os.path.exists(icon_file):
            print("Using fallback classic extracted icon:", icon_file)
            return icon_file
    except Exception as e:
        print("Classic icon extraction failed:", e)
    return ""

# ==== ENCRYPTION UTILITY ====
STORAGE_KEY = hashlib.sha256(b"UltraSecretVRManiaKey").digest()[:32]
def pad(s): n = AES.block_size - len(s) % AES.block_size; return s + bytes([n])*n
def unpad(s): return s[:-s[-1]]
def encrypt_bytes(data: bytes) -> str:
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(STORAGE_KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data))
    return base64.b64encode(iv + ct).decode("utf-8")
def decrypt_bytes(b64str: str) -> bytes:
    raw = base64.b64decode(b64str)
    iv, ct = raw[:AES.block_size], raw[AES.block_size:]
    cipher = AES.new(STORAGE_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct))
def load_encrypted_json(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r") as f: b64 = f.read()
    try: dec = decrypt_bytes(b64); return json.loads(dec.decode("utf-8"))
    except Exception: return []
def save_encrypted_json(filename, obj):
    enc = encrypt_bytes(json.dumps(obj).encode("utf-8"))
    with open(filename, "w") as f: f.write(enc)

def file_browser(select_callback, title="Select file", filetypes=None):
    import threading
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        tk = None
    if sys.platform == "win32" and tk:
        def tk_thread():
            root = tk.Tk(); root.withdraw()
            options = {'title': title}
            if filetypes: options['filetypes'] = filetypes
            filename = filedialog.askopenfilename(**options)
            root.destroy()
            if filename:
                Clock.schedule_once(lambda dt: select_callback(filename))
        threading.Thread(target=tk_thread).start()
    else:
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.boxlayout import BoxLayout
        box = BoxLayout(orientation='vertical', spacing=5)
        fc = FileChooserIconView(filters=["*.png","*.jpg","*.jpeg","*.bmp","*.ico","*.exe","*"], path=os.getcwd())
        box.add_widget(fc)
        def choose_fn(instance):
            if fc.selection:
                select_callback(fc.selection[0])
            popup.dismiss()
        box.add_widget(Button(text="Select", size_hint_y=None, height=40, on_release=choose_fn))
        popup = Popup(title=title, content=box, size_hint=(0.9, 0.9))
        popup.open()

GAMES_FILE = "games.json.enc"
MIN_COINS = 3
SUPPORTED_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".ico")
aes_keys = [
    [0x99, 0xD4, 0xB5, 0xD4, 0xCF, 0xBC, 0x0B, 0x26, 0x27, 0x7D, 0x73, 0x44, 0x7D, 0x46, 0x9B, 0x50],
    [0xD8, 0x45, 0xE2, 0x8C, 0x61, 0x6C, 0xF6, 0x95, 0x1B, 0x5D, 0xCD, 0x40, 0xA0, 0xE2, 0xB8, 0x78],
    [0x29, 0x81, 0xD2, 0xB1, 0x22, 0xF6, 0x1C, 0x2E, 0x76, 0x50, 0xE1, 0x1F, 0x2F, 0x2E, 0x98, 0x70],
    [0x40, 0xFE, 0xDA, 0x5A, 0xA7, 0x1C, 0xC7, 0x21, 0x62, 0xA8, 0x79, 0xAC, 0x9F, 0x67, 0xE9, 0x6D],
    [0x5E, 0x23, 0x10, 0x62, 0x9A, 0xA6, 0xA7, 0x7B, 0xC0, 0xAB, 0xF3, 0x1C, 0x60, 0x73, 0x90, 0x2A],
]
UART_FRAME_LEN = 20
START_BYTE = 0xAA
END_BYTE = 0x55
CHECKSUM_XOR_CONST = 0xA5
VID = 0x10C4
PID = 0xEA60
BAUDRATE = 9600
COIN_INC_CMD = 0x10
COIN_DEC_CMD = 0x11

def load_games(): return load_encrypted_json(GAMES_FILE)
def save_games(games): save_encrypted_json(GAMES_FILE, games)
def parse_frame(frame, algo=None):
    if len(frame) != UART_FRAME_LEN: return False, "Bad length", None
    if frame[0] != START_BYTE or frame[-1] != END_BYTE: return False, "Start/end byte error", None
    algo_idx = frame[1]
    if algo is not None: algo_idx = algo
    if not (0 <= algo_idx < len(aes_keys)): return False, "Bad key index", None
    key = bytes(aes_keys[algo_idx])
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(frame[2:18])
    checksum = 0
    for b in decrypted: checksum ^= b
    encrypted_checksum = frame[18]
    if (checksum ^ CHECKSUM_XOR_CONST) != encrypted_checksum: return False, "Checksum failed", None
    cmd = decrypted[0]
    payload = decrypted[1:]
    return True, cmd, payload
def list_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        if port.vid == VID and port.pid == PID:
            ports.append(port.device)
    return ports
def select_port():
    ports = list_ports()
    if not ports:
        print("No matching device found.")
        return None
    if len(ports) == 1:
        print(f"Using {ports[0]}")
        return ports[0]
    for i, p in enumerate(ports):
        print(f"{i+1}. {p}")
    sel = input("Select port [1]: ")
    sel = int(sel or "1") - 1
    return ports[sel]
def send_challenge_frame(ser):
    now = datetime.now()
    time_str = now.strftime("%H%M%S")
    command = 0x05
    payload = bytearray(16)
    payload[0] = command
    payload[1:7] = time_str.encode("ascii")
    key_index = random.randint(0, len(aes_keys)-1)
    key = bytes(aes_keys[key_index])
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(payload)
    frame = bytearray(20)
    frame[0] = START_BYTE
    frame[1] = key_index
    frame[2:18] = encrypted
    checksum = 0
    for b in payload:
        checksum ^= b
    frame[18] = checksum ^ CHECKSUM_XOR_CONST
    frame[19] = END_BYTE
    print(f"[UART TX] {frame.hex().upper()} | Challenge Time: {time_str}")
    ser.write(frame)
    return now, time_str

class GameCard(ButtonBehavior, BoxLayout):
    def __init__(self, img_path, game_name, coins_text, on_press_fn, can_play, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint_y = None
        self.height = 255
        self.padding = [1, 4, 1, 1]
        self.spacing = 0
        with self.canvas.before:
            from kivy.graphics import Color, Line
            if can_play: Color(0.2, 1, 0.3, 1)
            else: Color(1, 0.1, 0.1, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
        def update_border(*a): self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.bind(pos=update_border, size=update_border)
        img = Image(
            source=img_path if img_path and os.path.isfile(img_path) and img_path.lower().endswith(SUPPORTED_IMAGE_EXTS) else '',
            size_hint=(1, 0.75), allow_stretch=True, keep_ratio=True,
        )
        self.add_widget(img)
        name_lbl = Label(text=game_name, size_hint=(1, 0.13), halign='center', valign='middle', font_size=26, color=(1,1,1,1))
        name_lbl.bind(size=name_lbl.setter('text_size'))
        self.add_widget(name_lbl)
        coins_lbl = Label(text=coins_text, size_hint=(1, 0.12), halign='center', valign='middle', font_size=20, color=(0.13,0.45,0.92,1), markup=True)
        coins_lbl.bind(size=coins_lbl.setter('text_size'))
        self.add_widget(coins_lbl)
        self.on_release = on_press_fn

class HomeScreen(Screen):
    coins = 0
    selected_game = None
    game_proc = None
    timer_thread = None
    settings_visible = False
    serial_ref = None

    def on_pre_enter(self):
        self.ids.game_grid.clear_widgets()
        self.load_games()
        self.ids.coin_label.text = f"Coins: {self.coins}"
        self.ids.status.text = "Ready!"
        self.toggle_settings(self.settings_visible)

    def load_games(self):
        self.games = load_games()
        for idx, game in enumerate(self.games):
            icon_path = game.get('icon', '')
            name = game.get('name', 'Unknown')
            coins_required = game.get('coins_required', MIN_COINS)
            coins_text = f"[b]{self.coins} / {coins_required} coins[/b]"
            can_play = self.coins >= coins_required
            def make_launch(idx):
                return lambda *args: self.try_launch_game(idx)
            card = GameCard(
                img_path=icon_path,
                game_name=name,
                coins_text=coins_text,
                on_press_fn=make_launch(idx),
                can_play=can_play
            )
            self.ids.game_grid.add_widget(card)

    def insert_coin(self):
        self.coins += 1
        self.ids.coin_label.text = f"Coins: {self.coins}"
        self.ids.game_grid.clear_widgets()
        self.load_games()

    def decrement_coin(self):
        if self.coins > 0:
            self.coins -= 1
            self.ids.coin_label.text = f"Coins: {self.coins}"
            self.ids.game_grid.clear_widgets()
            self.load_games()

    def get_session_seconds(self, game=None):
        if game is not None:
            try:
                gamewise = int(game.get('playtime', 0))
                if gamewise > 0:
                    return gamewise * 60
            except Exception:
                pass
        try:
            s = int(self.ids.sec_input.text)
        except Exception:
            return 180
        return max(min(s, 9999), 1)

    def try_launch_game(self, idx):
        if self.game_proc and self.game_proc.poll() is None:
            self.ids.status.text = "A game is already running. Please close it first."
            return
        coins_needed = self.games[idx].get('coins_required', MIN_COINS)
        if self.coins < coins_needed:
            self.ids.status.text = f"Insert {coins_needed - self.coins} more coins to play."
            return
        self.launch_game(idx, coins_needed)

    def launch_game(self, idx, coins_needed):
        game = self.games[idx]
        self.selected_game = game
        self.ids.status.text = f"Launching {game['name']} ..."
        try:
            self.game_proc = subprocess.Popen([game['path']] + (game.get('args','').split() if game.get('args') else []))
        except Exception as e:
            self.ids.status.text = f"Failed to launch {game['name']}: {e}"
            return
        self.coins -= coins_needed
        self.ids.coin_label.text = f"Coins: {self.coins}"
        self.ids.game_grid.clear_widgets()
        self.load_games()
        session_seconds = self.get_session_seconds(game)
        self.timer_thread = threading.Thread(target=self.session_timer, args=(session_seconds,), daemon=True)
        self.timer_thread.start()

    def session_timer(self, session_seconds):
        for i in range(session_seconds, 0, -1):
            if self.game_proc and self.game_proc.poll() is not None:
                Clock.schedule_once(lambda dt: self.update_status("Game exited."))
                return
            msg = f"Playing {self.selected_game['name']} - Time left: {i} sec"
            Clock.schedule_once(lambda dt: self.update_status(msg))
            time.sleep(1)
        Clock.schedule_once(lambda dt: self.update_status("Session over! Closing game..."))
        if self.game_proc and self.game_proc.poll() is None:
            try:
                self.game_proc.terminate()
                Clock.schedule_once(lambda dt: self.update_status("Game closed!"))
            except Exception:
                Clock.schedule_once(lambda dt: self.update_status("Failed to close game. Please close manually."))

    @mainthread
    def update_status(self, msg):
        self.ids.status.text = msg

    @mainthread
    def coin_inc(self):
        self.insert_coin()

    @mainthread
    def coin_dec(self):
        self.decrement_coin()

    def open_manage(self):
        self.manager.get_screen('managegames').refresh_list()
        self.manager.current = 'managegames'

    def toggle_settings(self, show):
        self.settings_visible = show
        try:
            self.ids.play_time_box.opacity = 1 if show else 0
            self.ids.manage_btn.opacity = 1 if show else 0
            self.ids.play_time_box.disabled = not show
            self.ids.manage_btn.disabled = not show
        except Exception:
            pass

class ManageGamesScreen(Screen):
    challenge_status_color = ListProperty([1, 0, 0, 1])
    settings_visible = False
    serial_ref = None

    def on_pre_enter(self):
        self.refresh_list()
        self.toggle_settings(self.settings_visible)

    def refresh_list(self):
        self.ids.games_list.clear_widgets()
        self.games = load_games()
        for idx, game in enumerate(self.games):
            hbox = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=6)
            icon_path = game.get('icon', '')
            img = Image(source=icon_path if icon_path and os.path.isfile(icon_path) and icon_path.lower().endswith(SUPPORTED_IMAGE_EXTS) else '', size_hint=(None, 1), width=38)
            hbox.add_widget(img)
            hbox.add_widget(Label(text=game.get('name', 'Unknown'), size_hint_x=0.45, halign='left', valign='middle', font_size=26, color=(1,1,1,1)))
            hbox.add_widget(Label(text=f"Coins Needed: {game.get('coins_required', MIN_COINS)}", size_hint_x=0.23, font_size=26, color=(0.65,0.9,1,1)))
            edit_btn = Button(
                text="Edit", size_hint=(None, 1), width=65, font_size=20,
                background_normal='', background_color=(0.14,0.51,0.88,0.9),
                color=(1,1,1,1),
                on_release=lambda btn, i=idx: self.edit_game(i)
            )
            del_btn = Button(
                text="Delete", size_hint=(None, 1), width=65, font_size=20,
                background_normal='', background_color=(0.95,0.22,0.2,0.95),
                color=(1,1,1,1),
                on_release=lambda btn, i=idx: self.delete_game(i)
            )
            hbox.add_widget(edit_btn)
            hbox.add_widget(del_btn)
            self.ids.games_list.add_widget(hbox)

    def add_game(self):
        EditGamePopup(on_save=self.save_new_game).open()

    def edit_game(self, idx):
        games = load_games()
        EditGamePopup(game=games[idx], on_save=lambda data: self.save_edit_game(idx, data)).open()

    def save_new_game(self, data):
        games = load_games()
        games.append(data)
        save_games(games)
        self.refresh_list()

    def save_edit_game(self, idx, data):
        games = load_games()
        games[idx] = data
        save_games(games)
        self.refresh_list()

    def delete_game(self, idx):
        games = load_games()
        games.pop(idx)
        save_games(games)
        self.refresh_list()

    def back(self):
        self.manager.current = "home"

    def toggle_settings(self, show):
        self.settings_visible = show
        try:
            self.ids.add_game_btn.opacity = 1 if show else 0
            self.ids.add_game_btn.disabled = not show
        except Exception:
            pass

class EditGamePopup(Popup):
    def __init__(self, game=None, on_save=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Edit Game" if game else "Add Game"
        self.size_hint = (0.7, 0.92)
        self.auto_dismiss = False
        self.on_save = on_save
        self.game = game or {"name": "", "path": "", "icon": "", "args": "", "playtime": 15, "coins_required": MIN_COINS}
        layout = BoxLayout(orientation="vertical", spacing=8, padding=10)

        layout.add_widget(Label(text="Game Name:", color=(1,1,1,1)))
        self.name_input = TextInput(text=self.game['name'], multiline=False, size_hint_y=None, height=32, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        layout.add_widget(self.name_input)

        layout.add_widget(Label(text="Executable Path:", color=(1,1,1,1)))
        path_box = BoxLayout(size_hint_y=None, height=36, spacing=4)
        self.path_input = TextInput(text=self.game['path'], multiline=False, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        choose_path = Button(text="Browse", size_hint=(None, 1), width=60,
                             background_normal='', background_color=(0.14,0.51,0.88,0.9), color=(1,1,1,1))
        choose_path.bind(on_release=lambda *a: file_browser(self.set_exe_path, "Select Game Executable", [("Executable", "*.exe" if sys.platform == "win32" else "*")]))
        path_box.add_widget(self.path_input)
        path_box.add_widget(choose_path)
        layout.add_widget(path_box)

        layout.add_widget(Label(text="Icon:", color=(1,1,1,1)))
        icon_box = BoxLayout(size_hint_y=None, height=36, spacing=4)
        self.icon_input = TextInput(text=self.game['icon'], multiline=False, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        choose_icon = Button(text="Browse", size_hint=(None, 1), width=60,
                             background_normal='', background_color=(0.14,0.51,0.88,0.9), color=(1,1,1,1))
        choose_icon.bind(on_release=lambda *a: file_browser(self.set_icon_path, "Select Icon", [("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.ico")]))
        icon_box.add_widget(self.icon_input)
        icon_box.add_widget(choose_icon)
        layout.add_widget(icon_box)

        self.icon_preview = Image(source=self.game['icon'], size_hint=(1, None), height=48)
        layout.add_widget(self.icon_preview)

        layout.add_widget(Label(text="Launch Arguments (optional):", color=(1,1,1,1)))
        self.args_input = TextInput(text=self.game.get('args', ''), multiline=False, size_hint_y=None, height=32, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        layout.add_widget(self.args_input)

        layout.add_widget(Label(text="Coins Required:", color=(1,1,1,1)))
        self.coins_required_input = TextInput(text=str(self.game.get('coins_required', MIN_COINS)), multiline=False, input_filter='int', size_hint_y=None, height=32, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        layout.add_widget(self.coins_required_input)

        layout.add_widget(Label(text="Playtime (min, 0 for global):", color=(1,1,1,1)))
        self.playtime_input = TextInput(text=str(self.game.get('playtime', 0)), multiline=False, input_filter='int', size_hint_y=None, height=32, foreground_color=(0.12,0.6,0.93,1), background_color=(0.12,0.12,0.23,0.95))
        layout.add_widget(self.playtime_input)

        btn_box = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        btn_box.add_widget(Button(text="Cancel", on_release=lambda *a: self.dismiss(), background_normal='', background_color=(0.19,0.21,0.27,1), color=(1,1,1,1)))
        btn_box.add_widget(Button(text="Save", on_release=self.save, background_normal='', background_color=(0.14,0.51,0.88,0.97), color=(1,1,1,1)))
        layout.add_widget(btn_box)
        self.content = layout

    @mainthread
    def set_exe_path(self, path):
        self.path_input.text = path
        icon_file = ""
        if path and path.lower().endswith(".exe"):
            icon_file = get_best_icon_for_exe(path)
        if icon_file and os.path.exists(icon_file):
            self.icon_input.text = icon_file
            self.icon_preview.source = icon_file
        else:
            self.icon_input.text = ""
            self.icon_preview.source = ""
    @mainthread
    def set_icon_path(self, path):
        if path and os.path.isfile(path) and path.lower().endswith(tuple(SUPPORTED_IMAGE_EXTS)):
            self.icon_input.text = path
            self.icon_preview.source = path
        else:
            self.icon_input.text = ""
            self.icon_preview.source = ""
    def save(self, *a):
        try:
            playtime = int(self.playtime_input.text)
        except Exception:
            playtime = 0
        try:
            coins_required = int(self.coins_required_input.text)
        except Exception:
            coins_required = MIN_COINS
        data = {
            "name": self.name_input.text,
            "path": self.path_input.text,
            "icon": self.icon_input.text,
            "args": self.args_input.text,
            "playtime": playtime,
            "coins_required": coins_required,
        }
        if (not data["icon"] and os.path.isfile(data["path"]) and data["path"].lower().endswith(".exe")):
            base_icon = os.path.splitext(os.path.basename(data["path"]))[0]
            icon_path = os.path.join(os.path.dirname(data["path"]), f"{base_icon}_icon.png")
            try:
                icon_file = extract_icon_to_png(data["path"], icon_path)
                if icon_file and os.path.exists(icon_file):
                    data["icon"] = icon_file
                    self.icon_input.text = icon_file
                    self.icon_preview.source = icon_file
            except Exception as e:
                print("Could not extract icon:", e)
        if self.on_save:
            self.on_save(data)
        self.dismiss()

serial_port_instance = None

def serial_listener(port, home_screen, stop_event):
    global serial_port_instance
    if port is None:
        return
    try:
        with serial.Serial(port, BAUDRATE, timeout=0.1) as ser:
            serial_port_instance = ser
            home_screen.serial_ref = ser
            rx = b''
            while not stop_event.is_set():
                rx += ser.read(ser.in_waiting or 1)
                while len(rx) >= UART_FRAME_LEN:
                    frame = rx[:UART_FRAME_LEN]
                    rx = rx[UART_FRAME_LEN:]
                    print(f"[UART RX] {frame.hex().upper()}")
                    ok, cmd, payload = parse_frame(frame)
                    print("[Parsed]", ok, f"CMD: 0x{cmd:02X}" if ok else cmd, payload.hex() if (ok and payload) else payload)
                    if ok:
                        if cmd == 0x04:
                            if len(payload) and payload[0] == 0x2B:
                                Clock.schedule_once(lambda dt: home_screen.coin_inc())
                            elif len(payload) and payload[0] == 0x2D:
                                Clock.schedule_once(lambda dt: home_screen.coin_dec())
                        elif cmd == 0x05:
                            Clock.schedule_once(lambda dt: App.get_running_app().handle_challenge_response(payload))
                time.sleep(0.01)
    except Exception as e:
        print(f"Serial error: {e}")

class ArcadeApp(App):
    challenge_status_color = ListProperty([1, 0, 0, 1])
    challenge_waiting = BooleanProperty(False)
    challenge_sent_time = ObjectProperty(None)
    challenge_timeout_event = ObjectProperty(None)
    last_challenge_time_str = ""
    challenge_sent_dt = ObjectProperty(None)
    challenge_clock = ObjectProperty(None)
    challenge_fail_count = 0

    def build(self):
        Window.title = "VR Mania"
        Builder.load_string('''
#:kivy 2.2.0

<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.6, 1, 1
        Triangle:
            points: [self.x, self.y, self.x, self.top, self.center_x, self.top]
        Color:
            rgba: 0.6, 0.5, 1, 1
        Triangle:
            points: [self.x, self.y, self.right, self.y, self.right, self.top, self.center_x, self.top]
    FloatLayout:
        size: root.size
        Widget:
            size_hint: None, None
            size: 24, 24
            pos_hint: {'x': 0.01, 'top': 0.97}
            canvas:
                Color:
                    rgba: app.challenge_status_color
                Ellipse:
                    pos: self.pos
                    size: self.size
        BoxLayout:
            orientation: "vertical"
            spacing: 2
            padding: [2, 2, 2, 2]
            size_hint: 1, 1
            BoxLayout:
                size_hint_y: None
                height: 150
                            
                Widget:
                    size_hint_x: 0.15
                Image:
                    source: "VRMania.png"
                    allow_stretch: True
                    keep_ratio: True
                    size_hint: None, None
                    width: 500
                    height: 150
                Widget:
                    size_hint_x: 0.15
                Button:
                    id: manage_btn
                    text: "Manage Games"
                    size_hint_x: None
                    width: 150
                    size_hint_y: None
                    height: 50         # <--- FIX
                    font_size: 20
                    background_normal: ''
                    background_color: 0.902, 0.721, 0, 1
                    color: 1,1,1,1
                    on_release: root.open_manage()
            BoxLayout:
                spacing: 2
                size_hint_y: None
                height: 38
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_x: 0.2
                    Label:
                        id: coin_label
                        text: "Coins: 0"
                        width: 120
                        font_size: 48
                        color: 1, 0, 0, 1
                BoxLayout:
                    id: play_time_box
                    orientation: "horizontal"
                    spacing: 1
                    Label:
                        text: "Play Time:"
                        size_hint_x: None
                        width: 240
                        font_size: 40
                        color: 1,1,1,1
                    TextInput:
                        id: sec_input
                        text: "180"
                        input_filter: 'int'
                        size_hint_x: None
                        width: 72
                        multiline: False
                        font_size: 26
                        foreground_color: 0.12,0.6,0.93,1
                        background_color: 0.12,0.12,0.23,0.95
            ScrollView:
                do_scroll_x: False
                GridLayout:
                    id: game_grid
                    cols: 3
                    spacing: 8
                    padding: [2,2]
                    size_hint_y: None
                    height: self.minimum_height
            Label:
                id: status
                text: ""
                size_hint_y: None
                height: 28
                font_size: 16
                color: 1,1,1,1

<ManageGamesScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.6, 1, 1
        Triangle:
            points: [self.x, self.y, self.x, self.top, self.center_x, self.top]
        Color:
            rgba: 0.6, 0.5, 1, 1
        Triangle:
            points: [self.x, self.y, self.right, self.y, self.right, self.top, self.center_x, self.top]
    BoxLayout:
        orientation: "vertical"
        spacing: 2
        padding: [2, 20, 2, 2]
        BoxLayout:
            size_hint_y: None
            height: 54
            Label:
                text: "Manage Games"
                font_size: 48
                halign: "center"
                valign: "middle"
                color: 1,1,1,1
                background_color: 0.12,0.6,0.93,0.96                            
            Button:
                id: add_game_btn
                text: "Add Game"
                size_hint_x: None
                width: 100
                font_size: 20
                background_normal: ''
                background_color: 0.12,0.6,0.93,0.96
                color: 1,1,1,1
                on_release: root.add_game()
            Button:
                text: "Back"
                size_hint_x: None
                width: 88
                font_size: 20
                background_normal: ''
                background_color: 0.19,0.21,0.27,1
                color: 1,1,1,1
                on_release: root.back()
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: games_list
                orientation: "vertical"
                spacing: 3
                padding: [2,2]
                size_hint_y: None
                height: self.minimum_height

''')
        sm = ScreenManager(transition=FadeTransition())
        home = HomeScreen(name='home')
        manage = ManageGamesScreen(name='managegames')
        sm.add_widget(home)
        sm.add_widget(manage)
        port = select_port()
        stop_event = threading.Event()
        t = threading.Thread(target=serial_listener, args=(port, home, stop_event), daemon=True)
        t.start()
        self.stop_event = stop_event

        self.challenge_status_color = [1, 0, 0, 1]
        self.challenge_waiting = False
        self.challenge_sent_time = None
        self.challenge_timeout_event = None
        self.last_challenge_time_str = ""
        self.challenge_sent_dt = None
        self.challenge_clock = Clock.schedule_interval(self.start_challenge, 5)
        self.challenge_fail_count = 0

        self.operator_settings = False
        Window.bind(on_key_down=self.on_key_down)
        self.sm = sm
        return sm

    def start_challenge(self, dt=None):
        global serial_port_instance
        if not serial_port_instance:
            return
        self.challenge_waiting = True
        self.challenge_sent_dt, self.last_challenge_time_str = send_challenge_frame(serial_port_instance)
        self.challenge_status_color = [1, 1, 0, 1]
        if self.challenge_timeout_event:
            self.challenge_timeout_event.cancel()
        self.challenge_timeout_event = Clock.schedule_once(self.challenge_timeout, 2)

    def handle_challenge_response(self, payload):
        try:
            payload_time = payload[:6].decode("ascii")
        except Exception:
            payload_time = None
        try:
            expected_str = str(int(self.last_challenge_time_str) + 5).zfill(6)
        except Exception:
            expected_str = None
        print(f"[DEBUG] Received Challenge Response: {payload_time} | Expected: {expected_str}")
        if self.challenge_waiting and payload_time == expected_str:
            self.challenge_waiting = False
            self.challenge_status_color = [0, 1, 0, 1]
            self.challenge_fail_count = 0
            if self.challenge_timeout_event:
                self.challenge_timeout_event.cancel()

    def challenge_timeout(self, *a):
        if self.challenge_waiting:
            self.challenge_waiting = False
            self.challenge_status_color = [1, 0, 0, 1]
            self.challenge_fail_count += 1
            print("[CHALLENGE] Timeout. Dongle not found!")
            if self.challenge_fail_count >= 2:
                Popup(
                    title="Dongle Error",
                    content=Label(text="No dongle detected. Please insert dongle and restart the software!", font_size=16),
                    size_hint=(0.7, 0.25)
                ).open()

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if ('ctrl' in modifiers and 'shift' in modifiers and codepoint == 's'):
            self.operator_settings = not self.operator_settings
            for screen in self.sm.screens:
                if hasattr(screen, "toggle_settings"):
                    screen.toggle_settings(self.operator_settings)
        return False

    def on_stop(self):
        if hasattr(self, 'stop_event'):
            self.stop_event.set()

if __name__ == '__main__':
    ArcadeApp().run()
