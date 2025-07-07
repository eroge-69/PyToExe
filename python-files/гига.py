import tkinter as tk
from tkinter import filedialog
import zipfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import uuid
import re

def sanitize_path(name):
    """Обработка строки для безопасного использования в путях файлов путем удаления недопустимых символов."""
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)
    sanitized = sanitized.strip().strip('.')
    return sanitized if sanitized else 'unnamed'

def get_object_type_name(metadata_tree, object_type_id):
    """Получение имени объекта (OBJECT_TYPE) по значению атрибута F_OBJ_TYPE из файла MetaDataBrief.xml."""
    for obj_type in metadata_tree.findall(".//OBJECT_TYPE"):
        if obj_type.find("F_OBJ_TYPE").text == object_type_id:
            return obj_type.find("F_OBJ_TYPE_NAME").text
    return None

def get_project_object_id(relations_tree, part_obj_id):
    """Получение значения F_PROJ_OBJ из файла Relations.xml по атрибуту F_PART_OBJ."""
    for relation in relations_tree.findall(".//RELATION"):
        if relation.find("F_PART_OBJ").text == part_obj_id:
            return relation.find("F_PROJ_OBJ").text
    return None

def get_object_caption_and_type(objects_tree, object_id):
    """Получение значений CAPTION и F_OBJECT_TYPE из файла Objects.xml по ID объекта."""
    for obj in objects_tree.findall(".//OBJECT"):
        if obj.find("F_OBJECT_ID").text == object_id:
            return obj.find("CAPTION").text, obj.find("F_OBJECT_TYPE").text
    return None, None

def get_object_id_by_blb_path(objects_tree, blb_path):
    """Получение значения F_OBJECT_ID из файла Objects.xml по пути к блоб-файлу (.blb)."""
    blb_path = str(Path(blb_path))
    for obj in objects_tree.findall(".//OBJECT"):
        for attr in obj.findall(".//ATTRIBUTE"):
            if attr.find("F_PATH2FILE") is not None:
                xml_path = str(Path(attr.find("F_PATH2FILE").text)).replace("\\", "/")
                if xml_path == blb_path.replace("\\", "/"):
                    return obj.find("F_OBJECT_ID").text
    return None

def get_next_file_number(folder_path, base_name):
    """Возвращает следующий доступный номер файла в формате base_name_X."""
    folder_path = Path(folder_path)
    i = 1
    while (folder_path / f"{base_name}_{i}.blb").exists():
        i += 1
    return i

def process_blb_files(zip_path, results_dir):
    # Чтение пути к архиву и результирующей папке
    zip_path = Path(zip_path)
    results_dir = Path(results_dir)
    
    # Создаем отдельную папку для каждого архива
    individual_results_dir = results_dir / zip_path.stem
    individual_results_dir.mkdir(parents=True, exist_ok=True)
    
    # Основная папка "ТП" внутри индивидуальной папки
    tp_dir = individual_results_dir / "ТП"
    tp_dir.mkdir(parents=True, exist_ok=True)
    
    # Открываем архив
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Извлечение XML-файлов
        objects_xml = zip_ref.read('Objects.xml')
        relations_xml = zip_ref.read('Relations.xml')
        metadata_xml = zip_ref.read('MetaDataBrief.xml')
        
        # Парсим XML
        objects_tree = ET.fromstring(objects_xml)
        relations_tree = ET.fromstring(relations_xml)
        metadata_tree = ET.fromstring(metadata_xml)
        
        # Все .blb файлы
        blb_files = [f for f in zip_ref.namelist() if f.endswith('.blb')]
        
        for blb_file in blb_files:
            # Получаем ID объекта по пути к BLB-файлу
            object_id = get_object_id_by_blb_path(objects_tree, blb_file)
            if not object_id:
                print(f"Пропускаем файл {blb_file}: объект не найден.")
                continue
            
            # Связь с проектом
            proj_obj_id = get_project_object_id(relations_tree, object_id)
            if not proj_obj_id:
                # Если связи нет, сохраняем в папку "Без связи"
                folder_path = tp_dir / "Без связи"
                folder_path.mkdir(parents=True, exist_ok=True)
                dest_path = folder_path / Path(blb_file).name
                with zip_ref.open(blb_file) as source:
                    with open(dest_path, 'wb') as dest:
                        shutil.copyfileobj(source, dest)
                print(f"Сохранили файл {blb_file} в {dest_path}")
                continue
            
            # Название и тип объекта
            caption, object_type_id = get_object_caption_and_type(objects_tree, proj_obj_id)
            if not caption or not object_type_id:
                print(f"Ошибка извлечения названия или типа объекта для проекта {proj_obj_id}")
                continue
            
            # Тип объекта
            obj_type_name = get_object_type_name(metadata_tree, object_type_id)
            if not obj_type_name:
                print(f"Тип объекта '{object_type_id}' не найден в метаданных.")
                continue
            
            # Безопасное преобразование названий
            sanitized_caption = sanitize_path(caption)
            sanitized_obj_type_name = sanitize_path(obj_type_name)
            
            # Формируем пути и названия
            if sanitized_obj_type_name == sanitize_path("Переход"):
                folder_path = tp_dir / "переход" / sanitized_caption
                base_name = "эскиз_переход"
            elif sanitized_obj_type_name == sanitize_path("Операция"):
                folder_path = tp_dir / sanitized_caption
                base_name = "эскиз_операции"
            elif sanitized_obj_type_name == sanitize_path("Техпроцесс единичный"):
                folder_path = tp_dir
                base_name = "единичный_ТП"
            else:
                print(f"Неизвестный тип объекта: {obj_type_name}")
                continue
            
            # Создаем папку назначения
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Номер следующего свободного файла
            file_number = get_next_file_number(folder_path, base_name)
            
            # Копируем файл
            with zip_ref.open(blb_file) as source:
                dest_path = folder_path / f"{base_name}_{file_number}.blb"
                with open(dest_path, 'wb') as dest:
                    shutil.copyfileobj(source, dest)
                print(f"Копировали файл {blb_file} в {dest_path}")

def process_directory(directory):
    """
    Обрабатывает все архивы (*.zip) в выбранной директории, создавая отдельную папку "ТП" для каждого архива.
    """
    directory = Path(directory)
    
    # Общая папка результатов
    results_dir = directory / "результаты"
    results_dir.mkdir(exist_ok=True)
    
    # Получаем список всех архивов (*.zip) в директории
    zip_files = list(directory.glob("*.zip"))
    
    # Обрабатываем каждый архив
    for zip_file in zip_files:
        print(f"\nОбрабатываем архив: {zip_file.name}\n")
        process_blb_files(str(zip_file), results_dir)

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Скрывает главное окно Tkinter
    folder_selected = filedialog.askdirectory(title="Выберите папку с архивами")
    if folder_selected:
        process_directory(folder_selected)
    else:
        print("Пользователь отменил выбор папки.")

if __name__ == "__main__":
    select_folder()