def detectar_monto(numeros, monto_objetivo):
    diferencia_minima = float('inf')
    mejor_aproximacion = None
    operacion = None

    for i in range(len(numeros)):
        if numeros[i] == monto_objetivo:
            return True, [numeros[i]], "número solo"
        if abs(numeros[i] - monto_objetivo) < diferencia_minima:
            diferencia_minima = abs(numeros[i] - monto_objetivo)
            mejor_aproximacion = [numeros[i]]
            operacion = "número solo"

        for j in range(i+1, len(numeros)):
            suma_2 = numeros[i] + numeros[j]
            resta_2 = abs(numeros[i] - numeros[j])
            if suma_2 == monto_objetivo:
                return True, [numeros[i], numeros[j]], "suma"
            if resta_2 == monto_objetivo:
                return True, [numeros[i], numeros[j]], "resta"

            if abs(suma_2 - monto_objetivo) < diferencia_minima:
                diferencia_minima = abs(suma_2 - monto_objetivo)
                mejor_aproximacion = [numeros[i], numeros[j]]
                operacion = "suma"
            if abs(resta_2 - monto_objetivo) < diferencia_minima:
                diferencia_minima = abs(resta_2 - monto_objetivo)
                mejor_aproximacion = [numeros[i], numeros[j]]
                operacion = "resta"

            for k in range(j+1, len(numeros)):
                suma_3 = numeros[i] + numeros[j] + numeros[k]
                if suma_3 == monto_objetivo:
                    return True, [numeros[i], numeros[j], numeros[k]], "suma"
                if abs(suma_3 - monto_objetivo) < diferencia_minima:
                    diferencia_minima = abs(suma_3 - monto_objetivo)
                    mejor_aproximacion = [numeros[i], numeros[j], numeros[k]]
                    operacion = "suma"

    return False, mejor_aproximacion, operacion, diferencia_minima


print("Para pegar los montos de búsqueda, debe copiar y pegarlos sin decimales ni separador de miles.")

while True:
    entrada = input("Ingrese los montos sin decimales, separados por espacios: ")
    numeros = list(map(int, entrada.strip().split()))

    while True:
        monto_objetivo = int(input("Ingrese el monto a detectar: "))
        resultado = detectar_monto(numeros, monto_objetivo)

        if resultado[0]:
            _, numeros_usados, operacion = resultado
            print(f"Monto {monto_objetivo} detectado con {operacion} de los números: {numeros_usados}")
        else:
            _, numeros_cercanos, operacion, diferencia = resultado
            print(f"No se pudo detectar el monto {monto_objetivo}. La mejor aproximación fue con {operacion} de {numeros_cercanos} con diferencia {diferencia}.")

        repetir = input("¿Desea ubicar otro monto en el mismo rango de búsqueda? (Si/No): ").strip().lower()
        if repetir != 'si':
            break
