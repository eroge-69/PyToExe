from flask import Flask, redirect, render_template, request, jsonify, url_for
import pandas as pd
import os
import sys
import re

target_directory = os.path.abspath('calculos/')
sys.path.append(target_directory)

from calculoSuperiorCategoria import calcular_total_general


app = Flask(__name__)


#------------------CALCULO DE NÓMINAS------------------#
# Cargar CSV y categorías al iniciar la app
archivo_csv = './files/converted/7. TABLA SALARIAL VIGENTE.csv'
df = pd.read_csv(archivo_csv, sep=';', skiprows=3, decimal=',', skip_blank_lines=True)
df.columns = [col.strip() for col in df.columns]

# Limpieza específicos en columna salario base
df['SALARIO BASE (X12)'] = df['SALARIO BASE (X12)'].astype(str)\
    .str.replace('[€]', '', regex=True)\
    .str.replace(',', '.').str.strip()
df['SALARIO BASE (X12)'] = pd.to_numeric(df['SALARIO BASE (X12)'], errors='coerce')

def cargar_categorias():
    categorias = df['NIVELES LABORALES'].dropna().unique().tolist()
    categorias = [cat.strip() for cat in categorias if cat.strip() != '']
    return categorias

categorias = cargar_categorias()

@app.route('/calculo-de-nominas')
def calculo_nominas():
    return render_template('calculo_nominas.html', categorias=categorias)

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    resultado = calcular_total_general(
        data['categoria_inferior'],
        data['categoria_superior'],
        float(data['dias_trabajados']),
        float(data['dias_mes']),
        int(data['trienios']),
        float(data['porc_inferior']),
        float(data['porc_superior'])
    )
    return jsonify(resultado)

#------------------INCIDENCIAS------------------#
#------------------CARGA DE DATOS------------------#
# Cargar incidencias
archivo_incidencias = './files/converted/4. RESUMEN INCIDENCIAS (volcado de variables recibidas en pdf).csv'
df_incidencias = pd.read_csv(archivo_incidencias, sep=';', skiprows=0)
df_incidencias.columns = [col.strip() for col in df_incidencias.columns]

# Filtrar filas que no tengan trabajador
df_incidencias = df_incidencias[df_incidencias['TRABAJADOR/A'].notna()]

# Carga complementos salariales con limpieza especial
archivo_complementos = './files/converted/6. Complementos salariales VARIABLES.csv'
df_complementos = pd.read_csv(archivo_complementos, sep=';', skiprows=2, names=['plus', 'importe'])

#------------------CARGA COMPLEMENTOS Y LIMPIEZA------------------#

# Limpiar y normalizar nombres de plus
df_complementos['plus'] = df_complementos['plus'].str.strip().str.upper()

# Función para limpiar importes
def limpiar_importe(valor):
    if pd.isna(valor):
        return 0.0
    valor_str = str(valor)
    # Tomamos solo los números y reemplazamos ',' por '.'
    match = re.search(r'[\d,.]+', valor_str)
    if not match:
        return 0.0
    num_str = match.group(0).replace(',', '.')
    try:
        return float(num_str)
    except:
        return 0.0

# Aplicar limpieza
df_complementos['importe'] = df_complementos['importe'].apply(limpiar_importe)

# Diccionario limpio
complementos_dict_clean = {k.strip().upper(): v for k, v in zip(df_complementos['plus'], df_complementos['importe'])}

#------------------MAPEO INCIDENCIAS -> COMPLEMENTOS------------------#
# Esto asegura que cada cabecera del CSV de incidencias encuentre el plus correcto
MAPA_INCIDENCIAS_COMPLEMENTOS = {
    "QUEBRANTO DE MONEDA (PROPORCIONAL EN VACACIONES)": "QUEBRANTO DE MONEDA",
    "PLUS DE NOCTURNIDAD": "NOCTURNIDAD",
    "KILOMETRAJE": "KILOMETRAJE",
    "DIF. SALARIAL TRABAJOS SUPERIOR CATEGORÍA": "DIF. SALARIAL TRABAJOS SUPERIOR CATEGORÍA",
    "PLUS DE CONECTIVIDAD": "CONECTIVIDAD MOXSI",
    "PLUS DE GUARDIA/ OTROS": "GUARDIAS EVENTOS - IDENTIDAD Y CLIENTES"
}


# Función para obtener el valor unitario correcto de cada incidencia

def obtener_valor_unitario(plus):
    plus_upper = plus.strip().upper()
    # buscar en el mapa
    clave_complemento = MAPA_INCIDENCIAS_COMPLEMENTOS.get(plus_upper, plus_upper)
    return complementos_dict_clean.get(clave_complemento, 0.0)


