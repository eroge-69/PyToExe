import random

def generar_lista_objetivo():
    n0 = random.randint(0, 11)
    print(f"Número inicial (n0): {n0}")

    distintos = set()

    while True:
        nuevo = random.randint(0, 11)
        if nuevo != n0:
            distintos.add(nuevo)

        if len(distintos) in {3, 5, 7} or len(distintos) > 7:
            break

    print(f"Números distintos a {n0} generados: {sorted(distintos)}")
    input("\nPresiona ENTER para salir...")

# Ejecutar solo si es programa principal
if __name__ == "__main__":
    generar_lista_objetivo()
