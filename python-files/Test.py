import tkinter as tk
from math import pi, sqrt

def calculate_perimeter():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())

        # Ramanujan's approximation
        perimeter = pi * (3*(a + b) - sqrt((3*a + b)*(a + 3*b)))
        result_label.config(text=f"Perimeter ≈ {perimeter:.4f}")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

# Setup the GUI
root = tk.Tk()
root.title("Ellipse Perimeter Calculator")

# Labels and entries
tk.Label(root, text="Semi-major axis (a):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_a = tk.Entry(root)
entry_a.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Semi-minor axis (b):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_b = tk.Entry(root)
entry_b.grid(row=1, column=1, padx=10, pady=5)

# Calculate button
calc_button = tk.Button(root, text="Calculate Perimeter", command=calculate_perimeter)
calc_button.grid(row=2, column=0, columnspan=2, pady=10)

# Result display
result_label = tk.Label(root, text="Enter values and press Calculate.")
result_label.grid(row=3, column=0, columnspan=2, pady=5)

# Run the GUI
root.mainloop()