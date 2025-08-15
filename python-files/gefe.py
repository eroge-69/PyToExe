import tkinter as tk
from tkinter import ttk, messagebox

ventana = tk.Tk()
ventana.title("Escala de Notas")
ventana.geometry("600x500")

# Contenedor principal
main_frame = tk.Frame(ventana, padx=10, pady=10)
main_frame.pack(fill='both', expand=True)

# Frame de entrada de datos
input_frame = tk.LabelFrame(main_frame, text="Parámetros", padx=5, pady=5)
input_frame.pack(fill='x', pady=5)

# Campos de entrada
tk.Label(input_frame, text="Nota Mínima:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
cuadronotaminima = tk.Entry(input_frame, width=10)
cuadronotaminima.grid(row=0, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Nota Máxima:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
cuadronotamaxima = tk.Entry(input_frame, width=10)
cuadronotamaxima.grid(row=1, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Puntaje Máximo:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
cuadropuntaje = tk.Entry(input_frame, width=10)
cuadropuntaje.grid(row=2, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Exigencia (%):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
cuadroexigencia = tk.Entry(input_frame, width=10)
cuadroexigencia.grid(row=3, column=1, padx=5, pady=2)

# Botón de generación
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=5)
generar_btn = tk.Button(button_frame, text="Generar Tabla", command=lambda: generar_tabla())
generar_btn.pack()

# Frame para la tabla de resultados
table_frame = tk.LabelFrame(main_frame, text="Resultados", padx=5, pady=5)
table_frame.pack(fill='both', expand=True, pady=5)

# Text widget para mostrar resultados como en escaladenotas.cl
resultados_text = tk.Text(table_frame, wrap='word', height=15, font=('Courier New', 10))
scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=resultados_text.yview)
resultados_text.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')
resultados_text.pack(side='left', fill='both', expand=True)

def generar_tabla():
    try:
        # Limpiar resultados existentes
        resultados_text.config(state='normal')
        resultados_text.delete(1.0, tk.END)
        
        # Obtener valores
        nota_min = float(cuadronotaminima.get())
        nota_max = float(cuadronotamaxima.get())
        puntaje_max = float(cuadropuntaje.get())
        exigencia = float(cuadroexigencia.get())
        
        # Validaciones
        if not (1.0 <= nota_min < nota_max <= 7.0):
            messagebox.showerror("Error", "Notas deben ser: 1.0 ≤ Mínima < Máxima ≤ 7.0")
            return
            
        if not (0 < exigencia < 100):
            messagebox.showerror("Error", "Exigencia debe estar entre 0% y 100%")
            return
        
        # Calcular y mostrar notas
        puntaje_aprobacion = puntaje_max * (exigencia/100)
        
        for puntaje in range(0, int(puntaje_max)+1):
            if puntaje >= puntaje_aprobacion:
                nota = 4.0 + (puntaje - puntaje_aprobacion) / (puntaje_max - puntaje_aprobacion) * 3.0
            else:
                nota = 1.0 + puntaje / puntaje_aprobacion * 2.9
            
            nota_redondeada = max(1.0, min(7.0, round(nota, 1)))
            
            # Configurar color (rojo para reprobados, negro para aprobados)
            color = 'red' if nota_redondeada < 4.0 else 'black'
            
            # Insertar texto con formato
            resultados_text.tag_config(color, foreground=color)
            resultados_text.insert(tk.END, f"{puntaje:3} pts = {nota_redondeada:4.1f}   ")
            
            # Salto de línea cada 4 elementos
            if (puntaje + 1) % 4 == 0:
                resultados_text.insert(tk.END, '\n')
        
        resultados_text.config(state='disabled')
        
    except ValueError:
        messagebox.showerror("Error", "Ingrese valores numéricos válidos")

ventana.mainloop()