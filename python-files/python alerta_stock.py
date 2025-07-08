import pandas as pd

# Leer el archivo Excel
archivo = "stock.xlsx"
df = pd.read_excel(archivo, skiprows=7)

# Renombrar columnas importantes
df = df.rename(columns={
    'Codigo  ': 'Codigo',
    'Descripción           ': 'Descripcion',
    'Stock           ': 'Stock'
})

# Filtrar columnas necesarias
df = df[['Codigo', 'Descripcion', 'Stock']]
df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce')
df = df.dropna(subset=['Codigo', 'Stock'])

# Lista de códigos a controlar (ejemplos)
codigos_a_controlar = ['Nmsl6', 'Tpe4-3', 'Tpm4-1', 'Blow2']

# Umbral mínimo de stock
umbral_stock = 2

# Filtrar productos controlados
alertas = df[df['Codigo'].isin(codigos_a_controlar) & (df['Stock'] < umbral_stock)]

# Mostrar alertas
if alertas.empty:
    print("Todos los productos seleccionados tienen stock suficiente.")
else:
    print("ALERTA: Los siguientes productos tienen bajo stock:\n")
    print(alertas[['Codigo', 'Descripcion', 'Stock']])
