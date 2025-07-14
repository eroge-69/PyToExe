import os
import openpyxl

def create_excel_from_filenames_no_extension(directory=".", filename="filenames_no_ext.xlsx"):

    try:
        filenames = os.listdir(directory)
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        row = 1

        for filename_item in filenames:
            name, ext = os.path.splitext(filename_item)  # Разделяем имя и расширение
            sheet.cell(row=row, column=1, value=name)  # Записываем только имя
            row += 1

        workbook.save(filename)
        print(f"Excel-файл '{filename}' успешно создан.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    create_excel_from_filenames_no_extension()