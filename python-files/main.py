import tkinter as tk
from tkinter import messagebox

def decimal_u_oktalni():
    try:
        decimalni_broj = int(entry.get())
        oktalni_broj = oct(decimalni_broj)[2:]  # uklanja '0o' prefix
        rezultat_label.config(text=f"Oktalni broj: {oktalni_broj}")
    except ValueError:
        messagebox.showerror("Greška", "Molim te unesi validan ceo broj.")

# Glavni prozor
prozor = tk.Tk()
prozor.title("Decimalni u Oktalni konverter")
prozor.geometry("300x150")

# Labela za instrukciju
instrukcija = tk.Label(prozor, text="Unesi decimalni broj:")
instrukcija.pack(pady=5)

# Polje za unos decimalnog broja
entry = tk.Entry(prozor, width=30)
entry.pack(pady=5)

# Dugme za konverziju
dugme = tk.Button(prozor, text="Pretvori u oktalni", command=decimal_u_oktalni)
dugme.pack(pady=5)

# Labela za prikaz rezultata
rezultat_label = tk.Label(prozor, text="")
rezultat_label.pack(pady=5)

# Pokretanje GUI aplikacije
prozor.mainloop()
