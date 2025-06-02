
import tkinter as tk
from tkinter import messagebox
import yt_dlp

def skini_muziku(link):
    opcije = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(opcije) as ydl:
            ydl.download([link])
        return True
    except Exception as e:
        messagebox.showerror("Greška", f"Došlo je do greške: {str(e)}")
        return False

def on_click():
    link = entry.get()
    if not link.strip():
        messagebox.showwarning("Upozorenje", "Unesi YouTube link.")
        return
    btn.config(state="disabled")
    success = skini_muziku(link)
    if success:
        messagebox.showinfo("Gotovo", "Muzika je uspešno skinuta!")
    btn.config(state="normal")

# GUI
app = tk.Tk()
app.title("YouTube MP3 Downloader")
app.geometry("400x150")
app.resizable(False, False)

tk.Label(app, text="Unesi YouTube link:").pack(pady=10)
entry = tk.Entry(app, width=50)
entry.pack(pady=5)

btn = tk.Button(app, text="Skini MP3", command=on_click)
btn.pack(pady=10)

app.mainloop()
