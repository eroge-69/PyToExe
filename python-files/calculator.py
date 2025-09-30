import tkinter as tk
import tkinter.messagebox
from tkinter.constants import SUNKEN

# Create main window
win = tk.Tk()
win.title('Calculator')

# Set fixed window size
win.geometry('500x640')
win.resizable(False, False)

# Create main frame
frame = tk.Frame(win, bg="#2C3E50", padx=10)
frame.pack(fill=tk.BOTH, expand=True)

# Font
font = ("Helvetica", 30)

# Entry display
entry = tk.Entry(frame, relief=SUNKEN, borderwidth=2, width=30, font=font, bg="#ECF0F1", justify='right')
entry.grid(row=0, column=0, columnspan=4, ipady=10, pady=20, sticky="nsew")

# Helper: check if character is an operator
def is_operator(char):
    return char in '+-/*X'

# ✅ Smart character input
def click(value):
    current_input = entry.get()

    # If input is empty, prevent starting with operator (except minus for negative numbers)
    if not current_input and is_operator(value) and value != '-':
        return

    # If last character is an operator and new value is also an operator → replace
    if current_input and is_operator(current_input[-1]) and is_operator(value):
        entry.delete(len(current_input)-1, tk.END)
        entry.insert(tk.END, value)
        return

    # Else, just insert as usual
    entry.insert(tk.END, value)

# ✅ Evaluate result
def equal():
    try:
        expression = entry.get().replace('X', '*')
        if len(expression) > 50:
            tk.messagebox.showinfo("Error", "Expression too long")
            return
        result = str(eval(expression))
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except Exception:
        tk.messagebox.showinfo("Error", "Syntax Error")

# ✅ Clear the entry
def clear():
    entry.delete(0, tk.END)

# ✅ Backspace (delete last character)
def backspace():
    current_input = entry.get()
    if current_input:
        entry.delete(len(current_input)-1, tk.END)

# Buttons layout
buttons = [
    ('C', 1, 0), ('1', 1, 1), ('2', 1, 2), ('3', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('+', 2, 3),
    ('7', 3, 0), ('8', 3, 1), ('9', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('X', 4, 2), ('/', 4, 3)
]

# Create number and operator buttons
for txt, r, c in buttons:
    if txt == 'C':
        command = clear
    else:
        command = lambda t=txt: click(t)

    btn = tk.Button(frame, text=txt, padx=20, pady=20, font=font,
                    bg="#1ABC9C", fg="white", relief="flat",
                    activebackground="#16A085", command=command)
    btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

# Backspace button
backspace_button = tk.Button(frame, text="←", padx=20, pady=20, font=font,
                             bg="#E67E22", fg="white", relief="flat",
                             activebackground="#D35400", command=backspace)
backspace_button.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)

# Equal button
equal_button = tk.Button(frame, text="=", padx=20, pady=20, font=font,
                         bg="#2980B9", fg="white", relief="flat",
                         activebackground="#3498DB", command=equal)
equal_button.grid(row=5, column=2, columnspan=2, sticky="nsew", padx=5, pady=10)

# Make rows/columns expandable
for i in range(6):
    frame.grid_rowconfigure(i, weight=1)
for j in range(4):
    frame.grid_columnconfigure(j, weight=1)

# Start the app
win.mainloop()
