import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard
import threading, time, json, os

SETTINGS_FILE = "settings.json"

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.load_settings()
        self.running = {"left": False, "right": False}
        self.create_gui()
        self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.listener.start()

    def load_settings(self):
        defaults = {
            "left_cps": 13, "right_cps": 13,
            "left_key": "x2", "right_key": "x1",
            "theme": "dark"
        }
        if os.path.isfile(SETTINGS_FILE):
            try:
                settings = json.load(open(SETTINGS_FILE))
                defaults.update(settings)
            except:
                pass
        self.settings = defaults

    def save_settings(self):
        json.dump(self.settings, open(SETTINGS_FILE, "w"))

    def create_gui(self):
        theme = self.settings.get("theme", "dark")
        bg = "#2A2A2A" if theme == "dark" else "#F0F0F0"
        fg = "#FFFFFF" if theme == "dark" else "#000000"
        self.root.configure(bg=bg)
        self.root.title("Autoclicker by Jerry")

        # Left section
        lf = ttk.LabelFrame(self.root, text="🖱️ Lewy Klikacz")
        lf.pack(padx=10, pady=5, fill="x")
        ttk.Label(lf, text="CPS:").grid(row=0, column=0, sticky="w")
        self.left_cps = tk.IntVar(value=self.settings["left_cps"])
        left_slider = ttk.Scale(lf, from_=1, to=64, variable=self.left_cps, command=self.on_left_slider)
        left_slider.grid(row=0, column=1, sticky="we", padx=5)
        self.left_key = tk.StringVar(value=self.settings["left_key"])
        ttk.Label(lf, text="Przycisk:").grid(row=1, column=0, sticky="w")
        ttk.Entry(lf, textvariable=self.left_key).grid(row=1, column=1, sticky="we", padx=5)

        # Right section – analogicznie
        rf = ttk.LabelFrame(self.root, text="🖱️ Prawy Klikacz")
        rf.pack(padx=10, pady=5, fill="x")
        ttk.Label(rf, text="CPS:").grid(row=0, column=0, sticky="w")
        self.right_cps = tk.IntVar(value=self.settings["right_cps"])
        right_slider = ttk.Scale(rf, from_=1, to=64, variable=self.right_cps, command=self.on_right_slider)
        right_slider.grid(row=0, column=1, sticky="we", padx=5)
        self.right_key = tk.StringVar(value=self.settings["right_key"])
        ttk.Label(rf, text="Przycisk:").grid(row=1, column=0, sticky="w")
        ttk.Entry(rf, textvariable=self.right_key).grid(row=1, column=1, sticky="we", padx=5)

        # Status
        self.status_label = ttk.Label(self.root, text="Status: idle", foreground="orange")
        self.status_label.pack(pady=5)

        # Save / theme / exit buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Zapisz ustawienia", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zmień motyw", command=self.toggle_theme).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Wyjdź", command=self.root.quit).pack(side="left", padx=5)

        for c in lf, rf, btn_frame:
            c.columnconfigure(1, weight=1)

    def on_left_slider(self, _):
        self.settings["left_cps"] = self.left_cps.get()

    def on_right_slider(self, _):
        self.settings["right_cps"] = self.right_cps.get()

    def toggle_theme(self):
        self.settings["theme"] = "light" if self.settings["theme"]=="dark" else "dark"
        self.save_settings()
        self.root.destroy()
        main()

    def on_save(self):
        self.settings["left_key"] = self.left_key.get()
        self.settings["right_key"] = self.right_key.get()
        self.save_settings()

    def on_key_press(self, key):
        try:
            name = key.name.lower()
        except:
            name = str(key)
        if name == self.settings["left_key"].lower():
            if not self.running["left"]:
                self.running["left"] = True
                threading.Thread(target=self.click_loop, args=("left",), daemon=True).start()
        if name == self.settings["right_key"].lower():
            if not self.running["right"]:
                self.running["right"] = True
                threading.Thread(target=self.click_loop, args=("right",), daemon=True).start()

    def on_key_release(self, key):
        try:
            name = key.name.lower()
        except:
            name = str(key)
        if name == self.settings["left_key"].lower():
            self.running["left"] = False
        if name == self.settings["right_key"].lower():
            self.running["right"] = False

    def click_loop(self, side):
        m = mouse.Controller()
        while self.running[side]:
            if side == "left":
                m.click(mouse.Button.left, 1)
                cps = self.settings["left_cps"]
            else:
                m.click(mouse.Button.right, 1)
                cps = self.settings["right_cps"]
            self.status_label.config(text=f"{side.title()} clicking... {cps} CPS")
            time.sleep(1.0 / cps)
        self.status_label.config(text="Status: idle")

def main():
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
