import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import random

# Liste pour stocker les chemins des images utilisées
images_utilisees = []

# Définition des succès avec descriptions
succes = {
    "Débutant": {
        "accompli": False,
        "description": "Terminez votre premier puzzle."
    },
    "Intermédiaire": {
        "accompli": False,
        "description": "Terminez 5 puzzles."
    },
    "Expert": {
        "accompli": False,
        "description": "Terminez 10 puzzles."
    },
    "Maître du Puzzle": {
        "accompli": False,
        "description": "Terminez 20 puzzles."
    }
}

class PuzzleGame:
    def __init__(self, root, image_path):
        self.root = root
        img = Image.open(image_path)
        taille_min = min(img.size)
        img = img.crop((0, 0, taille_min, taille_min))
        self.nb_cases = 3
        self.taille_case = taille_min // self.nb_cases
        self.image_originale = img.resize((self.taille_case * self.nb_cases, self.taille_case * self.nb_cases))

        self.pieces_originales = self.decouper_image(self.image_originale)
        self.pieces_melangees, self.vide = self.melanger_pieces()
        self.boutons = [None] * (self.nb_cases ** 2)
        self.tk_images = [None] * (self.nb_cases ** 2)
        self.root.geometry(f"{self.taille_case * self.nb_cases}x{self.taille_case * self.nb_cases}")
        self.afficher_grille()

    def decouper_image(self, img):
        pieces = []
        for i in range(self.nb_cases):
            for j in range(self.nb_cases):
                box = (j * self.taille_case, i * self.taille_case,
                       (j + 1) * self.taille_case, (i + 1) * self.taille_case)
                piece = img.crop(box)
                pieces.append(piece)
        return pieces

    def melanger_pieces(self):
        pieces = self.pieces_originales.copy()
        vide_index = len(pieces) - 1
        pieces[vide_index] = None
        indices = list(range(len(pieces)))
        indices.remove(vide_index)
        random.shuffle(indices)
        grille = [None] * len(pieces)
        for i, idx in enumerate(indices):
            grille[i] = self.pieces_originales[idx]
        grille[vide_index] = None
        return grille, vide_index

    def afficher_grille(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        for i, img in enumerate(self.pieces_melangees):
            if img:
                self.tk_images[i] = ImageTk.PhotoImage(img)
                btn = tk.Button(self.root, image=self.tk_images[i], command=lambda i=i: self.deplacer(i))
                btn.grid(row=i // self.nb_cases, column=i % self.nb_cases)
                self.boutons[i] = btn
            else:
                frame_vide = tk.Frame(self.root, width=self.taille_case, height=self.taille_case, bg="black")
                frame_vide.grid(row=i // self.nb_cases, column=i % self.nb_cases)
                self.boutons[i] = frame_vide

    def deplacer(self, idx):
        if self.est_voisin(idx, self.vide):
            self.pieces_melangees[self.vide], self.pieces_melangees[idx] = self.pieces_melangees[idx], self.pieces_melangees[self.vide]
            self.vide = idx
            self.afficher_grille()
            if self.est_termine():
                messagebox.showinfo("Succès", "Puzzle terminé !")
                self.verifier_succes()

    def verifier_succes(self):
        # Logique pour vérifier et attribuer les succès
        if not succes["Débutant"]["accompli"]:
            succes["Débutant"]["accompli"] = True
        elif not succes["Intermédiaire"]["accompli"]:
            succes["Intermédiaire"]["accompli"] = True
        elif not succes["Expert"]["accompli"]:
            succes["Expert"]["accompli"] = True
        else:
            succes["Maître du Puzzle"]["accompli"] = True

    def est_voisin(self, a, b):
        ligne_a, col_a = a // self.nb_cases, a % self.nb_cases
        ligne_b, col_b = b // self.nb_cases, b % self.nb_cases
        return abs(ligne_a - ligne_b) + abs(col_a - col_b) == 1

    def est_termine(self):
        for i in range(len(self.pieces_originales) - 1):
            if self.pieces_melangees[i] != self.pieces_originales[i]:
                return False
        return True

def choisir_image_et_lancer():
    filepath = filedialog.askopenfilename(title="Choisis une image", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if filepath:
        if filepath not in images_utilisees:
            images_utilisees.append(filepath)
        fenetre = tk.Toplevel(root)
        PuzzleGame(fenetre, filepath)

def show_puzzle_game():
    choisir_image_et_lancer()

def show_gallery():
    gallery_window = tk.Toplevel(root)
    gallery_window.title("Galerie")
    gallery_window.geometry("600x400")

    label = tk.Label(gallery_window, text="Images utilisées dans le jeu", font=("Helvetica", 14))
    label.pack(pady=10)

    frame = tk.Frame(gallery_window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for img_path in images_utilisees:
        img = Image.open(img_path)
        img.thumbnail((100, 100))
        img_tk = ImageTk.PhotoImage(img)
        label_img = tk.Label(scrollable_frame, image=img_tk)
        label_img.image = img_tk
        label_img.pack(pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def show_success():
    success_window = tk.Toplevel(root)
    success_window.title("Succès")
    success_window.geometry("500x400")

    label = tk.Label(success_window, text="Vos Succès", font=("Helvetica", 16))
    label.pack(pady=10)

    for achievement, details in succes.items():
        achievement_frame = tk.Frame(success_window)
        achievement_frame.pack(fill=tk.X, pady=5)

        if details["accompli"]:
            achievement_label = tk.Label(achievement_frame, text=achievement, font=("Helvetica", 12), fg="green")
        else:
            achievement_label = tk.Label(achievement_frame, text=achievement, font=("Helvetica", 12), fg="gray")

        achievement_label.pack(side=tk.LEFT)

        btn_description = tk.Button(achievement_frame, text="Voir Description", command=lambda d=details["description"]: messagebox.showinfo("Description", d))
        btn_description.pack(side=tk.RIGHT)

def quit_game():
    root.quit()

root = tk.Tk()
root.title("Menu Principal")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

label_titre = tk.Label(root, text="Bienvenue au Jeu de Puzzle", font=("Helvetica", 16), bg="#f0f0f0")
label_titre.pack(pady=10)

btn_play = tk.Button(root, text="Jouer", command=show_puzzle_game, font=("Helvetica", 12), bg="#4CAF50", fg="white")
btn_play.pack(pady=10)

btn_gallery = tk.Button(root, text="Galerie", command=show_gallery, font=("Helvetica", 12), bg="#008CBA", fg="white")
btn_gallery.pack(pady=10)

btn_success = tk.Button(root, text="Succès", command=show_success, font=("Helvetica", 12), bg="#f44336", fg="white")
btn_success.pack(pady=10)

btn_quit = tk.Button(root, text="Quitter", command=quit_game, font=("Helvetica", 12), bg="#555555", fg="white")
btn_quit.pack(pady=10)

root.mainloop()
