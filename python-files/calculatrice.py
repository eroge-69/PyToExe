import tkinter as tk
from tkinter import font
import math

# Fonction pour mettre à jour l'affichage de la calculatrice
def bouton_click(chiffre):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + str(chiffre))

# Fonction pour supprimer le dernier caractère
def bouton_effacer():
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current[:-1])

# Fonction pour calculer l'expression
def calculer():
    try:
        expression = entry.get()
        expression = expression.replace('÷', '/').replace('x', '*').replace(',', '.').replace('C', 'Retour arrière')  # Remplacer ÷ par /, x par *, , par .
        result = eval(expression)
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
        animate_result()
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Errooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooor")

# Fonction pour réinitialiser l'affichage
def reset():
    entry.delete(0, tk.END)

# Fonction pour calculer la racine carrée
def racine_carre():
    try:
        current = float(entry.get())
        result = math.sqrt(current)
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
        animate_result()
    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Erroooooooooooooooooooooooooooooooooooor")

# Fonction pour calculer la puissance
def puissance():
    try:
        current = float(entry.get())
        result = current ** 2  # Exemple de carré
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
        animate_result()
    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Errooooooooooooooooooooooooooooor")

# Fonction pour calculer log ou sin
def log_sin(func):
    try:
        current = float(entry.get())
        if func == "log":
            result = math.log10(current)
        elif func == "sin":
            result = math.sin(math.radians(current))  # Calcul en radians
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
        animate_result()
    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Erroooooooooooooooooor")

# Fonction pour basculer entre le thème sombre et clair
def toggle_theme():
    if fenetre.option_get('theme', 'dark') == 'dark':
        fenetre.tk_setPalette(background='#FFFFFF', foreground='#000000')
        entry.config(bg='#FFFFFF', fg='#000000')
        for widget in fenetre.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg='#DDDDDD', fg='#000000')
        fenetre.option_add('*TButton*highlightBackground', 'gray')
        fenetre.option_add('*TButton*highlightColor', 'gray')
        fenetre.option_add('theme', 'light')
    else:
        fenetre.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
        entry.config(bg='#333333', fg='#FFFFFF')
        for widget in fenetre.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg='#333333', fg='#FFFFFF')
        fenetre.option_add('*TButton*highlightBackground', 'darkgray')
        fenetre.option_add('*TButton*highlightColor', 'darkgray')
        fenetre.option_add('theme', 'dark')

# Animation de l'affichage du résultat
def animate_result():
    entry.config(bg="#FFD700")  # Changer la couleur de fond du champ de saisie
    fenetre.after(300, lambda: entry.config(bg="#333333"))  # Rétablir la couleur après 300ms

# Fonction pour ajouter un beep au clic
def beep():
    fenetre.bell()

# Initialisation de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Calculatrice")
fenetre.configure(bg="#2E2E2E")
fenetre.option_add('theme', 'dark')

# Passer en mode plein écran
fenetre.attributes("-fullscreen", True)

# Variables pour la police
font_bouton = font.Font(family="Helvetica", size=24, weight="bold")
font_entry = font.Font(family="Helvetica", size=32, weight="bold")

# Champ de saisie pour l'expression
entry = tk.Entry(fenetre, font=font_entry, borderwidth=2, relief="solid", justify="right", bg="#333333", fg="#FFFFFF")
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=20, sticky="nsew")

# Définir les boutons avec les nouvelles positions
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('÷', 1, 3),  # Changer / en ÷
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('x', 2, 3),   # Changer * en x
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 1), (',', 4, 2), ('+', 4, 3),  # Remplacer . par ,
    ('(', 5, 1), (')', 5, 2),
    ('log', 5, 0),
    ('sin', 4, 0),
    ('Effacer', 6, 0), ('Retour arrière', 6, 1),('=', 6, 2)
]

# Configurer la grille pour qu'elle soit dynamique
for i in range(7):  # 7 lignes
    fenetre.grid_rowconfigure(i, weight=1, uniform="equal")
for j in range(5):  # 5 colonnes
    fenetre.grid_columnconfigure(j, weight=1, uniform="equal")

# Création des boutons et liaison avec les fonctions
for (texte, ligne, col) in buttons:
    if texte == "=":
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=lambda: [calculer(), beep()], bg="#4CAF50", fg="#FFFFFF", relief="solid")
    elif texte == "Retour arrière":
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=bouton_effacer, bg="#FFA500", fg="#FFFFFF", relief="solid")
    elif texte == "Effacer":
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=reset, bg="#FF6347", fg="#FFFFFF", relief="solid")
    elif texte == "log" or texte == "sin":
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=lambda t=texte: log_sin(t), bg="#333333", fg="#FFFFFF", relief="solid")
    elif texte == "(" or texte == ")":
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=lambda t=texte: bouton_click(t), bg="#333333", fg="#FFFFFF", relief="solid")
    else:
        bouton = tk.Button(fenetre, text=texte, font=font_bouton, command=lambda t=texte: bouton_click(t), bg="#333333", fg="#FFFFFF", relief="solid")
    
    bouton.grid(row=ligne, column=col, padx=10, pady=10, sticky="nsew")
    
# Lancer l'interface
fenetre.mainloop()
