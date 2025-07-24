import pandas as pd
import numpy as np
import os

def process_excel_file():
    print("⚙️ Обработка Excel-файла выгрузки из 1С")

    # Ввод пути к файлу
    input_path = input("Введите путь к Excel-файлу (.xlsx): ").strip('"')

    if not os.path.exists(input_path):
        print("❌ Указанный файл не найден.")
        return

    try:
        # Загрузка данных
        df = pd.read_excel(input_path)
        df = df.drop(range(0, 12)).reset_index(drop=True)

        # Удаление пустых столбцов
        empty_cols = df.columns[df.isna().all()].tolist()
        df = df.drop(columns=empty_cols)

        # Заполнение нужных столбцов (если структура совпадает)
        columns_to_ffill = [
            'В отчет выведены результаты предварительного закрытия месяца. \nПосле выполнения окончательного закрытия месяца результат может измениться.',
            'Unnamed: 3',
            'Unnamed: 4'
        ]
        df[columns_to_ffill] = df[columns_to_ffill].ffill()

        # Фильтрация строк, где все значения в этих столбцах — NaN
        cols_to_check = ['Unnamed: 5', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13']
        df = df[~df[cols_to_check].isna().all(axis=1)]

        # Переименование столбцов
        rename_map = {
            'В отчет выведены результаты предварительного закрытия месяца. \nПосле выполнения окончательного закрытия месяца результат может измениться.':'Период, квартал',
            'Unnamed: 3': 'Период, неделя',
            'Unnamed: 4': 'Период, день',
            'Unnamed: 5': 'Заказ клиента / Реализация',
            'Unnamed: 9': 'Дата',
            'Unnamed: 10': 'Номер',
            'Unnamed: 11': 'БГ35',
            'Unnamed: 12': 'Номенклатура.Артикул',
            'Unnamed: 13': 'Номенклатура.Наименование для печати',
            'Unnamed: 14': 'Количество',
            'Unnamed: 15': 'Выручка',
            'Unnamed: 16': 'Выручка НДС',
            'Unnamed: 17': 'Выручка (с НДС)',
            'Unnamed: 18': 'Себестоимость товаров, всего',
            'Unnamed: 19': 'Себестоимость товаров, Стоимость закупки',
            'Unnamed: 20': 'Себестоимость товаров, доп расходы',
            'Unnamed: 21': 'Валовая прибыль',
            'Unnamed: 22': 'Рентабельность, %'
        }
        df = df.rename(columns=rename_map)

        # Отображение БГ35 на БЕ
        mapping = {
            'F+B2B_DATA_CPU': 'F+B2B_DATA',
            'F+B2B_DATA_DDR': 'F+B2B_DATA',
            'F+B2B_DATA_NET': 'F+B2B_DATA',
            'F+B2B_DATA_OEM': 'F+B2B_DATA',
            'F+B2B_DATA_options': 'F+B2B_DATA',
            'F+B2B_DATA_R': 'F+B2B_DATA',
            'F+B2B_DATA_RnD': 'F+B2B_DATA',
            'F+B2B_DATA_SSD_HDD': 'F+B2B_DATA',
            'F+B2B_DATA_storage_R': 'F+B2B_DATA',
            'F+B2B_DATA_x86_R': 'F+B2B_DATA',
            'F+B2B_Huawei_XF_OEM': 'F+B2B_DATA',
            'F+B2B_Imaging_OEM': 'F+B2B_Imaging',
            'F+B2B_Imaging_toners': 'F+B2B_Imaging',
            'F+B2B_LCD_R': 'F+B2B_PRO',
            'F+B2B_Networks_BOM': 'F+B2B_Networks',
            'F+B2B_Networks_OEM': 'F+B2B_Networks',
            'F+B2B_PRO_NB_R': 'F+B2B_PRO',
            'F+B2B_PRO_PC_R': 'F+B2B_PRO',
            'F+B2B_PRO_phones_OEM': 'F+B2B_PRO',
            'F+B2B_PRO_phones_R': 'F+B2B_PRO',
            'F+B2B_PRO_Tablet_OEM': 'F+B2B_PRO',
            'F+B2B_PRO_Tablet_R': 'F+B2B_PRO',
            'F+B2C_LTP': 'F+B2C',
            'F+B2C_Accesstyle_CE': 'F+B2C',
            'F+B2B_Networks_Wifi': 'F+B2B_Networks',
            'F+B2B_PRO_NB_OEM': 'F+B2B_PRO',
            'F+B2B_DATA_BOM': 'F+B2B_DATA',
            'F+B2B_DATA': 'F+B2B_DATA',
            '': 'F+B2B_DATA',
        }

        df['БЕ'] = df['БГ35'].map(mapping)

        # Сохранение файла
        dir_name = os.path.dirname(input_path)
        output_path = os.path.join(dir_name, 'Валовая прибыль (обработано).xlsx')
        df.to_excel(output_path, index=False)

        print(f"✅ Файл успешно обработан и сохранён: {output_path}")

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")

# Запуск
if __name__ == "__main__":
    process_excel_file()
