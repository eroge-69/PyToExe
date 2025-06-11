import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = "C:/Users/Alberto/Desktop/TVSeriesManager/CineManager.db"

# Connessione al database
def connect_db():
    return sqlite3.connect(DB_PATH)

# Schermata iniziale con piè di pagina
def start_screen():
    global root
    root = tk.Tk()
    root.title("CineManager")
    root.state('zoomed')

    title_label = tk.Label(root, text="CineManager", font=("Arial", 32, "bold"))
    title_label.pack(pady=100)

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    tk.Button(btn_frame, text="Login", font=("Arial", 14), width=15, command=show_login).pack(side="left", padx=20, pady=20)
    tk.Button(btn_frame, text="Registrati", font=("Arial", 14), width=15, command=show_register).pack(side="right", padx=20, pady=20)

    # 🔵 Pulsante "Aggiungi Produzione" posizionato sopra "Esci"
    tk.Button(root, text="Aggiungi Produzione", font=("Arial", 14), width=20, command=show_add_production).pack(pady=10)

    # 🔴 Pulsante "Esci" posizionato **sotto** il frame principale
    tk.Button(root, text="Esci", font=("Arial", 14), width=15, command=root.destroy).pack(pady=30)

    # Piè di pagina
    footer = tk.Label(root, text="Powered by Alberto Belligoli", font=("Arial", 10, "italic"))
    footer.pack(side="bottom", pady=10)

    root.mainloop()

# Schermata di login
def show_login():
    clear_screen()
    tk.Label(root, text="Login", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(root, text="Username:").pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="Password:").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    def login():
        global logged_user_id, logged_username
        username, password = entry_username.get(), entry_password.get()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Username FROM Users WHERE Username=? AND Password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            logged_user_id, logged_username = user
            messagebox.showinfo("Accesso", "Login riuscito!", parent=root)
            show_main_window()
        else:
            messagebox.showerror("Errore", "Username o password errati!", parent=root)

    tk.Button(root, text="Login", command=login).pack(pady=10)

# Schermata di registrazione
def show_register():
    clear_screen()
    tk.Label(root, text="Registrazione", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(root, text="Username:").pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="Password:").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    tk.Label(root, text="Nome:").pack()
    entry_name = tk.Entry(root)
    entry_name.pack()

    tk.Label(root, text="Cognome:").pack()
    entry_surname = tk.Entry(root)
    entry_surname.pack()

    # Selezione del genere
    tk.Label(root, text="Sesso:").pack()
    gender_var = tk.StringVar(value="M")
    tk.Radiobutton(root, text="M", variable=gender_var, value="M").pack()
    tk.Radiobutton(root, text="F", variable=gender_var, value="F").pack()

    # Selezione della data di nascita
    tk.Label(root, text="Data di nascita:").pack()
    birth_frame = tk.Frame(root)
    birth_frame.pack()

    day_combo = ttk.Combobox(birth_frame, values=[str(i) for i in range(1, 32)], width=5)
    day_combo.pack(side="left")

    month_combo = ttk.Combobox(birth_frame, values=[str(i) for i in range(1, 13)], width=5)
    month_combo.pack(side="left", padx=5)

    year_combo = ttk.Combobox(birth_frame, values=[str(i) for i in range(1900, 2025)], width=7)
    year_combo.pack(side="left")

    def register():
        username, password, name, surname = entry_username.get(), entry_password.get(), entry_name.get(), entry_surname.get()
        gender = gender_var.get()
        birth = f"{year_combo.get()}-{month_combo.get()}-{day_combo.get()}"

        if not all([username, password, name, surname, gender, birth]):
            messagebox.showerror("Errore", "Compila tutti i campi!", parent=root)
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (Username, Password, Name, Surname, Gender, Birth)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password, name, surname, gender, birth))
        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", "Registrazione completata!", parent=root)
        root.destroy()
        start_screen()  # Dopo la registrazione si torna alla schermata iniziale

    tk.Button(root, text="Registrati", command=register).pack(pady=20)

