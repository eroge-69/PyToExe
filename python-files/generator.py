import tkinter as tk
import random

# ===========================
# TU WPISUJESZ SWOJE POMYSŁY
# oddzielaj przecinkami albo myślnikami
pomysly = [
    "Scena z dowolnego filmu",
    "Scena z dowolnej gry",
    "Wybrany pojazd",
    "Stanowisko komputerowe",
    "Warsztat samochodowy",
    "Domek w lesie",
    "garaż samochodowy",
    "oczko wodne",
    "plac zabaw",
    "basen",
    "wiata samochodowa",
    "domek letniskowy",
    
]
# ===========================

def losuj_pomysl():
    """Losuje pomysł z listy i wyświetla go w etykiecie."""
    if pomysly:
        pomysl = random.choice(pomysly)
        wynik_label.config(text=pomysl)
    else:
        wynik_label.config(text="Brak pomysłów na liście!")

# Tworzenie okna
root = tk.Tk()
root.title("Generator pomysłów 3D")
root.geometry("400x200")

# Tekst powitalny
intro_label = tk.Label(root, text="Kliknij 'Odśwież' aby wylosować pomysł:", font=("Arial", 12))
intro_label.pack(pady=10)

# Wynik (losowany pomysł)
wynik_label = tk.Label(root, text="", font=("Arial", 14), wraplength=350, justify="center")
wynik_label.pack(pady=20)

# Przycisk do odświeżania
losuj_button = tk.Button(root, text="Odśwież", command=losuj_pomysl, font=("Arial", 12))
losuj_button.pack(pady=10)

# Uruchomienie aplikacji
root.mainloop()
