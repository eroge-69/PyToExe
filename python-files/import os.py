import os
from tkinter import Tk, filedialog
from PyPDF2 import PdfReader, PdfWriter


def select_folder(title):
    root = Tk()
    root.withdraw()  # скрываем главное окно tkinter
    folder_path = filedialog.askdirectory(title=title)
    return folder_path


# Выбор двух папок
folder_title = select_folder("Выберите папку с титульниками")
folder_content = select_folder("Выберите папку с содержанием")

if not folder_title or not folder_content:
    print("Отмена операции.")
else:
    title_files = sorted(os.listdir(folder_title))
    content_files = sorted(os.listdir(folder_content))

    desktop_path = os.path.expanduser('~/Desktop')
    output_dir = os.path.join(desktop_path, 'Готово')
    os.makedirs(output_dir, exist_ok=True)  # создаем директорию Готово на рабочем столе

    for title_file in title_files:
        if title_file.endswith('.pdf'):
            file_name_without_ext = os.path.splitext(title_file)[0]

            matching_content_file = next(
                (f for f in content_files if f.startswith(file_name_without_ext)),
                None
            )

            if matching_content_file is None:
                print(f'Файл содержания для "{file_name_without_ext}" не найден.')
                continue

            output_pdf = PdfWriter()

            with open(os.path.join(folder_title, title_file), 'rb') as title_fh:
                title_reader = PdfReader(title_fh)
                for page in title_reader.pages:
                    output_pdf.add_page(page)

            with open(os.path.join(folder_content, matching_content_file), 'rb') as content_fh:
                content_reader = PdfReader(content_fh)
                for page in content_reader.pages:
                    output_pdf.add_page(page)

            output_filename = f"{file_name_without_ext}.pdf"
            full_output_path = os.path.join(output_dir, output_filename)
            with open(full_output_path, 'wb') as merged_file:
                output_pdf.write(merged_file)

            print(f"Сохранён объединённый файл {full_output_path}")