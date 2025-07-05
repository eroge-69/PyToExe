import tkinter as tk
from tkinter import messagebox
import calendar
import datetime

# === Calculator Functionality ===
def evaluate_expression():
    try:
        result = eval(calc_entry.get())
        calc_entry.delete(0, tk.END)
        calc_entry.insert(tk.END, str(result))
    except:
        messagebox.showerror("Error", "Invalid Expression")

# === Calendar Viewer ===
def show_calendar():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    cal = calendar.month(year, month)
    messagebox.showinfo(f"Calendar {month}/{year}", cal)

# === GUI Setup ===
root = tk.Tk()
root.title("Calculator + Calendar")
root.geometry("300x300")

# Calculator
tk.Label(root, text="🧮 Calculator").pack()
calc_entry = tk.Entry(root, width=25)
calc_entry.pack(pady=5)

tk.Button(root, text="=", command=evaluate_expression).pack()

# Calendar
tk.Label(root, text="📅 Calendar").pack(pady=(20, 0))
tk.Button(root, text="Show This Month", command=show_calendar).pack(pady=5)

root.mainloop()
