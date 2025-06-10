import pandas as pd

# Загрузка данных из Excel
df = pd.read_excel('МТР в ЗНВ.xlsx', sheet_name='TDSheet')

# Разделение строк с несколькими кодами ЛРВ
df['Код ЛРВ'] = df['Код ЛРВ'].astype(str)  # Преобразование в строку, если это не так
df = df.assign(Код_ЛРВ=df['Код ЛРВ'].str.split(',')).explode('Код_ЛРВ').reset_index(drop=True)
df['Код_ЛРВ'] = df['Код_ЛРВ'].str.strip()  # Удаление лишних пробелов

# Сохранение обработанных данных в новый файл
df.to_excel('МТР в ЗНВ_обработанный.xlsx', index=False)