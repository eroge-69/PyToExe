import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, date
import calendar
import os
import sys

class AnalisiCaringFinale:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisi Caring")
        self.root.geometry("1600x1000")
        
        self.df_caring = None
        self.risultati_completi = None
        
        # Operatori disponibili
        self.operatori_target = ['CRISTINA', 'MARIA', 'ALESSIA', 'ALESSIO', 'SILVIA', 'GIOVANNI', 'GABRIELE']
        
        # Mesi 2025 - COMPLETI
        self.mesi_affido = ['GENNAIO_25', 'FEBBRAIO_25', 'MARZO_25', 'APRILE_25', 'MAGGIO_25', 'GIUGNO_25', 'LUGLIO_25', 'AGOSTO_25', 'SETTEMBRE_25', 'OTTOBRE_25', 'NOVEMBRE_25', 'DICEMBRE_25']
        self.mesi_analisi = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']
        
        # Variabili checkbox
        self.societa_vars = {}
        self.operatori_vars = {}
        
        self.setup_ui()
        self.carica_dati()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="📊 Analisi Caring", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Frame controlli
        controlli_frame = ttk.LabelFrame(main_frame, text="Selezioni", padding="15")
        controlli_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Frame società
        societa_frame = ttk.LabelFrame(controlli_frame, text="Società", padding="10")
        societa_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        
        for i, societa in enumerate(['FACILE', 'SEI']):
            var = tk.BooleanVar(value=True)
            self.societa_vars[societa] = var
            ttk.Checkbutton(societa_frame, text=societa, variable=var).grid(row=i, column=0, sticky=tk.W)
        
        # Frame operatori  
        operatori_frame = ttk.LabelFrame(controlli_frame, text="Operatori", padding="10")
        operatori_frame.grid(row=0, column=1, sticky=(tk.W, tk.N), padx=(0, 20))
        
        for i, operatore in enumerate(self.operatori_target):
            var = tk.BooleanVar(value=True)
            self.operatori_vars[operatore] = var
            ttk.Checkbutton(operatori_frame, text=operatore, variable=var).grid(
                row=i//3, column=i%3, sticky=tk.W, padx=8, pady=2)
        
        # Parametri
        params_frame = ttk.LabelFrame(controlli_frame, text="Parametri", padding="10")
        params_frame.grid(row=0, column=2, sticky=(tk.W, tk.N))
        
        ttk.Label(params_frame, text="Clienti Affidati:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.clienti_affidati_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.clienti_affidati_var, width=15).grid(row=1, column=0, pady=(0, 5))
        ttk.Label(params_frame, text="(se vuoto usa dati reali)", font=('Arial', 8)).grid(row=2, column=0)
        
        # Pulsanti
        btn_frame = ttk.Frame(controlli_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=(15, 0))
        
        ttk.Button(btn_frame, text="🔍 Analisi Completa", command=self.genera_analisi_excel_replica).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="✓ Tutto", command=self.seleziona_tutto).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="💾 Salva", command=self.salva_risultati).pack(side=tk.LEFT)
        
        # Risultati in formato Excel
        risultati_frame = ttk.LabelFrame(main_frame, text="Risultati - Formato Foglio ANALISI", padding="10")
        risultati_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        risultati_frame.columnconfigure(0, weight=1)
        risultati_frame.rowconfigure(1, weight=1)
        
        self.info_label = ttk.Label(risultati_frame, text="Clicca 'Analisi Completa' per generare i risultati", 
                                   font=('Arial', 11))
        self.info_label.grid(row=0, column=0, pady=(0, 10))
        
        # Text widget per mostrare risultati in formato tabella Excel
        self.risultati_text = tk.Text(risultati_frame, font=('Courier New', 8), wrap=tk.NONE)
        self.risultati_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scroll_v = ttk.Scrollbar(risultati_frame, orient=tk.VERTICAL, command=self.risultati_text.yview)
        scroll_v.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.risultati_text.configure(yscrollcommand=scroll_v.set)
        
        scroll_h = ttk.Scrollbar(risultati_frame, orient=tk.HORIZONTAL, command=self.risultati_text.xview)
        scroll_h.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.risultati_text.configure(xscrollcommand=scroll_h.set)
    
    def carica_dati(self):
        """Carica dati dal foglio CARING INTERNO"""
        try:
            # Per exe: cerca il file nella stessa directory dell'eseguibile
            if getattr(sys, 'frozen', False):
                # Se è un exe compilato
                base_path = os.path.dirname(sys.executable)
            else:
                # Se è uno script Python
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            file_path = os.path.join(base_path, "ANALISI CARING (1).xlsx")
            self.df_caring = pd.read_excel(file_path, sheet_name='CARING INTERNO')
            
            # Converti date
            self.df_caring['DATA FINE'] = pd.to_datetime(self.df_caring['DATA FINE'], errors='coerce')
            
            # Filtra operatori target
            self.df_caring = self.df_caring[self.df_caring['OPERATORE'].isin(self.operatori_target)].copy()
            
            print(f"Dati caricati: {len(self.df_caring)} record")
            self.info_label.config(text=f"✅ Dati caricati: {len(self.df_caring)} record dal foglio CARING INTERNO")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento: {e}")
    
    def calcola_data_limite(self, mese_nome, anno=2025):
        """Calcola ultimo giorno del mese"""
        mesi_map = {
            'GENNAIO': 1, 'FEBBRAIO': 2, 'MARZO': 3, 'APRILE': 4, 'MAGGIO': 5, 'GIUGNO': 6,
            'LUGLIO': 7, 'AGOSTO': 8, 'SETTEMBRE': 9, 'OTTOBRE': 10, 'NOVEMBRE': 11, 'DICEMBRE': 12
        }
        mese_num = mesi_map[mese_nome]
        ultimo_giorno = calendar.monthrange(anno, mese_num)[1]
        return date(anno, mese_num, ultimo_giorno)
    
    def genera_analisi_excel_replica(self):
        """
        Genera analisi ESATTAMENTE come nel foglio ANALISI Excel:
        
        Logica:
        - Per ogni operatore, per ogni mese di AFFIDO
        - AFFIDATI = clienti affidati in quel mese 
        - Per ogni mese SUCCESSIVO di analisi:
        - RIMASTI = di quelli affidati, quanti hanno data_fine >= limite_mese_analisi OR data_fine vuota
        - % = rimasti/affidati
        """
        if self.df_caring is None:
            return
        
        try:
            societa_sel = [s for s, var in self.societa_vars.items() if var.get()]
            operatori_sel = [o for o, var in self.operatori_vars.items() if var.get()]
            
            if not societa_sel or not operatori_sel:
                messagebox.showwarning("Attenzione", "Seleziona società e operatori")
                return
            
            # Pulisci display
            self.risultati_text.delete(1.0, tk.END)
            
            output_lines = []
            output_lines.append("=" * 120)
            output_lines.append("                        ANALISI CARING - REPLICA FOGLIO ANALISI EXCEL")
            output_lines.append("=" * 120)
            
            clienti_affidati_input = None
            if self.clienti_affidati_var.get().strip():
                try:
                    clienti_affidati_input = int(self.clienti_affidati_var.get())
                except:
                    pass
            
            # Per ogni operatore selezionato
            for operatore in operatori_sel:
                output_lines.append(f"\n{'═' * 50} OPERATORE: {operatore} {'═' * 50}")
                
                # Header tabella
                header = f"{'Mese Affido':<15} | {'Società':<8} | {'Affidati':<8} |"
                for mese_analisi in self.mesi_analisi:
                    header += f" {mese_analisi[:3]:<13} |"
                output_lines.append(header)
                output_lines.append("-" * len(header))
                
                # Per ogni mese di affido
                for mese_affido in self.mesi_affido:
                    for societa in societa_sel:
                        
                        # 1. AFFIDATI nel mese di affido
                        affidati = self.df_caring[
                            (self.df_caring['OPERATORE'] == operatore) &
                            (self.df_caring['MESE INIZIO'] == mese_affido) &
                            (self.df_caring['SEI'] == societa)
                        ]
                        
                        num_affidati = len(affidati)
                        
                        if num_affidati > 0:
                            # Se specificato clienti affidati custom, usa quello
                            if clienti_affidati_input:
                                num_affidati = clienti_affidati_input
                                # In questo caso analizza tutti i clienti dell'operatore/società
                                affidati = self.df_caring[
                                    (self.df_caring['OPERATORE'] == operatore) &
                                    (self.df_caring['SEI'] == societa)
                                ]
                            
                            row_data = f"{mese_affido:<15} | {societa:<8} | {num_affidati:<8} |"
                            
                            # 2. Per ogni mese di analisi successivo
                            for mese_analisi in self.mesi_analisi:
                                data_limite = self.calcola_data_limite(mese_analisi)
                                
                                # RIMASTI = quelli con data_fine >= limite OR data_fine vuota
                                rimasti = affidati[
                                    (affidati['DATA FINE'] >= pd.to_datetime(data_limite)) |
                                    (affidati['DATA FINE'].isna())
                                ]
                                
                                num_rimasti = len(rimasti)
                                percentuale = (num_rimasti / num_affidati) * 100 if num_affidati > 0 else 0
                                
                                # Mostra sia numero che percentuale con spazio fisso
                                row_data += f" {num_rimasti:3}({percentuale:5.1f}%) |"
                            
                            output_lines.append(row_data)
            
            # Mostra risultati
            self.risultati_text.insert(tk.END, "\n".join(output_lines))
            
            # Statistiche
            total_combinations = len(operatori_sel) * len(societa_sel) * len(self.mesi_affido)
            self.info_label.config(
                text=f"✅ Analisi completata! {total_combinations} combinazioni possibili analizzate\n"
                     f"📊 Logica: Per ogni affido mensile → % clienti rimasti nei mesi successivi"
            )
            
            # Salva risultati per esportazione
            self.risultati_completi = output_lines
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore analisi: {e}")
            import traceback
            traceback.print_exc()
    
    def seleziona_tutto(self):
        for var in list(self.societa_vars.values()) + list(self.operatori_vars.values()):
            var.set(True)
    
    def salva_risultati(self):
        """Salva risultati in file Excel"""
        if not hasattr(self, 'risultati_completi') or not self.risultati_completi:
            messagebox.showwarning("Attenzione", "Nessun risultato da salvare")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"analisi_caring_replica_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Salva Analisi",
                initialfile=default_name
            )
            
            if file_path:
                # Converti i risultati in DataFrame per salvare in Excel
                data_for_excel = []
                
                # Parse dei risultati per creare un DataFrame strutturato
                parsing_data = False
                current_operatore = ""
                
                for line in self.risultati_completi:
                    if "OPERATORE:" in line:
                        current_operatore = line.split("OPERATORE:")[1].split("═")[0].strip()
                    elif "|" in line and not line.startswith("=") and not line.startswith("-") and "Mese Affido" not in line:
                        # Riga di dati
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 3:
                            mese_affido = parts[0].strip()
                            societa = parts[1].strip()
                            affidati = parts[2].strip()
                            
                            # I mesi successivi sono nelle colonne successive
                            mesi_data = parts[3:]
                            
                            row_data = {
                                'Operatore': current_operatore,
                                'Mese_Affido': mese_affido,
                                'Societa': societa,
                                'Clienti_Affidati': affidati
                            }
                            
                            # Aggiungi dati dei mesi
                            mesi_nomi = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 
                                        'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']
                            
                            for i, mese_data in enumerate(mesi_data):
                                if i < len(mesi_nomi) and mese_data.strip():
                                    row_data[mesi_nomi[i]] = mese_data.strip()
                            
                            data_for_excel.append(row_data)
                
                # Crea DataFrame e salva in Excel
                if data_for_excel:
                    df_excel = pd.DataFrame(data_for_excel)
                    df_excel.to_excel(file_path, index=False, engine='openpyxl')
                    messagebox.showinfo("Successo", f"✅ Risultati salvati in Excel:\n{file_path}")
                else:
                    # Fallback: salva i risultati testuali in Excel
                    df_text = pd.DataFrame({'Risultati_Analisi': self.risultati_completi})
                    df_text.to_excel(file_path, index=False, engine='openpyxl')
                    messagebox.showinfo("Successo", f"✅ Risultati salvati in Excel:\n{file_path}")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Errore", f"Errore salvamento: {e}")

def main():
    root = tk.Tk()
    
    # Stile
    style = ttk.Style()
    style.theme_use('clam')
    
    app = AnalisiCaringFinale(root)
    root.mainloop()

if __name__ == "__main__":
    main()
