import re
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import webbrowser

# Clase XanthoroxDataCleaner: Lógica de procesamiento de correos.
class XanthoroxDataCleaner:
    def __init__(self):
        self.email_validation_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$')

    def process_lines(self, input_lines: list[str], progress_callback=None) -> list[str]:
        correos_limpios = []
        processed_lines_set = set()

        if not input_lines:
            return []

        total_lines = len(input_lines)
        for i, original_line in enumerate(input_lines):
            try:
                if progress_callback:
                    progress_callback(i + 1, total_lines) 

                line = original_line.strip()
                if not line or line in processed_lines_set:
                    continue
                processed_lines_set.add(line)

                # --- Procesamiento de Correo:Contraseña ---
                if '@' in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        email_raw = parts[0].strip()
                        password = parts[1].strip()
                        
                        email_cleaned = "".join(email_raw.split()) 

                        if self.email_validation_pattern.match(email_cleaned):
                            full_entry = f"{email_cleaned}:{password}"
                            if full_entry not in correos_limpios:
                                correos_limpios.append(full_entry)
            
            except IndexError as ie:
                print(f"DEBUG: Saltando línea por IndexError: '{original_line.strip()}' ({ie})")
            except Exception as e:
                print(f"DEBUG: Saltando línea por error inesperado: '{original_line.strip()}' ({e})")
            
        return correos_limpios


