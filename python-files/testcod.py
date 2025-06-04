import tkinter as tk
import threading
import time
import json
import os
import win32api
import win32con
import keyboard

SAVE_FILE = "clicker_data.json"

class FloatingClicker:
    def __init__(self, number, x=300, y=300):
        self.win = tk.Toplevel()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg='white')
        self.win.wm_attributes("-transparentcolor", "white")
        self.win.geometry(f"60x60+{x}+{y}")
        self.number = number

        self.canvas = tk.Canvas(self.win, width=60, height=60, bg="white", highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_oval(5, 5, 55, 55, outline="#00FFC6", width=3)
        self.canvas.create_text(30, 30, text=str(number), fill="#00FFC6", font=("Arial", 16, "bold"))

        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)

        self.pos = (x + 30, y + 30)

    def start_move(self, event):
        self.x0 = event.x
        self.y0 = event.y

    def do_move(self, event):
        dx = event.x - self.x0
        dy = event.y - self.y0
        x = self.win.winfo_x() + dx
        y = self.win.winfo_y() + dy
        self.win.geometry(f"+{x}+{y}")
        self.pos = (x + 30, y + 30)

    def destroy(self):
        self.win.destroy()

class ClickerApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry("230x360+20+100")
        self.master.configure(bg="#121212")
        self.master.title("Hexor Clicker")
        self.clickers = []
        self.running = False
        self._r_pressed = False
        self._plus_pressed = False

        self.delay = tk.IntVar(value=500)
        self.repeat = tk.IntVar(value=1)

        tk.Label(master, text="🔥 Made by Hexor 🔥", fg="#00FFC6", bg="#121212",
                 font=("Segoe UI", 11, "bold")).pack(pady=10)

        tk.Label(master, text="Press 'R' to auto-click\n+ to add\nX to clear\nDraggable Circles",
                 fg="white", bg="#121212", wraplength=200).pack(pady=5)

        btn_frame = tk.Frame(master, bg="#121212")
        btn_frame.pack(pady=5)

        self.add_btn = tk.Button(btn_frame, text="+", command=self.add_clicker_gui, bg="#1E88E5", fg="white", font=("Arial", 16, "bold"))
        self.add_btn.pack(side="left", padx=10)

        self.clear_btn = tk.Button(btn_frame, text="×", command=self.clear_clickers, bg="#D32F2F", fg="white", font=("Arial", 16, "bold"))
        self.clear_btn.pack(side="right", padx=10)

        tk.Label(master, text="Delay (ms):", bg="#121212", fg="white").pack()
        tk.Entry(master, textvariable=self.delay, width=10, justify='center').pack()

        tk.Label(master, text="Repeat:", bg="#121212", fg="white").pack()
        tk.Entry(master, textvariable=self.repeat, width=10, justify='center').pack(pady=(0, 10))

        self.load_clickers()
        self.check_keys()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_clicker_gui(self):
        self.add_clicker()

    def add_clicker(self):
        number = len(self.clickers) + 1
        y_offset = 200 + number * 70
        clicker = FloatingClicker(number, x=300, y=y_offset)
        self.clickers.append(clicker)

    def clear_clickers(self):
        for c in self.clickers:
            c.destroy()
        self.clickers.clear()
        self.save_clickers()

    def real_click(self, x, y):
        win32api.SetCursorPos((int(x), int(y)))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def perform_clicks(self):
        for _ in range(self.repeat.get()):
            for c in self.clickers:
                x, y = c.pos
                self.real_click(x, y)
                time.sleep(self.delay.get() / 1000.0)
        self.running = False

    def toggle_clicks(self):
        if not self.running and self.clickers:
            self.running = True
            threading.Thread(target=self.perform_clicks, daemon=True).start()

    def check_keys(self):
        if keyboard.is_pressed('r') and not self._r_pressed:
            self._r_pressed = True
            self.toggle_clicks()
            self.master.after(300, self.reset_r_flag)

        if keyboard.is_pressed('+') and not self._plus_pressed:
            self._plus_pressed = True
            self.add_clicker()
            self.master.after(300, self.reset_plus_flag)

        if keyboard.is_pressed('x'):
            self.clear_clickers()

        self.master.after(100, self.check_keys)

    def reset_r_flag(self):
        self._r_pressed = False

    def reset_plus_flag(self):
        self._plus_pressed = False

    def save_clickers(self):
        data = [{"x": c.win.winfo_x(), "y": c.win.winfo_y()} for c in self.clickers]
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_clickers(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                    for i, pos in enumerate(data, start=1):
                        clicker = FloatingClicker(i, x=pos["x"], y=pos["y"])
                        self.clickers.append(clicker)
            except:
                pass

    def on_close(self):
        self.save_clickers()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClickerApp(root)
    root.mainloop()
