import ctypes
import time
import threading
import tkinter as tk

user32 = ctypes.WinDLL("user32", use_last_error=True)
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

POS_1 = (1265, 847)
POS_2 = (1421, 851)
CLICK_HOLD = 0.05
WAIT_AFTER_FIRST = 1.0
WAIT_AFTER_SECOND = 1.0
START_DELAY = 10.0
CYCLE_PROFIT = 950
MAX_RUNTIME = 90 * 60

class RubleFarmer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ruble Farmer")
        self.configure(bg="#000")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.running = False
        self.paused = False
        self.cycle_count = 0
        self.total_money = 0
        self.start_time = None
        self.pause_start = None
        self.farming_started = False
        self._rainbow_colors = [
            "#ff0000", "#ff7f00", "#ffff00", "#7fff00", "#00ff00",
            "#00ff7f", "#00ffff", "#007fff", "#0000ff", "#7f00ff", "#ff00ff", "#ff007f"
        ]
        self._credit_idx = 0
        self._glow_state = 0

        self.header = tk.Label(self, text="Ruble Farmer", font=("Segoe UI", 28, "bold"), bg="#000")
        self.header.pack(pady=(25, 5))

        self.credit = tk.Label(self, text="Made By AWJ Chedder", font=("Segoe UI", 14, "bold"), bg="#000")
        self.credit.pack()

        self.money_label = tk.Label(self, text="₽0,000,000,000", font=("Segoe UI", 24, "bold"), fg="#00ff00", bg="#000")
        self.money_label.pack(pady=(10, 10))

        self.time_label = tk.Label(self, text="Farming For : 00:00:00", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#000")
        self.time_label.pack(pady=(0, 20))

        btn_frame = tk.Frame(self, bg="#000")
        btn_cfg = {
            "font": ("Segoe UI", 12, "bold"),
            "fg": "white",
            "bd": 0,
            "relief": "flat",
            "width": 10,
            "height": 1,
        }
        self.start_btn = tk.Button(btn_frame, text="Start", bg="#28a745", activebackground="#3ec97c", command=self.start, **btn_cfg)
        self.pause_btn = tk.Button(btn_frame, text="Pause", bg="#ffc107", activebackground="#ffcf40", command=self.pause_resume, state="disabled", **btn_cfg)
        self.stop_btn = tk.Button(btn_frame, text="Stop", bg="#dc3545", activebackground="#e76b6b", command=self.stop, state="disabled", **btn_cfg)
        self.start_btn.grid(row=0, column=0, padx=6)
        self.pause_btn.grid(row=0, column=1, padx=6)
        self.stop_btn.grid(row=0, column=2, padx=6)
        btn_frame.pack(pady=(0, 20))

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_reqheight()
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(ws - w)//2}+{(hs - h)//2}")

        self._animate_credit()
        self._animate_header()
        self._animate_timer()
        self._pulse_money()

    def _animate_credit(self):
        self.credit.config(fg=self._rainbow_colors[self._credit_idx])
        self._credit_idx = (self._credit_idx + 1) % len(self._rainbow_colors)
        self.after(150, self._animate_credit)

    def _animate_header(self):
        self.header.config(fg=self._rainbow_colors[self._credit_idx])
        self.after(150, self._animate_header)

    def _animate_timer(self):
        self.time_label.config(fg=self._rainbow_colors[self._credit_idx])
        self.after(150, self._animate_timer)

    def _pulse_money(self):
        shades = ["#00ff00", "#33ff33", "#66ff66", "#33ff33"]
        self.money_label.config(fg=shades[self._glow_state])
        self._glow_state = (self._glow_state + 1) % len(shades)
        self.after(400, self._pulse_money)

    def _click(self, x, y):
        user32.SetCursorPos(x, y)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(CLICK_HOLD)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def start(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.cycle_count = 0
        self.total_money = 0
        self.farming_started = False
        self.money_label.config(text="₽0,000,000,000")
        self.time_label.config(text="Farming For : 00:00:00")
        self.start_time = time.time()
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="Pause")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self._run, daemon=True).start()

    def pause_resume(self):
        if not self.running:
            return
        if self.paused:
            self.start_time += time.time() - self.pause_start
            self.paused = False
            self.pause_start = None
            self.pause_btn.config(text="Pause")
        else:
            self.paused = True
            self.pause_start = time.time()
            self.pause_btn.config(text="Resume")

    def stop(self):
        self.running = False

    def _run(self):
        countdown = START_DELAY
        while countdown > 0 and self.running:
            self.money_label.config(text=f"Starting in {int(countdown)}s")
            self.time_label.config(text="Farming For : 00:00:00")
            time.sleep(1)
            countdown -= 1

        self.farming_started = True
        self.start_time = time.time()
        self._update_money()
        self._update_timer()

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
            if time.time() - self.start_time >= MAX_RUNTIME:
                self.stop()
                break
            self._click(*POS_1)
            time.sleep(WAIT_AFTER_FIRST)
            self._click(*POS_2)
            time.sleep(WAIT_AFTER_SECOND)
            self.cycle_count += 1
            self.total_money = self.cycle_count * CYCLE_PROFIT
            self._update_money()

        self._reset()

    def _update_money(self):
        if not self.farming_started:
            self.money_label.config(text="₽0,000,000,000")
        else:
            self.money_label.config(text=f"₽{self.total_money:,}")

    def _update_timer(self):
        if not self.running or not self.farming_started:
            return
        elapsed = int(time.time() - self.start_time)
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        self.time_label.config(text=f"Farming For : {hours:02}:{minutes:02}:{seconds:02}")
        self.after(1000, self._update_timer)

    def _reset(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Pause")
        self.stop_btn.config(state="disabled")
        self.money_label.config(text=f"₽{self.total_money:,}")
        self.time_label.config(text="Farming For : 00:00:00")

if __name__ == "__main__":
    RubleFarmer().mainloop()