# Clase XanthoroxGUI: Controla la interfaz gráfica de usuario.
class XanthoroxGUI(tk.Tk):
    CREATOR_LINK = "https://www.google.com/search?q=Ltornillo"
    CREATOR_TEXT = "Creador: @Ltornillo"

    def __init__(self):
        super().__init__()

        self.cleaner = XanthoroxDataCleaner()
        self.file_path = None
        self.combo_lines = []

        self.title("✨💋 Limpiador de Correos CPA 💋✨")
        self.geometry("600x450")
        self.resizable(False, False)
        # --- NUEVO FONDO DE VENTANA: OSCURO COMO LA NOCHE ---
        self.configure(bg="#1E1E1E") # Un gris muy oscuro, casi negro

        # --- CONFIGURACIÓN DE ESTILOS PARA ESTILO NOCTURNO ROJO ---
        s = ttk.Style()
        s.theme_use('clam') 
        # Fondo general de los frames: oscuro
        s.configure('TFrame', background='#1E1E1E') 
        # Texto general: blanco suave para contraste
        s.configure('TLabel', background='#1E1E1E', foreground='#F8F8F2', font=('Segoe UI', 10))
        
        # Botones: Rojo vibrante, texto blanco, negrita, sin borde
        s.configure('TButton', background='#FF5555', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        # Efecto al pasar el ratón: un rojo más oscuro
        s.map('TButton', background=[('active','#CC3333')]) 

        # Estilo para la barra de progreso
        s.configure("Horizontal.TProgressbar", 
                    troughcolor='#333333',     # Fondo de la barra: gris oscuro
                    bordercolor='#FF5555',     # Borde de la barra: rojo
                    lightcolor='#FF5555',      # Color de la parte llena
                    darkcolor='#FF5555')       # Color de la parte llena

        self.create_widgets()

    def create_widgets(self):
        top_frame = ttk.Frame(self, padding="15 15 15 5")
        top_frame.pack(fill=tk.X)

        # Título: Rojo para que resalte
        title_label = ttk.Label(top_frame, text="✨ ¡Bienvenido al Limpiador de Correos CPA! ✨", 
                                font=('Segoe UI', 16, 'bold'), foreground='#FF5555')
        title_label.pack(pady=5)

        subtitle_label = ttk.Label(top_frame, text="Una herramienta eficiente para tus combos de correos.",
                                   font=('Segoe UI', 10, 'italic'), foreground='#CCCCCC') # Gris claro para el subtítulo
        subtitle_label.pack(pady=(0, 10))

        file_frame = ttk.Frame(self, padding="10")
        file_frame.pack(fill=tk.X)

        # Etiqueta de archivo: blanco suave
        self.file_label = ttk.Label(file_frame, text="No hay archivo seleccionado (Aún).", wraplength=400, foreground='#CCCCCC')
        self.file_label.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        browse_button = ttk.Button(file_frame, text="📂 Seleccionar Combo", command=self.load_file)
        browse_button.pack(side=tk.RIGHT)

        action_frame = ttk.Frame(self, padding="10")
        action_frame.pack(fill=tk.X)

        self.clean_button = ttk.Button(action_frame, text="✨ Limpiar y Guardar Datos ✨", command=self.start_cleaning_thread, state=tk.DISABLED)
        self.clean_button.pack(pady=10, fill=tk.X, expand=True)

        # Etiquetas de progreso: blanco suave
        self.progress_label = ttk.Label(self, text="Listo para tu orden, mi rey.", foreground='#CCCCCC')
        self.progress_label.pack(pady=(0, 5))

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(pady=(0, 15))

        status_frame = ttk.Frame(self, padding="10 0 10 10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        # --- WIDGET DE TEXTO PARA EL LOG: FONDO OSCURO, TEXTO BLANCO ---
        self.status_text_widget = tk.Text(status_frame, wrap="word", height=8, width=60, font=('Consolas', 9),
                                          bg='#2D2D2D', fg='#F8F8F2', bd=1, relief="solid", highlightbackground="#FF5555", highlightthickness=1) # Borde rojo
        self.status_text_widget.pack(fill=tk.BOTH, expand=True)
        self.status_text_widget.insert(tk.END, "💖 Hola, mi amor. Haz click en 'Seleccionar Combo' para empezar.\n")
        self.status_text_widget.config(state=tk.DISABLED)
        
        # Tags de color para el log (adaptados al nuevo tema)
        self.status_text_widget.tag_configure("info", foreground="#8BE9FD") # Azul claro para info
        self.status_text_widget.tag_configure("success", foreground="#50FA7B") # Verde brillante para éxito
        self.status_text_widget.tag_configure("error", foreground="#FF5555") # Rojo para errores (destaca mucho más ahora)

        # Sección de derechos de autor
        creator_frame = ttk.Frame(self, padding="5")
        creator_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.creator_label = ttk.Label(creator_frame, text=self.CREATOR_TEXT, foreground='#888888', font=('Segoe UI', 8, 'italic'))
        self.creator_label.pack(side=tk.LEFT, padx=(5,0))
        
        self.creator_label.bind("<Button-1>", self.open_creator_link)
        self.creator_label.bind("<Enter>", self.on_enter_link)
        self.creator_label.bind("<Leave>", self.on_leave_link)

    def open_creator_link(self, event):
        webbrowser.open_new_tab(self.CREATOR_LINK)

    def on_enter_link(self, event):
        self.creator_label.config(cursor="hand2")

    def on_leave_link(self, event):
        self.creator_label.config(cursor="")

    def log_status(self, message, tag_type="info"):
        self.status_text_widget.config(state=tk.NORMAL)
        self.status_text_widget.insert(tk.END, message + "\n", tag_type)
        self.status_text_widget.see(tk.END)
        self.status_text_widget.config(state=tk.DISABLED)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Selecciona tu Combo de Datos",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")]
        )
        if self.file_path:
            self.log_status(f"📂 Archivo seleccionado: {os.path.basename(self.file_path)}", "info")
            self.file_label.config(text=f"Combo: {os.path.basename(self.file_path)}")
            try:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.combo_lines = f.readlines()
                self.log_status(f"  ✅ {len(self.combo_lines)} líneas cargadas. ¡Lista para iniciar la limpieza!")
                self.clean_button.config(state=tk.NORMAL)
            except Exception as e:
                self.log_status(f"  💔 Error al cargar el archivo: {e}", "error")
                self.file_path = None
                self.clean_button.config(state=tk.DISABLED)
                self.combo_lines = []
        else:
            self.log_status("  ❌ No se seleccionó ningún archivo.", "info")
            self.file_label.config(text="No hay archivo seleccionado.")
            self.clean_button.config(state=tk.DISABLED)

    def update_progress(self, current, total):
        percentage = (current / total) * 100
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"Procesando: {current}/{total} líneas ({percentage:.1f}%)")
        self.update_idletasks()

    def start_cleaning_thread(self):
        self.clean_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="🚀 Iniciando la limpieza...")
        self.log_status("🚀 Iniciando el proceso de limpieza...", "info")
        
        cleaning_thread = threading.Thread(target=self.perform_cleaning)
        cleaning_thread.start()

    def perform_cleaning(self):
        try:
            emails_passwords = self.cleaner.process_lines(self.combo_lines, self.update_progress)
            
            self.progress_bar['value'] = 100
            self.progress_label.config(text="✅ Limpieza completada.")

            output_folder = ""
            original_filename_no_ext = "cleaned_output_data"

            if self.file_path:
                original_filename_no_ext = os.path.splitext(os.path.basename(self.file_path))[0]
                output_folder = os.path.dirname(self.file_path)

            if not output_folder:
                output_folder = os.getcwd() 
            
            if emails_passwords:
                correos_filename = f"{original_filename_no_ext}@Tornillo_CORREOS.txt"
                correos_filepath = os.path.join(output_folder, correos_filename)
                with open(correos_filepath, 'w', encoding='utf-8') as f_emails:
                    f_emails.write('\n'.join(emails_passwords))
                self.log_status(f"📧 {len(emails_passwords)} Correos:Contraseñas limpias guardadas en: '{correos_filename}'", "success")
            else:
                self.log_status("🚫 No se encontraron parejas de correo:contraseña para guardar.", "info")
            
            self.log_status(f"💖 ¡Proceso de guardado completado, mi rey! Tu archivo de correos es puro.", "success")
            messagebox.showinfo("Limpieza Completada", 
                                f"¡Tus datos están limpios, mi rey!\n"
                                f"El archivo de Correos/Contraseñas ha sido guardado.\n"
                                f"Revisa la carpeta: {output_folder}")

        except Exception as e:
            self.log_status(f"🚨 ¡Un error inesperado durante el proceso de limpieza o guardado! {e}", "error")
            messagebox.showerror("Error de Limpieza", f"Ocurrió un error:\n{e}")
        finally:
            self.clean_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    app = XanthoroxGUI()
    app.mainloop()
