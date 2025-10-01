import tkinter as tk
def oblicz():
        uczniowie = int(pole_ilosc_uczniuw.get())
        cukierki = int(pole_ilosc_cukierkuw.get())
        na_osobe = cukierki // uczniowie
        reszta_dla_jubilata = cukierki % uczniowie
        wynik_label.config(text=(f"Każdy (w tym jubilat) dostaje: {na_osobe}\n"f"Jubilat dostaje dodatkowo: {reszta_dla_jubilata}") )
okno = tk.Tk()
okno.title("Urodziny")
okno.geometry("300x250")
okno.configure(bg='lightblue')
etykieta_uczniowie = tk.Label(okno, text="Liczba uczniów (z jubilatem):")
etykieta_uczniowie.pack()
pole_ilosc_uczniuw = tk.Entry(okno, width=5)
pole_ilosc_uczniuw.pack()
etykieta_cukierki = tk.Label(okno, text="Liczba cukierków:")
etykieta_cukierki.pack()
pole_ilosc_cukierkuw = tk.Entry(okno, width=5)
pole_ilosc_cukierkuw.pack()
przycisk_oblicz = tk.Button(okno, text="Oblicz", command=oblicz)
przycisk_oblicz.pack(pady=10)
wynik_label = tk.Label(okno, text="")
wynik_label.pack()
okno.mainloop()