import tkinter as tk
from tkinter import ttk

# Dimensiuni camion (cm)
LUNGIME_CAMION = 1300
LATIME_CAMION = 245
INALTIME_CAMION = 270

# Dimensiuni panou (cm)
LUNGIME_PANOU = 250
LATIME_PANOU = 100
GROSIMI_PANOURI_CM = [4, 5, 6, 8, 10, 12, 15, 16, 20]  # cm

# Calcul panouri
def calculeaza_panouri():
    rezultate = []
    panouri_pe_lungime = LUNGIME_CAMION // LUNGIME_PANOU
    panouri_pe_latime = LATIME_CAMION // LATIME_PANOU
    pozitii_baza = panouri_pe_lungime * panouri_pe_latime

    for grosime in GROSIMI_PANOURI_CM:
        panouri_pe_inaltime = INALTIME_CAMION // grosime
        total = pozitii_baza * panouri_pe_inaltime
        rezultate.append((f"{grosime} cm", total))
    return rezultate

# Interfață grafică simplă
def ruleaza_aplicatia():
    rezultate = calculeaza_panouri()

    root = tk.Tk()
    root.title("Calculator Încărcare Panouri în Camion")

    label = tk.Label(root, text="Rezultat încărcare panouri:", font=("Arial", 14))
    label.pack(pady=10)

    tree = ttk.Treeview(root, columns=("Grosime", "Nr. Panouri"), show='headings')
    tree.heading("Grosime", text="Grosime Panou")
    tree.heading("Nr. Panouri", text="Număr Panouri")
    for grosime, total in rezultate:
        tree.insert("", tk.END, values=(grosime, total))
    tree.pack(padx=20, pady=10)

    root.mainloop()

# Rulează aplicația
ruleaza_aplicatia()
