import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import pygame
import keyboard
import os

# === CONFIG ===
gif_url = "https://c.tenor.com/Ov2a4Trw4kkAAAAd/tenor.gif"
sound_path = r"F:\Downloads\RAVENCHECKSOUND.mp3"  # Ensure this path and extension is correct

# === INIT SOUND ===
pygame.mixer.init()

def play_sound():
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

# === GIF PLAYER ===
class GifPlayer(threading.Thread):
    def __init__(self, root, gif_url):
        threading.Thread.__init__(self)
        self.root = root
        self.label = tk.Label(root, bg="black")  # Placeholder for the gif
        self.frames = []
        self.load_gif(gif_url)
        self.playing = False

    def load_gif(self, path_or_url):
        import requests
        from io import BytesIO

        if path_or_url.startswith("http"):
            response = requests.get(path_or_url)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(path_or_url)

        for frame in ImageSequence.Iterator(image):
            frame = frame.resize((200, 200))  # Resize if needed
            self.frames.append(ImageTk.PhotoImage(frame))

    def show(self):
        self.label.pack()
        self.playing = True
        self.start()

    def run(self):
        idx = 0
        while self.playing:
            frame = self.frames[idx]
            self.label.configure(image=frame)
            idx = (idx + 1) % len(self.frames)
            time.sleep(0.1)

# === MAIN APP ===
def main():
    root = tk.Tk()
    root.title("RAVENCHECK")
    root.geometry("+0+0")  # Top-left of screen
    root.configure(bg='black')
    root.overrideredirect(True)  # Borderless window

    # Do not display anything initially
    gif_player = GifPlayer(root, gif_url)

    # Key listener for 'H'
    def on_h_press():
        threading.Thread(target=handle_h_sequence).start()

    def handle_h_sequence():
        play_sound()
        time.sleep(4)
        gif_player.show()
        play_sound()
        # GIF keeps playing forever

    # Start keyboard listener
    def key_listener():
        while True:
            if keyboard.is_pressed('h'):
                on_h_press()
                while keyboard.is_pressed('h'):
                    time.sleep(0.1)  # Wait until key is released
            time.sleep(0.1)

    threading.Thread(target=key_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
