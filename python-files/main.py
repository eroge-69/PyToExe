import csv
import os

# путь к csv файлу
csv_file = "data.csv"
# папка для заметок
output_dir = "notes"

os.makedirs(output_dir, exist_ok=True)

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')  # если Excel выгрузил табами
    for i, row in enumerate(reader, start=1):
        if not row:
            continue
        # убираем лишние [[ ]]
        cleaned = [col.strip("[] ") for col in row]
        fio, company, position, status, source = cleaned

        # имя файла – по ФИО (без пробелов)
        filename = f"{fio.replace(' ', '_')}.md"
        filepath = os.path.join(output_dir, filename)

        # контент заметки со ссылками Obsidian [[...]]
        content = f"""# [[{fio}]]

**Компания:** [[{company}]]  
**Должность:** {position}  
**Статус:** {status}  
**Источник:** {source}
"""

        with open(filepath, "w", encoding="utf-8") as md:
            md.write(content)
