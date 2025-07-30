import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def salva_excel():
    testo = text_area.get("1.0", tk.END).strip()
    if not testo:
        messagebox.showwarning("Attenzione", "Il campo di testo è vuoto.")
        return

    righe = testo.split("\n")
    intestazioni = righe[0].split("\t")
    dati = [riga.split("\t") for riga in righe[1:] if riga.strip()]

    try:
        df = pd.DataFrame(dati, columns=intestazioni)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella creazione del file:\n{e}")
        return

    percorso_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("File Excel", "*.xlsx")])
    if percorso_file:
        df.to_excel(percorso_file, index=False)
        messagebox.showinfo("Successo", f"File salvato:\n{percorso_file}")
    else:
        messagebox.showinfo("Annullato", "Salvataggio annullato.")

# Interfaccia grafica
finestra = tk.Tk()
finestra.title("Converti Tabella Testo in Excel")
finestra.geometry("900x600")

istruzioni = tk.Label(finestra, text="📋 Incolla qui sotto la tabella con colonne separate da TAB (⇥):", font=("Arial", 12))
istruzioni.pack(pady=10)

text_area = tk.Text(finestra, wrap="none", font=("Courier New", 10))
text_area.pack(expand=True, fill="both", padx=10)

scroll_y = tk.Scrollbar(text_area, orient="vertical", command=text_area.yview)
text_area.config(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")

bottone = tk.Button(finestra, text="💾 Salva come Excel", command=salva_excel, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
bottone.pack(pady=10)

finestra.mainloop()
