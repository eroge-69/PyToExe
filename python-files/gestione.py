# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 09:29:18 2025

@author: alberto.salvato.ext
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
from datetime import datetime, timedelta

MAGAZZINO_FILE = "magazzino_aghi.csv"
MOVIMENTI_FILE = "movimenti_aghi.csv"


# Funzioni per gestione magazzino
def carica_magazzino():
    magazzino = []
    try:
        with open(MAGAZZINO_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['quantita'] = int(row['quantita'])
                magazzino.append(row)
    except FileNotFoundError:
        pass
    return magazzino

def salva_magazzino(magazzino):
    with open(MAGAZZINO_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['tipo', 'lotto', 'quantita', 'scadenza']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ago in magazzino:
            writer.writerow(ago)

def aggiorna_tabella(filtro_tipo="", filtro_lotto=""):
    for row in tree.get_children():
        tree.delete(row)
    oggi = datetime.today()
    magazzino_sorted = sorted(magazzino, key=lambda x: x['scadenza'])
    for ago in magazzino_sorted:
        if filtro_tipo and filtro_tipo.lower() not in ago['tipo'].lower():
            continue
        if filtro_lotto and filtro_lotto.lower() not in ago['lotto'].lower():
            continue
        scad = datetime.strptime(ago['scadenza'], "%Y-%m-%d")
        if scad < oggi:
            stato = "SCADUTO"
            tag = "scaduto"
        elif scad - oggi <= timedelta(days=30):
            stato = "PROSSIMO"
            tag = "prossimo"
        else:
            stato = ""
            tag = "valido"
        tree.insert("", "end", values=(ago['tipo'], ago['lotto'], ago['quantita'], ago['scadenza'], stato), tags=(tag,))

    # Colori per evidenziare
    tree.tag_configure("scaduto", background="lightcoral")
    tree.tag_configure("prossimo", background="orange")
    tree.tag_configure("valido", background="white")
        
def registra_movimento(ago, quantita, operatore, motivazione):
    # Salva la rimozione su file CSV
    try:
        with open(MOVIMENTI_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['tipo', 'lotto', 'quantita', 'operatore', 'motivazione', 'data']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Se il file è vuoto, scrive l'intestazione
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({
                'tipo': ago['tipo'],
                'lotto': ago['lotto'],
                'quantita': quantita,
                'operatore': operatore,
                'motivazione': motivazione,
                'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvare il movimento: {e}")

def aggiungi_aghi_gui():
    tipo = simpledialog.askstring("Tipo", "Inserisci il tipo di ago:")
    if not tipo: return
    lotto = simpledialog.askstring("Lotto", "Inserisci il numero di lotto:")
    if not lotto: return
    quantita = simpledialog.askinteger("Quantità", "Inserisci la quantità:")
    if quantita is None: return
    scadenza = simpledialog.askstring("Scadenza", "Inserisci la scadenza (AAAA-MM-GG):")
    try:
        datetime.strptime(scadenza, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Errore", "Formato data non valido!")
        return
    magazzino.append({"tipo": tipo, "lotto": lotto, "quantita": quantita, "scadenza": scadenza})
    salva_magazzino(magazzino)
    aggiorna_tabella()
"""
def rimuovi_aghi_gui():
    lotto = simpledialog.askstring("Lotto", "Inserisci il numero di lotto da rimuovere:")
    if not lotto: return
    quantita = simpledialog.askinteger("Quantità", "Inserisci la quantità da rimuovere:")
    if quantita is None: return
    operatore = simpledialog.askstring("Operatore", "Inserisci il nome dell'operatore:")
    if not operatore: return
    motivazione = simpledialog.askstring("Motivazione", "Inserisci la motivazione dell'utilizzo:")
    if not motivazione: return
    if quantita is None: return
    for ago in magazzino:
        if ago['lotto'] == lotto:
            if ago['quantita'] >= quantita:
                ago['quantita'] -= quantita
                registra_movimento(ago, quantita, operatore, motivazione)
                if ago['quantita'] == 0:
                    magazzino.remove(ago)
                salva_magazzino(magazzino)
                aggiorna_tabella()
                return
            else:
                messagebox.showerror("Errore", "Quantità insufficiente nel lotto!")
                return
    messagebox.showerror("Errore", "Lotto non trovato!")
  """ 
def rimuovi_aghi_gui():
    if not magazzino:
        messagebox.showinfo("Info", "Magazzino vuoto!")
        return

    # Finestra popup
    rimuovi_win = tk.Toplevel(root)
    rimuovi_win.title("Utilizzo Ago")
    rimuovi_win.geometry("550x350")
    rimuovi_win.resizable(True, True)

    # Variabili
    lotto_var = tk.StringVar()

    # Lotto
    tk.Label(rimuovi_win, text="Seleziona lotto:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    lotto_cb = ttk.Combobox(rimuovi_win, textvariable=lotto_var,
                            values=[ago['lotto'] for ago in magazzino], width=30)
    lotto_cb.grid(row=0, column=1, padx=10, pady=10, sticky='w')

    # Quantità
    tk.Label(rimuovi_win, text="Quantità:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    quantita_entry = tk.Entry(rimuovi_win, width=10)
    quantita_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    # Operatore
    tk.Label(rimuovi_win, text="Operatore:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    operatore_entry = tk.Entry(rimuovi_win, width=30)
    operatore_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

    # Motivazione
    tk.Label(rimuovi_win, text="Motivazione:").grid(row=3, column=0, padx=10, pady=10, sticky='ne')
    motivazione_text = tk.Text(rimuovi_win, width=40, height=6)
    motivazione_text.grid(row=3, column=1, padx=10, pady=10, sticky='w')

    # Funzione di conferma rimozione
    def conferma_rimozione():
        lotto = lotto_var.get()
        try:
            quantita = int(quantita_entry.get())
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un numero valido per la quantità")
            return
        operatore = operatore_entry.get().strip()
        motivazione = motivazione_text.get("1.0", tk.END).strip()

        if not lotto or not operatore or not motivazione:
            messagebox.showerror("Errore", "Tutti i campi sono obbligatori")
            return

        for ago in magazzino:
            if ago['lotto'] == lotto:
                if ago['quantita'] >= quantita:
                    ago['quantita'] -= quantita
                    registra_movimento(ago, quantita, operatore, motivazione)
                    if ago['quantita'] == 0:
                        magazzino.remove(ago)
                    salva_magazzino(magazzino)
                    aggiorna_tabella()
                    rimuovi_win.destroy()
                    return
                else:
                    messagebox.showerror("Errore", "Quantità insufficiente nel lotto!")
                    return
        messagebox.showerror("Errore", "Lotto non trovato!")

    # Pulsante conferma
    tk.Button(rimuovi_win, text="Conferma", command=conferma_rimozione).grid(
        row=4, column=0, columnspan=2, pady=15
    )

def filtra_tabella():
    filtro_tipo = entry_tipo.get()
    filtro_lotto = entry_lotto.get()
    aggiorna_tabella(filtro_tipo, filtro_lotto)
    
def visualizza_movimenti():
    # Crea una nuova finestra
    mov_window = tk.Toplevel(root)
    mov_window.title("Storico Movimenti")
    mov_window.geometry("1500x600")

    columns = ("tipo", "lotto", "quantita", "operatore", "motivazione", "data")
    tree_mov = ttk.Treeview(mov_window, columns=columns, show="headings")
    for col in columns:
        tree_mov.heading(col, text=col.capitalize())
    tree_mov.pack(expand=True, fill='both')

    # Carica i movimenti dal file CSV
    try:
        with open(MOVIMENTI_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tree_mov.insert("", "end", values=(
                    row['tipo'], row['lotto'], row['quantita'], 
                    row['operatore'], row['motivazione'], row['data']
                ))
    except FileNotFoundError:
        messagebox.showinfo("Info", "Nessun movimento registrato.")

# Creazione finestra principale
root = tk.Tk()
root.title("Gestione Magazzino Aghi")
root.geometry("1500x600")

magazzino = carica_magazzino()

# Filtro
frame_filtro = tk.Frame(root)
frame_filtro.pack(pady=5)
tk.Label(frame_filtro, text="Filtra per tipo:").pack(side='left')
entry_tipo = tk.Entry(frame_filtro)
entry_tipo.pack(side='left', padx=5)
tk.Label(frame_filtro, text="Filtra per lotto:").pack(side='left')
entry_lotto = tk.Entry(frame_filtro)
entry_lotto.pack(side='left', padx=5)
tk.Button(frame_filtro, text="Applica filtro", command=filtra_tabella).pack(side='left', padx=5)
tk.Button(frame_filtro, text="Reset filtro", command=lambda: aggiorna_tabella()).pack(side='left', padx=5)


# Tabella con Treeview
columns = ("tipo", "lotto", "quantita", "scadenza", "stato")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col.capitalize())
tree.pack(expand=True, fill='both')

# Pulsanti
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)
tk.Button(frame_btn, text="Aggiungi Ago", command=aggiungi_aghi_gui).pack(side='left', padx=5)
tk.Button(frame_btn, text="Rimuovi Ago", command=rimuovi_aghi_gui).pack(side='left', padx=5)
tk.Button(frame_btn, text="Aggiorna Tabella", command=aggiorna_tabella).pack(side='left', padx=5)
tk.Button(frame_btn, text="Visualizza Movimenti", command=visualizza_movimenti).pack(side='left', padx=5)

aggiorna_tabella()
root.mainloop()