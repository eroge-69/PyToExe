import tkinter as tk
from tkinter import messagebox

def calcola_acceleratori():
    try:
        n = int(entry_acceleratori.get())
        totale_minuti = n * 5
        ore = totale_minuti // 60
        minuti = totale_minuti % 60
        risultato = f"Totale: {ore} ore e {minuti} minuti"
        label_risultato_acc.config(text=risultato)
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero valido di acceleratori.")

def calcola_accelerazione():
    try:
        giorni = int(entry_giorni.get() or 0)
        ore = int(entry_ore.get() or 0)
        minuti = int(entry_minuti.get() or 0)
        percentuale = float(entry_percentuale.get())

        # Calcolo totale in minuti
        minuti_totali = giorni * 24 * 60 + ore * 60 + minuti

        # Applica accelerazione
        fattore = 1 + (percentuale / 100)
        minuti_finali = int(minuti_totali * fattore)

        # Converti di nuovo in giorni, ore, minuti
        giorni_f = minuti_finali // (24 * 60)
        ore_f = (minuti_finali % (24 * 60)) // 60
        minuti_f = minuti_finali % 60

        risultato = f"Tempo aumentato: {giorni_f}g {ore_f}h {minuti_f}min"
        label_risultato_temp.config(text=risultato)

    except ValueError:
        messagebox.showerror("Errore", "Controlla che tutti i campi siano numeri validi.")

# GUI setup
root = tk.Tk()
root.title("Calcoli Accelerazione")
root.geometry("400x400")
root.resizable(False, False)

# Sezione 1: Acceleratori
frame1 = tk.LabelFrame(root, text="1. Calcolo acceleratori (5 min ciascuno)")
frame1.pack(padx=10, pady=10, fill="x")

tk.Label(frame1, text="Numero di acceleratori:").pack()
entry_acceleratori = tk.Entry(frame1)
entry_acceleratori.pack()

tk.Button(frame1, text="Calcola tempo totale", command=calcola_acceleratori).pack(pady=5)
label_risultato_acc = tk.Label(frame1, text="Totale: ")
label_risultato_acc.pack()

# Sezione 2: Accelerazione tempo
frame2 = tk.LabelFrame(root, text="2. Calcolo accelerazione su tempistica")
frame2.pack(padx=10, pady=10, fill="x")

tk.Label(frame2, text="Tempo iniziale").pack()
row1 = tk.Frame(frame2)
row1.pack()
tk.Label(row1, text="Giorni:").pack(side="left")
entry_giorni = tk.Entry(row1, width=5)
entry_giorni.pack(side="left", padx=5)
tk.Label(row1, text="Ore:").pack(side="left")
entry_ore = tk.Entry(row1, width=5)
entry_ore.pack(side="left", padx=5)
tk.Label(row1, text="Minuti:").pack(side="left")
entry_minuti = tk.Entry(row1, width=5)
entry_minuti.pack(side="left", padx=5)

tk.Label(frame2, text="Percentuale accelerazione (es. 280):").pack(pady=5)
entry_percentuale = tk.Entry(frame2)
entry_percentuale.pack()

tk.Button(frame2, text="Calcola tempo aumentato", command=calcola_accelerazione).pack(pady=5)
label_risultato_temp = tk.Label(frame2, text="Tempo aumentato:")
label_risultato_temp.pack()

root.mainloop()
