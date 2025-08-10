#para obtener la fecha actual del sistema
from datetime import datetime 

# Presentacion de la app
print("=== Bienvenido/a a DesenchufApp ===")
print("Sabias que los electrodomesticos consumen energia aunque esten apagados? Esto se llama <consumo fantasma> y puede aumentar el costo de tu factura de luz.")
print("⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣦⠀")
print("⠀⠀⠀⠀⣰⣿⡟⢻⣿⡟⢻⣧")
print("⠀⠀⠀⣰⣿⣿⣇⣸⣿⣇⣸⣿")
print("⠀⠀⣴⣿⣿⣿⣿⠟⢻⣿⣿⣿")
print("⣠⣾⣿⣿⣿⣿⣿⣤⣼⣿⣿⠇")
print("⢿⡿⢿⣿⣿⣿⣿⣿⣿⣿⡿⠀")
print("⠀⠀⠈⠿⠿⠋⠙⢿⣿⡿⠁⠀")
print("DesenchufApp te ayuda a registrar el uso de tus electrodomesticos, calcular cuanto consumen (activo y en consumo fantasma) y cuanto CO2 generan.")
print("¡Compite con tus amigos usando DesenchufApp! Registra ecohabitos para sumar ecopuntos y reduce tu consumo electrico para generar menos CO2. ¿Quien sera el mas eco-friendly? Empecemos a ahorrar energia!")
print("Empecemos a ahorrar energia!")

# Menu principal y las opciones
def menu():
    print("\n=== DesenchufApp ===")
    print("1. Mostrar electrodomesticos")
    print("2. Registrar electrodomestico")
    print("3. Modificar electrodomestico")
    print("4. Registrar consumo electrico")
    print("5. Ver consumos electricos")
    print("6. Registrar ecohabito")
    print("7. Ver ecohabitos")
    print("8. Calcular kWh y CO2")
    print("9. Salir")

# Mostrar electrodomesticos
def mostrar_electros():
    archivo = open("electrodomesticos.txt", "r")
    lineas = archivo.readlines() #lineas guarda todo nuestro archivo en una sola variable
    archivo.close()
    print("\nElectrodomesticos registrados:") #<\n> da salto de linea para hacer espacio
    for linea in lineas: #recorremos todo el archivo y en cada iteracion en la variable <<linea>> tenemos lo que seria un registro en pseudocodigo
        if linea.strip():
            nombre, watts = linea.strip().split(",") #separamos por comas cada variable que vamos a usar
            kwh = float(watts) / 1000
            consumo_fantasma = kwh * 0.05
            print(f"- {nombre} (Activo: {kwh:.3f} kWh, Consumo fantasma: {consumo_fantasma:.3f} kWh)") #recorda usar <<: .3f>> para mostrar max 3 decimales y <<f>> para escribir mas facil el mensaje con llaves
    return True

# Buscar un electrodomestico (usado mas adelante)
def buscar_electro(nombre):
    archivo = open("electrodomesticos.txt", "r")
    for linea in archivo:
        if linea.strip():
            nombre_electro, watts = linea.strip().split(",")
            if nombre_electro.lower() == nombre.lower():
                archivo.close()
                kwh = float(watts) / 1000
                consumo_fantasma = kwh * 0.05
                return nombre_electro, kwh, consumo_fantasma
    archivo.close()
    return None, None, None

# Registrar un electrodomestico
def registrar_electro():

    #Guia para que los usuarios aprendan a identificar el gasto de su electrodomestico
    print("\n=== Guia para saber los watts ===")
    print("1. Busca la etiqueta energetica en la parte trasera o inferior del electrodomestico. Suele decir los watts (W) o voltios (V) y amperios (A).")
    print("2. Si dice voltios y amperios, multiplica: Watts = Voltios * Amperios. En Argentina usamos 220 voltios.")
    print("3. Si no esta en la etiqueta, mira el manual del electrodomestico o la pagina del fabricante.")
    print("4. Si no lo encontras, podes usar un medidor de consumo electrico.")
    print("Ejemplo: Un televisor puede decir '100 W' o '220 V, 0.45 A' (220 * 0.45 = 99 W).")
    
    # Mostrar electrodomesticos registrados antes de pedir uno nuevo
    mostrar_electros()
    
    print()
    nombre = input("\nNombre del electrodomestico: ")
    print()
    watts = float(input("\nWatts que usa: "))
    archivo = open("electrodomesticos.txt", "a")
    archivo.write(f"{nombre},{watts}\n")
    archivo.close()
    print(f"{nombre} registrado con {watts} Watts!")

