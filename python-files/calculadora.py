print("Uriel Germán Martínez, Grupo: 2do A")

def mostrar_menu():
    print("\nCalculadora de Unidades")
    print("Selecciona el tipo de conversión:")
    print("1. Longitud")
    print("2. Masa")
    print("3. Volumen")
    print("4. Presión")
    print("5. Energía")
    print("6. Temperatura")
    print("0. Salir")

while True:
    mostrar_menu()
    opcion = input("Escribe el número de la opción: ")

    if opcion == "1":
        while True:
            print("\nConversión de Longitud")
            print("1. Pulgadas a metros")
            print("2. Pies a metros")
            print("3. Yardas a metros")
            print("4. Millas a metros")
            print("5. Milla náutica a metros")
            subop = input("Elige una opción: ")

            if subop in ["1", "2", "3", "4", "5"]:
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor * 0.0254, "m")
                elif subop == "2":
                    print("Resultado:", valor * 0.3048, "m")
                elif subop == "3":
                    print("Resultado:", valor * 0.9144, "m")
                elif subop == "4":
                    print("Resultado:", valor * 1609.344, "m")
                elif subop == "5":
                    print("Resultado:", valor * 1852, "m")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "2":
        while True:
            print("\nConversión de Masa")
            print("1. Libras a kilogramos")
            print("2. Onzas a kilogramos")
            print("3. Tonelada corta a kilogramos")
            print("4. Tonelada larga a kilogramos")
            subop = input("Elige una opción: ")

            if subop in ["1", "2", "3", "4"]:
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor * 0.45359237, "kg")
                elif subop == "2":
                    print("Resultado:", valor * 0.0283495, "kg")
                elif subop == "3":
                    print("Resultado:", valor * 907.18474, "kg")
                elif subop == "4":
                    print("Resultado:", valor * 1016.04641, "kg")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "3":
        while True:
            print("\nConversión de Volumen")
            print("1. Galón a litros")
            print("2. Barril petrolero a litros")
            subop = input("Elige una opción: ")

            if subop == "1" or subop == "2":
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor * 3.78541, "L")
                elif subop == "2":
                    print("Resultado:", valor * 158.987244928, "L")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "4":
        while True:
            print("\nConversión de Presión")
            print("1. Atmósferas a pascales")
            print("2. Bar a pascales")
            print("3. PSI a pascales")
            subop = input("Elige una opción: ")

            if subop in ["1", "2", "3"]:
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor * 101325, "Pa")
                elif subop == "2":
                    print("Resultado:", valor * 100000, "Pa")
                elif subop == "3":
                    print("Resultado:", valor * 6894.76, "Pa")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "5":
        while True:
            print("\nConversión de Energía")
            print("1. Calorías a julios")
            print("2. Kilocalorías a julios")
            subop = input("Elige una opción: ")

            if subop == "1" or subop == "2":
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor * 4.184, "J")
                elif subop == "2":
                    print("Resultado:", valor * 4184, "J")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "6":
        while True:
            print("\nConversión de Temperatura")
            print("1. Centígrados a Kelvin")
            print("2. Fahrenheit a Kelvin")
            subop = input("Elige una opción: ")

            if subop == "1" or subop == "2":
                valor = float(input("Ingresa el valor: "))
                if subop == "1":
                    print("Resultado:", valor + 273.15, "K")
                elif subop == "2":
                    print("Resultado:", (valor - 32) * 5/9 + 273.15, "K")
                break
            else:
                print("Opción inválida, intenta de nuevo.")

    elif opcion == "0":
        print("Gracias por usar la calculadora")
        break

    else:
        print("Opción no válida, intenta nuevamente.")
        continue

    repetir = input("\n¿Deseas realizar otra conversión? (s/n): ").lower()
    if repetir != "s":
        print("Gracias por usar la calculadora")
        break
