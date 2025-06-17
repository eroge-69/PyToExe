import cv2
import numpy as np
from mss import mss
import time
import torch
import threading
import win32api
import math
import os
import ctypes
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from ultralytics import YOLO
from pypresence import Presence
import serial  # NEU: Für serielle Kommunikation
import serial.tools.list_ports  # NEU: Für die Auflistung der seriellen Ports

# --- Automatische Konfiguration ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

SCREEN_WIDTH = win32api.GetSystemMetrics(0)
SCREEN_HEIGHT = win32api.GetSystemMetrics(1)
INITIAL_FOV_SIZE = 350

# --- Einstellungen ---
PT_MODEL_PATH = 'best.pt'
TENSORRT_ENGINE_PATH = 'best.engine'

# Hotkeys
QUIT_KEY = 0x71        # F2
KEY_MAP = {0x01: "LMB", 0x02: "RMB", 0x04: "MMB", 0x05: "X1", 0x06: "X2"}
for i in range(0x41, 0x5B):
    KEY_MAP[i] = chr(i)

# Styling
COLORS = {"background": "#08080A", "sidebar": "#1A1A1A", "content": "#212121", "accent": "#0487FC", "text": "#EAEAEA", "text_green": "#2ECC71", "text_red": "#E74C3C", "widget_gray": "#333333"}
FONTS = {"title": ("Roboto", 14, "bold"), "body": ("Roboto", 12)}
ESP_COLORS = {"Blau": "#0487FC", "Rot": "#E74C3C", "Grün": "#2ECC71", "Pink": "#F08080", "Gelb": "#F1C40F"}

# Logik
AIM_POINT_PERCENTAGES = {"Head": 0.15, "Neck": 0.25, "Body": 0.50, "Feet": 0.90}
INVERTED_TARGET_MAP = {"Head": "Feet", "Neck": "Body", "Body": "Neck", "Feet": "Head"}

# --- NEU: Discord Rich Presence Thread ---
class DiscordPresenceThread(threading.Thread):
    def __init__(self, client_id):
        super().__init__(daemon=True)
        self.client_id = client_id
        self.rpc = None
        self.running = True

    def run(self):
        while self.running:
            try:
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                print("[INFO] Discord Rich Presence verbunden.")
                start_time = int(time.time())
                while self.running:
                    self.rpc.update(
                        state="Best Ai on Market",
                        details="RedDolphin AI",
                        start=start_time,
                        large_image="verified",
                        small_image="https://media.tenor.com/WQ67K3ynhV0AAAAd/verified.gif",
                        large_text="RedDolphin Suite"
                    )
                    time.sleep(15)
            except Exception as e:
                print(f"[WARNUNG] Discord Verbindung fehlgeschlagen: {e}. Versuche in 30s erneut.")
                time.sleep(30)
            finally:
                if self.rpc:
                    self.rpc.close()

    def stop(self):
        self.running = False
        if self.rpc:
            self.rpc.close()
        print("[INFO] Discord Rich Presence getrennt.")

