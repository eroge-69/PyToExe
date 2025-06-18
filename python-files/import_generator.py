import pandas as pd

# Загрузка исходного файла
file_path = 'enter_file.xlsx'
df = pd.read_excel(file_path, sheet_name='ALL')

# Выбор нужных столбцов (укажите свои)
selected_columns = ['policy_number', 'date_from', 'date_to', 'prog_name', 'address', 'birth_date', 'person_sex', 'company_of_work', 'per_last_name', 'per_first_name', 'insurer', 'insurer']
filtered_df = df[selected_columns]

# Сохранение в новый файл
filtered_df.to_excel('out_file.xlsx', index=False)