import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        expression = entry.get()
        result = eval(expression)
        entry.delete(0, tk.END)
        entry.insert(0, str(result))
    except ZeroDivisionError:
        messagebox.showerror("Math Error","You Can't Divide By Zero!")
    except Exception as e:
        messagebox.showerror("Error",f"Invalide input{e}")

def press(key):
    entry.insert(tk.END, key)

def clear():
    entry.delete(0, tk.END)

root= tk.Tk()
root.title("Yadel's simple calculater")

entry= tk.Entry(root, width=25, font=('Arial', 16), borderwidth=2, relief="ridge", justify='right')
entry.grid(row=0, column=0, columnspan=4, pady=10, padx=10)

buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('+', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('*', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('C', 4, 2), ('/', 4, 3),
]

for (text, row, col) in buttons:
    if text == 'C':
        tk.Button(root, text=text, width=5, height=2, font=('Arial', 14),
                  command=clear).grid(row=row, column=col, padx=5, pady=5)
    else:
        tk.Button(root, text=text, width=5, height=2, font=('Arial', 14),
                  command=lambda val=text: press(val)).grid(row=row, column=col, padx=5, pady=5)

    tk.Button(root, text='=', width=20, height=2, font=('Arial', 14),
          command=calculate).grid(row=5, column=0, columnspan=4, padx=5, pady=10)

root.mainloop()
    
    