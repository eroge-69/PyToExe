
import tkinter as tk
from tkinter import ttk

def calculate_depreciated_value():
    try:
        present_value = float(present_value_var.get())
        inflation_rate = float(inflation_rate_var.get())
        years = int(years_var.get())

        rate = 1 - inflation_rate / 100
        depreciated_factor = rate ** years
        future_value = present_value * depreciated_factor

        result_var.set(f"R {future_value:,.2f}")
    except ValueError:
        result_var.set("Invalid input. Please enter valid numbers.")

# Create the main window
root = tk.Tk()
root.title("Inflation Depreciation Calculator")
root.geometry("400x300")
root.resizable(False, False)

# Variables
present_value_var = tk.StringVar()
inflation_rate_var = tk.StringVar(value="6")
years_var = tk.StringVar(value="1")
result_var = tk.StringVar()

# Layout
frame = ttk.Frame(root, padding="20")
frame.pack(fill="both", expand=True)

# Present Value
ttk.Label(frame, text="Present Value (R):").pack(anchor="w")
ttk.Entry(frame, textvariable=present_value_var).pack(fill="x")

# Inflation Rate
ttk.Label(frame, text="Inflation Rate (%):").pack(anchor="w", pady=(10, 0))
ttk.Entry(frame, textvariable=inflation_rate_var).pack(fill="x")

# Years
ttk.Label(frame, text="Years:").pack(anchor="w", pady=(10, 0))
ttk.Entry(frame, textvariable=years_var).pack(fill="x")

# Calculate Button
ttk.Button(frame, text="Calculate", command=calculate_depreciated_value).pack(pady=20)

# Result Display
ttk.Label(frame, text="Future Value:").pack()
ttk.Label(frame, textvariable=result_var, font=("Arial", 14, "bold"), foreground="green").pack()

# Start the GUI loop
root.mainloop()
