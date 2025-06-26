import tkinter as tk
from tkinter import ttk, messagebox

class SaludApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Evaluador de Salud Corporal")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        
        # Estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        
        self.create_widgets()
    
    def create_widgets(self):
        # Marco principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Evaluación de Salud Corporal",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Peso
        peso_frame = ttk.Frame(main_frame)
        peso_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(peso_frame, text="Peso (kg):").pack(side=tk.LEFT)
        self.peso_slider = ttk.Scale(
            peso_frame, 
            from_=30, 
            to=150, 
            orient=tk.HORIZONTAL,
            command=self.update_peso_label
        )
        self.peso_slider.set(70)
        self.peso_slider.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        self.peso_label = ttk.Label(peso_frame, text="70.0 kg")
        self.peso_label.pack(side=tk.RIGHT, padx=5)
        
        # Altura
        altura_frame = ttk.Frame(main_frame)
        altura_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(altura_frame, text="Altura (cm):").pack(side=tk.LEFT)
        self.altura_slider = ttk.Scale(
            altura_frame, 
            from_=120, 
            to=220, 
            orient=tk.HORIZONTAL,
            command=self.update_altura_label
        )
        self.altura_slider.set(170)
        self.altura_slider.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        self.altura_label = ttk.Label(altura_frame, text="170 cm")
        self.altura_label.pack(side=tk.RIGHT, padx=5)
        
        # Edad
        edad_frame = ttk.Frame(main_frame)
        edad_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(edad_frame, text="Edad:").pack(side=tk.LEFT)
        self.edad_slider = ttk.Scale(
            edad_frame, 
            from_=10, 
            to=100, 
            orient=tk.HORIZONTAL,
            command=self.update_edad_label
        )
        self.edad_slider.set(30)
        self.edad_slider.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        self.edad_label = ttk.Label(edad_frame, text="30 años")
        self.edad_label.pack(side=tk.RIGHT, padx=5)
        
        # Botón de evaluación
        evaluar_btn = ttk.Button(
            main_frame, 
            text="Evaluar mi salud", 
            command=self.evaluar_salud
        )
        evaluar_btn.pack(pady=20)
        
        # Resultados
        self.resultado_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, padding=10)
        self.resultado_frame.pack(fill=tk.BOTH, expand=True)
        
        self.resultado_text = tk.Text(
            self.resultado_frame, 
            wrap=tk.WORD, 
            height=8,
            state=tk.DISABLED,
            font=('Arial', 9)
        )
        self.resultado_text.pack(fill=tk.BOTH, expand=True)
    
    def update_peso_label(self, event=None):
        peso = round(self.peso_slider.get(), 1)
        self.peso_label.config(text=f"{peso} kg")
    
    def update_altura_label(self, event=None):
        altura = round(self.altura_slider.get())
        self.altura_label.config(text=f"{altura} cm")
    
    def update_edad_label(self, event=None):
        edad = round(self.edad_slider.get())
        self.edad_label.config(text=f"{edad} años")
    
    def evaluar_salud(self):
        peso = round(self.peso_slider.get(), 1)
        altura = round(self.altura_slider.get()) / 100  # Convertir a metros
        edad = round(self.edad_slider.get())
        
        # Calcular IMC
        imc = peso / (altura ** 2)
        
        # Evaluar condición
        condicion, color = self.evaluar_imc(imc, edad)
        
        # Generar recomendaciones
        recomendaciones = self.generar_recomendaciones(imc, edad)
        
        # Mostrar resultados
        self.mostrar_resultados(imc, condicion, color, recomendaciones)
    
    def evaluar_imc(self, imc, edad):
        if edad < 18:
            # Tablas de IMC para niños/adolescentes son diferentes
            # Usamos una simplificación para este ejemplo
            if imc < 18.5:
                return "Bajo peso para tu edad", "red"
            elif 18.5 <= imc < 24.9:
                return "Peso normal para tu edad", "green"
            elif 25 <= imc < 29.9:
                return "Sobrepeso para tu edad", "orange"
            else:
                return "Obesidad para tu edad", "red"
        else:
            # Adultos
            if imc < 18.5:
                return "Bajo peso", "red"
            elif 18.5 <= imc < 24.9:
                return "Peso normal", "green"
            elif 25 <= imc < 29.9:
                return "Sobrepeso", "orange"
            else:
                return "Obesidad", "red"
    
    def generar_recomendaciones(self, imc, edad):
        recomendaciones = []
        
        if imc < 18.5:
            recomendaciones.append("- Aumenta tu ingesta calórica con alimentos nutritivos")
            recomendaciones.append("- Consume proteínas magras (pollo, pescado, legumbres)")
            recomendaciones.append("- Realiza ejercicios de fuerza para ganar masa muscular")
            recomendaciones.append("- Come 5-6 comidas pequeñas al día en lugar de 3 grandes")
            if edad < 18:
                recomendaciones.append("- Consulta a un pediatra o nutricionista infantil")
        elif 18.5 <= imc < 24.9:
            recomendaciones.append("- Mantén tus hábitos saludables actuales")
            recomendaciones.append("- Realiza ejercicio regular (150 min/semana)")
            recomendaciones.append("- Consume una dieta balanceada con frutas y verduras")
            recomendaciones.append("- Controla tu peso periódicamente")
        elif 25 <= imc < 29.9:
            recomendaciones.append("- Reduce el consumo de alimentos procesados y azúcares")
            recomendaciones.append("- Aumenta tu actividad física diaria")
            recomendaciones.append("- Controla las porciones de tus comidas")
            recomendaciones.append("- Incorpora más fibra en tu dieta")
            if edad > 40:
                recomendaciones.append("- Consulta a un médico para chequeo cardiovascular")
        else:
            recomendaciones.append("- Consulta a un médico o nutricionista para un plan personalizado")
            recomendaciones.append("- Reduce gradualmente la ingesta calórica")
            recomendaciones.append("- Empieza con ejercicio de bajo impacto (caminar, nadar)")
            recomendaciones.append("- Evita dietas extremas, busca cambios sostenibles")
            if edad > 50:
                recomendaciones.append("- Pide un examen de glucosa y presión arterial")
        
        return recomendaciones
    
    def mostrar_resultados(self, imc, condicion, color, recomendaciones):
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        
        # Mostrar IMC y condición
        self.resultado_text.insert(tk.END, f"Tu IMC es: {imc:.1f}\n", "center")
        self.resultado_text.tag_configure("center", justify='center')
        self.resultado_text.insert(tk.END, f"Condición: ", "bold")
        self.resultado_text.insert(tk.END, f"{condicion}\n\n", ("bold", color))
        self.resultado_text.tag_configure("bold", font=('Arial', 9, 'bold'))
        self.resultado_text.tag_configure(color, foreground=color)
        
        # Mostrar recomendaciones
        self.resultado_text.insert(tk.END, "Recomendaciones:\n", "bold")
        for rec in recomendaciones:
            self.resultado_text.insert(tk.END, f"{rec}\n")
        
        self.resultado_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SaludApp(root)
    root.mainloop()