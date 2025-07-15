import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from pathlib import Path
import datetime
import getpass

class CAMManager:
    def __init__(self, root):
        self.root = root
        self.root.title("CAM Datenverwaltung")
        self.root.geometry("1000x750")
        
        # Pfade definieren
        self.archiv_base_path = Path("J:/CAM/P/NC-Data/CCC/Archiv_NX")
        self.workdir_path = Path.home() / "Workdir"  # C:\Users\[Benutzer]\Workdir
        
        # Standard-Maschinen
        self.machines = ["5250_5255", "5347"]
        
        # Aktuelle Maschinenauswahl für Anzeige (beide Fenster verwenden dieselbe Maschine)
        self.current_machine = "5250_5255"
        
        # Aktuellen Benutzernamen ermitteln
        self.username = getpass.getuser()
        
        self.setup_ui()
        self.sync_machines_from_archive()
        self.refresh_project_list()
        
    def setup_ui(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel mit Benutzername
        title_label = ttk.Label(main_frame, text=f"CAM Datenverwaltung - Benutzer: {self.username}", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Maschinen-Management
        machine_frame = ttk.LabelFrame(main_frame, text="Maschinen-Verwaltung", padding="10")
        machine_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(machine_frame, text="Verfügbare Maschinen:").grid(row=0, column=0, sticky=tk.W)
        
        self.machine_listbox = tk.Listbox(machine_frame, height=3, width=20)
        self.machine_listbox.grid(row=0, column=1, padx=(10, 5), sticky=(tk.W, tk.E))
        
        # Maschinen-Buttons
        btn_machine_frame = ttk.Frame(machine_frame)
        btn_machine_frame.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Button(btn_machine_frame, text="Neue Maschine", 
                  command=self.add_machine).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btn_machine_frame, text="Maschine entfernen", 
                  command=self.remove_machine).grid(row=0, column=1)
        
        self.update_machine_list()
        
        # Sektion 1: Neues Projekt erstellen
        create_frame = ttk.LabelFrame(main_frame, text="Neues Projekt erstellen", 
                                     padding="10")
        create_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), 
                         pady=(0, 10))
        
        ttk.Label(create_frame, text="TYP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.typ_entry = ttk.Entry(create_frame, width=20)
        self.typ_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(create_frame, text="Sachnummer:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.sachnummer_entry = ttk.Entry(create_frame, width=20)
        self.sachnummer_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(create_frame, text="Speicherort:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        ttk.Label(create_frame, text="Workdir - Maschine:").grid(row=1, column=1, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        # Dropdown für Maschinenauswahl
        self.create_machine_var = tk.StringVar(value=self.machines[0] if self.machines else "5250_5255")
        self.create_machine_combo = ttk.Combobox(create_frame, textvariable=self.create_machine_var, 
                                               values=self.machines, state="readonly", width=15)
        self.create_machine_combo.grid(row=1, column=2, padx=(5, 0), pady=(10, 0))
        
        create_btn = ttk.Button(create_frame, text="Projekt erstellen", 
                               command=self.create_project)
        create_btn.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        # Sektion 2: Projektliste und Verwaltung
        manage_frame = ttk.LabelFrame(main_frame, text="Projektverwaltung", 
                                     padding="10")
        manage_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         pady=(0, 10))
        
        # Workdir-Sektion (Links)
        workdir_frame = ttk.LabelFrame(manage_frame, text="WORKDIR", padding="5")
        workdir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=(0, 5))
        
        # Maschinen-Umschalter für Workdir
        workdir_header_frame = ttk.Frame(workdir_frame)
        workdir_header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(workdir_header_frame, text="Maschine:").grid(row=0, column=0, sticky=tk.W)
        self.machine_var = tk.StringVar(value=self.current_machine)
        self.machine_combo = ttk.Combobox(workdir_header_frame, textvariable=self.machine_var, 
                                         values=self.machines, state="readonly", width=15)
        self.machine_combo.grid(row=0, column=1, padx=(5, 0))
        self.machine_combo.bind('<<ComboboxSelected>>', self.on_machine_change)
        
        # Treeview für Workdir
        self.workdir_tree = ttk.Treeview(workdir_frame, columns=("Typ", "Sachnummer", "Datum"), 
                                        show="headings", height=15)
        self.workdir_tree.heading("Typ", text="TYP", command=lambda: self.sort_tree(self.workdir_tree, "Typ", False))
        self.workdir_tree.heading("Sachnummer", text="Sachnummer", command=lambda: self.sort_tree(self.workdir_tree, "Sachnummer", False))
        self.workdir_tree.heading("Datum", text="Geändert", command=lambda: self.sort_tree(self.workdir_tree, "Datum", True))
        self.workdir_tree.column("Typ", width=80)
        self.workdir_tree.column("Sachnummer", width=80)
        self.workdir_tree.column("Datum", width=100)
        
        # Tags für farbliche Markierung
        self.workdir_tree.tag_configure("newer", background="#90EE90")  # Hellgrün für neuere Version
        self.workdir_tree.tag_configure("older", background="#FFB6C1")   # Hellrot für ältere Version
        self.workdir_tree.tag_configure("same", background="#F0F0F0")    # Grau für gleiche Version
        self.workdir_tree.tag_configure("unique", background="#E6E6FA")  # Lavendel für nur hier vorhanden
        
        # Sortierrichtung für Workdir-Tree speichern
        self.workdir_sort_reverse = {"Typ": False, "Sachnummer": False, "Datum": True}
        
        # Scrollbar für Workdir-Treeview
        workdir_scrollbar = ttk.Scrollbar(workdir_frame, orient="vertical", 
                                         command=self.workdir_tree.yview)
        self.workdir_tree.configure(yscrollcommand=workdir_scrollbar.set)
        
        self.workdir_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        workdir_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Button für Workdir-Ordner öffnen
        open_workdir_btn = ttk.Button(workdir_frame, text="Ordner öffnen", 
                                     command=lambda: self.open_project_folder("workdir"))
        open_workdir_btn.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Mittel-Sektion mit Buttons
        button_frame = ttk.Frame(manage_frame)
        button_frame.grid(row=0, column=1, padx=10, pady=50)
        
        # Checkin-Button (Workdir → Archiv)
        checkin_btn = ttk.Button(button_frame, text="→\nCheckin\n→", 
                                command=self.checkin_project, width=12)
        checkin_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Checkout-Button (Archiv → Workdir)
        checkout_btn = ttk.Button(button_frame, text="←\nCheckout\n←", 
                                 command=self.checkout_project, width=12)
        checkout_btn.grid(row=1, column=0, pady=(0, 10))
        
        # Refresh-Button
        refresh_btn = ttk.Button(button_frame, text="↻\nAktualisieren", 
                                command=self.refresh_project_list, width=12)
        refresh_btn.grid(row=2, column=0)
        
        # Archiv-Sektion (Rechts)
        archiv_frame = ttk.LabelFrame(manage_frame, text="ARCHIV", 
                                     padding="5")
        archiv_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         padx=(5, 0))
        
        # Maschinen-Umschalter für Archiv (nur Anzeige, da mit Workdir synchronisiert)
        archiv_header_frame = ttk.Frame(archiv_frame)
        archiv_header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(archiv_header_frame, text="Maschine:").grid(row=0, column=0, sticky=tk.W)
        self.archiv_machine_label = ttk.Label(archiv_header_frame, text=self.current_machine, 
                                             font=("Arial", 10, "bold"), foreground="blue")
        self.archiv_machine_label.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        # Treeview für Archiv
        self.archiv_tree = ttk.Treeview(archiv_frame, columns=("Typ", "Sachnummer", "Datum"), 
                                       show="headings", height=15)
        self.archiv_tree.heading("Typ", text="TYP", command=lambda: self.sort_tree(self.archiv_tree, "Typ", False))
        self.archiv_tree.heading("Sachnummer", text="Sachnummer", command=lambda: self.sort_tree(self.archiv_tree, "Sachnummer", False))
        self.archiv_tree.heading("Datum", text="Geändert", command=lambda: self.sort_tree(self.archiv_tree, "Datum", True))
        self.archiv_tree.column("Typ", width=80)
        self.archiv_tree.column("Sachnummer", width=80)
        self.archiv_tree.column("Datum", width=100)
        
        # Tags für farbliche Markierung
        self.archiv_tree.tag_configure("newer", background="#90EE90")  # Hellgrün für neuere Version
        self.archiv_tree.tag_configure("older", background="#FFB6C1")   # Hellrot für ältere Version
        self.archiv_tree.tag_configure("same", background="#F0F0F0")    # Grau für gleiche Version
        self.archiv_tree.tag_configure("unique", background="#E6E6FA")  # Lavendel für nur hier vorhanden
        
        # Sortierrichtung für Archiv-Tree speichern
        self.archiv_sort_reverse = {"Typ": False, "Sachnummer": False, "Datum": True}
        
        # Scrollbar für Archiv-Treeview
        archiv_scrollbar = ttk.Scrollbar(archiv_frame, orient="vertical", 
                                        command=self.archiv_tree.yview)
        self.archiv_tree.configure(yscrollcommand=archiv_scrollbar.set)
        
        self.archiv_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        archiv_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Button für Archiv-Ordner öffnen
        open_archiv_btn = ttk.Button(archiv_frame, text="Ordner öffnen", 
                                    command=lambda: self.open_project_folder("archiv"))
        open_archiv_btn.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Status-Label
        self.status_label = ttk.Label(main_frame, text="Bereit", 
                                     foreground="green")
        self.status_label.grid(row=4, column=0, columnspan=4, pady=(10, 0))
        
        # Ladeanzeige (wird bei Bedarf angezeigt)
        self.loading_label = ttk.Label(main_frame, text="", 
                                      font=("Arial", 12, "bold"), foreground="orange")
        self.loading_label.grid(row=5, column=0, columnspan=4, pady=(5, 0))
        
        # Legende für Farbkodierung
        legend_frame = ttk.LabelFrame(main_frame, text="Legende", padding="5")
        legend_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(legend_frame, text="🟢 Neuer", background="#90EE90").grid(row=0, column=0, padx=(0, 10))
        ttk.Label(legend_frame, text="🔴 Älter", background="#FFB6C1").grid(row=0, column=1, padx=(0, 10))
        ttk.Label(legend_frame, text="⚪ Gleich", background="#F0F0F0").grid(row=0, column=2, padx=(0, 10))
        ttk.Label(legend_frame, text="🟣 Nur hier", background="#E6E6FA").grid(row=0, column=3)
        
        # Grid-Konfiguration für Responsivität
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.columnconfigure(2, weight=1)
        manage_frame.rowconfigure(0, weight=1)
        workdir_frame.columnconfigure(0, weight=1)
        workdir_frame.rowconfigure(1, weight=1)
        archiv_frame.columnconfigure(0, weight=1)
        archiv_frame.rowconfigure(1, weight=1)
        
    def update_machine_list(self):
        """Aktualisiert die Maschinenliste"""
        self.machine_listbox.delete(0, tk.END)
        for machine in self.machines:
            self.machine_listbox.insert(tk.END, machine)
    
    def add_machine(self):
        """Fügt eine neue Maschine hinzu"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Neue Maschine hinzufügen")
        dialog.geometry("300x170")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Name der neuen Maschine:", font=("Arial", 10)).pack(pady=20)
        
        entry = ttk.Entry(dialog, width=20, font=("Arial", 10))
        entry.pack(pady=5)
        entry.focus()
        
        result = tk.StringVar()
        
        def on_ok():
            machine_name = entry.get().strip()
            if machine_name and machine_name not in self.machines:
                result.set(machine_name)
                dialog.destroy()
            elif machine_name in self.machines:
                messagebox.showerror("Fehler", "Maschine existiert bereits!")
            else:
                messagebox.showerror("Fehler", "Bitte einen Namen eingeben!")
        
        def on_cancel():
            dialog.destroy()
        
        def on_enter(event):
            on_ok()
        
        entry.bind('<Return>', on_enter)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        
        if result.get():
            self.machines.append(result.get())
            self.machines.sort()
            self.update_machine_list()
            self.machine_combo['values'] = self.machines
            self.create_machine_combo['values'] = self.machines
            
            # Maschinenverzeichnisse erstellen
            new_machine = result.get()
            try:
                # Nur Workdir-Verzeichnis erstellen (kein Archiv-Verzeichnis)
                (self.workdir_path / new_machine).mkdir(parents=True, exist_ok=True)
                # Archiv-Verzeichnis wird automatisch beim ersten Checkin erstellt
                self.status_label.config(text=f"Maschine '{new_machine}' hinzugefügt und Workdir-Verzeichnis erstellt", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Maschine hinzugefügt, aber Fehler beim Erstellen des Verzeichnisses: {str(e)}", foreground="orange")
    
    def remove_machine(self):
        """Entfernt eine ausgewählte Maschine"""
        selection = self.machine_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte eine Maschine auswählen!")
            return
        
        machine = self.machines[selection[0]]
        
        # Prüfen ob Projekte in dieser Maschine existieren
        machine_workdir = self.workdir_path / machine
        machine_archiv = self.archiv_base_path / machine
        
        has_workdir_projects = machine_workdir.exists() and any(machine_workdir.iterdir())
        has_archiv_projects = machine_archiv.exists() and any(machine_archiv.iterdir())
        
        if has_workdir_projects or has_archiv_projects:
            locations = []
            if has_workdir_projects:
                locations.append("Workdir")
            if has_archiv_projects:
                locations.append("Archiv")
            
            result = messagebox.askyesno("Warnung", 
                                       f"In der Maschine '{machine}' befinden sich noch Projekte in: {', '.join(locations)}.\n"
                                       f"Maschine trotzdem entfernen?\n\n"
                                       f"Die Ordner werden nicht gelöscht, nur aus der Liste entfernt.")
            if not result:
                return
        
        self.machines.remove(machine)
        self.update_machine_list()
        self.machine_combo['values'] = self.machines
        self.create_machine_combo['values'] = self.machines
        
        # Aktuelle Auswahl anpassen falls nötig
        if self.current_machine == machine:
            self.current_machine = self.machines[0] if self.machines else "5250_5255"
            self.machine_var.set(self.current_machine)
            self.archiv_machine_label.config(text=self.current_machine)
            self.refresh_project_list()
        
        # Dropdown für Projekterstellung anpassen
        if self.create_machine_var.get() == machine:
            self.create_machine_var.set(self.machines[0] if self.machines else "5250_5255")
        
        self.status_label.config(text=f"Maschine '{machine}' entfernt", foreground="orange")
    
    def sync_machines_from_archive(self):
        """Synchronisiert die Maschinenliste mit den Ordnern im Archiv"""
        try:
            if not self.archiv_base_path.exists():
                return
            
            # Sammle alle Maschinenordner aus dem Archiv
            archive_machines = []
            for item in self.archiv_base_path.iterdir():
                if (item.is_dir() and not item.name.startswith('.') and 
                    not item.name.startswith("Backups")):
                    archive_machines.append(item.name)
            
            # Sortiere die Liste
            archive_machines.sort()
            
            # Prüfe ob neue Maschinen hinzugekommen sind
            new_machines = set(archive_machines) - set(self.machines)
            removed_machines = set(self.machines) - set(archive_machines)
            
            if new_machines or removed_machines:
                # Aktualisiere die Maschinenliste
                self.machines = archive_machines.copy()
                
                # Standard-Maschinen hinzufügen falls sie nicht existieren
                for default_machine in ["5250_5255", "5347"]:
                    if default_machine not in self.machines:
                        self.machines.append(default_machine)
                
                self.machines.sort()
                
                # UI aktualisieren
                self.update_machine_list()
                self.machine_combo['values'] = self.machines
                self.create_machine_combo['values'] = self.machines
                
                # Aktuelle Maschine anpassen falls nötig
                if self.current_machine not in self.machines:
                    self.current_machine = self.machines[0] if self.machines else "5250_5255"
                    self.machine_var.set(self.current_machine)
                    self.archiv_machine_label.config(text=self.current_machine)
                
                # Dropdown für Projekterstellung anpassen
                if self.create_machine_var.get() not in self.machines:
                    self.create_machine_var.set(self.machines[0] if self.machines else "5250_5255")
                
                # Status-Meldung
                if new_machines:
                    self.status_label.config(
                        text=f"Neue Maschinen gefunden: {', '.join(new_machines)}", 
                        foreground="green"
                    )
                elif removed_machines:
                    self.status_label.config(
                        text=f"Maschinen entfernt: {', '.join(removed_machines)}", 
                        foreground="orange"
                    )
        except Exception as e:
            self.status_label.config(text=f"Fehler beim Synchronisieren: {str(e)}", foreground="red")
    
    def update_location_buttons(self):
        """Aktualisiert die Radiobuttons für Speicherorte - nur Workdir"""
        # Alle bestehenden Buttons entfernen
        for widget in self.location_buttons_frame.winfo_children():
            widget.destroy()
        
        # Nur Workdir-Buttons für alle Maschinen (kein Archiv mehr)
        for i, machine in enumerate(self.machines):
            ttk.Radiobutton(self.location_buttons_frame, text=f"Workdir ({machine})", 
                           variable=self.location_var, value=f"workdir_{machine}").grid(row=0, column=i, sticky=tk.W, padx=(0, 10))
    
    def show_loading(self, message):
        """Zeigt eine Ladeanzeige"""
        self.loading_label.config(text=f"⏳ {message}...")
        self.root.update()
    
    def hide_loading(self):
        """Versteckt die Ladeanzeige"""
        self.loading_label.config(text="")
        self.root.update()
    
    def on_machine_change(self, event):
        """Wird aufgerufen wenn die Maschine geändert wird - beide Fenster werden synchronisiert"""
        self.show_loading("Wechsle Maschine")
        try:
            self.current_machine = self.machine_var.get()
            self.archiv_machine_label.config(text=self.current_machine)
            self.refresh_project_list()
        finally:
            self.hide_loading()
    
    def sort_tree(self, tree, col, is_date):
        """Sortiert die Treeview nach der angegebenen Spalte"""
        # Bestimme welche Sortierrichtung verwendet werden soll
        if tree == self.archiv_tree:
            sort_dict = self.archiv_sort_reverse
        else:
            sort_dict = self.workdir_sort_reverse
        
        # Aktuelle Sortierrichtung umkehren
        reverse = sort_dict[col] = not sort_dict[col]
        
        # Alle Einträge sammeln
        data = []
        for child in tree.get_children():
            values = tree.item(child)['values']
            data.append((values, child))
        
        # Sortieren
        if is_date:
            # Datum sortieren - erst in datetime umwandeln für korrekte Sortierung
            def date_sort_key(item):
                try:
                    # Datum ist immer in der letzten Spalte
                    date_index = len(item[0]) - 1
                    date_str = item[0][date_index]
                    if date_str == "Unbekannt":
                        return datetime.datetime.min if reverse else datetime.datetime.max
                    return datetime.datetime.strptime(date_str, '%d.%m.%Y %H:%M')
                except:
                    return datetime.datetime.min if reverse else datetime.datetime.max
            
            data.sort(key=date_sort_key, reverse=reverse)
        else:
            # Text sortieren
            col_index = {"Typ": 0, "Sachnummer": 1, "Datum": 2}[col]
            data.sort(key=lambda x: str(x[0][col_index]).lower(), reverse=reverse)
        
        # Treeview reorganisieren
        for index, (values, child) in enumerate(data):
            tree.move(child, '', index)
        
        # Spaltenüberschrift mit Sortierrichtung aktualisieren
        col_names = {"Typ": "TYP", "Sachnummer": "Sachnummer", "Datum": "Geändert"}
        all_cols = ["Typ", "Sachnummer", "Datum"]
        
        arrow = " ↓" if reverse else " ↑"
        
        # Alle Überschriften zurücksetzen
        for c in all_cols:
            tree.heading(c, text=col_names[c])
        
        # Aktuelle Spalte mit Pfeil markieren
        tree.heading(col, text=col_names[col] + arrow)
    
    def get_folder_timestamp(self, folder_path):
        """Ermittelt den neuesten Zeitstempel eines Ordners"""
        try:
            if not folder_path.exists():
                return 0
            
            # Neuestes Änderungsdatum aller Dateien im Ordner ermitteln
            latest_time = folder_path.stat().st_mtime
            
            # Durchsuche alle Dateien und Unterordner rekursiv
            for item in folder_path.rglob('*'):
                if item.is_file():
                    file_time = item.stat().st_mtime
                    if file_time > latest_time:
                        latest_time = file_time
            
            return latest_time
        except:
            return 0
    
    def get_folder_date(self, folder_path):
        """Ermittelt das Änderungsdatum eines Ordners"""
        try:
            timestamp = self.get_folder_timestamp(folder_path)
            if timestamp == 0:
                return "Unbekannt"
            
            # Formatiere das Datum
            return datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
        except:
            return "Unbekannt"
    
    def refresh_project_list(self):
        self.show_loading("Lade Projektlisten")
        try:
            # Zuerst Maschinen synchronisieren
            self.sync_machines_from_archive()
            
            # Beide Treeviews leeren
            for item in self.archiv_tree.get_children():
                self.archiv_tree.delete(item)
            for item in self.workdir_tree.get_children():
                self.workdir_tree.delete(item)
            
            archiv_count = 0
            workdir_count = 0
            
            # Archiv-Projekte für aktuelle Maschine sammeln
            archiv_projects = {}
            current_archiv_path = self.archiv_base_path / self.current_machine
            if current_archiv_path.exists():
                for item in current_archiv_path.iterdir():
                    # Backups-Ordner und Backup-Dateien ausschließen
                    if (item.is_dir() and "_" in item.name and 
                        not item.name.startswith("Backups") and 
                        "_backup_" not in item.name):
                        parts = item.name.split("_", 1)
                        if len(parts) == 2:
                            datum = self.get_folder_date(item)
                            timestamp = self.get_folder_timestamp(item)
                            project_key = f"{parts[0]}_{parts[1]}"
                            archiv_projects[project_key] = {
                                'typ': parts[0],
                                'sachnummer': parts[1],
                                'datum': datum,
                                'timestamp': timestamp,
                                'mtime': item.stat().st_mtime
                            }
            
            # Workdir-Projekte für aktuelle Maschine sammeln
            workdir_projects = {}
            current_machine_path = self.workdir_path / self.current_machine
            if current_machine_path.exists():
                for item in current_machine_path.iterdir():
                    if item.is_dir() and "_" in item.name:
                        parts = item.name.split("_", 1)
                        if len(parts) == 2:
                            datum = self.get_folder_date(item)
                            timestamp = self.get_folder_timestamp(item)
                            project_key = f"{parts[0]}_{parts[1]}"
                            workdir_projects[project_key] = {
                                'typ': parts[0],
                                'sachnummer': parts[1],
                                'datum': datum,
                                'timestamp': timestamp,
                                'mtime': item.stat().st_mtime
                            }
            
            # Archiv-Projekte mit Farbkodierung hinzufügen
            archiv_list = []
            for project_key, project in archiv_projects.items():
                tag = "unique"  # Standard: nur im Archiv vorhanden
                
                if project_key in workdir_projects:
                    workdir_time = workdir_projects[project_key]['timestamp']
                    archiv_time = project['timestamp']
                    
                    if archiv_time > workdir_time:
                        tag = "newer"  # Archiv ist neuer
                    elif archiv_time < workdir_time:
                        tag = "older"  # Archiv ist älter
                    else:
                        tag = "same"   # Beide gleich alt
                
                archiv_list.append((project['typ'], project['sachnummer'], project['datum'], project['mtime'], tag))
            
            # Workdir-Projekte mit Farbkodierung hinzufügen
            workdir_list = []
            for project_key, project in workdir_projects.items():
                tag = "unique"  # Standard: nur im Workdir vorhanden
                
                if project_key in archiv_projects:
                    workdir_time = project['timestamp']
                    archiv_time = archiv_projects[project_key]['timestamp']
                    
                    if workdir_time > archiv_time:
                        tag = "newer"  # Workdir ist neuer
                    elif workdir_time < archiv_time:
                        tag = "older"  # Workdir ist älter
                    else:
                        tag = "same"   # Beide gleich alt
                
                workdir_list.append((project['typ'], project['sachnummer'], project['datum'], project['mtime'], tag))
            
            # Nach Datum sortiert zur Archiv-Treeview hinzufügen (neueste zuerst)
            for project in sorted(archiv_list, key=lambda x: x[3], reverse=True):
                self.archiv_tree.insert("", "end", values=(project[0], project[1], project[2]), tags=(project[4],))
            archiv_count = len(archiv_list)
            
            # Nach Datum sortiert zur Workdir-Treeview hinzufügen (neueste zuerst)
            for project in sorted(workdir_list, key=lambda x: x[3], reverse=True):
                self.workdir_tree.insert("", "end", values=(project[0], project[1], project[2]), tags=(project[4],))
            workdir_count = len(workdir_list)
            
            # Titel mit aktueller Maschine aktualisieren
            workdir_frame = self.workdir_tree.master
            workdir_frame.configure(text=f"WORKDIR ({self.current_machine})")
            
            archiv_frame = self.archiv_tree.master
            archiv_frame.configure(text=f"ARCHIV ({self.current_machine})")
            
            self.status_label.config(text=f"Maschine {self.current_machine} - Workdir: {workdir_count} | Archiv: {archiv_count} Projekte", 
                                   foreground="blue")
        finally:
            self.hide_loading()
    
    def get_selected_project_archiv(self):
        selection = self.archiv_tree.selection()
        if not selection:
            return None
        
        item = self.archiv_tree.item(selection[0])
        values = item['values']
        typ, sachnummer = values[0], values[1]
        project_name = f"{typ}_{sachnummer}"
        
        return {
            'name': project_name,
            'typ': typ,
            'sachnummer': sachnummer,
            'maschine': self.current_machine,
            'standort': 'archiv'
        }
    
    def get_selected_project_workdir(self):
        selection = self.workdir_tree.selection()
        if not selection:
            return None
        
        item = self.workdir_tree.item(selection[0])
        values = item['values']
        typ, sachnummer = values[0], values[1]
        project_name = f"{typ}_{sachnummer}"
        
        return {
            'name': project_name,
            'typ': typ,
            'sachnummer': sachnummer,
            'maschine': self.current_machine,
            'standort': 'workdir'
        }
    
    def create_project(self):
        typ = self.typ_entry.get().strip()
        sachnummer = self.sachnummer_entry.get().strip()
        selected_machine = self.create_machine_var.get()
        
        if not typ or not sachnummer:
            messagebox.showerror("Fehler", "Bitte TYP und Sachnummer eingeben!")
            return
        
        if not selected_machine:
            messagebox.showerror("Fehler", "Bitte eine Maschine auswählen!")
            return
        
        # Projektname erstellen
        project_name = f"{typ}_{sachnummer}"
        
        # Zielpfad (nur Workdir erlaubt)
        base_path = self.workdir_path / selected_machine
        project_path = base_path / project_name
        
        try:
            # Prüfen ob Projekt bereits existiert (in allen Verzeichnissen)
            existing_locations = []
            
            # Prüfe alle Archiv-Verzeichnisse
            for check_machine in self.machines:
                archiv_machine_path = self.archiv_base_path / check_machine
                if (archiv_machine_path / project_name).exists():
                    existing_locations.append(f"Archiv ({check_machine})")
            
            # Prüfe alle Workdir-Verzeichnisse
            for check_machine in self.machines:
                workdir_machine_path = self.workdir_path / check_machine
                if (workdir_machine_path / project_name).exists():
                    existing_locations.append(f"Workdir ({check_machine})")
            
            if existing_locations:
                messagebox.showwarning("Warnung", 
                                     f"Projekt '{project_name}' existiert bereits in: {', '.join(existing_locations)}!")
                return
            
            # Basis-Pfad erstellen falls nicht vorhanden
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Projektordner erstellen
            project_path.mkdir()
            
            # Unterordner erstellen
            subfolders = ["Modelle", "Zeichnungen", "Arbeitplan"]
            for folder in subfolders:
                (project_path / folder).mkdir()
            
            # Info-Datei erstellen
            info_file = project_path / "projekt_info.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Projekt: {project_name}\n")
                f.write(f"TYP: {typ}\n")
                f.write(f"Sachnummer: {sachnummer}\n")
                f.write(f"Maschine: {selected_machine}\n")
                f.write(f"Erstellt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Erstellt von: {self.username}\n")
                f.write(f"Erstellt in: Workdir ({selected_machine})\n")
            
            self.status_label.config(text=f"Projekt '{project_name}' erfolgreich in Workdir ({selected_machine}) erstellt!", 
                                   foreground="green")
            
            # Eingabefelder leeren
            self.typ_entry.delete(0, tk.END)
            self.sachnummer_entry.delete(0, tk.END)
            
            # Projektliste aktualisieren
            self.refresh_project_list()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden:\n{str(e)}")
            self.status_label.config(text="Fehler beim Erstellen des Projekts", 
                                   foreground="red")
    
    def checkout_project(self):
        project = self.get_selected_project_archiv()
        if not project:
            messagebox.showwarning("Warnung", "Bitte ein Projekt im Archiv auswählen!")
            return
        
        self.show_loading("Bereite Checkout vor")
        try:
            # Maschinenauswahl für Checkout
            machine_dialog = tk.Toplevel(self.root)
            machine_dialog.title("Maschine auswählen")
            machine_dialog.geometry("350x200")
            machine_dialog.transient(self.root)
            machine_dialog.grab_set()
            
            # Zentrieren
            machine_dialog.update_idletasks()
            x = (machine_dialog.winfo_screenwidth() // 2) - (machine_dialog.winfo_width() // 2)
            y = (machine_dialog.winfo_screenheight() // 2) - (machine_dialog.winfo_height() // 2)
            machine_dialog.geometry(f"+{x}+{y}")
            
            ttk.Label(machine_dialog, text=f"Auf welcher Maschine soll\n'{project['name']}' bearbeitet werden?", 
                     font=("Arial", 10)).pack(pady=20)
            
            selected_machine = tk.StringVar(value=self.machines[0] if self.machines else "5250_5255")
            
            # Radiobuttons für alle verfügbaren Maschinen
            for machine in self.machines:
                ttk.Radiobutton(machine_dialog, text=machine, variable=selected_machine, 
                               value=machine).pack()
            
            result = tk.BooleanVar()
            
            def on_ok():
                result.set(True)
                machine_dialog.destroy()
            
            def on_cancel():
                result.set(False)
                machine_dialog.destroy()
            
            btn_frame = ttk.Frame(machine_dialog)
            btn_frame.pack(pady=20)
            
            ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Abbrechen", command=on_cancel).pack(side=tk.LEFT, padx=5)
            
            self.hide_loading()
            machine_dialog.wait_window()
            
            if not result.get():
                return
            
            self.show_loading("Führe Checkout durch")
            
            # Zielpfad basierend auf ausgewählter Maschine
            machine = selected_machine.get()
            source_path = self.archiv_base_path / project['maschine'] / project['name']
            dest_path = self.workdir_path / machine / project['name']
            
            # Datumsvergleich durchführen
            if dest_path.exists():
                source_time = self.get_folder_timestamp(source_path)
                dest_time = self.get_folder_timestamp(dest_path)
                
                source_date = datetime.datetime.fromtimestamp(source_time).strftime('%d.%m.%Y %H:%M')
                dest_date = datetime.datetime.fromtimestamp(dest_time).strftime('%d.%m.%Y %H:%M')
                
                if dest_time > source_time:
                    # Workdir ist neuer als Archiv
                    result = messagebox.askyesno("⚠️ WARNUNG - Datenverlust möglich!", 
                                               f"Das Projekt '{project['name']}' im Workdir ist NEUER als im Archiv:\n\n"
                                               f"💻 Workdir ({machine}): {dest_date} (neuer)\n"
                                               f"📁 Archiv ({project['maschine']}): {source_date}\n\n"
                                               f"Beim Checkout würden Sie NEUERE Daten überschreiben!\n\n"
                                               f"Empfehlung: Checken Sie erst das Workdir-Projekt ein.\n\n"
                                               f"Trotzdem fortfahren und neuere Daten überschreiben?",
                                               icon='warning')
                    if not result:
                        self.status_label.config(text="Checkout abgebrochen - Neuere Daten geschützt", 
                                               foreground="orange")
                        return
                elif dest_time == source_time:
                    # Beide Versionen sind gleich alt
                    result = messagebox.askyesno("Information", 
                                               f"Beide Versionen von '{project['name']}' haben dasselbe Datum:\n\n"
                                               f"💻 Workdir ({machine}): {dest_date}\n"
                                               f"📁 Archiv ({project['maschine']}): {source_date}\n\n"
                                               f"Trotzdem checkout durchführen?")
                    if not result:
                        return
                else:
                    # Archiv ist neuer - normaler Fall
                    result = messagebox.askyesno("Bestätigung", 
                                               f"Projekt '{project['name']}' auf Maschine {machine} auschecken?\n\n"
                                               f"📁 Archiv ({project['maschine']}): {source_date} (neuer)\n"
                                               f"💻 Workdir ({machine}): {dest_date}\n\n"
                                               f"Das Workdir wird mit der neueren Archiv-Version überschrieben.")
                    if not result:
                        return
                
                shutil.rmtree(dest_path)
            
            # Workdir-Pfad erstellen falls nicht vorhanden
            (self.workdir_path / machine).mkdir(parents=True, exist_ok=True)
            
            # Projekt kopieren
            shutil.copytree(source_path, dest_path)
            
            # Checkout-Info hinzufügen
            info_file = dest_path / "checkout_info.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Ausgecheckt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Benutzer: {self.username}\n")
                f.write(f"Von: {source_path}\n")
                f.write(f"Nach: {dest_path}\n")
                f.write(f"Maschine: {machine}\n")
                f.write(f"Archiv-Datum: {self.get_folder_date(source_path)}\n")
            
            self.status_label.config(text=f"Projekt '{project['name']}' auf Maschine {machine} erfolgreich ausgecheckt!", 
                                   foreground="green")
            self.refresh_project_list()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht ausgecheckt werden:\n{str(e)}")
            self.status_label.config(text="Fehler beim Auschecken", foreground="red")
        finally:
            self.hide_loading()
    
    def checkin_project(self):
        project = self.get_selected_project_workdir()
        if not project:
            messagebox.showwarning("Warnung", "Bitte ein Projekt im Workdir auswählen!")
            return
        
        self.show_loading("Führe Checkin durch")
        try:
            # Quellpfad basierend auf aktueller Workdir-Maschine
            source_path = self.workdir_path / project['maschine'] / project['name']
            dest_path = self.archiv_base_path / self.current_machine / project['name']
            
            # Datumsvergleich durchführen
            backup_path = None
            if dest_path.exists():
                source_time = self.get_folder_timestamp(source_path)
                dest_time = self.get_folder_timestamp(dest_path)
                
                source_date = datetime.datetime.fromtimestamp(source_time).strftime('%d.%m.%Y %H:%M')
                dest_date = datetime.datetime.fromtimestamp(dest_time).strftime('%d.%m.%Y %H:%M')
                
                if dest_time > source_time:
                    # Archiv ist neuer als Workdir
                    result = messagebox.askyesno("⚠️ WARNUNG - Datenverlust möglich!", 
                                               f"Das Projekt '{project['name']}' im Archiv ist NEUER als im Workdir:\n\n"
                                               f"💻 Workdir ({project['maschine']}): {source_date}\n"
                                               f"📁 Archiv ({self.current_machine}): {dest_date} (neuer)\n\n"
                                               f"Beim Einchecken würden Sie NEUERE Daten im Archiv überschreiben!\n\n"
                                               f"Empfehlung: Checken Sie erst die neuere Archiv-Version aus.\n\n"
                                               f"Trotzdem fortfahren und neuere Archiv-Daten überschreiben?",
                                               icon='warning')
                    if not result:
                        self.status_label.config(text="Checkin abgebrochen - Neuere Archiv-Daten geschützt", 
                                               foreground="orange")
                        return
                elif dest_time == source_time:
                    # Beide Versionen sind gleich alt
                    result = messagebox.askyesno("Information", 
                                               f"Beide Versionen von '{project['name']}' haben dasselbe Datum:\n\n"
                                               f"💻 Workdir ({project['maschine']}): {source_date}\n"
                                               f"📁 Archiv ({self.current_machine}): {dest_date}\n\n"
                                               f"Trotzdem einchecken?")
                    if not result:
                        return
                else:
                    # Workdir ist neuer - normaler Fall
                    result = messagebox.askyesno("Bestätigung", 
                                               f"Projekt '{project['name']}' von Maschine {project['maschine']} in Archiv ({self.current_machine}) einchecken?\n\n"
                                               f"💻 Workdir ({project['maschine']}): {source_date} (neuer)\n"
                                               f"📁 Archiv ({self.current_machine}): {dest_date}\n\n"
                                               f"Das Archiv wird mit der neueren Workdir-Version überschrieben.\n"
                                               f"Ein Backup der alten Version wird erstellt.")
                    if not result:
                        return
                
                # Backup erstellen
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_folder = self.archiv_base_path / self.current_machine / "Backups"
                backup_folder.mkdir(exist_ok=True)  # Backup-Ordner erstellen falls nicht vorhanden
                backup_path = backup_folder / f"{project['name']}_backup_{timestamp}"
            
            # Archiv-Pfad erstellen falls nicht vorhanden
            (self.archiv_base_path / self.current_machine).mkdir(parents=True, exist_ok=True)
            
            # Backup erstellen
            if backup_path:
                shutil.move(str(dest_path), str(backup_path))
            
            # Projekt ins Archiv kopieren
            shutil.copytree(source_path, dest_path)
            
            # Checkin-Info hinzufügen
            info_file = dest_path / "checkin_info.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Eingecheckt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Benutzer: {self.username}\n")
                f.write(f"Von: {source_path}\n")
                f.write(f"Nach: {dest_path}\n")
                f.write(f"Maschine: {project['maschine']}\n")
                f.write(f"Ziel-Archiv: {self.current_machine}\n")
                f.write(f"Workdir-Datum: {self.get_folder_date(source_path)}\n")
                if backup_path:
                    f.write(f"Backup erstellt: {backup_path}\n")
                    f.write(f"Backup-Datum: {self.get_folder_date(backup_path)}\n")
            
            # Checkout-Info aus Workdir-Version entfernen
            checkout_info = source_path / "checkout_info.txt"
            if checkout_info.exists():
                checkout_info.unlink()
            
            self.status_label.config(text=f"Projekt '{project['name']}' von Maschine {project['maschine']} in Archiv ({self.current_machine}) eingecheckt!", 
                                   foreground="green")
            self.refresh_project_list()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht eingecheckt werden:\n{str(e)}")
            self.status_label.config(text="Fehler beim Einchecken", foreground="red")
        finally:
            self.hide_loading()
    
    def open_project_folder(self, location):
        if location == "archiv":
            project = self.get_selected_project_archiv()
            if not project:
                messagebox.showwarning("Warnung", "Bitte ein Projekt im Archiv auswählen!")
                return
            project_path = self.archiv_base_path / project['maschine'] / project['name']
        else:  # workdir
            project = self.get_selected_project_workdir()
            if not project:
                messagebox.showwarning("Warnung", "Bitte ein Projekt im Workdir auswählen!")
                return
            
            # Pfad basierend auf aktueller Maschine
            project_path = self.workdir_path / project['maschine'] / project['name']
        
        try:
            # Windows Explorer öffnen
            os.startfile(str(project_path))
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden:\n{str(e)}")

def main():
    root = tk.Tk()
    app = CAMManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()