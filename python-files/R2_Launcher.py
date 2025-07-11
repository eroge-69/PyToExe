import os
import sys
import requests
import hashlib
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import zipfile
import io

class R2OnlineLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("R2 Online Launcher")
        self.root.geometry("500x400")
        
        # Configuration
        self.config = {
            "server_url": "https://your-update-server.com/r2online/",
            "version_file": "version.json",
            "client_folder": "R2OnlineClient",
            "temp_folder": "temp_updates"
        }
        
        # UI Elements
        self.setup_ui()
        
        # Check for updates on start
        self.check_for_updates()
    
    def setup_ui(self):
        """Initialize the user interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title
        self.logo_label = ttk.Label(
            self.main_frame, 
            text="R2 Online", 
            font=("Arial", 24, "bold")
        )
        self.logo_label.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame, 
            text="Checking for updates...", 
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # Play button
        self.play_button = ttk.Button(
            self.main_frame, 
            text="Play", 
            command=self.launch_game,
            state=tk.DISABLED
        )
        self.play_button.pack(pady=20)
        
        # News/Info frame
        self.news_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Latest News", 
            padding="10"
        )
        self.news_frame.pack(fill=tk.BOTH, expand=True)
        
        self.news_text = tk.Text(
            self.news_frame, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.news_text.pack(fill=tk.BOTH, expand=True)
        
        # Set initial news
        self.update_news("Loading latest news...")
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def update_news(self, content):
        """Update the news section"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, content)
        self.news_text.config(state=tk.DISABLED)
    
    def check_for_updates(self):
        """Check for game updates in a separate thread"""
        self.update_status("Connecting to update server...")
        self.play_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self._check_updates_thread, daemon=True).start()
    
    def _check_updates_thread(self):
        """Thread for checking and downloading updates"""
        try:
            # Step 1: Get server version info
            self.update_status("Checking for updates...")
            version_url = f"{self.config['server_url']}{self.config['version_file']}"
            response = requests.get(version_url)
            response.raise_for_status()
            
            server_data = response.json()
            self.update_news(server_data.get("news", "No news available."))
            
            # Step 2: Check local version
            local_version = self.get_local_version()
            
            if local_version == server_data["version"]:
                self.update_status("Game is up to date!")
                self.play_button.config(state=tk.NORMAL)
                return
            
            # Step 3: Download updates
            self.update_status(f"Downloading update {server_data['version']}...")
            self.download_updates(server_data["files"])
            
            # Step 4: Apply updates
            self.update_status("Applying updates...")
            self.apply_updates()
            
            # Step 5: Update local version
            self.update_local_version(server_data["version"])
            
            self.update_status("Update complete! Ready to play.")
            self.play_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.update_status(f"Update failed: {str(e)}")
            messagebox.showerror("Update Error", f"Failed to update the game:\n{str(e)}")
            
            # If we have the client files, still allow playing
            if os.path.exists(self.config["client_folder"]):
                self.play_button.config(state=tk.NORMAL)
    
    def get_local_version(self):
        """Get the local version of the game"""
        version_file = os.path.join(self.config['client_folder'], 'version.json')
        
        if not os.path.exists(version_file):
            return "0.0.0"
            
        with open(version_file, 'r') as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    
    def update_local_version(self, version):
        """Update the local version file"""
        os.makedirs(self.config['client_folder'], exist_ok=True)
        version_file = os.path.join(self.config['client_folder'], 'version.json')
        
        with open(version_file, 'w') as f:
            json.dump({"version": version}, f)
    
    def download_updates(self, files):
        """Download all update files"""
        os.makedirs(self.config['temp_folder'], exist_ok=True)
        total_files = len(files)
        
        for i, file_info in enumerate(files):
            file_url = f"{self.config['server_url']}{file_info['path']}"
            file_path = os.path.join(self.config['temp_folder'], file_info['path'])
            
            # Create directory structure if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            self.update_status(f"Downloading {file_info['path']}...")
            self.update_progress((i / total_files) * 100)
            
            try:
                response = requests.get(file_url, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify file hash
                if not self.verify_file(file_path, file_info['hash']):
                    raise Exception(f"File {file_info['path']} failed verification")
                    
            except Exception as e:
                # Clean up temp folder on error
                shutil.rmtree(self.config['temp_folder'], ignore_errors=True)
                raise Exception(f"Failed to download {file_info['path']}: {str(e)}")
        
        self.update_progress(100)
    
    def verify_file(self, file_path, expected_hash):
        """Verify file integrity using SHA-256 hash"""
        if not os.path.exists(file_path):
            return False
            
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # 64kb chunks
                if not data:
                    break
                hasher.update(data)
        
        return hasher.hexdigest() == expected_hash
    
    def apply_updates(self):
        """Apply downloaded updates to the client folder"""
        temp_dir = self.config['temp_folder']
        client_dir = self.config['client_folder']
        
        # Create client directory if it doesn't exist
        os.makedirs(client_dir, exist_ok=True)
        
        # Copy all files from temp to client
        for root, _, files in os.walk(temp_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, temp_dir)
                dest_path = os.path.join(client_dir, rel_path)
                
                # Create destination directory if needed
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(src_path, dest_path)
        
        # Clean up temp folder
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def launch_game(self):
        """Launch the R2 Online game client"""
        self.update_status("Launching game...")
        
        # Find the game executable
        game_exe = None
        for root, _, files in os.walk(self.config['client_folder']):
            for file in files:
                if file.lower().endswith('.exe'):
                    game_exe = os.path.join(root, file)
                    break
            if game_exe:
                break
        
        if not game_exe:
            messagebox.showerror("Error", "Game executable not found!")
            self.update_status("Game executable not found!")
            return
        
        try:
            # Launch the game
            os.startfile(game_exe)
            self.update_status("Game launched!")
            
            # Close the launcher after a short delay
            self.root.after(2000, self.root.destroy)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game:\n{str(e)}")
            self.update_status(f"Launch failed: {str(e)}")

def main():
    root = tk.Tk()
    launcher = R2OnlineLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()