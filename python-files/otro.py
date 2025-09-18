echo "
animales = [
    'Aguila', 'Buey', 'Burro', 'Camello', 'Canguro',
    'Carpa', 'Cotorra', 'Elefante', 'Gallo', 'Gato',
    'León', 'Lobo', 'Mariposa', 'Perro', 'Pescado',
    'Pez', 'Rana', 'Ratón', 'Serpiente', 'Tigre'
]

frecuencias = {animal: 0 for animal in animales}
total_resultados = 0

def actualizar_frecuencias(nuevos_resultados):
    global total_resultados
    for res in nuevos_resultados:
        if res in frecuencias:
            frecuencias[res] += 1
            total_resultados += 1

def calcular_probabilidades():
    probabilidades = {}
    for animal, freq in frecuencias.items():
        probabilidades[animal] = freq / total_resultados if total_resultados > 0 else 0
    return probabilidades

def animal_mas_probable(probabilidades):
    animal = max(probabilidades, key=probabilidades.get) if probabilidades else None
    return animal, probabilidades.get(animal,0)

def main():
    print('Iniciando sistema de análisis de Lotería Animalitos...')
    resultados_historicos = ['Gallo', 'Perro', 'Gato', 'Rana', 'Tigre', 'Perro', 'Aguila', 'Perro', 'León', 'Gallo']
    actualizar_frecuencias(resultados_historicos)
    while True:
        probabilidades = calcular_probabilidades()
        animal, prob = animal_mas_probable(probabilidades)
        print(f'Animal con mayor probabilidad: {animal} ({prob:.2%})')
        print('Probabilidades de todos los animales:')
        for a, p in probabilidades.items():
            print(f'  {a}: {p:.2%}')
        entrada = input('\\nIngrese resultados nuevos separados por coma (o salir): ').strip()
        if entrada.lower() == 'salir':
            print('Terminando sistema.')
            break
        nuevos_resultados = [x.strip().capitalize() for x in entrada.split(',')]
        actualizar_frecuencias(nuevos_resultados)

if __name__ == '__main__':
    main()
" > animalitos.py && pyinstaller --onefile animalitos.py