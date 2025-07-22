
import tkinter as tk
from tkinter import ttk

# Conversion function
def convert():
    value = entry.get()
    from_unit = from_unit_var.get()
    to_unit = to_unit_var.get()

    try:
        value = float(value)
    except ValueError:
        result_label.config(text="Please enter a valid number")
        return

    result = 0
    if from_unit == "Kilometers" and to_unit == "Miles":
        result = value * 0.621371
    elif from_unit == "Miles" and to_unit == "Kilometers":
        result = value / 0.621371
    elif from_unit == "Kilograms" and to_unit == "Pounds":
        result = value * 2.20462
    elif from_unit == "Pounds" and to_unit == "Kilograms":
        result = value / 2.20462
    elif from_unit == "Celsius" and to_unit == "Fahrenheit":
        result = (value * 9/5) + 32
    elif from_unit == "Fahrenheit" and to_unit == "Celsius":
        result = (value - 32) * 5/9
    else:
        result = value  # If units are the same

    result_label.config(text=f"Result: {round(result, 2)}")

# GUI setup
root = tk.Tk()
root.title("Unit Converter")
root.geometry("350x300")

# Entry for user input
entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10)

# Dropdown for selecting units
unit_options = ["Kilometers", "Miles", "Kilograms", "Pounds", "Celsius", "Fahrenheit"]

from_unit_var = tk.StringVar(value="Kilometers")
to_unit_var = tk.StringVar(value="Miles")

from_menu = ttk.Combobox(root, textvariable=from_unit_var, values=unit_options, state="readonly", font=("Arial", 12))
from_menu.pack(pady=5)

to_menu = ttk.Combobox(root, textvariable=to_unit_var, values=unit_options, state="readonly", font=("Arial", 12))
to_menu.pack(pady=5)

# Convert button
convert_btn = tk.Button(root, text="Convert", command=convert, font=("Arial", 12), bg="#3498db", fg="white")
convert_btn.pack(pady=10)

# Label for displaying result
result_label = tk.Label(root, text="Result: ", font=("Arial", 14))
result_label.pack(pady=10)

root.mainloop()
