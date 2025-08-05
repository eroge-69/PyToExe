import pyautogui
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import threading
import pystray
import keyboard
import win32com.client
import sys

# === Global Config ===
BASE_SAVE_DIR = "C:\\Screenshots"
DEFAULT_REGION = (100, 100, 800, 600)
current_region = DEFAULT_REGION
current_save_folder = None  # Active screenshot folder

# === Create New Folder Manually or on First Shot ===
def create_new_save_folder():
    global current_save_folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(BASE_SAVE_DIR, timestamp)
    os.makedirs(folder_path, exist_ok=True)
    current_save_folder = folder_path
    print(f"[Folder Created] New screenshot folder: {current_save_folder}")

# === Screenshot Function ===
def capture_screenshot(region=None):
    global current_save_folder
    try:
        if region is None:
            region = current_region

        if current_save_folder is None:
            create_new_save_folder()  # Create folder on first use

        timestamp = datetime.now().strftime("%H-%M-%S-%f")  # Unique filename
        file_path = os.path.join(current_save_folder, f"screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(file_path)

        print(f"[Screenshot Saved] {file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# === Region Selector ===
def select_region():
    def on_mouse_up(event):
        global current_region
        x0, y0 = start_x, start_y
        x1, y1 = canvas.canvasx(event.x), canvas.canvasy(event.y)
        left = min(x0, x1)
        top = min(y0, y1)
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        current_region = (left, top, width, height)
        selector.destroy()
        print(f"[Region Selected] {current_region}")

    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = canvas.canvasx(event.x), canvas.canvasy(event.y)

    selector = tk.Tk()
    selector.attributes("-alpha", 0.3)
    selector.attributes("-fullscreen", True)
    selector.configure(bg='black')
    selector.title("Select Area")
    canvas = tk.Canvas(selector, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = 0
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    selector.mainloop()

# === Tray Icon Helpers ===
def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
    return image

# === Tray Menu Actions ===
def on_capture(icon, item):
    capture_screenshot()

def on_select_area(icon, item):
    select_region()

def on_new_folder(icon, item):
    create_new_save_folder()

def toggle_autostart(icon, item):
    script_path = sys.argv[0]
    shell = win32com.client.Dispatch("WScript.Shell")
    startup = shell.SpecialFolders("Startup")
    shortcut_path = os.path.join(startup, "ScreenshotTool.lnk")

    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print("[Auto-Start] Disabled")
    else:
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.save()
        print("[Auto-Start] Enabled")

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

# === System Tray ===
def run_tray():
    icon = pystray.Icon("screenshot_tool")
    icon.icon = create_image()
    icon.menu = pystray.Menu(
        pystray.MenuItem("Capture Screenshot", on_capture),
        pystray.MenuItem("Select Area", on_select_area),
        pystray.MenuItem("Start New Folder", on_new_folder),
        pystray.MenuItem("Toggle Auto-Start", toggle_autostart),
        pystray.MenuItem("Exit", on_exit)
    )
    icon.run()

# === Hotkey Listener ===
def listen_for_hotkeys():
    keyboard.add_hotkey("ctrl+alt+s", capture_screenshot)
    keyboard.add_hotkey("ctrl+alt+a", select_region)
    print("[Hotkeys Active] Ctrl+Alt+S = Capture | Ctrl+Alt+A = Select Area")
    keyboard.wait()

# === Main Entry Point ===
if __name__ == "__main__":
    if not os.path.exists(BASE_SAVE_DIR):
        os.makedirs(BASE_SAVE_DIR)

    threading.Thread(target=listen_for_hotkeys, daemon=True).start()
    run_tray()
