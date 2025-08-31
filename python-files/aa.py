import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import serial
import threading
import time
from serial.tools import list_ports

class AdvancedTransferFunctionAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Avanzado de Función de Transferencia con Serial")
        self.root.geometry("1400x900")
        
        # Variables
        self.data = None
        self.results = None
        self.serial_port = None
        self.is_reading = False
        self.serial_thread = None
        
        # Configurar interfaz
        self.setup_gui()
        
    def setup_gui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar pesos de la grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Controles superiores
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="Cargar Datos CSV", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Analizar", command=self.analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exportar Resultados", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Controles de comunicación serial
        serial_frame = ttk.Frame(main_frame)
        serial_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(serial_frame, text="Puerto COM:").pack(side=tk.LEFT, padx=5)
        self.com_port = tk.StringVar(value="COM19")
        com_entry = ttk.Entry(serial_frame, textvariable=self.com_port, width=10)
        com_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(serial_frame, text="Baudrate:").pack(side=tk.LEFT, padx=5)
        self.baudrate = tk.StringVar(value="9600")
        baud_entry = ttk.Entry(serial_frame, textvariable=self.baudrate, width=10)
        baud_entry.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = ttk.Button(serial_frame, text="Conectar", command=self.toggle_serial)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(serial_frame, text="PWM a enviar:").pack(side=tk.LEFT, padx=5)
        self.pwm_value = tk.StringVar(value="0")
        pwm_entry = ttk.Entry(serial_frame, textvariable=self.pwm_value, width=5)
        pwm_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(serial_frame, text="Enviar PWM", command=self.send_pwm).pack(side=tk.LEFT, padx=5)
        ttk.Button(serial_frame, text="Barrido Automático", command=self.auto_sweep).pack(side=tk.LEFT, padx=5)
        
        # Área de gráficos
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout(pad=5.0)
        
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Área de resultados
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Notebook para organizar resultados
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de resultados
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Resultados")
        
        self.results_text = tk.Text(results_tab, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_tab, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de métricas
        metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(metrics_tab, text="Métricas")
        
        self.metrics_text = tk.Text(metrics_tab, wrap=tk.WORD)
        scrollbar_metrics = ttk.Scrollbar(metrics_tab, orient=tk.VERTICAL, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=scrollbar_metrics.set)
        
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_metrics.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de datos en tiempo real
        realtime_tab = ttk.Frame(self.notebook)
        self.notebook.add(realtime_tab, text="Datos Tiempo Real")
        
        self.realtime_text = tk.Text(realtime_tab, wrap=tk.WORD, height=10)
        scrollbar_realtime = ttk.Scrollbar(realtime_tab, orient=tk.VERTICAL, command=self.realtime_text.yview)
        self.realtime_text.configure(yscrollcommand=scrollbar_realtime.set)
        
        self.realtime_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_realtime.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Inicializar DataFrame para datos seriales
        self.serial_data = pd.DataFrame(columns=['time_seconds', 'pwm', 'distance'])
        self.start_time = None
        
    def toggle_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        try:
            self.serial_port = serial.Serial(
                port=self.com_port.get(),
                baudrate=int(self.baudrate.get()),
                timeout=1
            )
            self.is_reading = True
            self.connect_btn.config(text="Desconectar")
            self.status_var.set(f"Conectado a {self.com_port.get()}")
            
            # Iniciar hilo para lectura serial
            self.serial_thread = threading.Thread(target=self.read_serial_data)
            self.serial_thread.daemon = True
            self.serial_thread.start()
            
            # Reiniciar datos
            self.serial_data = pd.DataFrame(columns=['time_seconds', 'pwm', 'distance'])
            self.start_time = time.time()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al puerto serial: {str(e)}")
    
    def disconnect_serial(self):
        self.is_reading = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connect_btn.config(text="Conectar")
        self.status_var.set("Desconectado")
    
    def read_serial_data(self):
        while self.is_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode().strip()
                    if line:
                        try:
                            distance = float(line)
                            current_time = time.time() - self.start_time
                            current_pwm = int(self.pwm_value.get()) if self.pwm_value.get().isdigit() else 0
                            
                            # Agregar datos al DataFrame
                            new_data = pd.DataFrame({
                                'time_seconds': [current_time],
                                'pwm': [current_pwm],
                                'distance': [distance]
                            })
                            self.serial_data = pd.concat([self.serial_data, new_data], ignore_index=True)
                            
                            # Actualizar texto en tiempo real
                            self.realtime_text.insert(tk.END, f"T: {current_time:.2f}s, PWM: {current_pwm}, Distancia: {distance}\n")
                            self.realtime_text.see(tk.END)
                            
                        except ValueError:
                            # Ignorar líneas que no se pueden convertir a float
                            pass
            except Exception as e:
                print(f"Error en lectura serial: {str(e)}")
                break
            time.sleep(0.01)
    
    def send_pwm(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                pwm_val = int(self.pwm_value.get())
                if 0 <= pwm_val <= 255:
                    self.serial_port.write(f"{pwm_val}\n".encode())
                    self.status_var.set(f"PWM {pwm_val} enviado")
                else:
                    messagebox.showwarning("Advertencia", "El valor PWM debe estar entre 0 y 255")
            except ValueError:
                messagebox.showwarning("Advertencia", "Ingrese un valor numérico para PWM")
        else:
            messagebox.showwarning("Advertencia", "Primero conecte el puerto serial")
    
    def auto_sweep(self):
        if not (self.serial_port and self.serial_port.is_open):
            messagebox.showwarning("Advertencia", "Primero conecte el puerto serial")
            return
        
        # Barrido automático de PWM
        def sweep_thread():
             self.serial_port.write("0")
             self.serial_port.write("cal0")
             self.serial_port.write("255")
             self.serial_port.write("cal100")
             self.serial_port.write("0")
             pwm_values = list(range(0, 256, 25)) + list(range(255, -1, -5))
             for pwm in pwm_values:
                if not self.is_reading:
                    break
                self.pwm_value.set(str(pwm))
                self.serial_port.write(f"{pwm}\n".encode())
                self.status_var.set(f"Barrido automático: PWM {pwm} enviado")
                time.sleep(2)  # Esperar 2 segundos entre cambios
            
                self.status_var.set("Barrido automático completado")
        
        threading.Thread(target=sweep_thread, daemon=True).start()
    
    def load_data(self):
        # Opción para cargar datos desde CSV o usar datos seriales
        if len(self.serial_data) > 0:
            if messagebox.askyesno("Seleccionar datos", "¿Usar datos adquiridos por serial? Si selecciona No, podrá cargar un archivo CSV."):
                self.data = self.serial_data.copy()
                self.status_var.set(f"Datos seriales cargados: {len(self.data)} registros")
                return
        
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.status_var.set(f"Datos cargados: {len(self.data)} registros")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def analyze(self):
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero carga un archivo CSV o adquiere datos por serial")
            return
        
        try:
            self.status_var.set("Analizando datos...")
            self.root.update()
            
            # Realizar análisis
            self.results = self.advanced_analysis(self.data)
            
            # Mostrar resultados
            self.display_results()
            self.plot_results()
            
            self.status_var.set("Análisis completado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en el análisis: {str(e)}")
            print(traceback.format_exc())
    
    def advanced_analysis(self, data):
        # Preprocesamiento de datos
        data_clean = data.dropna()
        
        # Identificar cambios de PWM
        pwm_diff = data_clean['pwm'].diff().fillna(0)
        step_indices = np.where(np.abs(pwm_diff) > 5)[0]
        
        results = []
        
        for i in range(len(step_indices) - 1):
            start_idx = step_indices[i]
            end_idx = step_indices[i + 1]
            
            segment = data_clean.iloc[start_idx:end_idx].copy()
            
            if len(segment) < 20:  # Segmento demasiado corto
                continue
            
            # Preparar datos para el ajuste
            t = segment['time_seconds'] - segment['time_seconds'].iloc[0]
            y = segment['distance'].values
            u = segment['pwm'].iloc[0]  # Valor de PWM para este segmento
            
            # Valor inicial y final para normalización
            y0 = np.mean(y[:5])  # Promedio de los primeros 5 puntos
            y_ss = np.mean(y[-5:])  # Promedio de los últimos 5 puntos
            
            # Normalizar respuesta
            y_norm = (y - y0) / (y_ss - y0) if (y_ss - y0) != 0 else y - y0
            
            # Ajustar modelos
            try:
                # Modelo de primer orden
                def first_order(t, K, tau):
                    return K * (1 - np.exp(-t / tau))
                
                popt_1st, pcov_1st = curve_fit(first_order, t, y_norm, p0=[1, 1], maxfev=5000)
                y_pred_1st = first_order(t, *popt_1st)
                
                # Modelo de segundo orden
                def second_order(t, K, tau, zeta):
                    if zeta < 1:  # Subamortiguado
                        omega_n = 1 / tau
                        omega_d = omega_n * np.sqrt(1 - zeta**2)
                        return K * (1 - (np.exp(-zeta * omega_n * t) / np.sqrt(1 - zeta**2)) * 
                                  np.sin(omega_d * t + np.arccos(zeta)))
                    else:  # Sobreamortiguado
                        # Aproximación a dos polos reales
                        return K * (1 - (tau / (tau - 1)) * np.exp(-t / tau) + 
                                  (1 / (tau - 1)) * np.exp(-tau * t))
                
                popt_2nd, pcov_2nd = curve_fit(second_order, t, y_norm, p0=[1, 1, 0.7], maxfev=10000)
                y_pred_2nd = second_order(t, *popt_2nd)
                
                # Calcular métricas de error
                mse_1st = np.mean((y_norm - y_pred_1st) ** 2)
                mse_2nd = np.mean((y_norm - y_pred_2nd) ** 2)
                
                r2_1st = 1 - np.sum((y_norm - y_pred_1st) ** 2) / np.sum((y_norm - np.mean(y_norm)) ** 2)
                r2_2nd = 1 - np.sum((y_norm - y_pred_2nd) ** 2) / np.sum((y_norm - np.mean(y_norm)) ** 2)
                
                # Test F para comparar modelos
                ssr_1st = np.sum((y_norm - y_pred_1st) ** 2)
                ssr_2nd = np.sum((y_norm - y_pred_2nd) ** 2)
                
                n = len(y_norm)
                p1, p2 = 2, 3  # Parámetros en cada modelo
                
                f_stat = ((ssr_1st - ssr_2nd) / (p2 - p1)) / (ssr_2nd / (n - p2))
                p_value = 1 - stats.f.cdf(f_stat, p2 - p1, n - p2)
                
                # Determinar mejor modelo
                best_model = "Primer orden" if mse_1st < mse_2nd and p_value > 0.05 else "Segundo orden"
                
                results.append({
                    'segment': i + 1,
                    'pwm': u,
                    'first_order': {
                        'K': popt_1st[0],
                        'tau': popt_1st[1],
                        'mse': mse_1st,
                        'r2': r2_1st
                    },
                    'second_order': {
                        'K': popt_2nd[0],
                        'tau': popt_2nd[1],
                        'zeta': popt_2nd[2],
                        'mse': mse_2nd,
                        'r2': r2_2nd
                    },
                    'comparison': {
                        'f_stat': f_stat,
                        'p_value': p_value,
                        'best_model': best_model
                    },
                    'data': {
                        't': t.values,
                        'y_norm': y_norm,
                        'y_pred_1st': y_pred_1st,
                        'y_pred_2nd': y_pred_2nd
                    }
                })
                
            except Exception as e:
                print(f"Error en el segmento {i+1}: {str(e)}")
                continue
        
        return results
    
    def display_results(self):
        if not self.results:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "No se encontraron resultados válidos.")
            return
        
        # Calcular promedios ponderados por calidad de ajuste
        k_1st_avg = np.average([r['first_order']['K'] for r in self.results], 
                              weights=[1/r['first_order']['mse'] for r in self.results if r['first_order']['mse'] > 0])
        tau_1st_avg = np.average([r['first_order']['tau'] for r in self.results],
                                weights=[1/r['first_order']['mse'] for r in self.results if r['first_order']['mse'] > 0])
        
        k_2nd_avg = np.average([r['second_order']['K'] for r in self.results],
                              weights=[1/r['second_order']['mse'] for r in self.results if r['second_order']['mse'] > 0])
        tau_2nd_avg = np.average([r['second_order']['tau'] for r in self.results],
                                weights=[1/r['second_order']['mse'] for r in self.results if r['second_order']['mse'] > 0])
        zeta_avg = np.average([r['second_order']['zeta'] for r in self.results],
                             weights=[1/r['second_order']['mse'] for r in self.results if r['second_order']['mse'] > 0])
        
        # Contar mejores modelos
        best_model_counts = {
            'Primer orden': sum(1 for r in self.results if r['comparison']['best_model'] == 'Primer orden'),
            'Segundo orden': sum(1 for r in self.results if r['comparison']['best_model'] == 'Segundo orden')
        }
        
        # Generar texto de resultados
        result_text = "=== FUNCIÓN DE TRANSFERENCIA ESTIMADA ===\n\n"
        
        result_text += f"Modelo de Primer Orden:\n"
        result_text += f"  G(s) = {k_1st_avg:.4f} / ({tau_1st_avg:.4f}s + 1)\n\n"
        
        result_text += f"Modelo de Segundo Orden:\n"
        if zeta_avg < 1:
            result_text += f"  G(s) = {k_2nd_avg:.4f} * ωₙ² / (s² + {2*zeta_avg:.4f}ωₙs + ωₙ²)\n"
            result_text += f"  donde ωₙ = {1/tau_2nd_avg:.4f} rad/s, ζ = {zeta_avg:.4f}\n\n"
        else:
            result_text += f"  G(s) = {k_2nd_avg:.4f} / ({tau_2nd_avg:.4f}s + 1)({zeta_avg:.4f}s + 1)\n\n"
        
        result_text += "=== COMPARACIÓN DE MODELOS ===\n\n"
        result_text += f"Mejor modelo según segmentos:\n"
        result_text += f"  Primer orden: {best_model_counts['Primer orden']} segmentos\n"
        result_text += f"  Segundo orden: {best_model_counts['Segundo orden']} segmentos\n\n"
        
        result_text += "=== DETALLES POR SEGMENTO ===\n\n"
        for r in self.results:
            result_text += f"Segmento {r['segment']} (PWM = {r['pwm']}):\n"
            result_text += f"  Primer orden: K={r['first_order']['K']:.4f}, τ={r['first_order']['tau']:.4f}, R²={r['first_order']['r2']:.4f}\n"
            result_text += f"  Segundo orden: K={r['second_order']['K']:.4f}, τ={r['second_order']['tau']:.4f}, ζ={r['second_order']['zeta']:.4f}, R²={r['second_order']['r2']:.4f}\n"
            result_text += f"  Mejor modelo: {r['comparison']['best_model']} (p={r['comparison']['p_value']:.4f})\n\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)
        
        # Generar texto de métricas
        metrics_text = "=== MÉTRICAS DE AJUSTE ===\n\n"
        
        metrics_text += "Error Cuadrático Medio (MSE) - Promedio ponderado:\n"
        mse_1st_avg = np.average([r['first_order']['mse'] for r in self.results])
        mse_2nd_avg = np.average([r['second_order']['mse'] for r in self.results])
        metrics_text += f"  Primer orden: {mse_1st_avg:.6f}\n"
        metrics_text += f"  Segundo orden: {mse_2nd_avg:.6f}\n\n"
        
        metrics_text += "Coeficiente de Determinación (R²) - Promedio ponderado:\n"
        r2_1st_avg = np.average([r['first_order']['r2'] for r in self.results])
        r2_2nd_avg = np.average([r['second_order']['r2'] for r in self.results])
        metrics_text += f"  Primer orden: {r2_1st_avg:.4f}\n"
        metrics_text += f"  Segundo orden: {r2_2nd_avg:.4f}\n\n"
        
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, metrics_text)
    
    def plot_results(self):
        # Limpiar gráficos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        # Gráfico 1: Comparación de modelos para todos los segmentos
        for r in self.results:
            t = r['data']['t']
            y_norm = r['data']['y_norm']
            y_pred_1st = r['data']['y_pred_1st']
            y_pred_2nd = r['data']['y_pred_2nd']
            
            self.ax1.plot(t, y_norm, 'o', markersize=2, alpha=0.7)
            self.ax1.plot(t, y_pred_1st, '-', linewidth=1, alpha=0.7)
            self.ax1.plot(t, y_pred_2nd, '--', linewidth=1, alpha=0.7)
        
        self.ax1.set_xlabel('Tiempo (s)')
        self.ax1.set_ylabel('Respuesta Normalizada')
        self.ax1.set_title('Comparación de Ajustes por Segmento')
        self.ax1.legend(['Datos', '1er Orden', '2do Orden'], loc='best')
        self.ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Error de predicción
        errors_1st = []
        errors_2nd = []
        
        for r in self.results:
            errors_1st.extend(r['data']['y_norm'] - r['data']['y_pred_1st'])
            errors_2nd.extend(r['data']['y_norm'] - r['data']['y_pred_2nd'])
        
        self.ax2.hist(errors_1st, bins=30, alpha=0.7, label='1er Orden')
        self.ax2.hist(errors_2nd, bins=30, alpha=0.7, label='2do Orden')
        self.ax2.set_xlabel('Error de Predicción')
        self.ax2.set_ylabel('Frecuencia')
        self.ax2.set_title('Distribución de Errores')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Comparación de R²
        r2_1st = [r['first_order']['r2'] for r in self.results]
        r2_2nd = [r['second_order']['r2'] for r in self.results]
        
        segments = range(1, len(self.results) + 1)
        self.ax3.plot(segments, r2_1st, 'o-', label='1er Orden')
        self.ax3.plot(segments, r2_2nd, 's-', label='2do Orden')
        self.ax3.set_xlabel('Segmento')
        self.ax3.set_ylabel('R²')
        self.ax3.set_title('Comparación de Calidad de Ajuste (R²)')
        self.ax3.legend()
        self.ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Parámetros del modelo de segundo orden
        zeta_values = [r['second_order']['zeta'] for r in self.results]
        self.ax4.plot(segments, zeta_values, 'o-')
        self.ax4.set_xlabel('Segmento')
        self.ax4.set_ylabel('ζ (Coeficiente de Amortiguamiento)')
        self.ax4.set_title('Parámetro ζ del Modelo de Segundo Orden')
        self.ax4.grid(True, alpha=0.3)
        
        # Ajustar diseño y dibujar
        self.fig.tight_layout()
        self.canvas.draw()
    
    def export_results(self):
        if not self.results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Crear DataFrame con resultados
                export_data = []
                for r in self.results:
                    export_data.append({
                        'segmento': r['segment'],
                        'pwm': r['pwm'],
                        'k_1er_orden': r['first_order']['K'],
                        'tau_1er_orden': r['first_order']['tau'],
                        'r2_1er_orden': r['first_order']['r2'],
                        'mse_1er_orden': r['first_order']['mse'],
                        'k_2do_orden': r['second_order']['K'],
                        'tau_2do_orden': r['second_order']['tau'],
                        'zeta_2do_orden': r['second_order']['zeta'],
                        'r2_2do_orden': r['second_order']['r2'],
                        'mse_2do_orden': r['second_order']['mse'],
                        'mejor_modelo': r['comparison']['best_model'],
                        'valor_p': r['comparison']['p_value']
                    })
                
                df = pd.DataFrame(export_data)
                df.to_csv(file_path, index=False)
                
                self.status_var.set(f"Resultados exportados a {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron exportar los resultados: {str(e)}")

def main():
    root = tk.Tk()
    app = AdvancedTransferFunctionAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()