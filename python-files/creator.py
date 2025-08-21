# -*- coding: utf-8 -*-

import json
import shutil
import logging
from pathlib import Path

# Попытка импортировать библиотеку для определения языка
try:
    from langdetect import detect, LangDetectException
except ImportError:
    logging.error("Библиотека 'langdetect' не найдена!")
    logging.error("Пожалуйста, установите ее командой: pip install langdetect")
    exit()

# --- КОНФИГУРАЦИЯ ---

# Название файла для логирования обработанных проектов (в формате JSON)
PROCESSED_LOG_FILE = "processed_projects.json"

# Названия подпапок, которые будут созданы
SUBFOLDER_NAMES = {
    "chinese": "1. Китайский оригинал",
    "english": "2. Английский перевод",
    "russian": "3. Русский готовый перевод",
    "glossary": "4. Глоссарий"
}

# Настройка логирования для красивого вывода в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)


def detect_language(filename: str) -> str:
    """
    Определяет язык названия файла.
    Возвращает 'en', 'ru' или 'unknown'.
    """
    try:
        # Убираем расширение для более точного определения
        stem = Path(filename).stem
        # Убираем цифры и знаки препинания, которые могут мешать
        cleaned_stem = ''.join(filter(str.isalpha, stem))
        
        if not cleaned_stem:
            return 'unknown' # Если в названии только цифры/символы

        lang = detect(cleaned_stem)
        if lang in ['en']:
            return 'en'
        if lang in ['ru']:
            return 'ru'
        return 'unknown'
    except LangDetectException:
        # Эта ошибка может возникнуть, если в тексте нет надежных признаков языка
        return 'unknown'
    except Exception as e:
        logging.warning(f"Не удалось определить язык для '{filename}': {e}")
        return 'unknown'


def load_processed_projects(log_path: Path) -> set:
    """Загружает список уже обработанных проектов из JSON-лога."""
    if not log_path.exists():
        return set()
    try:
        with log_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            logging.warning("Формат лога некорректен, создается новый лог.")
            return set()
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Не удалось прочитать лог-файл '{log_path}': {e}")
        return set()

def save_processed_projects(log_path: Path, projects_set: set):
    """Сохраняет обновленный список проектов в JSON-лог."""
    try:
        with log_path.open('w', encoding='utf-8') as f:
            json.dump(sorted(list(projects_set)), f, ensure_ascii=False, indent=2)
    except IOError as e:
        logging.error(f"Не удалось записать в лог-файл '{log_path}': {e}")


def synchronize_log_with_reality(target_dir: Path, log_path: Path) -> set:
    """Синхронизирует JSON-лог с фактическим наличием папок."""
    logging.info("Синхронизация лога с папками...")
    
    processed_projects_from_log = load_processed_projects(log_path)
    
    existing_projects_in_log = {
        project for project in processed_projects_from_log 
        if (target_dir / project).is_dir()
    }
    
    removed_count = len(processed_projects_from_log) - len(existing_projects_in_log)
    if removed_count > 0:
        logging.info(f"Удалено из лога {removed_count} записей об отсутствующих папках.")
    
    all_dirs_on_disk = {
        p.name for p in target_dir.iterdir() 
        if p.is_dir()
    }
    
    all_known_projects = existing_projects_in_log.union(all_dirs_on_disk)
    
    added_count = len(all_known_projects) - len(existing_projects_in_log)
    if added_count > 0:
        logging.info(f"Добавлено в лог {added_count} ранее не отслеживаемых папок.")
    
    save_processed_projects(log_path, all_known_projects)
    logging.info("Синхронизация завершена.")
    return all_known_projects