# --- NEU: Arduino Maussteuerung Thread ---
class ArduinoMouseControl:
    def __init__(self):
        self.ser = None
        self.port = None
        self.baud_rate = 115200  # Standard-Baudrate für Arduino
        self.connected = False
        self.lock = threading.Lock() # Um Race Conditions beim Verbinden/Trennen zu vermeiden

    def connect(self, port):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.disconnect()
            try:
                self.ser = serial.Serial(port, self.baud_rate, timeout=0.01)
                self.port = port
                self.connected = True
                print(f"[INFO] Arduino verbunden auf {port}")
                return True
            except serial.SerialException as e:
                print(f"[FEHLER] Arduino Verbindung fehlgeschlagen auf {port}: {e}")
                self.connected = False
                return False

    def disconnect(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.connected = False
                print(f"[INFO] Arduino Verbindung getrennt von {self.port}")
                self.port = None

    def move_mouse(self, dx, dy):
        with self.lock:
            if self.connected and self.ser.is_open:
                try:
                    # Senden Sie die Bewegung als kommaseparierten String
                    # z.B. "50,20\n" für dx=50, dy=20
                    self.ser.write(f"{int(dx)},{int(dy)}\n".encode())
                    return True
                except serial.SerialException as e:
                    print(f"[FEHLER] Fehler beim Senden an Arduino: {e}")
                    self.connected = False # Verbindung ist möglicherweise unterbrochen
                    return False
            return False

    def get_available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

class FovOverlay:
    def __init__(self, master):
        self.root = ctk.CTkToplevel(master)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.canvas = tk.Canvas(self.root, bg="magenta", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.displayed_boxes = {}
        self.hide()

    def update(self, fov_area, aimbot):
        self.root.geometry(f"{fov_area['width']}x{fov_area['height']}+{fov_area['left']}+{fov_area['top']}")
        self.canvas.delete("all")
        # Ensure FOV border thickness is consistent or configurable
        self.canvas.create_rectangle(0, 0, fov_area['width']-1, fov_area['height']-1, outline=aimbot.esp_color, width=2) # Changed to 2 for consistency

        if aimbot.use_corner_esp:
            with aimbot.lock:
                esp_targets = aimbot.esp_targets.copy()
            current_ids = set(esp_targets.keys())
            previous_ids = set(self.displayed_boxes.keys())
            for box_id in previous_ids - current_ids:
                if box_id in self.displayed_boxes:
                    del self.displayed_boxes[box_id]
            for box_id, new_coords in esp_targets.items():
                if box_id not in self.displayed_boxes:
                    self.displayed_boxes[box_id] = new_coords
                else:
                    old_coords = self.displayed_boxes[box_id]
                    smoothed_coords = [old + (new - old) * aimbot.esp_smoothing for old, new in zip(old_coords, new_coords)]
                    self.displayed_boxes[box_id] = smoothed_coords
            for box in self.displayed_boxes.values():
                self.draw_corner_box(box[0], box[1], box[2], box[3], aimbot.esp_color, 2, 15) # Thickness 2 for consistency

        if aimbot.show_aim_line:
            with aimbot.lock:
                aim_line_coords = aimbot.aim_line_coords
            if aim_line_coords:
                start_x, start_y, target_x, target_y = aim_line_coords
                self.canvas.create_line(start_x, start_y, target_x, target_y, fill=aimbot.esp_color, width=1)

    def draw_corner_box(self, x1, y1, x2, y2, color, thickness, length):
        self.canvas.create_line(x1, y1, x1 + length, y1, fill=color, width=thickness)
        self.canvas.create_line(x1, y1, x1, y1 + length, fill=color, width=thickness)
        self.canvas.create_line(x2, y1, x2 - length, y1, fill=color, width=thickness)
        self.canvas.create_line(x2, y1, x2, y1 + length, fill=color, width=thickness)
        self.canvas.create_line(x1, y2, x1 + length, y2, fill=color, width=thickness)
        self.canvas.create_line(x1, y2, x1, y2 - length, fill=color, width=thickness)
        self.canvas.create_line(x2, y2, x2 - length, y2, fill=color, width=thickness)
        self.canvas.create_line(x2, y2, x2, y2 - length, fill=color, width=thickness)

    def show(self):
        self.root.deiconify()
    def hide(self):
        self.root.withdraw()
    def destroy(self):
        if self.root:
            self.root.destroy()
            self.root = None

class ScreenCaptureThread(threading.Thread):
    def __init__(self,):
        super().__init__(daemon=True)
        self.capture_box = None
        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        with mss() as sct:
            while self.running:
                with self.lock:
                    current_box = self.capture_box.copy() if self.capture_box else None
                if current_box:
                    frame_raw = sct.grab(current_box)
                    frame = np.array(frame_raw)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    with self.lock:
                        self.latest_frame = frame_bgr
                time.sleep(0.001)

    def get_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    def update_capture_box(self, new_box):
        with self.lock:
            self.capture_box = new_box
    def stop(self):
        self.running = False

class Aimbot:
    def __init__(self):
        self.running = True
        self.aimbot_enabled = True
        self.use_trigger_bot = True
        self.show_fov_overlay = True
        self.use_corner_esp = True
        self.show_aim_line = True
        self.x_offset = 0
        self.smoothing = 0.2
        self.confidence = 0.45
        self.fov_size = INITIAL_FOV_SIZE
        self.aim_target = "Head"
        self.invert_aim = False
        self.esp_smoothing = 0.3
        self.esp_targets = {}
        self.lock = threading.Lock()
        self.esp_color = COLORS["accent"]
        self.current_fps = 0
        self.cuda_available = torch.cuda.is_available()
        self.target_key = 0x02
        self.gpu_name = torch.cuda.get_device_name(0) if self.cuda_available else "N/A"
        self.aim_line_coords = None
        self.model = self.load_tensorrt_model()

        # NEU: Arduino Steuerung
        self.use_arduino_mouse = False
        self.arduino_controller = ArduinoMouseControl()

    def load_tensorrt_model(self):
        if not self.cuda_available:
            print("[FEHLER] Kein CUDA-fähiges Gerät gefunden!")
            self.running = False
            return None
        if not os.path.exists(PT_MODEL_PATH):
            print(f"[FEHLER] '{PT_MODEL_PATH}' nicht gefunden!")
            self.running = False
            return None
        if os.path.exists(TENSORRT_ENGINE_PATH):
            print(f"[INFO] Lade TensorRT-Modell: {TENSORRT_ENGINE_PATH}")
            return YOLO(TENSORRT_ENGINE_PATH, task='detect')
        else:
            print(f"[INFO] Erstelle TensorRT-Modell aus '{PT_MODEL_PATH}'...")
            try:
                model = YOLO(PT_MODEL_PATH)
                model.export(format='engine', device='cuda:0', half=True, imgsz=INITIAL_FOV_SIZE)
                return YOLO(TENSORRT_ENGINE_PATH, task='detect')
            except Exception as e:
                print(f"[FEHLER] Konnte TensorRT-Modell nicht erstellen: {e}")
                self.running = False
                return None

    def left_click(self):
        # Wenn Arduino-Steuerung aktiv, könnte ein Klick-Signal auch über Arduino gesendet werden
        # Für den Moment bleibt es bei win32api, da Arduino HID Maus nur Bewegung oft unterstützt.
        win32api.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(0x0004, 0, 0, 0, 0)

    def is_target_locked(self, x, y):
        return SCREEN_WIDTH/2 - 5 <= x <= SCREEN_WIDTH/2 + 5 and SCREEN_HEIGHT/2 - 5 <= y <= SCREEN_HEIGHT/2 + 5

    def run(self):
        capture_thread = ScreenCaptureThread()
        capture_thread.start()
        prev_time = time.perf_counter()
        with torch.inference_mode():
            while self.running and not win32api.GetAsyncKeyState(QUIT_KEY) & 0x8000:
                detection_area = {'left': int(SCREEN_WIDTH/2 - self.fov_size/2), 'top': int(SCREEN_HEIGHT/2 - self.fov_size/2), 'width': self.fov_size, 'height': self.fov_size}
                capture_thread.update_capture_box(detection_area)
                frame = capture_thread.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue

                results = self.model.track(source=frame, verbose=False, conf=self.confidence, half=True, persist=True)
                with self.lock:
                    if results and results[0] and results[0].boxes.id is not None:
                        self.esp_targets = {int(box.id): box.xyxy[0].tolist() for box in results[0].boxes}
                    elif results and results[0] and len(results[0].boxes) > 0:
                        self.esp_targets = {i: box.xyxy[0].tolist() for i, box in enumerate(results[0].boxes)}
                    else:
                        self.esp_targets = {}

                is_aiming = self.aimbot_enabled and win32api.GetAsyncKeyState(self.target_key) & 0x8000 and self.esp_targets
                with self.lock:
                    self.aim_line_coords = None
                if is_aiming:
                    fov_center_x = self.fov_size // 2
                    aimbot_targets = list(self.esp_targets.values())
                    closest_detection_coords = min(aimbot_targets, key=lambda b: math.dist(((b[0]+b[2])/2, (b[1]+b[3])/2), (fov_center_x, self.fov_size // 2)))
                    x1, y1, x2, y2 = map(int, closest_detection_coords)

                    actual_target_key = INVERTED_TARGET_MAP[self.aim_target] if self.invert_aim else self.aim_target
                    target_percentage = AIM_POINT_PERCENTAGES[actual_target_key]
                    rhx = int((x1+x2)/2)
                    rhy = int(y1 + (y2-y1) * target_percentage)
                    with self.lock:
                        self.aim_line_coords = (fov_center_x, 0, rhx, rhy)

                    abs_x = detection_area['left'] + rhx + self.x_offset
                    abs_y = detection_area['top'] + rhy

                    if self.use_trigger_bot and self.is_target_locked(abs_x, abs_y):
                        if not (win32api.GetKeyState(0x01) in (-127, -128)):
                            self.left_click()

                    curr_x, curr_y = win32api.GetCursorPos()
                    move_x = int((abs_x - curr_x) * self.smoothing)
                    move_y = int((abs_y - curr_y) * self.smoothing)

                    # NEU: Bewegung über Arduino oder win32api
                    if self.use_arduino_mouse and self.arduino_controller.connected:
                        self.arduino_controller.move_mouse(move_x, move_y)
                    else:
                        win32api.mouse_event(0x0001, move_x, move_y, 0, 0)

                current_time = time.perf_counter()
                self.current_fps = 1/(current_time - prev_time) if (current_time - prev_time) > 0 else 0
                prev_time = current_time
                time.sleep(0.001)
        capture_thread.stop()
        # Sicherstellen, dass die Arduino-Verbindung beim Beenden getrennt wird
        if self.arduino_controller.connected:
            self.arduino_controller.disconnect()
        print("\n[INFO] Aimbot-Thread wird beendet.")

class App(ctk.CTk):
    def __init__(self, aimbot_instance):
        super().__init__()
        self.aimbot = aimbot_instance
        self.title("Control Panel")
        self.geometry("450x520")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(fg_color=COLORS["accent"])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["background"])
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.setup_sidebar_and_content()
        self.fov_overlay = FovOverlay(self)
        self.update_gui_and_overlays()
        self.show_frame("ai")

    def setup_sidebar_and_content(self):
        sidebar_frame = ctk.CTkFrame(self.main_frame, width=80, corner_radius=0, fg_color=COLORS["sidebar"])
        sidebar_frame.grid(row=0, column=0, sticky="nsw")
        sidebar_frame.grid_rowconfigure(6, weight=1) # Erhöht, um Platz für neuen Button zu schaffen
        try:
            logo_image = ctk.CTkImage(Image.open("logo.png"), size=(40, 40))
            ctk.CTkLabel(sidebar_frame, image=logo_image, text="").pack(pady=20, padx=20)
        except FileNotFoundError:
            ctk.CTkLabel(sidebar_frame, text="RD", font=("Impact", 30), text_color=COLORS["text"]).pack(pady=20, padx=20)

        button_font = ("Segoe UI Emoji", 22)
        self.sidebar_buttons = {}
        # NEU: "Arduino" Tab hinzugefügt
        for name, icon in zip(["ai", "visuals", "arduino", "info", "debug"], ["🧠", "👁️", "🔌", "ℹ️", "⚙️"]):
            button = ctk.CTkButton(sidebar_frame, text=icon, font=button_font, width=50, fg_color="transparent", hover_color=COLORS["content"], command=lambda n=name: self.show_frame(n))
            button.pack(pady=10)
            self.sidebar_buttons[name] = button

        ctk.CTkButton(sidebar_frame, text="❌", font=("Segoe UI Emoji", 20), width=50, fg_color="transparent", hover_color="#c0392b", command=self.on_closing).pack(side="bottom", pady=20)

        content_wrapper = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_wrapper.grid(row=0, column=1, sticky="nsew")
        content_wrapper.grid_columnconfigure(0, weight=1)
        content_wrapper.grid_rowconfigure(1, weight=1)

        title_bar = ctk.CTkFrame(content_wrapper, height=40, corner_radius=0, fg_color=COLORS["sidebar"])
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.do_move)

        title_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=1)
        ctk.CTkLabel(title_frame, text="Red", font=FONTS["title"], text_color=COLORS["text_red"]).pack(side="left")
        ctk.CTkLabel(title_frame, text="Dolphin", font=FONTS["title"], text_color=COLORS["accent"]).pack(side="left")
        ctk.CTkLabel(title_bar, text="| V: 0.1 (Dev)", font=FONTS["body"], text_color=COLORS["text"]).pack(side="left", padx=5)

        self.content_area = ctk.CTkFrame(content_wrapper, fg_color=COLORS["background"])
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.frames = {}
        # NEU: "arduino" zu den Frames hinzugefügt
        for name in ["ai", "visuals", "arduino", "info", "debug"]:
            frame = ctk.CTkFrame(self.content_area, fg_color=COLORS["content"])
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame
            frame.grid_columnconfigure(0, weight=1)

        self.setup_ai_tab(self.frames["ai"])
        self.setup_visuals_tab(self.frames["visuals"])
        self.setup_arduino_tab(self.frames["arduino"]) # NEU: Arduino Tab Setup
        self.setup_info_tab(self.frames["info"])
        self.setup_debug_tab(self.frames["debug"])

    def setup_ai_tab(self, tab):
        ctk.CTkLabel(tab, text="Aimpoint", text_color=COLORS["text"], font=FONTS["body"]).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkOptionMenu(tab, values=list(AIM_POINT_PERCENTAGES.keys()), command=self.update_aim_target, fg_color=COLORS["sidebar"], button_color=COLORS["content"], button_hover_color=COLORS["accent"], text_color=COLORS["text"], dropdown_fg_color=COLORS["content"], dropdown_text_color=COLORS["text"]).pack(fill="x", padx=20, pady=(0, 10))
        self.hotkey_button = ctk.CTkButton(tab, text=f"Aim-Hotkey: {KEY_MAP.get(self.aimbot.target_key, f'0x{self.aimbot.target_key:02X}')}", command=self.start_key_binding)
        self.hotkey_button.pack(fill="x", padx=20, pady=10)

        checkbox_kwargs = {"text_color": COLORS["text"], "fg_color": COLORS["accent"], "hover_color": COLORS["accent"]}
        self.aimbot_enabled_var = tk.BooleanVar(value=self.aimbot.aimbot_enabled)
        self.trigger_bot_enabled_var = tk.BooleanVar(value=self.aimbot.use_trigger_bot)
        self.invert_aim_var = tk.BooleanVar(value=self.aimbot.invert_aim)
        ctk.CTkCheckBox(tab, text="Aimbot", variable=self.aimbot_enabled_var, command=lambda: setattr(self.aimbot, 'aimbot_enabled', self.aimbot_enabled_var.get()), **checkbox_kwargs).pack(anchor="w", padx=20, pady=5)
        ctk.CTkCheckBox(tab, text="Trigger Bot", variable=self.trigger_bot_enabled_var, command=lambda: setattr(self.aimbot, 'use_trigger_bot', self.trigger_bot_enabled_var.get()), **checkbox_kwargs).pack(anchor="w", padx=20, pady=5)
        ctk.CTkCheckBox(tab, text="Invert Aim", variable=self.invert_aim_var, command=lambda: setattr(self.aimbot, 'invert_aim', self.invert_aim_var.get()), **checkbox_kwargs).pack(anchor="w", padx=20, pady=10)

        self.confidence_label = ctk.CTkLabel(tab, text="", text_color=COLORS["text"], font=FONTS["body"])
        self.confidence_label.pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkSlider(tab, from_=0.01, to=1.0, command=self.update_confidence).set(self.aimbot.confidence)
        tab.winfo_children()[-1].pack(fill="x", padx=20, pady=(0,10))

        self.smoothing_label = ctk.CTkLabel(tab, text="", text_color=COLORS["text"], font=FONTS["body"])
        self.smoothing_label.pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkSlider(tab, from_=0, to=100, command=self.update_smoothing).set(self.aimbot.smoothing*100)
        tab.winfo_children()[-1].pack(fill="x", padx=20, pady=(0,10))

        self.xoffset_label = ctk.CTkLabel(tab, text="", text_color=COLORS["text"], font=FONTS["body"])
        self.xoffset_label.pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkSlider(tab, from_=0, to=200, command=self.update_x_offset).set(self.aimbot.x_offset+100)
        tab.winfo_children()[-1].pack(fill="x", padx=20, pady=(0,10))

        self.update_confidence(self.aimbot.confidence)
        self.update_smoothing(self.aimbot.smoothing*100)
        self.update_x_offset(self.aimbot.x_offset+100)

    def setup_visuals_tab(self, tab):
        checkbox_kwargs = {"text_color": COLORS["text"], "fg_color": COLORS["accent"], "hover_color": COLORS["accent"]}
        self.fov_overlay_enabled_var = tk.BooleanVar(value=self.aimbot.show_fov_overlay)
        self.corner_esp_enabled_var = tk.BooleanVar(value=self.aimbot.use_corner_esp)
        self.aim_line_enabled_var = tk.BooleanVar(value=self.aimbot.show_aim_line)

        ctk.CTkCheckBox(tab, text="Show FOV", variable=self.fov_overlay_enabled_var, command=self.toggle_fov, **checkbox_kwargs).pack(anchor="w", padx=20, pady=15)
        ctk.CTkCheckBox(tab, text="ESP", variable=self.corner_esp_enabled_var, command=lambda: setattr(self.aimbot, 'use_corner_esp', self.corner_esp_enabled_var.get()), **checkbox_kwargs).pack(anchor="w", padx=20, pady=15)
        ctk.CTkCheckBox(tab, text="Show Aimline", variable=self.aim_line_enabled_var, command=lambda: setattr(self.aimbot, 'show_aim_line', self.aim_line_enabled_var.get()), **checkbox_kwargs).pack(anchor="w", padx=20, pady=15)

        self.fov_size_label = ctk.CTkLabel(tab, text="", text_color=COLORS["text"], font=FONTS["body"])
        self.fov_size_label.pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkSlider(tab, from_=100, to=1000, command=self.update_fov_size).set(self.aimbot.fov_size)
        tab.winfo_children()[-1].pack(fill="x", padx=20, pady=(0,15))

        ctk.CTkLabel(tab, text="Visuals Color", text_color=COLORS["text"], font=FONTS["body"]).pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkOptionMenu(tab, values=list(ESP_COLORS.keys()), command=self.update_esp_color, fg_color=COLORS["sidebar"], button_color=COLORS["content"], button_hover_color=COLORS["accent"], text_color=COLORS["text"], dropdown_fg_color=COLORS["content"], dropdown_text_color=COLORS["text"]).pack(fill="x", padx=20, pady=(0,15))

        self.esp_smoothing_label = ctk.CTkLabel(tab, text="", text_color=COLORS["text"], font=FONTS["body"])
        self.esp_smoothing_label.pack(anchor="w", padx=20, pady=(10,0))
        ctk.CTkSlider(tab, from_=1, to=100, command=self.update_esp_smoothing).set(self.aimbot.esp_smoothing*100)
        tab.winfo_children()[-1].pack(fill="x", padx=20, pady=(0,15))

        self.update_fov_size(self.aimbot.fov_size)
        self.update_esp_smoothing(self.aimbot.esp_smoothing*100)

    # NEU: Setup für den Arduino-Tab
    def setup_arduino_tab(self, tab):
        checkbox_kwargs = {"text_color": COLORS["text"], "fg_color": COLORS["accent"], "hover_color": COLORS["accent"]}

        self.use_arduino_mouse_var = tk.BooleanVar(value=self.aimbot.use_arduino_mouse)
        ctk.CTkCheckBox(tab, text="Use Arduino for Mouse Control", variable=self.use_arduino_mouse_var, command=self.toggle_arduino_mouse, **checkbox_kwargs).pack(anchor="w", padx=20, pady=15)

        ctk.CTkLabel(tab, text="Select COM Port:", text_color=COLORS["text"], font=FONTS["body"]).pack(anchor="w", padx=20, pady=(10, 5))

        self.available_ports = self.aimbot.arduino_controller.get_available_ports()
        if not self.available_ports:
            self.available_ports = ["No Ports Found"] # Zeigt an, wenn keine Ports gefunden wurden
            self.port_selector = ctk.CTkOptionMenu(tab, values=self.available_ports, state="disabled", fg_color=COLORS["sidebar"], button_color=COLORS["content"], button_hover_color=COLORS["accent"], text_color=COLORS["text"], dropdown_fg_color=COLORS["content"], dropdown_text_color=COLORS["text"])
        else:
            self.port_selector = ctk.CTkOptionMenu(tab, values=self.available_ports, command=self.select_arduino_port, fg_color=COLORS["sidebar"], button_color=COLORS["content"], button_hover_color=COLORS["accent"], text_color=COLORS["text"], dropdown_fg_color=COLORS["content"], dropdown_text_color=COLORS["text"])
            self.port_selector.set(self.aimbot.arduino_controller.port if self.aimbot.arduino_controller.port else self.available_ports[0]) # Setzt den initialen Wert

        self.port_selector.pack(fill="x", padx=20, pady=(0, 10))

        self.connect_arduino_button = ctk.CTkButton(tab, text="Connect Arduino", command=self.connect_arduino, fg_color=COLORS["accent"], hover_color=COLORS["accent"])
        self.connect_arduino_button.pack(fill="x", padx=20, pady=10)

        self.disconnect_arduino_button = ctk.CTkButton(tab, text="Disconnect Arduino", command=self.disconnect_arduino, fg_color=COLORS["text_red"], hover_color="#c0392b")
        self.disconnect_arduino_button.pack(fill="x", padx=20, pady=10)

        self.arduino_status_label = ctk.CTkLabel(tab, text="Status: Disconnected", text_color=COLORS["text_red"], font=FONTS["body"])
        self.arduino_status_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.update_arduino_status_label() # Initialer Status

    def update_arduino_status_label(self):
        if self.aimbot.arduino_controller.connected:
            self.arduino_status_label.configure(text=f"Status: Connected to {self.aimbot.arduino_controller.port}", text_color=COLORS["text_green"])
        else:
            self.arduino_status_label.configure(text="Status: Disconnected", text_color=COLORS["text_red"])

    def toggle_arduino_mouse(self):
        self.aimbot.use_arduino_mouse = self.use_arduino_mouse_var.get()
        if not self.aimbot.use_arduino_mouse:
            self.aimbot.arduino_controller.disconnect() # Trenne, wenn Option deaktiviert wird
            self.update_arduino_status_label()

    def select_arduino_port(self, port):
        # Der Port wird hier nur ausgewählt, die Verbindung erfolgt über den Connect-Button
        self.aimbot.arduino_controller.port = port
        print(f"[INFO] Ausgewählter Port: {port}")

    def connect_arduino(self):
        selected_port = self.port_selector.get()
        if selected_port == "No Ports Found":
            print("[WARNUNG] Keine seriellen Ports zum Verbinden gefunden.")
            return

        if self.aimbot.arduino_controller.connect(selected_port):
            self.update_arduino_status_label()
        else:
            self.update_arduino_status_label() # Zeigt Fehlerstatus an

    def disconnect_arduino(self):
        self.aimbot.arduino_controller.disconnect()
        self.update_arduino_status_label()

    def setup_info_tab(self, tab):
        ctk.CTkLabel(tab, text="Information", font=FONTS["title"], text_color=COLORS["text"]).pack(anchor="center", pady=20)
        info_frame = ctk.CTkFrame(tab, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(info_frame, text="Status:", font=FONTS["body"], text_color=COLORS["text"]).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(info_frame, text="Undetected", font=FONTS["body"], text_color=COLORS["text_green"]).pack(side="left", padx=10, pady=10)

    def setup_debug_tab(self, tab):
        ctk.CTkLabel(tab, text="Debug Information", font=FONTS["title"], text_color=COLORS["text"]).pack(anchor="center", pady=20)
        self.gpu_label = ctk.CTkLabel(tab, text=f"GPU: {self.aimbot.gpu_name}", font=FONTS["body"], text_color=COLORS["text"])
        self.gpu_label.pack(anchor="w", padx=20, pady=5)
        self.cuda_label = ctk.CTkLabel(tab, text=f"CUDA Verfügbar: {'Ja' if self.aimbot.cuda_available else 'Nein'}", font=FONTS["body"], text_color=COLORS["text_green"] if self.aimbot.cuda_available else COLORS["text_red"])
        self.cuda_label.pack(anchor="w", padx=20, pady=5)
        self.fps_label = ctk.CTkLabel(tab, text="AI FPS: 0", font=FONTS["body"], text_color=COLORS["text"])
        self.fps_label.pack(anchor="w", padx=20, pady=5)

    def show_frame(self, frame_name):
        self.frames[frame_name].tkraise()
        for name, button in self.sidebar_buttons.items():
            button.configure(fg_color=COLORS["content"] if name == frame_name else "transparent")

    def update_gui_and_overlays(self):
        if not self.aimbot.running:
            return
        if self.aimbot.show_fov_overlay:
            detection_area = {'left': int(SCREEN_WIDTH/2 - self.aimbot.fov_size/2), 'top': int(SCREEN_HEIGHT/2 - self.aimbot.fov_size/2), 'width': self.aimbot.fov_size, 'height': self.aimbot.fov_size}
            self.fov_overlay.show()
            self.fov_overlay.update(detection_area, self.aimbot)
        else:
            self.fov_overlay.hide()
        self.fps_label.configure(text=f"AI FPS: {int(self.aimbot.current_fps)}")
        self.after(30, self.update_gui_and_overlays)

    def start_key_binding(self):
        self.hotkey_button.configure(text="[ ... ]", state="disabled")
        threading.Thread(target=self.listen_for_key, daemon=True).start()

    def listen_for_key(self):
        time.sleep(0.1)
        while self.aimbot.running:
            for key_code in range(1, 255):
                if win32api.GetAsyncKeyState(key_code) & 0x8001:
                    if key_code == self.aimbot.target_key:
                        continue
                    self.aimbot.target_key = key_code
                    self.hotkey_button.configure(text=f"Aim-Hotkey: {KEY_MAP.get(key_code, f'0x{key_code:02X}')}", state="normal")
                    return
            time.sleep(0.05)
        self.hotkey_button.configure(text=f"Aim-Hotkey: {KEY_MAP.get(self.aimbot.target_key, f'0x{self.aimbot.target_key:02X}')}", state="normal")

    def toggle_fov(self):
        self.aimbot.show_fov_overlay = self.fov_overlay_enabled_var.get()
    def update_confidence(self, val):
        self.aimbot.confidence = val
        self.confidence_label.configure(text=f"Confidence: {val:.2f}")
    def update_smoothing(self, val):
        self.aimbot.smoothing = val/100.0
        self.smoothing_label.configure(text=f"Smoothing: {int(val)}%")
    def update_x_offset(self, val):
        self.aimbot.x_offset = int(val)-100
        self.xoffset_label.configure(text=f"X-Offset: {self.aimbot.x_offset}")
    def update_fov_size(self, val):
        self.aimbot.fov_size = int(val)
        self.fov_size_label.configure(text=f"FOV Size: {self.aimbot.fov_size}x{self.aimbot.fov_size}")
    def update_esp_color(self, color_name):
        self.aimbot.esp_color = ESP_COLORS[color_name]
    def update_aim_target(self, target):
        self.aimbot.aim_target = target
    def update_esp_smoothing(self, val):
        self.aimbot.esp_smoothing = val/100.0
        self.esp_smoothing_label.configure(text=f"ESP Smoothing: {int(val)}%")

    def start_move(self, event):
        self._x = event.x
        self._y = event.y
    def do_move(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self._x}+{self.winfo_y() + event.y - self._y}")
    def on_closing(self):
        self.aimbot.running = False
        self.fov_overlay.destroy()
        self.destroy()

if __name__ == "__main__":
    aimbot = Aimbot()
    if aimbot.model:
        app = App(aimbot)
        aimbot_thread = threading.Thread(target=aimbot.run, daemon=True)
        discord_thread = DiscordPresenceThread("1383967786107142255")
        aimbot_thread.start()
        discord_thread.start()
        app.mainloop()
        discord_thread.stop()