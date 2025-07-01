import tkinter as tk
from tkinter import messagebox
import math

def calculate():
    try:
        dose = float(dose_entry.get())
        days_per_week = int(days_entry.get())
        total_days = int(total_days_entry.get())

        total_amount = dose * days_per_week * (total_days / 7)
        suggested_1 = math.ceil(total_amount / 5) * 5
        suggested_2 = suggested_1 + 5

        result_label.config(text=f"Total Required: {total_amount:.2f} mL", fg="red")
        suggestion_label.config(
            text=f"Suggested: {suggested_1} mL, {suggested_2} mL", fg="green"
        )
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")

# GUI Setup
root = tk.Tk()
root.title("Sweet Treat Volume Estimator")
root.geometry("400x300")
root.configure(bg="white")

font_style = ("Arial", 12)

# Labels and Inputs
tk.Label(root, text="Dose per Use (mL):", bg="white", font=font_style).pack(pady=5)
dose_entry = tk.Entry(root, bg="yellow", font=font_style)
dose_entry.pack()

tk.Label(root, text="Days per Week:", bg="white", font=font_style).pack(pady=5)
days_entry = tk.Entry(root, bg="yellow", font=font_style)
days_entry.pack()

tk.Label(root, text="Total Days:", bg="white", font=font_style).pack(pady=5)
total_days_entry = tk.Entry(root, bg="yellow", font=font_style)
total_days_entry.pack()

tk.Button(root, text="Calculate", command=calculate, font=("Arial", 12, "bold")).pack(pady=15)

result_label = tk.Label(root, text="", bg="white", font=font_style)
result_label.pack()

suggestion_label = tk.Label(root, text="", bg="white", font=font_style)
suggestion_label.pack()

root.mainloop()
