
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

class ProfileAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Profilio Analizės Programa")
        self.root.geometry("400x200")
        
        # GUI elementai
        tk.Label(self.root, text="Profilio Analizės Programa", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Button(self.root, text="Pasirinkti Excel failą", command=self.select_file, 
                 font=("Arial", 12), bg="lightblue", width=20).pack(pady=10)
        tk.Button(self.root, text="Išeiti", command=self.root.quit, 
                 font=("Arial", 12), bg="lightcoral", width=20).pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="Pasirinkite Excel failą analizei", 
                                   font=("Arial", 10))
        self.status_label.pack(pady=10)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Pasirinkite Excel failą",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if file_path:
            self.analyze_profiles(file_path)
    
    def analyze_profiles(self, file_path):
        try:
            self.status_label.config(text="Analizuojami duomenys...")
            self.root.update()
            
            # Nuskaitome duomenis
            df = pd.read_excel(file_path)
            
            # Patikriname stulpelius
            required_columns = ['id', 'dist', 'h']
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Klaida", f"Excel faile turi būti stulpeliai: {required_columns}")
                return
            
            # Analizuojame kiekvieną profilį
            results = []
            unique_ids = sorted(df['id'].unique())
            
            for profile_id in unique_ids:
                profile_data = df[df['id'] == profile_id].sort_values('dist')
                result = self.analyze_single_profile(profile_id, profile_data)
                results.append(result)
                
                # Atnaujinamas statusas
                progress = len(results) / len(unique_ids) * 100
                self.status_label.config(text=f"Analizuojama: {progress:.1f}% ({len(results)}/{len(unique_ids)})")
                self.root.update()
            
            # Išsaugome rezultatus
            self.save_results(results, file_path)
            
            messagebox.showinfo("Sėkmė", f"Analizė baigta!\nIšanalizuota {len(results)} profilių.\nRezultatai išsaugoti.")
            self.status_label.config(text="Analizė baigta sėkmingai!")
            
        except Exception as e:
            messagebox.showerror("Klaida", f"Įvyko klaida: {str(e)}")
            self.status_label.config(text="Įvyko klaida analizės metu")
    
    def analyze_single_profile(self, profile_id, profile_data):
        x = profile_data['dist'].values
        h = profile_data['h'].values
        
        # Pagrindiniai parametrai
        min_h = np.min(h)
        x_min = np.min(x)
        x_max = np.max(x)
        h_at_xmin = profile_data[profile_data['dist'] == x_min]['h'].values[0]
        h_at_xmax = profile_data[profile_data['dist'] == x_max]['h'].values[0]
        avg_h = (h_at_xmin + h_at_xmax) / 2
        mean_h = np.mean(h)
        offset = h_at_xmin
        
        # Tiesinis trendas
        slope = (h_at_xmax - h_at_xmin) / (x_max - x_min) if x_max != x_min else 0
        intercept = h_at_xmin - slope * x_min
        trend = slope * x + intercept
        trend_bottom = trend + (min_h - avg_h)
        
        # Plotų skaičiavimai
        area_avg = np.trapz(np.maximum(h - avg_h, 0), x)
        area_min = np.trapz(h - min_h, x)
        area_trend = np.trapz(np.maximum(h - trend, 0), x)
        area_trend_bottom = np.trapz(np.maximum(h - trend_bottom, 0), x)
        
        # Su offset korekcija
        h_corrected = h - offset
        min_h_corrected = np.min(h_corrected)
        avg_h_corrected = (0 + (h_corrected[-1])) / 2
        trend_corrected = slope * x
        trend_bottom_corrected = trend_corrected + (min_h_corrected - avg_h_corrected)
        
        area_avg_corrected = np.trapz(np.maximum(h_corrected - avg_h_corrected, 0), x)
        area_min_corrected = np.trapz(h_corrected - min_h_corrected, x)
        area_trend_corrected = np.trapz(np.maximum(h_corrected - trend_corrected, 0), x)
        area_trend_bottom_corrected = np.trapz(np.maximum(h_corrected - trend_bottom_corrected, 0), x)
        
        return {
            'id': profile_id,
            'min_h': min_h,
            'x_min': x_min,
            'x_max': x_max,
            'h_at_xmin': h_at_xmin,
            'h_at_xmax': h_at_xmax,
            'avg_h': avg_h,
            'mean_h': mean_h,
            'offset': offset,
            'slope': slope,
            'intercept': intercept,
            'area_avg': area_avg,
            'area_min': area_min,
            'area_trend': area_trend,
            'area_trend_bottom': area_trend_bottom,
            'min_h_corrected': min_h_corrected,
            'avg_h_corrected': avg_h_corrected,
            'area_avg_corrected': area_avg_corrected,
            'area_min_corrected': area_min_corrected,
            'area_trend_corrected': area_trend_corrected,
            'area_trend_bottom_corrected': area_trend_bottom_corrected,
            'profile_length': x_max - x_min,
            'points_count': len(x)
        }
    
    def save_results(self, results, original_file_path):
        # Sukuriame DataFrame
        df_results = pd.DataFrame(results)
        
        # Failo pavadinimas su data ir laiku
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(original_file_path))[0]
        
        # Išsaugome į skirtingus formatus
        output_dir = os.path.dirname(original_file_path)
        
        # Excel
        excel_file = os.path.join(output_dir, f"{base_name}_rezultatai_{timestamp}.xlsx")
        df_results.to_excel(excel_file, index=False)
        
        # CSV
        csv_file = os.path.join(output_dir, f"{base_name}_rezultatai_{timestamp}.csv")
        df_results.to_csv(csv_file, index=False, sep=';', decimal=',')
        
        # TXT ataskaita
        txt_file = os.path.join(output_dir, f"{base_name}_ataskaita_{timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("PROFILIO ANALIZĖS ATASKAITA\n")
            f.write("=" * 50 + "\n")
            f.write(f"Analizės data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Originalus failas: {os.path.basename(original_file_path)}\n")
            f.write(f"Analizuotų profilių kiekis: {len(results)}\n\n")
            
            f.write("SUVESTINĖ STATISTIKA:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Vidutinis profilio ilgis: {df_results['profile_length'].mean():.2f} m\n")
            f.write(f"Vidutinis plotas virš min. aukščio: {df_results['area_min'].mean():.2f} m²\n")
            f.write(f"Vidutinis nuolydis: {df_results['slope'].mean():.6f}\n\n")
            
            f.write("DETALŪS REZULTATAI:\n")
            f.write("-" * 30 + "\n")
            for result in results:
                f.write(f"\nID {result['id']}:\n")
                f.write(f"  Profilio ilgis: {result['profile_length']:.2f} m\n")
                f.write(f"  Min. aukštis: {result['min_h']:.4f} m\n")
                f.write(f"  Nuolydis: {result['slope']:.6f}\n")
                f.write(f"  Plotas virš min.: {result['area_min']:.2f} m²\n")
                f.write(f"  Plotas virš vid.: {result['area_avg']:.2f} m²\n")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProfileAnalyzer()
    app.run()
