import os
import calendar

def crear_carpetas_por_mes(anio, mes, ruta_base="."):
    # Obtener cantidad de días del mes
    _, num_dias = calendar.monthrange(anio, mes)
    
    for dia in range(1, num_dias + 1):
        nombre_carpeta = f"{anio:04d}-{mes:02d}-{dia:02d}"
        ruta_completa = os.path.join(ruta_base, nombre_carpeta)
        os.makedirs(ruta_completa, exist_ok=True)
        print(f"Creada carpeta: {ruta_completa}")

if __name__ == "__main__":
    # 🔧 Cambia aquí el año, mes y ruta donde se crean las carpetas
    anio = 2025
    mes = 9
    ruta_destino = "./Fechas"  

    os.makedirs(ruta_destino, exist_ok=True)
    crear_carpetas_por_mes(anio, mes, ruta_destino)
    print("✅ Todas las carpetas fueron creadas.")
