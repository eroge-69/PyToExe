import tkinter as tk

# Expression store karne ke liye
expression = ""

# Operator list
operators = ["+", "-", "*", "/"]

# Button click function
def btn_click(item):
    global expression
    # Agar last character operator hai aur naya bhi operator hai -> ignore
    if expression and expression[-1] in operators and item in operators:
        return
    expression += str(item)
    input_text.set(expression)

# Equal function
def btn_equal():
    global expression
    try:
        result = str(eval(expression))
        input_text.set(result)
        expression = result
    except:
        input_text.set("Error")
        expression = ""

# Clear function
def btn_clear():
    global expression
    expression = ""
    input_text.set("")

# Tkinter window setup
root = tk.Tk()
root.title("PC Calculator")
root.geometry("300x400")
root.resizable(False, False)

input_text = tk.StringVar()

# Input field
input_frame = tk.Frame(root)
input_frame.pack()

input_field = tk.Entry(
    input_frame, textvariable=input_text,
    font=('Arial', 18), width=15,
    borderwidth=5, relief='ridge',
    justify='right'
)
input_field.grid(row=0, column=0)
input_field.pack(ipady=10)

# Buttons
btns_frame = tk.Frame(root)
btns_frame.pack()

buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
]

for (text, row, col) in buttons:
    if text == "=":
        btn = tk.Button(btns_frame, text=text, width=5, height=2, command=btn_equal)
    else:
        btn = tk.Button(btns_frame, text=text, width=5, height=2, command=lambda t=text: btn_click(t))
    btn.grid(row=row, column=col, padx=5, pady=5)

# Clear button
clear_btn = tk.Button(btns_frame, text="C", width=5, height=2, command=btn_clear, bg="red", fg="white")
clear_btn.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=5)

root.mainloop()
