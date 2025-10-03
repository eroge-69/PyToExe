import math
import io
import sys
from collections import defaultdict, Counter

# --- Constante del Tramo ---
LARGO_DE_TRAMO_ESTANDAR = 600.0  # cm 

# ==============================================================================
# 1. FUNCIONES DE ENTRADA Y LÓGICA DE CORTE
# ==============================================================================

def obtener_requerimientos():
    """
    Recoge múltiples órdenes de piezas, incluyendo el tipo de tubular.
    Retorna un diccionario de listas, agrupando las piezas por su tipo.
    """
    
    piezas_por_tipo = defaultdict(list)
    
    print("\n--- 🛠️ Calculadora de Tramos de Metal Optimizada y Lista de Corte ---")
    print(f"Cada tramo de metal estándar mide {LARGO_DE_TRAMO_ESTANDAR} cm.")
    
    orden_numero = 1
    while True:
        print(f"\n--- Orden de Corte #{orden_numero} ---")
        
        # 1. Solicitar Tipo de Tubular
        tipo_tubular = input("➡️ Escriba el TIPO de material (ej: Cuadrado 2x2, PTR 3x1, etc.): ").strip()
        if not tipo_tubular:
             print("⚠️ El tipo de material no puede estar vacío.")
             continue
        
        # 2. Solicitar Largo de Pieza (X)
        while True:
            try:
                largo_pieza_x = float(input(f"➡️ Largo de la pieza X (en cm): "))
                if largo_pieza_x <= 0:
                    print("⚠️ Error: El largo debe ser un número positivo.")
                    continue
                if largo_pieza_x > LARGO_DE_TRAMO_ESTANDAR:
                    print(f"\n❌ ¡Imposible Cortar! La pieza de {largo_pieza_x} cm es más larga que el tramo estándar.")
                    continue
                break
            except ValueError:
                print("⚠️ Entrada inválida. Por favor, ingrese un número para el largo.")
                
        # 3. Solicitar Cantidad de Piezas (Z)
        while True:
            try:
                numero_piezas_z = int(input("➡️ Cantidad total de piezas requeridas (Z): "))
                if numero_piezas_z <= 0:
                    print("⚠️ Error: Necesita al menos una pieza.")
                    continue
                break
            except ValueError:
                print("⚠️ Entrada inválida. Por favor, ingrese un número entero para la cantidad de piezas.")
        
        # 4. Agregar todas las piezas a la lista, agrupadas por su tipo
        for _ in range(numero_piezas_z):
            piezas_por_tipo[tipo_tubular].append(largo_pieza_x)
        
        # 5. Preguntar si desea continuar CON PROTECCIÓN
        while True:
            respuesta = input("\n¿Desea ingresar OTRA orden de corte? (s/n): ").lower().strip()
            
            if respuesta in ('s', 'si'):
                continuar = True
                break
            elif respuesta in ('n', 'no'):
                continuar = False
                break
            else:
                print("⚠️ Respuesta inválida. Por favor, escriba 's' para sí o 'n' para no.")
        
        if not continuar:
            break
            
        orden_numero += 1
            
    return piezas_por_tipo


def optimizar_corte(piezas_a_cortar):
    """
    Implementa FFD y retorna el detalle de cada tramo (sobrante y lista de cortes).
    """
    
    if not piezas_a_cortar:
        return 0, 0.0, 0, [] 
        
    piezas_a_cortar.sort(reverse=True)
    tramos_detalle = []  
    piezas_pendientes = list(piezas_a_cortar)
    
    while piezas_pendientes:
        pieza_actual = piezas_pendientes.pop(0)
        corte_encontrado = False
        
        for tramo in tramos_detalle:
            sobrante_actual = tramo['restante']
            
            if sobrante_actual >= pieza_actual - 0.001: 
                tramo['restante'] -= pieza_actual
                tramo['cortes'].append(pieza_actual)
                corte_encontrado = True
                break
        
        if not corte_encontrado:
            nuevo_tramo = {
                'restante': LARGO_DE_TRAMO_ESTANDAR - pieza_actual,
                'cortes': [pieza_actual]
            }
            tramos_detalle.append(nuevo_tramo)
            
    total_tramos_usados = len(tramos_detalle)
    total_desperdicio = sum(round(t.get('restante', 0), 2) for t in tramos_detalle)
    num_piezas = len(piezas_a_cortar)
    
    return total_tramos_usados, total_desperdicio, num_piezas, tramos_detalle


def formatear_cortes(lista_de_cortes):
    """
    Toma una lista de cortes [100.0, 100.0, 50.0] y la formatea como '2 x 100.0 cm + 1 x 50.0 cm'.
    """
    conteo = Counter(lista_de_cortes)
    medidas_ordenadas = sorted(conteo.keys(), reverse=True)
    
    cortes_formateados = []
    for medida in medidas_ordenadas:
        cantidad = conteo[medida]
        cortes_formateados.append(f"{cantidad} x {medida:.2f} cm")
        
    return " + ".join(cortes_formateados)

