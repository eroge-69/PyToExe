import tkinter as tk
from tkinter import font

def button_click(number):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, str(current) + str(number))

def button_clear():
    entry.delete(0, tk.END)

def button_equal():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")

root = tk.Tk()
root.title("ماشین حساب آیفون")
root.geometry("300x500")
root.resizable(False, False)
root.configure(bg="#000000")

entry = tk.Entry(root, width=15, borderwidth=0, font=("Helvetica", 32), justify="right", bg="#000000", fg="#FFFFFF")
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=20, ipady=10)

buttons = [
    ('C', 1, 0), ('±', 1, 1), ('%', 1, 2), ('÷', 1, 3),
    ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('×', 2, 3),
    ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
    ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
    ('0', 5, 0), ('.', 5, 2), ('=', 5, 3)
]

for (text, row, col) in buttons:
    if text == '0':
        btn = tk.Button(root, text=text, padx=36, pady=20, font=("Helvetica", 20), 
                        bg="#333333" if text not in ['C', '±', '%', '÷', '×', '-', '+', '='] else "#FF9500", 
                        fg="#FFFFFF", borderwidth=0)
        btn.grid(row=row, column=col, columnspan=2, padx=1, pady=1, sticky="nsew")
    else:
        btn = tk.Button(root, text=text, padx=20, pady=20, font=("Helvetica", 20), 
                        bg="#333333" if text not in ['C', '±', '%', '÷', '×', '-', '+', '='] else "#FF9500", 
                        fg="#FFFFFF", borderwidth=0)
        btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
    
    if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
        btn.configure(command=lambda t=text: button_click(t))
    elif text == 'C':
        btn.configure(command=button_clear)
    elif text == '=':
        btn.configure(command=button_equal)

root.mainloop()