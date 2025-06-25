import tkinter as tk
from tkinter import messagebox
import datetime

def valid_date(date_str):
    try:
        # Rozdzielamy dzień i miesiąc
        day, month = map(int, date_str.split("-"))
        year = datetime.datetime.now().year
        datetime.datetime(year, month, day)  # Sprawdzenie poprawności
        return True
    except (ValueError, IndexError):
        return False

def dodaj_wpis():
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
    full_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"  # Formatujemy do RRRR-MM-DD

    wpis = f"Router ID: {router_id}, Pokój: {pokoj}, Do: {full_date}"
    with open("lista_routerow.txt", "a") as plik:
        plik.write(wpis + "\n")

    messagebox.showinfo("Sukces", "Dane zapisane!")
    entry_id.delete(0, tk.END)
    entry_pokoj.delete(0, tk.END)
    entry_data.delete(0, tk.END)

# Tworzenie GUI
root = tk.Tk()
root.title("Monitorowanie routerów")
root.geometry("400x250")

tk.Label(root, text="ID Routera:").pack()
entry_id = tk.Entry(root)
entry_id.pack()

tk.Label(root, text="Numer pokoju:").pack()
entry_pokoj = tk.Entry(root)
entry_pokoj.pack()

tk.Label(root, text="Data do (DD-MM):").pack()
entry_data = tk.Entry(root)
entry_data.pack()

tk.Button(root, text="Zapisz dane", command=dodaj_wpis).pack(pady=10)

root.mainloop()