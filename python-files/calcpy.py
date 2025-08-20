import tkinter as tk

operation = ""

"""
    Update: snake_case as naming convention
    To-Do:
    - binary to decimal logic
    - implement it on the display
    How?
    Convert:            (label, grid 6,0, columnspan=4, justify="center")
    BTD     DTB     DTH (3x button, get screen on click)
"""

def calculate():
    global operation
    try:
        result = str(eval(operation))
        operation = result
        display_var.set(result)
    except:
        clear()
        display_var.set("Error")

def clear():
    global operation
    operation = ""
    display_var.set("")

def update_screen(user_input):
    global operation
    operation += str(user_input)
    display_var.set(operation)

ROOT_BG = "#000000"
DISPLAY_BG = "#000000"
DISPLAY_FG = "#B8C7C2"
BUTTON_BG = "#353C35"
BUTTON_FG = "#FFFFFF"
OPERATOR_BG = "#28798A"
SPECIAL_BG = "#FDE545"
ACTIVE_BG = "#495349"
TEXT_FONT = ("Hack", 20)
DISPLAY_FONT = ("Hack", 28, "bold")

root = tk.Tk()
root.title("CalcPy")
root.geometry("300x400")
root.resizable(False, False)
root.configure(bg=ROOT_BG)

display_var = tk.StringVar() 
# tk.StringVar is cool bc: it automatically updates the widgets,
# like with useState on ReactNative (trigger)
display = tk.Entry(
    root, 
    textvariable=display_var, 
    font=DISPLAY_FONT,
    bg=DISPLAY_BG, 
    fg=DISPLAY_FG,
    bd=0,                     
    justify="right",          
    insertwidth=0,          
    readonlybackground=DISPLAY_BG,
    state="readonly",
    width=12,
)
display.grid(row=0, column=0, columnspan=4, pady=20, padx=10, sticky="ew")

def create_button(text, row, col, bg=BUTTON_BG, command=None, colspan=1):
    if not command: 
        command = lambda: update_screen(text)
        # bc I'm not on a loop, I don't need the "freeze" thing on the lambda
        # text is always text

    return tk.Button(
        root,
        text=text,
        font=TEXT_FONT,
        bg=bg,
        fg=BUTTON_FG if bg != SPECIAL_BG else "black",
        activebackground=ACTIVE_BG,
        bd=0,
        height=1,
        width=3,
        command=command
    ).grid(
        row=row,
        column=col,
        columnspan=colspan,
        padx=5,
        pady=5,
        sticky="nsew"
    )

create_button("C", 1, 0, SPECIAL_BG, clear)
create_button("(", 1, 1, BUTTON_BG)
create_button(")", 1, 2, BUTTON_BG)
create_button("/", 1, 3, OPERATOR_BG)

create_button("7", 2, 0)
create_button("8", 2, 1)
create_button("9", 2, 2)
create_button("*", 2, 3, OPERATOR_BG)

create_button("4", 3, 0)
create_button("5", 3, 1)
create_button("6", 3, 2)
create_button("-", 3, 3, OPERATOR_BG)

create_button("1", 4, 0)
create_button("2", 4, 1)
create_button("3", 4, 2)
create_button("+", 4, 3, OPERATOR_BG)

create_button("0", 5, 0, colspan=2)
# colspan makes the thing occupy 2 spaces instead of 1
create_button(".", 5, 2)
create_button("=", 5, 3, OPERATOR_BG, calculate)

for i in range(1, 6):
    root.grid_rowconfigure(i, weight=1)
for i in range(4):
    root.grid_columnconfigure(i, weight=1)



root.mainloop()