import tkinter as tk
from tkinter import messagebox

def convert():
    try:
        val = float(entry_val.get())
        unit = unit_var.get()
        cf = float(entry_cf.get())
        cv = float(entry_cv.get())
        if unit == "imperial":
            # hundreds of ft³ → m³
            m3 = val * 2.83
        else:
            m3 = val
        kwh = (m3 * cf * cv) / 3.6
        result_var.set(f"{kwh:.2f}")
    except:
        messagebox.showerror("Error", "Please check your inputs.")

root = tk.Tk()
root.title("Gas kWh Converter")

unit_var = tk.StringVar(value="metric")
result_var = tk.StringVar()

tk.Label(root, text="Value:").grid(row=0, column=0)
entry_val = tk.Entry(root); entry_val.grid(row=0, column=1)
tk.Radiobutton(root, text="Metric (m³)", variable=unit_var, value="metric").grid(row=1, column=0)
tk.Radiobutton(root, text="Imperial (hundreds ft³)", variable=unit_var, value="imperial").grid(row=1, column=1)

tk.Label(root, text="Correction Factor (e.g. 1.02264):").grid(row=2, column=0, columnspan=2)
entry_cf = tk.Entry(root); entry_cf.grid(row=3, column=0, columnspan=2)
entry_cf.insert(0, "1.02264")

tk.Label(root, text="Calorific Value (e.g. 40):").grid(row=4, column=0, columnspan=2)
entry_cv = tk.Entry(root); entry_cv.grid(row=5, column=0, columnspan=2)
entry_cv.insert(0, "40")

tk.Button(root, text="Convert", command=convert).grid(row=6, column=0, columnspan=2, pady=5)
tk.Label(root, text="kWh:").grid(row=7, column=0)
tk.Label(root, textvariable=result_var).grid(row=7, column=1)

root.mainloop()
