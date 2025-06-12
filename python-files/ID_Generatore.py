import csv
import os

# Verzeichnis des aktuellen Skripts
skript_ordner = os.path.dirname(os.path.abspath(__file__))

input_datei = os.path.join(skript_ordner, 'contacts.csv')
output_datei = os.path.join(skript_ordner, 'contacts_importready.csv')

with open(input_datei, newline='', encoding='utf-8') as csv_in, \
     open(output_datei, 'w', newline='', encoding='utf-8') as csv_out:

    reader = csv.reader(csv_in)
    writer = csv.writer(csv_out)

    header = next(reader)
    writer.writerow(['ID'] + header)

    for i, row in enumerate(reader, start=1):
        writer.writerow([i] + row)