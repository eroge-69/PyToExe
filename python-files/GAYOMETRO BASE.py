import tkinter as tk
from tkinter import messagebox
import os

# Percorso della cartella sul desktop
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
folder_path = os.path.join(desktop_path, 'gestore clienti')
file_path = os.path.join(folder_path, 'clienti.txt')

os.makedirs(folder_path, exist_ok=True)

# Funzione per caricare i dati nel riquadro
def carica_dati():
    text_display.delete("1.0", tk.END)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                text_display.insert(tk.END, f"{i}. {line}")

# Salva nuovo dato
def salva_dati():
    nome = entry_nome.get()
    kg_miele = entry_miele.get()
    if nome and kg_miele.replace(".", "", 1).isdigit():
        dato = f"{nome} - {kg_miele} kg di miele"
        with open(file_path, 'a') as f:
            f.write(dato + '\n')
        entry_nome.delete(0, tk.END)
        entry_miele.delete(0, tk.END)
        carica_dati()
    else:
        messagebox.showerror("Errore", "Inserisci un nome e i kg di miele (numero valido).")

# Cancella una voce selezionata da input
def cancella_dato():
    numero_voce = entry_seleziona.get()
    if numero_voce.isdigit():
        numero_voce = int(numero_voce)
        with open(file_path, 'r') as f:
            righe = f.readlines()
        if 0 < numero_voce <= len(righe):
            del righe[numero_voce - 1]
            with open(file_path, 'w') as f:
                f.writelines(righe)
            carica_dati()
            entry_seleziona.delete(0, tk.END)
        else:
            messagebox.showerror("Errore", "Numero non valido.")
    else:
        messagebox.showerror("Errore", "Inserisci un numero di voce valido.")

# GUI
root = tk.Tk()
root.title("Gestore Clienti")

tk.Label(root, text="Nome:").grid(row=0, column=0)
entry_nome = tk.Entry(root, width=30)
entry_nome.grid(row=0, column=1)

tk.Label(root, text="Kg di miele:").grid(row=0, column=2)
entry_miele = tk.Entry(root, width=10)
entry_miele.grid(row=0, column=3)

btn_salva = tk.Button(root, text="Salva", command=salva_dati)
btn_salva.grid(row=1, column=0, columnspan=2)

btn_mostra = tk.Button(root, text="Aggiorna Lista", command=carica_dati)
btn_mostra.grid(row=1, column=2, columnspan=2)

text_display = tk.Text(root, height=10, width=60)
text_display.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

tk.Label(root, text="Voce da cancellare (n°):").grid(row=3, column=0)
entry_seleziona = tk.Entry(root, width=5)
entry_seleziona.grid(row=3, column=1)
btn_cancella = tk.Button(root, text="Cancella", command=cancella_dato)
btn_cancella.grid(row=3, column=2)

carica_dati()
root.mainloop()
