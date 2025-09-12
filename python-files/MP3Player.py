import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
import pygame
import customtkinter as ctk
from PIL import Image

class MP3Player(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Setup window
        self.title("MP3 Player")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Current track info
        self.current_track = None
        self.playing = False
        self.paused = False
        self.track_length = 0
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_widgets()
        
        # Update progress bar periodically
        self.update_progress()
    
    def create_widgets(self):
        # Title
        title = ctk.CTkLabel(self, text="MP3 Player", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20)
        
        # Now playing frame
        now_playing_frame = ctk.CTkFrame(self)
        now_playing_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Now playing label
        now_playing_label = ctk.CTkLabel(now_playing_frame, text="Now Playing:", font=ctk.CTkFont(weight="bold"))
        now_playing_label.pack(pady=(10, 5))
        
        # Track name
        self.track_name = ctk.CTkLabel(now_playing_frame, text="No track selected", 
                                      font=ctk.CTkFont(size=14), wraplength=400)
        self.track_name.pack(pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(now_playing_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Time labels
        time_frame = ctk.CTkFrame(now_playing_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=20)
        
        self.current_time = ctk.CTkLabel(time_frame, text="00:00")
        self.current_time.pack(side="left")
        
        self.total_time = ctk.CTkLabel(time_frame, text="00:00")
        self.total_time.pack(side="right")
        
        # Control buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        # Browse button
        self.browse_btn = ctk.CTkButton(button_frame, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=0, column=0, padx=5)
        
        # Play button
        self.play_btn = ctk.CTkButton(button_frame, text="Play", command=self.play_music, state="disabled")
        self.play_btn.grid(row=0, column=1, padx=5)
        
        # Pause button
        self.pause_btn = ctk.CTkButton(button_frame, text="Pause", command=self.pause_music, state="disabled")
        self.pause_btn.grid(row=0, column=2, padx=5)
        
        # Stop button
        self.stop_btn = ctk.CTkButton(button_frame, text="Stop", command=self.stop_music, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        # Volume control
        volume_frame = ctk.CTkFrame(self, fg_color="transparent")
        volume_frame.grid(row=3, column=0, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(volume_frame, text="Volume:").pack(side="left", padx=(0, 10))
        
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=1, command=self.set_volume)
        self.volume_slider.pack(side="left")
        self.volume_slider.set(0.5)
        pygame.mixer.music.set_volume(0.5)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MP3 file",
            filetypes=[("MP3 files", "*.mp3")]
        )
        
        if file_path:
            self.load_track(file_path)
    
    def load_track(self, file_path):
        # Stop currently playing track
        self.stop_music()
        
        # Load new track
        self.current_track = file_path
        track_name = os.path.basename(file_path)
        self.track_name.configure(text=track_name)
        
        # Get track length
        sound = pygame.mixer.Sound(file_path)
        self.track_length = sound.get_length()
        
        # Update total time label
        mins, secs = divmod(self.track_length, 60)
        self.total_time.configure(text=f"{int(mins):02d}:{int(secs):02d}")
        
        # Enable buttons
        self.play_btn.configure(state="normal")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
    
    def play_music(self):
        if self.current_track:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            else:
                pygame.mixer.music.load(self.current_track)
                pygame.mixer.music.play()
            
            self.playing = True
            self.paused = False
    
    def pause_music(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.progress_bar.set(0)
        self.current_time.configure(text="00:00")
    
    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))
    
    def update_progress(self):
        if self.playing and not self.paused:
            # Get current playback position
            current_pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
            
            if current_pos > 0:
                # Update progress bar
                progress = current_pos / self.track_length
                self.progress_bar.set(progress)
                
                # Update current time label
                mins, secs = divmod(current_pos, 60)
                self.current_time.configure(text=f"{int(mins):02d}:{int(secs):02d}")
        
        # Schedule next update
        self.after(100, self.update_progress)

if __name__ == "__main__":
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = MP3Player()
    app.mainloop()