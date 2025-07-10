import pandas as pd
import glob
import os

# Paso 1: Encuentra tus ficheros .csv en el directorio actual.
#file_paths = glob.glob('*.csv')
file_paths = ['ReportageLearnersReport-1.csv', 'ReportageLearnersReport-2.csv', 'ReportageLearnersReport-3.csv', 'ReportageLearnersReport-4.csv']

# Lista para guardar cada tabla (DataFrame)
data_frames = []

# Columnas que nos interesan
required_columns = ['Learner Id', 'Learner', 'Avg Score']

# Paso 2: Lee y prepara cada fichero.
if not file_paths:
    print("¡Advertencia! No se encontraron archivos .csv en el directorio actual.")
    print("Asegúrate de que los archivos estén en la misma carpeta que el script o especifica sus rutas.")
else:
    for i, path in enumerate(file_paths):
        print(f"\nProcesando el archivo: {os.path.basename(path)}")
        try:
            # Lee el fichero CSV
            df = pd.read_csv(path)

            # Verificar si las columnas requeridas existen en el DataFrame
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"¡Advertencia! Las siguientes columnas requeridas no se encontraron en '{os.path.basename(path)}': {', '.join(missing_columns)}")
                print(f"Columnas disponibles en este archivo: {df.columns.tolist()}")
                continue # Saltamos al siguiente archivo si faltan columnas esenciales

            # Selecciona solo las columnas de interés: "Learner Id", "Learner", "Avg Score"
            df_subset = df[required_columns].copy()

            # --- DIAGNÓSTICO AÑADIDO ---
            print(f"Valores originales de 'Avg Score' en '{os.path.basename(path)}' (primeros 5):")
            print(df_subset['Avg Score'].head().to_string())
            print(f"Tipo de datos original de 'Avg Score': {df_subset['Avg Score'].dtype}")

            # LIMPIEZA Y CONVERSIÓN CRÍTICA:
            # 1. Limpiar caracteres no numéricos como '%' y espacios
            if not df_subset['Avg Score'].empty and pd.notna(df_subset['Avg Score'].iloc[0]):
                if '%' in str(df_subset['Avg Score'].iloc[0]):
                    print("Detectado '%'. Eliminando '%' antes de la conversión.")
                    df_subset['Avg Score'] = df_subset['Avg Score'].astype(str).str.replace('%', '', regex=False).str.strip()
                else:
                     df_subset['Avg Score'] = df_subset['Avg Score'].astype(str).str.strip() # Siempre limpiar espacios
            else: # Si está vacío o es NaN, simplemente lo dejamos como está o lo convertimos a string para strip
                df_subset['Avg Score'] = df_subset['Avg Score'].astype(str).str.strip()

            # 2. Reemplazar comas por puntos si se usan como decimales
            if df_subset['Avg Score'].astype(str).str.contains(',').any():
                print("Detectada coma como separador decimal. Reemplazando por punto.")
                df_subset['Avg Score'] = df_subset['Avg Score'].astype(str).str.replace(',', '.')

            # Convertir 'Avg Score' a numérico.
            df_subset['Avg Score'] = pd.to_numeric(df_subset['Avg Score'], errors='coerce')

            # --- DIAGNÓSTICO DESPUÉS DE LA CONVERSIÓN ---
            print(f"Valores de 'Avg Score' DESPUÉS de conversión en '{os.path.basename(path)}' (primeros 5):")
            print(df_subset['Avg Score'].head().to_string())
            print(f"Tipo de datos de 'Avg Score' DESPUÉS de conversión: {df_subset['Avg Score'].dtype}")
            # ---------------------------------------------

            # Renombra la columna 'Avg Score' para que sea única en cada fichero.
            df_subset = df_subset.rename(columns={'Avg Score': f'Avg_Score_{i+1}'})

            data_frames.append(df_subset)

        except pd.errors.EmptyDataError:
            print(f"¡Error! El archivo '{os.path.basename(path)}' está vacío. Se saltará.")
        except FileNotFoundError:
            print(f"¡Error! El archivo '{os.path.basename(path)}' no se encontró. Verifica la ruta.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al leer '{os.path.basename(path)}': {e}")

