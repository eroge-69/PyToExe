import sys
import requests
import pickle
import os
from colorama import init, Fore, Back

# Inicializar colorama
init()

# Archivo de datos
archivo_datos = "almacenado.dat"

# Cargar datos si existen
if os.path.exists(archivo_datos):
    with open(archivo_datos, "rb") as archivo:
        almacenado = pickle.load(archivo)
else:
    almacenado = {}

# Obtener precio del dólar desde API
url = "https://pydolarve.org/api/v1/dollar?page=bcv&monitor=usd"
response = requests.get(url)
price = None

if response.status_code == 200:
    data = response.json()
    price = data.get("price")
    if price:
        print(Fore.GREEN + f"{' '*64}$: {price}")
    else:
        print("No se encontró el valor de 'price'")
else:
    print(f"Error al obtener datos de la API ({response.status_code})")
    sys.exit()

# Menú principal
def mostrar_menu():
    print(Fore.YELLOW + Back.YELLOW + "-"*90 + Back.RESET)
    print(Fore.WHITE + Back.BLUE + "                           B I E N V E N I D O                       " + Back.RESET)
    print(Fore.RED + Back.RED + "-"*90 + Back.RESET)
    print(Fore.GREEN + """
   MENU DE OPCIONES:
  1. Crear una lista de productos
  2. Consultar una lista de productos ya existente
  3. Consultar un precio rápidamente
  4. Salir del programa
""")

def guardar_datos():
    with open(archivo_datos, "wb") as archivo:
        pickle.dump(almacenado, archivo)

while True:
    mostrar_menu()
    try:
        opcion = int(input(Fore.GREEN + "Escoja una opción: "))
    except ValueError:
        print(Fore.RED + "Por favor, ingrese un número válido.")
        continue

    if opcion == 1:
        productos = {}
        for _ in range(10):
            nombre = input("Nombre del producto: ")
            try:
                valor_dolar = float(input("Precio en $: "))
            except ValueError:
                print("Valor inválido.")
                continue
            productos[nombre] = valor_dolar * price
        almacenado.update(productos)
        guardar_datos()
        print(Fore.GREEN + "Productos guardados:", productos)

    elif opcion == 2:
        if almacenado:
            print(Fore.CYAN + "Lista de productos:")
            for producto, valor in almacenado.items():
                print(f"{producto}: Bs {valor:.2f}")
        else:
            print(Fore.RED + "No hay productos almacenados.")

    elif opcion == 3:
        try:
            valor = float(input("Ingrese el precio en $: "))
            print(Fore.GREEN + f"Precio en Bs: {valor * price:.2f}")
        except ValueError:
            print("Valor inválido.")

    elif opcion == 4:
        print(Fore.GREEN + "Saliendo del programa...")
        break

    else:
        print(Fore.RED + "Opción no válida.")
