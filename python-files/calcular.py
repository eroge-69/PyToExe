def calcular_precio_enmarcado_por_perimetro(precio_metro, alto, ancho, unidad="m"):
    # Convertir medidas a metros si están en cm
    if unidad == "cm":
        alto /= 100
        ancho /= 100

    perimetro = 2 * (alto + ancho)  # Cálculo del perímetro
    costo_total = perimetro * precio_metro

    print(f"\nPerímetro del objeto: {perimetro:.2f} m")
    print(f"Precio por metro lineal: ${precio_metro:.2f}")
    print(f"Precio total del enmarcado: ${costo_total:.2f}")


# ---- Ejecución interactiva ----
precio_metro = float(input("Ingresa el precio por metro de moldura: "))
alto = float(input("Ingresa el alto del objeto a enmarcar: "))
ancho = float(input("Ingresa el ancho del objeto a enmarcar: "))
unidad = input("¿Las medidas están en 'm' o 'cm'? (por defecto 'cm'): ") or "cm"

calcular_precio_enmarcado_por_perimetro(precio_metro, alto, ancho, unidad)
                

