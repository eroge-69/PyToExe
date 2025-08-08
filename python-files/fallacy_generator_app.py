import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import random
import json
import os

# File di salvataggio per fallacie personalizzate
FALLACIES_FILE = "fallacies.json"

# Dizionario di fallacie e figure retoriche con descrizioni ed esempi
fallacies = {
    "Appello all'autorità": lambda x: f"Un esperto ha detto che '{x}', quindi deve essere vero.",
    "Argomento ad hominem": lambda x: f"Chi sostiene che '{x}' è una persona orribile, quindi non ha senso.",
    "Falsa causa": lambda x: f"Dopo che è accaduto '{x}', è successa una cosa negativa, quindi è colpa di '{x}'.",
    "Generalizzazione affrettata": lambda x: f"Una volta ho visto che '{x}', quindi è sempre così.",
    "Falso dilemma": lambda x: f"O accettiamo che '{x}' oppure tutto andrà in rovina.",
    "Ironia": lambda x: f"Oh certo, perché ovviamente '{x}' è la cosa più sensata del mondo...",
    "Iperbole": lambda x: f"È ovvio che '{x}' perché succede ogni singolo giorno della nostra vita!",
    "Metafora": lambda x: f"'{x}' è come un castello di sabbia destinato a crollare.",
    "Pendio scivoloso": lambda x: f"Se accettiamo che '{x}', allora presto saremo in una totale anarchia."
}

# Dizionario con spiegazioni ed esempi articolati
fallacy_descriptions = {
    "Appello all'autorità": "Si sostiene che qualcosa è vero solo perché lo afferma un'autorità, anche se non è competente nel campo specifico.\n\nEsempio: 'Il famoso attore sostiene che i vaccini sono pericolosi, quindi non dovremmo vaccinarci.'",
    "Argomento ad hominem": "Si attacca la persona invece dell'argomento da essa proposto.\n\nEsempio: 'Non possiamo fidarci della sua opinione sull'economia: ha divorziato tre volte.'",
    "Falsa causa": "Si presume una relazione causale inesistente tra due eventi.\n\nEsempio: 'Da quando ho comprato il nuovo telefono, ha iniziato a piovere ogni giorno.'",
    "Generalizzazione affrettata": "Si trae una conclusione generale da pochi esempi.\n\nEsempio: 'Ho incontrato due francesi scortesi, quindi tutti i francesi sono maleducati.'",
    "Falso dilemma": "Si presenta solo due opzioni come se fossero le uniche possibili.\n\nEsempio: 'O sei con noi, o sei contro di noi.'",
    "Ironia": "Si afferma il contrario di ciò che si intende comunicare, spesso in modo sarcastico.\n\nEsempio: 'Certo, arrivare in ritardo a un colloquio è il miglior modo per fare colpo.'",
    "Iperbole": "Si esagera in modo estremo per rafforzare un punto di vista.\n\nEsempio: 'Se non mi compri quel gioco, morirò!'",
    "Metafora": "Si paragona una cosa a un'altra per esprimere un concetto in modo figurato.\n\nEsempio: 'La sua mente è un labirinto senza uscita.'",
    "Pendio scivoloso": "Si sostiene che una piccola azione porterà inevitabilmente a conseguenze catastrofiche.\n\nEsempio: 'Se legalizziamo questa sostanza, la società degenererà completamente.'"
}

# Caricamento fallacie personalizzate
if os.path.exists(FALLACIES_FILE):
    with open(FALLACIES_FILE, "r", encoding="utf-8") as f:
        custom_data = json.load(f)
        for nome, dati in custom_data.items():
            fallacy_descriptions[nome] = dati["descrizione"]
            fallacies[nome] = lambda x, s=dati["struttura"]: s.replace("{x}", x)

# Funzione per salvare le fallacie personalizzate
def salva_fallacie_personalizzate():
    personalizzate = {
        nome: {
            "descrizione": fallacy_descriptions[nome],
            "struttura": struttura
        }
        for nome, struttura in strutture_custom.items()
    }
    with open(FALLACIES_FILE, "w", encoding="utf-8") as f:
        json.dump(personalizzate, f, indent=4, ensure_ascii=False)

strutture_custom = {}  # Contiene le strutture delle fallacie aggiunte

# Funzione per generare la nuova asserzione
def genera_asserzione():
    asserzione = entry_asserzione.get()
    fallacia = combo_fallacia.get()
    if asserzione and fallacia in fallacies:
        nuova_asserzione = fallacies[fallacia](asserzione)
        label_output.config(text=f"Asserzione generata:\n{nuova_asserzione}")
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, nuova_asserzione)
    else:
        label_output.config(text="Per favore inserisci un'asserzione e seleziona una fallacia o figura retorica.")

