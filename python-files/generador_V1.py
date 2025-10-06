import pandas as pd
import os
import re
import sys

# --- Funciones Auxiliares ---

def _obtener_metadata_y_columnas(csv_plantilla_path, template_name):
    """
    Extrae las líneas de metadatos, los encabezados de columna y los valores por defecto 
    de la primera fila de datos del CSV de la plantilla.
    """
    
    metadata_lines = []
    encabezado_linea_idx = -1
    
    try:
        # 1. Lectura de líneas (Manejo de codificación tolerante)
        try:
            with open(csv_plantilla_path, 'r', encoding='utf-8-sig') as f:
                lineas = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(csv_plantilla_path, 'r', encoding='utf-16') as f:
                    lineas = f.readlines()
            except UnicodeDecodeError:
                with open(csv_plantilla_path, 'r', encoding='latin-1') as f:
                    lineas = f.readlines()
        
        # 2. Buscar el encabezado y capturar metadata
        for i, line in enumerate(lineas):
            linea_limpia = line.strip()
            
            if linea_limpia.lower().startswith(':tagname'):
                encabezado_linea_idx = i
                break
            
            if linea_limpia:
                if linea_limpia.lower().startswith(':template'):
                    metadata_lines.append(f':TEMPLATE=${template_name}')
                else: 
                    metadata_lines.append(linea_limpia)

        if encabezado_linea_idx == -1:
            raise ValueError(f"No se encontró la línea de encabezado ':Tagname' en la plantilla.")

        # 3. EXTRACCIÓN DE COLUMNAS
        header_line = lineas[encabezado_linea_idx].strip()
        if header_line.startswith(':'):
            header_line = header_line[1:]
            
        columnas_plantilla_original = [col.strip() for col in header_line.split(',')]
        columnas_plantilla_original = [col for col in columnas_plantilla_original if col]
        
        # 4. EXTRACCIÓN DE VALORES POR DEFECTO (Copia la primera fila de datos)
        # FIX CLAVE: Forzar dtype=str y keep_default_na=False para que los campos vacíos
        # como Container/ContainedName se lean como "" y no como 'nan' de Pandas.
        try:
            df_template = pd.read_csv(
                csv_plantilla_path,
                encoding='utf-16',
                sep=',',
                skiprows=encabezado_linea_idx + 1,
                header=None,
                nrows=1,
                dtype=str,              # Forzar la lectura como string
                keep_default_na=False   # No convertir celdas vacías a NaN
            )
        except Exception:
             # Segundo intento de lectura con otra codificación
            df_template = pd.read_csv(
                csv_plantilla_path,
                encoding='latin-1',
                sep=',',
                skiprows=encabezado_linea_idx + 1,
                header=None,
                nrows=1,
                dtype=str,              # Forzar la lectura como string
                keep_default_na=False   # No convertir celdas vacías a NaN
            )

        default_values_map = {}
        if not df_template.empty and len(df_template.columns) >= len(columnas_plantilla_original):
            # Aseguramos que se traten como strings y rellenamos cualquier posible NaN restante con ''
            default_row = df_template.iloc[0].fillna('')
            for i, col in enumerate(columnas_plantilla_original):
                # El valor ya es cadena gracias al dtype=str y fillna('')
                default_values_map[col] = str(default_row[i])
        else:
            print("  ⚠️ Advertencia: No se pudo leer la fila de valores por defecto de la plantilla. Usando cadena vacía para todo.")
            default_values_map = {col: '' for col in columnas_plantilla_original}
            
        # Aseguramos que Tagname se inicialice como vacío para poner el nombre de la instancia
        if 'Tagname' in default_values_map:
            default_values_map['Tagname'] = '' 

        return metadata_lines, columnas_plantilla_original, default_values_map
        
    except FileNotFoundError:
        print(f"  ⚠️ Error: Plantilla no encontrada en {csv_plantilla_path}. Asegúrese de que existe.")
        return None, None, None
    except Exception as e:
        print(f"  ❌ Error al procesar la plantilla '{template_name}': {e}", file=sys.stderr)
        return None, None, None

