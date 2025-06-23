import tkinter as tk
import random

class DemineurGUI:
    def __init__(self, root, taille=9, nb_mines=10):
        self.root = root
        self.taille = taille
        self.nb_mines = nb_mines
        self.boutons = {}
        self.mines = set()
        self.devoilees = set()
        self.grille = [[0 for _ in range(taille)] for _ in range(taille)]

        self._placer_mines()
        self._calculer_voisines()
        self._creer_widgets()

    def _placer_mines(self):
        while len(self.mines) < self.nb_mines:
            x = random.randint(0, self.taille - 1)
            y = random.randint(0, self.taille - 1)
            self.mines.add((x, y))

    def _calculer_voisines(self):
        for x in range(self.taille):
            for y in range(self.taille):
                if (x, y) in self.mines:
                    self.grille[x][y] = -1
                else:
                    self.grille[x][y] = sum(
                        (i, j) in self.mines
                        for i in range(x - 1, x + 2)
                        for j in range(y - 1, y + 2)
                        if 0 <= i < self.taille and 0 <= j < self.taille
                    )

    def _creer_widgets(self):
        for x in range(self.taille):
            for y in range(self.taille):
                bouton = tk.Button(self.root, text=' ', width=3, command=lambda x=x, y=y: self.devoiler(x, y))
                bouton.grid(row=x, column=y)
                self.boutons[(x, y)] = bouton

    def devoiler(self, x, y):
        if (x, y) in self.devoilees:
            return

        self.devoilees.add((x, y))
        bouton = self.boutons[(x, y)]

        if (x, y) in self.mines:
            bouton.config(text='💣', bg='red')
            self.fin_partie(False)
            return

        val = self.grille[x][y]
        bouton.config(text=str(val) if val > 0 else '', bg='lightgrey', relief=tk.SUNKEN)

        if val == 0:
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if 0 <= i < self.taille and 0 <= j < self.taille:
                        self.devoiler(i, j)

        if self._a_gagne():
            self.fin_partie(True)

    def fin_partie(self, gagne):
        for (x, y), bouton in self.boutons.items():
            if (x, y) in self.mines:
                bouton.config(text='💣')
            bouton.config(state=tk.DISABLED)

        message = "🎉 Gagné !" if gagne else "💥 Perdu !"
        resultat = tk.Label(self.root, text=message, font=('Helvetica', 14, 'bold'))
        resultat.grid(row=self.taille, column=0, columnspan=self.taille)

    def _a_gagne(self):
        return len(self.devoilees) == self.taille**2 - self.nb_mines

# Lancer l'interface graphique
root = tk.Tk()
root.title("Démineur")
app = DemineurGUI(root, taille=16, nb_mines=20)
root.mainloop()
