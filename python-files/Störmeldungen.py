Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
import pandas as pd
from datetime import datetime
import os

# -- Konfiguration der Anwendung --
APP_TITLE = "Störmelde-Manager (SEW-Eurodrive Design)"
EXCEL_FILE = "stoermeldungen.xlsx"
SEW_RED = "#D70025"
SEW_DARK_GRAY = "#252525"
SEW_LIGHT_GRAY = "#3A3A3A"
SEW_TEXT_COLOR = "#FFFFFF"

# -- Setup für das moderne UI (CustomTkinter) --
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ToolTip:
    """ Erzeugt ein Tooltip-Fenster für ein Widget. """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#2b2b2b", relief='solid', borderwidth=1,
                         font=("Arial", "10", "normal"), fg="white")
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class AddEntryDialog(ctk.CTkToplevel):
    """Dialog zum Hinzufügen einer neuen Störmeldung."""
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.title("Neue Störmeldung hinzufügen")
        self.geometry("400x300")
        self.grab_set() # Macht das Fenster modal

        self.result = None

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Fehlerbeschreibung:").pack(anchor="w")
        self.desc_entry = ctk.CTkEntry(main_frame, width=300)
        self.desc_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Anlage/Maschine:").pack(anchor="w")
        self.anlage_entry = ctk.CTkEntry(main_frame, width=300)
        self.anlage_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Priorität:").pack(anchor="w")
        self.prio_combo = ctk.CTkComboBox(main_frame, values=["Niedrig", "Mittel", "Hoch"], width=300)
        self.prio_combo.pack(fill="x", pady=(0, 20))
        self.prio_combo.set("Mittel")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom")

        ctk.CTkButton(button_frame, text="Abbrechen", command=self.cancel).pack(side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Speichern", command=self.save, fg_color=SEW_RED, hover_color="#A9001D").pack(side="right")

    def save(self):
        desc = self.desc_entry.get().strip()
        anlage = self.anlage_entry.get().strip()
        
        if not desc or not anlage:
            messagebox.showerror("Fehler", "Bitte füllen Sie alle Felder aus.", parent=self)
            return

        self.result = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Fehlerbeschreibung": desc,
            "Anlage": anlage,
            "Priorität": self.prio_combo.get(),
            "Status": "Offen"
        }
        self.destroy()

    def cancel(self):
        self.destroy()

