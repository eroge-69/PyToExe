import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta

# Tooltip helper
class CreateToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("tahoma", 9)
        )
        label.pack(ipadx=4)

    def hide_tip(self, event=None):
        tw = self.tip_window
        if tw:
            tw.destroy()
        self.tip_window = None


def safe_get_float(entry, field_name):
    """Try to convert entry to float, else show error dialog."""
    val = entry.get().strip()
    if val == "":
        messagebox.showerror("Missing Input", f"Please enter a value for {field_name}.")
        raise ValueError(f"Missing {field_name}")
    try:
        return float(val)
    except ValueError:
        messagebox.showerror("Invalid Input", f"{field_name} must be a number.")
        raise


def calculate(*args):
    try:
        boss_health = safe_get_float(entry_boss_health, "Boss Health per Fight")
        kill_time = safe_get_float(entry_kill_time, "Kill Time (seconds)")
        total_relics_needed = safe_get_float(entry_relics_needed, "Total Relics Needed")
        relics_owned = safe_get_float(entry_relics_owned, "Relics Owned")
        dmg_per_drop = safe_get_float(entry_dmg_per_drop, "Damage per Relic")
        uptime = safe_get_float(entry_uptime, "Boss Active Time (min)")
        downtime = safe_get_float(entry_downtime, "Boss Respawn Time (min)")

        # Start time
        date = cal_start.get_date()
        try:
            hour = int(spin_hour.get())
            minute = int(spin_min.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Start time must have valid hour and minute.")
            return
        start_time = datetime(date.year, date.month, date.day, hour, minute)

        # Calculate
        relics_remaining = int(total_relics_needed - relics_owned)
        total_damage_needed = relics_remaining * dmg_per_drop
        dps = boss_health / kill_time

        cycle_time = uptime + downtime
        uptime_seconds = uptime * 60
        damage_per_cycle = dps * uptime_seconds
        relics_per_cycle = damage_per_cycle / dmg_per_drop

        cycles_needed = relics_remaining / relics_per_cycle if relics_per_cycle > 0 else 0
        total_minutes = cycles_needed * cycle_time
        total_time = timedelta(minutes=total_minutes)
        end_time = start_time + total_time

        # Update output
        result_text.set(
            f"Relics remaining: {relics_remaining}\n"
            f"Total damage needed: {total_damage_needed:,.0f}\n"
            f"Approximate real-world time: {total_time}\n\n"
            f"Estimated end time: {end_time.strftime('%m/%d/%y %H:%M')}\n\n"
            f"Per Boss Rotation:\n"
            f"- Damage dealt: {damage_per_cycle:,.0f}\n"
            f"- Relics gained: {relics_per_cycle:.2f}"
        )
    except ValueError:
        return  # handled by safe_get_float


# GUI setup
root = tk.Tk()
root.title("Boss Calculator")
root.configure(bg="#1e1e1e")

fields = [
    ("Boss Health per Fight:", "The boss’s total HP in one fight."),
    ("Kill Time (seconds):", "How many seconds it takes you to kill the boss once."),
    ("Total Relics Needed:", "Total relics required for your goal."),
    ("Relics Owned:", "Relics you already have collected."),
    ("Damage per Relic:", "Damage required to earn 1 relic."),
    ("Boss Active Time (min):", "How long the boss stays active before despawning."),
    ("Boss Respawn Time (min):", "Time until the boss respawns after despawning."),
]

entries = []
for label_text, tip in fields:
    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(padx=5, pady=5, anchor="w")
    lbl = tk.Label(frame, text=label_text, fg="white", bg="#1e1e1e")
    lbl.pack(side="left")
    entry = tk.Entry(frame, bg="#2d2d2d", fg="white", insertbackground="white")
    entry.pack(side="left")
    CreateToolTip(lbl, tip)
    entries.append(entry)

(entry_boss_health, entry_kill_time, entry_relics_needed,
 entry_relics_owned, entry_dmg_per_drop, entry_uptime,
 entry_downtime) = entries

# Start time
frame_time = tk.Frame(root, bg="#1e1e1e")
frame_time.pack(padx=5, pady=5, anchor="w")
lbl_time = tk.Label(frame_time, text="Farming Start Time:", fg="white", bg="#1e1e1e")
lbl_time.pack(side="left")

cal_start = DateEntry(frame_time, background="darkblue", foreground="white", borderwidth=2)
cal_start.pack(side="left")
spin_hour = tk.Spinbox(frame_time, from_=0, to=23, width=3, bg="#2d2d2d", fg="white", insertbackground="white")
spin_hour.pack(side="left")
spin_min = tk.Spinbox(frame_time, from_=0, to=59, width=3, bg="#2d2d2d", fg="white", insertbackground="white")
spin_min.pack(side="left")

CreateToolTip(lbl_time, "When you want your farming session to begin.")

# Result box
result_text = tk.StringVar()
result_box = tk.Label(root, textvariable=result_text, fg="white", bg="#2d2d2d",
                      justify="left", anchor="nw", width=60, height=12,
                      relief="sunken", padx=5, pady=5, font=("Consolas", 10))
result_box.pack(padx=10, pady=10, fill="both", expand=True)

# Bind live updates
for e in entries:
    e.bind("<KeyRelease>", calculate)
spin_hour.bind("<KeyRelease>", calculate)
spin_min.bind("<KeyRelease>", calculate)
cal_start.bind("<<DateEntrySelected>>", calculate)

root.mainloop()