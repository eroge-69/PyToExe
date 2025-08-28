import numpy as np
import random
import time
from datetime import datetime
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, font

class VectorCompetencia:
    def __init__(self, nombre, umbral_dominio=3):
        self.nombre = nombre
        self.maestria = 0.0  # Valor entre 0 y 1
        self.respuestas_correctas = 0
        self.respuestas_totales = 0
        self.respuestas_consecutivas = 0
        self.tiempo_promedio = 0.0
        self.errores_comunes = {}
        self.umbral_dominio = umbral_dominio
    
    def actualizar(self, es_correcto, tiempo_respuesta, error_code=None):
        self.respuestas_totales += 1
        
        if es_correcto:
            self.respuestas_correctas += 1
            self.respuestas_consecutivas += 1
            
            # Actualizar tiempo promedio (media móvil)
            if self.tiempo_promedio == 0:
                self.tiempo_promedio = tiempo_respuesta
            else:
                self.tiempo_promedio = 0.8 * self.tiempo_promedio + 0.2 * tiempo_respuesta
        else:
            self.respuestas_consecutivas = 0
            if error_code:
                if error_code in self.errores_comunes:
                    self.errores_comunes[error_code] += 1
                else:
                    self.errores_comunes[error_code] = 1
        
        # Calcular nuevo nivel de maestría (fórmula que premia consistencia)
        if self.respuestas_totales > 0:
            self.maestria = min(1.0, (self.respuestas_consecutivas ** 2) / 
                               (self.respuestas_totales * self.umbral_dominio))
    
    def error_mas_comun(self):
        if not self.errores_comunes:
            return None
        return max(self.errores_comunes.items(), key=lambda x: x[1])[0]


class ModeloEstudiante:
    def __init__(self, estudiante_id):
        self.estudiante_id = estudiante_id
        self.vectores = {
            "VC1": VectorCompetencia("Significado conceptual"),
            "VC2": VectorCompetencia("Regla de signos (+)/(+) y (-)/(-)"),
            "VC3": VectorCompetencia("Regla de signos (+)/(-) y (-)/(+)"),
            "VC4": VectorCompetencia("División con cero"),
            "VC5": VectorCompetencia("Problemas en contexto")
        }
        self.historial = []
        self.estado = "INICIO"
        self.ultima_accion = None
        self.tiempo_inicio_sesion = time.time()
    
    def vector_mas_debil(self):
        return min(self.vectores.values(), key=lambda v: v.maestria)
    
    def ha_dominado_todo(self, umbral=0.8):
        return all(v.maestria >= umbral for v in self.vectores.values())
    
    def registrar_evento(self, evento, detalles):
        self.historial.append({
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "detalles": detalles,
            "estado_actual": {k: v.maestria for k, v in self.vectores.items()}
        })