class App(ctk.CTk):
    """Hauptanwendungsklasse."""
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x700")

        self.df = self.load_data()
        self.create_widgets()
        self.populate_treeview()

    def load_data(self):
        """Lädt Daten aus der Excel-Datei oder erstellt eine neue, falls nicht vorhanden."""
        expected_cols = ["Timestamp", "Fehlerbeschreibung", "Anlage", "Priorität", "Status"]
        if not os.path.exists(EXCEL_FILE):
            df = pd.DataFrame(columns=expected_cols)
            df.to_excel(EXCEL_FILE, index=False)
            messagebox.showinfo("Info", f"'{EXCEL_FILE}' wurde nicht gefunden und neu erstellt.")
            return df
        try:
            return pd.read_excel(EXCEL_FILE)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", f"Konnte die Excel-Datei nicht laden: {e}")
            return pd.DataFrame(columns=expected_cols)

    def save_data(self):
        """Speichert die aktuellen Daten in die Excel-Datei."""
        try:
            self.df.to_excel(EXCEL_FILE, index=False)
            messagebox.showinfo("Gespeichert", "Die Änderungen wurden erfolgreich in der Excel-Datei gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", f"Die Daten konnten nicht gespeichert werden: {e}")

    def create_widgets(self):
        """Erstellt alle UI-Elemente."""
        # --- Top Frame mit Titel und Buttons ---
        top_frame = ctk.CTkFrame(self, height=60, fg_color=SEW_RED)
        top_frame.pack(fill="x", side="top")
        
        title_label = ctk.CTkLabel(top_frame, text=APP_TITLE, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=20, pady=10)

        # --- Button Frame ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)

        self.add_button = ctk.CTkButton(button_frame, text="➕ Neu", command=self.add_entry, width=120)
        self.add_button.pack(side="left")
        ToolTip(self.add_button, "Neue Störmeldung hinzufügen")

        self.edit_button = ctk.CTkButton(button_frame, text="✏️ Status ändern", command=self.edit_status, width=120)
        self.edit_button.pack(side="left", padx=10)
        ToolTip(self.edit_button, "Den Status der ausgewählten Meldung ändern (z.B. auf 'In Bearbeitung')")

        self.delete_button = ctk.CTkButton(button_frame, text="❌ Löschen", command=self.delete_entry, width=120)
        self.delete_button.pack(side="left")
        ToolTip(self.delete_button, "Ausgewählte Meldung löschen")

        self.save_button = ctk.CTkButton(button_frame, text="💾 Speichern", command=self.save_data, fg_color=SEW_DARK_GRAY, width=120)
        self.save_button.pack(side="left", padx=(10,0))
        ToolTip(self.save_button, "Alle Änderungen in die Excel-Datei schreiben")
        
        # --- Such- und Filter-Frame ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 10))

        search_label = ctk.CTkLabel(search_frame, text="Suchen:")
        search_label.pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_data())
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300)
        search_entry.pack(side="left")

        # --- Treeview (Tabelle) ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background=SEW_DARK_GRAY,
                        foreground=SEW_TEXT_COLOR,
                        fieldbackground=SEW_DARK_GRAY,
                        rowheight=25,
                        font=('Calibri', 11))
        style.map('Treeview', background=[('selected', SEW_RED)])
        style.configure("Treeview.Heading", 
                        font=('Calibri', 12, 'bold'),
                        background=SEW_LIGHT_GRAY,
                        foreground=SEW_TEXT_COLOR)
        style.map("Treeview.Heading",
                  background=[('active', SEW_DARK_GRAY)])


        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_frame, columns=list(self.df.columns), show="headings")
        
        for col in self.df.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=150, anchor='w')

        self.tree.column("Fehlerbeschreibung", width=400)
        self.tree.column("Timestamp", width=150)

        vsb = ctk.CTkScrollbar(tree_frame, command=self.tree.yview, button_color=SEW_RED, button_hover_color="#A9001D")
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ctk.CTkScrollbar(tree_frame, command=self.tree.xview, orientation="horizontal", button_color=SEW_RED, button_hover_color="#A9001D")
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)

        self.tree.pack(expand=True, fill="both")

    def populate_treeview(self, data=None):
        """Füllt die Tabelle mit Daten."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        df_to_show = self.df if data is None else data
        
        for index, row in df_to_show.iterrows():
            self.tree.insert("", "end", values=list(row), iid=index)

    def add_entry(self):
        """Öffnet den Dialog zum Hinzufügen und verarbeitet das Ergebnis."""
        dialog = AddEntryDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            new_data = pd.DataFrame([dialog.result])
            self.df = pd.concat([self.df, new_data], ignore_index=True)
            self.filter_data()

    def edit_status(self):
        """Ändert den Status des ausgewählten Eintrags."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie zuerst einen Eintrag aus der Liste aus.")
            return
        
        item_index = int(selected_item[0])
        current_status = self.df.loc[item_index, 'Status']
        
        new_status = simpledialog.askstring("Status ändern", "Neuen Status eingeben:", 
                                            initialvalue=current_status, parent=self)
        
        if new_status:
            self.df.loc[item_index, 'Status'] = new_status
            self.filter_data() # Aktualisiert die Ansicht

    def delete_entry(self):
        """Löscht den ausgewählten Eintrag."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie zuerst einen Eintrag aus der Liste aus.")
            return

        if messagebox.askyesno("Löschen bestätigen", "Möchten Sie den ausgewählten Eintrag wirklich löschen?"):
            item_index = int(selected_item[0])
...             self.df = self.df.drop(item_index).reset_index(drop=True)
...             self.filter_data()
... 
...     def filter_data(self):
...         """Filtert die Daten basierend auf der Sucheingabe."""
...         search_term = self.search_var.get().lower()
...         if not search_term:
...             self.populate_treeview()
...             return
...         
...         # Sucht in allen Spalten nach dem Begriff
...         df_filtered = self.df[self.df.apply(lambda row: any(str(cell).lower().find(search_term) != -1 for cell in row), axis=1)]
...         self.populate_treeview(df_filtered)
... 
...     def sort_by_column(self, col, reverse):
...         """Sortiert die Tabelle nach einer Spalte."""
...         try:
...             # Konvertiere Spalte zu numerischem Typ, wenn möglich, für korrekte Sortierung
...             data = self.df.copy()
...             data[col] = pd.to_numeric(data[col], errors='ignore')
...             data = data.sort_values(by=col, ascending=not reverse)
...             
...             self.populate_treeview(data)
...             # Ändere den Sortierbefehl für den nächsten Klick
...             self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))
...         except Exception as e:
...             messagebox.showerror("Sortierfehler", f"Spalte '{col}' konnte nicht sortiert werden.\nFehler: {e}")
... 
... if __name__ == "__main__":
...     app = App()
...     app.mainloop()
>>> [DEBUG ON]
>>> [DEBUG OFF]
>>> 
================================ RESTART: Shell ================================
