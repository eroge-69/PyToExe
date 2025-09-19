import pandas as pd
import numpy as np
import glob
import os
import re
from datetime import datetime
import csv
import shutil

pd.options.mode.chained_assignment = None

def int_r(num):
    return int(num + 0.5)

def find_excel_files(folder, ext='*.xlsx'):
    return sorted(glob.glob(os.path.join(folder, ext)), key=lambda f: os.stat(f).st_mtime, reverse=True)

# Универсальная функция
def read_excels(files, header_row=0):
    return [pd.read_excel(f, header=header_row) for f in files]

def find_dataframe_with_value(dfs, search):
    for df in dfs:
        if any(df.apply(lambda x: x.astype(str).str.contains(search, na=False)).any()):
            return df.copy()
    return None

def find_all_dataframes_with_value(dfs, search):
    return [df.copy() for df in dfs if any(df.apply(lambda x: x.astype(str).str.contains(search, na=False)).any())]

def find_cell_indices(df, value):
    location = np.where(df.values == value)
    return location

def find_column_by_value(df, value, offset=0):
    i, j = find_cell_indices(df, value)
    if len(j) == 0:
        raise ValueError(f"Не найдено значение '{value}' в таблице")
    return int(j[0] + offset)

def find_row_by_value(df, column, value):
    try:
        return df.index[df[column] == value][0]
    except IndexError:
        raise ValueError(f"Не найдена строка '{value}' в столбце '{column}'")

def safe_sum(series):
    return series.sum() if not series.empty else 0

def backup_file(source_file, backup_folder, prefix, now_str):
    os.makedirs(backup_folder, exist_ok=True)
    if os.path.exists(source_file):
        dest_file = os.path.join(backup_folder, f"{prefix} {now_str}.csv")
        shutil.copy(source_file, dest_file)

### --- Оригинальный БЛОК: Исходники --- ###
files = find_excel_files('Исходники')
if len(files) < 3:
    raise FileNotFoundError("Обнаружено файлов меньше трёх в папке 'Исходники'.")
dfs = read_excels(files[:3], header_row=0)

df_dtpp = find_dataframe_with_value(dfs, 'Движение товаров по поставщикам')
if df_dtpp is None:
    raise Exception("Не найден нужный отчёт 'Движение товаров по поставщикам'")
dfs_profit = find_all_dataframes_with_value(dfs, 'Валовая прибыль и стоимостная оценка')
if len(dfs_profit) < 2:
    raise Exception("Не найдено два отчёта о валовой прибыли")

col_ost_opt = find_column_by_value(df_dtpp, 'ОПТ', offset=2)
col_prk = find_column_by_value(df_dtpp, 'ПРК')
col_ost_prk = col_prk + 1
col_0 = df_dtpp.columns[0]
row_itogo = find_row_by_value(df_dtpp, col_0, 'Итого')

filtered_VED = df_dtpp[df_dtpp[col_0].astype(str).str.contains('ВЭД', na=False)]
sum_ostatki_VED = safe_sum(filtered_VED[df_dtpp.columns[col_ost_opt]])
sum_ostatki = df_dtpp.iloc[row_itogo, col_ost_opt]
sum_ostatki_RUS = sum_ostatki - sum_ostatki_VED
sum_real_prk = df_dtpp.iloc[row_itogo, col_prk]
sum_ost_prk = df_dtpp.iloc[row_itogo, col_ost_prk]
col_real_itogo = find_column_by_value(df_dtpp, 'Итого')
sum_real_itogo_VED = safe_sum(filtered_VED[df_dtpp.columns[col_real_itogo]])
sum_real_itogo = df_dtpp.iloc[row_itogo, col_real_itogo]
sum_real_RUS = sum_real_itogo - sum_real_itogo_VED

value0 = dfs_profit[0].iloc[3, 3]
value1 = dfs_profit[1].iloc[3, 3]
dates0 = re.findall(r'\d{2}\.\d{2}\.\d{4}', str(value0))
dates1 = re.findall(r'\d{2}\.\d{2}\.\d{4}', str(value1))
if len(dates0) >= 2:
    date1, date2 = pd.to_datetime(dates0, format='%d.%m.%Y')
elif len(dates1) >= 2:
    date1, date2 = pd.to_datetime(dates1, format='%d.%m.%Y')
else:
    raise Exception("Не удалось найти 2 даты для интервала")
if (date2 - date1).days > 0:
    df_week, df_day = dfs_profit[0], dfs_profit[1]
