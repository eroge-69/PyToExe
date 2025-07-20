import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
import random

# Initialize pygame mixer
pygame.mixer.init()

# State variables
is_paused = False
is_playing = False

# --- Main functions ---
def play_music():
    global is_paused, is_playing
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file:
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            current_song.set(os.path.basename(file))
            pause_button.config(text="⏸ Pause")
            is_paused = False
            is_playing = True
        except Exception as e:
            messagebox.showerror("Error", str(e))

def pause_music():
    global is_paused, is_playing
    if not is_paused:
        pygame.mixer.music.pause()
        pause_button.config(text="▶ Resume")
        is_paused = True
        is_playing = False
    else:
        pygame.mixer.music.unpause()
        pause_button.config(text="⏸ Pause")
        is_paused = False
        is_playing = True

def stop_music():
    global is_paused, is_playing
    pygame.mixer.music.stop()
    current_song.set("🎵 No song playing")
    pause_button.config(text="⏸ Pause")
    is_paused = False
    is_playing = False

# --- Waveform animation ---
def animate_waveform():
    if is_playing:
        canvas.delete("all")
        width = 400
        num_bars = 60
        bar_width = width / num_bars
        for i in range(num_bars):
            height = random.randint(10, 100)
            x = i * bar_width
            canvas.create_line(x, 100, x, 100 - height, fill="white", width=2)
    else:
        canvas.delete("all")  # optional: remove waveform when paused/stopped
    root.after(100, animate_waveform)

# --- GUI setup ---
root = tk.Tk()
root.title("Mohammad Media Player")
root.geometry("460x380")
root.configure(bg="black")
root.iconbitmap("mu.ico") 
root.resizable(False, False) 
# Song name
current_song = tk.StringVar(value="🎵 No song playing")

# Waveform canvas
canvas = tk.Canvas(root, width=400, height=100, bg="black", highlightthickness=0)
canvas.pack(pady=15)

# Song label
song_label = tk.Label(root, textvariable=current_song, font=("Arial", 14), fg="white", bg="black")
song_label.pack(pady=10)

# Button frame
btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=10)

# Buttons
play_button = tk.Button(
    btn_frame, text="📂 Select & Play", font=("Arial", 12),
    bg="#007acc", fg="white", command=play_music, width=15
)
play_button.grid(row=0, column=0, padx=10)

pause_button = tk.Button(
    btn_frame, text="⏸ Pause", font=("Arial", 12),
    bg="#ffaa00", fg="white", command=pause_music, width=15
)
pause_button.grid(row=0, column=1, padx=10)

stop_button = tk.Button(
    root, text="⏹ Stop", font=("Arial", 12),
    bg="#e74c3c", fg="white", command=stop_music, width=34
)
stop_button.pack(pady=15)

# Footer
footer = tk.Label(root, text="By Mohammad KhanAhmadi", font=("Arial", 9), fg="#777", bg="black")
footer.pack(side="bottom", pady=5)

# Start animation loop and GUI
animate_waveform()
root.mainloop()
