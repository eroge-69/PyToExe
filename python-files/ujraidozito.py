
import re
import sys
from pathlib import Path

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    entries = []
    i = 0
    while i < len(lines):
        if re.match(r"^\d+$", lines[i].strip()):
            index = int(lines[i].strip())
            time_line = lines[i + 1].strip()
            text_lines = []
            i += 2
            while i < len(lines) and lines[i].strip() != "":
                text_lines.append(lines[i].strip())
                i += 1
            start, end = [t.strip() for t in time_line.split("-->")]
            text = "\n".join(text_lines)
            entries.append((index, start, end, text))
        i += 1
    return entries

def is_meta_entry(text):
    meta_keywords = ['készítette', 'fordította', 'lektorálta', 'hidden leaf', 'http', '@', 'gmail', 'freemail', 'citromail']
    return any(keyword.lower() in text.lower() for keyword in meta_keywords)

def reassign_timings(hun_path, eng_path, out_path):
    hun_entries = parse_srt(hun_path)
    eng_entries = parse_srt(eng_path)

    clean_hun = [e for e in hun_entries if not is_meta_entry(e[3])]
    clean_eng = [e for e in eng_entries if not is_meta_entry(e[3])]

    min_len = min(len(clean_hun), len(clean_eng))
    output = []

    for i in range(min_len):
        index = i + 1
        start, end = clean_eng[i][1], clean_eng[i][2]
        text = clean_hun[i][3]
        output.append(f"{index}\n{start} --> {end}\n{text}\n")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

    print(f"Sikeresen elkészült: {out_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Használat: python ujraidozito.py magyar.srt angol.srt kimenet.srt")
        sys.exit(1)

    reassign_timings(sys.argv[1], sys.argv[2], sys.argv[3])
