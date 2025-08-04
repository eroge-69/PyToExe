Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
...     os.system("shutdown /s /t 0")
...
... # GUI
... okno = tk.Tk()
... okno.title("Časovač vypnutí PC")
... okno.geometry("300x180")
... okno.resizable(False, False)
...
... # Popis
... popis = tk.Label(okno, text="Zadej čas do vypnutí:")
... popis.pack(pady=10)
...
... # Vstup pro čas
... cas_entry = tk.Entry(okno, width=10, justify="center")
... cas_entry.pack()
...
... # Výběr jednotky
... jednotka = tk.StringVar(value="minuty")
... frame = tk.Frame(okno)
... tk.Radiobutton(frame, text="Minuty", variable=jednotka, value="minuty").pack(side="left", padx=10)
... tk.Radiobutton(frame, text="Sekundy", variable=jednotka, value="sekundy").pack(side="left")
... frame.pack(pady=5)
...
... # Tlačítko
... tlacitko = tk.Button(okno, text="Spustit časovač", command=lambda: vypnout_za(cas_entry.get(), jednotka.get()))
... tlacitko.pack(pady=10)
...
... # Spustit okno
... okno.mainloop()

