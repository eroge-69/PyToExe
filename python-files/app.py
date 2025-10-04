import os
import zipfile, tarfile
import py7zr
import rarfile
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

ARCHIVE_EXTENSIONS = (".zip", ".tar", ".tar.gz", ".tgz", ".7z", ".rar")

def lister_archives():
    folder = filedialog.askdirectory(title="Choisir un dossier avec des archives")
    if not folder:
        return

    archives_list.delete(0, ttk.END)

    for f in os.listdir(folder):
        if f.lower().endswith(ARCHIVE_EXTENSIONS):
            archives_list.insert(ttk.END, os.path.join(folder, f))

def extraire_archive():
    selection = archives_list.curselection()
    if not selection:
        messagebox.showwarning("Aucune sélection", "Sélectionne une archive à extraire.")
        return

    archive_path = archives_list.get(selection[0])
    destination = filedialog.askdirectory(title="Choisir le dossier de destination")
    if not destination:
        return

    try:
        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(destination)
        elif archive_path.endswith((".tar", ".tar.gz", ".tgz")):
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(destination)
        elif archive_path.endswith(".7z"):
            with py7zr.SevenZipFile(archive_path, 'r') as z7:
                z7.extractall(path=destination)
        elif archive_path.endswith(".rar"):
            with rarfile.RarFile(archive_path) as rf:
                rf.extractall(destination)

        messagebox.showinfo("Succès", f"Archive extraite dans :\n{destination}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d’extraire l’archive :\n{e}")

# ---------------------------
# Interface moderne
# ---------------------------
app = ttk.Window(themename="cyborg")  # tu peux tester "flatly", "darkly", "cosmo", etc.
app.title("Extracteur d'archives moderne")
app.geometry("700x450")

title_label = ttk.Label(app, text="📦 Extracteur d'archives", font=("Helvetica", 20, "bold"))
title_label.pack(pady=20)

frame = ttk.Frame(app)
frame.pack(pady=10)

btn_lister = ttk.Button(frame, text="📂 Choisir dossier", command=lister_archives, bootstyle=PRIMARY)
btn_lister.grid(row=0, column=0, padx=10)

btn_extraire = ttk.Button(frame, text="⬇️ Extraire sélection", command=extraire_archive, bootstyle=SUCCESS)
btn_extraire.grid(row=0, column=1, padx=10)

archives_list = ttk.Listbox(app, width=80, height=15, bootstyle=INFO)
archives_list.pack(pady=20)

app.mainloop()
