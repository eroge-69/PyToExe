import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
from subprocess import call
import pygame
import os


os.system("pip install pygame")


def play_music(song_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[Error playing music] {e}")

def simulate_loading(root, progressbar, duration, file_to_open):
    for i in range(101):
        time.sleep(duration / 100)
        progressbar['value'] = i
        root.update_idletasks()
    root.destroy()

    try:
        subprocess.Popen([file_to_open], shell=True)
    except Exception as e:
        print(f"[Error opening file] {e}")

def main():
    # ✅ Song and file are in the same folder as this script
    song_path = "Iframe YouTube TV Startup Sound (Full) [aXUP9O3iAJY].mp3"
    file_to_open = "MAIN FILE.py"  # Change this to your file

    if not os.path.isfile(song_path):
        print(f"[Error] Song file not found: {song_path}")
        return

    if not os.path.isfile(file_to_open):
        print(f"[Error] File to open not found: {file_to_open}")
        return

    threading.Thread(target=play_music, args=(song_path,), daemon=True).start()

    root = tk.Tk()
    root.title("Loading...")
    root.geometry("300x120")

    tk.Label(root, text="Loading, please wait...").pack(pady=10)

    progressbar = ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate")
    progressbar.pack(pady=10)

    threading.Thread(
        target=simulate_loading, args=(root, progressbar, 5, file_to_open), daemon=True
    ).start()

    root.mainloop()

if __name__ == "__main__":
    main()
pygame.mixer.music.stop()
call(["python", "MAIN FILE.py"])