def split_file(input_path, lines_per_file=1_000_000):
    count = 0
    part = 1
    buffer = []

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
        for line in infile:
            buffer.append(line)
            count += 1

            if count == lines_per_file:
                with open(f'part_{part}.txt', 'w', encoding='utf-8') as outfile:
                    outfile.writelines(buffer)
                print(f"[+] Saved: part_{part}.txt")
                buffer = []
                count = 0
                part += 1

        # сохранить остаток
        if buffer:
            with open(f'part_{part}.txt', 'w', encoding='utf-8') as outfile:
                outfile.writelines(buffer)
            print(f"[+] Saved: part_{part}.txt")

# ==== НАСТРОЙКИ ====
# Укажи путь к твоему файлу ниже:
input_file = 'all_steamids - 2025-07-01T012629.019.txt'

# Укажи, сколько строк должно быть в каждом куске:
lines_per_part = 3_339

# Вызов функции
split_file(input_file, lines_per_part)
