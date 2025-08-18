import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import serial
import serial.tools.list_ports
from collections import deque
import threading
import queue
import time
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt, savgol_filter

class MPU6050Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("MPU6050 - Visualización en Tiempo Real")
        self.root.geometry("1400x800")
        
        # Configuración de datos
        self.sample_rate = 200  # Hz
        self.buffer_size = 1024
        self.time_window = 5.0  # segundos
        self.max_samples = int(self.sample_rate * self.time_window)
        
        # Parámetros de filtrado optimizados
        self.filter_order = 4
        self.lowpass_cutoff = 80.0  # Hz - Para eliminar ruido de alta frecuencia
        self.highpass_cutoff = 0.5  # Hz - Para eliminar deriva DC
        self.notch_freqs = [50, 60]  # Hz - Eliminar ruido de línea eléctrica
        self.noise_threshold = 0.01  # Umbral de ruido adaptativo
        
        # Buffers para datos
        self.accel_x = deque(maxlen=self.max_samples)
        self.accel_y = deque(maxlen=self.max_samples)
        self.accel_z = deque(maxlen=self.max_samples)
        self.gyro_x = deque(maxlen=self.max_samples)
        self.gyro_y = deque(maxlen=self.max_samples)
        self.gyro_z = deque(maxlen=self.max_samples)
        self.timestamps = deque(maxlen=self.max_samples)
        
        # Buffers para datos filtrados
        self.filtered_data_buffer = deque(maxlen=self.max_samples)
        
        # Variables de comunicación
        self.serial_port = None
        self.is_connected = False
        self.data_queue = queue.Queue()
        
        # Variable de selección de datos
        self.selected_data = tk.StringVar(value="accel_x")
        
        # Inicializar filtros
        self.setup_filters()
        
        self.setup_ui()
        self.setup_plots()
        
        # Thread para lectura de datos
        self.data_thread = None
        self.running = False
        
    def setup_filters(self):
        """Configurar filtros digitales"""
        nyquist = self.sample_rate / 2
        
        # Filtro pasa-bajos (elimina ruido de alta frecuencia)
        self.lowpass_b, self.lowpass_a = butter(
            self.filter_order, 
            self.lowpass_cutoff / nyquist, 
            btype='low'
        )
        
        # Filtro pasa-altos (elimina deriva DC)
        self.highpass_b, self.highpass_a = butter(
            self.filter_order, 
            self.highpass_cutoff / nyquist, 
            btype='high'
        )
        
    def apply_filters(self, data):
        """Aplicar filtros digitales a los datos"""
        if len(data) < 20:  # Necesitamos suficientes puntos para filtrar
            return np.array(data)
            
        data_array = np.array(data)
        
        # 1. Remover outliers usando percentiles
        q25, q75 = np.percentile(data_array, [25, 75])
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        data_array = np.clip(data_array, lower_bound, upper_bound)
        
        # 2. Filtro Savitzky-Golay para suavizado inicial
        if len(data_array) >= 11:
            window_length = min(11, len(data_array) if len(data_array) % 2 == 1 else len(data_array) - 1)
            data_array = savgol_filter(data_array, window_length, 3)
        
        # 3. Aplicar filtros Butterworth
        try:
            # Filtro pasa-altos
            data_filtered = filtfilt(self.highpass_b, self.highpass_a, data_array)
            # Filtro pasa-bajos
            data_filtered = filtfilt(self.lowpass_b, self.lowpass_a, data_filtered)
        except:
            data_filtered = data_array
        
        # 4. Reducción de ruido adaptativa
        noise_level = np.std(data_filtered) * 0.1
        data_filtered = np.where(np.abs(data_filtered) < noise_level, 0, data_filtered)
        
        return data_filtered
    
    def compute_enhanced_fft(self, data):
        """FFT mejorada con técnicas de reducción de ruido"""
        if len(data) < 64:
            return np.array([]), np.array([])
            
        # Usar ventana deslizante para mejor resolución temporal
        n_fft = min(len(data), 1024)
        data_segment = data[-n_fft:]
        
        # Remover tendencia lineal
        x = np.arange(len(data_segment))
        coeffs = np.polyfit(x, data_segment, 1)
        trend = coeffs[0] * x + coeffs[1]
        data_detrended = data_segment - trend
        
        # Aplicar ventana Hamming (mejor que Hanning para análisis de vibración)
        window = np.hamming(n_fft)
        data_windowed = data_detrended * window
        
        # Zero-padding para mejorar interpolación de frecuencia
        n_fft_padded = n_fft * 2
        data_padded = np.zeros(n_fft_padded)
        data_padded[:n_fft] = data_windowed
        
        # Calcular FFT
        fft_data = fft(data_padded)
        freqs = fftfreq(n_fft_padded, 1/self.sample_rate)
        
        # Tomar solo frecuencias positivas
        positive_freqs = freqs[:n_fft_padded//2]
        magnitude = np.abs(fft_data[:n_fft_padded//2])
        
        # Aplicar suavizado espectral
        if len(magnitude) > 5:
            magnitude = savgol_filter(magnitude, 5, 2)
        
        # Filtrar frecuencias de interés (típicamente 1-100 Hz para vibración mecánica)
        freq_mask = (positive_freqs >= 1.0) & (positive_freqs <= 100.0)
        filtered_freqs = positive_freqs[freq_mask]
        filtered_magnitude = magnitude[freq_mask]
        
        # Normalización adaptativa
        if len(filtered_magnitude) > 0:
            # Eliminar ruido de fondo
            noise_floor = np.percentile(filtered_magnitude, 20)
            filtered_magnitude = np.maximum(filtered_magnitude - noise_floor, 0)
            
            # Normalización logarítmica para mejor visualización
            max_mag = np.max(filtered_magnitude)
            if max_mag > 0:
                filtered_magnitude = filtered_magnitude / max_mag
        
        return filtered_freqs, filtered_magnitude
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de control
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selección de puerto
        ttk.Label(control_frame, text="Puerto:").pack(side=tk.LEFT, padx=(0, 5))
        self.port_combo = ttk.Combobox(control_frame, width=15)
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para refrescar puertos
        ttk.Button(control_frame, text="Refrescar", command=self.refresh_ports).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones de conexión
        self.connect_btn = ttk.Button(control_frame, text="Conectar", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Selección de datos a visualizar
        ttk.Label(control_frame, text="Datos:").pack(side=tk.LEFT, padx=(10, 5))
        data_options = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
        data_combo = ttk.Combobox(control_frame, textvariable=self.selected_data, values=data_options, width=10)
        data_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado de conexión
        self.status_label = ttk.Label(control_frame, text="Desconectado", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Inicializar lista de puertos
        self.refresh_ports()
        
    def setup_plots(self):
        # Crear figura con subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Configurar subplot del dominio del tiempo
        self.ax1.set_title('Dominio del Tiempo')
        self.ax1.set_xlabel('Tiempo (s)')
        self.ax1.set_ylabel('Aceleración (m/s²) / Velocidad Angular (rad/s)')
        self.ax1.grid(True, alpha=0.3)
        self.line_time, = self.ax1.plot([], [], 'b-', linewidth=1)
        
        # Configurar subplot del dominio de la frecuencia
        self.ax2.set_title('Análisis de Vibración - Dominio de la Frecuencia')
        self.ax2.set_xlabel('Frecuencia (Hz)')
        self.ax2.set_ylabel('Magnitud Normalizada')
        self.ax2.grid(True, alpha=0.3)
        self.line_freq, = self.ax2.plot([], [], 'r-', linewidth=2)
        
        # Configurar canvas
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Iniciar animación
        self.animation = FuncAnimation(self.fig, self.update_plots, interval=50, blit=False, cache_frame_data=False)
        
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            
    def toggle_connection(self):
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()
            
    def connect_serial(self):
        try:
            port = self.port_combo.get()
            if not port:
                messagebox.showerror("Error", "Selecciona un puerto")
                return
            
            # Cerrar conexión previa si existe
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                
            # Configuración más robusta del puerto serial
            self.serial_port = serial.Serial(
                port=port, 
                baudrate=115200, 
                timeout=0.1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Limpiar buffer
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            time.sleep(2)  # Esperar inicialización de Arduino
            
            self.is_connected = True
            self.running = True
            self.connect_btn.config(text="Desconectar")
            self.status_label.config(text="Conectado", foreground="green")
            
            # Limpiar buffers de datos
            self.accel_x.clear()
            self.accel_y.clear()
            self.accel_z.clear()
            self.gyro_x.clear()
            self.gyro_y.clear()
            self.gyro_z.clear()
            self.timestamps.clear()
            self.filtered_data_buffer.clear()
            
            # Iniciar thread de lectura de datos
            self.data_thread = threading.Thread(target=self.read_data_thread, daemon=True)
            self.data_thread.start()
            
            print(f"Conectado a {port}")
            
        except serial.SerialException as e:
            messagebox.showerror("Error de conexión", f"Error del puerto serial: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar: {str(e)}")
            
    def disconnect_serial(self):
        self.running = False
        self.is_connected = False
        
        # Esperar a que termine el thread de lectura
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=1.0)
        
        if self.serial_port:
            try:
                if self.serial_port.is_open:
                    self.serial_port.close()
            except Exception as e:
                print(f"Error cerrando puerto: {e}")
            finally:
                self.serial_port = None
            
        self.connect_btn.config(text="Conectar")
        self.status_label.config(text="Desconectado", foreground="red")
        print("Desconectado")
        
    def read_data_thread(self):
        """Thread para leer datos del puerto serial"""
        while self.running and self.serial_port:
            try:
                if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting > 0:
                    # Leer bytes crudos primero
                    raw_data = self.serial_port.readline()
                    if raw_data:
                        # Intentar decodificar con manejo de errores
                        try:
                            line = raw_data.decode('utf-8', errors='ignore').strip()
                            if line and ',' in line:
                                self.parse_data(line)
                        except UnicodeDecodeError:
                            # Intentar con latin-1 como fallback
                            line = raw_data.decode('latin-1', errors='ignore').strip()
                            if line and ',' in line:
                                self.parse_data(line)
                else:
                    time.sleep(0.001)  # Pequeña pausa para evitar uso excesivo de CPU
            except (serial.SerialException, OSError) as e:
                print(f"Error de comunicación serial: {e}")
                break
            except Exception as e:
                print(f"Error leyendo datos: {e}")
                time.sleep(0.01)
                
    def parse_data(self, line):
        """Parsear datos del MPU6050"""
        try:
            # Limpiar la línea de caracteres no válidos
            line = ''.join(char for char in line if char.isprintable())
            
            # Formato esperado: "ax,ay,az,gx,gy,gz"
            data = line.split(',')
            if len(data) == 6:
                # Validar que todos los valores sean numéricos
                numeric_data = []
                for value in data:
                    try:
                        numeric_data.append(float(value.strip()))
                    except ValueError:
                        return  # Si algún valor no es numérico, ignorar la línea
                
                # Convertir a valores físicos con calibración mejorada
                ax = numeric_data[0] * 9.81 / 16384.0  # Convertir a m/s²
                ay = numeric_data[1] * 9.81 / 16384.0
                az = numeric_data[2] * 9.81 / 16384.0
                gx = numeric_data[3] * np.pi / (180.0 * 131.0)  # Convertir a rad/s
                gy = numeric_data[4] * np.pi / (180.0 * 131.0)
                gz = numeric_data[5] * np.pi / (180.0 * 131.0)
                
                # Timestamp relativo
                current_time = time.time()
                if not self.timestamps:
                    self.start_time = current_time
                timestamp = current_time - self.start_time
                
                # Agregar a buffers
                self.accel_x.append(ax)
                self.accel_y.append(ay)
                self.accel_z.append(az)
                self.gyro_x.append(gx)
                self.gyro_y.append(gy)
                self.gyro_z.append(gz)
                self.timestamps.append(timestamp)
                
        except (ValueError, IndexError) as e:
            pass  # Silenciosamente ignorar líneas mal formateadas
        except Exception as e:
            print(f"Error parseando datos: {e}")
            
    def get_selected_data(self):
        """Obtener los datos seleccionados"""
        data_map = {
            "accel_x": self.accel_x,
            "accel_y": self.accel_y,
            "accel_z": self.accel_z,
            "gyro_x": self.gyro_x,
            "gyro_y": self.gyro_y,
            "gyro_z": self.gyro_z
        }
        return data_map.get(self.selected_data.get(), self.accel_x)
        
    def update_plots(self, frame):
        """Actualizar las gráficas"""
        if not self.timestamps or len(self.timestamps) < 2:
            return self.line_time, self.line_freq
            
        # Obtener datos seleccionados (originales sin filtrar para gráfica del tiempo)
        raw_data = list(self.get_selected_data())
        timestamps = list(self.timestamps)
        
        if len(raw_data) < 2:
            return self.line_time, self.line_freq
        
        # Actualizar gráfica del dominio del tiempo (datos originales como antes)
        self.line_time.set_data(timestamps, raw_data)
        self.ax1.set_xlim(max(0, timestamps[-1] - self.time_window), timestamps[-1])
        
        if raw_data:
            data_range = max(raw_data) - min(raw_data)
            if data_range > 0:
                margin = data_range * 0.1
                self.ax1.set_ylim(min(raw_data) - margin, max(raw_data) + margin)
            else:
                self.ax1.set_ylim(-1, 1)
        
        # Calcular FFT mejorada si hay suficientes datos (usando datos filtrados)
        if len(raw_data) >= 64:
            # Aplicar filtros solo para la FFT
            filtered_data_for_fft = self.apply_filters(raw_data)
            freqs, magnitude = self.compute_enhanced_fft(filtered_data_for_fft)
            
            if len(freqs) > 0 and len(magnitude) > 0:
                self.line_freq.set_data(freqs, magnitude)
                self.ax2.set_xlim(0, 100)  # Rango de interés para vibración mecánica
                
                # Configurar eje Y
                max_mag = np.max(magnitude) if len(magnitude) > 0 else 1
                self.ax2.set_ylim(0, max_mag * 1.1 if max_mag > 0 else 1)
                
                # Encontrar y mostrar picos principales
                if len(magnitude) > 10:
                    # Encontrar picos usando umbral adaptativo
                    threshold = np.mean(magnitude) + 2 * np.std(magnitude)
                    peaks = []
                    
                    for i in range(1, len(magnitude) - 1):
                        if (magnitude[i] > magnitude[i-1] and 
                            magnitude[i] > magnitude[i+1] and 
                            magnitude[i] > threshold):
                            peaks.append((freqs[i], magnitude[i]))
                    
                    # Mostrar los 3 picos más prominentes
                    peaks.sort(key=lambda x: x[1], reverse=True)
                    peak_text = ""
                    
                    for i, (freq, mag) in enumerate(peaks[:3]):
                        if i == 0:
                            peak_text = f"Principal: {freq:.1f}Hz"
                        else:
                            peak_text += f", {freq:.1f}Hz"
                    
                    if peak_text:
                        self.ax2.set_title(f'Análisis de Vibración - {peak_text}')
                    else:
                        self.ax2.set_title('Análisis de Vibración - Sin picos detectados')
            else:
                self.ax2.set_title('Análisis de Vibración - Insuficientes datos')
        else:
            self.ax2.set_title('Análisis de Vibración - Recolectando datos...')
        
        return self.line_time, self.line_freq
        
    def on_closing(self):
        """Manejar cierre de la aplicación"""
        self.disconnect_serial()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MPU6050Interface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
