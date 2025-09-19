import pdfplumber
import pandas as pd
from itertools import zip_longest
import warnings

warnings.filterwarnings("ignore")

pdf_file = "diversos 08092025.pdf"

with pdfplumber.open(pdf_file) as pdf:
    page = pdf.pages[1]  # página 2
    table = page.extract_table()

# Encabezados
headers = [h.replace("\n", " ").strip() for h in table[0]]

# Separar cada columna en filas (split por salto de línea)
columns = [col.split("\n") for col in table[1]]

# Transponer → convertir listas de columnas en listas de filas
data = list(zip_longest(*columns, fillvalue=None))

# Crear DataFrame
df = pd.DataFrame(data, columns=headers)

#print(df.head())

def parse_number(x):
    if x is None or str(x).strip() == "":
        return None
    return float(str(x).replace(".", "").replace(",", "."))

# Columnas que deben ser numéricas
numeric_cols = [
    "PRIMAS NETAS DE ANULACION",
    "SINIESTRALIDAD PROPIO AÑO",
    "DESVIACIONES",
    "IBNR",
    "TOTAL SINIESTRALIDAD",
    "% SINIESTR."
]

for col in numeric_cols:
    df[col] = df[col].apply(parse_number)

#print(df.dtypes)

df.to_excel('Gorka.xlsx', index=False)