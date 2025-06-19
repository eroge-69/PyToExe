# %%
import os
import shutil

# Исходная и целевая папки (укажи свои пути)
source_folder = r'\\192.168.226.2\FTP Partners\Multicarta\Weekly_LOGS'
target_folder = './'

# Создать целевую папку, если её нет
os.makedirs(target_folder, exist_ok=True)

# Переместить все .rar и .zip файлы, пропуская занятые
for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.rar', '.zip')):
        source_file = os.path.join(source_folder, filename)
        target_file = os.path.join(target_folder, filename)
        try:
            shutil.move(source_file, target_file)
            print(f"Перемещён: {filename}")
        except PermissionError:
            print(f"Файл занят, пропускаем: {filename}")
            continue
        except Exception as e:
            print(f"Ошибка при перемещении файла {filename}: {e}")
            continue

print("Готово!")

import re
import pandas as pd
from datetime import datetime

def extract_data(line):
    patterns = {
        'datetime': r'(\d{8}:\d{6})\..*?',
        'error_code': r'ErrorCode=(\w+)',
        'rc_error_code': r'RCErrorCode=(\w+)',
        'dip_switch': r'DipSwitch=([^;]+)',
        #'fatal_reason': r'FatalReason=([^;]+)',
        'cassette_ids': r'CassetteIDs=([^;]+)',
    }

    data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, line)
        if match:
            if key == 'datetime':
                datetime_str = match.group(1)
                datetime_format = '%Y%m%d:%H%M%S'
                data[key] = datetime.strptime(datetime_str, datetime_format)
            else:
                data[key] = match.group(1)

    return data

extracted_data_list = []

def main(log_file, tid, isSaga=False):
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                extracted_data = extract_data(line)
                if 'error_code' in extracted_data:
                    error_code = extracted_data['error_code']
                    # Include lines with error_code, excluding '0000000'
                    if error_code != '0000000':
                        cassette_ids = extracted_data.get('cassette_ids', None)
                        dipswitches = extracted_data.get('dip_switch', None)
                        brm = None

                        if cassette_ids and dipswitches:
                            cassette_ids = cassette_ids.split(',')
                            dipswitches = dipswitches.split(',')

                            if len(cassette_ids) == 5 or len(cassette_ids) == 7:
                                if len(cassette_ids) == 5:
                                    cassette_ids = [''] + [cassette_ids[4]] + cassette_ids[0:4]
                                    dipswitches = [''] + [dipswitches[4]] + dipswitches[0:4]
                                    brm = 'BRM20'
                                    if isSaga:
                                        dipswitches = [dipswitches[4]] + dipswitches[0:4]
                                if len(cassette_ids) == 7:
                                    cassette_ids = cassette_ids[1:]
                                    dipswitches = dipswitches[1:]
                                    brm = 'BRM5X'
                                    if isSaga:
                                        dipswitches = [dipswitches[5]] + dipswitches[0:5]
                                        cassette_ids = [cassette_ids[5]] + cassette_ids[0:5]

                        if brm:
                            extracted_data_list.append({
                                'tid': tid,
                                'brm': brm,
                                'DateTime': extracted_data.get('datetime', None),
                                'ErrorCode': extracted_data.get('error_code', None),
                                'RCErrorCode': extracted_data.get('rc_error_code', None),
                                'DipSwitch_RJ': dipswitches[0] if dipswitches else None,
                                'DipSwitch_DPC': dipswitches[1] if dipswitches else None,
                                'DipSwitch_100': dipswitches[2] if dipswitches else None,
                                'DipSwitch_500': dipswitches[3] if dipswitches else None,
                                'DipSwitch_1000': dipswitches[4] if dipswitches else None,
                                'DipSwitch_5000': dipswitches[5] if dipswitches else None,
                                #'FatalReason': extracted_data.get('fatal_reason', None),
                                'CassetteID_RJ': cassette_ids[0] if cassette_ids else None,
                                'CassetteID_DPC': cassette_ids[1] if cassette_ids else None,
                                'CassetteID_100': cassette_ids[2] if cassette_ids else None,
                                'CassetteID_500': cassette_ids[3] if cassette_ids else None,
                                'CassetteID_1000': cassette_ids[4] if cassette_ids else None,
                                'CassetteID_5000': cassette_ids[5] if cassette_ids else None,
                            })
                        else:
                            extracted_data_list.append({
                                'tid': tid,
                                'brm': None,
                                'DateTime': extracted_data.get('datetime', None),
                                'ErrorCode': extracted_data.get('error_code', None),
                                'RCErrorCode': extracted_data.get('rc_error_code', None),
                                'DipSwitch_RJ': None,
                                'DipSwitch_DPC': None,
                                'DipSwitch_100': None,
                                'DipSwitch_500': None,
                                'DipSwitch_1000': None,
                                'DipSwitch_5000': None,
                                #'FatalReason': extracted_data.get('fatal_reason', None),
                                'CassetteID_RJ': None,
                                'CassetteID_DPC': None,
                                'CassetteID_100': None,
                                'CassetteID_500': None,
                                'CassetteID_1000': None,
                                'CassetteID_5000': None,
                            })

    except FileNotFoundError:
        print(f"File {log_file} not found.")

