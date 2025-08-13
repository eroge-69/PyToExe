# Programa interactivo para identificar animales según sus características
# Incluye ejemplos de animales para mostrar coincidencias cercanas

def identificar_animal(habitat, alimentacion, patas, caracteristicas_adicionales):
    habitat = habitat.lower()
    alimentacion = alimentacion.lower()
    caracteristicas_adicionales = caracteristicas_adicionales.lower()

    # Base de datos de animales con sus características
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

    # Buscar coincidencia exacta
    for animal in animales:
        if (animal["habitat"] == habitat and
            animal["alimentacion"] == alimentacion and
            animal["patas"] == patas and
            all(carac in caracteristicas_adicionales for carac in animal["caracteristicas"])):
            return f"{animal['nombre']} (coincidencia exacta)"

    # Buscar coincidencias parciales
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

# Programa principal
def main():
    print("🦁 Identificador de animales 🐾")
    habitat = input("¿Dónde habita el animal? (selva, sabana, océano, aire, hogar): ")
    alimentacion = input("¿Qué tipo de alimentación tiene? (carnívoro, herbívoro, omnívoro): ")
    try:
        patas = int(input("¿Cuántas patas tiene?: "))
    except ValueError:
        print("Número de patas inválido. Debe ser un número entero.")
        return
    caracteristicas_adicionales = input("Describe algunas características adicionales (ej. melena, ruge, vuela, ladra): ")

    resultado = identificar_animal(habitat, alimentacion, patas, caracteristicas_adicionales)
    print(f"\n✅ Resultado: {resultado}")

# Ejecutar el programa
main()
