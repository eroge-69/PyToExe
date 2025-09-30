import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, ttk

# Flag globale per fermare il thread
stop_flag = False

def scegli_cartella():
    """Apre un dialog di Explorer per scegliere la cartella da analizzare"""
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Seleziona la cartella da analizzare")

def organizza_file(cartella_base, finestra, barra, testo_log, btn_annulla, btn_fine):
    """Sposta i file in sottocartelle basate sull'estensione e rimuove cartelle vuote"""
    global stop_flag
    file_totali = sum(len(files) for _, _, files in os.walk(cartella_base))
    progresso = 0

    for root_dir, dirs, files in os.walk(cartella_base, topdown=False):
        for nome_file in files:
            if stop_flag:
                testo_log.insert(tk.END, "\n⏹ Operazione annullata dall'utente.\n")
                btn_annulla.pack_forget()
                btn_fine.pack(side="left", padx=5)
                return  

            percorso_file = os.path.join(root_dir, nome_file)
            if not os.path.isfile(percorso_file):
                continue  

            estensione = os.path.splitext(nome_file)[1].lower().strip(".")
            if estensione == "":
                estensione = "senza_estensione"

            cartella_dest = os.path.join(cartella_base, estensione)
            os.makedirs(cartella_dest, exist_ok=True)

            nuovo_percorso = os.path.join(cartella_dest, nome_file)

            base_nome, est = os.path.splitext(nome_file)
            contatore = 1
            while os.path.exists(nuovo_percorso):
                nuovo_percorso = os.path.join(
                    cartella_dest, f"{base_nome}_{contatore}{est}"
                )
                contatore += 1

            try:
                shutil.move(percorso_file, nuovo_percorso)
                testo_log.insert(tk.END, f"✔ Spostato: {nome_file} → {estensione}\n")
            except PermissionError:
                testo_log.insert(tk.END, f"❌ Permesso negato: {percorso_file}\n")

            progresso += 1
            barra["value"] = (progresso / file_totali) * 100
            finestra.update_idletasks()

    for root_dir, dirs, _ in os.walk(cartella_base, topdown=False):
        for d in dirs:
            if stop_flag:
                return  
            percorso_dir = os.path.join(root_dir, d)
            try:
                os.rmdir(percorso_dir)
                testo_log.insert(tk.END, f"🗑 Rimossa cartella vuota: {percorso_dir}\n")
            except OSError:
                pass  

    testo_log.insert(tk.END, "\n✅ Operazione completata con successo!\n")
    btn_annulla.pack_forget()
    btn_fine.pack(side="left", padx=5)

def avvia_thread(cartella, finestra, barra, testo_log, btn_annulla, btn_fine):
    global stop_flag
    stop_flag = False
    thread = threading.Thread(target=organizza_file, args=(cartella, finestra, barra, testo_log, btn_annulla, btn_fine))
    thread.daemon = True
    thread.start()

def annulla_operazione():
    global stop_flag
    stop_flag = True

def avvia_organizzazione(cartella):
    finestra = tk.Tk()
    finestra.title("Organizzazione File")
    finestra.geometry("650x450")

    tk.Label(finestra, text=f"Cartella: {cartella}", anchor="w").pack(fill="x", padx=10, pady=5)

    barra = ttk.Progressbar(finestra, orient="horizontal", length=600, mode="determinate")
    barra.pack(padx=10, pady=10)

    testo_log = tk.Text(finestra, wrap="word", height=15)
    testo_log.pack(fill="both", expand=True, padx=10, pady=10)

    btn_frame = tk.Frame(finestra)
    btn_frame.pack(pady=5)

    btn_annulla = tk.Button(btn_frame, text="⏹ Annulla", command=annulla_operazione, bg="red", fg="white")
    btn_annulla.pack(side="left", padx=5)

    btn_fine = tk.Button(btn_frame, text="Fine", command=finestra.destroy, bg="green", fg="white")

    finestra.after(200, lambda: avvia_thread(cartella, finestra, barra, testo_log, btn_annulla, btn_fine))
    finestra.mainloop()

if __name__ == "__main__":
    cartella = scegli_cartella()
    if cartella:
        avvia_organizzazione(cartella)
    else:
        print("Nessuna cartella selezionata.")
