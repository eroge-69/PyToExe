# -*- coding: utf-8 -*-

import sys
import pandas as pd

new_columns = [
  'kod',
   'pib',
   'sum_bud',
   'sum_nj',
   'sum_ze',
   'object',
   'adresa',
   'to_katottg',
   'tg_katottg',
   'adrcmsuold',
   'kodu',
   'home',
   'acnt',
   'acnt49'

]

if len(sys.argv) < 2:
    print("Вкажіть ім'я вхідного Excel файлу")
    sys.exit(1)

input_file = sys.argv[1]
output_file = 'p_uniq.dbf'

# --- Читання Excel ---
df = pd.read_excel(input_file, dtype=object)  # усі дані як об'єкти

# --- Додаємо пусті стовпці, якщо їх менше ---
for i, col_name in enumerate(new_columns):
    if i >= len(df.columns):
        df[col_name] = ""  # новий порожній стовпець

# --- Обрізаємо зайві стовпці, якщо їх більше ---
df = df.iloc[:, :len(new_columns)]

# --- Перейменовуємо стовпці ---
df.columns = new_columns

from simpledbf import Dbf5
import dbf

 #Приклад функції для перетворення рядків перед записом у DBF
def dbf_safe_value(value, field_type):
    if pd.isna(value):
        if field_type.startswith('C'):
            return ''
        elif field_type.startswith('N'):
            return 0.0  # або None
    if field_type.startswith('C'):
        return str(value)
    elif field_type.startswith('N'):
        return float(value)
    return value


structure = [
    "KOD C(9)",
    "PIB C(50)",
    "SUM_BUD N(10,2)",
    "SUM_NJ C(11)",
    "SUM_ZE N(14,2)",
    "OBJECT C(55)",
    "ADRESA C(159)",
    "TO_KATOTTG C(19)",
    "TG_KATOTTG C(19)",
    "ADRCMSUOLD C(50)",
    "KODU C(3)",
    "HOME C(9)",
    "ACNT C(8)",
    "ACNT49 C(8)"
]

strctr = "KOD C(9); PIB C(50); SUM_BUD N(10,2); SUM_NJ C(11); SUM_ZE N(14,2); OBJECT C(55); ADRESA C(159); TO_KATOTTG C(19); TG_KATOTTG C(19); ADRCMSUOLD C(50); KODU C(3); HOME C(9); ACNT C(8); ACNT49 C(8)"
table = dbf.Table(
    output_file,
    field_specs= strctr,
    codepage='cp1251'
)
table.open(dbf.READ_WRITE)

col_map = {c.lower(): c for c in df.columns}  # маппінг для швидкого пошуку

for row in df.itertuples(index=False):
    record = {}
    for spec in structure:
        col_name = spec.split()[0].lower()  # DBF нижній регістр
        field_type = spec.split()[1]
        if col_name in col_map:
            value = getattr(row, col_map[col_name])
            record[col_name] = dbf_safe_value(value, field_type)
        else:
            record[col_name] = 0.0 if field_type.startswith('N') else ''
    table.append(record)


table.close()