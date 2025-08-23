import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pygame
import os
import threading
import time

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Аудио Плеер")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Create GUI
        self.create_widgets()
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume)
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection frame
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Open file button
        self.open_button = ttk.Button(file_frame, text="Открыть файл", command=self.open_file)
        self.open_button.grid(row=0, column=0, padx=(0, 10))
        
        # File name label
        self.file_label = ttk.Label(file_frame, text="Файл не выбран", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Play button
        self.play_button = ttk.Button(control_frame, text="Play", command=self.play, state="disabled")
        self.play_button.grid(row=0, column=0, padx=(0, 10))
        
        # Pause button
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.grid(row=0, column=2)
        
        # Volume frame
        volume_frame = ttk.Frame(main_frame)
        volume_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Volume label
        ttk.Label(volume_frame, text="Громкость:").grid(row=0, column=0, padx=(0, 10))
        
        # Volume scale
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                     command=self.change_volume, value=self.volume)
        self.volume_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Volume percentage label
        self.volume_label = ttk.Label(volume_frame, text=f"{int(self.volume * 100)}%")
        self.volume_label.grid(row=0, column=2)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
        volume_frame.columnconfigure(1, weight=1)
    
    def open_file(self):
        """Open audio file dialog"""
        file_types = [
            ("Аудио файлы", "*.mp3 *.wav *.ogg *.m4a"),
            ("MP3 файлы", "*.mp3"),
            ("WAV файлы", "*.wav"),
            ("OGG файлы", "*.ogg"),
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Выберите аудио файл",
            filetypes=file_types
        )
        
        if filename:
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            
            # Enable control buttons
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            
            # Stop current playback if any
            if self.is_playing:
                self.stop()
    
    def play(self):
        """Play the selected audio file"""
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите аудио файл!")
            return
        
        try:
            if self.is_paused:
                # Resume playback
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                # Start new playback
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
            
            self.is_playing = True
            
            # Update button states
            self.play_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.stop_button.config(state="normal")
            
            # Start monitoring thread
            self.monitor_playback()
            
        except pygame.error as e:
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл:\n{str(e)}")
    
    def pause(self):
        """Pause the audio playback"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            
            # Update button states
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
    
    def stop(self):
        """Stop the audio playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        
        # Update button states
        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
    
    def change_volume(self, value):
        """Change the volume"""
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)
        self.volume_label.config(text=f"{int(self.volume * 100)}%")
    
    def monitor_playback(self):
        """Monitor playback status in a separate thread"""
        def check_status():
            while self.is_playing and not self.is_paused:
                if not pygame.mixer.music.get_busy():
                    # Playback finished
                    self.root.after(0, self.stop)
                    break
                time.sleep(0.1)
        
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = AudioPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

