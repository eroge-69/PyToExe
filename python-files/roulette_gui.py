import tkinter as tk
import math

colori_roulette = {
    0: "green", 1: "red", 2: "black", 3: "red", 4: "black", 5: "red", 6: "black",
    7: "red", 8: "black", 9: "red", 10: "black", 11: "black", 12: "red", 13: "black",
    14: "red", 15: "black", 16: "red", 17: "black", 18: "red", 19: "red", 20: "black",
    21: "red", 22: "black", 23: "red", 24: "black", 25: "red", 26: "black", 27: "red",
    28: "black", 29: "black", 30: "red", 31: "black", 32: "red", 33: "black", 34: "red",
    35: "black", 36: "red"
}

sfondo_base = "#2e2e2e"
cassa_attuale = 100.0
numeri_inseriti = []
blocco_temp = []

puntate_per_step = {i: max(1, i // 5) for i in range(1, 51)}

morph = {
    "step": 1, "blocco": 1, "colpo": 0, "saldo": 0.0, "cassa_iniziale": 100.0,
    "numeri_blocco": [], "sestina": [], "terzina": [], "secco": None,
    "step_attivo": "", "stato": "inattivo"
}

finestra = tk.Tk()
finestra.title("Sestine Magiche – By Mozart373")
finestra.geometry("700x720")
finestra.configure(bg=sfondo_base)
finestra.resizable(True, True)

contenitore = tk.Frame(finestra, bg=sfondo_base)
contenitore.pack(fill="both", expand=True, padx=10, pady=10)

colonna_sx = tk.Frame(contenitore, bg=sfondo_base)
colonna_sx.grid(row=0, column=0, sticky="n")

colonna_centro = tk.Frame(contenitore, bg=sfondo_base)
colonna_centro.grid(row=0, column=1, padx=20)

colonna_dx = tk.Frame(contenitore, bg=sfondo_base)
colonna_dx.grid(row=0, column=2, sticky="n")

etichetta_cassa = tk.Label(finestra, text="Cassa: € 100.00", font=("Arial", 14, "bold"),
                           bg=sfondo_base, fg="white")
etichetta_cassa.pack()

def aggiorna_cassa_display():
    etichetta_cassa.config(text=f"Cassa: € {cassa_attuale:,.2f}")
# 📜 Colonna sinistra – Ultimi numeri
tk.Label(colonna_sx, text="📝 Ultimi 10 numeri:", font=("Arial", 12),
         bg=sfondo_base, fg="white").pack(pady=(10, 4))

frame_numeri = tk.Frame(colonna_sx, bg=sfondo_base)
frame_numeri.pack()

def aggiorna_lista():
    for widget in frame_numeri.winfo_children():
        widget.destroy()
    for n in reversed(numeri_inseriti[-10:]):
        colore = colori_roulette.get(n, "gray")
        testo = "white" if colore in ["red", "black"] else "black"
        tk.Label(frame_numeri, text=str(n), width=4, height=2,
                 bg=colore, fg=testo, font=("Arial", 11, "bold"),
                 relief="sunken").pack(pady=2)
def cancella_ultimo():
    if numeri_inseriti:
        numeri_inseriti.pop()
        aggiorna_lista()

# 🧹 Tasti sotto lo storico
frame_tasti = tk.Frame(colonna_sx, bg=sfondo_base)
frame_tasti.pack(pady=10)

entry_numero = tk.Entry(frame_tasti, width=10)
entry_numero.pack(pady=4)

tk.Button(frame_tasti, text="Inserisci", command=lambda: (
    inserisci_esito(entry_numero.get()), entry_numero.delete(0, tk.END)),
    bg="#5cb85c", fg="white", width=12).pack(pady=2)

tk.Button(frame_tasti, text="↩️ Ultimo", width=12,
          command=cancella_ultimo, bg="#d9534f", fg="white").pack(pady=2)
def elimina_tutto():
    global numeri_inseriti, cassa_attuale
    numeri_inseriti.clear()
    cassa_attuale = morph["cassa_iniziale"]
    morph.update({
        "step": 1, "colpo": 0, "saldo": 0.0, "blocco": 1,
        "sestina": [], "step_attivo": "", "stato": "inattivo",
        "numeri_blocco": [], "terzina": [], "secco": None
    })
    aggiorna_lista()
    aggiorna_gui_morph()
    aggiorna_cassa_display()

tk.Button(frame_tasti, text="🧹 Elimina tutto", width=16,
          command=elimina_tutto, bg="#343a40", fg="white").pack(pady=2)

# 🔘 Colonna centrale – Pulsantiera 0–36
tk.Label(colonna_centro, text="🎰 Clicca numero uscito:", font=("Arial", 12),
         bg=sfondo_base, fg="white").grid(row=0, column=0, columnspan=3, pady=6)

# 0 in alto
btn_0 = tk.Button(colonna_centro, text="0", width=10, height=2,
                  bg="green", fg="white", command=lambda: inserisci_esito(0))
btn_0.grid(row=1, column=0, columnspan=3, pady=(0, 6))

# Da 1 a 36 sotto
indice = 1
for riga in range(2, 14):
    for colonna in range(3):
        numero = indice
        colore = colori_roulette[numero]
        testo = "white" if colore in ["red", "black"] else "black"
        tk.Button(colonna_centro, text=str(numero), width=4, height=2,
                  bg=colore, fg=testo,
                  command=lambda n=numero: inserisci_esito(n)).grid(
            row=riga, column=colonna, padx=4, pady=2)
        indice += 1
# 🧠 Colonna destra – Pannello Morph System
frame_morph = tk.Frame(colonna_dx, bg="#1e1e1e", bd=2, relief="ridge")
frame_morph.pack(padx=4, pady=10, fill="both")

label_morph = tk.Label(frame_morph, text="Morph System", justify="left",
                       font=("Courier", 10), bg="#1e1e1e", fg="white")
label_morph.pack(padx=10, pady=10)

def aggiorna_gui_morph():
    sestina_txt = ", ".join(str(n) for n in morph["sestina"]) if morph["sestina"] else "—"
    extra = ""
    if morph["step_attivo"] == "terzina":
        extra = f"\n🎯 Terzina: {morph.get('terzina', [])}"
    elif morph["step_attivo"] == "secco":
        extra = f"\n🎯 Secco: {morph.get('secco', '—')}"
    testo = f"🌀 Sestine Magiche\n"
    testo += f"Blocco: {morph['blocco']} – Step: {morph['step']} – Colpo: {morph['colpo']}/6\n"
    testo += f"Tipo: {morph['step_attivo']} – Puntata: € {puntate_per_step.get(morph['step'],1)}\n"
    testo += f"Saldo: € {morph['saldo']:.2f}\n"
    testo += f"Sestina attiva: {sestina_txt}{extra}"
    label_morph.config(text=testo)

# 🔁 Gestione logica Morph
def calcola_sestina_iniziale(numeri):
    media = sum(numeri) / len(numeri)
    media = max(1, min(36, media))
    sestine = [(1, 6), (7, 12), (13, 18), (19, 24), (25, 30), (31, 36)]
    for s in sestine:
        if s[0] <= media <= s[1]:
            morph["sestina"] = list(range(s[0], s[1] + 1))
            morph["step_attivo"] = "sestina"
            break

def inserisci_esito(numero_uscito):
    try:
        numero_uscito = int(numero_uscito)
    except ValueError:
        return
    numeri_inseriti.append(numero_uscito)
    aggiorna_lista()

    global blocco_temp
    if morph["stato"] == "inattivo":
        blocco_temp.append(numero_uscito)
        if len(blocco_temp) == 5:
            morph["numeri_blocco"] = blocco_temp.copy()
            calcola_sestina_iniziale(blocco_temp)
            morph.update({
                "step": 1, "colpo": 0, "saldo": 0.0,
                "terzina": [], "secco": None, "stato": "in_corso"
            })
            blocco_temp.clear()
        aggiorna_gui_morph()
        return

    esito = False
    if morph["step_attivo"] == "sestina":
        esito = numero_uscito in morph["sestina"]
    elif morph["step_attivo"] == "terzina":
        esito = numero_uscito in morph.get("terzina", [])
    elif morph["step_attivo"] == "secco":
        esito = numero_uscito == morph.get("secco")
    esegui_colpo_morph(esito)
    aggiorna_gui_morph()

def esegui_colpo_morph(esito_vinto):
    if morph["step"] > 50:
        morph["stato"] = "concluso"
        return
    puntata = puntate_per_step.get(morph["step"], 1)
    morph["colpo"] += 1
    if morph["step_attivo"] == "sestina":
        costo = puntata
        vincita = puntata * 6 if esito_vinto else 0
    elif morph["step_attivo"] == "terzina":
        costo = puntata * 3
        vincita = puntata * 12 if esito_vinto else 0
    elif morph["step_attivo"] == "secco":
        costo = puntata
        vincita = puntata * 36 if esito_vinto else 0
    else:
        costo = vincita = 0
    morph["saldo"] += vincita - costo

    if esito_vinto or morph["saldo"] >= 0:
        termina_progressione(True)
    elif morph["colpo"] >= 6:
        passa_step_successivo()

def passa_step_successivo():
    morph["step"] += 1
    morph["colpo"] = 0
    if morph["step"] > 50:
        termina_progressione(False)
        return
    if morph["step_attivo"] == "sestina":
        morph["step_attivo"] = "terzina"
        morph["terzina"] = sorted(morph["sestina"])[-3:]
    elif morph["step_attivo"] == "terzina":
        media = sum(morph["numeri_blocco"]) / len(morph["numeri_blocco"])
        morph["secco"] = math.ceil(media)
        morph["step_attivo"] = "secco"
    elif morph["step_attivo"] == "secco":
        morph["step_attivo"] = "terzina"
        morph["terzina"] = sorted(morph["sestina"])[-3:]

def termina_progressione(vittoria):
    msg = (f"✅ Progressione completata allo step {morph['step']}.\nSaldo: € {morph['saldo']:.2f}"
           if vittoria else
           f"❌ Progressione fallita dopo 50 step.\nSaldo finale: € {morph['saldo']:.2f}")
    popup = tk.Toplevel(finestra)
    popup.title("Esito")
    popup.configure(bg=sfondo_base)
    popup.geometry("340x140")
    tk.Label(popup, text=msg, font=("Arial", 12), bg=sfondo_base, fg="white").pack(pady=(20, 10))

    def nuova():
        popup.destroy()
        morph.update({
            "blocco": morph["blocco"] + 1, "stato": "inattivo", "saldo": 0.0,
            "step": 1, "colpo": 0, "sestina": [], "terzina": [], "secco": None
        })
        aggiorna_gui_morph()

    tk.Button(popup, text="Nuovo blocco", command=nuova,
              bg="#5cb85c", fg="white", width=14).pack(pady=8)

# 🚀 Avvio app
aggiorna_cassa_display()
aggiorna_gui_morph()
finestra.mainloop()
