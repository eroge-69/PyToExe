import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
import tkinter as tk
from tkinter import messagebox
import seaborn as sns
import matplotlib.pyplot as plt

# Charger les données Excel (le fichier doit être dans le même dossier que ce script)
df = pd.read_excel("Classeur1.xlsx")

# Nettoyage et sélection des colonnes utiles
colonnes = ['PIB par habitant ($US)', 'Croissance (%)', 'Espérance de vie', 'Groupe de revenu']
df_clean = df[colonnes].copy()
df_clean.dropna(inplace=True)

# Encodage de la variable cible
encoder = LabelEncoder()
df_clean['Groupe de revenu'] = encoder.fit_transform(df_clean['Groupe de revenu'])

# Afficher la correspondance entre classes
classes = encoder.classes_
print("\nCorrespondance des classes :")
for i, label in enumerate(classes):
    print(f"Classe {i} → {label}")

# Séparation des données
X = df_clean.drop('Groupe de revenu', axis=1)
y = df_clean['Groupe de revenu']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Entraînement du modèle k-NN pondéré
model_weighted = KNeighborsClassifier(n_neighbors=5, weights='distance')
model_weighted.fit(X_train, y_train)

# Interface graphique avec tkinter
def predire_groupe():
    try:
        pib = float(entry_pib.get())
        croissance = float(entry_croissance.get())
        esperance = float(entry_esperance.get())

        entree = [[pib, croissance, esperance]]
        prediction = model_weighted.predict(entree)[0]
        label = classes[prediction]

        messagebox.showinfo("Résultat", f"Groupe de revenu prédit : {label}")

    except Exception as e:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.")

fenetre = tk.Tk()
fenetre.title("Prédiction du Groupe de Revenu")
fenetre.geometry("400x300")

tk.Label(fenetre, text="Saisir les données économiques :", font=("Arial", 14)).pack(pady=10)

tk.Label(fenetre, text="PIB par habitant ($US)").pack()
entry_pib = tk.Entry(fenetre)
entry_pib.pack()

tk.Label(fenetre, text="Croissance (%)").pack()
entry_croissance = tk.Entry(fenetre)
entry_croissance.pack()

tk.Label(fenetre, text="Espérance de vie").pack()
entry_esperance = tk.Entry(fenetre)
entry_esperance.pack()

tk.Button(fenetre, text="Prédire", command=predire_groupe, bg="lightblue").pack(pady=20)

fenetre.mainloop()
