import tkinter as tk
import serial
import threading
import time
import json
import os
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from PIL import Image, ImageTk
import ctypes
from ctypes import wintypes

# === KONFIGURATION ===
PORT = "COM2454"
BAUD = 9600
CONFIG_FILE = "config.json"
SLIDER_IDS = ["MASTER", "SLIDER1", "SLIDER2", "SLIDER3", "SLIDER4"]

# === AudioManager ===
class AudioManager:
    def __init__(self):
        self.update_sessions()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.master = interface.QueryInterface(IAudioEndpointVolume)

    def update_sessions(self):
        self.sessions = AudioUtilities.GetAllSessions()

    def set_volume(self, app_name, volume):
        if app_name == "MASTER":
            self.master.SetMasterVolumeLevelScalar(volume, None)
        elif app_name == "None":
            return
        else:
            self.update_sessions()
            for session in self.sessions:
                proc = session.Process
                if proc and proc.name():
                    name = proc.name().replace(".exe", "").lower()
                    if name == app_name.lower():
                        vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                        vol.SetMasterVolume(volume, None)
                        break

    def get_active_apps(self):
        self.update_sessions()
        apps = set()
        for session in self.sessions:
            proc = session.Process
            if proc and proc.name():
                name = proc.name().replace(".exe", "").capitalize()
                if name.lower() not in ("system", "audiodg"):
                    apps.add(name)
        return sorted(apps)

