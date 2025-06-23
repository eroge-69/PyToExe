import tkinter as tk
from tkinter import messagebox
import winsound
import time

class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visszaszámláló")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<space>', self.toggle_pause)
        self.root.bind('<Delete>', self.stop_countdown)
        self.root.bind('1', lambda e: [self.root.focus_set(), self.start_preset(60)])
        self.root.bind('2', lambda e: [self.root.focus_set(), self.start_preset(120)])
        self.root.bind('3', lambda e: [self.root.focus_set(), self.start_preset(180)])

        self.time_left = tk.StringVar()
        self.time_left.set("00:00:00")
        self.running = False
        self.paused = False
        self.counting_up = False
        self.warning_triggered = False
        self.initial_seconds = 0

        self.label = tk.Label(root, textvariable=self.time_left, font=("Arial", 200), fg='white', bg='black')
        self.label.pack(expand=True)

        self.input_frame = tk.Frame(root, bg='black')
        self.input_frame.pack(pady=20)

        self.minutes_spinbox = tk.Spinbox(self.input_frame, from_=0, to=59, width=3, font=("Arial", 20), justify='center', format="%02.0f")
        self.minutes_spinbox.delete(0, "end")
        self.minutes_spinbox.insert(0, "5")
        self.minutes_spinbox.pack(side=tk.LEFT, padx=5)

        self.colon_label = tk.Label(self.input_frame, text=":", font=("Arial", 20), fg='white', bg='black')
        self.colon_label.pack(side=tk.LEFT)

        self.seconds_spinbox = tk.Spinbox(self.input_frame, from_=0, to=59, width=3, font=("Arial", 20), justify='center', format="%02.0f")
        self.seconds_spinbox.delete(0, "end")
        self.seconds_spinbox.insert(0, "00")
        self.seconds_spinbox.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.input_frame, text="Indítás", font=("Arial", 20), command=self.start_countdown)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.preset_3min = tk.Button(self.input_frame, text="3 perc", font=("Arial", 20), command=lambda: self.start_preset(180))
        self.preset_3min.pack(side=tk.LEFT, padx=10)

        self.preset_2min = tk.Button(self.input_frame, text="2 perc", font=("Arial", 20), command=lambda: self.start_preset(120))
        self.preset_2min.pack(side=tk.LEFT, padx=10)

        self.preset_1min = tk.Button(self.input_frame, text="1 perc", font=("Arial", 20), command=lambda: self.start_preset(60))
        self.preset_1min.pack(side=tk.LEFT, padx=10)

        self.control_frame = tk.Frame(root, bg='black')
        self.pause_button = tk.Button(self.control_frame, text="Szünet", font=("Arial", 20), command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(self.control_frame, text="Stop", font=("Arial", 20), command=self.stop_countdown)
        self.stop_button.pack(side=tk.LEFT, padx=10)

    def parse_time(self):
        try:
            minutes = int(self.minutes_spinbox.get())
            seconds = int(self.seconds_spinbox.get())
            return minutes * 60 + seconds
        except ValueError:
            messagebox.showerror("Hiba", "Érvénytelen időformátum!")
            return 0

    def toggle_pause(self, event=None):
        if self.running:
            self.paused = not self.paused
            self.pause_button.config(text="Folytatás" if self.paused else "Szünet")
            if not self.paused:
                self.update_countdown()

    def start_countdown(self):
        if not self.running:
            self.remaining_seconds = self.parse_time()
            if self.remaining_seconds > 0:
                self.initial_seconds = self.remaining_seconds
                self.running = True
                self.paused = False
                self.counting_up = False
                self.warning_triggered = False
                self.label.config(fg='white')
                self.input_frame.pack_forget()
                self.control_frame.pack(pady=20)
                self.pause_button.config(text="Szünet")
                self.update_countdown()

    def start_preset(self, seconds):
        if not self.running:
            self.remaining_seconds = seconds
            self.initial_seconds = seconds
            if self.remaining_seconds > 0:
                self.running = True
                self.paused = False
                self.counting_up = False
                self.warning_triggered = False
                self.label.config(fg='white')
                self.input_frame.pack_forget()
                self.control_frame.pack(pady=20)
                self.pause_button.config(text="Szünet")
                self.update_countdown()

    def stop_countdown(self, event=None):
        if self.running:
            self.running = False
            self.paused = False
            self.counting_up = False
            self.warning_triggered = False
            self.remaining_seconds = 0
            self.initial_seconds = 0
            self.time_left.set("00:00:00")
            self.label.config(fg='white')
            self.control_frame.pack_forget()
            self.input_frame.pack(pady=20)
            self.pause_button.config(text="Szünet")
            self.minutes_spinbox.delete(0, "end")
            self.minutes_spinbox.insert(0, "5")
            self.seconds_spinbox.delete(0, "end")
            self.seconds_spinbox.insert(0, "00")

    def update_countdown(self):
        if self.running and not self.paused:
            if not self.counting_up:
                if self.remaining_seconds > 0:
                    self.remaining_seconds -= 1
                    mins = self.remaining_seconds // 60
                    secs = self.remaining_seconds % 60
                    self.time_left.set(f"{mins:02d}:{secs:02d}")

                    if not self.warning_triggered:
                        if self.remaining_seconds == 60 and self.initial_seconds >= 120:
                            winsound.Beep(1000, 500)
                            self.label.config(fg='orange')
                            self.warning_triggered = True
                        elif self.remaining_seconds == 30 and self.initial_seconds == 60:
                            winsound.Beep(1000, 500)
                            self.label.config(fg='orange')
                            self.warning_triggered = True

                    if self.remaining_seconds == 0:
                        winsound.Beep(1500, 1000)
                        self.counting_up = True
                        self.label.config(fg='red')
                        self.remaining_seconds = 1

                self.root.after(1000, self.update_countdown)
            else:
                self.remaining_seconds += 1
                mins = self.remaining_seconds // 60
                secs = self.remaining_seconds % 60
                self.time_left.set(f"{mins:02d}:{secs:02d}")
                if secs == 0 and self.remaining_seconds % 60 == 0:
                    winsound.Beep(1000, 500)
                self.root.after(1000, self.update_countdown)

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()