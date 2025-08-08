
import csv
import os
import requests

csv_file = 'image_urls.csv'
output_folder = 'downloaded_images'

os.makedirs(output_folder, exist_ok=True)

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # пропускаме заглавния ред
    for i, row in enumerate(reader, start=1):
        if not row:
            continue
        url = row[0].strip()
        if not url.lower().startswith(('http://', 'https://')):
            print(f'Пропуснат (невалиден URL): {url}')
            continue
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            filename = os.path.basename(url.split('?')[0])
            filepath = os.path.join(output_folder, filename)
            with open(filepath, 'wb') as img_file:
                img_file.write(resp.content)
            print(f'[{i}] Изтеглено: {filename}')
        except Exception as e:
            print(f'[{i}] Грешка при {url}: {e}')

print("\nГотово! Снимките са запазени в папката 'downloaded_images'.")
input("Натисни Enter за изход...")
