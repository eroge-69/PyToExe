import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Configuration
TIME_ZONES = [
    "Eastern Standard Time",
    "Central Standard Time",
    "Mountain Standard Time",
    "Pacific Standard Time",
    "Alaskan Standard Time",
    "Hawaiian Standard Time",
    "India Standard Time",
]

ZONE_OFFSETS = {
    "Eastern Standard Time":  timedelta(hours=-5),
    "Central Standard Time":  timedelta(hours=-6),
    "Mountain Standard Time": timedelta(hours=-7),
    "Pacific Standard Time":  timedelta(hours=-8),
    "Alaskan Standard Time": timedelta(hours=-9),
    "Hawaiian Standard Time": timedelta(hours=-10),
    "India Standard Time":    timedelta(hours=5, minutes=30),
}

def apply_timezone(zone_name):
    try:
        subprocess.run([
            "tzutil", "/s", zone_name
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        messagebox.showinfo("Success", f"Time zone set to:\n{zone_name}")
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="ignore") or f"Code {e.returncode}"
        messagebox.showerror("Error", f"Failed to set time zone:\n{msg}")

# Digital Clock Frame
class DigitalClock(ttk.Frame):
    def __init__(self, parent, zone_name, offset, **kwargs):
        super().__init__(parent, **kwargs)
        self.zone_name = zone_name
        self.offset = offset
        self.use_dst = True
        self.configure(style="Card.TFrame")

        self.label_zone = ttk.Label(self, text=zone_name, style="Title.TLabel")
        self.label_zone.pack(pady=(10, 0))
        self.label_time = ttk.Label(self, text="", style="Time.TLabel")
        self.label_time.pack(pady=(0, 10))

        self.bind("<Button-1>", self.on_click)
        self.label_time.bind("<Button-1>", self.on_click)
        self.label_zone.bind("<Button-1>", self.on_click)

    def update(self):
        now_utc = datetime.utcnow()
        offset = self.offset
        if self.use_dst:
            # Simple DST adjustment: add 1 hour if in DST months (approximation)
            # DST roughly from second Sunday in March to first Sunday in November in US
            month = now_utc.month
            day = now_utc.day
            weekday = now_utc.weekday()  # Monday=0 ... Sunday=6

            # Find second Sunday in March
            if month == 3:
                first_sunday = 7 - (now_utc.replace(day=1).weekday() + 1) % 7
                second_sunday = first_sunday + 7
                if day >= second_sunday:
                    dst_active = True
                else:
                    dst_active = False
            # Find first Sunday in November
            elif month == 11:
                first_sunday = 7 - (now_utc.replace(day=1).weekday() + 1) % 7
                if day < first_sunday:
                    dst_active = True
                else:
                    dst_active = False
            elif 4 <= month <= 10:
                dst_active = True
            else:
                dst_active = False

            if dst_active:
                offset += timedelta(hours=1)

        now = now_utc + offset
        self.label_time.config(text=now.strftime("%I:%M:%S %p"))

    def on_click(self, _evt):
        if messagebox.askyesno("Apply Time Zone", f"Set system time zone to\n{self.zone_name}?"):
            threading.Thread(target=apply_timezone, args=(self.zone_name,), daemon=True).start()

def run_app():
    root = tk.Tk()
    root.title("Time Zone Manager")
    root.geometry("830x480")  # Slightly smaller size
    root.configure(bg="#eaf3fb")
    root.resizable(True, True)

    # Help menu
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Contact Info", command=lambda: messagebox.showinfo(
        "Contact Information",
        "For support, please contact:\n\nEmail: sub.karthikeyan@enoahisolution.com\nPhone: 7200510593"
    ))
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TNotebook", background="#eaf3fb", borderwidth=0)
    style.configure("TNotebook.Tab", background="#d0e3f0", foreground="black", padding=10)
    style.map("TNotebook.Tab", background=[("selected", "#a6c8e6")])

    style.configure("Card.TFrame", background="white")
    style.configure("Title.TLabel", background="white", foreground="#003366", font=("Segoe UI", 11, "bold"))
    style.configure("Time.TLabel", background="white", foreground="#003366", font=("Consolas", 18, "bold"))

    notebook = ttk.Notebook(root)

    tab1 = ttk.Frame(notebook, padding=(10, 10, 10, 10), style="Card.TFrame")
    notebook.add(tab1, text="Change Time Zone")

    # Center alignment frame
    center_frame = ttk.Frame(tab1, style="Card.TFrame")
    center_frame.place(relx=0.5, rely=0.3, anchor="center")

    ttk.Label(center_frame, text="Select your time zone:", style="Title.TLabel").pack(pady=(0, 8))

    combo = ttk.Combobox(center_frame, values=TIME_ZONES, state="readonly", width=35, font=("Segoe UI", 10))
    combo.pack(ipady=3)
    combo.configure(background="#915c83", foreground="white")  # Antique Fuchsia style

    def on_apply():
        zone = combo.get()
        if not zone:
            messagebox.showwarning("Select", "Please pick a time zone.")
            return
        threading.Thread(target=apply_timezone, args=(zone,), daemon=True).start()

    apply_button = ttk.Button(center_frame, text="Apply", command=on_apply)
    apply_button.pack(pady=(10, 0))
    apply_button.configure(style="Green.TButton")

    style.configure("Green.TButton", background="#28a745", foreground="white", font=("Segoe UI", 10, "bold"))
    style.map("Green.TButton",
              foreground=[('active', 'white')],
              background=[('active', '#218838')])

    tab2 = ttk.Frame(notebook, padding=8, style="Card.TFrame")  # reduced padding
    notebook.add(tab2, text="Digital Clocks")

    tab2.columnconfigure((0, 1, 2), weight=1)
    tab2.rowconfigure((1, 2, 3), weight=1)

    dst_note = ttk.Label(tab2, text="Note: All times include daylight saving adjustment.\nClick the button below to disable it.", 
                        style="Title.TLabel", justify="center")
    dst_note.grid(row=0, column=0, columnspan=3, pady=(0, 8), sticky="n")

    clocks = []
    for i, (zone, offset) in enumerate(ZONE_OFFSETS.items()):
        frame = DigitalClock(tab2, zone, offset)
        frame.grid(row=(i//3)+1, column=i%3, padx=12, pady=12, sticky="nsew")
        clocks.append(frame)

    # DST toggle button
    def toggle_dst():
        new_state = not clocks[0].use_dst
        for clk in clocks:
            clk.use_dst = new_state
        if new_state:
            dst_button.config(text="Disable Daylight Saving")
        else:
            dst_button.config(text="Enable Daylight Saving")

    dst_button = ttk.Button(tab2, text="Disable Daylight Saving", command=toggle_dst)
    dst_button.grid(row=4, column=0, columnspan=3, pady=(0, 10))

    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def tick():
        for clk in clocks:
            clk.update()
        root.after(1000, tick)
    tick()

    root.mainloop()

if __name__ == "__main__":
    run_app()
