import tkinter as tk
from tkinter import messagebox

def calc_tax(annual_salary):
    slabs = [
        (600_000, 0, 0, 0),
        (1_200_000, 0.05, 600_000, 0),
        (2_200_000, 0.15, 1_200_000, 30_000),
        (3_200_000, 0.25, 2_200_000, 180_000),
        (4_100_000, 0.30, 3_200_000, 430_000),
        (float('inf'), 0.35, 4_100_000, 700_000),
    ]
    for upper, rate, base, extra in slabs:
        if annual_salary <= upper:
            return max(extra + rate * (annual_salary - base), 0)
    return 0

def calculate_from_salary():
    try:
        annual = float(entry_salary.get())
        tax = calc_tax(annual)
        monthly = annual / 12
        result.set(f"Monthly Salary: {monthly:,.2f} PKR\nAnnual Tax: {tax:,.2f} PKR")
    except:
        messagebox.showerror("Error", "Invalid number for salary.")

def calculate_from_tax():
    try:
        paid_tax = float(entry_tax.get())
        est = 600_000
        while est < 10_000_000_000:
            if abs(calc_tax(est) - paid_tax) < 1:
                break
            est += 100
        monthly = est / 12
        result.set(f"Estimated Annual Salary: {est:,.2f} PKR\nMonthly Salary: {monthly:,.2f} PKR")
    except:
        messagebox.showerror("Error", "Invalid number for tax.")

# GUI Setup
window = tk.Tk()
window.title("Pakistan Tax Calculator 2024‑25")
window.geometry("400x350")
window.configure(bg="#f0f0f0")

tk.Label(window, text="Enter Annual Salary (PKR):", bg="#f0f0f0").pack(pady=5)
entry_salary = tk.Entry(window, width=30); entry_salary.pack()
tk.Button(window, text="Calculate Tax", command=calculate_from_salary).pack(pady=5)

tk.Label(window, text="OR", bg="#f0f0f0").pack(pady=5)

tk.Label(window, text="Enter Annual Paid Tax (PKR):", bg="#f0f0f0").pack(pady=5)
entry_tax = tk.Entry(window, width=30); entry_tax.pack()
tk.Button(window, text="Estimate Salary", command=calculate_from_tax).pack(pady=5)

result = tk.StringVar()
tk.Label(window, textvariable=result, bg="#f0f0f0", fg="blue", font=("Arial", 11), wraplength=380, justify="center").pack(pady=15)
tk.Label(window, text="Created by ChatGPT", bg="#f0f0f0", fg="gray", font=("Arial", 8)).pack(side="bottom", pady=5)

window.mainloop()
