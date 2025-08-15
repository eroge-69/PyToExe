import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import winreg
import logging
import threading
import queue
import ctypes
import sys
import os
import concurrent.futures
from datetime import datetime
import subprocess

# Funktion, um zu überprüfen, ob das Skript mit Administratorrechten ausgeführt wird
def is_admin():
    """
    Überprüft, ob das Skript mit Administratorrechten ausgeführt wird.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Das Skript mit Administratorrechten neu starten, falls nötig
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

class RegistryCleaner:
    def __init__(self, root):
        self.root = root
        self.version = "1.2"  # Neue Versionnummer
        self.root.title(f"Registry Cleaner Pro v{self.version}") # Angepasster Fenstertitel
        self.root.geometry("1100x850") # Angepasste Höhe, um alle Elemente anzuzeigen
        
        # Variablen
        self.search_active = False
        self.should_stop = False
        self.search_queue = queue.Queue()
        self.backup_path = ""
        self.selected_items = {}  
        self.dry_run_var = tk.BooleanVar(value=False) # Variable für den Dry-Run-Modus
        
        # UI, Logging und Event-Handler einrichten
        self.setup_ui()
        self.setup_logging()
        self.setup_event_handling()

    def setup_ui(self):
        # --- Neuer Code für das Menü startet hier ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # "Hilfe" Menü erstellen
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)

        # "Über uns..." und "Copyright" Menüpunkte hinzufügen
        help_menu.add_command(label="Über uns...", command=self.show_about_dialog)
        help_menu.add_command(label="Copyright", command=self.show_copyright_dialog)
        # --- Neuer Code für das Menü endet hier ---

        # Linke Spalte - Steuerelemente
        left_frame = ttk.Frame(self.root, width=300, padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Suchbereich
        search_frame = ttk.LabelFrame(left_frame, text=" Sucheinstellungen ", padding="10")
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Registry-Hives:").pack(anchor=tk.W)
        
        self.hive_vars = {
            "HKEY_CLASSES_ROOT": tk.BooleanVar(value=True),
            "HKEY_CURRENT_USER": tk.BooleanVar(value=True),
            "HKEY_LOCAL_MACHINE": tk.BooleanVar(value=True),
            "HKEY_USERS": tk.BooleanVar(),
            "HKEY_CURRENT_CONFIG": tk.BooleanVar()
        }
        
        for hive, var in self.hive_vars.items():
            cb = ttk.Checkbutton(search_frame, text=hive, variable=var)
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(search_frame, text="Suchbegriff:").pack(anchor=tk.W, pady=(10,0))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill=tk.X, pady=5)
        # Event-Binding für die Enter-Taste hinzufügen
        self.search_entry.bind('<Return>', lambda event: self.start_search_thread())
        
        # Button-Bereich
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.search_btn = ttk.Button(btn_frame, text="Suchen starten", command=self.start_search_thread)
        self.search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stopp", command=self.stop_search, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Backup-Bereich
        backup_frame = ttk.LabelFrame(left_frame, text=" Backup ", padding="10")
        backup_frame.pack(fill=tk.X, pady=10)
        
        self.full_backup_btn = ttk.Button(backup_frame, text="Vollständiges Backup erstellen", command=self.create_full_registry_backup)
        self.full_backup_btn.pack(fill=tk.X, pady=5)

        self.backup_btn = ttk.Button(backup_frame, text="Ausgewählte Einträge sichern", command=self.create_backup_selected)
        self.backup_btn.pack(fill=tk.X, pady=5)
        
        self.restore_btn = ttk.Button(backup_frame, text="Backup wiederherstellen", command=self.restore_backup)
        self.restore_btn.pack(fill=tk.X, pady=5)
        
        # Auswahlbereich
        select_frame = ttk.LabelFrame(left_frame, text=" Auswahl ", padding="10")
        select_frame.pack(fill=tk.X, pady=10)
        
        dry_run_cb = ttk.Checkbutton(select_frame, text="Dry-Run-Modus (nur Simulation)", variable=self.dry_run_var)
        dry_run_cb.pack(anchor=tk.W, pady=5)
        
        self.select_all_btn = ttk.Button(select_frame, text="Alle auswählen", command=self.select_all)
        self.select_all_btn.pack(fill=tk.X, pady=5)
        
        self.delete_btn = ttk.Button(select_frame, text="Ausgewählte löschen", 
                                     command=self.delete_selected, style='Danger.TButton')
        self.delete_btn.pack(fill=tk.X, pady=10)
        
        # Statusbereich
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Bereit", foreground="gray")
        self.status_label.pack(fill=tk.X)
        
        # Hinzufügen des "Beenden" Buttons unten links
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.exit_btn = ttk.Button(bottom_frame, text="Beenden", command=self.exit_app)
        self.exit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Rechte Spalte - Ergebnisse
        self.right_frame = ttk.Frame(self.root, padding="15")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Treeview mit Checkbox-Spalte
        self.tree = ttk.Treeview(self.right_frame, columns=("Selected", "Status"), selectmode="none")
        self.tree.heading("Selected", text="", anchor=tk.CENTER)
        self.tree.heading("#0", text="Registry-Schlüssel", anchor=tk.W)
        self.tree.heading("Status", text="Status", anchor=tk.W)
        
        self.tree.column("Selected", width=30, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("#0", width=470, stretch=tk.YES)
        self.tree.column("Status", width=150, stretch=tk.NO)
        
        # Tags für visuelle Hervorhebung
        self.tree.tag_configure('selected', background='lightblue')

        # Scrollbars
        vsb = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.right_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Log-Bereich
        self.log_frame = ttk.Frame(self.right_frame)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, state='disabled', height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Layout konfigurieren
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Styling
        style = ttk.Style()
        style.configure('Danger.TButton', foreground='red')
        style.map('Treeview', background=[('selected', 'lightblue')])

        # Event-Binding für die Auswahl der gesamten Zeile
        self.tree.bind('<ButtonRelease-1>', self.on_tree_click)

    # --- Die neuen Menüfunktionen ---
    def show_about_dialog(self):
        """Zeigt ein 'Über uns' Dialogfeld an."""
        messagebox.showinfo(
            "Über Registry Cleaner Pro",
            f"Registry Cleaner Pro\n"
            f"Version: {self.version}\n"
            f"Erstellt von: Nikolco Andonov"
        )

    def show_copyright_dialog(self):
        """Zeigt ein 'Copyright' Dialogfeld an."""
        messagebox.showinfo(
            "Copyright",
            f"© 2024 Nikolco Andonov. Alle Rechte vorbehalten.\n\n"
            f"Dieses Programm ist urheberrechtlich geschützt."
        )

    # --- Rest des Codes bleibt unverändert ---
    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell" or region == "tree":
            if item_id in self.selected_items:
                current_state = self.selected_items[item_id]
                new_state = not current_state
                self.selected_items[item_id] = new_state
                
                self.tree.set(item_id, "Selected", "☑" if new_state else "☐")
                
                if new_state:
                    self.tree.tag_add("selected", item_id)
                else:
                    self.tree.tag_remove("selected", item_id)

    def _run_backup_thread(self, paths, status_message, backup_folder=None):
        """Hilfsfunktion, die das Backup im Hintergrund ausführt und den UI-Status aktualisiert."""
        self.search_active = True
        self.search_queue.put(("status", status_message))
        self.search_queue.put(("progress", 0))

        success_count = 0
        fail_count = 0
        total_items = len(paths)

        for i, full_path in enumerate(paths):
            if self.should_stop:
                break
            
            try:
                # Sicherer Dateiname erstellen
                filename = full_path.replace("\\", "_").replace(":", "")
                backup_file_path = os.path.join(backup_folder, f"{filename}.reg")
                
                self.search_queue.put(("status", f"Sichere: {full_path}..."))
                
                # subprocess.run wird verwendet, um das Konsolenfenster zu unterdrücken
                subprocess.run(
                    f'reg export "{full_path}" "{backup_file_path}" /y',
                    shell=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.search_queue.put(("log", ("info", f"Backup von '{full_path}' erfolgreich erstellt.")))
                success_count += 1
            except Exception as e:
                self.search_queue.put(("log", ("error", f"Fehler beim Backup von '{full_path}': {str(e)}")))
                fail_count += 1
            
            progress_value = (i + 1) / total_items * 100
            self.search_queue.put(("progress", progress_value))
            
        self.search_queue.put(("end_search", None))
        self.search_queue.put(("status", "Bereit"))
        
        if success_count > 0:
            self.search_queue.put(("messagebox", ("Erfolg", f"Backup erfolgreich abgeschlossen.\n"
                                                           f"Gesichert: {success_count} Einträge\n"
                                                           f"Fehler: {fail_count}")))
        else:
            self.search_queue.put(("messagebox", ("Fehler", "Backup ist fehlgeschlagen.")))

    def create_full_registry_backup(self):
        """Erstellt ein vollständiges Backup der wichtigsten Registry-Hives."""
        backup_dir = filedialog.askdirectory(title="Speicherort für vollständiges Backup auswählen")
        if not backup_dir:
            return

        hives_to_backup = [
            "HKEY_CLASSES_ROOT",
            "HKEY_CURRENT_USER",
            "HKEY_LOCAL_MACHINE",
            "HKEY_USERS",
            "HKEY_CURRENT_CONFIG"
        ]
        
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_folder = os.path.join(backup_dir, f"backup_full_{backup_timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        self.logger.info("Starte vollständiges Backup der Registry...")
        
        threading.Thread(
            target=self._run_backup_thread,
            args=(hives_to_backup, "Erstelle vollständiges Backup...", backup_folder),
            daemon=True
        ).start()

    def create_backup_selected(self):
        """Erstellt ein vollständiges Backup der ausgewählten Einträge."""
        selected_item_ids = [
            item_id for item_id, is_selected in self.selected_items.items() if is_selected
        ]
        
        if not selected_item_ids:
            messagebox.showwarning("Warnung", "Keine Einträge für Backup ausgewählt")
            return
        
        backup_dir = filedialog.askdirectory(title="Backup-Speicherort auswählen")
        if not backup_dir:
            return
        
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_folder = os.path.join(backup_dir, f"backup_selected_{backup_timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        paths_to_backup = [self.tree.item(item_id, "text") for item_id in selected_item_ids]
        
        self.logger.info("Starte Backup der ausgewählten Einträge...")
        
        threading.Thread(
            target=self._run_backup_thread,
            args=(paths_to_backup, "Sichere ausgewählte Einträge...", backup_folder),
            daemon=True
        ).start()

    def restore_backup(self):
        file_path = filedialog.askopenfilename(
            title="Backup-Datei auswählen",
            filetypes=[("Registry-Dateien", "*.reg")]
        )
        if not file_path:
            return
        
        confirm = messagebox.askyesno(
            "Bestätigen",
            f"Möchtest du das Backup wirklich wiederherstellen?\n"
            f"Datei: {file_path}\n"
            f"WARNUNG: Dies kann dein System beschädigen!"
        )
        if not confirm:
            return

        try:
            self.update_status("Wiederherstellung läuft...")
            # subprocess.run wird verwendet, um das Konsolenfenster zu unterdrücken
            subprocess.run(
                f'reg import "{file_path}"',
                shell=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.logger.info(f"Backup erfolgreich wiederhergestellt: {file_path}")
            messagebox.showinfo("Erfolg", "Backup erfolgreich wiederhergestellt.")
        except Exception as e:
            self.logger.error(f"Fehler bei der Wiederherstellung: {str(e)}")
            messagebox.showerror("Fehler", f"Wiederherstellung fehlgeschlagen:\n{str(e)}")
        finally:
            self.update_status("Bereit")

    def exit_app(self):
        self.root.destroy()
    
    def select_all(self):
        """Markiert alle Einträge im Treeview mit der Checkbox."""
        for item_id in self.tree.get_children():
            self.selected_items[item_id] = True
            self.tree.set(item_id, "Selected", "☑")
            self.tree.tag_add("selected", item_id)

    def setup_logging(self):
        self.logger = logging.getLogger("RegistryCleanerPro")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(self.LogStream(self.log_text))
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def setup_event_handling(self):
        self.root.after(100, self.process_queue)

    def start_search_thread(self):
        if self.search_active:
            return
            
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Warnung", "Bitte Suchbegriff eingeben")
            return
            
        self.tree.delete(*self.tree.get_children())
        self.selected_items = {}
        self.logger.info(f"Starte beschleunigte Suche nach: {search_term}")
        self.update_status("Parallele Suche läuft...")
        
        self.search_active = True
        self.should_stop = False
        self.search_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress["value"] = 0
        
        threading.Thread(
            target=self.parallel_search,
            args=(search_term,),
            daemon=True
        ).start()

    def parallel_search(self, search_term):
        hives_map = {
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }
        
        selected_hives = [hives_map[hive] for hive, var in self.hive_vars.items() if var.get()]
        search_lower = search_term.lower()
        total_hives = len(selected_hives)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i, hive in enumerate(selected_hives):
                if self.should_stop:
                    break
                    
                hive_name = next(key for key, value in hives_map.items() if value == hive)
                futures.append(
                    executor.submit(
                        self._search_registry_hive,
                        hive, hive_name, "", search_lower
                    )
                )
                self.search_queue.put(("progress", (i + 1) / total_hives * 100))
                self.search_queue.put(("status", f"Durchsuche {hive_name}..."))
                
            concurrent.futures.wait(futures)
        
        if self.should_stop:
            self.logger.info("Suche abgebrochen")
            self.search_queue.put(("status", "Bereit (Abgebrochen)"))
        else:
            self.logger.info("Parallele Suche abgeschlossen")
            self.search_queue.put(("status", "Bereit"))
            self.search_queue.put(("progress", 100))
            
        self.search_queue.put(("end_search", None))

    def _search_registry_hive(self, hive, hive_name, path, search_term, depth=0):
        if depth > 5:
            return
            
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                subkey_count = winreg.QueryInfoKey(key)[0]
                
                for i in range(subkey_count):
                    if self.should_stop:
                        return
                        
                    subkey_name = winreg.EnumKey(key, i)
                    full_path = f"{hive_name}\\{path}\\{subkey_name}" if path else f"{hive_name}\\{subkey_name}"
                    
                    if search_term in subkey_name.lower():
                        self.search_queue.put(("result", (full_path, "Gefunden")))
                        
                    try:
                        new_path = f"{path}\\{subkey_name}" if path else subkey_name
                        self._search_registry_hive(hive, hive_name, new_path, search_term, depth+1)
                    except WindowsError:
                        self.search_queue.put(("log", ("warning", f"Zugriff verweigert: {full_path}")))
                        
        except WindowsError:
            self.search_queue.put(("log", ("warning", f"Zugriff verweigert: {hive_name}\\{path}")))

    def process_queue(self):
        try:
            while True:
                task = self.search_queue.get_nowait()
                if task[0] == "result":
                    full_path, status = task[1]
                    item_id = self.tree.insert("", tk.END, text=full_path, values=("☐", status))
                    self.selected_items[item_id] = False
                elif task[0] == "status":
                    self.status_label.config(text=task[1])
                elif task[0] == "log":
                    level, message = task[1]
                    getattr(self.logger, level)(message)
                elif task[0] == "progress":
                    self.progress["value"] = task[1]
                elif task[0] == "end_search":
                    self.search_active = False
                    self.search_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                elif task[0] == "messagebox":
                    title, message = task[1]
                    messagebox.showinfo(title, message)
        except queue.Empty:
            pass
            
        self.root.after(100, self.process_queue)

    def delete_selected(self):
        items_to_delete = [item_id for item_id, is_selected in self.selected_items.items() if is_selected]

        if not items_to_delete:
            messagebox.showwarning("Warnung", "Keine Einträge ausgewählt")
            return
            
        is_dry_run = self.dry_run_var.get()
        if is_dry_run:
            message = f"Dry-Run-Modus: Es würden {len(items_to_delete)} Einträge gelöscht."
            self.logger.info(message)
            messagebox.showinfo("Dry-Run-Modus", message)
            
            for item_id in items_to_delete:
                full_path = self.tree.item(item_id, "text")
                self.logger.info(f"Dry-Run: '{full_path}' würde gelöscht werden.")
                self.tree.set(item_id, "Status", "Dry-Run: würde gelöscht")
            return
        
        confirm = messagebox.askyesno(
            "Bestätigen", 
            f"Sollen {len(items_to_delete)} Einträge gelöscht werden?\n"
            "WARNUNG: Dies kann Ihr System beschädigen!"
        )
        if not confirm:
            return
            
        success_count = 0
        fail_count = 0
        
        for item_id in items_to_delete:
            full_path = self.tree.item(item_id, "text")
            try:
                hive_name, path = full_path.split("\\", 1)
                hive = getattr(winreg, hive_name)
                
                self.delete_registry_key(hive, path)
                
                self.tree.set(item_id, "Status", "Gelöscht ✓")
                del self.selected_items[item_id]
                self.tree.tag_remove("selected", item_id)
                success_count += 1
                self.logger.info(f"Erfolgreich gelöscht: {full_path}")
            except Exception as e:
                fail_count += 1
                self.logger.error(f"Fehler beim Löschen von {full_path}: {e}")
                self.tree.set(item_id, "Status", f"Fehler: {str(e)}")
        
        messagebox.showinfo(
            "Ergebnis",
            f"Löschung abgeschlossen:\n"
            f"Erfolgreich: {success_count}\n"
            f"Fehlgeschlagen: {fail_count}"
        )

    def delete_registry_key(self, hive, sub_key):
        try:
            with winreg.OpenKey(hive, sub_key, 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY) as key:
                info = winreg.QueryInfoKey(key)
                for _ in range(info[0]):
                    subkey_name = winreg.EnumKey(key, 0)
                    self.delete_registry_key(hive, f"{sub_key}\\{subkey_name}")
        except WindowsError:
            pass
        
        try:
            winreg.DeleteKey(hive, sub_key)
        except WindowsError as e:
            raise Exception(f"Löschen fehlgeschlagen: {e}")

    def stop_search(self):
        self.should_stop = True
        self.logger.info("Suche wird gestoppt...")
        self.update_status("Stoppe Suche...")

    def update_status(self, message):
        self.search_queue.put(("status", message))

    class LogStream:
        def __init__(self, text_widget):
            self.text_widget = text_widget
        
        def write(self, message):
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, message)
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
        
        def flush(self):
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistryCleaner(root)
    root.mainloop()
