import PyPDF2
import easygui

def rotate_pages(pdf_file):
    """ Поворачиваем все страницы на 180 градусов """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    rotated_pages = []
    
    for page in pdf_reader.pages:
        # Применяем поворот каждой страницы на 180 градусов
        page.rotate(180)
        rotated_pages.append(page)
        
    return rotated_pages

def reverse_pages(pdf_file):
    """ Инвертируем порядок страниц PDF-документа """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    reversed_pages = list(reversed(pdf_reader.pages))
    return reversed_pages

def interleave_pages(first_pdf_pages, second_pdf_pages):
    """ Чередуем страницы двух файлов """
    merged_pages = []
    max_len = max(len(first_pdf_pages), len(second_pdf_pages))
    
    for i in range(max_len):
        if i < len(first_pdf_pages):
            merged_pages.append(first_pdf_pages[i])
        if i < len(second_pdf_pages):
            merged_pages.append(second_pdf_pages[i])
            
    return merged_pages

# Интерфейс выбора файлов с помощью easygui
first_file_path = easygui.fileopenbox(title="Выберите первый PDF-файл", default="*.pdf")
if not first_file_path:
    print("Первый файл не выбран.")
    exit()

second_file_path = easygui.fileopenbox(title="Выберите второй PDF-файл", default="*.pdf")
if not second_file_path:
    print("Второй файл не выбран.")
    exit()

output_file_path = easygui.filesavebox(title="Укажите путь и имя итогового PDF-файла", default="result.pdf")
if not output_file_path:
    print("Место сохранения не выбрано.")
    exit()

# Основная логика объединения файлов
with open(first_file_path, 'rb') as first_file, open(second_file_path, 'rb') as second_file:
    # Поворот страниц первого файла
    first_rotated_pages = rotate_pages(first_file)
    
    # Переворачиваем порядок страниц второго файла
    second_reversed_pages = reverse_pages(second_file)
    
    # Чередуем страницы обоих файлов
    final_pages = interleave_pages(first_rotated_pages, second_reversed_pages)
    
    # Создаем объект для записи финального PDF
    writer = PyPDF2.PdfWriter()
    for page in final_pages:
        writer.add_page(page)
    
    # Сохраняем полученный PDF
    with open(output_file_path, 'wb') as output_file:
        writer.write(output_file)

print(f'Файл успешно сохранён в {output_file_path}')