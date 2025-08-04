import calendar
from datetime import date, datetime

def generar_cuadrante(mes, año, nombres, festivos=[], ausencias={}):
    nombre_mes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][mes-1]
    _, dias_mes = calendar.monthrange(año, mes)

    calendario = []
    semana_actual = [0] * 7
    primer_dia = date(año, mes, 1).weekday()
    dia = 1
    for i in range(primer_dia, 7):
        semana_actual[i] = dia
        dia += 1
    calendario.append(semana_actual)
    while dia <= dias_mes:
        semana_actual = [0] * 7
        for i in range(7):
            if dia <= dias_mes:
                semana_actual[i] = dia
                dia += 1
        calendario.append(semana_actual)

    def trabajador_presente(i, dia_actual):
        if i in ausencias:
            _, inicio, fin = ausencias[i]
            if inicio and dia_actual < inicio:
                return False
            if fin and dia_actual > fin:
                return False
        return True

    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html>')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append(f'<title>Cuadrante Servicio Cementerio {nombre_mes} {año}</title>')
    html.append('<style>')
    html.append('table { border-collapse: collapse; width: 100%; }')
    html.append('th, td { border: 1px solid black; padding: 8px; text-align: center; }')
    html.append('th { background-color: #f2f2f2; }')
    html.append('.domingo { background-color: #FF0000; }')
    html.append('.festivo { background-color: #FF0000; }')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    html.append(f'<h1>Cuadrante Servicio Cementerio {nombre_mes.upper()} {año}</h1>')
    html.append('<table>')

    html.append('<tr>')
    for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
        html.append(f'<th>{dia}</th>')
    html.append('</tr>')

    trabajadores = nombres.copy()
    semana_anterior = nombres.copy()
    rotacion = 0

    for semana in calendario:
        html.append('<tr>')
        for i, dia_num in enumerate(semana):
            if dia_num == 0:
                html.append('<td></td>')
                continue
            clases = []
            if i == 6:
                clases.append('domingo')
                texto_dia = f'Domingo {dia_num}'
            else:
                texto_dia = str(dia_num)
            if dia_num in festivos:
                clases.append('festivo')
            clase_str = ' class="' + ' '.join(clases) + '"' if clases else ''
            html.append(f'<td{clase_str}><strong>{texto_dia}</strong></td>')
        html.append('</tr>')

        html.append('<tr>')
        for i, dia_num in enumerate(semana):
            if dia_num == 0:
                html.append('<td></td>')
                continue
            es_festivo = dia_num in festivos
            es_fin_semana = i >= 5
            es_lunes = i == 0

            trabajadores_actuales = []
            for idx, nombre in enumerate(trabajadores):
                if nombre and trabajador_presente(idx, dia_num):
                    trabajadores_actuales.append((idx, nombre))

            if es_fin_semana or es_festivo:
                turno = trabajadores_actuales[0][1] if trabajadores_actuales else ""
            elif es_lunes:
                if semana_anterior:
                    trabajador_descansa = semana_anterior[0]
                    turno = "<br>".join([n for (j, n) in trabajadores_actuales if n != trabajador_descansa])
                else:
                    turno = "<br>".join([n for (_, n) in trabajadores_actuales])
            else:
                turno = "<br>".join([n for (_, n) in trabajadores_actuales])

            html.append(f'<td>{turno}</td>')
        html.append('</tr>')

        html.append('<tr>')
        for _ in range(7):
            html.append('<td style="border: none; height: 20px;"></td>')
        html.append('</tr>')

        semana_anterior = trabajadores.copy()
        if rotacion % 3 == 0:
            trabajadores = [nombres[2], nombres[0], nombres[1]]
        elif rotacion % 3 == 1:
            trabajadores = [nombres[1], nombres[2], nombres[0]]
        else:
            trabajadores = nombres.copy()
        rotacion += 1

    html.append('</table>')
    html.append('</body>')
    html.append('</html>')

    return "\n".join(html)

def parse_fecha(texto):
    if texto.strip() == "":
        return None
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").day
    except:
        return None

def main():
    print("=" * 60)
    print("GENERADOR DE CUADRANTE DE SERVICIO - CEMENTERIO")
    print("=" * 60)

    mes = int(input("\nMes (1-12): "))
    año = int(input("Año: "))

    nombres = []
    ausencias = {}

    for i in range(3):
        nombre = input(f"\nNombre del {'primer' if i == 0 else 'segundo' if i == 1 else 'tercer'} trabajador: ").strip()
        if nombre == "":
            nombres.append("")
            continue

        print(f"Indique periodo de ausencia para {nombre} (en formato DD/MM/AAAA):")
        fecha_ini = input("  Fecha de inicio (dejar en blanco si no hay ausencia): ")
        fecha_fin = input("  Fecha de fin (dejar en blanco si ausencia es indefinida): ")

        inicio = parse_fecha(fecha_ini)
        fin = parse_fecha(fecha_fin)

        nombres.append(nombre)
        if inicio or fin:
            ausencias[i] = (nombre, inicio, fin)

    festivos_input = input("\nDías festivos (separados por comas, ej. 1,15,20): ")
    festivos = [int(d.strip()) for d in festivos_input.split(",") if d.strip().isdigit()] if festivos_input else []

    html = generar_cuadrante(mes, año, nombres, festivos, ausencias)

    archivo = f"Cuadrante_Servicio_Cementerio_{mes:02d}_{año}.html"
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(html)

    print("\n" + "=" * 80)
    print(f"✅ Cuadrante generado exitosamente: {archivo}")
    print("=" * 80)
    print("\nINSTRUCCIONES:")
    print(f"1. Abre el archivo {archivo} en tu navegador.")
    print("2. Para usar en Word:")
    print("   a. Abre Word, ve a 'Archivo' > 'Abrir'")
    print("   b. Selecciona el archivo HTML")
    print("   c. Word lo convertirá automáticamente a tabla")
    print("   d. Guarda como DOCX si lo deseas")

if __name__ == "__main__":
    main()
