
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END
import os
import threading
import subprocess

CHEMIN_BASE = r"W:\\06_0024\\20_EXPLOITA\\03_ELEC\\01_COMMUN_3\\05 - TRAVAUX CABINES CLIENTS\\09 - ARCHIVES"

class RechercheCabinesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recherche Cabines Clients")
        self.root.geometry("700x400")
        self.root.resizable(False, False)

        self.label = tk.Label(root, text="🔍 Rechercher un numéro ou nom de cabine :", font=('Segoe UI', 10))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=80)
        self.entry.pack(pady=5)
        self.entry.bind("<KeyRelease>", self.filter_list)

        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(root, width=100, height=15, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(pady=10)
        self.listbox.bind('<Double-1>', self.ouvrir_selection)

        self.scrollbar.config(command=self.listbox.yview)

        self.bouton_ouvrir = tk.Button(root, text="Ouvrir le dossier sélectionné", command=self.ouvrir_selection)
        self.bouton_ouvrir.pack(pady=10)

        self.dossiers = []
        self.scan_thread = threading.Thread(target=self.scan_dossiers)
        self.scan_thread.start()

    def scan_dossiers(self):
        for root, dirs, files in os.walk(CHEMIN_BASE):
            for d in dirs:
                self.dossiers.append(os.path.join(root, d))
        self.filter_list()

    def filter_list(self, event=None):
        critere = self.entry.get().lower()
        self.listbox.delete(0, END)
        for dossier in self.dossiers:
            if critere in os.path.basename(dossier).lower():
                self.listbox.insert(END, dossier)

    def ouvrir_selection(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            dossier = self.listbox.get(selection[0])
            subprocess.Popen(f'explorer "{dossier}"')
        else:
            messagebox.showinfo("Information", "Veuillez sélectionner un dossier.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RechercheCabinesApp(root)
    root.mainloop()
