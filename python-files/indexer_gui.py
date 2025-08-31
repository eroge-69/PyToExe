# indexer_gui.py

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import pickle
import threading
import queue

# Establecer la ruta de los modelos ANTES de importar deepface
project_path = os.path.dirname(os.path.abspath(__file__))
os.environ['DEEPFACE_HOME'] = project_path
from deepface import DeepFace

class IndexerApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Generador de Embeddings Faciales")
        self.window.geometry("600x500")

        # --- Variables ---
        self.db_path = tk.StringVar(value="database")
        self.model_name = tk.StringVar(value="ArcFace")
        self.models = ["ArcFace", "FaceNet", "VGG-Face", "SFace"]
        
        # Cola para comunicación entre el hilo de trabajo y la GUI
        self.queue = queue.Queue()

        # --- Creación de Widgets ---
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sección de Configuración ---
        config_frame = ttk.Labelframe(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(config_frame, text="Carpeta de DB:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.db_path_entry = ttk.Entry(config_frame, textvariable=self.db_path, width=40)
        self.db_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(config_frame, text="Seleccionar...", command=self.select_db_path).grid(row=0, column=2, padx=5)

        ttk.Label(config_frame, text="Modelo IA:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_name, values=self.models, state="readonly")
        self.model_combo.grid(row=1, column=1, sticky=tk.EW, padx=5)
        
        config_frame.columnconfigure(1, weight=1)

        # --- Sección de Acción ---
        self.start_button = ttk.Button(main_frame, text="Iniciar Indexación", command=self.start_indexing)
        self.start_button.pack(pady=10)

        # --- Sección de Progreso ---
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, expand=True)
        self.status_label = ttk.Label(progress_frame, text="Listo para iniciar.")
        self.status_label.pack(fill=tk.X, pady=5)

        # --- Log en Tiempo Real ---
        log_frame = ttk.Labelframe(main_frame, text="Registro de Proceso", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.configure(state='disabled') # Hacerlo de solo lectura

    def select_db_path(self):
        """Abre un diálogo para seleccionar la carpeta de la base de datos."""
        path = filedialog.askdirectory(title="Seleccione la carpeta de la base de datos de imágenes")
        if path:
            self.db_path.set(path)
    
    def log(self, message):
        """Añade un mensaje al área de log en la GUI."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END) # Auto-scroll
        self.log_area.configure(state='disabled')

    def start_indexing(self):
        """Inicia el proceso de indexación en un hilo separado."""
        db_path = self.db_path.get()
        model = self.model_name.get()

        if not os.path.isdir(db_path):
            messagebox.showerror("Error", f"La carpeta especificada no existe:\n{db_path}")
            return
            
        # Deshabilitar botón para evitar múltiples clics
        self.start_button.config(state="disabled")
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END) # Limpiar log anterior
        self.log_area.configure(state='disabled')
        self.progress_bar["value"] = 0
        self.status_label.config(text="Iniciando...")

        # Iniciar el hilo de trabajo
        self.thread = threading.Thread(target=self._run_indexing_thread, args=(db_path, model), daemon=True)
        self.thread.start()
        
        # Iniciar el monitoreo de la cola
        self.window.after(100, self.process_queue)

    def process_queue(self):
        """Procesa los mensajes de la cola para actualizar la GUI."""
        try:
            while True:
                msg = self.queue.get_nowait()
                if isinstance(msg, str):
                    self.log(msg)
                    if "¡Indexación completada!" in msg or "Error" in msg:
                        self.status_label.config(text=msg.split("\n")[0])
                        self.start_button.config(state="normal")
                elif isinstance(msg, (int, float)):
                    self.progress_bar["value"] = msg
                    self.status_label.config(text=f"Procesando... {msg:.1f}%")

        except queue.Empty:
            # Si la cola está vacía, volver a verificar después de 100ms si el hilo sigue vivo
            if self.thread.is_alive():
                self.window.after(100, self.process_queue)
            else:
                self.start_button.config(state="normal")

    def _run_indexing_thread(self, db_path, model_name):
        """La función que se ejecuta en el hilo. Contiene la lógica pesada."""
        try:
            embeddings_file = f"representations_{model_name.lower()}.pkl"
            
            image_files = [f for f in os.listdir(db_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            total_files = len(image_files)
            if not image_files:
                self.queue.put(f"Error: No se encontraron imágenes en la carpeta '{db_path}'")
                return

            self.queue.put(f"Iniciando indexación de {total_files} imágenes con el modelo {model_name}...")
            
            database_embeddings = []
            processed_count = 0

            for i, filename in enumerate(image_files, 1):
                image_path = os.path.join(db_path, filename)
                try:
                    embedding_objs = DeepFace.represent(img_path=image_path, model_name=model_name, enforce_detection=True, detector_backend='mtcnn')
                    embedding = embedding_objs[0]["embedding"]
                    database_embeddings.append([image_path, embedding])
                    self.queue.put(f"OK ({i}/{total_files}): {filename}")
                    processed_count += 1
                except Exception as e:
                    self.queue.put(f"ERROR ({i}/{total_files}): {filename} -> {e}")
                
                # Actualizar progreso
                progress = (i / total_files) * 100
                self.queue.put(progress)

            with open(embeddings_file, "wb") as f:
                pickle.dump(database_embeddings, f)
            
            self.queue.put(f"\n¡Indexación completada! {processed_count} de {total_files} embeddings guardados en '{embeddings_file}'.")

        except Exception as e:
            self.queue.put(f"\nError fatal durante la indexación: {e}")

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IndexerApp(root)
    root.mainloop()