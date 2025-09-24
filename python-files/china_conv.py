import os
import re
from pypinyin import lazy_pinyin

def contains_chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def chinese_to_pinyin(text: str) -> str:
    """Транслитерация + очистка"""
    raw = ''.join(lazy_pinyin(text))
    safe = re.sub(r'[^a-zA-Z0-9]', '', raw)  # только латиница и цифры
    return safe.lower()

def rename_in_resources(resources_dir: str):
    mapping = {}  # old_rel -> new_rel

    for current_path, dirs, files in os.walk(resources_dir, topdown=False):
        # файлы
        for filename in files:
            if contains_chinese(filename):
                new_name = chinese_to_pinyin(filename)
                old_path = os.path.join(current_path, filename)
                new_path = os.path.join(current_path, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)

                old_rel = os.path.relpath(old_path, resources_dir).replace("\\", "/")
                new_rel = os.path.relpath(new_path, resources_dir).replace("\\", "/")
                mapping[old_rel] = new_rel
                print(f"Файл: {old_rel} → {new_rel}")

        # папки
        for dirname in dirs:
            if contains_chinese(dirname):
                new_name = chinese_to_pinyin(dirname)
                old_path = os.path.join(current_path, dirname)
                new_path = os.path.join(current_path, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)

                old_rel = os.path.relpath(old_path, resources_dir).replace("\\", "/")
                new_rel = os.path.relpath(new_path, resources_dir).replace("\\", "/")
                mapping[old_rel] = new_rel
                print(f"Папка: {old_rel} → {new_rel}")

    return mapping

def update_file(file_path: str, mapping: dict):
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Сортировка по длине ключа, чтобы сначала менять длинные пути
    for old_rel, new_rel in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        if old_rel in content:
            content = content.replace(old_rel, new_rel)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Обновлён {file_path}")

if __name__ == "__main__":
    project_dir = os.getcwd()
    resources_dir = os.path.join(project_dir, "resources")
    json_path = os.path.join(project_dir, "editor.config.json")
    manifest_path = os.path.join(resources_dir, "manifest.xml")

    if not os.path.exists(resources_dir):
        print("❌ Папка 'resources' не найдена!")
        exit(1)

    mapping = rename_in_resources(resources_dir)

    if mapping:
        update_file(json_path, mapping)
        update_file(manifest_path, mapping)
    else:
        print("✅ Китайских имён не найдено, ничего менять не нужно")