# Modificar un electrodomestico
def modificar_electro():
    
    # Mostrar electrodomesticos registrados para ver cual modificar
    mostrar_electros()
    print()
    nombre = input("\nNombre del electrodomestico a modificar: ")
    nombre_existente, _, _ = buscar_electro(nombre)
    if nombre_existente is None:
        print("Electrodomestico no encontrado.")
        return
    
    print()
    nuevo_nombre = input("\nNuevo nombre del electrodomestico: ")
    print()
    nuevos_watts = float(input("\nNuevos watts que usa: "))
    
    archivo = open("electrodomesticos.txt", "r")
    lineas = archivo.readlines()
    archivo.close()
    
    archivo = open("electrodomesticos.txt", "w")
    for linea in lineas:
        if linea.strip():
            nombre_electro, _ = linea.strip().split(",")
            if nombre_electro.lower() == nombre.lower():
                archivo.write(f"{nuevo_nombre},{nuevos_watts}\n")
            else:
                archivo.write(linea)
    archivo.close()
    print(f"Electrodomestico '{nombre_existente}' modificado a '{nuevo_nombre}' con {nuevos_watts} Watts!")

# Registrar consumo electrico con horas de uso (0.75 kg co2 por hora sale de la media de la produccion de co2 por generacion con biomasa o termica que son fuentes en chaco)
def registrar_consumo():
    fecha = datetime.now().strftime("%d/%m/%Y") #Guardar en una variable la fecha actual en formato dd/mm/aaaa
    print(f"Hoy es {fecha}")
    
    mostrar_electros() #Uso de modularidad
    
    print()
    nombre = input("\nNombre del electrodomestico: ")
    nombre, kwh, consumo_fantasma_por_hora = buscar_electro(nombre) #Uso de modularidad
    if nombre is None:
        print("No se encontro el electrodomestico. Registra uno nuevo en la opcion 2.")
        return
    
    print()
    uso = input(f"\nUsaste el/la {nombre}? (si/no): ").lower()
    consumo_activo = 0.0
    consumo_fantasma = 0.0
    
    if uso == "si":
        print()
        horas = float(input(f"\nCuantas horas usaste el/la {nombre}? "))
        horas_fantasma = 24 - horas
        consumo_activo = kwh * horas
        consumo_fantasma = consumo_fantasma_por_hora * horas_fantasma
        co2_fantasma = consumo_fantasma * 0.75
        print(f"Consumo activo registrado: {consumo_activo:.3f} kWh por {horas} horas de uso")
        print(f"Las {horas_fantasma} horas restantes del dia, si no desenchufas el/la {nombre}, pueden generar un consumo fantasma de: {consumo_fantasma:.3f} kWh ({co2_fantasma:.3f} kg CO2)")
    else:
        print()
        desenchufado = input(f"\nEsta desenchufado/a el/la {nombre}? (si/no): ").lower()
        if desenchufado == "no":
            print()
            horas_enchufado = float(input(f"\nCuantas horas estima que el/la {nombre} estuvo enchufado? "))
            consumo_fantasma = consumo_fantasma_por_hora * horas_enchufado
            co2_fantasma = consumo_fantasma * 0.75
            print(f"Si no desenchufas el/la {nombre}, el consumo fantasma durante las {horas_enchufado} horas estimadas seria: {consumo_fantasma:.3f} kWh ({co2_fantasma:.3f} kg CO2)")
        else:
            print(f"Felicidades por desenchufar el/la {nombre}! Esto ayuda a reducir el consumo fantasma.")
    
    archivo = open("consumo_electrico.txt", "a")
    archivo.write(f"{fecha},{nombre},{consumo_activo:.3f},{consumo_fantasma:.3f}\n")
    archivo.close()
    print("Consumo registrado!")