#------------------FUNCIÓN DE CÁLCULO------------------#
def calcular_importes(incidencias):
    resultados = {}
    total = 0.0

    for plus, cantidad in incidencias.items():

        if plus == 'TRABAJADOR/A':
            continue

        if pd.isna(cantidad):
            cantidad = 0

        clave = plus.strip().upper()
        complemento = MAPA_INCIDENCIAS_COMPLEMENTOS.get(plus, plus)

        # Caso DIF. SALARIAL
        if clave == 'DIF. SALARIAL TRABAJOS SUPERIOR CATEGORÍA':
            unitario = 1
            total_plus = float(cantidad)
            resultados[plus] = {'unitario': round(unitario, 2), 'total': round(total_plus, 2)}

        # Caso FESTIVOS
        elif clave == 'FESTIVOS':
            cant_normal = float(incidencias.get('NORMAL', 0))
            cant_especial = float(incidencias.get('ESPECIAL', 0))
            unitario_normal = complementos_dict_clean.get('NORMAL', 0)
            unitario_especial = complementos_dict_clean.get('ESPECIAL', 0)

            total_normal = cant_normal * unitario_normal
            total_especial = cant_especial * unitario_especial
            total_plus = total_normal + total_especial

            resultados['NORMAL'] = {'unitario': round(unitario_normal, 2), 'total': round(total_normal, 2)}
            resultados['ESPECIAL'] = {'unitario': round(unitario_especial, 2), 'total': round(total_especial, 2)}
            resultados[plus] = {'unitario': '-', 'total': round(total_plus, 2)}  # '-' indica que no tiene unitario único

        # Caso QUEBRANTO DE MONEDA
        elif clave == 'QUEBRANTO DE MONEDA (PROPORCIONAL EN VACACIONES)':
            unitario = complementos_dict_clean.get("QUEBRANTO DE MONEDA", 0)
            total_plus = float(cantidad) * unitario
            resultados[plus] = {'unitario': round(unitario, 2), 'total': round(total_plus, 2)}

        # Resto de pluses
        else:
            unitario = complementos_dict_clean.get(complemento.upper(), 0)
            total_plus = float(cantidad) * unitario
            resultados[plus] = {'unitario': round(unitario, 2), 'total': round(total_plus, 2)}

        total += total_plus

    resultados['TOTAL'] = round(total, 2)
    return resultados

def calcular_importes(incidencias):
    resultados = {}
    total = 0.0
    
    for plus, valor_monetario in incidencias.items():
        if plus == 'TRABAJADOR/A':
            continue

        if pd.isna(valor_monetario):
            valor_monetario = 0.0

        clave = plus.strip().upper()
        complemento = MAPA_INCIDENCIAS_COMPLEMENTOS.get(plus, plus)

        # Caso DIF. SALARIAL
        if clave == 'DIF. SALARIAL TRABAJOS SUPERIOR CATEGORÍA':
            unitario = 1
            cantidad = float(valor_monetario)
            total_plus = cantidad
            resultados[plus] = {'unitario': round(unitario, 2),
                                'total': round(total_plus, 2),
                                'cantidad': round(cantidad, 2)}

        elif clave == 'FESTIVOS':
            # Mantener cantidad monetaria como antes
            cant_normal = float(incidencias.get('NORMAL', 0))
            cant_especial = float(incidencias.get('ESPECIAL', 0))
            unitario_normal = complementos_dict_clean.get('NORMAL', 0)
            unitario_especial = complementos_dict_clean.get('ESPECIAL', 0)
            total_plus = cant_normal * unitario_normal + cant_especial * unitario_especial

            resultados['NORMAL'] = {'unitario': round(unitario_normal, 2),
                                    'total': round(cant_normal * unitario_normal, 2),
                                    'cantidad': cant_normal}
            resultados['ESPECIAL'] = {'unitario': round(unitario_especial, 2),
                                      'total': round(cant_especial * unitario_especial, 2),
                                      'cantidad': cant_especial}
            resultados[plus] = {'unitario': 1, 'total': round(total_plus, 2), 'cantidad': 1}
        
        elif clave.startswith('QUEBRANTO DE MONEDA'):
            unitario = complementos_dict_clean.get('QUEBRANTO DE MONEDA', 0)
            cantidad = float(valor_monetario) / unitario if unitario else 0
            total_plus = cantidad * unitario
            resultados[plus] = {'unitario': round(unitario, 2),
                                'total': round(total_plus, 2),
                                'cantidad': round(cantidad, 2)}
        else:
            unitario = complementos_dict_clean.get(complemento.upper(), 0)
            cantidad = float(valor_monetario) / unitario if unitario else 0
            total_plus = cantidad * unitario
            resultados[plus] = {'unitario': round(unitario, 2),
                                'total': round(total_plus, 2),
                                'cantidad': round(cantidad, 2)}

        total += total_plus

    resultados['TOTAL'] = round(total, 2)
    return resultados