else:
    df_week, df_day = dfs_profit[1], dfs_profit[0]

col_rent = find_column_by_value(df_week, 'Рентабельность, %')
row_itogo_week = find_row_by_value(df_week, df_week.columns[0], 'Итого')
rent_value = df_week.iloc[row_itogo_week, col_rent]
col_viruch = find_column_by_value(df_day, 'Выручка, руб')
row_itogo_day = find_row_by_value(df_day, df_day.columns[0], 'Итого')
viruch_value = df_day.iloc[row_itogo_day, col_viruch]

# df_itog = pd.DataFrame([{
#     'продажи за день': int_r(viruch_value),
#     'прк продажи': int_r(sum_real_prk),
#     'Россия продажи': int_r(sum_real_RUS),
#     'ВЭД продажи': int_r(sum_real_itogo_VED),
#     'Ост розн': int_r(sum_ost_prk),
#     'Ост опт Рос': int_r(sum_ostatki_RUS),
#     'Ост опт ВЭД': int_r(sum_ostatki_VED),
#     'Ост общ опт': int_r(sum_ostatki),
#     'Рентабельность': rent_value
# }])
# print(df_itog)
now1 = datetime.now().strftime("%d-%m-%Y")
# df_itog.to_excel(f'для дашборда {now1}.xlsx', index=False)

source_file = 'commercial old.csv'
backup_file(source_file, 'БЭКАП', 'commercial', now1)

date_for_table = date2.strftime("%d.%m.%Y") if 'date2' in locals() else datetime.now().strftime("%d.%m.%Y")
def safe_int_div(a, b):
    return int_r(a * 30 / b) if b != 0 else 0
obor_rozn = safe_int_div(int_r(sum_ost_prk), int_r(sum_real_prk))
obor_opt = safe_int_div(int_r(sum_ostatki_RUS), int_r(sum_real_RUS))
obor_opt_VED = safe_int_div(int_r(sum_ostatki_VED), int_r(sum_real_itogo_VED))
rent_value_for_table = str(rent_value).replace('.', ',')

with open(source_file, 'a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    new_row = [
        date_for_table,
        obor_rozn,
        obor_opt,
        obor_opt_VED,
        int_r(viruch_value),
        int_r(sum_ost_prk),
        int_r(sum_ostatki_RUS),
        int_r(sum_ostatki_VED),
        int_r(sum_ostatki),
        rent_value_for_table
    ]
    writer.writerow(new_row)

### --- Новый блок: Исходники2 --- ###
files2 = find_excel_files('Исходники2')
if len(files2) < 3:
    raise FileNotFoundError("Обнаружено файлов меньше трёх в папке 'Исходники2'.")
dfs2 = read_excels(files2[:3], header_row=0)

df_mp = find_dataframe_with_value(dfs2, 'Продажи интернет-магазина')
if df_mp is None:
    raise Exception("Не найден нужный отчёт 'Продажи интернет-магазина' (Исходники2)")
df_ostatki = find_dataframe_with_value(dfs2, 'Сумма начальный остаток')
if df_ostatki is None:
    raise Exception("Не найден нужный отчёт 'Сумма начальный остаток' (Исходники2)")
df_prodaji = find_dataframe_with_value(dfs2, 'Показывать продажи: Кроме продаж между собственными юр. лицами')
if df_prodaji is None:
    raise Exception("Не найден нужный отчёт 'Показывать продажи: Кроме продаж между собственными юр. лицами' (Исходники2)")

#МП
col_prod_mp = find_column_by_value(df_mp, 'Сумма закупки', offset=0)
col_02 = df_mp.columns[0]
row_itogo2 = find_row_by_value(df_mp, col_02, 'Итого')

filtered_VED2 = df_mp[df_mp[col_02].astype(str).str.contains('ВЭД', na=False)]

sum_prod_mp_VED = safe_sum(filtered_VED2[df_mp.columns[col_prod_mp]])
sum_prod_mp = df_mp.iloc[row_itogo2, col_prod_mp]
sum_prod_mp_RUS = sum_prod_mp - sum_prod_mp_VED

#Остатки
col_ostatki_1 = find_column_by_value(df_ostatki, 'Сумма начальный остаток', offset=0)
col_ostatki_2 = find_column_by_value(df_ostatki, 'Сумма конечный остаток', offset=0)
col_03 = df_ostatki.columns[0]
row_itogo3 = find_row_by_value(df_ostatki, col_03, 'Итого')

