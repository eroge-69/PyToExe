import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def calculate_time():
    current_time_str = entry_time.get()
    distance_str = entry_distance.get()
    speed_str = entry_speed.get()

    # Validate inputs
    if not current_time_str or not distance_str or not speed_str:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    try:
        # Parse current time
        current_time = datetime.strptime(current_time_str, "%H:%M")
    except ValueError:
        messagebox.showerror("Time Format Error", "Current Time must be in hh:mm format.")
        return

    try:
        distance_km = float(distance_str)
        speed_m_s = float(speed_str)
        if speed_m_s <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Value Error", "Distance and Speed must be positive numbers.")
        return

    # Convert distance to meters
    distance_m = distance_km * 1000

    # Time required in seconds
    time_required_sec = distance_m / speed_m_s

    # Add to current time
    arrival_time = current_time + timedelta(seconds=time_required_sec)
    result = arrival_time.strftime("%H:%M")

    label_result.config(text=f"Arrival Time: {result}")

# Create window
root = tk.Tk()
root.title("Travel Time Calculator")
root.geometry("350x250")

# Labels and inputs
tk.Label(root, text="Current Time (hh:mm):").pack(pady=5)
entry_time = tk.Entry(root)
entry_time.pack()

tk.Label(root, text="Distance (km):").pack(pady=5)
entry_distance = tk.Entry(root)
entry_distance.pack()

tk.Label(root, text="Speed (m/s):").pack(pady=5)
entry_speed = tk.Entry(root)
entry_speed.insert(0, "22")  # Default speed
entry_speed.pack()

# Calculate button
btn = tk.Button(root, text="Calculate", command=calculate_time)
btn.pack(pady=15)

# Result label
label_result = tk.Label(root, text="", font=("Arial", 12))
label_result.pack(pady=10)

# Run the application
root.mainloop()
