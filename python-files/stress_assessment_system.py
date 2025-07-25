import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import datetime
import os

class SistemaEstresAcademico:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Evaluación de Estrés Académico (Test SISCO)")
        self.root.geometry("800x600")
        
        # Configurar base de datos
        self.setup_database()
        
        # Variables de control
        self.current_question = 0
        self.responses = {}
        self.student_data = {}
        
        # Base de conocimiento
        self.preguntas = {
            "filtro": [
                {"pregunta": "Durante el semestre, ¿has tenido momentos de preocupación o nerviosismo?", "tipo": "binaria"}
            ],
            "nivel": [
                {"pregunta": "Señala tu nivel de preocupación o nerviosismo (1=poco a 5=mucho)", "tipo": "escala"}
            ],
            "frecuencia": [
                "Competencia con los compañeros del grupo.",
                "Sobrecarga de tareas y trabajos universitarios.",
                "La personalidad y el carácter del profesor.",
                "Las evaluaciones de los profesores(examenes,trabajos de investigacion,etc.)",
                "El tipo de trabajo que te piden los profesores.",
                "No entender los temas que se abordan en clase.",
                "Participación en clase(responder a preguntas,exposiciones,etc.)",
                "Tiempo limitado para hacer el trabajo."
            ],
            "reacciones": [
                "Trastornos en el sueño(insomnio o pesadillas).",
                "Fatiga crónica(cansancio permanente).",
                "Dolores de cabeza o migrañas.",
                "Problemas de digestión, dolor abdominal o diarrea.",
                "Rascarse, morderse las uñas,frotarse,etc.",
                "Somnolencia o mayor necesidad de dormir.",
                "Inquietud (incapacidad de relajarse y estar tranquilo).",
                "Sentimientos de depresión y tristeza (decaído)..",
                "Ansiedad, angustia o desesperación.",
                "Problemas de concentración.",
                "Sentimiento de agresividad o aumento de irritabilidad.",
                "Conflictos o tendencia a polemizar o discutir",
                "Aislamiento de los demás",
                "Desgano para realizar las labores academicas.",
                "Aumento o reducción del consumo de alimentos."
            ],
            "afrontamiento": [
                "Habilidad asertiva (defender nuestras preferencias, ideas o sentimientos sin dañar a otros).",
                "Elaboración de un plan y ejecución de sus tareas.",
                "Elogios a sí mismo.",
                "La religiosidad (oraciones o asistencia a misa).",
                "Búsqueda de información sobre la situación.",
                "Ventilación y confidencias (verbalización de la situación que preocupa).",
                "Otras estrategias."
            ]
        }
        
        self.create_main_interface()
    
    def setup_database(self):
        """Configurar base de datos SQLite"""
        # Intentar conectar y verificar la estructura
        self.conn = sqlite3.connect('estres_academico.db')
        self.cursor = self.conn.cursor()
        
        try:
            # Verificar si las tablas existen y tienen la estructura correcta
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estudiantes'")
            table_exists = self.cursor.fetchone()
            
            if table_exists:
                # Verificar estructura de la tabla existente
                self.cursor.execute("PRAGMA table_info(estudiantes)")
                existing_columns = [column[1] for column in self.cursor.fetchall()]
                required_columns = ['id', 'nombre', 'edad', 'carrera', 'semestre', 'fecha_evaluacion', 'puntaje_total', 'nivel_estres']
                
                # Si faltan columnas, recrear la tabla
                if not all(col in existing_columns for col in required_columns):
                    print("Estructura de tabla incorrecta, recreando...")
                    self.cursor.execute("DROP TABLE IF EXISTS estudiantes")
                    self.cursor.execute("DROP TABLE IF EXISTS respuestas")
                    self.conn.commit()
                else:
                    print("Tabla con estructura correcta encontrada")
                    return
            
            # Crear tablas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edad INTEGER,
                    carrera TEXT,
                    semestre TEXT,
                    fecha_evaluacion TEXT,
                    puntaje_total INTEGER,
                    nivel_estres TEXT
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS respuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudiante_id INTEGER,
                    categoria TEXT,
                    pregunta TEXT,
                    respuesta INTEGER,
                    FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
                )
            ''')
            
            self.conn.commit()
            print("Base de datos configurada exitosamente")
            
            # Verificar estructura final
            self.cursor.execute("PRAGMA table_info(estudiantes)")
            columns = [column[1] for column in self.cursor.fetchall()]
            print(f"Columnas en tabla estudiantes: {columns}")
            
        except sqlite3.Error as e:
            print(f"Error configurando base de datos: {e}")
            # En caso de error, intentar recrear completamente
            try:
                self.conn.close()
                if os.path.exists('estres_academico.db'):
                    os.remove('estres_academico.db')
                    print("Base de datos eliminada")
                
                # Reconectar y crear nuevamente
                self.conn = sqlite3.connect('estres_academico.db')
                self.cursor = self.conn.cursor()
                
                self.cursor.execute('''
                    CREATE TABLE estudiantes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        edad INTEGER,
                        carrera TEXT,
                        semestre TEXT,
                        fecha_evaluacion TEXT,
                        puntaje_total INTEGER,
                        nivel_estres TEXT
                    )
                ''')
                
                self.cursor.execute('''
                    CREATE TABLE respuestas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        estudiante_id INTEGER,
                        categoria TEXT,
                        pregunta TEXT,
                        respuesta INTEGER,
                        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
                    )
                ''')
                
                self.conn.commit()
                print("Base de datos recreada exitosamente")
                
            except Exception as recreate_error:
                print(f"Error recreando base de datos: {recreate_error}")
                raise
    
    def create_main_interface(self):
        """Crear interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Evaluación de Estrés Académico", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Botones principales
        ttk.Button(main_frame, text="Nueva Evaluación", 
                  command=self.start_new_assessment, width=20).grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(main_frame, text="Ver Reportes", 
                  command=self.show_reports, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(main_frame, text="Exportar a Excel", 
                  command=self.export_to_excel, width=20).grid(row=1, column=2, padx=5, pady=5)
        
        # Frame para mostrar estadísticas rápidas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas Generales", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.grid(row=0, column=0)
        
        self.update_stats()
    
    def update_stats(self):
        """Actualizar estadísticas generales"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM estudiantes")
            total = self.cursor.fetchone()[0]
            
            if total > 0:
                self.cursor.execute("SELECT nivel_estres, COUNT(*) FROM estudiantes WHERE nivel_estres IS NOT NULL GROUP BY nivel_estres")
                results = self.cursor.fetchall()
                
                stats_text = f"Total de evaluaciones: {total}\n"
                for nivel, count in results:
                    if nivel:
                        stats_text += f"{nivel}: {count}\n"
            else:
                stats_text = "No hay evaluaciones registradas"
            
            self.stats_label.config(text=stats_text)
            
        except sqlite3.Error as e:
            print(f"Error actualizando estadísticas: {e}")
            self.stats_label.config(text="Error cargando estadísticas")
    
    def start_new_assessment(self):
        """Iniciar nueva evaluación"""
        self.assessment_window = tk.Toplevel(self.root)
        self.assessment_window.title("Nueva Evaluación")
        self.assessment_window.geometry("600x500")
        
        # Reiniciar variables
        self.current_question = 0
        self.responses = {}
        self.student_data = {}
        
        self.show_student_info_form()
    
    def show_student_info_form(self):
        """Mostrar formulario de información del estudiante"""
        for widget in self.assessment_window.winfo_children():
            widget.destroy()
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.assessment_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título centrado
        title_label = ttk.Label(main_frame, text="Información del Estudiante", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para el formulario con grid
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(anchor=tk.CENTER)
        
        # Configurar columnas del grid
        form_frame.columnconfigure(1, weight=1, minsize=300)
        
        # Campos de información con grid layout
        ttk.Label(form_frame, text="Nombre:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=8)
        self.nombre_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
        self.nombre_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8)
        
        ttk.Label(form_frame, text="Edad:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=8)
        self.edad_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
        self.edad_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8)
        
        ttk.Label(form_frame, text="Carrera:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=8)
        self.carrera_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
        self.carrera_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8)
        
        ttk.Label(form_frame, text="Semestre:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=8)
        self.semestre_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
        self.semestre_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=8)
        
        # Botón centrado
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(30, 0))
        
        ttk.Button(button_frame, text="Comenzar Evaluación", 
                  command=self.validate_and_start_questions).pack()
    
    def validate_and_start_questions(self):
        """Validar información y comenzar preguntas"""
        if not all([self.nombre_entry.get(), self.edad_entry.get(), 
                   self.carrera_entry.get(), self.semestre_entry.get()]):
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        try:
            edad = int(self.edad_entry.get())
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número")
            return
        
        self.student_data = {
            'nombre': self.nombre_entry.get(),
            'edad': edad,
            'carrera': self.carrera_entry.get(),
            'semestre': self.semestre_entry.get()
        }
        
        self.show_filter_question()
    
    def show_filter_question(self):
        """Mostrar pregunta filtro"""
        for widget in self.assessment_window.winfo_children():
            widget.destroy()
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.assessment_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título centrado
        title_label = ttk.Label(main_frame, text="Pregunta Filtro", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para la pregunta
        question_frame = ttk.Frame(main_frame)
        question_frame.pack(anchor=tk.CENTER, fill=tk.X, padx=50)
        
        question_text = self.preguntas["filtro"][0]["pregunta"]
        question_label = ttk.Label(question_frame, text=question_text, 
                                  wraplength=500, font=("Arial", 11),
                                  justify=tk.CENTER)
        question_label.pack(pady=(0, 30))
        
        # Frame para opciones con grid
        options_frame = ttk.Frame(question_frame)
        options_frame.pack(anchor=tk.CENTER)
        
        self.filter_var = tk.StringVar()
        
        # Radio buttons alineados
        ttk.Radiobutton(options_frame, text="Sí", variable=self.filter_var, 
                       value="si", width=10).grid(row=0, column=0, padx=20, pady=8, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="No", variable=self.filter_var, 
                       value="no", width=10).grid(row=1, column=0, padx=20, pady=8, sticky=tk.W)
        
        # Botón centrado
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(40, 0))
        
        ttk.Button(button_frame, text="Continuar", 
                  command=self.process_filter_response, width=15).pack()
    
    def process_filter_response(self):
        """Procesar respuesta del filtro"""
        if not self.filter_var.get():
            messagebox.showerror("Error", "Por favor seleccione una opción")
            return
        
        if self.filter_var.get() == "no":
            self.save_no_stress_result()
            return
        
        self.show_level_question()
    
    def save_no_stress_result(self):
        """Guardar resultado sin estrés"""
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
                INSERT INTO estudiantes (nombre, edad, carrera, semestre, fecha_evaluacion, puntaje_total, nivel_estres)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.student_data['nombre'], self.student_data['edad'], 
                  self.student_data['carrera'], self.student_data['semestre'],
                  fecha, 0, "Sin estrés académico"))
            
            self.conn.commit()
            
            messagebox.showinfo("Resultado", "Diagnóstico: Sin presencia de estrés académico")
            self.assessment_window.destroy()
            self.update_stats()
            
        except sqlite3.Error as e:
            print(f"Error guardando resultado sin estrés: {e}")
            messagebox.showerror("Error", f"Error al guardar resultado: {str(e)}")
    
    def show_level_question(self):
        """Mostrar pregunta de nivel"""
        for widget in self.assessment_window.winfo_children():
            widget.destroy()
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.assessment_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título centrado
        title_label = ttk.Label(main_frame, text="Nivel de Nerviosismo", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para la pregunta
        question_frame = ttk.Frame(main_frame)
        question_frame.pack(anchor=tk.CENTER, fill=tk.X, padx=50)
        
        question_text = self.preguntas["nivel"][0]["pregunta"]
        question_label = ttk.Label(question_frame, text=question_text, 
                                  wraplength=500, font=("Arial", 11),
                                  justify=tk.CENTER)
        question_label.pack(pady=(0, 30))
        
        # Frame para opciones con grid
        options_frame = ttk.Frame(question_frame)
        options_frame.pack(anchor=tk.CENTER)
        
        self.level_var = tk.IntVar()
        
        # Radio buttons alineados con descripciones
        options = [
            (1, "1 - Poco"),
            (2, "2 - Algo"),
            (3, "3 - Regular"),
            (4, "4 - Bastante"),
            (5, "5 - Mucho")
        ]
        
        for i, (value, text) in enumerate(options):
            ttk.Radiobutton(options_frame, text=text, variable=self.level_var, 
                           value=value, width=15).grid(row=i, column=0, padx=20, pady=5, sticky=tk.W)
        
        # Botón centrado
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(40, 0))
        
        ttk.Button(button_frame, text="Continuar", 
                  command=self.process_level_response, width=15).pack()
    
    def process_level_response(self):
        """Procesar respuesta de nivel"""
        if not self.level_var.get():
            messagebox.showerror("Error", "Por favor seleccione una opción")
            return
        
        self.responses["nivel"] = self.level_var.get()
        self.current_category = "frecuencia"
        self.current_question = 0
        self.show_category_questions()
    
    def show_category_questions(self):
        """Mostrar preguntas de categoría actual"""
        categories = ["frecuencia", "reacciones", "afrontamiento"]
        
        if self.current_category not in categories:
            self.calculate_final_result()
            return
        
        questions = self.preguntas[self.current_category]
        
        if self.current_question >= len(questions):
            # Pasar a la siguiente categoría
            current_index = categories.index(self.current_category)
            if current_index + 1 < len(categories):
                self.current_category = categories[current_index + 1]
                self.current_question = 0
                self.show_category_questions()
            else:
                self.calculate_final_result()
            return
        
        for widget in self.assessment_window.winfo_children():
            widget.destroy()
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.assessment_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        category_titles = {
            "frecuencia": "Frecuencia de Situaciones Estresantes",
            "reacciones": "Reacciones al Estrés",
            "afrontamiento": "Estrategias de Afrontamiento"
        }
        
        # Título y progreso
        title_label = ttk.Label(main_frame, text=category_titles[self.current_category], 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        progress_text = f"Pregunta {self.current_question + 1} de {len(questions)}"
        progress_label = ttk.Label(main_frame, text=progress_text, font=("Arial", 10))
        progress_label.pack(pady=(0, 20))
        
        # Frame para la pregunta
        question_frame = ttk.Frame(main_frame)
        question_frame.pack(anchor=tk.CENTER, fill=tk.X, padx=30)
        
        question_text = questions[self.current_question]
        question_label = ttk.Label(question_frame, text=question_text, 
                                  wraplength=500, font=("Arial", 11),
                                  justify=tk.LEFT)
        question_label.pack(pady=(0, 25))
        
        # Frame para opciones con grid
        options_frame = ttk.Frame(question_frame)
        options_frame.pack(anchor=tk.CENTER)
        
        self.question_var = tk.IntVar()
        scale_labels = [
            (1, "1 - Nunca"),
            (2, "2 - Rara vez"),
            (3, "3 - Algunas veces"),
            (4, "4 - Casi siempre"),
            (5, "5 - Siempre")
        ]
        
        for i, (value, label) in enumerate(scale_labels):
            ttk.Radiobutton(options_frame, text=label, variable=self.question_var, 
                           value=value, width=20).grid(row=i, column=0, padx=20, pady=4, sticky=tk.W)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(30, 0))
        
        # Crear frame interno para centrar botones
        buttons_inner = ttk.Frame(button_frame)
        buttons_inner.pack()
        
        if self.current_question > 0:
            ttk.Button(buttons_inner, text="◀ Anterior", 
                      command=self.previous_question, width=12).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_inner, text="Siguiente ▶", 
                  command=self.next_question, width=12).pack(side=tk.LEFT)
    
    def previous_question(self):
        """Ir a pregunta anterior"""
        if self.current_question > 0:
            self.current_question -= 1
            self.show_category_questions()
    
    def next_question(self):
        """Ir a siguiente pregunta"""
        if not self.question_var.get():
            messagebox.showerror("Error", "Por favor seleccione una opción")
            return
        
        # Guardar respuesta
        if self.current_category not in self.responses:
            self.responses[self.current_category] = []
        
        if len(self.responses[self.current_category]) <= self.current_question:
            self.responses[self.current_category].append(self.question_var.get())
        else:
            self.responses[self.current_category][self.current_question] = self.question_var.get()
        
        self.current_question += 1
        self.show_category_questions()
    
    def calculate_final_result(self):
        """Calcular y mostrar resultado final"""
        try:
            total_score = self.responses.get("nivel", 0)
            
            for category in ["frecuencia", "reacciones", "afrontamiento"]:
                if category in self.responses:
                    total_score += sum(self.responses[category])
            
            # Determinar nivel de estrés
            if total_score <= 33:
                nivel_estres = "Nivel de estrés académico LEVE"
            elif 34 <= total_score <= 66:
                nivel_estres = "Nivel de estrés académico MODERADO"
            else:
                nivel_estres = "Nivel de estrés académico PROFUNDO"
            
            # Guardar en base de datos
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
                INSERT INTO estudiantes (nombre, edad, carrera, semestre, fecha_evaluacion, puntaje_total, nivel_estres)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.student_data['nombre'], self.student_data['edad'], 
                  self.student_data['carrera'], self.student_data['semestre'],
                  fecha, total_score, nivel_estres))
            
            student_id = self.cursor.lastrowid
            
            # Guardar respuestas detalladas
            for category, responses in self.responses.items():
                if category == "nivel":
                    self.cursor.execute('''
                        INSERT INTO respuestas (estudiante_id, categoria, pregunta, respuesta)
                        VALUES (?, ?, ?, ?)
                    ''', (student_id, category, self.preguntas["nivel"][0]["pregunta"], responses))
                else:
                    questions = self.preguntas[category]
                    for i, response in enumerate(responses):
                        if i < len(questions):  # Verificar que el índice sea válido
                            self.cursor.execute('''
                                INSERT INTO respuestas (estudiante_id, categoria, pregunta, respuesta)
                                VALUES (?, ?, ?, ?)
                            ''', (student_id, category, questions[i], response))
            
            self.conn.commit()
            
            # Mostrar resultado
            result_text = f"Evaluación completada!\n\nPuntaje total: {total_score}\nDiagnóstico: {nivel_estres}"
            messagebox.showinfo("Resultado", result_text)
            
            self.assessment_window.destroy()
            self.update_stats()
            
        except sqlite3.Error as e:
            print(f"Error calculando resultado final: {e}")
            messagebox.showerror("Error", f"Error al guardar resultado: {str(e)}")
        except Exception as e:
            print(f"Error inesperado: {e}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def show_reports(self):
        """Mostrar ventana de reportes"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("Reportes")
        reports_window.geometry("800x600")
        
        # Frame para controles
        control_frame = ttk.Frame(reports_window, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Button(control_frame, text="Actualizar", 
                  command=lambda: self.load_reports_data(tree)).pack(side=tk.LEFT, padx=5)
        
        # Treeview para mostrar datos
        columns = ("ID", "Nombre", "Edad", "Carrera", "Semestre", "Fecha", "Puntaje", "Nivel")
        tree = ttk.Treeview(reports_window, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(reports_window, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(reports_window, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.load_reports_data(tree)
    
    def load_reports_data(self, tree):
        """Cargar datos en el reporte"""
        try:
            # Limpiar datos existentes
            for item in tree.get_children():
                tree.delete(item)
            
            # Cargar datos de la base de datos
            self.cursor.execute('''
                SELECT id, nombre, edad, carrera, semestre, fecha_evaluacion, puntaje_total, nivel_estres
                FROM estudiantes ORDER BY fecha_evaluacion DESC
            ''')
            
            for row in self.cursor.fetchall():
                tree.insert("", tk.END, values=row)
                
        except sqlite3.Error as e:
            print(f"Error cargando datos del reporte: {e}")
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def export_to_excel(self):
        """Exportar datos a Excel"""
        try:
            # Obtener datos
            self.cursor.execute('''
                SELECT nombre, edad, carrera, semestre, fecha_evaluacion, puntaje_total, nivel_estres
                FROM estudiantes ORDER BY fecha_evaluacion DESC
            ''')
            
            data = self.cursor.fetchall()
            
            if not data:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Crear DataFrame
            df = pd.DataFrame(data, columns=['Nombre', 'Edad', 'Carrera', 'Semestre', 
                                           'Fecha Evaluación', 'Puntaje Total', 'Nivel de Estrés'])
            
            # Seleccionar archivo de destino
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados exitosamente a {filename}")
        
        except sqlite3.Error as e:
            print(f"Error en consulta de base de datos: {e}")
            messagebox.showerror("Error", f"Error al acceder a los datos: {str(e)}")
        except Exception as e:
            print(f"Error al exportar: {e}")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()
        self.conn.close()

if __name__ == "__main__":
    app = SistemaEstresAcademico()
    app.run()