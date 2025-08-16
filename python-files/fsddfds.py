import tkinter as tk
from tkinter import messagebox

def calcular():
    """
    Función que toma el número del recuadro, realiza la operación y muestra el resultado.
    """
    try:
        # Obtiene el texto del recuadro y lo convierte a un número de tipo flotante
        entrada = float(campo_numero.get())
        
        # Realiza la operación solicitada
        resultado = entrada / 0.6 * 1.16
        
        # Muestra el resultado en la etiqueta de salida
        etiqueta_resultado.config(text=f"Resultado: {resultado:.2f}")
        
    except ValueError:
        # Muestra un mensaje de error si el usuario no ingresó un número válido
        messagebox.showerror("Error de entrada", "Por favor, ingresa solo números.")

# 1. Configurar la ventana principal de la aplicación
ventana = tk.Tk()
ventana.title("Mini Calculadora")
ventana.geometry("300x150")
ventana.resizable(False, False)

# 2. Crear los widgets (recuadro de entrada, botón y etiqueta de resultado)

# Etiqueta para indicar al usuario qué hacer
etiqueta_instruccion = tk.Label(ventana, text="Ingresa un número:")
etiqueta_instruccion.pack(pady=5)

# Campo de entrada para el número
campo_numero = tk.Entry(ventana)
campo_numero.pack(pady=5)

# Botón que llama a la función 'calcular' cuando se hace clic
boton_calcular = tk.Button(ventana, text="Calcular", command=calcular)
boton_calcular.pack(pady=5)

# Etiqueta para mostrar el resultado
etiqueta_resultado = tk.Label(ventana, text="Resultado: ")
etiqueta_resultado.pack(pady=5)

# 3. Iniciar el bucle principal de la aplicación
ventana.mainloop()