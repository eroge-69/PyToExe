import tkinter as tk
from tkinter import simpledialog
from datetime import datetime
import random

# Setup main app
root = tk.Tk()
root.overrideredirect(True)  # Remove title bar
root.attributes('-topmost', False)  # NOT on top of other windows
root.configure(bg='black')

# Ask for screen resolution manually
screen_width = int(simpledialog.askstring("Screen Width", "Enter screen width (e.g., 1600):"))
screen_height = int(simpledialog.askstring("Screen Height", "Enter screen height (e.g., 900):"))

# Ask for countdown target time
target_str = simpledialog.askstring("Target Date/Time", "Enter countdown target (YYYY-MM-DD HH:MM:SS):")
target_time = datetime.strptime(target_str, "%Y-%m-%d %H:%M:%S")

# Ask for title
title_text = simpledialog.askstring("Countdown Title", "Enter countdown title:", initialvalue="Time left")

# Font settings
font_size = 24
font_family = "Helvetica"
font_style = (font_family, font_size, "bold")
padding = 20

# Create frame and labels
frame = tk.Frame(root, bg="black", padx=padding, pady=padding)
frame.pack()

title_label = tk.Label(frame, text=title_text, font=font_style, fg="white", bg="black")
title_label.pack(anchor='center')

timer_label = tk.Label(frame, text="", font=font_style, fg="white", bg="black")
timer_label.pack(anchor='center')

# Colors for background & font
light_colors = ['#fefefe', '#e6e6e6', '#cccccc']
dark_colors = ['#222222', '#333333', '#111111']
current_bg = 'black'  # Proper initial assignment

def update_timer():
    now = datetime.now()
    remaining = target_time - now

    if remaining.total_seconds() > 0:
        days = remaining.days
        hours, rem = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        timer_label.config(text=f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s")
        root.after(1000, update_timer)
    else:
        timer_label.config(text="Time's up!")
        title_label.config(text="")

def change_color():
    global current_bg
    use_light = bool(random.getrandbits(1))
    bg = random.choice(light_colors if use_light else dark_colors)
    fg = 'black' if use_light else 'white'
    current_bg = bg
    root.configure(bg=bg)
    frame.configure(bg=bg)
    title_label.configure(bg=bg, fg=fg)
    timer_label.configure(bg=bg, fg=fg)
    root.after(5000, change_color)

# Position the window at top-right
def position_window():
    frame.update_idletasks()
    win_width = frame.winfo_width()
    x = screen_width - win_width - 10
    y = 10
    root.geometry(f"+{x}+{y}")

# Run
update_timer()
change_color()
position_window()
root.mainloop()
