from tkinter import *
import random

t = Tk()
t.title("Guess and Press")
t.geometry("320x380")
t.configure(bg='#f0f0f0')

def place_buttons():
    num_buttons = 8
    global buttons, correct_index
    buttons = []
    correct_index = random.randint(0, num_buttons - 1)

    for i in range(num_buttons):
        button = Button(t, text="?", command=lambda i=i: check_choice(i), bg="#add8e6", font=("Helvetica", 12))
        buttons.append(button)

    for btn in buttons:
        btn.pack(pady=5, padx=10, fill=BOTH, expand=True)

def check_choice(index):
    for btn in buttons:
        btn.destroy()

    global label
    if index == correct_index:
        label = Label(t, text="You clicked the correct button!", bg='#f0f0f0', fg='green', font=("Helvetica", 14, "bold"))
    else:
        label = Label(t, text="Wrong button! Try again...", bg='#f0f0f0', fg='red', font=("Helvetica", 14, "bold"))

    label.pack(pady=20, fill=BOTH, expand=True)
    t.after(1000, restart)

def restart():
    label.destroy()
    place_buttons()

place_buttons()
mainloop()