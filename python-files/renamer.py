import os
import re
import shutil
import pdfplumber
from PIL import Image
import pytesseract
from pathlib import Path

# Настройка пути к Tesseract (если он не в PATH, раскомментируйте и укажите путь)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_with_ocr(pdf_path):
    """
    Извлекает текст из PDF. Если pdfplumber не находит текст, применяет OCR.
    """
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                else:
                    # Если текст не извлечен, применяем OCR к изображению страницы
                    # Конвертируем страницу в изображение
                    img = page.to_image(resolution=150).original
                    ocr_text = pytesseract.image_to_string(img, lang='rus+eng')
                    full_text += ocr_text + "\n"
    except Exception as e:
        print(f"Ошибка при извлечении текста из {pdf_path}: {e}")
        return None
    return full_text.strip()

def parse_payment_info(text):
    """
    Парсит текст и извлекает ТИП платежа и ФИО на основе правил из ТЗ.
    Возвращает кортеж (тип, ФИО_сокр) или (None, None) в случае ошибки.
    """
    if not text:
        return None, None

    # Правило 1: Определение ТИПА
    payment_type = None
    if 'вознаграждение ФУ' in text:
        payment_type = 'депозита'
    elif 'депозит' in text:
        payment_type = 'депозита'
    elif 'расходы' in text:
        payment_type = 'расходов'
    else:
        return None, None  # Не удалось определить тип

    # Правило 2: Извлечение ФИО
    fio = None
    # Ищем ключевые фразы
    patterns = [
        r'Должник-\s*([А-Яа-яЁё\s\-]+)',
        r'Заявитель-\s*([А-Яа-яЁё\s\-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw_fio = match.group(1).strip()
            fio = abbreviate_fio(raw_fio)
            break

    if not fio:
        return None, None

    return payment_type, fio

def abbreviate_fio(full_name):
    """
    Сокращает ФИО до формата: Фамилия И.О. или Фамилия И.О.О.
    """
    parts = full_name.split()
    if len(parts) < 2:
        return None

    surname = parts[0]
    initials = []
    for part in parts[1:]:
        # Берем первую букву каждого имени/отчества
        if part:
            initials.append(part[0] + '.')

    abbreviated = surname + ' ' + ''.join(initials)
    return abbreviated

def generate_new_filename(payment_type, fio):
    """
    Генерирует новое имя файла по шаблону.
    """
    return f"Платежное поручение об оплате {payment_type} за {fio} на 1 л..pdf"

def get_unique_filename(folder, filename):
    """
    Гарантирует уникальность имени файла, добавляя суффикс _копия, _v2 и т.д.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while os.path.exists(os.path.join(folder, new_name)):
        if counter == 1:
            new_name = f"{base}_копия{ext}"
        else:
            new_name = f"{base}_v{counter}{ext}"
        counter += 1
    return new_name

def main():
    # Путь к папке с файлами. Можно сделать input() для интерактивного ввода.
    folder_path = input("Введите путь к папке с PDF-файлами: ").strip()
    if not os.path.exists(folder_path):
        print("Ошибка: Указанная папка не существует.")
        return

    # Создаем файл лога
    log_file_path = os.path.join(folder_path, "rename_log.txt")
    error_log_path = os.path.join(folder_path, "error_log.txt")

    with open(log_file_path, 'w', encoding='utf-8') as log_file, \
         open(error_log_path, 'w', encoding='utf-8') as error_log_file:

        log_file.write("Лог переименования файлов:\n")
        error_log_file.write("Лог ошибок:\n")

        # Проходим по всем PDF-файлам в папке
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                full_path = os.path.join(folder_path, filename)
                print(f"Обработка файла: {filename}")

                # Извлекаем текст
                text = extract_text_with_ocr(full_path)
                if not text:
                    error_msg = f"Ошибка: Не удалось извлечь текст из файла '{filename}'."
                    print(error_msg)
                    error_log_file.write(error_msg + "\n")
                    continue

                # Парсим тип и ФИО
                payment_type, fio = parse_payment_info(text)
                if not payment_type or not fio:
                    error_msg = f"Ошибка: Не удалось распознать тип платежа или ФИО в файле '{filename}'."
                    print(error_msg)
                    error_log_file.write(error_msg + "\n")
                    continue

                # Генерируем новое имя
                new_filename = generate_new_filename(payment_type, fio)
                unique_new_filename = get_unique_filename(folder_path, new_filename)
                new_full_path = os.path.join(folder_path, unique_new_filename)

                # Переименовываем файл
                try:
                    shutil.move(full_path, new_full_path)
                    success_msg = f"УСПЕХ: '{filename}' -> '{unique_new_filename}'"
                    print(success_msg)
                    log_file.write(success_msg + "\n")
                except Exception as e:
                    error_msg = f"Ошибка при переименовании '{filename}': {e}"
                    print(error_msg)
                    error_log_file.write(error_msg + "\n")

    print(f"\n✅ Обработка завершена.")
    print(f"📄 Лог операций: {log_file_path}")
    print(f"❗ Лог ошибок: {error_log_path}")

if __name__ == "__main__":
    main()