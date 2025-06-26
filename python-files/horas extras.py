import json
from datetime import datetime
import os

# Nombre del archivo para guardar los datos
ARCHIVO_DATOS = 'horas_extras.json'

def cargar_datos():
    """Carga los registros existentes desde el archivo JSON"""
    try:
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, 'r') as f:
                return json.load(f)
    except json.JSONDecodeError:
        print("Error al leer el archivo de datos. Se creará uno nuevo.")
    return []

def guardar_datos(datos):
    """Guarda los registros en el archivo JSON"""
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n--- Sistema de Registro de Horas Extras ---")
    print("1. Registrar horas extras")
    print("2. Ver resumen de horas")
    print("3. Borrar todos los registros")
    print("4. Salir")

def registrar_horas(registros):
    """Registra nuevas horas extras con fecha actual"""
    try:
        horas = float(input("Ingrese la cantidad de horas extras trabajadas: "))
        fecha = datetime.now().strftime("%Y-%m-%d")  # Formato: AAAA-MM-DD
        registro = {"fecha": fecha, "horas": horas}
        registros.append(registro)
        guardar_datos(registros)
        print(f"Registro guardado: {horas} horas el {fecha}")
    except ValueError:
        print("Error: Debe ingresar un número válido para las horas")

def mostrar_resumen(registros):
    """Muestra el resumen de horas por día y el total"""
    if not registros:
        print("\nNo hay registros de horas extras")
        return
    
    print("\n--- Resumen de Horas Extras ---")
    
    # Agrupar horas por fecha
    resumen = {}
    for registro in registros:
        fecha = registro["fecha"]
        if fecha in resumen:
            resumen[fecha] += registro["horas"]
        else:
            resumen[fecha] = registro["horas"]
    
    # Mostrar resultados
    total = 0
    for fecha, horas in sorted(resumen.items()):
        print(f"Fecha: {fecha} - Horas: {horas:.2f}")
        total += horas
    
    print(f"\nTotal acumulado: {total:.2f} horas")

def borrar_registros():
    """Borra todos los registros existentes"""
    confirmacion = input("¿Está seguro que desea borrar TODOS los registros? (s/n): ")
    if confirmacion.lower() == 's':
        guardar_datos([])
        print("Todos los registros han sido eliminados.")

def main():
    """Función principal del programa"""
    registros = cargar_datos()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            registrar_horas(registros)
            registros = cargar_datos()  # Recargar datos
        elif opcion == "2":
            mostrar_resumen(registros)
        elif opcion == "3":
            borrar_registros()
            registros = cargar_datos()  # Recargar datos
        elif opcion == "4":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()