# Registrar ecohabito con lista predefinida
def registrar_ecohabito():

    fecha = datetime.now().strftime("%d/%m/%Y") 
    print(f"Hoy es {fecha}")
    print("\n=== Menu de Ecohabitos ===")
    print("1. Apagar y desconectar: No te olvides de la luz, si nadie esta alli no hace falta luz")
    print("2. Usar bolsas ecologicas: No utilices materiales de un solo uso, mejor dale muchos usos a un solo material")
    print("3. Cuidar el agua: Reduce el tiempo de la ducha, repara las goteras")
    print("4. Almacenar el aceite de cocina: Ademas de contaminar bloquea las tuberias")
    print("5. Reciclar: Siempre es mejor separar y llevar a centros o puntos de reciclaje")
    print("6. Priorizar los materiales reutilizables: Botellas de un solo uso? puaj, prefiero unas retornables")
    print("7. Reducir el uso del automovil: Hoy puedes viajar en el transporte publico o hacer ejercicio con la bici")
    print("8. Planta un arbol: Planta un amigo que te ayude en la lucha contra la contaminacion")
    print("9. Almacenar baterias: Trata de no utilizar productos con baterias, estas deben be treated adecuadamente al final de su vida util")
    
    print()
    opcion = input("\nElige una opcion (1-9): ")
    
    if opcion == "1":
        ecohabito = "Apagar y desconectar"
        ecopuntos = 29
        co2_ahorro = "95-134 kg CO2 por año"
        impacto = "Reduce emisiones en el aire al disminuir el consumo electrico."
    elif opcion == "2":
        ecohabito = "Usar bolsas ecologicas"
        ecopuntos = 47
        co2_ahorro = "100-200 kg CO2 por año"
        impacto = "Disminuye residuos plasticos en la tierra y microplasticos en el agua."
    elif opcion == "3":
        ecohabito = "Cuidar el agua"
        ecopuntos = 70
        co2_ahorro = "150-581 kg CO2 por año"
        impacto = "Reduce el uso de agua potable y la contaminacion por aguas residuales."
    elif opcion == "4":
        ecohabito = "Almacenar el aceite de cocina"
        ecopuntos = 32
        co2_ahorro = "20-30 kg CO2 por año"
        impacto = "Evita la contaminacion de cuerpos de agua y residuos en la tierra."
    elif opcion == "5":
        ecohabito = "Reciclar"
        ecopuntos = 95
        co2_ahorro = "555-605 kg CO2 por año"
        impacto = "Reduce residuos en la tierra, contaminacion en el agua y emisiones en el aire."
    elif opcion == "6":
        ecohabito = "Priorizar los materiales reutilizables"
        ecopuntos = 40
        co2_ahorro = "100-150 kg CO2 por año"
        impacto = "Disminuye residuos en la tierra y microplasticos en el agua."
    elif opcion == "7":
        ecohabito = "Reducir el uso del automovil"
        ecopuntos = 75
        co2_ahorro = "426 kg CO2 por año"
        impacto = "Reduce emisiones de gases y particulas contaminantes en el aire."
    elif opcion == "8":
        ecohabito = "Planta un arbol"
        ecopuntos = 32
        co2_ahorro = "20-40 kg CO2 por año"
        impacto = "Mejora la calidad del aire, retiene agua y enriquece la tierra."
    elif opcion == "9":
        ecohabito = "Almacenar baterias"
        ecopuntos = 36
        co2_ahorro = "5-10 kg CO2 por año"
        impacto = "Evita la contaminacion del agua y la tierra por metales pesados."
    else:
        print("Opcion incorrecta, intenta de nuevo.")
        return
    
    archivo = open("ecohabitos.txt", "a")
    archivo.write(f"{fecha},{ecohabito},{ecopuntos}\n")
    archivo.close()
    print(f"Ecohabito '{ecohabito}' registrado!")
    print(f"¡Felicidades! Has sumado {ecopuntos} ecopuntos ayudando al medioambiente.")
    print(f"Esto puede ahorrar hasta {co2_ahorro}.")
    print(f"Impacto: {impacto}")

# Mostrar ecohabitos
def ver_ecohabitos():
    archivo = open("ecohabitos.txt", "r")
    lineas = archivo.readlines()
    archivo.close()
    total_ecopuntos = 0
    print("\n=== Ecohabitos ===")
    for linea in lineas:
        if linea.strip():
            fecha, ecohabito, ecopuntos = linea.strip().split(",")
            ecopuntos = int(ecopuntos)
            total_ecopuntos += ecopuntos
            print(f"{fecha}: {ecohabito} ({ecopuntos} ecopuntos)")
    print(f"Total ecopuntos: {total_ecopuntos}")

# Mostrar consumos electricos
def ver_consumos():
    archivo = open("consumo_electrico.txt", "r")
    lineas = archivo.readlines()
    archivo.close()
    print("\n=== Consumos Electricos ===")
    for linea in lineas:
        if linea.strip():
            fecha, nombre, kwh, consumo_fantasma = linea.strip().split(",")
            kwh = float(kwh)
            consumo_fantasma = float(consumo_fantasma)
            co2_fantasma = consumo_fantasma * 0.75
            print(f"Fecha: {fecha} - {nombre} - Activo: {kwh:.3f} kWh - Consumo fantasma: {consumo_fantasma:.3f} kWh ({co2_fantasma:.3f} kg CO2)")

# Calcular kWh y CO2
def calcular_co2():
    archivo = open("consumo_electrico.txt", "r")
    lineas = archivo.readlines()
    archivo.close()
    total_kwh = 0.0
    print("\n=== Consumo y CO2 ===")
    for linea in lineas:
        if linea.strip():
            fecha, nombre, kwh, consumo_fantasma = linea.strip().split(",")
            kwh = float(kwh)
            consumo_fantasma = float(consumo_fantasma)
            total = kwh + consumo_fantasma
            total_kwh += total
            print(f"Fecha: {fecha} - {nombre}")
            print(f"  Activo: {kwh:.3f} kWh, Consumo fantasma: {consumo_fantasma:.3f} kWh")
            print(f"  Total: {total:.3f} kWh")
    
    co2 = total_kwh * 0.75
    print(f"\nTotal kWh: {total_kwh:.3f} kWh")
    print(f"Total CO2: {co2:.3f} kg")

# Programa principal con el menu
def main():
    while True:
        menu()
        opcion = input("\nElige una opcion (1-9): ")
        
        if opcion == "1":
            mostrar_electros()
        elif opcion == "2":
            registrar_electro()
        elif opcion == "3":
            modificar_electro()
        elif opcion == "4":
            registrar_consumo()
        elif opcion == "5":
            ver_consumos()
        elif opcion == "6":
            registrar_ecohabito()
        elif opcion == "7":
            ver_ecohabitos()
        elif opcion == "8":
            calcular_co2()
        elif opcion == "9":
            print("Hasta pronto, gracias por usar nuestro sistema!")
            break
        else:
            print("Opcion incorrecta, elige otra.")

# Iniciar el programa
if __name__ == "__main__":
    main()