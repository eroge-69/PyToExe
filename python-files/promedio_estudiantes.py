import os

def limpiar_pantalla():
    if os.name == 'nt':  # Si es Windows
        os.system('cls')
    else:  # Si es macOS o Linux
        os.system('clear')

def calcular_promedio(puntos_totales, puntos_errados):
    puntos_obtenidos = puntos_totales - puntos_errados
    promedio = (puntos_obtenidos / puntos_totales) * 4.4 + 0.6
    return puntos_obtenidos, puntos_errados, promedio

def main():
    limpiar_pantalla()  # Limpiar pantalla al iniciar
    puntos_totales = float(input("Ingresa la cantidad de puntos totales de la prueba: "))
    
    while True:
        opcion = input("¿Deseas ingresar los puntos correctos o los puntos incorrectos? (c/i, o ingresa 'salir' para terminar): ").lower()
        
        if opcion == 'salir':
            print("Proceso terminado.")
            break
        
        if opcion == 'c':
            puntos_correctos = float(input("Ingresa la cantidad de puntos correctos: "))
            puntos_errados = puntos_totales - puntos_correctos
        elif opcion == 'i':
            puntos_errados = float(input("Ingresa la cantidad de puntos errados: "))
            puntos_correctos = puntos_totales - puntos_errados
        else:
            print("Opción no válida. Inténtalo de nuevo.")
            continue
        
        _, _, promedio = calcular_promedio(puntos_totales, puntos_errados)
        
        limpiar_pantalla()  # Limpiar pantalla antes de mostrar los resultados
        
        print(f"Puntos correctos: {puntos_correctos} / {puntos_totales}")
        print(f"Puntos incorrectos: {puntos_errados}")
        print(f"El promedio del estudiante es: {promedio:.2f}")

if __name__ == "__main__":
    main()