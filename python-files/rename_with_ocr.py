import os
import re
import pytesseract
from pdf2image import convert_from_path
from tkinter import filedialog, messagebox, Tk, Toplevel, Label, Button
from PIL import Image

def extract_ip_number_from_image(image):
    """OCR + regex to extract number"""
    text = pytesseract.image_to_string(image, lang="rus+eng")

    # Ищем номер между ключевыми словами и словом "окончить"
    match = re.search(
        r'(?:1\.Исполнительное|производство|№)[^\d]*(\d{4,}/\d{2,}/\d{5,}-ИП)\s+окончить',
        text,
        re.IGNORECASE
    )
    return match.group(1) if match else None

def process_pdfs(folder, log_path):
    count = 0
    skipped = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(folder, filename)
            base_name = os.path.splitext(filename)[0]

            try:
                images = convert_from_path(filepath, dpi=300, first_page=1, last_page=1)
                if images:
                    ip_number = extract_ip_number_from_image(images[0])
                    if ip_number:
                        clean_number = ip_number.replace("/", "!")
                        new_filename = f"{base_name}_{clean_number}.pdf"
                        new_path = os.path.join(folder, new_filename)
                        os.rename(filepath, new_path)
                        count += 1
                    else:
                        skipped.append(filename)
                else:
                    skipped.append(filename)
            except Exception:
                skipped.append(filename)

    with open(log_path, 'w', encoding='utf-8') as log:
        for name in skipped:
            log.write(name + "\n")

    return count, skipped

def start_app():
    folder = filedialog.askdirectory(title="Выберите папку с PDF")
    if not folder:
        return

    def on_start():
        log_path = os.path.join(os.path.dirname(__file__), "skipped_files.txt")
        count, skipped = process_pdfs(folder, log_path)
        msg = f"Успешно переименовано: {count}"
        if skipped:
            msg += f"\nПропущено: {len(skipped)} файлов (см. skipped_files.txt)"
        messagebox.showinfo("Готово", msg)
        window.destroy()

    window = Toplevel()
    window.title("Переименование PDF с OCR")
    window.geometry("320x120")
    Label(window, text="Нажмите кнопку для начала").pack(pady=10)
    Button(window, text="Начать переименование", command=on_start).pack()

def main():
    root = Tk()
    root.withdraw()
    start_app()
    root.mainloop()

if __name__ == '__main__':
    main()
