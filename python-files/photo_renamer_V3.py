import os
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk

FORMATS_VALIDES = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# ---------- Partie principale ----------
class PhotoRenamerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Renommage de photos")

        tk.Label(self.root, text="Choisissez une option :", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.root, text="Renommer un ensemble de photos", command=self.mode_lot,
                  width=30, height=2, bg="lightblue").pack(pady=10)

        tk.Button(self.root, text="Renommer les photos une par une", command=self.mode_un_par_un,
                  width=30, height=2, bg="lightgreen").pack(pady=10)

        tk.Button(self.root, text="Renommer + copier dans un autre dossier", command=self.mode_copie_renommage,
                  width=30, height=2, bg="orange").pack(pady=10)

        self.root.mainloop()

    def choisir_dossier(self):
        dossier = filedialog.askdirectory(title="Choisir un dossier contenant des photos")
        if not dossier:
            return None
        fichiers = sorted([
            f for f in os.listdir(dossier)
            if f.lower().endswith(FORMATS_VALIDES)
        ])
        if not fichiers:
            messagebox.showerror("Erreur", "Le dossier ne contient pas de photos valides (jpg, png, etc.)")
            return None
        return dossier, fichiers

    def creer_nouveau_dossier(self):
        parent = filedialog.askdirectory(title="Choisir l'emplacement du nouveau dossier")
        if not parent:
            return None
        nom = simpledialog.askstring("Nom du dossier", "Nom du nouveau dossier :")
        if not nom:
            return None
        chemin = os.path.join(parent, nom)
        try:
            os.makedirs(chemin, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer le dossier : {e}")
            return None
        return chemin

    def mode_lot(self):
        resultat = self.choisir_dossier()
        if not resultat:
            return
        dossier, fichiers = resultat

        titre = simpledialog.askstring("Titre", "Entrer un titre pour l'ensemble des photos :")
        if not titre:
            return

        nouveaux_noms = []
        for i, f in enumerate(fichiers, 1):
            ext = os.path.splitext(f)[1]
            nouveau_nom = f"{titre} {i}{ext}"
            nouveaux_noms.append(nouveau_nom)

        preview_win = tk.Toplevel()
        preview_win.title("Prévisualisation du renommage")

        tk.Label(preview_win, text="Voici les nouveaux noms qui seront appliqués :", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(preview_win, width=50, height=15)
        listbox.pack(padx=20, pady=10)

        for ancien, nouveau in zip(fichiers, nouveaux_noms):
            listbox.insert(tk.END, f"{ancien}  →  {nouveau}")

        def confirmer():
            for ancien, nouveau in zip(fichiers, nouveaux_noms):
                os.rename(os.path.join(dossier, ancien), os.path.join(dossier, nouveau))
            messagebox.showinfo("Succès", f"{len(fichiers)} fichiers renommés avec succès.")
            preview_win.destroy()

        def annuler():
            preview_win.destroy()

        btn_frame = tk.Frame(preview_win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Confirmer", command=confirmer, bg="lightgreen", width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Annuler", command=annuler, bg="tomato", width=10).pack(side=tk.LEFT, padx=10)

    def mode_un_par_un(self):
        resultat = self.choisir_dossier()
        if not resultat:
            return
        dossier, fichiers = resultat
        RenommageInteractif(dossier, fichiers)

    def mode_copie_renommage(self):
        resultat = self.choisir_dossier()
        if not resultat:
            return
        dossier_source, fichiers = resultat

        choix_win = tk.Toplevel()
        choix_win.title("Choisir le dossier de destination")
        tk.Label(choix_win, text="Choisissez ou créez un dossier de destination :", font=("Arial", 12)).pack(pady=10)

        def choisir():
            chemin = filedialog.askdirectory(title="Choisir un dossier de destination")
            if chemin:
                choix_win.destroy()
                self.confirmer_copie(dossier_source, fichiers, chemin)

        def creer():
            chemin = self.creer_nouveau_dossier()
            if chemin:
                choix_win.destroy()
                self.confirmer_copie(dossier_source, fichiers, chemin)

        btn_frame = tk.Frame(choix_win)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Choisir dossier existant", command=choisir, bg="lightblue", width=22).pack(pady=5)
        tk.Button(btn_frame, text="Créer un nouveau dossier", command=creer, bg="lightyellow", width=22).pack(pady=5)

    def confirmer_copie(self, dossier_source, fichiers, dossier_dest):
        titre = simpledialog.askstring("Titre", "Entrer un nom de base pour les fichiers copiés :")
        if not titre:
            return

        nouveaux_noms = []
        for i, f in enumerate(fichiers, 1):
            ext = os.path.splitext(f)[1]
            base_nom = f"{titre} {i}{ext}"
            nouveau_nom = base_nom
            compteur = 1
            while os.path.exists(os.path.join(dossier_dest, nouveau_nom)):
                nouveau_nom = f"{titre} {i} ({compteur}){ext}"
                compteur += 1
            nouveaux_noms.append(nouveau_nom)

        preview_win = tk.Toplevel()
        preview_win.title("Prévisualisation des copies renommées")

        tk.Label(preview_win, text="Les fichiers seront copiés et renommés comme suit :", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(preview_win, width=60, height=15)
        listbox.pack(padx=20, pady=10)

        for ancien, nouveau in zip(fichiers, nouveaux_noms):
            listbox.insert(tk.END, f"{ancien}  →  {nouveau}")

        def confirmer():
            for ancien, nouveau in zip(fichiers, nouveaux_noms):
                shutil.copy2(os.path.join(dossier_source, ancien), os.path.join(dossier_dest, nouveau))
            messagebox.showinfo("Succès", f"{len(fichiers)} fichiers copiés et renommés avec succès.")
            preview_win.destroy()

        def annuler():
            preview_win.destroy()

        btn_frame = tk.Frame(preview_win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Confirmer", command=confirmer, bg="lightgreen", width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Annuler", command=annuler, bg="tomato", width=12).pack(side=tk.LEFT, padx=10)

# ---------- Interface de renommage un par un ----------
class RenommageInteractif:
    def __init__(self, dossier, fichiers):
        self.dossier = dossier
        self.fichiers = fichiers
        self.index = 0

        self.win = tk.Toplevel()
        self.win.title("Renommer les photos une par une")
        self.win.geometry("800x600")

        tk.Label(self.win, text="Dossier sélectionné :", font=("Arial", 10)).place(x=20, y=5)
        tk.Label(self.win, text=dossier, font=("Arial", 9), fg="gray").place(x=150, y=5)

        self.image_label = tk.Label(self.win)
        self.image_label.place(x=20, y=40)

        self.entry = tk.Entry(self.win, font=("Arial", 14), width=30)
        self.entry.place(x=450, y=120)
        self.entry.bind("<Return>", self.renommer)

        self.hint_label = tk.Label(self.win, text="+ ENTRÉE", font=("Arial", 10), fg="gray")
        self.hint_label.place(x=450, y=155)

        self.label_info = tk.Label(self.win, text="", font=("Arial", 12))
        self.label_info.place(x=450, y=80)

        self.progress_label = tk.Label(self.win, text="", font=("Arial", 10), fg="blue")
        self.progress_label.place(x=450, y=190)

        self.btn_prev = tk.Button(self.win, text="← Précédent", command=self.reculer, state=tk.DISABLED)
        self.btn_prev.place(x=450, y=230)

        self.btn_next = tk.Button(self.win, text="Suivant →", command=self.avancer, state=tk.DISABLED)
        self.btn_next.place(x=570, y=230)

        btn_quit = tk.Button(self.win, text="Quitter", command=self.win.destroy, bg="tomato")
        btn_quit.place(x=700, y=540)

        self.afficher_photo()

    def afficher_photo(self):
        if self.index >= len(self.fichiers):
            messagebox.showinfo("Terminé", "Toutes les photos ont été renommées.")
            self.win.destroy()
            return

        chemin = os.path.join(self.dossier, self.fichiers[self.index])
        image = Image.open(chemin)
        image.thumbnail((600, 600))
        self.tkimage = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.tkimage)

        self.label_info.config(text=f"Fichier {self.index + 1} sur {len(self.fichiers)}")
        self.progress_label.config(text=f"Nom actuel : {self.fichiers[self.index]}")
        self.entry.delete(0, tk.END)

        self.btn_prev.config(state=tk.NORMAL if self.index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.index < len(self.fichiers) - 1 else tk.DISABLED)

    def renommer(self, event=None):
        nouveau_nom = self.entry.get().strip()
        if not nouveau_nom:
            return
        ext = os.path.splitext(self.fichiers[self.index])[1]
        nouveau_fichier = f"{nouveau_nom}{ext}"
        ancien_chemin = os.path.join(self.dossier, self.fichiers[self.index])
        nouveau_chemin = os.path.join(self.dossier, nouveau_fichier)

        try:
            os.rename(ancien_chemin, nouveau_chemin)
            self.fichiers[self.index] = nouveau_fichier
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de renommer : {e}")
            return

        self.index += 1
        self.afficher_photo()

    def reculer(self):
        if self.index > 0:
            self.index -= 1
            self.afficher_photo()

    def avancer(self):
        if self.index < len(self.fichiers) - 1:
            self.index += 1
            self.afficher_photo()

# ---------- Lancement ----------
if __name__ == "__main__":
    PhotoRenamerApp()
