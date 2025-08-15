import ctypes
import tkinter as tk
from ctypes import wintypes

# ----------------------
# Einstellungen
# ----------------------
LINE_LEN = 10
GAP = 4
THICK = 2
COLOR = "#FF0000"  # Neonrot
# ----------------------

# Win32 Konstanten
WS_EX_LAYERED      = 0x00080000
WS_EX_TRANSPARENT  = 0x00000020
WS_EX_TOOLWINDOW   = 0x00000080
GWL_EXSTYLE        = -20
LWA_COLORKEY       = 0x1

SetWindowLong = ctypes.windll.user32.SetWindowLongW
GetWindowLong = ctypes.windll.user32.GetWindowLongW
SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics

SCREEN_W = GetSystemMetrics(0)
SCREEN_H = GetSystemMetrics(1)

# ----------------------
# Overlay erstellen
# ----------------------
root = tk.Tk()
root.overrideredirect(True)
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
root.attributes("-topmost", True)

# Canvas mit Magenta-Hintergrund (als transparente Farbe)
canvas = tk.Canvas(root, width=SCREEN_W, height=SCREEN_H, highlightthickness=0, bg="magenta")
canvas.pack(fill="both", expand=True)

# ----------------------
# Fensterstil setzen (Layered + Transparent + Klick-durchlässig)
# ----------------------
hwnd = wintypes.HWND(root.winfo_id())
ex_style = GetWindowLong(hwnd, GWL_EXSTYLE)
ex_style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)
SetLayeredWindowAttributes(hwnd, 0x00FF00FF, 0, LWA_COLORKEY)  # Magenta = transparent

# ----------------------
# Crosshair zeichnen
# ----------------------
cx = SCREEN_W // 2
cy = SCREEN_H // 2

canvas.create_line(cx - GAP - LINE_LEN, cy, cx - GAP, cy, fill=COLOR, width=THICK)
canvas.create_line(cx + GAP, cy, cx + GAP + LINE_LEN, cy, fill=COLOR, width=THICK)
canvas.create_line(cx, cy - GAP - LINE_LEN, cx, cy - GAP, fill=COLOR, width=THICK)
canvas.create_line(cx, cy + GAP, cx, cy + GAP + LINE_LEN, fill=COLOR, width=THICK)

# ----------------------
# Run Overlay
# ----------------------
root.mainloop()
