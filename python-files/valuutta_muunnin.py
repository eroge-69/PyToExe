from tkinter import *
from tkinter import ttk
import tkinter as tk

#window sets the window size and title also runs the window as program screen(at the bottom of code, mainloop)
window = Tk()
pic_icon = tk.PhotoImage(file="money.png")
window.iconphoto(False, pic_icon) # setting money.png as winow icon (top-left)
window.title("€uro value Modifier")
window.geometry("480x200")

# ---- FUNCTIONS
    # event=None needs to be if you desire to get Enter keyboard input used
def get_value(event=None): # this checks if the input, inside value_input_box is int or str value
    try:
        number = int(value_input_box.get())
        result_box.config(text=f"you gave € value {float(round(number, 2))}")
        clear_entry()     
    except ValueError:
        clear_entry()
        result_box.config(text="you did not type int value!") 

def pound_modifier():
    try:
        result_get = float(value_input_box.get()) 
        value_change = result_get * 0.864
        value_changed_box.config(text=f"€URO to British Pound: Value is {float(round(value_change, 2))}")
        result_box.config(text=f"you gave € value {result_get}")
        clear_entry()
              
    except ValueError:
        clear_entry()
        result_box.config(text="you did not type int value!")
           

def dollar_modifier():
    try:
        result_get = float(value_input_box.get()) 
        value_change = result_get * 1.1682
        value_changed_box.config(text=f"€URO to American Dollar: Value is {float(round(value_change, 2))}")
        result_box.config(text=f"you gave € value {result_get}")
        clear_entry()        
    except ValueError:
        clear_entry()
        result_box.config(text="you did not type int value!") 

def rouble_modifier():
    try:
        result_get = float(value_input_box.get()) 
        value_change = result_get * 0.011
        value_changed_box.config(text=f"€URO to Russian Rouble: Value is {float(round(value_change, 2))}")
        result_box.config(text=f"you gave € value {result_get}")        
        clear_entry()
    except ValueError:
        clear_entry()
        result_box.config(text="you did not type int value!") 

def clear_entry():
    value_input_box.delete(0, 'end')

def exit_program():
    window.destroy()       

# ---- WIDGETS
value_input_box = tk.Entry(window, text="") # ENTRY BOX for Value
value_input_box.place(x=150, y=50)
value_input_box.bind("<Return>", get_value) # setting valuebox input as Enter- keyboard activation

result_box = tk.Label(window, text="")
result_box.place(x=300, y=50)

value_changed_box = tk.Label(window, text="")
value_changed_box.place(x=200, y=10)

# ---- BUTTONS
tk.Button(window, text="£: Pound", command=pound_modifier).place(x=150, y=100)
tk.Button(window, text="$: Dollar", command=dollar_modifier).place(x=250, y=100)
tk.Button(window, text="₽: Rouble", command=rouble_modifier).place(x=350, y=100)
tk.Button(window, text="Exit", command=exit_program).place(x=50, y=100)

window.mainloop() # window mainloop, this runs the window screeen nonstop until closed