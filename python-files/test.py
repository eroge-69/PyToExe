import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import platform
import os
import json
from datetime import datetime

LOG_FILE = "timer_log.json"

class ChildTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KIDS GARDEN")
        self.root.geometry("1100x750")
        self.sound_enabled = True
        self.timers = []

        # Sound setup
        try:
            if platform.system() == "Windows":
                import winsound
                self.beep = lambda: winsound.Beep(1000, 500)
            elif platform.system() == "Darwin":
                self.beep = lambda: os.system('afplay /System/Library/Sounds/Ping.aiff &')
            else:
                self.beep = lambda: os.system('play -nq -t alsa synth 0.5 sine 1000')
        except:
            self.sound_enabled = False

        # Load previous logs
        self.log_data = self.load_logs()

        # UI
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Headers
        headers = ["No", "Çocuk Adı", "Not", "Dakika", "Geri Sayım", "Kontrol"]
        for col, text in enumerate(headers):
            ttk.Label(self.scrollable_frame, text=text, font=('Arial', 10, 'bold')).grid(row=0, column=col, padx=5, pady=5, sticky="ew")

        # Timers
        for i in range(1, 31):
            self.add_child(f"Çocuk {i}", "", "30", i)

        # Ses Aç/Kapat Butonu
        ttk.Button(main_frame, text=" Ses Aç/Kapat", command=self.toggle_sound).pack(pady=5)

        # Exit log save
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

    def load_logs(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_logs(self):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)

    def add_child(self, name, note, minutes, row):
        ttk.Label(self.scrollable_frame, text=str(row)).grid(row=row, column=0, padx=5)

        name_var = tk.StringVar(value=name)
        ttk.Entry(self.scrollable_frame, textvariable=name_var, width=15).grid(row=row, column=1, padx=5)

        note_var = tk.StringVar(value=note)
        ttk.Entry(self.scrollable_frame, textvariable=note_var, width=25).grid(row=row, column=2, padx=5)

        time_var = tk.StringVar(value=minutes)
        ttk.Entry(self.scrollable_frame, textvariable=time_var, width=5).grid(row=row, column=3, padx=5)

        countdown_var = tk.StringVar(value=f"00:{minutes}:00")
        countdown_label = ttk.Label(self.scrollable_frame, textvariable=countdown_var)
        countdown_label.grid(row=row, column=4, padx=5)

        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=row, column=5, padx=5)

        ttk.Button(btn_frame, text="Başlat", width=6, command=lambda r=row-1: self.start_timer(r)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Durdur", width=6, command=lambda r=row-1: self.stop_timer(r)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Sıfırla", width=6, command=lambda r=row-1: self.reset_timer(r)).pack(side="left", padx=2)

        self.timers.append({
            "name": name_var,
            "note": note_var,
            "time": time_var,
            "countdown": countdown_var,
            "running": False,
            "remaining": int(minutes)*60,
            "thread": None,
            "start_time": None
        })

    def start_timer(self, row):
        timer = self.timers[row]
        if not timer["running"]:
            try:
                timer["remaining"] = int(timer["time"].get()) * 60
                timer["running"] = True
                timer["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.update_display(row)

                # Log start
                name = timer["name"].get()
                self.log_data[name] = {
                    "start_time": timer["start_time"],
                    "note": timer["note"].get(),
                    "minutes": timer["time"].get()
                }
                self.save_logs()

                timer["thread"] = threading.Thread(target=self.run_timer, args=(row,), daemon=True)
                timer["thread"].start()
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir dakika girin")

    def stop_timer(self, row):
        self.timers[row]["running"] = False

    def reset_timer(self, row):
        self.timers[row]["running"] = False
        try:
            mins = int(self.timers[row]["time"].get())
            self.timers[row]["remaining"] = mins * 60
            self.update_display(row)
        except ValueError:
            pass

    def run_timer(self, row):
        timer = self.timers[row]
        while timer["running"] and timer["remaining"] > 0:
            time.sleep(1)
            timer["remaining"] -= 1
            self.update_display(row)

        if timer["remaining"] <= 0 and timer["running"]:
            timer["running"] = False
            self.root.after(0, self.timer_completed, row)

    def update_display(self, row):
        timer = self.timers[row]
        mins, secs = divmod(timer["remaining"], 60)
        hours, mins = divmod(mins, 60)
        timer["countdown"].set(f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")

    def timer_completed(self, row):
        if self.sound_enabled:
            try:
                self.beep()
            except:
                pass
        name = self.timers[row]["name"].get()
        note = self.timers[row]["note"].get()
        message = f"⌛ {name} - Zaman doldu!"
        if note:
            message += f"\n\nNot: {note}"
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)
        messagebox.showinfo("Süre Doldu", message)

    def on_close(self):
        self.save_logs()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChildTimerApp(root)
    root.mainloop()
