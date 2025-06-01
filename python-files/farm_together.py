import tkinter as tk
from tkinter import messagebox

def calculate_roi():
    try:
        total_gold = float(entry_total_gold.get())
        gold_per_crop = float(entry_gold_per_crop.get())
        hours = int(entry_hours.get())
        minutes = int(entry_minutes.get())

        # Total grow time in minutes
        grow_time_minutes = hours * 60 + minutes
        if grow_time_minutes == 0:
            raise ValueError("Grow time cannot be zero.")

        # Number of crops that can be planted
        crop_count = total_gold // gold_per_crop

        # Total profit
        total_profit = crop_count * gold_per_crop

        # ROI per minute
        roi_per_minute = total_profit / grow_time_minutes

        label_result.config(text=f"ROI: {roi_per_minute:.2f} gold/min")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# UI Setup
root = tk.Tk()
root.title("Crop ROI Calculator")

tk.Label(root, text="Total Gold:").grid(row=0, column=0, sticky="e")
entry_total_gold = tk.Entry(root)
entry_total_gold.grid(row=0, column=1)

tk.Label(root, text="Gold per Crop:").grid(row=1, column=0, sticky="e")
entry_gold_per_crop = tk.Entry(root)
entry_gold_per_crop.grid(row=1, column=1)

tk.Label(root, text="Grow Time - Hours:").grid(row=2, column=0, sticky="e")
entry_hours = tk.Entry(root)
entry_hours.grid(row=2, column=1)

tk.Label(root, text="Grow Time - Minutes:").grid(row=3, column=0, sticky="e")
entry_minutes = tk.Entry(root)
entry_minutes.grid(row=3, column=1)

tk.Button(root, text="Calculate ROI", command=calculate_roi).grid(row=4, column=0, columnspan=2, pady=10)

label_result = tk.Label(root, text="ROI: ")
label_result.grid(row=5, column=0, columnspan=2)

root.mainloop()
