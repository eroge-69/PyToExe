import tkinter as tk
from tkinter import messagebox

def calculate_total():
    try:
        iron = float(entry_iron.get())
        plastic = float(entry_plastic.get())
        total = iron * 20 + plastic * 10
        label_result.config(text=f"Total to charge: ${total:.2f}")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for iron and plastic.")

# Create the main window
root = tk.Tk()
root.title("Repair Cost Calculator")

# Iron input
tk.Label(root, text="Total Iron for repair:").grid(row=0, column=0, padx=10, pady=10)
entry_iron = tk.Entry(root)
entry_iron.grid(row=0, column=1, padx=10, pady=10)

# Plastic input
tk.Label(root, text="Total Plastic for repair:").grid(row=1, column=0, padx=10, pady=10)
entry_plastic = tk.Entry(root)
entry_plastic.grid(row=1, column=1, padx=10, pady=10)

# Calculate button
btn_calculate = tk.Button(root, text="Calculate Total", command=calculate_total)
btn_calculate.grid(row=2, column=0, columnspan=2, pady=10)

# Result label
label_result = tk.Label(root, text="Total to charge: $0.00", font=("Arial", 14))
label_result.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
