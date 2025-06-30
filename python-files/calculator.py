# calculator_app.py

import tkinter as tk

def btn_click(symbol):
    entry.insert(tk.END, symbol)

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

# GUI setup
root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

entry = tk.Entry(root, font=("Arial", 18), bd=10, relief=tk.RIDGE, justify='right')
entry.pack(pady=10, padx=10, fill=tk.BOTH)

# Button layout
buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', '=', '+']
]

for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")
    for btn in row:
        if btn == "=":
            b = tk.Button(frame, text=btn, font=("Arial", 18), bg="lightblue",
                          command=calculate)
        else:
            b = tk.Button(frame, text=btn, font=("Arial", 18),
                          command=lambda b=btn: btn_click(b))
        b.pack(side="left", expand=True, fill="both")

# Clear Button
clear_btn = tk.Button(root, text="Clear", font=("Arial", 18), bg="lightgray", command=clear)
clear_btn.pack(expand=True, fill="both", padx=10, pady=5)

root.mainloop()
