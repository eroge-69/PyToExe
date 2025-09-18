import ctypes
import threading
import time
import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk
import pystray
import colorsys
import sys
import os
import winsound

# -------------------- Windows ekran çözünürlüğü --------------------
CCHDEVICENAME = 32
CCHFORMNAME = 32
ENUM_CURRENT_SETTINGS = -1
DM_PELSWIDTH = 0x80000
DM_PELSHEIGHT = 0x100000

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * CCHDEVICENAME),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_uint),
        ("dmPosition_x", ctypes.c_long),
        ("dmPosition_y", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_uint),
        ("dmDisplayFixedOutput", ctypes.c_uint),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * CCHFORMNAME),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_uint),
        ("dmPelsWidth", ctypes.c_uint),
        ("dmPelsHeight", ctypes.c_uint),
        ("dmDisplayFlags", ctypes.c_uint),
        ("dmDisplayFrequency", ctypes.c_uint),
        ("dmICMMethod", ctypes.c_uint),
        ("dmICMIntent", ctypes.c_uint),
        ("dmMediaType", ctypes.c_uint),
        ("dmDitherType", ctypes.c_uint),
        ("dmReserved1", ctypes.c_uint),
        ("dmReserved2", ctypes.c_uint),
        ("dmPanningWidth", ctypes.c_uint),
        ("dmPanningHeight", ctypes.c_uint),
    ]

user32 = ctypes.windll.user32
ChangeDisplaySettings = user32.ChangeDisplaySettingsW
EnumDisplaySettings = user32.EnumDisplaySettingsW

def get_current_dev_mode():
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    if EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)) == 0:
        raise RuntimeError("EnumDisplaySettings başarısız.")
    return dm

def set_resolution(width, height):
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    if EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)) == 0:
        return False
    dm.dmPelsWidth = width
    dm.dmPelsHeight = height
    dm.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT
    result = ChangeDisplaySettings(ctypes.byref(dm), 0)
    return result == 0

def enum_available_resolutions():
    i = 0
    modes = set()
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    while EnumDisplaySettings(None, i, ctypes.byref(dm)):
        modes.add((dm.dmPelsWidth, dm.dmPelsHeight))
        i += 1
    return sorted(modes)

def valorant_running():
    for p in psutil.process_iter(attrs=["name"]):
        try:
            name = (p.info["name"] or "").lower()
            if "valorant" in name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

# -------------------- Monitor Thread --------------------
class MonitorThread(threading.Thread):
    def __init__(self, get_target_resolution, status_callback=None):
        super().__init__(daemon=True)
        self.get_target_resolution = get_target_resolution
        self.status_callback = status_callback
        self._stop_event = threading.Event()
        self._is_switched = False
        self.original = get_current_dev_mode()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            valorant = valorant_running()
            if valorant and not self._is_switched:
                target = self.get_target_resolution()
                if target and set_resolution(*target):
                    self._is_switched = True
                    self.status_callback(f"Valorant açıldı → {target[0]}x{target[1]}")
                    winsound.Beep(1000, 100)  # ince ding sesi
            elif not valorant and self._is_switched:
                orig = self.original
                if set_resolution(orig.dmPelsWidth, orig.dmPelsHeight):
                    winsound.Beep(500, 150)  # uyumlu dong sesi
                self._is_switched = False
                self.status_callback(f"Valorant kapandı → {orig.dmPelsWidth}x{orig.dmPelsHeight}")
            time.sleep(1.5)

