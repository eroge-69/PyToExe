import tkinter as tk
from tkinter import messagebox

# Base de datos de animales
animales = [
    {"nombre": "León", "habitat": "selva", "alimentacion": "carnívoro", "patas": 4, "caracteristicas": ["melena", "ruge"]},
    {"nombre": "Cebra", "habitat": "sabana", "alimentacion": "herbívoro", "patas": 4, "caracteristicas": ["rayas"]},
    {"nombre": "Elefante", "habitat": "selva", "alimentacion": "herbívoro", "patas": 4, "caracteristicas": ["trompa"]},
    {"nombre": "Tiburón", "habitat": "océano", "alimentacion": "carnívoro", "patas": 0, "caracteristicas": ["aletas"]},
    {"nombre": "Ave", "habitat": "aire", "alimentacion": "omnívoro", "patas": 2, "caracteristicas": ["vuela"]},
    {"nombre": "Perro", "habitat": "hogar", "alimentacion": "omnívoro", "patas": 4, "caracteristicas": ["ladra"]},
    {"nombre": "Gato", "habitat": "hogar", "alimentacion": "carnívoro", "patas": 4, "caracteristicas": ["maúlla"]},
    {"nombre": "Pingüino", "habitat": "aire", "alimentacion": "carnívoro", "patas": 2, "caracteristicas": ["no vuela", "camina erguido"]},
    {"nombre": "Caballo", "habitat": "sabana", "alimentacion": "herbívoro", "patas": 4, "caracteristicas": ["crin", "relincha"]},
    {"nombre": "Delfín", "habitat": "océano", "alimentacion": "carnívoro", "patas": 0, "caracteristicas": ["inteligente", "salta"]}
]

def identificar_animal(habitat, alimentacion, patas, caracteristicas_adicionales):
    habitat = habitat.lower()
    alimentacion = alimentacion.lower()
    caracteristicas_adicionales = caracteristicas_adicionales.lower()

    for animal in animales:
        if (animal["habitat"] == habitat and
            animal["alimentacion"] == alimentacion and
            animal["patas"] == patas and
            all(carac in caracteristicas_adicionales for carac in animal["caracteristicas"])):
            return f"{animal['nombre']} (coincidencia exacta)"

    coincidencias = []
    for animal in animales:
        puntuacion = 0
        if animal["habitat"] == habitat:
            puntuacion += 1
        if animal["alimentacion"] == alimentacion:
            puntuacion += 1
        if animal["patas"] == patas:
            puntuacion += 1
        puntuacion += sum(1 for carac in animal["caracteristicas"] if carac in caracteristicas_adicionales)
        if puntuacion >= 3:
            coincidencias.append((animal["nombre"], puntuacion))

    if coincidencias:
        coincidencias.sort(key=lambda x: x[1], reverse=True)
        sugerencias = ", ".join([f"{nombre} (coincidencia: {puntos})" for nombre, puntos in coincidencias])
        return f"No se encontró una coincidencia exacta. Sugerencias: {sugerencias}"
    else:
        return "No se encontró un animal que coincida con las características proporcionadas."

def procesar():
    try:
        patas = int(entry_patas.get())
    except ValueError:
        messagebox.showerror("Error", "Número de patas inválido. Debe ser un número entero.")
        return
    resultado = identificar_animal(entry_habitat.get(), entry_alimentacion.get(), patas, entry_caracteristicas.get())
    messagebox.showinfo("Resultado", resultado)

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Identificador de Animales")
ventana.geometry("400x300")

tk.Label(ventana, text="Hábitat (selva, sabana, océano, aire, hogar):").pack()
entry_habitat = tk.Entry(ventana)
entry_habitat.pack()

tk.Label(ventana, text="Alimentación (carnívoro, herbívoro, omnívoro):").pack()
entry_alimentacion = tk.Entry(ventana)
entry_alimentacion.pack()

tk.Label(ventana, text="Número de patas:").pack()
entry_patas = tk.Entry(ventana)
entry_patas.pack()

tk.Label(ventana, text="Características adicionales (ej. melena, ruge, vuela):").pack()
entry_caracteristicas = tk.Entry(ventana)
entry_caracteristicas.pack()

tk.Button(ventana, text="Identificar Animal", command=procesar).pack(pady=10)

ventana.mainloop()
