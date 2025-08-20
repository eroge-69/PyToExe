import sys
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
import re

log_file = "error_log.txt"

# --- Funkcja do wyświetlania błędów w GUI ---
def show_error(exc_type, exc_value, exc_traceback):
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    root_err = tk.Tk()
    root_err.withdraw()
    messagebox.showerror("Błąd", f"Wystąpił błąd! Sprawdź {log_file}\n\n{exc_value}")
    sys.exit(1)

sys.excepthook = show_error

# --- Walidacja danych ---
def poprawny_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def poprawny_pesel(pesel):
    return pesel.isdigit() and len(pesel) == 10

# --- Połączenie z bazą danych ---
import mysql.connector
conn = mysql.connector.connect(
    host="192.100.100.4",
    user="rodo_software",
    password="wuBimO688i",
    database="shark",
    port=3308
)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rodo (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255),
        password VARCHAR(10)
    )
''')
conn.commit()

# --- Funkcje GUI ---
def odswiez_dane(filter_type=None, filter_value=None):
    for row in tree.get_children():
        tree.delete(row)
    if filter_type == "pesel":
        cursor.execute("SELECT * FROM rodo WHERE password LIKE %s ORDER BY id DESC", (f"%{filter_value}%",))
    elif filter_type == "email":
        cursor.execute("SELECT * FROM rodo WHERE email LIKE %s ORDER BY id DESC", (f"%{filter_value}%",))
    elif filter_type == "top10":
        cursor.execute("SELECT * FROM rodo ORDER BY id DESC LIMIT 10")
    else:
        cursor.execute("SELECT * FROM rodo ORDER BY id DESC LIMIT 20")
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)

def dodaj_rekord():
    email = entry_email.get().strip()
    pesel = entry_pesel.get().strip()
    if not email or not pesel:
        messagebox.showwarning("Błąd", "Podaj email i PESEL")
        return
    if not poprawny_email(email):
        messagebox.showerror("Błąd", "Niepoprawny format emaila")
        return
    if not poprawny_pesel(pesel):
        messagebox.showerror("Błąd", "PESEL musi składać się z 10 cyfr")
        return
    cursor.execute("SELECT * FROM rodo WHERE email = %s", (email,))
    if cursor.fetchone():
        messagebox.showerror("Błąd", "Rekord z tym emailem już istnieje")
        return
    cursor.execute("INSERT INTO rodo (email, password) VALUES (%s, %s)", (email, pesel))
    conn.commit()
    entry_email.delete(0, tk.END)
    entry_pesel.delete(0, tk.END)
    odswiez_dane()

def usun_rekord():
    wybrany = tree.selection()
    if wybrany:
        rekord = tree.item(wybrany)['values']
        cursor.execute("DELETE FROM rodo WHERE id = %s", (rekord[0],))
        conn.commit()
        odswiez_dane()
    else:
        messagebox.showwarning("Błąd", "Wybierz rekord do usunięcia")

def zapisz_zmiany():
    wybrany = tree.selection()
    if wybrany:
        nowe_email = entry_edytuj_email.get().strip()
        nowe_pesel = entry_edytuj_pesel.get().strip()
        if not poprawny_email(nowe_email):
            messagebox.showerror("Błąd", "Niepoprawny format emaila")
            return
        if not poprawny_pesel(nowe_pesel):
            messagebox.showerror("Błąd", "PESEL musi składać się z 10 cyfr")
            return
        cursor.execute("SELECT * FROM rodo WHERE email = %s AND id != %s", (nowe_email, tree.item(wybrany)['values'][0]))
        if cursor.fetchone():
            messagebox.showerror("Błąd", "Inny rekord z tym emailem już istnieje")
            return
        rekord = tree.item(wybrany)['values']
        cursor.execute("UPDATE rodo SET email = %s, password = %s WHERE id = %s", (nowe_email, nowe_pesel, rekord[0]))
        conn.commit()
        odswiez_dane()
    else:
        messagebox.showwarning("Błąd", "Wybierz rekord do edycji")

def on_select(event):
    wybrany = tree.selection()
    if wybrany:
        rekord = tree.item(wybrany)['values']
        entry_edytuj_email.delete(0, tk.END)
        entry_edytuj_email.insert(0, rekord[1])
        entry_edytuj_pesel.delete(0, tk.END)
        entry_edytuj_pesel.insert(0, rekord[2])

def filtruj():
    typ = filtr_typ.get()
    wartosc = filtr_wartosc.get()
    if typ in ["pesel", "email"] and not wartosc:
        messagebox.showwarning("Błąd", "Wprowadź wartość do filtrowania.")
        return
    if typ == "top10":
        odswiez_dane("top10")
    elif typ == "pesel":
        odswiez_dane("pesel", wartosc)
    elif typ == "email":
        odswiez_dane("email", wartosc)
    else:
        odswiez_dane()

# --- GUI ---
root = tk.Tk()
root.title("Shark RODO")
root_width = 1050
root_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cord = int((screen_width/2) - (root_width/2))
y_cord = int((screen_height/2) - (root_height/2))
root.geometry(f"{root_width}x{root_height}+{x_cord}+{y_cord}")

tree = ttk.Treeview(root, columns=('ID', 'Email', 'PESEL'), show='headings', height=18)
tree.heading('ID', text='ID')
tree.heading('Email', text='Email')
tree.heading('PESEL', text='PESEL')
tree.column('Email', width=400)
tree.column('PESEL', width=150)
tree.bind("<<TreeviewSelect>>", on_select)
tree.grid(row=0, column=0, padx=10, pady=10)

panel = tk.Frame(root)
panel.grid(row=0, column=1, sticky='n', padx=10, pady=10)
tk.Label(panel, text="✏️ Edycja rekordu").pack(pady=5)
tk.Label(panel, text="Email:").pack()
entry_edytuj_email = tk.Entry(panel, width=40)
entry_edytuj_email.pack(pady=2)
tk.Label(panel, text="PESEL:").pack()
entry_edytuj_pesel = tk.Entry(panel, width=20)
entry_edytuj_pesel.pack(pady=2)
tk.Button(panel, text="Zapisz zmiany", width=20, command=zapisz_zmiany).pack(pady=5)
tk.Button(panel, text="Usuń rekord", width=20, command=usun_rekord).pack(pady=5)

tk.Label(root, text="➕ Nowy wpis").grid(row=1, column=0, columnspan=2, pady=(10, 0))
input_frame = tk.Frame(root)
input_frame.grid(row=2, column=0, columnspan=2, pady=5)
tk.Label(input_frame, text="Email:").grid(row=0, column=0)
entry_email = tk.Entry(input_frame, width=40)
entry_email.grid(row=0, column=1, padx=5)
tk.Label(input_frame, text="PESEL:").grid(row=0, column=2)
entry_pesel = tk.Entry(input_frame, width=20)
entry_pesel.grid(row=0, column=3, padx=5)
tk.Button(input_frame, text="Wyślij", width=15, command=dodaj_rekord).grid(row=0, column=4, padx=10)

tk.Label(root, text="🔍 Filtrowanie danych").grid(row=3, column=0, columnspan=2)
filtr_frame = tk.Frame(root)
filtr_frame.grid(row=4, column=0, columnspan=2, pady=5)
filtr_typ = ttk.Combobox(filtr_frame, values=["pesel", "email", "top10"], width=10)
filtr_typ.set("pesel")
filtr_typ.grid(row=0, column=0)
filtr_wartosc = tk.Entry(filtr_frame, width=20)
filtr_wartosc.grid(row=0, column=1, padx=5)
tk.Button(filtr_frame, text="Filtruj", width=10, command=filtruj).grid(row=0, column=2)

odswiez_dane()
root.mainloop()
conn.close()