# Schermata principale dopo il login
def show_main_window():
    clear_screen()

    root.title("CineManager")
    tk.Label(root, text=f"Utente Loggato: {logged_username}", font=("Arial", 12, "bold")).pack(pady=5)

    # 🔎 Tabella delle produzioni disponibili (CinemaData)
    tk.Label(root, text="Seleziona una serie da CinemaData:", font=("Arial", 12)).pack()
    columns_cd = ("Serie", "Lingua", "Anno", "Produzione", "Genere")
    tree_cd = ttk.Treeview(root, columns=columns_cd, show="headings")

    for col in columns_cd:
        tree_cd.heading(col, text=col)
        tree_cd.column(col, width=150)

    tree_cd.pack(expand=True, fill="both", pady=5)

    # Pulsante per aggiungere la serie selezionata alla lista dell'utente
    tk.Button(root, text="Aggiungi alla mia lista", font=("Arial", 12), width=20, command=lambda: add_selected_record(tree_cd)).pack(pady=10)

    # 🔍 Tabella della lista utente (UserInterface)
    tk.Label(root, text="Le tue serie:", font=("Arial", 12)).pack()
    columns_ui = ("Serie", "Num. Serie", "Num. Episodio", "Note")
    global tree_ui
    tree_ui = ttk.Treeview(root, columns=columns_ui, show="headings")

    for col in columns_ui:
        tree_ui.heading(col, text=col)
        tree_ui.column(col, width=200)

    tree_ui.pack(expand=True, fill="both", pady=5)
    
    tk.Button(root, text="Elimina dalla mia lista", font=("Arial", 12), width=20, command=lambda: delete_selected_record(tree_ui)).pack(pady=10)

    tk.Button(root, text="Logout", command=lambda: [root.destroy(), start_screen()]).pack(side="right", padx=10, pady=10)

    # Carica i dati
    fetch_cinema_data(tree_cd)  # Popola CinemaData
    fetch_records(tree_ui)  # Popola UserInterface

    tree_ui.bind("<Double-1>", lambda event: edit_record(tree_ui, event))

    # Piè di pagina
    footer = tk.Label(root, text="Powered by Alberto Belligoli", font=("Arial", 10, "italic"))
    footer.pack(side="bottom", pady=10)

def close_and_start():
    root.destroy()  # Chiude la finestra corrente
    start_screen()  # Riapre la schermata iniziale
    

    # Piè di pagina
    footer = tk.Label(root, text="Powered by Alberto Belligoli", font=("Arial", 10, "italic"))
    footer.pack(side="bottom", pady=10)

def fetch_cinema_data(tree_cd):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, OriginalLanguage, YEAR, TvCompany, Genre FROM CinemaData ORDER BY YEAR DESC")
    records = cursor.fetchall()
    conn.close()

    for row in tree_cd.get_children():
        tree_cd.delete(row)
    for record in records:
        tree_cd.insert("", "end", values=record)

# Recupero e filtraggio dei record
def fetch_records(tree, search_term=""):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.Name, UI.SeriesNumber, UI.EpisodeNumber, UI.Note
        FROM UserInterface UI
        JOIN CinemaData C ON UI.CinemaID = C.CinemaID
        WHERE UI.UserID = ? AND C.Name LIKE ?
        ORDER BY UI.RecordID DESC
    """, (logged_user_id, f"%{search_term}%"))
    records = cursor.fetchall()
    conn.close()

    for row in tree.get_children():
        tree.delete(row)
    for record in records:
        tree.insert("", "end", values=record)
        
# Eliminazione record dalla lista

def delete_selected_record(tree_ui):
    try:
        selected_item = tree_ui.selection()[0]  # Ottieni la selezione
        values = tree_ui.item(selected_item, "values")  # Recupera i dati del record selezionato

        if not values:
            messagebox.showerror("Errore", "Seleziona un record prima di eliminarlo!", parent=root)
            return

        series_name, num_series, num_episode, note = values  # Estrai dati

        # Conferma eliminazione
        confirm = messagebox.askyesno("Conferma eliminazione", f"Vuoi eliminare '{series_name}' dalla tua lista?", parent=root)
        if not confirm:
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM UserInterface
            WHERE UserID = ? AND CinemaID = (SELECT CinemaID FROM CinemaData WHERE Name=?) 
            AND SeriesNumber = ? AND EpisodeNumber = ?
        """, (logged_user_id, series_name, num_series, num_episode))

        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", f"'{series_name}' è stato eliminato dalla tua lista.", parent=root)
        fetch_records(tree_ui)  # Aggiorna la tabella dopo l'eliminazione

    except IndexError:
        messagebox.showerror("Errore", "Nessun record selezionato!", parent=root)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'eliminazione:\n{e}", parent=root)


# Funzione per aggiungere la serie alla lista dell'utente
def add_selected_record(tree_cd):
    try:
        selected_item = tree_cd.selection()[0]  # Ottieni la selezione
        values = tree_cd.item(selected_item, "values")  # Recupera i dati della serie

        if not values:
            messagebox.showerror("Errore", "Seleziona una serie prima di aggiungerla!", parent=root)
            return

        series_name, language, year, tv_company, genre = values  # Estrai dati

        conn = connect_db()
        cursor = conn.cursor()

        # 📌 **Controlla se la serie è già presente nella lista dell'utente**
        cursor.execute("""
            SELECT COUNT(*) FROM UserInterface 
            WHERE UserID = ? AND CinemaID = (SELECT CinemaID FROM CinemaData WHERE Name=?)
        """, (logged_user_id, series_name))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            messagebox.showerror("Errore", f"La serie '{series_name}' è già presente nei tuoi record!", parent=root)
            conn.close()
            return

        # Se la serie non è nei record, esegui l'INSERT
        cursor.execute("""
            INSERT INTO UserInterface (UserID, CinemaID, SeriesNumber, EpisodeNumber, Note)
            VALUES (?, (SELECT CinemaID FROM CinemaData WHERE Name=?), ?, ?, ?)
        """, (logged_user_id, series_name, 1, 1, "Aggiunta manualmente"))  # Valori predefiniti

        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", f"La serie '{series_name}' è stata aggiunta ai tuoi record!", parent=root)
        fetch_records(tree_ui)  # Aggiorna la tabella UserInterface

    except IndexError:
        messagebox.showerror("Errore", "Nessuna serie selezionata!", parent=root)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante l'aggiunta:\n{e}", parent=root)

