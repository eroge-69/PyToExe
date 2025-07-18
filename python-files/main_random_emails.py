import pandas as pd
import random
import re
import os
import subprocess
import sys
import glob


def install_package(package):
    """Автоматически устанавливает недостающий пакет"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def check_and_install_dependencies():
    """Проверяет и устанавливает необходимые зависимости"""
    try:
        import openpyxl
    except ImportError:
        print("Установка недостающих зависимостей openpyxl...")
        install_package("openpyxl")
        print("openpyxl успешно установлен!")


def find_files_in_directory():
    """
    Ищет все CSV и Excel файлы в текущей папке
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Ищем файлы с нужными расширениями
    csv_files = glob.glob(os.path.join(current_dir, "*.csv"))
    xlsx_files = glob.glob(os.path.join(current_dir, "*.xlsx"))
    xls_files = glob.glob(os.path.join(current_dir, "*.xls"))

    # Объединяем все файлы
    all_files = csv_files + xlsx_files + xls_files

    # Оставляем только имена файлов без пути
    file_names = [os.path.basename(f) for f in all_files]

    return file_names


def select_file():
    """
    Позволяет пользователю выбрать файл из списка
    """
    files = find_files_in_directory()

    if not files:
        print("❌ В текущей папке не найдено файлов CSV или Excel!")
        print("Убедитесь, что файлы находятся в той же папке, что и скрипт.")
        return None

    print(f"📁 Найдено {len(files)} файл(ов) в папке:")
    print("-" * 50)

    for i, file in enumerate(files, 1):
        file_size = os.path.getsize(file)
        file_size_mb = file_size / (1024 * 1024)
        print(f"{i}. {file} ({file_size_mb:.2f} MB)")

    print("-" * 50)

    while True:
        try:
            choice = input(f"Выберите номер файла (1-{len(files)}): ")
            choice_num = int(choice)

            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num - 1]
                print(f"✅ Выбран файл: {selected_file}")
                return selected_file
            else:
                print(f"❌ Введите число от 1 до {len(files)}")

        except ValueError:
            print("❌ Введите корректное число")


def find_email_column(df):
    """
    Автоматически находит столбец с email адресами
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    for column in df.columns:
        # Проверяем первые несколько строк на наличие email
        sample_data = df[column].dropna().head(10).astype(str)
        email_count = sum(1 for value in sample_data if re.search(email_pattern, value))

        # Если больше половины значений похожи на email, считаем это email столбцом
        if email_count > len(sample_data) * 0.5:
            return column

    return None


def extract_emails_from_text(text):
    """
    Извлекает email из текста (на случай если в ячейке есть дополнительный текст)
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, str(text))
    return emails[0] if emails else None


def read_file_safely(filename):
    """
    Безопасное чтение файла с обработкой ошибок зависимостей
    """
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(filename)
        elif filename.endswith(('.xlsx', '.xls')):
            # Проверяем и устанавливаем openpyxl при необходимости
            check_and_install_dependencies()
            return pd.read_excel(filename)
        else:
            raise ValueError("Поддерживаются только файлы CSV и Excel (.xlsx, .xls)")
    except ImportError as e:
        if "openpyxl" in str(e):
            print("Устанавливаю необходимую зависимость...")
            check_and_install_dependencies()
            return pd.read_excel(filename)
        else:
            raise e


def main():
    print("🔍 Поиск файлов для обработки email адресов")
    print("=" * 60)

    try:
        # Позволяем пользователю выбрать файл
        filename = select_file()

        if filename is None:
            return

        # Читаем выбранный файл
        df = read_file_safely(filename)

        print(f"\n📊 Файл '{filename}' успешно загружен. Строк: {len(df)}")
        print(f"📋 Столбцы в файле: {list(df.columns)}")

        # Автоматически находим столбец с email
        email_column = find_email_column(df)

        if email_column is None:
            print("\n❌ Ошибка: Не удалось найти столбец с email адресами.")
            print("Убедитесь, что в таблице есть столбец с корректными email адресами.")
            return

        print(f"✅ Найден столбец с email: '{email_column}'")

        # Создаем копию DataFrame для работы с email
        df_with_emails = df.copy()

        # Извлекаем и очищаем email адреса
        df_with_emails['clean_email'] = df_with_emails[email_column].apply(
            lambda x: extract_emails_from_text(x) if pd.notna(x) else None
        )

        # Удаляем строки без корректных email
        df_with_emails = df_with_emails[df_with_emails['clean_email'].notna()]

        # Удаляем дубликаты по email
        df_unique = df_with_emails.drop_duplicates(subset=['clean_email'])

        total_emails = len(df_unique)

        print(f"📧 Найдено уникальных email адресов: {total_emails}")

        if total_emails == 0:
            print("❌ Ошибка: В файле не найдено корректных email адресов.")
            return

        # Запрашиваем количество случайных email
        print("\n" + "=" * 40)
        while True:
            try:
                requested_count = int(input(f"Сколько случайных записей нужно выбрать? (максимум {total_emails}): "))

                if requested_count <= 0:
                    print("❌ Ошибка: Количество должно быть больше 0.")
                    continue
                elif requested_count > total_emails:
                    print(
                        f"❌ Ошибка: Запрошено {requested_count} записей, но в файле только {total_emails} уникальных email адресов.")
                    continue
                else:
                    break

            except ValueError:
                print("❌ Ошибка: Введите корректное число.")

        # Выбираем случайные строки
        random_rows = df_unique.sample(n=requested_count, random_state=random.randint(1, 10000))

        # Удаляем служебный столбец clean_email
        result_df = random_rows.drop('clean_email', axis=1)

        # Сбрасываем индекс
        result_df = result_df.reset_index(drop=True)

        # Генерируем имена выходных файлов
        base_name = os.path.splitext(filename)[0]
        output_filename_csv = f"{base_name}_random_emails.csv"
        output_filename_excel = f"{base_name}_random_emails.xlsx"

        # Сохраняем файлы в стандартном формате
        print("\n💾 Сохранение файлов...")

        # Сохраняем CSV
        result_df.to_csv(output_filename_csv, index=False, encoding='utf-8-sig')

        # Сохраняем Excel
        check_and_install_dependencies()
        result_df.to_excel(output_filename_excel, index=False)

        print(f"\n🎉 Готово! Выбрано {requested_count} случайных записей.")
        print(f"💾 Создано 2 файла:")
        print(f"   📄 CSV: '{output_filename_csv}'")
        print(f"   📊 Excel: '{output_filename_excel}'")

        print(f"\n📋 Сохранены столбцы: {list(result_df.columns)}")
        print(f"\n📋 Первые несколько записей из результата:")
        print(result_df.head(min(5, len(result_df))))

    except Exception as e:
        print(f"❌ Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main()
