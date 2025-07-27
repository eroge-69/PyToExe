import tkinter as tk
import pygame
import os

pygame.mixer.init()

sound_path = r"C:\Users\muhib\Downloads\ouch.ogg"
icon_path = r"C:\Users\muhib\Downloads\Head.ico"

def play_sound(event=None):
    try:
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
    except Exception as e:
        print("Error playing sound:", e)

app = tk.Tk()
app.title("OOF")
app.geometry("820x500")  # Window size
app.configure(bg="white")

if os.path.exists(icon_path):
    app.iconbitmap(icon_path)
else:
    print("Icon file not found:", icon_path)

label = tk.Label(app, text="oof", fg="black", bg="white", font=("Arial", 69))
label.pack(expand=True)
label.bind("<Button-1>", play_sound)

app.mainloop()
