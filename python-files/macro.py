import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import random
import math
import sys

class AntiAFKApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AntiAFK GTA V")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Variable de control
        self.is_running = False
        self.thread = None
        
        # Estilo
        style = ttk.Style()
        style.configure('TFrame', background='#333333')
        style.configure('TLabel', background='#333333', foreground='black')
        style.configure('TButton', background='#555555', foreground='black')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
    
        # Marco principal
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="AntiAFK para GTA V", style='Header.TLabel')
        title_label.pack(pady=10)
        
        # Configuración de intervalo
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(pady=15, fill=tk.X)
        
        ttk.Label(interval_frame, text="Intervalo (minutos):").pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar(value="5")
        self.interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=60, textvariable=self.interval_var, width=10)
        self.interval_spinbox.pack(side=tk.RIGHT)
        
        # Configuración de intensidad
        intensity_frame = ttk.Frame(main_frame)
        intensity_frame.pack(pady=15, fill=tk.X)
        
        ttk.Label(intensity_frame, text="Intensidad de movimiento:").pack(side=tk.LEFT)
        
        self.intensity_var = tk.StringVar(value="5")
        intensity_scale = ttk.Scale(intensity_frame, from_=1, to=10, variable=self.intensity_var, orient=tk.HORIZONTAL)
        intensity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.toggle_afk)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Salir", command=self.quit_app).pack(side=tk.RIGHT, padx=10)
        
        # Estado
        self.status_var = tk.StringVar(value="Estado: Inactivo")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=10)
        
        # Log
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="Registro de actividad:").pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, height=6, width=50, bg='#222222', fg='white')
        self.log_text.pack(fill=tk.BOTH, pady=5)
        
        # Configuración de pyautogui
        pyautogui.FAILSAFE = False
        self.log("Aplicación iniciada. Configura el intervalo y presiona Iniciar.")
        
    def log(self, message):
        """Añade un mensaje al registro"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def move_camera(self, intensity=5):
        """Mueve la cámara en un patrón circular suave"""
        intensity = max(1, min(10, intensity))  # Asegurar que está entre 1 y 10
        radius = intensity * 2
        
        for i in range(12):
            if not self.is_running:
                break
            angle = i * (2 * math.pi / 12)
            dx = math.cos(angle) * radius
            dy = math.sin(angle) * radius
            pyautogui.moveRel(dx, dy, duration=0.1)
            time.sleep(0.05)

    def perform_actions(self):
        """Simula presión de teclas y movimiento de cámara"""
        intensity = int(self.intensity_var.get())
        
        # Presionar W
        pyautogui.keyDown('w')
        time.sleep(0.3 + (intensity * 0.04))
        pyautogui.keyUp('w')
        time.sleep(0.2)
        
        # Presionar S
        pyautogui.keyDown('s')
        time.sleep(0.3 + (intensity * 0.04))
        pyautogui.keyUp('s')
        time.sleep(0.2)
        
        # Mover cámara
        self.move_camera(intensity)

    def afk_loop(self):
        """Bucle principal del anti-AFK"""
        self.log("Anti-AFK iniciado")
        
        while self.is_running:
            try:
                self.perform_actions()
                self.log("Acciones anti-AFK ejecutadas")
                
                # Calcular tiempo de espera
                wait_minutes = float(self.interval_var.get())
                wait_seconds = wait_minutes * 60
                self.log(f"Esperando {wait_minutes} minutos...")
                
                # Espera con verificación periódica para poder detener
                for _ in range(int(wait_seconds)):
                    if not self.is_running:
                        break
                    time.sleep(1)
                        
            except Exception as e:
                self.log(f"Error: {str(e)}")
                time.sleep(5)

    def toggle_afk(self):
        """Inicia o detiene el anti-AFK"""
        if not self.is_running:
            # Validar intervalo
            try:
                interval = float(self.interval_var.get())
                if interval <= 0:
                    raise ValueError("El intervalo debe ser mayor a 0")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un intervalo válido (número mayor a 0)")
                return
                
            # Iniciar
            self.is_running = True
            self.start_button.config(text="Detener")
            self.status_var.set("Estado: Activo")
            self.thread = threading.Thread(target=self.afk_loop)
            self.thread.daemon = True
            self.thread.start()
            
        else:
            # Detener
            self.is_running = False
            self.start_button.config(text="Iniciar")
            self.status_var.set("Estado: Inactivo")
            self.log("Anti-AFK detenido")

    def quit_app(self):
        """Cierra la aplicación"""
        self.is_running = False
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiAFKApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()