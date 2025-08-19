
import tkinter as tk
from tkinter import ttk
import datetime as dt
import calendar
import threading
import time

APP_TITLE = "Durga Puja 2025 Countdown"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))  # Asia/Kolkata

PUJA_DATES = [
    ("Mahalaya", dt.datetime(2025, 9, 21, 0, 0, tzinfo=IST)),
    ("Maha Panchami", dt.datetime(2025, 9, 27, 0, 0, tzinfo=IST)),
    ("Maha Shashthi", dt.datetime(2025, 9, 28, 0, 0, tzinfo=IST)),
    ("Maha Saptami", dt.datetime(2025, 9, 29, 0, 0, tzinfo=IST)),
    ("Maha Ashtami", dt.datetime(2025, 9, 30, 0, 0, tzinfo=IST)),
    ("Maha Navami", dt.datetime(2025, 10, 1, 0, 0, tzinfo=IST)),
    ("Vijaya Dashami", dt.datetime(2025, 10, 2, 0, 0, tzinfo=IST)),
]

def find_default_target(now_ist):
    for name, d in PUJA_DATES[2:]:
        if d > now_ist:
            return name
    return "Vijaya Dashami"

class CountdownApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)

        style = ttk.Style(self)
        try:
            self.tk.call("tk", "scaling", 1.2)
        except Exception:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Big.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Small.TLabel", font=("Segoe UI", 10))
        style.configure("Day.TLabel", font=("Segoe UI", 10))
        style.configure("DaySel.TLabel", font=("Segoe UI", 10, "bold"), foreground="#d13bff")
        style.configure("Head.TLabel", font=("Segoe UI", 11, "bold"))

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Durga Puja 2025", style="Title.TLabel").pack(side="left")
        self.always_on_top = tk.BooleanVar(value=True)
        aot_btn = ttk.Checkbutton(header, text="Always on top", variable=self.always_on_top, command=self.toggle_aot)
        aot_btn.pack(side="right")
        self.toggle_aot()

        control = ttk.Frame(container)
        control.grid(row=1, column=0, pady=(8, 6), sticky="ew")
        ttk.Label(control, text="Countdown to:").pack(side="left")
        self.target_var = tk.StringVar()
        now_ist = dt.datetime.now(IST)
        self.target_var.set(find_default_target(now_ist))
        self.target_combo = ttk.Combobox(control, state="readonly", values=[name for name, _ in PUJA_DATES],
                                         textvariable=self.target_var, width=18)
        self.target_combo.pack(side="left", padx=6)
        self.target_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_calendar())

        self.countdown_lbl = ttk.Label(container, text="--", style="Big.TLabel")
        self.countdown_lbl.grid(row=2, column=0, pady=(2, 10))

        self.cal_frame = ttk.Frame(container, borderwidth=1, relief="solid", padding=8)
        self.cal_frame.grid(row=3, column=0, sticky="nsew")
        self.cal_header = ttk.Label(self.cal_frame, text="", style="Head.TLabel")
        self.cal_header.grid(row=0, column=0, columnspan=7, pady=(0, 6))

        self.day_labels = []
        for i, wd in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ttk.Label(self.cal_frame, text=wd, style="Small.TLabel").grid(row=1, column=i, padx=3, pady=2)

        for r in range(6):
            row_labels = []
            for c in range(7):
                lbl = ttk.Label(self.cal_frame, text="", style="Day.TLabel", width=3, anchor="center")
                lbl.grid(row=2+r, column=c, padx=3, pady=2)
                row_labels.append(lbl)
            self.day_labels.append(row_labels)

        self.refresh_calendar()

        self.status_lbl = ttk.Label(container, text="Made for India (IST) • Close to exit", style="Small.TLabel")
        self.status_lbl.grid(row=4, column=0, pady=(8, 0))

        self._stop = False
        t = threading.Thread(target=self._ticker, daemon=True)
        t.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def toggle_aot(self):
        self.attributes("-topmost", bool(self.always_on_top.get()))

    def _on_close(self):
        self._stop = True
        self.destroy()

    def get_target_dt(self):
        name = self.target_var.get()
        for n, d in PUJA_DATES:
            if n == name:
                return d
        return PUJA_DATES[-1][1]

    def _format_delta(self, delta: dt.timedelta):
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            return "Started! \U0001FA94"
        days, rem = divmod(total_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{days} \u09a6\u09bf\u09a8 {hours:02d}:{minutes:02d}:{seconds:02d}"

    def _ticker(self):
        while not self._stop:
            now = dt.datetime.now(IST)
            target = self.get_target_dt()
            delta = target - now
            text = self._format_delta(delta)
            self.countdown_lbl.configure(text=text)
            self.status_lbl.configure(text=f"Target: {self.target_var.get()} \u2022 {target.strftime('%d %b %Y, %a, %H:%M IST')}")
            time.sleep(1)

    def refresh_calendar(self):
        target = self.get_target_dt()
        year, month, day = target.year, target.month, target.day
        self.cal_header.configure(text=target.strftime("%B %Y"))
        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdayscalendar(year, month)
        for r in range(6):
            for c in range(7):
                self.day_labels[r][c].configure(text="", style="Day.TLabel")
        for r, week in enumerate(month_weeks):
            for c, d in enumerate(week):
                if d == 0:
                    self.day_labels[r][c].configure(text="")
                else:
                    style = "DaySel.TLabel" if d == day else "Day.TLabel"
                    self.day_labels[r][c].configure(text=str(d), style=style)

if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()
