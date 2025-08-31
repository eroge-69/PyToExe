import tkinter as tk
from tkinter import messagebox

# Parametri regime forfettario
COEFF_REDDITIVITA = 0.78  # 78%
ALIQUOTA_IMPOSTA = 0.05   # 5% per primi 5 anni
ALIQUOTA_INPS = 0.2607    # 26,07% Gestione Separata

def lordo_to_netto(lordo):
    """Calcola il netto partendo dal lordo (fatturato)."""
    reddito_lordo = lordo * COEFF_REDDITIVITA
    contributi_inps = reddito_lordo * ALIQUOTA_INPS
    reddito_imponibile = reddito_lordo - contributi_inps
    imposta = reddito_imponibile * ALIQUOTA_IMPOSTA
    netto = lordo - contributi_inps - imposta
    return netto, contributi_inps, imposta

def netto_to_lordo(netto):
    """Calcola il lordo necessario per ottenere un certo netto."""
    fattore_interno = ALIQUOTA_INPS + (1 - ALIQUOTA_INPS) * ALIQUOTA_IMPOSTA
    fattore = 1 - COEFF_REDDITIVITA * fattore_interno
    lordo = netto / fattore
    netto_calcolato, contributi, imposta = lordo_to_netto(lordo)
    return lordo, contributi, imposta

def calcola():
    """Gestisce il calcolo in base all'opzione selezionata."""
    try:
        importo = float(entry_importo.get())
        if importo <= 0:
            messagebox.showerror("Errore", "Inserisci un importo positivo.")
            return
        scelta = var_scelta.get()
        result_text.delete(1.0, tk.END)  # Pulisce l'area di testo

        if scelta == 1:  # Lordo a netto
            netto, contributi, imposta = lordo_to_netto(importo)
            result_text.insert(tk.END, f"Risultati:\n"
                                      f"Reddito lordo imponibile: {importo * COEFF_REDDITIVITA:.2f} €\n"
                                      f"Contributi INPS: {contributi:.2f} €\n"
                                      f"Imposta sostitutiva: {imposta:.2f} €\n"
                                      f"Netto finale: {netto:.2f} €")
        elif scelta == 2:  # Netto a lordo
            lordo, contributi, imposta = netto_to_lordo(importo)
            result_text.insert(tk.END, f"Risultati:\n"
                                      f"Lordo da fatturare: {lordo:.2f} €\n"
                                      f"Contributi INPS: {contributi:.2f} €\n"
                                      f"Imposta sostitutiva: {imposta:.2f} €\n"
                                      f"Netto risultante: {importo:.2f} € (verifica)")
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un importo numerico valido.")

# Creazione della finestra principale
root = tk.Tk()
root.title("Calcolatore Regime Forfettario - Web Designer")
root.geometry("400x500")

# Variabile per la scelta (lordo->netto o netto->lordo)
var_scelta = tk.IntVar(value=1)

# Elementi dell'interfaccia
tk.Label(root, text="Calcolatore Forfettario 2025", font=("Arial", 14, "bold")).pack(pady=10)

# Selezione tipo calcolo
tk.Radiobutton(root, text="Da lordo a netto", variable=var_scelta, value=1).pack(anchor="w", padx=20)
tk.Radiobutton(root, text="Da netto a lordo", variable=var_scelta, value=2).pack(anchor="w", padx=20)

# Campo per l'importo
tk.Label(root, text="Inserisci importo (€):").pack(pady=10)
entry_importo = tk.Entry(root)
entry_importo.pack()

# Pulsante Calcola
tk.Button(root, text="Calcola", command=calcola, bg="lightgreen").pack(pady=20)

# Area per i risultati
result_text = tk.Text(root, height=6, width=40)
result_text.pack(pady=10)

# Avvio dell'applicazione
root.mainloop()