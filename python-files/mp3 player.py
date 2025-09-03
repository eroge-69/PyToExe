import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
from pathlib import Path

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Player")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.mp3_files = []
        self.current_playing_index = -1
        self.paused = False
        
        # Create UI elements
        self.create_widgets()
        
        # Bind events
        self.bind_events()
        
    def create_widgets(self):
        # Listbox for MP3 files
        self.listbox_frame = ttk.Frame(self.root)
        self.listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(self.listbox_frame, font=("Microsoft Sans Serif", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Button frame
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.browse_button = ttk.Button(self.button_frame, text="Browse Folder", command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = ttk.Button(self.button_frame, text="Play", command=self.play_selected_mp3, state=tk.DISABLED)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_mp3, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(self.button_frame, text="Pause", command=self.pause_resume_mp3, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        self.volume_frame = ttk.Frame(self.root)
        self.volume_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.volume_label = ttk.Label(self.volume_frame, text="Volume:")
        self.volume_label.pack(side=tk.LEFT)
        
        self.volume_scale = ttk.Scale(self.volume_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume_scale.get() / 100)
        
        # Now playing label
        self.now_playing_label = ttk.Label(self.root, text="No file selected", font=("Microsoft Sans Serif", 10, "bold"), foreground="blue")
        self.now_playing_label.pack(pady=5, padx=10, fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Ready - Select a folder with MP3 files to begin", font=("Microsoft Sans Serif", 9))
        self.status_label.pack(pady=5, padx=10, fill=tk.X)
        
    def bind_events(self):
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        self.listbox.bind('<Double-Button-1>', self.on_listbox_double_click)
        self.volume_scale.bind('<Motion>', self.on_volume_change)
        
    def format_file_size(self, size):
        if size > 1024**3:  # GB
            return f"{size / (1024**3):.1f} GB"
        elif size > 1024**2:  # MB
            return f"{size / (1024**2):.1f} MB"
        elif size > 1024:  # KB
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size} B"
    
    def get_mp3_files(self, folder_path):
        try:
            mp3_files = []
            for file in Path(folder_path).iterdir():
                if file.is_file() and file.suffix.lower() == '.mp3':
                    mp3_files.append(file)
            return mp3_files
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing folder: {str(e)}")
            return []
    
    def load_mp3_files(self, folder_path):
        self.listbox.delete(0, tk.END)
        self.status_label.config(text="Loading MP3 files...")
        self.root.update()
        
        self.mp3_files = self.get_mp3_files(folder_path)
        
        if not self.mp3_files:
            self.status_label.config(text="No MP3 files found in selected folder")
            self.play_button.config(state=tk.DISABLED)
            return
        
        for file in self.mp3_files:
            file_size = file.stat().st_size
            display_text = f"{file.name} - {self.format_file_size(file_size)}"
            self.listbox.insert(tk.END, display_text)
        
        self.status_label.config(text=f"Loaded {len(self.mp3_files)} MP3 file(s) - Click on a file to play it")
        self.play_button.config(state=tk.NORMAL)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder containing MP3 files")
        if folder_path:
            self.load_mp3_files(folder_path)
    
    def on_listbox_select(self, event):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            file_name = self.mp3_files[index].name
            self.status_label.config(text=f"Selected: {file_name} - Click Play to start")
    
    def on_listbox_double_click(self, event):
        if self.listbox.curselection():
            self.play_selected_mp3()
    
    def play_selected_mp3(self):
        if not self.listbox.curselection():
            messagebox.showinfo("Info", "Please select an MP3 file to play")
            return
        
        selected_index = self.listbox.curselection()[0]
        file_path = self.mp3_files[selected_index]
        file_name = self.mp3_files[selected_index].name
        
        try:
            # Stop current playback if any
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play new file
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play()
            
            self.current_playing_index = selected_index
            self.now_playing_label.config(text=f"Now Playing: {file_name}")
            self.status_label.config(text=f"Playing: {file_name}")
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.pause_button.config(text="Pause")
            self.paused = False
            
            # Highlight the currently playing item
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(selected_index)
            self.listbox.activate(selected_index)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error playing file: {str(e)}")
            self.status_label.config(text="Error playing file")
    
    def stop_mp3(self):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.status_label.config(text="Playback stopped")
                self.now_playing_label.config(text="Playback stopped")
                self.stop_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.DISABLED)
                self.pause_button.config(text="Pause")
                self.paused = False
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping playback: {str(e)}")
    
    def pause_resume_mp3(self):
        try:
            if self.paused:
                pygame.mixer.music.unpause()
                self.pause_button.config(text="Pause")
                self.status_label.config(text=f"Playing: {self.mp3_files[self.current_playing_index].name}")
                self.now_playing_label.config(text=f"Now Playing: {self.mp3_files[self.current_playing_index].name}")
                self.paused = False
            else:
                pygame.mixer.music.pause()
                self.pause_button.config(text="Resume")
                self.status_label.config(text=f"Paused: {self.mp3_files[self.current_playing_index].name}")
                self.now_playing_label.config(text=f"Paused: {self.mp3_files[self.current_playing_index].name}")
                self.paused = True
        except Exception as e:
            messagebox.showerror("Error", f"Error controlling playback: {str(e)}")
    
    def on_volume_change(self, event):
        volume = self.volume_scale.get() / 100
        pygame.mixer.music.set_volume(volume)
        self.status_label.config(text=f"Volume set to: {int(self.volume_scale.get())}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3Player(root)
    root.mainloop()