class GeneradorEjercicios:
    @staticmethod
    def generar_ejercicio(vector_objetivo, nivel_dificultad):
        vc_nombre = vector_objetivo.nombre
        
        if vc_nombre == "Significado conceptual":
            return GeneradorEjercicios._ejercicio_significado_conceptual(nivel_dificultad)
        elif "Regla de signos" in vc_nombre:
            return GeneradorEjercicios._ejercicio_regla_signos(vc_nombre, nivel_dificultad)
        elif vc_nombre == "División con cero":
            return GeneradorEjercicios._ejercicio_division_cero(nivel_dificultad)
        elif vc_nombre == "Problemas en contexto":
            return GeneradorEjercicios._ejercicio_contexto(nivel_dificultad)
    
    @staticmethod
    def _ejercicio_significado_conceptual(nivel):
        if nivel == "bajo":
            a, b = random.choice([(12, 3), (15, 5), (20, 4)])
            signo_a, signo_b = "+", "+"
            pregunta = f"¿Qué significa conceptualmente la operación ({signo_a}{a}) ÷ ({signo_b}{b})?"
            opciones = [
                "Dividir una deuda entre varias personas",
                "Repartir ganancias entre socios",
                "Distribuir recursos limitados",
                "Calcular la tasa de cambio"
            ]
            respuesta_correcta = 1  # Repartir ganancias entre socios
            explicacion = "Un dividendo positivo representa ganancias o recursos positivos, y un divisor positivo representa un número de receptores."
        
        elif nivel == "medio":
            a, b = random.choice([(-12, 3), (-15, 5), (-20, 4)])
            signo_a, signo_b = "-", "+"
            pregunta = f"¿Cómo interpretas la operación ({a}) ÷ ({b}) usando la analogía de flujos de energía?"
            opciones = [
                "Una pérdida de energía distribuida entre fuentes",
                "Una ganancia de energía concentrada en pocos puntos",
                "Una deuda que se reparte entre acreedores",
                "Un excedente que se divide entre consumidores"
            ]
            respuesta_correcta = 2  # Una deuda que se reparte entre acreedores
            explicacion = "Un dividendo negativo representa una deuda o pérdida, y un divisor positivo representa entre cuántas partes se distribuye esta deuda."
        
        else:  # alto
            a, b = random.choice([(12, -3), (15, -5), (20, -4)])
            signo_a, signo_b = "+", "-"
            pregunta = f"Explica el significado de ({a}) ÷ ({b}) en términos de balance energético:"
            opciones = [
                "La energía requerida para contrarrestar consumidores",
                "La distribución de excedentes entre fuentes",
                "La pérdida sistemática en un sistema estable",
                "La ganancia neta después de compensar pérdidas"
            ]
            respuesta_correcta = 0  # La energía requerida para contrarrestar consumidores
            explicacion = "Un dividendo positivo con divisor negativo representa la energía necesaria para contrarrestar cada unidad de consumo."
        
        return {
            "tipo": "opcion_multiple",
            "pregunta": pregunta,
            "opciones": opciones,
            "respuesta_correcta": respuesta_correcta,
            "explicacion": explicacion,
            "vc": "VC1",
            "dificultad": nivel
        }
    
    @staticmethod
    def _ejercicio_regla_signos(vc_nombre, nivel):
        # Asegurar que el dividendo sea múltiplo del divisor
        if "(+)/(+) y (-)/(-)" in vc_nombre:
            if random.random() > 0.5:
                signo_a, signo_b = "+", "+"
            else:
                signo_a, signo_b = "-", "-"
        else:  # "(+)/(-) y (-)/(+)"
            if random.random() > 0.5:
                signo_a, signo_b = "+", "-"
            else:
                signo_a, signo_b = "-", "+"
        
        if nivel == "bajo":
            b = random.randint(1, 5)
            a = b * random.randint(1, 5)
            pregunta = f"Calcula: ({signo_a}{a}) ÷ ({signo_b}{b})"
        elif nivel == "medio":
            b = random.randint(2, 10)
            a = b * random.randint(1, 10)
            pregunta = f"Resuelve: ({signo_a}{a}) ÷ ({signo_b}{b})"
        else:  # alto
            b = random.randint(3, 12)
            a = b * random.randint(5, 15)
            pregunta = f"Usando la recta numérica, calcula: ({signo_a}{a}) ÷ ({signo_b}{b})"
        
        resultado = a // b
        if (signo_a == "-" and signo_b == "+") or (signo_a == "+" and signo_b == "-"):
            resultado = -resultado
        
        vc = "VC2" if "(+)/(+) y (-)/(-)" in vc_nombre else "VC3"
        
        return {
            "tipo": "respuesta_numerica",
            "pregunta": pregunta,
            "respuesta_correcta": resultado,
            "explicacion": f"La regla de signos indica que {signo_a}{a} ÷ {signo_b}{b} = {resultado}",
            "vc": vc,
            "dificultad": nivel
        }
    
    @staticmethod
    def _ejercicio_division_cero(nivel):
        scenarios = [
            ("0 ÷ 5", 0, "VC4", "Cero dividido por cualquier número distinto de cero es cero"),
            ("10 ÷ 0", 0, "VC4", "La división por cero no está definida en matemáticas"),
            ("0 ÷ 0", 0, "VC4", "La división cero entre cero es una forma indeterminada")
        ]
        
        pregunta, respuesta_correcta, vc, explicacion = random.choice(scenarios)
        
        if nivel != "bajo":
            pregunta = f"¿Cuál es el resultado de {pregunta}? Explica por qué."
        
        return {
            "tipo": "respuesta_numerica" if respuesta_correcta is not None else "explicacion",
            "pregunta": pregunta,
            "respuesta_correcta": respuesta_correcta,
            "explicacion": explicacion,
            "vc": vc,
            "dificultad": nivel
        }
    
    @staticmethod
    def _ejercicio_contexto(nivel):
        contexts = [
            {
                "scenario": "Una empresa tuvo una pérdida de $%d en los últimos %d meses. Si la pérdida fue constante cada mes, ¿cuál fue el cambio promedio mensual en el balance?",
                "values": [(15000, 3), (24000, 6), (45000, 9)],
                "expected": lambda a, b: -a // b,
                "vc": "VC5"
            },
            {
                "scenario": "Un cohete cambia su velocidad en -%d m/s durante %d segundos para realizar una corrección de órbita. ¿Cuál fue su aceleración media?",
                "values": [(100, 5), (250, 10), (500, 20)],
                "expected": lambda a, b: -a // b,
                "vc": "VC5"
            },
            {
                "scenario": "Repartir una deuda de $%d entre %d personas equitativamente. ¿Cuánto debe cada persona?",
                "values": [(120, 4), (350, 7), (810, 9)],
                "expected": lambda a, b: -a // b,
                "vc": "VC5"
            }
        ]
        
        context = random.choice(contexts)
        a, b = random.choice(context["values"])
        pregunta = context["scenario"] % (a, b)
        respuesta_correcta = context["expected"](a, b)
        
        if nivel == "alto":
            pregunta += " Explica tu razonamiento paso a paso."
        
        return {
            "tipo": "respuesta_numerica",
            "pregunta": pregunta,
            "respuesta_correcta": respuesta_correcta,
            "explicacion": f"El resultado es {respuesta_correcta} porque estamos distribuyendo una cantidad negativa entre un número positivo de partes.",
            "vc": context["vc"],
            "dificultad": nivel
        }



