import tkinter as tk
from tkinter import messagebox

def calculate_burst_time():
    try:
        rpm = float(entry_rpm.get())
        ammo = float(entry_ammo.get())
        rps = rpm / 60
        burst_time = ammo / rps
        result_label.config(text=f"Burst Time: {burst_time:.2f} seconds")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")

# Create the main window
window = tk.Tk()
window.title("Burst Time Calculator")
window.geometry("300x200")

# RPM input
tk.Label(window, text="RPM:").pack()
entry_rpm = tk.Entry(window)
entry_rpm.pack()

# Ammo input
tk.Label(window, text="Ammo:").pack()
entry_ammo = tk.Entry(window)
entry_ammo.pack()

# Calculate button
tk.Button(window, text="Calculate", command=calculate_burst_time).pack(pady=10)

# Result label
result_label = tk.Label(window, text="Burst Time: --")
result_label.pack()

# Start the GUI event loop
window.mainloop()