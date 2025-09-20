from datetime import date, timedelta, datetime
from itertools import permutations

def obtener_combinaciones_fecha(dia, mes):
    """
    Calcula el número, la suma de dígitos y las combinaciones para una fecha.
    """
    numero = dia + mes
    suma = sum(int(d) for d in str(numero))
    
    digitos_numero = list(str(numero))
    digitos_suma = [str(suma)[-1]] if suma >= 10 else list(str(suma))
    
    digitos = digitos_numero + digitos_suma
    combinaciones = sorted({f"{a}{b}" for a, b in permutations(digitos, 2)})[:6]
    
    return {
        "dia": dia,
        "mes": mes,
        "numero": numero,
        "suma": suma,
        "combinaciones": combinaciones
    }

def solicitar_fecha_usuario():
    """Solicita una fecha al usuario y la valida."""
    while True:
        fecha_str = input("Ingrese la fecha (DD/MM/AAAA): ").strip()
        try:
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            return fecha_obj
        except ValueError:
            print("❌ Formato de fecha inválido. Por favor, use DD/MM/AAAA.")

def mostrar_resultados_dia(fecha, datos):
    """Función para imprimir los resultados de un solo día."""
    print(f"📅 Fecha: {fecha.strftime('%d/%m/%Y')}")
    print(f"🔢 {datos['dia']} + {datos['mes']} = {datos['numero']}")
    print(f"➕ {datos['numero']} → {datos['suma']}")
    print("🌈 Combinaciones:")
    for i, combo in enumerate(datos['combinaciones'], 1):
        print(f"   {i}. {combo}")

def mostrar_resultados_tres_dias():
    """Genera y muestra los datos para tres días adyacentes."""
    hoy = date.today()
    mes_actual = hoy.month
    
    print("🔍 Días adyacentes:")
    print("-" * 30)
    
    for offset in [-1, 0, 1]:
        fecha = hoy + timedelta(days=offset)
        if fecha.month == mes_actual:
            datos = obtener_combinaciones_fecha(fecha.day, mes_actual)
            print(f"\n{fecha.strftime('%d/%m')}: {datos['dia']}+{datos['mes']}={datos['numero']}→{datos['suma']}")
            for i, combo in enumerate(datos['combinaciones'], 1):
                print(f"   {i}. {combo}")

def menu():
    """Maneja el menú principal de la aplicación."""
    print("=" * 40)
    print("🎰 GENERADOR DE COMBINACIONES")
    print("=" * 40)
    print("1 - Solo hoy")
    print("2 - 3 días (ayer, hoy, mañana)")
    print("3 - Ingresar fecha")
    print("=" * 40)
    
    try:
        opcion = input("Seleccione una opción (1/2/3): ").strip()
        print()
        
        if opcion == "1":
            hoy = date.today()
            datos = obtener_combinaciones_fecha(hoy.day, hoy.month)
            mostrar_resultados_dia(hoy, datos)
        elif opcion == "2":
            mostrar_resultados_tres_dias()
        elif opcion == "3":
            fecha_elegida = solicitar_fecha_usuario()
            datos = obtener_combinaciones_fecha(fecha_elegida.day, fecha_elegida.month)
            mostrar_resultados_dia(fecha_elegida, datos)
        else:
            print("❌ Opción inválida.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    menu()
    print("\n✅ ¡Listo!")