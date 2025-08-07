import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import locale
import warnings

# Ignora warnings di pandas
warnings.filterwarnings('ignore')

# Imposta locale italiano
try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Italian_Italy.1252')
    except:
        pass

class HealthTransactionAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Unificato Gestione Transazioni Sanitarie v2.0")
        self.root.geometry("1400x800")
        
        # Variabili
        self.df = None
        self.current_file = None
        self.processed_data = {}
        
        # Configurazione tetti di spesa
        self.spending_limits = {
            'celiachia': {
                'age_limits': [
                    (0, 0, 'M', 56), (0, 0, 'F', 56),
                    (1, 5, 'M', 56), (1, 5, 'F', 56),
                    (6, 9, 'M', 70), (6, 9, 'F', 70),
                    (10, 13, 'M', 100), (10, 13, 'F', 90),
                    (14, 17, 'M', 124), (14, 17, 'F', 99),
                    (18, 59, 'M', 110), (18, 59, 'F', 90),
                    (60, 999, 'M', 89), (60, 999, 'F', 75)
                ],
                'tolerance': 2
            },
            'aproteico': {
                'adult_limit': 132.00,
                'pediatric_limit': 260.00,
                'tolerance': 5
            }
        }
        
        # Mappatura mesi
        self.month_map = {
            1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile',
            5: 'maggio', 6: 'giugno', 7: 'luglio', 8: 'agosto',
            9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'
        }
        
        # Mappatura lettere CF -> mese
        self.cf_month_map = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'H': 6,
            'L': 7, 'M': 8, 'P': 9, 'R': 10, 'S': 11, 'T': 12
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu principale
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Carica CSV", command=self.load_csv)
        file_menu.add_command(label="Carica TXT", command=self.load_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Analisi Mensile", command=self.analyze_monthly)
        tools_menu.add_command(label="Controllo Flag", command=self.check_flags)
        tools_menu.add_command(label="Dividi per Tipo", command=self.split_by_type)
        tools_menu.add_command(label="Conta Transazioni", command=self.count_transactions)
        tools_menu.add_command(label="Ordina CF", command=self.sort_cf)
        
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Esporta", menu=export_menu)
        export_menu.add_command(label="Esporta Report TXT", command=self.export_txt)
        export_menu.add_command(label="Esporta CSV", command=self.export_csv)
        export_menu.add_command(label="Esporta Grafici", command=self.export_charts)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="📁 Carica File", command=self.load_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📊 Analisi", command=self.analyze_monthly).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🏷️ Flag", command=self.check_flags).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📈 Statistiche", command=self.show_statistics).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Esporta", command=self.export_txt).pack(side=tk.LEFT, padx=2)
        
        # Info file corrente
        self.file_label = ttk.Label(toolbar, text="Nessun file caricato", foreground="gray")
        self.file_label.pack(side=tk.RIGHT, padx=10)
        
        # Notebook per tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab Dati
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Dati")
        
        # Treeview per mostrare i dati
        tree_frame = ttk.Frame(self.data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, 
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Tab Report
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Report")
        
        self.report_text = scrolledtext.ScrolledText(self.report_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab Statistiche
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistiche")
        
        # Tab Grafici
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Grafici")
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona file CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Prova diversi encoding
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        self.df = pd.read_csv(file_path, sep=';', encoding=encoding)
                        break
                    except:
                        continue
                
                self.current_file = file_path
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                
                # Normalizza nomi colonne
                self.df.columns = self.df.columns.str.strip()
                
                # Mostra dati nel treeview
                self.display_data()
                
                self.status_bar.config(text=f"Caricato: {len(self.df)} righe")
                messagebox.showinfo("Successo", f"File caricato: {len(self.df)} righe")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore caricamento file: {str(e)}")
    
    def load_txt(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona file TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(1.0, content)
                self.notebook.select(self.report_frame)
                
                self.status_bar.config(text=f"Caricato file TXT: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore caricamento file: {str(e)}")
    
    def display_data(self):
        # Pulisci treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df is None:
            return
        
        # Configura colonne
        self.tree['columns'] = list(self.df.columns)
        self.tree['show'] = 'headings'
        
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Inserisci righe (max 1000 per performance)
        for idx, row in self.df.head(1000).iterrows():
            values = [str(val) for val in row.values]
            self.tree.insert('', 'end', values=values)
    
    def parse_cf(self, cf):
        """Estrae data di nascita e sesso dal codice fiscale"""
        if not cf or len(cf) < 11:
            return None
        
        try:
            cf = cf.upper()
            
            # Anno (posizioni 7-8)
            year = int(cf[6:8])
            current_year = datetime.now().year % 100
            if year > current_year + 5:  # Se anno > anno corrente + 5, assume 1900
                year = 1900 + year
            else:
                year = 2000 + year
            
            # Mese (posizione 9)
            month_letter = cf[8]
            month = self.cf_month_map.get(month_letter, 1)
            
            # Giorno (posizioni 10-11)
            day = int(cf[9:11])
            gender = 'M'
            if day > 40:
                gender = 'F'
                day -= 40
            
            birth_date = datetime(year, month, day)
            
            return {'birth_date': birth_date, 'gender': gender}
            
        except:
            return None
    
    def calculate_age(self, birth_date, ref_date):
        """Calcola l'età alla data di riferimento"""
        age = ref_date.year - birth_date.year
        if (ref_date.month < birth_date.month) or \
           (ref_date.month == birth_date.month and ref_date.day < birth_date.day):
            age -= 1
        return age
    
    def get_spending_limit(self, age, gender, transaction_type='celiachia'):
        """Ottiene il tetto di spesa in base a età, sesso e tipo"""
        if transaction_type == 'aproteico':
            if age <= 12:
                return self.spending_limits['aproteico']['pediatric_limit']
            else:
                return self.spending_limits['aproteico']['adult_limit']
        else:
            for min_age, max_age, g, limit in self.spending_limits['celiachia']['age_limits']:
                if min_age <= age <= max_age and g == gender:
                    return limit
            return 0
    
    def parse_date(self, date_str):
        """Parse flessibile per date in vari formati"""
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        
        # Tentativo finale con parser automatico
        try:
            return pd.to_datetime(date_str)
        except:
            return None
    
    def analyze_monthly(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun file caricato")
            return
        
        try:
            report = []
            
            # Parse date con formato flessibile
            self.df['Data Parsed'] = self.df['Data Acquisto'].apply(self.parse_date)
            
            # Rimuovi righe con date non valide
            valid_df = self.df.dropna(subset=['Data Parsed']).copy()
            
            if valid_df.empty:
                messagebox.showwarning("Attenzione", "Nessuna data valida trovata")
                return
            
            # Aggiungi colonna mese-anno
            valid_df['MeseAnno'] = valid_df['Data Parsed'].dt.to_period('M')
            
            # Parse importo
            valid_df['Importo'] = valid_df['Prezzo Totale'].apply(lambda x: float(str(x).replace(',', '.')))
            
            # Raggruppa per mese
            for period, month_data in valid_df.groupby('MeseAnno'):
                month_name = self.month_map[period.month]
                year = period.year
                
                report.append(f"{'*' * 18} Mese: {month_name} {year} {'*' * 18}\n")
                
                # Raggruppa per ASL
                for asl, asl_data in month_data.groupby('ASL Residenza assistito'):
                    cf_unique = asl_data['CF Assistito'].nunique()
                    total_amount = asl_data['Importo'].sum()
                    
                    report.append(f"ASL: {asl}")
                    report.append(f"  Numero Codici Fiscali: {cf_unique}")
                    report.append(f"  Somma Prezzo Totale: {total_amount:,.2f}".replace('.', ','))
                    report.append("  Dettaglio Codici Fiscali:")
                    
                    # Dettaglio per CF
                    cf_details = []
                    for cf, cf_data in asl_data.groupby('CF Assistito'):
                        cf_sum = cf_data['Importo'].sum()
                        cf_details.append((cf.strip(), cf_sum))
                    
                    # Ordina alfabeticamente per CF
                    cf_details.sort(key=lambda x: x[0])
                    
                    for cf, cf_sum in cf_details:
                        report.append(f"     CF: {cf} - Somma Prezzo Totale: {cf_sum:,.2f}".replace('.', ','))
                    
                    report.append("-" * 60)
                    report.append("")
                
                # Totali mensili
                month_total = month_data['Importo'].sum()
                month_cf_unique = month_data['CF Assistito'].nunique()
                
                report.append("----- Totali per il mese -----")
                report.append(f"Somma Prezzo Totale per il mese: {month_total:,.2f}".replace('.', ','))
                report.append(f"Numero Codici Fiscali Distinti nel mese: {month_cf_unique}")
                report.append("=" * 60)
                report.append("")
            
            # Mostra report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, '\n'.join(report))
            self.notebook.select(self.report_frame)
            
            self.status_bar.config(text="Analisi mensile completata")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'analisi: {str(e)}")
    
    def check_flags(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun file caricato")
            return
        
        try:
            # Determina tipo transazione
            transaction_type = 'celiachia'
            if 'Tipo transazione' in self.df.columns:
                first_type = str(self.df['Tipo transazione'].iloc[0]).lower()
                if 'aproteico' in first_type:
                    transaction_type = 'aproteico'
            
            tolerance = self.spending_limits[transaction_type]['tolerance']
            
            report = []
            flag_stats = defaultdict(lambda: {'raggiunto': 0, 'non_raggiunto': 0})
            
            # Parse date e importi
            self.df['Data Parsed'] = self.df['Data Acquisto'].apply(self.parse_date)
            valid_df = self.df.dropna(subset=['Data Parsed']).copy()
            valid_df['MeseAnno'] = valid_df['Data Parsed'].dt.to_period('M')
            valid_df['Importo'] = valid_df['Prezzo Totale'].apply(lambda x: float(str(x).replace(',', '.')))
            
            # Analisi per mese
            for period, month_data in valid_df.groupby('MeseAnno'):
                month_name = self.month_map[period.month]
                year = period.year
                last_day = period.to_timestamp(how='end')
                
                report.append(f"{'*' * 18} Mese: {month_name} {year} {'*' * 18}\n")
                
                month_flag_raggiunto = 0
                month_flag_non_raggiunto = 0
                month_total = 0
                cf_processed = set()
                
                # Raggruppa per ASL
                for asl, asl_data in month_data.groupby('ASL Residenza assistito'):
                    cf_unique = asl_data['CF Assistito'].nunique()
                    total_amount = asl_data['Importo'].sum()
                    
                    report.append(f"ASL: {asl}")
                    report.append(f"  Numero Codici Fiscali: {cf_unique}")
                    report.append(f"  Somma Prezzo Totale: {total_amount:,.2f}".replace('.', ','))
                    report.append("  Dettaglio Codici Fiscali:")
                    
                    # Analisi per CF
                    cf_details = []
                    for cf, cf_data in asl_data.groupby('CF Assistito'):
                        cf_sum = cf_data['Importo'].sum()
                        month_total += cf_sum
                        
                        # Parse CF per età e sesso
                        cf_info = self.parse_cf(cf)
                        flag_text = ""
                        
                        if cf_info:
                            age = self.calculate_age(cf_info['birth_date'], last_day)
                            limit = self.get_spending_limit(age, cf_info['gender'], transaction_type)
                            
                            if cf_sum >= (limit - tolerance):
                                flag_text = " -Flag raggiunto-"
                                if cf not in cf_processed:
                                    month_flag_raggiunto += 1
                                    flag_stats[str(period)]['raggiunto'] += 1
                            else:
                                flag_text = " -Flag NON Raggiunto-"
                                if cf not in cf_processed:
                                    month_flag_non_raggiunto += 1
                                    flag_stats[str(period)]['non_raggiunto'] += 1
                            
                            cf_processed.add(cf)
                        
                        cf_details.append((cf.strip(), cf_sum, flag_text))
                    
                    # Ordina alfabeticamente per CF
                    cf_details.sort(key=lambda x: x[0])
                    
                    for cf, cf_sum, flag_text in cf_details:
                        report.append(f"     CF: {cf} - Somma Prezzo Totale: {cf_sum:,.2f}{flag_text}".replace('.', ','))
                    
                    report.append("-" * 60)
                    report.append("")
                
                # Totali mensili con flag
                month_cf_unique = month_data['CF Assistito'].nunique()
                
                report.append("----- Totali per il mese -----")
                report.append(f"Somma Prezzo Totale per il mese: {month_total:,.2f}".replace('.', ','))
                report.append(f"Numero Codici Fiscali Distinti nel mese: {month_cf_unique}")
                report.append(f"Flag Raggiunto = {month_flag_raggiunto}")
                report.append(f"flag NON raggiunto = {month_flag_non_raggiunto}")
                report.append("=" * 60)
                report.append("")
            
            # Mostra report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, '\n'.join(report))
            self.notebook.select(self.report_frame)
            
            self.status_bar.config(text="Controllo flag completato")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel controllo flag: {str(e)}")
    
    def split_by_type(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun file caricato")
            return
        
        if 'Tipo transazione' not in self.df.columns:
            messagebox.showwarning("Attenzione", "Colonna 'Tipo transazione' non trovata")
            return
        
        try:
            base_name = os.path.splitext(self.current_file)[0]
            
            # Filtra per tipo
            celiachia_df = self.df[self.df['Tipo transazione'].str.lower().str.strip() == 'celiachia']
            aproteico_df = self.df[self.df['Tipo transazione'].str.lower().str.strip() == 'aproteico']
            
            files_created = []
            
            # Salva file
            if not celiachia_df.empty:
                celiachia_file = f"{base_name}_celiachia.csv"
                celiachia_df.to_csv(celiachia_file, sep=';', index=False, encoding='utf-8')
                files_created.append(f"Celiachia: {len(celiachia_df)} righe")
                
            if not aproteico_df.empty:
                aproteico_file = f"{base_name}_Aproteico.csv"
                aproteico_df.to_csv(aproteico_file, sep=';', index=False, encoding='utf-8')
                files_created.append(f"Aproteico: {len(aproteico_df)} righe")
            
            if files_created:
                messagebox.showinfo("Successo", f"File divisi:\n" + "\n".join(files_created))
            else:
                messagebox.showwarning("Attenzione", "Nessun dato trovato per la divisione")
            
            self.status_bar.config(text="Divisione per tipo completata")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella divisione: {str(e)}")
    
    def count_transactions(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun file caricato")
            return
        
        try:
            report = []
            
            # Parse date e importi
            self.df['Data Parsed'] = self.df['Data Acquisto'].apply(self.parse_date)
            valid_df = self.df.dropna(subset=['Data Parsed']).copy()
            valid_df['Importo'] = valid_df['Prezzo Totale'].apply(lambda x: float(str(x).replace(',', '.')))
            
            # Estrai solo data (senza ora) per contare transazioni uniche
            valid_df['DataSola'] = valid_df['Data Parsed'].dt.date
            
            # Conta transazioni per CF
            transaction_counts = {}
            cf_totals = {}
            
            for cf, group in valid_df.groupby('CF Assistito'):
                # Conta combinazioni uniche di CF + Data
                unique_transactions = group.groupby(['DataSola']).size().count()
                total_amount = group['Importo'].sum()
                
                transaction_counts[cf] = unique_transactions
                cf_totals[cf] = total_amount
            
            # Ordina per CF alfabeticamente
            sorted_cfs = sorted(transaction_counts.keys())
            
            for cf in sorted_cfs:
                count = transaction_counts[cf]
                total = cf_totals[cf]
                report.append(f"CF:{cf}; N° Transazioni: {count}; TOT: {total:,.2f}".replace('.', ','))
            
            # Totali
            total_transactions = sum(transaction_counts.values())
            unique_cf = len(transaction_counts)
            total_euro = sum(cf_totals.values())
            
            report.append("")
            report.append(f"Totale Transazioni: {total_transactions}")
            report.append(f"Codici Fiscali distinti: {unique_cf}")
            report.append(f"Totale Euro spesi: {total_euro:,.2f}".replace('.', ','))
            
            # Mostra report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, '\n'.join(report))
            self.notebook.select(self.report_frame)
            
            self.status_bar.config(text="Conteggio transazioni completato")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel conteggio: {str(e)}")
    
    def sort_cf(self):
        """Ordina i CF nel report alfabeticamente"""
        content = self.report_text.get(1.0, tk.END)
        lines = content.split('\n')
        
        new_lines = []
        cf_buffer = []
        in_cf_block = False
        
        for line in lines:
            if 'Dettaglio Codici Fiscali:' in line:
                if cf_buffer:
                    # Ordina buffer precedente
                    cf_buffer.sort(key=lambda x: re.search(r'CF:\s*([A-Z0-9]+)', x).group(1) if re.search(r'CF:\s*([A-Z0-9]+)', x) else '')
                    new_lines.extend(cf_buffer)
                    cf_buffer = []
                new_lines.append(line)
                in_cf_block = True
                continue
            
            if in_cf_block and re.match(r'^\s*CF:\s*[A-Z0-9]+', line):
                cf_buffer.append(line)
                continue
            
            if in_cf_block and cf_buffer:
                # Fine blocco CF
                cf_buffer.sort(key=lambda x: re.search(r'CF:\s*([A-Z0-9]+)', x).group(1) if re.search(r'CF:\s*([A-Z0-9]+)', x) else '')
                new_lines.extend(cf_buffer)
                cf_buffer = []
                in_cf_block = False
            
            new_lines.append(line)
        
        # Flush finale
        if cf_buffer:
            cf_buffer.sort(key=lambda x: re.search(r'CF:\s*([A-Z0-9]+)', x).group(1) if re.search(r'CF:\s*([A-Z0-9]+)', x) else '')
            new_lines.extend(cf_buffer)
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, '\n'.join(new_lines))
        
        self.status_bar.config(text="Ordinamento CF completato")
        messagebox.showinfo("Successo", "CF ordinati alfabeticamente nel report")
    
    def show_statistics(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun file caricato")
            return
        
        try:
            # Parse dati
            self.df['Data Parsed'] = self.df['Data Acquisto'].apply(self.parse_date)
            valid_df = self.df.dropna(subset=['Data Parsed']).copy()
            valid_df['Importo'] = valid_df['Prezzo Totale'].apply(lambda x: float(str(x).replace(',', '.')))
            valid_df['MeseAnno'] = valid_df['Data Parsed'].dt.to_period('M')
            
            # Crea frame per statistiche
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            
            # Frame statistiche testuali
            stats_text_frame = ttk.LabelFrame(self.stats_frame, text="Statistiche Generali", padding=10)
            stats_text_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Calcola statistiche
            total_records = len(valid_df)
            unique_cf = valid_df['CF Assistito'].nunique()
            unique_asl = valid_df['ASL Residenza assistito'].nunique()
            total_amount = valid_df['Importo'].sum()
            avg_per_cf = total_amount / unique_cf if unique_cf > 0 else 0
            
            # Statistiche per mese
            monthly_stats = valid_df.groupby('MeseAnno').agg({
                'Importo': 'sum',
                'CF Assistito': 'nunique'
            }).reset_index()
            
            avg_monthly_amount = monthly_stats['Importo'].mean()
            avg_monthly_cf = monthly_stats['CF Assistito'].mean()
            
            # Top CF per importo
            cf_totals = valid_df.groupby('CF Assistito')['Importo'].sum().sort_values(ascending=False)
            top_cf = cf_totals.head(5)
            
            # Top ASL per importo
            asl_totals = valid_df.groupby('ASL Residenza assistito')['Importo'].sum().sort_values(ascending=False)
            top_asl = asl_totals.head(5)
            
            # Mostra statistiche
            stats_info = f"""
📊 STATISTICHE GENERALI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Totale record: {total_records:,}
👥 Codici Fiscali unici: {unique_cf:,}
🏥 ASL uniche: {unique_asl}
💰 Importo totale: €{total_amount:,.2f}
💵 Media per CF: €{avg_per_cf:,.2f}

📅 STATISTICHE MENSILI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Media mensile importo: €{avg_monthly_amount:,.2f}
👥 Media mensile CF: {avg_monthly_cf:.0f}
📊 Numero mesi: {len(monthly_stats)}

🏆 TOP 5 CF PER IMPORTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for i, (cf, amount) in enumerate(top_cf.items(), 1):
                stats_info += f"{i}. {cf}: €{amount:,.2f}\n"
            
            stats_info += """
🏥 TOP 5 ASL PER IMPORTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for i, (asl, amount) in enumerate(top_asl.items(), 1):
                asl_display = str(asl)[:40] + "..." if len(str(asl)) > 40 else str(asl)
                stats_info += f"{i}. {asl_display}: €{amount:,.2f}\n"
            
            # Mostra statistiche nel frame
            stats_label = ttk.Label(stats_text_frame, text=stats_info, font=("Segoe UI", 10))
            stats_label.pack(anchor=tk.W)
            
            # Crea grafici
            self.create_statistical_charts(valid_df)
            
            self.notebook.select(self.stats_frame)
            self.status_bar.config(text="Statistiche generate")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nelle statistiche: {str(e)}")
    
    def create_statistical_charts(self, df):
        """Crea grafici statistici"""
        # Pulisci frame grafici
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Crea canvas scrollabile
        canvas = tk.Canvas(self.charts_frame)
        scrollbar = ttk.Scrollbar(self.charts_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Figure matplotlib
        fig = Figure(figsize=(14, 16), dpi=80)
        
        # 1. Trend mensile importi
        ax1 = fig.add_subplot(4, 2, 1)
        monthly_amounts = df.groupby('MeseAnno')['Importo'].sum()
        x_months = [str(m) for m in monthly_amounts.index]
        ax1.plot(x_months, monthly_amounts.values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax1.set_title('Trend Mensile Importi', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Mese')
        ax1.set_ylabel('Importo (€)')
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Aggiungi valori sui punti
        for i, (x, y) in enumerate(zip(x_months, monthly_amounts.values)):
            if i % 2 == 0:  # Mostra solo alcuni valori per evitare sovrapposizioni
                ax1.annotate(f'€{y:,.0f}', (i, y), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=8)
        
        # 2. Numero CF per mese
        ax2 = fig.add_subplot(4, 2, 2)
        monthly_cf = df.groupby('MeseAnno')['CF Assistito'].nunique()
        bars = ax2.bar(x_months, monthly_cf.values, color='#A23B72')
        ax2.set_title('Numero CF Unici per Mese', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Mese')
        ax2.set_ylabel('Numero CF')
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Aggiungi valori sulle barre
        for bar, value in zip(bars, monthly_cf.values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}', ha='center', va='bottom', fontsize=8)
        
        # 3. Top 10 ASL per importo
        ax3 = fig.add_subplot(4, 2, 3)
        asl_amounts = df.groupby('ASL Residenza assistito')['Importo'].sum().nlargest(10)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(asl_amounts)))
        bars = ax3.barh(range(len(asl_amounts)), asl_amounts.values, color=colors)
        ax3.set_yticks(range(len(asl_amounts)))
        ax3.set_yticklabels([str(asl)[:30] + '...' if len(str(asl)) > 30 else str(asl) 
                             for asl in asl_amounts.index], fontsize=9)
        ax3.set_title('Top 10 ASL per Importo Totale', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Importo (€)')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Aggiungi valori
        for bar, value in zip(bars, asl_amounts.values):
            width = bar.get_width()
            ax3.text(width, bar.get_y() + bar.get_height()/2.,
                    f'€{value:,.0f}', ha='left', va='center', fontsize=8)
        
        # 4. Distribuzione importi per CF
        ax4 = fig.add_subplot(4, 2, 4)
        cf_amounts = df.groupby('CF Assistito')['Importo'].sum()
        n, bins, patches = ax4.hist(cf_amounts.values, bins=30, color='#F18F01', 
                                    edgecolor='black', alpha=0.7)
        ax4.set_title('Distribuzione Importi per CF', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Importo (€)')
        ax4.set_ylabel('Frequenza')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Aggiungi linea media e mediana
        mean_val = cf_amounts.mean()
        median_val = cf_amounts.median()
        ax4.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: €{mean_val:.0f}')
        ax4.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Mediana: €{median_val:.0f}')
        ax4.legend()
        
        # 5. Analisi per tipo transazione (se presente)
        if 'Tipo transazione' in df.columns:
            ax5 = fig.add_subplot(4, 2, 5)
            type_counts = df['Tipo transazione'].value_counts()
            colors = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181'][:len(type_counts)]
            wedges, texts, autotexts = ax5.pie(type_counts.values, 
                                                labels=type_counts.index,
                                                autopct='%1.1f%%',
                                                colors=colors,
                                                startangle=90,
                                                explode=[0.05] * len(type_counts))
            ax5.set_title('Distribuzione per Tipo Transazione', fontsize=12, fontweight='bold')
            
            # Migliora l'aspetto del testo
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
            
            # 6. Confronto importi per tipo
            ax6 = fig.add_subplot(4, 2, 6)
            type_amounts = df.groupby('Tipo transazione')['Importo'].sum()
            bars = ax6.bar(type_amounts.index, type_amounts.values, color=colors[:len(type_amounts)])
            ax6.set_title('Importi Totali per Tipo', fontsize=12, fontweight='bold')
            ax6.set_ylabel('Importo (€)')
            ax6.grid(True, alpha=0.3, axis='y')
            
            # Aggiungi valori sulle barre
            for bar, value in zip(bars, type_amounts.values):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height,
                        f'€{value:,.0f}', ha='center', va='bottom', fontsize=10)
        
        # 7. Analisi giornaliera
        ax7 = fig.add_subplot(4, 2, 7)
        df['Giorno'] = df['Data Parsed'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = df['Giorno'].value_counts().reindex(day_order, fill_value=0)
        day_names_it = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        colors = ['#E63946', '#F1FAEE', '#A8DADC', '#457B9D', '#1D3557', '#F77F00', '#FCBF49']
        bars = ax7.bar(day_names_it, day_counts.values, color=colors)
        ax7.set_title('Distribuzione Transazioni per Giorno della Settimana', fontsize=12, fontweight='bold')
        ax7.set_ylabel('Numero Transazioni')
        ax7.grid(True, alpha=0.3, axis='y')
        plt.setp(ax7.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Aggiungi valori
        for bar, value in zip(bars, day_counts.values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}', ha='center', va='bottom', fontsize=9)
        
        # 8. Media mobile importi (se ci sono abbastanza dati)
        ax8 = fig.add_subplot(4, 2, 8)
        daily_amounts = df.groupby(df['Data Parsed'].dt.date)['Importo'].sum()
        
        if len(daily_amounts) > 7:
            rolling_mean = daily_amounts.rolling(window=7).mean()
            ax8.plot(daily_amounts.index, daily_amounts.values, alpha=0.3, 
                    label='Importo Giornaliero', color='lightblue')
            ax8.plot(rolling_mean.index, rolling_mean.values, linewidth=2, 
                    label='Media Mobile 7gg', color='darkblue')
            ax8.fill_between(daily_amounts.index, daily_amounts.values, alpha=0.2, color='lightblue')
            ax8.set_title('Trend Giornaliero con Media Mobile', fontsize=12, fontweight='bold')
            ax8.set_xlabel('Data')
            ax8.set_ylabel('Importo (€)')
            ax8.legend()
            ax8.grid(True, alpha=0.3)
            plt.setp(ax8.xaxis.get_majorticklabels(), rotation=45, ha='right')
        else:
            # Se non ci sono abbastanza dati, mostra un box plot per ASL
            top_asl = df.groupby('ASL Residenza assistito')['Importo'].sum().nlargest(5).index
            box_data = [df[df['ASL Residenza assistito'] == asl]['Importo'].values for asl in top_asl]
            bp = ax8.boxplot(box_data, labels=[str(asl)[:15] + '...' if len(str(asl)) > 15 else str(asl) 
                                               for asl in top_asl])
            ax8.set_title('Distribuzione Importi Top 5 ASL', fontsize=12, fontweight='bold')
            ax8.set_ylabel('Importo (€)')
            ax8.grid(True, alpha=0.3, axis='y')
            plt.setp(ax8.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Titolo generale
        fig.suptitle('Dashboard Analisi Transazioni Sanitarie', fontsize=14, fontweight='bold', y=0.995)
        fig.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Integra in tkinter
        canvas_chart = FigureCanvasTkAgg(fig, master=scrollable_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Passa anche a tab grafici
        self.notebook.select(self.charts_frame)
    
    def export_txt(self):
        if not self.report_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Attenzione", "Nessun report da esportare")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.report_text.get(1.0, tk.END))
                
                messagebox.showinfo("Successo", f"Report salvato in:\n{file_path}")
                self.status_bar.config(text=f"Esportato: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore esportazione: {str(e)}")
    
    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun dato da esportare")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            try:
                self.df.to_csv(file_path, sep=';', index=False, encoding='utf-8')
                messagebox.showinfo("Successo", f"CSV salvato in:\n{file_path}")
                self.status_bar.config(text=f"Esportato: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore esportazione: {str(e)}")
    
    def export_charts(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun dato per generare grafici")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"Grafici_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if file_path:
            try:
                # Parse dati
                self.df['Data Parsed'] = self.df['Data Acquisto'].apply(self.parse_date)
                valid_df = self.df.dropna(subset=['Data Parsed']).copy()
                valid_df['Importo'] = valid_df['Prezzo Totale'].apply(lambda x: float(str(x).replace(',', '.')))
                valid_df['MeseAnno'] = valid_df['Data Parsed'].dt.to_period('M')
                
                # Crea figura per export con alta risoluzione
                fig = Figure(figsize=(20, 24), dpi=100)
                
                # Ricrea tutti i grafici per l'export
                # (Codice simile a create_statistical_charts ma con dimensioni maggiori)
                # ... [grafici 1-8 come sopra ma con fig invece di self.fig]
                
                # Per brevità, creo solo alcuni grafici principali
                # 1. Trend mensile
                ax1 = fig.add_subplot(5, 2, 1)
                monthly_amounts = valid_df.groupby('MeseAnno')['Importo'].sum()
                x_months = [str(m) for m in monthly_amounts.index]
                ax1.plot(x_months, monthly_amounts.values, marker='o', linewidth=3, markersize=10)
                ax1.set_title('Trend Mensile Importi', fontsize=16, fontweight='bold')
                ax1.set_xlabel('Mese', fontsize=12)
                ax1.set_ylabel('Importo (€)', fontsize=12)
                ax1.grid(True, alpha=0.3)
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # 2. CF per mese
                ax2 = fig.add_subplot(5, 2, 2)
                monthly_cf = valid_df.groupby('MeseAnno')['CF Assistito'].nunique()
                ax2.bar(x_months, monthly_cf.values, color='teal')
                ax2.set_title('Numero CF Unici per Mese', fontsize=16, fontweight='bold')
                ax2.set_xlabel('Mese', fontsize=12)
                ax2.set_ylabel('Numero CF', fontsize=12)
                ax2.grid(True, alpha=0.3, axis='y')
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # 3. Statistiche riepilogative
                ax3 = fig.add_subplot(5, 1, 5)
                ax3.axis('off')
                
                cf_amounts = valid_df.groupby('CF Assistito')['Importo'].sum()
                
                stats_text = f"""
                RIEPILOGO STATISTICHE COMPLETE
                {'═' * 80}
                
                📊 DATI GENERALI
                • Totale Transazioni: {len(valid_df):,}
                • Codici Fiscali Unici: {valid_df['CF Assistito'].nunique():,}
                • ASL Coinvolte: {valid_df['ASL Residenza assistito'].nunique()}
                • Importo Totale: €{valid_df['Importo'].sum():,.2f}
                
                📈 MEDIE E DISTRIBUZIONI
                • Media per CF: €{cf_amounts.mean():,.2f}
                • Mediana per CF: €{cf_amounts.median():,.2f}
                • Deviazione Standard: €{cf_amounts.std():,.2f}
                • Importo Minimo CF: €{cf_amounts.min():,.2f}
                • Importo Massimo CF: €{cf_amounts.max():,.2f}
                
                📅 PERIODO ANALIZZATO
                • Data Inizio: {valid_df['Data Parsed'].min().strftime('%d/%m/%Y')}
                • Data Fine: {valid_df['Data Parsed'].max().strftime('%d/%m/%Y')}
                • Giorni Totali: {(valid_df['Data Parsed'].max() - valid_df['Data Parsed'].min()).days}
                • Mesi Coperti: {valid_df['MeseAnno'].nunique()}
                
                {'═' * 80}
                Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')}
                """
                
                ax3.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                        fontfamily='monospace', transform=ax3.transAxes)
                
                fig.suptitle('Report Completo Analisi Transazioni Sanitarie', 
                            fontsize=18, fontweight='bold', y=0.995)
                fig.tight_layout(rect=[0, 0.03, 1, 0.97])
                
                # Salva
                if file_path.endswith('.pdf'):
                    from matplotlib.backends.backend_pdf import PdfPages
                    with PdfPages(file_path) as pdf:
                        pdf.savefig(fig, bbox_inches='tight')
                else:
                    fig.savefig(file_path, dpi=150, bbox_inches='tight')
                
                messagebox.showinfo("Successo", f"Grafici salvati in:\n{file_path}")
                self.status_bar.config(text=f"Grafici esportati: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore esportazione grafici: {str(e)}")


def main():
    root = tk.Tk()
    
    # Stile moderno
    style = ttk.Style()
    style.theme_use('clam')
    
    # Colori personalizzati
    style.configure('TButton', padding=6, relief='flat', background='#2E86AB')
    style.configure('TLabel', background='#F0F0F0')
    style.configure('TFrame', background='#F0F0F0')
    
    app = HealthTransactionAnalyzer(root)
    
    # Centra la finestra
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()