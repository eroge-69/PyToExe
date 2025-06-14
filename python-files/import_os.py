import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

class MP3MetadataExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Metadata Extractor")

        # Default music folder (can be changed)
        self.music_folder = os.path.expanduser("~/Music")

        # UI Elements
        tk.Label(root, text="Select Music Folder:").pack(pady=5)
        self.folder_entry = tk.Entry(root, width=50)
        self.folder_entry.pack(pady=5)
        self.folder_entry.insert(0, self.music_folder)
        tk.Button(root, text="Browse", command=self.browse_folder).pack(pady=5)

        tk.Button(root, text="Extract Metadata", command=self.extract_metadata).pack(pady=10)

        self.output_text = scrolledtext.ScrolledText(root, width=60, height=15)
        self.output_text.pack(pady=5)

        tk.Button(root, text="Open Output File", command=self.open_output_file).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.music_folder = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.music_folder)

    def extract_metadata(self):
        output_file = os.path.join(self.music_folder, "song_list.txt")
        song_data = []
        
        if not os.path.exists(self.music_folder):
            messagebox.showerror("Error", "Selected folder does not exist!")
            return
        
        for file in os.listdir(self.music_folder):
            if file.endswith(".mp3"):
                file_path = os.path.join(self.music_folder, file)
                try:
                    audio = MP3(file_path, ID3=EasyID3)
                    title = audio.get("title", ["Unknown Title"])[0]
                    artist = audio.get("artist", ["Unknown Artist"])[0]
                    song_data.append(f"{title} - {artist}")
                except Exception as e:
                    song_data.append(f"Error processing {file}: {e}")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(song_data))
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(song_data))
        messagebox.showinfo("Success", f"Song list saved to {output_file}")

    def open_output_file(self):
        output_file = os.path.join(self.music_folder, "song_list.txt")
        if os.path.exists(output_file):
            os.startfile(output_file)
        else:
            messagebox.showerror("Error", "Output file does not exist!")

# Run the application
root = tk.Tk()
app = MP3MetadataExtractor(root)
root.mainloop()