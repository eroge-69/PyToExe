import tkinter as tk
from tkinter import messagebox

def add():
    try:
        a = float(entry_num1.get())
        b = float(entry_num2.get())
        result_var.set(f"Result: {a + b}")
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers!")

def subtract():
    try:
        a = float(entry_num1.get())
        b = float(entry_num2.get())
        result_var.set(f"Result: {a - b}")
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers!")

def multiply():
    try:
        a = float(entry_num1.get())
        b = float(entry_num2.get())
        result_var.set(f"Result: {a * b}")
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers!")

def divide():
    try:
        a = float(entry_num1.get())
        b = float(entry_num2.get())
        if b == 0:
            raise ZeroDivisionError("Division by zero.")
        result_var.set(f"Result: {a / b}")
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers!")
    except ZeroDivisionError:
        messagebox.showerror("Math Error", "Division by zero is not allowed!")

# Create the main window
app = tk.Tk()
app.title("Ethana Basic Calculator")
app.geometry("300x250")
app.resizable(False, False)

# Title label
title_label = tk.Label(app, text="Ethana Basic Calculator", font=("Helvetica", 14, "bold"))
title_label.pack(pady=10)

# Number 1 input
frame_num1 = tk.Frame(app)
frame_num1.pack(pady=5)
label_num1 = tk.Label(frame_num1, text="Number 1:")
label_num1.pack(side=tk.LEFT, padx=5)
entry_num1 = tk.Entry(frame_num1, width=15)
entry_num1.pack(side=tk.LEFT)

# Number 2 input
frame_num2 = tk.Frame(app)
frame_num2.pack(pady=5)
label_num2 = tk.Label(frame_num2, text="Number 2:")
label_num2.pack(side=tk.LEFT, padx=5)
entry_num2 = tk.Entry(frame_num2, width=15)
entry_num2.pack(side=tk.LEFT)

# Operation buttons
frame_buttons = tk.Frame(app)
frame_buttons.pack(pady=10)
btn_add = tk.Button(frame_buttons, text="Add", width=8, command=add)
btn_add.grid(row=0, column=0, padx=5, pady=5)
btn_subtract = tk.Button(frame_buttons, text="Subtract", width=8, command=subtract)
btn_subtract.grid(row=0, column=1, padx=5, pady=5)
btn_multiply = tk.Button(frame_buttons, text="Multiply", width=8, command=multiply)
btn_multiply.grid(row=1, column=0, padx=5, pady=5)
btn_divide = tk.Button(frame_buttons, text="Divide", width=8, command=divide)
btn_divide.grid(row=1, column=1, padx=5, pady=5)

# Result display
result_var = tk.StringVar()
result_var.set("Result: ")
result_label = tk.Label(app, textvariable=result_var, font=("Helvetica", 12))
result_label.pack(pady=10)

# Exit button
exit_button = tk.Button(app, text="Exit", command=app.quit)
exit_button.pack(pady=10)

app.mainloop()
