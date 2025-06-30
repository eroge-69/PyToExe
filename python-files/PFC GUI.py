import tkinter as tk
from tkinter import messagebox
import math

def calculate_correction():
    try:
        real_power = float(entry_real_power.get())
        PF1 = float(entry_PF1.get())
        PF2 = float(entry_PF2.get())

        if not (-1 <= PF2 <= 1):
            raise ValueError("PF2 must be between -1 and 1")

        # Apparent Power
        apparent_power = real_power / PF1

        # Current Reactive Power
        reactive_power = math.sqrt(apparent_power**2 - real_power**2)

        # Desired Reactive Power
        angle = math.acos(PF2)
        new_reactive_power = real_power * math.tan(angle)

        # Power Factor Correction
        delta_Q = reactive_power - new_reactive_power

        result_label.config(
            text=f"Power Factor Correction required: {delta_Q:.2f} kVAR"
        )

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


# GUI setup
root = tk.Tk()
root.title("Power Factor Correction Calculator")
root.geometry("400x300")

tk.Label(root, text="Load Rating (kW):").pack(pady=5)
entry_real_power = tk.Entry(root)
entry_real_power.pack()

tk.Label(root, text="Current Power Factor (PF1):").pack(pady=5)
entry_PF1 = tk.Entry(root)
entry_PF1.pack()

tk.Label(root, text="Desired Power Factor (PF2):").pack(pady=5)
entry_PF2 = tk.Entry(root)
entry_PF2.pack()

tk.Button(root, text="Calculate Correction", command=calculate_correction).pack(pady=15)

result_label = tk.Label(root, text="", fg="blue", font=("Arial", 12))
result_label.pack(pady=10)

root.mainloop()