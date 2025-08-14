import tkinter as tk
from tkinter import filedialog
import subprocess
import os

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)

def browse_folder():
    folderpath = filedialog.askdirectory()
    if folderpath:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folderpath)

def start_ffmpeg():
    input_path = input_entry.get()
    output_name = output_entry.get().strip()
    save_folder = folder_entry.get().strip()

    if not os.path.isfile(input_path):
        print("Ugyldig videofil")
        return
    if not output_name:
        print("Skriv inn et output-navn")
        return
    if not os.path.isdir(save_folder):
        print("Ugyldig mappe for lagring")
        return

    ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe")
    if not os.path.isfile(ffmpeg_path):
        print("Fant ikke ffmpeg.exe i samme mappe")
        return

    output_path = os.path.join(save_folder, output_name)

    command = f'"{ffmpeg_path}" -i "{input_path}" -r 30 -c:v libx264 -preset veryfast -crf 18 -c:a copy "{output_path}" & pause'
    subprocess.Popen(["cmd", "/k", command])

# GUI-oppsett
root = tk.Tk()
root.title("60FPS TIL 30FPS")
root.configure(bg="#7092BE")

label_style = {"bg": "#7092BE", "fg": "black", "font": ("Segoe UI", 10)}
entry_style = {"bg": "white", "fg": "black", "font": ("Segoe UI", 10)}

# Select video file
tk.Label(root, text="Select video file:", **label_style).pack(pady=(10, 0))
input_entry = tk.Entry(root, width=60, **entry_style)
input_entry.pack(padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_file).pack(pady=5)

# Output name
tk.Label(root, text="OUTPUT NAME (f.eks. output.mp4):", **label_style).pack(pady=(10, 0))
output_entry = tk.Entry(root, width=60, **entry_style)
output_entry.pack(padx=10, pady=5)

# Save to folder
tk.Label(root, text="Save to (velg mappe):", **label_style).pack(pady=(10, 0))
folder_entry = tk.Entry(root, width=60, **entry_style)
folder_entry.pack(padx=10, pady=5)
tk.Button(root, text="Browse Folder", command=browse_folder).pack(pady=5)

# Start-knapp
tk.Button(root, text="Start", command=start_ffmpeg).pack(pady=15)

root.mainloop()