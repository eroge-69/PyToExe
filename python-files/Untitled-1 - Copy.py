import pygame
import os
import tkinter as tk
from tkinter import filedialog

# Initialize pygame mixer for audio
pygame.mixer.init()

# Setup tkinter window
root = tk.Tk()
root.title("Music Player")
root.geometry("400x300")

# Label to show current song
playing = tk.Label(root, text="Current song:")
playing.pack(pady=10)

# Global variable to store the folder path
folder_selected = ""

# Music files list
ogg_files = []

# Boolean to track if repeat is enabled
repeat_enabled = False

# Function to open a file dialog to select a music folder
def select_folder():
    global folder_selected  # Declare folder_selected as global
    folder_selected = filedialog.askdirectory()  # Open folder dialog
    if folder_selected:
        load_music_files(folder_selected)  # Load music files from the selected folder

# Function to load music files from the selected folder
def load_music_files(folder):
    global ogg_files
    ogg_files = [f for f in os.listdir(folder) if f.endswith('.mp3') or f.endswith('.flac')]

    # Clear previous buttons and recreate based on the new folder
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    # Create buttons for each music file
    for song in ogg_files:
        label = tk.Button(root, text=song, command=lambda x=song: play(x))
        label.pack(pady=5)

# Function to handle music play/stop
def play(x):
    if folder_selected:  # Ensure the folder is selected
        file_path = os.path.join(folder_selected, x)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()  # Stop if already playing
            playing.config(text="Current song:")
        else:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loops=0, start=0.0)
            playing.config(text=f"Currently playing: {x}")

# Function to toggle repeat
def toggle_repeat():
    global repeat_enabled
    repeat_enabled = repeat_var.get()  # Get the checkbox state

# Function to check if the music has finished and needs to repeat
def check_repeat():
    if repeat_enabled and not pygame.mixer.music.get_busy():  # If repeat is enabled and music is finished
        pygame.mixer.music.play(loops=0, start=0.0)  # Replay the current song
    root.after(100, check_repeat)  # Check every 100ms if music is finished

# Button to select folder
select_button = tk.Button(root, text="Select Music Folder", command=select_folder)
select_button.pack(pady=10)

# Checkbox to enable/disable repeat
repeat_var = tk.BooleanVar()
repeat_checkbox = tk.Checkbutton(root, text="Repeat Song", variable=repeat_var, command=toggle_repeat)
repeat_checkbox.pack(pady=10)

# Start the tkinter main loop
check_repeat()  # Start checking if the song needs to repeat
root.mainloop()
