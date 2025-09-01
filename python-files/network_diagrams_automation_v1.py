import win32com.client
import os
import argparse
from datetime import datetime
import logging
import pythoncom
import re
import glob


def setup_directories():
    """Создает необходимые папки, если они не существуют"""
    directories = [
        'templates',
        'templates/archive',
        'templates/current',
        'data',
        'data/processed',
        'data/archive',
        'data/raw_archive',
        'output',
        'output/archive',
        'output/current',
        'logs'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def setup_logging():
    """Настройка логирования"""
    log_file = os.path.join('logs', 'visio_processor.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )


def initialize_com():
    """Инициализация COM для многопоточных сред"""
    try:
        pythoncom.CoInitialize()
    except:
        pass


def uninitialize_com():
    """Деинициализация COM"""
    try:
        pythoncom.CoUninitialize()
    except:
        pass


def generate_empty_device_data():
    """Генерирует содержимое файла device_path_data с пустыми ключами для dev1-dev20"""
    content = "# Формат данных для устройств:\n"
    content += "# Вы можете использовать один из двух форматов:\n"
    content += "# 1. Пары 'ключ=значение' (рекомендуется) - просто заполните значения после знака =\n"
    content += "# 2. Блоки по 6 строк на устройство (для обратной совместимости)\n\n"
    content += "# Пустые ключи для заполнения (формат 'ключ=значение'):\n\n"

    for i in range(1, 21):
        content += f"dev{i}_pl=PL{i}\n"
        content += f"dev{i}_geograph_address=\n"
        content += f"dev{i}_ip=\n"
        content += f"dev{i}_nioss_name=\n"
        content += f"dev{i}_vendor_model=\n"
        content += f"dev{i}_uplink=\n"
        content += f"dev{i}_downlink=\n\n"

    content += "# Пример данных в формате ключ=значение:\n"
    content += "# dev1_geograph_address=ул. Вагонная, 13/3, п. 1 [г. Комсомольск-на-Амуре]\n"
    content += "# dev1_ip=10.220.190.186\n"
    content += "# dev1_nioss_name=ETH__108\n"
    content += "# dev1_vendor_model=Huawei Quidway S2326TP-EI\n"
    content += "# dev1_uplink=GE0/0/1\n"
    content += "# dev1_downlink=Eth0/0/1\n\n"
    content += "# Пример данных в блочном формате (6 строк на устройство):\n"
    content += "# ул. Вагонная, 13/3, п. 1 [г. Комсомольск-на-Амуре]\n"
    content += "# 10.220.190.186\n"
    content += "# ETH__108\n"
    content += "# Huawei Quidway S2326TP-EI\n"
    content += "# GE0/0/1\n"
    content += "# Eth0/0/1\n"

    return content


def ensure_data_files():
    """Проверяет наличие файлов данных и создает их при первом запуске"""
    # Проверяем и создаем файл engineer_data при первом запуске
    engineer_data_path = os.path.join('data', 'engineer_data.txt')
    if not os.path.exists(engineer_data_path):
        engineer_data = {}
        engineer_data['pskk_engineer_name'] = input("ФИО инженера: ")
        engineer_data['pskk_engineer_mobile_phone_number'] = input("Мобильный телефон инженера: ")
        engineer_data['pskk_engineer_ip_phone_number'] = input("Внутренний телефон инженера: ")

        # Сохраняем данные в файл
        with open(engineer_data_path, 'w', encoding='utf-8') as f:
            for key, value in engineer_data.items():
                f.write(f"{key}={value}\n")

    # Проверяем и создаем файл client_data при первом запуске
    client_data_path = os.path.join('data', 'client_data.txt')
    if not os.path.exists(client_data_path):
        create_default_client_data()

    # Проверяем и создаем файл device_path_data при первом запуске
    device_data_path = os.path.join('data', 'device_path_data.txt')
    if not os.path.exists(device_data_path):
        with open(device_data_path, 'w', encoding='utf-8') as f:
            f.write(generate_empty_device_data())


def create_default_client_data():
    """Создает файл client_data.txt с ключами по умолчанию"""
    client_data_path = os.path.join('data', 'client_data.txt')

    default_data = {
        'client_name': '',
        'client_geograph_address': '',
        'rnr_number': '',
        'channel_bandwidth': '',
        'contract_number': '',
        'qos_ts': '',
        'tpo_number': '',
        'STAG': '',
        'CTAG': '',
        'port_mode': '',
        'contact_name': '',
        'contact_phone': '',
        'opening_hours': ''
    }

    with open(client_data_path, 'w', encoding='utf-8') as f:
        for key, value in default_data.items():
            f.write(f"{key}={value}\n")

    return client_data_path


def detect_data_format(content):
    """Определяет формат данных в файле device_path_data"""
    lines = content.split('\n')

    # Проверяем, есть ли строки в формате ключ=значение
    key_value_lines = 0
    total_lines = 0

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            total_lines += 1
            if '=' in line:
                key_value_lines += 1

    # Если больше половины некомментированных строк содержат '=', считаем что это формат ключ=значение
    if total_lines > 0 and key_value_lines / total_lines > 0.5:
        return 'key_value'
    else:
        return 'block'


def parse_key_value_device_data(content):
    """Парсит данные устройств в формате ключ=значение"""
    device_data = {}

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Добавляем только ключи устройств (devX_*)
            if key.startswith('dev') and '_' in key:
                device_data[key] = value

    return device_data


def parse_device_data(raw_data):
    """Парсит сырые данные об устройствах в блочном формате и возвращает словарь с ключами"""
    device_dict = {}

    # Удаляем комментарии и разбиваем на строки
    lines = []
    for line in raw_data.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
            lines.append(line)

    # Определяем количество устройств (каждое устройство имеет 6 строк данных)
    num_devices = len(lines) // 6
    if len(lines) % 6 != 0:
        logging.warning(f"Некорректное количество строк данных: {len(lines)}. Ожидается кратное 6.")

    # Обрабатываем устройства в обратном порядке (последнее устройство = dev1)
    for i in range(num_devices):
        dev_num = num_devices - i  # Обратная нумерация: последнее устройство = dev1
        start_idx = i * 6

        # Извлекаем данные для устройства
        if start_idx + 5 < len(lines):
            geograph_address = lines[start_idx]
            ip = lines[start_idx + 1]
            nioss_name = lines[start_idx + 2]
            vendor_model = lines[start_idx + 3]
            uplink = lines[start_idx + 4]
            downlink = lines[start_idx + 5]

            # Добавляем в словарь
            device_dict[f'dev{dev_num}_pl'] = f"PL{dev_num}"
            device_dict[f'dev{dev_num}_geograph_address'] = geograph_address
            device_dict[f'dev{dev_num}_ip'] = ip
            device_dict[f'dev{dev_num}_nioss_name'] = nioss_name
            device_dict[f'dev{dev_num}_vendor_model'] = vendor_model
            device_dict[f'dev{dev_num}_uplink'] = uplink
            device_dict[f'dev{dev_num}_downlink'] = downlink

    return device_dict


def parse_data_file(file_path):
    """Парсит файл с данными в формате ключ=значение"""
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Если это файл с данными устройств, парсим особым образом
            if 'device_path_data' in file_path:
                # Определяем формат данных
                data_format = detect_data_format(content)

                if data_format == 'key_value':
                    print("Обнаружен формат 'ключ=значение' в device_path_data.txt")
                    device_data = parse_key_value_device_data(content)
                else:
                    print("Обнаружен блочный формат в device_path_data.txt")
                    # Спросим пользователя о формате
                    choice = input(
                        "Хотите использовать блочный формат (b) или преобразовать в ключ=значение (k)? [b/k]: ").lower().strip()

                    if choice == 'k':
                        print("Преобразование данных в формат 'ключ=значение'...")
                        device_data = parse_key_value_device_data(content)
                    else:
                        device_data = parse_device_data(content)

                data.update(device_data)
            else:
                # Стандартный парсинг для других файлов
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        data[key] = value

    except Exception as e:
        logging.error(f"Ошибка при чтении файла данных: {e}")
    return data


def load_all_data():
    """Загружает данные из всех трех файлов и объединяет их"""
    data = {}

    # Файлы данных
    data_files = {
        'device': os.path.join('data', 'device_path_data.txt'),
        'engineer': os.path.join('data', 'engineer_data.txt'),
        'client': os.path.join('data', 'client_data.txt')
    }

    # Загружаем данные из каждого файл
    for data_type, file_path in data_files.items():
        if os.path.exists(file_path):
            file_data = parse_data_file(file_path)
            data.update(file_data)

    return data


def get_available_templates():
    """Возвращает список доступных шаблонов в папке templates/current"""
    templates = []
    template_dir = os.path.join('templates', 'current')

    if os.path.exists(template_dir):
        for ext in ['*.vstx', '*.vsdx', '*.vst']:
            templates.extend(glob.glob(os.path.join(template_dir, ext)))

    return templates


def select_template_interactively(available_templates):
    """Интерактивный выбор шаблонов из списка доступных"""
    if not available_templates:
        return None

    if len(available_templates) == 1:
        print(f"Найден один шаблон: {os.path.basename(available_templates[0])}")
        return available_templates[0]

    print("\nДоступные шаблоны:")
    for i, template_path in enumerate(available_templates, 1):
        print(f"{i}. {os.path.basename(template_path)}")

    while True:
        try:
            choice = input("\nВыберите номер шаблона (или 'q' для выхода): ")

            if choice.lower() == 'q':
                return None

            choice_idx = int(choice) - 1

            if 0 <= choice_idx < len(available_templates):
                return available_templates[choice_idx]
            else:
                print(f"Пожалуйста, введите число от 1 до {len(available_templates)}")

        except ValueError:
            print("Пожалуйста, введите корректный номер")


def ask_for_restart():
    """Спрашивает пользователя, хочет ли он запустить скрипт снова"""
    while True:
        choice = input("\nХотите запустить скрипт снова? (y/n): ").lower().strip()

        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("Пожалуйста, введите 'y' или 'n'")


def clean_filename(text):
    """Очищает текст для использования в имени файла"""
    # Заменяем двойные кавычки на одинарные
    text = text.replace('"', "'")

    # Удаляем недопустимые символы для имен файлов
    text = re.sub(r'[<>:"/\\|?*]', '', text)

    # Удаляем начальные и конечные пробелы
    text = text.strip()

    return text


def format_filename(data_dict):
    """Форматирует имя файла в формате: client_name, client_geograph_address, дата и время"""
    client_name = data_dict.get('client_name', 'unknown')
    client_address = data_dict.get('client_geograph_address', 'unknown')

    # Очищаем имена от недопустимых символов
    clean_client_name = clean_filename(client_name)
    clean_client_address = clean_filename(client_address)

    # Получаем текущую дату и время
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    # Формируем имя файла
    filename = f"{clean_client_name}, {clean_client_address}, {timestamp}"

    return filename


def replace_text_in_object(obj, data_dict, obj_type="фигура"):
    """Заменяет заполнители в тексте объекта (фигуры или страницы)"""
    replacements_count = 0
    try:
        # Безопасная проверка наличия текста у объекта
        if hasattr(obj, 'Text'):
            try:
                original_text = obj.Text
                if not original_text or not isinstance(original_text, str):
                    return 0

                updated_text = original_text

                # Ищем все заполнители в тексте
                placeholders = re.findall(r'\{\{([^}]+)\}\}', original_text)

                for placeholder in placeholders:
                    # Ищем соответствующий ключ в данных
                    if placeholder in data_dict:
                        value = data_dict[placeholder]
                        # Заменяем полный заполнитель {{...}} на значение
                        updated_text = updated_text.replace(f'{{{{{placeholder}}}}}', value)
                        replacements_count += 1

                # Применение измененного текста
                if updated_text != original_text:
                    obj.Text = updated_text
            except Exception as text_error:
                pass

        # Обработка ячеек данных фигуры
        if hasattr(obj, 'SectionExists') and obj_type == "фигура":
            try:
                if obj.SectionExists(3):  # 3 = visSectionObject (данные фигуры)
                    for j in range(1, obj.RowCount(3) + 1):
                        try:
                            cell = obj.CellsSRC(3, j, 0)  # Значение
                            if hasattr(cell, 'Formula'):
                                formula = cell.Formula

                                # Ищем заполнители в формуле
                                placeholders = re.findall(r'\{\{([^}]+)\}\}', formula)

                                for placeholder in placeholders:
                                    # Ищем соответствующий ключ в данных
                                    if placeholder in data_dict:
                                        value = data_dict[placeholder]
                                        # Заменяем полный заполнитель {{...}} на значение
                                        new_formula = formula.replace(f'{{{{{placeholder}}}}}', value)
                                        cell.Formula = new_formula
                                        replacements_count += 1
                        except Exception as cell_error:
                            continue
            except Exception as section_error:
                pass

    except Exception as e:
        pass

    return replacements_count


def update_visio_template(template_path, output_path, data_dict):
    """
    Обновляет Visio шаблон, заменяя заполнители на реальные данные
    с улучшенной обработкой ошибок
    """
    visio = None
    doc = None
    total_replacements = 0

    try:
        # Открытие Visio и шаблона
        visio = win32com.client.Dispatch("Visio.Application")
        visio.Visible = False  # Скрыть окно Visio

        # Получаем абсолютные пути для избежания проблем с путями
        template_path = os.path.abspath(template_path)
        output_path = os.path.abspath(output_path)

        # Проверяем существование шаблона
        if not os.path.exists(template_path):
            logging.error(f"Файл шаблона не найден: {template_path}")
            return False, 0

        doc = visio.Documents.Open(template_path)

        # Обход всех страниц документа
        for page in doc.Pages:
            # Обработка текста непосредственно на странице (вне фигур)
            page_replacements = replace_text_in_object(page, data_dict, "страница")
            total_replacements += page_replacements

            # Обход всех фигур на странице
            shapes_count = page.Shapes.Count
            for i in range(1, shapes_count + 1):
                try:
                    shape = page.Shapes.Item(i)
                    shape_replacements = replace_text_in_object(shape, data_dict, "фигура")
                    total_replacements += shape_replacements

                    # Рекурсивная обработка фигур в группах
                    if hasattr(shape, 'Type') and shape.Type == 2:  # 2 = visTypeGroup
                        for j in range(1, shape.Shapes.Count + 1):
                            try:
                                sub_shape = shape.Shapes.Item(j)
                                sub_replacements = replace_text_in_object(sub_shape, data_dict, "подфигура")
                                total_replacements += sub_replacements
                            except Exception as sub_shape_error:
                                continue

                except Exception as shape_error:
                    continue

        # Сохранение измененного документа
        doc.SaveAs(output_path)

        # Закрытие
        doc.Close()
        visio.Quit()

        return True, total_replacements

    except Exception as e:
        logging.error(f"Ошибка при обработке Visio документа: {e}")
        # Всегда пытаемся закрыть приложение в случае ошибки
        try:
            if doc:
                doc.Close()
        except:
            pass
        try:
            if visio:
                visio.Quit()
        except:
            pass
        return False, total_replacements


def archive_and_recreate_data_files(data_dict):
    """Архивирует исходные файлы и создает новые с теми же именами"""
    try:
        # Формируем базовое имя файла для архива
        base_filename = format_filename(data_dict)

        # Файлы данных для архивации
        data_files = {
            'device': os.path.join('data', 'device_path_data.txt'),
            'engineer': os.path.join('data', 'engineer_data.txt'),
            'client': os.path.join('data', 'client_data.txt')
        }

        # Архивируем каждый файл
        for data_type, file_path in data_files.items():
            if os.path.exists(file_path):
                # Читаем исходное содержимое
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                # Сохраняем оригинальное содержимое в raw_archive
                raw_archive_filename = f"{base_filename}_{data_type}_raw.txt"
                raw_archive_path = os.path.join('data', 'raw_archive', raw_archive_filename)

                with open(raw_archive_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Для device файла также сохраняем преобразованные данные
                if data_type == 'device':
                    # Определяем формат и парсим данные
                    data_format = detect_data_format(original_content)
                    if data_format == 'key_value':
                        parsed_data = parse_key_value_device_data(original_content)
                    else:
                        parsed_data = parse_device_data(original_content)

                    parsed_content = "\n".join([f"{k}={v}" for k, v in parsed_data.items()])

                    parsed_archive_filename = f"{base_filename}_{data_type}_parsed.txt"
                    parsed_archive_path = os.path.join('data', 'archive', parsed_archive_filename)

                    with open(parsed_archive_path, 'w', encoding='utf-8') as f:
                        f.write(parsed_content)

                # Перемещаем оригинальный файл в архив
                archive_filename = f"{base_filename}_{data_type}.txt"
                archive_path = os.path.join('data', 'archive', archive_filename)

                os.rename(file_path, archive_path)

        # Создаем новые файлы с теми же именами
        # 1. Engineer data - копируем из архива (сохраняем данные инженера)
        engineer_archive_path = os.path.join('data', 'archive', f"{base_filename}_engineer.txt")
        if os.path.exists(engineer_archive_path):
            with open(engineer_archive_path, 'r', encoding='utf-8') as src:
                with open(data_files['engineer'], 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

        # 2. Client data - создаем с ключами по умолчанию
        create_default_client_data()

        # 3. Device path data - создаем файл с пустыми ключами
        with open(data_files['device'], 'w', encoding='utf-8') as f:
            f.write(generate_empty_device_data())

    except Exception as e:
        logging.error(f"Ошибка при архивации и создании файлов: {e}")


def process_single_run():
    """Обрабатывает один запуск скрипта"""
    # Получаем список доступных шаблонов
    available_templates = get_available_templates()

    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Автоматическое заполнение шаблонов Visio')
    parser.add_argument('--template', help='Путь к файлу шаблона')
    parser.add_argument('--output', help='Путь для сохранения результата')

    args = parser.parse_args()

    # Если шаблон не указан, предлагаем выбрать интерактивно
    if not args.template:
        if not available_templates:
            logging.error("Не найден ни один шаблон в папке templates/current")
            print("Ошибка: Не найден ни один шаблон в папке templates/current")
            print("Пожалуйста, поместите шаблоны в папку templates/current и запустите скрипт снова.")
            return False, None, 0

        selected_template = select_template_interactively(available_templates)

        if not selected_template:
            print("Работа скрипта прервана пользователем.")
            return False, None, 0

        args.template = selected_template
        print(f"Выбран шаблон: {os.path.basename(args.template)}")

    # Проверка существования шаблона
    if not os.path.exists(args.template):
        logging.error(f"Файл шаблона не найден: {args.template}")
        print(f"Ошибка: Файл шаблона не найден: {args.template}")
        return False, None, 0

    # Загрузка данных из всех файлов
    print("Загрузка данных из файлов...")
    data_dict = load_all_data()

    if not data_dict:
        logging.error("Не удалось загрузить данные из файлов")
        print("Ошибка: Не удалось загрузить данные из файлов")
        return False, None, 0

    print(f"Загружено {len(data_dict)} записей из файлов данных")

    # Определение пути для выходного файла
    if not args.output:
        # Формируем имя файла
        base_filename = format_filename(data_dict)
        output_filename = f"{base_filename}.vsdx"
        args.output = os.path.join('output', 'current', output_filename)

    # Обновление шаблона
    print("Обновление шаблона Visio...")
    success, replacements_count = update_visio_template(args.template, args.output, data_dict)

    if success:
        if replacements_count > 0:
            print(f"\n✓ Процесс завершен успешно!")
            print(f"✓ Выполнено замен: {replacements_count}")
            print(f"✓ Файл сохранен как: {args.output}")

            # Архивируем файлы данных и создаем новые
            archive_and_recreate_data_files(data_dict)
            print("✓ Файлы данных архивированы и созданы новые файлы для следующего использования")

            return True, args.output, replacements_count
        else:
            print("Процесс завершен, но замен не выполнено. Проверьте шаблон и данные.")
            return True, args.output, 0
    else:
        print("Произошла ошибка при обработке. Проверьте лог-файл для получения подробной информации.")
        return False, None, 0


def main():
    """Основная функция"""
    # Инициализация COM
    initialize_com()

    try:
        # Настройка папок и логирования
        setup_directories()
        setup_logging()

        # Проверяем и создаем файлы данных при первом запуске
        ensure_data_files()

        # Основной цикл выполнения
        while True:
            # Выполняем один запуск скрипта
            success, output_path, replacements_count = process_single_run()

            # Спрашиваем, хочет ли пользователь запустить скрипт снова
            if not ask_for_restart():
                break

            print("\n" + "=" * 50)
            print("Запуск скрипта снова...")
            print("=" * 50 + "\n")

    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        print(f"Критическая ошибка: {e}")

    finally:
        # Всегда деинициализируем COM
        uninitialize_com()
        print("Работа скрипта завершена.")


if __name__ == "__main__":
    main()
