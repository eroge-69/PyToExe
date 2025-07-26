import datetime

# Función para reducir a un solo dígito o número maestro
def reducir_numero(n):
    while True:
        if n in (11, 22, 33):
            return n
        elif n < 10:
            return n
        else:
            n = sum(int(d) for d in str(n))

# Calcula la Ruta de Vida
def calcular_ruta_de_vida(dia, mes, anio):
    dia_reducido = reducir_numero(sum(int(d) for d in str(dia)))
    mes_reducido = reducir_numero(sum(int(d) for d in str(mes)))
    anio_reducido = reducir_numero(sum(int(d) for d in str(anio)))
    total = dia_reducido + mes_reducido + anio_reducido
    return reducir_numero(total)

# Calcula el Año Personal
def calcular_ano_personal(dia, mes, anio_actual):
    dia_mes_reducido = reducir_numero(sum(int(d) for d in f"{dia:02d}{mes:02d}"))
    anio_actual_reducido = reducir_numero(sum(int(d) for d in str(anio_actual)))
    total = dia_mes_reducido + anio_actual_reducido
    return reducir_numero(total)

# Calcula el Número de Nacimiento
def calcular_numero_nacimiento(dia):
    return reducir_numero(sum(int(d) for d in str(dia)))

# Función principal
def main():
    print("Calculadora de Numerología Pitagórica Clásica")
    fecha_input = input("Introduce tu fecha de nacimiento (dd/mm/aaaa): ")

    try:
        dia, mes, anio = map(int, fecha_input.strip().split("/"))
        fecha_valida = datetime.date(anio, mes, dia)
    except ValueError:
        print("Fecha inválida. Por favor usa el formato dd/mm/aaaa.")
        return

    anio_actual = datetime.date.today().year

    ruta_vida = calcular_ruta_de_vida(dia, mes, anio)
    ano_personal = calcular_ano_personal(dia, mes, anio_actual)
    numero_nacimiento = calcular_numero_nacimiento(dia)

    print(f"\nResultados para la fecha {fecha_input}:")
    print(f"--------------------------")
    print(f"🔹 Número de Ruta de Vida: {ruta_vida}")
    print("Tu camino principal en la vida, propósito y lecciones centrales.")
    print(f"--------------------------")
    print(f"🔹 Número de Año Personal ({anio_actual}): {ano_personal}")
    print("Energía y enfoque específico que influye en tu año actual.")
    print(f"--------------------------")
    print(f"🔹 Número de Nacimiento: {numero_nacimiento}")
    print("Talento natural o don especial que traes desde el nacimiento.")
    print(f"--------------------------")
    print(f" ")
    print(f" ")

if __name__ == "__main__":
    main()
