import os

def bytes_to_gb(size):
    return size / (1024 ** 3)

def find_big_files(path, min_size_gb):
    big_files = []
    for root, _, files in os.walk(path):
        for name in files:
            try:
                filepath = os.path.join(root, name)
                size = os.path.getsize(filepath)
                size_gb = bytes_to_gb(size)
                if size_gb >= min_size_gb:
                    big_files.append((filepath, size_gb))
            except:
                continue
    return sorted(big_files, key=lambda x: -x[1])

def show_and_delete(files):
    print(f"\nНайдено {len(files)} файлов больше 0.9 ГБ:\n")
    for i, (path, size) in enumerate(files, start=1):
        print(f"{i}. {path} — {size:.2f} ГБ")
    
    inp = input("\nВведи номера файлов для удаления через запятую (например: 1,3,5) или нажми Enter, чтобы выйти: ")
    if not inp.strip():
        print("Выход без удаления.")
        return
    
    nums = []
    try:
        nums = [int(x.strip()) for x in inp.split(',')]
    except:
        print("Ошибка: неправильный формат ввода.")
        return

    for num in nums:
        if 1 <= num <= len(files):
            file = files[num - 1][0]
            try:
                os.remove(file)
                print(f"Удалён: {file}")
            except Exception as e:
                print(f"Не удалось удалить {file}: {e}")
        else:
            print(f"Нет файла с номером: {num}")

if __name__ == "__main__":
    scan_path = "E:\\"
    min_size = 0.9

    files = find_big_files(scan_path, min_size)
    if not files:
        print("Файлы больше 900 МБ не найдены.")
    else:
        show_and_delete(files)

    input("\nНажми Enter для выхода...")
