import tkinter as tk

def check_password():
    if entry.get().lower() == "love":
        label.config(text="💖 Ce n’était qu’une blague... Je t’aime 💖", fg="lightgreen")
        root.after(3000, root.destroy)
    else:
        label.config(text="❌ Mauvais mot de passe. Tu es à moi maintenant...")

def flash_colors():
    current = root.cget("bg")
    next_color = "black" if current == "red" else "red"
    root.configure(bg=next_color)
    root.after(500, flash_colors)

# Création de la fenêtre principale
root = tk.Tk()
root.title("System Breach")
root.attributes("-fullscreen", True)  # Plein écran
root.configure(bg="red")

# Texte principal
label = tk.Label(
    root,
    text="💀 SYSTEM HACKED 💀\n\nEntre le code secret pour sortir...",
    font=("Courier", 28),
    fg="white",
    bg="red"
)
label.pack(pady=100)

# Zone de saisie
entry = tk.Entry(root, font=("Courier", 24), show="*")
entry.pack()
entry.focus()

# Bouton de validation
btn = tk.Button(root, text="Valider", font=("Courier", 20), command=check_password)
btn.pack(pady=20)

# Empêche de quitter avec Alt+F4
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Démarre le clignotement
flash_colors()

# Boucle principale
root.mainloop()