# Funzione per salvare il contenuto generato in un file
def salva_asserzione():
    contenuto = text_output.get("1.0", tk.END).strip()
    if contenuto:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(contenuto)

# Funzione per esportare tutte le descrizioni in un file
def esporta_descrizioni():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            for nome, descrizione in fallacy_descriptions.items():
                f.write(f"{nome}:\n{descrizione}\n\n")

# Funzione per modificare manualmente l'asserzione generata
def modifica_asserzione():
    text_output.config(state=tk.NORMAL)
    text_output.focus_set()

# Funzione per mostrare la descrizione della fallacia selezionata
def mostra_descrizione():
    fallacia = combo_fallacia.get()
    descrizione = fallacy_descriptions.get(fallacia, "Descrizione non disponibile.")
    messagebox.showinfo("Descrizione della fallacia", f"{fallacia}:\n\n{descrizione}")

# Funzione per mostrare tutte le descrizioni
def mostra_tutte_le_descrizioni():
    tutte = ""
    for nome, descrizione in fallacy_descriptions.items():
        tutte += f"{nome}:\n{descrizione}\n\n"
    finestra_descrizioni = tk.Toplevel(root)
    finestra_descrizioni.title("Tutte le Fallacie")
    text_box = tk.Text(finestra_descrizioni, wrap="word", width=90, height=30)
    text_box.insert(tk.END, tutte)
    text_box.config(state=tk.DISABLED)
    text_box.pack(padx=10, pady=10)

# Funzione per aggiungere una nuova fallacia manualmente
def aggiungi_fallacia():
    nome = simpledialog.askstring("Nuova fallacia", "Nome della fallacia o figura retorica:")
    if nome and nome.strip():
        descrizione = simpledialog.askstring("Descrizione", f"Descrizione di '{nome}':")
        esempio = simpledialog.askstring("Esempio", f"Esempio articolato per '{nome}':")
        struttura = simpledialog.askstring("Struttura frase", f"Come trasformare un'asserzione con '{nome}'? Usa {{x}} per l'asserzione base:")
        if descrizione and struttura:
            fallacy_descriptions[nome] = descrizione + (f"\n\nEsempio: {esempio}" if esempio else "")
            fallacies[nome] = lambda x, s=struttura: s.replace("{x}", x)
            strutture_custom[nome] = struttura
            combo_fallacia['values'] = list(fallacies.keys())
            salva_fallacie_personalizzate()
            messagebox.showinfo("Fallacia aggiunta", f"'{nome}' è stata aggiunta con successo.")

# Creazione GUI
root = tk.Tk()
root.title("Generatore di Asserzioni Fallaci")
root.geometry("700x750")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

label1 = ttk.Label(frame, text="Inserisci un'asserzione iniziale:")
label1.pack(pady=5)

entry_asserzione = ttk.Entry(frame, width=80)
entry_asserzione.pack(pady=5)

label2 = ttk.Label(frame, text="Seleziona una fallacia o figura retorica:")
label2.pack(pady=5)

combo_fallacia = ttk.Combobox(frame, values=list(fallacies.keys()), width=50)
combo_fallacia.pack(pady=5)

button_descrizione = ttk.Button(frame, text="Mostra descrizione", command=mostra_descrizione)
button_descrizione.pack(pady=5)

button_tutte = ttk.Button(frame, text="Mostra tutte le descrizioni", command=mostra_tutte_le_descrizioni)
button_tutte.pack(pady=5)

button_export = ttk.Button(frame, text="Esporta descrizioni su file", command=esporta_descrizioni)
button_export.pack(pady=5)

button_aggiungi = ttk.Button(frame, text="Aggiungi nuova fallacia", command=aggiungi_fallacia)
button_aggiungi.pack(pady=5)

button_generare = ttk.Button(frame, text="Genera nuova asserzione", command=genera_asserzione)
button_generare.pack(pady=10)

label_output = ttk.Label(frame, text="", wraplength=500, justify="left")
label_output.pack(pady=5)

text_output = tk.Text(frame, height=5, width=70, wrap="word", state=tk.NORMAL)
text_output.pack(pady=5)

button_modifica = ttk.Button(frame, text="Modifica", command=modifica_asserzione)
button_modifica.pack(pady=5)

button_salva = ttk.Button(frame, text="Salva su file", command=salva_asserzione)
button_salva.pack(pady=5)

root.mainloop()
