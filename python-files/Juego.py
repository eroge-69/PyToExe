# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import random
import os
import threading
import time

class QuienSabeSabe(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Concurso 'Quien Sabe Sabe'")
        self.geometry("1000x800")
        self.configure(bg="#1a1a1a") # Fondo oscuro principal
        
        # Permite que la ventana principal se redimensione
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Variables de la aplicación
        self.preguntas_df = None
        self.preguntas = []
        self.indice_pregunta_actual = -1
        self.puntuacion_a = 0
        self.puntuacion_b = 0
        self.jokers_usados_a = 0
        self.jokers_usados_b = 0
        self.tiempo_restante = 10
        self.timer_running = False
        self.jokers_disponibles = {"A": {"50/50": True, "30s": True, "Publico": True},
                                   "B": {"50/50": True, "30s": True, "Publico": True}}
        self.turno_actual = None
        self.buzzer_round_active = False
        self.lock = threading.Lock()
        self.archivo_path = None
        self.MAX_JOKERS = 2
        
        # Nombres de los equipos
        self.nombre_equipo_a = "Equipo A"
        self.nombre_equipo_b = "Equipo B"

        # Configuración de estilos
        self.estilo_etiqueta_grande = {"fg": "white", "font": ("Helvetica", 18, "bold")}
        self.estilo_botones = {"bg": "#3498db", "fg": "white", "font": ("Helvetica", 12), "padx": 15, "pady": 10, "activebackground": "#2980b9"}
        self.estilo_botones_joker = {"bg": "#e67e22", "fg": "white", "font": ("Helvetica", 10), "padx": 10, "pady": 5, "activebackground": "#d35400"}
        self.estilo_botones_moderador = {"bg": "#e74c3c", "fg": "white", "font": ("Helvetica", 10), "padx": 10, "pady": 5, "activebackground": "#c0392b"}
        self.estilo_botones_turno = {"bg": "#27ae60", "fg": "white", "font": ("Helvetica", 12, "bold"), "padx": 20, "pady": 15, "activebackground": "#229954"}
        self.estilo_botones_deshabilitados = {"bg": "#5a6a7c", "fg": "white", "font": ("Helvetica", 12), "padx": 15, "pady": 10, "activebackground": "#5a6a7c"}
        
        self.crear_widgets_iniciales()
        self.reset_game_state()

    def crear_widgets_iniciales(self):
        # Marco principal que ocupa toda la ventana para el diseño de la cuadrícula
        main_frame = tk.Frame(self, bg="#1a1a1a", padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew") 
        
        # Configuración de las filas del marco principal para un diseño más compacto
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0) # Título
        main_frame.grid_rowconfigure(1, weight=0) # Puntuaciones, turnos, joker counters
        main_frame.grid_rowconfigure(2, weight=0) # Controles de la pregunta y temporizador
        main_frame.grid_rowconfigure(3, weight=1) # Pregunta y opciones (la fila que se estira)
        main_frame.grid_rowconfigure(4, weight=0) # Controles de jokers
        main_frame.grid_rowconfigure(5, weight=0) # Mensajes de estado
        main_frame.grid_rowconfigure(6, weight=0) # Botones de moderador
        
        # Marco para el título con borde redondeado (simulado)
        title_frame = tk.Frame(main_frame, bg="#2c3e50", padx=10, pady=10, relief="flat")
        title_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        tk.Label(title_frame, text="Concurso 'Quien Sabe Sabe'", bg="#2c3e50", fg="white", font=("Helvetica", 24, "bold")).pack(expand=True)

        # Marco superior para Puntuación, Botones de Turno y Contadores de Jokers
        top_info_frame = tk.Frame(main_frame, bg="#1a1a1a")
        top_info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        top_info_frame.grid_columnconfigure(0, weight=1)
        top_info_frame.grid_columnconfigure(1, weight=1)
        top_info_frame.grid_columnconfigure(2, weight=1)

        # Columna 0: Puntuación y Jokers del Equipo A
        team_a_frame = tk.Frame(top_info_frame, bg="#1a1a1a")
        team_a_frame.grid(row=0, column=0, sticky="w", padx=20)
        self.lbl_puntuacion_a = tk.Label(team_a_frame, text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}", **self.estilo_etiqueta_grande, bg="#1a1a1a")
        self.lbl_puntuacion_a.pack(anchor="w")
        self.lbl_jokers_a = tk.Label(team_a_frame, text=f"Opciones especiales {self.nombre_equipo_a}: {self.jokers_usados_a}/{self.MAX_JOKERS}", bg="#1a1a1a", fg="#f1c40f", font=("Helvetica", 12))
        self.lbl_jokers_a.pack(anchor="w")

        # Columna 1: Controles centrales (Botones de Turno, Buzzer y Temporizador)
        center_controls_frame = tk.Frame(top_info_frame, bg="#1a1a1a")
        center_controls_frame.grid(row=0, column=1)

        self.btn_turno_a = tk.Button(center_controls_frame, text=f"Turno {self.nombre_equipo_a}", command=lambda: self.start_turn("A"), state="disabled", **self.estilo_botones_turno)
        self.btn_turno_a.pack(side="left", padx=5)

        self.btn_activar_luz = tk.Button(center_controls_frame, text="Activar Luz", command=self.start_buzzer_delay, state="disabled", **self.estilo_botones_moderador)
        self.btn_activar_luz.pack(side="left", padx=5)
        
        self.luz_canvas = tk.Canvas(center_controls_frame, width=30, height=30, bg="#1a1a1a", highlightthickness=0)
        self.luz_canvas.pack(side="left", padx=5)
        self.luz_circulo = self.luz_canvas.create_oval(0, 0, 30, 30, fill="gray", outline="")

        self.lbl_tiempo = tk.Label(center_controls_frame, text=f"Tiempo: {self.tiempo_restante}", bg="#1a1a1a", fg="#f1c40f", font=("Helvetica", 16, "bold"))
        self.lbl_tiempo.pack(side="left", padx=10)
        
        self.btn_turno_b = tk.Button(center_controls_frame, text=f"Turno {self.nombre_equipo_b}", command=lambda: self.start_turn("B"), state="disabled", **self.estilo_botones_turno)
        self.btn_turno_b.pack(side="left", padx=5)
        
        # Columna 2: Puntuación y Jokers del Equipo B
        team_b_frame = tk.Frame(top_info_frame, bg="#1a1a1a")
        team_b_frame.grid(row=0, column=2, sticky="e", padx=20)
        self.lbl_puntuacion_b = tk.Label(team_b_frame, text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}", **self.estilo_etiqueta_grande, bg="#1a1a1a")
        self.lbl_puntuacion_b.pack(anchor="e")
        self.lbl_jokers_b = tk.Label(team_b_frame, text=f"Opciones especiales {self.nombre_equipo_b}: {self.jokers_usados_b}/{self.MAX_JOKERS}", bg="#1a1a1a", fg="#f1c40f", font=("Helvetica", 12))
        self.lbl_jokers_b.pack(anchor="e")
        
        # Nuevo contenedor para las indicaciones, encima de la pregunta
        status_message_frame = tk.Frame(main_frame, bg="#1a1a1a")
        status_message_frame.grid(row=2, column=0, sticky="ew", pady=(10, 5))
        status_message_frame.grid_columnconfigure(0, weight=1)
        self.lbl_turno_actual = tk.Label(status_message_frame, text="", bg="#1a1a1a", fg="white", font=("Helvetica", 16, "bold"))
        self.lbl_turno_actual.grid(row=0, column=0, sticky="nsew")

        # Contenedor para la pregunta y las opciones
        content_frame = tk.Frame(main_frame, bg="#1a1a1a")
        content_frame.grid(row=3, column=0, sticky="nsew", pady=(10, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=0) 
        content_frame.grid_rowconfigure(1, weight=1) 

        # Marco para la pregunta
        question_frame = tk.Frame(content_frame, bg="#34495e", padx=20, pady=20, relief="flat")
        question_frame.grid(row=0, column=0, pady=20, sticky="ew")
        self.lbl_pregunta = tk.Label(question_frame, text="Presiona 'Comenzar Juego' para empezar...", wraplength=900, bg="#34495e", fg="white", font=("Helvetica", 18, "bold"))
        self.lbl_pregunta.pack(expand=True, fill="both")

        # Marco para las opciones de respuesta con un nuevo formato de lista vertical
        opciones_container_frame = tk.Frame(content_frame, bg="#1a1a1a")
        opciones_container_frame.grid(row=1, column=0, sticky="nsew")
        opciones_container_frame.grid_columnconfigure(0, weight=1)
        opciones_container_frame.grid_rowconfigure(0, weight=1)
        opciones_container_frame.grid_rowconfigure(1, weight=1)
        opciones_container_frame.grid_rowconfigure(2, weight=1)
        opciones_container_frame.grid_rowconfigure(3, weight=1)

        self.botones_opcion = []
        self.labels_opcion = []
        letras_opciones = ['A', 'B', 'C', 'D']
        for i in range(4):
            opcion_item_frame = tk.Frame(opciones_container_frame, bg="#1a1a1a")
            opcion_item_frame.grid(row=i, column=0, padx=10, pady=10, sticky="nsew")
            opcion_item_frame.grid_columnconfigure(0, weight=0) 
            opcion_item_frame.grid_columnconfigure(1, weight=1)
            opcion_item_frame.grid_rowconfigure(0, weight=1)

            btn = tk.Button(opcion_item_frame, text=letras_opciones[i], command=lambda i=i: self.check_answer(self.opciones[i]), **self.estilo_botones_deshabilitados)
            btn.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            self.botones_opcion.append(btn)
            
            lbl_opcion = tk.Label(opcion_item_frame, text="", wraplength=800, bg="#000000", fg="white", font=("Helvetica", 12), padx=10, pady=10, relief="solid", bd=2, highlightcolor="white", highlightbackground="white")
            lbl_opcion.grid(row=0, column=1, sticky="nsew")
            self.labels_opcion.append(lbl_opcion)

        # Controles de Jokers
        joker_frame = tk.Frame(main_frame, bg="#1a1a1a")
        joker_frame.grid(row=4, column=0, pady=(10, 20), sticky="ew")
        joker_frame.grid_columnconfigure(0, weight=1)
        joker_frame.grid_columnconfigure(1, weight=1)
        joker_frame.grid_columnconfigure(2, weight=1)
        self.btn_5050 = tk.Button(joker_frame, text="50/50", command=self.use_5050, state="disabled", **self.estilo_botones_joker)
        self.btn_5050.grid(row=0, column=0, sticky="ew", padx=10)
        self.btn_30s = tk.Button(joker_frame, text="+30s", command=self.use_add_time, state="disabled", **self.estilo_botones_joker)
        self.btn_30s.grid(row=0, column=1, sticky="ew", padx=10)
        self.btn_publico = tk.Button(joker_frame, text="Preguntar al Público", command=self.use_ask_audience, state="disabled", **self.estilo_botones_joker)
        self.btn_publico.grid(row=0, column=2, sticky="ew", padx=10)
        
        # Botones de Moderador (Fila separada en la ventana principal)
        moderador_control_frame = tk.Frame(main_frame, bg="#1a1a1a")
        moderador_control_frame.grid(row=5, column=0, pady=(5, 10), sticky="ew")
        moderador_control_frame.grid_columnconfigure(0, weight=1)
        
        # FIX: Se crea un nuevo marco para los controles del cronómetro y se centraliza.
        timer_control_frame = tk.Frame(moderador_control_frame, bg="#1a1a1a")
        timer_control_frame.pack(fill="x", pady=5)
        
        self.btn_moderador_pausa = tk.Button(timer_control_frame, text="Pausar/Reanudar", command=self.toggle_moderador_pausa, state="disabled", bg="#e74c3c", fg="white", font=("Helvetica", 14, "bold"), padx=15, pady=10, activebackground="#c0392b")
        self.btn_moderador_pausa.pack(side="left", padx=5)
        self.btn_add_10s = tk.Button(timer_control_frame, text="+10s", command=self.add_10_seconds, state="disabled", **self.estilo_botones_moderador)
        self.btn_add_10s.pack(side="left", padx=5)
        self.btn_reset_timer = tk.Button(timer_control_frame, text="Reiniciar Cronómetro", command=self.reset_timer, state="disabled", **self.estilo_botones_moderador)
        self.btn_reset_timer.pack(side="left", padx=5)

        # Contenedor para el resto de los botones de moderador
        otros_botones_moderador_frame = tk.Frame(moderador_control_frame, bg="#1a1a1a")
        otros_botones_moderador_frame.pack(fill="x", pady=5)
        
        self.btn_comenzar_juego = tk.Button(otros_botones_moderador_frame, text="Comenzar Juego", command=self.load_questions_from_file, **self.estilo_botones_moderador)
        self.btn_comenzar_juego.pack(side="left", padx=5)
        self.btn_cambiar_db = tk.Button(otros_botones_moderador_frame, text="Cambiar DB", command=self.load_questions_from_file, state="disabled", **self.estilo_botones_moderador)
        self.btn_cambiar_db.pack(side="left", padx=5)
        self.btn_fin_del_juego = tk.Button(otros_botones_moderador_frame, text="Fin del Juego", command=self.end_game, state="disabled", **self.estilo_botones_moderador)
        self.btn_fin_del_juego.pack(side="left", padx=5)
        self.btn_reset_scores = tk.Button(otros_botones_moderador_frame, text="Reiniciar Puntuaciones", command=self.reset_scores, state="disabled", **self.estilo_botones_moderador)
        self.btn_reset_scores.pack(side="left", padx=5)
        self.btn_ajustar_puntos = tk.Button(otros_botones_moderador_frame, text="Añadir/Quitar Puntos", command=self.show_adjust_points_popup, **self.estilo_botones_moderador)
        self.btn_ajustar_puntos.pack(side="left", padx=5)
        self.btn_cambiar_nombres = tk.Button(otros_botones_moderador_frame, text="Cambiar Nombres", command=self.show_change_names_popup, **self.estilo_botones_moderador)
        self.btn_cambiar_nombres.pack(side="left", padx=5)
        self.btn_foul_play = tk.Button(otros_botones_moderador_frame, text="Foul Play", command=self.foul_play_and_pause, state="disabled", **self.estilo_botones_moderador)
        self.btn_foul_play.pack(side="left", padx=5)
        
        # FIX: El botón de "Siguiente" se mantiene en un marco propio para darle importancia.
        next_button_frame = tk.Frame(moderador_control_frame, bg="#1a1a1a")
        next_button_frame.pack(fill="x", pady=5)
        self.btn_siguiente = tk.Button(next_button_frame, text="Siguiente Pregunta", command=self.next_question, state="disabled", font=("Helvetica", 14, "bold"), padx=25, pady=15, bg="#2c3e50", fg="white", activebackground="#34495e")
        self.btn_siguiente.pack(side="right", padx=10)

    def reset_game_state(self):
        """Reinicia todas las variables a su estado inicial, incluyendo la lista de preguntas."""
        self.puntuacion_a = 0
        self.puntuacion_b = 0
        self.jokers_usados_a = 0
        self.jokers_usados_b = 0
        self.indice_pregunta_actual = -1
        self.preguntas = []
        self.jokers_disponibles = {"A": {"50/50": True, "30s": True, "Publico": True},
                                   "B": {"50/50": True, "30s": True, "Publico": True}}
        self.tiempo_restante = 10
        self.timer_running = False
        self.buzzer_round_active = False
        self.turno_actual = None

        # Actualizar la UI a un estado inicial
        self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
        self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
        self.lbl_jokers_a.config(text=f"Opciones especiales {self.nombre_equipo_a}: {self.jokers_usados_a}/{self.MAX_JOKERS}", font=("Helvetica", 12))
        self.lbl_jokers_b.config(text=f"Opciones especiales {self.nombre_equipo_b}: {self.jokers_usados_b}/{self.MAX_JOKERS}", font=("Helvetica", 12))
        self.lbl_pregunta.config(text="Presiona 'Comenzar Juego' para empezar...")
        self.lbl_turno_actual.config(text="")
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}", font=("Helvetica", 16, "bold"))
        self.luz_canvas.itemconfig(self.luz_circulo, fill="gray")
        
        letras_opciones = ['A', 'B', 'C', 'D']
        for i, boton in enumerate(self.botones_opcion):
            boton.config(text=letras_opciones[i], **self.estilo_botones_deshabilitados)
            self.labels_opcion[i].config(text="", bg="#000000", fg="white")

        # Habilitar/Deshabilitar botones
        self.btn_comenzar_juego.config(state="normal")
        self.btn_cambiar_db.config(state="disabled")
        self.btn_activar_luz.config(state="disabled")
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        self.btn_moderador_pausa.config(state="disabled")
        self.btn_foul_play.config(state="disabled")
        self.btn_add_10s.config(state="disabled")
        self.btn_reset_timer.config(state="disabled")
        self.btn_reset_scores.config(state="disabled")
        self.btn_fin_del_juego.config(state="disabled")
        self.btn_siguiente.config(state="disabled")
        self.btn_cambiar_nombres.config(state="normal")
        self.btn_ajustar_puntos.config(state="normal")

    def load_questions_from_file(self):
        """Carga las preguntas desde un archivo y prepara un nuevo juego."""
        try:
            self.archivo_path = filedialog.askopenfilename(
                title="Selecciona el archivo de Excel con las preguntas",
                filetypes=[("Archivos de Excel", "*.xlsx")]
            )
            if not self.archivo_path:
                messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
                return

            self.preguntas_df = pd.read_excel(self.archivo_path)
            
            columnas_requeridas = ['Pregunta', 'Opción A', 'Opción B', 'Opción C', 'Opción D', 'Respuesta Correcta']
            if not all(col in self.preguntas_df.columns for col in columnas_requeridas):
                columnas_faltantes = [col for col in columnas_requeridas if col not in self.preguntas_df.columns]
                error_msg = f"El archivo de Excel no tiene las columnas requeridas: {', '.join(columnas_faltantes)}. Por favor, verifica los nombres de las columnas."
                messagebox.showerror("Error de archivo", error_msg)
                return

            todas_las_preguntas = self.preguntas_df.to_dict('records')
            
            if not todas_las_preguntas:
                messagebox.showwarning("Advertencia", "El archivo de Excel no contiene preguntas.")
                return

            primera_pregunta = todas_las_preguntas[0]
            resto_preguntas = todas_las_preguntas[1:]
            random.shuffle(resto_preguntas)
            
            self.preguntas = [primera_pregunta] + resto_preguntas
            
            self.show_start_game_popup()

        except FileNotFoundError:
            messagebox.showerror("Error", "El archivo no se encontró.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo de Excel: {e}")

    def show_start_game_popup(self):
        """Muestra una ventana emergente para confirmar el inicio del juego y definir nombres de equipos."""
        popup = tk.Toplevel(self)
        popup.title("Juego Cargado")
        
        popup_width = 600
        popup_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (popup_width / 2)
        y_coordinate = (screen_height / 2) - (popup_height / 2)
        popup.geometry(f"{popup_width}x{popup_height}+{int(x_coordinate)}+{int(y_coordinate)}")
        
        popup.configure(bg="#2c3e50")
        popup.grab_set()

        filename = os.path.basename(self.archivo_path)
        tk.Label(popup, text="Base de datos cargada correctamente.", bg="#2c3e50", fg="white", font=("Helvetica", 14)).pack(pady=10)
        tk.Label(popup, text=f"Archivo: {filename}", bg="#2c3e50", fg="white", font=("Helvetica", 12, "bold")).pack()
        
        names_frame = tk.Frame(popup, bg="#2c3e50")
        names_frame.pack(pady=10)
        
        tk.Label(names_frame, text="Nombre del Equipo A:", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.entry_nombre_a = tk.Entry(names_frame)
        self.entry_nombre_a.insert(0, self.nombre_equipo_a)
        self.entry_nombre_a.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(names_frame, text="Nombre del Equipo B:", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.entry_nombre_b = tk.Entry(names_frame)
        self.entry_nombre_b.insert(0, self.nombre_equipo_b)
        self.entry_nombre_b.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        btn_frame = tk.Frame(popup, bg="#2c3e50")
        btn_frame.pack(pady=20)

        btn_empezar_nuevo = tk.Button(btn_frame, text="Empezar Juego", command=lambda: self.start_new_game_from_popup(popup), **self.estilo_botones_turno)
        btn_empezar_nuevo.pack(side="left", padx=5)

        btn_seguir_actual = tk.Button(btn_frame, text="Seguir con las puntuaciones actuales", command=lambda: self.continue_with_current_scores_from_popup(popup), **self.estilo_botones_turno)
        btn_seguir_actual.pack(side="left", padx=5)

        btn_cambiar = tk.Button(btn_frame, text="Cambiar Base de Datos", command=lambda: self.change_db_from_popup(popup), **self.estilo_botones_moderador)
        btn_cambiar.pack(side="left", padx=5)

    def change_db_from_popup(self, popup):
        """Cierra el popup actual y permite al usuario seleccionar un nuevo archivo."""
        popup.destroy()
        self.load_questions_from_file()

    def start_new_game_from_popup(self, popup):
        """Inicia un juego nuevo, reseteando las puntuaciones."""
        self.nombre_equipo_a = self.entry_nombre_a.get()
        self.nombre_equipo_b = self.entry_nombre_b.get()
        popup.destroy()
        
        self.puntuacion_a = 0
        self.puntuacion_b = 0
        self.jokers_usados_a = 0
        self.jokers_usados_b = 0
        self.indice_pregunta_actual = -1
        self.jokers_disponibles = {"A": {"50/50": True, "30s": True, "Publico": True},
                                   "B": {"50/50": True, "30s": True, "Publico": True}}
        self.tiempo_restante = 10
        self.timer_running = False
        self.buzzer_round_active = False
        self.turno_actual = None
        
        self.btn_comenzar_juego.config(state="disabled")
        self.btn_cambiar_db.config(state="normal")
        self.btn_foul_play.config(state="normal")
        self.btn_fin_del_juego.config(state="normal")
        self.btn_reset_scores.config(state="normal")
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        self.btn_siguiente.config(state="normal")
        
        self.update_team_names_on_ui()
        
        messagebox.showinfo("¡A Jugar!", f"Se cargaron {len(self.preguntas)} preguntas. La primera pregunta será la de la fila 1.")
        
        self.next_question()

    def continue_with_current_scores_from_popup(self, popup):
        """Continúa el juego con una nueva base de datos, manteniendo las puntuaciones actuales."""
        self.nombre_equipo_a = self.entry_nombre_a.get()
        self.nombre_equipo_b = self.entry_nombre_b.get()
        popup.destroy()
        
        self.indice_pregunta_actual = -1
        self.jokers_disponibles = {"A": {"50/50": True, "30s": True, "Publico": True},
                                   "B": {"50/50": True, "30s": True, "Publico": True}}
        self.tiempo_restante = 10
        self.timer_running = False
        self.buzzer_round_active = False
        self.turno_actual = None
        
        self.btn_comenzar_juego.config(state="disabled")
        self.btn_cambiar_db.config(state="normal")
        self.btn_foul_play.config(state="normal")
        self.btn_fin_del_juego.config(state="normal")
        self.btn_reset_scores.config(state="normal")
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        self.btn_siguiente.config(state="normal")
        
        self.update_team_names_on_ui()
        
        messagebox.showinfo("¡A Jugar!", f"Se cargaron {len(self.preguntas)} preguntas. La primera pregunta será la de la fila 1.")
        
        self.next_question()

    def update_team_names_on_ui(self):
        """Actualiza todos los elementos de la UI con los nombres de equipo actuales."""
        self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
        self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
        self.lbl_jokers_a.config(text=f"Opciones especiales {self.nombre_equipo_a}: {self.jokers_usados_a}/{self.MAX_JOKERS}", font=("Helvetica", 12))
        self.lbl_jokers_b.config(text=f"Opciones especiales {self.nombre_equipo_b}: {self.jokers_usados_b}/{self.MAX_JOKERS}", font=("Helvetica", 12))
        self.btn_turno_a.config(text=f"Turno {self.nombre_equipo_a}")
        self.btn_turno_b.config(text=f"Turno {self.nombre_equipo_b}")

    def show_change_names_popup(self):
        """Muestra una ventana emergente para cambiar los nombres de los equipos en cualquier momento."""
        popup = tk.Toplevel(self)
        popup.title("Cambiar Nombres de Equipo")
        popup.geometry("350x200")
        popup.configure(bg="#2c3e50")
        popup.grab_set()
        
        tk.Label(popup, text="Introduce los nuevos nombres de los equipos", bg="#2c3e50", fg="white", font=("Helvetica", 12)).pack(pady=10)
        
        names_frame = tk.Frame(popup, bg="#2c3e50")
        names_frame.pack(pady=10)
        
        tk.Label(names_frame, text=f"{self.nombre_equipo_a}:", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        entry_a = tk.Entry(names_frame)
        entry_a.insert(0, self.nombre_equipo_a)
        entry_a.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(names_frame, text=f"{self.nombre_equipo_b}:", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=2, sticky="e")
        entry_b = tk.Entry(names_frame)
        entry_b.insert(0, self.nombre_equipo_b)
        entry_b.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        def save_names_and_continue():
            self.nombre_equipo_a = entry_a.get()
            self.nombre_equipo_b = entry_b.get()
            self.update_team_names_on_ui()
            messagebox.showinfo("Nombres Actualizados", "Los nombres de los equipos han sido actualizados.")
            popup.destroy()
        
        tk.Button(popup, text="Guardar y Continuar", command=save_names_and_continue, **self.estilo_botones_turno).pack(pady=10)
    
    def show_adjust_points_popup(self):
        """Muestra una ventana emergente para que el moderador añada o quite puntos."""
        self.timer_running = False
        
        popup = tk.Toplevel(self)
        popup.title("Ajustar Puntos")
        popup.geometry("350x250")
        popup.configure(bg="#2c3e50")
        popup.grab_set()
        
        tk.Label(popup, text="Ajustar puntos de los equipos", bg="#2c3e50", fg="white", font=("Helvetica", 14)).pack(pady=10)
        
        self.equipo_seleccionado = tk.StringVar(self)
        self.equipo_seleccionado.set("A")
        
        frame_equipos = tk.Frame(popup, bg="#2c3e50")
        frame_equipos.pack(pady=5)
        tk.Radiobutton(frame_equipos, text=self.nombre_equipo_a, variable=self.equipo_seleccionado, value="A", bg="#2c3e50", fg="white", selectcolor="#1a1a1a").pack(side="left", padx=10)
        tk.Radiobutton(frame_equipos, text=self.nombre_equipo_b, variable=self.equipo_seleccionado, value="B", bg="#2c3e50", fg="white", selectcolor="#1a1a1a").pack(side="left", padx=10)
        
        tk.Label(popup, text="Cantidad de puntos:", bg="#2c3e50", fg="white", font=("Helvetica", 12)).pack(pady=(10, 0))
        self.entry_puntos_ajuste = tk.Entry(popup, width=10)
        self.entry_puntos_ajuste.insert(0, "0")
        self.entry_puntos_ajuste.pack(pady=5)
        
        frame_botones_ajuste = tk.Frame(popup, bg="#2c3e50")
        frame_botones_ajuste.pack(pady=10)
        
        btn_anadir = tk.Button(frame_botones_ajuste, text="Añadir Puntos", command=lambda: self.apply_points_adjustment(1, popup), bg="#27ae60", fg="white", font=("Helvetica", 12), width=15)
        btn_anadir.pack(side="left", padx=5)
        
        btn_quitar = tk.Button(frame_botones_ajuste, text="Quitar Puntos", command=lambda: self.apply_points_adjustment(-1, popup), bg="#e74c3c", fg="white", font=("Helvetica", 12), width=15)
        btn_quitar.pack(side="left", padx=5)

    def apply_points_adjustment(self, signo, popup):
        """Aplica el ajuste de puntos al equipo seleccionado."""
        try:
            puntos = int(self.entry_puntos_ajuste.get())
            equipo = self.equipo_seleccionado.get()
            
            ajuste = puntos * signo
            
            if equipo == "A":
                self.puntuacion_a += ajuste
                self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
            else:
                self.puntuacion_b += ajuste
                self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
                
            accion = "añadido" if signo == 1 else "restado"
            nombre_equipo = self.nombre_equipo_a if equipo == "A" else self.nombre_equipo_b
            messagebox.showinfo("Ajuste de Puntos", f"Se han {accion} {puntos} puntos al equipo {nombre_equipo}.")
            
            popup.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número válido para los puntos.")

    def display_question(self):
        self.tiempo_restante = 10
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}", font=("Helvetica", 16, "bold"))
        
        self.reset_ui_per_question()
        self.lbl_turno_actual.config(text="Presiona 'Activar Luz' para comenzar el turno de los buzzers.")
        
        pregunta_actual = self.preguntas[self.indice_pregunta_actual]
        self.lbl_pregunta.config(text=pregunta_actual['Pregunta'])
        
        self.opciones = [pregunta_actual['Opción A'], pregunta_actual['Opción B'], pregunta_actual['Opción C'], pregunta_actual['Opción D']]
        random.shuffle(self.opciones)
        
        for i in range(4):
            self.labels_opcion[i].config(text=self.opciones[i])
            self.botones_opcion[i].config(state="disabled", **self.estilo_botones_deshabilitados)
            
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        
        self.start_buzzer_setup()

    def start_buzzer_setup(self):
        self.buzzer_round_active = True
        self.luz_canvas.itemconfig(self.luz_circulo, fill="red")
        self.btn_activar_luz.config(state="normal")

    def start_buzzer_delay(self):
        if self.buzzer_round_active:
            self.btn_activar_luz.config(state="disabled")
            delay_seconds = random.randint(2, 5)
            self.lbl_turno_actual.config(text="Temporizador en marcha... ¡prepárense para presionar!", fg="#f1c40f")
            self.after(delay_seconds * 1000, self.turn_light_green)

    def turn_light_green(self):
        if self.buzzer_round_active:
            self.luz_canvas.itemconfig(self.luz_circulo, fill="green")
            self.lbl_turno_actual.config(text="¡Luz verde! El moderador debe asignar el turno.", fg="#2ecc71")
            self.btn_turno_a.config(state="normal")
            self.btn_turno_b.config(state="normal")
            
    def start_turn(self, equipo):
        if not self.buzzer_round_active:
             messagebox.showwarning("Advertencia", "El turno solo se puede asignar cuando la luz está verde.")
             return
        
        self.buzzer_round_active = False
        self.turno_actual = equipo
        self.luz_canvas.itemconfig(self.luz_circulo, fill="gray")
        
        nombre_equipo = self.nombre_equipo_a if equipo == "A" else self.nombre_equipo_b
        self.lbl_turno_actual.config(text=f"¡Turno para el equipo {nombre_equipo}!", fg="#2ecc71")
        
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        
        for boton in self.botones_opcion:
            boton.config(**self.estilo_botones, state="normal")
            
        self.btn_moderador_pausa.config(state="normal")
        self.btn_add_10s.config(state="normal")
        self.btn_reset_timer.config(state="normal")
        self.start_timer()

        if (equipo == "A" and self.jokers_usados_a < self.MAX_JOKERS) or \
           (equipo == "B" and self.jokers_usados_b < self.MAX_JOKERS):
            
            if self.jokers_disponibles[equipo]["50/50"]:
                self.btn_5050.config(state="normal")
            else:
                self.btn_5050.config(state="disabled")
                
            if self.jokers_disponibles[equipo]["30s"]:
                self.btn_30s.config(state="normal")
            else:
                self.btn_30s.config(state="disabled")
                
            if self.jokers_disponibles[equipo]["Publico"]:
                self.btn_publico.config(state="normal")
            else:
                self.btn_publico.config(state="disabled")
        else:
            self.btn_5050.config(state="disabled")
            self.btn_30s.config(state="disabled")
            self.btn_publico.config(state="disabled")

    def start_timer(self):
        self.tiempo_restante = 10
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        
        with self.lock:
            if self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}")
                self.after(1000, self.update_timer)
            else:
                self.timer_running = False
                self.lbl_tiempo.config(text="¡Tiempo terminado!")
                self.disable_all_options()
                
                if self.turno_actual == "A":
                    self.puntuacion_a -= 2
                    self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
                else:
                    self.puntuacion_b -= 2
                    self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")

                self.show_feedback(tiempo_agotado=True, respuesta_correcta=self.preguntas[self.indice_pregunta_actual]['Respuesta Correcta'])

    def toggle_moderador_pausa(self):
        if self.timer_running:
            self.timer_running = False
            messagebox.showinfo("Pausa", "El moderador ha pausado el juego.")
        else:
            self.timer_running = True
            messagebox.showinfo("Reanudado", "El moderador ha reanudado el juego.")
            self.update_timer()

    # FIX: Se eliminó la verificación de self.timer_running para permitir añadir tiempo en cualquier momento.
    def add_10_seconds(self):
        self.tiempo_restante += 10
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}")
        messagebox.showinfo("Tiempo extra", "Se han añadido 10 segundos al cronómetro.")

    def reset_timer(self):
        self.tiempo_restante = 10
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}")
        messagebox.showinfo("Cronómetro reiniciado", "El cronómetro se ha reiniciado a 10 segundos.")

    def reset_scores(self):
        """Reinicia las puntuaciones de ambos equipos a cero."""
        self.puntuacion_a = 0
        self.puntuacion_b = 0
        self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
        self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
        messagebox.showinfo("Puntuaciones Reiniciadas", "Las puntuaciones de ambos equipos se han reiniciado a 0.")
            
    def end_game(self):
        self.timer_running = False
        self.disable_all_options()
        
        if self.puntuacion_a > self.puntuacion_b:
            ganador = self.nombre_equipo_a
        elif self.puntuacion_b > self.puntuacion_a:
            ganador = self.nombre_equipo_b
        else:
            ganador = "¡Es un empate!"
            
        messagebox.showinfo("Fin del Juego", f"¡El juego ha terminado!\n\nPuntuación {self.nombre_equipo_a}: {self.puntuacion_a}\nPuntuación {self.nombre_equipo_b}: {self.puntuacion_b}\n\nGanador: {ganador}")
        self.reset_game_state()

    def check_answer(self, respuesta_elegida):
        self.timer_running = False
        self.disable_all_options()
        
        pregunta_actual = self.preguntas[self.indice_pregunta_actual]
        respuesta_correcta = pregunta_actual['Respuesta Correcta']
        
        nombre_equipo = self.nombre_equipo_a if self.turno_actual == "A" else self.nombre_equipo_b
        
        if str(respuesta_elegida) == str(respuesta_correcta):
            if self.turno_actual == "A":
                self.puntuacion_a += 5
                self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
            else:
                self.puntuacion_b += 5
                self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
            self.show_feedback(correcto=True, respuesta_correcta=respuesta_correcta, respuesta_elegida=respuesta_elegida)
        else:
            if self.turno_actual == "A":
                self.puntuacion_a -= 2
                self.lbl_puntuacion_a.config(text=f"Puntuación {self.nombre_equipo_a}: {self.puntuacion_a}")
            else:
                self.puntuacion_b -= 2
                self.lbl_puntuacion_b.config(text=f"Puntuación {self.nombre_equipo_b}: {self.puntuacion_b}")
            self.show_feedback(incorrecto=True, respuesta_correcta=respuesta_correcta, respuesta_elegida=respuesta_elegida)
        
            
    def show_feedback(self, correcto=False, incorrecto=False, tiempo_agotado=False, respuesta_correcta=None, respuesta_elegida=None):
        for i, label in enumerate(self.labels_opcion):
            opcion_texto = self.opciones[i]
            if str(opcion_texto) == str(respuesta_correcta):
                label.config(bg="#27ae60", fg="white")
            if (incorrecto or tiempo_agotado) and str(opcion_texto) == str(respuesta_elegida):
                label.config(bg="#c0392b", fg="white")
        
        nombre_equipo = self.nombre_equipo_a if self.turno_actual == "A" else self.nombre_equipo_b
        
        if correcto:
            messagebox.showinfo("¡Correcto!", f"¡El equipo {nombre_equipo} ha respondido correctamente!")
        elif incorrecto:
            messagebox.showinfo("Incorrecto", f"¡Respuesta incorrecta del equipo {nombre_equipo}! La respuesta correcta era: {respuesta_correcta}. Se han restado 2 puntos.")
        elif tiempo_agotado: 
             messagebox.showinfo("Tiempo agotado", f"¡Se acabó el tiempo para el equipo {nombre_equipo}! Se han restado 2 puntos. La respuesta correcta era: {respuesta_correcta}")
        else:
             messagebox.showinfo("Tiempo agotado", f"¡Se acabó el tiempo para el equipo {nombre_equipo}! La respuesta correcta era: {respuesta_correcta}")

    def next_question(self):
        self.timer_running = False

        self.indice_pregunta_actual += 1
        if self.indice_pregunta_actual < len(self.preguntas):
            self.display_question()
        else:
            self.end_game()

    def foul_play_and_pause(self):
        self.timer_running = False
        messagebox.showinfo("Juego Pausado", "El temporizador se ha detenido para aplicar la penalización.")
        self.foul_play_popup()
    
    def foul_play_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Foul Play")
        popup.geometry("300x150")
        popup.configure(bg="#2c3e50")
        
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)

        tk.Label(popup, text="¿A qué equipo quieres restar puntos?", bg="#2c3e50", fg="white", font=("Helvetica", 12)).pack(pady=10)
        
        frame_botones = tk.Frame(popup, bg="#2c3e50")
        frame_botones.pack(pady=10)
        
        btn_equipo_a = tk.Button(frame_botones, text=f"{self.nombre_equipo_a} (-3)", command=lambda: self.apply_foul_play("A", popup), **self.estilo_botones_moderador)
        btn_equipo_a.pack(side="left", padx=5)
        
        btn_equipo_b = tk.Button(frame_botones, text=f"{self.nombre_equipo_b} (-3)", command=lambda: self.apply_foul_play("B", popup), **self.estilo_botones_moderador)
        btn_equipo_b.pack(side="left", padx=5)
        
    def apply_foul_play(self, equipo, popup):
        if equipo:
            nombre_equipo = self.nombre_equipo_a if equipo == "A" else self.nombre_equipo_b
            if equipo == "A":
                self.puntuacion_a -= 3
                self.lbl_puntuacion_a.config(text=f"Puntuación {nombre_equipo}: {self.puntuacion_a}")
            else:
                self.puntuacion_b -= 3
                self.lbl_puntuacion_b.config(text=f"Puntuación {nombre_equipo}: {self.puntuacion_b}")
            
            messagebox.showinfo("Foul Play", f"Se han restado 3 puntos al equipo {nombre_equipo}.")
        
        popup.destroy()

    def reset_ui_per_question(self):
        letras_opciones = ['A', 'B', 'C', 'D']
        for i, boton in enumerate(self.botones_opcion):
            boton.config(text=letras_opciones[i], **self.estilo_botones_deshabilitados)
            self.labels_opcion[i].config(text="", bg="#000000", fg="white")
        
        self.btn_5050.config(state="disabled")
        self.btn_30s.config(state="disabled")
        self.btn_publico.config(state="disabled")
        
        self.luz_canvas.itemconfig(self.luz_circulo, fill="gray")
        self.btn_activar_luz.config(state="disabled")
        self.buzzer_round_active = False
        
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}", font=("Helvetica", 16, "bold"))
        self.btn_moderador_pausa.config(state="disabled")
        self.btn_add_10s.config(state="disabled")
        self.btn_reset_timer.config(state="disabled")

    def disable_all_options(self):
        for boton in self.botones_opcion:
            boton.config(state="disabled")
        
        self.btn_turno_a.config(state="disabled")
        self.btn_turno_b.config(state="disabled")
        
        self.btn_5050.config(state="disabled")
        self.btn_30s.config(state="disabled")
        self.btn_publico.config(state="disabled")
        self.btn_activar_luz.config(state="disabled")
        self.btn_moderador_pausa.config(state="disabled")
        self.btn_add_10s.config(state="disabled")
        self.btn_reset_timer.config(state="disabled")
    
    # --- Funciones de Jokers ---
    def use_5050(self):
        if self.turno_actual == "A" and self.jokers_usados_a >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_a} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return
        if self.turno_actual == "B" and self.jokers_usados_b >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_b} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return

        self.jokers_disponibles[self.turno_actual]["50/50"] = False
        self.btn_5050.config(state="disabled")
        self.incrementar_contador_joker()
        
        pregunta_actual = self.preguntas[self.indice_pregunta_actual]
        respuesta_correcta = pregunta_actual['Respuesta Correcta']
        
        opciones_incorrectas = [op for op in self.opciones if str(op) != str(respuesta_correcta)]
        
        opciones_a_deshabilitar = random.sample(opciones_incorrectas, 2)
        
        for i, opcion in enumerate(self.opciones):
            if opcion in opciones_a_deshabilitar:
                self.labels_opcion[i].config(text="")
                self.botones_opcion[i].config(state="disabled")
    
    def use_add_time(self):
        if self.turno_actual == "A" and self.jokers_usados_a >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_a} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return
        if self.turno_actual == "B" and self.jokers_usados_b >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_b} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return

        self.jokers_disponibles[self.turno_actual]["30s"] = False
        self.btn_30s.config(state="disabled")
        self.incrementar_contador_joker()
        self.tiempo_restante += 30
        self.lbl_tiempo.config(text=f"Tiempo: {self.tiempo_restante}", font=("Helvetica", 16, "bold"))
        messagebox.showinfo("Tiempo extra", "Se han añadido 30 segundos a tu tiempo.")
    
    def use_ask_audience(self):
        if self.turno_actual == "A" and self.jokers_usados_a >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_a} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return
        if self.turno_actual == "B" and self.jokers_usados_b >= self.MAX_JOKERS:
            messagebox.showwarning("Límite de Jokers", f"El Equipo {self.nombre_equipo_b} ya ha usado su límite de {self.MAX_JOKERS} opciones especiales.")
            return

        self.jokers_disponibles[self.turno_actual]["Publico"] = False
        self.btn_publico.config(state="disabled")
        self.incrementar_contador_joker()
        self.timer_running = False
        messagebox.showinfo("Preguntar al público", "El tiempo se ha detenido. Un moderador debe reanudarlo para continuar.")

    def incrementar_contador_joker(self):
        if self.turno_actual == "A":
            self.jokers_usados_a += 1
            self.lbl_jokers_a.config(text=f"Opciones especiales {self.nombre_equipo_a}: {self.jokers_usados_a}/{self.MAX_JOKERS}", font=("Helvetica", 12))
        elif self.turno_actual == "B":
            self.jokers_usados_b += 1
            self.lbl_jokers_b.config(text=f"Opciones especiales {self.nombre_equipo_b}: {self.jokers_usados_b}/{self.MAX_JOKERS}", font=("Helvetica", 12))

if __name__ == "__main__":
    app = QuienSabeSabe()
    app.mainloop()