def process_file(file_path: Path, log_path: Path, processed_projects_log: set):
    """
    Создает структуру папок для EPUB файла и перемещает его в нужную папку по языку.
    """
    try:
        project_name = file_path.stem
        project_folder = file_path.parent / project_name

        logging.info(f"Обнаружен EPUB '{file_path.name}'. Создаю проект '{project_name}'...")

        # 1. Создаем главную папку проекта
        project_folder.mkdir()

        # 2. Создаем 4 вложенные папки и запоминаем пути
        subfolder_paths = {}
        for key, folder_name in SUBFOLDER_NAMES.items():
            subfolder_path = project_folder / folder_name
            subfolder_path.mkdir()
            subfolder_paths[key] = subfolder_path
        
        logging.info(f"Структура папок для '{project_name}' создана.")

        # --- 3. ОПРЕДЕЛЯЕМ ЯЗЫК И ПЕРЕМЕЩАЕМ ФАЙЛ ---
        lang = detect_language(file_path.name)
        destination_folder = None
        destination_description = ""
        
        if lang in ['en', 'ru']:
            destination_folder = subfolder_paths["english"]
            destination_description = SUBFOLDER_NAMES["english"]
        else: # 'unknown' или любой другой язык
            destination_folder = subfolder_paths["chinese"]
            destination_description = SUBFOLDER_NAMES["chinese"]

        destination_path = destination_folder / file_path.name
        shutil.move(str(file_path), str(destination_path))
        
        logging.info(f"Файл '{file_path.name}' (язык: {lang}) перемещен в папку «{destination_description}».")

        # 4. Добавляем имя проекта в лог после успешной обработки
        processed_projects_log.add(project_name)
        save_processed_projects(log_path, processed_projects_log)

    except FileExistsError:
        logging.warning(f"Папка '{project_name}' уже существует. Файл '{file_path.name}' будет пропущен.")
        processed_projects_log.add(project_name)
        save_processed_projects(log_path, processed_projects_log)
    except FileNotFoundError:
        logging.error(f"Файл '{file_path.name}' исчез до того, как был обработан.")
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка при обработке файла '{file_path.name}': {e}")


def run_organizer(target_dir: Path):
    """
    Сканирует папку и обрабатывает все .epub файлы, для которых еще не созданы папки.
    """
    if not target_dir.is_dir():
        logging.error(f"Ошибка: Не удалось определить текущую папку: '{target_dir}'")
        return

    script_path = Path(__file__).resolve()
    log_path = target_dir / PROCESSED_LOG_FILE
    
    logging.info(f"Запускаю проверку папки: {target_dir.resolve()}")
    logging.info(f"Используется JSON-лог: {PROCESSED_LOG_FILE}")
    logging.info("-" * 40)

    # 1. Синхронизируем лог с реальностью
    processed_projects_log = synchronize_log_with_reality(target_dir, log_path)
    logging.info("-" * 40)

    # 2. Ищем .epub файлы, для которых еще не созданы проекты
    processed_count = 0
    all_epub_files = [
        p for p in target_dir.glob('*.epub') 
        if p.is_file() and p.resolve() != script_path
    ]

    files_to_process = [
        f for f in all_epub_files if f.stem not in processed_projects_log
    ]

    if not files_to_process:
        logging.info("Новых .epub файлов для обработки не найдено.")
    else:
        logging.info(f"Найдено {len(files_to_process)} новых .epub файлов. Начинаю обработку...")
        for file_path in files_to_process:
            process_file(file_path, log_path, processed_projects_log)
            processed_count += 1
            logging.info("-" * 20) # Разделитель между файлами

    logging.info("=" * 40)
    logging.info("Проверка завершена.")
    logging.info(f"Всего обработано за этот запуск: {processed_count} файлов.")
    logging.info("=" * 40)


if __name__ == "__main__":
    # Автоматически определяем папку, в которой находится скрипт
    script_directory = Path(__file__).parent.resolve()
    
    # Запускаем основную функцию
    run_organizer(script_directory)
    
    # Пауза перед закрытием окна
    try:
        input("Нажмите Enter для выхода...")
    except Exception:
        pass