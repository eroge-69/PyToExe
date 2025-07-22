
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import os
import pandas as pd

# Fișier Excel în care salvăm cererile
excel_file = "cereri_concedii.xlsx"

# Inițializare angajați și drepturi concediu (poți extinde după nevoie)
angajati = {
    1: "Ana Popescu",
    2: "Dan Ionescu"
}

drepturi_concediu = {
    (1, 2022): 21,
    (1, 2023): 21,
    (1, 2024): 23,
    (2, 2023): 21,
    (2, 2024): 21
}

# Încărcăm cererile existente dacă fișierul există
if os.path.exists(excel_file):
    df_cereri = pd.read_excel(excel_file)
    cereri_concediu = df_cereri.to_dict("records")
else:
    cereri_concediu = []

def calculeaza_zile(start_str, end_str):
    fmt = "%Y-%m-%d"
    try:
        start = datetime.datetime.strptime(start_str, fmt)
        end = datetime.datetime.strptime(end_str, fmt)
        return (end - start).days + 1
    except ValueError:
        return None

def salveaza_cerere():
    try:
        nume = combo_angajat.get()
        id_ang = next(k for k, v in angajati.items() if v == nume)
        an = int(entry_an.get())
        start = entry_start.get()
        end = entry_end.get()
        tip = combo_tip.get()

        zile = calculeaza_zile(start, end)
        if zile is None or zile <= 0:
            raise ValueError("Date invalide.")

        cerere = {
            "ID angajat": id_ang,
            "Nume": nume,
            "An": an,
            "Data început": start,
            "Data sfârșit": end,
            "Nr. zile": zile,
            "Tip concediu": tip
        }
        cereri_concediu.append(cerere)

        # Salvăm în Excel
        df_save = pd.DataFrame(cereri_concediu)
        df_save.to_excel(excel_file, index=False)

        # Recalculăm situația
        efectuate = sum(c["Nr. zile"] for c in cereri_concediu if c["ID angajat"] == id_ang and c["An"] == an and c["Tip concediu"] == "Odihnă")
        drept = drepturi_concediu.get((id_ang, an), 0)
        ramas = drept - efectuate

        lbl_rezultat["text"] = f"{nume} - An {an}:\nDrept: {drept} zile, Efectuate: {efectuate} zile, Rămase: {ramas} zile"
    except Exception as e:
        messagebox.showerror("Eroare", str(e))

# Interfață grafică
root = tk.Tk()
root.title("Evidență concedii")

tk.Label(root, text="Angajat:").grid(row=0, column=0, sticky="e")
combo_angajat = ttk.Combobox(root, values=list(angajati.values()), state="readonly")
combo_angajat.grid(row=0, column=1)

tk.Label(root, text="An:").grid(row=1, column=0, sticky="e")
entry_an = tk.Entry(root)
entry_an.grid(row=1, column=1)

tk.Label(root, text="Data început (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
entry_start = tk.Entry(root)
entry_start.grid(row=2, column=1)

tk.Label(root, text="Data sfârșit (YYYY-MM-DD):").grid(row=3, column=0, sticky="e")
entry_end = tk.Entry(root)
entry_end.grid(row=3, column=1)

tk.Label(root, text="Tip concediu:").grid(row=4, column=0, sticky="e")
combo_tip = ttk.Combobox(root, values=["Odihnă", "Fără plată", "Medical"], state="readonly")
combo_tip.grid(row=4, column=1)

btn_salvare = tk.Button(root, text="Adaugă concediu", command=salveaza_cerere)
btn_salvare.grid(row=5, column=0, columnspan=2, pady=10)

lbl_rezultat = tk.Label(root, text="", fg="green", justify="left")
lbl_rezultat.grid(row=6, column=0, columnspan=2)

root.mainloop()
