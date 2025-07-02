import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class JDXReader:
    """Classe per leggere file JCAMP-DX (.jdx)"""
    
    def __init__(self):
        self.title = ""
        self.x_units = ""
        self.y_units = ""
        self.x_data = []
        self.y_data = []
        self.x_factor = 1.0
        self.y_factor = 1.0
        self.first_x = 0.0
        self.last_x = 0.0
        self.n_points = 0
        
    def read_jdx_file(self, filepath):
        """Legge un file JDX e estrae i dati spettrali"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Estrai i metadati
            self._extract_metadata(content)
            
            # Estrai i dati spettrali
            self._extract_spectral_data(content)
            
            return True
            
        except Exception as e:
            print(f"Errore nella lettura del file: {e}")
            return False
    
    def _extract_metadata(self, content):
        """Estrae i metadati dal file JDX"""
        # Titolo
        title_match = re.search(r'##TITLE=(.+)', content, re.IGNORECASE)
        if title_match:
            self.title = title_match.group(1).strip()
        
        # Unità degli assi
        xunits_match = re.search(r'##XUNITS=(.+)', content, re.IGNORECASE)
        if xunits_match:
            self.x_units = xunits_match.group(1).strip()
        
        yunits_match = re.search(r'##YUNITS=(.+)', content, re.IGNORECASE)
        if yunits_match:
            self.y_units = yunits_match.group(1).strip()
        
        # Fattori di scala
        xfactor_match = re.search(r'##XFACTOR=(.+)', content, re.IGNORECASE)
        if xfactor_match:
            self.x_factor = float(xfactor_match.group(1).strip())
        
        yfactor_match = re.search(r'##YFACTOR=(.+)', content, re.IGNORECASE)
        if yfactor_match:
            self.y_factor = float(yfactor_match.group(1).strip())
        
        # Valori estremi e numero di punti
        firstx_match = re.search(r'##FIRSTX=(.+)', content, re.IGNORECASE)
        if firstx_match:
            self.first_x = float(firstx_match.group(1).strip())
        
        lastx_match = re.search(r'##LASTX=(.+)', content, re.IGNORECASE)
        if lastx_match:
            self.last_x = float(lastx_match.group(1).strip())
        
        npoints_match = re.search(r'##NPOINTS=(.+)', content, re.IGNORECASE)
        if npoints_match:
            self.n_points = int(npoints_match.group(1).strip())
    
    def _extract_spectral_data(self, content):
        """Estrae i dati spettrali dal file JDX"""
        # Cerca la sezione dei dati
        data_start = content.find('##XYDATA')
        if data_start == -1:
            data_start = content.find('##XYPOINTS')
        if data_start == -1:
            data_start = content.find('##PEAK TABLE')
        
        if data_start != -1:
            data_section = content[data_start:]
            data_end = data_section.find('##END')
            if data_end != -1:
                data_section = data_section[:data_end]
            
            # Estrai le linee di dati
            lines = data_section.split('\n')[1:]  # Salta la prima linea con il tag
            
            x_data = []
            y_data = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('##'):
                    # Rimuovi eventuali caratteri di controllo
                    line = re.sub(r'[^\d\s\.\-\+eE,]', '', line)
                    
                    # Prova diversi formati di separatori
                    if ',' in line:
                        parts = line.split(',')
                    else:
                        parts = line.split()
                    
                    # Estrai coppie X,Y
                    for i in range(0, len(parts)-1, 2):
                        try:
                            x_val = float(parts[i]) * self.x_factor
                            y_val = float(parts[i+1]) * self.y_factor
                            x_data.append(x_val)
                            y_data.append(y_val)
                        except (ValueError, IndexError):
                            continue
            
            # Converti in array numpy
            x_data = np.array(x_data)
            y_data = np.array(y_data)
            
            # ORDINA I DATI per X crescente per evitare linee che vanno avanti e indietro
            if len(x_data) > 0:
                sorted_indices = np.argsort(x_data)
                self.x_data = x_data[sorted_indices]
                self.y_data = y_data[sorted_indices]
            else:
                self.x_data = x_data
                self.y_data = y_data
            
            # Se non ci sono dati estratti, prova un approccio alternativo
            if len(self.x_data) == 0 and self.n_points > 0:
                self._generate_x_data_from_metadata()

    def _generate_x_data_from_metadata(self):
        """Genera i dati X dai metadati se non sono presenti nel file"""
        if self.n_points > 0 and self.first_x != 0 and self.last_x != 0:
            self.x_data = np.linspace(self.first_x, self.last_x, self.n_points)

class IRSpectrumViewer:
    """Interfaccia grafica per visualizzare spettri infrarossi"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Visualizzatore Spettri Infrarossi")
        self.root.geometry("800x600")
        
        self.jdx_reader = JDXReader()
        self.show_absorbance = tk.BooleanVar(value=False)  # Default: Trasmittanza
        self.setup_gui()
        
    def setup_gui(self):
        """Configura l'interfaccia grafica"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bottone per caricare file
        load_button = ttk.Button(main_frame, text="Carica File JDX", 
                                command=self.load_file)
        load_button.grid(row=0, column=0, pady=10)
        
        # Etichetta per info file
        self.file_info = ttk.Label(main_frame, text="Nessun file caricato")
        self.file_info.grid(row=1, column=0, pady=5)
        
        # Frame per le opzioni
        options_frame = ttk.LabelFrame(main_frame, text="Opzioni di visualizzazione", padding="10")
        options_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Checkbox per assorbanza/trasmittanza
        absorbance_check = ttk.Checkbutton(options_frame, 
                                          text="Visualizza Assorbanza (A = -log₁₀(T))",
                                          variable=self.show_absorbance)
        absorbance_check.grid(row=0, column=0, sticky=tk.W)
        
        # Bottone per visualizzare grafico
        self.plot_button = ttk.Button(main_frame, text="Visualizza Spettro", 
                                     command=self.plot_spectrum, state='disabled')
        self.plot_button.grid(row=3, column=0, pady=10)
        
        # Configurazione ridimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(0, weight=1)
        
    def convert_to_absorbance(self, transmittance_data):
        """Converte dati di trasmittanza in assorbanza usando A = -log₁₀(T)"""
        # Normalizza i dati di trasmittanza (assicurati che siano tra 0 e 1)
        t_data = transmittance_data.copy()
        
        # Se i dati sono in percentuale (0-100), convertili in frazione (0-1)
        if np.max(t_data) > 1.0:
            t_data = t_data / 100.0
        
        # Evita valori <= 0 che causerebbero errori nel logaritmo
        t_data = np.where(t_data <= 0, 1e-6, t_data)  # Sostituisce valori <= 0 con 1e-6
        t_data = np.where(t_data > 1.0, 1.0, t_data)  # Limita valori > 1.0
        
        # Calcola assorbanza: A = -log₁₀(T)
        absorbance = -np.log10(t_data)
        
        return absorbance
    def load_file(self):
        """Carica un file JDX"""
        file_path = filedialog.askopenfilename(
            title="Seleziona file JDX",
            filetypes=[("File JDX", "*.jdx"), ("Tutti i file", "*.*")]
        )
        
        if file_path:
            if self.jdx_reader.read_jdx_file(file_path):
                filename = Path(file_path).name
                self.file_info.config(text=f"File caricato: {filename}")
                self.plot_button.config(state='normal')
                
                # Mostra info sul file
                info_text = f"Titolo: {self.jdx_reader.title}\n"
                info_text += f"Punti dati: {len(self.jdx_reader.x_data)}"
                messagebox.showinfo("File caricato", info_text)
            else:
                messagebox.showerror("Errore", "Impossibile leggere il file JDX")
    
    def plot_spectrum(self):
        """Visualizza lo spettro infrarosso"""
        if len(self.jdx_reader.x_data) == 0:
            messagebox.showwarning("Attenzione", "Nessun dato da visualizzare")
            return
        
        # Crea il grafico con sfondo grigio scuro
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2e2e2e')
        ax.set_facecolor('#2e2e2e')
        
        # Verifica se i dati sono ordinati, altrimenti ordinali
        x_data = self.jdx_reader.x_data
        y_data = self.jdx_reader.y_data
        
        if len(x_data) > 1:
            # Controlla se i dati sono già ordinati
            if not np.all(x_data[:-1] <= x_data[1:]):
                # Ordina i dati se non sono ordinati
                sorted_indices = np.argsort(x_data)
                x_data = x_data[sorted_indices]
                y_data = y_data[sorted_indices]
        
        # Determina se mostrare assorbanza o trasmittanza
        if self.show_absorbance.get():
            # Converti in assorbanza
            y_plot_data = self.convert_to_absorbance(y_data)
            y_label = "Assorbanza (A)"
        else:
            # Usa trasmittanza originale
            y_plot_data = y_data
            y_label = f'Trasmittanza ({self.jdx_reader.y_units or "%"})'
        
        # Curva azzurra liscia - usa plot normale per connettere tutti i punti
        plt.plot(x_data, y_plot_data, 
                color='#00BFFF', linewidth=1.5, alpha=0.9, 
                linestyle='-', marker='', markersize=0, 
                solid_capstyle='round', solid_joinstyle='round')
        
        # Configurazione del grafico per spettri IR
        plt.xlabel(f'Numero d\'onda ({self.jdx_reader.x_units or "cm⁻¹"})', 
                  color='white', fontsize=12)
        plt.ylabel(y_label, color='white', fontsize=12)
        
        # Titolo con indicazione del tipo di dati
        title_suffix = " (Assorbanza)" if self.show_absorbance.get() else " (Trasmittanza)"
        plt.title((self.jdx_reader.title or "Spettro Infrarosso") + title_suffix, 
                 color='white', fontsize=14, fontweight='bold')
        
        # Inverti l'asse X (tipico per spettri IR)
        plt.gca().invert_xaxis()
        
        # Per l'assorbanza, potresti voler invertire anche l'asse Y (opzionale)
        # if self.show_absorbance.get():
        #     plt.gca().invert_yaxis()
        
        # Personalizza assi e griglia
        ax.tick_params(colors='white', which='both')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        # Griglia sottile
        plt.grid(True, alpha=0.2, color='gray', linestyle='--', linewidth=0.5)
        
        # Layout
        plt.tight_layout()
        
        # Mostra il grafico
        plt.show()
    
    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()

def plot_jdx_spectrum(filepath, show_absorbance=False):
    """Funzione standalone per plottare uno spettro da file JDX"""
    reader = JDXReader()
    if reader.read_jdx_file(filepath):
        # Sfondo grigio scuro
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#2e2e2e')
        ax.set_facecolor('#2e2e2e')
        
        # Verifica se i dati sono ordinati, altrimenti ordinali
        x_data = reader.x_data
        y_data = reader.y_data
        
        if len(x_data) > 1:
            # Controlla se i dati sono già ordinati
            if not np.all(x_data[:-1] <= x_data[1:]):
                # Ordina i dati se non sono ordinati
                sorted_indices = np.argsort(x_data)
                x_data = x_data[sorted_indices]
                y_data = y_data[sorted_indices]
        
        # Determina se mostrare assorbanza o trasmittanza
        if show_absorbance:
            # Converti in assorbanza
            viewer = IRSpectrumViewer()  # Crea un'istanza temporanea per accedere al metodo
            y_plot_data = viewer.convert_to_absorbance(y_data)
            y_label = "Assorbanza (A)"
            title_suffix = " (Assorbanza)"
        else:
            # Usa trasmittanza originale
            y_plot_data = y_data
            y_label = f'Trasmittanza ({reader.y_units or "%"})'
            title_suffix = " (Trasmittanza)"
        
        # Curva azzurra liscia
        plt.plot(x_data, y_plot_data, 
                color='#00BFFF', linewidth=1.5, alpha=0.9, 
                linestyle='-', marker='', markersize=0,
                solid_capstyle='round', solid_joinstyle='round')
        
        plt.xlabel(f'Numero d\'onda ({reader.x_units or "cm⁻¹"})', 
                  color='white', fontsize=12)
        plt.ylabel(y_label, color='white', fontsize=12)
        plt.title((reader.title or "Spettro Infrarosso") + title_suffix, 
                 color='white', fontsize=14, fontweight='bold')
        
        plt.gca().invert_xaxis()
        
        # Personalizza assi e griglia
        ax.tick_params(colors='white', which='both')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        plt.grid(True, alpha=0.2, color='gray', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        plt.show()
    else:
        print("Errore nella lettura del file JDX")

if __name__ == "__main__":
    # Avvia l'interfaccia grafica
    app = IRSpectrumViewer()
    app.run()
    
    # Esempi di uso diretto:
    # plot_jdx_spectrum("percorso/al/tuo/file.jdx")  # Trasmittanza
    # plot_jdx_spectrum("percorso/al/tuo/file.jdx", show_absorbance=True)  # Assorbanza