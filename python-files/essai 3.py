# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 22:45:24 2025

@author: ARRAIS JEAN
"""

import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime

class Application(tk.Tk):
    """
    Une application avec une interface graphique pour capturer et enregistrer des images à partir d'une caméra USB.
    """
    def __init__(self):
        """
        Initialise l'application.
        """
        super().__init__()
        self.title("Application de Capture d'Image")
        self.geometry("1024x768") # Agrandir la fenêtre pour une meilleure disposition

        # Création des widgets de l'interface
        self._creer_widgets()

        # Initialisation de la caméra
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur Caméra", "Impossible d'accéder à la caméra. Vérifiez qu'elle est bien branchée.")
            self.destroy()
            return
           
        self._afficher_flux_camera()

    def _creer_widgets(self):
        """
        Crée et place les widgets dans la fenêtre principale.
        """
        # --- Cadre principal ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Cadre de gauche pour la saisie des données ---
        left_frame = tk.Frame(main_frame, borderwidth=2, relief="groove")
        left_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
       
        tk.Label(left_frame, text="Informations de la Photo", font=("Helvetica", 14, "bold")).pack(pady=10)

        labels = ["Nom Client:", "Produit:", "Batch:", "Wafer:", "Die:", "Serial Number:"]
        self.entries = {}

        form_frame = tk.Frame(left_frame)
        form_frame.pack(padx=10)

        for i, label_text in enumerate(labels):
            label = tk.Label(form_frame, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=8, sticky="w")
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=8)
            self.entries[label_text.split(":")[0].replace(" ", "_").lower()] = entry

        # --- Cadre de droite pour la visualisation ---
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # Cadre pour l'affichage de la caméra
        self.label_camera = tk.Label(right_frame)
        self.label_camera.pack(pady=10, fill="both", expand=True)

        # Bouton de prise de photo
        bouton_photo = tk.Button(right_frame, text="Prendre une photo", font=("Helvetica", 12, "bold"), command=self._prendre_photo)
        bouton_photo.pack(pady=20)

    def _afficher_flux_camera(self):
        """
        Capture une image de la caméra et l'affiche dans l'interface.
        """
        ret, frame = self.cap.read()
        if ret:
            # Redimensionner l'image pour qu'elle s'adapte au cadre
            frame_resized = self._redimensionner_image(frame, self.label_camera.winfo_width())

            # Convertir l'image de BGR (OpenCV) à RGB
            image_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            # Convertir l'image en un format compatible avec Tkinter
            image_pil = Image.fromarray(image_rgb)
            image_tk = ImageTk.PhotoImage(image=image_pil)

            # Mettre à jour le label avec la nouvelle image
            self.label_camera.imgtk = image_tk
            self.label_camera.configure(image=image_tk)

        # Répéter cette fonction toutes les 15 millisecondes
        self.after(15, self._afficher_flux_camera)

    def _redimensionner_image(self, frame, largeur_cible):
        """Redimensionne une image en conservant son ratio."""
        if largeur_cible < 10: # Eviter les erreurs au démarrage
            largeur_cible = 640

        h, w, _ = frame.shape
        ratio = h / w
        hauteur_cible = int(largeur_cible * ratio)
        return cv2.resize(frame, (largeur_cible, hauteur_cible))

    def _reinitialiser_champs(self):
        """Efface le contenu de tous les champs de saisie."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def _prendre_photo(self):
        """
        Capture l'image actuelle, la nomme, l'enregistre et demande si on réinitialise les champs.
        """
        # Récupérer les valeurs des champs de saisie
        info_photo = {key: entry.get() for key, entry in self.entries.items()}

        # Vérifier que tous les champs sont remplis
        if not all(info_photo.values()):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        # Créer le chemin du dossier de base
        base_dir = r"C:\PHOTO"
        chemin_dossier_client = os.path.join(base_dir, info_photo["nom_client"])
       
        try:
            os.makedirs(chemin_dossier_client, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Erreur de création de dossier", f"Impossible de créer le dossier : {chemin_dossier_client}\nErreur: {e}")
            return

        # Créer le nom du fichier
        date_photo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nom_fichier = f"{info_photo['produit']}_{info_photo['batch']}_{info_photo['wafer']}_{info_photo['die']}_{info_photo['serial_number']}_{date_photo}.jpg"
        chemin_fichier_complet = os.path.join(chemin_dossier_client, nom_fichier)

        # Capturer et enregistrer l'image
        ret, frame = self.cap.read()
        if ret:
            try:
                cv2.imwrite(chemin_fichier_complet, frame)
                messagebox.showinfo("Succès", f"Photo enregistrée sous : {chemin_fichier_complet}")
               
                # Demander si on réinitialise les champs
                if messagebox.askyesno("Réinitialiser ?", "Voulez-vous réinitialiser les champs ?"):
                    self._reinitialiser_champs()

            except Exception as e:
                messagebox.showerror("Erreur d'enregistrement", f"Impossible d'enregistrer la photo.\nErreur: {e}")

    def on_closing(self):
        """
        Libère la caméra et ferme l'application.
        """
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()