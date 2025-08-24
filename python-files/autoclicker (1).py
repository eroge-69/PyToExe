import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput import mouse, keyboard
import win32api, win32con

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox 连点器")
        self.root.geometry("300x200")

        self.clicking = False
        self.delay = tk.DoubleVar(value=0.01) # 默认点击间隔0.01秒

        self.create_widgets()
        self.setup_hotkeys()

    def create_widgets(self):
        # 点击间隔设置
        delay_frame = ttk.Frame(self.root)
        delay_frame.pack(pady=10)

        ttk.Label(delay_frame, text="点击间隔 (秒):").pack(side=tk.LEFT)
        ttk.Entry(delay_frame, textvariable=self.delay, width=10).pack(side=tk.LEFT)

        # 控制按钮
        self.start_button = ttk.Button(self.root, text="开始 (F6)", command=self.start_clicking)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(self.root, text="停止 (F6)", command=self.stop_clicking, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def setup_hotkeys(self):
        self.hotkey_listener = keyboard.Listener(on_press=self.on_press)
        self.hotkey_listener.start()

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                if self.clicking:
                    self.stop_clicking()
                else:
                    self.start_clicking()
        except AttributeError:
            pass

    def clicker_thread(self):
        while self.clicking:
            x, y = win32api.GetCursorPos()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(self.delay.get())

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.click_thread = threading.Thread(target=self.clicker_thread)
            self.click_thread.start()

    def stop_clicking(self):
        if self.clicking:
            self.clicking = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()


