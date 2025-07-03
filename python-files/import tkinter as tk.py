import tkinter as tk
from tkinter import messagebox
import random

class JeuDevineNombre:
    def __init__(self, master):
        self.master = master
        self.master.title("🎮 Devine le Nombre")
        self.master.geometry("300x200")
        self.nombre_secret = random.randint(1, 100)
        self.essais = 0

        self.label = tk.Label(master, text="Devine un nombre entre 1 et 100")
        self.label.pack(pady=10)

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.button = tk.Button(master, text="Vérifier", command=self.verifier)
        self.button.pack(pady=5)

        self.resultat = tk.Label(master, text="")
        self.resultat.pack()

    def verifier(self):
        try:
            choix = int(self.entry.get())
            self.essais += 1

            if choix < self.nombre_secret:
                self.resultat.config(text="🔻 Trop petit !")
            elif choix > self.nombre_secret:
                self.resultat.config(text="🔺 Trop grand !")
            else:
                messagebox.showinfo("✅ Gagné !", f"Bravo ! Tu as trouvé {self.nombre_secret} en {self.essais} essais.")
                self.master.destroy()
        except ValueError:
            self.resultat.config(text="⛔ Entre un nombre valide.")

if __name__ == "__main__":
    root = tk.Tk()
    jeu = JeuDevineNombre(root)
    root.mainloop()
