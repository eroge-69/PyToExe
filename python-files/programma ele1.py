import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkFont
import csv
import json
import os
import shutil
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import threading
import time
import webbrowser
from pathlib import Path
import logging
import sys

# --- Import opzionali (per esportazione) ---
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('servizi_clienti.log', encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Costanti globali
VERSIONE = "2.0.0"
BACKUP_INTERVAL = 300  # 5 minuti
MAX_LOG_ENTRIES = 10000

# ===================================================================
# CLASSE PER BACKUP AUTOMATICO
# ===================================================================
class BackupManager:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.backup_folder = os.path.join(data_folder, "backups")
        self.max_backups = 10
        os.makedirs(self.backup_folder, exist_ok=True)
        
    def create_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_folder, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            config_file = os.path.join(self.data_folder, "clienti_config.json")
            log_file = os.path.join(self.data_folder, "registro_attivita.json")
            
            if os.path.exists(config_file): shutil.copy2(config_file, backup_path)
            if os.path.exists(log_file): shutil.copy2(log_file, backup_path)
                
            self._cleanup_old_backups()
            logger.info(f"Backup creato: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Errore durante il backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        try:
            backups = sorted([os.path.join(self.backup_folder, d) for d in os.listdir(self.backup_folder) if os.path.isdir(os.path.join(self.backup_folder, d))],
                             key=os.path.getmtime, reverse=True)
            for old_backup in backups[self.max_backups:]:
                shutil.rmtree(old_backup)
                logger.info(f"Backup rimosso: {old_backup}")
        except Exception as e:
            logger.error(f"Errore pulizia backup: {e}")

# ===================================================================
# CLASSE PER STATISTICHE
# ===================================================================
class StatisticsManager:
    def __init__(self, data_by_category, prices):
        self.data_by_category = data_by_category
        self.prices = prices
        
    def get_total_revenue(self):
        total = 0
        service_names = list(self.prices.keys())
        for category_data in self.data_by_category.values():
            for client in category_data:
                client_values = client.get('values', [])
                for i, count in enumerate(client_values):
                    if i < len(service_names):
                        service_name = service_names[i]
                        total += count * self.prices.get(service_name, 0)
        return total

    def get_category_stats(self):
        stats = {}
        service_names = list(self.prices.keys())
        for category, clients in self.data_by_category.items():
            revenue = 0
            for client in clients:
                client_values = client.get('values', [])
                for i, count in enumerate(client_values):
                     if i < len(service_names):
                        service_name = service_names[i]
                        revenue += count * self.prices.get(service_name, 0)
            stats[category] = {'client_count': len(clients), 'revenue': revenue}
        return stats

# ===================================================================
# CLASSE PRINCIPALE
# ===================================================================
class ServiziClientiManager:
    def __init__(self, root):
        self.root = root
        self.base_title = f"Servizi Clienti Manager v{VERSIONE}"
        self.root.title(self.base_title)
        
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        width = 1800 if screen_width >= 1920 else int(screen_width * 0.9)
        height = 1000 if screen_height >= 1080 else int(screen_height * 0.9)
        self.root.geometry(f"{width}x{height}+{(screen_width-width)//2}+{(screen_height-height)//2}")
        self.root.minsize(1200, 800)
        
        self.dark_mode = False
        self.data_folder = os.path.join(os.path.expanduser('~'), 'Documents', 'ServiziClientiManagerData')
        self.config_file = os.path.join(self.data_folder, "clienti_config.json")
        self.log_file = os.path.join(self.data_folder, "registro_attivita.json")
        
        self.is_log_view_active = False
        self.editing_item = None
        self.last_backup_time = None
        self.data_is_dirty = False

        self.setup_professional_theme()
        
        try:
            self.load_config()
            self.load_log()
            self.backup_manager = BackupManager(self.data_folder)
            self.stats_manager = StatisticsManager(self.data_by_category, self.prices)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore fatale in inizializzazione: {e}")
            logger.error(f"Errore fatale in inizializzazione: {e}")
            self.root.destroy()
            return

        self.create_professional_interface()
        self.start_backup_thread()
        self.setup_keyboard_shortcuts()
        
        def on_closing():
            if self.data_is_dirty:
                response = messagebox.askyesnocancel("Uscita", "Ci sono modifiche non salvate. Vuoi salvarle prima di uscire?", icon='warning')
                if response is True: # Yes
                    self.save_all_data()
                    root.destroy()
                elif response is False: # No
                    root.destroy()
                else: # Cancel
                    return
            else:
                root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.update_statistics()
        self.update_backup_info()

    def set_dirty(self, is_dirty=True):
        if is_dirty == self.data_is_dirty:
            return
        
        self.data_is_dirty = is_dirty
        if is_dirty:
            self.root.title(f"{self.base_title} *")
        else:
            self.root.title(self.base_title)

    def setup_professional_theme(self):
        colors_light = {'primary': '#0078D4', 'primary_dark': '#005A9E', 'surface': '#FFFFFF', 'background': '#F8F9FA',
                        'surface_alt': '#F3F4F6', 'surface_elevated': '#FFFFFF', 'text': '#202124', 'text_secondary': '#5F6368',
                        'success': '#107C10', 'accent': '#D83B01', 'border': '#DADCE0'}
        colors_dark = {'primary': '#007ACC', 'primary_dark': '#005A9E', 'surface': '#252526', 'background': '#1E1E1E',
                       'surface_alt': '#313136', 'surface_elevated': '#2D2D30', 'text': '#CCCCCC', 'text_secondary': '#9CDCFE',
                       'success': '#4CAF50', 'accent': '#FF6B35', 'border': '#454545'}
        self.colors = colors_dark if self.dark_mode else colors_light
        
        self.root.configure(bg=self.colors['background'])
        self.fonts = {'title': ('Segoe UI', 22, 'bold'), 'body': ('Segoe UI', 12), 'subheading': ('Segoe UI', 14, 'bold'),
                      'button': ('Segoe UI Semibold', 12), 'caption': ('Segoe UI', 10)}
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Professional.Treeview", background=self.colors['surface'], foreground=self.colors['text'], 
                        fieldbackground=self.colors['surface'], borderwidth=0, font=self.fonts['body'], rowheight=50)
        style.configure("Professional.Treeview.Heading", font=self.fonts['subheading'], background=self.colors['surface_elevated'],
                        foreground=self.colors['text_secondary'], relief='flat')
        style.map("Professional.Treeview", background=[('selected', self.colors['primary'])])
        style.configure("Log.Professional.Treeview", rowheight=40, font=self.fonts['body'])

    def load_config(self):
        default = {"prices": {"Servizio 1": 10.0}, "categories": ["Default"], "data": {"Default": []}}
        if not os.path.exists(self.config_file):
            self.prices, self.categories, self.data_by_category = default['prices'], default['categories'], default['data']
            return
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.prices = config.get("prices", default['prices'])
        self.categories = config.get("categories", default['categories'])
        self.data_by_category = config.get("data", default['data'])
        self.current_category = self.categories[0] if self.categories else "Default"
        self.service_names = list(self.prices.keys())

    def save_all_data(self):
        try:
            os.makedirs(self.data_folder, exist_ok=True)
            data = {"prices": self.prices, "categories": self.categories, "data": self.data_by_category}
            with open(self.config_file, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
            with open(self.log_file, 'w', encoding='utf-8') as f: json.dump(self.activity_log, f, indent=2, ensure_ascii=False)
            self.set_dirty(False)
            return True
        except Exception as e:
            self.update_status_bar(f"Errore salvataggio: {e}", "accent")
            return False

    def load_log(self):
        self.activity_log = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f: self.activity_log = json.load(f)
            except json.JSONDecodeError: pass

    def create_professional_interface(self):
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_professional_header(main_container)
        self.create_control_bar(main_container)
        self.create_professional_footer(main_container)
        self.create_main_area(main_container)

    def create_professional_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['surface_elevated'], height=120)
        header.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)

        left = tk.Frame(header, bg=header['bg']); left.pack(side=tk.LEFT, padx=40, pady=20)
        
        title_frame = tk.Frame(left, bg=header['bg'])
        title_frame.pack(anchor='w', pady=(0, 10))
        tk.Label(title_frame, text="Servizi Clienti Manager", font=self.fonts['title'], bg=header['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        tk.Label(title_frame, text=f"v{VERSIONE}", font=self.fonts['caption'], bg=header['bg'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=10)

        # Sposto i pulsanti secondari a sinistra
        bottom_buttons = tk.Frame(left, bg=header['bg']); bottom_buttons.pack(anchor='w')
        btn_config = [("⚙️", "Impostazioni", self.open_settings), ("❓", "Aiuto", self.show_help), ("🌙", "Tema", self.toggle_dark_mode)]
        for icon, text, cmd in btn_config:
            self.create_professional_button(bottom_buttons, f"{icon} {text}", cmd, 'secondary').pack(side=tk.LEFT, padx=(0, 8))

        right = tk.Frame(header, bg=header['bg']); right.pack(side=tk.RIGHT, padx=40, pady=30)
        top_buttons = tk.Frame(right, bg=header['bg']); top_buttons.pack(anchor='e')
        self.create_professional_button(top_buttons, "📊 Statistiche", self.show_statistics_dashboard, 'secondary').pack(side=tk.LEFT, padx=(0, 8))
        self.create_professional_button(top_buttons, "💾 SALVA ADESSO", self.manual_save, 'success').pack(side=tk.LEFT)
        
    def create_control_bar(self, parent):
        bar = tk.Frame(parent, bg=self.colors['surface'], height=80)
        bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        bar.pack_propagate(False)

        self.tabs_container = tk.Frame(bar, bg=bar['bg']); self.tabs_container.pack(side=tk.LEFT, padx=30, pady=15)
        self.create_professional_tabs()

        actions = tk.Frame(bar, bg=bar['bg']); actions.pack(side=tk.RIGHT, padx=30, pady=15)
        self.create_professional_button(actions, "📤 Esporta", self.export_data, 'secondary').pack(side=tk.LEFT, padx=(0,8))
        self.create_professional_button(actions, "🗑️ Elimina", self.elimina_cliente, 'secondary').pack(side=tk.LEFT, padx=(0,8))
        self.create_professional_button(actions, "➕ Nuovo", self.add_new_client, 'primary').pack(side=tk.LEFT)

        search_frame = tk.Frame(bar, bg=bar['bg']); search_frame.pack(side=tk.RIGHT, padx=20)
        tk.Label(search_frame, text="Ricerca:", font=self.fonts['body'], bg=bar['bg'], fg=self.colors['text_secondary']).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.fonts['body'], width=25)
        search_entry.pack(side=tk.LEFT, ipady=8, padx=5); search_entry.bind('<KeyRelease>', lambda e: self.refresh_table())
        self.create_professional_button(search_frame, "Avanzata", self.advanced_search, 'secondary').pack(side=tk.LEFT)

    def create_main_area(self, parent):
        self.main_content_frame = tk.Frame(parent, bg=self.colors['surface'])
        self.main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.create_professional_table()

    def create_professional_footer(self, parent):
        footer = tk.Frame(parent, bg=self.colors['surface_elevated'], height=80)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        footer.pack_propagate(False)

        # Left Frame
        left = tk.Frame(footer, bg=footer['bg']); left.pack(side=tk.LEFT, padx=30, pady=10, fill=tk.Y)
        self.status_label = tk.Label(left, text="Pronto", font=self.fonts['body'], bg=footer['bg'], fg=self.colors['success'])
        self.status_label.pack(anchor='w')
        self.backup_label = tk.Label(left, text="Backup...", font=self.fonts['caption'], bg=footer['bg'], fg=self.colors['text_secondary'])
        self.backup_label.pack(anchor='w')

        # Right Frame
        right = tk.Frame(footer, bg=footer['bg']); right.pack(side=tk.RIGHT, padx=30, pady=10, fill=tk.Y)
        self.version_label = tk.Label(right, text=f"Versione: {VERSIONE}", font=self.fonts['body'], bg=footer['bg'], fg=self.colors['text_secondary'])
        self.version_label.pack(anchor='e')
        self.abs_backup_label = tk.Label(right, text="", font=self.fonts['caption'], bg=footer['bg'], fg=self.colors['text_secondary'])
        self.abs_backup_label.pack(anchor='e')

        # Center Frame
        center = tk.Frame(footer, bg=footer['bg']); center.pack(expand=True, fill=tk.BOTH)
        center_content = tk.Frame(center, bg=footer['bg'])
        center_content.pack(anchor='center', expand=True)
        self.revenue_label = tk.Label(center_content, text="€0.00", font=self.fonts['body'], bg=footer['bg'], fg=self.colors['success'])
        self.revenue_label.pack(side=tk.LEFT, padx=20)
        self.clients_total_label = tk.Label(center_content, text="0 clienti", font=self.fonts['body'], bg=footer['bg'], fg=self.colors['primary'])
        self.clients_total_label.pack(side=tk.LEFT, padx=20)
        
    def create_professional_button(self, parent, text, command, style):
        color_map = {'primary': (self.colors['primary'], self.colors['surface']),
                     'secondary': (self.colors['surface_alt'], self.colors['text']),
                     'success': (self.colors['success'], self.colors['surface'])}
        bg, fg = color_map.get(style, (self.colors['surface_alt'], self.colors['text']))
        hover_bg = self.colors['primary_dark'] if style=='primary' else self.colors['border']
        
        btn = tk.Button(parent, text=text, command=command, font=self.fonts['button'], bg=bg, fg=fg, 
                       relief='flat', padx=15, pady=8, cursor='hand2')
        btn.bind("<Enter>", lambda e, b=btn, c=hover_bg: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn
    
    def create_professional_tabs(self):
        for w in self.tabs_container.winfo_children(): w.destroy()
        self.tab_buttons = {}
        for cat in self.categories:
            btn = tk.Button(self.tabs_container, text=cat, command=lambda c=cat: self.switch_to_category_view(c), 
                            font=self.fonts['body'], relief='flat', padx=15, pady=10)
            btn.pack(side=tk.LEFT)
            self.tab_buttons[cat] = btn
        self.log_tab_button = tk.Button(self.tabs_container, text="📜 Registro", command=self.switch_to_log_view,
                                       font=self.fonts['body'], relief='flat', padx=15, pady=10)
        self.log_tab_button.pack(side=tk.LEFT, padx=(10,0))
        self.update_tab_appearance()

    def create_professional_table(self):
        if hasattr(self, 'table_container'): self.table_container.destroy()
        self.table_container = tk.Frame(self.main_content_frame)
        self.table_container.pack(fill=tk.BOTH, expand=True)

        if self.is_log_view_active:
            self.log_sort_by = ('timestamp', False) # (column, reverse_sort)
            self.tree = ttk.Treeview(self.table_container, columns=["Timestamp"], show='tree headings', style="Log.Professional.Treeview")
            self.tree.heading('#0', text='Dettagli Attività', command=lambda: self.sort_log_view('details'))
            self.tree.column('#0', width=800, stretch=tk.YES)
            self.tree.heading('Timestamp', text='Data e Ora', command=lambda: self.sort_log_view('timestamp'))
            self.tree.column('Timestamp', width=150, anchor='center')
            self.tree.bind('<Double-1>', self.on_double_click)
        else:
            cols = ['👤 Cliente'] + self.service_names + ['💰 Totale €']
            self.tree = ttk.Treeview(self.table_container, columns=cols, show='headings', style="Professional.Treeview")
            for col in cols:
                w = 350 if col == cols[0] else 150 if col == cols[-1] else 120
                self.tree.heading(col, text=col)
                self.tree.column(col, width=w, anchor='w' if col == cols[0] else 'e' if col == cols[-1] else 'center')
            
            self.tree.bind('<Double-1>', self.on_double_click)
            self.tree.bind('<ButtonRelease-1>', self.process_click)

        scrollbar = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        search_query = self.search_var.get().lower()

        if self.is_log_view_active:
            self.display_log_data(search_query)
        else:
            clients = [c for c in self.data_by_category.get(self.current_category, []) if search_query in c.get('Cliente', '').lower()]
            for client in clients:
                if len(client.get('values', [])) != len(self.prices): client['values'] = [0] * len(self.prices)
                total = sum(client['values'][i] * price for i, price in enumerate(self.prices.values()))
                values = [client['Cliente']] + client['values'] + [f"€ {total:.2f}"]
                self.tree.insert('', 'end', values=values, tags=(client['id'],))
    
    def sort_log_view(self, column):
        """Ordina la vista del registro quando si clicca sull'intestazione di una colonna."""
        current_col, reverse = self.log_sort_by
        if column == current_col:
            reverse = not reverse
        else:
            reverse = False
        self.log_sort_by = (column, reverse)
        self.refresh_table()

    def display_log_data(self, search_query=""):
        """Mostra i dati del log in modo strutturato, con filtro di ricerca."""
        # Filtra i log se c'è una query di ricerca
        logs_to_display = self.activity_log
        if search_query:
            logs_to_display = [
                entry for entry in self.activity_log
                if search_query in entry.get('client_name', "").lower() or
                   search_query in entry.get('action', '').lower() or
                   search_query in entry.get('service', '').lower()
            ]

        # Ordina i log prima di raggrupparli
        sort_key, reverse = self.log_sort_by
        if sort_key == 'timestamp':
            logs_to_display.sort(key=lambda e: e['timestamp'], reverse=reverse)
        elif sort_key == 'details':
            logs_to_display.sort(key=lambda e: (e.get('client_name', 'z'), e['timestamp']), reverse=reverse)


        processed_logs = self.group_consecutive_updates(list(logs_to_display))

        client_map = {c['id']: c['Cliente'] for cat in self.data_by_category.values() for c in cat}

        logs_by_client_id = defaultdict(list)
        for entry in processed_logs:
            logs_by_client_id[entry.get('client_id')].append(entry)
        
        client_list_for_view = []
        for client_id, entries in logs_by_client_id.items():
            display_name = client_map.get(client_id) or entries[0].get('client_name') or "Cliente Eliminato"
            latest_timestamp = max(e['timestamp'] for e in entries)
            client_list_for_view.append({
                'id': client_id,
                'name': display_name,
                'latest_timestamp': latest_timestamp,
                'entries': entries
            })

        sort_key, reverse = self.log_sort_by
        if sort_key == 'details':
            client_list_for_view.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        elif sort_key == 'timestamp':
            client_list_for_view.sort(key=lambda x: x['latest_timestamp'], reverse=reverse)

        for client_data in client_list_for_view:
            client_node = self.tree.insert('', 'end', text=f"👤 {client_data['name']}", open=bool(search_query))
            
            sorted_entries = sorted(client_data['entries'], key=lambda e: e['timestamp'], reverse=True)
            
            for entry in sorted_entries:
                time_str = datetime.fromisoformat(entry['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
                action = entry.get('action', 'N/A')
                
                if entry.get('is_group', False):
                    details = f"🔄 {entry.get('service', 'N/A')}: da {entry.get('original_value')} a {entry.get('new_value')} ({entry.get('count', 0)} modifiche)"
                    group_node = self.tree.insert(client_node, 'end', text=f"   - {details}", values=(time_str,), open=False)
                    for sub_entry in sorted(entry.get('sub_entries', []), key=lambda e: e['timestamp']):
                        sub_time = datetime.fromisoformat(sub_entry['timestamp']).strftime('%d/%m/%Y %H:%M')
                        sub_details = f"{sub_entry.get('original_value')} -> {sub_entry.get('new_value')}"
                        self.tree.insert(group_node, 'end', text=f"      - {sub_details}", values=(sub_time,))
                else:
                    details = f"{entry.get('service', 'N/A')}: {entry.get('original_value','?')} -> {entry.get('new_value','?')}" if 'Valore' in action else action
                    self.tree.insert(client_node, 'end', text=f"   - {details}", values=(time_str,))

    def group_consecutive_updates(self, logs):
        if not logs:
            return []
        
        # Per il raggruppamento, i log devono essere ordinati dal più vecchio al più nuovo
        logs.sort(key=lambda e: e['timestamp'])
        
        grouped_logs = []
        i = 0
        while i < len(logs):
            current_log = logs[i]
            
            # Controlla solo gli aggiornamenti di valore
            if 'Aggiornamento Valore' in current_log.get('action', ''):
                j = i + 1
                consecutive_sequence = [current_log]
                while (j < len(logs) and
                       'Aggiornamento Valore' in logs[j].get('action', '') and
                       logs[j].get('client_id') == current_log.get('client_id') and
                       logs[j].get('service') == current_log.get('service') and
                       logs[j].get('original_value') == logs[j-1].get('new_value')):
                    consecutive_sequence.append(logs[j])
                    j += 1
                
                if len(consecutive_sequence) > 1:
                    first = consecutive_sequence[0]
                    last = consecutive_sequence[-1]
                    grouped_entry = {
                        'is_group': True,
                        'timestamp': last['timestamp'], # Usa il timestamp del più recente
                        'client_id': first['client_id'],
                        'client_name': first.get('client_name'),
                        'service': first['service'],
                        'action': 'Gruppo di Aggiornamenti',
                        'original_value': first['original_value'],
                        'new_value': last['new_value'],
                        'count': len(consecutive_sequence),
                        'sub_entries': consecutive_sequence # Dal più vecchio al più nuovo
                    }
                    grouped_logs.append(grouped_entry)
                    i = j # Salta i log già raggruppati
                    continue

            # Se non è una sequenza o è un log singolo, aggiungilo normalmente
            grouped_logs.append(current_log)
            i += 1
            
        return grouped_logs

    def update_tab_appearance(self):
        is_log = self.is_log_view_active
        for cat, btn in self.tab_buttons.items():
            active = not is_log and cat == self.current_category
            btn.config(bg=self.colors['primary'] if active else self.colors['surface'], 
                       fg=self.colors['surface'] if active else self.colors['text_secondary'])
        self.log_tab_button.config(bg=self.colors['primary'] if is_log else self.colors['surface'],
                                   fg=self.colors['surface'] if is_log else self.colors['text_secondary'])
    
    def switch_to_category_view(self, category):
        self.is_log_view_active = False
        self.current_category = category
        self.create_professional_table()
        self.update_tab_appearance()

    def switch_to_log_view(self):
        self.is_log_view_active = True
        self.current_category = None
        self.create_professional_table()
        self.update_tab_appearance()
    
    def on_double_click(self, event):
        if self.is_log_view_active:
            item_id = self.tree.identify_row(event.y)
            if item_id: self.tree.item(item_id, open=not self.tree.item(item_id, 'open'))
            return

        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item_id or col != '#1': return
        
        self.editing_item = item_id
        x, y, w, h = self.tree.bbox(item_id, col)
        entry = tk.Entry(self.tree, font=self.fonts['body'])
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, self.tree.item(item_id, 'values')[0])
        entry.focus()
        entry.bind('<Return>', lambda e, i=item_id, en=entry: self.finish_edit(i, en))
        entry.bind('<FocusOut>', lambda e, en=entry: en.destroy())
    
    def finish_edit(self, item_id, entry):
        new_name = entry.get()
        entry.destroy()
        if not new_name: return
        
        client_id = self.tree.item(item_id, 'tags')[0]
        for client in self.data_by_category[self.current_category]:
            if client['id'] == client_id:
                old_name = client['Cliente']
                if old_name != new_name:
                    client['Cliente'] = new_name
                    self.add_log_entry(client['id'], new_name, "Applicazione", f"Cliente rinominato da '{old_name}' a '{new_name}'")
                    self.set_dirty(True)
                break
        self.refresh_table()
        self.update_status_bar(f"Cliente '{old_name}' rinominato in '{new_name}'.", "success")

    def process_click(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item_id or col == '#1' or col == f"#{len(self.prices)+2}": return
        
        col_index = int(col.replace('#','')) - 2
        client_id = self.tree.item(item_id, 'tags')[0]
        
        for client in self.data_by_category[self.current_category]:
            if client.get('id') == client_id:
                if len(client.get('values', [])) != len(self.prices): client['values'] = [0] * len(self.prices)
                
                x, y, w, h = self.tree.bbox(item_id, col)
                service_name = self.service_names[col_index]
                old_value = client['values'][col_index]
                if event.x > x + w / 2:
                    client['values'][col_index] += 1
                else:
                    client['values'][col_index] = max(0, client['values'][col_index] - 1)
                
                new_value = client['values'][col_index]
                if old_value != new_value:
                    self.add_log_entry(client_id, client['Cliente'], service_name, "Aggiornamento Valore", old_value, new_value)
                    self.update_status_bar(f"'{client['Cliente']}': {service_name} aggiornato a {new_value}.", "success")
                    self.set_dirty(True)
                break
        self.refresh_table()
        self.update_statistics()

    def add_new_client(self):
        new_client = {"id": str(uuid.uuid4()), "Cliente": "Nuovo Cliente", "values": [0] * len(self.prices)}
        if self.current_category not in self.data_by_category:
            self.data_by_category[self.current_category] = []
        self.data_by_category[self.current_category].append(new_client)
        self.add_log_entry(new_client['id'], new_client['Cliente'], "Applicazione", f"Nuovo cliente aggiunto in '{self.current_category}'")
        self.set_dirty(True)
        self.refresh_table()
        self.update_statistics()
        self.update_status_bar("Nuovo cliente aggiunto con successo.", "success")

    def elimina_cliente(self):
        selected_items = self.tree.selection()
        if not selected_items: return
        
        client_ids_to_delete = {self.tree.item(item, 'tags')[0] for item in selected_items}
        if messagebox.askyesno("Conferma", f"Eliminare {len(client_ids_to_delete)} clienti? L'azione è irreversibile."):
            
            clients_to_keep = []
            for client in self.data_by_category[self.current_category]:
                if client.get('id') in client_ids_to_delete:
                    self.add_log_entry(client.get('id'), client.get('Cliente'), "Applicazione", f"Cliente '{client.get('Cliente')}' eliminato.")
                else:
                    clients_to_keep.append(client)
            
            self.data_by_category[self.current_category] = clients_to_keep
            self.set_dirty(True)
            self.refresh_table()
            self.update_statistics()
            self.update_status_bar(f"{len(client_ids_to_delete)} cliente/i eliminato/i.", "accent")

    def manual_save(self):
        if self.save_all_data():
            self.update_status_bar("Dati salvati manualmente.", "success")
    
    def toggle_dark_mode(self): 
        self.dark_mode = not self.dark_mode
        self.setup_professional_theme()
        for w in self.root.winfo_children(): w.destroy()
        self.create_professional_interface()

    def show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("Guida - Servizi Clienti Manager")
        help_win.geometry("600x450")
        help_win.configure(bg=self.colors['background'])
        help_win.transient(self.root)
        help_win.grab_set()

        main_frame = tk.Frame(help_win, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(main_frame, text="Guida Rapida", font=self.fonts['title'], bg=self.colors['background'], fg=self.colors['text']).pack(anchor='w', pady=(0,15))

        def add_section(title, content):
            tk.Label(main_frame, text=title, font=self.fonts['subheading'], bg=self.colors['background'], fg=self.colors['primary']).pack(anchor='w', pady=(10,2))
            tk.Label(main_frame, text=content, font=self.fonts['body'], wraplength=550, justify=tk.LEFT, bg=self.colors['background'], fg=self.colors['text']).pack(anchor='w')

        add_section("Interazione Tabella Clienti",
                    "• Doppio click sul nome di un cliente per modificarlo.\n"
                    "• Click sulla metà destra di una cella servizio per incrementare il valore.\n"
                    "• Click sulla metà sinistra di una cella servizio per decrementare il valore.")
        
        add_section("Scorciatoie da Tastiera",
                    "• Ctrl + S: Salva manualmente tutti i dati.\n"
                    "• Ctrl + F: Attiva la barra di ricerca globale.")
        
        add_section("Registro Attività",
                    "La sezione 'Registro' mostra tutte le modifiche effettuate. Usa la barra di ricerca per filtrare le attività per nome cliente, tipo di azione o servizio.")

        self.create_professional_button(main_frame, "OK", help_win.destroy, 'primary').pack(side=tk.BOTTOM, pady=20)


    def open_settings(self):
        self.original_service_order = list(self.prices.keys())
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Impostazioni")
        settings_win.geometry("800x700") # Resized for better fit
        settings_win.configure(bg=self.colors['background'])
        settings_win.transient(self.root)
        settings_win.grab_set()

        def on_close():
            try:
                # Get all (service, price) pairs from the treeview
                service_price_pairs = [self.settings_service_tree.item(i, 'values') for i in self.settings_service_tree.get_children()]
                
                final_order = [str(pair[0]) for pair in service_price_pairs]
                temp_prices = {str(pair[0]): float(pair[1]) for pair in service_price_pairs}

                if final_order != self.original_service_order or temp_prices != self.prices:
                    self.set_dirty(True)

                self.prices = temp_prices
                self.service_names = list(self.prices.keys())
                
                current_categories = self.categories_listbox.get(0, tk.END)
                if list(current_categories) != self.categories:
                    self.categories = list(current_categories)
                    self.set_dirty(True)

                if self.data_is_dirty:
                    self.create_professional_tabs()
                    self.create_professional_table()
                    self.update_statistics()

            except Exception as e:
                logger.error(f"Errore alla chiusura delle impostazioni: {e}")
            finally:
                settings_win.destroy()

        settings_win.protocol("WM_DELETE_WINDOW", on_close)
        
        # --- Main Layout ---
        title_frame = tk.Frame(settings_win, bg=self.colors['background'])
        title_frame.pack(fill=tk.X, padx=20, pady=(10,0))
        tk.Label(title_frame, text="Impostazioni Applicazione", font=self.fonts['title'], bg=self.colors['background'], fg=self.colors['text']).pack(pady=(0, 10), anchor='w')

        bottom_frame = tk.Frame(settings_win, bg=self.colors['background'])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        self.create_professional_button(bottom_frame, "Salva e Chiudi", on_close, 'primary').pack()

        # --- Scrollable Area ---
        canvas = tk.Canvas(settings_win, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20,0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,20))
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # --- Content Cards (in scrollable frame) ---
        cat_card = self.create_card(scrollable_frame, "Gestione Categorie")
        self.create_categories_section(cat_card)

        serv_card = self.create_card(scrollable_frame, "Gestione Servizi e Prezzi")
        self.create_dynamic_prices_section(serv_card)

        data_card = self.create_card(scrollable_frame, "Cartella Dati")
        self.create_data_folder_section(data_card)
        
        maint_card = self.create_card(scrollable_frame, "Manutenzione")
        self.create_maintenance_section(maint_card)


    def create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors['surface'], relief='solid', borderwidth=1, highlightthickness=1, highlightbackground=self.colors['border'])
        card.pack(fill=tk.X, pady=10, expand=True)
        tk.Label(card, text=title, font=self.fonts['subheading'], bg=card['bg'], fg=self.colors['text']).pack(anchor='w', padx=15, pady=(10,5))
        separator = ttk.Separator(card, orient='horizontal')
        separator.pack(fill='x', padx=15, pady=(0, 10))
        content_frame = tk.Frame(card, bg=card['bg'])
        content_frame.pack(fill=tk.X, padx=15, pady=(0,15))
        return content_frame

    def create_categories_section(self, parent):
        list_frame = tk.Frame(parent, bg=parent['bg'])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        self.categories_listbox = tk.Listbox(list_frame, font=self.fonts['body'], bg=self.colors['surface_alt'], relief='flat', height=5)
        self.categories_listbox.pack(fill=tk.BOTH, expand=True)
        for cat in self.categories: self.categories_listbox.insert(tk.END, cat)
        
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        btn_frame.pack(side=tk.LEFT)
        self.create_professional_button(btn_frame, "➕ Aggiungi", self.add_category, 'secondary').pack(fill=tk.X, pady=2)
        self.create_professional_button(btn_frame, "❌ Rimuovi", self.remove_category, 'secondary').pack(fill=tk.X, pady=2)

    def create_dynamic_prices_section(self, parent):
        tree_frame = tk.Frame(parent, bg=parent['bg'])
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        
        self.settings_service_tree = ttk.Treeview(tree_frame, columns=("Servizio", "Prezzo"), show="headings", style="Professional.Treeview")
        self.settings_service_tree.heading("Servizio", text="Nome Servizio")
        self.settings_service_tree.heading("Prezzo", text="Prezzo (€)");
        self.settings_service_tree.column("Servizio", width=250, anchor='w')
        self.settings_service_tree.column("Prezzo", width=100, anchor='e')
        self.settings_service_tree.pack(fill=tk.BOTH, expand=True)
        self.rebuild_price_list()

        btn_frame = tk.Frame(parent, bg=parent['bg'])
        btn_frame.pack(side=tk.LEFT)
        self.create_professional_button(btn_frame, "➕", self.add_service, 'secondary').pack(fill=tk.X, pady=2)
        self.create_professional_button(btn_frame, "❌", self.remove_service, 'secondary').pack(fill=tk.X, pady=2)
        self.create_professional_button(btn_frame, "✏️", self.edit_price_in_tree, 'secondary').pack(fill=tk.X, pady=2)
        self.create_professional_button(btn_frame, "🔼", self.move_service_up, 'secondary').pack(fill=tk.X, pady=2)
        self.create_professional_button(btn_frame, "🔽", self.move_service_down, 'secondary').pack(fill=tk.X, pady=2)

    def create_data_folder_section(self, parent):
        self.data_folder_var = tk.StringVar(value=self.data_folder)
        entry = tk.Entry(parent, textvariable=self.data_folder_var, font=self.fonts['body'], state='readonly', relief='flat', bg=self.colors['surface_alt'])
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0,10))
        self.create_professional_button(parent, "Cambia...", self.change_data_folder, 'secondary').pack(side=tk.LEFT)

    def create_maintenance_section(self, parent):
        self.create_professional_button(parent, "🗑️ Svuota Registro Attività", self.clear_activity_log, 'secondary').pack(anchor='w')

    def clear_activity_log(self):
        if messagebox.askyesno("Conferma Svuotamento", "Sei sicuro di voler cancellare permanentemente tutte le voci dal registro attività? L'azione è irreversibile."):
            if not self.activity_log:
                self.update_status_bar("Il registro attività è già vuoto.", "success")
                return
            self.activity_log.clear()
            self.set_dirty(True)
            self.update_status_bar("Registro attività svuotato. Salvare le modifiche.", "success")
            if self.is_log_view_active:
                self.refresh_table()

    def add_category(self):
        name = simpledialog.askstring("Nuova Categoria", "Nome della nuova categoria:")
        if name and name not in self.categories:
            self.categories.append(name)
            self.data_by_category[name] = []
            self.categories_listbox.insert(tk.END, name)
            self.create_professional_tabs()

    def remove_category(self):
        selected = self.categories_listbox.curselection()
        if not selected: return
        name = self.categories_listbox.get(selected[0])
        if messagebox.askyesno("Conferma", f"Rimuovere la categoria '{name}' e tutti i suoi clienti? L'operazione non è reversibile."):
            self.categories.remove(name)
            del self.data_by_category[name]
            self.categories_listbox.delete(selected[0])
            if name == self.current_category:
                self.current_category = self.categories[0] if self.categories else None
            self.create_professional_tabs()
    
    def change_data_folder(self):
        new_folder = filedialog.askdirectory(title="Seleziona nuova cartella dati", initialdir=self.data_folder)
        if new_folder and os.path.isdir(new_folder):
            if messagebox.askyesno("Conferma Spostamento", "Spostare i file di dati attuali nella nuova cartella?"):
                self.set_data_folder(new_folder, move_data=True)
            else:
                self.set_data_folder(new_folder, move_data=False)

    def set_data_folder(self, new_folder, move_data=True):
        try:
            old_folder = self.data_folder
            new_config_path = os.path.join(new_folder, "clienti_config.json")
            new_log_path = os.path.join(new_folder, "registro_attivita.json")

            if move_data:
                # Prima salva i dati correnti per assicurarsi che siano aggiornati
                self.save_all_data()
                if os.path.exists(self.config_file): shutil.copy2(self.config_file, new_config_path)
                if os.path.exists(self.log_file): shutil.copy2(self.log_file, new_log_path)
                # Pulisce i vecchi file solo se la copia ha avuto successo
                if os.path.exists(self.config_file): os.remove(self.config_file)
                if os.path.exists(self.log_file): os.remove(self.log_file)
            
            self.data_folder = new_folder
            self.data_folder_var.set(new_folder)
            self.config_file = new_config_path
            self.log_file = new_log_path
            
            # Aggiorna il backup manager con la nuova cartella
            self.backup_manager.data_folder = new_folder
            
            # Ricarica la configurazione dalla nuova posizione (o crea default)
            self.load_config()
            self.load_log()
            
            self.update_status_bar(f"Cartella dati cambiata in: {new_folder}", "success")
        except Exception as e:
            logger.error(f"Errore cambiando cartella dati: {e}")
            messagebox.showerror("Errore", f"Impossibile cambiare cartella dati: {e}")
            self.set_data_folder(old_folder, move_data=False) # Torna alla cartella precedente in caso di errore

    def rebuild_price_list(self):
        if not hasattr(self, 'settings_service_tree'): return
        for i in self.settings_service_tree.get_children(): self.settings_service_tree.delete(i)
        for service, price in self.prices.items():
            self.settings_service_tree.insert("", "end", values=(service, f"{price:.2f}"))

    def add_service(self):
        name = simpledialog.askstring("Nuovo Servizio", "Nome servizio:")
        if name and name not in self.prices:
            price = simpledialog.askfloat("Prezzo", f"Prezzo per {name}:")
            if price is not None:
                self.prices[name] = price
                self.rebuild_price_list()

    def remove_service(self):
        selected = self.settings_service_tree.selection()
        if not selected: return
        name = self.settings_service_tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Conferma", f"Rimuovere il servizio '{name}'? Sarà rimosso da tutti i clienti."):
            del self.prices[name]
            self.rebuild_price_list()

    def edit_price_in_tree(self):
        selected = self.settings_service_tree.selection()
        if not selected: return
        name = self.settings_service_tree.item(selected[0], "values")[0]
        new_price = simpledialog.askfloat("Modifica Prezzo", f"Nuovo prezzo per {name}:", initialvalue=self.prices[name])
        if new_price is not None:
            self.prices[name] = new_price
            self.rebuild_price_list()
    
    def move_service_up(self):
        selected = self.settings_service_tree.selection()
        if not selected: return
        self.settings_service_tree.move(selected[0], "", self.settings_service_tree.index(selected[0])+1)

    def move_service_down(self):
        selected = self.settings_service_tree.selection()
        if not selected: return
        self.settings_service_tree.move(selected[0], "", self.settings_service_tree.index(selected[0])-1)


    def show_statistics_dashboard(self): 
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Dashboard Statistiche")
        stats_win.geometry("900x600")
        stats_win.configure(bg=self.colors['background'])
        stats_win.transient(self.root)
        stats_win.grab_set()

        main_frame = tk.Frame(stats_win, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(main_frame, text="Riepilogo Statistiche", font=self.fonts['title'], bg=self.colors['background'], fg=self.colors['text']).pack(anchor='w', pady=(0, 20))
        
        total_revenue = self.stats_manager.get_total_revenue()
        total_clients = sum(len(c) for c in self.data_by_category.values())
        
        summary_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        summary_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(summary_frame, text="Fatturato Totale", font=self.fonts['subheading'], bg=summary_frame['bg'], fg=self.colors['text_secondary']).grid(row=0, column=0, padx=20, pady=10, sticky='w')
        tk.Label(summary_frame, text=f"€ {total_revenue:,.2f}", font=('Segoe UI', 20, 'bold'), bg=summary_frame['bg'], fg=self.colors['success']).grid(row=1, column=0, padx=20, pady=(0,10), sticky='w')
        
        tk.Label(summary_frame, text="Clienti Totali", font=self.fonts['subheading'], bg=summary_frame['bg'], fg=self.colors['text_secondary']).grid(row=0, column=1, padx=20, pady=10, sticky='w')
        tk.Label(summary_frame, text=f"{total_clients}", font=('Segoe UI', 20, 'bold'), bg=summary_frame['bg'], fg=self.colors['primary']).grid(row=1, column=1, padx=20, pady=(0,10), sticky='w')

        # Detail Treeview
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        
        stats_tree = ttk.Treeview(tree_frame, columns=("Clienti", "Fatturato"), style="Professional.Treeview")
        stats_tree.heading('#0', text='Categoria')
        stats_tree.heading('Clienti', text='N. Clienti')
        stats_tree.heading('Fatturato', text='Fatturato Categoria (€)')
        stats_tree.column('Clienti', width=120, anchor='center')
        stats_tree.column('Fatturato', width=200, anchor='e')
        stats_tree.pack(fill=tk.BOTH, expand=True)

        category_stats = self.stats_manager.get_category_stats()
        for category, data in sorted(category_stats.items()):
            stats_tree.insert('', 'end', text=category, values=(data['client_count'], f"{data['revenue']:,.2f}"))

        self.create_professional_button(main_frame, "Chiudi", stats_win.destroy, 'secondary').pack(side=tk.BOTTOM, pady=20)


    def export_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv"), ("Excel file", "*.xlsx")])
        if not filename: return

        try:
            if filename.endswith('.xlsx') and OPENPYXL_AVAILABLE:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Clienti"
                ws.append(['Categoria', 'Cliente'] + self.service_names)
                for cat, clients in self.data_by_category.items():
                    for client in clients:
                        ws.append([cat, client['Cliente']] + client['values'])
                wb.save(filename)
            else: # CSV
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Categoria', 'Cliente'] + self.service_names)
                    for cat, clients in self.data_by_category.items():
                        for client in clients:
                            writer.writerow([cat, client['Cliente']] + client['values'])
            self.update_status_bar("Dati esportati con successo in formato CSV.", "success")
        except Exception as e:
            messagebox.showerror("Errore Esportazione", str(e))
            self.update_status_bar(f"Errore durante l'esportazione: {e}", "accent")

    def advanced_search(self): 
        search_win = tk.Toplevel(self.root)
        search_win.title("Ricerca Avanzata")
        search_win.geometry("400x300")
        search_win.configure(bg=self.colors['background'])
        search_win.transient(self.root)
        search_win.grab_set()
        
        tk.Label(search_win, text="Funzionalità non ancora completa", font=self.fonts['subheading'], bg=self.colors['background'], fg=self.colors['text']).pack(pady=50)

    def update_status_bar(self, text, style, duration=4000):
        self.status_label.config(text=text, fg=self.colors.get(style, self.colors['text']))
        if duration:
            self.root.after(duration, lambda: self.status_label.config(text="Pronto", fg=self.colors['success']))
    
    def update_backup_info(self):
        if self.last_backup_time:
            time_str = self.last_backup_time.strftime('%d/%m/%Y %H:%M')
            self.abs_backup_label.config(text=f"Ultimo backup: {time_str}")
            delta = (datetime.now() - self.last_backup_time).total_seconds()
            self.backup_label.config(text=f"Backup: {int(delta/60)}m fa")
        else:
            self.backup_label.config(text="Backup non eseguito", fg=self.colors['text_secondary'])
            self.abs_backup_label.config(text="")
        self.root.after(30000, self.update_backup_info)
        
    def update_statistics(self):
        if hasattr(self, 'stats_manager'):
            self.stats_manager = StatisticsManager(self.data_by_category, self.prices)
            total_revenue = self.stats_manager.get_total_revenue()
            total_clients = sum(len(c) for c in self.data_by_category.values())
            
            self.revenue_label.config(text=f"€{total_revenue:,.2f}")
            self.clients_total_label.config(text=f"{total_clients} clienti")
        
    def setup_keyboard_shortcuts(self):
        self.root.bind("<Control-s>", lambda e: self.manual_save())
    
    def start_backup_thread(self):
        def worker():
            while True:
                time.sleep(BACKUP_INTERVAL)
                if self.backup_manager.create_backup():
                    self.last_backup_time = datetime.now()
        threading.Thread(target=worker, daemon=True).start()

    def add_log_entry(self, client_id, client_name, action_type, action_name, old_value=None, new_value=None):
        """Aggiunge un'entrata al registro delle attività."""
        entry = {
            "timestamp": datetime.now().isoformat(), 
            "client_id": client_id,
            "client_name": client_name,
            "service": "", # Servizio coinvolto (se applicabile)
            "action": action_name,
            "original_value": old_value,
            "new_value": new_value
        }
        if action_type == "Applicazione":
            entry["action"] = f"{action_type} '{action_name}'"
        elif action_type == "Modifica":
            entry["action"] = f"{action_type} '{action_name}'"
            entry["service"] = action_name
        elif action_type == "Aggiunta":
            entry["action"] = f"{action_type} '{action_name}'"
        elif action_type == "Eliminazione":
            entry["action"] = f"{action_type} '{action_name}'"
        self.activity_log.insert(0, entry)
        if len(self.activity_log) > MAX_LOG_ENTRIES:
            self.activity_log = self.activity_log[:MAX_LOG_ENTRIES]


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    
    root = tk.Tk()
    app = ServiziClientiManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
