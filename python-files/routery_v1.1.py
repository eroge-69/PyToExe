import tkinter as tk
from tkinter import messagebox
import datetime
import os

plik_nazwa = "lista_routerow.txt"

def valid_date(date_str):
    try:
        day, month = map(int, date_str.split("-"))
        year = datetime.datetime.now().year
        datetime.datetime(year, month, day)
        return True
    except (ValueError, IndexError):
        return False

def dodaj_lub_nadpisz_wpis():
    router_id = entry_id.get()
    pokoj = entry_pokoj.get()
    data_dm = entry_data.get()

    if not router_id.isdigit():
        messagebox.showerror("Błąd", "ID routera musi być liczbą.")
        return
    if not pokoj.isdigit() or len(pokoj) != 3:
        messagebox.showerror("Błąd", "Numer pokoju musi mieć dokładnie 3 cyfry.")
        return
    if not valid_date(data_dm):
        messagebox.showerror("Błąd", "Nieprawidłowy format daty (DD-MM).")
        return

    day, month = data_dm.split("-")
    year = datetime.datetime.now().year
    full_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    wpis = f"Router ID: {router_id}, Pokój: {pokoj}, Do: {full_date}"

    # Nadpisywanie
    nowe_linie = []
    nadpisano = False

    if os.path.exists(plik_nazwa):
        with open(plik_nazwa, "r") as plik:
            for linia in plik:
                if f"Router ID: {router_id}," in linia:
                    nowe_linie.append(wpis + "\n")
                    nadpisano = True
                else:
                    nowe_linie.append(linia)

    if not nadpisano:
        nowe_linie.append(wpis + "\n")

    with open(plik_nazwa, "w") as plik:
        plik.writelines(nowe_linie)

    messagebox.showinfo("Sukces", "Dane zapisane!" if not nadpisano else "Wpis zaktualizowany!")
    entry_id.delete(0, tk.END)
    entry_pokoj.delete(0, tk.END)
    entry_data.delete(0, tk.END)

def usun_router():
    router_id = entry_usun.get()
    if not router_id.isdigit():
        messagebox.showerror("Błąd", "ID routera musi być liczbą.")
        return

    if not os.path.exists(plik_nazwa):
        messagebox.showinfo("Informacja", "Plik jest pusty lub nie istnieje.")
        return

    nowe_linie = []
    usunieto = False

    with open(plik_nazwa, "r") as plik:
        for linia in plik:
            if f"Router ID: {router_id}," not in linia:
                nowe_linie.append(linia)
            else:
                usunieto = True

    with open(plik_nazwa, "w") as plik:
        plik.writelines(nowe_linie)

    if usunieto:
        messagebox.showinfo("Sukces", f"Router ID {router_id} usunięty.")
    else:
        messagebox.showinfo("Informacja", f"Router ID {router_id} nie został znaleziony.")
    entry_usun.delete(0, tk.END)

# Tworzenie GUI
root = tk.Tk()
root.title("Monitorowanie routerów")
root.geometry("420x320")

# Sekcja dodawania
tk.Label(root, text="ID Routera:").pack()
entry_id = tk.Entry(root)
entry_id.pack()

tk.Label(root, text="Numer pokoju:").pack()
entry_pokoj = tk.Entry(root)
entry_pokoj.pack()

tk.Label(root, text="Data do (DD-MM):").pack()
entry_data = tk.Entry(root)
entry_data.pack()

tk.Button(root, text="Zapisz / Zaktualizuj", command=dodaj_lub_nadpisz_wpis).pack(pady=10)

# Separator
tk.Label(root, text="------------------------------------").pack(pady=5)

# Sekcja usuwania
tk.Label(root, text="Usuń router po ID:").pack()
entry_usun = tk.Entry(root)
entry_usun.pack()

tk.Button(root, text="Usuń router", command=usun_router).pack(pady=10)

root.mainloop()