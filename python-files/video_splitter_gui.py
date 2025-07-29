
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip

def split_video(video_path, output_folder, chunk_duration):
    try:
        video = VideoFileClip(video_path)
        duration = int(video.duration)
        os.makedirs(output_folder, exist_ok=True)

        for i in range(0, duration, chunk_duration):
            start = i
            end = min(i + chunk_duration, duration)
            clip = video.subclip(start, end)
            output_path = os.path.join(output_folder, f"{(i // chunk_duration) + 1}.mp4")
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        messagebox.showinfo("Done", f"Video split into parts in:\n{output_folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")]
    )
    if file_path:
        entry_video_path.delete(0, tk.END)
        entry_video_path.insert(0, file_path)

def browse_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        entry_output_folder.delete(0, tk.END)
        entry_output_folder.insert(0, folder)

def run_split():
    video_path = entry_video_path.get()
    output_folder = entry_output_folder.get()
    try:
        chunk_duration = int(entry_duration.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Duration must be an integer.")
        return
    if not os.path.exists(video_path):
        messagebox.showerror("Error", "Video file does not exist.")
        return
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    split_video(video_path, output_folder, chunk_duration)

# GUI SETUP
root = tk.Tk()
root.title("🎬 Video Splitter Tool")
root.geometry("520x280")
root.resizable(False, False)

tk.Label(root, text="Video File:").pack(pady=5)
entry_video_path = tk.Entry(root, width=60)
entry_video_path.pack()
tk.Button(root, text="Browse", command=browse_file).pack(pady=2)

tk.Label(root, text="Output Folder:").pack(pady=5)
entry_output_folder = tk.Entry(root, width=60)
entry_output_folder.pack()
tk.Button(root, text="Choose Folder", command=browse_output_folder).pack(pady=2)

tk.Label(root, text="Chunk Duration (seconds):").pack(pady=5)
entry_duration = tk.Entry(root)
entry_duration.insert(0, "5")
entry_duration.pack()

tk.Button(root, text="Split Video", command=run_split, bg="green", fg="white").pack(pady=15)

root.mainloop()