def convertir_a_cantidad(incidencias_monetario, importes):
    """
    Convierte los valores monetarios del CSV en 'cantidades' para el formulario,
    haciendo cantidad = total / unitario. No afecta a FESTIVOS (se deja como está).
    
    incidencias_monetario: dict con valores monetarios del CSV
    importes: dict con estructura {'PLUS': {'unitario': X, 'total': Y}}
    """
    incidencias_cantidad = {}
    
    for plus, datos in importes.items():
        if plus == 'TRABAJADOR/A':
            continue

        if plus == 'TOTAL':
            continue

        # FESTIVOS no se convierte
        if plus == 'FESTIVOS':
            incidencias_cantidad[plus] = incidencias_monetario.get(plus, 0)
            continue

        unitario = datos.get('unitario', 0)
        total = incidencias_monetario.get(plus, 0)
        
        if unitario != 0:
            cantidad = float(total) / float(unitario)
        else:
            cantidad = 0  # prevenir división por cero
        
        incidencias_cantidad[plus] = round(cantidad, 4)  # redondeo para inputs

    return incidencias_cantidad

#------------------RUTA FLASK------------------#
@app.route('/incidencias', methods=['GET'])
def mostrar_incidencias():
    # Filtrar filas que no empiezan con "ÁREA"
    df_filtrado = df_incidencias[~df_incidencias['TRABAJADOR/A'].str.startswith('ÁREA')]

    # Extraer áreas distintas desde filas que empiezan con "ÁREA"
    areas = df_incidencias[df_incidencias['TRABAJADOR/A'].str.startswith('ÁREA')]['TRABAJADOR/A'].unique().tolist()

    area_seleccionada = request.args.get('area')

    if area_seleccionada:
        idx_area = df_incidencias[df_incidencias['TRABAJADOR/A'] == area_seleccionada].index[0]
        idx_siguientes_area = df_incidencias[df_incidencias['TRABAJADOR/A'].str.startswith('ÁREA') & (df_incidencias.index > idx_area)]
        idx_fin = idx_siguientes_area.index.min() if not idx_siguientes_area.empty else df_incidencias.index.max() + 1

        empleados_area = df_incidencias.loc[idx_area+1:idx_fin-1]
        empleados_area = empleados_area[~empleados_area['TRABAJADOR/A'].str.startswith('ÁREA')]
        empleados_area_list = empleados_area['TRABAJADOR/A'].dropna().unique().tolist()
    else:
        empleados_area_list = []

    empleado_seleccionado = request.args.get('empleado')
    incidencias = {}
    importes = {}
    if empleado_seleccionado:
        fila = df_incidencias[df_incidencias['TRABAJADOR/A'] == empleado_seleccionado]
        if not fila.empty:
            fila_dict = fila.iloc[0].to_dict()
            # Calcular importes monetarios usando complementos y reglas especiales
            importes = calcular_importes(fila_dict)
            # Convertir monetario a cantidad para el formulario
            incidencias = convertir_a_cantidad(fila_dict, importes)

    return render_template('editar_incidencias.html',
                           areas=areas,
                           area=area_seleccionada,
                           empleados=empleados_area_list,
                           empleado=empleado_seleccionado,
                           incidencias=incidencias,
                           importes=importes,
                           complementos_dict=complementos_dict_clean)

@app.route('/incidencias/update', methods=['POST'])
def actualizar_incidencias():
    global df_incidencias
    empleado = request.form.get('empleado')
    if not empleado:
        return redirect(url_for('mostrar_incidencias'))

    idx = df_incidencias[df_incidencias['TRABAJADOR/A'] == empleado].index
    if idx.empty:
        return redirect(url_for('mostrar_incidencias'))

    idx = idx[0]

    # Calcular importes actuales en memoria para referencia
    fila_incidencias = df_incidencias.loc[idx].to_dict()
    # Extraer solo columnas de incidencias (numéricas) para el cálculo
    fila_incidencias = df_incidencias.loc[idx].drop(labels=['TRABAJADOR/A']).to_dict()
    importes = calcular_importes(fila_incidencias)  # tu función de cálculo de importes

    for col in df_incidencias.columns:
        if col == 'TRABAJADOR/A':
            continue

        col_upper = col.strip().upper()
        cantidad_str = request.form.get(col, '0').replace(',', '.')
        try:
            cantidad = float(cantidad_str) if cantidad_str else 0.0
        except ValueError:
            cantidad = 0.0

        # -----------------------------
        # Guardar valor monetario
        # -----------------------------
        if col_upper == 'DIF. SALARIAL TRABAJOS SUPERIOR CATEGORÍA':
            # valor monetario directo desde el popup
            valor_guardar = cantidad
        elif col_upper == 'FESTIVOS':
            # total monetario de FESTIVOS calculado en importes (normal + especial)
            valor_guardar = importes.get('FESTIVOS', {}).get('total', 0.0)
        else:
            # corregir nombres según mapa de complementos
            clave_complemento = MAPA_INCIDENCIAS_COMPLEMENTOS.get(col_upper, col_upper)
            unitario = complementos_dict_clean.get(clave_complemento, 0.0)
            valor_guardar = cantidad * unitario

        # Guardar en el dataframe redondeado a 2 decimales
        df_incidencias.at[idx, col] = round(valor_guardar, 2)

    # Guardar cambios en CSV
    df_incidencias.to_csv(archivo_incidencias, sep=';', index=False)

    # Redirigir mostrando la persona actualizada
    return redirect(url_for('mostrar_incidencias'))

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
