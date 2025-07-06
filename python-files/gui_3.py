import tkinter as tk

# Window Setup
root = tk.Tk()
root.title("Calculator")
root.geometry("500x350")
root.config(bg="#9babbc")

# Fonts
label_font = ("Segoe UI", 12)
entry_font = ("Segoe UI", 12)
button_font = ("Segoe UI", 12, "bold")
result_font = ("Segoe UI", 14, "bold")

# Title Label
title_label = tk.Label(root, text="Simple Calculator", font=("Segoe UI", 16, "bold"),
                       bg="#9babbc", fg="white")
title_label.pack(pady=15)

# Input Frame
frame = tk.Frame(root, bg="#f0f4f8")
frame.pack(pady=10)

# Entry Fields
label_1 = tk.Label(frame, text="Enter number 1:", font=label_font, bg="#f0f4f8")
label_1.grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_1 = tk.Entry(frame, font=entry_font, width=20)
entry_1.grid(row=0, column=1, padx=10, pady=10)

label_2 = tk.Label(frame, text="Enter number 2:", font=label_font, bg="#f0f4f8")
label_2.grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_2 = tk.Entry(frame, font=entry_font, width=20)
entry_2.grid(row=1, column=1, padx=10, pady=10)

# Result Label
result_label = tk.Label(root, text="", font=result_font, bg="#9babbc", fg="white")
result_label.pack(pady=10)

# Calculation Functions
def calculate(op):
    try:
        num1 = float(entry_1.get())
        num2 = float(entry_2.get())

        if op == "+":
            result = num1 + num2
        elif op == "-":
            result = num1 - num2
        elif op == "*":
            result = num1 * num2
        elif op == "/":
            if num2 == 0:
                result_label.config(text="Cannot divide by zero!", fg="red")
                return
            result = num1 / num2
        else:
            result = "Invalid Operation"

        result_label.config(text=f"Result: {result}", fg="lightgreen")
    except ValueError:
        result_label.config(text="Please enter valid numbers!", fg="red")

# Button Frame
btn_frame = tk.Frame(root, bg="#9babbc")
btn_frame.pack(pady=10)

# Buttons
btn_add = tk.Button(btn_frame, text="Add (+)", font=button_font, bg="#4caf50", fg="white",
                    padx=10, pady=5, command=lambda: calculate("+"))
btn_add.grid(row=0, column=0, padx=10)

btn_sub = tk.Button(btn_frame, text="Subtract (-)", font=button_font, bg="#2196f3", fg="white",
                    padx=10, pady=5, command=lambda: calculate("-"))
btn_sub.grid(row=0, column=1, padx=10)

btn_mul = tk.Button(btn_frame, text="Multiply (*)", font=button_font, bg="#ff9800", fg="white",
                    padx=10, pady=5, command=lambda: calculate("*"))
btn_mul.grid(row=0, column=2, padx=10)

btn_div = tk.Button(btn_frame, text="Divide (/)", font=button_font, bg="#f44336", fg="white",
                    padx=10, pady=5, command=lambda: calculate("/"))
btn_div.grid(row=0, column=3, padx=10)

# Run the GUI
root.mainloop()
