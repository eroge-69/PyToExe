def euclides_extendido(a, b):
    """
    Algoritmo extendido de Euclides.
    Devuelve (mcd, x, y) tal que: mcd = x*a + y*b
    """
    if b == 0:
        return a, 1, 0
    else:
        mcd, x1, y1 = euclides_extendido(b, a % b)
        # retrocedemos en la recursión
        x = y1
        y = x1 - (a // b) * y1
        return mcd, x, y


# Programa principal
if __name__ == "__main__":
    a = int(input("Ingrese el primer número positivo: "))
    b = int(input("Ingrese el segundo número positivo: "))

    mcd, x, y = euclides_extendido(a, b)

    print(f"El MCD de {a} y {b} es {mcd}")
    print(f"Y puede escribirse como: {mcd} = ({x})*{a} + ({y})*{b}")
