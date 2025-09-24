#Python Calculator of Real Love

import tkinter

button_values = [
    ["AC", "+/-", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "√", "="]
]

right_symbols = ["+", "×", "÷", "-", "="]
top_symbols = ["AC", "+/-", "%"]
extra_symbol = ["√"]

row_count = len(button_values) #5
column_count = len(button_values[0]) #4

color_red = "#CDCDCD"
color_black = "#1C1C1C"
color_yellow = "#e6cc00"
color_green = "#244747"
color_white = "white"

#Window setup
window = tkinter.Tk() #create the window
window.title("Magic Calculator")
window.resizable(False, False)

frame = tkinter.Frame(window)
label = tkinter.Label(frame, text="Work, bitch!", font=("Times New Roman", 40), background=color_black,
                      foreground=color_white, anchor="e", width=column_count)

label.grid(row=0, column=0, columnspan=column_count, sticky="we")

for row in range(row_count):
    for column in range(column_count):
        value = button_values[row][column]
        button = tkinter.Button(frame, text=value, font=("Times New Roman", 30),
                                width=column_count-1, height=1,
                                command=lambda value=value: button_clicked(value))

        if value in top_symbols:
            button.config(foreground=color_black, background=color_yellow)
        elif value in right_symbols:
            button.config(foreground=color_black, background=color_green)
        else:
            button.config(foreground=color_black, background=color_red)
        button.grid(row=row+1, column=column)

frame.pack()

#A+B,A-B, A*b, A/B
A = "0"
operator = None
B = None

def clear_all():
    global A, B, operator
    A = "0"
    operator = None
    B = None

def remove_zero(num):
    if num % 1 == 0:
        num = int(num)
    return str(num)

def button_clicked(value):
    global right_symbols, top_symbols, label, A, B, operator, extra_symbol

    if value in right_symbols:
        if value == "=":
            if A is not None and operator is not None:
                B = label["text"]
                numA = float(A)
                numB = float (B)

                if operator == "+":
                    label["text"] = remove_zero(numA + numB) [:10]
                elif operator == "-":
                    label["text"] = remove_zero(numA - numB) [:10]
                elif operator == "×":
                    label["text"] = remove_zero(numA * numB) [:10]
                elif operator == "÷":
                    label["text"] = remove_zero(numA / numB) [:10]

                clear_all()

        elif value in "+×÷-":
            if operator is None:
                A = label["text"]
                label["text"] = "yes, and?"
                B = "0"

            elif value in "+×÷-":
                label["text"] =  "Press AC, bb"

        operator = value

    elif value in top_symbols:
        if value == "AC":
            clear_all()
            label["text"] = "U ate all up"

        elif value == "+/-":
            result = float(label["text"]) * -1
            label["text"] = remove_zero(result) [:10]

        elif value == "%":
            result = float(label["text"]) / 100
            label["text"] = remove_zero(result) [:10]

    elif value in extra_symbol:
        result = float(label["text"]) **  0.5
        label["text"] = remove_zero(result) [:10]

    else:
        if value == ".":
            if value not in label["text"]:
                label["text"] += value

        elif value in "0123456789":
            if label["text"] == "Work, bitch!":
                label["text"] = value
            elif label["text"] == "U ate all up":
                label["text"] = value
            elif label["text"] == "yes, and?":
                label["text"] = value
            elif label["text"] == "Press AC, bb":
                label["text"] = value
            else:
                label["text"] += value

#center the window
window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (window_height/2))

#format "(x)*(h)+(x)+(y)"
window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()