filtered_VED3 = df_ostatki[df_ostatki[col_03].astype(str).str.contains('ВЭД', na=False)]

sum_ostatki_1_VED = safe_sum(filtered_VED3[df_ostatki.columns[col_ostatki_1]])
sum_ostatki_2_VED = safe_sum(filtered_VED3[df_ostatki.columns[col_ostatki_2]])
sum_ostatki_srednya_VED = (sum_ostatki_1_VED + sum_ostatki_2_VED)/2

sum_ostatki_1 = df_ostatki.iloc[row_itogo3, col_ostatki_1]
sum_ostatki_2 = df_ostatki.iloc[row_itogo3, col_ostatki_2]

sum_ostatki_1_RUS = sum_ostatki_1 - sum_ostatki_1_VED
sum_ostatki_2_RUS = sum_ostatki_2 - sum_ostatki_2_VED
sum_ostatki_srednya_RUS = (sum_ostatki_1_RUS + sum_ostatki_2_RUS)/2

#Продажи
col_prodaji = find_column_by_value(df_prodaji, 'Прибыль по закупочной', offset=-1) #ебать какой хитрый, столбец левее
col_04 = df_prodaji.columns[0]
row_itogo4 = find_row_by_value(df_prodaji, col_04, 'Итого')

filtered_VED4 = df_prodaji[df_prodaji[col_04].astype(str).str.contains('ВЭД', na=False)]

sum_prodaji_VED = safe_sum(filtered_VED4[df_prodaji.columns[col_prodaji]])
sum_prodaji = df_prodaji.iloc[row_itogo4, col_prodaji]
sum_prodaji_RUS = sum_prodaji - sum_prodaji_VED

#Оборачиваемость
obor_VED = (sum_ostatki_srednya_VED/(sum_prodaji_VED+sum_prod_mp_VED))*30
obor_RUS = (sum_ostatki_srednya_RUS/(sum_prodaji_RUS+sum_prod_mp_RUS))*30


df_itog2 = pd.DataFrame([{
    'продажи за день': int_r(viruch_value),
    'прк продажи': int_r(sum_real_prk),
    'Россия продажи': int_r(sum_real_RUS),
    'ВЭД продажи': int_r(sum_real_itogo_VED),
    'Ост розн': int_r(sum_ost_prk),
    'Ост опт Рос': int_r(sum_ostatki_RUS),
    'Ост опт ВЭД': int_r(sum_ostatki_VED),
    'Ост общ опт': int_r(sum_ostatki),
    'Рентабельность': rent_value,
    'Продажи2_РФ': int_r(sum_prodaji_RUS),
    'Продажи2_ВЭД': int_r(sum_prodaji_VED),
    'Продажи2МП_РФ': int_r(sum_prod_mp_RUS),
    'Продажи2МП_ВЭД': int_r(sum_prod_mp_VED),
    'Остатки2_РФ': int_r(sum_ostatki_srednya_RUS),
    'Остатки2_ВЭД': int_r(sum_ostatki_srednya_VED),
    'Обор2_РФ': int_r(obor_RUS),
    'Обор2_ВЭД': int_r(obor_VED)


}])
print(df_itog2)
now2 = datetime.now().strftime("%d-%m-%Y")
df_itog2.to_excel(f'для дашборда new {now2}.xlsx', index=False)

source_file2 = 'commercial.csv'
backup_file(source_file2, 'БЭКАП', 'commercial new', now2)

# date_for_table2 = date2_2.strftime("%d.%m.%Y") if 'date2_2' in locals() else datetime.now().strftime("%d.%m.%Y")
# def safe_int_div2(a, b):
#     return int_r(a * 30 / b) if b != 0 else 0
# obor_rozn2 = safe_int_div2(int_r(sum_ost_prk2), int_r(sum_real_prk2))
# obor_opt2 = safe_int_div2(int_r(sum_prod_mp_RUS), int_r(sum_real_RUS2))
# obor_opt_VED2 = safe_int_div2(int_r(sum_prod_mp_VED), int_r(sum_real_itogo_VED2))
# rent_value_for_table2 = str(rent_value2).replace('.', ',')

with open(source_file2, 'a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    new_row2 = [
        date_for_table,
        obor_rozn,
        int_r(obor_RUS),
        int_r(obor_VED),
        int_r(viruch_value),
        int_r(sum_ost_prk),
        int_r(sum_ostatki_RUS),
        int_r(sum_ostatki_VED),
        int_r(sum_ostatki),
        rent_value_for_table
    ]
    writer.writerow(new_row2)

