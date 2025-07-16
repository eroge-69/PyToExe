import os
import shutil
from datetime import datetime

def find_tdata_dirs(root_path):
    tdata_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        if os.path.basename(dirpath) == "tdata":
            tdata_dirs.append(dirpath)
    return tdata_dirs

def copy_tdata_dirs(tdata_dirs, output_base):
    os.makedirs(output_base, exist_ok=True)
    for idx, tdata_path in enumerate(tdata_dirs, start=1):
        new_folder = os.path.join(output_base, f"Telegram ({idx})")
        os.makedirs(new_folder, exist_ok=True)
        dst_path = os.path.join(new_folder, "tdata")
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(tdata_path, dst_path)
        print(f"[+] Скопировано: {tdata_path} -> {dst_path}")

def main():
    root = input("Введите путь к папке: ").strip()
    if not os.path.isdir(root):
        print("⛔ Указанный путь не существует или не является директорией.")
        return

    tdata_dirs = find_tdata_dirs(root)
    if not tdata_dirs:
        print("❗ Папки tdata не найдены.")
        return

    # Путь рядом с текущим скриптом
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_base = os.path.join(base_dir, f"Telegrams ({timestamp})")

    copy_tdata_dirs(tdata_dirs, output_base)
    print(f"\n✅ Готово. Все папки сохранены в: {output_base}")

if __name__ == "__main__":
    main()
