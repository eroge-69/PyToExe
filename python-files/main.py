import os 
import shutil
import tempfile
import tkinter as tk 
from tkinter import messagebox, ttk

APP_NAME = "Inso Cleaner"

def nettoyer_systeme():
    fichiers_supprimes = 0

    temp_dir = tempfile.gettempdir()
    fichiers_supprimes += supprimer_contenu_dossier(temp_dir)

    win_temp = r"C:\Windows\Temp"
    fichiers_supprimes += supprimer_contenu_dossier(win_temp)

    win_prefetch = r"C:\Windows\Prefetch"
    fichiers_supprimes += supprimer_contenu_dossier(win_prefetch)

    try:
        vider_corbeille()
    except:
        pass

    messagebox.showinfo(APP_NAME, f"Nettoyage terminé.\nFichiers supprimés : {fichiers_supprimes}")

def supprimer_contenu_dossier(dossier):
    count = 0
    if not os.path.exists(dossier):
        return 0
    for root, dirs, files in os.walk(dossier):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
                count += 1
            except:
                pass
        for dir in dirs:
            try:
                shutil.rmtree(os.path.join(root, dir), ignore_errors=True)
                count += 1
            except:
                pass
    return count

def vider_corbeille():
    import ctypes
    SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
    SHEmptyRecycleBin(None, None, 0x00000001)

def lancer_interface():
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("500x300")
    root.configure(bg="black")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton",
                    foreground="#00FF00",
                    background="black",
                    font=("Courier", 12, "bold"),
                    borderwidth=0)

    titre = tk.Label(root, text="INSO CLEANER", font=("Courier", 24, "bold"), fg="#00FF00", bg="black")
    titre.pack(pady=20)

    bouton = ttk.Button(root, text="Lancer le Nettoyage", command=nettoyer_systeme)
    bouton.pack(pady=20)

    label_info = tk.Label(root, text="Optimisez votre PC avec Inso!", fg="#00FF00", bg="black", font=("Courier", 10))
    label_info.pack(side="bottom", pady=20)

    root.mainloop()

if __name__ == "__main__":
    lancer_interface()