# Example usage
# main('path_to_log_file.log', 'tid_value', isSaga=False)


# %%
import os
import patoolib
import tempfile
from pathlib import Path

archives = []
saga_archives = []

def find_archives(directory):
    for archive in os.listdir(directory):
        if archive.endswith('.RAR'):
            archives.append(archive)
        if archive.endswith('.zip'):
            saga_archives.append(archive)

find_archives('./')

for archive in archives:
    if archive.endswith('.RAR'):
        print(f"Processing archive: {archive}")
        try:
            # Create a temporary directory to extract the archive to
            temp_dir = tempfile.TemporaryDirectory()
            patoolib.extract_archive(archive, outdir=temp_dir.name, verbosity=-1)
            for file in os.listdir(temp_dir.name):
                if file.endswith('.ERL'):
                    print(f"Processing file: {file}")
                    file_path = os.path.join(temp_dir.name, file)
                    try:
                        main(file_path, archive[0:6])
                    except Exception as e:
                        print(f"Error processing file {file}: {e}")
            temp_dir.cleanup()
        except Exception as e:
            print(f"Error processing archive {archive}: {e}")

for archive in saga_archives:
    if archive.endswith('zip'):
        try:
            temp_dir = tempfile.TemporaryDirectory()
            path = patoolib.extract_archive(archive, outdir=temp_dir.name, verbosity=-1)
            archive_path = Path(path)
            erl_dir = archive_path / 'scs' / 'LOGS' / 'ERL'
            erls_array = sorted([f for f in erl_dir.iterdir() if f.suffix == '.ERL'])
            for file in erls_array:
                print(f"Processing file: {file}")
                try:
                    main(str(file), archive[0:6], isSaga=True)
                except Exception as e:
                    print(f"Error processing file {file}: {e}")
            temp_dir.cleanup()
        except Exception as e:
            print(f"Error processing archive {archive}: {e}")

        

# %%
df = pd.DataFrame(extracted_data_list)


# %%
import pandas as pd

    # Шаг 1: Прочитать данные из файла "Ошибки BRM.xlsx"
    # Шаг 1: Прочитать данные из файла "Ошибки BRM.xlsx"
brm_errors_df = pd.read_excel('Ошибки BRM.xlsx')

    # Шаг 2: Создать функцию для определения модуля
def determine_module(row, brm_errors_df):
    brm = row['brm']
    rc_error_code = row['RCErrorCode']
    error_code = row['ErrorCode']

        # Если RCErrorCode равен 0000000, проверяем по ErrorCode
    if rc_error_code == '0000000':
        matching_rows = brm_errors_df[
            (brm_errors_df['BRM'] == brm) &
            (brm_errors_df['Код ошибки'].astype(str).str.contains(error_code, na=False))
        ]
    else:
            # Иначе проверяем по RCErrorCode
        matching_rows = brm_errors_df[
            (brm_errors_df['BRM'] == brm) &
            (brm_errors_df['Код ошибки'].astype(str).str.contains(rc_error_code, na=False))
        ]

    if not matching_rows.empty:
        return matching_rows['Модуль'].values[0]

        # Если не нашлось совпадений, возвращаем None
    return None

    # Шаг 3: Применить функцию к датафрейму с извлеченными данными
