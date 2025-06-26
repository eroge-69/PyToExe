try:
    import tkinter as tk
    from tkinter import ttk
    from tkcalendar import DateEntry
except ModuleNotFoundError:
    raise ImportError("Moduł tkinter nie jest zainstalowany. Zainstaluj go (np. python3-tk) i uruchom ponownie aplikację.")

FONT = ("Segoe UI", 12)
TEXT_FONT = ("Segoe UI", 14)

def toggle_inne_entry():
    if var_inne.get():
        entry_inne.config(state='normal')
    else:
        entry_inne.delete(0, tk.END)
        entry_inne.config(state='disabled')

def toggle_chlodnia_entry():
    if var_chlodnia.get():
        entry_temp.config(state='normal')
    else:
        entry_temp.delete(0, tk.END)
        entry_temp.config(state='disabled')

def generuj_opis():
    zaladunek = entry_zaladunek.get()
    data_zaladunku = kalendarz_zaladunek.get_date()
    data_zaladunku_str = data_zaladunku.strftime("%d.%m")
    godzina_od = combo_godz_od_zaladunek.get().replace(":", ".")
    godzina_do = combo_godz_do_zaladunek.get().replace(":", ".")
    rozladunek = entry_rozladunek.get()
    data_rozladunku = kalendarz_rozladunek.get_date()
    data_rozladunku_str = data_rozladunku.strftime("%d.%m")
    godzina_od_roz = combo_godz_od_rozladunek.get().replace(":", ".")
    godzina_do_roz = combo_godz_do_rozladunek.get().replace(":", ".")
    tonaz = combo_tonaz.get()
    wymiana = var_wymiana.get()

    dodatki = []
    if var_adr.get():
        dodatki.append("ADR")
    if var_kodxl.get():
        dodatki.append("Kod XL")
    if var_inne.get():
        inne_text = entry_inne.get().strip()
        if inne_text:
            dodatki.append(inne_text)
        else:
            dodatki.append("Inne")

    wymiana_text = "wymiana palet" if wymiana == "Tak" else "bez wymiany palet"
    dodatki_text = ", ".join(dodatki)
    if dodatki_text:
        dodatki_text = ", " + dodatki_text

    temp_text = ""
    temp_val = entry_temp.get().strip()
    if var_chlodnia.get() and temp_val:
        temp_text = f"\ntemp. {temp_val}"

    stawka = entry_stawka.get()

    wymiana_text_en = "pallet exchange" if wymiana == "Tak" else "no pallet exchange"
    dodatki_en_list = []
    for d in dodatki:
        if d == "ADR":
            dodatki_en_list.append("ADR")
        elif d == "Kod XL":
            dodatki_en_list.append("Code XL")
        elif d == "Inne":
            dodatki_en_list.append("Other")
        else:
            dodatki_en_list.append(d)
    dodatki_text_en = ", ".join(dodatki_en_list)
    if dodatki_text_en:
        dodatki_text_en = ", " + dodatki_text_en

    opis_pl = (
        f"Dzień dobry\n"
        f"{zaladunek} > {rozladunek}\n"
        f"Załadunek {data_zaladunku_str}, {godzina_od}-{godzina_do}\n"
        f"Rozładunek {data_rozladunku_str}, {godzina_od_roz}-{godzina_do_roz}\n"
        f"{wymiana_text}, {tonaz} ton{dodatki_text}{temp_text}\n"
        f"€{stawka}"
    )

    opis_en = (
        f"Hi\n"
        f"{zaladunek} > {rozladunek}\n"
        f"Loading {data_zaladunku_str}, {godzina_od}-{godzina_do}\n"
        f"Delivery {data_rozladunku_str}, {godzina_od_roz}-{godzina_do_roz}\n"
        f"{wymiana_text_en}, {tonaz} t{dodatki_text_en}{temp_text}\n"
        f"€{stawka}"
    )

    wynik.delete(1.0, tk.END)
    wynik.insert(tk.END, opis_pl + "\n\n" + opis_en)

