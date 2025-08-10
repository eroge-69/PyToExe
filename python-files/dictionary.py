
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import pygame
import os

# Load dictionary data
with open("data/words.json", "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)

pygame.mixer.init()

def play_sound(path):
    """Play an audio file."""
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    else:
        tk.messagebox.showerror("Error", f"Audio file not found:\n{path}")

def search_word():
    word = entry.get().strip().lower()
    if word in DICTIONARY:
        info = DICTIONARY[word]

        meaning_label.config(text=f"Meaning: {info['meaning']}")
        example_label.config(text=f"Example: {info['example']}")

        # Show image if available
        if info["image"] and os.path.exists(info["image"]):
            img = Image.open(info["image"])
            img = img.resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            image_label.config(image=photo)
            image_label.image = photo
        else:
            image_label.config(image="", text="No image available")

        # Set sound buttons
        uk_btn.config(command=lambda: play_sound(info["audio_uk"]))
        us_btn.config(command=lambda: play_sound(info["audio_us"]))

    else:
        meaning_label.config(text="Word not found in dictionary.")
        example_label.config(text="")
        image_label.config(image="", text="")
        uk_btn.config(command=lambda: None)
        us_btn.config(command=lambda: None)

# GUI
root = tk.Tk()
root.title("Offline English Dictionary")
root.geometry("500x500")

entry = ttk.Entry(root, width=40)
entry.pack(pady=10)

ttk.Button(root, text="Search", command=search_word).pack(pady=5)

meaning_label = ttk.Label(root, text="", wraplength=480)
meaning_label.pack(pady=5)

example_label = ttk.Label(root, text="", wraplength=480)
example_label.pack(pady=5)

image_label = ttk.Label(root)
image_label.pack(pady=5)

uk_btn = ttk.Button(root, text="🔊 UK")
uk_btn.pack(side="left", padx=20)

us_btn = ttk.Button(root, text="🔊 US")
us_btn.pack(side="left", padx=20)

root.mainloop()
