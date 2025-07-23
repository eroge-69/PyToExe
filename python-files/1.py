import pandas as pd
from collections import defaultdict
import pdfplumber
import sys

def parse_pdf(file_path):
    fuel_data = defaultdict(lambda: defaultdict(float))
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue  # Пропуск пустых страниц
            for line in text.split('\n'):
                if "ДТ-Л-К5" in line or "АИ-95-К5" in line or "АИ-92-К5" in line:
                    parts = line.split()
                    try:
                        # Пример строки: "05-01 15:33 370 12 40.00 2.58 103.20 0.00 ДТ-Л-К5 ..."
                        date = parts[0]          # "05-01"
                        liters = float(parts[4]) # "40.00"
                        # Ищем фамилию (она может быть в разных местах в зависимости от строки)
                        surname = None
                        for part in parts:
                            if part in ["ДТ-Л-К5", "АИ-95-К5", "АИ-92-К5"]:
                                idx = parts.index(part)
                                if idx + 3 < len(parts):
                                    surname = parts[idx + 3]  # Пример: "МинскАЗ" -> берём предыдущее слово
                                break
                        if surname:
                            fuel_data[surname][date] += liters
                    except (IndexError, ValueError) as e:
                        print(f"Ошибка в строке: {line}\n{str(e)}")
                        continue
    
    if not fuel_data:
        print("Данные не найдены. Проверьте формат PDF.")
        return
    
    df = pd.DataFrame.from_dict(fuel_data, orient='index').fillna(0)
    output_file = "fuel_report.xlsx"
    df.to_excel(output_file)
    print(f"Отчет сохранен в файл: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к PDF-файлу: fuel_report.py <путь_к_файлу.pdf>")
    else:
        parse_pdf(sys.argv[1])