import threading
import os
from tkinter import Tk, Button, Label
from playsound import playsound
from tkvideo import tkvideo







# ----- CONFIG -----
SOUND_FILE = "You are an idiot HAHAHAHAHA!.mp3"   # mets ton son dans le même dossier
VIDEO_FILE = "You are an idiot HAHAHAHAHA!.mp4"   # mets ta vidéo dans le même dossier
# ------------------

Window = Tk()
Window.title("You are an idiot")
Window.geometry("600x400")

# Label qui va contenir la vidéo
video_label = Label(Window)
video_label.pack()

# Fonction pour jouer le son en boucle dans un thread
def play_sound_loop():
    while True:
        playsound(SOUND_FILE)

# Fonction appelée par le bouton "Idiot"
def start_idiot():
    # lancer le son en boucle dans un thread
    threading.Thread(target=play_sound_loop, daemon=True).start()

    # lancer la vidéo dans le label
    player = tkvideo(VIDEO_FILE, video_label, loop=1, size=(600,400))
    player.play()

# Bouton idiot
idiot_button = Button(Window, text="YOU ARE AN IDIOT", command=start_idiot)
idiot_button.pack()

Window.mainloop()
