import os
import tkinter as tk
from tkinter import filedialog, messagebox
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

class MP3TagEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Tag Editor")
        self.root.geometry("500x350")
        
        self.current_file = None
        
        # UI elements
        self.label_file = tk.Label(root, text="No file selected")
        self.label_file.pack(pady=10)
        
        self.btn_select = tk.Button(root, text="Select MP3 File", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        tk.Label(root, text="Song Title:").pack(pady=5)
        self.entry_title = tk.Entry(root, width=50)
        self.entry_title.pack(pady=5)
        
        tk.Label(root, text="Artist:").pack(pady=5)
        self.entry_artist = tk.Entry(root, width=50)
        self.entry_artist.pack(pady=5)
        
        self.btn_save = tk.Button(root, text="Save Changes", command=self.save_tags)
        self.btn_save.pack(pady=20)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.current_file = file_path
            self.label_file.config(text=os.path.basename(file_path))
            self.load_tags()
    
    def load_tags(self):
        try:
            audio = MP3(self.current_file, ID3=ID3)
            title = audio['TIT2'].text[0] if 'TIT2' in audio else ''
            artist = audio['TPE1'].text[0] if 'TPE1' in audio else ''
            
            self.entry_title.delete(0, tk.END)
            self.entry_title.insert(0, title)
            self.entry_artist.delete(0, tk.END)
            self.entry_artist.insert(0, artist)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")
    
    def save_tags(self):
        if not self.current_file:
            messagebox.showwarning("Warning", "Please select an MP3 file first")
            return
        
        try:
            title = self.entry_title.get()
            artist = self.entry_artist.get()
            
            audio = MP3(self.current_file, ID3=ID3)
            audio['TIT2'] = TIT2(encoding=3, text=title)
            audio['TPE1'] = TPE1(encoding=3, text=artist)
            audio.save()
            
            messagebox.showinfo("Success", "Tags saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving tags: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3TagEditor(root)
    root.mainloop()
