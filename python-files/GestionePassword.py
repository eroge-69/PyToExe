import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import base64
import sys

# --- Configurazione Applicazione ---
# ATTENZIONE: Password e dati NON sono memorizzati in modo sicuro! Questo è a scopo didattico.
PASSWORD_SEGRETA = "Stefano1974" # Password per l'accesso all'app

NOME_FILE_DATI = os.path.join(os.path.expanduser("~"), "Desktop", "dati_applicativi.json")

# Dizionario per memorizzare i dati:
# Chiave=Nome Categoria, Valore=Lista di Dizionari, dove ogni dizionario è {'email': '...', 'password': '...'}
dati_categorie = {}

attuale_categoria_selezionata = None
# Riferimento alla finestra dei dettagli, per poterla chiudere se già aperta
dettagli_window = None 

# --- Funzioni di Offuscamento ---

def offusca_singolo_dato(dato_stringa):
    """Metodo semplicissimo per offuscare una SINGOLA stringa (email o password)."""
    return dato_stringa[::-1]

def de_offusca_singolo_dato(dato_offuscato_stringa):
    """De-offusca una SINGOLA stringa invertendola."""
    if isinstance(dato_offuscato_stringa, str):
        return dato_offuscato_stringa[::-1]
    return ""

def offusca_contenuto_file(input_stringa):
    """
    Offusca una stringa (come l'intero JSON) usando Base64 e una semplice permutazione.
    QUESTO È PER L'INTERO CONTENUTO DEL FILE.
    """
    encoded_bytes = base64.b64encode(input_stringa.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')

    if len(encoded_string) > 1:
        permutated_string = encoded_string[1:] + encoded_string[0]
    else:
        permutated_string = encoded_string
        
    return permutated_string

def de_offusca_contenuto_file(offuscated_string):
    """
    De-offusca una stringa (come l'intero JSON) ripristinando la permutazione e decodificando Base64.
    QUESTO È PER L'INTERO CONTENUTO DEL FILE.
    """
    if not offuscated_string:
        return ""

    if len(offuscated_string) > 1:
        unpermutated_string = offuscated_string[-1] + offuscated_string[:-1]
    else:
        unpermutated_string = offuscated_string

    try:
        decoded_bytes = base64.b64decode(unpermutated_string.encode('utf-8'))
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        print(f"Errore durante la decodifica Base64 del file: {e}. Il contenuto potrebbe essere corrotto.")
        return ""

# --- Funzioni di Logica Dati ---

def inizializza_dati_categorie():
    """Inizializza o aggiorna la struttura dei dati con le categorie predefinite."""
    global dati_categorie
    categorie_predefinite = [
        "Instagram", "Facebook", "Netflix", "TikTok", "X (Twitter)",
        "Gmail", "LinkedIn", "Amazon", "PayPal", "Spotify", "Discord", "Steam",
        "Minecraft Premium", "Google"
    ]
    
    for categoria in categorie_predefinite:
        if categoria not in dati_categorie:
            dati_categorie[categoria] = [] 

# --- Funzioni per la Persistenza dei Dati (Caricamento/Salvataggio File) ---

def carica_dati_da_file():
    """Carica i dati dal file (offuscato con Base64 e permutazione) all'avvio dell'applicazione."""
    global dati_categorie
    if os.path.exists(NOME_FILE_DATI):
        try:
            with open(NOME_FILE_DATI, 'r', encoding='utf-8') as file:
                contenuto_offuscato_da_file = file.read()
            
            if not contenuto_offuscato_da_file:
                print(f"Il file '{NOME_FILE_DATI}' è vuoto. Inizializzazione nuova struttura.")
                dati_categorie = {}
            else:
                contenuto_de_offuscato_json_string = de_offusca_contenuto_file(contenuto_offuscato_da_file)
                
                if not contenuto_de_offuscato_json_string:
                    raise ValueError("Contenuto del file de-offuscato non valido o vuoto.")

                dati_caricati = json.loads(contenuto_de_offuscato_json_string)
                
                if isinstance(dati_caricati, dict):
                    dati_categorie = dati_caricati
                    print(f"Dati caricati e de-offuscati con successo da '{NOME_FILE_DATI}'.")
                else:
                    messagebox.showwarning("Formato Dati", "Il contenuto de-offuscato non è nel formato JSON atteso. Inizializzazione nuova struttura.")
                    dati_categorie = {}
        except json.JSONDecodeError:
            messagebox.showerror("Errore Caricamento", f"Errore nella lettura del contenuto de-offuscato del file '{NOME_FILE_DATI}'. Potrebbe essere corrotto. Inizializzazione nuova struttura.")
            dati_categorie = {}
        except ValueError as ve:
            messagebox.showerror("Errore Caricamento", f"Errore durante la de-offuscazione o il formato dati: {ve}. Inizializzazione nuova struttura.")
            dati_categorie = {}
        except Exception as e:
            messagebox.showerror("Errore Caricamento", f"Si è verificato un errore inaspettato durante il caricamento e de-offuscamento: {e}")
            dati_categorie = {}
    else:
        print(f"File '{NOME_FILE_DATI}' non trovato. Sarà creato al primo salvataggio.")
    
    inizializza_dati_categorie()

def salva_dati_su_file():
    """Salva i dati attuali nel dizionario, offuscando l'intero contenuto JSON prima di scriverlo."""
    try:
        dati_json_stringa = json.dumps(dati_categorie, indent=4, ensure_ascii=False)
        contenuto_da_salvare_offuscato = offusca_contenuto_file(dati_json_stringa)
        
        cartella_dati = os.path.dirname(NOME_FILE_DATI)
        if not os.path.exists(cartella_dati):
            os.makedirs(cartella_dati)

        with open(NOME_FILE_DATI, 'w', encoding='utf-8') as file:
            file.write(contenuto_da_salvare_offuscato)
        print(f"Dati salvati e offuscati con successo su '{NOME_FILE_DATI}'.")
    except Exception as e:
        messagebox.showerror("Errore Salvataggio", f"Errore durante il salvataggio e offuscamento dei dati su '{NOME_FILE_DATI}': {e}")

# --- Funzioni per la GUI ---

def centra_finestra(window):
    """Centra la finestra Tkinter sullo schermo."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def mostra_frame(frame_da_mostrare):
    """Nasconde tutti i frame principali e mostra solo quello specificato."""
    for frame in [accesso_frame, categorie_frame]: 
        frame.pack_forget()
    frame_da_mostrare.pack(expand=True, fill='both')

def toggle_password_visibility():
    """Mostra o nasconde la password nel campo di input."""
    if entry_password.cget('show') == '*':
        entry_password.config(show='') # Mostra i caratteri
        btn_toggle_password.config(text="Nascondi Password")
    else:
        entry_password.config(show='*') # Nasconde i caratteri con asterischi
        btn_toggle_password.config(text="Mostra Password")

def verifica_password():
    """Verifica la password inserita dall'utente per l'accesso."""
    password_inserita = entry_password.get()
    if password_inserita == PASSWORD_SEGRETA:
        messagebox.showinfo("Successo", "Accesso consentito!")
        entry_password.delete(0, tk.END)
        # Resetta la visualizzazione della password a nascosta per la prossima volta
        entry_password.config(show='*') 
        btn_toggle_password.config(text="Mostra Password")
        
        combobox_categorie['values'] = list(dati_categorie.keys())
        combobox_categorie.set("Seleziona qui")
        
        mostra_frame(categorie_frame)
    else:
        messagebox.showerror("Errore", "Password errata. Riprova.")
        entry_password.delete(0, tk.END)
        # Resetta la visualizzazione della password a nascosta
        entry_password.config(show='*')
        btn_toggle_password.config(text="Mostra Password")


def apri_gestione_dati_categoria():
    """
    Funzione per aprire la nuova finestra di gestione dei dati multipli per una categoria.
    """
    global attuale_categoria_selezionata, dettagli_window

    categoria_selezionata = combobox_categorie.get()
    if not categoria_selezionata or categoria_selezionata not in dati_categorie:
        messagebox.showwarning("Selezione", "Seleziona una categoria valida dal menu a tendina.")
        return

    attuale_categoria_selezionata = categoria_selezionata

    if dettagli_window and dettagli_window.winfo_exists():
        dettagli_window.destroy()

    dettagli_window = tk.Toplevel(root)
    dettagli_window.title(f"Dettagli: {attuale_categoria_selezionata}")
    dettagli_window.geometry("600x450")
    centra_finestra(dettagli_window)

    lbl_titolo = tk.Label(dettagli_window, text=f"Dati per '{attuale_categoria_selezionata}'", font=("Arial", 14, "bold"))
    lbl_titolo.pack(pady=10)

    input_frame = tk.Frame(dettagli_window)
    input_frame.pack(pady=10)

    lbl_email_input = tk.Label(input_frame, text="Email:", font=("Arial", 10))
    lbl_email_input.grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nuova_email = tk.Entry(input_frame, width=35, font=("Arial", 10))
    entry_nuova_email.grid(row=0, column=1, padx=5, pady=2)

    lbl_password_input = tk.Label(input_frame, text="Password:", font=("Arial", 10))
    lbl_password_input.grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_nuova_password = tk.Entry(input_frame, width=35, font=("Arial", 10))
    entry_nuova_password.grid(row=1, column=1, padx=5, pady=2)

    btn_aggiungi_dato = tk.Button(input_frame, text="Aggiungi Credenziali", 
                                  command=lambda: aggiungi_credenziali(entry_nuova_email, entry_nuova_password, tree), 
                                  font=("Arial", 10), width=20)
    btn_aggiungi_dato.grid(row=2, column=0, columnspan=2, pady=10)

    scrollbar = ttk.Scrollbar(dettagli_window, orient="vertical")
    tree = ttk.Treeview(dettagli_window, columns=("Email", "Password"), show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)

    tree.heading("Email", text="Email")
    tree.heading("Password", text="Password")
    tree.column("Email", width=250, anchor="w")
    tree.column("Password", width=250, anchor="w")

    tree.pack(fill="both", expand=True, padx=10, pady=5)
    scrollbar.pack(side="right", fill="y")

    def on_tree_select(event):
        selected_item = tree.selection()
        if selected_item:
            item_values = tree.item(selected_item[0], 'values')
            entry_nuova_email.delete(0, tk.END)
            entry_nuova_email.insert(0, item_values[0])
            entry_nuova_password.delete(0, tk.END)
            entry_nuova_password.insert(0, item_values[1])
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    btn_frame = tk.Frame(dettagli_window)
    btn_frame.pack(pady=10)

    btn_modifica = tk.Button(btn_frame, text="Modifica Selezionato", 
                             command=lambda: modifica_credenziali(tree, entry_nuova_email, entry_nuova_password), 
                             font=("Arial", 10), width=20)
    btn_modifica.pack(side="left", padx=5)

    btn_elimina = tk.Button(btn_frame, text="Elimina Selezionato", 
                            command=lambda: elimina_credenziali(tree), 
                            font=("Arial", 10), width=20)
    btn_elimina.pack(side="left", padx=5)

    carica_dati_treeview(tree, attuale_categoria_selezionata)

def carica_dati_treeview(tree_widget, categoria):
    """Carica i dati della categoria nel Treeview specificato."""
    for item in tree_widget.get_children():
        tree_widget.delete(item)
    
    for idx, credenziale_set in enumerate(dati_categorie[categoria]):
        email = de_offusca_singolo_dato(credenziale_set['email'])
        password = de_offusca_singolo_dato(credenziale_set['password'])
        tree_widget.insert("", "end", iid=idx, values=(email, password)) 

def aggiungi_credenziali(entry_email, entry_password, tree_widget):
    """Aggiunge un nuovo set di credenziali alla categoria attuale."""
    global attuale_categoria_selezionata
    email = entry_email.get().strip()
    password = entry_password.get().strip()

    if not email or not password:
        messagebox.showwarning("Input Errato", "Email e Password non possono essere vuote.")
        return
    
    for credenziale in dati_categorie[attuale_categoria_selezionata]:
        if isinstance(credenziale, dict) and de_offusca_singolo_dato(credenziale.get('email', '')) == email:
            messagebox.showwarning("Duplicato", "Credenziali con questa email esistono già per questa categoria.")
            return

    nuovo_set = {'email': offusca_singolo_dato(email), 'password': offusca_singolo_dato(password)}
    dati_categorie[attuale_categoria_selezionata].append(nuovo_set)
    salva_dati_su_file()

    messagebox.showinfo("Aggiunto", "Credenziali aggiunte con successo!")
    entry_email.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    carica_dati_treeview(tree_widget, attuale_categoria_selezionata)

def modifica_credenziali(tree_widget, entry_email, entry_password):
    """Modifica il set di credenziali selezionato nel Treeview."""
    global attuale_categoria_selezionata
    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Selezione", "Seleziona un elemento da modificare.")
        return

    idx_da_modificare = int(selected_item[0]) 

    nuova_email = entry_email.get().strip()
    nuova_password = entry_password.get().strip()

    if not nuova_email or not nuova_password:
        messagebox.showwarning("Input Errato", "Email e Password non possono essere vuote per la modifica.")
        return
    
    for i, credenziale in enumerate(dati_categorie[attuale_categoria_selezionata]):
        if isinstance(credenziale, dict) and i != idx_da_modificare and de_offusca_singolo_dato(credenziale.get('email', '')) == nuova_email:
            messagebox.showwarning("Duplicato", "La nuova email esiste già in un altro record per questa categoria.")
            return

    dati_categorie[attuale_categoria_selezionata][idx_da_modificare]['email'] = offusca_singolo_dato(nuova_email)
    dati_categorie[attuale_categoria_selezionata][idx_da_modificare]['password'] = offusca_singolo_dato(nuova_password)
    
    salva_dati_su_file()
    messagebox.showinfo("Modificato", "Credenziali modificate con successo!")
    
    entry_email.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    carica_dati_treeview(tree_widget, attuale_categoria_selezionata) 
    tree_widget.selection_remove(selected_item[0])

def elimina_credenziali(tree_widget):
    """Elimina il set di credenziali selezionato dal Treeview."""
    global attuale_categoria_selezionata
    selected_item = tree_widget.selection()
    if not selected_item:
        messagebox.showwarning("Selezione", "Seleziona un elemento da eliminare.")
        return
    
    if messagebox.askyesno("Conferma Eliminazione", "Sei sicuro di voler eliminare le credenziali selezionate? Questa operazione è irreversibile."):
        idx_da_eliminare = int(selected_item[0])
        del dati_categorie[attuale_categoria_selezionata][idx_da_eliminare]
        
        salva_dati_su_file()
        messagebox.showinfo("Eliminato", "Credenziali eliminate con successo!")
        carica_dati_treeview(tree_widget, attuale_categoria_selezionata)

# --- Configurazione della Finestra Principale (Root Window) ---
root = tk.Tk()
root.title("Gestore Credenziali Personali")
root.geometry("500x400")
root.resizable(False, False)

# --- Frame di Accesso (Login) ---
accesso_frame = tk.Frame(root)
lbl_titolo_accesso = tk.Label(accesso_frame, text="Benvenuto!\nInserisci la Password per accedere", font=("Arial", 16, "bold"))
lbl_titolo_accesso.pack(pady=40)
lbl_password = tk.Label(accesso_frame, text="Password:", font=("Arial", 12))
lbl_password.pack(pady=5)

# Utilizzo di un Frame per allineare campo password e pulsante
password_input_frame = tk.Frame(accesso_frame)
password_input_frame.pack(pady=5)

entry_password = tk.Entry(password_input_frame, show="*", width=30, font=("Arial", 12))
entry_password.pack(side="left", padx=(0, 5)) # Un po' di padding a destra

# Pulsante per mostrare/nascondere la password
btn_toggle_password = tk.Button(password_input_frame, text="Mostra Password", 
                                command=toggle_password_visibility, font=("Arial", 9))
btn_toggle_password.pack(side="left")

entry_password.bind("<Return>", lambda event=None: verifica_password())
btn_accedi = tk.Button(accesso_frame, text="Accedi", command=verifica_password, font=("Arial", 12), width=15, height=2)
btn_accedi.pack(pady=20)

# --- Frame Categorie Principale ---
categorie_frame = tk.Frame(root)
lbl_titolo_categorie = tk.Label(categorie_frame, text="Seleziona una Categoria:", font=("Arial", 16, "bold"))
lbl_titolo_categorie.pack(pady=20)
combobox_categorie = ttk.Combobox(categorie_frame, values=[], state="readonly", width=30, font=("Arial", 12))
combobox_categorie.set("Seleziona qui")
combobox_categorie.pack(pady=10)

btn_gestisci_dati = tk.Button(categorie_frame, text="Gestisci Dati Categoria", 
                              command=apri_gestione_dati_categoria, 
                              font=("Arial", 12), width=25, height=2)
btn_gestisci_dati.pack(pady=20)

btn_esci_categorie = tk.Button(categorie_frame, text="Esci dall'Applicazione", command=root.destroy, font=("Arial", 12), width=25, height=2)
btn_esci_categorie.pack(pady=30)

# --- Avvio Applicazione ---
carica_dati_da_file()
mostra_frame(accesso_frame)
root.update_idletasks()
centra_finestra(root)
root.mainloop()