# Menu para elegir operador
# Funcion para cada operador? o Funcion con todos los operadores?
# Poder cambiar el operador cuando sea
# Loop "infinito", posible salir si el usuario escribe "salir"

menu = ["suma", "resta", "multiplicacion", "division", "salir"]

def sumar_numeros(*args):
    suma = 0
    for numero in args:
        suma += numero
    return suma

def restar_numeros(*args):
    if not args:
        return 0
    resta = args[0]
    for numero in args[1:]:
        resta -= numero
    return resta

def multiplicar_numeros(*args):
    multiplicacion = 1
    for numero in args:
        multiplicacion * numero
    return multiplicacion

def dividir_numeros(*args):
    if not args:
        return 0
    division = args[0]
    for numero in args[1:]:
        division /= numero
    return division

numeros = []
calculadora = True
parar = True

while calculadora:
    print(f"""\n
---MENU---
1.suma
2.resta
3.multiplicacion
4.division
5.salir
""")
    seleccion = input("escribe el nombre de la opcion: ")
    if seleccion == menu[0]:
        while parar:
            entrada = input("Escribe un número (o 'fin' para terminar): ")
            if entrada.lower() == "fin":
                resultado = sumar_numeros(*numeros)
                print(resultado)
                break
            numeros.append(int(entrada))
    elif seleccion == menu[1]:
        while parar:
            entrada = input("Escribe un número (o 'fin' para terminar): ")
            if entrada.lower() == "fin":
                resultado = restar_numeros(*numeros)
                print(resultado)
                break
            numeros.append(int(entrada))
    elif seleccion == menu[2]:
        while parar:
            entrada = input("Escribe un número (o 'fin' para terminar): ")
            if entrada.lower() == "fin":
                resultado = multiplicar_numeros(*numeros)
                print(resultado)
                break
            numeros.append(int(entrada))
    elif seleccion == menu[3]:
        while parar:
            entrada = input("Escribe un número (o 'fin' para terminar): ")
            if entrada.lower() == "fin":
                resultado = dividir_numeros(*numeros)
                print(resultado)
                break
            numeros.append(int(entrada))
    elif seleccion == menu[4]:
        print("Hasta luego!")
        break
    else:
        print("Opcion no valida.\n")