import tkinter as tk
from tkinter import messagebox

def vypocet():
    try:
        # Načtení hodnot (s automatickým mazáním starého výsledku)
        values = [entry_C1.get(), entry_V1.get(), entry_C2.get(), entry_V2.get()]
        entries = [entry_C1, entry_V1, entry_C2, entry_V2]

        # Převod na čísla nebo None
        vals = [float(v) if v != "" else None for v in values]

        C1, V1, C2, V2 = vals

        # Počítání podle chybějící hodnoty
        if C1 is None:
            C1 = (C2 * V2) / V1
            entries[0].delete(0, tk.END)
            entries[0].insert(0, round(C1, 4))
        elif V1 is None:
            V1 = (C2 * V2) / C1
            entries[1].delete(0, tk.END)
            entries[1].insert(0, round(V1, 4))
        elif C2 is None:
            C2 = (C1 * V1) / V2
            entries[2].delete(0, tk.END)
            entries[2].insert(0, round(C2, 4))
        elif V2 is None:
            V2 = (C1 * V1) / C2
            entries[3].delete(0, tk.END)
            entries[3].insert(0, round(V2, 4))
        else:
            messagebox.showerror("Chyba", "Musí být prázdná právě jedna hodnota.")

    except (ValueError, TypeError):
        messagebox.showerror("Chyba", "Zadej čísla nebo nech jedno pole prázdné.")

# Hlavní okno
root = tk.Tk()
root.title("Zřeďovací rovnice – C1·V1 = C2·V2")
root.geometry("350x220")
root.configure(bg="#f5f5f5")

# Styl popisků
label_style = {"bg": "#f5f5f5", "fg": "#333", "font": ("Arial", 11)}

# Popisky a vstupy
tk.Label(root, text="C1 (původní koncentrace)", **label_style).grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_C1 = tk.Entry(root, font=("Arial", 11))
entry_C1.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="V1 (původní objem)", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_V1 = tk.Entry(root, font=("Arial", 11))
entry_V1.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="C2 (cílová koncentrace)", **label_style).grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_C2 = tk.Entry(root, font=("Arial", 11))
entry_C2.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="V2 (cílový objem)", **label_style).grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_V2 = tk.Entry(root, font=("Arial", 11))
entry_V2.grid(row=3, column=1, padx=5, pady=5)

# Tlačítko výpočtu
btn = tk.Button(root, text="💧 Spočítat", command=vypocet, bg="#4CAF50", fg="white", font=("Arial", 11), relief="flat")
btn.grid(row=4, column=0, columnspan=2, pady=15, ipadx=10, ipady=5)

root.mainloop()
