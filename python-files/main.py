import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

# Variabile globale per il dataframe
df = None
df_original = None

def log_message(message):
    log_text.insert(tk.END, f"{message}\n")
    log_text.see(tk.END)

def update_data_preview(dataframe):
    preview_text.delete('1.0', tk.END)
    preview_text.insert('1.0', dataframe.to_string(max_rows=15))

def load_csv():
    global df, df_original
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    try:
        df_original = pd.read_csv(filepath)
        df = df_original.copy()
        log_message("File CSV caricato con successo!")
        update_data_preview(df)
        
        # Aggiorna il Combobox con i nomi delle colonne
        column_combo['values'] = list(df.columns)
        column_combo.set('')
        
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile caricare il file: {e}")

def clean_data():
    global df
    if df is None:
        messagebox.showwarning("Attenzione", "Carica prima un file CSV.")
        return

    # Rimozione righe con valori mancanti
    if remove_na_var.get():
        rows_before = len(df)
        df.dropna(inplace=True)
        rows_after = len(df)
        log_message(f"Rimosse {rows_before - rows_after} righe con valori mancanti.")
    
    # Conversione a numeri (seleziona colonna specifica)
    if convert_numeric_var.get():
        selected_column = column_combo.get()
        if selected_column:
            try:
                df[selected_column] = df[selected_column].astype(str).str.strip()
                df[selected_column] = pd.to_numeric(df[selected_column], errors='coerce')
                
                if df[selected_column].isnull().any():
                    messagebox.showwarning("Avviso Conversione", f"Alcuni valori nella colonna '{selected_column}' non sono stati convertiti e sono diventati NaN.")
                
                log_message(f"Colonna '{selected_column}' convertita in tipo numerico.")
            except Exception as e:
                log_message(f"Errore nella conversione di '{selected_column}': {e}")
        else:
            messagebox.showwarning("Attenzione", "Seleziona una colonna da convertire.")

    # Rimuovi duplicati
    if remove_duplicates_var.get():
        rows_before = len(df)
        df.drop_duplicates(inplace=True)
        rows_after = len(df)
        log_message(f"Rimosse {rows_before - rows_after} righe duplicate.")
    
    # Ricerca e Sostituzione
    if find_replace_var.get():
        find_text = find_entry.get()
        replace_text = replace_entry.get()
        if find_text and replace_text:
            try:
                # Applica la sostituzione a tutte le colonne di tipo 'object' (stringhe)
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(find_text, replace_text)
                log_message(f"Sostituito '{find_text}' con '{replace_text}' in tutte le colonne di testo.")
            except Exception as e:
                log_message(f"Errore nella sostituzione: {e}")
        else:
            messagebox.showwarning("Attenzione", "Inserisci sia il testo da cercare che quello da sostituire.")
        
    update_data_preview(df)
    messagebox.showinfo("Successo", "Dati puliti in base alle opzioni selezionate!")

def save_file():
    global df
    if df is None:
        messagebox.showwarning("Attenzione", "Nessun dato da salvare.")
        return

    file_type = file_format_combo.get() # Ottieni il formato di salvataggio

    if file_type == "CSV (*.csv)":
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            df.to_csv(filepath, index=False)
            log_message(f"File salvato in formato CSV: {filepath}")
            messagebox.showinfo("Successo", "File salvato con successo!")
    elif file_type == "Excel (*.xlsx)":
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filepath:
            try:
                df.to_excel(filepath, index=False)
                log_message(f"File salvato in formato Excel: {filepath}")
                messagebox.showinfo("Successo", "File salvato con successo!")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile salvare il file: {e}\nAssicurati di avere 'openpyxl' installato.")
    else:
        messagebox.showwarning("Attenzione", "Seleziona un formato di salvataggio.")

# Configurazione della finestra principale
root = tk.Tk()
root.title("CSV-Cleaner Pro")
root.geometry("1200x800")

# --- Creazione dei Frame ---
control_frame = ttk.LabelFrame(root, text="Controlli")
control_frame.pack(side="left", fill="y", padx=10, pady=10)

options_frame = ttk.LabelFrame(control_frame, text="Opzioni di Pulizia")
options_frame.pack(pady=10, padx=5, fill="x")

preview_frame = ttk.LabelFrame(root, text="Anteprima Dati")
preview_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

log_frame = ttk.LabelFrame(root, text="Log Attività")
log_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# --- Controlli nel 'control_frame' ---
load_button = ttk.Button(control_frame, text="Carica CSV", command=load_csv)
load_button.pack(fill="x", pady=5, padx=5)

clean_button = ttk.Button(control_frame, text="Pulisci Dati", command=clean_data)
clean_button.pack(fill="x", pady=5, padx=5)

# Aggiungi un'etichetta per il formato file
ttk.Label(control_frame, text="Formato di salvataggio:").pack(anchor="w", padx=5, pady=5)

# Combobox per la selezione del formato
file_format_combo = ttk.Combobox(control_frame, values=["CSV (*.csv)", "Excel (*.xlsx)"], state="readonly")
file_format_combo.set("CSV (*.csv)") # Valore predefinito
file_format_combo.pack(fill="x", padx=5)

# Nuovo pulsante per salvare il file
save_button = ttk.Button(control_frame, text="Salva File", command=save_file)
save_button.pack(fill="x", pady=5, padx=5)

# --- Opzioni di Pulizia (Checkbox, Combobox e Entry) ---
remove_na_var = tk.BooleanVar()
remove_na_check = ttk.Checkbutton(options_frame, text="Rimuovi righe con valori mancanti", variable=remove_na_var)
remove_na_check.pack(anchor="w", pady=2)

convert_numeric_var = tk.BooleanVar()
convert_numeric_check = ttk.Checkbutton(options_frame, text="Converti colonna in numerico", variable=convert_numeric_var)
convert_numeric_check.pack(anchor="w", pady=2)

column_combo = ttk.Combobox(options_frame, state="readonly")
column_combo.pack(fill="x", padx=5, pady=5)

remove_duplicates_var = tk.BooleanVar()
remove_duplicates_check = ttk.Checkbutton(options_frame, text="Rimuovi righe duplicate", variable=remove_duplicates_var)
remove_duplicates_check.pack(anchor="w", pady=2)

# Sezione Ricerca e Sostituzione
find_replace_var = tk.BooleanVar()
find_replace_check = ttk.Checkbutton(options_frame, text="Sostituisci testo", variable=find_replace_var)
find_replace_check.pack(anchor="w", pady=5)

ttk.Label(options_frame, text="Cerca:").pack(anchor="w", padx=5)
find_entry = ttk.Entry(options_frame)
find_entry.pack(fill="x", padx=5)

ttk.Label(options_frame, text="Sostituisci con:").pack(anchor="w", padx=5)
replace_entry = ttk.Entry(options_frame)
replace_entry.pack(fill="x", padx=5)

# --- Anteprima dati nel 'preview_frame' ---
preview_text = tk.Text(preview_frame, wrap="none", font=("Courier", 10))
preview_text.pack(fill="both", expand=True, padx=5, pady=5)

# --- Log nel 'log_frame' ---
log_text = tk.Text(log_frame, height=5, wrap="word")
log_text.pack(fill="x", padx=5, pady=5)

root.mainloop()