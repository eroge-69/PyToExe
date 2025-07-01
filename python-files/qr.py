import os
import json
from bs4 import BeautifulSoup
import sys
from collections import defaultdict
from datetime import datetime
import zipfile
try:
    from pylibdmtx.pylibdmtx import encode
    from PIL import Image
    HAS_DATAMATRIX_LIBS = True
except ImportError:
    HAS_DATAMATRIX_LIBS = False

def extract_gtin(sgtin):
    """Извлекаем GTIN (первые 14 символов)"""
    return sgtin[:14] if len(sgtin) >= 14 else sgtin

def load_source_data(filepath, selected_groups):
    """Загружаем и парсим исходные данные"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Ищем первый ключ в data['data'], который содержит XML
        xml_content = None
        for key in data['data']:
            if isinstance(data['data'][key], str) and '<' in data['data'][key]:
                xml_content = data['data'][key]
                break

        if not xml_content:
            print("Ошибка: Не найдены XML данные в файле")
            return None

        soup = BeautifulSoup(xml_content, 'lxml-xml')

        # Собираем все SGTIN и их GTIN
        sgtins = []
        found_groups = set()

        for section in selected_groups:
            section_tag = soup.find(section)
            if section_tag:
                found_groups.add(section)
                sgtins.extend((sgtin.text.strip(), extract_gtin(sgtin.text.strip()))
                    for sgtin in section_tag.find_all('sgtin'))

        # Проверяем, были ли найдены запрошенные группы
        not_found_groups = set(selected_groups) - found_groups
        if not_found_groups:
            print(f"Предупреждение: В исходном файле не найдены данные для групп: {', '.join(not_found_groups)}")

        if not sgtins:
            print("Ошибка: Не найдены SGTIN ни в одной из выбранных групп")
            return None

        return sgtins

def process_xml_files(script_dir, source_gtins, sgtin_gtin_pairs):
    """Обрабатываем XML файлы"""
    results = []
    found_gtins = set()

    for filename in os.listdir(script_dir):
        if not filename.endswith('.xml'):
            continue

        filepath = os.path.join(script_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                xml_soup = BeautifulSoup(f.read(), 'lxml-xml')

                # Проверяем GTIN
                xml_gtin = xml_soup.find('gtin')
                if not xml_gtin:
                    continue

                xml_gtin = xml_gtin.text.strip()

                if xml_gtin not in source_gtins:
                    print(f"Ошибка: Неверный GTIN {xml_gtin} в файле {filename}")
                    return None

                found_gtins.add(xml_gtin)

                # Быстрый поиск по SN
                sn_dict = defaultdict(list)
                for sgtin, gtin in sgtin_gtin_pairs:
                    if gtin == xml_gtin:
                        sn = sgtin[14:]  # Берем часть после GTIN
                        sn_dict[sn].append(sgtin)

                # Обрабатываем serial_numbers
                serial_numbers = xml_soup.find('serial_numbers')
                if serial_numbers:
                    for ids in serial_numbers.find_all('ids'):
                        sn = ids.find('sn')
                        if not sn:
                            continue

                        sn_value = sn.text.strip()
                        if sn_value in sn_dict:
                            ck = ids.find('ck')
                            cs = ids.find('cs')

                            for sgtin in sn_dict[sn_value]:
                                results.append({
                                    'gtin': xml_gtin,
                                    'sgtin': sgtin,
                                    'sn': sn_value,
                                    'ck': ck.text.strip() if ck else None,
                                    'cs': cs.text.strip() if cs else None
                                })

        except Exception as e:
            print(f"Ошибка в файле {filename}: {str(e)}")
            continue

    # Проверяем все ли GTIN найдены
    missing_gtins = source_gtins - found_gtins
    if missing_gtins:
        print(f"Ошибка: Не найдены данные для GTIN: {', '.join(missing_gtins)}")
        return None

    return results

def select_groups():
    """Выбор групп для обработки"""
    print("Выберите группы для обработки:")
    print("1. aggregation_packages")
    print("2. destroyed_serial_numbers")
    print("3. samplingd_serial_numbers")
    print("4. Все группы")

    while True:
        choice = input("Введите номера через запятую (1-4): ").strip()
        selected = []

        if choice == '4':
            return ['aggregation_packages', 'destroyed_serial_numbers', 'samplingd_serial_numbers']

        for num in choice.split(','):
            num = num.strip()
            if num == '1':
                selected.append('aggregation_packages')
            elif num == '2':
                selected.append('destroyed_serial_numbers')
            elif num == '3':
                selected.append('samplingd_serial_numbers')
            else:
                print(f"Неверный номер: {num}")
                break
        else:
            if selected:
                return selected

        print("Пожалуйста, введите правильные номера (1-4)")

def save_qr_data(results):
    """Сохраняем данные для QR-кодов в файл"""
    with open('qr.txt', 'w', encoding='utf-8') as f:
        for item in results:
            line = f"01{item['gtin']}21{item['sn']}"
            if item['ck']:
                line += f"\x1D91{item['ck']}"
            if item['cs']:
                line += f"\x1D92{item['cs']}"
            f.write(line + "\n")
    print(f"\nДанные для {len(results)} QR-кодов сохранены в qr.txt")
    return 'qr.txt'

def create_datamatrix_codes(input_data, input_type='file'):
    """Создает DataMatrix коды из файла с данными или строки"""
    if not HAS_DATAMATRIX_LIBS:
        print("\nДля генерации DataMatrix необходимо установить библиотеки")
        print("pip install pylibdmtx pillow")
        return

    # Читаем данные из файла или используем строку
    codes = []
    try:
        if input_type == 'file':
            with open(input_data, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Удаляем скобки и преобразуем в стандартный формат
                    code = line.replace('(01)', '01').replace('(21)', '21') \
                               .replace('(91)', '\x1D91').replace('(92)', '\x1D92')
                    codes.append(code)
        else:
            codes = [input_data.strip()]
    except Exception as e:
        print(f"Ошибка чтения данных: {e}")
        return

    # Создаем временную папку
    temp_dir = 'temp_datamatrix'
    os.makedirs(temp_dir, exist_ok=True)

    generated_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"datamatrix_codes_{timestamp}.zip"

    print("\nГенерация DataMatrix кодов...")

    for i, code in enumerate(codes, 1):
        try:
            # Создаем DataMatrix
            encoded = encode(code.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

            # Сохраняем изображение
            filename = os.path.join(temp_dir, f"datamatrix_{i}.png")
            img.save(filename)
            generated_files.append(filename)
            print(f"Создан DataMatrix {i}/{len(codes)}")
        except Exception as e:
            print(f"Ошибка при создании DataMatrix {i}: {e}")

    # Создаем ZIP-архив
    if generated_files:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))

        # Удаляем временные файлы
        for file in generated_files:
            os.remove(file)
        os.rmdir(temp_dir)

        print(f"\nВсе DataMatrix коды сохранены в архиве: {zip_filename}")
    else:
        print("Не удалось создать ни одного DataMatrix кода")

def manual_qr_generation():
    """Ручной ввод данных для генерации QR-кода"""
    print("\nРучной ввод данных для генерации QR-кода")
    print("Формат данных: 01<GTIN>21<SN>91<CK>92<CS>")
    print("Где:")
    print(" - GTIN (14 цифр) - глобальный номер товара")
    print(" - SN (серийный номер) - строка переменной длины")
    print(" - CK (контрольный ключ, опционально)")
    print(" - CS (криптохвост, опционально)")
    
    while True:
        print("\nВведите данные (оставьте поле пустым, если не требуется):")
        prefix = input("GTIN (14 цифр): ").strip()
        sn = input("Серийный номер (SN): ").strip()
        ck = input("Контрольный ключ (CK): ").strip()
        cs = input("Криптохвост (CS): ").strip()
        
        if not prefix and not sn and not ck and not cs:
            print("Не введено ни одного значения. Попробуйте снова.")
            continue
            
        if not prefix:
            print("Предупреждение: GTIN не введен, код может быть невалидным")
        elif len(prefix) != 14 or not prefix.isdigit():
            print("Предупреждение: GTIN должен содержать 14 цифр")
            
        if not sn:
            print("Предупреждение: Серийный номер не введен")
            
        # Формируем строку для QR-кода
        qr_data = ""
        if prefix:
            qr_data += f"01{prefix}"
        if sn:
            qr_data += f"21{sn}"
        if ck:
            qr_data += f"\x1D91{ck}"
        if cs:
            qr_data += f"\x1D92{cs}"
            
        print(f"\nСгенерированные данные для QR-кода: {qr_data}")
        
        action = input("\nВыберите действие: [g]enerate, [e]dit, [s]ave to file, [q]uit: ").lower().strip()
        
        if action == 'g':
            if HAS_DATAMATRIX_LIBS:
                create_datamatrix_codes(qr_data, input_type='string')
            else:
                print("\nДля создания DataMatrix кодов установите библиотеки:")
                print("pip install pylibdmtx pillow")
        elif action == 'e':
            continue
        elif action == 's':
            filename = "manual_qr_codes.txt"
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(qr_data + "\n")
            print(f"Данные сохранены в файл {filename}")
        elif action == 'q':
            return
        else:
            print("Неизвестное действие, попробуйте снова")

def main():
    print("="*50)
    print("Генерация данных для кодов маркировки")
    print("="*50)
    
    # Выбор режима работы
    print("\nВыберите режим работы:")
    print("1. Обработка файлов OSC (автоматическая генерация)")
    print("2. Ручной ввод данных для генерации QR-кода")
    print("3. Генерация DataMatrix из файла. (Внимание разделители казывать в скобках (01),(21),(91),(92)")
    
    mode = input("Введите номер режима (1-3): ").strip()
    
    if mode == '1':
        # Оригинальный режим обработки файлов OSC
        selected_groups = select_groups()
        print(f"Выбраны группы: {', '.join(selected_groups)}")

        source_file = 'osc.txt'
        if not os.path.isfile(source_file):
            print(f"Файл {source_file} не найден")
            return

        try:
            sgtin_gtin_pairs = load_source_data(source_file, selected_groups)
            if sgtin_gtin_pairs is None:
                return

            source_gtins = {gtin for _, gtin in sgtin_gtin_pairs}
            script_dir = os.path.dirname(os.path.abspath(__file__))

            results = process_xml_files(script_dir, source_gtins, sgtin_gtin_pairs)
            if results is None:
                return

            qr_file = save_qr_data(results)

            if HAS_DATAMATRIX_LIBS:
                create_dm = input("\nХотите создать DataMatrix коды? (y/n): ").strip().lower()
                if create_dm == 'y':
                    create_datamatrix_codes(qr_file)
            else:
                print("\nДля создания DataMatrix кодов установите библиотеки:")
                print("pip install pylibdmtx pillow")

        except Exception as e:
            print(f"\nОшибка: {str(e)}")
            return
            
    elif mode == '2':
        # Режим ручного ввода
        manual_qr_generation()
        
    elif mode == '3':
        # Режим генерации из файла
        file_path = input("Введите путь к файлу с данными для генерации: ").strip()
        if os.path.isfile(file_path):
            create_datamatrix_codes(file_path)
        else:
            print("Файл не найден!")
    else:
        print("Неверный выбор режима")

if __name__ == '__main__':
    main()
