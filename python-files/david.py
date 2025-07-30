
import tkinter as tk
from tkinter import PhotoImage
import pyttsx3
import time
import threading

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # British Female or change index
    engine.say(text)
    engine.runAndWait()

def startup_sequence():
    speak("Hello David Vincent. Systems online and ready.")
    current_time = time.strftime('%I:%M %p')
    speak("The time is " + current_time)

def animate_eyes(canvas, eye_img):
    def blink():
        while True:
            canvas.itemconfig("eye", image=eye_img)
            time.sleep(2)
    threading.Thread(target=blink, daemon=True).start()

# GUI Window setup
root = tk.Tk()
root.title("DAVID 1.5")
root.geometry("300x300")
root.resizable(False, False)
root.configure(bg='black')

# Load images
eye = PhotoImage(file="eye.png")
mouth = PhotoImage(file="mouth.png")

# Place images on GUI
canvas = tk.Canvas(root, width=300, height=300, bg='black', highlightthickness=0)
canvas.pack()
canvas.create_image(150, 100, image=eye, tags="eye")
canvas.create_image(150, 200, image=mouth)

# Startup voice and time
threading.Thread(target=startup_sequence, daemon=True).start()
animate_eyes(canvas, eye)

# Keep window on top and small
root.attributes('-topmost', True)
root.mainloop()
