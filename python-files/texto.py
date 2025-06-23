import pyttsx3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
from pathlib import Path
import os

class GeneradorAudioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech - Piripituchy")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.engine = None
        self.voces_disponibles = []
        self.reproduciendo = False
        
        # Inicializar motor de voz
        self.inicializar_motor()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar texto predeterminado
        self.cargar_texto_predeterminado()
    
    def inicializar_motor(self):
        """Inicializa el motor de texto a voz y obtiene las voces disponibles"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.voces_disponibles = [(voz.name, voz.id) for voz in voices if voz]
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar el motor de voz: {e}")
    
    def crear_interfaz(self):
        """Crea toda la interfaz gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar peso de las filas y columnas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🎙️ Generador de Texto a Audio", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Selección de voz
        ttk.Label(config_frame, text="Voz:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.combo_voz = ttk.Combobox(config_frame, width=40)
        self.combo_voz.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Cargar voces en el combobox
        nombres_voces = [nombre for nombre, _ in self.voces_disponibles]
        self.combo_voz['values'] = nombres_voces
        
        # Seleccionar voz en español por defecto
        for i, (nombre, _) in enumerate(self.voces_disponibles):
            if 'spanish' in nombre.lower() or 'español' in nombre.lower():
                self.combo_voz.current(i)
                break
        else:
            if nombres_voces:
                self.combo_voz.current(0)
        
        # Velocidad
        ttk.Label(config_frame, text="Velocidad:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.velocidad = tk.IntVar(value=160)
        velocidad_frame = ttk.Frame(config_frame)
        velocidad_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.scale_velocidad = ttk.Scale(velocidad_frame, from_=50, to=300, 
                                        orient=tk.HORIZONTAL, variable=self.velocidad)
        self.scale_velocidad.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.label_velocidad = ttk.Label(velocidad_frame, text="160")
        self.label_velocidad.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Actualizar etiqueta de velocidad
        self.scale_velocidad.configure(command=self.actualizar_velocidad)
        
        # Nombre del archivo
        ttk.Label(config_frame, text="Nombre del archivo:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.entry_nombre = ttk.Entry(config_frame, width=40)
        self.entry_nombre.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        self.entry_nombre.insert(0, "tutorial_scrumone.wav")
        
        # Área de texto
        texto_frame = ttk.LabelFrame(main_frame, text="Texto a convertir", padding="10")
        texto_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        texto_frame.columnconfigure(0, weight=1)
        texto_frame.rowconfigure(0, weight=1)
        
        self.text_area = scrolledtext.ScrolledText(texto_frame, wrap=tk.WORD, 
                                                  width=80, height=15, font=('Arial', 10))
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Botones
        self.btn_preview = ttk.Button(botones_frame, text="🔊 Reproducir Vista Previa", 
                                     command=self.reproducir_preview)
        self.btn_preview.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_detener = ttk.Button(botones_frame, text="⏹️ Detener", 
                                     command=self.detener_reproduccion, state=tk.DISABLED)
        self.btn_detener.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_guardar = ttk.Button(botones_frame, text="💾 Guardar Audio", 
                                     command=self.guardar_audio)
        self.btn_guardar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_cargar = ttk.Button(botones_frame, text="📁 Cargar Texto", 
                                    command=self.cargar_archivo)
        self.btn_cargar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_limpiar = ttk.Button(botones_frame, text="🗑️ Limpiar", 
                                     command=self.limpiar_texto)
        self.btn_limpiar.pack(side=tk.LEFT)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Etiqueta de estado
        self.label_estado = ttk.Label(main_frame, text="Listo para generar audio", 
                                     font=('Arial', 9))
        self.label_estado.grid(row=5, column=0, columnspan=3)
    
    def actualizar_velocidad(self, valor):
        """Actualiza la etiqueta de velocidad"""
        self.label_velocidad.config(text=str(int(float(valor))))
    
    def cargar_texto_predeterminado(self):
        """Carga el texto predeterminado del tutorial"""
        texto_predeterminado = """Hola, bienvenido al tutorial de métricas y reportes en ScrumOne.
A continuación, te explicaré cada sección del sistema de análisis, paso a paso.
"""
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, texto_predeterminado)
    
    def configurar_motor(self):
        """Configura el motor de voz con los parámetros seleccionados"""
        if not self.engine:
            return False
        
        try:
            # Configurar voz
            if self.combo_voz.current() >= 0:
                voz_seleccionada = self.voces_disponibles[self.combo_voz.current()][1]
                self.engine.setProperty('voice', voz_seleccionada)
            
            # Configurar velocidad
            self.engine.setProperty('rate', self.velocidad.get())
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar el motor: {e}")
            return False
    
    def reproducir_preview(self):
        """Reproduce una vista previa del audio"""
        def reproducir():
            texto = self.text_area.get(1.0, tk.END).strip()
            if not texto:
                messagebox.showwarning("Advertencia", "Por favor, ingresa algún texto.")
                return
            
            if not self.configurar_motor():
                return
            
            try:
                self.reproduciendo = True
                self.btn_preview.config(state=tk.DISABLED)
                self.btn_detener.config(state=tk.NORMAL)
                self.label_estado.config(text="Reproduciendo vista previa...")
                
                # Tomar solo las primeras 2 líneas para la vista previa
                lineas = texto.split('\n')
                texto_preview = '\n'.join(lineas[:3]) + "..."
                
                self.engine.say(texto_preview)
                self.engine.runAndWait()
                
                self.reproduciendo = False
                self.btn_preview.config(state=tk.NORMAL)
                self.btn_detener.config(state=tk.DISABLED)
                self.label_estado.config(text="Vista previa completada")
                
            except Exception as e:
                self.reproduciendo = False
                self.btn_preview.config(state=tk.NORMAL)
                self.btn_detener.config(state=tk.DISABLED)
                messagebox.showerror("Error", f"Error durante la reproducción: {e}")
                self.label_estado.config(text="Error en la reproducción")
        
        # Ejecutar en un hilo separado para no bloquear la interfaz
        thread = threading.Thread(target=reproducir, daemon=True)
        thread.start()
    
    def detener_reproduccion(self):
        """Detiene la reproducción actual"""
        if self.engine and self.reproduciendo:
            try:
                self.engine.stop()
                self.reproduciendo = False
                self.btn_preview.config(state=tk.NORMAL)
                self.btn_detener.config(state=tk.DISABLED)
                self.label_estado.config(text="Reproducción detenida")
            except Exception as e:
                messagebox.showerror("Error", f"Error al detener: {e}")
    
    def guardar_audio(self):
        """Guarda el audio en un archivo"""
        def guardar():
            texto = self.text_area.get(1.0, tk.END).strip()
            if not texto:
                messagebox.showwarning("Advertencia", "Por favor, ingresa algún texto.")
                return
            
            nombre_archivo = self.entry_nombre.get().strip()
            if not nombre_archivo:
                messagebox.showwarning("Advertencia", "Por favor, ingresa un nombre para el archivo.")
                return
            
            if not self.configurar_motor():
                return
            
            try:
                self.progress.start()
                self.label_estado.config(text="Generando archivo de audio...")
                
                # Obtener ruta de guardado
                ruta_documentos = Path.home() / "Documents" / nombre_archivo
                
                # Asegurar que tenga extensión .wav
                if not nombre_archivo.lower().endswith('.wav'):
                    ruta_documentos = ruta_documentos.with_suffix('.wav')
                
                # Guardar archivo
                self.engine.save_to_file(texto, str(ruta_documentos))
                self.engine.runAndWait()
                
                self.progress.stop()
                self.label_estado.config(text=f"✅ Audio guardado exitosamente")
                
                messagebox.showinfo("Éxito", f"Audio guardado en:\n{ruta_documentos}")
                
            except Exception as e:
                self.progress.stop()
                messagebox.showerror("Error", f"Error al guardar el archivo: {e}")
                self.label_estado.config(text="Error al guardar el archivo")
        
        # Ejecutar en un hilo separado
        thread = threading.Thread(target=guardar, daemon=True)
        thread.start()
    
    def cargar_archivo(self):
        """Carga texto desde un archivo"""
        try:
            archivo = filedialog.askopenfilename(
                title="Seleccionar archivo de texto",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, contenido)
                
                self.label_estado.config(text=f"Archivo cargado: {Path(archivo).name}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {e}")
    
    def limpiar_texto(self):
        """Limpia el área de texto"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar todo el texto?"):
            self.text_area.delete(1.0, tk.END)
            self.label_estado.config(text="Texto limpiado")

def main():
    """Función principal"""
    root = tk.Tk()
    app = GeneradorAudioGUI(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()