import pandas as pd
import os

def split_excel_sheets():
    input_file = input("Введите путь к Excel файлу (*.xlsx): ").strip()
    if not os.path.isfile(input_file):
        print("Файл не найден.")
        return

    output_dir = input("Введите путь к папке для сохранения листов: ").strip()
    if not os.path.isdir(output_dir):
        print("Папка не найдена.")
        return

    try:
        xls = pd.read_excel(input_file, sheet_name=None)

        for sheet_name, df in xls.items():
            safe_name = "".join(c for c in sheet_name if c not in r'<>:"/\|?*')
            output_path = os.path.join(output_dir, f"{safe_name}.xlsx")
            df.to_excel(output_path, index=False)
            print(f"Сохранено: {output_path}")

        print("\n✅ Все листы успешно сохранены.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    split_excel_sheets()