def kopiuj_do_schowka():
    root.clipboard_clear()
    root.clipboard_append(wynik.get(1.0, tk.END).strip())

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Generator opisu ładunku dla spedytora 🚛")
    root.geometry("600x820")  # zwiększona wysokość na dodatkowe pola

    ttk.Label(root, text="Załadunek (kod i miasto):", font=FONT).grid(row=0, column=0, sticky='e', pady=5, padx=5)
    entry_zaladunek = ttk.Entry(root, font=FONT)
    entry_zaladunek.grid(row=0, column=1, pady=5, padx=5)

    ttk.Label(root, text="Data załadunku:", font=FONT).grid(row=1, column=0, sticky='e', pady=5, padx=5)
    kalendarz_zaladunek = DateEntry(root, date_pattern='yyyy-mm-dd', font=FONT)
    kalendarz_zaladunek.grid(row=1, column=1, pady=5, padx=5)

    ttk.Label(root, text="Godzina załadunku:", font=FONT).grid(row=2, column=0, sticky='e', pady=5, padx=5)
    frame_godz_zaladunek = ttk.Frame(root)
    frame_godz_zaladunek.grid(row=2, column=1, pady=5, padx=5, sticky='w')

    combo_godz_od_zaladunek = ttk.Combobox(frame_godz_zaladunek, values=[f"{h:02}:00" for h in range(24)], font=FONT, width=5)
    combo_godz_od_zaladunek.grid(row=0, column=0)
    combo_godz_od_zaladunek.current(8)

    ttk.Label(frame_godz_zaladunek, text=" - ", font=FONT).grid(row=0, column=1, padx=5)

    combo_godz_do_zaladunek = ttk.Combobox(frame_godz_zaladunek, values=[f"{h:02}:00" for h in range(24)], font=FONT, width=5)
    combo_godz_do_zaladunek.grid(row=0, column=2)
    combo_godz_do_zaladunek.current(8)

    ttk.Label(root, text="Rozładunek (kod i miasto):", font=FONT).grid(row=3, column=0, sticky='e', pady=5, padx=5)
    entry_rozladunek = ttk.Entry(root, font=FONT)
    entry_rozladunek.grid(row=3, column=1, pady=5, padx=5)

    ttk.Label(root, text="Data rozładunku:", font=FONT).grid(row=4, column=0, sticky='e', pady=5, padx=5)
    kalendarz_rozladunek = DateEntry(root, date_pattern='yyyy-mm-dd', font=FONT)
    kalendarz_rozladunek.grid(row=4, column=1, pady=5, padx=5)

    ttk.Label(root, text="Godzina rozładunku:", font=FONT).grid(row=5, column=0, sticky='e', pady=5, padx=5)
    frame_godz_rozladunek = ttk.Frame(root)
    frame_godz_rozladunek.grid(row=5, column=1, pady=5, padx=5, sticky='w')

    combo_godz_od_rozladunek = ttk.Combobox(frame_godz_rozladunek, values=[f"{h:02}:00" for h in range(24)], font=FONT, width=5)
    combo_godz_od_rozladunek.grid(row=0, column=0)
    combo_godz_od_rozladunek.current(8)

    ttk.Label(frame_godz_rozladunek, text=" - ", font=FONT).grid(row=0, column=1, padx=5)

    combo_godz_do_rozladunek = ttk.Combobox(frame_godz_rozladunek, values=[f"{h:02}:00" for h in range(24)], font=FONT, width=5)
    combo_godz_do_rozladunek.grid(row=0, column=2)
    combo_godz_do_rozladunek.current(8)

    ttk.Label(root, text="Tonaż:", font=FONT).grid(row=6, column=0, sticky='e', pady=5, padx=5)
    combo_tonaz = ttk.Combobox(root, values=[str(i) for i in range(1, 25)], font=FONT, width=5)
    combo_tonaz.grid(row=6, column=1, pady=5, padx=5)
    combo_tonaz.current(23)  # domyślnie 24

    ttk.Label(root, text="Wymiana palet:", font=FONT).grid(row=7, column=0, sticky='e', pady=5, padx=5)
    frame_wymiana = ttk.Frame(root)
    frame_wymiana.grid(row=7, column=1, pady=5, padx=5, sticky='w')

    var_wymiana = tk.StringVar(value="Nie")
    ttk.Radiobutton(frame_wymiana, text="Tak", variable=var_wymiana, value="Tak").grid(row=0, column=0, padx=(0,10))
    ttk.Radiobutton(frame_wymiana, text="Nie", variable=var_wymiana, value="Nie").grid(row=0, column=1)

    ttk.Label(root, text="Dodatkowe wymagania:", font=FONT).grid(row=8, column=0, sticky='e', pady=5, padx=5)
    frame_check = ttk.Frame(root)
    frame_check.grid(row=8, column=1, sticky='w', padx=5)

    var_adr = tk.BooleanVar()
    cb_adr = ttk.Checkbutton(frame_check, text="ADR", variable=var_adr)
    cb_adr.grid(row=0, column=0, padx=5)

    var_kodxl = tk.BooleanVar()
    cb_kodxl = ttk.Checkbutton(frame_check, text="Kod XL", variable=var_kodxl)
    cb_kodxl.grid(row=0, column=1, padx=5)

    var_inne = tk.BooleanVar()
    cb_inne = ttk.Checkbutton(frame_check, text="Inne", variable=var_inne, command=toggle_inne_entry)
    cb_inne.grid(row=0, column=2, padx=5)

    entry_inne = ttk.Entry(frame_check, font=FONT, state='disabled', width=20)
    entry_inne.grid(row=0, column=3, padx=5)

    var_chlodnia = tk.BooleanVar()
    cb_chlodnia = ttk.Checkbutton(root, text="Chłodnia", variable=var_chlodnia, command=toggle_chlodnia_entry)
    cb_chlodnia.grid(row=9, column=0, sticky='e', pady=5, padx=5)

    entry_temp = ttk.Entry(root, font=FONT, state='disabled', width=20)
    entry_temp.grid(row=9, column=1, pady=5, padx=5)

    ttk.Label(root, text="Stawka (EUR):", font=FONT).grid(row=10, column=0, sticky='e', pady=5, padx=5)
    entry_stawka = ttk.Entry(root, font=FONT)
    entry_stawka.grid(row=10, column=1, pady=5, padx=5)

    btn_generuj = ttk.Button(root, text="Generuj opis", command=generuj_opis)
    btn_generuj.grid(row=11, column=0, columnspan=2, pady=10)

    frame_wynik = ttk.Frame(root)
    frame_wynik.grid(row=12, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

    wynik = tk.Text(frame_wynik, height=12, width=60, font=TEXT_FONT, wrap='word')
    wynik.grid(row=0, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(frame_wynik, orient='vertical', command=wynik.yview)
    scrollbar.grid(row=0, column=1, sticky='ns')
    wynik.configure(yscrollcommand=scrollbar.set)

    frame_wynik.columnconfigure(0, weight=1)
    frame_wynik.rowconfigure(0, weight=1)

    btn_kopiuj = ttk.Button(root, text="Kopiuj", command=kopiuj_do_schowka)
    btn_kopiuj.grid(row=13, column=0, columnspan=2, pady=(5, 15))

    root.mainloop()
