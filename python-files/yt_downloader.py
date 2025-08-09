import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
import threading
import tkinter.filedialog


# Funkcija za preuzimanje YouTube fajla
def download_video(link, folder, progress_var):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: progress_hook(d, progress_var)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        messagebox.showinfo("Gotovo!", "Preuzimanje je završeno!")
    except Exception as e:
        messagebox.showerror("Greška", f"Došlo je do greške: {str(e)}")


def progress_hook(d, progress_var):
    if d['status'] == 'downloading':
        progress_var.set(d['downloaded_bytes'] * 100 / d['total_bytes'])


# Funkcija za izbor foldera
def browse_folder(folder_label):
    folder = tk.filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)


# Funkcija za pokretanje preuzimanja
def start_download(link_entry, folder_label):
    link = link_entry.get()
    folder = folder_label.cget("text")
    if not link or folder == "Izaberi folder":
        messagebox.showerror("Greška", "Unesite link i folder!")
        return
    # Prikaz pozdravne poruke na početku
    messagebox.showinfo("Dobrodošli!", "Hvala što koristite ovaj program\nby.kimich")

    # Preuzimanje videa
    open_download_window(link, folder)


# Funkcija za otvaranje prozora za preuzimanje
def open_download_window(link, folder):
    tk.Label(root, text="Preuzimanje u toku...").pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(pady=20)

    threading.Thread(target=download_video, args=(link, folder, progress_var), daemon=True).start()


# Glavni GUI Setup
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("450x350+100+100")

# Unos linka i foldera za preuzimanje
tk.Label(root, text="Unesite YouTube link:").pack(pady=10)
link_entry = tk.Entry(root, width=50)
link_entry.pack(pady=5)

tk.Label(root, text="Izaberite folder:").pack(pady=10)
folder_label = tk.Label(root, text="Izaberi folder")
folder_label.pack(pady=5)

# Dugme za izbor foldera
browse_button = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_label))
browse_button.pack(pady=5)

# Dugme za početak preuzimanja (START)
download_button = tk.Button(root, text="Start", command=lambda: start_download(link_entry, folder_label))
download_button.pack(pady=20)

# Glavni prozor
root.mainloop()

root.mainloop()


