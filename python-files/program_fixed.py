# coding: utf-8
import os
import sqlite3
import PyPDF2
from pathlib import Path

def setup_database():
    """Создание и настройка базы данных"""
    conn = sqlite3.connect('pdf_database.db')
    cursor = conn.cursor()

    # Создание таблицы для хранения текста из PDF
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pdf_texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        content TEXT NOT NULL,
        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Создание таблицы для индексации (для быстрого поиска)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_index (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdf_id INTEGER,
        word TEXT,
        FOREIGN KEY (pdf_id) REFERENCES pdf_texts (id)
    )
    ''')

    conn.commit()
    return conn

def extract_text_from_pdf(pdf_path):
    """Извлечение текста из PDF файла"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Ошибка при чтении файла {pdf_path}: {e}")
        return None
    return text

def process_pdf_folder(folder_path, conn):
    """Обработка всех PDF файлов в папке"""
    cursor = conn.cursor()
    pdf_files = list(Path(folder_path).glob('*.pdf'))

    print(f"Найдено {len(pdf_files)} PDF файлов для обработки")

    for pdf_file in pdf_files:
        print(f"Обрабатывается: {pdf_file.name}")

        # Проверяем, не обрабатывался ли уже этот файл
        cursor.execute("SELECT id FROM pdf_texts WHERE filename = ?", (pdf_file.name,))
        if cursor.fetchone():
            print(f"Файл {pdf_file.name} уже обработан, пропускаем...")
            continue

        # Извлекаем текст
        text = extract_text_from_pdf(pdf_file)
        if text:
            # Сохраняем в базу данных
            cursor.execute('''
            INSERT INTO pdf_texts (filename, filepath, content)
            VALUES (?, ?, ?)
            ''', (pdf_file.name, str(pdf_file), text))

            pdf_id = cursor.lastrowid

            # Создаем простой поисковый индекс (разбиваем на слова)
            words = set(text.lower().split())
            for word in words:
                if len(word) > 2:  # Игнорируем слишком короткие слова
                    cursor.execute('''
                    INSERT INTO search_index (pdf_id, word)
                    VALUES (?, ?)
                    ''', (pdf_id, word))

            conn.commit()
            print(f"✓ {pdf_file.name} успешно обработан")
        else:
            print(f"✗ Не удалось обработать {pdf_file.name}")

def main():
    # Настройка базы данных
    conn = setup_database()

    # Запрос пути к папке с PDF файлами
    folder_path = input("Введите путь к папке с PDF файлами: ").strip()

    if not os.path.exists(folder_path):
        print("Указанная папка не существует!")
        return

    # Обработка PDF файлов
    process_pdf_folder(folder_path, conn)

    # Закрытие соединения
    conn.close()
    print("Обработка завершена!")

if __name__ == "__main__":
    # Установите необходимые зависимости:
    # pip install PyPDF2
    main()