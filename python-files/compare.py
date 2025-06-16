def compare_files(file1_path, file2_path):
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        cleand_lines = []
        for line in lines1:
            new_line = line.replace('.', '').replace(',', '').replace('>', '').replace('»', '').replace('\n', '').replace('?', '').replace('25', '').replace('20', '').replace('15', '').replace('10', '').replace('5', '')
            if new_line != '':
                cleand_lines.append(new_line)

        lines1 = cleand_lines

        max_lines = max(len(lines1), len(lines2))

        for i in range(max_lines):
            line1 = lines1[i].strip() if i < len(lines1) else "<Keine Zeile>"
            line2 = lines2[i].strip() if i < len(lines2) else "<Keine Zeile>"

            if line1 != line2:
                print(f"{line1}")
                print(f"{line2}")
                print()

    except FileNotFoundError as e:
        print(f"Datei nicht gefunden: {e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# Beispielaufruf
compare_files('ref_text.txt', 'my_text.txt')