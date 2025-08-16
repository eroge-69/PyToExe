import tkinter as tk
import random

messages = [
    "I LOVE YOU PAAROOO....."
    "You make my world brighter ✨",
    "I love you forever 💖",
    "You are my sunshine 🌞",
    "With you, every moment is special 💕",
    "Your are everything for me "
    "Please forgive me , i am sorry "
]

def show_message():
    msg = random.choice(messages)
    label.config(text=msg)

root = tk.Tk()
root.title("For My Love")
root.geometry("400x250")

label = tk.Label(root, text="Click for a surprise 💌", font=("Arial", 16), wraplength=350)
label.pack(pady=40)

btn = tk.Button(root, text="Click Me 💖", font=("Arial", 14), command=show_message)
btn.pack()

root.mainloop()
