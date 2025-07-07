
def calcular_precio_sin_iva(precio_con_iva):
    return precio_con_iva / 1.21

def calcular_precio_con_iva(precio_sin_iva):
    return precio_sin_iva * 1.21

def main():
    while True:
        print("\n💰 CALCULADORA DE PRECIOS CON Y SIN IVA")
        print("---------------------------------------")
        print("1. Calcular PRECIO SIN IVA (desde precio CON IVA)")
        print("2. Calcular PRECIO CON IVA (desde precio SIN IVA)")
        print("3. Salir")

        opcion = input("\nElegí una opción (1-3): ")

        if opcion == "1":
            try:
                precio = float(input("\n👉 Ingresá el precio CON IVA: $"))
                resultado = calcular_precio_sin_iva(precio)
                print(f"✅ Precio SIN IVA: ${resultado:.2f}")
            except ValueError:
                print("❌ Por favor, ingresá un número válido.")

        elif opcion == "2":
            try:
                precio = float(input("\n👉 Ingresá el precio SIN IVA: $"))
                resultado = calcular_precio_con_iva(precio)
                print(f"✅ Precio CON IVA: ${resultado:.2f}")
            except ValueError:
                print("❌ Por favor, ingresá un número válido.")

        elif opcion == "3":
            print("\n👋 ¡Hasta luego!")
            break

        else:
            print("⚠️ Opción inválida. Probá de nuevo.")

        input("\nPresioná Enter para continuar...")

if __name__ == "__main__":
    main()
