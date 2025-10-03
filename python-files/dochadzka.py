from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

def parse_saldo(saldo_str):
    saldo_str = saldo_str.strip()
    if saldo_str and saldo_str[0] in "+-":
        znak = saldo_str[0]
        saldo_str = saldo_str[1:]
    else:
        znak = "-"  # predpokladá mínus, ak nie je +/-

    if ":" in saldo_str:
        hod, minu = map(int, saldo_str.split(":"))
    else:
        hod, minu = 0, int(saldo_str)

    saldo = timedelta(hours=hod, minutes=minu)
    return znak, saldo

def vypocitaj():
    prichod_str = entry_prichod.get()
    saldo_str = entry_saldo.get()
    try:
        denny_fond = timedelta(hours=8, minutes=30)
        prichod = datetime.strptime(prichod_str, "%H:%M")
        znak, saldo = parse_saldo(saldo_str)
        if znak == "-":
            denny_fond += saldo
        else:
            denny_fond -= saldo
        odchod = prichod + denny_fond
        label_vysledok.config(text=f"Dnes môžeš ísť na pivo o: {odchod.strftime('%H:%M')}")
    except Exception as e:
        messagebox.showerror("Chyba", "Skontroluj formát času alebo salda!\nFormát príchodu: HH:MM\nFormát salda: -30, 1:15, +0:45")

# ----------------- GUI -----------------
root = tk.Tk()
root.title("Dochádzka")

tk.Label(root, text="Čas príchodu (HH:MM):").grid(row=0, column=0, padx=5, pady=5)
entry_prichod = tk.Entry(root)
entry_prichod.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Saldo (+H:MM alebo -H:MM):").grid(row=1, column=0, padx=5, pady=5)
entry_saldo = tk.Entry(root)
entry_saldo.grid(row=1, column=1, padx=5, pady=5)

btn_vypocitaj = tk.Button(root, text="Vypočítať odchod", command=vypocitaj)
btn_vypocitaj.grid(row=2, column=0, columnspan=2, pady=10)

label_vysledok = tk.Label(root, text="")
label_vysledok.grid(row=3, column=0, columnspan=2, pady=5)

root.mainloop()
