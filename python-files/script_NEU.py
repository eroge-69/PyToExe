import re
import os

# CRC-32 Tabelle erzeugen
def generate_crc32_table():
    poly = 0xEDB88320
    table = []
    for byte in range(256):
        crc = byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
        table.append(crc)
    return table

CRC32_TABLE = generate_crc32_table()

def calculate_crc32(data: bytes):
    crc = 0xFFFFFFFF
    for byte in data:
        crc = CRC32_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF

# Eingabe des Dateinamens (ohne .xml)
filename_input = input('Bitte den Quell-Dateinamen eingeben (ohne .xml): ').strip()

# XML-Endung anhängen
input_file = filename_input + '.xml'

# Existenz prüfen
if not os.path.isfile(input_file):
    raise FileNotFoundError(f'Datei {input_file} wurde nicht gefunden.')

# Zieldateiname erzeugen
output_file = filename_input + '_checked.xml'

# Datei im Binärmodus einlesen
with open(input_file, 'rb') as file:
    content = file.read()

# <stamp crc="..."/> als Bytes suchen
match = re.search(rb'<stamp\s+crc="[^"]*"\s*/>', content)
if not match:
    raise ValueError('Kein <stamp crc="..." /> Tag gefunden.')

# Temporär das crc-Attribut leeren (als Bytes)
start, end = match.span()
stamp_empty = re.sub(rb'crc="[^"]*"', b'crc=""', match.group())
content_for_crc = content[:start] + stamp_empty + content[end:]

# CRC berechnen
crc_value = calculate_crc32(content_for_crc)
crc_decimal = str(crc_value).encode('ascii')  # Als Bytes

# CRC-Wert in den Originaltext (Bytes!) einfügen
new_stamp = stamp_empty.replace(b'crc=""', b'crc="' + crc_decimal + b'"')
final_content = content[:start] + new_stamp + content[end:]

# Neue Datei im Binärmodus speichern
with open(output_file, 'wb') as file:
    file.write(final_content)

print(f'Die neue Datei wurde mit CRC {crc_value} gespeichert als: {output_file}')