df = pd.DataFrame(extracted_data_list)
df['Module'] = df.apply(lambda row: determine_module(row, brm_errors_df) if isinstance(row['brm'], str) and isinstance(row['RCErrorCode'], str) and isinstance(row['ErrorCode'], str) else None, axis=1)

with open('BRM20.txt', 'r') as brm20_file:
        brm20_tids = set(brm20_file.read().splitlines())
        
df['brm'] = df.apply(lambda row: 'BRM20' if row['tid'] in brm20_tids else 'BRM5X', axis=1)
    # Вывести датафрейм с новой колонкой "Module"
df = df.drop_duplicates()
print(df)



# %%
from datetime import datetime

current_dateTime = datetime.now()
filename = current_dateTime.strftime("%Y-%m-%d_%H-%M-%S")  # Без запрещённых символов
df.to_excel(f'{filename}.xlsx', index=False)  # Путь можно уточнить при необходимости
print(f"Файл сохранён: {filename}.xlsx")

# %%
import psycopg2
from io import StringIO
import pandas as pd

# PostgreSQL connection details
db_user = 'postgres'
db_password = '153759QQ'
db_host = '192.168.226.3'
db_port = '5432'
db_name = 'DBReports'
table_name = 'erl_logs_table'

# Create a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# Create a cursor object
cur = conn.cursor()

# Check if the table exists and create it if it doesn't
cur.execute("""
    SELECT EXISTS (
        SELECT FROM
            pg_tables
        WHERE
            schemaname = 'public' AND
            tablename = %s
    )
""", [table_name])
table_exists = cur.fetchone()[0]

if not table_exists:
    create_table_query = """
        CREATE TABLE {} (
            tid VARCHAR(50),
            brm VARCHAR(50),
            DateTime TIMESTAMP,
            ErrorCode VARCHAR(50),
            RCErrorCode VARCHAR(50),
            DipSwitch_RJ VARCHAR(50),
            DipSwitch_DPC VARCHAR(50),
            DipSwitch_100 VARCHAR(50),
            DipSwitch_500 VARCHAR(50),
            DipSwitch_1000 VARCHAR(50),
            DipSwitch_5000 VARCHAR(50),
            CassetteID_RJ VARCHAR(50),
            CassetteID_DPC VARCHAR(50),
            CassetteID_100 VARCHAR(50),
            CassetteID_500 VARCHAR(50),
            CassetteID_1000 VARCHAR(50),
            CassetteID_5000 VARCHAR(50),
            Module VARCHAR(50)
        )
    """.format(table_name)
    cur.execute(create_table_query)
    conn.commit()

# Очистка данных от символов новой строки
df = df.replace(r'\n', ' ', regex=True)

# Use StringIO to upload the DataFrame to PostgreSQL
buffer = StringIO()
df.to_csv(buffer, index=False, header=False)
buffer.seek(0)

# Copy the data from the buffer to the PostgreSQL table
cur.copy_expert("COPY {} FROM STDIN WITH CSV ESCAPE '\\'".format(table_name), buffer)
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print(f"Data successfully uploaded to {table_name}.")


# %%
import os
import shutil

# Исходная и целевая папки (укажи свои пути)
source_folder = './'
target_folder = r'.\done'

# Создать целевую папку, если её нет
os.makedirs(target_folder, exist_ok=True)

# Переместить все .rar файлы
for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.rar', '.zip')):
        source_file = os.path.join(source_folder, filename)
        target_file = os.path.join(target_folder, filename)
        shutil.move(source_file, target_file)
        print(f"Перемещён: {filename}")

print("Готово!")



