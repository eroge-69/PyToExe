import tkinter as tk
from tkinter import messagebox

# Expression string
expression = ""

def press(key):
    global expression
    if key == "=":
        try:
            result = str(eval(expression))
            display_var.set(result)
            expression = result
        except:
            messagebox.showerror("Error", "Invalid Expression")
            display_var.set("")
            expression = ""
    elif key == "C":
        expression = ""
        display_var.set("")
    else:
        expression += str(key)
        display_var.set(expression)

# GUI setup
root = tk.Tk()
root.title("Windows Calculator")
root.geometry("300x400")
root.resizable(False, False)

# Display
display_var = tk.StringVar()
entry = tk.Entry(root, textvariable=display_var, font=("Arial", 24), bd=10, relief=tk.RIDGE, justify="right")
entry.pack(fill=tk.BOTH, ipadx=8, ipady=15, pady=10, padx=10)

# Buttons
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C"]
]

for row_values in buttons:
    row = tk.Frame(root)
    row.pack(expand=True, fill="both")
    for char in row_values:
        btn = tk.Button(row, text=char, font=("Arial", 18), relief=tk.RIDGE)
        btn.pack(side="left", expand=True, fill="both")
        btn.config(command=lambda c=char: press(c))

root.mainloop()
