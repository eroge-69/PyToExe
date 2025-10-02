#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flyzel Work Calendar - Tkinter App (modified for shift-based coloring)
---------------------------------------------------------------------
Detects activity in two shifts:
 - Morning: 10:00 - 13:30  (10:00–13:30)
 - Afternoon: 15:00 - 19:00 (15:00–19:00)

If a date has activity in only one shift -> green
If a date has activity in both shifts -> yellow
"""
import os
import sys
import calendar
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date, time
from pathlib import Path
from collections import defaultdict

APP_TITLE = "Flyzel Work Calendar"
PADDING = 8

# Colors
COLOR_BG = "#0b1020"
COLOR_PANEL = "#121a33"
COLOR_TEXT = "#e8ecf1"
COLOR_MUTED = "#98a2b3"
COLOR_SUNDAY = "#ffb4b4"     # Sunday day number
COLOR_WORKDAY = "#39d98a"    # Work (one shift) = green
COLOR_BOTH = "#ffd166"       # Both shifts = yellow
COLOR_NOWORK = "#2a334d"     # No work
COLOR_TODAY_OUTLINE = "#ffd166"
COLOR_BORDER = "#27314d"

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def daterange_key(ts: float):
    d = datetime.fromtimestamp(ts)
    return d.date(), d.time()

def time_in_morning(t: time):
    # Morning shift: 10:00–13:30
    return time(10,0,0) <= t <= time(13,30,0)

def time_in_afternoon(t: time):
    # Afternoon shift: 15:00–19:00
    return time(15,0,0) <= t <= time(19,0,0)

def scan_folder_activity(folder: Path, year: int, month: int):
    activity_map = defaultdict(set)
    sample_files = defaultdict(list)
    if not folder.exists():
        return activity_map, sample_files

    month_start = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    month_end = date(year, month, last_day)

    for root, dirs, files in os.walk(folder):
        for fname in files:
            try:
                fpath = Path(root) / fname
                stat = fpath.stat()
                for ts in (stat.st_mtime, stat.st_ctime):
                    d, t = daterange_key(ts)
                    if not (month_start <= d <= month_end):
                        continue
                    if time_in_morning(t):
                        activity_map[d].add("morning")
                    if time_in_afternoon(t):
                        activity_map[d].add("afternoon")
                    if len(sample_files[d]) < 5:
                        try:
                            rp = fpath.relative_to(folder)
                        except Exception:
                            rp = fpath
                        sample_files[d].append(str(rp))
            except (PermissionError, FileNotFoundError):
                continue
            except Exception as e:
                print(f"Warning: {e}", file=sys.stderr)
                continue
    return activity_map, sample_files

class FlyzelCalendar(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=COLOR_BG)
        self.geometry("980x720")
        self.minsize(900, 640)

        today = date.today()
        self.selected_year = tk.IntVar(value=today.year)
        self.selected_month = tk.IntVar(value=today.month)
        self.selected_folder = tk.StringVar(value="")

        self.cache = {}
        self._build_ui()
        self._draw_calendar()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLOR_PANEL, bd=0, highlightthickness=0)
        top.pack(side=tk.TOP, fill=tk.X)

        self.folder_label = tk.Label(top, text="Folder: (none)", bg=COLOR_PANEL, fg=COLOR_TEXT, anchor="w")
        self.folder_label.pack(side=tk.LEFT, padx=(PADDING, 0), pady=PADDING, expand=True, fill=tk.X)

        pick_btn = ttk.Button(top, text="Select Folder", command=self.pick_folder)
        pick_btn.pack(side=tk.RIGHT, padx=PADDING, pady=PADDING)

        controls = tk.Frame(self, bg=COLOR_BG)
        controls.pack(side=tk.TOP, fill=tk.X, padx=PADDING, pady=(PADDING, 0))

        prev_btn = ttk.Button(controls, text="◀", width=3, command=self.prev_month)
        prev_btn.pack(side=tk.LEFT, padx=(0, 4))

        months = [calendar.month_name[i] for i in range(1, 13)]
        self.month_cb = ttk.Combobox(controls, values=months, width=14, state="readonly")
        self.month_cb.current(self.selected_month.get() - 1)
        self.month_cb.bind("<<ComboboxSelected>>", self.on_month_change)
        self.month_cb.pack(side=tk.LEFT, padx=4)

        self.year_sb = ttk.Spinbox(controls, from_=1970, to=9999, width=7, textvariable=self.selected_year, command=self.on_year_change)
        self.year_sb.pack(side=tk.LEFT, padx=4)

        next_btn = ttk.Button(controls, text="▶", width=3, command=self.next_month)
        next_btn.pack(side=tk.LEFT, padx=4)

        refresh_btn = ttk.Button(controls, text="Refresh Scan", command=self.refresh_scan)
        refresh_btn.pack(side=tk.LEFT, padx=8)

        legend = tk.Frame(controls, bg=COLOR_BG)
        legend.pack(side=tk.RIGHT, padx=4)
        def legend_item(parent, color, text):
            f = tk.Frame(parent, bg=COLOR_BG)
            swatch = tk.Canvas(f, width=18, height=18, bg=COLOR_BG, highlightthickness=0)
            swatch.create_rectangle(1, 1, 17, 17, fill=color, outline=COLOR_BORDER)
            swatch.pack(side=tk.LEFT)
            lbl = tk.Label(f, text=text, bg=COLOR_BG, fg=COLOR_TEXT)
            lbl.pack(side=tk.LEFT, padx=4)
            f.pack(side=tk.LEFT, padx=8)

        legend_item(legend, COLOR_WORKDAY, "Work (one shift)")
        legend_item(legend, COLOR_BOTH, "Work (both shifts)")
        legend_item(legend, COLOR_NOWORK, "No work")
        legend_item(legend, COLOR_SUNDAY, "Sunday")

        self.canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        self.status = tk.Text(self, height=6, bg=COLOR_PANEL, fg=COLOR_TEXT, bd=0)
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=PADDING, pady=(0, PADDING))
        self.status.insert("1.0", "Tip: Select a folder and month. Click a day to view sample files.\n")
        self.status.config(state="disabled")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TButton", padding=6)
        style.configure("TCombobox", padding=4)

        self.canvas.bind("<Configure>", lambda e: self._draw_calendar())

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            self.selected_folder.set(folder)
            self.folder_label.config(text=f"Folder: {folder}")
            self.refresh_scan()

    def prev_month(self):
        m = self.selected_month.get()
        y = self.selected_year.get()
        if m == 1:
            m = 12
            y -= 1
        else:
            m -= 1
        self.selected_month.set(m)
        self.month_cb.current(m - 1)
        self.selected_year.set(y)
        self._draw_calendar()

    def next_month(self):
        m = self.selected_month.get()
        y = self.selected_year.get()
        if m == 12:
            m = 1
            y += 1
        else:
            m += 1
        self.selected_month.set(m)
        self.month_cb.current(m - 1)
        self.selected_year.set(y)
        self._draw_calendar()

    def on_month_change(self, _evt=None):
        self.selected_month.set(self.month_cb.current() + 1)
        self._draw_calendar()

    def on_year_change(self):
        try:
            y = int(self.year_sb.get())
            self.selected_year.set(y)
        except ValueError:
            pass
        self._draw_calendar()

    def refresh_scan(self):
        folder = Path(self.selected_folder.get()) if self.selected_folder.get() else None
        if not folder:
            messagebox.showinfo("Select Folder", "Please select a folder first.")
            return
        key = (str(folder), self.selected_year.get(), self.selected_month.get())
        if key in self.cache:
            del self.cache[key]
        self._draw_calendar()

    def _get_activity(self, folder: Path, year: int, month: int):
        key = (str(folder), year, month)
        if key not in self.cache:
            activity_map, samples = scan_folder_activity(folder, year, month)
            self.cache[key] = (activity_map, samples)
        return self.cache[key]

    def _draw_calendar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 200 or h < 200:
            return

        y = self.selected_year.get()
        m = self.selected_month.get()
        folder = Path(self.selected_folder.get()) if self.selected_folder.get() else None

        title = f"{calendar.month_name[m]} {y} — {APP_TITLE}"
        self.canvas.create_text(w//2, 18, text=title, fill=COLOR_TEXT, font=("Segoe UI", 16, "bold"))

        left = 10
        top = 40
        right = w - 10
        bottom = h - 10
        grid_w = right - left
        grid_h = bottom - top

        cols = 7
        rows = 7
        col_w = grid_w / cols
        row_h = grid_h / rows

        for c in range(cols):
            x = left + c * col_w
            wd = WEEKDAY_NAMES[c]
            color = COLOR_TEXT if wd != "Sun" else COLOR_SUNDAY
            self.canvas.create_text(x + col_w/2, top + row_h/2 - 12, text=wd, fill=color, font=("Segoe UI", 11, "bold"))

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(y, m)

        activity_map = {}
        samples = defaultdict(list)
        if folder and folder.exists():
            activity_map, samples = self._get_activity(folder, y, m)

        today = date.today()

        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                x0 = left + c * col_w + 4
                y0 = top + r * row_h + 4
                x1 = left + (c + 1) * col_w - 4
                y1 = top + (r + 1) * row_h - 4

                if day == 0:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_BG, outline=COLOR_BG)
                    continue

                d = date(y, m, day)
                is_sun = (c == 6)
                shifts = activity_map.get(d, set())

                if not shifts:
                    bg = COLOR_NOWORK
                elif len(shifts) == 2:
                    bg = COLOR_BOTH
                else:
                    bg = COLOR_WORKDAY

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=bg, outline=COLOR_BORDER)

                dn_color = COLOR_SUNDAY if is_sun else COLOR_TEXT
                self.canvas.create_text(x0 + 10, y0 + 12, text=str(day), anchor="w",
                                        fill=dn_color, font=("Segoe UI", 11, "bold"))

                if not shifts:
                    sub = "—"
                else:
                    sub = " + ".join(sorted(shifts))
                self.canvas.create_text(x1 - 10, y1 - 12, text=sub, anchor="e",
                                        fill=COLOR_MUTED, font=("Segoe UI", 9))

                if d == today:
                    self.canvas.create_rectangle(x0, y0, x1, y1, outline=COLOR_TODAY_OUTLINE, width=2)

                def make_onclick(clicked_date: date):
                    def _on_click(event):
                        self.show_day_details(clicked_date, samples, activity_map.get(clicked_date, set()))
                    return _on_click

                tag = f"day_{y}_{m}_{day}"
                self.canvas.tag_bind(self.canvas.create_rectangle(x0, y0, x1, y1, outline="", fill="", tags=(tag,)),
                                     "<Button-1>", make_onclick(d))
                self.canvas.tag_bind(self.canvas.create_text((x0+x1)/2, (y0+y1)/2, text="", tags=(tag,)),
                                     "<Button-1>", make_onclick(d))

    def show_day_details(self, d: date, samples_map, shifts_set):
        self.status.config(state="normal")
        self.status.delete("1.0", "end")
        self.status.insert("1.0", f"Details for {d.isoformat()}:\n")
        if not shifts_set:
            self.status.insert("end", "No work recorded for this day.\n")
        else:
            self.status.insert("end", f"Shifts with activity: {', '.join(sorted(shifts_set))}\n\n")
        files = samples_map.get(d, [])
        if not files:
            self.status.insert("end", "No sample files recorded for this day.\n")
        else:
            self.status.insert("end", "Sample files (up to 5):\n")
            for f in files:
                self.status.insert("end", f" • {f}\n")
        self.status.config(state="disabled")

def main():
    app = FlyzelCalendar()
    app.mainloop()

if __name__ == "__main__":
    main()
