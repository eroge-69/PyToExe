
import tkinter as tk
from tkinter import ttk

def calculeaza_pret():
    try:
        lat_ref = float(entry_latime_ref.get())
        lung_ref = float(entry_lungime_ref.get())
        pret_ref = float(entry_pret_ref.get())

        lat_nou = float(entry_latime_nou.get())
        lung_nou = float(entry_lungime_nou.get())

        suprafata_ref = lat_ref * lung_ref
        suprafata_noua = lat_nou * lung_nou

        pret_nou = (suprafata_noua / suprafata_ref) * pret_ref
        entry_pret_nou.config(state='normal')
        entry_pret_nou.delete(0, tk.END)
        entry_pret_nou.insert(0, f"{pret_nou:.2f}")
        entry_pret_nou.config(state='readonly')
    except ValueError:
        entry_pret_nou.config(state='normal')
        entry_pret_nou.delete(0, tk.END)
        entry_pret_nou.insert(0, "Eroare")
        entry_pret_nou.config(state='readonly')

app = tk.Tk()
app.title("Pret Material")
app.geometry("400x200")
app.resizable(False, False)

# Etichete și câmpuri stânga (Referință)
ttk.Label(app, text="Latime (mm)").grid(row=0, column=0)
entry_latime_ref = ttk.Entry(app)
entry_latime_ref.grid(row=1, column=0)

ttk.Label(app, text="Lungime (mm)").grid(row=2, column=0)
entry_lungime_ref = ttk.Entry(app)
entry_lungime_ref.grid(row=3, column=0)

ttk.Label(app, text="Pret total (lei)").grid(row=4, column=0)
entry_pret_ref = ttk.Entry(app)
entry_pret_ref.grid(row=5, column=0)

# Etichete și câmpuri dreapta (Nou)
ttk.Label(app, text="Latime (mm)").grid(row=0, column=1)
entry_latime_nou = ttk.Entry(app)
entry_latime_nou.grid(row=1, column=1)

ttk.Label(app, text="Lungime (mm)").grid(row=2, column=1)
entry_lungime_nou = ttk.Entry(app)
entry_lungime_nou.grid(row=3, column=1)

ttk.Label(app, text="Pret calculat (lei)").grid(row=4, column=1)
entry_pret_nou = ttk.Entry(app, state='readonly')
entry_pret_nou.grid(row=5, column=1)

# Buton pentru calcul
btn_calculeaza = ttk.Button(app, text="Calculeaza", command=calculeaza_pret)
btn_calculeaza.grid(row=6, column=0, columnspan=2, pady=10)

app.mainloop()
