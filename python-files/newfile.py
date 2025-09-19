import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pygame import mixer
import os
import random

# -----------------------------
# Music Player Configuration
# -----------------------------
mixer.init()
MUSIC_FOLDER = "stray_kids_songs"
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Preload songs (fill folder with your Stray Kids MP3s)
songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3") or f.endswith(".ogg")]
current_index = 0
shuffle_mode = False
repeat_mode = False
volume_level = 0.7
mixer.music.set_volume(volume_level)

# -----------------------------
# Helper Functions
# -----------------------------
def play_song(index=None):
    global current_index
    if songs:
        if index is not None:
            current_index = index
        mixer.music.load(os.path.join(MUSIC_FOLDER, songs[current_index]))
        mixer.music.play()
        song_label.config(text=f"Now Playing: {songs[current_index]}")
        highlight_playlist()
    else:
        song_label.config(text="No songs in folder")

def stop_song():
    mixer.music.stop()
    song_label.config(text="Stopped")

def next_song():
    global current_index
    if songs:
        if shuffle_mode:
            current_index = random.randint(0, len(songs)-1)
        else:
            current_index = (current_index + 1) % len(songs)
        play_song(current_index)

def prev_song():
    global current_index
    if songs:
        if shuffle_mode:
            current_index = random.randint(0, len(songs)-1)
        else:
            current_index = (current_index - 1) % len(songs)
        play_song(current_index)

def add_song():
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.ogg")])
    if file:
        dest = os.path.join(MUSIC_FOLDER, os.path.basename(file))
        os.rename(file, dest)
        songs.append(os.path.basename(file))
        playlist_listbox.insert(tk.END, os.path.basename(file))

def toggle_shuffle():
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    shuffle_btn.config(bg="#1DB954" if shuffle_mode else "white")

def toggle_repeat():
    global repeat_mode
    repeat_mode = not repeat_mode
    repeat_btn.config(bg="#1DB954" if repeat_mode else "white")

def set_volume(val):
    mixer.music.set_volume(float(val))

def highlight_playlist():
    playlist_listbox.selection_clear(0, tk.END)
    playlist_listbox.selection_set(current_index)
    playlist_listbox.activate(current_index)

# -----------------------------
# GUI Setup
# -----------------------------
root = tk.Tk()
root.title("Stray Kids Spotify Player")
root.geometry("800x600")
root.configure(bg="#1DB954")  # Spotify green vibe

# Top Frame
top_frame = tk.Frame(root, bg="#1DB954", height=50)
top_frame.pack(side="top", fill="x")

song_label = tk.Label(top_frame, text="No song playing", bg="#1DB954", fg="white", font=("Segoe UI", 14))
song_label.pack(pady=10)

# Playlist Frame
playlist_frame = tk.Frame(root, bg="#171a21")
playlist_frame.pack(pady=5, padx=10, fill="both", expand=True)

playlist_listbox = tk.Listbox(playlist_frame, bg="#1b2838", fg="white", width=50, height=20, font=("Segoe UI", 12))
playlist_listbox.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(playlist_frame)
scrollbar.pack(side="right", fill="y")
playlist_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=playlist_listbox.yview)

for s in songs:
    playlist_listbox.insert(tk.END, s)

def playlist_click(event):
    global current_index
    selection = playlist_listbox.curselection()
    if selection:
        current_index = selection[0]
        play_song(current_index)

playlist_listbox.bind("<Double-1>", playlist_click)

# Control Frame
controls_frame = tk.Frame(root, bg="#1DB954")
controls_frame.pack(pady=10)

prev_btn = tk.Button(controls_frame, text="<< Prev", command=prev_song, bg="white", width=8)
prev_btn.grid(row=0, column=0, padx=5)
play_btn = tk.Button(controls_frame, text="Play", command=lambda: play_song(current_index), bg="white", width=8)
play_btn.grid(row=0, column=1, padx=5)
stop_btn = tk.Button(controls_frame, text="Stop", command=stop_song, bg="white", width=8)
stop_btn.grid(row=0, column=2, padx=5)
next_btn = tk.Button(controls_frame, text="Next >>", command=next_song, bg="white", width=8)
next_btn.grid(row=0, column=3, padx=5)

# Shuffle and Repeat
shuffle_btn = tk.Button(controls_frame, text="Shuffle", command=toggle_shuffle, bg="white", width=8)
shuffle_btn.grid(row=0, column=4, padx=5)
repeat_btn = tk.Button(controls_frame, text="Repeat", command=toggle_repeat, bg="white", width=8)
repeat_btn.grid(row=0, column=5, padx=5)

# Volume
volume_frame = tk.Frame(root, bg="#1DB954")
volume_frame.pack(pady=10)
tk.Label(volume_frame, text="Volume", bg="#1DB954", fg="white").pack(side="left", padx=5)
volume_slider = tk.Scale(volume_frame, from_=0, to=1, resolution=0.01, orient="horizontal", bg="#1DB954",
                         fg="white", troughcolor="black", command=set_volume, length=200)
volume_slider.set(volume_level)
volume_slider.pack(side="left")

# Add Song Button
tk.Button(root, text="Add Song", command=add_song, bg="white").pack(pady=10)

# -----------------------------
# Mini-Player Placeholder
# -----------------------------
miniplayer_frame = tk.Frame(root, bg="#1b2838", height=50)
miniplayer_frame.pack(side="bottom", fill="x")
tk.Label(miniplayer_frame, text="Mini Player Mode: Coming Soon", fg="white", bg="#1b2838").pack(pady=10)

# -----------------------------
# Lyrics Panel Placeholder
# -----------------------------
lyrics_frame = tk.Frame(root, bg="#171a21", height=100)
lyrics_frame.pack(side="bottom", fill="x")
tk.Label(lyrics_frame, text="Lyrics Panel (Placeholder)", fg="white", bg="#171a21").pack(pady=10)

# Start main loop
root.mainloop()