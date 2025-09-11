import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
import json
import csv
import shutil
from tkinter import simpledialog
from PIL import Image, ImageTk
import calendar

class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magazyn Dowodów Rzeczowych PSG w Gdyni")
        self.root.geometry("1200x800")
        
        self.program_dir = os.path.dirname(os.path.abspath(__file__))
        self.evidence_dir = os.path.join(self.program_dir, "Dowody rzeczowe")
        self.backup_dir = os.path.join(self.program_dir, "backup")
        os.makedirs(self.evidence_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.config_path = os.path.join(self.program_dir, 'config.json')
        self.default_db_path = os.path.join(self.program_dir, 'magazyn.db')
        
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('SmallFilter.TButton', font=('Arial', 9), padding=3)
        self.style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=8)
 
        self.db_path = None
        self.conn = None
        self.c = None
 
        # Inicjalizacja zmiennych do sortowania
        self.sort_column = None
        self.sort_direction = "asc"
        self.treeview_extra_data = {}
 
        self.load_config_and_connect_db()
        self.setup_ui()
        self.show_preview_view()

    def load_config_and_connect_db(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.db_path = config_data.get('db_path', self.default_db_path)
                    # Wczytaj też ścieżkę do dowodów jeśli istnieje
                    self.evidence_dir = config_data.get('evidence_dir', self.evidence_dir)
            except (json.JSONDecodeError, FileNotFoundError):
                # Jeśli plik config jest uszkodzony, użyj domyślnych wartości
                self.db_path = self.default_db_path
        else:
            self.db_path = self.default_db_path
            self.save_config()  # Utwórz domyślny config
            
        self.connect_db()

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.c = self.conn.cursor()
            self.create_tables()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Błąd połączenia z bazą", f"Nie można połączyć się z bazą danych w ścieżce:\n{self.db_path}\n\n"
                                                           f"Sprawdź, czy plik bazy danych nie jest używany przez inną aplikację i spróbuj ponownie.\n"
                                                           f"W przypadku braku pliku, zostanie on utworzony w domyślnej lokalizacji.")
            self.db_path = self.default_db_path
            self.connect_db()

    def save_config(self):
        config_data = {
            'db_path': self.db_path,
            'evidence_dir': self.evidence_dir  # Dodajemy też ścieżkę do dowodów
        }
        try:
            # Upewnij się, że folder config istnieje
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Błąd zapisu konfiguracji", f"Nie udało się zapisać pliku konfiguracyjnego:\n{str(e)}")

    def create_tables(self):
        # Tabela produktów
        self.c.execute('''CREATE TABLE IF NOT EXISTS produkty (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nazwa TEXT NOT NULL,
                        kod TEXT UNIQUE,
                        ilosc INTEGER DEFAULT 0,
                        jednostka TEXT DEFAULT 'szt.',
                        cena REAL DEFAULT 0.0,
                        data_dodania TEXT,
                        lokalizacja TEXT DEFAULT 'magazyn',
                        min_ilosc INTEGER DEFAULT 5
                        )''')
        
        # Tabela wykazów
        self.c.execute('''CREATE TABLE IF NOT EXISTS wykazy (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numer_rsd TEXT NOT NULL,
                        numer_wykazu TEXT NOT NULL UNIQUE,
                        data_wykazu TEXT NOT NULL,
                        data_utworzenia TEXT NOT NULL,
                        sciezka_pliku TEXT,
                        w_magazynie INTEGER DEFAULT 0,
                        wydano INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'W trakcie',
                        uwagi TEXT,
                        UNIQUE(numer_rsd, numer_wykazu)
                        )''')
        
        # Tabela pozycji w wykazach
        self.c.execute('''CREATE TABLE IF NOT EXISTS wykazy_pozycje (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_wykazu INTEGER,
                        pozycja_nr INTEGER,
                        nazwa TEXT NOT NULL,
                        ilosc INTEGER DEFAULT 1,
                        jednostka TEXT DEFAULT 'szt.',
                        status TEXT DEFAULT 'Magazyn',
                        uwagi TEXT,
                        FOREIGN KEY (id_wykazu) REFERENCES wykazy(id) ON DELETE CASCADE,
                        UNIQUE(id_wykazu, pozycja_nr)
                        )''')
        
        # Tabela dokumenty (kwity)
        self.c.execute('''CREATE TABLE IF NOT EXISTS dokumenty (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_wykazu INTEGER,
                        id_pozycji TEXT,
                        nazwa_pliku TEXT,
                        sciezka TEXT,
                        opis TEXT,
                        data_dodania TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_wykazu) REFERENCES wykazy(id) ON DELETE CASCADE
                        )''')
        
        # Nowa tabela historia_zmian z poprawną strukturą
        self.c.execute('''CREATE TABLE IF NOT EXISTS historia_zmian (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        typ_operacji TEXT NOT NULL,
                        tabela TEXT NOT NULL,
                        numer_rsd TEXT,
                        numer_wykazu TEXT,
                        szczegoly TEXT NOT NULL,
                        data_zmiany TEXT DEFAULT CURRENT_TIMESTAMP
                        )''')
        
        self.conn.commit()
        
        # Migracja - dodanie brakujących kolumn, jeśli baza danych jest starsza
        self.c.execute("PRAGMA table_info(wykazy)")
        columns = [col[1] for col in self.c.fetchall()]
        if 'status' not in columns:
            self.c.execute("ALTER TABLE wykazy ADD COLUMN status TEXT DEFAULT 'W trakcie'")
 
        self.c.execute("PRAGMA table_info(wykazy_pozycje)")
        columns = [col[1] for col in self.c.fetchall()]
        if 'status' not in columns:
            self.c.execute("ALTER TABLE wykazy_pozycje ADD COLUMN status TEXT DEFAULT 'Magazyn'")
 
        self.conn.commit()

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        menu_frame = ttk.Frame(main_frame, relief="raised", padding="5")
        menu_frame.grid(row=0, column=0, sticky="ew")

        # Główne przyciski menu
        ttk.Button(menu_frame, text="Podgląd", command=self.show_preview_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Nowy wykaz", command=self.create_new_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Inwentaryzacja", command=self.inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Załączone kwity", command=self.show_docs_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Historia zmian", command=self.change_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Ustawienia", command=self.settings).pack(side=tk.LEFT, padx=5)
        
        # Przycisk informacyjny "i" po prawej stronie - ZMIENIONE
        info_button = tk.Button(menu_frame, text="ⓘ", font=('Arial', 12, 'bold'), 
                               command=self.show_info, relief=tk.FLAT, bd=1, width=2, height=1)
        info_button.pack(side=tk.RIGHT, padx=5)
        
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def sort_treeview(self, column):
        """Sortuje treeview po wybranej kolumnie"""
        # Jeśli kliknięto tę samą kolumnę, zmień kierunek sortowania
        if self.sort_column == column:
            self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"
        else:
            self.sort_column = column
            self.sort_direction = "asc"
        
        # Aktualizuj nagłówki z strzałkami sortowania
        self.update_sort_headers()
        
        # Załaduj dane z sortowaniem
        self.load_lists()

    def update_sort_headers(self):
        """Aktualizuje nagłówki kolumn ze strzałkami sortowania"""
        for col in self.list_treeview["columns"]:
            current_text = self.list_treeview.heading(col)["text"]
            # Usuń istniejące strzałki sortowania
            clean_text = current_text.replace(" ▲", "").replace(" ▼", "")
            
            if col == self.sort_column:
                arrow = " ▲" if self.sort_direction == "asc" else " ▼"
                self.list_treeview.heading(col, text=clean_text + arrow)
            else:
                self.list_treeview.heading(col, text=clean_text)

    def get_sql_order_by(self, column_name):
        """Mapuje nazwę kolumny w treeview na odpowiednią kolumnę w SQL"""
        mapping = {
            "ID": "w.id",
            "Numer RSD": "w.numer_rsd",
            "Numer wykazu": "w.numer_wykazu",
            "Data wykazu": "w.data_wykazu",
            "Status wykazu": "w.status",
            "Pozycja": "wp.pozycja_nr",
            "Przedmiot": "wp.nazwa",
            "Ilość": "wp.ilosc",
            "Status przedmiotu": "wp.status",
            "Uwagi": "wp.uwagi",
            "Kwity": "(SELECT COUNT(*) FROM dokumenty d WHERE d.id_wykazu = w.id AND d.id_pozycji = wp.id)"
        }
        return mapping.get(column_name)

    def show_preview_view(self):
        self.clear_content_frame()
        
        main_frame = ttk.Frame(self.content_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Panel filtrów
        filter_frame = ttk.LabelFrame(main_frame, text="Filtry", padding="5")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=5)

        ttk.Label(filter_frame, text="Numer RSD:").pack(side=tk.LEFT, padx=5)
        self.rsd_filter_entry = ttk.Entry(filter_frame, width=12)
        self.rsd_filter_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Numer Wykazu:").pack(side=tk.LEFT, padx=5)
        self.list_num_filter_entry = ttk.Entry(filter_frame, width=12)
        self.list_num_filter_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Status Wykazu:").pack(side=tk.LEFT, padx=5)
        self.list_status_filter = ttk.Combobox(filter_frame, values=["Wszystkie", "Na stanie", "Rozliczony"], width=12)
        self.list_status_filter.set("Wszystkie")
        self.list_status_filter.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Status Przedmiotu:").pack(side=tk.LEFT, padx=5)
        self.item_status_filter = ttk.Combobox(filter_frame, values=["Wszystkie", "Na stanie", "Rozliczono"], width=12)
        self.item_status_filter.set("Wszystkie")
        self.item_status_filter.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Przedmiot:").pack(side=tk.LEFT, padx=5)
        self.item_name_filter_entry = ttk.Entry(filter_frame, width=15)
        self.item_name_filter_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Filtruj", command=self.load_lists).pack(side=tk.LEFT, padx=5)

        # Panel przycisków akcji - ZMIENIONE: używamy ttk.Button z minimalnym paddingiem
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=1, column=0, sticky="ew", pady=5)

        # Definiuj styl dla przycisków akcji (minimalny padding)
        self.style.configure('Compact.TButton', 
                            font=('Arial', 9),
                            padding=(2, 1),  # Minimalne paddingi
                            anchor='center')

        # Lista przycisków z ujednoliconą szerokością
        action_buttons = [
            ("Status wykazu", self.change_list_status),
            ("Status przedm.", self.change_item_status),
            ("Edytuj", self.edit_position),
            ("Usuń poz.", self.delete_position),
            ("Usuń wykaz", self.delete_list),
            ("Odśwież", self.load_lists),
            ("Import", self.import_single_list),
            ("Eksport", self.export_single_list)
        ]

        # Utwórz przyciski z ujednoliconą szerokością przez ramkę wewnętrzną
        for text, command in action_buttons:
            # Ramka wewnętrzna do kontrolowania szerokości
            btn_frame = ttk.Frame(action_frame, width=100, height=22)
            btn_frame.pack_propagate(False)  # Zapobiega zmianie rozmiaru przez dzieci
            btn_frame.pack(side=tk.LEFT, padx=2)
            
            btn = ttk.Button(
                btn_frame, 
                text=text, 
                command=command,
                style='Compact.TButton'
            )
            btn.pack(fill=tk.BOTH, expand=True)

        # Tabela z danymi - zaktualizowane kolumny
        columns = [
            ("ID", 40),
            ("Numer RSD", 100),
            ("Numer wykazu", 100),
            ("Data wykazu", 100),
            ("Status wykazu", 100),
            ("Pozycja", 70),
            ("Przedmiot", 250),
            ("Ilość", 60),
            ("Status przedmiotu", 120),
            ("Uwagi", 200),
            ("Kwity", 80)  # Nowa kolumna dla załączników
        ]
        
        self.list_treeview = ttk.Treeview(main_frame, columns=[col[0] for col in columns], 
                                        show="headings", height=25)
        
        # Konfiguracja kolumn z wyśrodkowaniem
        for col_name, width in columns:
            self.list_treeview.heading(col_name, text=col_name, 
                                     command=lambda c=col_name: self.sort_treeview(c))
            # Wyśrodkuj wszystkie kolumny oprócz "Przedmiot" i "Uwagi"
            anchor = tk.CENTER
            if col_name in ("Przedmiot", "Uwagi"):
                anchor = tk.W
            self.list_treeview.column(col_name, width=width, anchor=anchor)
            
        self.list_treeview.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.list_treeview.bind("<Double-1>", self.view_list_details)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.list_treeview.yview)
        self.list_treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=1, sticky="ns")

        # Konfiguracja kolorów
        self.list_treeview.tag_configure('rozliczony', background='#ffdddd')
        self.list_treeview.tag_configure('na_stanie', background='#ddffdd')

        self.load_lists()
        # Aktualizuj nagłówki po załadowaniu danych
        self.update_sort_headers()
    
    def load_lists(self):
        for item in self.list_treeview.get_children():
            self.list_treeview.delete(item)
        
        # Słownik do przechowywania dodatkowych danych
        self.treeview_extra_data = {}
            
        query = '''SELECT 
                    w.id,
                    w.numer_rsd,
                    w.numer_wykazu,
                    CASE 
                        WHEN w.data_wykazu IS NULL THEN ''
                        WHEN length(w.data_wykazu) = 10 AND 
                             substr(w.data_wykazu, 5, 1) = '-' AND 
                             substr(w.data_wykazu, 8, 1) = '-' THEN strftime('%d.%m.%Y', w.data_wykazu)
                        WHEN length(w.data_wykazu) = 10 AND 
                             substr(w.data_wykazu, 3, 1) = '.' AND 
                             substr(w.data_wykazu, 6, 1) = '.' THEN w.data_wykazu
                        ELSE ''
                    END as formatted_date,
                    CASE WHEN w.status = 'Rozliczony' THEN 'Rozliczony' ELSE 'Na stanie' END as status_wykazu,
                    wp.pozycja_nr || '/' || (SELECT COUNT(*) FROM wykazy_pozycje WHERE id_wykazu = w.id) as pozycja,
                    wp.nazwa,
                    wp.ilosc,
                    CASE WHEN wp.status = 'Rozliczono' THEN 'Rozliczono' ELSE 'Na stanie' END as status_przedmiotu,
                    COALESCE(wp.uwagi, '') as uwagi,
                    wp.id as id_pozycji,
                    w.id as id_wykazu
                  FROM wykazy w
                  JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu'''
        
        params = []
        where_clauses = []
        
        rsd_filter = self.rsd_filter_entry.get()
        list_num_filter = self.list_num_filter_entry.get()
        list_status_filter = self.list_status_filter.get()
        item_status_filter = self.item_status_filter.get()
        item_name_filter = self.item_name_filter_entry.get()
        
        if rsd_filter:
            where_clauses.append("w.numer_rsd LIKE ?")
            params.append(f"%{rsd_filter}%")
        
        if list_num_filter:
            where_clauses.append("w.numer_wykazu LIKE ?")
            params.append(f"%{list_num_filter}%")
        
        if list_status_filter != "Wszystkie":
            where_clauses.append("w.status = ?")
            status_value = "Rozliczony" if list_status_filter == "Rozliczony" else "Na stanie"
            params.append(status_value)
        
        if item_status_filter != "Wszystkie":
            where_clauses.append("wp.status = ?")
            item_status_value = "Rozliczono" if item_status_filter == "Rozliczono" else "Na stanie"
            params.append(item_status_value)
        
        if item_name_filter:
            where_clauses.append("wp.nazwa LIKE ?")
            params.append(f"%{item_name_filter}%")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Dodaj sortowanie jeśli wybrano kolumnę
        if self.sort_column:
            order_by = self.get_sql_order_by(self.sort_column)
            if order_by:
                query += f" ORDER BY {order_by}"
                if self.sort_direction == "desc":
                    query += " DESC"
            else:
                query += " ORDER BY w.data_wykazu DESC, w.numer_rsd, wp.pozycja_nr"
        else:
            query += " ORDER BY w.data_wykazu DESC, w.numer_rsd, wp.pozycja_nr"
        
        self.c.execute(query, params)
        rows = self.c.fetchall()
        
        for i, row in enumerate(rows, 1):
            # Sprawdź ilość załączników dla tej pozycji
            self.c.execute('''SELECT COUNT(*) FROM dokumenty 
                           WHERE id_wykazu = ? AND id_pozycji = ?''',
                         (row[11], row[10]))
            
            doc_count = self.c.fetchone()[0]
            
            # Przygotuj tekst z przyciskami dla załączników
            kwity_text = ""
            if doc_count > 0:
                # Tworzymy tekst z kwadratami odpowiadającymi liczbie załączników
                kwity_text = "■ " * doc_count
            
            values = (
                i,          # ID (numer porządkowy)
                row[1],     # numer_rsd
                row[2],     # numer_wykazu
                row[3],     # data_wykazu (sformatowana)
                row[4],     # status_wykazu
                row[5],     # pozycja
                row[6],     # nazwa przedmiotu
                row[7],     # ilość
                row[8],     # status przedmiotu
                row[9],     # uwagi
                kwity_text  # kwity - załączniki
            )
            
            if row[4] == 'Rozliczony' or row[8] == 'Rozliczono':
                tags = ('rozliczony',)
            else:
                tags = ('na_stanie',)
            
            # Dodajemy item do treeview
            item_id = self.list_treeview.insert("", tk.END, values=values, tags=tags)
            
            # Przechowujemy dodatkowe dane w słowniku
            self.treeview_extra_data[item_id] = {
                'wykaz_id': row[11],
                'pozycja_id': row[10],
                'has_documents': doc_count > 0
            }
        
        # Aktualizuj nagłówki ze strzałkami sortowania
        self.update_sort_headers()
        
        # Dodajemy obsługę kliknięcia w kolumnę "Kwity"
        self.list_treeview.bind('<Button-1>', self.on_treeview_click)

    def on_treeview_click(self, event):
        """Obsługa kliknięcia w treeview, szczególnie w kolumnę 'Kwity'"""
        region = self.list_treeview.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        column = self.list_treeview.identify_column(event.x)
        item = self.list_treeview.identify_row(event.y)
        
        if not item:
            return
            
        # Sprawdź czy kliknięto w kolumnę "Kwity" (kolumna 11, indeksy zaczynają się od 1)
        if column == "#11":  # Kolumna "Kwity"
            # Sprawdź czy item ma dodatkowe dane
            if item in self.treeview_extra_data:
                extra_data = self.treeview_extra_data[item]
                if extra_data['has_documents']:
                    self.show_documents_for_position(extra_data['wykaz_id'], extra_data['pozycja_id'])

    def show_documents_for_position(self, wykaz_id, pozycja_id):
        """Wyświetla dokumenty dla wybranej pozycji"""
        # Pobierz dane wykazu i pozycji
        self.c.execute('''SELECT w.numer_rsd, w.numer_wykazu, wp.pozycja_nr, wp.nazwa
                       FROM wykazy w
                       JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                       WHERE w.id = ? AND wp.id = ?''', (wykaz_id, pozycja_id))
        result = self.c.fetchone()
        
        if not result:
            return
            
        numer_rsd, numer_wykazu, pozycja_nr, nazwa_pozycji = result
        
        # Pobierz dokumenty dla tej pozycji
        self.c.execute('''SELECT nazwa_pliku, sciezka, opis, data_dodania
                       FROM dokumenty 
                       WHERE id_wykazu = ? AND id_pozycji = ?
                       ORDER BY data_dodania''', (wykaz_id, pozycja_id))
        
        documents = self.c.fetchall()
        
        if not documents:
            messagebox.showinfo("Informacja", "Brak dokumentów dla wybranej pozycji.")
            return
        
        # Utwórz okno z listą dokumentów
        docs_window = tk.Toplevel(self.root)
        docs_window.title(f"Dokumenty - {numer_rsd}/{numer_wykazu} poz. {pozycja_nr}")
        docs_window.geometry("600x400")
        
        # Nagłówek
        header_frame = ttk.Frame(docs_window, padding=10)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, 
                 text=f"Pozycja {pozycja_nr}: {nazwa_pozycji}", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Lista dokumentów
        tree_frame = ttk.Frame(docs_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("nazwa", "data", "opis"), show="headings")
        tree.heading("nazwa", text="Nazwa pliku")
        tree.heading("data", text="Data dodania")
        tree.heading("opis", text="Opis")
        
        tree.column("nazwa", width=200)
        tree.column("data", width=120, anchor=tk.CENTER)
        tree.column("opis", width=250)
        
        for doc in documents:
            # Formatuj datę
            try:
                data = datetime.strptime(doc[3], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
            except:
                data = doc[3]
                
            tree.insert("", tk.END, values=(doc[0], data, doc[2]), tags=(doc[1],))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Przyciski
        btn_frame = ttk.Frame(docs_window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Podgląd dokumentu", 
                  command=lambda: self.preview_selected_document(tree)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Zamknij", 
                  command=docs_window.destroy).pack(side=tk.RIGHT, padx=10)

    def preview_selected_document(self, tree):
        """Podgląd wybranego dokumentu z listy"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz dokument z listy")
            return
        
        filepath = tree.item(selected[0], "tags")[0]  # Pobierz ścieżkę z tagów
        
        if not os.path.exists(filepath):
            messagebox.showerror("Błąd", "Plik dokumentu nie istnieje!")
            return
        
        self.preview_file(filepath)

    def change_list_status(self):
        """Zmienia status wybranego wykazu po potwierdzeniu"""
        selected_items = self.list_treeview.selection()
        if not selected_items:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać wykaz z listy")
            return
        
        selected_item = selected_items[0]
        item_data = self.list_treeview.item(selected_item)
        values = item_data['values']
        
        numer_rsd = values[1]
        numer_wykazu = values[2]
        current_status = values[4]  # To co widzi użytkownik ("Na stanie" lub "Rozliczony")
        
        # Ustal nowy status (dla komunikatu i bazy danych)
        if current_status == "Na stanie":
            new_status_display = "Rozliczony"
            new_status_db = "Rozliczony"
            new_items_status = "Rozliczono"
        else:
            new_status_display = "Na stanie"
            new_status_db = "Na stanie"
            new_items_status = "Na stanie"
        
        confirm = messagebox.askyesno(
            "Potwierdzenie zmiany statusu",
            f"Czy na pewno chcesz zmienić status wykazu:\n\n"
            f"Numer RSD: {numer_rsd}\n"
            f"Numer wykazu: {numer_wykazu}\n\n"
            f"Z {current_status} na {new_status_display}?",
            icon='question'
        )
        
        if not confirm:
            return
        
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            # Pobierz ID wykazu
            self.c.execute('''SELECT id FROM wykazy 
                            WHERE numer_rsd = ? AND numer_wykazu = ?''',
                          (numer_rsd, numer_wykazu))
            wykaz_data = self.c.fetchone()
            
            if not wykaz_data:
                messagebox.showerror("Błąd", "Nie znaleziono wykazu w bazie danych")
                return
            
            wykaz_id = wykaz_data[0]
            
            # Pobierz aktualne pozycje przed zmianą
            self.c.execute('''SELECT id, pozycja_nr, status 
                            FROM wykazy_pozycje 
                            WHERE id_wykazu=?''', (wykaz_id,))
            pozycje_przed = {row[0]: (row[1], row[2]) for row in self.c.fetchall()}
            
            # Aktualizuj status wykazu
            self.c.execute('''UPDATE wykazy SET status=? WHERE id=?''', 
                          (new_status_db, wykaz_id))
            
            # Aktualizuj statusy pozycji
            self.c.execute('''UPDATE wykazy_pozycje 
                            SET status=?
                            WHERE id_wykazu=?''',
                          (new_items_status, wykaz_id))
            
            # Zaloguj zmianę
            self.log_change("edycja", "wykazy", wykaz_id,
                          before={'status': current_status},
                          after={'status': new_status_db})
            
            # Zaloguj zmiany pozycji
            self.c.execute('''SELECT id, pozycja_nr, status 
                            FROM wykazy_pozycje 
                            WHERE id_wykazu=?''', (wykaz_id,))
            for row in self.c.fetchall():
                poz_id, poz_nr, new_status = row
                old_status = pozycje_przed.get(poz_id, (None, None))[1]
                
                if old_status != new_status:
                    self.log_change("edycja", "wykazy_pozycje", poz_id,
                                  before={'status': old_status},
                                  after={'status': new_status,
                                        'pozycja_nr': poz_nr,
                                        'id_wykazu': wykaz_id})
            
            self.conn.commit()
            self.load_lists()
            messagebox.showinfo("Sukces", f"Zmieniono status wykazu {numer_rsd}/{numer_wykazu}")
        
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas zmiany statusu: {str(e)}")

    def change_item_status(self):
        """Zmienia status wybranego przedmiotu po potwierdzeniu"""
        selected_item = self.list_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać przedmiot z listy")
            return
        
        item = self.list_treeview.item(selected_item[0])
        item_values = item['values']
        
        current_status = item_values[8]
        new_status = "Rozliczono" if current_status == "Na stanie" else "Na stanie"
        
        confirm = messagebox.askyesno(
            "Potwierdzenie zmiany statusu",
            f"Czy na pewno chcesz zmienić status przedmiotu:\n\n"
            f"Numer RSD: {item_values[1]}\n"
            f"Numer wykazu: {item_values[2]}\n"
            f"Pozycja: {item_values[5]}\n"
            f"Nazwa: {item_values[6]}\n\n"
            f"Z {current_status} na {new_status}?",
            icon='question'
        )
        
        if not confirm:
            return
        
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            # Pobierz ID pozycji
            self.c.execute('''SELECT wp.id, wp.pozycja_nr, wp.nazwa, wp.status
                            FROM wykazy_pozycje wp
                            JOIN wykazy w ON wp.id_wykazu = w.id
                            WHERE w.numer_rsd = ? AND w.numer_wykazu = ? AND wp.pozycja_nr = ?''',
                          (item_values[1], item_values[2], int(item_values[5].split('/')[0])))
            result = self.c.fetchone()
            
            if not result:
                messagebox.showerror("Błąd", "Nie znaleziono wybranej pozycji w bazie danych")
                return
            
            item_id, poz_nr, nazwa, old_status = result
            
            # Aktualizuj status pozycji
            self.c.execute('''UPDATE wykazy_pozycje 
                            SET status = ?
                            WHERE id = ?''', (new_status, item_id))
            
            # Zaloguj zmianę
            self.log_change("edycja", "wykazy_pozycje", item_id,
                          before={
                              'status': old_status,
                              'pozycja_nr': poz_nr,
                              'nazwa': nazwa
                          },
                          after={
                              'status': new_status,
                              'pozycja_nr': poz_nr,
                              'nazwa': nazwa
                          })
            
            self.conn.commit()
            self.load_lists()
            messagebox.showinfo("Sukces", "Status przedmiotu został zmieniony")
        
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas zmiany statusu: {str(e)}")

    def edit_position(self):
        """Edytuje wybraną pozycję z wykazu"""
        selected_items = self.list_treeview.selection()
        if not selected_items:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać pozycję z listy")
            return
        
        selected_item = selected_items[0]
        item_data = self.list_treeview.item(selected_item)
        values = item_data['values']
        
        # Pobierz ID pozycji z bazy danych
        self.c.execute('''SELECT wp.id 
                        FROM wykazy_pozycje wp
                        JOIN wykazy w ON wp.id_wykazu = w.id
                        WHERE w.numer_rsd = ? AND w.numer_wykazu = ? AND wp.pozycja_nr = ?''',
                      (values[1], values[2], int(values[5].split('/')[0])))
        result = self.c.fetchone()
        
        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono wybranej pozycji w bazie danych")
            return
        
        # Otwórz okno edycji
        self.open_edit_position_window(result[0], values)

    def open_edit_position_window(self, position_id, current_values):
        """Otwiera okno edycji pozycji"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edytuj pozycję {current_values[5]}")
        edit_window.geometry("500x350")
        
        # Nazwa przedmiotu
        ttk.Label(edit_window, text="Nazwa przedmiotu:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window)
        name_entry.pack(fill=tk.X, padx=20, pady=5)
        name_entry.insert(0, current_values[6])
        
        # Ilość
        ttk.Label(edit_window, text="Ilość:").pack()
        qty_entry = ttk.Entry(edit_window)
        qty_entry.pack(fill=tk.X, padx=20, pady=5)
        qty_entry.insert(0, current_values[7])
        
        # Status
        ttk.Label(edit_window, text="Status:").pack()
        status_var = tk.StringVar(value=current_values[8])
        status_combobox = ttk.Combobox(edit_window, 
                                     textvariable=status_var,
                                     values=["Na stanie", "Rozliczono"])
        status_combobox.pack(fill=tk.X, padx=20, pady=5)
        
        # Uwagi
        ttk.Label(edit_window, text="Uwagi:").pack()
        notes_entry = tk.Text(edit_window, height=5)
        notes_entry.pack(fill=tk.X, padx=20, pady=5)
        notes_entry.insert(tk.END, current_values[9])
        
        # Przyciski
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Zapisz", 
                  command=lambda: self.save_position_changes(
                      position_id,
                      name_entry.get(),
                      qty_entry.get(),
                      status_var.get(),
                      notes_entry.get("1.0", tk.END),
                      edit_window
                  )).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(btn_frame, text="Anuluj", 
                  command=edit_window.destroy).pack(side=tk.LEFT, padx=10)

    def save_position_changes(self, position_id, name, quantity, status, notes, window):
        """Zapisuje zmiany w pozycji z pełnym logowaniem"""
        try:
            if not name:
                messagebox.showerror("Błąd", "Nazwa przedmiotu jest wymagana!", parent=window)
                return
            
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Błąd", "Ilość musi być większa od zera!", parent=window)
                return
            
            # Pobierz aktualne dane przed zmianą
            self.c.execute('''SELECT * FROM wykazy_pozycje WHERE id=?''', (position_id,))
            old_data = self.c.fetchone()
            
            if not old_data:
                messagebox.showerror("Błąd", "Nie znaleziono pozycji do edycji!", parent=window)
                return
            
            old_values = {
                'nazwa': old_data[3],
                'ilosc': old_data[4],
                'status': old_data[6],
                'uwagi': old_data[7]
            }
            
            new_values = {
                'nazwa': name,
                'ilosc': quantity,
                'status': status,
                'uwagi': notes.strip()
            }
            
            # Przygotuj dane zmian
            changes = {}
            for key in old_values:
                if old_values[key] != new_values[key]:
                    changes[key] = {
                        'old': old_values[key],
                        'new': new_values[key]
                    }
            
            # Jeśli są zmiany do zapisania
            if changes:
                self.c.execute('''UPDATE wykazy_pozycje 
                                SET nazwa=?, ilosc=?, status=?, uwagi=?
                                WHERE id=?''',
                              (name, quantity, status, notes.strip(), position_id))
                
                # Zaloguj zmianę
                self.log_change("edycja", "wykazy_pozycje", position_id,
                              before=changes,
                              after={
                                  'id_wykazu': old_data[1],
                                  'pozycja_nr': old_data[2]
                              })
                
                self.conn.commit()
                messagebox.showinfo("Sukces", "Zmiany zostały zapisane!", parent=window)
                window.destroy()
                self.load_lists()
            else:
                messagebox.showinfo("Informacja", "Nie wprowadzono żadnych zmian", parent=window)
                window.destroy()
        
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa ilość! Wprowadź liczbę.", parent=window)
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}", parent=window)
            self.conn.rollback()

    def delete_list(self):
        """Usuwa cały wybrany wykaz wraz z pozycjami i dokumentami"""
        selected_items = self.list_treeview.selection()
        if not selected_items:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać wykaz z listy")
            return
        
        selected_item = selected_items[0]
        item_data = self.list_treeview.item(selected_item)
        values = item_data['values']
        
        confirm = messagebox.askyesno(
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz USUNĄĆ CAŁY WYKAZ:\n\n"
            f"Numer RSD: {values[1]}\n"
            f"Numer wykazu: {values[2]}\n\n"
            "Ta operacja usunie również WSZYSTKIE powiązane pozycje i dokumenty!",
            icon='warning'
        )
        
        if not confirm:
            return
        
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            # Pobierz pełne dane wykazu
            self.c.execute('''SELECT * FROM wykazy 
                            WHERE numer_rsd = ? AND numer_wykazu = ?''',
                          (values[1], values[2]))
            wykaz_data = self.c.fetchone()
            
            if not wykaz_data:
                messagebox.showerror("Błąd", "Nie znaleziono wykazu w bazie danych")
                return
            
            wykaz_id = wykaz_data[0]
            numer_rsd = wykaz_data[1]
            numer_wykazu = wykaz_data[2]
            
            # 1. Najpierw usuń wszystkie powiązane dokumenty i ich pliki
            self.c.execute('''SELECT sciezka FROM dokumenty WHERE id_wykazu = ?''', (wykaz_id,))
            documents = self.c.fetchall()
            
            for doc in documents:
                try:
                    if os.path.exists(doc[0]):
                        os.remove(doc[0])
                except Exception as e:
                    print(f"Nie udało się usunąć pliku {doc[0]}: {str(e)}")
            
            # 2. Usuń rekordy dokumentów z bazy
            self.c.execute('''DELETE FROM dokumenty WHERE id_wykazu = ?''', (wykaz_id,))
            
            # 3. Usuń pozycje wykazu
            self.c.execute('''DELETE FROM wykazy_pozycje WHERE id_wykazu = ?''', (wykaz_id,))
            
            # 4. Usuń sam wykaz
            self.c.execute('''DELETE FROM wykazy WHERE id = ?''', (wykaz_id,))
            
            # Zaloguj zmianę
            self.log_change("usunięcie", "wykazy", wykaz_id,
                          before={
                              'numer_rsd': numer_rsd,
                              'numer_wykazu': numer_wykazu,
                              'data_wykazu': wykaz_data[3],
                              'status': wykaz_data[8]
                          })
            
            self.conn.commit()
            
            # Kompleksowe odświeżenie widoków
            self.load_lists()
            
            # Jeśli jesteśmy w widoku dokumentów, odśwież go
            if hasattr(self, 'docs_tree') and self.docs_tree.winfo_exists():
                self.load_docs_lists()
                if hasattr(self, 'docs_treeview'):
                    self.docs_treeview.delete(*self.docs_treeview.get_children())
            
            messagebox.showinfo("Sukces", "Wykaz został całkowicie usunięty")
        
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Błąd", f"Nie udało się usunąć wykazu:\n{str(e)}")

    def delete_position(self):
        """Usuwa tylko wybraną pozycję z wykazu"""
        selected_items = self.list_treeview.selection()
        if not selected_items:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać pozycję z listy")
            return
        
        selected_item = selected_items[0]
        item_data = self.list_treeview.item(selected_item)
        values = item_data['values']
        
        # Potwierdzenie usunięcia
        confirm = messagebox.askyesno(
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć POZYCJĘ:\n\n"
            f"Numer RSD: {values[1]}\n"
            f"Numer wykazu: {values[2]}\n"
            f"Pozycja: {values[5]}\n"
            f"Nazwa: {values[6]}",
            icon='warning'
        )
        
        if not confirm:
            return
        
        try:
            # Rozpocznij transakcję
            self.conn.execute("BEGIN TRANSACTION")
            
            # Pobierz ID pozycji
            self.c.execute('''SELECT wp.id 
                            FROM wykazy_pozycje wp
                            JOIN wykazy w ON wp.id_wykazu = w.id
                            WHERE w.numer_rsd = ? AND w.numer_wykazu = ? AND wp.pozycja_nr = ?''',
                          (values[1], values[2], int(values[5].split('/')[0])))
            result = self.c.fetchone()
            
            if not result:
                messagebox.showerror("Błąd", "Nie znaleziono wybranej pozycji w bazie danych")
                return
            
            item_id = result[0]
            
            # Zaloguj usunięcie pozycji (pobierz pełne dane przed usunięciem)
            self.c.execute('''SELECT * FROM wykazy_pozycje WHERE id = ?''', (item_id,))
            pozycja_data = self.c.fetchone()
            self.log_change("usunięcie", "wykazy_pozycje", item_id, before=pozycja_data)
            
            # Zaloguj wszystkie powiązane dokumenty (przed usunięciem)
            self.c.execute('''SELECT * FROM dokumenty 
                            WHERE id_wykazu = (
                                SELECT id FROM wykazy 
                                WHERE numer_rsd = ? AND numer_wykazu = ?
                            )
                            AND id_pozycji = ?''',
                          (values[1], values[2], int(values[5].split('/')[0])))
            
            for dokument in self.c.fetchall():
                self.log_change("usunięcie", "dokumenty", before=dokument)
            
            # 1. Najpierw usuń dokumenty powiązane z pozycją
            self.c.execute('''DELETE FROM dokumenty 
                            WHERE id_wykazu = (
                                SELECT id FROM wykazy 
                                WHERE numer_rsd = ? AND numer_wykazu = ?
                            )
                            AND id_pozycji = ?''',
                          (values[1], values[2], int(values[5].split('/')[0])))
            
            # 2. Potem usuń samą pozycję
            self.c.execute('''DELETE FROM wykazy_pozycje 
                            WHERE id = ?''', (item_id,))
            
            # Zatwierdź transakcję
            self.conn.commit()
            
            # Odśwież widok
            self.load_lists()
            if hasattr(self, 'docs_treeview'):  # Jeśli jest otwarty widok dokumentów
                self.load_documents_list()
            
            messagebox.showinfo("Sukces", "Pozycja została usunięta")
        
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Błąd", f"Nie udało się usunąć pozycji:\n{str(e)}")

    def view_list_details(self, event):
        selected_item = self.list_treeview.selection()
        if not selected_item:
            return
        
        item_data = self.list_treeview.item(selected_item[0], 'values')
        list_id = item_data[0]
        
        # Pobierz dane wykazu
        self.c.execute("SELECT * FROM wykazy WHERE id=?", (list_id,))
        wykaz = self.c.fetchone()
        
        # Pobierz pozycje wykazu
        self.c.execute('''SELECT id, pozycja_nr, nazwa, ilosc, jednostka, status, uwagi 
                        FROM wykazy_pozycje 
                        WHERE id_wykazu=? 
                        ORDER BY pozycja_nr''', (list_id,))
        pozycje = self.c.fetchall()
        
        # Utwórz nowe okno z podglądem wykazu
        list_window = tk.Toplevel(self.root)
        list_window.title(f"Podgląd wykazu {wykaz[1]} / {wykaz[2]}")
        list_window.geometry("1000x700")
        
        # Nagłówek wykazu
        header_frame = ttk.Frame(list_window, borderwidth=2, relief=tk.GROOVE, padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Numer RSD: {wykaz[1]}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Numer wykazu: {wykaz[2]}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Data wykazu: {wykaz[3]}", font=('Arial', 10)).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Status: {wykaz[8]}", font=('Arial', 10)).pack(anchor=tk.W)
        if wykaz[9]:
            ttk.Label(header_frame, text=f"Uwagi: {wykaz[9]}", font=('Arial', 10)).pack(anchor=tk.W)
        
        # Przyciski akcji
        btn_frame = ttk.Frame(list_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Zmień status wykazu", 
                  command=lambda: self.change_list_status()).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eksportuj do PDF", 
                  command=lambda: self.export_to_pdf(wykaz_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Zamknij", 
                  command=list_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Tabela pozycji
        tree_frame = ttk.Frame(list_window)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("LP", "Nazwa", "Ilość", "Jednostka", "Status", "Uwagi"), show="headings")
        tree.heading("LP", text="L.p.")
        tree.heading("Nazwa", text="Nazwa przedmiotu")
        tree.heading("Ilość", text="Ilość")
        tree.heading("Jednostka", text="Jednostka")
        tree.heading("Status", text="Status")
        tree.heading("Uwagi", text="Uwagi")
        
        tree.column("LP", width=50, anchor=tk.CENTER)
        tree.column("Nazwa", width=300)
        tree.column("Ilość", width=80, anchor=tk.CENTER)
        tree.column("Jednostka", width=80, anchor=tk.CENTER)
        tree.column("Status", width=100, anchor=tk.CENTER)
        tree.column("Uwagi", width=300)
        
        for pozycja in pozycje:
            tree.insert("", tk.END, values=(pozycja[1], pozycja[2], pozycja[3], pozycja[4], pozycja[5], pozycja[6]))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)

    def export_single_list(self):
        selected = self.list_treeview.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz wykaz do eksportu")
            return
        
        item = self.list_treeview.item(selected[0])
        values = item['values']
        
        # Pobierz pełne dane z bazy
        self.c.execute('''SELECT w.numer_rsd, w.numer_wykazu, w.data_wykazu, 
                         wp.pozycja_nr, wp.nazwa, wp.ilosc, wp.jednostka, wp.status
                       FROM wykazy w
                       JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                       WHERE w.numer_rsd=? AND w.numer_wykazu=?''',
                     (values[1], values[2]))
        
        result = self.c.fetchall()
        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono danych wykazu")
            return
        
        # Przygotuj strukturę danych
        export_data = {
            "numer_rsd": result[0][0],
            "numer_wykazu": result[0][1],
            "data_wykazu": result[0][2],
            "pozycje": []
        }
        
        for row in result:
            export_data["pozycje"].append({
                "lp": row[3],
                "nazwa": row[4],
                "ilosc": row[5],
                "jednostka": row[6],
                "status": row[7]
            })
        
        # Zapisz do pliku
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"Wykaz_{export_data['numer_rsd']}_{export_data['numer_wykazu']}.json"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4)
            messagebox.showinfo("Sukces", f"Wyeksportowano do:\n{file_path}")

    def import_single_list(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Walidacja podstawowa
            required = ["numer_rsd", "numer_wykazu", "data_wykazu", "pozycje"]
            if not all(key in data for key in required):
                raise ValueError("Nieprawidłowy format pliku - brak wymaganych pól")
            
            # Sprawdź czy wykaz już istnieje
            self.c.execute('''SELECT id FROM wykazy 
                            WHERE numer_rsd=? AND numer_wykazu=?''',
                         (data["numer_rsd"], data["numer_wykazu"]))
            existing = self.c.fetchone()
            
            if existing:
                # Zapytaj użytkownika o nadpisanie
                if not messagebox.askyesno(
                    "Wykaz istnieje",
                    f"Wykaz {data['numer_rsd']}/{data['numer_wykazu']} już istnieje.\n"
                    "Czy chcesz go nadpisać?",
                    icon='warning'
                ):
                    return  # Anuluj jeśli użytkownik nie chce nadpisywać
                
                wykaz_id = existing[0]
                # 1. Usuń stare pozycje
                self.c.execute('''DELETE FROM wykazy_pozycje 
                                WHERE id_wykazu=?''', (wykaz_id,))
                # 2. Aktualizuj nagłówek
                self.c.execute('''UPDATE wykazy SET
                                data_wykazu=?,
                                data_utworzenia=?
                                WHERE id=?''',
                             (data["data_wykazu"],
                              datetime.now().strftime("%Y-%m-%d"),
                              wykaz_id))
            else:
                # Dodaj nowy wykaz
                self.c.execute('''INSERT INTO wykazy 
                                (numer_rsd, numer_wykazu, data_wykazu, data_utworzenia)
                                VALUES (?, ?, ?, ?)''',
                             (data["numer_rsd"], 
                              data["numer_wykazu"],
                              data["data_wykazu"],
                              datetime.now().strftime("%Y-%m-%d")))
                wykaz_id = self.c.lastrowid
            
            # Dodaj pozycje
            for poz in data["pozycje"]:
                self.c.execute('''INSERT INTO wykazy_pozycje
                                (id_wykazu, pozycja_nr, nazwa, ilosc, jednostka, status)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (wykaz_id,
                              poz.get("lp", 1),
                              poz["nazwa"],
                              poz["ilosc"],
                              poz.get("jednostka", "szt."),
                              poz.get("status", "Na stanie")))
            
            self.conn.commit()
            
            # Odśwież widok i ustaw filtry
            if hasattr(self, 'rsd_filter_entry'):
                self.rsd_filter_entry.delete(0, tk.END)
                self.rsd_filter_entry.insert(0, data["numer_rsd"])
            if hasattr(self, 'list_num_filter_entry'):
                self.list_num_filter_entry.delete(0, tk.END)
                self.list_num_filter_entry.insert(0, data["numer_wykazu"])
            
            self.load_lists()
            messagebox.showinfo("Sukces", "Wykaz został zaimportowany!")
            
        except json.JSONDecodeError:
            messagebox.showerror("Błąd", "Nieprawidłowy format pliku JSON!")
            self.conn.rollback()
        except Exception as e:
            messagebox.showerror("Błąd", f"Import nieudany:\n{str(e)}")
            self.conn.rollback()

    def create_new_list(self):
        """Wyświetla formularz tworzenia nowego wykazu"""
        self.clear_content_frame()
        self.current_items = []  # Reset listy pozycji
        
        # Pobierz istniejące numery RSD dla listy rozwijanej
        self.c.execute("SELECT DISTINCT numer_rsd FROM wykazy ORDER BY numer_rsd")
        self.current_rsd_numbers = [row[0] for row in self.c.fetchall()]
        
        # Ramka dla danych wykazu
        form_frame = ttk.Frame(self.content_frame, borderwidth=2, relief=tk.GROOVE, padding=10)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Kontener na pola w jednej linii
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill=tk.X, pady=5)
        
        # Pole Numer RSD - wersja uproszczona bez przycisku "Nowy"
        rsd_frame = ttk.Frame(fields_frame)
        rsd_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(rsd_frame, text="Numer RSD:").pack(anchor=tk.W)
        
        self.rsd_var = tk.StringVar()
        if self.current_rsd_numbers:
            self.rsd_combobox = ttk.Combobox(rsd_frame, textvariable=self.rsd_var, 
                                           values=self.current_rsd_numbers)
            self.rsd_combobox.pack(fill=tk.X)
        else:
            self.rsd_entry = ttk.Entry(rsd_frame, textvariable=self.rsd_var)
            self.rsd_entry.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(fields_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Pole Numer wykazu MS - nowa wersja
        wykaz_frame = ttk.Frame(fields_frame)
        wykaz_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(wykaz_frame, text="Numer wykazu:").pack(anchor=tk.W)
        self.wykaz_entry = ttk.Entry(wykaz_frame)
        self.wykaz_entry.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(fields_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Pole Data wykazu - nowa wersja
        data_frame = ttk.Frame(fields_frame)
        data_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(data_frame, text="Data wykazu:").pack(anchor=tk.W)
        self.data_entry = ttk.Entry(data_frame)
        self.data_entry.pack(fill=tk.X)
        self.data_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Separator
        ttk.Separator(fields_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Pole Uwagi - nowa wersja
        uwagi_frame = ttk.Frame(fields_frame)
        uwagi_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(uwagi_frame, text="Uwagi:").pack(anchor=tk.W)
        self.uwagi_entry = ttk.Entry(uwagi_frame)
        self.uwagi_entry.pack(fill=tk.X)
        
        # Przyciski dla pozycji - nowa wersja (mniejsze)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=(5, 10))
        
        style = ttk.Style()
        style.configure('Small.TButton', padding=2, font=('Arial', 8))
        
        ttk.Button(btn_frame, text="Dodaj pozycję", command=self.add_position_form, 
                  style='Small.TButton').grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Edytuj pozycję", command=self.edit_position, 
                  style='Small.TButton').grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Usuń pozycję", command=self.delete_position, 
                  style='Small.TButton').grid(row=0, column=2, padx=2)
        
        # Tabela dodanych pozycji
        self.position_tree = ttk.Treeview(self.content_frame, 
                                        columns=("LP", "Nazwa", "Ilość", "Jednostka", "Uwagi"), 
                                        show="headings", selectmode='browse')
        
        for col in ("LP", "Nazwa", "Ilość", "Jednostka", "Uwagi"):
            self.position_tree.heading(col, text=col)
        
        self.position_tree.column("LP", width=50, anchor=tk.CENTER)
        self.position_tree.column("Nazwa", width=300)
        self.position_tree.column("Ilość", width=80, anchor=tk.CENTER)
        self.position_tree.column("Jednostka", width=80, anchor=tk.CENTER)
        self.position_tree.column("Uwagi", width=300)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.position_tree.yview)
        self.position_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.position_tree.pack(expand=True, fill=tk.BOTH, padx=20, pady=(0, 10))
        
        # Przyciski zapisz/anuluj - wersja kompaktowa
        btn_frame_bottom = ttk.Frame(self.content_frame)
        btn_frame_bottom.pack(pady=(0, 10))

        # Definicja stylu dla małych przycisków (jeśli nie istnieje)
        self.style.configure('Small.TButton', 
                            font=('Arial', 8),
                            padding=2,
                            width=12,
                            anchor='center')

        # Przyciski w kompaktowym stylu
        ttk.Button(btn_frame_bottom, 
                  text="Zapisz wykaz", 
                  command=self.save_list,
                  style='Small.TButton').grid(row=0, column=0, padx=2, ipadx=2, ipady=1)

        ttk.Button(btn_frame_bottom,
                  text="Anuluj",
                  command=self.show_preview_view,
                  style='Small.TButton').grid(row=0, column=1, padx=2, ipadx=2, ipady=1)
    
    def new_rsd(self):
        """Przełącza na ręczne wprowadzanie numeru RSD"""
        self.rsd_combobox.pack_forget()
        for widget in self.rsd_combobox.master.winfo_children()[2:]:
            widget.pack_forget()
        
        self.rsd_entry = ttk.Entry(self.rsd_combobox.master, textvariable=self.rsd_var)
        self.rsd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def add_position_form(self):
        """Wyświetla formularz dodawania nowej pozycji"""
        self.position_window = tk.Toplevel(self.root)
        self.position_window.title("Dodaj pozycję")
        self.position_window.geometry("500x350")
        
        # Numer pozycji
        position_frame = ttk.Frame(self.position_window)
        position_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(position_frame, text="Pozycja nr:").pack(side=tk.LEFT)
        self.position_number = ttk.Entry(position_frame)
        self.position_number.pack(side=tk.LEFT, padx=10)
        self.position_number.insert(0, len(self.current_items) + 1)
        
        # Nazwa przedmiotu
        name_frame = ttk.Frame(self.position_window)
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(name_frame, text="Nazwa przedmiotu:").pack(side=tk.LEFT)
        self.position_name = ttk.Entry(name_frame)
        self.position_name.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Ilość i jednostka
        quantity_frame = ttk.Frame(self.position_window)
        quantity_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(quantity_frame, text="Ilość:").pack(side=tk.LEFT)
        self.position_quantity = ttk.Entry(quantity_frame, width=10)
        self.position_quantity.pack(side=tk.LEFT, padx=5)
        self.position_quantity.insert(0, "1")
        
        ttk.Label(quantity_frame, text="Jednostka:").pack(side=tk.LEFT, padx=5)
        self.position_unit = ttk.Combobox(quantity_frame, values=["szt.", "kg", "m", "l", "opak."], width=10)
        self.position_unit.pack(side=tk.LEFT)
        self.position_unit.set("szt.")
        
        # Uwagi
        notes_frame = ttk.Frame(self.position_window)
        notes_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(notes_frame, text="Uwagi:").pack(side=tk.LEFT)
        self.position_notes = tk.Text(notes_frame, height=5, width=40)
        self.position_notes.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Przyciski
        btn_frame = ttk.Frame(self.position_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Dodaj", command=self.add_position, 
                  style='TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Anuluj", command=self.position_window.destroy, 
                  style='TButton').pack(side=tk.LEFT, padx=10)
    
    def add_position(self):
        """Dodaje pozycję do tymczasowej listy"""
        try:
            position_nr = int(self.position_number.get())
            name = self.position_name.get()
            quantity = int(self.position_quantity.get())
            unit = self.position_unit.get()
            notes = self.position_notes.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Błąd", "Nazwa przedmiotu jest wymagana!")
                return
            
            if quantity <= 0:
                messagebox.showerror("Błąd", "Ilość musi być większa od zera!")
                return
            
            # Sprawdź czy pozycja o tym numerze już istnieje
            for item in self.current_items:
                if item[0] == position_nr:
                    if messagebox.askyesno("Potwierdzenie", 
                                         f"Pozycja o numerce {position_nr} już istnieje. Czy chcesz ją zastąpić?"):
                        # Usuń istniejącą pozycję
                        self.current_items = [item for item in self.current_items if item[0] != position_nr]
                    else:
                        return
            
            self.current_items.append((position_nr, name, quantity, unit, notes))
            
            # Posortuj pozycje po numerze
            self.current_items.sort(key=lambda x: x[0])
            
            # Aktualizuj widok tabeli
            self.update_position_tree()
            
            self.position_window.destroy()
        
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe dane! Sprawdź numer pozycji i ilość.")
    
    def update_position_tree(self):
        """Aktualizuje widok tabeli pozycji"""
        for item in self.position_tree.get_children():
            self.position_tree.delete(item)
        
        for position in self.current_items:
            self.position_tree.insert("", tk.END, values=position)
    
    def save_list(self):
        """Zapisuje nowy wykaz do bazy danych i tworzy plik z wykazem"""
        try:
            numer_rsd = self.rsd_var.get()
            numer_wykazu = self.wykaz_entry.get()
            data_wykazu = self.data_entry.get()
            uwagi = self.uwagi_entry.get()
            
            if not numer_rsd or not numer_wykazu or not data_wykazu:
                messagebox.showerror("Błąd", "Pola: Numer RSD, Numer wykazu i Data wykazu są wymagane!")
                return
            
            if not self.current_items:
                messagebox.showerror("Błąd", "Wykaz musi zawierać co najmniej jedną pozycję!")
                return
            
            # Sprawdź format daty
            try:
                datetime.strptime(data_wykazu, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty! Użyj formatu DD.MM.RRRR")
                return
            
            # Sprawdź unikalność numeru wykazu
            self.c.execute("SELECT id FROM wykazy WHERE numer_wykazu=?", (numer_wykazu,))
            if self.c.fetchone():
                messagebox.showerror("Błąd", "Wykaz o podanym numerze już istnieje!")
                return
            
            # Generuj nazwę pliku
            clean_rsd = numer_rsd.replace("/", "_")
            clean_wykaz = numer_wykazu.replace("/", "_")
            filename = f"Wykaz_{clean_rsd}_{clean_wykaz}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(self.evidence_dir, filename)
            
            # Przygotuj dane do zapisania w pliku
            wykaz_data = {
                "numer_rsd": numer_rsd,
                "numer_wykazu": numer_wykazu,
                "data_wykazu": data_wykazu,
                "data_utworzenia": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "uwagi": uwagi,
                "pozycje": self.current_items
            }
            
            # Zapisz do pliku JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(wykaz_data, f, ensure_ascii=False, indent=4)
            
            # Zapisz nagłówek wykazu do bazy danych
            self.c.execute('''INSERT INTO wykazy 
                            (numer_rsd, numer_wykazu, data_wykazu, data_utworzenia, 
                             sciezka_pliku, uwagi)
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                            (numer_rsd, numer_wykazu, data_wykazu, 
                             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                             file_path, uwagi))
            wykaz_id = self.c.lastrowid
            
            # Zaloguj dodanie wykazu
            self.log_change("dodanie", "wykazy", wykaz_id, 
                           after={
                               'numer_rsd': numer_rsd,
                               'numer_wykazu': numer_wykazu,
                               'data_wykazu': data_wykazu,
                               'uwagi': uwagi,
                               'sciezka_pliku': file_path
                           })
            
            # Zapisz pozycje wykazu do bazy danych
            for position in self.current_items:
                self.c.execute('''INSERT INTO wykazy_pozycje 
                                (id_wykazu, pozycja_nr, nazwa, ilosc, jednostka, uwagi)
                                VALUES (?, ?, ?, ?, ?, ?)''', 
                                (wykaz_id, *position))
                
                # Zaloguj dodanie pozycji
                self.log_change("dodanie", "wykazy_pozycje", self.c.lastrowid,
                              after={
                                  'id_wykazu': wykaz_id,
                                  'pozycja_nr': position[0],
                                  'nazwa': position[1],
                                  'ilosc': position[2],
                                  'jednostka': position[3],
                                  'uwagi': position[4]
                              })
            
            self.conn.commit()
            messagebox.showinfo("Sukces", f"Wykaz został pomyślnie zapisany!\nŚcieżka: {file_path}")
            self.show_preview_view()
        
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Błąd", f"Konflikt danych: {str(e)}")
            self.conn.rollback()
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas zapisywania wykazu:\n{str(e)}")
            self.conn.rollback()

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        menu_frame = ttk.Frame(main_frame, relief="raised", padding="5")
        menu_frame.grid(row=0, column=0, sticky="ew")

        # Główne przyciski menu
        ttk.Button(menu_frame, text="Podgląd", command=self.show_preview_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Nowy wykaz", command=self.create_new_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Inwentaryzacja", command=self.inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Załączone kwity", command=self.show_docs_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Historia zmian", command=self.change_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Ustawienia", command=self.settings).pack(side=tk.LEFT, padx=5)
        
        # Tworzymy ładniejszy przycisk informacyjny - ZMIENIONE
        self.create_info_button(menu_frame)
        
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=10)

    def create_info_button(self, parent):
        """Tworzy ładny przycisk informacyjny z obrazkiem"""
        try:
            # Tworzymy mały obrazek "i" w kółku programowo
            from PIL import Image, ImageDraw, ImageTk
            
            # Tworzymy obrazek 16x16 pikseli
            img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Rysujemy niebieskie kółko
            draw.ellipse([2, 2, 14, 14], fill='#0078D7', outline='#005A9E')
            
            # Rysujemy białą literę "i"
            draw.text((7, 3), "i", fill='white', font=ImageFont.load_default())
            
            # Konwertujemy do formatu Tkinter
            self.info_icon = ImageTk.PhotoImage(img)
            
            # Tworzymy przycisk z ikoną
            info_button = ttk.Button(parent, image=self.info_icon, 
                                   command=self.show_info, width=20)
            info_button.pack(side=tk.RIGHT, padx=5)
            
        except ImportError:
            # Fallback: jeśli PIL nie jest dostępny, użyj prostszego przycisku
            info_button = ttk.Button(parent, text="i", width=2, 
                                   command=self.show_info, style='TButton')
            info_button.pack(side=tk.RIGHT, padx=5)

    def show_info(self):
        """Wyświetla informacje o autorze"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Informacje")
        info_window.geometry("300x200")
        info_window.resizable(False, False)
        
        # Wyśrodkuj okno na ekranie
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Ustaw styl okna
        info_window.configure(bg='white')
        
        # Ramka główna
        main_frame = ttk.Frame(info_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tekst informacyjny wyśrodkowany
        info_text = """    Autor:

    sierż. SG Łukasz Jabłoński
    Placówka Straży Granicznej
    w Gdyni
    
    lukasz.jablonski@strazgraniczna.pl"""
        
        label = ttk.Label(main_frame, text=info_text, justify=tk.CENTER, 
                         font=('Arial', 10))
        label.pack(expand=True)

    def create_info_button(self, parent):
        """Tworzy ładny przycisk informacyjny bez obrazka"""
        # Stylizowany przycisk z okrągłym tłem
        style = ttk.Style()
        style.configure('Info.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#0078D7',
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('Info.TButton', 
                 background=[('active', '#005A9E')])
        
        info_button = ttk.Button(parent, text="i", width=2,
                               command=self.show_info, style='Info.TButton')
        info_button.pack(side=tk.RIGHT, padx=5)

    def inventory(self):
        """Wyświetla panel inwentaryzacji z poprawionymi statusami"""
        self.clear_content_frame()
        
        # Ramka tylko dla filtrów
        filter_frame = ttk.LabelFrame(self.content_frame, text="Filtry", padding=10)
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Lewa strona - kontrolki filtrowania
        left_filter_frame = ttk.Frame(filter_frame)
        left_filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Wybór roku
        ttk.Label(left_filter_frame, text="Rok:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar(value="Wszystkie")
        
        # Pobierz dostępne lata z bazy
        self.c.execute("SELECT DISTINCT strftime('%Y', data_wykazu) FROM wykazy WHERE data_wykazu IS NOT NULL")
        years = ["Wszystkie"] + [row[0] for row in self.c.fetchall() if row[0]]
        
        year_combo = ttk.Combobox(left_filter_frame, textvariable=self.year_var, 
                                values=years, state="readonly", width=10)
        year_combo.pack(side=tk.LEFT, padx=5)
        
        # Przycisk zastosuj filtry - teraz w tej samej linii
        ttk.Button(left_filter_frame, text="Zastosuj", command=self.update_inventory_stats,
                  style='SmallFilter.TButton', width=10).pack(side=tk.LEFT, padx=5)
        
        # Przycisk odśwież - DODANY W TEJ SAMEJ LINII
        ttk.Button(left_filter_frame, text="Odśwież", command=self.inventory,
                  style='SmallFilter.TButton', width=10).pack(side=tk.LEFT, padx=5)
        
        # Prawa strona - przyciski raportów
        right_btn_frame = ttk.Frame(filter_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        report_buttons = [
            ("PDF", lambda: self.generate_report('PDF')),
            ("WORD", lambda: self.generate_report('WORD')),
            ("EXCEL", lambda: self.generate_report('EXCEL'))
        ]
        
        for text, command in report_buttons:
            ttk.Button(right_btn_frame, text=text, command=command,
                      style='SmallFilter.TButton', width=6).pack(side=tk.LEFT, padx=2)
        
        # Tabela statystyk
        table_frame = ttk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 10), expand=True)
        
        # Nagłówki kolumn - zmienione na "Na stanie" zamiast "Aktywne"
        headers = ["Kategoria", "Wszystkie", "Na stanie", "Rozliczone"]
        for col, header in enumerate(headers):
            header_label = ttk.Label(table_frame, text=header, font=('Arial', 10, 'bold'),
                                   background='#f0f0f0', padding=5)
            header_label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        
        # Wiersze z danymi - teraz 3 kategorie: Przedmioty, Wykazy i Sprawy RSD
        self.stat_rows = {
            'przedmioty': [  # ZMIENIONE Z 'products' NA 'przedmioty'
                ttk.Label(table_frame, text="Przedmioty", padding=5),  # ZMIENIONE
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5)
            ],
            'lists': [
                ttk.Label(table_frame, text="Wykazy", padding=5),
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5)
            ],
            'rsd_cases': [
                ttk.Label(table_frame, text="Sprawy RSD", padding=5),
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5),
                ttk.Label(table_frame, text="0", padding=5)
            ]
        }
        
        # Ułożenie wierszy w tabeli
        for row_idx, row_key in enumerate(['przedmioty', 'lists', 'rsd_cases'], start=1):  # ZMIENIONE
            bg_color = '#ffffff' if row_idx % 2 == 1 else '#f9f9f9'
            for col_idx, label in enumerate(self.stat_rows[row_key]):
                label.configure(background=bg_color)
                label.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
        
        # Konfiguracja rozciągania kolumn
        for i in range(4):
            table_frame.columnconfigure(i, weight=1)
        
        # Pierwsze ładowanie danych
        self.update_inventory_stats()

    def update_inventory_stats(self):
        """Aktualizuje statystyki z poprawnym liczeniem przedmiotów, wykazów i spraw RSD"""
        selected_year = self.year_var.get()
        
        year_condition = ""
        if selected_year != "Wszystkie":
            year_condition = f" AND strftime('%Y', data_wykazu) = '{selected_year}'"
        
        try:
            # 1. PRZEDMIOTY (pozycje wykazów) - ZMIENIONE
            # Wszystkie przedmioty
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy_pozycje wp
                            JOIN wykazy w ON wp.id_wykazu = w.id
                            WHERE 1=1 {year_condition}""")
            total_items = self.c.fetchone()[0] or 0
            
            # Przedmioty na stanie
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy_pozycje wp
                            JOIN wykazy w ON wp.id_wykazu = w.id
                            WHERE wp.status = 'Na stanie' {year_condition}""")
            active_items = self.c.fetchone()[0] or 0
            
            # Przedmioty rozliczone
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy_pozycje wp
                            JOIN wykazy w ON wp.id_wykazu = w.id
                            WHERE wp.status = 'Rozliczono' {year_condition}""")
            closed_items = self.c.fetchone()[0] or 0

            # 2. WYKAZY
            # Wszystkie wykazy
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy 
                            WHERE 1=1 {year_condition}""")
            total_lists = self.c.fetchone()[0] or 0
            
            # Wykazy na stanie
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy 
                            WHERE status = 'Na stanie' {year_condition}""")
            active_lists = self.c.fetchone()[0] or 0
            
            # Wykazy rozliczone
            self.c.execute(f"""SELECT COUNT(*) 
                            FROM wykazy 
                            WHERE status = 'Rozliczony' {year_condition}""")
            closed_lists = self.c.fetchone()[0] or 0

            # 3. SPRAWY RSD
            # Wszystkie sprawy RSD (unikalne numery RSD)
            self.c.execute(f"""SELECT COUNT(DISTINCT numer_rsd) 
                            FROM wykazy 
                            WHERE numer_rsd IS NOT NULL 
                            AND numer_rsd != '' {year_condition}""")
            total_cases = self.c.fetchone()[0] or 0
            
            # Sprawy RSD z przynajmniej jednym wykazem na stanie
            self.c.execute(f"""SELECT COUNT(DISTINCT w1.numer_rsd)
                            FROM wykazy w1
                            WHERE w1.numer_rsd IS NOT NULL 
                            AND w1.numer_rsd != ''
                            AND EXISTS (
                                SELECT 1 FROM wykazy w2 
                                WHERE w2.numer_rsd = w1.numer_rsd 
                                AND w2.status = 'Na stanie'
                                {year_condition.replace('AND', 'AND w2.')}
                            )
                            {year_condition}""")
            active_cases = self.c.fetchone()[0] or 0
            
            # Sprawy RSD gdzie wszystkie wykazy są rozliczone
            self.c.execute(f"""SELECT COUNT(DISTINCT w1.numer_rsd)
                            FROM wykazy w1
                            WHERE w1.numer_rsd IS NOT NULL 
                            AND w1.numer_rsd != ''
                            AND NOT EXISTS (
                                SELECT 1 FROM wykazy w2 
                                WHERE w2.numer_rsd = w1.numer_rsd 
                                AND w2.status != 'Rozliczony'
                                {year_condition.replace('AND', 'AND w2.')}
                            )
                            {year_condition}""")
            closed_cases = self.c.fetchone()[0] or 0

            # Aktualizacja interfejsu
            self.stat_rows['przedmioty'][1].config(text=str(total_items))
            self.stat_rows['przedmioty'][2].config(text=str(active_items))
            self.stat_rows['przedmioty'][3].config(text=str(closed_items))
            
            self.stat_rows['lists'][1].config(text=str(total_lists))
            self.stat_rows['lists'][2].config(text=str(active_lists))
            self.stat_rows['lists'][3].config(text=str(closed_lists))
            
            self.stat_rows['rsd_cases'][1].config(text=str(total_cases))
            self.stat_rows['rsd_cases'][2].config(text=str(active_cases))
            self.stat_rows['rsd_cases'][3].config(text=str(closed_cases))
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować statystyk:\n{str(e)}")
            
    def generate_report(self, report_type):
        """Generuje raport w wybranym formacie"""
        selected_year = self.year_var.get()
        messagebox.showinfo("Raport", 
                           f"Generowanie raportu {report_type} dla roku {selected_year}\n"
                           "Ta funkcjonalność będzie dostępna w przyszłej wersji")

    def show_docs_view(self):
        """Wyświetla panel dokumentów z dwiema sekcjami"""
        self.clear_content_frame()
        
        # Główny kontener
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- FILTRY ---
        filter_frame = ttk.LabelFrame(main_frame, text="Filtry", padding=10)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Numer RSD:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.docs_rsd_filter = ttk.Entry(filter_frame, width=15)
        self.docs_rsd_filter.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Numer wykazu:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.docs_list_filter = ttk.Entry(filter_frame, width=15)
        self.docs_list_filter.grid(row=0, column=3, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.docs_status_filter = ttk.Combobox(filter_frame, 
                                             values=["Wszystkie", "Aktywne", "Rozliczone"],
                                             width=12)
        self.docs_status_filter.grid(row=0, column=5, padx=5, sticky=tk.W)
        self.docs_status_filter.set("Wszystkie")

        ttk.Button(filter_frame, text="Filtruj", command=self.load_docs_lists,
                  style='SmallFilter.TButton', width=10).grid(row=0, column=6, padx=10)

        # --- LISTA WYKAZÓW ---
        list_frame = ttk.LabelFrame(main_frame, text="Lista wykazów", padding=10)
        list_frame.pack(fill=tk.BOTH, pady=5, expand=True)

        self.docs_tree = ttk.Treeview(list_frame, 
                                    columns=("numer_rsd", "numer_wykazu", "pozycje", "data", "status"),
                                    show="headings", height=8)
        
        # Konfiguracja kolumn
        columns = [
            ("numer_rsd", "Numer RSD", 120),
            ("numer_wykazu", "Numer wykazu", 120), 
            ("pozycje", "Liczba pozycji", 100, tk.CENTER),
            ("data", "Data", 100),
            ("status", "Status", 100)
        ]
        
        for col in columns:
            self.docs_tree.heading(col[0], text=col[1])
            if len(col) > 3:
                self.docs_tree.column(col[0], width=col[2], anchor=col[3])
            else:
                self.docs_tree.column(col[0], width=col[2])

        scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.docs_tree.yview)
        self.docs_tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- PRZYCISKI AKCJI DLA WYKAZÓW ---
        list_btn_frame = ttk.Frame(main_frame)
        list_btn_frame.pack(fill=tk.X, pady=(0, 10))

        # Przyciski z ujednoliconym stylem
        list_buttons = [
            ("Pokaż dokumenty", self.show_selected_list_documents),
            ("Szczegóły", self.show_list_details),
            ("Dodaj dok.", self.add_document_dialog),
            ("Odśwież", self.load_docs_lists)
        ]

        for col, (text, command) in enumerate(list_buttons):
            btn = ttk.Button(
                list_btn_frame,
                text=text,
                command=command,
                style='SmallFilter.TButton',
                width=15
            )
            btn.grid(row=0, column=col, padx=2, sticky='ew')

        # --- LISTA DOKUMENTÓW ---
        docs_frame = ttk.LabelFrame(main_frame, text="Dokumenty wybranego wykazu", padding=10)
        docs_frame.pack(fill=tk.BOTH, pady=5, expand=True)

        self.docs_treeview = ttk.Treeview(docs_frame, 
                                        columns=("pozycja", "nazwa", "data", "opis"),
                                        show="headings",
                                        height=10)
        
        # Konfiguracja kolumn dokumentów
        doc_columns = [
            ("pozycja", "Pozycja", 80, tk.CENTER),
            ("nazwa", "Nazwa dokumentu", 200),
            ("data", "Data dodania", 120),
            ("opis", "Opis", 300)
        ]
        
        for col in doc_columns:
            self.docs_treeview.heading(col[0], text=col[1])
            self.docs_treeview.column(col[0], width=col[2], anchor=col[3] if len(col) > 3 else tk.W)

        scroll_y = ttk.Scrollbar(docs_frame, orient=tk.VERTICAL, command=self.docs_treeview.yview)
        self.docs_treeview.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- PRZYCISKI AKCJI DLA DOKUMENTÓW ---
        doc_btn_frame = ttk.Frame(main_frame)
        doc_btn_frame.pack(fill=tk.X, pady=(0, 10))

        # Przyciski z ujednoliconym stylem
        doc_buttons = [
            ("Podgląd", self.preview_document),
            ("Usuń", self.delete_document)
        ]

        for col, (text, command) in enumerate(doc_buttons):
            btn = ttk.Button(
                doc_btn_frame,
                text=text,
                command=command,
                style='SmallFilter.TButton',
                width=15
            )
            btn.grid(row=0, column=col, padx=2, sticky='ew')

        # Ładowanie danych
        self.load_docs_lists()

    def show_all_documents(self):
        """Pokazuje wszystkie dokumenty dla wybranego wykazu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz wykaz z listy")
            return
        
        list_id = selected[0]
        self.c.execute('''SELECT d.id_pozycji, d.nazwa_pliku, d.sciezka, d.opis, d.data_dodania,
                         wp.nazwa as nazwa_pozycji
                       FROM dokumenty d
                       LEFT JOIN wykazy_pozycje wp ON d.id_wykazu = wp.id_wykazu AND d.id_pozycji = wp.pozycja_nr
                       WHERE d.id_wykazu=?''', (list_id,))
        
        documents = self.c.fetchall()
        
        if not documents:
            messagebox.showinfo("Informacja", "Brak dokumentów dla wybranego wykazu")
            return
        
        # Okno z listą dokumentów
        docs_window = tk.Toplevel(self.root)
        docs_window.title("Wszystkie dokumenty wykazu")
        docs_window.geometry("800x600")
        
        # Treeview z dokumentami
        tree = ttk.Treeview(docs_window, columns=("pozycja", "nazwa", "data", "opis"), show="headings")
        tree.heading("pozycja", text="Pozycja")
        tree.heading("nazwa", text="Nazwa pliku")
        tree.heading("data", text="Data dodania")
        tree.heading("opis", text="Opis")
        
        tree.column("pozycja", width=100)
        tree.column("nazwa", width=200)
        tree.column("data", width=150)
        tree.column("opis", width=350)
        
        for doc in documents:
            tree.insert("", tk.END, 
                      values=(doc[0], doc[1], doc[4], doc[3]),
                      tags=(doc[2],))  # Ścieżka pliku jako tag
        
        scrollbar = ttk.Scrollbar(docs_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)
        
        # Przycisk podglądu
        btn_frame = ttk.Frame(docs_window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, 
                  text="Podgląd wybranego dokumentu", 
                  command=lambda: self.preview_selected_document(tree)).pack()
        
    def preview_selected_document(self, tree):
        """Podgląd wybranego dokumentu z listy"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz dokument z listy")
            return
        
        filepath = tree.item(selected[0], "tags")[0]  # Pobierz ścieżkę z tagów
        
        if not os.path.exists(filepath):
            messagebox.showerror("Błąd", "Plik dokumentu nie istnieje!")
            return
        
        self.preview_file(filepath)
        
    def preview_document(self):
        """Podgląd dokumentu z głównej listy"""
        selected = self.docs_treeview.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz dokument z listy")
            return
        
        item = self.docs_treeview.item(selected[0])
        list_id = self.current_doc_list
        
        # Pobierz pełną ścieżkę z bazy danych
        self.c.execute('''SELECT sciezka FROM dokumenty 
                        WHERE id_wykazu=? AND id_pozycji=?''',
                     (list_id, item['values'][0]))
        
        result = self.c.fetchone()
        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono ścieżki dokumentu")
            return
        
        filepath = result[0]
        self.preview_file(filepath)
        
    def preview_file(self, filepath):
        """Podgląd pliku (obsługa różnych formatów)"""
        if not os.path.exists(filepath):
            messagebox.showerror("Błąd", "Plik nie istnieje!")
            return
        
        # Dla obrazów
        if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img_window = tk.Toplevel(self.root)
                img_window.title(f"Podgląd: {os.path.basename(filepath)}")
                
                img = Image.open(filepath)
                img.thumbnail((800, 800))
                img_tk = ImageTk.PhotoImage(img)
                
                label = ttk.Label(img_window, image=img_tk)
                label.image = img_tk
                label.pack()
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można otworzyć obrazu:\n{str(e)}")
        
        # Dla PDF
        elif filepath.lower().endswith('.pdf'):
            try:
                os.startfile(filepath)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można otworzyć PDF:\n{str(e)}")
        
        # Dla innych plików
        else:
            try:
                os.startfile(filepath)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można otworzyć pliku:\n{str(e)}")

    def _load_positions_for_document(self):
        """Ładuje dostępne pozycje z wybranego wykazu"""
        if not hasattr(self, 'current_doc_list'):
            return
        
        try:
            # Pobierz pozycje z bazy danych
            self.c.execute("""SELECT pozycja_nr, nazwa 
                           FROM wykazy_pozycje 
                           WHERE id_wykazu=? 
                           ORDER BY pozycja_nr""", (self.current_doc_list,))
            
            positions = [f"{row[0]} - {row[1]}" for row in self.c.fetchall()]
            self.doc_position['values'] = positions
            if positions:
                self.doc_position.current(0)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować pozycji: {str(e)}")

    def show_selected_list_documents(self):
        """Wypełnia dolną tabelę dokumentami wybranego wykazu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz wykaz z listy")
            return
        
        list_id = selected[0]
        self.current_doc_list = list_id  # Zapamiętaj wybrany wykaz
        
        # Pobierz dokumenty z bazy danych
        self.c.execute('''SELECT d.id_pozycji, d.nazwa_pliku, d.data_dodania, d.opis,
                         wp.nazwa as nazwa_pozycji
                       FROM dokumenty d
                       LEFT JOIN wykazy_pozycje wp ON d.id_wykazu = wp.id_wykazu AND d.id_pozycji = wp.pozycja_nr
                       WHERE d.id_wykazu=? ORDER BY d.id_pozycji''', (list_id,))
        
        documents = self.c.fetchall()
        
        # Wyczyść obecną listę
        for item in self.docs_treeview.get_children():
            self.docs_treeview.delete(item)
        
        # Wypełnij dolną tabelę dokumentami
        for doc in documents:
            # Formatuj datę
            try:
                data = datetime.strptime(doc[2], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
            except:
                data = doc[2]
            
            self.docs_treeview.insert("", tk.END, 
                                    values=(doc[0], doc[1], data, doc[3]),
                                    tags=(doc[4],))  # Nazwa pozycji jako tag

    def _setup_validation(self):
        """Konfiguruje walidację pól"""
        # Walidacja daty
        def validate_date(new_val):
            try:
                if new_val:
                    datetime.strptime(new_val, "%d.%m.%Y")
                return True
            except ValueError:
                return False
        
        reg = self.doc_window.register(validate_date)
        self.doc_date_entry.config(validate="key",
                                 validatecommand=(reg, '%P'))

    def load_documents_list(self):
        """Ładuje listę dokumentów dla wybranego wykazu"""
        for item in self.docs_treeview.get_children():
            self.docs_treeview.delete(item)
            
        if not self.current_doc_list:
            return
        
        self.c.execute('''SELECT d.id_pozycji, wp.nazwa, d.data_dodania, d.opis 
                        FROM dokumenty d
                        LEFT JOIN wykazy_pozycje wp ON d.id_wykazu = wp.id_wykazu AND d.id_pozycji = wp.pozycja_nr
                        WHERE d.id_wykazu=? ORDER BY d.id_pozycji''', 
                      (self.current_doc_list,))

        for doc in self.c.fetchall():
            # Formatuj datę do czytelnej postaci
            try:
                data = datetime.strptime(doc[2], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
            except:
                data = doc[2]
            
            self.docs_treeview.insert("", tk.END, 
                                    values=(doc[0], doc[1], data, doc[3]))
    
    def load_docs_lists(self):
        """Ładuje listę wykazów w sekcji Kwity z prawidłowym statusem"""
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)
            
        query = '''SELECT 
                    w.id,
                    w.numer_rsd,
                    w.numer_wykazu,
                    CASE 
                        WHEN w.data_wykazu IS NULL THEN ''
                        WHEN length(w.data_wykazu) = 10 AND 
                             substr(w.data_wykazu, 5, 1) = '-' AND 
                             substr(w.data_wykazu, 8, 1) = '-' THEN strftime('%d.%m.%Y', w.data_wykazu)
                        WHEN length(w.data_wykazu) = 10 AND 
                             substr(w.data_wykazu, 3, 1) = '.' AND 
                             substr(w.data_wykazu, 6, 1) = '.' THEN w.data_wykazu
                        ELSE ''
                    END as formatted_date,
                    CASE WHEN w.status = 'Rozliczony' THEN 'Rozliczony' ELSE 'Na stanie' END as status_wykazu,
                    COUNT(wp.id) as liczba_pozycji
                  FROM wykazy w
                  LEFT JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                  GROUP BY w.id
                  ORDER BY w.data_wykazu DESC'''
        
        self.c.execute(query)
        
        for row in self.c.fetchall():
            self.docs_tree.insert("", tk.END, 
                                values=(row[1], row[2], row[5], row[3], row[4]),
                                iid=row[0])

    def show_list_details(self):
        """Wyświetla szczegóły wybranego wykazu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz wykaz z listy")
            return
        
        list_id = selected[0]  # Używamy iid które jest ID wykazu
        
        # Pobierz dane wykazu
        self.c.execute('''SELECT 
                        w.numer_rsd,
                        w.numer_wykazu,
                        w.data_wykazu,
                        w.data_utworzenia,
                        w.status,
                        w.uwagi
                      FROM wykazy w
                      WHERE w.id = ?''', (list_id,))
        wykaz = self.c.fetchone()
        
        # Pobierz pozycje wykazu
        self.c.execute('''SELECT 
                        wp.pozycja_nr,
                        wp.nazwa,
                        wp.ilosc,
                        wp.jednostka,
                        wp.status
                      FROM wykazy_pozycje wp
                      WHERE wp.id_wykazu = ?
                      ORDER BY wp.pozycja_nr''', (list_id,))
        pozycje = self.c.fetchall()
        
        # Okno szczegółów
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Szczegóły wykazu {wykaz[1]}")
        details_window.geometry("800x600")
        
        # Nagłówek wykazu
        header_frame = ttk.Frame(details_window, padding=10)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=f"Numer RSD: {wykaz[0]}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Numer wykazu: {wykaz[1]}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Data wykazu: {wykaz[2]}").pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Data utworzenia: {wykaz[3]}").pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Status: {wykaz[4]}").pack(anchor=tk.W)
        if wykaz[5]:
            ttk.Label(header_frame, text=f"Uwagi: {wykaz[5]}").pack(anchor=tk.W)
        
        # Tabela pozycji
        tree_frame = ttk.Frame(details_window)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, 
                           columns=("lp", "nazwa", "ilosc", "jednostka", "status"), 
                           show="headings")
        tree.heading("lp", text="L.p.")
        tree.heading("nazwa", text="Nazwa przedmiotu")
        tree.heading("ilosc", text="Ilość")
        tree.heading("jednostka", text="Jednostka")
        tree.heading("status", text="Status")
        
        tree.column("lp", width=50, anchor=tk.CENTER)
        tree.column("nazwa", width=300)
        tree.column("ilosc", width=80, anchor=tk.CENTER)
        tree.column("jednostka", width=80, anchor=tk.CENTER)
        tree.column("status", width=100, anchor=tk.CENTER)
        
        for pozycja in pozycje:
            tree.insert("", tk.END, values=pozycja)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)
        
        # Przycisk zamknij
        ttk.Button(details_window, text="Zamknij", 
                  command=details_window.destroy).pack(pady=10)

    def add_document_dialog(self):
        """Wyświetla formularz dodawania nowego dokumentu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz najpierw wykaz")
            return

        # Pobierz dane z Treeview
        selected_item = self.docs_tree.item(selected[0])
        values = selected_item['values']
        
        if len(values) < 2:
            messagebox.showerror("Błąd", "Nie można odczytać danych wykazu")
            return
        
        numer_rsd = values[0]
        numer_wykazu = values[1]
        wykaz_id = selected[0]

        # Okno dialogowe
        self.doc_window = tk.Toplevel(self.root)
        self.doc_window.title(f"Dodaj dokument do: {numer_rsd} / {numer_wykazu}")
        self.doc_window.geometry("500x450")
        
        # Zapisz ID wykazu jako atrybut instancji
        self.current_doc_list = wykaz_id
        self.selected_file_path = None
        
        # Ramka główna
        main_frame = ttk.Frame(self.doc_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pole Numer RSD - StringVar (pierwszy wiersz)
        self.rsd_var = tk.StringVar(value=numer_rsd)
        ttk.Label(main_frame, text="Numer RSD:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        rsd_entry = ttk.Entry(main_frame, textvariable=self.rsd_var, state='readonly')
        rsd_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)

        # Pole Numer wykazu - StringVar (drugi wiersz)
        self.wykaz_var = tk.StringVar(value=numer_wykazu)
        ttk.Label(main_frame, text="Numer wykazu:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        wykaz_entry = ttk.Entry(main_frame, textvariable=self.wykaz_var, state='readonly')
        wykaz_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        # Pole Pozycja w wykazie (trzeci wiersz)
        ttk.Label(main_frame, text="Pozycja w wykazie:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.doc_position = ttk.Combobox(main_frame, state="readonly")
        self.doc_position.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Załaduj pozycje z wykazu
        self._load_positions_for_document()
        
        # Data dokumentu (czwarty wiersz)
        ttk.Label(main_frame, text="Data dokumentu:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.doc_date = ttk.Entry(main_frame)
        self.doc_date.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.doc_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Opis dokumentu (piąty wiersz)
        ttk.Label(main_frame, text="Opis dokumentu:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        self.doc_description = tk.Text(main_frame, height=5, width=40)
        self.doc_description.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Wybór pliku (szósty wiersz)
        ttk.Label(main_frame, text="Załączony plik:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_info_label = ttk.Label(main_frame, text="Brak wybranego pliku", foreground="gray")
        self.file_info_label.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Przyciski (siódmy wiersz)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Wybierz plik", 
                  command=self._select_document_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Zapisz", 
                  command=self.save_document).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Anuluj", 
                  command=self.doc_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Konfiguracja grid
        main_frame.grid_columnconfigure(1, weight=1)  # Rozciąganie drugiej kolumny

    def save_document(self):
        """Zapisuje nowy dokument (kwit) do bazy danych i kopiuje plik do folderu dokumentów"""
        try:
            # Pobierz wartości z formularza
            numer_rsd = self.rsd_var.get()
            numer_wykazu = self.wykaz_var.get()
            pozycja = self.doc_position.get().split(" - ")[0] if self.doc_position.get() else ""
            opis = self.doc_description.get("1.0", tk.END).strip()
            
            # Walidacja podstawowych pól
            if not all([numer_rsd, numer_wykazu, pozycja]):
                messagebox.showwarning("Ostrzeżenie", "Wypełnij wszystkie wymagane pola (RSD, Numer wykazu i Pozycję)")
                return

            # Walidacja daty
            try:
                data_dokumentu = datetime.strptime(self.doc_date.get(), "%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty! Użyj DD.MM.RRRR")
                return

            # Sprawdź czy wybrano plik
            if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
                messagebox.showwarning("Ostrzeżenie", "Wybierz plik do załączenia")
                return

            # Przygotuj strukturę folderów
            docs_dir = os.path.join(self.program_dir, "Dokumenty")
            os.makedirs(docs_dir, exist_ok=True)
            
            safe_rsd = numer_rsd.replace("/", "_").replace("\\", "_")
            rsd_dir = os.path.join(docs_dir, f"RSD_{safe_rsd}")
            os.makedirs(rsd_dir, exist_ok=True)

            # Przygotuj nazwę pliku
            original_filename = os.path.basename(self.selected_file_path)
            file_ext = os.path.splitext(original_filename)[1]
            base_name = f"Wykaz_{numer_wykazu.replace('/', '_')}_poz_{pozycja}"
            
            # Generuj unikalną nazwę pliku
            counter = 1
            new_filename = f"{base_name}{file_ext}"
            new_filepath = os.path.join(rsd_dir, new_filename)
            
            while os.path.exists(new_filepath):
                new_filename = f"{base_name}_{counter}{file_ext}"
                new_filepath = os.path.join(rsd_dir, new_filename)
                counter += 1

            # Skopiuj plik
            shutil.copy2(self.selected_file_path, new_filepath)

            # Zapisz do bazy danych
            self.c.execute('''INSERT INTO dokumenty 
                            (id_wykazu, id_pozycji, nazwa_pliku, sciezka, opis, data_dodania)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (self.current_doc_list, pozycja, new_filename, new_filepath, opis, data_dokumentu))
            self.conn.commit()

            messagebox.showinfo("Sukces", "Dokument został pomyślnie zapisany!")
            self.doc_window.destroy()
            
            # Odśwież listę dokumentów w Treeview
            self.load_documents_list()

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas zapisywania dokumentu:\n{str(e)}")
            if hasattr(self, 'conn'):
                self.conn.rollback()
            
    def load_documents_list(self):
        """Ładuje listę dokumentów dla wybranego wykazu"""
        # Wyczyść obecną listę
        for item in self.docs_treeview.get_children():
            self.docs_treeview.delete(item)
            
        if not hasattr(self, 'current_doc_list') or not self.current_doc_list:
            return
        
        # Pobierz dokumenty z bazy danych
        self.c.execute('''SELECT d.id_pozycji, wp.nazwa, d.data_dodania, d.opis 
                        FROM dokumenty d
                        LEFT JOIN wykazy_pozycje wp ON d.id_wykazu = wp.id_wykazu AND d.id_pozycji = wp.pozycja_nr
                        WHERE d.id_wykazu=? ORDER BY d.id_pozycji''', 
                     (self.current_doc_list,))

        for doc in self.c.fetchall():
            # Formatuj datę do czytelnej postaci
            try:
                data = datetime.strptime(doc[2], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
            except:
                data = doc[2]
            
            self.docs_treeview.insert("", tk.END, 
                                    values=(doc[0], doc[1], data, doc[3]))
            
    def _select_document_file(self):
        """Wybierz plik do załączenia, nie chowając okna dialogowego"""
        # Tymczasowo podnieś okno do góry, aby nie zniknęło
        self.doc_window.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            parent=self.doc_window,  # Ustaw okno jako rodzic
            title="Wybierz dokument do załączenia",
            filetypes=[
                ("Obrazy", "*.jpg *.jpeg *.png"),
                ("PDF", "*.pdf"), 
                ("Dokumenty", "*.doc *.docx"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        # Przywróć normalne zachowanie okna
        self.doc_window.attributes('-topmost', False)
        
        if file_path:
            self.selected_file_path = file_path
            self.file_info_label.config(
                text=os.path.basename(file_path),
                foreground="black"
            )
    
    def add_document(self):
        """Dodaje nowy dokument do wykazu"""
        if not hasattr(self, 'current_doc_list'):
            messagebox.showwarning("Ostrzeżenie", "Wybierz najpierw wykaz")
            return
            
        file_path = filedialog.askopenfilename(
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png"), ("PDF", "*.pdf"), ("Wszystkie pliki", "*.*")],
            title="Wybierz dokument do załączenia"
        )
        
        if not file_path:
            return
            
        # Okno dialogowe do wprowadzenia informacji
        doc_info_window = tk.Toplevel(self.root)
        doc_info_window.title("Informacje o dokumencie")
        
        ttk.Label(doc_info_window, text="Pozycja w wykazie:").grid(row=0, column=0, padx=5, pady=5)
        position_entry = ttk.Entry(doc_info_window)
        position_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(doc_info_window, text="Opis:").grid(row=1, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(doc_info_window)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
    
    def view_document(self):
        """Wyświetla podgląd wybranego dokumentu"""
        selected = self.docs_listbox.curselection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz dokument")
            return
            
        filename = self.docs_listbox.get(selected[0])
        filepath = os.path.join(self.docs_dir, self.current_doc_list, filename)
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Otwórz obraz w nowym oknie
            img_window = tk.Toplevel(self.root)
            img_window.title(f"Podgląd: {filename}")
            
            try:
                img = Image.open(filepath)
                img.thumbnail((800, 800))
                img_tk = ImageTk.PhotoImage(img)
                
                label = ttk.Label(img_window, image=img_tk)
                label.image = img_tk  # Keep reference
                label.pack()
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można otworzyć obrazu:\n{str(e)}")
                
        elif filename.lower().endswith('.pdf'):
            # Otwórz PDF w domyślnej aplikacji
            try:
                os.startfile(filepath)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można otworzyć PDF:\n{str(e)}")
    
    def delete_document(self):
        """Usuwa wybrany dokument z bazy danych i systemu plików"""
        selected = self.docs_treeview.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz dokument z listy")
            return
        
        item = self.docs_treeview.item(selected[0])
        pozycja = item['values'][0]
        
        if not hasattr(self, 'current_doc_list') or not self.current_doc_list:
            messagebox.showwarning("Ostrzeżenie", "Nie wybrano wykazu")
            return
        
        # Pobierz pełne dane dokumentu z bazy
        self.c.execute('''SELECT * FROM dokumenty 
                        WHERE id_wykazu=? AND id_pozycji=?''',
                     (self.current_doc_list, pozycja))
        result = self.c.fetchone()
        
        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono dokumentu w bazie danych")
            return
        
        filepath = result[3]  # indeks 3 to kolumna 'sciezka'
        
        # Potwierdzenie usunięcia
        confirm = messagebox.askyesno(
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć dokument pozycji {pozycja}?\n"
            f"Plik: {os.path.basename(filepath)}\n\n"
            "Ta operacja jest nieodwracalna!",
            icon='warning'
        )
        
        if not confirm:
            return
        
        try:
            # Rozpocznij transakcję
            self.conn.execute("BEGIN TRANSACTION")
            
            # Zaloguj usunięcie dokumentu
            self.log_change("usunięcie", "dokumenty", before=result)
            
            # Usuń plik jeśli istnieje
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Usuń rekord z bazy danych
            self.c.execute('''DELETE FROM dokumenty 
                            WHERE id_wykazu=? AND id_pozycji=?''',
                         (self.current_doc_list, pozycja))
            
            # Zatwierdź transakcję
            self.conn.commit()
            
            # Odśwież widok
            self.load_documents_list()
            messagebox.showinfo("Sukces", "Dokument został usunięty")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas usuwania:\n{str(e)}")

    def change_history(self):
        """Wyświetla panel historii zmian z mniejszym odstępem od góry"""
        self.clear_content_frame()

        # Główny kontener z mniejszym paddingiem Y (zmienione pady=10 na pady=5)
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=0)  # Zmiana tutaj

        # Ramka filtrów - identyczna jak w "Kwity"
        filter_frame = ttk.LabelFrame(main_frame, text="Filtry", padding=10)
        filter_frame.pack(fill=tk.X, pady=5)
        
        # Filtry wewnątrz ramki
        ttk.Label(filter_frame, text="Typ operacji:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.history_operation_filter = ttk.Combobox(filter_frame, 
                                                   values=["Wszystkie", "Dodanie", "Edycja", "Usunięcie"],
                                                   width=12, state="readonly")
        self.history_operation_filter.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.history_operation_filter.set("Wszystkie")
        
        ttk.Label(filter_frame, text="Tabela:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.history_table_filter = ttk.Combobox(filter_frame, 
                                               values=["Wszystkie", "Wykazy", "Pozycje wykazów", "Dokumenty"],
                                               width=15, state="readonly")
        self.history_table_filter.grid(row=0, column=3, padx=5, sticky=tk.W)
        self.history_table_filter.set("Wszystkie")
        
        ttk.Button(filter_frame, text="Filtruj", command=self.load_history,
                  style='SmallFilter.TButton', width=10).grid(row=0, column=4, padx=5)

        # Tabela z historią zmian
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        columns = [
            ("Data zmiany", 150),
            ("Typ operacji", 100),
            ("Tabela", 120),
            ("Numer RSD", 120),
            ("Numer wykazu", 120),
            ("Szczegóły", 400)
        ]
        
        self.history_tree = ttk.Treeview(tree_frame, 
                                       columns=[col[0] for col in columns],
                                       show="headings",
                                       height=25)
        
        for col in columns:
            self.history_tree.heading(col[0], text=col[0])
            anchor = tk.CENTER if col[0] in ("Typ operacji", "Tabela") else tk.W
            self.history_tree.column(col[0], width=col[1], anchor=anchor)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(expand=True, fill=tk.BOTH)

        # Przyciski akcji
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Odśwież", command=self.load_history,
                  style='SmallFilter.TButton', width=10).pack(side=tk.LEFT, padx=5)
        
        # Ładowanie danych
        self.load_history()

    def load_history(self):
        """Ładuje historię zmian z uwzględnieniem filtrów i nowych kolumn"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        query = '''SELECT 
                    strftime('%d.%m.%Y %H:%M', data_zmiany) as data,
                    typ_operacji,
                    tabela,
                    COALESCE(numer_rsd, '') as numer_rsd,
                    COALESCE(numer_wykazu, '') as numer_wykazu,
                    szczegoly
                  FROM historia_zmian'''
        
        params = []
        where_clauses = []
        
        operation = self.history_operation_filter.get()
        if operation != "Wszystkie":
            where_clauses.append("typ_operacji = ?")
            params.append(operation)
        
        table = self.history_table_filter.get()
        if table != "Wszystkie":
            # Mapowanie czytelnych nazw z powrotem na nazwy tabel
            table_mapping = {
                "Wykazy": "wykazy",
                "Pozycje wykazów": "wykazy_pozycje",
                "Dokumenty": "dokumenty"
            }
            where_clauses.append("tabela = ?")
            params.append(table_mapping.get(table, table))
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY data_zmiany DESC"
        
        self.c.execute(query, params)
        
        for row in self.c.fetchall():
            # Formatowanie typu operacji dla lepszej czytelności
            operation_display = {
                "dodanie": "Dodanie",
                "edycja": "Edycja",
                "usunięcie": "Usunięcie"
            }.get(row[1], row[1])
            
            self.history_tree.insert("", tk.END, values=(
                row[0],  # Data
                operation_display,  # Typ operacji
                row[2],  # Tabela
                row[3],  # Numer RSD
                row[4],  # Numer wykazu
                row[5]   # Szczegóły
            ))

    def format_history_details(self, operation, before_data):
        """Formatuje szczegóły zmian w czytelnej formie"""
        try:
            if not before_data:
                return "Brak danych"
            
            data = json.loads(before_data)
            
            if operation == "usunięcie":
                if isinstance(data, dict):
                    return f"Usunięto: {data.get('numer_rsd', '')}/{data.get('numer_wykazu', '')}"
                return f"Usunięto obiekt"
            
            elif operation == "dodanie":
                if isinstance(data, dict):
                    return f"Dodano: {data.get('nazwa', '')}"
                return f"Dodano nowy obiekt"
            
            else:  # edycja
                if isinstance(data, dict):
                    changes = []
                    for key, value in data.items():
                        if isinstance(value, dict) and 'old' in value and 'new' in value:
                            changes.append(f"{key}: {value['old']} → {value['new']}")
                    return "\n".join(changes) if changes else "Zmodyfikowano obiekt"
                return "Zmodyfikowano obiekt"
        
        except json.JSONDecodeError:
            return "Błąd formatowania danych"

    def show_deleted_items(self):
        """Pokazuje tylko usunięte elementy"""
        self.history_operation_filter.set("usunięcie")
        self.load_history()

    def log_change(self, operation, table, object_id=None, before=None, after=None):
        """Zapisuje zmianę w historii z nowym formatem"""
        try:
            # Przygotuj czytelne nazwy tabel
            table_names = {
                'wykazy': 'Wykazy',
                'wykazy_pozycje': 'Pozycje wykazów',
                'dokumenty': 'Dokumenty'
            }
            
            # Przygotuj szczegóły operacji w czytelnej formie
            details = ""
            numer_rsd = ""
            numer_wykazu = ""
            
            if operation == "edycja":
                if table == 'wykazy':
                    if 'status' in (before or {}):
                        details = f"Zmieniono status wykazu: {before.get('status')} → {after.get('status')}"
                    else:
                        details = "Zmodyfikowano dane wykazu"
                    numer_rsd = after.get('numer_rsd', before.get('numer_rsd', ''))
                    numer_wykazu = after.get('numer_wykazu', before.get('numer_wykazu', ''))
                
                elif table == 'wykazy_pozycje':
                    if 'status' in (before or {}):
                        details = f"Zmieniono status przedmiotu: {before.get('status')} → {after.get('status')}"
                    else:
                        details = "Zmodyfikowano dane przedmiotu"
                    
                    # Pobierz numer RSD i wykazu dla pozycji
                    if object_id:
                        self.c.execute('''SELECT w.numer_rsd, w.numer_wykazu 
                                       FROM wykazy w
                                       JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                                       WHERE wp.id = ?''', (object_id,))
                        result = self.c.fetchone()
                        if result:
                            numer_rsd, numer_wykazu = result
            
            elif operation == "dodanie":
                if table == 'wykazy':
                    details = "Dodano nowy wykaz"
                    numer_rsd = after.get('numer_rsd', '')
                    numer_wykazu = after.get('numer_wykazu', '')
                elif table == 'wykazy_pozycje':
                    details = "Dodano nową pozycję"
                    if object_id:
                        self.c.execute('''SELECT w.numer_rsd, w.numer_wykazu 
                                       FROM wykazy w
                                       JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                                       WHERE wp.id = ?''', (object_id,))
                        result = self.c.fetchone()
                        if result:
                            numer_rsd, numer_wykazu = result
            
            elif operation == "usunięcie":
                if table == 'wykazy':
                    details = "Usunięto cały wykaz"
                    numer_rsd = before.get('numer_rsd', '')
                    numer_wykazu = before.get('numer_wykazu', '')
                elif table == 'wykazy_pozycje':
                    details = "Usunięto pozycję z wykazu"
                    numer_rsd = before.get('numer_rsd', '')
                    numer_wykazu = before.get('numer_wykazu', '')
            
            # Wstaw rekord do historii
            self.c.execute('''INSERT INTO historia_zmian 
                            (typ_operacji, tabela, numer_rsd, numer_wykazu, szczegoly)
                            VALUES (?, ?, ?, ?, ?)''',
                          (operation, table_names.get(table, table), 
                           numer_rsd, numer_wykazu, details))
            self.conn.commit()
            
        except Exception as e:
            print(f"Błąd podczas logowania zmiany: {str(e)}")
            self.conn.rollback()
    
    def show_low_stock_report(self):
        """Pokazuje raport produktów niskostanowych"""
        self.c.execute('''SELECT id, nazwa, ilosc, min_ilosc, lokalizacja, cena 
                       FROM produkty 
                       WHERE ilosc <= min_ilosc 
                       ORDER BY ilosc''')
        products = self.c.fetchall()
        
        # Wyczyść poprzednie wyniki
        for item in self.report_results.get_children():
            self.report_results.delete(item)
        
        # Dodaj nowe wyniki
        for product in products:
            status = "BRAK" if product[2] == 0 else "NISKI STAN"
            value = product[2] * product[5]
            self.report_results.insert("", tk.END, 
                                     values=(product[0], product[1], product[2], product[3], 
                                            status, product[4], f"{product[5]:.2f}", f"{value:.2f}"))
    
    def show_inventory_value(self):
        """Pokazuje raport wartości magazynu"""
        self.c.execute('''SELECT id, nazwa, ilosc, min_ilosc, lokalizacja, cena 
                       FROM produkty 
                       ORDER BY lokalizacja, nazwa''')
        products = self.c.fetchall()
        
        # Wyczyść poprzednie wyniki
        for item in self.report_results.get_children():
            self.report_results.delete(item)
        
        # Dodaj nowe wyniki
        total_value = 0
        for product in products:
            value = product[2] * product[5]
            total_value += value
            status = "OK"
            if product[2] <= product[3]:
                status = "NISKI STAN" if product[2] > 0 else "BRAK"
            
            self.report_results.insert("", tk.END, 
                                     values=(product[0], product[1], product[2], product[3], 
                                            status, product[4], f"{product[5]:.2f}", f"{value:.2f}"))
        
        # Dodaj podsumowanie
        self.report_results.insert("", tk.END, 
                                 values=("", "RAZEM:", "", "", "", "", "", f"{total_value:.2f}"))
    
    def show_lists_history(self):
        """Pokazuje historię wykazów"""
        self.c.execute('''SELECT w.id, w.numer_rsd, w.numer_wykazu, w.data_wykazu, 
                        COUNT(wp.id), w.status
                      FROM wykazy w
                      LEFT JOIN wykazy_pozycje wp ON w.id = wp.id_wykazu
                      GROUP BY w.id
                      ORDER BY w.data_wykazu DESC''')
        lists = self.c.fetchall()
        
        # Wyczyść poprzednie wyniki
        for item in self.report_results.get_children():
            self.report_results.delete(item)
        
        # Zmień kolumny dla tego raportu
        self.report_results['columns'] = ("ID", "Numer RSD", "Numer Wykazu", "Data wykazu", "Liczba pozycji", "Status")
        for col in self.report_results['columns']:
            self.report_results.heading(col, text=col)
        
        self.report_results.column("ID", width=50, anchor=tk.CENTER)
        self.report_results.column("Numer RSD", width=120)
        self.report_results.column("Numer Wykazu", width=120)
        self.report_results.column("Data wykazu", width=100, anchor=tk.CENTER)
        self.report_results.column("Liczba pozycji", width=100, anchor=tk.CENTER)
        self.report_results.column("Status", width=100, anchor=tk.CENTER)
        
        # Dodaj dane
        for list_item in lists:
            self.report_results.insert("", tk.END, values=list_item)
    
    def export_report(self):
        """Eksportuje aktualny raport do pliku CSV"""
        try:
            items = []
            for item in self.report_results.get_children():
                items.append(self.report_results.item(item)['values'])
            
            if not items:
                messagebox.showwarning("Brak danych", "Brak danych do eksportu")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Pliki CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
                initialdir=self.evidence_dir,
                title="Zapisz raport"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                
                # Nagłówki kolumn
                writer.writerow(self.report_results['columns'])
                
                # Dane
                writer.writerows(items)
            
            messagebox.showinfo("Sukces", f"Raport został wyeksportowany do pliku:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas eksportu:\n{str(e)}")

    def change_evidence_path(self):
        """Zmienia ścieżkę do folderu z dowodami"""
        new_path = filedialog.askdirectory(
            initialdir=self.evidence_dir,
            title="Wybierz folder dla dowodów rzeczowych"
        )
        
        if new_path:
            self.evidence_path.set(new_path)
            self.evidence_dir = new_path
            self.save_config()
            messagebox.showinfo("Sukces", f"Ścieżka do dowodów została zmieniona na:\n{new_path}")

    def load_backup_status(self):
        """Ładuje status kopii zapasowych"""
        for item in self.backup_treeview.get_children():
            self.backup_treeview.delete(item)
        
        current_year = datetime.now().year
        backup_files = os.listdir(self.backup_dir) if os.path.exists(self.backup_dir) else []

        for month in range(1, 13):
            month_name = calendar.month_name[month]
            status = "Brak"

            for file in backup_files:
                if f"magazyn_backup_{current_year}{month:02d}" in file:
                    status = "Utworzono"
                    break
            
            self.backup_treeview.insert("", tk.END, values=(month_name, status))

    def export_database_to_csv(self):
        """Eksportuje bazę danych do pliku CSV"""
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.c.fetchall()

        if not tables:
            messagebox.showwarning("Brak danych", "Brak tabel w bazie danych do eksportu.")
            return

        export_dir = filedialog.askdirectory(
            title="Wybierz folder do zapisu plików CSV"
        )

        if not export_dir:
            return

        try:
            for table_name in [t[0] for t in tables]:
                self.c.execute(f"SELECT * FROM {table_name}")
                rows = self.c.fetchall()
                if not rows:
                    continue

                csv_path = os.path.join(export_dir, f"{table_name}.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow([description[0] for description in self.c.description])
                    writer.writerows(rows)
            
            messagebox.showinfo("Sukces", f"Wszystkie tabele zostały wyeksportowane do folderu:\n{export_dir}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas eksportu:\n{str(e)}")

    def backup_database(self):
        """Tworzy kopię zapasową bazy danych"""
        backup_dir = os.path.join(self.program_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"magazyn_backup_{timestamp}.db")
        
        try:
            self.conn.close()
            shutil.copyfile(self.db_path, backup_path)
            self.conn = sqlite3.connect(self.db_path)
            self.c = self.conn.cursor()
            
            messagebox.showinfo("Kopia zapasowa", f"Kopia zapasowa bazy danych została utworzona pomyślnie:\n{backup_path}")
            self.load_backup_status()
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas tworzenia kopii zapasowej:\n{str(e)}")
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.c = self.conn.cursor()
            except:
                pass

    def load_backup_status(self):
        """Ładuje status kopii zapasowych z informacjami o dacie i rozmiarze"""
        # Wyczyść istniejące wpisy
        for item in self.backup_treeview.get_children():
            self.backup_treeview.delete(item)
        
        backup_dir = os.path.join(self.program_dir, "backup")
        if not os.path.exists(backup_dir):
            return
        
        # Znajdź wszystkie pliki backupów
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("magazyn_backup_") and filename.endswith(".db"):
                file_path = os.path.join(backup_dir, filename)
                if os.path.isfile(file_path):
                    # Pobierz czas utworzenia i rozmiar pliku
                    created_time = os.path.getctime(file_path)
                    file_size = os.path.getsize(file_path)
                    backup_files.append((filename, created_time, file_size))
        
        # Posortuj od najnowszych do najstarszych
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Dodaj do treeview
        for filename, created_time, file_size in backup_files:
            # Formatuj datę i czas
            dt = datetime.fromtimestamp(created_time)
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Formatuj rozmiar pliku
            size_mb = file_size / (1024 * 1024)
            size_str = f"rozmiar: {size_mb:.1f} MB"
            
            # Wyodrębnij timestamp z nazwy pliku dla dodatkowej informacji
            if "_" in filename and "." in filename:
                try:
                    timestamp_part = filename.split("_")[2].split(".")[0]
                    status_str = f"utworzono, {size_str}"
                except:
                    status_str = f"utworzono, {size_str}"
            else:
                status_str = f"utworzono, {size_str}"
            
            self.backup_treeview.insert("", tk.END, values=(date_str, status_str))

    def reset_settings(self):
        """Przywraca domyślne ustawienia"""
        if messagebox.askyesno("Potwierdzenie", 
                              "Czy na pewno chcesz przywrócić domyślne ustawienia?\n"
                              "Spowoduje to powrót do domyślnych ścieżek."):
            self.db_path = self.default_db_path
            self.evidence_dir = os.path.join(self.program_dir, "Dowody rzeczowe")
            
            # Utwórz folder jeśli nie istnieje
            os.makedirs(self.evidence_dir, exist_ok=True)
            
            self.save_config()
            
            if self.conn:
                self.conn.close()
            self.connect_db()
            
            messagebox.showinfo("Sukces", "Przywrócono domyślne ustawienia.")
            self.settings()  # Odśwież widok ustawienia
    
    def select_db_path(self):
        """Pozwala użytkownikowi wybrać nową lokalizację bazy danych"""
        # Domyślnie pokazuj folder programu
        initial_dir = os.path.dirname(self.db_path) if self.db_path else self.program_dir
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Baza danych SQLite", "*.db")],
            initialdir=initial_dir,
            title="Wybierz lokalizację bazy danych",
            initialfile=os.path.basename(self.db_path) if self.db_path else "magazyn.db"
        )
        
        if file_path:
            self.db_path_entry.delete(0, tk.END)
            self.db_path_entry.insert(0, file_path)
    
    def save_db_path_change(self):
        """Zapisuje zmianę ścieżki bazy danych"""
        new_db_path = self.db_path_entry.get().strip()
        
        if not new_db_path:
            messagebox.showerror("Błąd", "Ścieżka do bazy danych nie może być pusta!")
            return
        
        if not new_db_path.endswith('.db'):
            new_db_path += '.db'
        
        # Sprawdź czy ścieżka jest w folderze programu
        if not os.path.dirname(new_db_path):  # Jeśli tylko nazwa pliku
            new_db_path = os.path.join(self.program_dir, new_db_path)
        
        # Utwórz folder jeśli nie istnieje
        os.makedirs(os.path.dirname(new_db_path), exist_ok=True)
        
        try:
            # Zamknij obecne połączenie
            if self.conn:
                self.conn.close()
            
            # Jeśli baza już istnieje w nowej lokalizacji, skopiuj dane
            if os.path.exists(self.db_path) and self.db_path != new_db_path:
                shutil.copy2(self.db_path, new_db_path)
            
            # Uaktualnij ścieżkę i połącz z nową bazą
            self.db_path = new_db_path
            self.connect_db()
            
            # Zapisz konfigurację
            self.save_config()
            
            messagebox.showinfo("Sukces", f"Ścieżka bazy danych została zmieniona na:\n{new_db_path}")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zmienić ścieżki bazy:\n{str(e)}")
            # Przywróć poprzednie połączenie
            try:
                self.connect_db()
            except:
                pass

    def save_evidence_path(self):
        """Zapisuje zmianę ścieżki folderu dowodów"""
        new_evidence_path = self.evidence_path.get()
        
        if not os.path.isdir(new_evidence_path):
            messagebox.showerror("Błąd", "Wybrana ścieżka nie istnieje!")
            return
        
        self.evidence_dir = new_evidence_path
        self.save_config()
        messagebox.showinfo("Sukces", f"Ścieżka do dowodów została zapisana:\n{new_evidence_path}")

    def settings(self):
        self.clear_content_frame()

        # Ramka dla ścieżki bazy danych
        db_frame = ttk.LabelFrame(self.content_frame, text="Ustawienia bazy danych", padding=10)
        db_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(db_frame, text="Ścieżka do bazy danych:").pack(side=tk.LEFT, padx=5)
        self.db_path_entry = ttk.Entry(db_frame, width=60)
        self.db_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.db_path_entry.insert(0, self.db_path)
        
        ttk.Button(db_frame, text="Zmień", command=self.select_db_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(db_frame, text="Zapisz", command=self.save_db_path_change).pack(side=tk.LEFT, padx=5)

        # Ramka dla ścieżki dowodów
        evidence_frame = ttk.LabelFrame(self.content_frame, text="Ścieżka folderu dowodów", padding=10)
        evidence_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(evidence_frame, text="Bieżąca ścieżka:").pack(side=tk.LEFT, padx=5)
        self.evidence_path = tk.StringVar(value=self.evidence_dir)
        evidence_entry = ttk.Entry(evidence_frame, textvariable=self.evidence_path, width=60)
        evidence_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(evidence_frame, text="Zmień", command=self.change_evidence_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(evidence_frame, text="Zapisz", command=self.save_evidence_path).pack(side=tk.LEFT, padx=5)

        # Przyciski dodatkowe - UŁOŻONE POZIOMO
        btn_frame = ttk.Frame(self.content_frame, padding=10)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Eksportuj bazę do CSV", command=self.export_database_to_csv).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Utwórz kopię zapasową", command=self.backup_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Przywróć domyślne ustawienia", command=self.reset_settings).pack(side=tk.LEFT, padx=5, pady=5)

        # Tabela kopii zapasowych - ZMIENIONE NAZWY KOLUMN I DANE
        backup_frame = ttk.LabelFrame(self.content_frame, text="Kopie zapasowe", padding=10)
        backup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Data utworzenia kopii", "Status")
        self.backup_treeview = ttk.Treeview(backup_frame, columns=columns, show="headings")
        
        # Ustawienie szerokości kolumn
        self.backup_treeview.column("Data utworzenia kopii", width=200, anchor=tk.CENTER)
        self.backup_treeview.column("Status", width=250, anchor=tk.CENTER)
        
        for col in columns:
            self.backup_treeview.heading(col, text=col)

        # Dodaj pasek przewijania
        scrollbar = ttk.Scrollbar(backup_frame, orient=tk.VERTICAL, command=self.backup_treeview.yview)
        self.backup_treeview.configure(yscrollcommand=scrollbar.set)
        
        self.backup_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_backup_status()

    def on_close(self):
        """Zamykanie aplikacji"""
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
