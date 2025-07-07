import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import random
import math
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import os
import tempfile
import urllib.parse

# Spotify API credentials (replace with your own)
SPOTIFY_CLIENT_ID = "f52a6389d73a402a8207cc543086263b"
SPOTIFY_CLIENT_SECRET = "6986084955ab4c5d9009c755a4203014"

class SpotifyTournamentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Song Tournament")
        self.root.geometry("1200x800")
        self.songs = []
        self.winners = []
        self.current_phase = 0
        self.current_groups = []
        self.current_group_index = 0
        self.image_references = []  # Keep references to avoid garbage collection
        self.temp_dir = tempfile.mkdtemp()  # Temporary directory for images

        # Initialize GUI elements
        self.setup_initial_screen()

    def setup_initial_screen(self):
        """Create the initial screen for entering the playlist URL."""
        self.clear_window()
        tk.Label(self.root, text="Spotify Playlist Song Tournament", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(self.root, text="Spotify Playlist URL:").pack()
        self.playlist_url_entry = tk.Entry(self.root, width=50)
        self.playlist_url_entry.pack(pady=5)
        
        tk.Button(self.root, text="Start Tournament", command=self.start_tournament).pack(pady=20)

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def get_playlist_id(self, url):
        """Extract playlist ID from Spotify URL."""
        pattern = r'(?:https?:\/\/)?open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid Spotify playlist URL")
        return match.group(1)

    def get_playlist_data(self, playlist_url):
        """Fetch song names and album cover URLs from a Spotify playlist."""
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))
            playlist_id = self.get_playlist_id(playlist_url)
            results = sp.playlist_tracks(playlist_id)
            songs = []
            for item in results['items']:
                if item['track']:
                    song_name = item['track']['name']
                    album_image = item['track']['album']['images'][1]['url'] if len(item['track']['album']['images']) > 1 else None
                    songs.append({'name': song_name, 'image_url': album_image})
            while results['next']:
                results = sp.next(results)
                songs.extend([
                    {'name': item['track']['name'], 'image_url': item['track']['album']['images'][1]['url'] if len(item['track']['album']['images']) > 1 else None}
                    for item in results['items'] if item['track']
                ])
            return songs
        except Exception as e:
            raise Exception(f"Error fetching playlist: {str(e)}")

    def download_image(self, url):
        """Download and cache an image, return PIL Image object."""
        if not url:
            return None
        # Create a safe filename from the URL
        filename = urllib.parse.quote(url, safe='')[:100] + '.jpg'
        filepath = os.path.join(self.temp_dir, filename)
        
        if not os.path.exists(filepath):
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                print(f"Error downloading image: {e}")
                return None
        
        try:
            image = Image.open(filepath)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def start_tournament(self):
        """Initialize the tournament with playlist data."""
        try:
            playlist_url = self.playlist_url_entry.get().strip()
            
            if not playlist_url:
                messagebox.showerror("Error", "Please enter a playlist URL")
                return
            
            self.songs = self.get_playlist_data(playlist_url)
            if len(self.songs) < 4:
                messagebox.showerror("Error", "Playlist must have at least 4 songs")
                return
            
            random.shuffle(self.songs)
            self.run_phase_1()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_group(self, group, phase, group_num):
        """Display a group of songs with album covers."""
        self.clear_window()
        tk.Label(self.root, text=f"Phase {phase}: Group {group_num}", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        self.image_references = []  # Clear previous image references
        
        for i, song in enumerate(group):
            song_frame = tk.Frame(frame)
            song_frame.grid(row=0, column=i, padx=20)
            
            # Display album cover
            image = self.download_image(song['image_url'])
            if image:
                img_label = tk.Label(song_frame, image=image)
                img_label.pack()
                self.image_references.append(image)  # Keep reference
            else:
                tk.Label(song_frame, text="[No Image]").pack()
            
            # Display song name
            tk.Label(song_frame, text=song['name'], wraplength=200, justify="center").pack(pady=5)
            
            # Selection button
            tk.Button(song_frame, text="Choose", command=lambda s=song: self.select_winner(s)).pack(pady=5)

    def select_winner(self, song):
        """Handle selection of a winner and proceed to next group or phase."""
        self.winners.append(song)
        self.current_group_index += 1
        
        if self.current_phase == 1:
            if self.current_group_index < len(self.current_groups):
                self.display_group(self.current_groups[self.current_group_index], self.current_phase, self.current_group_index + 1)
            else:
                self.run_phase_2()
        elif self.current_phase == 2:
            if self.current_group_index < len(self.current_groups):
                self.display_group(self.current_groups[self.current_group_index], self.current_phase, self.current_group_index + 1)
            else:
                self.run_phase_3()
        elif self.current_phase == 3:
            if self.current_group_index < len(self.current_groups):
                self.display_group(self.current_groups[self.current_group_index], self.current_phase, self.current_group_index + 1)
            else:
                self.finalize_phase_3()

    def run_phase_1(self):
        """Run Phase 1: Groups of 4."""
        self.current_phase = 1
        self.winners = []
        self.current_groups = [self.songs[i:i+4] for i in range(0, len(self.songs), 4)]
        self.current_group_index = 0
        
        # Handle single-song groups
        for i, group in enumerate(self.current_groups):
            if len(group) == 1:
                self.winners.append(group[0])
                messagebox.showinfo("Info", f"{group[0]['name']} advances automatically.")
                self.current_groups[i] = []
        
        self.current_groups = [g for g in self.current_groups if g]  # Remove empty groups
        
        if not self.current_groups:
            self.run_phase_2()
        else:
            self.display_group(self.current_groups[0], 1, 1)

    def run_phase_2(self):
        """Run Phase 2: Groups of 3."""
        if len(self.winners) < 3:
            messagebox.showerror("Error", "Not enough songs to continue to Phase 2")
            return
        
        self.current_phase = 2
        random.shuffle(self.winners)
        self.current_groups = [self.winners[i:i+3] for i in range(0, len(self.winners), 3)]
        self.winners = []
        self.current_group_index = 0
        
        # Handle single-song groups
        for i, group in enumerate(self.current_groups):
            if len(group) == 1:
                self.winners.append(group[0])
                messagebox.showinfo("Info", f"{group[0]['name']} advances automatically.")
                self.current_groups[i] = []
        
        self.current_groups = [g for g in self.current_groups if g]
        
        if not self.current_groups:
            self.run_phase_3()
        else:
            self.display_group(self.current_groups[0], 2, 1)

    def run_phase_3(self):
        """Run Phase 3: 1-on-1 matchups."""
        if len(self.winners) < 2:
            self.show_winner()
            return
        
        self.current_phase = 3
        random.shuffle(self.winners)
        self.current_groups = [self.winners[i:i+2] for i in range(0, len(self.winners), 2)]
        self.winners = []
        self.current_group_index = 0
        
        # Handle single-song groups
        for i, group in enumerate(self.current_groups):
            if len(group) == 1:
                self.winners.append(group[0])
                messagebox.showinfo("Info", f"{group[0]['name']} advances automatically.")
                self.current_groups[i] = []
        
        self.current_groups = [g for g in self.current_groups if g]
        
        if not self.current_groups:
            self.finalize_phase_3()
        else:
            self.display_group(self.current_groups[0], 3, 1)

    def finalize_phase_3(self):
        """Finalize Phase 3 and proceed to next round or declare winner."""
        if len(self.winners) > 1:
            self.run_phase_3()
        else:
            self.show_winner()

    def show_winner(self):
        """Display the final winner."""
        self.clear_window()
        if self.winners:
            tk.Label(self.root, text="Tournament Winner!", font=("Arial", 16, "bold")).pack(pady=10)
            song_frame = tk.Frame(self.root)
            song_frame.pack(pady=10)
            
            image = self.download_image(self.winners[0]['image_url'])
            if image:
                img_label = tk.Label(song_frame, image=image)
                img_label.pack()
                self.image_references.append(image)
            else:
                tk.Label(song_frame, text="[No Image]").pack()
            
            tk.Label(song_frame, text=self.winners[0]['name'], font=("Arial", 12), wraplength=300).pack(pady=5)
            tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=20)
        else:
            tk.Label(self.root, text="No winner determined.", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=20)

    def __del__(self):
        """Clean up temporary directory on exit."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

def main():
    root = tk.Tk()
    app = SpotifyTournamentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