# Funzione per modificare un record con doppio clic
def edit_record(tree, event):
    item = tree.selection()[0]
    values = tree.item(item, "values")

    edit_window = tk.Toplevel(root)
    edit_window.title("Modifica Record")
    
   # Ottieni dimensioni della finestra principale
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    # Definisci dimensioni della finestra di modifica
    edit_width = 300
    edit_height = 200

    # Calcola posizione centrale rispetto alla finestra principale
    edit_x = root_x + (root_width - edit_width) // 2
    edit_y = root_y + (root_height - edit_height) // 2

    edit_window.geometry(f"{edit_width}x{edit_height}+{edit_x}+{edit_y}")
    entries = []
    labels = ["Serie", "Num. Serie", "Num. Episodio", "Note"]

    for i, label in enumerate(labels):
        tk.Label(edit_window, text=label).grid(row=i, column=0)
        entry = tk.Entry(edit_window)
        entry.grid(row=i, column=1)
        entry.insert(0, values[i])
        entries.append(entry)

    def save_changes():
        new_values = [entry.get() for entry in entries]

# Se i dati non sono cambiati, non eseguire l'UPDATE
        if new_values == list(values):
            messagebox.showinfo("Nessuna modifica", "Non hai apportato alcuna modifica.")
            edit_window.destroy()
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE UserInterface
            SET SeriesNumber=?, EpisodeNumber=?, Note=?
            WHERE CinemaID=(SELECT CinemaID FROM CinemaData WHERE Name=?) AND UserID=?
        """, (new_values[1], new_values[2], new_values[3], new_values[0], logged_user_id))
        conn.commit()
        conn.close()
        fetch_records(tree)
        edit_window.destroy()

    tk.Button(edit_window, text="Salva", command=save_changes).grid(row=len(labels), column=1)

def show_add_production():
    add_window = tk.Toplevel(root)
    add_window.title("Aggiungi Produzione")

    # Ottieni le dimensioni della finestra principale per centrare la nuova finestra
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    # Definisci dimensioni della finestra di aggiunta
    add_width = 400
    add_height = 300

    # Calcola posizione centrale
    add_x = root_x + (root_width - add_width) // 2
    add_y = root_y + (root_height - add_height) // 2

    # Imposta dimensioni e posizione
    add_window.geometry(f"{add_width}x{add_height}+{add_x}+{add_y}")
    add_window.transient(root)
    add_window.grab_set()

    # Etichette e campi di input
    labels = ["Nome", "Lingua Originale", "Anno", "Casa di Produzione", "Genere"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(add_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(add_window, width=30)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    # Bottone per salvare la produzione
    tk.Button(add_window, text="Salva", font=("Arial", 12), width=15, command=lambda: save_production(entries, add_window)).grid(row=len(labels), column=1, pady=10)


def save_production(entries, add_window):
    try:
        # Recupera i dati dai campi di input
        name = entries["Nome"].get().strip()
        language = entries["Lingua Originale"].get().strip()
        year = entries["Anno"].get().strip()
        tv_company = entries["Casa di Produzione"].get().strip()
        genre = entries["Genere"].get().strip()

        # Controlla che tutti i campi siano compilati
        if not all([name, language, year, tv_company, genre]):
            messagebox.showerror("Errore", "Compila tutti i campi!", parent=add_window)
            return

        # Converte "Anno" in numero e verifica la validità
        if not year.isdigit() or int(year) < 1900 or int(year) > 2025:
            messagebox.showerror("Errore", "Inserisci un anno valido (1900-2025)!", parent=add_window)
            return

        conn = connect_db()
        cursor = conn.cursor()

        # 📌 **Controlla se la produzione esiste già**
        cursor.execute("SELECT COUNT(*) FROM CinemaData WHERE Name=?", (name,))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            messagebox.showerror("Errore", f"La serie '{name}' è già presente nel database!", parent=add_window)
            conn.close()
            return

        # Se la produzione non esiste, esegui l'INSERT
        cursor.execute("""
            INSERT INTO CinemaData (Name, OriginalLanguage, "YEAR", TvCompany, Genre)
            VALUES (?, ?, ?, ?, ?)
        """, (name, language, int(year), tv_company, genre))

        conn.commit()
        conn.close()

        messagebox.showinfo("Successo", "Produzione aggiunta con successo!", parent=add_window)
        add_window.destroy()

    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un problema:\n{e}", parent=add_window)





# Pulisce la schermata prima di cambiarla
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

start_screen()
