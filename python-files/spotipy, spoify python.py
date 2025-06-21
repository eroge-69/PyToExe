import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import json

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced MP3 Player")
        self.root.geometry("500x320")

        pygame.mixer.init()
        self.playlist = []
        self.current_index = -1
        self.paused = False
        self.repeat = False

        self.label = tk.Label(root, text="No song playing", wraplength=480)
        self.label.pack(pady=10)

        # Controls
        controls = tk.Frame(root)
        controls.pack()
        tk.Button(controls, text="⏮️", command=self.skip_back).grid(row=0, column=0)
        tk.Button(controls, text="▶️", command=self.play).grid(row=0, column=1)
        tk.Button(controls, text="⏸️", command=self.pause_unpause).grid(row=0, column=2)
        tk.Button(controls, text="⏭️", command=self.skip_forward).grid(row=0, column=3)
        self.repeat_button = tk.Button(controls, text="🔁 Repeat: Off", command=self.toggle_repeat)
        self.repeat_button.grid(row=0, column=4)
        tk.Button(root, text="🎵 Select MP3s", command=self.select_files).pack(pady=5)

        # Volume
        volume_frame = tk.Frame(root)
        volume_frame.pack()
        tk.Label(volume_frame, text="🔊 Volume").pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(0.5)
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(fill=tk.X, padx=10)

        # Progress bar
        self.progress = ttk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Playlist save/load
        playlist_buttons = tk.Frame(root)
        playlist_buttons.pack()
        tk.Button(playlist_buttons, text="💾 Save Playlist", command=self.save_playlist).grid(row=0, column=0, padx=5)
        tk.Button(playlist_buttons, text="📂 Load Playlist", command=self.load_playlist).grid(row=0, column=1, padx=5)

        self.update_progress()

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        if files:
            self.playlist = list(files)
            self.current_index = 0
            self.load_song()

    def load_song(self):
        if 0 <= self.current_index < len(self.playlist):
            pygame.mixer.music.load(self.playlist[self.current_index])
            self.label.config(text=f"Now Playing: {os.path.basename(self.playlist[self.current_index])}")
            pygame.mixer.music.play()
            self.paused = False

    def play(self):
        if not self.playlist:
            return
        pygame.mixer.music.play()
        self.paused = False

    def pause_unpause(self):
        if pygame.mixer.music.get_busy():
            if self.paused:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            self.paused = not self.paused

    def skip_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_song()

    def skip_forward(self):
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.load_song()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def update_progress(self):
        if pygame.mixer.music.get_busy():
            try:
                pos = pygame.mixer.music.get_pos() / 1000  # ms to seconds
                self.progress.set(pos)
            except:
                pass
        else:
            if not self.paused and self.playlist:
                if self.repeat:
                    self.load_song()
                else:
                    self.skip_forward()
        self.root.after(1000, self.update_progress)

    def save_playlist(self):
        if not self.playlist:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Playlist", "*.json")])
        if path:
            with open(path, "w") as f:
                json.dump(self.playlist, f)

    def load_playlist(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Playlist", "*.json")])
        if path:
            with open(path, "r") as f:
                self.playlist = json.load(f)
            self.current_index = 0
            self.load_song()

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.repeat_button.config(text=f"🔁 Repeat: {'On' if self.repeat else 'Off'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3Player(root)
    root.mainloop()
