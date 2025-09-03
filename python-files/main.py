import tkinter as tk
from tkinter import messagebox
from collections import Counter

# Colores por nivel
LEVEL_COLORS = [
    "lightgray",   # Nivel 0 (sin repeticiones)
    "lightblue",   # Nivel 1
    "lightgreen",  # Nivel 2
    "yellow",      # Nivel 3
    "orange",      # Nivel 4
    "red",         # Nivel 5+
]

class LineAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Líneas de Números")
        
        self.line_number = 0
        self.lines = []         # Almacena líneas procesadas
        self.levels = {}        # Diccionario de niveles con líneas
        
        self.create_widgets()

    def create_widgets(self):
        # Título
        tk.Label(self.root, text="Matriz de Números (1-80)", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        # Matriz de números del 1 al 80 en 7 columnas
        matrix_frame = tk.Frame(self.root)
        matrix_frame.pack()
        for i in range(1, 81):
            lbl = tk.Label(matrix_frame, text=str(i), width=4, borderwidth=1, relief="solid")
            lbl.grid(row=(i - 1) // 7, column=(i - 1) % 7, padx=1, pady=1)

        # Entrada de línea
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Ingrese 20 números (1-80) separados por espacio:").grid(row=0, column=0, columnspan=2)

        self.line_entry = tk.Entry(input_frame, width=80)
        self.line_entry.grid(row=1, column=0, padx=5)

        tk.Button(input_frame, text="Procesar Línea", command=self.process_line).grid(row=1, column=1)

        # Área de niveles
        self.level_frames = []
        for level in range(6):
            frame = tk.LabelFrame(self.root, text=f"Nivel {level}", bg=LEVEL_COLORS[level], padx=5, pady=5)
            frame.pack(fill="x", padx=10, pady=2)
            self.level_frames.append(frame)

        # Botones inferiores
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)
        
        self.line_label = tk.Label(bottom_frame, text="Línea actual: 0")
        self.line_label.pack(side="left", padx=10)
        
        tk.Button(bottom_frame, text="Limpiar Todo", command=self.reset_all).pack(side="right", padx=10)

    def process_line(self):
        text = self.line_entry.get().strip()
        try:
            numbers = list(map(int, text.split()))
        except ValueError:
            messagebox.showerror("Error", "Entrada inválida. Asegúrese de ingresar solo números.")
            return

        if len(numbers) != 20:
            messagebox.showerror("Error", "Debe ingresar exactamente 20 números.")
            return

        if not all(1 <= num <= 80 for num in numbers):
            messagebox.showerror("Error", "Todos los números deben estar entre 1 y 80.")
            return

        # Verificar cuántos números están repetidos
        counts = Counter(numbers)
        repeat_count = sum(1 for count in counts.values() if count > 1)

        level = min(repeat_count, 5)  # Máximo nivel mostrado es 5

        # Guardar línea
        self.lines.append((numbers, level))

        # Mostrar línea en el frame correspondiente
        display_text = f"Línea {self.line_number + 1}: " + " ".join(map(str, numbers))
        label = tk.Label(self.level_frames[level], text=display_text, bg=LEVEL_COLORS[level])
        label.pack(anchor="w")

        # Actualizar estado
        self.line_number += 1
        self.line_label.config(text=f"Línea actual: {self.line_number}")
        self.line_entry.delete(0, tk.END)

    def reset_all(self):
        self.lines.clear()
        self.line_number = 0
        self.line_label.config(text="Línea actual: 0")
        self.line_entry.delete(0, tk.END)
        for frame in self.level_frames:
            for widget in frame.winfo_children():
                widget.destroy()

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = LineAnalyzerApp(root)
    root.mainloop()