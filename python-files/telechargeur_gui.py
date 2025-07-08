import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import yt_dlp
import threading

def telecharger(url, mode, log_widget):
    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer un lien.")
        return

    options = {}

    if mode == "audio":
        options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }
    elif mode == "video":
        options = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
        }

    log_widget.insert(tk.END, f"🔄 Téléchargement en cours ({mode})...\n")
    log_widget.see(tk.END)

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        log_widget.insert(tk.END, "✅ Terminé avec succès !\n\n")
    except Exception as e:
        log_widget.insert(tk.END, f"❌ Erreur : {str(e)}\n\n")
    log_widget.see(tk.END)

def lancer_telechargement(mode):
    url = url_entry.get()
    thread = threading.Thread(target=telecharger, args=(url, mode, log_box))
    thread.start()

# === Interface graphique ===
fenetre = tk.Tk()
fenetre.title("Téléchargeur Vidéo/Audio Pro")
fenetre.geometry("600x400")
fenetre.configure(bg="#1e1e1e")

# Champ URL
tk.Label(fenetre, text="Lien de la vidéo :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)
url_entry = tk.Entry(fenetre, width=70, font=("Arial", 11))
url_entry.pack(pady=5)

# Boutons
btn_frame = tk.Frame(fenetre, bg="#1e1e1e")
btn_frame.pack(pady=10)

audio_btn = tk.Button(btn_frame, text="🎵 Télécharger Audio", width=25, bg="#007ACC", fg="white", font=("Arial", 10), command=lambda: lancer_telechargement("audio"))
audio_btn.pack(side=tk.LEFT, padx=10)

video_btn = tk.Button(btn_frame, text="🎬 Télécharger Vidéo", width=25, bg="#007ACC", fg="white", font=("Arial", 10), command=lambda: lancer_telechargement("video"))
video_btn.pack(side=tk.LEFT, padx=10)

# Logs
log_box = scrolledtext.ScrolledText(fenetre, width=70, height=12, bg="#2e2e2e", fg="white", font=("Consolas", 10))
log_box.pack(pady=10)

fenetre.mainloop()
