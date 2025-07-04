import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# === Database Setup ===
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS gebruikers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS projecten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS uren (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gebruiker_id INTEGER,
    project_id INTEGER,
    datum TEXT,
    uren REAL,
    FOREIGN KEY(gebruiker_id) REFERENCES gebruikers(id),
    FOREIGN KEY(project_id) REFERENCES projecten(id)
)""")

conn.commit()

# === GUI Application ===
class UrenregistratieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Urenregistratie Systeem")
        self.geometry("600x400")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.init_tab_gebruiker()
        self.init_tab_project()
        self.init_tab_uren()
        self.init_tab_overzicht()

    def init_tab_gebruiker(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Gebruiker toevoegen")

        ttk.Label(tab, text="Naam:").pack(pady=10)
        self.entry_naam = ttk.Entry(tab)
        self.entry_naam.pack()

        ttk.Button(tab, text="Voeg toe", command=self.gebruiker_toevoegen).pack(pady=10)

    def init_tab_project(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Project toevoegen")

        ttk.Label(tab, text="Projectnaam:").pack(pady=10)
        self.entry_project = ttk.Entry(tab)
        self.entry_project.pack()

        ttk.Button(tab, text="Voeg toe", command=self.project_toevoegen).pack(pady=10)

    def init_tab_uren(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Uren registreren")

        self.combo_gebruiker = ttk.Combobox(tab, state="readonly")
        self.combo_project = ttk.Combobox(tab, state="readonly")
        self.entry_datum = ttk.Entry(tab)
        self.entry_uren = ttk.Entry(tab)

        ttk.Label(tab, text="Gebruiker:").pack()
        self.combo_gebruiker.pack()

        ttk.Label(tab, text="Project:").pack()
        self.combo_project.pack()

        ttk.Label(tab, text="Datum (YYYY-MM-DD):").pack()
        self.entry_datum.pack()

        ttk.Label(tab, text="Uren:").pack()
        self.entry_uren.pack()

        ttk.Button(tab, text="Registreer uren", command=self.uren_loggen).pack(pady=10)
        self.update_comboboxes()

    def init_tab_overzicht(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Uren overzicht")

        self.combo_overzicht = ttk.Combobox(tab, state="readonly")
        self.combo_overzicht.pack(pady=10)
        ttk.Button(tab, text="Toon overzicht", command=self.overzicht_opvragen).pack()

        self.text_output = tk.Text(tab, height=15)
        self.text_output.pack(pady=10)

        self.update_gebruikers_overzicht()

    def gebruiker_toevoegen(self):
        naam = self.entry_naam.get().strip()
        if not naam:
            messagebox.showerror("Fout", "Naam mag niet leeg zijn.")
            return
        cursor.execute("INSERT INTO gebruikers (naam) VALUES (?)", (naam,))
        conn.commit()
        messagebox.showinfo("Succes", f"Gebruiker '{naam}' toegevoegd.")
        self.entry_naam.delete(0, tk.END)
        self.update_comboboxes()
        self.update_gebruikers_overzicht()

    def project_toevoegen(self):
        project = self.entry_project.get().strip()
        if not project:
            messagebox.showerror("Fout", "Projectnaam mag niet leeg zijn.")
            return
        cursor.execute("INSERT INTO projecten (naam) VALUES (?)", (project,))
        conn.commit()
        messagebox.showinfo("Succes", f"Project '{project}' toegevoegd.")
        self.entry_project.delete(0, tk.END)
        self.update_comboboxes()

    def uren_loggen(self):
        try:
            gebruiker = self.combo_gebruiker.get()
            project = self.combo_project.get()
            datum = self.entry_datum.get().strip()
            uren = float(self.entry_uren.get().strip())

            datetime.strptime(datum, "%Y-%m-%d")  # valideer datum

            gebruiker_id = self.get_gebruiker_id(gebruiker)
            project_id = self.get_project_id(project)

            cursor.execute("""
                INSERT INTO uren (gebruiker_id, project_id, datum, uren)
                VALUES (?, ?, ?, ?)""", (gebruiker_id, project_id, datum, uren))
            conn.commit()
            messagebox.showinfo("Succes", "Uren geregistreerd.")
            self.entry_datum.delete(0, tk.END)
            self.entry_uren.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Fout", "Ongeldige invoer.")

    def overzicht_opvragen(self):
        self.text_output.delete(1.0, tk.END)
        gebruiker = self.combo_overzicht.get()
        gebruiker_id = self.get_gebruiker_id(gebruiker)

        cursor.execute("""
            SELECT p.naam, u.datum, u.uren
            FROM uren u
            JOIN projecten p ON u.project_id = p.id
            WHERE u.gebruiker_id = ?
            ORDER BY u.datum
        """, (gebruiker_id,))
        rows = cursor.fetchall()

        if rows:
            for project, datum, uren in rows:
                self.text_output.insert(tk.END, f"{datum} - {project}: {uren} uur\n")
        else:
            self.text_output.insert(tk.END, "Geen uren geregistreerd.")

    def update_comboboxes(self):
        cursor.execute("SELECT naam FROM gebruikers")
        gebruikers = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT naam FROM projecten")
        projecten = [r[0] for r in cursor.fetchall()]

        self.combo_gebruiker['values'] = gebruikers
        self.combo_project['values'] = projecten

    def update_gebruikers_overzicht(self):
        cursor.execute("SELECT naam FROM gebruikers")
        gebruikers = [r[0] for r in cursor.fetchall()]
        self.combo_overzicht['values'] = gebruikers

    def get_gebruiker_id(self, naam):
        cursor.execute("SELECT id FROM gebruikers WHERE naam = ?", (naam,))
        return cursor.fetchone()[0]

    def get_project_id(self, naam):
        cursor.execute("SELECT id FROM projecten WHERE naam = ?", (naam,))
        return cursor.fetchone()[0]

# Start applicatie
if __name__ == "__main__":
    app = UrenregistratieApp()
    app.mainloop()
