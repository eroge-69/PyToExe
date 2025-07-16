
import tkinter as tk
from tkinter import messagebox

def rozpisz_zeby():
    dane = entry.get().strip()
    try:
        if '-' not in dane:
            raise ValueError("Zakres musi zawierać '-'")
        poczatek_str, koniec_str = dane.split('-')
        poczatek = int(poczatek_str)
        koniec = int(koniec_str)

        if not (10 <= poczatek <= 48 and 10 <= koniec <= 48):
            raise ValueError("Podane liczby muszą być w zakresie 10-48 (wg Viohla)")

        krok = 1 if poczatek <= koniec else -1
        wynik = [str(i) for i in range(poczatek, koniec + krok, krok)]
        wynik_label.config(text="Zęby: " + ", ".join(wynik))

    except ValueError as e:
        messagebox.showerror("Błąd", f"Niepoprawny format: {e}")

# Tworzenie GUI
root = tk.Tk()
root.title("Rozpiska zębów Viohla")

tk.Label(root, text="Podaj zakres (np. 17-14):").pack(pady=5)

entry = tk.Entry(root, width=20)
entry.pack(pady=5)

btn = tk.Button(root, text="Rozpisz", command=rozpisz_zeby)
btn.pack(pady=5)

wynik_label = tk.Label(root, text="")
wynik_label.pack(pady=10)

root.mainloop()
