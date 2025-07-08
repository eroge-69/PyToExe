# guia_telefonica.py
# Software simple de Guia Telefonica Antel 1997 estilo Volt Autologic Directories

# Datos ejemplo: lista de diccionarios con nombre, teléfono y dirección
contactos = [
    {"nombre": "Juan Perez", "telefono": "29000001", "direccion": "Av. Italia 1234"},
    {"nombre": "Maria Gomez", "telefono": "29000002", "direccion": "Calle 18 de Julio 5678"},
    {"nombre": "Carlos Lopez", "telefono": "29000003", "direccion": "Bulevar Artigas 910"},
    {"nombre": "Ana Rodriguez", "telefono": "29000004", "direccion": "Rambla 123"},
    {"nombre": "Luis Martinez", "telefono": "29000005", "direccion": "Av. Uruguay 456"},
]

def buscar_por_nombre(nombre):
    nombre = nombre.lower()
    resultados = []
    for c in contactos:
        if nombre in c["nombre"].lower():
            resultados.append(c)
    return resultados

def buscar_por_numero(numero):
    resultados = []
    for c in contactos:
        if numero in c["telefono"]:
            resultados.append(c)
    return resultados

def mostrar_resultados(resultados):
    if len(resultados) == 0:
        print("No se encontraron resultados.")
    else:
        print(f"Se encontraron {len(resultados)} resultados:")
        for c in resultados:
            print(f"Nombre: {c['nombre']}, Teléfono: {c['telefono']}, Dirección: {c['direccion']}")

def menu():
    while True:
        print("\n--- Guía Telefónica Antel 1997 ---")
        print("1. Buscar por nombre")
        print("2. Buscar por número")
        print("3. Salir")
        opcion = input("Seleccione una opción (1-3): ")

        if opcion == "1":
            nombre = input("Ingrese nombre a buscar: ")
            resultados = buscar_por_nombre(nombre)
            mostrar_resultados(resultados)
        elif opcion == "2":
            numero = input("Ingrese número a buscar: ")
            resultados = buscar_por_numero(numero)
            mostrar_resultados(resultados)
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()