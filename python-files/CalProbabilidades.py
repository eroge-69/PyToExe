import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math

class CalculadoraProbabilisticaCompleta:
    def __init__(self, root):
        self.root = root
        self.root.title("🧮 Calculadora Probabilística Completa")
        self.root.geometry("1024x768")
        self.root.configure(bg='#2c3e50')
        self.root.minsize(1000, 700)
        
        # Configurar estilo
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configurar estilos para la interfaz"""
        self.style = ttk.Style()
        
        # Configurar colores
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='white', font=('Arial', 9))
        self.style.configure('TButton', font=('Arial', 8), padding=4)
        self.style.configure('TEntry', font=('Arial', 9))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#3498db')
        self.style.configure('Title.TLabel', font=('Arial', 10, 'bold'), foreground='#e74c3c')
        self.style.configure('Subtitle.TLabel', font=('Arial', 9, 'bold'), foreground='#f39c12')
        
    # ========== FUNCIONES MATEMÁTICAS BÁSICAS ==========
    def factorial(self, n):
        """Calcula el factorial de un número"""
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def combinaciones(self, n, k):
        """Calcula combinaciones C(n, k)"""
        if k > n:
            return 0
        return self.factorial(n) // (self.factorial(k) * self.factorial(n - k))
    
    def funcion_error(self, x):
        """Aproximación de la función error para distribución normal"""
        sign = 1 if x >= 0 else -1
        x = abs(x)
        
        t = 1.0 / (1.0 + 0.3275911 * x)
        poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + 
                        t * (-1.453152027 + t * 1.061405429))))
        return sign * (1.0 - poly * math.exp(-x * x))
    
    def distribucion_normal_acumulada(self, x):
        """Calcula la distribución normal acumulada estándar"""
        return 0.5 * (1 + self.funcion_error(x / math.sqrt(2)))
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título principal
        title_label = ttk.Label(main_frame, 
                               text="🧮 CALCULADORA PROBABILÍSTICA COMPLETA", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear las diferentes pestañas
        self.create_introduccion_tab(notebook)
        self.create_probabilidad_basica_tab(notebook)
        self.create_distribucion_binomial_tab(notebook)
        self.create_distribucion_poisson_tab(notebook)
        self.create_distribucion_normal_tab(notebook)
        self.create_combinatoria_tab(notebook)
        self.create_estadisticas_tab(notebook)
        self.create_ejemplos_practicos_tab(notebook)
        
        # Área de resultados
        self.create_results_area(main_frame)
        
    def create_introduccion_tab(self, notebook):
        """Crear pestaña de introducción a la probabilidad"""
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="📚 Introducción")
        
        # Frame con scroll para el contenido
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        contenido = """
¿QUÉ ES LA PROBABILIDAD?

La probabilidad mide qué tan posible es que ocurra un evento. Se expresa como un número entre 0 y 1:

• 0 = Evento IMPOSIBLE (nunca ocurrirá)
• 0.5 = Evento con MISMA posibilidad de ocurrir o no
• 1 = Evento SEGURO (siempre ocurrirá)

CONCEPTOS FUNDAMENTALES:

🎯 ESPACIO MUESTRAL (S): 
   Conjunto de todos los resultados posibles
   Ejemplo: Al lanzar un dado, S = {1,2,3,4,5,6}

🎯 EVENTO (E): 
   Subconjunto del espacio muestral
   Ejemplo: "Obtener número par" = {2,4,6}

🎯 PROBABILIDAD CLÁSICA:
   P(E) = Número de casos favorables / Número de casos posibles

🎯 PROBABILIDAD FRECUENTISTA:
   P(E) = Frecuencia del evento / Total de observaciones

AXIOMAS DE LA PROBABILIDAD:

1. 0 ≤ P(E) ≤ 1 para cualquier evento E
2. P(S) = 1 (La probabilidad del espacio muestral es 1)
3. Si eventos E1, E2 son mutuamente excluyentes:
   P(E1 ∪ E2) = P(E1) + P(E2)

TIPOS DE EVENTOS:

