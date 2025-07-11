import random

preguntas_respuestas = {
    "¿Qué es la regresión lineal y cuál es su objetivo principal?": "La regresión lineal es una técnica de machine learning para predecir un valor numérico continuo basándose en una o más características. Su objetivo es encontrar una función matemática que describa la relación entre las variables para hacer predicciones precisas.",
    "¿Por qué es crucial dividir los datos en entrenamiento y validación?": "Dividir los datos permite entrenar el modelo con un subconjunto y evaluar su rendimiento con datos no vistos, ayudando a evitar el sobreajuste y asegurando que el modelo generalice bien.",
    "¿Cuál es la diferencia fundamental entre clasificación y regresión?": "La regresión predice valores numéricos continuos, mientras que la clasificación predice categorías o clases discretas.",
    "¿Qué es una matriz de confusión y para qué se usa?": "Es una tabla que muestra los resultados de predicción cruzando etiquetas reales y predichas, usada para evaluar el rendimiento de modelos de clasificación.",
    "¿Cuál es el objetivo principal del agrupamiento en aprendizaje no supervisado?": "Identificar patrones y agrupar elementos similares en clusters sin usar etiquetas conocidas.",
    "¿Por qué es importante normalizar los datos?": "Para escalar características numéricas a un rango común y evitar que una domine el entrenamiento del modelo.",
    "¿Cuál es la diferencia entre una instancia de cómputo y un cluster en Azure ML Studio?": "Una instancia es una estación de trabajo individual para desarrollo, y un cluster es un grupo escalable de máquinas para entrenamiento intensivo.",
    "¿Qué permite hacer la clasificación de imágenes en Computer Vision?": "Permite categorizar imágenes basándose en su contenido, como identificar tipos de frutas o detectar mascarillas.",
    "¿Cómo funciona el análisis de sentimiento en NLP?": "Determina la emoción o tono predominante en un texto usando frases clave y patrones lingüísticos.",
    "Menciona dos consideraciones éticas al desarrollar chatbots.": "Confiabilidad para dar respuestas precisas y privacidad para proteger los datos del usuario."
}

def jugar_preguntas():
    print("Juego interactivo de preguntas cortas sobre Machine Learning")
    preguntas = list(preguntas_respuestas.keys())
    random.shuffle(preguntas)
    for pregunta in preguntas:
        print(f"\nPregunta: {pregunta}")
        input("Presiona Enter para ver la respuesta...")
        print(f"Respuesta: {preguntas_respuestas[pregunta]}")

jugar_preguntas()