# Paso 3: Une todas las tablas en una sola.
if not data_frames:
    print("\nNo hay DataFrames válidos para combinar. No se creará la tabla final.")
else:
    # Empezamos con el primer DataFrame
    merged_df = data_frames[0]

    # Ahora, unimos los DataFrames restantes.
    # La unión se hace usando "Learner Id" y "Learner" como claves.
    for df_to_merge in data_frames[1:]:
        merged_df = pd.merge(merged_df, df_to_merge, on=['Learner Id', 'Learner'], how='outer')

    # Paso 4: Muestra y guarda el resultado y aplica formato condicional.
    print("\n--- Tabla combinada (primeras 5 filas) ---")
    print(merged_df.head().to_string())
    if len(merged_df) > 5:
        print(f"... y {len(merged_df) - 5} filas más.")

    output_filename = 'tabla_final_columnas_ABI.xlsx'

    # Crea un objeto ExcelWriter
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

    # Escribe el DataFrame en una hoja de Excel
    merged_df.to_excel(writer, sheet_name='Resultados', index=False)

    # Accede al objeto workbook y worksheet de XlsxWriter
    workbook = writer.book
    worksheet = writer.sheets['Resultados']

    # Define los formatos de celda
    green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'}) # Verde claro
    yellow_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'}) # Amarillo

    # Obtiene las columnas 'Avg_Score_X' para aplicar el formato
    avg_score_cols = [col for col in merged_df.columns if col.startswith('Avg_Score_')]

    # Columnas Learner Id y Learner
    learner_info_cols = ['Learner Id', 'Learner']

    # Itera sobre cada fila del DataFrame para aplicar el formato
    # Empezamos desde la segunda fila de Excel (índice 1 de Pandas es fila 2 de Excel)
    for row_num in range(1, len(merged_df) + 1):
        # Reiniciar estas banderas para cada nueva fila
        all_scores_above_80 = True
        has_all_scores = True # NUEVA BANDERA: Para verificar si tiene todos los scores, no solo si hay alguno.
        
        # Recopilar los scores de la fila actual
        current_scores = []
        for col_name in avg_score_cols:
            score = merged_df.iloc[row_num - 1][col_name]
            if pd.notna(score):
                current_scores.append(score)
            else:
                has_all_scores = False # Si una celda está vacía, no tiene todos los scores

        # Si no tiene todos los scores o si tiene scores y alguno es < 80, entonces no es "todo verde".
        if not has_all_scores or any(score < 80 for score in current_scores):
            all_scores_above_80 = False
        
        # Si no hay scores en la fila, tampoco es "todo verde" para el Learner Id/Learner
        if not current_scores:
            all_scores_above_80 = False


        # Aplicar formato a las columnas 'Learner Id' y 'Learner'
        # SOLO si all_scores_above_80 es True (lo que ahora implica que están todos presentes y son >= 80)
        if all_scores_above_80: # Simplificado
            for col_name in learner_info_cols:
                col_idx = merged_df.columns.get_loc(col_name)
                cell_value = merged_df.iloc[row_num - 1][col_name]
                if pd.notna(cell_value): # Asegurarse de que la celda no esté vacía
                    worksheet.write(row_num, col_idx, cell_value, green_format)

        # Ahora aplicamos el formato a las celdas 'Avg_Score_X' de la fila actual
        for col_name in avg_score_cols:
            col_idx = merged_df.columns.get_loc(col_name) # Obtiene el índice de la columna en Excel
            score = merged_df.iloc[row_num - 1][col_name]

            if pd.notna(score): # Si la celda no está vacía (NaN)
                if all_scores_above_80: # Si ya sabemos que todos son verdes para esta persona (y están todos presentes)
                    worksheet.write(row_num, col_idx, score, green_format)
                else: # Si no todos son verdes (o no están todos presentes), aplicar formato individual
                    if score >= 80:
                        worksheet.write(row_num, col_idx, score, green_format)
                    else:
                        worksheet.write(row_num, col_idx, score, yellow_format)
            else:
                 pass # Las celdas vacías se dejan sin formato.


    # Cierra el objeto ExcelWriter para guardar el archivo
    writer.close()

    print(f"\nLa tabla combinada se ha guardado como '{output_filename}' con formato condicional.")
    
    