• MUTUAMENTE EXCLUYENTES: No pueden ocurrir simultáneamente
• INDEPENDIENTES: La ocurrencia de uno no afecta al otro
• DEPENDIENTES: La ocurrencia de uno afecta la probabilidad del otro
"""
        
        text_widget = tk.Text(scrollable_frame, width=85, height=25, font=('Arial', 9), 
                             bg='#ecf0f1', fg='#2c3e50', wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert('1.0', contenido)
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_probabilidad_basica_tab(self, notebook):
        """Crear pestaña para probabilidades básicas"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔢 Básica")
        
        # Frame principal con scroll
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        ttk.Label(scrollable_frame, text="CÁLCULOS DE PROBABILIDAD BÁSICA", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(scrollable_frame, text="📖 Explicación", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """
PROBABILIDAD SIMPLE (Regla de Laplace):
P(A) = Casos favorables A / Casos totales

PROBABILIDAD COMPUESTA:
• P(A y B) = P(A) × P(B)  [Eventos independientes]
• P(A y B) = P(A) × P(B|A) [Eventos dependientes]

PROBABILIDAD DE LA UNIÓN:
• P(A o B) = P(A) + P(B) - P(A y B) [Eventos no excluyentes]
• P(A o B) = P(A) + P(B) [Eventos mutuamente excluyentes]

PROBABILIDAD CONDICIONAL:
P(A|B) = P(A y B) / P(B)  [Probabilidad de A dado que B ocurrió]
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Frame para cálculos básicos
        calc_frame = ttk.LabelFrame(scrollable_frame, text="🧮 Calculadora Básica", padding="8")
        calc_frame.pack(fill=tk.X, pady=8, padx=8)
        
        # Probabilidad Simple
        simple_frame = ttk.Frame(calc_frame)
        simple_frame.pack(fill=tk.X, pady=4)
        ttk.Label(simple_frame, text="Probabilidad Simple:", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        input_frame = ttk.Frame(simple_frame)
        input_frame.pack(fill=tk.X, pady=3)
        ttk.Label(input_frame, text="Casos favorables:").grid(row=0, column=0, padx=2)
        self.casos_favorables = ttk.Entry(input_frame, width=8)
        self.casos_favorables.grid(row=0, column=1, padx=2)
        ttk.Label(input_frame, text="Casos totales:").grid(row=0, column=2, padx=2)
        self.casos_totales = ttk.Entry(input_frame, width=8)
        self.casos_totales.grid(row=0, column=3, padx=2)
        ttk.Button(input_frame, text="Calcular P(A)", 
                  command=self.calcular_probabilidad_simple, width=12).grid(row=0, column=4, padx=5)
        
        # Probabilidad Compuesta
        comp_frame = ttk.Frame(calc_frame)
        comp_frame.pack(fill=tk.X, pady=4)
        ttk.Label(comp_frame, text="Probabilidad Compuesta:", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        input_comp = ttk.Frame(comp_frame)
        input_comp.pack(fill=tk.X, pady=3)
        ttk.Label(input_comp, text="P(A):").grid(row=0, column=0, padx=2)
        self.p_a_comp = ttk.Entry(input_comp, width=8)
        self.p_a_comp.grid(row=0, column=1, padx=2)
        ttk.Label(input_comp, text="P(B):").grid(row=0, column=2, padx=2)
        self.p_b_comp = ttk.Entry(input_comp, width=8)
        self.p_b_comp.grid(row=0, column=3, padx=2)
        ttk.Button(input_comp, text="P(A y B) Independientes", 
                  command=self.calcular_probabilidad_compuesta_ind, width=18).grid(row=0, column=4, padx=2)
        ttk.Button(input_comp, text="P(A y B) Dependientes", 
                  command=self.calcular_probabilidad_compuesta_dep, width=18).grid(row=0, column=5, padx=2)
        
        # Probabilidad de Unión
        union_frame = ttk.Frame(calc_frame)
        union_frame.pack(fill=tk.X, pady=4)
        ttk.Label(union_frame, text="Probabilidad de la Unión:", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        input_union = ttk.Frame(union_frame)
        input_union.pack(fill=tk.X, pady=3)
        ttk.Label(input_union, text="P(A):").grid(row=0, column=0, padx=2)
        self.p_a_union = ttk.Entry(input_union, width=8)
        self.p_a_union.grid(row=0, column=1, padx=2)
        ttk.Label(input_union, text="P(B):").grid(row=0, column=2, padx=2)
        self.p_b_union = ttk.Entry(input_union, width=8)
        self.p_b_union.grid(row=0, column=3, padx=2)
        ttk.Label(input_union, text="P(A y B):").grid(row=0, column=4, padx=2)
        self.p_ayb_union = ttk.Entry(input_union, width=8)
        self.p_ayb_union.grid(row=0, column=5, padx=2)
        ttk.Button(input_union, text="Calcular P(A o B)", 
                  command=self.calcular_probabilidad_union, width=14).grid(row=0, column=6, padx=5)
        
        # Probabilidad Condicional
        cond_frame = ttk.Frame(calc_frame)
        cond_frame.pack(fill=tk.X, pady=4)
        ttk.Label(cond_frame, text="Probabilidad Condicional:", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        input_cond = ttk.Frame(cond_frame)
        input_cond.pack(fill=tk.X, pady=3)
        ttk.Label(input_cond, text="P(A y B):").grid(row=0, column=0, padx=2)
        self.p_ayb_cond = ttk.Entry(input_cond, width=8)
        self.p_ayb_cond.grid(row=0, column=1, padx=2)
        ttk.Label(input_cond, text="P(B):").grid(row=0, column=2, padx=2)
        self.p_b_cond = ttk.Entry(input_cond, width=8)
        self.p_b_cond.grid(row=0, column=3, padx=2)
        ttk.Button(input_cond, text="Calcular P(A|B)", 
                  command=self.calcular_probabilidad_condicional, width=12).grid(row=0, column=4, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_distribucion_binomial_tab(self, notebook):
        """Crear pestaña para distribución binomial"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📊 Binomial")
        
        ttk.Label(frame, text="DISTRIBUCIÓN BINOMIAL", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(frame, text="📖 ¿Qué es la Distribución Binomial?", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """CARACTERÍSTICAS:
• Número FIJO de ensayos (n)
• Cada ensayo es INDEPENDIENTE
• Solo DOS resultados posibles: Éxito o Fracaso
• Probabilidad de éxito CONSTANTE (p)

FÓRMULA: P(X = k) = C(n,k) × pᵏ × (1-p)⁽ⁿ⁻ᵏ⁾

EJEMPLOS:
• Lanzar moneda 10 veces, probabilidad de 5 caras
• 8 de cada 10 pacientes se recuperan, prob. de que 6 se recuperen
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Frame para parámetros
        param_frame = ttk.Frame(frame)
        param_frame.pack(pady=10)
        
        # Parámetros en filas más compactas
        ttk.Label(param_frame, text="Número de ensayos (n):").grid(row=0, column=0, sticky=tk.W, pady=3, padx=3)
        self.n_binomial = ttk.Entry(param_frame, width=10)
        self.n_binomial.grid(row=0, column=1, pady=3, padx=3)
        
        ttk.Label(param_frame, text="Probabilidad de éxito (p):").grid(row=1, column=0, sticky=tk.W, pady=3, padx=3)
        self.p_binomial = ttk.Entry(param_frame, width=10)
        self.p_binomial.grid(row=1, column=1, pady=3, padx=3)
        
        ttk.Label(param_frame, text="Número de éxitos (k):").grid(row=2, column=0, sticky=tk.W, pady=3, padx=3)
        self.k_binomial = ttk.Entry(param_frame, width=10)
        self.k_binomial.grid(row=2, column=1, pady=3, padx=3)
        
        # Frame para botones - organizados en grid
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        # Botones de cálculo en 2x2 grid
        ttk.Button(button_frame, text="P(X = k) - Exactamente k", 
                  command=self.calcular_binomial_igual, width=18).grid(row=0, column=0, pady=3, padx=3)
        ttk.Button(button_frame, text="P(X ≤ k) - Máximo k", 
                  command=self.calcular_binomial_acumulada, width=18).grid(row=0, column=1, pady=3, padx=3)
        ttk.Button(button_frame, text="P(X ≥ k) - Mínimo k", 
                  command=self.calcular_binomial_minimo, width=18).grid(row=1, column=0, pady=3, padx=3)
        ttk.Button(button_frame, text="P(a ≤ X ≤ b) - Entre a y b", 
                  command=self.calcular_binomial_intervalo, width=18).grid(row=1, column=1, pady=3, padx=3)

    def create_distribucion_poisson_tab(self, notebook):
        """Crear pestaña para distribución de Poisson"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📈 Poisson")
        
        ttk.Label(frame, text="DISTRIBUCIÓN DE POISSON", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(frame, text="📖 ¿Qué es la Distribución de Poisson?", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """CARACTERÍSTICAS:
• Cuenta número de eventos en intervalo de tiempo/espacio
• Eventos INDEPENDIENTES entre sí
• Tasa promedio CONSTANTE (λ)

FÓRMULA: P(X = k) = (e⁻λ × λᵏ) / k!

EJEMPLOS:
• Número de clientes por hora
• Número de accidentes por día
• Llamadas a call center por minuto
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Frame para parámetros
        param_frame = ttk.Frame(frame)
        param_frame.pack(pady=10)
        
        # Parámetros
        ttk.Label(param_frame, text="Tasa promedio (λ):").grid(row=0, column=0, sticky=tk.W, pady=4, padx=3)
        self.lambda_poisson = ttk.Entry(param_frame, width=10)
        self.lambda_poisson.grid(row=0, column=1, pady=4, padx=3)
        
        ttk.Label(param_frame, text="Número de eventos (k):").grid(row=1, column=0, sticky=tk.W, pady=4, padx=3)
        self.k_poisson = ttk.Entry(param_frame, width=10)
        self.k_poisson.grid(row=1, column=1, pady=4, padx=3)
        
        # Frame para botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        # Botones de cálculo
        ttk.Button(button_frame, text="P(X = k) - Exactamente k", 
                  command=self.calcular_poisson_igual, width=18).grid(row=0, column=0, pady=3, padx=3)
        ttk.Button(button_frame, text="P(X ≤ k) - Máximo k", 
                  command=self.calcular_poisson_acumulada, width=18).grid(row=0, column=1, pady=3, padx=3)
        ttk.Button(button_frame, text="P(X ≥ k) - Mínimo k", 
                  command=self.calcular_poisson_minimo, width=18).grid(row=1, column=0, pady=3, padx=3)

    def create_distribucion_normal_tab(self, notebook):
        """Crear pestaña para distribución normal"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📉 Normal")
        
        ttk.Label(frame, text="DISTRIBUCIÓN NORMAL", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(frame, text="📖 ¿Qué es la Distribución Normal?", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """CARACTERÍSTICAS:
• Forma de CAMPANA simétrica
• Definida por media (μ) y desviación estándar (σ)
• Regla 68-95-99.7:
  - 68% datos dentro de μ ± σ
  - 95% datos dentro de μ ± 2σ
  - 99.7% datos dentro de μ ± 3σ

FÓRMULA: f(x) = (1/(σ√(2π))) × e⁻⁽⁽ˣ⁻μ⁾²/(2σ²)⁾
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Frame para parámetros
        param_frame = ttk.Frame(frame)
        param_frame.pack(pady=10)
        
        # Parámetros
        ttk.Label(param_frame, text="Media (μ):").grid(row=0, column=0, sticky=tk.W, pady=3, padx=3)
        self.mu_normal = ttk.Entry(param_frame, width=10)
        self.mu_normal.insert(0, "0")
        self.mu_normal.grid(row=0, column=1, pady=3, padx=3)
        
        ttk.Label(param_frame, text="Desviación estándar (σ):").grid(row=1, column=0, sticky=tk.W, pady=3, padx=3)
        self.sigma_normal = ttk.Entry(param_frame, width=10)
        self.sigma_normal.insert(0, "1")
        self.sigma_normal.grid(row=1, column=1, pady=3, padx=3)
        
        ttk.Label(param_frame, text="Valor x:").grid(row=2, column=0, sticky=tk.W, pady=3, padx=3)
        self.x_normal = ttk.Entry(param_frame, width=10)
        self.x_normal.grid(row=2, column=1, pady=3, padx=3)
        
        # Frame para botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        # Botones de cálculo
        ttk.Button(button_frame, text="P(X ≤ x) - Acumulada", 
                  command=self.calcular_normal_acumulada, width=16).grid(row=0, column=0, pady=3, padx=3)
        ttk.Button(button_frame, text="P(X ≥ x) - Complementaria", 
                  command=self.calcular_normal_minimo, width=16).grid(row=0, column=1, pady=3, padx=3)
        ttk.Button(button_frame, text="P(a ≤ X ≤ b) - Intervalo", 
                  command=self.calcular_normal_intervalo, width=16).grid(row=1, column=0, pady=3, padx=3)

    def create_combinatoria_tab(self, notebook):
        """Crear pestaña para cálculos combinatorios"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔀 Combinatoria")
        
        ttk.Label(frame, text="ANÁLISIS COMBINATORIO", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(frame, text="📖 ¿Qué es el Análisis Combinatorio?", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """PERMUTACIONES (Orden SÍ importa, TODOS elementos):
P(n) = n! = n × (n-1) × ... × 2 × 1

VARIACIONES (Orden SÍ importa, NO todos):
V(n,k) = n! / (n-k)!

COMBINACIONES (Orden NO importa):
C(n,k) = n! / (k! × (n-k)!)

EJEMPLOS:
• Permutaciones: Ordenar 3 libros = 3! = 6 formas
• Variaciones: Elegir presidente/vice de 5 = V(5,2) = 20
• Combinaciones: Comité de 3 de 8 = C(8,3) = 56
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Combinaciones
        comb_frame = ttk.LabelFrame(frame, text="COMBINACIONES C(n,k)", padding="6")
        comb_frame.pack(fill=tk.X, pady=6, padx=8)
        
        comb_input = ttk.Frame(comb_frame)
        comb_input.pack(pady=3)
        ttk.Label(comb_input, text="n:").grid(row=0, column=0, padx=2)
        self.n_comb = ttk.Entry(comb_input, width=8)
        self.n_comb.grid(row=0, column=1, padx=2)
        ttk.Label(comb_input, text="k:").grid(row=0, column=2, padx=2)
        self.k_comb = ttk.Entry(comb_input, width=8)
        self.k_comb.grid(row=0, column=3, padx=2)
        ttk.Button(comb_input, text="Calcular", 
                  command=self.calcular_combinaciones, width=10).grid(row=0, column=4, padx=5)
        
        # Permutaciones
        perm_frame = ttk.LabelFrame(frame, text="PERMUTACIONES P(n)", padding="6")
        perm_frame.pack(fill=tk.X, pady=6, padx=8)
        
        perm_input = ttk.Frame(perm_frame)
        perm_input.pack(pady=3)
        ttk.Label(perm_input, text="n:").grid(row=0, column=0, padx=2)
        self.n_perm = ttk.Entry(perm_input, width=8)
        self.n_perm.grid(row=0, column=1, padx=2)
        ttk.Button(perm_input, text="Calcular", 
                  command=self.calcular_permutaciones, width=10).grid(row=0, column=2, padx=5)
        
        # Variaciones
        var_frame = ttk.LabelFrame(frame, text="VARIACIONES V(n,k)", padding="6")
        var_frame.pack(fill=tk.X, pady=6, padx=8)
        
        var_input = ttk.Frame(var_frame)
        var_input.pack(pady=3)
        ttk.Label(var_input, text="n:").grid(row=0, column=0, padx=2)
        self.n_var = ttk.Entry(var_input, width=8)
        self.n_var.grid(row=0, column=1, padx=2)
        ttk.Label(var_input, text="k:").grid(row=0, column=2, padx=2)
        self.k_var = ttk.Entry(var_input, width=8)
        self.k_var.grid(row=0, column=3, padx=2)
        ttk.Button(var_input, text="Calcular", 
                  command=self.calcular_variaciones, width=10).grid(row=0, column=4, padx=5)

    def create_estadisticas_tab(self, notebook):
        """Crear pestaña para estadísticas básicas"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📐 Estadísticas")
        
        ttk.Label(frame, text="ESTADÍSTICAS DESCRIPTIVAS", style='Title.TLabel').pack(pady=8)
        
        # Frame para explicación
        expl_frame = ttk.LabelFrame(frame, text="📖 Medidas Estadísticas Básicas", padding="8")
        expl_frame.pack(fill=tk.X, pady=8, padx=8)
        
        expl_text = """MEDIDAS DE TENDENCIA CENTRAL:
📊 MEDIA: μ = (Σxᵢ) / n
📊 MEDIANA: Valor central
📊 MODA: Valor más frecuente

MEDIDAS DE DISPERSIÓN:
📊 VARIANZA: σ² = Σ(xᵢ - μ)² / n
📊 DESVIACIÓN ESTÁNDAR: σ = √σ²
📊 RANGO: Máximo - Mínimo
"""
        ttk.Label(expl_frame, text=expl_text, justify=tk.LEFT, font=('Arial', 8)).pack()
        
        # Entrada de datos
        data_frame = ttk.LabelFrame(frame, text="📝 Ingresar datos (separados por comas)", padding="6")
        data_frame.pack(fill=tk.X, pady=8, padx=8)
        
        self.datos_entrada = ttk.Entry(data_frame, width=50)
        self.datos_entrada.pack(pady=3, padx=5)
        self.datos_entrada.insert(0, "1,2,3,4,5,6,7,8,9,10")
        
        # Botones de estadísticas
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(pady=10)
        
        ttk.Button(stats_frame, text="Media", 
                  command=self.calcular_media, width=12).grid(row=0, column=0, pady=2, padx=2)
        ttk.Button(stats_frame, text="Mediana", 
                  command=self.calcular_mediana, width=12).grid(row=0, column=1, pady=2, padx=2)
        ttk.Button(stats_frame, text="Varianza", 
                  command=self.calcular_varianza, width=12).grid(row=1, column=0, pady=2, padx=2)
        ttk.Button(stats_frame, text="Desviación", 
                  command=self.calcular_desviacion, width=12).grid(row=1, column=1, pady=2, padx=2)
        ttk.Button(stats_frame, text="Rango", 
                  command=self.calcular_rango, width=12).grid(row=2, column=0, pady=2, padx=2)
        ttk.Button(stats_frame, text="Calcular Todo", 
                  command=self.calcular_todo_estadisticas, width=12).grid(row=2, column=1, pady=2, padx=2)

    def create_ejemplos_practicos_tab(self, notebook):
        """Crear pestaña con ejemplos prácticos"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🎯 Ejemplos")
        
        # Frame con scroll
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        contenido = """
EJEMPLOS PRÁCTICOS DE APLICACIÓN

🎲 EJEMPLO 1: PROBABILIDAD SIMPLE
Problema: ¿Probabilidad de sacar un as de una baraja de 52 cartas?
Solución: 
• Casos favorables: 4 ases
• Casos totales: 52 cartas
• P(As) = 4/52 = 1/13 ≈ 0.0769 (7.69%)

🎲 EJEMPLO 2: DISTRIBUCIÓN BINOMIAL
Problema: Lanzar moneda 10 veces, ¿probabilidad de 6 caras?
Parámetros:
• n = 10 ensayos
• p = 0.5 (probabilidad de cara)
• k = 6 éxitos
Fórmula: P(X=6) = C(10,6) × 0.5⁶ × 0.5⁴ = 210 × 0.015625 × 0.0625 ≈ 0.205

🎲 EJEMPLO 3: DISTRIBUCIÓN POISSON
Problema: En un banco llegan 3 clientes por hora en promedio,
¿probabilidad de que lleguen exactamente 2 clientes en una hora?
Parámetros:
• λ = 3 clientes/hora
• k = 2 clientes
Fórmula: P(X=2) = (e⁻³ × 3²) / 2! ≈ (0.0498 × 9) / 2 ≈ 0.224

🎲 EJEMPLO 4: DISTRIBUCIÓN NORMAL
Problema: CI con media 100 y desviación 15,
¿probabilidad de que una persona tenga CI ≤ 115?
Solución:
• z = (115 - 100) / 15 = 1
• P(X ≤ 115) = P(Z ≤ 1) ≈ 0.8413 (84.13%)

INTERPRETACIÓN DE RESULTADOS:
• 0.0 - 0.2: Muy improbable
• 0.2 - 0.4: Poco probable  
• 0.4 - 0.6: Probabilidad media
• 0.6 - 0.8: Bastante probable
• 0.8 - 1.0: Muy probable
"""
        
        text_widget = tk.Text(scrollable_frame, width=85, height=25, font=('Arial', 9), 
                             bg='#ecf0f1', fg='#2c3e50', wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert('1.0', contenido)
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_results_area(self, parent):
        """Crear área de resultados"""
        results_frame = ttk.LabelFrame(parent, text="📋 RESULTADOS Y EXPLICACIONES", padding="6")
        results_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # Área de resultados con altura fija
        self.result_text = scrolledtext.ScrolledText(results_frame, width=90, height=12, 
                                                   font=('Consolas', 8), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones de control
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill=tk.X, pady=3)
        
        ttk.Button(control_frame, text="🧹 Limpiar Resultados", 
                  command=self.limpiar_resultados, width=15).pack(side=tk.LEFT, padx=5)
        
    def agregar_resultado(self, texto):
        """Agregar texto al área de resultados"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"\n🕒 [{timestamp}]\n{texto}\n" + "═" * 70 + "\n")
        self.result_text.see(tk.END)
        
    def limpiar_resultados(self):
        """Limpiar el área de resultados"""
        self.result_text.delete('1.0', tk.END)

    # ========== FUNCIONES DE VALIDACIÓN ==========
    def validar_numero(self, valor, nombre, mayor_igual_cero=True):
        """Validar que un valor sea numérico"""
        try:
            num = float(valor)
            if mayor_igual_cero and num < 0:
                raise ValueError(f"{nombre} debe ser mayor o igual a 0")
            return num
        except ValueError:
            messagebox.showerror("Error", f"❌ {nombre} debe ser un número válido")
            return None
            
    def validar_entero(self, valor, nombre, mayor_igual_cero=True):
        """Validar que un valor sea entero"""
        try:
            num = int(valor)
            if mayor_igual_cero and num < 0:
                raise ValueError(f"{nombre} debe ser mayor o igual a 0")
            return num
        except ValueError:
            messagebox.showerror("Error", f"❌ {nombre} debe ser un número entero válido")
            return None

    # ========== FUNCIONES DE CÁLCULO (Implementaciones básicas) ==========
    
    def calcular_probabilidad_simple(self):
        favorables = self.validar_entero(self.casos_favorables.get(), "Casos favorables")
        totales = self.validar_entero(self.casos_totales.get(), "Casos totales")
        
        if favorables is None or totales is None:
            return
            
        if favorables > totales:
            messagebox.showerror("Error", "❌ Los casos favorables no pueden ser más que los totales")
            return
            
        probabilidad = favorables / totales
        
        resultado = "🎯 PROBABILIDAD SIMPLE\n"
        resultado += f"P(A) = {favorables} / {totales} = {probabilidad:.6f}\n"
        resultado += f"Porcentaje: {probabilidad*100:.4f}%"
        
        self.agregar_resultado(resultado)

    def calcular_probabilidad_compuesta_ind(self):
        p_a = self.validar_numero(self.p_a_comp.get(), "P(A)")
        p_b = self.validar_numero(self.p_b_comp.get(), "P(B)")
        
        if p_a is None or p_b is None:
            return
            
        probabilidad = p_a * p_b
        
        resultado = "🎯 PROBABILIDAD COMPUESTA - INDEPENDIENTES\n"
        resultado += f"P(A y B) = {p_a:.4f} × {p_b:.4f} = {probabilidad:.6f}\n"
        resultado += f"Porcentaje: {probabilidad*100:.4f}%"
        
        self.agregar_resultado(resultado)

    def calcular_probabilidad_compuesta_dep(self):
        p_a = self.validar_numero(self.p_a_comp.get(), "P(A)")
        p_b = self.validar_numero(self.p_b_comp.get(), "P(B)")
        
        if p_a is None or p_b is None:
            return
            
        p_b_dado_a = tk.simpledialog.askfloat("Probabilidad Condicional", "Ingrese P(B|A):")
        if p_b_dado_a is None:
            return
            
        probabilidad = p_a * p_b_dado_a
        
        resultado = "🎯 PROBABILIDAD COMPUESTA - DEPENDIENTES\n"
        resultado += f"P(A y B) = {p_a:.4f} × {p_b_dado_a:.4f} = {probabilidad:.6f}\n"
        resultado += f"Porcentaje: {probabilidad*100:.4f}%"
        
        self.agregar_resultado(resultado)

    def calcular_probabilidad_union(self):
        p_a = self.validar_numero(self.p_a_union.get(), "P(A)")
        p_b = self.validar_numero(self.p_b_union.get(), "P(B)")
        p_ayb = self.validar_numero(self.p_ayb_union.get(), "P(A y B)")
        
        if p_a is None or p_b is None or p_ayb is None:
            return
            
        probabilidad = p_a + p_b - p_ayb
        
        resultado = "🎯 PROBABILIDAD DE LA UNIÓN\n"
        resultado += f"P(A o B) = {p_a:.4f} + {p_b:.4f} - {p_ayb:.4f} = {probabilidad:.6f}\n"
        resultado += f"Porcentaje: {probabilidad*100:.4f}%"
        
        self.agregar_resultado(resultado)

    def calcular_probabilidad_condicional(self):
        p_ayb = self.validar_numero(self.p_ayb_cond.get(), "P(A y B)")
        p_b = self.validar_numero(self.p_b_cond.get(), "P(B)")
        
        if p_ayb is None or p_b is None:
            return
            
        if p_b == 0:
            messagebox.showerror("Error", "❌ P(B) no puede ser cero")
            return
            
        probabilidad = p_ayb / p_b
        
        resultado = "🎯 PROBABILIDAD CONDICIONAL\n"
        resultado += f"P(A|B) = {p_ayb:.4f} / {p_b:.4f} = {probabilidad:.6f}\n"
        resultado += f"Porcentaje: {probabilidad*100:.4f}%"
        
        self.agregar_resultado(resultado)

    def calcular_binomial_igual(self):
        n = self.validar_entero(self.n_binomial.get(), "n")
        p = self.validar_numero(self.p_binomial.get(), "p")
        k = self.validar_entero(self.k_binomial.get(), "k")
        
        if n is None or p is None or k is None:
            return
            
        probabilidad = self.combinaciones(n, k) * (p ** k) * ((1 - p) ** (n - k))
        resultado = f"📊 BINOMIAL - P(X = {k})\n"
        resultado += f"Resultado: {probabilidad:.8f} ({probabilidad*100:.4f}%)"
        
        self.agregar_resultado(resultado)

    def calcular_binomial_acumulada(self):
        n = self.validar_entero(self.n_binomial.get(), "n")
        p = self.validar_numero(self.p_binomial.get(), "p")
        k = self.validar_entero(self.k_binomial.get(), "k")
        
        if n is None or p is None or k is None:
            return
            
        probabilidad = 0
        for i in range(k + 1):
            probabilidad += self.combinaciones(n, i) * (p ** i) * ((1 - p) ** (n - i))
            
        resultado = f"📊 BINOMIAL - P(X ≤ {k})\n"
        resultado += f"Resultado: {probabilidad:.8f} ({probabilidad*100:.4f}%)"
        
        self.agregar_resultado(resultado)

    # ... (implementar las demás funciones de cálculo de manera similar)

    def obtener_datos(self):
        """Obtener y validar datos de entrada"""
        datos_str = self.datos_entrada.get()
        try:
            datos = [float(x.strip()) for x in datos_str.split(',')]
            return datos
        except ValueError:
            messagebox.showerror("Error", "❌ Los datos deben ser números separados por comas")
            return None

    def calcular_media(self):
        datos = self.obtener_datos()
        if datos is None:
            return
            
        media = sum(datos) / len(datos)
        resultado = f"📊 MEDIA\nResultado: {media:.4f}"
        self.agregar_resultado(resultado)

    def calcular_mediana(self):
        datos = self.obtener_datos()
        if datos is None:
            return
            
        datos_ordenados = sorted(datos)
        n = len(datos_ordenados)
        if n % 2 == 0:
            mediana = (datos_ordenados[n//2 - 1] + datos_ordenados[n//2]) / 2
        else:
            mediana = datos_ordenados[n//2]
            
        resultado = f"📊 MEDIANA\nResultado: {mediana:.4f}"
        self.agregar_resultado(resultado)

    def calcular_todo_estadisticas(self):
        datos = self.obtener_datos()
        if datos is None:
            return
            
        media = sum(datos) / len(datos)
        datos_ordenados = sorted(datos)
        n = len(datos_ordenados)
        
        if n % 2 == 0:
            mediana = (datos_ordenados[n//2 - 1] + datos_ordenados[n//2]) / 2
        else:
            mediana = datos_ordenados[n//2]
            
        varianza = sum((x - media) ** 2 for x in datos) / len(datos)
        desviacion = math.sqrt(varianza)
        rango = max(datos) - min(datos)
        
        resultado = f"📊 ESTADÍSTICAS COMPLETAS\n"
        resultado += f"Media: {media:.4f}\n"
        resultado += f"Mediana: {mediana:.4f}\n"
        resultado += f"Varianza: {varianza:.4f}\n"
        resultado += f"Desviación: {desviacion:.4f}\n"
        resultado += f"Rango: {rango:.4f}"
        
        self.agregar_resultado(resultado)

    # Placeholders para funciones no implementadas completamente
    def calcular_binomial_minimo(self): pass
    def calcular_binomial_intervalo(self): pass
    def calcular_poisson_igual(self): pass
    def calcular_poisson_acumulada(self): pass
    def calcular_poisson_minimo(self): pass
    def calcular_normal_acumulada(self): pass
    def calcular_normal_minimo(self): pass
    def calcular_normal_intervalo(self): pass
    def calcular_combinaciones(self): pass
    def calcular_permutaciones(self): pass
    def calcular_variaciones(self): pass
    def calcular_varianza(self): pass
    def calcular_desviacion(self): pass
    def calcular_rango(self): pass

def main():
    root = tk.Tk()
    app = CalculadoraProbabilisticaCompleta(root)
    root.mainloop()

if __name__ == "__main__":
    main()