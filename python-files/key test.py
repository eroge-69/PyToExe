from pynput.keyboard import Key, Controller
from time import sleep
from random import randint
import tkinter as tk


def scan_text():
    text = macro_input.get("1.0", "end-1c")
    symbols = []
    number_lanes = 1
    for s in text:
        symbols.append(s)
    symbols.append("end")
    for s in text:
        if s == "\n":
            number_lanes += 1
    j = 0
    sleep(3)
    for i in range(number_lanes):
        text_to_do = ''
        number_times = ''
        while symbols[j] != '!':
            text_to_do += symbols[j]
            j += 1
        j += 1
        while symbols[j] != '\n' and symbols[j] != 'end':
            number_times += symbols[j]
            j += 1
        j += 1
        number_times = int(number_times)
        word(text_to_do, number_times)





root = tk.Tk()
root.geometry("400x300")
root.title("Ultimate macro lord")
greetings = tk.Label(root, text='Welcome to ultimate macro lord!')
instruction = tk.Label(root, text='Enter text to write down there. Use !2 !3 ect to write the lane more times')
macro_input = tk.Text(root, height=9, width=35)
start_b = tk.Button(root, text="Launch macro", command=scan_text)
macro_warning = tk.Label(root, text="Note: don't use '!' outside of setting the number of repeats\ndon't leave any lanes without '!' and a number at the end\nif you need 1 repeat just put !1\ndon't put anything besides numbers and enters after the '!'")

keyboard = Controller()



def hit(_k):
    if _k == ' ':
        keyboard.press(Key.space)
        keyboard.release(Key.space)
    else:
        keyboard.press(_k)
        keyboard.release(_k)


def word(wrd, times=1):
    for i in range(times):
        for i in range(len(wrd)):
            hit(wrd[i])


greetings.pack()
instruction.pack()
macro_input.pack()
start_b.pack()
macro_warning.pack()

root.mainloop()