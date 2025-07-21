import tkinter as tk
from tkinter import messagebox
import sys

class PositionCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcolatore Posizione v6.3")
        self.root.geometry("320x450")
        self.root.resizable(True, True)
        self.root.configure(bg='#f8f9fa')
        
        # Variables to track dragging
        self.start_x = 0
        self.start_y = 0
        
        # Make window draggable
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)
        
        self.create_widgets()
        
    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def on_move(self, event):
        x = self.root.winfo_x() + event.x - self.start_x
        y = self.root.winfo_y() + event.y - self.start_y
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#ffffff', padx=15, pady=15)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#e8f0fe', pady=8)
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(header_frame, text="📊 Posizione v6.3", 
                              font=('Segoe UI', 14, 'bold'), 
                              bg='#e8f0fe', fg='#333')
        title_label.pack()
        
        # Input fields
        self.create_input_field(main_frame, "ACCOUNT ($):", 0)
        self.account_entry = self.entries[0]
        
        self.create_input_field(main_frame, "RISCHIO (%):", 1)
        self.risk_percentage_entry = self.entries[1]
        self.percentage_result = self.results[1]
        
        self.create_input_field(main_frame, "RISCHIO ($):", 2)
        self.risk_dollar_entry = self.entries[2]
        self.dollar_result = self.results[2]
        
        self.create_input_field(main_frame, "STOP LOSS ($):", 3)
        self.stop_entry = self.entries[3]
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack(fill='x', pady=10)
        
        calc_btn = tk.Button(button_frame, text="📈 CALCOLA", 
                           command=self.calculate,
                           bg='#667eea', fg='white', 
                           font=('Segoe UI', 10, 'bold'),
                           pady=8, relief='flat')
        calc_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        reset_btn = tk.Button(button_frame, text="🔄 RESET", 
                            command=self.reset,
                            bg='#f8f9fa', fg='#6c757d',
                            font=('Segoe UI', 10, 'bold'),
                            pady=8, relief='flat')
        reset_btn.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Warning label
        self.warning_label = tk.Label(main_frame, text="", 
                                    font=('Segoe UI', 9, 'bold'),
                                    bg='#ffffff')
        self.warning_label.pack(pady=5)
        
        # Results frame
        self.results_frame = tk.Frame(main_frame, bg='#ffffff')
        self.results_frame.pack(fill='x', pady=10)
        
        # Results labels
        self.shares_result = tk.Label(self.results_frame, text="", 
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#f8f9fa', fg='#333',
                                    pady=5, relief='flat')
        
        self.result_20 = tk.Label(self.results_frame, text="", 
                                font=('Segoe UI', 9),
                                bg='#f8f9fa', fg='#333',
                                pady=3, relief='flat')
        
        self.result_30 = tk.Label(self.results_frame, text="", 
                                font=('Segoe UI', 9),
                                bg='#f8f9fa', fg='#333',
                                pady=3, relief='flat')
        
        self.result_50 = tk.Label(self.results_frame, text="", 
                                font=('Segoe UI', 9),
                                bg='#f8f9fa', fg='#333',
                                pady=3, relief='flat')
        
        # Bind events for real-time calculation
        self.risk_percentage_entry.bind("<KeyRelease>", self.update_from_percentage)
        self.risk_dollar_entry.bind("<KeyRelease>", self.update_from_dollars)
        
    def create_input_field(self, parent, label_text, index):
        if not hasattr(self, 'entries'):
            self.entries = []
            self.results = []
            
        frame = tk.Frame(parent, bg='#ffffff')
        frame.pack(fill='x', pady=3)
        
        label = tk.Label(frame, text=label_text, 
                        font=('Segoe UI', 9, 'bold'), 
                        bg='#ffffff', fg='#555',
                        width=12, anchor='w')
        label.pack(side='left')
        
        entry_frame = tk.Frame(frame, bg='#ffffff')
        entry_frame.pack(side='left', fill='x', expand=True)
        
        entry = tk.Entry(entry_frame, font=('Segoe UI', 10),
                        bg='#fafafa', relief='flat', bd=1)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        result_label = tk.Label(entry_frame, text="", 
                              font=('Segoe UI', 9, 'bold'),
                              bg='#ffffff', width=10, anchor='e')
        result_label.pack(side='right')
        
        self.entries.append(entry)
        self.results.append(result_label)
        
    def update_from_percentage(self, event=None):
        try:
            account = float(self.account_entry.get() or 0)
            perc = float(self.risk_percentage_entry.get() or 0)
            
            if account <= 0 or perc < 0:
                self.clear_results()
                return
                
            dollars = round(account * perc / 100, 2)
            self.risk_dollar_entry.delete(0, tk.END)
            self.risk_dollar_entry.insert(0, str(dollars))
            self.update_display(perc, dollars)
            
        except:
            self.clear_results()
            
    def update_from_dollars(self, event=None):
        try:
            account = float(self.account_entry.get() or 0)
            dollars = float(self.risk_dollar_entry.get() or 0)
            
            if account <= 0 or dollars < 0:
                self.clear_results()
                return
                
            perc = round(dollars / account * 100, 2)
            self.risk_percentage_entry.delete(0, tk.END)
            self.risk_percentage_entry.insert(0, str(perc))
            self.update_display(perc, dollars)
            
        except:
            self.clear_results()
            
    def update_display(self, perc, dollars):
        self.dollar_result.config(text=f"{dollars:.2f}$")
        self.percentage_result.config(text=f"{perc:.2f}%")
        
        if perc > 5:
            color = "#dc3545"  # Red
            risk_text = "ALTO RISCHIO"
        elif perc >= 3:
            color = "#fd7e14"  # Orange
            risk_text = "RISCHIO MEDIO"
        else:
            color = "#28a745"  # Green
            risk_text = "RISCHIO BASSO"
            
        self.dollar_result.config(fg=color)
        self.percentage_result.config(fg=color)
        self.warning_label.config(text=f"{risk_text}: {perc:.2f}%", fg=color)
        
    def calculate(self):
        try:
            risk = float(self.risk_dollar_entry.get())
            stop = float(self.stop_entry.get())
            
            if not risk or not stop or risk <= 0 or stop <= 0:
                messagebox.showerror("Errore", "Verifica i valori inseriti.")
                return
                
            shares = int(risk / stop)
            shares_20 = int(shares * 0.2)
            shares_30 = int(shares * 0.3)
            shares_50 = int(shares * 0.5)
            
            remaining_20 = shares - shares_20
            remaining_30 = shares - shares_30
            remaining_50 = shares - shares_50
            
            # Show results
            self.shares_result.config(text=f"Azioni Totali: {shares}")
            self.shares_result.pack(fill='x', pady=2)
            
            self.result_20.config(text=f"📊 20%: {shares_20} azioni → Ne mancano {remaining_20}")
            self.result_20.pack(fill='x', pady=1)
            
            self.result_30.config(text=f"📊 30%: {shares_30} azioni → Ne mancano {remaining_30}")
            self.result_30.pack(fill='x', pady=1)
            
            self.result_50.config(text=f"📊 50%: {shares_50} azioni → Ne mancano {remaining_50}")
            self.result_50.pack(fill='x', pady=1)
            
        except Exception as e:
            messagebox.showerror("Errore", "Errore nel calcolo. Verifica i valori inseriti.")
            
    def reset(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
            
        self.clear_results()
        
        # Hide result labels
        for label in [self.shares_result, self.result_20, self.result_30, self.result_50]:
            label.pack_forget()
            
    def clear_results(self):
        self.dollar_result.config(text="", fg="black")
        self.percentage_result.config(text="", fg="black")
        self.warning_label.config(text="", fg="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = PositionCalculator(root)
    root.mainloop()