import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.special import expi
import pandas as pd
from typing import Tuple, Dict, Optional

class TRT_MLS_Analyzer:
    """
    Analizzatore per Thermal Response Test (TRT) basato sulla teoria 
    Moving Line Source (MLS) per sonde geotermiche.
    """
    
    def __init__(self):
        self.data = None
        self.results = {}
        
    def load_data(self, filepath: str = None, time_col: str = 'time', 
                  temp_col: str = 'temperature', power_col: str = 'power'):
        """
        Carica i dati del TRT da file CSV o permette inserimento manuale.
        
        Args:
            filepath: percorso del file CSV (opzionale)
            time_col: nome colonna tempo [h]
            temp_col: nome colonna temperatura [°C]
            power_col: nome colonna potenza [W]
        """
        if filepath:
            try:
                self.data = pd.read_csv(filepath)
                self.data = self.data.rename(columns={
                    time_col: 'time',
                    temp_col: 'temperature', 
                    power_col: 'power'
                })
                print(f"Dati caricati: {len(self.data)} punti")
            except Exception as e:
                print(f"Errore nel caricamento: {e}")
        else:
            print("Usa set_manual_data() per inserire i dati manualmente")
    
    def set_manual_data(self, time_hours, temperature_celsius, power_watts):
        """
        Imposta i dati manualmente.
        
        Args:
            time_hours: array dei tempi in ore
            temperature_celsius: array delle temperature in °C
            power_watts: array delle potenze in W (o valore singolo se costante)
        """
        self.data = pd.DataFrame({
            'time': np.array(time_hours),
            'temperature': np.array(temperature_celsius),
            'power': np.array(power_watts) if hasattr(power_watts, '__len__') else np.full(len(time_hours), power_watts)
        })
        print(f"Dati impostati: {len(self.data)} punti")
    
    def mls_temperature_response(self, t: np.ndarray, q: float, lambda_eff: float, 
                                alpha: float, H: float, rb: float) -> np.ndarray:
        """
        Calcola la risposta termica secondo il modello Moving Line Source.
        
        Args:
            t: tempo [h]
            q: flusso termico per unità di lunghezza [W/m]
            lambda_eff: conducibilità termica effettiva [W/mK]
            alpha: diffusività termica [m²/s]
            H: lunghezza della sonda [m]
            rb: raggio della sonda [m]
            
        Returns:
            Delta T rispetto alla temperatura iniziale [K]
        """
        # Conversione tempo da ore a secondi
        t_sec = t * 3600
        
        # Evita valori troppo piccoli di tempo
        t_sec = np.maximum(t_sec, 1e-6)
        
        # Parametro adimensionale
        tau = alpha * t_sec / (rb**2)
        
        # Funzione G per MLS (approssimazione per grandi tempi)
        # Per tau >> 1: G ≈ ln(tau) + gamma - ln(4) + O(1/tau)
        gamma_euler = 0.5772156649015329  # costante di Eulero
        
        # Calcolo della funzione G del modello MLS
        G = np.zeros_like(tau)
        
        for i, tau_val in enumerate(tau):
            if tau_val > 10:  # Approssimazione per grandi tempi
                G[i] = np.log(tau_val) + gamma_euler - np.log(4)
            else:  # Calcolo più accurato per tempi piccoli
                # Integrazione numerica della funzione esponenziale
                u_max = min(tau_val, 10)
                u_vals = np.linspace(1e-8, u_max, 1000)
                integrand = (1 - np.exp(-u_vals)) / u_vals
                G[i] = np.trapz(integrand, u_vals)
        
        # Temperatura secondo MLS
        delta_T = (q / (4 * np.pi * lambda_eff)) * G
        
        return delta_T
    
    def objective_function(self, params: np.ndarray, t: np.ndarray, 
                          T_measured: np.ndarray, q: float, H: float, rb: float) -> float:
        """
        Funzione obiettivo per l'ottimizzazione dei parametri.
        
        Args:
            params: [lambda_eff, alpha, T0] parametri da ottimizzare
            t: tempo [h]
            T_measured: temperatura misurata [°C]
            q: flusso termico per unità di lunghezza [W/m]
            H: lunghezza sonda [m]
            rb: raggio sonda [m]
            
        Returns:
            Somma dei quadrati dei residui
        """
        lambda_eff, alpha, T0 = params
        
        # Vincoli fisici sui parametri
        if lambda_eff <= 0 or alpha <= 0:
            return 1e10
            
        try:
            T_calculated = T0 + self.mls_temperature_response(t, q, lambda_eff, alpha, H, rb)
            residuals = T_measured - T_calculated
            return np.sum(residuals**2)
        except:
            return 1e10
    
    def analyze_trt(self, H: float, rb: float, initial_guess: Dict = None) -> Dict:
        """
        Esegue l'analisi TRT con il modello MLS.
        
        Args:
            H: lunghezza della sonda [m]
            rb: raggio della sonda [m]
            initial_guess: valori iniziali per l'ottimizzazione
                         {'lambda_eff': W/mK, 'alpha': m²/s, 'T0': °C}
        
        Returns:
            Dizionario con i risultati dell'analisi
        """
        if self.data is None:
            raise ValueError("Nessun dato caricato. Usa load_data() o set_manual_data()")
        
        # Estrai i dati
        t = self.data['time'].values
        T = self.data['temperature'].values
        P = self.data['power'].values
        
        # Calcola il flusso termico per unità di lunghezza
        q = np.mean(P) / H  # W/m
        
        # Valori iniziali per l'ottimizzazione
        if initial_guess is None:
            initial_guess = {
                'lambda_eff': 2.5,    # W/mK (tipico per terreno)
                'alpha': 1e-6,        # m²/s (tipico per terreno)
                'T0': T[0]           # temperatura iniziale
            }
        
        # Parametri iniziali
        x0 = [initial_guess['lambda_eff'], initial_guess['alpha'], initial_guess['T0']]
        
        # Bounds per i parametri
        bounds = [(0.5, 10.0),      # lambda_eff [W/mK]
                  (1e-8, 1e-4),     # alpha [m²/s]
                  (T[0]-5, T[0]+5)] # T0 [°C]
        
        print("Inizio ottimizzazione parametri MLS...")
        
        # Ottimizzazione
        result = minimize(
            self.objective_function,
            x0,
            args=(t, T, q, H, rb),
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        if not result.success:
            print(f"Attenzione: ottimizzazione non convergente - {result.message}")
        
        # Estrai parametri ottimali
        lambda_eff_opt, alpha_opt, T0_opt = result.x
        
        # Calcola la temperatura teorica
        T_theoretical = T0_opt + self.mls_temperature_response(t, q, lambda_eff_opt, alpha_opt, H, rb)
        
        # Calcola metriche di qualità del fit
        residuals = T - T_theoretical
        rmse = np.sqrt(np.mean(residuals**2))
        r_squared = 1 - np.sum(residuals**2) / np.sum((T - np.mean(T))**2)
        
        # Salva i risultati
        self.results = {
            'lambda_eff': lambda_eff_opt,      # Conducibilità termica [W/mK]
            'alpha': alpha_opt,                # Diffusività termica [m²/s]
            'T0': T0_opt,                      # Temperatura iniziale [°C]
            'q': q,                            # Flusso termico [W/m]
            'H': H,                            # Lunghezza sonda [m]
            'rb': rb,                          # Raggio sonda [m]
            'rmse': rmse,                      # Errore quadratico medio
            'r_squared': r_squared,            # Coefficiente di determinazione
            'T_measured': T,                   # Temperature misurate
            'T_theoretical': T_theoretical,    # Temperature teoriche
            'time': t,                         # Tempi
            'residuals': residuals,            # Residui
            'power_avg': np.mean(P)            # Potenza media
        }
        
        print(f"\nRisultati analisi MLS:")
        print(f"Conducibilità termica efficace: {lambda_eff_opt:.3f} W/mK")
        print(f"Diffusività termica: {alpha_opt:.2e} m²/s")
        print(f"Temperatura iniziale: {T0_opt:.2f} °C")
        print(f"RMSE: {rmse:.3f} K")
        print(f"R²: {r_squared:.4f}")
        
        return self.results
    
    def plot_results(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Genera grafici dei risultati dell'analisi.
        
        Args:
            figsize: dimensioni della figura
        """
        if not self.results:
            print("Nessun risultato disponibile. Esegui prima analyze_trt()")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # Grafico 1: Temperature misurate vs teoriche
        ax1.plot(self.results['time'], self.results['T_measured'], 'bo-', 
                label='Misurate', markersize=4, linewidth=1)
        ax1.plot(self.results['time'], self.results['T_theoretical'], 'r-', 
                label='Modello MLS', linewidth=2)
        ax1.set_xlabel('Tempo [h]')
        ax1.set_ylabel('Temperatura [°C]')
        ax1.set_title('Confronto Temperature: Misurate vs Modello MLS')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Grafico 2: Residui
        ax2.plot(self.results['time'], self.results['residuals'], 'go-', 
                markersize=4, linewidth=1)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Tempo [h]')
        ax2.set_ylabel('Residui [K]')
        ax2.set_title(f'Residui (RMSE = {self.results["rmse"]:.3f} K)')
        ax2.grid(True, alpha=0.3)
        
        # Grafico 3: Distribuzione residui
        ax3.hist(self.results['residuals'], bins=20, alpha=0.7, color='skyblue', 
                edgecolor='black')
        ax3.set_xlabel('Residui [K]')
        ax3.set_ylabel('Frequenza')
        ax3.set_title('Distribuzione dei Residui')
        ax3.grid(True, alpha=0.3)
        
        # Grafico 4: Parametri identificati
        params = [
            ('λ_eff [W/mK]', self.results['lambda_eff'], ':.3f'),
            ('α [m²/s]', self.results['alpha'], ':.2e'),
            ('T₀ [°C]', self.results['T0'], ':.2f'),
            ('q [W/m]', self.results['q'], ':.1f'),
            ('R²', self.results['r_squared'], ':.4f')
        ]
        
        ax4.axis('off')
        y_pos = 0.9
        ax4.text(0.1, y_pos, 'Parametri Identificati:', fontsize=14, fontweight='bold')
        
        for param_name, value, fmt in params:
            y_pos -= 0.15
            ax4.text(0.1, y_pos, f'{param_name}: {value{fmt}}', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def export_results(self, filename: str):
        """
        Esporta i risultati in un file CSV.
        
        Args:
            filename: nome del file di output
        """
        if not self.results:
            print("Nessun risultato disponibile.")
            return
        
        # Crea DataFrame con tutti i dati
        export_data = pd.DataFrame({
            'time_h': self.results['time'],
            'T_measured_C': self.results['T_measured'],
            'T_theoretical_C': self.results['T_theoretical'],
            'residuals_K': self.results['residuals']
        })
        
        # Aggiungi parametri come header
        header_info = [
            f"# Analisi TRT - Modello Moving Line Source",
            f"# Conducibilita termica efficace: {self.results['lambda_eff']:.3f} W/mK",
            f"# Diffusivita termica: {self.results['alpha']:.2e} m2/s",
            f"# Temperatura iniziale: {self.results['T0']:.2f} C",
            f"# Flusso termico: {self.results['q']:.1f} W/m",
            f"# RMSE: {self.results['rmse']:.3f} K",
            f"# R-squared: {self.results['r_squared']:.4f}",
            "#"
        ]
        
        # Salva con header
        with open(filename, 'w') as f:
            for line in header_info:
                f.write(line + '\n')
        
        export_data.to_csv(filename, mode='a', index=False)
        print(f"Risultati esportati in: {filename}")


# Esempio d'uso
if __name__ == "__main__":
    # Crea l'analizzatore
    analyzer = TRT_MLS_Analyzer()
    
    # Esempio con dati simulati
    print("=== ESEMPIO DI UTILIZZO ===")
    print("Generazione dati di esempio...")
    
    # Parametri della sonda
    H = 100.0  # lunghezza sonda [m]
    rb = 0.075  # raggio sonda [m] (150mm diametro)
    
    # Parametri del terreno (valori reali di esempio)
    lambda_true = 2.2  # W/mK
    alpha_true = 1.2e-6  # m²/s
    T0_true = 12.0  # °C
    q_true = 50.0  # W/m
    
    # Genera dati temporali (48 ore di test)
    time_hours = np.linspace(1, 48, 48)
    
    # Genera temperature teoriche + rumore
    T_theoretical = T0_true + analyzer.mls_temperature_response(
        time_hours, q_true, lambda_true, alpha_true, H, rb)
    
    # Aggiungi rumore realistico
    np.random.seed(42)
    noise = np.random.normal(0, 0.1, len(time_hours))
    T_measured = T_theoretical + noise
    
    # Potenza costante
    power_watts = q_true * H
    
    # Imposta i dati
    analyzer.set_manual_data(time_hours, T_measured, power_watts)
    
    # Esegui l'analisi
    print("\nEsecuzione analisi TRT con modello MLS...")
    results = analyzer.analyze_trt(H=H, rb=rb)
    
    # Mostra i grafici
    analyzer.plot_results()
    
    # Esporta i risultati
    analyzer.export_results('risultati_trt_mls.csv')
    
    print("\n=== CONFRONTO CON VALORI VERI ===")
    print(f"Conducibilità - Vero: {lambda_true:.3f}, Stimato: {results['lambda_eff']:.3f} W/mK")
    print(f"Diffusività - Vero: {alpha_true:.2e}, Stimato: {results['alpha']:.2e} m²/s")
    print(f"Errore λ: {abs(lambda_true - results['lambda_eff'])/lambda_true*100:.1f}%")
    print(f"Errore α: {abs(alpha_true - results['alpha'])/alpha_true*100:.1f}%")