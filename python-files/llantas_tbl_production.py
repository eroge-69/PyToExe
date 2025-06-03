import pyodbc
import pandas as pd
from datetime import datetime
import string

class BarcodeSearcher:
    def __init__(self, connection_string):
        """
        Inicializa el buscador de barcodes
        
        Args:
            connection_string (str): Cadena de conexión a SQL Server
        """
        self.connection_string = connection_string
        self.conn = None
    
    def connect(self):
        """Establece la conexión a la base de datos"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            print("Conexión establecida exitosamente")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise
    
    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            print("Conexión cerrada")
    
    def get_missing_vulcanization_records(self, fecha_inicio, fecha_fin):
        """
        Obtiene los registros de vulcanización que no están en tbl_production
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'
            
        Returns:
            pandas.DataFrame: DataFrame con los registros faltantes
        """
        query = """
        DECLARE @FechaInicio DATE = ?
        DECLARE @FechaFin DATE = ?
        
        SELECT 
            v.[BarCode],
            v.[FechaProd] as FechaVulcanizacion,
            v.[CodProdTerminado],
            v.[Prensa],
            v.[IdOperador] as OperadorVulcanizacion,
            v.[CodigoSap]
        FROM [Vulca].[Vulcanizacion].[dbo].[Curing] v
        LEFT JOIN [MAM].[MAM].[dbo].[tbl_production] a 
            ON v.[BarCode] = a.[barcode]
        WHERE a.[barcode] IS NULL
            AND v.[FechaProd] BETWEEN @FechaInicio AND @FechaFin
        ORDER BY v.[FechaProd] DESC
        """
        
        try:
            df = pd.read_sql(query, self.conn, params=[fecha_inicio, fecha_fin])
            print(f"Se encontraron {len(df)} registros faltantes en tbl_production")
            return df
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return pd.DataFrame()
    
    def extract_barcode_parts(self, barcode):
        """
        Extrae las partes del barcode (prefijo y consecutivo)
        
        Args:
            barcode (str): Código de barras completo
            
        Returns:
            tuple: (prefijo, consecutivo) donde consecutivo son los últimos 4 caracteres
        """
        if len(barcode) < 4:
            return barcode, ""
        
        prefix = barcode[:-4]  # Todo excepto los últimos 4 caracteres
        consecutive = barcode[-4:]  # Últimos 4 caracteres
        
        return prefix, consecutive
    
    def generate_consecutive_variations(self, consecutive, max_iterations=5):
        """
        Genera variaciones del consecutivo para buscar registros relacionados
        
        Args:
            consecutive (str): Consecutivo original (últimos 4 caracteres)
            max_iterations (int): Número máximo de iteraciones para buscar
            
        Returns:
            list: Lista de posibles consecutivos
        """
        variations = []
        
        # Convertir el consecutivo a lista para facilitar manipulación
        chars = list(consecutive)
        
        # Generar variaciones incrementando cada posición
        for iteration in range(1, max_iterations + 1):
            # Crear una copia para modificar
            current_chars = chars.copy()
            carry = iteration
            
            # Aplicar el incremento de derecha a izquierda (como un contador)
            for i in range(len(current_chars) - 1, -1, -1):
                if carry == 0:
                    break
                    
                char = current_chars[i]
                
                if char.isdigit():
                    # Si es dígito, incrementar
                    new_val = (int(char) + carry) % 10
                    carry = (int(char) + carry) // 10
                    current_chars[i] = str(new_val)
                elif char.isalpha():
                    # Si es letra, incrementar en el alfabeto
                    if char.isupper():
                        new_ord = ((ord(char) - ord('A') + carry) % 26) + ord('A')
                        carry = (ord(char) - ord('A') + carry) // 26
                    else:
                        new_ord = ((ord(char) - ord('a') + carry) % 26) + ord('a')
                        carry = (ord(char) - ord('a') + carry) // 26
                    current_chars[i] = chr(new_ord)
            
            variations.append(''.join(current_chars))

        # Generar variaciones decrementando cada posición
        for iteration in range(1, max_iterations + 1):
            # Crear una copia para modificar
            current_chars = chars.copy()
            carry = iteration
            
            # Aplicar el decremento de derecha a izquierda (como un contador)
            for i in range(len(current_chars) - 1, -1, -1):
                if carry == 0:
                    break
                    
                char = current_chars[i]
                
                if char.isdigit():
                    # Si es dígito, decrementar
                    new_val = (int(char) - carry) % 10
                    carry = (int(char) - carry) // 10
                    current_chars[i] = str(new_val)
                elif char.isalpha():
                    # Si es letra, decrementar en el alfabeto
                    if char.isupper():
                        new_ord = ((ord(char) - ord('A') - carry) % 26) + ord('A')
                        carry = (ord(char) - ord('A') + carry) // 26
                    else:
                        new_ord = ((ord(char) - ord('a') - carry) % 26) + ord('a')
                        carry = (ord(char) - ord('a') - carry) // 26
                    current_chars[i] = chr(new_ord)
            
            variations.append(''.join(current_chars))
        
        print("Lista de variaciones: ", variations)
        
        return variations
    
    def search_related_barcode_info(self, barcode):
        """
        Busca información relacionada basándose en el barcode
        
        Args:
            barcode (str): Código de barras original
            
        Returns:
            dict: Información encontrada o None si no se encuentra
        """
        prefix, consecutive = self.extract_barcode_parts(barcode)
        print(f"Buscando información para: {barcode} (Prefijo: {prefix}, Consecutivo: {consecutive})")
        
        # Generar variaciones del consecutivo
        variations = self.generate_consecutive_variations(consecutive)
        
        # Buscar en tbl_production con cada variación
        for variation in variations:
            test_barcode = prefix + variation
            
            query = """
            SELECT TOP 1
                barcode,
                machineId,
                EmpName,
                producedDate,
                materialId
            FROM [MAM].[MAM].[dbo].[tbl_production]
            WHERE barcode = ?
            """
            
            try:
                result = pd.read_sql(query, self.conn, params=[test_barcode])
                if not result.empty:
                    print(f"Información encontrada con barcode: {test_barcode}")
                    return {
                        'barcode_encontrado': test_barcode,
                        'barcode_original': barcode,
                        'machineId': result.iloc[0]['machineId'],
                        'EmpName': result.iloc[0]['EmpName'],
                        'producedDate': result.iloc[0]['producedDate'],
                        'materialId': result.iloc[0]['materialId']
                    }
            except Exception as e:
                print(f"Error buscando {test_barcode}: {e}")
                continue
        
        print(f"No se encontró información relacionada para: {barcode}")
        return None
    
    def process_missing_records(self, fecha_inicio, fecha_fin):
        """
        Procesa todos los registros faltantes y busca información relacionada
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'
            fecha_fin (str): Fecha de fin en formato 'YYYY-MM-DD'
            
        Returns:
            tuple: (DataFrame con registros originales, lista con información encontrada)
        """
        # Obtener registros faltantes
        missing_records = self.get_missing_vulcanization_records(fecha_inicio, fecha_fin)
        
        if missing_records.empty:
            print("No hay registros faltantes para procesar")
            return missing_records, []
        
        # Buscar información relacionada para cada registro
        found_info = []
        
        for idx, row in missing_records.iterrows():
            barcode = row['BarCode']
            print(f"\nProcesando {idx + 1}/{len(missing_records)}: {barcode}")
            
            related_info = self.search_related_barcode_info(barcode)
            if related_info:
                # Combinar información original con la encontrada
                combined_info = {
                    'barcode_original': barcode,
                    'fecha_vulcanizacion': row['FechaVulcanizacion'],
                    'cod_prod_terminado': row['CodProdTerminado'],
                    'prensa': row['Prensa'],
                    'operador_vulcanizacion': row['OperadorVulcanizacion'],
                    'codigo_sap': row['CodigoSap'],
                    'barcode_encontrado': related_info['barcode_encontrado'],
                    'machine_id_sugerido': related_info['machineId'],
                    'employee_id_sugerido': related_info['EmpName'],
                    'created_at_referencia': related_info['producedDate'],
                    'materialId_id_referencia': related_info['materialId']
                }
                found_info.append(combined_info)
        
        return missing_records, found_info
    
    def export_results(self, missing_records, found_info, output_file='resultados_barcode_search.xlsx'):
        """
        Exporta los resultados a un archivo Excel
        
        Args:
            missing_records (DataFrame): Registros faltantes originales
            found_info (list): Lista con información encontrada
            output_file (str): Nombre del archivo de salida
        """
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Hoja 1: Registros faltantes originales
                missing_records.to_excel(writer, sheet_name='Registros_Faltantes', index=False)
                
                # Hoja 2: Información encontrada
                if found_info:
                    found_df = pd.DataFrame(found_info)
                    found_df.to_excel(writer, sheet_name='Informacion_Encontrada', index=False)
                
                print(f"Resultados exportados a: {output_file}")
        except Exception as e:
            print(f"Error al exportar: {e}")

def main():
    """Función principal para ejecutar el proceso"""
    
    # Configuración de conexión (ajusta según tu configuración)
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=10.177.144.165;"
        "DATABASE=PROINSYM;"
        "UID=ApoloUser;"
        "PWD=firestone1*;"
        "Trusted_Connection=no;"
    )
    
    # Fechas para la consulta
    #fecha_inicio = '2025-05-15'
    #fecha_fin = '2025-06-01'
    fecha_inicio = input("Digite la fecha inicial en formato año-mes-dia: ")
    fecha_fin = input("Digite la fecha final en formato año-mes-dia: ")
    
    # Crear instancia del buscador
    searcher = BarcodeSearcher(connection_string)
    
    try:
        # Conectar a la base de datos
        searcher.connect()
        
        # Procesar registros faltantes
        print(f"Iniciando búsqueda para el período: {fecha_inicio} - {fecha_fin}")
        missing_records, found_info = searcher.process_missing_records(fecha_inicio, fecha_fin)
        
        # Mostrar resumen
        print(f"\nRESUMEN:")
        print(f"  Registros faltantes: {len(missing_records)}")
        print(f"  Información encontrada: {len(found_info)}")
        print(f"  Tasa de éxito: {len(found_info)/len(missing_records)*100:.1f}%" if len(missing_records) > 0 else "No hay registros para procesar")
        
        # Exportar resultados
        if not missing_records.empty:
            searcher.export_results(missing_records, found_info)
        
        # Mostrar información encontrada
        if found_info:
            print(f"\nINFORMACIÓN ENCONTRADA:")
            for i, info in enumerate(found_info):
                print(f"{i+1}. {info['barcode_original']} → {info['barcode_encontrado']}")
                print(f"Machine ID: {info['machine_id_sugerido']}, Employee ID: {info['employee_id_sugerido']}")
    
    except Exception as e:
        print(f"Error en el proceso: {e}")
    
    finally:
        # Cerrar conexión
        searcher.close_connection()

if __name__ == "__main__":
    main()