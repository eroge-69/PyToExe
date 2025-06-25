import threading
import time
from pynput.mouse import Controller, Button
from pynput import keyboard
import tkinter as tk
from tkinter import ttk

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.is_running = False
        self.cps = 10  # 初期CPS
        self.mouse = Controller()

        # ホットキー（初期はF6）
        self.hotkey = keyboard.Key.f6

        # GUI構築
        self.create_widgets()

        # ホットキー監視スレッド開始
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        self.click_thread = None

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        # CPS調整スライダー
        ttk.Label(frame, text="クリック速度（CPS）:").pack()
        self.cps_var = tk.IntVar(value=self.cps)
        self.cps_slider = ttk.Scale(frame, from_=1, to=50, orient="horizontal", variable=self.cps_var, command=self.on_cps_change)
        self.cps_slider.pack(fill="x", padx=5, pady=5)

        # ホットキー設定
        ttk.Label(frame, text="ホットキー設定:").pack(pady=(10, 0))
        self.hotkey_var = tk.StringVar(value="F6")
        self.hotkey_entry = ttk.Entry(frame, textvariable=self.hotkey_var, width=10, justify="center")
        self.hotkey_entry.pack()
        self.hotkey_entry.bind("<FocusIn>", self.start_listen_hotkey)
        self.hotkey_entry.bind("<FocusOut>", self.stop_listen_hotkey)

        self.status_label = ttk.Label(frame, text="状態: 停止中", foreground="red")
        self.status_label.pack(pady=10)

        self.info_label = ttk.Label(frame, text="ホットキーをクリックボックスに入力後、フォーカスを外してください")
        self.info_label.pack()

    def on_cps_change(self, val):
        self.cps = int(float(val))

    def on_key_press(self, key):
        # ホットキー監視
        if key == self.hotkey:
            if self.is_running:
                self.stop_clicking()
            else:
                self.start_clicking()

    # ホットキー入力中のリスナー
    def on_hotkey_press(self, key):
        # 押されたキーを文字列にしてセット
        try:
            # 特殊キーはKey.f6などで表現される
            if isinstance(key, keyboard.Key):
                key_name = key.name.upper()
            else:
                key_name = key.char.upper()
        except AttributeError:
            key_name = str(key).upper()

        self.hotkey_var.set(key_name)
        self.set_hotkey(key)
        # 入力完了したのでリスナー停止しフォーカス外す
        self.hotkey_entry.selection_clear()
        self.root.focus()
        return False  # これでリスナー停止

    def set_hotkey(self, key):
        self.hotkey = key

    def start_listen_hotkey(self, event):
        # ホットキー入力用リスナー開始
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_listener = keyboard.Listener(on_press=self.on_hotkey_press)
        self.hotkey_listener.start()

    def stop_listen_hotkey(self, event):
        # フォーカス外れたらリスナー停止（もし動いてたら）
        if hasattr(self, "hotkey_listener"):
            self.hotkey_listener.stop()

    def start_clicking(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="状態: 実行中", foreground="green")
            self.click_thread = threading.Thread(target=self.click_loop)
            self.click_thread.daemon = True
            self.click_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="状態: 停止中", foreground="red")

    def click_loop(self):
        while self.is_running:
            self.mouse.click(Button.left)
            time.sleep(1 / self.cps)

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