def _crear_dataframe_instancias(template_name, df_subdata, columnas_plantilla, default_values_map):
    """
    Mapea los datos de entrada a las columnas de la plantilla de salida, 
    usando los valores por defecto de la plantilla.
    """
    
    # 1. Identificar el prefijo principal (ej: 'boolean')
    prefijo_principal = None
    for col in columnas_plantilla:
        m = re.match(r"^([a-zA-Z0-9_]+)\..*$", col, re.IGNORECASE)
        if m:
            p = m.group(1).lower()
            if p not in ("tagname", "area", "securitygroup", "container", "containedname", "aliasname", "shortdesc", "udas", "extensions", "cmddata", "userattrdata"):
                prefijo_principal = p
                break
    
    if not prefijo_principal:
        print(f"  ⚠️ Advertencia: No se pudo determinar el prefijo principal (ej: 'boolean') para {template_name}. Mapeo solo a columnas globales.")

    nuevas_filas = []

    # Se agrupa por la columna 'instancia' (ya limpia)
    for inst_name, df_inst in df_subdata.groupby('instancia', sort=False):
        
        # 🟢 Inicializar la fila con los valores por defecto del TEMPLATE (incluye XML, None, etc.)
        nueva_fila = pd.Series(default_values_map) 
        
        # Obtenemos los datos de la primera fila de la instancia. Las claves ya están limpias.
        row_datos_limpios = df_inst.iloc[0].to_dict()
        
        # 🟢 1. Sobrescribir el Tagname con el nombre de la instancia real
        if 'Tagname' in columnas_plantilla:
            nueva_fila['Tagname'] = inst_name

        for col_plantilla in columnas_plantilla:
            col_limpia = col_plantilla.lower().strip()
            
            # --- 2. Columnas Globales (Ej: Area, SecurityGroup, Container, ContainedName, AliasName, ShortDesc) ---
            # 'shortdesc' se mantiene como columna global de mapeo directo.
            if col_limpia in ('area', 'securitygroup', 'container', 'containedname', 'aliasname', 'shortdesc'):
                source_value = row_datos_limpios.get(col_limpia, '')
                # Sobrescribimos el valor por defecto solo si hay un valor en el Excel de entrada
                if source_value:
                    nueva_fila[col_plantilla] = source_value
                continue

            # --- 3. Columnas de Atributo (Ej: boolean.OnMsg, boolean.Priority) ---
            if prefijo_principal and col_limpia.startswith(prefijo_principal + '.'):
                
                # Extraemos la parte después del punto (Ej: 'onmsg', 'priority', 'alarm.timedeadband')
                try:
                    target_input_key_full = col_limpia.split('.', 1)[1]
                except IndexError:
                    continue
                
                source_value = ''
                
                # 3.1. Intentar con la clave completa (e.g., 'onmsg', 'priority')
                source_value = row_datos_limpios.get(target_input_key_full, '')
                
                # 3.2. Si no encontramos nada Y la clave es compuesta, intentar con solo el sufijo final (e.g., 'timedeadband')
                if not source_value and '.' in target_input_key_full:
                    final_suffix = target_input_key_full.split('.')[-1]
                    source_value = row_datos_limpios.get(final_suffix, '')

                # 🟢 Sobrescribimos el valor por defecto (XML/None) solo si encontramos un valor en el Excel.
                if source_value:
                    nueva_fila[col_plantilla] = source_value
                        
        nuevas_filas.append(nueva_fila)

    return pd.DataFrame(nuevas_filas, columns=columnas_plantilla)


# --- Función Principal ---

