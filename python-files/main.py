def calcular_tamano_cm(pixeles, escala, ppi):
    """
    Calcula el tamaño en centímetros a partir de píxeles, escala y PPI.

    Args:
        pixeles (float): La dimensión del lienzo en píxeles.
        escala (float): El valor de escala.
        ppi (float): Píxeles por pulgada (Pixels Per Inch).

    Returns:
        float: El tamaño en centímetros.
    """
    if ppi == 0:
        return "Error: PPI no puede ser cero."
    tam_cm = (pixeles * escala) / (ppi * 2.54)
    return tam_cm

def calcular_escala(tam_cm, ppi, pixeles):
    """
    Calcula la escala a partir del tamaño en centímetros, PPI y píxeles.

    Args:
        tam_cm (float): El tamaño en centímetros.
        ppi (float): Píxeles por pulgada (Pixels Per Inch).
        pixeles (float): La dimensión del lienzo en píxeles.

    Returns:
        float: El valor de escala.
    """
    if pixeles * 2.54 == 0:
        return "Error: La multiplicación de píxeles por 2.54 no puede ser cero."
    escala = (tam_cm * ppi) / (pixeles * 2.54)
    return escala

def main():
    """
    Función principal para interactuar con el usuario y aplicar las fórmulas.
    """
    while True:
        print("\nSelecciona una opción:")
        print("1. Calcular Tamaño en Cm (Tam.Cm.)")
        print("2. Calcular Escala")
        print("3. Salir")

        opcion = input("Ingresa el número de tu opción: ")

        if opcion == '1':
            try:
                pixeles = float(input("Ingresa la dimensión en píxeles del lienzo: "))
                escala = float(input("Ingresa el valor de la escala: "))
                ppi = float(input("Ingresa el valor de PPI (Píxeles por Pulgada): "))
                resultado = calcular_tamano_cm(pixeles, escala, ppi)
                print(f"El Tamaño en Cm es: {resultado:.4f} cm")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa números para los valores.")
        elif opcion == '2':
            try:
                tam_cm = float(input("Ingresa el Tamaño en Cm: "))
                ppi = float(input("Ingresa el valor de PPI (Píxeles por Pulgada): "))
                pixeles = float(input("Ingresa la dimensión en píxeles del lienzo: "))
                resultado = calcular_escala(tam_cm, ppi, pixeles)
                print(f"La Escala es: {resultado:.4f}")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa números para los valores.")
        elif opcion == '3':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if "_name_" == "_main_":
    main()