import re
from googletrans import Translator

# Fájlnevek
input_file = "Frame.strings"  # eredeti fájl
output_file = "Frame_hu.strings"  # fordított fájl

# Fordító inicializálása
translator = Translator()

# Fájl beolvasása
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

translated_lines = []

# Batch méret
batch_size = 50
text_batches = []
batch = []

for line in lines:
    match = re.match(r'(\s*"[^"]+"\s*=\s*)"([^"]*)"(;.*)?', line)
    if match:
        original_text = match.group(2)
        batch.append(original_text)
        if len(batch) == batch_size:
            text_batches.append(batch)
            batch = []
    else:
        text_batches.append([line])  # nem fordítható sor külön kerül

# Maradék hozzáadása
if batch:
    text_batches.append(batch)

# Fordítás batch-ekben (haladás kijelzéssel)
translated_texts = []
for i, batch in enumerate(text_batches):
    print(f"Fordítás folyamatban... {i * batch_size + 1} - {(i + 1) * batch_size} sor")
    try:
        result = translator.translate(batch, src='en', dest='hu')
        translated_texts.extend([res.text for res in result])
    except Exception as e:
        translated_texts.extend(batch)  # ha hiba, hagyjuk eredetiben

# Visszaépítés soronként
translated_index = 0
for line in lines:
    match = re.match(r'(\s*"[^"]+"\s*=\s*)"([^"]*)"(;.*)?', line)
    if match:
        prefix = match.group(1)
        suffix = match.group(3) if match.group(3) else ""
        translated_text = translated_texts[translated_index]
        translated_index += 1
        new_line = f'{prefix}"{translated_text}"{suffix}\n'
        translated_lines.append(new_line)
    else:
        translated_lines.append(line)

# Fordított fájl mentése
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(translated_lines)

print(f"Fordítás kész! Eredmény: {output_file}")
