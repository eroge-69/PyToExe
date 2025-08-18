import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL

def download_video():
    url = url_entry.get()
    if not url.strip():
        messagebox.showwarning("Erreur", "Veuillez entrer un lien YouTube.")
        return

    # Choisir dossier de sortie
    out_dir = filedialog.askdirectory(title="Choisissez le dossier de téléchargement")
    if not out_dir:
        return

    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(title).200B [%(id)s].%(ext)s"),
        # On cherche d’abord meilleure vidéo MP4 + meilleur audio M4A
        # sinon on prend le meilleur format dispo compatible MP4
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",  # sortie forcée en MP4
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [progress_hook],
    }

    def run_download():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Succès", "Téléchargement terminé en MP4 !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    threading.Thread(target=run_download).start()

def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        status_var.set(f"Téléchargement... {p}")
    elif d['status'] == 'finished':
        status_var.set("Fusion en MP4...")

# --- Interface Tkinter ---
root = tk.Tk()
root.title("Téléchargeur YouTube (MP4)")

tk.Label(root, text="Lien YouTube :").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Télécharger en MP4", command=download_video).pack(pady=10)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, fg="blue")
status_label.pack(pady=5)

root.mainloop()

