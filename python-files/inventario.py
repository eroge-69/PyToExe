
import os

archivo = "inventario.txt"

def cargar_inventario():
    inventario = {}
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            for linea in f:
                nombre, cantidad, precio = linea.strip().split("|")
                inventario[nombre] = {"cantidad": int(cantidad), "precio": float(precio)}
    return inventario

def guardar_inventario(inventario):
    with open(archivo, "w") as f:
        for nombre, datos in inventario.items():
            f.write(f"{nombre}|{datos['cantidad']}|{datos['precio']}\n")

def mostrar_menu():
    print("\n--- SISTEMA DE INVENTARIO ---")
    print("1. Agregar producto")
    print("2. Actualizar cantidad")
    print("3. Eliminar producto")
    print("4. Ver inventario")
    print("5. Salir")

def agregar_producto(inventario):
    nombre = input("Nombre del producto: ")
    cantidad = int(input("Cantidad: "))
    precio = float(input("Precio unitario: "))
    inventario[nombre] = {"cantidad": cantidad, "precio": precio}
    guardar_inventario(inventario)
    print("✅ Producto agregado.")

def actualizar_cantidad(inventario):
    nombre = input("Nombre del producto: ")
    if nombre in inventario:
        cantidad = int(input("Nueva cantidad: "))
        inventario[nombre]["cantidad"] = cantidad
        guardar_inventario(inventario)
        print("✅ Cantidad actualizada.")
    else:
        print("❌ Producto no encontrado.")

def eliminar_producto(inventario):
    nombre = input("Nombre del producto a eliminar: ")
    if nombre in inventario:
        del inventario[nombre]
        guardar_inventario(inventario)
        print("🗑️ Producto eliminado.")
    else:
        print("❌ Producto no encontrado.")

def ver_inventario(inventario):
    if inventario:
        print("\n--- INVENTARIO ---")
        total_valor = 0
        for nombre, datos in inventario.items():
            valor = datos["cantidad"] * datos["precio"]
            total_valor += valor
            print(f"{nombre} → Cantidad: {datos['cantidad']} | Precio: {datos['precio']} Bs | Valor: {valor} Bs")
        print(f"\n💰 Valor total del inventario: {total_valor} Bs")
    else:
        print("📭 Inventario vacío.")

inventario = cargar_inventario()

while True:
    mostrar_menu()
    opcion = input("Elige una opción: ")

    if opcion == "1":
        agregar_producto(inventario)
    elif opcion == "2":
        actualizar_cantidad(inventario)
    elif opcion == "3":
        eliminar_producto(inventario)
    elif opcion == "4":
        ver_inventario(inventario)
    elif opcion == "5":
        print("👋 Saliendo del sistema. ¡Hasta luego!")
        break
    else:
        print("⚠️ Opción no válida, intenta de nuevo.")
