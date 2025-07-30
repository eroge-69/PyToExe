
import tkinter as tk
from tkinter import messagebox

def dms_to_decimal(degrees, minutes, seconds):
    try:
        degrees = float(degrees)
        minutes = float(minutes)
        seconds = float(seconds)
        sign = -1 if degrees < 0 else 1
        return sign * (abs(degrees) + minutes / 60 + seconds / 3600)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for DMS fields.")
        return None

def decimal_to_dms(decimal_degrees):
    sign = -1 if decimal_degrees < 0 else 1
    decimal_degrees = abs(decimal_degrees)
    degrees = int(decimal_degrees)
    minutes = int((decimal_degrees - degrees) * 60)
    seconds = (decimal_degrees - degrees - minutes / 60) * 3600
    return f"{'-' if sign < 0 else ''}{degrees}° {minutes}' {seconds:.2f}\""

def calculate_grid_bearing():
    tb_deg = true_bearing_deg.get()
    tb_min = true_bearing_min.get()
    tb_sec = true_bearing_sec.get()

    gc_deg = convergence_deg.get()
    gc_min = convergence_min.get()
    gc_sec = convergence_sec.get()

    true_bearing = dms_to_decimal(tb_deg, tb_min, tb_sec)
    convergence = dms_to_decimal(gc_deg, gc_min, gc_sec)

    if true_bearing is not None and convergence is not None:
        grid_bearing = true_bearing - convergence
        result.set(f"Grid Bearing: {decimal_to_dms(grid_bearing)}")

# GUI Setup
root = tk.Tk()
root.title("Gyro to Grid Bearing Calculator")

tk.Label(root, text="True Bearing (DMS):").grid(row=0, column=0, padx=5, pady=5)
true_bearing_deg = tk.Entry(root, width=5)
true_bearing_deg.grid(row=0, column=1)
tk.Label(root, text="°").grid(row=0, column=2)
true_bearing_min = tk.Entry(root, width=5)
true_bearing_min.grid(row=0, column=3)
tk.Label(root, text="'").grid(row=0, column=4)
true_bearing_sec = tk.Entry(root, width=5)
true_bearing_sec.grid(row=0, column=5)
tk.Label(root, text='\"').grid(row=0, column=6)

tk.Label(root, text="Grid Convergence (DMS):").grid(row=1, column=0, padx=5, pady=5)
convergence_deg = tk.Entry(root, width=5)
convergence_deg.grid(row=1, column=1)
tk.Label(root, text="°").grid(row=1, column=2)
convergence_min = tk.Entry(root, width=5)
convergence_min.grid(row=1, column=3)
tk.Label(root, text="'").grid(row=1, column=4)
convergence_sec = tk.Entry(root, width=5)
convergence_sec.grid(row=1, column=5)
tk.Label(root, text='\"').grid(row=1, column=6)

result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 12), fg="blue").grid(row=3, column=0, columnspan=7, pady=10)

tk.Button(root, text="Calculate Grid Bearing", command=calculate_grid_bearing).grid(row=2, column=0, columnspan=7, pady=10)

root.mainloop()
