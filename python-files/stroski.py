import os
from datetime import date
import calendar
import tkinter as tk
from tkinter import messagebox

# Nastavitve
trenutni_mesec = date.today().strftime("%Y-%m")
datoteka = f"stroski_{trenutni_mesec}.txt"

dohodek = 0
stroški = []

def nalozi_podatke():
    global dohodek, stroški
    if os.path.exists(datoteka):
        with open(datoteka, "r", encoding="utf-8") as f:
            vrstice = f.readlines()
            if vrstice:
                dohodek = float(vrstice[0].strip())
                for vrstica in vrstice[1:]:
                    opis, znesek = vrstica.strip().split(" | ")
                    stroški.append((opis, float(znesek)))

def shrani_podatke():
    with open(datoteka, "w", encoding="utf-8") as f:
        f.write(f"{dohodek}\n")
        for opis, znesek in stroški:
            f.write(f"{opis} | {znesek}\n")

def dodaj_dohodek_gui():
    global dohodek
    try:
        znesek = float(entry_dohodek.get())
        dohodek += znesek
        entry_dohodek.delete(0, tk.END)
        shrani_podatke()
        osvezi_pregled()
    except ValueError:
        messagebox.showerror("Napaka", "Vnesi veljaven znesek.")

def dodaj_strosek_gui():
    try:
        opis = entry_opis.get()
        znesek = float(entry_strosek.get())
        stroški.append((opis, znesek))
        entry_opis.delete(0, tk.END)
        entry_strosek.delete(0, tk.END)
        shrani_podatke()
        osvezi_pregled()
    except ValueError:
        messagebox.showerror("Napaka", "Vnesi veljaven opis in znesek.")

def izracun_dnevno(stanje):
    danes = date.today()
    dni_v_mesecu = calendar.monthrange(danes.year, danes.month)[1]
    ostanek_dni = dni_v_mesecu - danes.day + 1
    return stanje / ostanek_dni if ostanek_dni > 0 else 0

def osvezi_pregled():
    skupaj_stroški = sum(z for _, z in stroški)
    stanje = dohodek - skupaj_stroški
    dnevno = izracun_dnevno(stanje)

    pregled_text = f"""
📅 Mesec: {trenutni_mesec}
-----------------------------
Dohodek: {dohodek:.2f} €
Stroški: {skupaj_stroški:.2f} €
Ostanek: {stanje:.2f} €
Dnevno (do konca meseca): {dnevno:.2f} €
-----------------------------
🧾 Stroški:
"""
    for opis, znesek in stroški:
        pregled_text += f" - {opis}: {znesek:.2f} €\n"

    pregled_box.config(state="normal")
    pregled_box.delete(1.0, tk.END)
    pregled_box.insert(tk.END, pregled_text.strip())
    pregled_box.config(state="disabled")

# --- GUI ---
nalozi_podatke()

okno = tk.Tk()
okno.title("Dnevnik stroškov")

# Vnos dohodka
tk.Label(okno, text="Dohodek (€):").grid(row=0, column=0, sticky="w")
entry_dohodek = tk.Entry(okno)
entry_dohodek.grid(row=0, column=1)
tk.Button(okno, text="Dodaj dohodek", command=dodaj_dohodek_gui).grid(row=0, column=2)

# Vnos stroška
tk.Label(okno, text="Opis stroška:").grid(row=1, column=0, sticky="w")
entry_opis = tk.Entry(okno)
entry_opis.grid(row=1, column=1)

tk.Label(okno, text="Znesek (€):").grid(row=2, column=0, sticky="w")
entry_strosek = tk.Entry(okno)
entry_strosek.grid(row=2, column=1)

tk.Button(okno, text="Dodaj strošek", command=dodaj_strosek_gui).grid(row=2, column=2)

# Pregled
pregled_box = tk.Text(okno, height=15, width=60)
pregled_box.grid(row=3, column=0, columnspan=3, pady=10)
pregled_box.config(state="disabled")

# Osveži prikaz
osvezi_pregled()
okno.mainloop()
