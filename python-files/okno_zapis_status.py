import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import xlwings as xw
from datetime import datetime

import os

plik_excel = None
haslo_arkusza = "JK2023"  # ← wpisz tu hasło lub zostaw pusty string jeśli nie ma

def wybierz_plik():
    global plik_excel
    plik_excel = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls;*.xlsx;*.xlsm")])
    if plik_excel:
        etykieta_plik.config(text=f"Wybrano:\n{plik_excel}", bg="green")

def zastosuj():

    global plik_excel
    if not plik_excel:
        messagebox.showerror("Błąd", "Najpierw wybierz plik.")
        return

    try:
        app = xw.App(visible=True)

        wb = app.books.open(plik_excel)

# Zamknij pusty zeszyt, jeśli nadal istnieje
        for book in app.books:
            if book.name.lower().startswith("zeszyt") and book != wb:
                book.close()

        ws = wb.sheets[0]  # lub konkretny arkusz np. wb.sheets["usterki"]


        # Odblokuj arkusz jeśli chroniony
        if ws.api.ProtectContents:
            try:
                ws.api.Unprotect(Password=haslo_arkusza)
            except:
                messagebox.showerror("Błąd", "Nie udało się odblokować arkusza. Sprawdź hasło.")
                app.quit()
                return

        ok_input = entry_ok.get().split(";")
        nok_input = entry_nok.get().split(";")

        ok_rows = set()
        nok_rows = set()

        for val in ok_input:
            val = val.strip()
            if val.isdigit():
                ok_rows.add(int(val) + 4)

        for val in nok_input:
            val = val.strip()
            if val.isdigit():
                nok_rows.add(int(val) + 4)

        zmienione = 0
        dzisiaj = datetime.today().strftime('%Y-%m-%d')

        for r in ok_rows:
            try:
                ws.cells(r, 14).value = dzisiaj
                ws.cells(r, 13).value = "OK"
                zmienione += 1
            except:
                continue

        for r in nok_rows:
            try:
                ws.cells(r, 14).value = dzisiaj
                ws.cells(r, 13).value = "NOK"
                zmienione += 1
            except:
                continue

        messagebox.showinfo("Zakończono", f"Wprowadzono zmiany w {zmienione} wierszach.\nPlik pozostaje otwarty — zapisz ręcznie, jeśli chcesz.")

    except Exception as e:
        messagebox.showerror("Błąd", f"Coś poszło nie tak:\n{str(e)}")

# GUI
root = tk.Tk()
root.title("Tabele usterek -  Ustawianie OK/NOK")
root.geometry("600x400")

bg_image = Image.open("C:\\Users\\pawel.janowiec\\Desktop\\Aplikacja - usterki\\tło- okno.jpg")  # ← Podaj ścieżkę do swojego pliku
bg_image = bg_image.resize((600, 400))  # Dostosuj do rozmiaru okna
bg_photo = ImageTk.PhotoImage(bg_image)

# 🔲 Dodaj etykietę z obrazkiem jako tło
background_label = tk.Label(root, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

etykieta_plik = tk.Label(root, text="Nie wybrano pliku.", wraplength=450, justify="center", bg="red")
etykieta_plik.pack(pady=15)

btn_wybierz = tk.Button(root, text="Wybierz plik Excel", command=wybierz_plik, )
btn_wybierz.pack(pady=10)

tk.Label(root, text="Wiersze OK (np. 1;3;5):").pack()
entry_ok = tk.Entry(root, width=60)
entry_ok.pack(pady=20)

tk.Label(root, text="Wiersze NOK (np. 2;4):").pack()
entry_nok = tk.Entry(root, width=60)
entry_nok.pack(pady=20)

btn_zastosuj = tk.Button(root, text="Zastosuj", command=zastosuj, bg="green", fg="white")
btn_zastosuj.pack(pady=30)

root.mainloop()
