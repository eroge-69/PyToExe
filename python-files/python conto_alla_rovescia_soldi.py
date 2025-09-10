import tkinter as tk
from tkinter import messagebox
import json
import os

# File per salvare i dati
SAVE_FILE = "soldi.json"

# Obiettivo
OBIETTIVO = 3000

# Carica il valore salvato
def carica_valore():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f).get("attuale", 2225)
    return 2225

# Salva il valore
def salva_valore():
    with open(SAVE_FILE, "w") as f:
        json.dump({"attuale": attuale}, f)

# Aggiungi soldi
def aggiungi(valore=None):
    global attuale
    try:
        if valore is None:  # input manuale
            valore = int(entry.get())
        if valore < 1 or valore > 1000:
            messagebox.showerror("Errore", "Puoi aggiungere solo da 1 a 1000 €")
            return
        attuale += valore
        if attuale >= OBIETTIVO:
            attuale = OBIETTIVO
            label_var.set(f"Hai raggiunto i {OBIETTIVO} € 🎉")
            messagebox.showinfo("Complimenti!", f"Hai raggiunto i {OBIETTIVO} €! 🎉")
            btn_add.config(state="disabled")
            for b in quick_buttons:
                b.config(state="disabled")
        else:
            manca = OBIETTIVO - attuale
            label_var.set(f"Hai {attuale} € 😁 → Mancano {manca} €")
        salva_valore()
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero valido")

# Reset
def reset():
    global attuale
    if messagebox.askyesno("Reset", "Vuoi davvero resettare a 2225 €?"):
        attuale = 2225
        label_var.set(f"Hai {attuale} € 😁 → Mancano {OBIETTIVO - attuale} €")
        btn_add.config(state="normal")
        for b in quick_buttons:
            b.config(state="normal")
        salva_valore()

# Inizializza valore attuale
attuale = carica_valore()

# GUI
root = tk.Tk()
root.title("💶 Conto alla rovescia soldi")
root.geometry("420x350")
root.configure(bg="#f0f8ff")

label_var = tk.StringVar()
label_var.set(f"Hai {attuale} € 😁 → Mancano {OBIETTIVO - attuale} €")

label = tk.Label(root, textvariable=label_var, font=("Arial", 16, "bold"), bg="#f0f8ff")
label.pack(pady=15)

entry = tk.Entry(root, font=("Arial", 14), justify="center")
entry.pack(pady=5)

btn_add = tk.Button(root, text="Aggiungi", font=("Arial", 14, "bold"),
                    bg="#90ee90", fg="black", relief="groove",
                    command=lambda: aggiungi(None))
btn_add.pack(pady=10)

frame = tk.Frame(root, bg="#f0f8ff")
frame.pack(pady=10)

quick_buttons = []
for val in [50, 100, 200, 500]:
    b = tk.Button(frame, text=f"+{val} €", font=("Arial", 12, "bold"),
                  bg="#add8e6", fg="black", relief="ridge",
                  width=8, command=lambda v=val: aggiungi(v))
    b.pack(side="left", padx=5)
    quick_buttons.append(b)

btn_reset = tk.Button(root, text="🔄 Reset", font=("Arial", 12),
                      bg="#ffcccb", command=reset)
btn_reset.pack(pady=15)

root.mainloop()
