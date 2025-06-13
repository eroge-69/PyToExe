import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, scrolledtext

# --- 1. Génération de la série logistique ---
def generer_serie_logistique(parametre_A, valeur_initiale, nb_points):
    serie = np.zeros(nb_points)
    serie[0] = valeur_initiale
    for i in range(1, nb_points):
        serie[i] = parametre_A * serie[i-1] * (1 - serie[i-1])
        serie[i] = np.clip(serie[i], 0, 1)
    return serie

# --- 2. Fonctions d'activation ---
def tanh(z):
    return np.tanh(z)

def dtanh(z):
    return 1 - np.tanh(z)**2

# --- 3. Réseau de neurones ---
class ReseauNeuronal:
    def __init__(self, dimension_entree, dimensions_cachees, dimension_sortie, graine=42):
        np.random.seed(graine)
        self.couches = []
        prev_dim = dimension_entree
        for dim in dimensions_cachees:
            poids = np.random.randn(prev_dim, dim) * np.sqrt(1 / prev_dim)
            biais = np.zeros((1, dim))
            self.couches.append((poids, biais))
            prev_dim = dim
        self.poids_sortie = np.random.randn(prev_dim, dimension_sortie) * np.sqrt(1 / prev_dim)
        self.biais_sortie = np.zeros((1, dimension_sortie))
        self.z_cachees = []
        self.activations = []

    def prediction(self, entrees):
        self.z_cachees = []
        self.activations = [entrees]
        for poids, biais in self.couches:
            z = np.dot(self.activations[-1], poids) + biais
            activation = tanh(z)
            self.z_cachees.append(z)
            self.activations.append(activation)
        self.z_sortie = np.dot(self.activations[-1], self.poids_sortie) + self.biais_sortie
        return self.z_sortie

    def calculer_perte(self, prediction, valeurs_reelles):
        return np.mean((prediction - valeurs_reelles)**2)

    def retropropagation(self, entrees, valeurs_reelles, taux_apprentissage, reg_l2):
        m = entrees.shape[0]
        dperte_dz_sortie = 2 * (self.z_sortie - valeurs_reelles) / m
        delta = dperte_dz_sortie

        grad_poids_sortie = np.dot(self.activations[-1].T, delta) + reg_l2 * self.poids_sortie
        grad_biais_sortie = np.sum(delta, axis=0, keepdims=True)

        self.poids_sortie -= taux_apprentissage * grad_poids_sortie
        self.biais_sortie -= taux_apprentissage * grad_biais_sortie

        for i in range(len(self.couches)-1, -1, -1):
            delta = np.dot(delta, self.poids_sortie.T if i == len(self.couches)-1 else self.couches[i+1][0].T) * dtanh(self.z_cachees[i])
            grad_poids = np.dot(self.activations[i].T, delta) + reg_l2 * self.couches[i][0]
            grad_biais = np.sum(delta, axis=0, keepdims=True)
            self.couches[i] = (self.couches[i][0] - taux_apprentissage * grad_poids,
                               self.couches[i][1] - taux_apprentissage * grad_biais)

    def entrainer(self, entrees, sorties, entrees_val, sorties_val, epochs, taux_apprentissage, reg_l2, text_output):
        pertes_train = []
        pertes_val = []
        for epoch in range(epochs):
            prediction_train = self.prediction(entrees)
            perte_train = self.calculer_perte(prediction_train, sorties)
            pertes_train.append(perte_train)
            self.retropropagation(entrees, sorties, taux_apprentissage, reg_l2)
            prediction_val = self.prediction(entrees_val)
            perte_val = self.calculer_perte(prediction_val, sorties_val)
            pertes_val.append(perte_val)
            if (epoch + 1) % (epochs // 10) == 0:
                text_output.insert(tk.END, f"Époque {epoch+1}/{epochs}, Perte entraînement = {perte_train:.8f}, Perte validation = {perte_val:.8f}\n")
                text_output.see(tk.END)
                text_output.update()
        return pertes_train, pertes_val

# --- 4. Prédiction multi-pas ---
def prediction_multi_pas(reseau, valeur_initiale, nb_pas, n_entrees=1):
    preds = [valeur_initiale]
    valeurs_courantes = [valeur_initiale]
    for _ in range(nb_pas):
        if len(valeurs_courantes) < n_entrees:
            entrees = np.array([[valeur_initiale] * (n_entrees - len(valeurs_courantes)) + valeurs_courantes]).reshape(1, n_entrees)
        else:
            entrees = np.array([valeurs_courantes[-n_entrees:]]).reshape(1, n_entrees)
        valeur_suivante = reseau.prediction(entrees)[0, 0]
        preds.append(valeur_suivante)
        valeurs_courantes.append(valeur_suivante)
    return np.array(preds)

def generer_serie_multi_pas(parametre_A, valeur_initiale, nb_pas):
    serie = [valeur_initiale]
    valeur = valeur_initiale
    for _ in range(nb_pas):
        valeur = parametre_A * valeur * (1 - valeur)
        valeur = np.clip(valeur, 0, 1)
        serie.append(valeur)
    return np.array(serie)

# --- 5. Préparation des données avec plusieurs entrées ---
def preparer_donnees(serie, n_entrees):
    entrees = []
    sorties = []
    for i in range(len(serie) - n_entrees):
        entrees.append(serie[i:i+n_entrees])
        sorties.append(serie[i+n_entrees])
    return np.array(entrees).reshape(-1, n_entrees), np.array(sorties).reshape(-1, 1)

# --- 6. Interface Tkinter ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Prédiction de la Suite Logistique avec RNA")
        self.root.geometry("1000x700")

        # Frame pour les contrôles
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        # Sélection de A
        tk.Label(self.control_frame, text="Valeur de A :").pack(side=tk.LEFT, padx=5)
        self.a_combobox = ttk.Combobox(self.control_frame, values=["2.0", "4.2"], state="readonly")
        self.a_combobox.set("2.0")
        self.a_combobox.pack(side=tk.LEFT, padx=5)

        # Bouton pour entraîner
        self.train_button = tk.Button(self.control_frame, text="Entraîner et Prédire", command=self.train_and_predict)
        self.train_button.pack(side=tk.LEFT, padx=5)

        # Zone de texte pour les résultats
        self.text_output = scrolledtext.ScrolledText(self.root, height=10, width=80, wrap=tk.WORD)
        self.text_output.pack(pady=10)

        # Zone pour les graphiques
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = None

    def train_and_predict(self):
        # Effacer la zone de texte
        self.text_output.delete(1.0, tk.END)

        # Paramètres
        parametre_A = float(self.a_combobox.get())
        valeur_initiale = 0.1
        nb_points = 500
        epochs = 2000 if parametre_A == 2.0 else 5000
        taux_apprentissage = 0.001 if parametre_A == 2.0 else 0.0005
        reg_l2 = 0.001
        architecture = [15] if parametre_A == 2.0 else [100, 30]
        n_entrees = 1 if parametre_A == 2.0 else 3

        self.text_output.insert(tk.END, f"\n=== Résultats pour A = {parametre_A} ===\n")
        self.text_output.update()

        # Générer la série
        serie_logistique = generer_serie_logistique(parametre_A, valeur_initiale, nb_points)

        # Préparer les données
        nb_train = int(0.8 * nb_points)
        entrees_apprentissage, sorties_apprentissage = preparer_donnees(serie_logistique[:nb_train], n_entrees)
        entrees_validation, sorties_validation = preparer_donnees(serie_logistique[nb_train:], n_entrees)

        # Initialiser et entraîner le réseau
        reseau = ReseauNeuronal(n_entrees, architecture, 1)
        pertes_train, pertes_val = reseau.entrainer(entrees_apprentissage, sorties_apprentissage,
                                                    entrees_validation, sorties_validation,
                                                    epochs, taux_apprentissage, reg_l2, self.text_output)

        # Créer les graphiques
        fig = plt.Figure(figsize=(10, 8))
        fig.subplots_adjust(hspace=0.4, wspace=0.3)

        # Graphique des pertes
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.plot(pertes_train, label="Perte entraînement")
        ax1.plot(pertes_val, label="Perte validation")
        ax1.set_xlabel("Époque")
        ax1.set_ylabel("Perte")
        ax1.set_title(f"Perte pour A = {parametre_A}")
        ax1.legend()
        ax1.grid(True)

        # Prédictions à un pas
        nb_tests = 10
        entrees_test, valeurs_reelles_test = preparer_donnees(serie_logistique[:nb_tests+n_entrees], n_entrees)
        predictions_test = reseau.prediction(entrees_test)

        self.text_output.insert(tk.END, f"\nPrédictions à un pas pour A = {parametre_A}:\n")
        erreurs = np.abs(predictions_test - valeurs_reelles_test)
        for i in range(nb_tests):
            self.text_output.insert(tk.END, f"Pas {i+1}: Attendu = {valeurs_reelles_test[i,0]:.8f}, "
                                            f"Prévu = {predictions_test[i,0]:.8f}, Erreur = {erreurs[i,0]:.8f}\n")
        self.text_output.see(tk.END)

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(range(1, nb_tests+1), valeurs_reelles_test, 'bo-', label="Attendu")
        ax2.plot(range(1, nb_tests+1), predictions_test, 'r*-', label="Prévu")
        ax2.set_xlabel("Indice")
        ax2.set_ylabel("Valeur")
        ax2.set_title(f"Prédiction à un pas pour A = {parametre_A}")
        ax2.legend()
        ax2.grid(True)
        ax2.set_ylim(0, 1)
        ax2.set_yticks(np.arange(0, 1.1, 0.1))
        ax2.set_xticks(np.arange(1, 11, 1))

        # Prédictions multi-pas
        indice_depart = 100
        valeur_initiale_prediction = serie_logistique[indice_depart]
        liste_pas = [3, 10]

        for i, nb_pas in enumerate(liste_pas):
            serie_predite = prediction_multi_pas(reseau, valeur_initiale_prediction, nb_pas, n_entrees)
            serie_reelle = generer_serie_multi_pas(parametre_A, valeur_initiale_prediction, nb_pas)

            self.text_output.insert(tk.END, f"\nPrédictions à {nb_pas} pas pour A = {parametre_A}:\n")
            erreurs = np.abs(serie_predite - serie_reelle)
            for j in range(nb_pas + 1):
                self.text_output.insert(tk.END, f"Pas {j}: Attendu = {serie_reelle[j]:.8f}, "
                                                f"Prévu = {serie_predite[j]:.8f}, Erreur = {erreurs[j]:.8f}\n")
            self.text_output.see(tk.END)

            ax = fig.add_subplot(2, 2, i+3)
            ax.plot(range(nb_pas+1), serie_reelle, 'bo-', label="Attendu")
            ax.plot(range(nb_pas+1), serie_predite, 'r*-', label="Prévu")
            ax.set_xlabel("Pas")
            ax.set_ylabel("Valeur")
            ax.set_title(f"Prédiction à {nb_pas} pas pour A = {parametre_A}")
            ax.legend()
            ax.grid(True)
            ax.set_ylim(0, 1)
            ax.set_yticks(np.arange(0, 1.1, 0.1))
            ax.set_xticks(np.arange(0, nb_pas+1, 1))

        # Supprimer l'ancien canvas s'il existe
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        # Afficher les graphiques dans Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- 7. Lancer l'application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()