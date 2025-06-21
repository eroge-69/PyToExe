import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
import threading
import time
from pathlib import Path
import json

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("400x600")
        self.root.configure(bg='#2c3e50')
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Player variables
        self.current_song = None
        self.song_list = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Load settings
        self.load_settings()
        
        # Create GUI
        self.create_widgets()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()
        
    def load_settings(self):
        """Load player settings from file"""
        try:
            if os.path.exists('player_settings.json'):
                with open('player_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.volume = settings.get('volume', 0.7)
        except:
            self.volume = 0.7
    
    def save_settings(self):
        """Save player settings to file"""
        try:
            settings = {
                'volume': self.volume
            }
            with open('player_settings.json', 'w') as f:
                json.dump(settings, f)
        except:
            pass
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎵 Simple Music Player", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2c3e50', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Current song display
        self.song_label = tk.Label(main_frame, text="No song selected", 
                                  font=('Arial', 10), 
                                  bg='#34495e', fg='white',
                                  wraplength=350, height=3)
        self.song_label.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=350)
        self.progress_bar.pack(pady=(0, 5))
        
        # Time labels
        time_frame = tk.Frame(main_frame, bg='#2c3e50')
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_time_label = tk.Label(time_frame, text="0:00", 
                                          bg='#2c3e50', fg='white')
        self.current_time_label.pack(side=tk.LEFT)
        
        self.total_time_label = tk.Label(time_frame, text="0:00", 
                                        bg='#2c3e50', fg='white')
        self.total_time_label.pack(side=tk.RIGHT)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(pady=10)
        
        # Previous button
        self.prev_button = tk.Button(control_frame, text="⏮", 
                                    font=('Arial', 14), width=3,
                                    bg='#3498db', fg='white',
                                    command=self.previous_song)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        # Play/Pause button
        self.play_button = tk.Button(control_frame, text="▶", 
                                    font=('Arial', 14), width=3,
                                    bg='#27ae60', fg='white',
                                    command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Next button
        self.next_button = tk.Button(control_frame, text="⏭", 
                                    font=('Arial', 14), width=3,
                                    bg='#3498db', fg='white',
                                    command=self.next_song)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = tk.Button(control_frame, text="⏹", 
                                    font=('Arial', 14), width=3,
                                    bg='#e74c3c', fg='white',
                                    command=self.stop_song)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Volume frame
        volume_frame = tk.Frame(main_frame, bg='#2c3e50')
        volume_frame.pack(pady=10)
        
        volume_label = tk.Label(volume_frame, text="🔊 Volume:", 
                               bg='#2c3e50', fg='white')
        volume_label.pack(side=tk.LEFT)
        
        self.volume_var = tk.DoubleVar(value=self.volume * 100)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, 
                                    orient=tk.HORIZONTAL, variable=self.volume_var,
                                    bg='#2c3e50', fg='white', highlightbackground='#2c3e50',
                                    command=self.change_volume, length=200)
        self.volume_scale.pack(side=tk.LEFT, padx=10)
        
        # Playlist frame
        playlist_frame = tk.Frame(main_frame, bg='#2c3e50')
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        playlist_label = tk.Label(playlist_frame, text="Playlist", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2c3e50', fg='white')
        playlist_label.pack(anchor=tk.W)
        
        # Playlist listbox
        self.playlist_box = tk.Listbox(playlist_frame, bg='#34495e', fg='white',
                                      selectbackground='#3498db', height=8)
        self.playlist_box.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar for playlist
        playlist_scrollbar = tk.Scrollbar(playlist_frame, orient=tk.VERTICAL)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_box.config(yscrollcommand=playlist_scrollbar.set)
        playlist_scrollbar.config(command=self.playlist_box.yview)
        
        # Bind double-click to playlist
        self.playlist_box.bind('<Double-Button-1>', self.play_selected)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Add songs button
        add_button = tk.Button(button_frame, text="Add Songs", 
                              bg='#9b59b6', fg='white',
                              command=self.add_songs)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Clear playlist button
        clear_button = tk.Button(button_frame, text="Clear Playlist", 
                                bg='#e67e22', fg='white',
                                command=self.clear_playlist)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Remove selected button
        remove_button = tk.Button(button_frame, text="Remove Selected", 
                                 bg='#e74c3c', fg='white',
                                 command=self.remove_selected)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def add_songs(self):
        """Add songs to playlist"""
        filetypes = [
            ('Audio Files', '*.mp3 *.wav *.ogg *.flac *.m4a'),
            ('MP3 Files', '*.mp3'),
            ('WAV Files', '*.wav'),
            ('All Files', '*.*')
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Music Files",
            filetypes=filetypes
        )
        
        for file in files:
            if file not in self.song_list:
                self.song_list.append(file)
                filename = os.path.basename(file)
                self.playlist_box.insert(tk.END, filename)
    
    def clear_playlist(self):
        """Clear the entire playlist"""
        if messagebox.askyesno("Clear Playlist", "Are you sure you want to clear the playlist?"):
            self.stop_song()
            self.song_list.clear()
            self.playlist_box.delete(0, tk.END)
            self.current_song = None
            self.current_index = 0
            self.song_label.config(text="No song selected")
    
    def remove_selected(self):
        """Remove selected song from playlist"""
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            self.playlist_box.delete(index)
            self.song_list.pop(index)
            
            # Adjust current index if necessary
            if self.current_index >= len(self.song_list):
                self.current_index = 0
                self.current_song = None
                self.song_label.config(text="No song selected")
    
    def play_selected(self, event=None):
        """Play the selected song from playlist"""
        selection = self.playlist_box.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_song()
    
    def play_song(self):
        """Play the current song"""
        if not self.song_list:
            return
            
        try:
            if self.current_index >= len(self.song_list):
                self.current_index = 0
            
            self.current_song = self.song_list[self.current_index]
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            
            # Update display
            filename = os.path.basename(self.current_song)
            self.song_label.config(text=f"Now Playing:\n{filename}")
            
            # Update playlist selection
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)
            self.playlist_box.see(self.current_index)
            
            self.is_playing = True
            self.is_paused = False
            self.play_button.config(text="⏸")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not play file: {str(e)}")
    
    def play_pause(self):
        """Play or pause the current song"""
        if not self.song_list:
            return
            
        if not self.is_playing:
            if self.current_song is None:
                self.play_song()
            else:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.is_paused = False
                self.play_button.config(text="⏸")
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.play_button.config(text="▶")
    
    def stop_song(self):
        """Stop the current song"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.play_button.config(text="▶")
        self.progress_var.set(0)
        self.current_time_label.config(text="0:00")
    
    def next_song(self):
        """Play the next song"""
        if self.song_list:
            self.current_index = (self.current_index + 1) % len(self.song_list)
            self.play_song()
    
    def previous_song(self):
        """Play the previous song"""
        if self.song_list:
            self.current_index = (self.current_index - 1) % len(self.song_list)
            self.play_song()
    
    def change_volume(self, value):
        """Change the volume"""
        self.volume = float(value) / 100
        pygame.mixer.music.set_volume(self.volume)
    
    def update_progress(self):
        """Update the progress bar and time labels"""
        while True:
            if self.is_playing and not self.is_paused:
                try:
                    # Get current position and length
                    current_pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
                    
                    # Update progress bar (approximate)
                    if hasattr(pygame.mixer.music, 'get_length'):
                        total_length = pygame.mixer.music.get_length()
                        if total_length > 0:
                            progress = (current_pos / total_length) * 100
                            self.progress_var.set(progress)
                    
                    # Update time labels
                    current_min = int(current_pos // 60)
                    current_sec = int(current_pos % 60)
                    self.current_time_label.config(text=f"{current_min}:{current_sec:02d}")
                    
                    # Check if song ended
                    if not pygame.mixer.music.get_busy() and self.is_playing:
                        self.next_song()
                        
                except:
                    pass
            
            time.sleep(0.1)
    
    def on_closing(self):
        """Handle window closing"""
        self.save_settings()
        pygame.mixer.quit()
        self.root.destroy()

def main():
    """Main function to run the music player"""
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 