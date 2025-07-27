import tkinter as tk
from datetime import datetime, timedelta
import time

REAL_SECONDS_PER_GAME_MINUTE = 6




class RDOInGameClockOverlay:
    def __init__(self):
        self.clock_on_top = True
        self.bank_time_enabled = False
        self.guarma_time_enabled = False

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 1.0)
        self.root.configure(bg='magenta')
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.root.geometry("+50+50")

        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<F7>", lambda e: self.reset_time())
        self.root.bind("<F10>", lambda e: self.add_one_hour())
        self.root.bind("<F8>", lambda e: self.add_one_minute())
        self.root.bind("<F9>", lambda e: self.subtract_one_minute())
        self.root.bind("<F11>", lambda e: self.subtract_one_hour())

        self.main_frame = tk.Frame(self.root, bg="magenta")
        self.main_frame.pack()

        self.label = tk.Label(self.main_frame, font=("Courier", 44), fg="orange", bg="magenta")
        self.description_label = tk.Label(self.main_frame, font=("Arial", 12), fg="white", bg="magenta")

        self.bank_status_label = tk.Label(self.main_frame, font=("Arial", 12), fg="cyan", bg="magenta")
        self.bank_toggle_msg = tk.Label(self.main_frame, font=("Arial", 10), fg="yellow", bg="magenta")

        self.guarma_status_label = tk.Label(self.main_frame, font=("Arial", 12), fg="lightblue", bg="magenta")
        self.guarma_toggle_msg = tk.Label(self.main_frame, font=("Arial", 10), fg="yellow", bg="magenta")

        self.btn_frame = tk.Frame(self.main_frame, bg="magenta")

        tk.Button(self.btn_frame, text="⇵ สลับด้าน", command=self.toggle_clock_position,
                  font=("Arial", 12), bg="purple", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="🏦 เปิด/ปิดแจ้งเตือนเวลาทำการธนาคาร", command=self.toggle_bank_time,
                  font=("Arial", 12), bg="goldenrod", fg="black", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="⛵ เปิด/ปิดแจ้งเวลาทำการเรือเกาะกัวม่า", command=self.toggle_guarma_time,
                  font=("Arial", 12), bg="dodgerblue", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="⟳ Reset (F7)", command=self.reset_time,
                  font=("Arial", 12), bg="gray20", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="+1 Min (F8)", command=self.add_one_minute,
                  font=("Arial", 12), bg="green", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="-1 Min (F9)", command=self.subtract_one_minute,
                  font=("Arial", 12), bg="darkgreen", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="+1 Hr (F10)", command=self.add_one_hour,
                  font=("Arial", 12), bg="blue", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="-1 Hr (F11)", command=self.subtract_one_hour,
                  font=("Arial", 12), bg="darkblue", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="✕ Close (Esc)", command=self.root.destroy,
                  font=("Arial", 12), bg="red", fg="white", relief="flat")\
            .pack(side="left", padx=5)

        self.footer = tk.Label(self.main_frame,
            text="เบนจามินบอกว่าทำให้คนที่เบนจามินใส่ใจขอบคุณสำหรับแรงบันดาลใจนะครับ",
            font=("Arial", 15), fg="white", bg="magenta")

        self.draw_widgets()

        self.start_time = time.time()
        self.in_game_time = datetime.strptime("00:00", "%H:%M")
        self.update_clock()
        self.root.mainloop()

    def draw_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()

        if self.clock_on_top:
            self.label.pack(pady=(10, 0))
            self.description_label.pack(pady=(5, 2))
            self.bank_status_label.pack(pady=(0, 2))
            self.bank_toggle_msg.pack()
            self.guarma_status_label.pack(pady=(0, 2))
            self.guarma_toggle_msg.pack()
            self.btn_frame.pack(pady=(0, 5))
            self.footer.pack(pady=(0, 10))
        else:
            self.btn_frame.pack(pady=(5, 5))
            self.guarma_toggle_msg.pack()
            self.guarma_status_label.pack(pady=(0, 2))
            self.bank_toggle_msg.pack()
            self.bank_status_label.pack(pady=(0, 2))
            self.description_label.pack(pady=(5, 2))
            self.label.pack(pady=(10, 10))
            self.footer.pack(pady=(0, 10))

    def toggle_clock_position(self):
        self.clock_on_top = not self.clock_on_top
        self.draw_widgets()

    def toggle_bank_time(self):
        self.bank_time_enabled = not self.bank_time_enabled
        if self.bank_time_enabled:
            self.bank_toggle_msg.config(text="✅ เปิดการแจ้งเตือนเวลาทำการธนาคาร")
        else:
            self.bank_toggle_msg.config(text="❌ ปิดการแจ้งเตือนเวลาทำการธนาคาร")
            self.bank_status_label.config(text="")
        self.root.after(5000, lambda: self.bank_toggle_msg.config(text=""))

    def toggle_guarma_time(self):
        self.guarma_time_enabled = not self.guarma_time_enabled
        if self.guarma_time_enabled:
            self.guarma_toggle_msg.config(text="✅ เปิดแจ้งเตือนเรือไป-กลับเกาะกัวม่า")
        else:
            self.guarma_toggle_msg.config(text="❌ ปิดแจ้งเตือนเรือไป-กลับเกาะกัวม่า")
            self.guarma_status_label.config(text="")
        self.root.after(5000, lambda: self.guarma_toggle_msg.config(text=""))

    def start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_start_x
        y = self.root.winfo_y() + event.y - self._drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def reset_time(self):
        self.start_time = time.time()
        self.in_game_time = datetime.strptime("00:00", "%H:%M")

    def add_one_minute(self):
        self.in_game_time += timedelta(minutes=1)
        self.start_time = time.time()

    def subtract_one_minute(self):
        self.in_game_time -= timedelta(minutes=1)
        self.start_time = time.time()

    def add_one_hour(self):
        self.in_game_time += timedelta(hours=1)
        self.start_time = time.time()

    def subtract_one_hour(self):
        self.in_game_time -= timedelta(hours=1)
        self.start_time = time.time()

    def update_clock(self):
        elapsed_real_seconds = time.time() - self.start_time
        elapsed_game_minutes = int(elapsed_real_seconds / REAL_SECONDS_PER_GAME_MINUTE)
        current_game_time = self.in_game_time + timedelta(minutes=elapsed_game_minutes)

        hour = current_game_time.hour
        minute = current_game_time.minute

        emoji = "☀️" if 6 <= hour < 18 else "🌙"
        if hour == 0 and minute == 0:
            emoji = "🌙☀️"
        elif hour == 12 and minute == 0:
            emoji = "☀️🌙"

        time_str = current_game_time.strftime("%H:%M")
        self.label.config(text=f"{time_str} {emoji}")

        # Descriptions
        description = ""
        if hour == 0 and minute == 0:
            description = "🌙 Midnight"
        elif hour == 6 and minute == 0:
            description = "🌅 Morning"
        elif hour == 12 and minute == 0:
            description = "☀️ Noon"
        elif hour == 18 and minute == 0:
            description = "🌇 Dusk"
        self.description_label.config(text=description)

        # Bank
        if self.bank_time_enabled:
            if 7 <= hour < 21:
                self.bank_status_label.config(text="🏦 ธนาคารเปิดอยู่")
            else:
                self.bank_status_label.config(text="🏦 ธนาคารปิดแล้วจ้า")

        # Guarma
        if self.guarma_time_enabled:
            if 7 <= hour < 22:
                self.guarma_status_label.config(text="⛵ เรือไปเกาะกัวม่ายังเปิดให้บริการอยู่")
            else:
                self.guarma_status_label.config(text="⛵ เรือไปเกาะกัวม่าปิดแล้วงับ")

        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    RDOInGameClockOverlay()