class MotorRetroalimentacion:
    ERRORES = {
        "E-101": "Parece que confundiste la regla de signos. Recuerda: signos iguales dan positivo, signos diferentes dan negativo.",
        "E-102": "Has dividido incorrectamente los valores absolutos. Revisa tu cálculo aritmético.",
        "E-103": "La división entre cero no está definida. Cualquier número dividido entre cero es indefinido.",
        "E-104": "Cero dividido entre cualquier número (excepto cero) es cero.",
        "E-201": "Interpretación conceptual incorrecta. Revisa la analogía de flujos de energía.",
        "E-202": "No aplicaste el contexto correctamente al problema.",
        "E-203": "Error en la traducción del problema verbal a expresión matemática."
    }
    
    @staticmethod
    def proporcionar_retroalimentacion(es_correcto, ejercicio, respuesta_estudiante, error_code=None):
        if es_correcto:
            mensajes_correctos = [
                "¡Excelente! Has aplicado perfectamente el concepto.",
                "¡Muy bien! Tu comprensión es sólida.",
                "¡Correcto! Dominas este tema.",
                "¡Perfecto! Has entendido la esencia del problema."
            ]
            return random.choice(mensajes_correctos) + " " + ejercicio.get("explicacion", "")
        else:
            mensaje = "Vamos a revisar este ejercicio.\n"
            if error_code and error_code in MotorRetroalimentacion.ERRORES:
                mensaje += MotorRetroalimentacion.ERRORES[error_code] + "\n"
            else:
                mensaje += "Tu respuesta no es correcta.\n"
            
            mensaje += f"\nExplicación: {ejercicio.get('explicacion', '')}"
            
            # Sugerencia específica según tipo de error
            if error_code == "E-101":
                mensaje += "\n\nSugerencia: Practica con la 'Ley de Signos':\n(+) ÷ (+) = +\n(-) ÷ (-) = +\n(+) ÷ (-) = -\n(-) ÷ (+) = -"
            elif error_code == "E-201":
                mensaje += "\n\nSugerencia: Recuerda la analogía:\n+ = Aporte de energía (ganancia)\n- = Pérdida de energía (deuda)\nDivisor = Número de partes"
            
            return mensaje


