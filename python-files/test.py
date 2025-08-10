import tkinter as tk

def click_button(symbol):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + symbol)

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Błąd")

root = tk.Tk()
root.title("Kalkulator")
root.geometry("300x400")
root.resizable(False, False)

entry = tk.Entry(root, width=16, font=('Arial', 20), borderwidth=2, relief="solid", justify="right")
entry.pack(pady=10)

buttons = [
    ('7', '8', '9', '/'),
    ('4', '5', '6', '*'),
    ('1', '2', '3', '-'),
    ('0', '.', '=', '+')
]

for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill='both')
    for btn_text in row:
        if btn_text == '=':
            btn = tk.Button(frame, text=btn_text, font=('Arial', 18), command=calculate)
        else:
            btn = tk.Button(frame, text=btn_text, font=('Arial', 18), command=lambda b=btn_text: click_button(b))
        btn.pack(side='left', expand=True, fill='both')

clear_btn = tk.Button(root, text="C", font=('Arial', 18), command=clear)
clear_btn.pack(expand=True, fill='both')

root.mainloop()