def generar_csv_instancias_unificado(csv_datos_path, plantilla_dir, csv_salida_nombre="Instancias_Multiples_Unificado.csv"):
    
    print(f"Iniciando análisis del archivo de datos: {os.path.basename(csv_datos_path)}")
    
    # 1. Leer y preparar los datos de entrada (AJUSTADO A TU FORMATO PUNTO Y COMA)
    try:
        # Intentamos leer con los parámetros conocidos
        df_datos = pd.read_csv(
            csv_datos_path, 
            encoding='latin-1', 
            sep=';',              
            engine='python',      
            on_bad_lines='skip'   
        ) 
        
        # 🟢 PASO DE LIMPIEZA 1: Forzar todas las celdas a string y limpiar espacios, incluyendo NaN
        for col in df_datos.columns:
            # Reemplaza saltos de línea y fuerza a cadena
            df_datos[col] = df_datos[col].apply(lambda x: str(x).strip().replace('\r', '').replace('\n', ''))

        # 🟢 PASO DE LIMPIEZA 2: Rellenar celdas "nan" que quedaron después del str() con cadena vacía
        df_datos = df_datos.replace('nan', '', regex=False)
        
        # 🟢 PASO CRÍTICO: Normalización de nombres de columnas a minúsculas y sin espacios
        df_datos.columns = [col.strip().lower().replace(' ', '') for col in df_datos.columns]
        
        # Verificación de columnas requeridas (ahora en minúsculas)
        columnas_requeridas = ['template', 'instancia', 'atributo']
        for col in columnas_requeridas:
            if col not in df_datos.columns:
                print(f"❌ Error: La columna '{col}' no se encontró. Revise el nombre de su encabezado.")
                print(f"   Columnas encontradas (limpias): {df_datos.columns.tolist()}")
                return
        
        df_datos['templatename'] = df_datos['template'].astype(str).str.strip()
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo de datos. Revise que la ruta sea {csv_datos_path}")
        return
    except Exception as e:
        print(f"❌ Error fatal al procesar el archivo de datos: {e}.", file=sys.stderr)
        return

    # 2. Escribir el archivo de salida (OUTPUT: UTF-16, DELIMITADOR: COMA)
    templates_unicos = df_datos['templatename'].unique()
    print(f"\nPlantillas únicas detectadas: {', '.join(templates_unicos)}")
    total_instancias = 0
    
    try:
        # El archivo de SALIDA usa UTF-16 y coma (,) como delimitador, requerido por el importador.
        with open(csv_salida_nombre, 'w', newline='', encoding='utf-16') as f:
            
            for template_name in templates_unicos:
                print(f"\n--- Procesando plantilla: '{template_name}' ---")
                
                # Asume que el archivo de plantilla se llama exactamente "{template_name}.csv" 
                # Ahora buscará en la carpeta 'templates' que se pasó como argumento
                csv_plantilla_path = os.path.join(plantilla_dir, f"{template_name}.csv")
                
                df_subdata = df_datos[df_datos['templatename'] == template_name].copy()
                
                # 🟢 Obtener metadata, encabezados Y VALORES POR DEFECTO
                metadata_lines, columnas_plantilla, default_values_map = _obtener_metadata_y_columnas(csv_plantilla_path, template_name)
                
                if metadata_lines and columnas_plantilla and default_values_map is not None:
                    # 🟢 Pasar los valores por defecto a la función de creación de instancias
                    df_instancias = _crear_dataframe_instancias(template_name, df_subdata, columnas_plantilla, default_values_map)
                    
                    if not df_instancias.empty:
                        # 1. Escribir líneas de metadata
                        f.write('\n'.join(metadata_lines) + '\n')
                        
                        # 2. Escribir la línea de encabezado de System Platform
                        column_headers = df_instancias.columns.tolist()
                        
                        # Reemplazamos 'Tagname' (el interno) por ':Tagname' (el de salida)
                        if 'Tagname' in column_headers:
                            tagname_index = column_headers.index('Tagname')
                            column_headers[tagname_index] = ':Tagname'
                        
                        encabezado_linea_final = ','.join(column_headers)
                        f.write(encabezado_linea_final + '\n')
                        
                        # 3. Escribir los datos de las instancias (con coma)
                        # Usamos 'to_csv' sin header y sin index. El encoding ya está gestionado por el open().
                        df_instancias.to_csv(f, header=False, index=False, sep=',')
                        
                        print(f"  ✅ Bloque '{template_name}' añadido con {len(df_instancias)} instancias.")
                        total_instancias += len(df_instancias)
                    else:
                        print(f"  ⚠️ Plantilla '{template_name}' no generó instancias (datos vacíos).")

        print(f"\n✅ Éxito: Se generó el archivo unificado '{csv_salida_nombre}' correctamente.")
        print(f"   Total de instancias generadas: {total_instancias}")
        
    except Exception as e:
        print(f"❌ Error al escribir el archivo de salida final: {e}", file=sys.stderr)


# --- CONFIGURACIÓN Y EJECUCIÓN ---

# Define la ruta base (asumiendo que los archivos están en la misma carpeta)
# MODIFICADO: Ahora apunta a la subcarpeta 'templates'
PLANTILLAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates') 

# 🚨 AJUSTAR ESTE NOMBRE AL ARCHIVO CSV DE SU LISTA DE SEÑALES 🚨
# Se asume que el archivo Lista de señales.csv está en la misma carpeta que el script.
CSV_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lista de señales.csv') 

# Ejecutar la función
if __name__ == "__main__":
    try:
        import pandas as pd
    except ImportError:
        print("Librería requerida 'pandas' no encontrada. Por favor, instálela usando: pip install pandas", file=sys.stderr)
        sys.exit(1)
        
    generar_csv_instancias_unificado(CSV_DATOS, PLANTILLAS_DIR)






