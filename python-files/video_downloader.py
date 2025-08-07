import tkinter as tk
from tkinter import messagebox, filedialog
from yt_dlp import YoutubeDL
import threading

def download_video():
    url = url_entry.get().strip()
    choice = format_choice.get()

    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    # Ask where to save the file
    download_path = filedialog.askdirectory(title="Choose download folder")
    if not download_path:
        return

    # Options for yt-dlp
    options = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
    }

    if choice == 'Video':
        options['format'] = 'bestvideo+bestaudio/best'
    elif choice == 'Audio (MP3)':
        options.update({
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

    def run_download():
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            messagebox.showerror("Download Failed", str(e))

    # Run in background to keep UI responsive
    threading.Thread(target=run_download).start()

# GUI setup
app = tk.Tk()
app.title("Video Downloader")
app.geometry("400x250")
app.resizable(False, False)

tk.Label(app, text="Video URL:").pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack()

tk.Label(app, text="Select format:").pack(pady=10)
format_choice = tk.StringVar(value="Video")
tk.OptionMenu(app, format_choice, "Video", "Audio (MP3)").pack()

tk.Button(app, text="Download", command=download_video, bg="green", fg="white").pack(pady=20)

tk.Label(app, text="Powered by yt-dlp", fg="gray").pack(side="bottom", pady=10)

app.mainloop()