# ==============================================================================
# 2. FUNCIÓN DE SALIDA Y EXPORTACIÓN
# ==============================================================================

def generar_reporte(lista_de_piezas):
    """
    Genera el reporte completo (cálculos y lista de corte) y lo retorna como una cadena de texto.
    """
    
    output = io.StringIO()
    
    # Redirigir la salida temporalmente a StringIO para capturarla
    original_stdout = sys.stdout
    sys.stdout = output
    
    # ------------------------------------------------------------------------------------------------
    ## Ejecutar Cálculos y Generar Salida
    # ------------------------------------------------------------------------------------------------
    
    total_general_tramos = 0
    
    print(f"\n" + "=" * 70)
    print(f"| CALCULADORA DE CORTE OPTIMIZADA | TRAMO ESTÁNDAR: {LARGO_DE_TRAMO_ESTANDAR:.0f} cm |")
    print("=" * 70)
    print("\n--- 📋 LISTA DE CORTE Y CÁLCULO OPTIMIZADO POR TIPO DE MATERIAL ---")
    
    for tipo, piezas in lista_de_piezas.items():
        
        tramos_usados, desperdicio, num_piezas, detalle_tramos = optimizar_corte(piezas)
        total_general_tramos += tramos_usados
        
        print(f"\n🏷️ TIPO DE TUBULAR: **{tipo}**")
        print("-" * (18 + len(tipo)))
        print(f"  - Piezas totales a cortar: {num_piezas}")
        print(f"  - Tramos de {LARGO_DE_TRAMO_ESTANDAR:.0f} cm necesarios: **{tramos_usados}** tramos")
        print(f"  - Desperdicio total (Suma de sobrantes): {desperdicio:.2f} cm")
        
        # Mostrar la LISTA DE CORTE DETALLADA
        print("\n  **LISTA DE CORTE DETALLADA POR TRAMO:**")
        if not detalle_tramos:
            print("    * No se usaron tramos.")
        else:
            for i, tramo in enumerate(detalle_tramos):
                cortes_str = formatear_cortes(tramo['cortes'])
                sobrante_final = round(tramo['restante'], 2)
                
                print(f"    * Tramo #{i+1}:")
                print(f"        -> CORTAR: [{cortes_str}]")
                print(f"        -> SOBRANTE: {sobrante_final:.2f} cm")
        
        
    print("=" * 70)
    
    # Resumen Final Consolidado
    print("\n--- ✅ RESUMEN DE MATERIAL TOTAL REQUERIDO ---")
    print(f"Suma de tramos de *todos* los tipos de tubular:")
    print(f"**TOTAL GENERAL DE TRAMOS: {total_general_tramos} tramos**")
    print("-" * 50)
    
    # Restaurar la salida a la consola
    sys.stdout = original_stdout
    
    return output.getvalue()


def exportar_a_archivo(contenido):
    """
    Pregunta al usuario si desea exportar y guarda el contenido en un archivo de texto.
    """
    while True:
        respuesta = input("\n💾 ¿Desea exportar el cálculo a un archivo de texto? (s/n): ").lower().strip()
        
        if respuesta in ('s', 'si'):
            nombre_archivo = "lista_de_corte_optimizada.txt"
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    # Escribimos la cadena de texto completa capturada
                    f.write(contenido)
                print(f"\n🎉 ¡Éxito! El reporte se ha guardado en el archivo: **{nombre_archivo}**")
            except IOError:
                print(f"\n❌ Error al guardar el archivo. Verifique los permisos en el directorio.")
            break
            
        elif respuesta in ('n', 'no'):
            break
            
        else:
            print("⚠️ Respuesta inválida. Por favor, escriba 's' para sí o 'n' para no.")


# ==============================================================================
# 3. FUNCIÓN PRINCIPAL
# ==============================================================================

def iniciar_aplicacion():
    """Ejecuta el proceso completo: entrada, cálculo, muestra y exportación."""
    
    lista_de_piezas = obtener_requerimientos()
    
    if not lista_de_piezas:
        print("\nNo se ingresaron requerimientos.")
        print("\n👋 Gracias por usar la calculadora. ¡Adiós!")
        return

    # Generar el reporte completo (esto no lo imprime aún, solo lo captura)
    reporte_contenido = generar_reporte(lista_de_piezas)
    
    # Mostrar el reporte en la consola
    print(reporte_contenido)
    
    # Preguntar si desea exportar y realizar la exportación si es necesario
    exportar_a_archivo(reporte_contenido)
    
    print("\n👋 ¡Cortes listos! ¿Necesitas calcular el material para un nuevo proyecto?")

# Iniciar la aplicación
iniciar_aplicacion()