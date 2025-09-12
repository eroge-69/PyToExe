import random
import string
import pyperclip
import keyboard

def generer_mot(longueur=8):
    """Génère un mot aléatoire de 'longueur' lettres."""
    lettres = string.ascii_lowercase
    return ''.join(random.choice(lettres) for _ in range(longueur))

def action():
    mot = generer_mot()
    pyperclip.copy(mot)
    print(f"Mot généré et copié : {mot}")

print("Appuie sur CTRL droit + SHIFT droit pour générer un mot... (Ctrl+C pour quitter)")

# Déclenche l'action à la combinaison voulue
keyboard.add_hotkey('right ctrl+right shift', action)

# Boucle infinie pour garder le programme actif
keyboard.wait()
