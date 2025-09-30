import os
import tkinter as tk
from tkinter import filedialog, messagebox

def przeskaluj_linie(linie, nowy_min):
    liczby = [float(l.strip()) for l in linie if l.strip()]
    czesci_calk = [int(l) for l in liczby]
    min_calk = min(czesci_calk)
    offset = nowy_min - min_calk

    wynik = []
    for l in liczby:
        calk = int(l)
        frac = l - calk
        nowa_liczba = calk + offset + frac
        wynik.append(str(nowa_liczba))
    return wynik

def wybierz_plik():
    plik_we = filedialog.askopenfilename(
        title="Wybierz plik tekstowy",
        filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")]
    )
    if plik_we:
        entry_plik.delete(0, tk.END)
        entry_plik.insert(0, plik_we)

def wybierz_folder():
    folder = filedialog.askdirectory(title="Wybierz folder wyjściowy")
    if folder:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder)

def wykonaj():
    plik_we = entry_plik.get()
    folder_wy = entry_folder.get()
    
    if not plik_we or not os.path.isfile(plik_we):
        messagebox.showerror("Błąd", "Nieprawidłowy plik wejściowy.")
        return
    if not folder_wy or not os.path.isdir(folder_wy):
        messagebox.showerror("Błąd", "Nieprawidłowy folder wyjściowy.")
        return
    try:
        nowy_min = int(entry_min.get())
    except ValueError:
        messagebox.showerror("Błąd", "Minimalna część całkowita musi być liczbą całkowitą.")
        return

    with open(plik_we, "r", encoding="utf-8") as f:
        linie = f.readlines()

    wynik = przeskaluj_linie(linie, nowy_min)

    plik_wy = os.path.join(folder_wy, "nowe.txt")
    with open(plik_wy, "w", encoding="utf-8") as f:
        f.write("\n".join(wynik))

    messagebox.showinfo("Gotowe", f"Zapisano wynik w {plik_wy}")

# GUI
root = tk.Tk()
root.title("pff jebac polski modding")

# Wiersz 0 - plik wejściowy
tk.Label(root, text="Plik wejściowy:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_plik = tk.Entry(root, width=50)
entry_plik.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Wybierz", command=wybierz_plik).grid(row=0, column=2, padx=5, pady=5)

# Wiersz 1 - minimalna część całkowita
tk.Label(root, text="Minimalna część całkowita:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_min = tk.Entry(root, width=10)
entry_min.insert(0, "-10")
entry_min.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Wiersz 2 - folder wyjściowy
tk.Label(root, text="Folder wyjściowy:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_folder = tk.Entry(root, width=50)
entry_folder.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Wybierz", command=wybierz_folder).grid(row=2, column=2, padx=5, pady=5)

# Wiersz 3 - przycisk wykonania
tk.Button(root, text="Przeskaluj i zapisz", command=wykonaj).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
