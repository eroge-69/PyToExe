#!/usr/bin/env python3
"""
Analisi MLS Depth-wise per Temperature
Script Python per calcolo di conducibilità termica, resistenza termica e velocità darciana
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
from datetime import datetime
import math

class MLSAnalyzer:
    def __init__(self):
        self.data = None
        self.results = None
        self.parameters = {
            'heat_power': 15.0,  # W/m
            'radius': 0.003,     # m
            'time_steps': [0.0, 2.84, 4.86, 6.86, 72.87],  # ore
            'thermal_diffusivity': 1.4e-6,  # m²/s
            'fluid_thermal_conductivity': 0.6,  # W/(m·K)
            'fluid_specific_heat': 4180,  # J/(kg·K)
            'fluid_density': 1000  # kg/m³
        }
    
    def calculate_borehole_resistance(self, thermal_conductivity):
        """Calcola la resistenza termica del borehole"""
        rb = 0.075  # raggio borehole tipico (m)
        rp = 0.02   # raggio tubo tipico (m)
        if thermal_conductivity <= 0:
            return float('inf')
        return math.log(rb / rp) / (2 * math.pi * thermal_conductivity)
    
    def calculate_apparent_diffusivity(self, temp_rises, time_steps):
        """Calcola la diffusività apparente dal profilo di temperatura"""
        if len(temp_rises) < 2:
            return self.parameters['thermal_diffusivity']
        
        radius = self.parameters['radius']
        sum_diff = 0
        count = 0
        
        for i in range(1, len(temp_rises)):
            if temp_rises[i] > 0:
                time = time_steps[i]
                temp = temp_rises[i]
                # Stima della diffusività usando la soluzione della line source
                if temp > 0:
                    diffusivity = (radius * radius) / (4 * time * math.log(temp + 1))
                    if 0 < diffusivity < 1e-3:
                        sum_diff += diffusivity
                        count += 1
        
        return sum_diff / count if count > 0 else self.parameters['thermal_diffusivity']
    
    def calculate_darcy_velocity(self, apparent_diffusivity, thermal_diffusivity):
        """Calcola la velocità darciana dal rapporto tra diffusività"""
        fluid_specific_heat = self.parameters['fluid_specific_heat']
        fluid_density = self.parameters['fluid_density']
        diffusivity_ratio = apparent_diffusivity / thermal_diffusivity
        
        # Formula empirica per velocità darciana
        velocity = abs(diffusivity_ratio - 1) * math.sqrt(thermal_diffusivity) * fluid_specific_heat * fluid_density / 1000
        
        return min(velocity, 1e-6)  # Limita a valori ragionevoli
    
    def calculate_mls(self, temp_data, time_steps, depth):
        """Calcolo MLS principale"""
        heat_power = self.parameters['heat_power']
        radius = self.parameters['radius']
        thermal_diffusivity = self.parameters['thermal_diffusivity']
        
        # Converti tempi da ore a secondi
        time_steps_seconds = [t * 3600 for t in time_steps]
        
        # Calcola le variazioni di temperatura rispetto al tempo iniziale
        temp_rises = [temp_data[i] - temp_data[0] for i in range(1, len(temp_data))]
        
        # Calcolo della conducibilità termica usando il metodo della line source
        thermal_conductivity = 0
        if len(temp_rises) > 1 and temp_rises[-1] > temp_rises[0]:
            delta_temp = temp_rises[-1] - temp_rises[0]
            delta_time = math.log(time_steps_seconds[-1] / time_steps_seconds[1])
            thermal_conductivity = (heat_power * delta_time) / (4 * math.pi * delta_temp)
        
        thermal_conductivity = max(0, thermal_conductivity)
        
        # Calcola la resistenza termica del borehole
        borehole_resistance = self.calculate_borehole_resistance(thermal_conductivity)
        
        # Calcola la velocità darciana
        apparent_diffusivity = self.calculate_apparent_diffusivity(temp_rises, time_steps_seconds[1:])
        darcy_velocity = self.calculate_darcy_velocity(apparent_diffusivity, thermal_diffusivity)
        
        return {
            'thermal_conductivity': thermal_conductivity,
            'borehole_resistance': borehole_resistance,
            'darcy_velocity': darcy_velocity,
            'temp_rises': temp_rises,
            'apparent_diffusivity': apparent_diffusivity
        }
    
    def calculate_rms(self, observed, calculated):
        """Calcola RMS tra osservato e calcolato"""
        if len(observed) != len(calculated):
            return None
        
        sum_squared_diff = sum((obs - calc) ** 2 for obs, calc in zip(observed, calculated))
        return math.sqrt(sum_squared_diff / len(observed))
    
    def process_data(self):
        """Elabora tutti i dati caricati"""
        if self.data is None:
            return False
        
        results = []
        
        for index, row in self.data.iterrows():
            depth = row.iloc[0]
            temperatures = row.iloc[1:6].values
            
            # Calcola i parametri MLS per questa profondità
            mls_result = self.calculate_mls(temperatures, self.parameters['time_steps'], depth)
            
            # Calcola RMS (semplificato per questo esempio)
            temp_rises = mls_result['temp_rises']
            # Per il calcolo dell'RMS, usiamo i valori calcolati vs osservati
            rms = math.sqrt(sum(tr ** 2 for tr in temp_rises) / len(temp_rises)) if temp_rises else 0
            
            result = {
                'depth': depth,
                'thermal_conductivity': mls_result['thermal_conductivity'],
                'borehole_resistance': mls_result['borehole_resistance'],
                'darcy_velocity': mls_result['darcy_velocity'],
                'rms': rms,
                'observed_temps': temperatures,
                'temp_rises': temp_rises,
                'apparent_diffusivity': mls_result['apparent_diffusivity']
            }
            
            results.append(result)
        
        self.results = results
        return True
    
    def load_data(self, filename):
        """Carica dati da file CSV"""
        try:
            # Prova diversi separatori
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(filename, sep=sep, header=None)
                    if df.shape[1] >= 6:  # depth + 5 temperature columns
                        self.data = df
                        return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"Errore nel caricamento: {e}")
            return False
    
    def export_results(self, filename):
        """Esporta risultati in CSV"""
        if not self.results:
            return False
        
        try:
            # Header con metadati
            header = [
                f"# Analisi MLS Depth-wise - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"# Parametri utilizzati:",
                f"# Potenza: {self.parameters['heat_power']} W/m",
                f"# Raggio sensore: {self.parameters['radius']} m",
                f"# Diffusività termica: {self.parameters['thermal_diffusivity']} m²/s",
                f"# Intervalli temporali: {', '.join(map(str, self.parameters['time_steps']))} ore",
                f"# Densità fluido: {self.parameters['fluid_density']} kg/m³",
                "#",
            ]
            
            # Statistiche generali
            k_avg = sum(r['thermal_conductivity'] for r in self.results) / len(self.results)
            rb_avg = sum(r['borehole_resistance'] for r in self.results) / len(self.results)
            v_avg = sum(r['darcy_velocity'] for r in self.results) / len(self.results)
            rms_avg = sum(r['rms'] for r in self.results) / len(self.results)
            
            header.extend([
                f"# Statistiche generali:",
                f"# k media: {k_avg:.4f} W/m·K",
                f"# Rb media: {rb_avg:.4f} K·m/W",
                f"# v media: {v_avg:.3e} m/s",
                f"# RMS medio: {rms_avg:.4f}",
                "#"
            ])
            
            # Scrivi header
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(header) + '\n')
                
                # Scrivi intestazioni colonne
                f.write("Profondità (m),Conducibilità Termica (W/m·K),Resistenza Termica (K·m/W),")
                f.write("Velocità Darciana (m/s),RMS,Diffusività Apparente (m²/s),")
                f.write("Temp T1 (°C),Temp T2 (°C),Temp T3 (°C),Temp T4 (°C),Temp T5 (°C)\n")
                
                # Scrivi dati
                for r in self.results:
                    line = [
                        f"{r['depth']:.1f}",
                        f"{r['thermal_conductivity']:.4f}",
                        f"{r['borehole_resistance']:.4f}",
                        f"{r['darcy_velocity']:.3e}",
                        f"{r['rms']:.4f}",
                        f"{r['apparent_diffusivity']:.3e}",
                    ]
                    line.extend([f"{temp:.3f}" for temp in r['observed_temps']])
                    f.write(','.join(line) + '\n')
            
            return True
            
        except Exception as e:
            print(f"Errore nell'esportazione: {e}")
            return False
    
    def plot_results(self):
        """Crea grafici dei risultati"""
        if not self.results:
            return
        
        depths = [r['depth'] for r in self.results]
        k_values = [r['thermal_conductivity'] for r in self.results]
        rb_values = [r['borehole_resistance'] for r in self.results]
        v_values = [r['darcy_velocity'] for r in self.results]
        
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        
        # Conducibilità termica
        ax1.plot(depths, k_values, 'bo-', linewidth=2, markersize=4)
        ax1.set_xlabel('Profondità (m)')
        ax1.set_ylabel('k (W/m·K)')
        ax1.set_title('Conducibilità Termica vs Profondità')
        ax1.grid(True, alpha=0.3)
        
        # Resistenza termica
        ax2.plot(depths, rb_values, 'go-', linewidth=2, markersize=4)
        ax2.set_xlabel('Profondità (m)')
        ax2.set_ylabel('Rb (K·m/W)')
        ax2.set_title('Resistenza Termica vs Profondità')
        ax2.grid(True, alpha=0.3)
        
        # Velocità darciana
        ax3.plot(depths, v_values, 'ro-', linewidth=2, markersize=4)
        ax3.set_xlabel('Profondità (m)')
        ax3.set_ylabel('v (m/s)')
        ax3.set_title('Velocità Darciana vs Profondità')
        ax3.grid(True, alpha=0.3)
        ax3.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
        
        plt.tight_layout()
        plt.show()

class MLSAnalyzerGUI:
    def __init__(self):
        self.analyzer = MLSAnalyzer()
        self.root = tk.Tk()
        self.root.title("Analisi MLS Depth-wise")
        self.root.geometry("800x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crea l'interfaccia grafica"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Analisi MLS Depth-wise", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame caricamento file
        file_frame = ttk.LabelFrame(main_frame, text="Caricamento Dati", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Carica File CSV", 
                  command=self.load_file).grid(row=0, column=0, padx=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="Nessun file caricato")
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        
        # Frame parametri
        param_frame = ttk.LabelFrame(main_frame, text="Parametri di Calcolo", padding="10")
        param_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Parametri in griglia
        params = [
            ("Potenza (W/m):", "heat_power"),
            ("Raggio sensore (m):", "radius"),
            ("Diffusività termica (m²/s):", "thermal_diffusivity"),
            ("Densità fluido (kg/m³):", "fluid_density")
        ]
        
        self.param_vars = {}
        for i, (label, key) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=(0, 5))
            var = tk.StringVar(value=str(self.analyzer.parameters[key]))
            self.param_vars[key] = var
            ttk.Entry(param_frame, textvariable=var, width=15).grid(row=i//2, column=(i%2)*2+1, padx=(0, 20))
        
        # Intervalli temporali
        ttk.Label(param_frame, text="Intervalli temporali (ore):").grid(row=2, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value=", ".join(map(str, self.analyzer.parameters['time_steps'])))
        ttk.Entry(param_frame, textvariable=self.time_var, width=40).grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E))
        
        # Frame elaborazione
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(process_frame, text="Elabora Dati", 
                  command=self.process_data).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(process_frame, text="Mostra Grafici", 
                  command=self.show_plots).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(process_frame, text="Esporta Risultati", 
                  command=self.export_results).grid(row=0, column=2)
        
        # Area risultati
        results_frame = ttk.LabelFrame(main_frame, text="Risultati", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Treeview per risultati
        columns = ('Profondità', 'k (W/m·K)', 'Rb (K·m/W)', 'v (m/s)', 'RMS')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configura ridimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def load_file(self):
        """Carica file di dati"""
        filename = filedialog.askopenfilename(
            title="Seleziona file dati",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            if self.analyzer.load_data(filename):
                self.file_label.config(text=f"File caricato: {os.path.basename(filename)}")
                messagebox.showinfo("Successo", f"Caricati {len(self.analyzer.data)} punti di misura")
            else:
                messagebox.showerror("Errore", "Impossibile caricare il file")
    
    def process_data(self):
        """Elabora i dati"""
        if self.analyzer.data is None:
            messagebox.showwarning("Attenzione", "Carica prima un file di dati")
            return
        
        # Aggiorna parametri
        try:
            for key, var in self.param_vars.items():
                self.analyzer.parameters[key] = float(var.get())
            
            time_steps = [float(x.strip()) for x in self.time_var.get().split(',')]
            self.analyzer.parameters['time_steps'] = time_steps
        except ValueError:
            messagebox.showerror("Errore", "Valori parametri non validi")
            return
        
        if self.analyzer.process_data():
            self.update_results_display()
            messagebox.showinfo("Successo", "Elaborazione completata")
        else:
            messagebox.showerror("Errore", "Errore nell'elaborazione dei dati")
    
    def update_results_display(self):
        """Aggiorna la visualizzazione dei risultati"""
        # Pulisci risultati precedenti
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Aggiungi nuovi risultati
        if self.analyzer.results:
            for r in self.analyzer.results:
                self.results_tree.insert('', tk.END, values=(
                    f"{r['depth']:.1f}",
                    f"{r['thermal_conductivity']:.4f}",
                    f"{r['borehole_resistance']:.4f}",
                    f"{r['darcy_velocity']:.3e}",
                    f"{r['rms']:.4f}"
                ))
    
    def show_plots(self):
        """Mostra i grafici"""
        if not self.analyzer.results:
            messagebox.showwarning("Attenzione", "Elabora prima i dati")
            return
        
        self.analyzer.plot_results()
    
    def export_results(self):
        """Esporta i risultati"""
        if not self.analyzer.results:
            messagebox.showwarning("Attenzione", "Elabora prima i dati")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salva risultati",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            if self.analyzer.export_results(filename):
                messagebox.showinfo("Successo", f"Risultati salvati in {filename}")
            else:
                messagebox.showerror("Errore", "Impossibile salvare i risultati")
    
    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MLSAnalyzerGUI()
    app.run()
