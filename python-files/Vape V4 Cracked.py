import tkinter as tk
from tkinter import messagebox

# Mostra il messaggio 5 volte
for _ in range(5):
    messagebox.showwarning("⚠ Attenzione ⚠", "Il tuo PC è stato infettato hahaha!")

# Finestra finale che si chiude dopo 5 secondi
def chiudi():
    root.destroy()

root = tk.Tk()
root.title("Infezione in corso...")
root.geometry("300x100")
label = tk.Label(root, text="Il virus sta agendo... 😱", font=("Arial", 12))
label.pack(pady=30)

# Chiudi dopo 5 secondi
root.after(5000, chiudi)
root.mainloop()
