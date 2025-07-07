# precio_sin_iva.py

def calcular_precio_sin_iva():
    print("💰 CALCULADORA DE PRECIO SIN IVA")
    print("--------------------------------")
    try:
        precio_con_iva = float(input("👉 Ingresá el precio de venta CON IVA incluido: $"))
        precio_sin_iva = precio_con_iva / 1.21
        print(f"\n✅ Precio SIN IVA para cargar en el sistema: ${precio_sin_iva:.2f}")
        input("\nPresioná Enter para salir...")
    except ValueError:
        print("❌ Por favor, ingresá un número válido.")
        input("\nPresioná Enter para salir...")

calcular_precio_sin_iva()