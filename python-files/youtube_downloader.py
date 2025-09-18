import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog

def download_media():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube video or playlist URL.")
        return

    ydl_opts = {
        'outtmpl': output_entry.get() or '%(title)s.%(ext)s',
        'writesubtitles': subtitles_var.get(),
        'writethumbnail': thumbnail_var.get(),
        'noplaylist': not playlist_var.get(),
    }

    if audio_only_var.get():
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format_var.get(),
                'preferredquality': audio_quality_var.get(),
            }],
        })
    else:
        format_choice = video_format_var.get()
        format_code = video_formats.get(format_choice, 'bestvideo+bestaudio/best')
        ydl_opts['format'] = format_code

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_output():
    filename = filedialog.asksaveasfilename(defaultextension='.%(ext)s', filetypes=[('All Files', '*.*')])
    if filename:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filename)

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# URL Entry
tk.Label(root, text="YouTube URL:").grid(row=0, column=0, sticky='e')
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, columnspan=3, pady=5)

# Output Template
tk.Label(root, text="Output Template:").grid(row=1, column=0, sticky='e')
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, columnspan=2, pady=5)
output_entry.insert(0, '%(title)s.%(ext)s')
tk.Button(root, text="Browse...", command=browse_output).grid(row=1, column=3, pady=5)

# Video Format
tk.Label(root, text="Video Format:").grid(row=2, column=0, sticky='e')
video_format_var = tk.StringVar(value='Best Quality')
video_formats = {
    'Best Quality': 'bestvideo+bestaudio/best',
    'High Quality (1080p)': 'bestvideo[height<=1080]+bestaudio/best',
    'Medium Quality (720p)': 'bestvideo[height<=720]+bestaudio/best',
    'Low Quality (480p)': 'bestvideo[height<=480]+bestaudio/best',
    'Very Low Quality (360p)': 'bestvideo[height<=360]+bestaudio/best',
    'WebM Format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]',
    'MP4 Format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
}
video_format_menu = tk.OptionMenu(root, video_format_var, *video_formats.keys())
video_format_menu.grid(row=2, column=1, columnspan=3, pady=5, sticky='w')

# Audio Only Option
audio_only_var = tk.BooleanVar()
tk.Checkbutton(root, text="Audio Only", variable=audio_only_var).grid(row=3, column=0, sticky='w')

# Audio Format
tk.Label(root, text="Audio Format:").grid(row=3, column=1, sticky='e')
audio_format_var = tk.StringVar(value='mp3')
audio_format_menu = tk.OptionMenu(root, audio_format_var, 'mp3', 'aac', 'wav', 'm4a')
audio_format_menu.grid(row=3, column=2, sticky='w')

# Audio Quality
tk.Label(root, text="Audio Quality (kbps):").grid(row=3, column=3, sticky='e')
audio_quality_var = tk.StringVar(value='192')
audio_quality_entry = tk.Entry(root, textvariable=audio_quality_var, width=5)
audio_quality_entry.grid(row=3, column=4, sticky='w')

# Thumbnail Option
thumbnail_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download Thumbnail", variable=thumbnail_var).grid(row=4, column=0, sticky='w')

# Subtitles Option
subtitles_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download Subtitles", variable=subtitles_var).grid(row=4, column=1, sticky='w')

# Playlist Option
playlist_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download Playlist", variable=playlist_var).grid(row=4, column=2, sticky='w')

# Download Button
download_button = tk.Button(root, text="Download", command=download_media)
download_button.grid(row=5, column=0, columnspan=5, pady=10)

root.mainloop()
