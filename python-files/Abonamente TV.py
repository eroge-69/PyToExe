import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta

# ----- Bază de date -----
conn = sqlite3.connect("abonamente_tv.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS clienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT,
    adresa TEXT,
    telefon TEXT,
    data_install TEXT,
    perioada INTEGER,
    pret REAL,
    platit INTEGER
)
''')
conn.commit()

# ----- Funcții -----
def adauga_client():
    try:
        nume = entry_nume.get()
        adresa = entry_adresa.get()
        telefon = entry_telefon.get()
        data_install = entry_data_install.get()
        perioada = int(combo_perioada.get().split()[0])
        pret = float(entry_pret.get())
        platit = var_platit.get()

        datetime.strptime(data_install, "%Y-%m-%d")  # verificare format

        cursor.execute('''
            INSERT INTO clienti (nume, adresa, telefon, data_install, perioada, pret, platit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nume, adresa, telefon, data_install, perioada, pret, platit))
        conn.commit()
        messagebox.showinfo("Succes", "Client adăugat!")
        afiseaza_clienti()
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la adăugare: {e}")

def afiseaza_clienti(filtru=None):
    for row in tree.get_children():
        tree.delete(row)

    if filtru == "platit":
        cursor.execute("SELECT * FROM clienti WHERE platit=1")
    elif filtru == "neplatit":
        cursor.execute("SELECT * FROM clienti WHERE platit=0")
    else:
        cursor.execute("SELECT * FROM clienti")

    for row in cursor.fetchall():
        id_c, nume, adresa, tel, data_inst, perioada, pret, platit = row
        data_exp = datetime.strptime(data_inst, "%Y-%m-%d") + timedelta(days=perioada*30)
        status = "DA" if platit else "NU"
        tree.insert("", "end", values=(nume, tel, data_inst, f"{perioada} luni", pret, status, data_exp.date()))

def verifica_expirari():
    azi = datetime.today()
    reminderi = []
    cursor.execute("SELECT nume, data_install, perioada FROM clienti")
    for nume, data_i, perioada in cursor.fetchall():
        data_exp = datetime.strptime(data_i, "%Y-%m-%d") + timedelta(days=perioada*30)
        if data_exp.date() <= azi.date():
            reminderi.append(f"{nume} - Expirat pe {data_exp.date()}")

    if reminderi:
        messagebox.showwarning("Abonamente expirate", "\n".join(reminderi))
    else:
        messagebox.showinfo("OK", "Niciun abonament expirat azi.")

# ----- Interfață -----
root = tk.Tk()
root.title("CRM - Canale TV Românești")
root.geometry("850x600")

# ----- Formular -----
frame_form = tk.LabelFrame(root, text="Adaugă Client Nou", padx=10, pady=10)
frame_form.pack(fill="x", padx=10, pady=5)

entry_nume = tk.Entry(frame_form, width=40)
entry_adresa = tk.Entry(frame_form, width=40)
entry_telefon = tk.Entry(frame_form, width=40)
entry_data_install = tk.Entry(frame_form, width=40)
combo_perioada = ttk.Combobox(frame_form, values=["3 luni", "6 luni", "12 luni"], width=37)
entry_pret = tk.Entry(frame_form, width=40)
var_platit = tk.IntVar()
check_platit = tk.Checkbutton(frame_form, text="Plătit", variable=var_platit)

tk.Label(frame_form, text="Nume").grid(row=0, column=0, sticky="w")
tk.Label(frame_form, text="Adresă").grid(row=1, column=0, sticky="w")
tk.Label(frame_form, text="Telefon").grid(row=2, column=0, sticky="w")
tk.Label(frame_form, text="Data instalare (YYYY-MM-DD)").grid(row=3, column=0, sticky="w")
tk.Label(frame_form, text="Perioada abonament").grid(row=4, column=0, sticky="w")
tk.Label(frame_form, text="Preț plătit").grid(row=5, column=0, sticky="w")

entry_nume.grid(row=0, column=1)
entry_adresa.grid(row=1, column=1)
entry_telefon.grid(row=2, column=1)
entry_data_install.grid(row=3, column=1)
combo_perioada.grid(row=4, column=1)
entry_pret.grid(row=5, column=1)
check_platit.grid(row=6, column=1, sticky="w")

tk.Button(frame_form, text="Adaugă Client", command=adauga_client).grid(row=7, column=1, pady=10)

# ----- Tabel -----
frame_tabel = tk.LabelFrame(root, text="Lista Clienți")
frame_tabel.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_tabel, columns=("Nume", "Telefon", "Instalare", "Perioadă", "Preț", "Plătit", "Expiră"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill="both", expand=True)

# ----- Butoane filtre -----
frame_btn = tk.Frame(root)
frame_btn.pack(pady=5)

tk.Button(frame_btn, text="Toți Clienții", command=lambda: afiseaza_clienti()).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="Plătiți", command=lambda: afiseaza_clienti("platit")).grid(row=0, column=1, padx=5)
tk.Button(frame_btn, text="Neplătiți", command=lambda: afiseaza_clienti("neplatit")).grid(row=0, column=2, padx=5)
tk.Button(frame_btn, text="Verifică Expirări", command=verifica_expirari).grid(row=0, column=3, padx=5)

afiseaza_clienti()
root.mainloop()
