import tkinter as tk
from tkinter import messagebox

def calculate_weight():
    try:
        diameter = float(entry_diameter.get())
        length = float(entry_length.get())
        bars = int(entry_bars.get())

        weight_per_meter = (diameter ** 2) / 162
        total_weight = weight_per_meter * length * bars

        label_result.config(text=f"Total Weight: {total_weight:.2f} kg")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")

# GUI setup
window = tk.Tk()
window.title("Reinforcement Steel Weight Calculator")
window.geometry("400x300")
window.config(padx=20, pady=20)

tk.Label(window, text="Diameter (mm):", font=("Arial", 12)).pack()
entry_diameter = tk.Entry(window, font=("Arial", 12))
entry_diameter.pack()

tk.Label(window, text="Length of One Bar (m):", font=("Arial", 12)).pack()
entry_length = tk.Entry(window, font=("Arial", 12))
entry_length.pack()

tk.Label(window, text="Number of Bars:", font=("Arial", 12)).pack()
entry_bars = tk.Entry(window, font=("Arial", 12))
entry_bars.pack()

tk.Button(window, text="Calculate", font=("Arial", 12), command=calculate_weight).pack(pady=10)

label_result = tk.Label(window, text="", font=("Arial", 14, "bold"))
label_result.pack()

window.mainloop()
