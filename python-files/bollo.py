import tkinter as tk
from datetime import date

# Funzioni di calcolo
def calcola_bollo_veneto(kw, euro):
    tariffe = {0: (3.30, 4.95), 1: (3.19, 4.79), 2: (3.08, 4.62),
               3: (2.97, 4.46), 4: (2.84, 4.26), 5: (2.84, 4.26), 6: (2.58, 3.87)}
    base, extra = tariffe[euro]
    return round(kw*base if kw<=100 else 100*base + (kw-100)*extra, 2)

def calcola_superbollo(kw, immatricolazione):
    if kw <= 185:
        return 0.0, "Nessun superbollo (≤185 kW)"
    ecc = kw-185
    oggi = date.today()
    eta = oggi.year - immatricolazione.year - ((oggi.month, oggi.day) < (immatricolazione.month, immatricolazione.day))
    if eta <= 5:
        return round(ecc*20,2), f"Veicolo di {eta} anni → tariffa piena: 20 €/kW"
    elif 6 <= eta <=10:
        return round(ecc*12,2), f"Veicolo di {eta} anni → riduzione 40%: 12 €/kW"
    elif 11 <= eta <=14:
        return round(ecc*6,2), f"Veicolo di {eta} anni → riduzione 70%: 6 €/kW"
    elif 15 <= eta <=19:
        return round(ecc*3,2), f"Veicolo di {eta} anni → riduzione 85%: 3 €/kW"
    else:
        return 0.0, f"Veicolo di {eta} anni → esente da superbollo"

# Funzione calcolo
def calcola():
    risultato_text.delete(1.0, tk.END)
    try:
        g = int(giorno_entry.get())
        m = int(mese_entry.get())
        a = int(anno_entry.get())
        euro = int(euro_entry.get())
        kw = float(kw_entry.get())
        imm = date(a,m,g)
        oggi = date.today()
        if imm > oggi:
            risultato_text.insert(tk.END,"⚠️ La data immatricolazione è nel futuro!\n")
            return
        if euro<0 or euro>6:
            risultato_text.insert(tk.END,"⚠️ Categoria Euro non valida (0-6)!\n")
            return
        if kw<=0:
            risultato_text.insert(tk.END,"⚠️ kW non valido!\n")
            return
        bollo = calcola_bollo_veneto(kw,euro)
        superbollo, det = calcola_superbollo(kw,imm)
        totale = bollo+superbollo
        eta = oggi.year - imm.year - ((oggi.month, oggi.day) < (imm.month, imm.day))
        risultato = f"Data immatricolazione: {imm.strftime('%d/%m/%Y')} ({eta} anni)\n"
        risultato += f"Potenza: {kw} kW - Categoria Euro {euro}\n"
        risultato += f"Bollo base: € {bollo}\n"
        risultato += f"Superbollo: € {superbollo} → {det}\n"
        risultato += f"Totale da pagare: € {totale}\n"
        risultato_text.insert(tk.END, risultato)
    except ValueError:
        risultato_text.insert(tk.END,"⚠️ Controlla di aver inserito numeri validi in tutti i campi!\n")

# GUI principale
root = tk.Tk()
root.title("Calcolatore Bollo Auto Veneto 2025")
root.geometry("700x400")  # finestra più larga

# Titolo
tk.Label(root,text="Inserisci i dati del veicolo", font=("Arial",14)).grid(row=0, column=0, columnspan=6, pady=10)

# Giorno, Mese, Anno
tk.Label(root,text="Giorno (gg):").grid(row=1, column=0)
giorno_entry = tk.Entry(root,width=5)
giorno_entry.grid(row=2, column=0, padx=5)

tk.Label(root,text="Mese (mm):").grid(row=1, column=1)
mese_entry = tk.Entry(root,width=5)
mese_entry.grid(row=2, column=1, padx=5)

tk.Label(root,text="Anno (aaaa):").grid(row=1, column=2)
anno_entry = tk.Entry(root,width=7)
anno_entry.grid(row=2, column=2, padx=5)

# Categoria Euro
tk.Label(root,text="Categoria Euro (0-6):").grid(row=1, column=3)
euro_entry = tk.Entry(root,width=5)
euro_entry.grid(row=2, column=3, padx=5)

# kW
tk.Label(root,text="Potenza kW:").grid(row=1, column=4)
kw_entry = tk.Entry(root,width=7)
kw_entry.grid(row=2, column=4, padx=5)

# Bottone Calcola
tk.Button(root,text="Calcola Bollo", command=calcola).grid(row=2, column=5, padx=10)

# Risultato
tk.Label(root,text="Risultato:", font=("Arial",12)).grid(row=3,column=0,columnspan=6,pady=10)
risultato_text = tk.Text(root,height=10,width=80)
risultato_text.grid(row=4,column=0,columnspan=6,padx=10)

root.mainloop()
