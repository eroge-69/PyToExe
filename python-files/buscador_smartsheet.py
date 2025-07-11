
import smartsheet

# === CONFIGURACIÓN ===
API_TOKEN = 'HxFFbbFTCpWDQEqpmWg63ADcC45Ky3vgR2uKU'  # Reemplaza con tu token real
SHEET_ID = '57hgVxhvcc9XqGx2RJwM5Mvqv8c4m4GQHQFcP5M1'
COLUMNA_BUSQUEDA = 'Ref N° DE SERIE'
COLUMNAS_OBJETIVO = ['USUARIOUS', 'NOMBRE', 'EQUIPO EN USO', 'DESCRIPCION', 'VERSION WINDOWS', 'LUGAR DE TRABAJO']

def buscar_por_numero_de_serie(numero_serie):
    smartsheet_client = smartsheet.Smartsheet(API_TOKEN)
    sheet = smartsheet_client.Sheets.get_sheet(SHEET_ID)

    column_map = {col.title: col.id for col in sheet.columns}

    fila_encontrada = None
    for row in sheet.rows:
        for cell in row.cells:
            if cell.column_id == column_map[COLUMNA_BUSQUEDA] and str(cell.value).strip() == numero_serie:
                fila_encontrada = row
                break
        if fila_encontrada:
            break

    if fila_encontrada:
        print(f"\n🔍 Resultados para '{numero_serie}':")
        for col in COLUMNAS_OBJETIVO:
            valor = next((c.value for c in fila_encontrada.cells if c.column_id == column_map[col]), None)
            print(f"{col}: {valor}")
    else:
        print(f"\n⚠️ No se encontró ninguna fila con '{numero_serie}' en la columna '{COLUMNA_BUSQUEDA}'.")

if __name__ == "__main__":
    numero = input("Ingresa el número de serie a buscar: ")
    buscar_por_numero_de_serie(numero)
