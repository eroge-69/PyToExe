import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import webbrowser
from datetime import datetime, timedelta

# Database Initialization
def initialize_db():
    conn = sqlite3.connect('personalverwaltung.db')
    cursor = conn.cursor()

    # Table for employees
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mitarbeiter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vorname TEXT NOT NULL,
            nachname TEXT NOT NULL,
            geburtsdatum TEXT, -- Stored as TEXT in YYYY-MM-DD format
            inventur_link TEXT
        )
    ''')

    # Table for qualifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qualifikationen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mitarbeiter_id INTEGER NOT NULL,
            qualifikationstyp TEXT NOT NULL,
            zertifikat_link TEXT, -- Path to file or URL
            gueltig_bis TEXT,    -- New column: Valid until (YYYY-MM-DD)
            FOREIGN KEY (mitarbeiter_id) REFERENCES mitarbeiter(id) ON DELETE CASCADE
        )
    ''')

    # Add 'gueltig_bis' column to qualifikationen if it doesn't exist
    try:
        cursor.execute("ALTER TABLE qualifikationen ADD COLUMN gueltig_bis TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Table for eyesight
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sehfaehigkeit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mitarbeiter_id INTEGER NOT NULL,
            status TEXT NOT NULL, -- e.g., "Passed", "Failed"
            zertifikat_link TEXT, -- Path to file or URL
            gueltig_bis TEXT,    -- New column: Valid until (YYYY-MM-DD)
            FOREIGN KEY (mitarbeiter_id) REFERENCES mitarbeiter(id) ON DELETE CASCADE
        )
    ''')

    # Add 'gueltig_bis' column to sehfaehigkeit if it doesn't exist
    try:
        cursor.execute("ALTER TABLE sehfaehigkeit ADD COLUMN gueltig_bis TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()

# Helper function to display messages (replaces alert/confirm)
def show_message(title, message):
    messagebox.showinfo(title, message)

def show_error(title, message):
    messagebox.showerror(title, message)

def ask_question(title, message):
    return messagebox.askyesno(title, message)

class PersonnelManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personalverwaltungs-App")
        self.root.geometry("1000x700")

        # Initialize the database
        initialize_db()

        # Create a Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Tab for employee management
        self.employee_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_frame, text="Mitarbeiter")
        self.create_employee_tab(self.employee_frame)

        # Tab for qualification management
        self.qualification_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.qualification_frame, text="Qualifikationen")
        self.create_qualification_tab(self.qualification_frame)

        # Tab for eyesight management
        self.eyesight_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.eyesight_frame, text="Sehfähigkeit")
        self.create_eyesight_tab(self.eyesight_frame)

        # Global variable for the selected employee
        self.selected_employee_id = None

        # Populate lists on startup
        self.populate_employee_list()

        # Bind notebook tab change event to update expiration checks
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Initial check for expirations
        self.check_expirations()

    def on_tab_change(self, event):
        # When tab changes, update the employee selection for the current tab
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Qualifikationen" and self.selected_employee_id:
            self.populate_qualification_list(self.selected_employee_id)
        elif selected_tab == "Sehfähigkeit" and self.selected_employee_id:
            self.populate_eyesight_list(self.selected_employee_id)

    # --- Employee Tab ---
    def create_employee_tab(self, parent_frame):
        # Input area
        input_frame = ttk.LabelFrame(parent_frame, text="Mitarbeiterdaten")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Vorname:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.vorname_entry = ttk.Entry(input_frame, width=40)
        self.vorname_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Nachname:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.nachname_entry = ttk.Entry(input_frame, width=40)
        self.nachname_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Geburtsdatum (JJJJ-MM-TT):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.geburtsdatum_entry = ttk.Entry(input_frame, width=40)
        self.geburtsdatum_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Inventur-Link:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.inventur_link_entry = ttk.Entry(input_frame, width=40)
        self.inventur_link_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        inventur_link_button = ttk.Button(input_frame, text="Datei wählen", command=lambda: self.select_file_or_url(self.inventur_link_entry))
        inventur_link_button.grid(row=3, column=2, padx=5, pady=5)


        # Buttons
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Mitarbeiter hinzufügen", command=self.add_employee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Mitarbeiter aktualisieren", command=self.update_employee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Mitarbeiter löschen", command=self.delete_employee).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Felder leeren", command=self.clear_employee_fields).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Details anzeigen", command=self.show_selected_employee_details).pack(side="left", padx=5) # New button
        ttk.Button(button_frame, text="Gültigkeiten prüfen", command=self.check_expirations).pack(side="right", padx=5)


        # Employee list
        self.employee_tree = ttk.Treeview(parent_frame, columns=("ID", "Vorname", "Nachname", "Geburtsdatum", "Inventur-Link"), show="headings")
        self.employee_tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Vorname", text="Vorname")
        self.employee_tree.heading("Nachname", text="Nachname")
        self.employee_tree.heading("Geburtsdatum", text="Geburtsdatum")
        self.employee_tree.heading("Inventur-Link", text="Inventur-Link")

        # Adjust column widths
        self.employee_tree.column("ID", width=50, anchor="center")
        self.employee_tree.column("Vorname", width=150, anchor="w")
        self.employee_tree.column("Nachname", width=150, anchor="w")
        self.employee_tree.column("Geburtsdatum", width=120, anchor="center")
        self.employee_tree.column("Inventur-Link", width=250, anchor="w")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", in_=self.employee_tree)


        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        self.employee_tree.bind("<Double-1>", self.open_selected_inventur_link) # Keep original double-click for inventur link

    def populate_employee_list(self):
        # Clear current list
        for i in self.employee_tree.get_children():
            self.employee_tree.delete(i)

        conn = sqlite3.connect('personalverwaltung.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mitarbeiter ORDER BY nachname, vorname")
        employees = cursor.fetchall()
        conn.close()

        for emp in employees:
            self.employee_tree.insert("", "end", values=emp)

    def add_employee(self):
        vorname = self.vorname_entry.get().strip()
        nachname = self.nachname_entry.get().strip()
        geburtsdatum = self.geburtsdatum_entry.get().strip()
        inventur_link = self.inventur_link_entry.get().strip()

        if not vorname or not nachname:
            show_error("Eingabefehler", "Vorname und Nachname dürfen nicht leer sein.")
            return

        # Validate birthday format (optional, but recommended)
        if geburtsdatum:
            try:
                datetime.strptime(geburtsdatum, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges Geburtsdatum-Format. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO mitarbeiter (vorname, nachname, geburtsdatum, inventur_link) VALUES (?, ?, ?, ?)",
                           (vorname, nachname, geburtsdatum, inventur_link))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Mitarbeiter erfolgreich hinzugefügt.")
            self.clear_employee_fields()
            self.populate_employee_list()
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Hinzufügen des Mitarbeiters: {e}")

    def update_employee(self):
        selected_item = self.employee_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie einen Mitarbeiter zum Aktualisieren aus.")
            return

        employee_id = self.employee_tree.item(selected_item, "values")[0]
        vorname = self.vorname_entry.get().strip()
        nachname = self.nachname_entry.get().strip()
        geburtsdatum = self.geburtsdatum_entry.get().strip()
        inventur_link = self.inventur_link_entry.get().strip()

        if not vorname or not nachname:
            show_error("Eingabefehler", "Vorname und Nachname dürfen nicht leer sein.")
            return

        if geburtsdatum:
            try:
                datetime.strptime(geburtsdatum, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges Geburtsdatum-Format. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE mitarbeiter SET vorname=?, nachname=?, geburtsdatum=?, inventur_link=? WHERE id=?",
                           (vorname, nachname, geburtsdatum, inventur_link, employee_id))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Mitarbeiter erfolgreich aktualisiert.")
            self.clear_employee_fields()
            self.populate_employee_list()
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Aktualisieren des Mitarbeiters: {e}")

    def delete_employee(self):
        selected_item = self.employee_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie einen Mitarbeiter zum Löschen aus.")
            return

        employee_id = self.employee_tree.item(selected_item, "values")[0]
        employee_name = f"{self.employee_tree.item(selected_item, 'values')[1]} {self.employee_tree.item(selected_item, 'values')[2]}"

        if ask_question("Bestätigen", f"Möchten Sie den Mitarbeiter '{employee_name}' wirklich löschen?\nAlle zugehörigen Qualifikationen und Sehfähigkeitsdaten werden ebenfalls gelöscht."):
            try:
                conn = sqlite3.connect('personalverwaltung.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mitarbeiter WHERE id=?", (employee_id,))
                conn.commit()
                conn.close()
                show_message("Erfolg", "Mitarbeiter erfolgreich gelöscht.")
                self.clear_employee_fields()
                self.populate_employee_list()
            except sqlite3.Error as e:
                show_error("Datenbankfehler", f"Fehler beim Löschen des Mitarbeiters: {e}")

    def clear_employee_fields(self):
        self.vorname_entry.delete(0, tk.END)
        self.nachname_entry.delete(0, tk.END)
        self.geburtsdatum_entry.delete(0, tk.END)
        self.inventur_link_entry.delete(0, tk.END)
        self.employee_tree.selection_remove(self.employee_tree.selection())
        self.selected_employee_id = None # Reset the selected employee

    def on_employee_select(self, event):
        selected_item = self.employee_tree.selection()
        if selected_item:
            values = self.employee_tree.item(selected_item, "values")
            self.selected_employee_id = values[0] # Store the ID of the selected employee

            self.vorname_entry.delete(0, tk.END)
            self.vorname_entry.insert(0, values[1])
            self.nachname_entry.delete(0, tk.END)
            self.nachname_entry.insert(0, values[2])
            self.geburtsdatum_entry.delete(0, tk.END)
            self.geburtsdatum_entry.insert(0, values[3])
            self.inventur_link_entry.delete(0, tk.END)
            self.inventur_link_entry.insert(0, values[4])

            # Update qualification and eyesight lists in the main window's tabs
            self.populate_qualification_list(self.selected_employee_id)
            self.populate_eyesight_list(self.selected_employee_id)
        else:
            self.selected_employee_id = None
            self.clear_qualification_fields()
            self.clear_eyesight_fields()
            self.qualification_tree.delete(*self.qualification_tree.get_children())
            self.eyesight_tree.delete(*self.eyesight_tree.get_children())


    def open_link(self, link_path):
        if not link_path:
            show_message("Fehler", "Kein Link oder Dateipfad vorhanden.")
            return

        if os.path.exists(link_path): # Is it a file path?
            try:
                # Cross-platform file opening
                if os.name == 'nt':  # Windows
                    os.startfile(link_path)
                elif os.uname().sysname == 'Darwin':  # macOS
                    os.system(f'open "{link_path}"')
                else:  # Linux and other Unix-based systems
                    os.system(f'xdg-open "{link_path}"')
            except Exception as e:
                show_error("Fehler", f"Konnte Datei nicht öffnen: {e}")
        elif link_path.startswith("http://") or link_path.startswith("https://"): # Is it a URL?
            try:
                webbrowser.open(link_path)
            except Exception as e:
                show_error("Fehler", f"Konnte Link nicht öffnen: {e}")
        else:
            show_error("Fehler", "Ungültiger Dateipfad oder URL. Stellen Sie sicher, dass der Pfad korrekt ist oder mit 'http://'/'https://' beginnt.")

    def open_selected_inventur_link(self, event):
        selected_item = self.employee_tree.selection()
        if selected_item:
            link = self.employee_tree.item(selected_item, "values")[4] # Inventur-Link is the 5th column (index 4)
            self.open_link(link)

    def select_file_or_url(self, entry_widget):
        # Dialog to select a file
        file_path = filedialog.askopenfilename(
            title="Zertifikat oder Dokument auswählen",
            filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
        else:
            # If no file was selected, the user can manually enter a URL
            pass


    # --- Qualification Tab ---
    def create_qualification_tab(self, parent_frame):
        # Display of the selected employee
        ttk.Label(parent_frame, text="Ausgewählter Mitarbeiter:").pack(padx=10, pady=5, anchor="w")
        self.selected_employee_qual_label = ttk.Label(parent_frame, text="Kein Mitarbeiter ausgewählt")
        self.selected_employee_qual_label.pack(padx=10, pady=2, anchor="w")

        # Input area
        input_frame = ttk.LabelFrame(parent_frame, text="Qualifikation hinzufügen/bearbeiten")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Qualifikationstyp:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.qualifikation_type_entry = ttk.Entry(input_frame, width=40)
        self.qualifikation_type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Zertifikat-Link:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.qualifikation_link_entry = ttk.Entry(input_frame, width=40)
        self.qualifikation_link_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        qual_link_button = ttk.Button(input_frame, text="Datei wählen", command=lambda: self.select_file_or_url(self.qualifikation_link_entry))
        qual_link_button.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Gültig bis (JJJJ-MM-TT):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.qualifikation_gueltig_bis_entry = ttk.Entry(input_frame, width=40)
        self.qualifikation_gueltig_bis_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")


        # Buttons
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Qualifikation hinzufügen", command=self.add_qualification).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Qualifikation aktualisieren", command=self.update_qualification).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Qualifikation löschen", command=self.delete_qualification).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Felder leeren", command=self.clear_qualification_fields).pack(side="left", padx=5)


        # Qualification list
        self.qualification_tree = ttk.Treeview(parent_frame, columns=("ID", "Qualifikationstyp", "Zertifikat-Link", "Gültig bis"), show="headings")
        self.qualification_tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.qualification_tree.heading("ID", text="ID")
        self.qualification_tree.heading("Qualifikationstyp", text="Qualifikationstyp")
        self.qualification_tree.heading("Zertifikat-Link", text="Zertifikat-Link")
        self.qualification_tree.heading("Gültig bis", text="Gültig bis")

        self.qualification_tree.column("ID", width=50, anchor="center")
        self.qualification_tree.column("Qualifikationstyp", width=150, anchor="w")
        self.qualification_tree.column("Zertifikat-Link", width=250, anchor="w")
        self.qualification_tree.column("Gültig bis", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.qualification_tree.yview)
        self.qualification_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", in_=self.qualification_tree)

        self.qualification_tree.bind("<<TreeviewSelect>>", self.on_qualification_select)
        self.qualification_tree.bind("<Double-1>", self.open_selected_qualification_link)


    def populate_qualification_list(self, employee_id, tree_widget=None):
        if tree_widget is None:
            tree_widget = self.qualification_tree
            self.selected_employee_qual_label.config(text=f"Ausgewählter Mitarbeiter: {self.get_employee_name(employee_id)}")

        for i in tree_widget.get_children():
            tree_widget.delete(i)

        if employee_id is None:
            return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, qualifikationstyp, zertifikat_link, gueltig_bis FROM qualifikationen WHERE mitarbeiter_id=?", (employee_id,))
            qualifications = cursor.fetchall()
            conn.close()

            for qual in qualifications:
                tree_widget.insert("", "end", values=qual)
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Laden der Qualifikationen: {e}")

    def add_qualification(self):
        if self.selected_employee_id is None:
            show_error("Auswahlfehler", "Bitte wählen Sie zuerst einen Mitarbeiter auf dem 'Mitarbeiter'-Tab aus.")
            return

        qual_type = self.qualifikation_type_entry.get().strip()
        cert_link = self.qualifikation_link_entry.get().strip()
        gueltig_bis = self.qualifikation_gueltig_bis_entry.get().strip()

        if not qual_type:
            show_error("Eingabefehler", "Qualifikationstyp darf nicht leer sein.")
            return

        if gueltig_bis:
            try:
                datetime.strptime(gueltig_bis, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges 'Gültig bis'-Datumformat. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO qualifikationen (mitarbeiter_id, qualifikationstyp, zertifikat_link, gueltig_bis) VALUES (?, ?, ?, ?)",
                           (self.selected_employee_id, qual_type, cert_link, gueltig_bis))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Qualifikation erfolgreich hinzugefügt.")
            self.clear_qualification_fields()
            self.populate_qualification_list(self.selected_employee_id)
            self.check_expirations() # Check expirations after adding/updating
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Hinzufügen der Qualifikation: {e}")

    def update_qualification(self):
        selected_item = self.qualification_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie eine Qualifikation zum Aktualisieren aus.")
            return

        qual_id = self.qualification_tree.item(selected_item, "values")[0]
        qual_type = self.qualifikation_type_entry.get().strip()
        cert_link = self.qualifikation_link_entry.get().strip()
        gueltig_bis = self.qualifikation_gueltig_bis_entry.get().strip()


        if not qual_type:
            show_error("Eingabefehler", "Qualifikationstyp darf nicht leer sein.")
            return

        if gueltig_bis:
            try:
                datetime.strptime(gueltig_bis, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges 'Gültig bis'-Datumformat. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE qualifikationen SET qualifikationstyp=?, zertifikat_link=?, gueltig_bis=? WHERE id=?",
                           (qual_type, cert_link, gueltig_bis, qual_id))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Qualifikation erfolgreich aktualisiert.")
            self.clear_qualification_fields()
            self.populate_qualification_list(self.selected_employee_id)
            self.check_expirations() # Check expirations after adding/updating
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Aktualisieren der Qualifikation: {e}")

    def delete_qualification(self):
        selected_item = self.qualification_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie eine Qualifikation zum Löschen aus.")
            return

        qual_id = self.qualification_tree.item(selected_item, "values")[0]
        qual_type = self.qualification_tree.item(selected_item, "values")[1]

        if ask_question("Bestätigen", f"Möchten Sie die Qualifikation '{qual_type}' wirklich löschen?"):
            try:
                conn = sqlite3.connect('personalverwaltung.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM qualifikationen WHERE id=?", (qual_id,))
                conn.commit()
                conn.close()
                show_message("Erfolg", "Qualifikation erfolgreich gelöscht.")
                self.clear_qualification_fields()
                self.populate_qualification_list(self.selected_employee_id)
                self.check_expirations() # Check expirations after deleting
            except sqlite3.Error as e:
                show_error("Datenbankfehler", f"Fehler beim Löschen der Qualifikation: {e}")

    def clear_qualification_fields(self):
        self.qualifikation_type_entry.delete(0, tk.END)
        self.qualifikation_link_entry.delete(0, tk.END)
        self.qualifikation_gueltig_bis_entry.delete(0, tk.END)
        self.qualification_tree.selection_remove(self.qualification_tree.selection())

    def on_qualification_select(self, event):
        selected_item = self.qualification_tree.selection()
        if selected_item:
            values = self.qualification_tree.item(selected_item, "values")
            self.qualifikation_type_entry.delete(0, tk.END)
            self.qualifikation_type_entry.insert(0, values[1])
            self.qualifikation_link_entry.delete(0, tk.END)
            self.qualifikation_link_entry.insert(0, values[2])
            self.qualifikation_gueltig_bis_entry.delete(0, tk.END)
            # Ensure index 3 exists before accessing it (for older entries without 'gueltig_bis')
            if len(values) > 3:
                self.qualifikation_gueltig_bis_entry.insert(0, values[3])

    def open_selected_qualification_link(self, event):
        selected_item = self.qualification_tree.selection()
        if selected_item:
            link = self.qualification_tree.item(selected_item, "values")[2]
            self.open_link(link)

    # --- Eyesight Tab ---
    def create_eyesight_tab(self, parent_frame):
        # Display of the selected employee
        ttk.Label(parent_frame, text="Ausgewählter Mitarbeiter:").pack(padx=10, pady=5, anchor="w")
        self.selected_employee_eyesight_label = ttk.Label(parent_frame, text="Kein Mitarbeiter ausgewählt")
        self.selected_employee_eyesight_label.pack(padx=10, pady=2, anchor="w")

        # Input area
        input_frame = ttk.LabelFrame(parent_frame, text="Sehfähigkeit hinzufügen/bearbeiten")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.eyesight_status_entry = ttk.Entry(input_frame, width=40)
        self.eyesight_status_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Zertifikat-Link:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.eyesight_link_entry = ttk.Entry(input_frame, width=40)
        self.eyesight_link_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        eyesight_link_button = ttk.Button(input_frame, text="Datei wählen", command=lambda: self.select_file_or_url(self.eyesight_link_entry))
        eyesight_link_button.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Gültig bis (JJJJ-MM-TT):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.eyesight_gueltig_bis_entry = ttk.Entry(input_frame, width=40)
        self.eyesight_gueltig_bis_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")


        # Buttons
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Sehfähigkeit hinzufügen", command=self.add_eyesight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sehfähigkeit aktualisieren", command=self.update_eyesight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sehfähigkeit löschen", command=self.delete_eyesight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Felder leeren", command=self.clear_eyesight_fields).pack(side="left", padx=5)


        # Eyesight list
        self.eyesight_tree = ttk.Treeview(parent_frame, columns=("ID", "Status", "Zertifikat-Link", "Gültig bis"), show="headings")
        self.eyesight_tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.eyesight_tree.heading("ID", text="ID")
        self.eyesight_tree.heading("Status", text="Status")
        self.eyesight_tree.heading("Zertifikat-Link", text="Zertifikat-Link")
        self.eyesight_tree.heading("Gültig bis", text="Gültig bis")

        self.eyesight_tree.column("ID", width=50, anchor="center")
        self.eyesight_tree.column("Status", width=150, anchor="w")
        self.eyesight_tree.column("Zertifikat-Link", width=250, anchor="w")
        self.eyesight_tree.column("Gültig bis", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.eyesight_tree.yview)
        self.eyesight_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", in_=self.eyesight_tree)

        self.eyesight_tree.bind("<<TreeviewSelect>>", self.on_eyesight_select)
        self.eyesight_tree.bind("<Double-1>", self.open_selected_eyesight_link)

    def populate_eyesight_list(self, employee_id, tree_widget=None):
        if tree_widget is None:
            tree_widget = self.eyesight_tree
            self.selected_employee_eyesight_label.config(text=f"Ausgewählter Mitarbeiter: {self.get_employee_name(employee_id)}")

        for i in tree_widget.get_children():
            tree_widget.delete(i)

        if employee_id is None:
            return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, zertifikat_link, gueltig_bis FROM sehfaehigkeit WHERE mitarbeiter_id=?", (employee_id,))
            eyesight_data = cursor.fetchall()
            conn.close()

            for es_data in eyesight_data:
                tree_widget.insert("", "end", values=es_data)
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Laden der Sehfähigkeitsdaten: {e}")

    def add_eyesight(self):
        if self.selected_employee_id is None:
            show_error("Auswahlfehler", "Bitte wählen Sie zuerst einen Mitarbeiter auf dem 'Mitarbeiter'-Tab aus.")
            return

        status = self.eyesight_status_entry.get().strip()
        cert_link = self.eyesight_link_entry.get().strip()
        gueltig_bis = self.eyesight_gueltig_bis_entry.get().strip()

        if not status:
            show_error("Eingabefehler", "Status der Sehfähigkeit darf nicht leer sein.")
            return

        if gueltig_bis:
            try:
                datetime.strptime(gueltig_bis, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges 'Gültig bis'-Datumformat. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sehfaehigkeit (mitarbeiter_id, status, zertifikat_link, gueltig_bis) VALUES (?, ?, ?, ?)",
                           (self.selected_employee_id, status, cert_link, gueltig_bis))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Sehfähigkeit erfolgreich hinzugefügt.")
            self.clear_eyesight_fields()
            self.populate_eyesight_list(self.selected_employee_id)
            self.check_expirations() # Check expirations after adding/updating
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Hinzufügen der Sehfähigkeit: {e}")

    def update_eyesight(self):
        selected_item = self.eyesight_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie einen Eintrag zur Sehfähigkeit zum Aktualisieren aus.")
            return

        eyesight_id = self.eyesight_tree.item(selected_item, "values")[0]
        status = self.eyesight_status_entry.get().strip()
        cert_link = self.eyesight_link_entry.get().strip()
        gueltig_bis = self.eyesight_gueltig_bis_entry.get().strip()

        if not status:
            show_error("Eingabefehler", "Status der Sehfähigkeit darf nicht leer sein.")
            return

        if gueltig_bis:
            try:
                datetime.strptime(gueltig_bis, '%Y-%m-%d')
            except ValueError:
                show_error("Eingabefehler", "Ungültiges 'Gültig bis'-Datumformat. Bitte JJJJ-MM-TT verwenden.")
                return

        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE sehfaehigkeit SET status=?, zertifikat_link=?, gueltig_bis=? WHERE id=?",
                           (status, cert_link, gueltig_bis, eyesight_id))
            conn.commit()
            conn.close()
            show_message("Erfolg", "Sehfähigkeit erfolgreich aktualisiert.")
            self.clear_eyesight_fields()
            self.populate_eyesight_list(self.selected_employee_id)
            self.check_expirations() # Check expirations after adding/updating
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Aktualisieren der Sehfähigkeit: {e}")

    def delete_eyesight(self):
        selected_item = self.eyesight_tree.selection()
        if not selected_item:
            show_error("Auswahlfehler", "Bitte wählen Sie einen Eintrag zur Sehfähigkeit zum Löschen aus.")
            return

        eyesight_id = self.eyesight_tree.item(selected_item, "values")[0]
        status = self.eyesight_tree.item(selected_item, "values")[1]

        if ask_question("Bestätigen", f"Möchten Sie den Sehfähigkeits-Eintrag '{status}' wirklich löschen?"):
            try:
                conn = sqlite3.connect('personalverwaltung.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sehfaehigkeit WHERE id=?", (eyesight_id,))
                conn.commit()
                conn.close()
                show_message("Erfolg", "Sehfähigkeit erfolgreich gelöscht.")
                self.clear_eyesight_fields()
                self.populate_eyesight_list(self.selected_employee_id)
                self.check_expirations() # Check expirations after deleting
            except sqlite3.Error as e:
                show_error("Datenbankfehler", f"Fehler beim Löschen der Sehfähigkeit: {e}")

    def clear_eyesight_fields(self):
        self.eyesight_status_entry.delete(0, tk.END)
        self.eyesight_link_entry.delete(0, tk.END)
        self.eyesight_gueltig_bis_entry.delete(0, tk.END)
        self.eyesight_tree.selection_remove(self.eyesight_tree.selection())

    def on_eyesight_select(self, event):
        selected_item = self.eyesight_tree.selection()
        if selected_item:
            values = self.eyesight_tree.item(selected_item, "values")
            self.eyesight_status_entry.delete(0, tk.END)
            self.eyesight_status_entry.insert(0, values[1])
            self.eyesight_link_entry.delete(0, tk.END)
            self.eyesight_link_entry.insert(0, values[2])
            self.eyesight_gueltig_bis_entry.delete(0, tk.END)
            # Ensure index 3 exists before accessing it (for older entries without 'gueltig_bis')
            if len(values) > 3:
                self.eyesight_gueltig_bis_entry.insert(0, values[3])

    def open_selected_eyesight_link(self, event):
        selected_item = self.eyesight_tree.selection()
        if selected_item:
            link = self.eyesight_tree.item(selected_item, "values")[2]
            self.open_link(link)

    # Helper function to get employee name by ID
    def get_employee_name(self, employee_id):
        if employee_id is None:
            return "Kein Mitarbeiter ausgewählt"
        try:
            conn = sqlite3.connect('personalverwaltung.db')
            cursor = conn.cursor()
            cursor.execute("SELECT vorname, nachname FROM mitarbeiter WHERE id=?", (employee_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return f"{result[0]} {result[1]}"
            return f"Unbekannter Mitarbeiter"
        except sqlite3.Error as e:
            show_error("Datenbankfehler", f"Fehler beim Abrufen des Mitarbeiternamens: {e}")
            return f"Fehler"

    # --- New: Show Employee Details Window ---
    def show_selected_employee_details(self):
        if self.selected_employee_id is None:
            show_error("Auswahlfehler", "Bitte wählen Sie zuerst einen Mitarbeiter aus, um dessen Details anzuzeigen.")
            return

        self.show_employee_details(self.selected_employee_id)

    def show_employee_details(self, employee_id):
        # Fetch employee details
        conn = sqlite3.connect('personalverwaltung.db')
        cursor = conn.cursor()
        cursor.execute("SELECT vorname, nachname, geburtsdatum, inventur_link FROM mitarbeiter WHERE id=?", (employee_id,))
        employee_data = cursor.fetchone()
        conn.close()

        if not employee_data:
            show_error("Fehler", "Mitarbeiter nicht gefunden.")
            return

        vorname, nachname, geburtsdatum, inventur_link = employee_data
        full_name = f"{vorname} {nachname}"

        # Create new Toplevel window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Mitarbeiterdetails: {full_name}")
        details_window.geometry("800x600")

        # Employee Basic Info Frame
        info_frame = ttk.LabelFrame(details_window, text="Personaldatenblatt")
        info_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(info_frame, text=f"Name: {full_name}").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(info_frame, text=f"Geburtsdatum: {geburtsdatum if geburtsdatum else 'Nicht angegeben'}").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        inventur_label = ttk.Label(info_frame, text=f"Inventur-Link: {inventur_link if inventur_link else 'Nicht vorhanden'}", cursor="hand2", foreground="blue")
        inventur_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        inventur_label.bind("<Button-1>", lambda e: self.open_link(inventur_link))
        if not inventur_link: # Disable cursor/color if no link
            inventur_label.config(cursor="", foreground="black")


        # Qualifications Frame
        qual_frame = ttk.LabelFrame(details_window, text="Qualifikationen")
        qual_frame.pack(padx=10, pady=10, expand=True, fill="both")

        qual_tree = ttk.Treeview(qual_frame, columns=("ID", "Qualifikationstyp", "Zertifikat-Link", "Gültig bis"), show="headings")
        qual_tree.pack(expand=True, fill="both")

        qual_tree.heading("ID", text="ID")
        qual_tree.heading("Qualifikationstyp", text="Qualifikationstyp")
        qual_tree.heading("Zertifikat-Link", text="Zertifikat-Link")
        qual_tree.heading("Gültig bis", text="Gültig bis")

        qual_tree.column("ID", width=50, anchor="center")
        qual_tree.column("Qualifikationstyp", width=150, anchor="w")
        qual_tree.column("Zertifikat-Link", width=250, anchor="w")
        qual_tree.column("Gültig bis", width=120, anchor="center")

        qual_scrollbar = ttk.Scrollbar(qual_frame, orient="vertical", command=qual_tree.yview)
        qual_tree.configure(yscrollcommand=qual_scrollbar.set)
        qual_scrollbar.pack(side="right", fill="y", in_=qual_tree)

        # Populate qualifications for THIS employee
        self.populate_qualification_list(employee_id, tree_widget=qual_tree)
        qual_tree.bind("<Double-1>", lambda e: self.open_link(qual_tree.item(qual_tree.selection(), "values")[2]))


        # Eyesight Frame
        eyesight_frame = ttk.LabelFrame(details_window, text="Sehfähigkeit")
        eyesight_frame.pack(padx=10, pady=10, expand=True, fill="both")

        eyesight_tree = ttk.Treeview(eyesight_frame, columns=("ID", "Status", "Zertifikat-Link", "Gültig bis"), show="headings")
        eyesight_tree.pack(expand=True, fill="both")

        eyesight_tree.heading("ID", text="ID")
        eyesight_tree.heading("Status", text="Status")
        eyesight_tree.heading("Zertifikat-Link", text="Zertifikat-Link")
        eyesight_tree.heading("Gültig bis", text="Gültig bis")

        eyesight_tree.column("ID", width=50, anchor="center")
        eyesight_tree.column("Status", width=150, anchor="w")
        eyesight_tree.column("Zertifikat-Link", width=250, anchor="w")
        eyesight_tree.column("Gültig bis", width=120, anchor="center")

        eyesight_scrollbar = ttk.Scrollbar(eyesight_frame, orient="vertical", command=eyesight_tree.yview)
        eyesight_tree.configure(yscrollcommand=eyesight_scrollbar.set)
        eyesight_scrollbar.pack(side="right", fill="y", in_=eyesight_tree)

        # Populate eyesight for THIS employee
        self.populate_eyesight_list(employee_id, tree_widget=eyesight_tree)
        eyesight_tree.bind("<Double-1>", lambda e: self.open_link(eyesight_tree.item(eyesight_tree.selection(), "values")[2]))


    # --- Expiration Check Functionality ---
    def check_expirations(self):
        expiring_soon_qual = [] # Qualifications expiring within 30 days
        expired_qual = []       # Expired qualifications
        expiring_soon_eyesight = [] # Eyesight expiring within 30 days
        expired_eyesight = []       # Expired eyesight

        today = datetime.now().date()
        thirty_days_from_now = today + timedelta(days=120)

        conn = sqlite3.connect('personalverwaltung.db')
        cursor = conn.cursor()

        # Check qualifications
        cursor.execute("SELECT m.vorname, m.nachname, q.qualifikationstyp, q.gueltig_bis FROM qualifikationen q JOIN mitarbeiter m ON q.mitarbeiter_id = m.id WHERE q.gueltig_bis IS NOT NULL AND q.gueltig_bis != ''")
        quals = cursor.fetchall()
        for vorname, nachname, qual_type, gueltig_bis_str in quals:
            try:
                gueltig_bis_date = datetime.strptime(gueltig_bis_str, '%Y-%m-%d').date()
                if gueltig_bis_date < today:
                    expired_qual.append(f"{vorname} {nachname}: {qual_type} (Abgelaufen am: {gueltig_bis_str})")
                elif gueltig_bis_date <= thirty_days_from_now:
                    expiring_soon_qual.append(f"{vorname} {nachname}: {qual_type} (Läuft ab am: {gueltig_bis_str})")
            except ValueError:
                # Handle invalid date format in DB (should ideally be prevented by input validation)
                print(f"Warnung: Ungültiges Datumsformat für Qualifikation '{qual_type}' von {vorname} {nachname}: {gueltig_bis_str}")


        # Check eyesight
        cursor.execute("SELECT m.vorname, m.nachname, s.status, s.gueltig_bis FROM sehfaehigkeit s JOIN mitarbeiter m ON s.mitarbeiter_id = m.id WHERE s.gueltig_bis IS NOT NULL AND s.gueltig_bis != ''")
        eyesight_records = cursor.fetchall()
        for vorname, nachname, status, gueltig_bis_str in eyesight_records:
            try:
                gueltig_bis_date = datetime.strptime(gueltig_bis_str, '%Y-%m-%d').date()
                if gueltig_bis_date < today:
                    expired_eyesight.append(f"{vorname} {nachname}: Sehfähigkeit '{status}' (Abgelaufen am: {gueltig_bis_str})")
                elif gueltig_bis_date <= thirty_days_from_now:
                    expiring_soon_eyesight.append(f"{vorname} {nachname}: Sehfähigkeit '{status}' (Läuft ab am: {gueltig_bis_str})")
            except ValueError:
                # Handle invalid date format in DB
                print(f"Warnung: Ungültiges Datumsformat für Sehfähigkeit '{status}' von {vorname} {nachname}: {gueltig_bis_str}")

        conn.close()

        alert_message = []
        if expired_qual:
            alert_message.append("Abgelaufene Qualifikationen:")
            alert_message.extend(expired_qual)
            alert_message.append("-" * 30)
        if expiring_soon_qual:
            alert_message.append("Ablaufende Qualifikationen (in den nächsten 120 Tagen):")
            alert_message.extend(expiring_soon_qual)
            alert_message.append("-" * 30)
        if expired_eyesight:
            alert_message.append("Abgelaufene Sehfähigkeitsnachweise:")
            alert_message.extend(expired_eyesight)
            alert_message.append("-" * 30)
        if expiring_soon_eyesight:
            alert_message.append("Ablaufende Sehfähigkeitsnachweise (in den nächsten 120 Tagen):")
            alert_message.extend(expiring_soon_eyesight)
            alert_message.append("-" * 30)

        if alert_message:
            # Join messages with newline and show alert
            message = "\n".join(alert_message)
            show_message("Gültigkeitsprüfung", message)
        else:
            show_message("Gültigkeitsprüfung", "Keine abgelaufenen oder in den nächsten 120 Tagen ablaufenden Zertifizierungen gefunden.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PersonnelManagementApp(root)
    root.mainloop()