class OptimizadorALORA:
    def __init__(self):
        self.politica = self._inicializar_politica()
        self.recompensas_historial = []
    
    def _inicializar_politica(self):
        # Política inicial basada en conocimiento experto
        return {
            ("VC1", "bajo"): {"ejercicio": "significado", "dificultad": "bajo", "recompensa_esperada": 0},
            ("VC1", "medio"): {"ejercicio": "significado", "dificultad": "medio", "recompensa_esperada": 0},
            ("VC1", "alto"): {"ejercicio": "significado", "dificultad": "alto", "recompensa_esperada": 0},
            ("VC2", "bajo"): {"ejercicio": "regla_signos", "dificultad": "bajo", "recompensa_esperada": 0},
            ("VC2", "medio"): {"ejercicio": "regla_signos", "dificultad": "medio", "recompensa_esperada": 0},
            ("VC2", "alto"): {"ejercicio": "regla_signos", "dificultad": "alto", "recompensa_esperada": 0},
            ("VC3", "bajo"): {"ejercicio": "regla_signos", "dificultad": "bajo", "recompensa_esperada": 0},
            ("VC3", "medio"): {"ejercicio": "regla_signos", "dificultad": "medio", "recompensa_esperada": 0},
            ("VC3", "alto"): {"ejercicio": "regla_signos", "dificultad": "alto", "recompensa_esperada": 0},
            ("VC4", "bajo"): {"ejercicio": "division_cero", "dificultad": "bajo", "recompensa_esperada": 0},
            ("VC4", "medio"): {"ejercicio": "division_cero", "dificultad": "medio", "recompensa_esperada": 0},
            ("VC4", "alto"): {"ejercicio": "division_cero", "dificultad": "alto", "recompensa_esperada": 0},
            ("VC5", "bajo"): {"ejercicio": "contexto", "dificultad": "bajo", "recompensa_esperada": 0},
            ("VC5", "medio"): {"ejercicio": "contexto", "dificultad": "medio", "recompensa_esperada": 0},
            ("VC5", "alto"): {"ejercicio": "contexto", "dificultad": "alto", "recompensa_esperada": 0}
        }
    
    def elegir_accion(self, vector_objetivo):
        # Determinar nivel de dificultad basado en maestría
        if vector_objetivo.maestria < 0.4:
            nivel = "bajo"
        elif vector_objetivo.maestria < 0.7:
            nivel = "medio"
        else:
            nivel = "alto"
        
        clave = (vector_objetivo.nombre, nivel)
        
        # 80% seguir política, 20% explorar (para optimización)
        if random.random() < 0.8 or clave not in self.politica:
            # Explotar: usar la política actual
            if clave in self.politica:
                return self.politica[clave]
            else:
                # Valor por defecto si no está en la política
                return {"ejercicio": "regla_signos", "dificultad": nivel, "recompensa_esperada": 0}
        else:
            # Explorar: elegir aleatoriamente
            tipos_ejercicio = ["significado", "regla_signos", "division_cero", "contexto"]
            return {
                "ejercicio": random.choice(tipos_ejercicio),
                "dificultad": nivel,
                "recompensa_esperada": 0
            }
    
    def actualizar_politica(self, estado_anterior, accion, recompensa, estado_resultante):
        # Algoritmo de aprendizaje por refuerzo simplificado (Q-learning)
        clave = (estado_anterior.nombre, accion["dificultad"])
        
        if clave in self.politica:
            # Actualizar recompensa esperada (valor Q)
            alpha = 0.1  # Tasa de aprendizaje
            gamma = 0.9  # Factor de descuento
            
            # Calcular la mejor recompensa futura estimada
            mejor_recompensa_futura = 0
            for v in estado_resultante.vectores.values():
                nivel = "bajo" if v.maestria < 0.4 else "medio" if v.maestria < 0.7 else "alto"
                clave_futura = (v.nombre, nivel)
                if clave_futura in self.politica:
                    mejor_recompensa_futura = max(mejor_recompensa_futura, self.politica[clave_futura]["recompensa_esperada"])
            
            # Fórmula de Q-learning
            self.politica[clave]["recompensa_esperada"] = (1 - alpha) * self.politica[clave]["recompensa_esperada"] + \
                                                         alpha * (recompensa + gamma * mejor_recompensa_futura)
        
        # Guardar historial para análisis
        self.recompensas_historial.append({
            "timestamp": datetime.now().isoformat(),
            "estado_anterior": estado_anterior.nombre,
            "accion": accion,
            "recompensa": recompensa,
            "estado_resultante": estado_resultante.nombre if estado_resultante else "N/A"
        })


