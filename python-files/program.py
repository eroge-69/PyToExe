import tkinter as tk
from tkinter import messagebox
import pyautogui
import pygetwindow as gw
import time
import random
import threading
import win32gui
import win32con

# 🧠 Pomocnicze funkcje

def is_white(rgb, tolerance=10):
    return all(abs(c - 255) <= tolerance for c in rgb)

def find_and_click_white_button(min_width=10, min_height=10, delay_seconds=60):
    current_time = time.time()
    if hasattr(find_and_click_white_button, "last_click_time"):
        if current_time - find_and_click_white_button.last_click_time < delay_seconds:
            return False
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size

    for x in range(0, width - min_width, 5):
        for y in range(0, height - min_height, 5):
            match = True
            for dx in range(0, min_width, 5):
                for dy in range(0, min_height, 5):
                    if not is_white(screenshot.getpixel((x + dx, y + dy))):
                        match = False
                        break
                if not match:
                    break
            if match:
                print(f"[INFO] Biały przycisk {min_width}x{min_height} wykryty przy ({x}, {y}) – klikam.")
                pyautogui.click(x + min_width // 2, y + min_height // 2)
                find_and_click_white_button.last_click_time = current_time
                return True
    return False

find_and_click_white_button.last_click_time = 0  # inicjalizacja


def focus_app(title):
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        return False
    win = windows[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(0.5)
    pyautogui.press('space')
    time.sleep(0.2)
    pyautogui.press(random.choice(['w', 'a', 's', 'd']))
    time.sleep(0.2)
    win.minimize()
    return True

def set_this_window_on_top(root):
    hwnd = win32gui.FindWindow(None, root.title())
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# 🖼️ GUI

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Fokus & Rejoin")
        self.root.geometry("350x310")
        self.running = False
        self.thread = None

        tk.Label(root, text="Tytuł okna aplikacji:").pack(pady=(10, 0))
        self.app_title_entry = tk.Entry(root)
        self.app_title_entry.insert(0, "Notatnik")
        self.app_title_entry.pack()

        tk.Label(root, text="Interwał (minuty):").pack(pady=(10, 0))
        self.time_entry = tk.Entry(root)
        self.time_entry.insert(0, "5")
        self.time_entry.pack()

        self.always_on_top_var = tk.BooleanVar()
        self.rejoin_var = tk.BooleanVar()

        tk.Checkbutton(root, text="Zawsze na wierzchu (dla tej aplikacji)", variable=self.always_on_top_var,
                       command=self.toggle_on_top).pack(pady=(10, 0))
        tk.Checkbutton(root, text="Automatycznie klikaj Rejoin", variable=self.rejoin_var).pack()

        self.status_label = tk.Label(root, text="Status: Nieaktywny", fg="red")
        self.status_label.pack(pady=10)

        self.start_btn = tk.Button(root, text="Start", command=self.start)
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.stop)

        if self.always_on_top_var.get():
            self.toggle_on_top()

    def toggle_on_top(self):
        if self.always_on_top_var.get():
            set_this_window_on_top(self.root)

    def start(self):
        if self.running:
            return
        try:
            minutes = float(self.time_entry.get())
            self.interval = minutes * 60
            self.app_title = self.app_title_entry.get()
            self.running = True
            self.status_label.config(text="Status: Aktywny", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True
            self.thread.start()
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną liczbę minut.")

    def stop(self):
        self.running = False
        self.status_label.config(text="Status: Nieaktywny", fg="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.root.attributes("-topmost", False)

    def loop(self):
        while self.running:
            success = focus_app(self.app_title)

            if not success:
                print("[BŁĄD] Nie znaleziono okna:", self.app_title)

            if self.rejoin_var.get():
                find_and_click_white_button(min_width=10, min_height=10, delay_seconds=60)

            time.sleep(self.interval)

# ▶️ Start aplikacji

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
