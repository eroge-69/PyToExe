import tkinter as tk
from tkinter import messagebox
import os
import gdown
import zipfile
import shutil
import webbrowser

# Dossier de destination
DEST_FOLDER = r"C:\Users\Marc\Images"

def extract_file_id(url):
    """
    Extrait l'ID du fichier depuis l'URL Google Drive.
    """
    if "id=" in url:
        return url.split("id=")[-1]
    elif "/file/d/" in url:
        return url.split("/file/d/")[1].split("/")[0]
    else:
        return None

def download_and_extract(url):
    file_id = extract_file_id(url)
    if not file_id:
        messagebox.showerror("Erreur", "Lien Google Drive invalide.")
        return

    os.makedirs(DEST_FOLDER, exist_ok=True)

    output_zip_path = os.path.join(DEST_FOLDER, "archive.zip")
    gdown.download(id=file_id, output=output_zip_path, quiet=False)

    if not os.path.exists(output_zip_path):
        messagebox.showerror("Erreur", "Le téléchargement a échoué.")
        return

    with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
        zip_ref.extractall(DEST_FOLDER)

    os.remove(output_zip_path)  # Supprime le zip après extraction

    root.destroy()  # Ferme la fenêtre

    # Ouvre l'explorateur de fichiers
    webbrowser.open(DEST_FOLDER)

def lancer_interface():
    global root
    root = tk.Tk()
    root.title("Téléchargement Google Drive")

    tk.Label(root, text="Colle ici le lien du fichier Google Drive (ZIP) :").pack(padx=10, pady=10)

    url_entry = tk.Entry(root, width=60)
    url_entry.pack(padx=10, pady=5)

    def on_valider():
        url = url_entry.get()
        if url.strip() == "":
            messagebox.showwarning("Attention", "Le lien est vide.")
            return
        download_and_extract(url)

    tk.Button(root, text="Télécharger et Dézipper", command=on_valider).pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    lancer_interface()
