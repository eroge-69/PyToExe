
import tkinter as tk
from tkinter import messagebox
import time
import winsound
import sys
import os

# Funktion zum Abspielen eines Sounds
def play_sound():
    try:
        winsound.PlaySound("alert.wav", winsound.SND_FILENAME)
    except:
        pass

def show_question():
    answer = messagebox.askquestion("Frage", "Du bist ein Idiot?")
    if answer == 'yes':
        messagebox.showinfo("Info", "Ich wusste es!")
        root.destroy()
    else:
        play_sound()
        time.sleep(1)  # kleine Verzögerung
        show_question()

root = tk.Tk()
root.withdraw()
show_question()
