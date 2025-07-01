import tkinter as tk
from tkinter import messagebox

def porownaj_ciagi():
    ciag1 = entry1.get()
    ciag2 = entry2.get()

    if ciag1 == ciag2:
        wynik_label.config(text="Ciągi są identyczne ✅", fg="green")
    else:
        wynik_label.config(text="Ciągi się różnią ❌", fg="red")

# Tworzenie głównego okna
root = tk.Tk()
root.title("Porównywarka ciągów tekstowych")
root.geometry("400x250")

# Etykiety i pola tekstowe
label1 = tk.Label(root, text="Wprowadź pierwszy ciąg:")
label1.pack(pady=(10, 0))
entry1 = tk.Entry(root, width=40)
entry1.pack(pady=(0, 10))

label2 = tk.Label(root, text="Wprowadź drugi ciąg:")
label2.pack()
entry2 = tk.Entry(root, width=40)
entry2.pack(pady=(0, 10))

# Przycisk do porównania
porownaj_button = tk.Button(root, text="Porównaj", command=porownaj_ciagi)
porownaj_button.pack(pady=10)

# Etykieta na wynik
wynik_label = tk.Label(root, text="", font=('Arial', 12))
wynik_label.pack(pady=10)

# Uruchomienie pętli głównej aplikacji
root.mainloop()
