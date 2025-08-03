import tkinter as tk
from datetime import datetime

# Function to calculate countdown
def calculate():
    target_date = datetime(2025, 10, 6, 9, 30, 0)
    today = datetime.today()

    days_remaining = (target_date - today).days
    weeks = days_remaining // 7
    remaining_days = days_remaining % 7
    full_date = today.strftime("%A, %d %B %Y")

    # Update GUI
    full_date_label.config(text=f"📅 {full_date}")
    days_label.config(text=f"🕒 {days_remaining} Days Left")
    weeks_label.config(text=f"📆 {weeks} Weeks & {remaining_days} Days")
    exam_label.config(
        text=f"🎯 I will enter the exam room in {weeks} weeks,\nwith confidence and pride. 🧠💥"
    )

# Create window
root = tk.Tk()
root.title("🔥 PSLE Countdown 🔥")
root.geometry("600x400")
root.configure(bg="#ffe4e1")  # Light peach background

# Title
title_label = tk.Label(
    root,
    text="🎓 PSLE Countdown Tracker",
    font=("Helvetica", 24, "bold"),
    bg="#ffe4e1",
    fg="#8B0000"
)
title_label.pack(pady=20)

# Full date
full_date_label = tk.Label(
    root,
    text="📅",
    font=("Helvetica", 16),
    bg="#ffe4e1"
)
full_date_label.pack(pady=10)

# Days left
days_label = tk.Label(
    root,
    text="",
    font=("Helvetica", 20, "bold"),
    bg="#ffe4e1",
    fg="#FF4500"
)
days_label.pack(pady=5)

# Weeks left
weeks_label = tk.Label(
    root,
    text="",
    font=("Helvetica", 18),
    bg="#ffe4e1",
    fg="#1E90FF"
)
weeks_label.pack(pady=5)

# Motivational message
exam_label = tk.Label(
    root,
    text="",
    font=("Helvetica", 16, "italic"),
    bg="#ffe4e1",
    fg="#006400",
    wraplength=550,
    justify="center"
)
exam_label.pack(pady=20)

# Button
calculate_button = tk.Button(
    root,
    text="🚀 Show Countdown",
    font=("Helvetica", 16, "bold"),
    bg="#FF69B4",
    fg="white",
    activebackground="#FF1493",
    padx=20,
    pady=10,
    command=calculate
)
calculate_button.pack()

# Run the app
root.mainloop()