# === GUI-Komponenten ===
class SliderBar(tk.Canvas):
    def __init__(self, master, height=200):
        super().__init__(master, width=50, height=height, bg="#1e1f23", highlightthickness=0)
        self.height = height
        self.handle_height = 35
        self.handle_width = 30
        self.bar_width = 8

        self.track = self.create_rectangle(21, 0, 21 + self.bar_width, height, fill="#3c3f45", outline="")
        self.handle_y = height // 2

        self.handle_top = self.create_oval(10, self.handle_y - self.handle_height // 2,
                                           10 + self.handle_width, self.handle_y - self.handle_height // 2 + 10,
                                           fill="#f0f0f0", outline="#f0f0f0")
        self.handle_rect = self.create_rectangle(10, self.handle_y - self.handle_height // 2 + 5,
                                                 10 + self.handle_width, self.handle_y + self.handle_height // 2 - 5,
                                                 fill="#f0f0f0", outline="#f0f0f0")
        self.handle_bot = self.create_oval(10, self.handle_y + self.handle_height // 2 - 10,
                                           10 + self.handle_width, self.handle_y + self.handle_height // 2,
                                           fill="#f0f0f0", outline="#f0f0f0")

        self.ridges = []
        for i in range(-8, 9, 4):
            y = self.handle_y + i
            self.ridges.append(self.create_line(13, y, 37, y, fill="#aaaaaa"))

    def set_value(self, val):
        y = int(self.height - (val / 1023.0) * self.height)
        y = min(max(y, self.handle_height // 2), self.height - self.handle_height // 2)
        self.handle_y = y

        self.coords(self.handle_top, 10, y - self.handle_height // 2,
                                10 + self.handle_width, y - self.handle_height // 2 + 10)
        self.coords(self.handle_rect, 10, y - self.handle_height // 2 + 5,
                                 10 + self.handle_width, y + self.handle_height // 2 - 5)
        self.coords(self.handle_bot, 10, y + self.handle_height // 2 - 10,
                                10 + self.handle_width, y + self.handle_height // 2)

        for i, line in enumerate(range(-8, 9, 4)):
            new_y = y + line
            self.coords(self.ridges[i], 13, new_y, 37, new_y)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print("Fehler beim Speichern:", e)

def choose_app_list(master, slider_id, current_selection, callback, x, y):
    apps = audio_manager.get_active_apps()
    apps = ["None"] + apps

    # Kleines Listbox Fenster direkt unter Text (keine Windows-Statusbar)
    listbox_popup = tk.Toplevel(master)
    listbox_popup.overrideredirect(True)
    listbox_popup.configure(bg="#2e2f33")
    listbox_popup.geometry(f"+{x}+{y}")

    # Größe so wählen, wie viele Apps da sind (max 10, sonst scrollbar)
    max_visible = 10
    visible_apps = min(len(apps), max_visible)

    listbox = tk.Listbox(listbox_popup, bg="#2e2f33", fg="white", selectbackground="#4fe36a",
                         activestyle='none', height=visible_apps)
    listbox.pack()

    for app in apps:
        listbox.insert(tk.END, app)

    if current_selection in apps:
        idx = apps.index(current_selection)
        listbox.selection_set(idx)
        listbox.see(idx)

    def on_select(event=None):
        sel = listbox.curselection()
        if sel:
            chosen = listbox.get(sel[0])
            callback(chosen)
        listbox_popup.destroy()

    listbox.bind("<<ListboxSelect>>", on_select)

    # Klick außerhalb schließt die Liste
    def click_outside(event):
        if event.widget is not listbox:
            listbox_popup.destroy()

    listbox_popup.focus_force()
    listbox_popup.grab_set()
    listbox_popup.bind("<FocusOut>", lambda e: listbox_popup.destroy())

    # Positionierung & Fokus für besseres UX
    listbox_popup.lift()

# === Schließen der App ===
def close_app():
    root.destroy()

root = tk.Tk()
root.title("Controlify")
root.geometry("620x400")
root.configure(bg="#1e1f23")
root.resizable(False, False)

# === Custom Fensterramen, aber in Taskleiste sichtbar (Windows) ===
root.overrideredirect(True)  # Kein Standard Windows-Rahmen

# Windows API Fensterstil ändern, damit Fenster in Taskleiste sichtbar bleibt
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
style = style & ~WS_EX_TOOLWINDOW
style = style | WS_EX_APPWINDOW
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW

# === Eigene Titlebar ===
title_bar = tk.Frame(root, bg="#1e1f23", height=30)
title_bar.pack(fill=tk.X, side="top")

logo_img = Image.open("logo.ico").resize((25, 25), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(title_bar, image=logo_photo, bg="#1e1f23")
logo_label.image = logo_photo
logo_label.pack(side="left", padx=(12, 5), pady=(5, 0))  # Etwas nach unten mit pady

app_name = tk.Label(title_bar, text="Controlify", bg="#1e1f23", fg="white",
                    font=("Segoe UI", 14, "bold"))
app_name.pack(side="left", pady=(5, 0), padx=(0, 15))  # Padding rechts + unten

status_label = tk.Label(title_bar, text="   Connected", fg="#4fe36a", bg="#1e1f23",
                        font=("Segoe UI", 14, "bold"))
status_label.pack(side="left", padx=5, pady=(5, 0))

close_button = tk.Button(title_bar, text="✕", command=close_app, bg="#1e1f23", fg="#E4080A",
                         font=("Segoe UI", 14, "bold"), activebackground="#ff4c4c",
                         activeforeground="white", bd=0, cursor="hand2")
close_button.pack(side="right", padx=10, pady=(5, 0))

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_motion(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

title_bar.bind("<Button-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", on_motion)

audio_manager = AudioManager()
sliders = []
slider_config = load_config()
selected_apps = {sid: slider_config.get(sid, "None") for sid in SLIDER_IDS}
selected_apps["MASTER"] = "MASTER"

connected_event = threading.Event()

def update_status(connected):
    if connected:
        connected_event.set()
        status_label.config(text="   Connected", fg="#4fe36a")
    else:
        connected_event.clear()
        status_label.config(text="   Checking connection", fg="#E4080A")

def animate_checking(i=0):
    if not connected_event.is_set():
        dots = ["", ".", "..", "..."]
        status_label.config(text=f"   Checking connection{dots[i % len(dots)]}", fg="#E4080A")
        root.after(500, animate_checking, i + 1)

animate_checking()

slider_frame = tk.Frame(root, bg="#1e1f23")
slider_frame.pack(expand=True, pady=10)

def on_app_label_click(event, sid, label):
    x = label.winfo_rootx()
    y = label.winfo_rooty() + label.winfo_height()
    def callback(app):
        selected_apps[sid] = app
        label.config(text=app)
        save_config(selected_apps)
    choose_app_list(root, sid, selected_apps[sid], callback, x, y)

for sid in SLIDER_IDS:
    col = tk.Frame(slider_frame, bg="#1e1f23")
    col.pack(side="left", padx=30)
    slider = SliderBar(col)
    slider.pack()
    sliders.append(slider)

    text = sid if sid == "MASTER" else selected_apps[sid]
    label = tk.Label(col, text=text, fg="white", bg="#1e1f23", font=("Segoe UI", 10, "bold"), cursor="hand2")
    label.pack(pady=8)

    if sid != "MASTER":
        label.bind("<Button-1>", lambda e, s=sid, l=label: on_app_label_click(e, s, l))

def serial_thread():
    ser = None
    was_connected = False
    while True:
        try:
            if ser is None:
                ser = serial.Serial(PORT, BAUD, timeout=1)
                update_status(True)
                was_connected = True

            line = ser.readline().decode("utf-8").strip()
            parts = line.split(",")
            if len(parts) == len(sliders):
                values = [int(p) for p in parts]
                for i in range(len(sliders)):
                    sliders[i].set_value(values[i])
                    app = selected_apps[SLIDER_IDS[i]]
                    vol = values[i] / 1023.0
                    audio_manager.set_volume(app, vol)
        except serial.SerialException:
            if was_connected:
                update_status(False)
                was_connected = False
            if ser:
                try: ser.close()
                except: pass
            ser = None
            time.sleep(1)
        except Exception as e:
            print("Fehler:", e)
            time.sleep(1)

threading.Thread(target=serial_thread, daemon=True).start()
root.mainloop()
