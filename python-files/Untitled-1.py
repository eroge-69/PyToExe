import tkinter as tk
from tkinter import messagebox

# Fonction d'évaluation pour chaque critère
def evaluer_idee(idee):
    def evaluer_faisabilite(idee):
        if "facile" in idee or "simple" in idee:
            return 8
        elif "complexe" in idee or "difficile" in idee:
            return 4
        return 6

    def evaluer_creativite(idee):
        if "nouveau" in idee or "unique" in idee or "innovant" in idee:
            return 8
        elif "copier" in idee or "répéter" in idee:
            return 3
        return 6

    def evaluer_impact_social(idee):
        if "aider" in idee or "social" in idee or "bénéfice" in idee:
            return 9
        elif "personnel" in idee or "égoïste" in idee:
            return 3
        return 5

    def evaluer_durabilite(idee):
        if "écologique" in idee or "durable" in idee or "vert" in idee:
            return 8
        elif "pollution" in idee or "non durable" in idee:
            return 2
        return 5

    # Calcul des scores pour chaque critère
    score_faisabilite = evaluer_faisabilite(idee)
    score_creativite = evaluer_creativite(idee)
    score_impact = evaluer_impact_social(idee)
    score_durabilite = evaluer_durabilite(idee)

    # Moyenne des scores
    score_final = (score_faisabilite + score_creativite + score_impact + score_durabilite) / 4

    # Définir le verdict
    if score_final >= 7:
        verdict = "Bien ! C'est une excellente idée."
    elif score_final >= 5:
        verdict = "Correct. L'idée a du potentiel, mais il y a des points à améliorer."
    else:
        verdict = "Pas bien... Il y a plusieurs aspects à revoir."

    return verdict

# Fonction qui sera appelée quand l'utilisateur clique sur "Évaluer l'idée"
def evaluer_idee_ui():
    idee_input = entry_idee.get()  # Récupère l'idée entrée par l'utilisateur
    if idee_input.strip() == "":
        messagebox.showwarning("Alerte", "Veuillez entrer une idée.")
        return
    verdict = evaluer_idee(idee_input)
    messagebox.showinfo("Évaluation de l'idée", verdict)

# Fonction pour quitter l'application
def quitter_application():
    root.quit()

# Création de la fenêtre principale
root = tk.Tk()
root.title("Évaluation d'idées")

# Création de l'interface
label_instruction = tk.Label(root, text="Entrez votre idée pour l'évaluer :")
label_instruction.pack(pady=10)

entry_idee = tk.Entry(root, width=50)
entry_idee.pack(pady=5)

button_evaluer = tk.Button(root, text="Évaluer l'idée", command=evaluer_idee_ui)
button_evaluer.pack(pady=10)

button_quitter = tk.Button(root, text="Quitter", command=quitter_application)
button_quitter.pack(pady=5)

# Lancer la fenêtre principale
root.mainloop()
