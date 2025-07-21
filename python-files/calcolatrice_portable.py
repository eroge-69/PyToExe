#!/usr/bin/env python3
"""
Calcolatore Posizione Trading v6.3 - Versione Portatile
Versione ottimizzata per la conversione in eseguibile Windows
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

class PortableCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.create_interface()
        self.setup_bindings()
        
    def setup_window(self):
        """Configura la finestra principale"""
        self.root.title("Calcolatore Posizione Trading v6.3")
        self.root.geometry("300x480")
        self.root.resizable(False, False)
        
        # Colori tema
        self.colors = {
            'bg': '#ffffff',
            'header': '#667eea',
            'accent': '#e8f0fe', 
            'success': '#28a745',
            'warning': '#fd7e14',
            'danger': '#dc3545',
            'text': '#333333',
            'muted': '#6c757d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Always on top e posizionamento
        self.root.wm_attributes('-topmost', True)
        self.position_window()
        
        # Drag & drop
        self.drag_data = {'x': 0, 'y': 0}
        
    def position_window(self):
        """Posiziona la finestra nell'angolo superiore destro"""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        x = screen_w - 320
        y = 50
        self.root.geometry(f"+{x}+{y}")
        
    def setup_variables(self):
        """Inizializza le variabili"""
        self.entries = {}
        self.results = {}
        self.calculations = {
            'shares': 0,
            'shares_20': 0,
            'shares_30': 0, 
            'shares_50': 0
        }
        
    def create_interface(self):
        """Crea l'interfaccia utente"""
        # Container principale
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], relief='solid', bd=1)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Header
        self.create_header(main_frame)
        
        # Input fields
        self.create_inputs(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Warning area
        self.create_warning(main_frame)
        
        # Results area
        self.create_results(main_frame)
        
        # Status bar
        self.create_status(main_frame)
        
    def create_header(self, parent):
        """Crea l'header con titolo"""
        header = tk.Frame(parent, bg=self.colors['header'], height=40)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        # Bind drag events to header
        header.bind('<Button-1>', self.drag_start)
        header.bind('<B1-Motion>', self.drag_motion)
        
        title = tk.Label(header, text="📊 Calcolatore Posizione v6.3", 
                        font=('Segoe UI', 11, 'bold'),
                        bg=self.colors['header'], fg='white')
        title.pack(expand=True)
        title.bind('<Button-1>', self.drag_start)
        title.bind('<B1-Motion>', self.drag_motion)
        
    def create_inputs(self, parent):
        """Crea i campi di input"""
        inputs_frame = tk.Frame(parent, bg=self.colors['bg'])
        inputs_frame.pack(fill='x', pady=5)
        
        # Definizione dei campi
        fields = [
            ('account', 'ACCOUNT ($):'),
            ('risk_perc', 'RISCHIO (%):'),
            ('risk_dollar', 'RISCHIO ($):'),
            ('stop_loss', 'STOP LOSS ($):')
        ]
        
        for field_id, label_text in fields:
            self.create_input_row(inputs_frame, field_id, label_text)
            
    def create_input_row(self, parent, field_id, label_text):
        """Crea una riga di input"""
        row = tk.Frame(parent, bg=self.colors['bg'])
        row.pack(fill='x', pady=2)
        
        # Label
        label = tk.Label(row, text=label_text, 
                        font=('Segoe UI', 9, 'bold'),
                        bg=self.colors['bg'], fg=self.colors['text'],
                        width=15, anchor='w')
        label.pack(side='left')
        
        # Input container
        input_frame = tk.Frame(row, bg=self.colors['bg'])
        input_frame.pack(side='left', fill='x', expand=True)
        
        # Entry field
        entry = tk.Entry(input_frame, font=('Segoe UI', 9),
                        bg='#fafafa', relief='solid', bd=1,
                        highlightthickness=1, highlightcolor=self.colors['header'])
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Result label
        result = tk.Label(input_frame, text="", 
                         font=('Segoe UI', 8, 'bold'),
                         bg=self.colors['bg'], width=10, anchor='e')
        result.pack(side='right')
        
        self.entries[field_id] = entry
        self.results[field_id] = result
        
    def create_buttons(self, parent):
        """Crea i pulsanti di azione"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=10)
        
        # Calcola
        calc_btn = tk.Button(btn_frame, text="📈 CALCOLA",
                           command=self.calculate,
                           bg=self.colors['header'], fg='white',
                           font=('Segoe UI', 9, 'bold'),
                           relief='flat', cursor='hand2',
                           height=2)
        calc_btn.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        # Reset  
        reset_btn = tk.Button(btn_frame, text="🔄 RESET",
                            command=self.reset,
                            bg='#f8f9fa', fg=self.colors['muted'],
                            font=('Segoe UI', 9, 'bold'),
                            relief='flat', cursor='hand2',
                            height=2)
        reset_btn.pack(side='right', fill='x', expand=True, padx=(3, 0))
        
    def create_warning(self, parent):
        """Crea l'area di warning"""
        self.warning_label = tk.Label(parent, text="",
                                    font=('Segoe UI', 9, 'bold'),
                                    bg=self.colors['bg'], 
                                    height=2)
        self.warning_label.pack(fill='x', pady=5)
        
    def create_results(self, parent):
        """Crea l'area risultati"""
        self.results_frame = tk.Frame(parent, bg=self.colors['bg'])
        self.results_frame.pack(fill='x', pady=5)
        
        # Labels risultati (inizialmente nascosti)
        self.total_label = tk.Label(self.results_frame, text="",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['accent'], fg=self.colors['text'],
                                  height=2, relief='flat')
        
        self.dist_labels = {}
        for perc in ['20', '30', '50']:
            self.dist_labels[perc] = tk.Label(self.results_frame, text="",
                                            font=('Segoe UI', 9),
                                            bg='#f8f9fa', fg=self.colors['text'],
                                            height=2, relief='flat')
            
    def create_status(self, parent):
        """Crea la barra di stato"""
        status_frame = tk.Frame(parent, bg='#e9ecef', height=20)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Pronto", 
                                   font=('Segoe UI', 8),
                                   bg='#e9ecef', fg=self.colors['muted'])
        self.status_label.pack(side='left', padx=5)
        
    def setup_bindings(self):
        """Configura gli event bindings"""
        # Real-time calculations
        self.entries['risk_perc'].bind('<KeyRelease>', self.update_from_percentage)
        self.entries['risk_dollar'].bind('<KeyRelease>', self.update_from_dollars)
        
        # Enter key for calculate
        for entry in self.entries.values():
            entry.bind('<Return>', lambda e: self.calculate())
            
    def drag_start(self, event):
        """Inizia il drag della finestra"""
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y
        
    def drag_motion(self, event):
        """Gestisce il movimento durante il drag"""
        x = self.root.winfo_x() + event.x - self.drag_data['x']
        y = self.root.winfo_y() + event.y - self.drag_data['y']
        self.root.geometry(f"+{x}+{y}")
        
    def update_from_percentage(self, event=None):
        """Aggiorna i valori dal campo percentuale"""
        try:
            account = float(self.entries['account'].get() or 0)
            perc = float(self.entries['risk_perc'].get() or 0)
            
            if account <= 0 or perc < 0:
                self.clear_displays()
                return
                
            dollars = round(account * perc / 100, 2)
            self.entries['risk_dollar'].delete(0, tk.END)
            self.entries['risk_dollar'].insert(0, str(dollars))
            
            self.update_risk_display(perc, dollars)
            self.status_label.config(text=f"Calcolato: {perc}% = ${dollars}")
            
        except ValueError:
            self.clear_displays()
            
    def update_from_dollars(self, event=None):
        """Aggiorna i valori dal campo dollari"""
        try:
            account = float(self.entries['account'].get() or 0)
            dollars = float(self.entries['risk_dollar'].get() or 0)
            
            if account <= 0 or dollars < 0:
                self.clear_displays()
                return
                
            perc = round(dollars / account * 100, 2)
            self.entries['risk_perc'].delete(0, tk.END)
            self.entries['risk_perc'].insert(0, str(perc))
            
            self.update_risk_display(perc, dollars)
            self.status_label.config(text=f"Calcolato: ${dollars} = {perc}%")
            
        except ValueError:
            self.clear_displays()
            
    def update_risk_display(self, perc, dollars):
        """Aggiorna la visualizzazione del rischio"""
        # Colors and text based on risk level
        if perc > 5:
            color = self.colors['danger']
            risk_text = "⚠️ ALTO RISCHIO"
        elif perc >= 3:
            color = self.colors['warning'] 
            risk_text = "⚡ RISCHIO MEDIO"
        else:
            color = self.colors['success']
            risk_text = "✅ RISCHIO BASSO"
            
        self.results['risk_perc'].config(text=f"{perc:.2f}%", fg=color)
        self.results['risk_dollar'].config(text=f"${dollars:.2f}", fg=color)
        self.warning_label.config(text=f"{risk_text}: {perc:.2f}%", fg=color)
        
    def calculate(self):
        """Esegue il calcolo principale"""
        try:
            risk = float(self.entries['risk_dollar'].get() or 0)
            stop = float(self.entries['stop_loss'].get() or 0)
            
            if risk <= 0 or stop <= 0:
                messagebox.showerror("Errore Input", 
                                   "Inserisci valori maggiori di zero per:\n• Rischio ($)\n• Stop Loss ($)")
                return
                
            # Calcoli
            shares = int(risk / stop)
            shares_20 = int(shares * 0.2)
            shares_30 = int(shares * 0.3)  
            shares_50 = int(shares * 0.5)
            
            remaining_20 = shares - shares_20
            remaining_30 = shares - shares_30
            remaining_50 = shares - shares_50
            
            # Salva calcoli
            self.calculations = {
                'shares': shares,
                'shares_20': shares_20,
                'shares_30': shares_30,
                'shares_50': shares_50
            }
            
            # Mostra risultati
            self.display_results(shares, shares_20, shares_30, shares_50, 
                               remaining_20, remaining_30, remaining_50)
            
            self.status_label.config(text=f"Calcolato: {shares} azioni totali")
            
        except ValueError:
            messagebox.showerror("Errore Calcolo", 
                               "Verifica che tutti i valori siano numeri validi.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore imprevisto:\n{str(e)}")
            
    def display_results(self, shares, s20, s30, s50, r20, r30, r50):
        """Visualizza i risultati dei calcoli"""
        # Total shares
        self.total_label.config(text=f"Azioni Totali: {shares}")
        self.total_label.pack(fill='x', pady=(0, 5))
        
        # Distributions
        distributions = {
            '20': (s20, r20),
            '30': (s30, r30), 
            '50': (s50, r50)
        }
        
        for perc, (sold, remaining) in distributions.items():
            text = f"📊 {perc}%: {sold} azioni → Rimangono {remaining}"
            self.dist_labels[perc].config(text=text)
            self.dist_labels[perc].pack(fill='x', pady=1)
            
    def reset(self):
        """Reset completo dell'applicazione"""
        # Clear entries
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            
        # Clear displays
        self.clear_displays()
        
        # Hide results
        self.total_label.pack_forget()
        for label in self.dist_labels.values():
            label.pack_forget()
            
        # Reset calculations
        self.calculations = {
            'shares': 0,
            'shares_20': 0,
            'shares_30': 0,
            'shares_50': 0
        }
        
        self.status_label.config(text="Reset completato")
        
    def clear_displays(self):
        """Pulisce i display dei risultati in tempo reale"""
        for result in self.results.values():
            result.config(text="", fg='black')
        self.warning_label.config(text="", fg='black')
        
    def run(self):
        """Avvia l'applicazione"""
        try:
            self.status_label.config(text="Calcolatore avviato - Versione 6.3")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Errore Critico", f"Errore nell'applicazione:\n{str(e)}")
            
def main():
    """Entry point principale"""
    try:
        # Verifica ambiente
        if sys.platform.startswith('win'):
            # Configurazioni specifiche per Windows
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TradingCalculator.6.3")
            
        # Avvia applicazione
        app = PortableCalculator()
        app.run()
        
    except ImportError as e:
        print(f"Errore import: {e}")
        print("Assicurati che tkinter sia installato.")
        input("Premi Enter per chiudere...")
        
    except Exception as e:
        print(f"Errore critico: {e}")
        input("Premi Enter per chiudere...")

if __name__ == "__main__":
    main()