class AplicacionALORA:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema ALORA - Aprendizaje de División de Enteros")
        self.root.geometry("1000x700")
        
        # Inicializar componentes del sistema
        self.modelo_estudiante = ModeloEstudiante("Estudiante_01")
        self.generador = GeneradorEjercicios()
        self.motor_retro = MotorRetroalimentacion()
        self.optimizador = OptimizadorALORA()
        
        # Estado de la aplicación
        self.ejercicio_actual = None
        self.tiempo_inicio_ejercicio = 0
        self.estado = "INICIO"
        
        # Interfaz de usuario
        self.crear_interfaz()
        
        # Iniciar con un ejercicio
        self.siguiente_ejercicio()
    
    def crear_interfaz(self):
        # Configurar fuentes más grandes
        self.fuente_grande = ("Arial", 12)
        self.fuente_pregunta = ("Arial", 12, "bold")
        
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de información del estudiante
        info_frame = ttk.LabelFrame(main_frame, text="Progreso del Estudiante", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.lbl_progreso = ttk.Label(info_frame, text="Maestría: VC1: 0%, VC2: 0%, VC3: 0%, VC4: 0%, VC5: 0%", font=self.fuente_grande)
        self.lbl_progreso.grid(row=0, column=0, sticky=tk.W)
        
        self.lbl_ejercicio = ttk.Label(info_frame, text="Ejercicio: 0/0 - Tiempo: 0s", font=self.fuente_grande)
        self.lbl_ejercicio.grid(row=0, column=1, sticky=tk.E)
        
        # Panel de ejercicio
        ejercicio_frame = ttk.LabelFrame(main_frame, text="Ejercicio", padding="10")
        ejercicio_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        ejercicio_frame.columnconfigure(0, weight=1)
        ejercicio_frame.rowconfigure(0, weight=1)
        
        self.lbl_pregunta = ttk.Label(ejercicio_frame, text="Pregunta aparecerá aquí", wraplength=900, justify=tk.LEFT, font=self.fuente_pregunta)
        self.lbl_pregunta.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Panel de opciones (para preguntas de opción múltiple)
        self.frame_opciones = ttk.Frame(ejercicio_frame)
        self.frame_opciones.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.opcion_seleccionada = tk.IntVar(value=-1)
        self.botones_opciones = []
        
        for i in range(4):
            btn = ttk.Radiobutton(self.frame_opciones, variable=self.opcion_seleccionada, value=i)
            btn.grid(row=i, column=0, sticky=tk.W, pady=2)
            self.botones_opciones.append(btn)
        
        # Campo de entrada (para preguntas numéricas)
        self.frame_entrada = ttk.Frame(ejercicio_frame)
        self.frame_entrada.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(self.frame_entrada, text="Respuesta:", font=self.fuente_grande).grid(row=0, column=0, sticky=tk.W)
        self.entrada_respuesta = ttk.Entry(self.frame_entrada, width=20, font=self.fuente_grande)
        self.entrada_respuesta.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.frame_entrada.columnconfigure(1, weight=1)
        
        # Botones de acción
        botones_frame = ttk.Frame(ejercicio_frame)
        botones_frame.grid(row=3, column=0, sticky=tk.E, pady=(0, 10))
        
        self.btn_verificar = ttk.Button(botones_frame, text="Verificar", command=self.verificar_respuesta)
        self.btn_verificar.grid(row=0, column=0, padx=(0, 5))
        
        self.btn_siguiente = ttk.Button(botones_frame, text="Siguiente", command=self.siguiente_ejercicio, state=tk.DISABLED)
        self.btn_siguiente.grid(row=0, column=1)
        
        # Panel de retroalimentación
        retro_frame = ttk.LabelFrame(main_frame, text="Retroalimentación", padding="5")
        retro_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        retro_frame.columnconfigure(0, weight=1)
        retro_frame.rowconfigure(0, weight=1)
        
        self.texto_retro = tk.Text(retro_frame, wrap=tk.WORD, height=8, state=tk.DISABLED, font=self.fuente_grande)
        scrollbar = ttk.Scrollbar(retro_frame, orient=tk.VERTICAL, command=self.texto_retro.yview)
        self.texto_retro.configure(yscrollcommand=scrollbar.set)
        
        self.texto_retro.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Panel de gráficos
        graph_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="5")
        graph_frame.grid(row=1, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Actualizar interfaz inicial
        self.actualizar_interfaz()
    
    def actualizar_interfaz(self):
        # Actualizar información del estudiante
        maestria_texto = "Maestría: " + ", ".join([
            f"{vc.nombre.split()[-1]}: {vc.maestria*100:.1f}%"
            for vc in self.modelo_estudiante.vectores.values()
        ])
        self.lbl_progreso.config(text=maestria_texto)
        
        # Actualizar contador de ejercicios
        total_ejercicios = sum(vc.respuestas_totales for vc in self.modelo_estudiante.vectores.values())
        self.lbl_ejercicio.config(text=f"Ejercicios: {total_ejercicios}")
        
        # Actualizar gráfico de progreso
        self.actualizar_grafico()
    
    def actualizar_grafico(self):
        self.ax.clear()
        
        # Preparar datos para el gráfico
        vectores = list(self.modelo_estudiante.vectores.keys())
        maestrias = [vc.maestria * 100 for vc in self.modelo_estudiante.vectores.values()]
        colores = ['skyblue', 'lightgreen', 'lightcoral', 'gold', 'plum']
        
        # Crear gráfico de barras
        bars = self.ax.bar(vectores, maestrias, color=colores)
        self.ax.set_ylabel('Nivel de Maestría (%)')
        self.ax.set_title('Progreso por Competencia')
        self.ax.set_ylim(0, 100)
        
        # Añadir valores en las barras
        for bar, valor in zip(bars, maestrias):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{valor:.1f}%', ha='center', va='bottom')
        
        self.canvas.draw()
    
    def siguiente_ejercicio(self):
        # Reiniciar estado de la interfaz
        self.estado = "EJERCICIO"
        self.btn_verificar.config(state=tk.NORMAL)
        self.btn_siguiente.config(state=tk.DISABLED)
        self.entrada_respuesta.delete(0, tk.END)
        self.opcion_seleccionada.set(-1)
        self.mostrar_retroalimentacion("")
        
        # Obtener el vector de competencia más débil
        vector_objetivo = self.modelo_estudiante.vector_mas_debil()
        
        # Usar el optimizador para elegir la siguiente acción
        accion = self.optimizador.elegir_accion(vector_objetivo)
        self.modelo_estudiante.ultima_accion = accion
        
        # Determinar nivel de dificultad basado en maestría
        if vector_objetivo.maestria < 0.4:
            nivel = "bajo"
        elif vector_objetivo.maestria < 0.7:
            nivel = "medio"
        else:
            nivel = "alto"
        
        # Generar ejercicio
        self.ejercicio_actual = self.generador.generar_ejercicio(vector_objetivo, nivel)
        
        # Mostrar ejercicio
        self.mostrar_ejercicio(self.ejercicio_actual)
        
        # Iniciar temporizador
        self.tiempo_inicio_ejercicio = time.time()
        
        # Registrar evento
        self.modelo_estudiante.registrar_evento("NUEVO_EJERCICIO", {
            "ejercicio": self.ejercicio_actual,
            "vector_objetivo": vector_objetivo.nombre
        })
    
    def mostrar_ejercicio(self, ejercicio):
        # Mostrar pregunta
        self.lbl_pregunta.config(text=ejercicio["pregunta"])
        
        # Configurar interfaz según el tipo de ejercicio
        if ejercicio["tipo"] == "opcion_multiple":
            self.frame_opciones.grid()
            self.frame_entrada.grid_remove()
            
            for i, opcion in enumerate(ejercicio["opciones"]):
                self.botones_opciones[i].config(text=opcion)
                self.botones_opciones[i].grid()
        
        else:  # respuesta_numerica o explicacion
            self.frame_opciones.grid_remove()
            self.frame_entrada.grid()
            self.entrada_respuesta.focus()
    
    def verificar_respuesta(self):
        if not self.ejercicio_actual:
            return
        
        # Calcular tiempo de respuesta
        tiempo_respuesta = time.time() - self.tiempo_inicio_ejercicio
        
        # Obtener respuesta del estudiante
        if self.ejercicio_actual["tipo"] == "opcion_multiple":
            respuesta_estudiante = self.opcion_seleccionada.get()
            es_correcto = respuesta_estudiante == self.ejercicio_actual["respuesta_correcta"]
            error_code = "E-201" if not es_correcto else None
        else:
            try:
                respuesta_estudiante = int(self.entrada_respuesta.get())
                es_correcto = respuesta_estudiante == self.ejercicio_actual["respuesta_correcta"]
                
                # Detectar tipo de error
                if not es_correcto:
                    if self.ejercicio_actual["vc"] in ["VC2", "VC3"]:
                        error_code = "E-101"  # Error regla de signos
                    elif self.ejercicio_actual["vc"] == "VC4":
                        error_code = "E-103" if self.ejercicio_actual["respuesta_correcta"] is None else "E-104"
                    else:
                        error_code = "E-202"  # Error contextual
                else:
                    error_code = None
            except ValueError:
                es_correcto = False
                error_code = "E-102"  # Error aritmético
                respuesta_estudiante = "No numérica"
        
        # Actualizar modelo del estudiante
        vector_key = self.ejercicio_actual["vc"]
        self.modelo_estudiante.vectores[vector_key].actualizar(es_correcto, tiempo_respuesta, error_code)
        
        # Calcular recompensa
        if es_correcto:
            if tiempo_respuesta < self.modelo_estudiante.vectores[vector_key].tiempo_promedio / 2:
                recompensa = 15  # Muy rápido
            elif tiempo_respuesta < self.modelo_estudiante.vectores[vector_key].tiempo_promedio:
                recompensa = 10  # Rápido
            else:
                recompensa = 5   # Correcto pero lento
        else:
            recompensa = -2  # Incorrecto
        
        # Actualizar política de optimización
        self.optimizador.actualizar_politica(
            self.modelo_estudiante.vectores[vector_key],
            self.modelo_estudiante.ultima_accion,
            recompensa,
            self.modelo_estudiante.vectores[vector_key]  # Estado resultante (el mismo vector actualizado)
        )
        
        # Mostrar retroalimentación
        retroalimentacion = self.motor_retro.proporcionar_retroalimentacion(
            es_correcto, self.ejercicio_actual, respuesta_estudiante, error_code
        )
        self.mostrar_retroalimentacion(retroalimentacion)
        
        # Actualizar interfaz
        self.actualizar_interfaz()
        
        # Cambiar estado
        self.estado = "RETROALIMENTACION"
        self.btn_verificar.config(state=tk.DISABLED)
        self.btn_siguiente.config(state=tk.NORMAL)
        
        # Registrar evento
        self.modelo_estudiante.registrar_evento("RESPUESTA_VERIFICADA", {
            "ejercicio": self.ejercicio_actual["pregunta"],
            "respuesta_estudiante": respuesta_estudiante,
            "es_correcto": es_correcto,
            "tiempo_respuesta": tiempo_respuesta,
            "error_code": error_code
        })
        
        # Verificar si ha dominado todo
        if self.modelo_estudiante.ha_dominado_todo():
            self.mostrar_felicidades()
    
    def mostrar_retroalimentacion(self, mensaje):
        self.texto_retro.config(state=tk.NORMAL)
        self.texto_retro.delete(1.0, tk.END)
        self.texto_retro.insert(tk.END, mensaje)
        self.texto_retro.config(state=tk.DISABLED)
    
    def mostrar_felicidades(self):
        mensaje = "¡Felicidades! 🎉\n\nHas dominado todos los conceptos de división de números enteros.\n\n"
        mensaje += "Tu comprensión conceptual y tu habilidad para aplicar las reglas en contextos diversos "
        mensaje += "es ahora sólida y puedes enfrentarte a cualquier desafío relacionado con este tema."
        
        self.mostrar_retroalimentacion(mensaje)
        messagebox.showinfo("¡Completado!", mensaje)
        
        # Opcional: reiniciar el sistema o ofrecer nuevos desafíos
        self.btn_siguiente.config(state=tk.DISABLED)
        self.btn_verificar.config(state=tk.DISABLED)


# Punto de entrada de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionALORA(root)
    root.mainloop()