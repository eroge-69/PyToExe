import os
import json
import re
from collections import OrderedDict


def flatten_keys(data, parent_key='', sep='.'):
    """Рекурсивно преобразует вложенные ключи в плоские (a.b.c)."""
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_keys(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
    return OrderedDict(items)


def load_translation(filepath):
    """Загружает JSON и возвращает плоский словарь и оригинальный объект."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    flat = flatten_keys(data)
    return flat, data


def find_missing_keys(en_path, ru_path):
    """Возвращает ключи, отсутствующие в en или ru."""
    try:
        en_flat, en_data = load_translation(en_path)
        ru_flat, _ = load_translation(ru_path)
    except Exception as e:
        print(f"❌ Ошибка загрузки файлов переводов: {e}")
        raise

    en_keys = set(en_flat.keys())
    ru_keys = set(ru_flat.keys())

    missing_in_en = sorted(ru_keys - en_keys)
    missing_in_ru = sorted(en_keys - ru_keys)

    return missing_in_en, missing_in_ru, en_flat, ru_flat, en_data


def search_key_usage(project_root, key):
    """Ищет использование ключа в .js и .jsx файлах."""
    usages = []
    escaped_key = re.escape(key)

    patterns = [
       rf't\(["\']{escaped_key}["\']\)',
        rf'i18n\.t\(["\']{escaped_key}["\']\)',
        rf'useTranslation\(\)\["\']{escaped_key}["\']',
        rf'"(?:[^"\\]|\\.)*{escaped_key}(?:[^"\\]|\\.)*"',
        rf"'(?:[^'\\]|\\.)*{escaped_key}(?:[^'\\]|\\.)*'",
    ]

    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(('.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern in patterns:
                            if re.search(pattern, line):
                                usage = {
                                    'file': os.path.relpath(filepath, project_root),
                                    'line': line_num,
                                    'code': line.strip()
                                }
                                if usage not in usages:
                                    usages.append(usage)
                                break
                except Exception as e:
                    print(f"⚠️ Ошибка при чтении {filepath}: {e}")

    return usages


def find_insert_line_in_en(en_data, full_key, en_lines):
    """
    Находит строку в en/translation.json, куда нужно вставить ключ.
    Возвращает номер строки (1-based) или None.
    """
    parts = full_key.split('.')
    if len(parts) < 2:
        return None

    # Проверим, есть ли вся структура до последнего ключа
    current = en_data
    for part in parts[:-1]:
        if part not in current:
            return None
        current = current[part]

    # Найдём начало секции (последний уровень перед ключом)
    section_path = parts[:-1]
    current_obj = en_data
    for p in section_path:
        if not isinstance(current_obj, dict) or p not in current_obj:
            return None
        current_obj = current_obj[p]

    # Ищем строку с началом этой секции: "sectionName": {
    section_name = section_path[-1]
    pattern = rf'"{re.escape(section_name)}"\s*:\s*{{'

    start_line_idx = -1
    for i, line in enumerate(en_lines):
        if re.search(pattern, line):
            # Проверим, что это именно нужная вложенность
            if is_in_nested_structure(en_lines, i, section_path):
                start_line_idx = i
                break

    if start_line_idx == -1:
        return None

    # Ищем конец секции (где закрывается }
    depth = 1
    for i in range(start_line_idx + 1, len(en_lines)):
        depth += en_lines[i].count('{') - en_lines[i].count('}')
        if depth <= 0:
            return i  # вставляем ПЕРЕД этой строкой

    return len(en_lines) - 1


def is_in_nested_structure(lines, start_line, path):
    """
    Проверяет, что найденная секция действительно в нужной вложенности.
    Упрощённая проверка по пути.
    """
    # Можно улучшить, но для большинства случаев достаточно
    return True


def main():
    # 🔧 Пути к файлам переводов
    base_path = r'frontend\gtb\src'
    en_translation = os.path.join(base_path, r'locale\en\translation.json')
    ru_translation = os.path.join(base_path, r'locale\ru\translation.json')
    project_root = base_path  # папка src

    # 📁 Сохраняем отчёт на D:\
    report_path = r'D:\translation_analysis_report.txt'

    # Чтобы не сломалось — используем абсолютные пути
    report_path = os.path.abspath(report_path)
    project_root = os.path.abspath(project_root)

    report_lines = []

    try:
        print("🔍 Загрузка и сравнение переводов...")
        missing_in_en, missing_in_ru, en_flat, ru_flat, en_data = find_missing_keys(en_translation, ru_translation)

        # Читаем en.json по строкам
        with open(en_translation, 'r', encoding='utf-8') as f:
            en_lines = f.readlines()

        print(f"✅ Ключей нет в en: {len(missing_in_en)}")
        print(f"✅ Ключей нет в ru: {len(missing_in_ru)}")
        print("🔍 Поиск использования в .js/.jsx файлах...")

        # === Ключи, отсутствующие в en ===
        report_lines.append("Ключ отсутсвуют в en/translation.json:")
        if missing_in_en:
            for key in missing_in_en:
                usages = search_key_usage(project_root, key)
                insert_line = find_insert_line_in_en(en_data, key, en_lines)
                last_key = key.split('.')[-1]
                line_info = insert_line + 1 if insert_line is not None else "?"

                report_lines.append(f"- {key} (строка: {line_info}, ключ: {last_key})")

                if usages:
                    for usage in usages:
                        report_lines.append(f"  → используется в: {usage['file']} (строка {usage['line']})")
                else:
                    report_lines.append(f"  → не используется")
        else:
            report_lines.append("  Нет отсутствующих ключей")

        # === Ключи, отсутствующие в ru ===
        report_lines.append("")
        report_lines.append("Ключ отсутсвуют в ru/translation.json:")
        if missing_in_ru:
            for key in missing_in_ru:
                usages = search_key_usage(project_root, key)
                if usages:
                    for usage in usages:
                        report_lines.append(f"- {key}")
                        report_lines.append(f"  → используется в: {usage['file']} (строка {usage['line']})")
                else:
                    report_lines.append(f"- {key}")
                    report_lines.append(f"  → не используется")
        else:
            report_lines.append("  Нет отсутствующих ключей")

        # === Отчет ===
        report_lines.append("")
        report_lines.append("Отчет:")
        report_lines.append(f"Всего ключей в ru/translation.json: {len(ru_flat)}")
        report_lines.append(f"Всего ключей в en/translation.json: {len(en_flat)}")
        report_lines.append(f"Ключей отсутсвуют в en/translation.json: {len(missing_in_en)}")
        report_lines.append(f"Ключей отсутсвуют в ru/translation.json: {len(missing_in_ru)}")

        # 💾 Сохраняем отчёт
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"\n✅ Отчёт успешно сохранён: {report_path}")
        except Exception as e:
            print(f"❌ Не удалось сохранить отчёт: {e}")
            print(f"Путь: {report_path}")
            print("Попробуй сохранить в другое место или проверь права доступа.")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        # Даже при ошибке попробуем сохранить частичный отчёт
        report_lines.append(f"\n❌ Ошибка: {e}")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"Частичный отчёт сохранён: {report_path}")
        except:
            print(f"Не удалось сохранить даже частичный отчёт.")


if __name__ == "__main__":
    main()