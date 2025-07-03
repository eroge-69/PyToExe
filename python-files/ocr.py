from paddleocr import PaddleOCR
import json
import re
import os
from tkinter import Tk, filedialog, messagebox
from tkinter import ttk


# Инициализация OCR
ocr = PaddleOCR(
    ocr_version="PP-OCRv5",
    lang="ru",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

def process_image(image_path):
    """Обработка изображения с помощью OCR"""
    try:
        result = ocr.predict(image_path)
        output_dir = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        for res in result:
            res.print()
            res.save_to_img(output_dir)
            res.save_to_json(output_dir)
        return result
    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        return None

def extract_text_from_json(json_path):
    """Извлечение текста из JSON файла"""
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data.get("rec_texts", [])
    except Exception as e:
        print(f"Ошибка при чтении JSON файла: {e}")
        return []

def save_text_to_file(text_lines, txt_path):
    """Сохранение текста в файл"""
    try:
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            for line in text_lines:
                txt_file.write(line + '\n')
        print(f"Текст успешно сохранен в файл: {txt_path}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении текста: {e}")
        return False

def normalize_phone(phone):
    """Нормализация телефонного номера"""
    return re.sub(r'\D', '', phone)

def is_part_of(short_num, long_num):
    """Проверка, является ли короткий номер частью длинного"""
    return long_num.endswith(short_num)

def extract_phones(text):
    """Извлечение телефонных номеров из текста"""
    phone_pattern_7dig = r'(?:T\.:\s*)?(\d{3}-\d{2}-\d{2})'
    phone_pattern_10dig = r'(?:8|\+7)[\s\-\(\)]*(\d{3})[\s\-\(\)]*(\d{3})[\s\-\(\)]*(\d{2})[\s\-\(\)]*(\d{2})'
    
    all_phones = []
    
    for match in re.finditer(phone_pattern_7dig, text):
        normalized = normalize_phone(match.group(1))
        all_phones.append((normalized, len(normalized)))
    
    for match in re.finditer(phone_pattern_10dig, text):
        normalized = f"8{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}"
        all_phones.append((normalized, len(normalized)))
    
    # Удаление дубликатов
    unique_phones = []
    seen_numbers = set()
    
    for phone, length in sorted(all_phones, key=lambda x: -x[1]):
        if not any(is_part_of(phone, seen) or is_part_of(seen, phone) for seen in seen_numbers):
            unique_phones.append(phone)
            seen_numbers.add(phone)
    
    return unique_phones

def process_selected_image():
    """Обработка выбранного изображения"""
    file_path = filedialog.askopenfilename(
        title="Выберите изображение",
        filetypes=(("Изображения", "*.jpg *.jpeg *.png"), ("Все файлы", "*.*"))
    )
    
    if not file_path:
        return
    
    # Определяем пути для выходных файлов
    output_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    json_path = os.path.join(output_dir, f"{base_name}_res.json")
    txt_path = os.path.join(output_dir, f"{base_name}_text.txt")
    
    # Обработка изображения
    process_image(file_path)
    
    # Извлечение текста
    text_lines = extract_text_from_json(json_path)
    if not text_lines:
        messagebox.showerror("Ошибка", "Не удалось извлечь текст из изображения")
        return
    
    # Сохранение текста
    if not save_text_to_file(text_lines, txt_path):
        messagebox.showerror("Ошибка", "Не удалось сохранить текст в файл")
        return
    
    # Чтение текста для анализа
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении текстового файла: {e}")
        return
    
    # Извлечение информации
    phones = extract_phones(text)
    
    # Вывод результатов
    result_text = "Найденные телефоны:\n" + "\n".join(f"- {phone}" for phone in phones) if phones else "Телефоны не найдены"
    messagebox.showinfo("Результат", result_text)

def create_gui():
    """Создание графического интерфейса"""
    root = Tk()
    root.title("Извлечение телефонов из изображения")
    root.geometry("400x200")
    
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 12), padding=10)
    
    label = ttk.Label(root, text="Выберите изображение для обработки", font=('Arial', 12))
    label.pack(pady=20)
    
    btn = ttk.Button(root, text="Выбрать изображение", command=process_selected_image)
    btn.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()