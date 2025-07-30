import tkinter as tk
from tkinter import messagebox
import unicodedata
import os

def normaliser(texte):
    texte = texte.lower()
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    return texte.strip()

def tronquer_apres_virgule(texte):
    return texte.split(',', 1)[0].strip()

class RechercheApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Recherche COM / MON")
        self.master.geometry("1500x850")
        self.master.configure(bg="#e5e7eb")  # gris clair

        self.base_COM = []
        self.base_MON = []

        # Titre
        tk.Label(master, text="🔎 Recherche dans les bases COM et MON",
                 font=("Segoe UI", 18, "bold"), bg="#e5e7eb", fg="#111827").pack(pady=20)

        # Barre de recherche
        self.entry = tk.Entry(master, font=("Segoe UI", 16), width=60)
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.rechercher)

        # Liste de résultats
        self.result_listbox = tk.Listbox(master, font=("Consolas", 12), width=170, height=30,bg="#ffffff", fg="#1f2937", activestyle="none",selectbackground="#93c5fd", selectforeground="#000")
        self.result_listbox.pack(pady=10, padx=30)
        self.result_listbox.bind("<Double-Button-1>", self.copier_selection)

        # Boutons en bas
        bouton_frame = tk.Frame(master, bg="#e5e7eb")
        bouton_frame.pack(pady=10)

        # Bouton Quitter
        quitter_btn = tk.Button(bouton_frame, text="❌ Quitter", command=master.quit,bg="#fecaca", fg="#7f1d1d", font=("Segoe UI", 12, "bold"), width=20)
        quitter_btn.pack(side=tk.LEFT, padx=10)

        # Message d’état
        self.label_info = tk.Label(master, text="", font=("Segoe UI", 10), bg="#e5e7eb", fg="#374151")
        self.label_info.pack(pady=5)

        self.charger_bases_depuis_dossier()

    def charger_bases_depuis_dossier(self):
        dossier = os.path.dirname(os.path.abspath(__file__))
        fichier_com = os.path.join(dossier, "partition_LGSCM_COM_ACQ_CMD.dic")
        fichier_mon = os.path.join(dossier, "LGSCM_MON.dic")

        messages = []
        if os.path.exists(fichier_com):
            with open(fichier_com, 'r', encoding='utf-8') as f:
                self.base_COM = [line.strip() for line in f if line.strip()]
            messages.append(f"✅ COM.dic chargé ({len(self.base_COM)} lignes)")
        else:
            messages.append("⚠️ Fichier COM.dic introuvable.")

        if os.path.exists(fichier_mon):
            with open(fichier_mon, 'r', encoding='utf-8') as f:
                self.base_MON = [line.strip() for line in f if line.strip()]
            messages.append(f"✅ MON.dic chargé ({len(self.base_MON)} lignes)")
        else:
            messages.append("⚠️ Fichier MON.dic introuvable.")

        self.label_info.config(text='\n'.join(messages))
        self.rechercher()

    def rechercher(self, event=None):
        recherche = normaliser(self.entry.get())
        self.result_listbox.delete(0, tk.END)

        resultats_COM = [l for l in self.base_COM if recherche in normaliser(l)] if recherche else self.base_COM
        resultats_MON = [l for l in self.base_MON if recherche in normaliser(l)] if recherche else self.base_MON

        if resultats_COM:
            self.result_listbox.insert(tk.END, "─── Résultats COM ───")
            for ligne in resultats_COM:
                self.result_listbox.insert(tk.END, tronquer_apres_virgule(ligne))

        if resultats_MON:
            self.result_listbox.insert(tk.END, "─── Résultats MON ───")
            for ligne in resultats_MON:
                self.result_listbox.insert(tk.END, tronquer_apres_virgule(ligne))

        if not resultats_COM and not resultats_MON:
            self.result_listbox.insert(tk.END, "Aucun résultat trouvé.")

    def copier_selection(self, event=None):
        selection = self.result_listbox.curselection()
        if selection:
            texte = self.result_listbox.get(selection[0])
            if texte.startswith("───") or texte.strip() == "":
                messagebox.showwarning("Non copiable", "Cette ligne est un séparateur.")
                return
            self.master.clipboard_clear()
            self.master.clipboard_append(texte)
            messagebox.showinfo("Copié", f"✅ Copié :\n{texte}")
        else:
            messagebox.showwarning("Rien sélectionné", "Veuillez sélectionner un élément à copier.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RechercheApp(root)
    root.mainloop()