# -------------------- Rounded Button with Shadow --------------------
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, radius=12, width=120, height=40, bg="#1e1e1e", fg="white"):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.text = text
        self.shadow_offset = 3
        self.shadow_rect = self.create_rounded_rect(
            2+self.shadow_offset, 2+self.shadow_offset,
            width-2+self.shadow_offset, height-2+self.shadow_offset,
            radius, fill="#000000", outline=""
        )
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, radius, fill=bg, outline=fg, width=3)
        self.label = self.create_text(width//2, height//2, text=text, fill=fg, font=("Segoe UI", 10, "bold"))
        self.bind("<Button-1>", lambda e: command() if command else None)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.hover = False

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        return self.create_polygon(
            x1+r, y1,
            x2-r, y1,
            x2, y1+r,
            x2, y2-r,
            x2-r, y2,
            x1+r, y2,
            x1, y2-r,
            x1, y1+r,
            smooth=True, **kwargs
        )

    def on_hover(self, event):
        self.hover = True
        self.move(self.shadow_rect, 1, 1)

    def on_leave(self, event):
        self.hover = False
        self.move(self.shadow_rect, -1, -1)

    def update_color(self, color):
        outline_color = "#ffffff" if self.hover else color
        self.itemconfig(self.rect, outline=outline_color)

# -------------------- App --------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Valorant Resizer")
        root.geometry("500x330")
        root.resizable(False, False)
        root.configure(bg="#1e1e1e")

        self.status_var = tk.StringVar(value="Durum: Bekleniyor")
        self.thread = None

        # Gömmeli ico yolu
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        ico_path = resource_path("valg.ico")
        self.root.iconbitmap(ico_path)

        # Çözünürlükler
        available = enum_available_resolutions()
        common_133 = [(1024,768), (1280,960), (1600,1200)]
        targets = sorted(set(available) | set(common_133))
        self.display_map = {}
        combo_values = []
        for w,h in targets:
            label = f"✔️ {w}x{h}" if (w,h) in available else f"❌ {w}x{h}"
            combo_values.append(label)
            self.display_map[label] = (w,h)

        tk.Label(root, text="Hedef çözünürlük seç:", bg="#1e1e1e", fg="white").pack(pady=(10,0))

        self.combo_frame = tk.Frame(root, bg="#1e1e1e", highlightthickness=3)
        self.combo_frame.pack(pady=5)
        self.combo = ttk.Combobox(self.combo_frame, values=combo_values, state="readonly", width=25)
        self.combo.current(0)
        self.combo.pack(padx=2, pady=2)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.root.focus())

        # Butonlar
        self.start_btn = RoundedButton(root, text="Başlat", command=self.start)
        self.stop_btn = RoundedButton(root, text="Durdur", command=self.stop)
        self.start_btn.pack(pady=5)
        self.stop_btn.pack(pady=5)
        self.buttons = [self.start_btn, self.stop_btn]

        # İmza
        tk.Label(root, text="Doshu", bg="#1e1e1e", fg="white", font=("Segoe UI", 8, "italic")).pack(side="bottom", pady=5)

        # Durum
        tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 10, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)

        # Sistem tepsi ikonu
        icon_image = Image.open(ico_path)
        self.icon = pystray.Icon("valorant", icon_image, "Valorant Resizer", menu=pystray.Menu(
            pystray.MenuItem("Göster", self.show_window),
            pystray.MenuItem("Çıkış", self.exit_app)
        ))
        threading.Thread(target=self.icon.run, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Gradient animasyon
        self.hue = 0
        self.animate_buttons()

    def animate_buttons(self):
        self.hue = (self.hue + 0.005) % 1.0
        r,g,b = colorsys.hsv_to_rgb(self.hue, 0.6, 1.0)
        color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        for btn in self.buttons:
            btn.update_color(color)
        self.combo_frame.config(highlightbackground=color)
        self.root.after(50, self.animate_buttons)

    def get_selected_resolution(self):
        val = self.combo.get()
        self.root.focus()
        return self.display_map.get(val, None)

    def start(self):
        if self.thread and self.thread.is_alive():
            messagebox.showinfo("Bilgi", "İzleme zaten çalışıyor.")
            return
        self.thread = MonitorThread(get_target_resolution=self.get_selected_resolution, status_callback=self.update_status)
        self.thread.start()
        self.update_status("İzleme başlatıldı")

    def stop(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
            self.update_status("İzleme durduruldu")

    def update_status(self, msg):
        self.status_var.set("Durum: " + msg)

    def hide_window(self):
        self.root.withdraw()

    def show_window(self, icon=None, item=None):
        self.root.deiconify()

    def exit_app(self, icon=None, item=None):
        if self.thread:
            self.thread.stop()
        self.icon.stop()
        self.root.destroy()

# -------------------- Ana program --------------------
if __name__ == "__main__":
    import platform
    if platform.system().lower() != "windows":
        print("Bu program sadece Windows üzerinde çalışır.")
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
