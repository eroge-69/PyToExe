from tkinter import *

expr = ""  # Ընդհանուր արտահայտություն

def press(key):
    global expr
    expr += str(key)
    display.set(expr)

def equal():
    global expr
    try:
        result = str(eval(expr))
        display.set(result)
        expr = ""
    except:
        display.set("Սխալ")
        expr = ""

def clear():
    global expr
    expr = ""
    display.set("")

root = Tk()
root.configure(bg="lightgreen")
root.title("Հաշվիչ Այգեստանի միջնակարգ դպրոց 7-րդ դասարան")
root.geometry("600x400")

display = StringVar()
entry = Entry(root, textvariable=display, font=("Arial", 25))
entry.grid(columnspan=4, ipadx=50, pady=10)

buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('+', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('×', 3, 3),
    ('0', 4, 0), ('C', 4, 1), ('=', 4, 2), ('÷', 4, 3),
]

for (text, row, col) in buttons:
    if text == 'C':
        action = clear
    elif text == '=':
        action = equal
    else:
        # Convert Armenian × and ÷ back to Python * and /
        key = '*' if text == '×' else '/' if text == '÷' else text
        action = lambda t=key: press(t)
    Button(root, text=text, width=5, height=2, font=("Arial", 20), command=action) \
        .grid(row=row, column=col, padx=2, pady=2)

root.mainloop()


