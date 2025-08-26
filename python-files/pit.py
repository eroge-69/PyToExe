import tkinter as tk
from tkinter import messagebox

def saluta():
    nome = entry_nome.get()
    if nome.strip():
        messagebox.showinfo("Saluto", f"Ciao, {nome}! Benvenuto nel mondo degli EXE con GUI.")
    else:
        messagebox.showwarning("Attenzione", "Per favore inserisci un nome.")

# Crea la finestra principale
root = tk.Tk()
root.title("Saluto GUI")
root.geometry("300x150")

# Label
label = tk.Label(root, text="Inserisci il tuo nome:")
label.pack(pady=10)

# Entry (campo testo)
entry_nome = tk.Entry(root)
entry_nome.pack(pady=5)

# Bottone
bottone = tk.Button(root, text="Saluta", command=saluta)
bottone.pack(pady=10)

# Avvia la GUI
root.mainloop()
