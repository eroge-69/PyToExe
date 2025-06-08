import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

# Configurar tema de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TransformerCalculator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Calculadora Avanzada de Transformador")
        self.root.geometry("1200x800")
        
        # Variables para almacenar parámetros
        self.parameters = {}
        self.transfer_function = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(main_frame, text="Calculadora Avanzada de Transformador", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)
        
        # Frame para parámetros y gráfico
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame izquierdo para parámetros
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        # Frame derecho para gráfico
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        self.setup_parameters_panel(left_frame)
        self.setup_graph_panel(right_frame)
        
    def setup_parameters_panel(self, parent):
        # Título de parámetros
        params_title = ctk.CTkLabel(parent, text="Parámetros del Sistema", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        params_title.pack(pady=10)
        
        # Scrollable frame para parámetros
        scrollable_frame = ctk.CTkScrollableFrame(parent, width=350, height=500)
        scrollable_frame.pack(fill="both", expand=True, padx=10)
        
        # Parámetros del transformador
        transformer_label = ctk.CTkLabel(scrollable_frame, text="Parámetros del Transformador", 
                                       font=ctk.CTkFont(size=16, weight="bold"))
        transformer_label.pack(pady=(10, 5))
        
        self.param_entries = {}
        
        transformer_params = [
            ("a", "Relación de voltaje (a)", ""),
            ("Re", "Resistencia primario (Re) [Ω]", ""),
            ("Le", "Inductancia primario (Le) [H]", ""),
            ("Ro", "Resistencia secundario (Ro) [Ω]", ""),
            ("Lo", "Inductancia secundario (Lo) [H]", ""),
            ("Rm", "Resistencia magnética (Rm) [Ω]", ""),
            ("Lm", "Inductancia magnética (Lm) [H]", "")
        ]
        
        for param, label, default in transformer_params:
            self.create_parameter_entry(scrollable_frame, param, label, default)
        
        # Separador
        separator1 = ctk.CTkFrame(scrollable_frame, height=2)
        separator1.pack(fill="x", pady=10)
        
        # Parámetros de carga
        load_label = ctk.CTkLabel(scrollable_frame, text="Parámetros de la Carga", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        load_label.pack(pady=(10, 5))
        
        load_params = [
            ("R", "Resistencia carga (R) [Ω]", ""),
            ("L", "Inductancia carga (L) [H]", ""),
            ("C", "Capacitancia carga (C) [F]", "")
        ]
        
        for param, label, default in load_params:
            self.create_parameter_entry(scrollable_frame, param, label, default)
        
        # Botones
        button_frame = ctk.CTkFrame(scrollable_frame)
        button_frame.pack(fill="x", pady=20)
        
        calc_button = ctk.CTkButton(button_frame, text="Calcular", 
                                   command=self.calculate_transfer_function,
                                   font=ctk.CTkFont(size=14, weight="bold"))
        calc_button.pack(pady=5)
        
        clear_button = ctk.CTkButton(button_frame, text="Limpiar", 
                                    command=self.clear_parameters,
                                    fg_color="orange", hover_color="darkorange")
        clear_button.pack(pady=5)
        
        # Frame para consulta de frecuencia
        freq_frame = ctk.CTkFrame(scrollable_frame)
        freq_frame.pack(fill="x", pady=10)
        
        freq_label = ctk.CTkLabel(freq_frame, text="Consulta de Frecuencia", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        freq_label.pack(pady=5)
        
        self.freq_entry = ctk.CTkEntry(freq_frame, placeholder_text="Frecuencia [Hz]")
        self.freq_entry.pack(pady=5)
        
        freq_button = ctk.CTkButton(freq_frame, text="Consultar", 
                                   command=self.query_frequency)
        freq_button.pack(pady=5)
        
        # Text widget para resultados
        self.results_text = ctk.CTkTextbox(scrollable_frame, height=100)
        self.results_text.pack(fill="x", pady=10)
        
    def create_parameter_entry(self, parent, param_key, label_text, default_value):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=2)
        
        label = ctk.CTkLabel(frame, text=label_text, width=200, anchor="w")
        label.pack(side="left", padx=5)
        
        entry = ctk.CTkEntry(frame, width=100, placeholder_text=default_value)
        entry.pack(side="right", padx=5)
        
        self.param_entries[param_key] = entry
        
    def setup_graph_panel(self, parent):
        # Título del gráfico
        graph_title = ctk.CTkLabel(parent, text="Diagrama de Bode", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        graph_title.pack(pady=10)
        
        # Frame para el gráfico
        self.graph_frame = ctk.CTkFrame(parent)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear figura inicial
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        self.ax1.set_title('Diagrama de Bode del Transformador', color='white')
        self.ax1.set_ylabel('Magnitud [dB]', color='white')
        self.ax1.grid(True, which="both", ls="-", alpha=0.3)
        
        self.ax2.set_ylabel('Fase [grados]', color='white')
        self.ax2.set_xlabel('Frecuencia [rad/s]', color='white')
        self.ax2.grid(True, which="both", ls="-", alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def get_parameters(self):
        """Obtener parámetros de las entradas"""
        params = {}
        try:
            for key, entry in self.param_entries.items():
                value = entry.get().strip()
                if not value:
                    raise ValueError(f"El parámetro {key} está vacío")
                params[key] = float(value)
            return params
        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Error en los parámetros: {str(e)}")
            return None
    
    def calculate_transfer_function(self):
        """Calcular función de transferencia y mostrar gráfico"""
        parameters = self.get_parameters()
        if parameters is None:
            return
        
        try:
            # Definición de parámetros
            a = parameters['a']
            Re = parameters['Re']
            Le = parameters['Le']
            Rm = parameters['Rm']
            Lm = parameters['Lm']
            Ro = parameters['Ro']
            Lo = parameters['Lo']
            R = parameters['R']
            L = parameters['L']
            C = parameters['C']

            # Función f1 (ganancia estática)
            f1 = Rm / (a * Le)

            # Función f2 (sistema de segundo orden)
            num_f2 = [1, 0]  # s
            den_f2 = [1, (Re/Le + Rm/Lm + Rm/Le), (Re*Rm)/(Le*Lm)]
            f2 = signal.TransferFunction(num_f2, den_f2)

            # Función f3 (sistema de segundo orden)
            num_f3 = [L*C, R*C, 1]
            den_f3 = [(L + Lo)*C, (R + Ro)*C, 1]
            f3 = signal.TransferFunction(num_f3, den_f3)

            # Multiplicación de funciones de transferencia
            G_num = np.convolve(np.squeeze(f2.num), np.squeeze(f3.num)) * f1
            G_den = np.convolve(np.squeeze(f2.den), np.squeeze(f3.den))
            self.transfer_function = signal.TransferFunction(G_num, G_den)
            
            # Mostrar polos
            self.show_poles()
            
            # Generar gráfico de Bode
            self.plot_bode()
            
            messagebox.showinfo("Éxito", "Función de transferencia calculada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Error al calcular: {str(e)}")
    
    def show_poles(self):
        """Mostrar información de los polos"""
        if self.transfer_function is None:
            return
        
        poles = self.transfer_function.poles
        non_zero_poles = poles[poles != 0]
        
        result_text = "Frecuencias características del sistema:\n"
        if len(non_zero_poles) == 0:
            result_text += "No hay raíces distintas de cero\n"
        else:
            for i, p in enumerate(non_zero_poles, 1):
                freq_hz = np.abs(p) / (2 * np.pi)
                result_text += f"Polo {i}: {freq_hz:.2f} Hz\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", result_text)
    
    def plot_bode(self):
        """Generar diagrama de Bode"""
        if self.transfer_function is None:
            return
        
        # Limpiar gráficos anteriores
        self.ax1.clear()
        self.ax2.clear()
        
        # Configurar estilo
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        # Frecuencias
        omega = np.logspace(-8, 10, 1000)
        w, mag, phase = signal.bode(self.transfer_function, omega)

        # Gráfico de magnitud
        self.ax1.semilogx(w, mag, 'cyan', linewidth=2)
        self.ax1.set_title('Diagrama de Bode del Transformador', color='white')
        self.ax1.set_ylabel('Magnitud [dB]', color='white')
        self.ax1.grid(True, which="both", ls="-", alpha=0.3)

        # Gráfico de fase
        self.ax2.semilogx(w, phase, 'yellow', linewidth=2)
        self.ax2.set_ylabel('Fase [grados]', color='white')
        self.ax2.set_xlabel('Frecuencia [rad/s]', color='white')
        self.ax2.grid(True, which="both", ls="-", alpha=0.3)

        plt.tight_layout()
        self.canvas.draw()
    
    def query_frequency(self):
        """Consultar ganancia y fase a frecuencia específica"""
        if self.transfer_function is None:
            messagebox.showwarning("Advertencia", "Primero debe calcular la función de transferencia")
            return
        
        try:
            freq_hz = float(self.freq_entry.get())
            w = freq_hz * 2 * np.pi  # Convertir a rad/s
            _, mag, phase = signal.bode(self.transfer_function, [w])
            
            result_text = f"Resultados a {freq_hz} Hz:\n"
            result_text += f"- Ganancia: {mag[0]:.2f} dB\n"
            result_text += f"- Fase: {phase[0]:.2f} grados\n\n"
            
            current_text = self.results_text.get("1.0", "end")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", result_text + current_text)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una frecuencia válida")
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular: {str(e)}")
    
    def clear_parameters(self):
        """Limpiar todos los parámetros"""
        for entry in self.param_entries.values():
            entry.delete(0, "end")
        
        self.freq_entry.delete(0, "end")
        self.results_text.delete("1.0", "end")
        
        # Limpiar gráfico
        self.ax1.clear()
        self.ax2.clear()
        self.canvas.draw()
        
        self.transfer_function = None
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TransformerCalculator()
    app.run()