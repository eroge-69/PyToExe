import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.optimize import curve_fit
import matplotlib.patches as patches

class MRTAnalyzer:
    def __init__(self):
        self.flip_angles = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90]
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.selected_x = None
        self.selected_y = None
        self.reference_image = None
        self.rect = None
        
        # MRT-Parameter
        self.T_E = 0.003  # Echozeit in Sekunden (3 ms)
        self.T_R = 0.030  # Repetitionszeit in Sekunden (30 ms)
        
        # Figure setup
        self.fig = plt.figure(figsize=(20, 8))
        
        # Subplot für Bildauswahl (links)
        self.ax_image = self.fig.add_subplot(131)
        self.ax_image.set_title('FA5.png - Klicken Sie auf einen Punkt', fontsize=14)
        
        # Subplot für Plot (mitte)
        self.ax_plot = self.fig.add_subplot(132)
        
        # Subplot für Parameter (rechts)
        self.ax_params = self.fig.add_subplot(133)
        self.ax_params.axis('off')
        
        # Referenzbild laden (FA5.png)
        self.load_reference_image()
        
        # Event-Handler für Mausklicks
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        plt.tight_layout()
        plt.show()
    
    def steady_state_signal(self, theta_deg, y_offset, rho_0, T1, T2_star):
        """
        Steady-State-Signalgleichung (Gleichung 18.14) mit Offset
        
        Parameters:
        - theta_deg: Flipwinkel in Grad
        - y_offset: Baseline-Offset
        - rho_0: Protonendichte
        - T1: Longitudinale Relaxationszeit in Sekunden
        - T2_star: Effektive transversale Relaxationszeit in Sekunden
        """
        # Konvertierung zu Radiant
        theta = np.radians(theta_deg)
        
        # E1 berechnen
        E1 = np.exp(-self.T_R / T1)
        
        # Signal mit Offset berechnen
        signal = y_offset + rho_0 * np.sin(theta) * (1 - E1) / (1 - E1 * np.cos(theta)) * np.exp(-self.T_E / T2_star)
        
        return signal
    
    def load_reference_image(self):
        """Lädt das Referenzbild FA5.png"""
        filepath = os.path.join(self.current_dir, "FA5.png")
        
        if os.path.exists(filepath):
            img = Image.open(filepath)
            self.reference_image = img.convert('L')
            img_array = np.array(self.reference_image)
            
            # Bild anzeigen
            self.ax_image.imshow(img_array, cmap='gray')
            self.ax_image.set_xlabel('X-Koordinate')
            self.ax_image.set_ylabel('Y-Koordinate')
            
            # Bildgröße für Validierung speichern
            self.img_height, self.img_width = img_array.shape
        else:
            print(f"Fehler: FA5.png nicht gefunden!")
            plt.close()
    
    def on_click(self, event):
        """Event-Handler für Mausklicks"""
        if event.inaxes == self.ax_image:
            # Koordinaten des Klicks
            x, y = int(event.xdata), int(event.ydata)
            
            # Prüfen ob Klick im gültigen Bereich (mindestens 1 Pixel Abstand zum Rand)
            if 1 <= x < self.img_width - 1 and 1 <= y < self.img_height - 1:
                self.selected_x = x
                self.selected_y = y
                
                # Altes Rechteck entfernen
                if self.rect:
                    self.rect.remove()
                
                # Neues Rechteck zeichnen (3x3 Bereich)
                self.rect = Rectangle((x-1.5, y-1.5), 3, 3, 
                                    linewidth=2, edgecolor='red', 
                                    facecolor='none')
                self.ax_image.add_patch(self.rect)
                
                # Titel aktualisieren
                self.ax_image.set_title(f'FA5.png - Ausgewählter Punkt: ({x}, {y})', 
                                      fontsize=14)
                
                # Analyse durchführen
                self.analyze_region()
                
                # Canvas aktualisieren
                self.fig.canvas.draw()
            else:
                print("Bitte wählen Sie einen Punkt mit mindestens 1 Pixel Abstand zum Rand!")
    
    def analyze_region(self):
        """Analysiert den 3x3 Bereich in allen Bildern"""
        if self.selected_x is None or self.selected_y is None:
            return
        
        mean_values = []
        std_values = []
        valid_angles = []
        
        print(f"\nAnalyse der 3x3 Region um Punkt ({self.selected_x}, {self.selected_y}):")
        print("-" * 60)
        
        # Durch alle Flipwinkel iterieren
        for angle in self.flip_angles:
            filename = f"FA{angle}.png"
            filepath = os.path.join(self.current_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    # Bild laden
                    img = Image.open(filepath).convert('L')
                    img_array = np.array(img)
                    
                    # 3x3 Region extrahieren
                    region = img_array[self.selected_y-1:self.selected_y+2, 
                                     self.selected_x-1:self.selected_x+2]
                    
                    # Mittelwert und Standardabweichung der 9 Pixel berechnen
                    mean_val = np.mean(region)
                    std_val = np.std(region)
                    
                    mean_values.append(mean_val)
                    std_values.append(std_val)
                    valid_angles.append(angle)
                    
                    print(f"{filename}: {mean_val:.2f} ± {std_val:.2f}")
                    
                except Exception as e:
                    print(f"Fehler bei {filename}: {e}")
        
        # Fit durchführen und Plot aktualisieren
        self.fit_and_plot(valid_angles, mean_values, std_values)
    
    def fit_and_plot(self, angles, means, stds):
        """Führt den Fit durch und aktualisiert den Plot"""
        self.ax_plot.clear()
        
        # Daten für Fit vorbereiten
        angles_array = np.array(angles)
        means_array = np.array(means)
        stds_array = np.array(stds)
        
        try:
            # Bessere Startwerte basierend auf den Daten
            max_idx = np.argmax(means_array)
            max_signal = means_array[max_idx]
            min_signal = np.min(means_array)
            
            # Schätzung für Offset (Minimum der Messwerte oder 100)
            y_offset_start = min(100, min_signal * 0.8)
            
            # Startwerte: [y_offset, rho_0, T1, T2*]
            p0 = [y_offset_start,      # y_offset
                  max_signal - y_offset_start,  # rho_0 (angepasst für Offset)
                  0.3,                 # T1 (300ms)
                  0.02]                # T2* (20ms)
            
            # Grenzen mit Offset
            # y_offset: 0 bis min(Messwerte)
            # T1: 50ms - 5000ms
            # T2*: 1ms - 200ms
            bounds = ([0, 0, 0.05, 0.001], 
                     [min_signal, max_signal * 2, 5.0, 0.2])
            
            # Fit mit Gewichtung durchführen
            weights = 1.0 / (stds_array + 1e-6)
            
            popt, pcov = curve_fit(self.steady_state_signal, angles_array, means_array, 
                                 p0=p0, bounds=bounds, sigma=1/weights, absolute_sigma=True,
                                 method='trf', maxfev=5000)
            
            y_offset_fit, rho_0_fit, T1_fit, T2_star_fit = popt
            
            # Standardfehler berechnen
            perr = np.sqrt(np.diag(pcov))
            y_offset_err, rho_0_err, T1_err, T2_star_err = perr
            
            # R² berechnen
            y_pred = self.steady_state_signal(angles_array, *popt)
            ss_res = np.sum((means_array - y_pred)**2)
            ss_tot = np.sum((means_array - np.mean(means_array))**2)
            r_squared = 1 - (ss_res / ss_tot)
            
            # Fit-Kurve berechnen
            angles_fit = np.linspace(0, 90, 200)
            signal_fit = self.steady_state_signal(angles_fit, *popt)
            
            # E1 und Ernst-Winkel berechnen
            E1_fit = np.exp(-self.T_R / T1_fit)
            ernst_angle = np.degrees(np.arccos(np.clip(E1_fit, -1, 1)))
            
            # Plot mit Messdaten und Fit
            self.ax_plot.errorbar(angles, means, yerr=stds, 
                                fmt='o', markersize=8, capsize=5,
                                color='darkblue', markeredgecolor='black', 
                                markeredgewidth=1, ecolor='gray', alpha=0.8,
                                label='Messdaten')
            
            self.ax_plot.plot(angles_fit, signal_fit, 'r-', linewidth=2, 
                            label=f'Fit mit Offset (R² = {r_squared:.4f})')
            
            # Offset-Linie anzeigen
            self.ax_plot.axhline(y=y_offset_fit, color='orange', linestyle=':', 
                               alpha=0.7, label=f'Offset: {y_offset_fit:.1f}')
            
            # Ernst-Winkel markieren
            if 0 <= ernst_angle <= 90:
                ernst_signal = self.steady_state_signal(ernst_angle, *popt)
                self.ax_plot.axvline(x=ernst_angle, color='green', linestyle='--', 
                                   alpha=0.7, label=f'Ernst-Winkel: {ernst_angle:.1f}°')
            
            # Parameter anzeigen
            self.display_parameters(y_offset_fit, y_offset_err, rho_0_fit, rho_0_err, 
                                  T1_fit, T1_err, T2_star_fit, T2_star_err, 
                                  E1_fit, ernst_angle, r_squared)
            
        except Exception as e:
            print(f"Fehler beim Fit: {e}")
            # Nur Messdaten plotten wenn Fit fehlschlägt
            self.ax_plot.errorbar(angles, means, yerr=stds, 
                                fmt='o-', markersize=8, capsize=5,
                                color='darkblue', markeredgecolor='black', 
                                markeredgewidth=1, ecolor='gray', alpha=0.8)
            
            # Fehlermeldung in Parameter-Bereich anzeigen
            self.ax_params.clear()
            self.ax_params.axis('off')
            self.ax_params.text(0.1, 0.5, f"Fit fehlgeschlagen:\n{str(e)}", 
                              transform=self.ax_params.transAxes,
                              fontsize=11, verticalalignment='center', 
                              bbox=dict(boxstyle='round,pad=0.5', 
                                      facecolor='red', alpha=0.3))
        
        # Achsenbeschriftungen
        self.ax_plot.set_xlabel('Flipwinkel (Grad)', fontsize=12)
        self.ax_plot.set_ylabel('Mittlere Graustufe (3x3 Region)', fontsize=12)
        self.ax_plot.set_title(f'Steady-State-Signal Fit mit Offset für Position ({self.selected_x}, {self.selected_y})', 
                              fontsize=14)
        
        # Gitter und Legende
        self.ax_plot.grid(True, alpha=0.3)
        self.ax_plot.legend(loc='best')
        
        # X-Achse
        self.ax_plot.set_xlim(-5, 95)
        
        # Achsenbeschriftungen
        self.ax_plot.set_xlabel('Flipwinkel (Grad)', fontsize=12)
        self.ax_plot.set_ylabel('Mittlere Graustufe (3x3 Region)', fontsize=12)
        self.ax_plot.set_title(f'Steady-State-Signal Fit mit Offset für Position ({self.selected_x}, {self.selected_y})', 
                              fontsize=14)
        
        # Gitter und Legende
        self.ax_plot.grid(True, alpha=0.3)
        self.ax_plot.legend(loc='best')
        
        # X-Achse
        self.ax_plot.set_xlim(-5, 95)
        
    def display_parameters(self, y_offset, y_offset_err, rho_0, rho_0_err, 
                          T1, T1_err, T2_star, T2_star_err, E1, ernst_angle, r_squared):
        """Zeigt die extrahierten Parameter an"""
        self.ax_params.clear()
        self.ax_params.axis('off')
        
        # Parameter-Text
        param_text = f"""
EXTRAHIERTE PARAMETER
Position: ({self.selected_x}, {self.selected_y})

Eingabeparameter:
━━━━━━━━━━━━━━━━━━━━━━━
T_E = {self.T_E*1000:.1f} ms
T_R = {self.T_R*1000:.1f} ms

Fit-Parameter:
━━━━━━━━━━━━━━━━━━━━━━━
y₀ = {y_offset:.1f} ± {y_offset_err:.1f}
   (Baseline-Offset)

ρ₀ = {rho_0:.1f} ± {rho_0_err:.1f}
   (Protonendichte)

T₁ = {T1*1000:.1f} ± {T1_err*1000:.1f} ms
   (Longitudinale Relaxation)

T₂* = {T2_star*1000:.1f} ± {T2_star_err*1000:.1f} ms
   (Effektive transversale Relaxation)

Berechnete Werte:
━━━━━━━━━━━━━━━━━━━━━━━
E₁ = {E1:.3f}
   (exp(-T_R/T₁))

Ernst-Winkel θ_E = {ernst_angle:.1f}°
   (Optimaler Flipwinkel)

Fit-Qualität:
━━━━━━━━━━━━━━━━━━━━━━━
R² = {r_squared:.4f}
   (Bestimmtheitsmaß)
"""
        
        self.ax_params.text(0.1, 0.95, param_text, transform=self.ax_params.transAxes,
                          fontsize=11, verticalalignment='top', fontfamily='monospace',
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))
        
        self.ax_params.text(0.1, 0.95, param_text, transform=self.ax_params.transAxes,
                          fontsize=11, verticalalignment='top', fontfamily='monospace',
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

# Hauptprogramm
if __name__ == "__main__":
    print("MRT Steady-State-Signal Analyse mit Offset-Fit")
    print("=" * 60)
    print("Klicken Sie auf einen Punkt im linken Bild (FA5.png)")
    print("Die Analyse fittet die Steady-State-Gleichung (18.14) mit Baseline-Offset")
    print("Fit-Funktion: y = y₀ + ρ₀·sin(θ)·(1-E₁)/(1-E₁·cos(θ))·exp(-T_E/T₂*)")
    print("Hinweis: Wählen Sie Punkte mit mind. 1 Pixel Abstand zum Rand\n")
    
    analyzer = MRTAnalyzer()