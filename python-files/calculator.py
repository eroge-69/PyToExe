import tkinter as tk
import math

def click(event):
    text = event.widget.cget("text")
    current = entry.get()

    if text == "=":
        try:
            expression = current.replace("×", "*").replace("^", "**").replace("π", str(math.pi)).replace("√", "math.sqrt")
            result = eval(expression)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    elif text == "C":
        entry.delete(0, tk.END)
    elif text in ["sin", "cos", "tan", "log"]:
        try:
            val = float(current)
            if text == "sin":
                result = math.sin(math.radians(val))
            elif text == "cos":
                result = math.cos(math.radians(val))
            elif text == "tan":
                result = math.tan(math.radians(val))
            elif text == "log":
                result = math.log10(val)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    else:
        entry.insert(tk.END, text)

# Main Window
window = tk.Tk()
window.title("🧮 Sumon Ahmed Scientific Calculator")
window.geometry("400x600")
window.configure(bg="#202124")
window.resizable(False, False)

# Entry field
entry = tk.Entry(window, font="Helvetica 24", bd=10, relief=tk.FLAT, justify='right', bg="#303134", fg="white", insertbackground="white")
entry.pack(fill=tk.BOTH, ipadx=8, ipady=20, padx=10, pady=10)

# Button layout
buttons = [
    ['C', 'π', '√', '^'],
    ['sin', 'cos', 'tan', 'log'],
    ['7', '8', '9', '/'],
    ['4', '5', '6', '×'],
    ['1', '2', '3', '-'],
    ['0', '.', '=', '+']
]

# Button colors
def get_color(btn):
    if btn in ['=', 'sin', 'cos', 'tan', 'log', '√', '^']:
        return "#8ab4f8"  # blue
    elif btn in ['+', '-', '×', '/', '^']:
        return "#34a853"  # green
    elif btn == "C":
        return "#ea4335"  # red
    elif btn == 'π':
        return "#fbbc05"  # yellow
    else:
        return "#3c4043"  # normal

for row in buttons:
    btn_row = tk.Frame(window, bg="#202124")
    btn_row.pack(expand=True, fill='both')
    for btn in row:
        button = tk.Button(
            btn_row,
            text=btn,
            font="Helvetica 18 bold",
            fg="white",
            bg=get_color(btn),
            relief=tk.FLAT,
            activebackground="#5f6368",
            activeforeground="white"
        )
        button.pack(side='left', expand=True, fill='both', padx=1, pady=1)
        button.bind("<Button-1>", click)

window.mainloop()

input()