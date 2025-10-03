# -*- coding: utf-8 -*-

import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext, simpledialog
from collections import defaultdict
from datetime import datetime, time
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch, Rectangle
import numpy as np
import json
import threading
import queue
import unicodedata
import pyautogui
import time as time_module
from PIL import Image, ImageGrab, ImageTk
import cv2
import keyboard
import random
import screeninfo
from pynput import mouse, keyboard as kb_listener
from pytesseract import pytesseract
import pytesseract
from PIL import Image, ImageGrab, ImageFilter, ImageEnhance
import numpy as np


# Убедитесь что путь к Tesseract правильный
try:
    pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    print("Tesseract не найден, OCR будет отключен")

# УСТАНАВЛИВАЕМ ШРИФТ, КОТОРЫЙ ПОДДЕРЖИВАЕТ UNICODE
import matplotlib.font_manager as fm
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Расширенная функция для очистки текста от эмодзи и специальных символов
def clean_text(text):
    """Удаляет эмодзи и специальные символы, оставляя только читаемый текст"""
    if not text:
        return text
    
    # Нормализуем текст для лучшей обработки
    text = unicodedata.normalize('NFKC', str(text))
    
    # Паттерн для удаления эмодзи и специальных символов
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # эмоции
        "\U0001F300-\U0001F5FF"  # символы и пиктограммы
        "\U0001F680-\U0001F6FF"  # транспорт и карты
        "\U0001F700-\U0001F77F"  # астрология
        "\U0001F780-\U0001F7FF"  # геометрические фигуры
        "\U0001F800-\U0001F8FF"  # дополнительные символы
        "\U0001F900-\U0001F9FF"  # дополнительные символы-2
        "\U0001FA00-\U0001FA6F"  # шахматы
        "\U0001FA70-\U0001FAFF"  # дополнительные символы-3
        "\U00002702-\U000027B0"  # декоративные символы
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+", 
        flags=re.UNICODE
    )
    
    # Удаляем эмодзи
    cleaned = emoji_pattern.sub('', text)
    
    # Удаляем цветовые коды типа {ffffff}
    cleaned = re.sub(r'\{[0-9a-fA-F]{6}\}', '', cleaned)
    
    # Удаляем другие проблемные символы
    problem_chars = [
        '\U0005022b', '\U00051767', '\U0005047a', '\U000516a4',
        '\U0005020a', '\U000505e9', '\U0005022c', '\U000510f8',
        '\U000501ff', '\U0005058c', '�'
    ]
    
    for char in problem_chars:
        cleaned = cleaned.replace(char, '')
    
    # Удаляем множественные пробелы и trim
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else "Неизвестный предмет"

# Улучшенная функция для извлечения читаемого названия предмета
def extract_item_name(text):
    """Извлекает название предмета из строки с эмодзи"""
    if not text:
        return "Неизвестный предмет"
    
    # Очищаем текст
    cleaned = clean_text(text)
    
    # Пытаемся извлечь название после ключевых слов
    patterns = [
        r'Вам был добавлен предмет (.+?)\.',
        r'Получено: (.+?) и (.+?)!',
        r'и получили (.+?)!',
        r'Предмет: (.+?)(?:\.|$)',
        r'Выпало: (.+?)(?:\.|$)',
        r'Получено: (.+?)(?:\.|$)',
        r'Вы открыли .+? и получили (.+?)!',
        r'Вы использовали .+? и получили (.+?)!'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            if len(match.groups()) > 1:
                # Для случаев с двумя предметами
                item1 = clean_text(match.group(1))
                item2 = clean_text(match.group(2))
                return f"{item1} и {item2}"
            else:
                extracted = clean_text(match.group(1))
                if extracted and extracted != "Неизвестный предмет":
                    return extracted
    
    # Если не нашли паттерн, пытаемся извлечь из оригинальной строки
    if "Получено:" in cleaned:
        parts = cleaned.split("Получено:")
        if len(parts) > 1:
            item_part = parts[1].strip()
            if item_part:
                return clean_text(item_part.replace("!", "").strip())
    
    # Если все еще не нашли, возвращаем очищенный текст
    return cleaned if cleaned and cleaned != "Неизвестный предмет" else "Неизвестный предмет"

# Обновленная функция нормализации названий
def normalize_item_name(item_name):
    """Объединяет различные написания предметов"""
    if not item_name or item_name == "Неизвестный предмет":
        return "Неизвестный предмет"
    
    # Сначала очищаем от эмодзи
    cleaned_name = clean_text(item_name)
    
    # Нормализация ларцов и ящиков
    name_mappings = {
        "ларец super car": "Super Car Box",
        "super car ларец": "Super Car Box", 
        "super car box": "Super Car Box",
        "ларец олигарха": "Ларец Олигарха",
        "оллигарх ларец": "Ларец Олигарха",
        "оллигарх": "Ларец Олигарха",
        "ларец с премией": "Ларец с премией",
        "премиум ларец": "Ларец с премией",
        "рандомный ларец": "Рандомный Ларец",
        "ностальгический ящик": "Ностальгический ящик",
        "платиновая рулетка": "Платиновая рулетка",
        "золотая рулетка": "Золотая рулетка", 
        "серебряная рулетка": "Серебряная рулетка",
        "бронзовая рулетка": "Бронзовая рулетка",
        "рулетка платиновая": "Платиновая рулетка",
        "рулетка золотая": "Золотая рулетка",
        "рулетка серебряная": "Серебряная рулетка",
        "рулетка бронзовая": "Бронзовая рулетка"
    }
    
    # Приводим к нижнему регистру для сравнения
    lower_name = cleaned_name.lower()
    
    for wrong, correct in name_mappings.items():
        if wrong in lower_name:
            return correct
    
    # Стандартизация написания
    corrections = {
        "ларец": "Ларец",
        "ящик": "Ящик", 
        "сундук": "Сундук",
        "рулетка": "Рулетка",
        "тайник": "Тайник",
        "box": "Box"
    }
    
    for wrong, correct in corrections.items():
        if wrong in lower_name:
            # Сохраняем оригинальную капитализацию, но исправляем ключевые слова
            words = cleaned_name.split()
            corrected_words = []
            for word in words:
                lower_word = word.lower()
                if lower_word == wrong:
                    corrected_words.append(correct)
                else:
                    corrected_words.append(word)
            cleaned_name = " ".join(corrected_words)
    
    return cleaned_name if cleaned_name else "Неизвестный предмет"

def parse_date_from_filename(filename):
    """Парсит дату из имени файла YYYY-MM-DD"""
    try:
        date_str = filename[:10]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.date()
    except ValueError:
        return None

def get_player_and_stars_from_line(line):
    """ИСПРАВЛЕННЫЙ парсинг игрока и звезд для ДВУХ форматов"""
    stars = "0"
    player_nick = None
    
    # ФОРМАТ 1: Старый (который уже в коде)
    # Пример: Kirill_Alekseed[194] был(а) объявлен(a) в розыск на {FF6347}3{FFFFFF} звезды
    stars_match_old = re.search(r'розыск на \{FF6347\}(\d+)\{FFFFFF\} звезды', line)
    if stars_match_old:
        stars = stars_match_old.group(1)
    else:
        # ФОРМАТ 2: Новый (который вы указали)
        # Пример: Kurt_Rise[333] был(а) объявлен(a) в розыск! Причина: убийство | Уровень розыска: {FFFFFF}7.
        stars_match_new = re.search(r'Уровень розыска:\s*\{FFFFFF\}(\d+)', line)
        if stars_match_new:
            stars = stars_match_new.group(1)
    
    # Парсим ник игрока (общий для обоих форматов)
    # Формат: Kurt_Rise[333] или Kirill_Alekseed[194]
    player_match = re.search(r'(\w+)[\(\[]\d+[\)\]]', line)
    if player_match:
        player_nick = player_match.group(1)
    else:
        # Альтернативный парсинг для нового формата
        player_match_alt = re.search(r'Внимание!\s*\{FFFFFF\}(\w+)\[\d+\]', line)
        if player_match_alt:
            player_nick = player_match_alt.group(1)
    
    return player_nick, stars

# ИСПРАВЛЕННЫЙ ПАРСИНГ ОБВИНИТЕЛЯ
def get_accuser_from_line(line):
    """ИСПРАВЛЕННЫЙ парсинг обвинителя"""
    # Если есть "Обвинитель:" в строке
    if "Обвинитель:" in line:
        match = re.search(r"Обвинитель: (\w+)", line)
        if match:
            return match.group(1)
    
    # Если обвинителя нет (угон ТС, ограбление и т.д.)
    return "Система"

def parse_time(time_str):
    """Парсит время HH:MM:SS"""
    try:
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return None

def parse_time_extended(time_str):
    """Парсит время HH:MM или HH:MM:SS"""
    try:
        if len(time_str.split(':')) == 2:
            return datetime.strptime(time_str, "%H:%M").time()
        else:
            return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return None

# ИСПРАВЛЕННЫЙ ПАРСИНГ ЛОГОВ С ДОБАВЛЕНИЕМ ФИКСАЦИИ ДЕНЕГ
def parse_logs_from_folder(folder_path, progress_queue=None):
    """Полный парсинг всех данных из txt-файлов в папке"""
    all_cases = []
    deposit_stats = defaultdict(lambda: {"deposit": 0, "salary": 0})
    chest_stats = defaultdict(lambda: defaultdict(int))
    chest_source_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    chest_logs = defaultdict(list)
    purchase_stats = defaultdict(lambda: defaultdict(lambda: {"quantity": 0, "total_price": 0, "transactions": 0}))
    purchase_logs = defaultdict(list)
    roulette_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    roulette_logs = defaultdict(list)
    money_stats = defaultdict(int)  # Статистика по деньгам
    
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    total_files = len(txt_files)
    
    for file_idx, txt_file in enumerate(txt_files):
        file_path = os.path.join(folder_path, txt_file)
        file_date = parse_date_from_filename(txt_file)
        try:
            with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                lines = [line.strip() for line in f]
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            continue

        idx = 0
        while idx < len(lines):
            line = lines[idx]
            cleaned_line = clean_text(line)

            # ФИКСАЦИЯ ДЕНЕГ - НОВЫЙ КОД
            money_match = re.search(r'\[Подсказка\]\s*Вы получили \+\$(\d+)(?:\.|!)', cleaned_line)
            if money_match and file_date:
                try:
                    money_amount = int(money_match.group(1).replace(",", ""))
                    money_stats[file_date] += money_amount
                except ValueError:
                    pass

            # ИСПРАВЛЕННЫЙ ПАРСИНГ РОЗЫСКА
            if "был(а) объявлен(a) в розыск" in line:  # Используем оригинальную строку для парсинга звезд
                case_block = [line]
                
                # ИСПРАВЛЕННЫЙ ПАРСИНГ ИГРОКА И ЗВЕЗД
                player_nick, stars = get_player_and_stars_from_line(line)
                current_nick = player_nick
                
                # ИСПРАВЛЕННЫЙ ПАРСИНГ ОБВИНИТЕЛЯ
                accuser = get_accuser_from_line(line)
                
                case_time = re.search(r"\[(\d+:\d+:\d+)\]", cleaned_line)
                case_time_str = case_time.group(1) if case_time else "Неизвестно"

                # ИСПРАВЛЕННЫЙ ПАРСИНГ ПРИЧИНЫ
                reason = "Неизвестно"
                reason_match = re.search(r"Причина: (.+?)(?:\n|$)", cleaned_line)
                if reason_match:
                    reason = clean_text(reason_match.group(1).strip())
                elif idx + 1 < len(lines) and "[Розыск]" in clean_text(lines[idx + 1]) and "Причина:" in clean_text(lines[idx + 1]):
                    reason_match = re.search(r"Причина: (.+?)(?:\n|$)", clean_text(lines[idx + 1]))
                    if reason_match:
                        reason = clean_text(reason_match.group(1).strip())
                    case_block.append(lines[idx + 1])
                    idx += 1

                # ИСПРАВЛЕННЫЙ ПОИСК ВРЕМЕНИ ПОСАДКИ И ВЫХОДА
                j = idx + 1
                exit_found = False
                arrest_time = "Неизвестно"
                while j < len(lines):
                    next_line = lines[j]
                    cleaned_next_line = clean_text(next_line)
                    
                    if "был(а) объявлен(a) в розыск" in cleaned_next_line:
                        break

                    # Время посадки
                    arrest_match = re.search(r"\[(\d+:\d+:\d+)\] .*посадил в КПЗ", cleaned_next_line)
                    if arrest_match:
                        arrest_time = arrest_match.group(1)
                        case_block.append(next_line)

                    # Выход из игры - ИСПРАВЛЕННАЯ ПРОВЕРКА
                    if current_nick and f"{current_nick} вышел при попытке избежать ареста" in cleaned_next_line:
                        exit_found = True
                        case_block.append(next_line)
                        break

                    # Альтернативная проверка выхода
                    if re.search(r"\[.*\] Полицейский .* посадил в КПЗ нового преступника!", cleaned_next_line):
                        case_block.append(next_line)
                        if j + 1 < len(lines):
                            maybe_exit = lines[j + 1]
                            if current_nick and re.search(rf"> Игрок {re.escape(current_nick)}\(\d+\) вышел при попытке избежать ареста", clean_text(maybe_exit)):
                                case_block.append(maybe_exit)
                                exit_found = True
                                j += 1
                        break

                    j += 1

                all_cases.append({
                    "accuser": accuser,  # ИСПРАВЛЕННЫЙ ОБВИНИТЕЛЬ
                    "player": current_nick,
                    "stars": stars,  # ДОБАВЛЕНЫ ЗВЕЗДЫ
                    "block": case_block,
                    "source_file": txt_file,
                    "file_date": file_date,
                    "exit_found": exit_found,
                    "lines": lines,
                    "case_time": case_time_str,
                    "arrest_time": arrest_time,
                    "reason": reason
                })

            # Парсинг депозита и ЗП
            deposit_match = re.search(r"Текущая сумма на депозите: \$\d+ \{[^}]+\}\(\+\$(\d+)\)", cleaned_line)
            salary_match = re.search(r"Текущая сумма в банке: \$\d+ \{[^}]+\}\(\+\$(\d+)\)", cleaned_line)
            
            if deposit_match and file_date:
                try:
                    deposit_amount = int(deposit_match.group(1).replace(",", ""))
                    deposit_stats[file_date]["deposit"] += deposit_amount
                except ValueError:
                    pass
                
            if salary_match and file_date:
                try:
                    salary_amount = int(salary_match.group(1).replace(",", ""))
                    deposit_stats[file_date]["salary"] += salary_amount
                except ValueError:
                    pass

            # УЛУЧШЕННЫЙ ПАРСИНГ ТАЙНИКОВ И СУНДУКОВ
            source = None
            item_name = None
            
            # Определяем источник (тайник/сундук)
            source_patterns = [
                (r"Вы открыли (Тайник Лос Сантоса)", "Тайник Лос Сантоса"),
                (r"Вы открыли (Тайник Vice City)", "Тайник Vice City"),
                (r"Вы использовали (Тайник Илона Маска)", "Тайник Илона Маска"),
                (r"Вы использовали (Сундук с рулетками)", "Сундук с рулетками"),
                (r"Вы использовали (Платиновый сундук с рулетками)", "Платиновый сундук с рулетками"),
                (r"Вы использовали (тайник|сундук).*?и получили", "Тайник/Сундук"),
            ]
            
            for pattern, source_name in source_patterns:
                source_match = re.search(pattern, cleaned_line, re.IGNORECASE)
                if source_match:
                    source = source_name
                    break
            
            # Парсим лут из тайников/сундуков
            if file_date and source:
                # Паттерн для одного предмета
                single_pattern = r"(?:Вы использовали|Вы открыли).*?и получили (.+?)!"
                single_match = re.search(single_pattern, cleaned_line, re.IGNORECASE)
                
                # Паттерн для двух предметов
                multi_pattern = r"Получено: (.+?) и (.+?)!"
                multi_match = re.search(multi_pattern, cleaned_line)
                
                if single_match:
                    raw_item = single_match.group(1).strip()
                    item_name = normalize_item_name(extract_item_name(raw_item))
                    if item_name and item_name != "Неизвестный предмет":
                        chest_stats[file_date][item_name] += 1
                        chest_source_stats[file_date][source][item_name] += 1
                        chest_logs[file_date].append({
                            'source': source,
                            'item': item_name,
                            'line': line
                        })
                
                elif multi_match:
                    raw_item1 = multi_match.group(1).strip()
                    raw_item2 = multi_match.group(2).strip()
                    item1 = normalize_item_name(extract_item_name(raw_item1))
                    item2 = normalize_item_name(extract_item_name(raw_item2))
                    
                    if item1 and item1 != "Неизвестный предмет":
                        chest_stats[file_date][item1] += 1
                        chest_source_stats[file_date][source][item1] += 1
                    if item2 and item2 != "Неизвестный предмет":
                        chest_stats[file_date][item2] += 1
                        chest_source_stats[file_date][source][item2] += 1
                    
                    chest_logs[file_date].append({
                        'source': source,
                        'item': f"{item1} и {item2}",
                        'line': line
                    })
                
                # Дополнительная проверка для строки с "Получено:" следующей за строкой открытия
                elif idx + 1 < len(lines):
                    next_line_cleaned = clean_text(lines[idx + 1])
                    next_multi_match = re.search(r"Получено: (.+?) и (.+?)!", next_line_cleaned)
                    next_single_match = re.search(r"Получено: (.+?)!", next_line_cleaned)
                    
                    if next_multi_match:
                        raw_item1 = next_multi_match.group(1).strip()
                        raw_item2 = next_multi_match.group(2).strip()
                        item1 = normalize_item_name(extract_item_name(raw_item1))
                        item2 = normalize_item_name(extract_item_name(raw_item2))
                        
                        if item1 and item1 != "Неизвестный предмет":
                            chest_stats[file_date][item1] += 1
                            chest_source_stats[file_date][source][item1] += 1
                        if item2 and item2 != "Неизвестный предмет":
                            chest_stats[file_date][item2] += 1
                            chest_source_stats[file_date][source][item2] += 1
                        
                        chest_logs[file_date].append({
                            'source': source,
                            'item': f"{item1} и {item2}",
                            'line': f"{line}\n{lines[idx + 1]}"
                        })
                        idx += 1
                    
                    elif next_single_match:
                        raw_item = next_single_match.group(1).strip()
                        item_name = normalize_item_name(extract_item_name(raw_item))
                        if item_name and item_name != "Неизвестный предмет":
                            chest_stats[file_date][item_name] += 1
                            chest_source_stats[file_date][source][item_name] += 1
                            chest_logs[file_date].append({
                                'source': source,
                                'item': item_name,
                                'line': f"{line}\n{lines[idx + 1]}"
                            })
                            idx += 1

            # Парсинг выпадений из рулеток с улучшенной фиксацией
            if "Вам был добавлен предмет" in cleaned_line and file_date:
                vip_bonus = False
                bonus_multiplier = 1.0
                
                for i in range(max(0, idx-4), min(len(lines), idx+5)):
                    if "[Premium VIP]" in clean_text(lines[i]) and "+15%" in clean_text(lines[i]):
                        vip_bonus = True
                        bonus_multiplier = 1.15
                        break
                
                item_name = extract_item_name(line)
                
                if item_name == "Неизвестный предмет":
                    idx += 1
                    continue
                
                skip_items = ['рулетка', 'ларец', 'ящик', 'box', 'сундук', 'тайник', 'лот', 'чек']
                if any(skip in item_name.lower() for skip in skip_items):
                    idx += 1
                    continue
                
                quantity = 1
                quantity_match = re.search(r"\((\d+) шт\)", cleaned_line)
                if quantity_match:
                    quantity = int(quantity_match.group(1))
                
                if vip_bonus:
                    quantity = int(quantity * bonus_multiplier)
                
                roulette_type = "Неизвестно"
                for i in range(max(0, idx-3), idx):
                    prev_line = clean_text(lines[i])
                    if "платиновая рулетка" in prev_line.lower():
                        roulette_type = "Платиновая"
                    elif "золотая рулетка" in prev_line.lower():
                        roulette_type = "Золотая"
                    elif "серебряная рулетка" in prev_line.lower():
                        roulette_type = "Серебряная"
                    elif "бронзовая рулетка" in prev_line.lower():
                        roulette_type = "Бронзовая"
                
                if roulette_type != "Неизвестно":
                    roulette_stats[file_date][roulette_type][item_name] += quantity
                    roulette_logs[file_date].append({
                        'time': re.search(r"\[(\d+:\d+:\d+)\]", cleaned_line).group(1) if re.search(r"\[(\d+:\d+:\d+)\]", cleaned_line) else "Неизвестно",
                        'type': roulette_type,
                        'item': item_name,
                        'quantity': quantity,
                        'vip_bonus': vip_bonus,
                        'line': line
                    })

            # Парсинг скупки
            purchase_patterns = [
                r"\[(\d+:\d+:\d+)\] Вы купили (.+?) \((\d+) шт\.\) у игрока .+ за \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Вы купили (.+?) \((\d+) штук?\) у игрока .+ за \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Вы купили (.+?) у игрока .+ за \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Покупка: (.+?) \((\d+) шт\.\) за \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Куплено: (.+?) \((\d+) шт\.\) за \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Приобретение: (.+?) \((\d+) шт\.\) - \$(\d+)",
                r"\[(\d+:\d+:\d+)\] Вы купили (.+?) за \$(\d+) \(\d+ шт\.\)",
                r"\[(\d+:\d+:\d+)\] Покупка: (.+?) за \$(\d+) \(\d+ шт\.\)",
            ]
            
            for pattern in purchase_patterns:
                purchase_match = re.search(pattern, cleaned_line)
                if purchase_match and file_date:
                    time_str = purchase_match.group(1)
                    raw_item_name = purchase_match.group(2).strip()
                    item_name = normalize_item_name(extract_item_name(raw_item_name))
                    
                    if "за $" in cleaned_line and "шт." in cleaned_line:
                        if len(purchase_match.groups()) >= 4:
                            try:
                                quantity = int(purchase_match.group(3))
                                total_price = int(purchase_match.group(4))
                            except ValueError:
                                continue
                        else:
                            quantity_match = re.search(r"\((\d+) шт\.\)", cleaned_line)
                            price_match = re.search(r"за \$(\d+)", cleaned_line)
                            quantity = int(quantity_match.group(1)) if quantity_match else 1
                            total_price = int(price_match.group(1)) if price_match else 0
                    else:
                        quantity = 1
                        try:
                            total_price = int(purchase_match.group(3))
                        except ValueError:
                            continue
                    
                    if total_price <= 0:
                        continue
                        
                    purchase_stats[file_date][item_name]["quantity"] += quantity
                    purchase_stats[file_date][item_name]["total_price"] += total_price
                    purchase_stats[file_date][item_name]["transactions"] += 1
                    purchase_logs[file_date].append({
                        "time": time_str,
                        "item": item_name,
                        "quantity": quantity,
                        "price": total_price,
                        "line": line
                    })
                    break

            idx += 1

        if progress_queue:
            progress = int((file_idx + 1) / total_files * 100)
            progress_queue.put(progress)
    
    return all_cases, deposit_stats, chest_stats, chest_source_stats, chest_logs, purchase_stats, purchase_logs, roulette_stats, roulette_logs, money_stats

# КОНФИГУРАЦИЯ ЦЕН
class PriceConfigManager:
    def __init__(self):
        self.configs = {}
        self.current_config = None
        self.config_path = None
    
    def load_config(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.configs[path] = config
            self.current_config = config
            self.config_path = path
            return True
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            return False
    
    def save_config(self, path=None):
        if not self.current_config:
            return False
        
        save_path = path or self.config_path
        if not save_path:
            return False
            
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
            return False
    
    def create_new_config(self, items, save_path=None):
        new_config = {}
        for item in items:
            new_config[item] = 0
        self.current_config = new_config
        if save_path:
            self.config_path = save_path
            self.save_config()
        return new_config
    
    def get_price(self, item):
        if self.current_config and item in self.current_config:
            return self.current_config[item]
        return 0
    
    def set_price(self, item, price):
        if self.current_config is not None:
            self.current_config[item] = price

# УЛУЧШЕННЫЙ АВТОКЛИКЕР С ВОЗМОЖНОСТЬЮ ОСТАНОВКИ И ИСПОЛЬЗОВАНИЕМ МЫШИ
class AdvancedAutoClicker:
    def __init__(self):
        self.points = []
        self.running = False
        self.radius = 5
        self.cooldown = 1.0
        self.cycles = 1
        self.safe_mode = True
        self.captcha_after = 10
        self.current_cycle = 0
        self.click_window = None
        self.captcha_window = None
        self.original_pos = None
        self.captcha_callback = None
        self.stop_key = 'f9'  # Клавиша для остановки
        self.keyboard_listener = None
        self.click_thread = None
        
    def add_point(self, x, y):
        self.points.append((x, y, len(self.points) + 1))
        
    def remove_point(self, index):
        if 0 <= index < len(self.points):
            self.points.pop(index)
            for i, point in enumerate(self.points):
                self.points[i] = (point[0], point[1], i + 1)
                
    def start_clicking(self):
        if not self.points:
            if self.click_window:
                self.click_window.show_status("Ошибка: Добавьте точки для клика")
            return
            
        self.running = True
        self.current_cycle = 0
        self.original_pos = pyautogui.position()
        
        # Запускаем слушатель клавиатуры для остановки
        self.start_keyboard_listener()
        
        def click_loop():
            while self.running and self.current_cycle < self.cycles:
                self.current_cycle += 1
                
                for i, (x, y, num) in enumerate(self.points):
                    if not self.running:
                        break
                    
                    # Сохраняем текущую позицию мыши
                    current_pos = pyautogui.position()
                    
                    # Добавляем случайное смещение если радиус > 0
                    if self.radius > 0:
                        offset_x = random.randint(-self.radius, self.radius)
                        offset_y = random.randint(-self.radius, self.radius)
                        click_x = x + offset_x
                        click_y = y + offset_y
                    else:
                        click_x = x
                        click_y = y
                    
                    # Кликаем без перемещения курсора
                    pyautogui.click(click_x, click_y, _pause=False)
                    
                    # Возвращаем курсор на исходную позицию
                    pyautogui.moveTo(current_pos.x, current_pos.y, _pause=False)
                    
                    # Обновляем статус в GUI
                    if self.click_window:
                        self.click_window.update_status(f"Цикл: {self.current_cycle}/{self.cycles}, Точка: {i+1}/{len(self.points)}")
                    
                    # КД между точками
                    if i < len(self.points) - 1:
                        time_module.sleep(self.cooldown)
                
                # Проверка капчи
                if self.safe_mode and self.captcha_after > 0 and self.current_cycle % self.captcha_after == 0:
                    self.running = False
                    if self.click_window:
                        self.click_window.show_captcha_dialog()
                    break
                    
                # КД между циклами
                if self.current_cycle < self.cycles:
                    time_module.sleep(self.cooldown * 2)
            
            self.running = False
            self.stop_keyboard_listener()
            if self.click_window:
                self.click_window.on_clicking_finished()
        
        self.click_thread = threading.Thread(target=click_loop, daemon=True)
        self.click_thread.start()
        
    def start_keyboard_listener(self):
        """Запускает слушатель клавиатуры для остановки"""
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == self.stop_key:
                    self.stop_clicking()
                elif hasattr(key, 'name') and key.name.lower() == self.stop_key:
                    self.stop_clicking()
            except AttributeError:
                pass
        
        self.keyboard_listener = kb_listener.Listener(on_press=on_press)
        self.keyboard_listener.start()
        
    def stop_keyboard_listener(self):
        """Останавливает слушатель клавиатуры"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
    def stop_clicking(self):
        self.running = False
        self.stop_keyboard_listener()

# УЛУЧШЕННАЯ СИСТЕМА КАПЧИ
class CaptchaSystem:
    def __init__(self):
        self.captcha_window = None
        self.callback = None
        
    def show_captcha(self, current_cycle, callback):
        self.callback = callback
        
        self.captcha_window = tk.Toplevel()
        self.captcha_window.title("🔒 ПРОВЕРКА БЕЗОПАСНОСТИ")
        self.captcha_window.attributes('-topmost', True)
        self.captcha_window.geometry("400x300+700+300")
        self.captcha_window.resizable(False, False)
        self.captcha_window.configure(bg='#2c3e50')
        
        # Заголовок
        title_label = tk.Label(self.captcha_window, text="🚨 ТРЕБУЕТСЯ ПОДТВЕРЖДЕНИЕ", 
                              font=('Arial', 14, 'bold'), fg='#e74c3c', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Информация
        info_label = tk.Label(self.captcha_window, 
                             text=f"Выполнено циклов: {current_cycle}\nВведите текст 'ПРОДОЛЖИТЬ' для подтверждения:",
                             font=('Arial', 11), fg='white', bg='#2c3e50')
        info_label.pack(pady=10)
        
        # Поле ввода
        self.captcha_entry = tk.Entry(self.captcha_window, font=('Arial', 14), 
                                     width=20, justify='center')
        self.captcha_entry.pack(pady=15)
        self.captcha_entry.focus()
        
        # Кнопки
        button_frame = tk.Frame(self.captcha_window, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        continue_btn = tk.Button(button_frame, text="✅ ПРОДОЛЖИТЬ", 
                               command=self._on_continue,
                               bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                               width=12, height=1)
        continue_btn.pack(side='left', padx=10)
        
        stop_btn = tk.Button(button_frame, text="⛔ ОСТАНОВИТЬ", 
                           command=self._on_stop,
                           bg='#c0392b', fg='white', font=('Arial', 12, 'bold'),
                           width=12, height=1)
        stop_btn.pack(side='left', padx=10)
        
        self.captcha_entry.bind('<Return>', lambda e: self._on_continue())
        
    def _on_continue(self):
        captcha_text = self.captcha_entry.get().strip()
        if captcha_text.upper() == "ПРОДОЛЖИТЬ":
            if self.callback:
                self.callback(True, captcha_text)
            self.captcha_window.destroy()
        else:
            messagebox.showwarning("Внимание", "Введите текст 'ПРОДОЛЖИТЬ' для подтверждения")
            
    def _on_stop(self):
        if self.callback:
            self.callback(False, "")
        if self.captcha_window:
            self.captcha_window.destroy()

# ЭКРАН НАЛОЖЕНИЯ С ВОЗМОЖНОСТЬЮ ОСТАНОВКИ ПОВЕРХ ВСЕХ ОКОН
class OverlayScreen:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.overlay_window = None
        self.canvas = None
        self.zoom_factor = 1.0
        self.dragging = False
        self.start_x = self.start_y = 0
        self.screen_width = 1920
        self.screen_height = 1080
        self.clicker_ref = None
        self.control_window = None
        
    def detect_resolution(self):
        """Автоопределение разрешения экрана"""
        try:
            monitors = screeninfo.get_monitors()
            if monitors:
                primary = monitors[0]
                self.screen_width = primary.width
                self.screen_height = primary.height
                return self.screen_width, self.screen_height
        except Exception as e:
            print(f"Ошибка определения разрешения: {e}")
        return 1920, 1080  # Fallback
        
    def show(self, clicker_instance=None):
        """Показать экран наложения с плавающим окном управления"""
        if self.overlay_window:
            self.overlay_window.destroy()
            
        self.clicker_ref = clicker_instance
        self.detect_resolution()
        
        # Основное окно наложения
        self.overlay_window = tk.Toplevel(self.parent_app)
        self.overlay_window.title("🎯 ЭКРАН НАЛОЖЕНИЯ - Установка точек")
        self.overlay_window.attributes('-fullscreen', True)
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-alpha', 0.3)
        self.overlay_window.configure(bg='black')
        self.overlay_window.bind('<Escape>', lambda e: self.close())
        
        self.canvas = tk.Canvas(self.overlay_window, highlightthickness=0, 
                               bg='black', cursor='crosshair')
        self.canvas.pack(fill='both', expand=True)
        
        # Отображение информации
        self._draw_info()
        
        # Сетка
        self._draw_grid()
        
        # Существующие точки
        if self.clicker_ref and self.clicker_ref.points:
            self._draw_existing_points()
        
        # Привязка событий
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<MouseWheel>', self._on_zoom)
        self.canvas.bind('<Button-3>', self._on_right_click)
        
        # Плавающее окно управления поверх всех окон
        self._create_floating_control_panel()
        
    def _create_floating_control_panel(self):
        """Создает плавающее окно управления поверх всех окон"""
        if self.control_window:
            self.control_window.destroy()
            
        self.control_window = tk.Toplevel(self.parent_app)
        self.control_window.title("🎮 Управление автокликером")
        self.control_window.attributes('-topmost', True)
        self.control_window.attributes('-toolwindow', True)
        self.control_window.geometry("300x200+50+50")
        self.control_window.resizable(False, False)
        self.control_window.configure(bg='#2c3e50')
        
        # Заголовок
        title_label = tk.Label(self.control_window, text="🎮 УПРАВЛЕНИЕ", 
                              font=('Arial', 12, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Кнопка остановки
        stop_btn = tk.Button(self.control_window, text="⛔ ОСТАНОВИТЬ (F9)", 
                           command=self._stop_clicker,
                           bg='#c0392b', fg='white', font=('Arial', 12, 'bold'),
                           width=20, height=2)
        stop_btn.pack(pady=10)
        
        # Информация
        info_label = tk.Label(self.control_window, 
                             text="Вы можете использовать мышь\nво время работы кликера",
                             font=('Arial', 10), fg='white', bg='#2c3e50')
        info_label.pack(pady=5)
        
        # Кнопка закрытия
        close_btn = tk.Button(self.control_window, text="❌ Закрыть все", 
                            command=self.close_all,
                            bg='#34495e', fg='white', font=('Arial', 10),
                            width=15)
        close_btn.pack(pady=5)
        
    def _stop_clicker(self):
        """Остановить автокликер"""
        if self.clicker_ref:
            self.clicker_ref.stop_clicking()
            messagebox.showinfo("Остановлено", "Автокликер остановлен")
            
    def close_all(self):
        """Закрыть все окна"""
        self.close()
        if self.control_window:
            self.control_window.destroy()
            
    def _draw_info(self):
        """Отобразить информацию о разрешении"""
        info_text = f"Разрешение: {self.screen_width}×{self.screen_height} | Масштаб: {self.zoom_factor:.1f}x | ЛКМ - добавить точку | ПКМ - удалить | ESC - выход"
        self.canvas.create_text(20, 20, text=info_text, anchor='nw',
                               fill='white', font=('Arial', 12, 'bold'))
        
    def _draw_grid(self):
        """Нарисовать сетку"""
        step = 100
        for x in range(0, self.screen_width, step):
            self.canvas.create_line(x, 0, x, self.screen_width, 
                                   fill='#333333', width=1)
        for y in range(0, self.screen_height, step):
            self.canvas.create_line(0, y, self.screen_width, y, 
                                   fill='#333333', width=1)
            
    def _draw_existing_points(self):
        """Нарисовать существующие точки"""
        for x, y, num in self.clicker_ref.points:
            color = '#ff4444' if num % 2 == 0 else '#44ff44'
            self.canvas.create_oval(x-6, y-6, x+6, y+6, 
                                   fill=color, outline='white', width=2)
            self.canvas.create_text(x, y, text=str(num), 
                                   fill='white', font=('Arial', 8, 'bold'))
            
    def _on_click(self, event):
        """Обработчик клика мыши"""
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y
        
        # Добавление точки при клике
        self._add_point(event.x, event.y)
        
    def _on_drag(self, event):
        """Обработчик перемещения мыши"""
        if self.dragging:
            pass
            
    def _on_release(self, event):
        """Обработчик отпускания мыши"""
        self.dragging = False
        
    def _on_zoom(self, event):
        """Обработчик масштабирования"""
        if event.delta > 0:
            self._adjust_zoom(1.1)
        else:
            self._adjust_zoom(0.9)
            
    def _on_right_click(self, event):
        """Правый клик - удаление ближайшей точки"""
        if self.clicker_ref:
            closest_point = None
            min_distance = float('inf')
            
            for i, (x, y, num) in enumerate(self.clicker_ref.points):
                distance = ((x - event.x)**2 + (y - event.y)**2)**0.5
                if distance < min_distance and distance < 20:
                    min_distance = distance
                    closest_point = i
                    
            if closest_point is not None:
                self.clicker_ref.remove_point(closest_point)
                self._redraw()
                
    def _add_point(self, x, y):
        """Добавить точку в автокликер"""
        if self.clicker_ref:
            self.clicker_ref.add_point(x, y)
            self._redraw()
            
    def _adjust_zoom(self, factor):
        """Настроить масштаб"""
        self.zoom_factor *= factor
        self.zoom_factor = max(0.5, min(3.0, self.zoom_factor))
        self._redraw()
        
    def _redraw(self):
        """Перерисовать canvas"""
        if self.canvas:
            self.canvas.delete("all")
            self._draw_info()
            self._draw_grid()
            if self.clicker_ref:
                self._draw_existing_points()
                
    def close(self):
        """Закрыть экран наложения"""
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None

# УЛУЧШЕННАЯ СИСТЕМА ФИКСАЦИИ ЛУТА С АВТОМАТИЧЕСКИМ РАСПОЗНАВАНИЕМ
class AdvancedLootCapture:
    def __init__(self):
        self.capturing = False
        self.region = None
        self.capture_rules = {
            "Вам был добавлен предмет": "item",
            "Вы получили \\+\\$": "money",
            "Получено:": "item",
            "Выпало:": "item"
        }
        self.captured_data = {
            'items': defaultdict(lambda: {'count': 0, 'logs': []}),
            'money': 0,
            'roulette_attempts': 0
        }
        self.capture_window = None
        self.overlay_window = None
        self.roulette_types = {
            "платиновая рулетка": "Платиновая",
            "золотая рулетка": "Золотая", 
            "серебряная рулетка": "Серебряная",
            "бронзовая рулетка": "Бронзовая"
        }
        
    def set_region(self, x1, y1, x2, y2):
        """Установить область захвата"""
        self.region = (x1, y1, x2, y2)
        
    def start_capture(self):
        """Начать фиксацию с улучшенным распознаванием"""
        if not self.region:
            return False
            
        self.capturing = True
        self.captured_data = {
            'items': defaultdict(lambda: {'count': 0, 'logs': []}),
            'money': 0,
            'roulette_attempts': 0
        }
        
        def capture_loop():
            last_text = ""
            while self.capturing:
                try:
                    # Захват экрана
                    screenshot = ImageGrab.grab(bbox=self.region)
                    
                    # Используем OCR для распознавания текста
                    try:
                        text = pytesseract.image_to_string(screenshot, lang='rus')
                        text = clean_text(text)
                        
                        # Проверяем на изменения текста
                        if text and text != last_text:
                            self._process_captured_text(text)
                            last_text = text
                            
                    except Exception as e:
                        print(f"OCR ошибка: {e}")
                        # Резервный метод - анализ пикселей
                        self._analyze_pixels(screenshot)
                    
                except Exception as e:
                    print(f"Ошибка захвата: {e}")
                    
                time_module.sleep(0.5)  # Уменьшил паузу для лучшей реакции
                
            # Завершение фиксации
            if self.capture_window:
                self.capture_window.on_capture_finished()
                
        threading.Thread(target=capture_loop, daemon=True).start()
        return True
        
    def _process_captured_text(self, text):
        """Обработка распознанного текста"""
        lines = text.split('\n')
        
        for line in lines:
            line_clean = clean_text(line)
            
            # Фиксация денег
            money_match = re.search(r'Вы получили \+\$(\d+)(?:\.|!)', line_clean)
            if money_match:
                try:
                    money_amount = int(money_match.group(1))
                    self.captured_data['money'] += money_amount
                    if self.capture_window:
                        self.capture_window._log_message(f"💰 Получено +${money_amount}")
                except ValueError:
                    pass
            
            # Фиксация предметов из рулеток
            item_match = re.search(r'Вам был добавлен предмет (.+?)(?:\.|$)', line_clean)
            if item_match:
                item_name = extract_item_name(item_match.group(1))
                if item_name != "Неизвестный предмет":
                    # Определяем количество
                    quantity = 1
                    quantity_match = re.search(r'\((\d+) шт\)', line_clean)
                    if quantity_match:
                        quantity = int(quantity_match.group(1))
                    
                    self.captured_data['items'][item_name]['count'] += quantity
                    self.captured_data['roulette_attempts'] += 1
                    
                    log_entry = {
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'text': f"Получен предмет: {item_name} ({quantity} шт.)"
                    }
                    self.captured_data['items'][item_name]['logs'].append(log_entry)
                    
                    if self.capture_window:
                        self.capture_window._log_message(f"🎁 {item_name} ({quantity} шт.)")
            
            # Фиксация других предметов
            for pattern in ["Получено:", "Выпало:"]:
                if pattern in line_clean:
                    # Упрощенная обработка для демонстрации
                    item_name = extract_item_name(line_clean)
                    if item_name != "Неизвестный предмет":
                        self.captured_data['items'][item_name]['count'] += 1
                        
                        log_entry = {
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'text': f"Получено: {item_name}"
                        }
                        self.captured_data['items'][item_name]['logs'].append(log_entry)
        
    def _analyze_pixels(self, screenshot):
        """Анализ пикселей для обнаружения изменений (резервный метод)"""
        # Простая проверка на значительные изменения
        try:
            # Конвертируем в numpy array для анализа
            img_array = np.array(screenshot)
            
            # Простой анализ - можно улучшить для конкретной игры
            avg_brightness = np.mean(img_array)
            
            # Если яркость значительно изменилась, возможно появилось новое сообщение
            if hasattr(self, 'last_brightness'):
                if abs(avg_brightness - self.last_brightness) > 10:
                    if self.capture_window:
                        self.capture_window._log_message("🔍 Обнаружено изменение на экране")
            
            self.last_brightness = avg_brightness
        except Exception as e:
            print(f"Ошибка анализа пикселей: {e}")
        
    def stop_capture(self):
        """Остановить фиксацию"""
        self.capturing = False
        
    def get_captured_data(self):
        """Получить собранные данные"""
        return self.captured_data

# ОКНО ФИКСАЦИИ ЛУТА С УЛУЧШЕННЫМ ИНТЕРФЕЙСОМ
class LootCaptureWindow(tk.Toplevel):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.parent = parent
        self.main_app = main_app
        self.loot_system = AdvancedLootCapture()
        self.loot_system.capture_window = self
        
        self.title("📷 СИСТЕМА ФИКСАЦИИ ЛУТА")
        self.geometry("800x700")
        self.configure(padx=10, pady=10)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Создать элементы интерфейса"""
        # Заголовок
        title_label = ttk.Label(self, text="📷 УНИВЕРСАЛЬНАЯ СИСТЕМА ФИКСАЦИИ ЛУТА", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Область захвата
        capture_frame = ttk.LabelFrame(self, text="Область захвата")
        capture_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture_frame, text="Выбрать область на экране", 
                  command=self._select_region).pack(pady=5)
                  
        self.region_label = ttk.Label(capture_frame, text="Область не выбрана", 
                                     foreground='red')
        self.region_label.pack(pady=5)
        
        # Управление
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=5)
        
        self.capture_btn = ttk.Button(control_frame, text="Начать фиксацию", 
                                     command=self._toggle_capture)
        self.capture_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Показать область", 
                  command=self.loot_system.show_region_overlay).pack(side='left', padx=5)
                  
        ttk.Button(control_frame, text="Сохранить данные", 
                  command=self._save_data).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Экспорт в таблицу", 
                  command=self._export_to_table).pack(side='left', padx=5)
                  
        # Статистика
        stats_frame = ttk.LabelFrame(self, text="Статистика в реальном времени")
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=4, wrap='word')
        self.stats_text.pack(fill='x', padx=5, pady=5)
        self.stats_text.insert('1.0', "Статус: Остановлено\nПопыток: 0\nДеньги: $0\nПредметы: 0")
        self.stats_text.config(state='disabled')
        
        # Лог
        log_frame = ttk.LabelFrame(self, text="Лог фиксации")
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Запуск обновления статистики
        self._update_stats()
        
    def _select_region(self):
        """Выбрать область на экране"""
        from screen_region_selector import ScreenRegionSelector
        selector = ScreenRegionSelector(self, self.loot_system)
        selector.select_region()
        
    def _toggle_capture(self):
        """Переключить режим фиксации"""
        if not self.loot_system.region:
            messagebox.showwarning("Ошибка", "Сначала выберите область фиксации")
            return
            
        if not self.loot_system.capturing:
            if self.loot_system.start_capture():
                self.capture_btn.config(text="Остановить фиксацию")
                self._log_message("Фиксация начата")
        else:
            self.loot_system.stop_capture()
            self.capture_btn.config(text="Начать фиксацию")
            self._log_message("Фиксация остановлена")
            
    def _log_message(self, message):
        """Добавить сообщение в лог"""
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        
    def _update_stats(self):
        """Обновить статистику в реальном времени"""
        if self.loot_system.capturing:
            data = self.loot_system.get_captured_data()
            
            stats_text = f"Статус: Активна\n"
            stats_text += f"Попыток: {data['roulette_attempts']}\n"
            stats_text += f"Деньги: ${data['money']:,}\n"
            stats_text += f"Предметы: {len(data['items'])}"
            
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats_text)
            self.stats_text.config(state='disabled')
        
        self.after(1000, self._update_stats)
        
    def _save_data(self):
        """Сохранить данные фиксации"""
        data = self.loot_system.get_captured_data()
        
        if not data['items'] and data['money'] == 0:
            messagebox.showinfo("Инфо", "Нет данных для сохранения")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                save_data = {
                    'timestamp': datetime.now().isoformat(),
                    'region': self.loot_system.region,
                    'captured_data': data
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                    
                messagebox.showinfo("Успех", f"Данные сохранены в: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
                
    def _export_to_table(self):
        """Экспорт данных в таблицу для анализа"""
        data = self.loot_system.get_captured_data()
        
        if not data['items']:
            messagebox.showinfo("Инфо", "Нет данных для экспорта")
            return
        
        # Создаем таблицу с данными
        table_data = []
        total_value = 0
        
        for item_name, item_data in data['items'].items():
            count = item_data['count']
            # Здесь можно добавить логику расчета стоимости
            price = 0  # Заглушка - нужно интегрировать с PriceConfigManager
            value = count * price
            total_value += value
            
            table_data.append([item_name, count, f"${price:,}", f"${value:,}"])
        
        # Показываем таблицу
        table_window = tk.Toplevel(self)
        table_window.title("Таблица выпадений")
        table_window.geometry("600x400")
        
        # Таблица
        tree = ttk.Treeview(table_window, columns=("Предмет", "Количество", "Цена", "Стоимость"), show='headings')
        tree.heading("Предмет", text="Предмет")
        tree.heading("Количество", text="Количество")
        tree.heading("Цена", text="Цена")
        tree.heading("Стоимость", text="Стоимость")
        
        for row in table_data:
            tree.insert("", "end", values=row)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Итоговая информация
        info_label = ttk.Label(table_window, 
                              text=f"Всего попыток: {data['roulette_attempts']} | Общая стоимость: ${total_value:,}",
                              font=('Arial', 10, 'bold'))
        info_label.pack(pady=5)
                
    def on_capture_finished(self):
        """Callback при завершении фиксации"""
        data = self.loot_system.get_captured_data()
        total_items = sum(item_data['count'] for item_data in data['items'].values())
        self._log_message(f"Фиксация завершена. Предметов: {total_items}, Деньги: ${data['money']:,}")

# КЛАСС ДЛЯ ВЫБОРА ОБЛАСТИ ЭКРАНА
class ScreenRegionSelector:
    def __init__(self, parent, loot_system):
        self.parent = parent
        self.loot_system = loot_system
        self.selector_window = None
        
    def select_region(self):
        """Выбор области экрана"""
        messagebox.showinfo("Инструкция", 
                           "После нажатия OK экран затемнится. Выделите область для фиксации лута.\n"
                           "Используйте ЛКМ для выделения, ESC для отмены.")
        
        # Создаем окно-оверлей для выбора области
        self.selector_window = tk.Toplevel(self.parent)
        self.selector_window.attributes('-fullscreen', True)
        self.selector_window.attributes('-alpha', 0.3)
        self.selector_window.configure(bg='black')
        self.selector_window.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.selector_window, highlightthickness=0, cursor='crosshair')
        self.canvas.pack(fill='both', expand=True)
        
        # Инструкция
        self.canvas.create_text(100, 50, 
                               text="Выделите область для фиксации лута\n(ЛКМ - выделить, ESC - отмена)", 
                               anchor='nw', fill='white', font=('Arial', 14, 'bold'))
        
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.selector_window.bind('<Escape>', lambda e: self.selector_window.destroy())
        
    def _on_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 
                                               self.start_x, self.start_y, 
                                               outline='red', width=3)
        
    def _on_mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            
    def _on_mouse_up(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            self.loot_system.set_region(x1, y1, x2, y2)
            if hasattr(self.parent, 'region_label'):
                self.parent.region_label.config(text=f"Область: ({x1}, {y1}) - ({x2}, {y2})", 
                                              foreground='green')
        
        self.selector_window.destroy()

# УЛУЧШЕННОЕ ОКНО АВТОКЛИКЕРА
class AdvancedClickerWindow(tk.Toplevel):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.parent = parent
        self.main_app = main_app
        
        self.auto_clicker = AdvancedAutoClicker()
        self.auto_clicker.click_window = self
        
        self.overlay_screen = OverlayScreen(self)
        self.captcha_system = CaptchaSystem()
        
        self.title("🎮 УЛУЧШЕННЫЙ АВТОКЛИКЕР PRO")
        self.geometry("800x700")
        self.configure(padx=10, pady=10)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Создать интерфейс автокликера"""
        # Заголовок
        title_label = ttk.Label(self, text="🎮 УЛУЧШЕННЫЙ АВТОКЛИКЕР PRO", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Информация
        info_label = ttk.Label(self, 
                              text="💡 Кликер работает в фоновом режиме. Вы можете использовать мышь во время работы.\n"
                                   "⛔ Для остановки нажмите F9 или кнопку в плавающем окне",
                              font=('Arial', 10), foreground='blue')
        info_label.pack(pady=5)
        
        # Управление точками
        points_frame = ttk.LabelFrame(self, text="Управление точками")
        points_frame.pack(fill='x', pady=5)
        
        points_btn_frame = ttk.Frame(points_frame)
        points_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(points_btn_frame, text="📺 Открыть экран наложения", 
                  command=self._show_overlay).pack(side='left', padx=5)
                  
        ttk.Button(points_btn_frame, text="🎯 Добавить текущую позицию", 
                  command=self._add_current_pos).pack(side='left', padx=5)
                  
        ttk.Button(points_btn_frame, text="🗑️ Очистить все точки", 
                  command=self._clear_points).pack(side='left', padx=5)
        
        # Список точек
        self.points_listbox = tk.Listbox(points_frame, height=6)
        self.points_listbox.pack(fill='x', padx=5, pady=5)
        
        # Настройки
        settings_frame = ttk.LabelFrame(self, text="Настройки кликера")
        settings_frame.pack(fill='x', pady=5)
        
        # Радиус
        ttk.Label(settings_frame, text="Радиус случайности (пиксели):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.radius_var = tk.IntVar(value=5)
        ttk.Spinbox(settings_frame, from_=0, to=50, textvariable=self.radius_var, 
                   width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Задержка
        ttk.Label(settings_frame, text="Задержка между точками (сек):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(settings_frame, from_=0.1, to=10.0, increment=0.1, 
                   textvariable=self.delay_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Циклы
        ttk.Label(settings_frame, text="Количество циклов:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.cycles_var = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=1, to=9999, textvariable=self.cycles_var, 
                   width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # Капча
        ttk.Label(settings_frame, text="Капча после циклов:").grid(row=3, column=0, padx=5, pady=2, sticky='w')
        self.captcha_var = tk.IntVar(value=5)
        ttk.Spinbox(settings_frame, from_=0, to=1000, textvariable=self.captcha_var, 
                   width=10).grid(row=3, column=1, padx=5, pady=2)
        
        # Клавиша остановки
        ttk.Label(settings_frame, text="Клавиша остановки:").grid(row=4, column=0, padx=5, pady=2, sticky='w')
        self.stop_key_var = tk.StringVar(value='f9')
        ttk.Entry(settings_frame, textvariable=self.stop_key_var, width=10).grid(row=4, column=1, padx=5, pady=2)
        
        # Безопасный режим
        self.safe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Безопасный режим (капча)", 
                       variable=self.safe_var).grid(row=5, column=0, columnspan=2, padx=5, pady=2, sticky='w')
        
        # Управление
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="🚀 Запустить кликер", 
                                   command=self._toggle_clicker, width=20)
        self.start_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="📷 Фиксация лута", 
                  command=self._show_loot_capture).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="❌ Закрыть", 
                  command=self.destroy).pack(side='left', padx=5)
        
        # Статус
        self.status_label = ttk.Label(self, text="Готов к работе", 
                                     font=('Arial', 10))
        self.status_label.pack(pady=5)
        
    def _show_overlay(self):
        """Показать экран наложения"""
        self.overlay_screen.show(self.auto_clicker)
        
    def _add_current_pos(self):
        """Добавить текущую позицию курсора"""
        x, y = pyautogui.position()
        self.auto_clicker.add_point(x, y)
        self._update_points_display()
        
    def _clear_points(self):
        """Очистить все точки"""
        self.auto_clicker.points.clear()
        self._update_points_display()
        
    def _update_points_display(self):
        """Обновить отображение точек"""
        self.points_listbox.delete(0, tk.END)
        for i, (x, y, num) in enumerate(self.auto_clicker.points):
            self.points_listbox.insert(tk.END, f"{num}. X: {x}, Y: {y}")
            
    def _toggle_clicker(self):
        """Переключить состояние кликера"""
        if not self.auto_clicker.points:
            messagebox.showwarning("Ошибка", "Добавьте точки для клика")
            return
            
        if not self.auto_clicker.running:
            # Обновляем настройки
            self.auto_clicker.radius = self.radius_var.get()
            self.auto_clicker.cooldown = self.delay_var.get()
            self.auto_clicker.cycles = self.cycles_var.get()
            self.auto_clicker.captcha_after = self.captcha_var.get()
            self.auto_clicker.safe_mode = self.safe_var.get()
            self.auto_clicker.stop_key = self.stop_key_var.get().lower()
            
            # Запускаем
            self.auto_clicker.start_clicking()
            self.start_btn.config(text="⛔ Остановить")
            self.status_label.config(text="Кликер запущен...", foreground='green')
        else:
            self.auto_clicker.stop_clicking()
            self.start_btn.config(text="🚀 Запустить кликер")
            self.status_label.config(text="Остановлено", foreground='red')
            
    def _show_loot_capture(self):
        """Показать окно фиксации лута"""
        LootCaptureWindow(self, self.main_app)
        
    def update_status(self, message):
        """Обновить статус"""
        self.status_label.config(text=message)
        
    def show_captcha_dialog(self):
        """Показать диалог капчи"""
        self.captcha_system.show_captcha(
            self.auto_clicker.current_cycle,
            self._on_captcha_result
        )
        
    def _on_captcha_result(self, continue_clicking, captcha_text):
        """Обработчик результата капчи"""
        if continue_clicking:
            self.status_label.config(text="Продолжение работы...", foreground='orange')
            # Перезапускаем кликер
            self.auto_clicker.running = True
            threading.Thread(target=self.auto_clicker.start_clicking, daemon=True).start()
        else:
            self.start_btn.config(text="🚀 Запустить кликер")
            self.status_label.config(text="Остановлено пользователем", foreground='red')
            
    def on_clicking_finished(self):
        """Callback при завершении кликера"""
        self.start_btn.config(text="🚀 Запустить кликер")
        self.status_label.config(text=f"Завершено. Циклов: {self.auto_clicker.current_cycle}", 
                               foreground='blue')

# ИНТЕРАКТИВНЫЕ ГРАФИКИ
class InteractiveChart:
    def __init__(self, figure, axes, chart_type="bar"):
        self.figure = figure
        self.axes = axes if isinstance(axes, list) else [axes]
        self.chart_type = chart_type
        self.selected_index = None
        self.original_colors = {}
        self.data = {}
        
    def set_data(self, labels, values, axis_index=0):
        self.data[axis_index] = {'labels': labels, 'values': values}
        
    def add_highlight_handler(self, click_callback=None, hover_callback=None):
        self.click_callback = click_callback
        self.hover_callback = hover_callback
        
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
    def on_click(self, event):
        if event.inaxes not in self.axes:
            return
            
        ax_index = self.axes.index(event.inaxes)
        if ax_index not in self.data:
            return
            
        labels = self.data[ax_index]['labels']
        values = self.data[ax_index]['values']
        
        if self.chart_type == "bar":
            for i, bar in enumerate(self.axes[ax_index].patches):
                if bar.contains(event)[0]:
                    self.highlight_bar(i, ax_index)
                    if self.click_callback:
                        self.click_callback(labels[i], values[i], i)
                    break

    def on_hover(self, event):
        if event.inaxes not in self.axes:
            return
            
        ax_index = self.axes.index(event.inaxes)
        if ax_index not in self.data:
            return
            
        labels = self.data[ax_index]['labels']
        values = self.data[ax_index]['values']
        
        if self.chart_type == "bar":
            for i, bar in enumerate(self.axes[ax_index].patches):
                if bar.contains(event)[0]:
                    self.axes[ax_index].set_title(f"Наведено: {labels[i]} - {values[i]}", fontsize=10)
                    self.figure.canvas.draw_idle()
                    if self.hover_callback:
                        self.hover_callback(labels[i], values[i], i)
                    return

    def highlight_bar(self, index, axis_index=0):
        self.reset_highlight(axis_index)
        
        if axis_index not in self.original_colors:
            self.original_colors[axis_index] = [bar.get_facecolor() for bar in self.axes[axis_index].patches]
        
        self.axes[axis_index].patches[index].set_facecolor('red')
        self.axes[axis_index].patches[index].set_alpha(0.8)
        
        self.figure.canvas.draw_idle()
        self.selected_index = index
    
    def reset_highlight(self, axis_index=0):
        if axis_index in self.original_colors:
            for i, bar in enumerate(self.axes[axis_index].patches):
                bar.set_facecolor(self.original_colors[axis_index][i])
                bar.set_alpha(1.0)
        
        self.selected_index = None
        self.figure.canvas.draw_idle()

# ГЛАВНОЕ ОКНО ПРОГРАММЫ
class LogAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализатор Логов - ПОЛНАЯ ВЕРСИЯ + АВТОКЛИКЕР PRO")
        self.geometry("1400x900")
        self.configure(bg='#f0f0f0')
        
        self.bind('<Escape>', self.on_escape)

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Arial', 11), padding=10, background='#e0e0e0')
        self.style.map('TButton', background=[('active', '#b0d4e8')])
        self.style.configure('TLabel', font=('Arial', 11))
        self.style.configure('TProgressbar', thickness=25, background='#4caf50')
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        self.style.map('Treeview', background=[('selected', '#b0d4e8')])

        # Данные
        self.all_cases = []
        self.deposit_stats = defaultdict(lambda: {"deposit": 0, "salary": 0})
        self.chest_stats = defaultdict(lambda: defaultdict(int))
        self.chest_source_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.chest_logs = defaultdict(list)
        self.purchase_stats = defaultdict(lambda: defaultdict(lambda: {"quantity": 0, "total_price": 0, "transactions": 0}))
        self.purchase_logs = defaultdict(list)
        self.roulette_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.roulette_logs = defaultdict(list)
        self.money_stats = defaultdict(int)  # Добавлена статистика по деньгам
        
        # Системы
        self.price_manager = PriceConfigManager()
        self.roulette_price_manager = PriceConfigManager()
        self.advanced_clicker = AdvancedAutoClicker()
        self.loot_capture_system = AdvancedLootCapture()
        
        self.navigation_stack = []
        self.include_no_exit = tk.BooleanVar(value=True)

        self.create_select_frame()

    def on_escape(self, event=None):
        if self.navigation_stack:
            back_command = self.navigation_stack.pop()
            back_command()

    def push_navigation(self, back_command):
        self.navigation_stack.append(back_command)

    def create_select_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.navigation_stack = []
        self.select_frame = ttk.Frame(self, padding=30)
        self.select_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(self.select_frame, text="Добро пожаловать в ПОЛНЫЙ Анализатор Логов + АВТОКЛИКЕР PRO", font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)

        ttk.Label(self.select_frame, text="Выберите источник (папка или файл с .txt-логами):").pack(pady=10)

        folder_btn = ttk.Button(self.select_frame, text="📁 Выбрать папку с логами", command=self.select_folder)
        folder_btn.pack(pady=10)

        file_btn = ttk.Button(self.select_frame, text="📄 Выбрать отдельный файл", command=self.select_file)
        file_btn.pack(pady=10)
        
        # Дополнительные кнопки новых функций
        advanced_frame = ttk.Frame(self.select_frame)
        advanced_frame.pack(pady=20)
        
        ttk.Button(advanced_frame, text="🎮 УЛУЧШЕННЫЙ АВТОКЛИКЕР", 
                  command=self.show_advanced_clicker, width=25).pack(side='left', padx=10)
        ttk.Button(advanced_frame, text="📷 СИСТЕМА ФИКСАЦИИ ЛУТА", 
                  command=self.show_loot_capture, width=25).pack(side='left', padx=10)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с логами")
        if folder_path:
            self.start_processing(folder_path, True)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Выберите лог-файл", filetypes=[("Text files", "*.txt")])
        if file_path:
            self.start_processing(os.path.dirname(file_path), True)

    def start_processing(self, path, is_folder):
        self.select_frame.pack_forget()
        progress_frame = ttk.Frame(self, padding=30)
        progress_frame.pack(expand=True, fill='both')

        self.push_navigation(self.create_select_frame)

        self.progress_label = ttk.Label(progress_frame, text="Парсинг логов... Это может занять время для больших файлов.", font=('Arial', 12))
        self.progress_label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=500)
        self.progress_bar.pack(pady=10, expand=True)
        
        self.progress_percentage = ttk.Label(progress_frame, text="0%", foreground='green')
        self.progress_percentage.pack(pady=5)

        back_btn = ttk.Button(progress_frame, text="Назад", command=self.create_select_frame)
        back_btn.pack(pady=10)

        self.progress_queue = queue.Queue()
        threading.Thread(target=self.process_logs, args=(path,), daemon=True).start()
        self.after(100, self.update_progress)

    def process_logs(self, path):
        try:
            (self.all_cases, self.deposit_stats, self.chest_stats, self.chest_source_stats, 
             self.chest_logs, self.purchase_stats, self.purchase_logs, 
             self.roulette_stats, self.roulette_logs, self.money_stats) = parse_logs_from_folder(path, self.progress_queue)
            self.progress_queue.put('done')
        except Exception as e:
            self.progress_queue.put(f'error:{str(e)}')

    def update_progress(self):
        try:
            while True:
                item = self.progress_queue.get_nowait()
                if item == 'done':
                    self.display_main_menu()
                    return
                elif isinstance(item, str) and item.startswith('error:'):
                    error_msg = item.split(':', 1)[1]
                    self.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка парсинга: {error_msg}"))
                    self.after(0, self.create_select_frame)
                    return
                else:
                    self.progress_bar['value'] = item
                    self.progress_percentage.config(text=f"Прогресс: {item}%")
                    self.progress_label.config(text=f"Обработано {item}% файлов...")
        except queue.Empty:
            pass
        self.after(100, self.update_progress)

    def display_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.main_frame = ttk.Frame(self, padding=30)
        self.main_frame.pack(expand=True, fill='both')

        self.push_navigation(self.create_select_frame)

        title = ttk.Label(self.main_frame, text="Главное меню - Выберите действие", font=('Arial', 14, 'bold'))
        title.pack(pady=20)

        # Ползунок для включения всех случаев
        settings_frame = ttk.Frame(self.main_frame)
        settings_frame.pack(pady=10)
        
        ttk.Checkbutton(settings_frame, text="Включая случаи без выхода", 
                       variable=self.include_no_exit).pack(side='left', padx=10)

        # Дополнительные кнопки автокликера и фиксатора
        special_frame = ttk.Frame(self.main_frame)
        special_frame.pack(pady=20)
        
        ttk.Button(special_frame, text="🎮 УЛУЧШЕННЫЙ АВТОКЛИКЕР", 
                  command=self.show_advanced_clicker, width=25).pack(side='left', padx=10)
        ttk.Button(special_frame, text="📷 УНИВЕРСАЛЬНАЯ ФИКСАЦИЯ ЛУТА", 
                  command=self.show_loot_capture, width=25).pack(side='left', padx=10)

        buttons = [
            ("1. Анализ розысков", self.show_cases_menu_gui),
            ("2. Статистика наград", self.handle_rewards_menu_gui),
            ("3. Анализ скупки", self.handle_purchase_menu_gui),
            ("4. Анализ лута с рулеток", self.handle_roulette_menu_gui),
            ("5. Управление конфигами цен", self.handle_price_configs_gui),
            ("6. Сменить источник логов", self.create_select_frame),
            ("7. Выход", self.quit)
        ]

        for text, command in buttons:
            btn = ttk.Button(self.main_frame, text=text, command=command, width=50)
            btn.pack(pady=8, fill='x')

    # НОВЫЕ МЕТОДЫ ДЛЯ УЛУЧШЕННЫХ ФУНКЦИЙ
    def show_advanced_clicker(self):
        """Показать улучшенный автокликер"""
        AdvancedClickerWindow(self, self)
        
    def show_loot_capture(self):
        """Показать систему фиксации лута"""
        LootCaptureWindow(self, self)

    # ВСЕ ОСТАЛЬНЫЕ МЕТОДЫ КЛАССА LogAnalyzerApp
    def clear_main_frame(self):
        if hasattr(self, 'main_frame'):
            for widget in self.main_frame.winfo_children():
                widget.destroy()

    def show_table_gui(self, columns, data, title, on_select=None, back_command=None):
        self.clear_main_frame()
        
        if back_command:
            self.push_navigation(back_command)
        
        ttk.Label(self.main_frame, text=title, font=('Arial', 12, 'bold')).pack(pady=10)

        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(expand=True, fill='both', pady=10)

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Таблица")

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(expand=True, fill='both')

        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        for row in data:
            tree.insert('', 'end', values=row)
        tree.pack(expand=True, fill='both', side='left')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)

        if on_select:
            def select_event(e):
                selected = tree.selection()
                if selected:
                    index = tree.index(selected[0])
                    on_select(index)
            tree.bind("<<TreeviewSelect>>", select_event)

        ttk.Button(frame, text="Назад", command=back_command or self.display_main_menu).pack(pady=10)

    def show_text_gui(self, text_content, title, back_command=None):
        self.clear_main_frame()
        
        if back_command:
            self.push_navigation(back_command)
        
        ttk.Label(self.main_frame, text=title, font=('Arial', 12, 'bold')).pack(pady=10)

        text_widget = scrolledtext.ScrolledText(self.main_frame, wrap='word', font=('Courier', 10), height=20)
        text_widget.insert('end', text_content)
        text_widget.config(state='disabled')
        text_widget.pack(expand=True, fill='both')

        ttk.Button(self.main_frame, text="Назад", command=back_command or self.display_main_menu).pack(pady=10)

    def show_graph_gui(self, fig, title, back_command=None, click_handler=None):
        self.clear_main_frame()
        
        if back_command:
            self.push_navigation(back_command)
        
        ttk.Label(self.main_frame, text=title, font=('Arial', 12, 'bold')).pack(pady=10)

        try:
            canvas = FigureCanvasTkAgg(fig, master=self.main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill='both')

            if click_handler:
                canvas.mpl_connect('button_press_event', click_handler)
                
        except Exception as e:
            error_text = f"Ошибка при отображении графика: {str(e)}\n\n"
            error_text += "График не может быть отображен из-за проблем со шрифтами.\n"
            error_text += "Рекомендуется использовать текстовый вывод статистики."
            
            error_label = ttk.Label(self.main_frame, text=error_text, foreground='red', wraplength=800)
            error_label.pack(pady=20)

        ttk.Button(self.main_frame, text="Назад", command=back_command or self.display_main_menu).pack(pady=10)

    def summarize_cases_by_day(self, cases):
        summary = defaultdict(lambda: {"total":0, "exit":0, "system":0})
        for c in cases:
            day = c.get("file_date")
            if day:
                summary[day]["total"] += 1
                if c.get("exit_found"):
                    summary[day]["exit"] += 1
                if c.get("accuser") == "Система":
                    summary[day]["system"] += 1
        return summary

    def show_cases_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text="АНАЛИЗ РОЗЫСКОВ", font=('Arial', 12, 'bold')).pack(pady=10)

        # Фильтрация случаев в зависимости от настройки ползунка
        if self.include_no_exit.get():
            cases_to_show = self.all_cases
        else:
            cases_to_show = [c for c in self.all_cases if c.get("exit_found")]

        ttk.Button(self.main_frame, text="Показать все случаи", 
                  command=lambda: self.show_and_save_gui(cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Показать случаи за день", 
                  command=lambda: self.show_day_cases_gui(cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Поиск по обвинителю", 
                  command=lambda: self.handle_nick_cases_gui("обвинителя", cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Поиск по жертве", 
                  command=lambda: self.handle_nick_cases_gui("жертвы", cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Топ обвинителей", 
                  command=lambda: self.show_top_individual_gui("обвинителей", cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Топ жертв", 
                  command=lambda: self.show_top_individual_gui("жертв", cases_to_show)).pack(pady=5)
        ttk.Button(self.main_frame, text="Графики динамики", 
                  command=self.show_cases_charts_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", 
                  command=self.display_main_menu).pack(pady=5)

    def show_day_cases_gui(self, cases):
        days = sorted(set(c["file_date"] for c in cases if c.get("file_date")))
        if not days:
            messagebox.showinfo("Инфо", "Нет доступных дней.")
            return
        columns = ["№", "Дата"]
        data = [[i+1, str(day)] for i, day in enumerate(days)]
        
        def on_select(index):
            day = days[index]
            filtered_cases = [c for c in cases if c.get("file_date") == day]
            self.show_and_save_gui(filtered_cases)
        
        self.show_table_gui(columns, data, "Выберите день для просмотра случаев", on_select, self.show_cases_menu_gui)

    def show_and_save_gui(self, cases):
        if not cases:
            messagebox.showinfo("Инфо", "Нет случаев.")
            return
            
        # ИСПРАВЛЕННЫЕ КОЛОНКИ
        columns = ["№", "Файл", "Обвинитель", "Игрок", "Звезды", "Время дела", "Время посадки", "Причина", "Выход"]
        data = []
        for i, case in enumerate(cases, 1):
            reason = case.get('reason', 'Неизвестно')
            stars = case.get('stars', '0')
            data.append([
                i,
                case.get('source_file', 'Неизвестно'),
                case.get('accuser', 'Неизвестно'),
                case.get('player', 'Неизвестно'),
                stars + " ★",
                case.get('case_time', 'Неизвестно'),
                case.get('arrest_time', 'Неизвестно'),
                reason[:30] + '...' if len(reason) > 30 else reason,
                'Да' if case.get('exit_found') else 'Нет'
            ])

        def on_select(index):
            self.show_case_details_gui(cases[index])
        
        self.show_table_gui(columns, data, f"Найдено {len(cases)} случаев", on_select, self.show_cases_menu_gui)

        ttk.Button(self.main_frame, text="Сохранить в файл", command=lambda: self.save_cases_gui(cases)).pack(pady=5)

    def save_cases_gui(self, cases):
        output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as out_file:
                    for i, case in enumerate(cases, 1):
                        out_file.write(f"Случай {i} (файл: {case.get('source_file','Неизвестно')}):\n")
                        for line in case["block"]:
                            out_file.write(line + "\n")
                        out_file.write("\n" + "-"*50 + "\n\n")
                messagebox.showinfo("Сохранено", f"Сохранено в {output_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def show_case_details_gui(self, case):
        detail_window = tk.Toplevel(self)
        detail_window.title("Детали случая")
        detail_window.geometry("600x400")
        text = scrolledtext.ScrolledText(detail_window, wrap='word', font=('Courier', 10))
        text.insert('end', f"Файл: {case.get('source_file', 'Неизвестно')}\n")
        text.insert('end', f"Дата: {case.get('file_date', 'Неизвестно')}\n")
        text.insert('end', f"Обвинитель: {case.get('accuser', 'Неизвестно')}\n")
        text.insert('end', f"Игрок: {case.get('player', 'Неизвестно')}\n")
        text.insert('end', f"Звезды: {case.get('stars', '0')} ★\n")
        text.insert('end', f"Время дела: {case.get('case_time', 'Неизвестно')}\n")
        text.insert('end', f"Время посадки: {case.get('arrest_time', 'Неизвестно')}\n")
        text.insert('end', f"Причина: {case.get('reason', 'Неизвестно')}\n")
        text.insert('end', f"Выход: {'Да' if case.get('exit_found') else 'Нет'}\n\n")
        for line in case["block"]:
            text.insert('end', line + "\n")
        text.config(state='disabled')
        text.pack(expand=True, fill='both')

    def handle_nick_cases_gui(self, role, cases):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text=f"Поиск по {role}", font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Label(self.main_frame, text="Введите ник:").pack(pady=5)
        nick_entry = ttk.Entry(self.main_frame, width=30, font=('Arial', 11))
        nick_entry.pack(pady=5)

        def perform_search():
            nick = nick_entry.get().strip()
            if not nick:
                messagebox.showwarning("Ошибка", f"Введите ник {role}")
                return
            self.perform_nick_search_gui(nick, role, cases)

        ttk.Button(self.main_frame, text="Поиск", command=perform_search).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", command=self.display_main_menu).pack(pady=5)

    def perform_nick_search_gui(self, nick, role, cases):
        if role == "обвинителя":
            filtered = [c for c in cases if c.get("accuser") == nick]
        else:
            filtered = [c for c in cases if c.get("player") == nick]

        if not filtered:
            messagebox.showinfo("Результат", f"Случаев для {nick} не найдено")
            return

        self.clear_main_frame()
        self.push_navigation(lambda: self.handle_nick_cases_gui(role, cases))
        
        ttk.Label(self.main_frame, text=f"Случаи для {nick}").pack(pady=10)

        ttk.Button(self.main_frame, text="Показать все", command=lambda: self.show_and_save_gui(filtered)).pack(pady=5)
        ttk.Button(self.main_frame, text="По дням", command=lambda: self.show_nick_days_gui(filtered, nick, role)).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=lambda: self.handle_nick_cases_gui(role, cases)).pack(pady=5)

    def show_nick_days_gui(self, filtered, nick, role):
        daily_summary = self.summarize_cases_by_day(filtered)
        days = sorted(daily_summary.keys())
        columns = ["№", "Дата", "Всего", "Выходов", "% выхода", "Системных"]
        data = []
        for i, day in enumerate(days):
            total = daily_summary[day]["total"]
            exit_count = daily_summary[day]["exit"]
            system_count = daily_summary[day]["system"]
            exit_percent = (exit_count/total*100) if total > 0 else 0
            data.append([i+1, str(day), total, exit_count, f"{exit_percent:.1f}%", system_count])
        
        def on_select(index):
            day = days[index]
            day_cases = [c for c in filtered if c.get("file_date") == day]
            self.show_and_save_gui(day_cases)
        
        self.show_table_gui(columns, data, "По дням", on_select, lambda: self.perform_nick_search_gui(nick, role, filtered))

    def show_top_individual_gui(self, role, cases):
        if role == "обвинителей":
            count = defaultdict(int)
            for c in cases:
                if c.get("accuser"):
                    count[c["accuser"]] += 1
            title = "ТОП ОБВИНИТЕЛЕЙ"
            sorted_top = sorted(count.items(), key=lambda x: x[1], reverse=True)[:10]
            columns = ["Место", "Ник", "Количество"]
            data = [[i+1, nick, cnt] for i, (nick, cnt) in enumerate(sorted_top)]
            
        else:
            count = defaultdict(int)
            stars_count = defaultdict(int)
            
            for c in cases:
                if c.get("player"):
                    count[c["player"]] += 1
                    stars = int(c.get('stars', 0))
                    stars_count[c["player"]] += stars
            
            title = "ТОП ЖЕРТВ"
            sorted_top = sorted(count.items(), key=lambda x: x[1], reverse=True)[:10]
            columns = ["Место", "Ник", "Количество", "Всего звезд", "Средние звезды"]
            data = []
            for i, (nick, cnt) in enumerate(sorted_top):
                total_stars = stars_count[nick]
                avg_stars = total_stars / cnt if cnt > 0 else 0
                data.append([i+1, nick, cnt, total_stars, f"{avg_stars:.1f}"])
        
        self.show_table_gui(columns, data, title, None, self.display_main_menu)

    def show_cases_charts_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.show_cases_menu_gui)
        
        ttk.Label(self.main_frame, text="ГРАФИКИ ДИНАМИКИ РОЗЫСКОВ", font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Button(self.main_frame, text="Столбчатая диаграмма по дням", 
                  command=self.show_cases_bar_chart).pack(pady=5)
        ttk.Button(self.main_frame, text="Линейный график по дням", 
                  command=self.show_cases_line_chart).pack(pady=5)
        ttk.Button(self.main_frame, text="Диаграмма по часам (выбранный день)", 
                  command=self.show_cases_hourly_chart).pack(pady=5)
        ttk.Button(self.main_frame, text="Выдачи по системе", 
                  command=self.show_system_cases_chart).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", 
                  command=self.show_cases_menu_gui).pack(pady=5)

    def show_cases_bar_chart(self):
        daily_summary = self.summarize_cases_by_day(self.all_cases)
        if not daily_summary:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return

        days = [str(day) for day in sorted(daily_summary.keys())]
        total_cases = [daily_summary[day]["total"] for day in sorted(daily_summary.keys())]
        exit_cases = [daily_summary[day]["exit"] for day in sorted(daily_summary.keys())]
        system_cases = [daily_summary[day]["system"] for day in sorted(daily_summary.keys())]

        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(days))
        width = 0.25
        
        bars1 = ax.bar(x - width, total_cases, width, label='Всего случаев', color='blue', alpha=0.7)
        bars2 = ax.bar(x, exit_cases, width, label='Выходы с игры', color='red', alpha=0.7)
        bars3 = ax.bar(x + width, system_cases, width, label='Выдачи по системе', color='green', alpha=0.7)
        
        ax.set_title('Динамика розысков по дням', fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Количество случаев')
        ax.set_xticks(x)
        ax.set_xticklabels(days, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        interactive_chart = InteractiveChart(fig, ax, "bar")
        interactive_chart.set_data(days, total_cases)
        
        def on_bar_click(label, value, index):
            selected_day = list(sorted(daily_summary.keys()))[index]
            if self.include_no_exit.get():
                day_cases = [c for c in self.all_cases if c.get("file_date") == selected_day]
            else:
                day_cases = [c for c in self.all_cases if c.get("file_date") == selected_day and c.get("exit_found")]
            self.show_and_save_gui(day_cases)
        
        interactive_chart.add_highlight_handler(click_callback=on_bar_click)
        
        plt.tight_layout()
        self.show_graph_gui(fig, "Динамика розысков по дням", self.show_cases_charts_gui)

    def show_cases_line_chart(self):
        daily_summary = self.summarize_cases_by_day(self.all_cases)
        if not daily_summary:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return

        days = [str(day) for day in sorted(daily_summary.keys())]
        total_cases = [daily_summary[day]["total"] for day in sorted(daily_summary.keys())]
        exit_cases = [daily_summary[day]["exit"] for day in sorted(daily_summary.keys())]
        system_cases = [daily_summary[day]["system"] for day in sorted(daily_summary.keys())]

        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.plot(days, total_cases, marker='o', linewidth=2, markersize=6, label='Всего случаев', color='blue')
        ax.plot(days, exit_cases, marker='s', linewidth=2, markersize=6, label='Выходы с игры', color='red')
        ax.plot(days, system_cases, marker='^', linewidth=2, markersize=6, label='Выдачи по системе', color='green')
        
        ax.set_title('Динамика розысков по дням', fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Количество случаев')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        interactive_chart = InteractiveChart(fig, ax, "line")
        interactive_chart.set_data(days, total_cases)
        
        def on_point_click(label, value, index):
            selected_day = list(sorted(daily_summary.keys()))[index]
            if self.include_no_exit.get():
                day_cases = [c for c in self.all_cases if c.get("file_date") == selected_day]
            else:
                day_cases = [c for c in self.all_cases if c.get("file_date") == selected_day and c.get("exit_found")]
            self.show_and_save_gui(day_cases)
        
        interactive_chart.add_highlight_handler(click_callback=on_point_click)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        self.show_graph_gui(fig, "Динамика розысков по дням", self.show_cases_charts_gui)

    def show_system_cases_chart(self):
        """НОВЫЙ ГРАФИК - ВЫДАЧИ ПО СИСТЕМЕ"""
        system_cases = [c for c in self.all_cases if c.get("accuser") == "Система"]
        if not system_cases:
            messagebox.showinfo("Инфо", "Нет данных о выдачах по системе")
            return

        daily_summary = defaultdict(int)
        for case in system_cases:
            day = case.get("file_date")
            if day:
                daily_summary[day] += 1

        days = [str(day) for day in sorted(daily_summary.keys())]
        counts = [daily_summary[day] for day in sorted(daily_summary.keys())]

        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.bar(days, counts, color='orange', alpha=0.7)
        
        ax.set_title('Выдачи по системе по дням', fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Количество выдач')
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days, rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Добавляем значения на столбцы
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   str(count), ha='center', va='bottom')
        
        interactive_chart = InteractiveChart(fig, ax, "bar")
        interactive_chart.set_data(days, counts)
        
        def on_bar_click(label, value, index):
            selected_day = list(sorted(daily_summary.keys()))[index]
            day_cases = [c for c in system_cases if c.get("file_date") == selected_day]
            self.show_and_save_gui(day_cases)
        
        interactive_chart.add_highlight_handler(click_callback=on_bar_click)
        
        plt.tight_layout()
        self.show_graph_gui(fig, "Выдачи по системе", self.show_cases_charts_gui)

    def show_cases_hourly_chart(self):
        days = sorted(set(c["file_date"] for c in self.all_cases if c.get("file_date")))
        if not days:
            messagebox.showinfo("Инфо", "Нет доступных дней.")
            return
        
        self.clear_main_frame()
        self.push_navigation(self.show_cases_charts_gui)
        
        ttk.Label(self.main_frame, text="Выберите день для построения графика по часам", font=('Arial', 12, 'bold')).pack(pady=10)
        
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(self.main_frame, textvariable=day_var, values=[str(day) for day in days], state="readonly")
        day_combo.pack(pady=10)
        
        def show_chart():
            selected_day = day_var.get()
            if not selected_day:
                messagebox.showwarning("Ошибка", "Выберите день")
                return
                
            hourly_cases = defaultdict(lambda: {"total": 0, "exit": 0, "system": 0})
            for case in self.all_cases:
                if str(case.get("file_date")) == selected_day and case.get("case_time") != "Неизвестно":
                    try:
                        case_time = parse_time_extended(case["case_time"])
                        if case_time:
                            hour = case_time.hour
                            hourly_cases[hour]["total"] += 1
                            if case.get("exit_found"):
                                hourly_cases[hour]["exit"] += 1
                            if case.get("accuser") == "Система":
                                hourly_cases[hour]["system"] += 1
                    except:
                        continue
            
            if not hourly_cases:
                messagebox.showinfo("Инфо", f"Нет данных за {selected_day}")
                return
            
            hours = sorted(hourly_cases.keys())
            total_cases = [hourly_cases[hour]["total"] for hour in hours]
            exit_cases = [hourly_cases[hour]["exit"] for hour in hours]
            system_cases = [hourly_cases[hour]["system"] for hour in hours]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            x = np.arange(len(hours))
            width = 0.25
            
            bars1 = ax.bar(x - width, total_cases, width, label='Всего случаев', color='blue', alpha=0.7)
            bars2 = ax.bar(x, exit_cases, width, label='Выходы с игры', color='red', alpha=0.7)
            bars3 = ax.bar(x + width, system_cases, width, label='Выдачи по системе', color='green', alpha=0.7)
            
            ax.set_title(f'Распределение розысков по часам за {selected_day}', fontsize=16, fontweight='bold')
            ax.set_xlabel('Час')
            ax.set_ylabel('Количество случаев')
            ax.set_xticks(x)
            ax.set_xticklabels([f"{hour:02d}:00" for hour in hours])
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            interactive_chart = InteractiveChart(fig, ax, "bar")
            interactive_chart.set_data([f"{hour:02d}:00" for hour in hours], total_cases)
            
            def on_hour_click(label, value, index):
                hour = hours[index]
                if self.include_no_exit.get():
                    hour_cases = [c for c in self.all_cases if str(c.get("file_date")) == selected_day 
                                 and c.get("case_time") != "Неизвестно"
                                 and parse_time_extended(c["case_time"]).hour == hour]
                else:
                    hour_cases = [c for c in self.all_cases if str(c.get("file_date")) == selected_day 
                                 and c.get("case_time") != "Неизвестно"
                                 and parse_time_extended(c["case_time"]).hour == hour
                                 and c.get("exit_found")]
                self.show_and_save_gui(hour_cases)
            
            interactive_chart.add_highlight_handler(click_callback=on_hour_click)
            
            plt.tight_layout()
            self.show_graph_gui(fig, f"Распределение розысков по часам за {selected_day}", self.show_cases_charts_gui)
        
        ttk.Button(self.main_frame, text="Показать график", command=show_chart).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", command=self.show_cases_charts_gui).pack(pady=5)

    # СИСТЕМА КОНФИГОВ ЦЕН (ПОЛНЫЙ КОД)
    def handle_price_configs_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text="УПРАВЛЕНИЕ КОНФИГАМИ ЦЕН", font=('Arial', 14, 'bold')).pack(pady=20)

        buttons = [
            ("1. Конфиг цен для тайников/сундуков", self.handle_chest_price_config_gui),
            ("2. Конфиг цен для рулеток", self.handle_roulette_price_config_gui),
            ("3. Импорт конфига цен", self.import_price_config_gui),
            ("4. Экспорт конфига цен", self.export_price_config_gui),
            ("5. Назад", self.display_main_menu)
        ]

        for text, command in buttons:
            btn = ttk.Button(self.main_frame, text=text, command=command, width=40)
            btn.pack(pady=8)

    def handle_chest_price_config_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_price_configs_gui)
        
        ttk.Label(self.main_frame, text="КОНФИГ ЦЕН ДЛЯ ТАЙНИКОВ/СУНДУКОВ", font=('Arial', 14, 'bold')).pack(pady=10)
        
        all_items = set()
        for day_items in self.chest_stats.values():
            all_items.update(day_items.keys())
        
        if not all_items:
            messagebox.showinfo("Инфо", "Нет данных о предметах из тайников")
            self.handle_price_configs_gui()
            return
        
        if not self.price_manager.current_config:
            self.price_manager.create_new_config(all_items)
        
        config_frame = ttk.Frame(self.main_frame)
        config_frame.pack(pady=10, fill='x')
        
        ttk.Button(config_frame, text="Создать новый конфиг", 
                  command=lambda: self.create_new_chest_price_config(all_items)).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Загрузить конфиг", 
                  command=self.load_chest_price_config).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Сохранить конфиг", 
                  command=self.save_chest_price_config).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Сохранить как...", 
                  command=self.save_chest_price_config_as).pack(side='left', padx=5)
        
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(expand=True, fill='both', pady=10)
        
        columns = ("Предмет", "Количество", "Цена", "Общая стоимость")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        
        tree.column("Предмет", width=300, anchor='w')
        
        total_value = 0
        for item in sorted(all_items):
            count = sum(day_items.get(item, 0) for day_items in self.chest_stats.values())
            price = self.price_manager.get_price(item)
            item_value = count * price
            total_value += item_value
            
            tree.insert('', 'end', values=(item, count, f"${price:,}", f"${item_value:,}"))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        ttk.Label(self.main_frame, text=f"Общая стоимость лута: ${total_value:,}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        def on_double_click(event):
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0], 'values')[0]
                self.edit_chest_price(item, tree)
        
        tree.bind('<Double-1>', on_double_click)
        
        ttk.Button(self.main_frame, text="Редактировать выбранный предмет", 
                  command=lambda: self.edit_selected_chest_price(tree)).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", 
                  command=self.handle_price_configs_gui).pack(pady=5)
        
        self.chest_price_tree = tree

    def create_new_chest_price_config(self, items):
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Выберите папку и имя для нового конфига")
        if config_path:
            self.price_manager.create_new_config(items, config_path)
            messagebox.showinfo("Успех", f"Создан новый конфиг: {config_path}")
            self.handle_chest_price_config_gui()

    def load_chest_price_config(self):
        config_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if config_path:
            if self.price_manager.load_config(config_path):
                messagebox.showinfo("Успех", "Конфиг загружен!")
                self.handle_chest_price_config_gui()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить конфиг")

    def save_chest_price_config(self):
        if not self.price_manager.config_path:
            self.save_chest_price_config_as()
        else:
            if self.price_manager.save_config():
                messagebox.showinfo("Успех", "Конфиг сохранен!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить конфиг")

    def save_chest_price_config_as(self):
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")])
        if config_path:
            self.price_manager.config_path = config_path
            if self.price_manager.save_config():
                messagebox.showinfo("Успех", f"Конфиг сохранен в: {config_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить конфиг")

    def edit_chest_price(self, item, tree):
        current_price = self.price_manager.get_price(item)
        new_price = simpledialog.askinteger("Редактирование цены", 
                                          f"Цена для '{item}':", 
                                          initialvalue=current_price,
                                          minvalue=0)
        if new_price is not None:
            self.price_manager.set_price(item, new_price)
            self.update_chest_price_tree(tree)

    def edit_selected_chest_price(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите предмет для редактирования")
            return
        item = tree.item(selected[0], 'values')[0]
        self.edit_chest_price(item, tree)

    def update_chest_price_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        all_items = set()
        for day_items in self.chest_stats.values():
            all_items.update(day_items.keys())
        
        total_value = 0
        for item in sorted(all_items):
            count = sum(day_items.get(item, 0) for day_items in self.chest_stats.values())
            price = self.price_manager.get_price(item)
            item_value = count * price
            total_value += item_value
            
            tree.insert('', 'end', values=(item, count, f"${price:,}", f"${item_value:,}"))

    # Аналогичные методы для рулеток
    def handle_roulette_price_config_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_price_configs_gui)
        
        ttk.Label(self.main_frame, text="КОНФИГ ЦЕН ДЛЯ РУЛЕТОК", font=('Arial', 14, 'bold')).pack(pady=10)
        
        all_items = set()
        for day_data in self.roulette_stats.values():
            for roulette_type, items in day_data.items():
                all_items.update(items.keys())
        
        if not all_items:
            messagebox.showinfo("Инфо", "Нет данных о предметах из рулеток")
            self.handle_price_configs_gui()
            return
        
        if not self.roulette_price_manager.current_config:
            self.roulette_price_manager.create_new_config(all_items)
        
        config_frame = ttk.Frame(self.main_frame)
        config_frame.pack(pady=10, fill='x')
        
        ttk.Button(config_frame, text="Создать новый конфиг", 
                  command=lambda: self.create_new_roulette_price_config(all_items)).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Загрузить конфиг", 
                  command=self.load_roulette_price_config).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Сохранить конфиг", 
                  command=self.save_roulette_price_config).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Сохранить как...", 
                  command=self.save_roulette_price_config_as).pack(side='left', padx=5)
        
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(expand=True, fill='both', pady=10)
        
        columns = ("Предмет", "Количество", "Цена", "Общая стоимость")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        
        tree.column("Предмет", width=300, anchor='w')
        
        total_value = 0
        for item in sorted(all_items):
            count = 0
            for day_data in self.roulette_stats.values():
                for roulette_type, items in day_data.items():
                    count += items.get(item, 0)
            
            price = self.roulette_price_manager.get_price(item)
            item_value = count * price
            total_value += item_value
            
            tree.insert('', 'end', values=(item, count, f"${price:,}", f"${item_value:,}"))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        ttk.Label(self.main_frame, text=f"Общая стоимость лута: ${total_value:,}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        def on_double_click(event):
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0], 'values')[0]
                self.edit_roulette_price(item, tree)
        
        tree.bind('<Double-1>', on_double_click)
        
        ttk.Button(self.main_frame, text="Редактировать выбранный предмет", 
                  command=lambda: self.edit_selected_roulette_price(tree)).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", 
                  command=self.handle_price_configs_gui).pack(pady=5)
        
        self.roulette_price_tree = tree

    def create_new_roulette_price_config(self, items):
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Выберите папку и имя для нового конфига")
        if config_path:
            self.roulette_price_manager.create_new_config(items, config_path)
            messagebox.showinfo("Успех", f"Создан новый конфиг: {config_path}")
            self.handle_roulette_price_config_gui()

    def load_roulette_price_config(self):
        config_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if config_path:
            if self.roulette_price_manager.load_config(config_path):
                messagebox.showinfo("Успех", "Конфиг загружен!")
                self.handle_roulette_price_config_gui()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить конфиг")

    def save_roulette_price_config(self):
        if not self.roulette_price_manager.config_path:
            self.save_roulette_price_config_as()
        else:
            if self.roulette_price_manager.save_config():
                messagebox.showinfo("Успех", "Конфиг сохранен!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить конфиг")

    def save_roulette_price_config_as(self):
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")])
        if config_path:
            self.roulette_price_manager.config_path = config_path
            if self.roulette_price_manager.save_config():
                messagebox.showinfo("Успех", f"Конфиг сохранен в: {config_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить конфиг")

    def edit_roulette_price(self, item, tree):
        current_price = self.roulette_price_manager.get_price(item)
        new_price = simpledialog.askinteger("Редактирование цены", 
                                          f"Цена для '{item}':", 
                                          initialvalue=current_price,
                                          minvalue=0)
        if new_price is not None:
            self.roulette_price_manager.set_price(item, new_price)
            self.update_roulette_price_tree(tree)

    def edit_selected_roulette_price(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите предмет для редактирования")
            return
        item = tree.item(selected[0], 'values')[0]
        self.edit_roulette_price(item, tree)

    def update_roulette_price_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        all_items = set()
        for day_data in self.roulette_stats.values():
            for roulette_type, items in day_data.items():
                all_items.update(items.keys())
        
        total_value = 0
        for item in sorted(all_items):
            count = 0
            for day_data in self.roulette_stats.values():
                for roulette_type, items in day_data.items():
                    count += items.get(item, 0)
            
            price = self.roulette_price_manager.get_price(item)
            item_value = count * price
            total_value += item_value
            
            tree.insert('', 'end', values=(item, count, f"${price:,}", f"${item_value:,}"))

    def import_price_config_gui(self):
        config_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                is_roulette_config = any('рулетка' in key.lower() or 'az' in key.lower() for key in config_data.keys())
                
                if is_roulette_config:
                    if self.roulette_price_manager.load_config(config_path):
                        messagebox.showinfo("Успех", "Конфиг цен для рулеток загружен!")
                    else:
                        messagebox.showerror("Ошибка", "Не удалось загрузить конфиг")
                else:
                    if self.price_manager.load_config(config_path):
                        messagebox.showinfo("Успех", "Конфиг цен для тайников загружен!")
                    else:
                        messagebox.showerror("Ошибка", "Не удалось загрузить конфиг")
                        
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка чтения файла: {e}")

    def export_price_config_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_price_configs_gui)
        
        ttk.Label(self.main_frame, text="ЭКСПОРТ КОНФИГА ЦЕН", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Button(self.main_frame, text="Экспорт конфига для тайников", 
                  command=self.export_chest_config).pack(pady=10)
        ttk.Button(self.main_frame, text="Экспорт конфига для рулеток", 
                  command=self.export_roulette_config).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", 
                  command=self.handle_price_configs_gui).pack(pady=5)

    def export_chest_config(self):
        if not self.price_manager.current_config:
            messagebox.showinfo("Инфо", "Нет данных для экспорта")
            return
            
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")])
        if config_path:
            if self.price_manager.save_config(config_path):
                messagebox.showinfo("Успех", f"Конфиг экспортирован в: {config_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать конфиг")

    def export_roulette_config(self):
        if not self.roulette_price_manager.current_config:
            messagebox.showinfo("Инфо", "Нет данных для экспорта")
            return
            
        config_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")])
        if config_path:
            if self.roulette_price_manager.save_config(config_path):
                messagebox.showinfo("Успех", f"Конфиг экспортирован в: {config_path}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать конфиг")

    # ОСТАЛЬНЫЕ РАЗДЕЛЫ (статистика наград, скупки, рулеток)
    def handle_rewards_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text="СТАТИСТИКА НАГРАД").pack(pady=10)
        ttk.Button(self.main_frame, text="Депозит + ЗП", command=self.show_deposit_stats_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Тайники и сундуки", command=self.handle_chest_menu_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=self.display_main_menu).pack(pady=5)

    def show_deposit_stats_gui(self):
        table_data = []
        total_deposit = 0
        total_salary = 0
        total_combined = 0
        for day, data in sorted(self.deposit_stats.items()):
            day_deposit = data["deposit"]
            day_salary = data["salary"]
            day_combined = day_deposit + day_salary
            total_deposit += day_deposit
            total_salary += day_salary
            total_combined += day_combined
            table_data.append([str(day), f"${day_deposit:,}", f"${day_salary:,}", f"${day_combined:,}"])
        table_data.append(["ВСЕГО", f"${total_deposit:,}", f"${total_salary:,}", f"${total_combined:,}"])

        columns = ["Дата", "Депозит", "Зарплата", "Общая сумма"]
        self.show_table_gui(columns, table_data, "Статистика заработка", None, self.handle_rewards_menu_gui)

    def handle_chest_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_rewards_menu_gui)
        
        ttk.Label(self.main_frame, text="АНАЛИЗ ЛУТА ИЗ ТАЙНИКОВ/СУНДУКОВ").pack(pady=10)
        ttk.Button(self.main_frame, text="Простой показ", command=self.show_chest_stats_simple_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Детальный показ с ценами", command=self.show_chest_stats_detailed_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="По источникам", command=self.handle_chest_source_menu_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=self.handle_rewards_menu_gui).pack(pady=5)

    def show_chest_stats_simple_gui(self):
        total_items = defaultdict(int)
        for day_items in self.chest_stats.values():
            for item, count in day_items.items():
                total_items[item] += count
        total_count = sum(total_items.values())
        columns = ["Предмет", "Количество", "Процент"]
        data = [[item, count, f"{(count / total_count * 100):.1f}%" if total_count > 0 else 0] for item, count in sorted(total_items.items(), key=lambda x: x[1], reverse=True)]
        self.show_table_gui(columns, data, f"Общая статистика ({total_count} предметов)", None, self.handle_chest_menu_gui)

    def show_chest_stats_detailed_gui(self):
        if not self.price_manager.current_config:
            messagebox.showinfo("Инфо", "Сначала настройте цены в разделе конфигов")
            return

        total_money = 0
        total_count = 0
        for day_items in self.chest_stats.values():
            for item, count in day_items.items():
                total_money += count * self.price_manager.get_price(item)
                total_count += count

        all_items = set()
        for day_items in self.chest_stats.values():
            all_items.update(day_items.keys())

        columns = ["Предмет", "Кол-во", "Цена", "Сумма", "% кол-ва", "% суммы"]
        data = []
        for item in sorted(all_items):
            count = sum(day_items.get(item, 0) for day_items in self.chest_stats.values())
            item_total = count * self.price_manager.get_price(item)
            percentage_count = (count / total_count * 100) if total_count > 0 else 0
            percentage_money = (item_total / total_money * 100) if total_money > 0 else 0
            data.append([item, count, f"${self.price_manager.get_price(item):,}", f"${item_total:,}", f"{percentage_count:.1f}%", f"{percentage_money:.1f}%"])

        self.show_table_gui(columns, data, f"Детальная статистика: {total_count} предметов на ${total_money:,}", None, self.handle_chest_menu_gui)

    def handle_chest_source_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_chest_menu_gui)
        
        ttk.Label(self.main_frame, text="АНАЛИЗ ПО ИСТОЧНИКАМ").pack(pady=10)
        
        all_possible_sources = [
            "Тайник Илона Маска",
            "Тайник Лос Сантоса", 
            "Тайник Vice City",
            "Сундук с рулетками",
            "Платиновый сундук с рулетками",
        ]
        
        data_sources = set()
        for day_data in self.chest_source_stats.values():
            data_sources.update(day_data.keys())
        
        sources = list(set(all_possible_sources) | data_sources)
        
        if not sources:
            messagebox.showinfo("Инфо", "Нет данных по источникам")
            return
            
        columns = ["№", "Источник", "Статус"]
        data = []
        for i, source in enumerate(sorted(sources)):
            status = "Есть данные" if source in data_sources else "Нет данных"
            data.append([i+1, source, status])
        
        def on_select(index):
            source = sorted(sources)[index]
            if source in data_sources:
                self.show_source_stats_gui(source)
            else:
                messagebox.showinfo("Инфо", f"Нет данных для источника: {source}")
        
        self.show_table_gui(columns, data, "Выберите источник", on_select, self.handle_chest_menu_gui)

    def show_source_stats_gui(self, source):
        total_items = defaultdict(int)
        for day_data in self.chest_source_stats.values():
            if source in day_data:
                for item, count in day_data[source].items():
                    total_items[item] += count
        
        total_count = sum(total_items.values())
        columns = ["Предмет", "Количество", "Процент"]
        data = [[item, count, f"{(count / total_count * 100):.1f}%" if total_count > 0 else 0] for item, count in sorted(total_items.items(), key=lambda x: x[1], reverse=True)]
        self.show_table_gui(columns, data, f"{source}: {total_count} предметов", None, self.handle_chest_source_menu_gui)

    def handle_purchase_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text="АНАЛИЗ СКУПКИ", font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Button(self.main_frame, text="Показать по дням", command=self.show_purchase_by_day_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Общая статистика", command=self.show_purchase_all_days_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Фильтр по времени", command=self.show_purchase_time_filter_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Графики", command=self.handle_purchase_charts_menu_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Тенденция по часам", command=self.show_purchase_hourly_trend_gui).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=self.display_main_menu).pack(pady=5)

    def show_purchase_by_day_gui(self):
        days = sorted(self.purchase_stats.keys())
        if not days:
            messagebox.showinfo("Инфо", "Нет данных о скупке")
            return

        columns = ["№", "Дата"]
        data = [[i+1, str(day)] for i, day in enumerate(days)]
        
        def on_select(index):
            day = days[index]
            self.show_purchase_stats_for_day_gui(day)
        
        self.show_table_gui(columns, data, "Выберите день для просмотра скупки", on_select, self.handle_purchase_menu_gui)

    def show_purchase_stats_for_day_gui(self, day):
        day_stats = self.purchase_stats[day]
        day_logs = self.purchase_logs[day]

        total_quantity = sum(stats["quantity"] for stats in day_stats.values())
        total_price = sum(stats["total_price"] for stats in day_stats.values())
        total_transactions = sum(stats["transactions"] for stats in day_stats.values())

        columns = ["Предмет", "Транзакций", "% транз.", "Кол-во", "% кол-ва", "Сумма", "% суммы"]
        data = []
        for item, stats in sorted(day_stats.items(), key=lambda x: x[1]["total_price"], reverse=True):
            percent_transactions = (stats["transactions"] / total_transactions * 100) if total_transactions > 0 else 0
            percent_quantity = (stats["quantity"] / total_quantity * 100) if total_quantity > 0 else 0
            percent_price = (stats["total_price"] / total_price * 100) if total_price > 0 else 0
            data.append([item, stats["transactions"], f"{percent_transactions:.1f}%", stats["quantity"], f"{percent_quantity:.1f}%", f"${stats['total_price']:,}", f"{percent_price:.1f}%"])

        self.show_table_gui(columns, data, f"{day}: Транзакций {total_transactions}, шт. {total_quantity}, сумма ${total_price:,}", None, self.show_purchase_by_day_gui)

    def show_purchase_all_days_gui(self):
        all_stats = defaultdict(lambda: {"quantity": 0, "total_price": 0, "transactions": 0})
        for day_stats in self.purchase_stats.values():
            for item, stats in day_stats.items():
                all_stats[item]["quantity"] += stats["quantity"]
                all_stats[item]["total_price"] += stats["total_price"]
                all_stats[item]["transactions"] += stats["transactions"]

        total_quantity = sum(stats["quantity"] for stats in all_stats.values())
        total_price = sum(stats["total_price"] for stats in all_stats.values())
        total_transactions = sum(stats["transactions"] for stats in all_stats.values())

        columns = ["Предмет", "Транзакций", "% транз.", "Кол-во", "% кол-ва", "Сумма", "% суммы"]
        data = []
        for item, stats in sorted(all_stats.items(), key=lambda x: x[1]["total_price"], reverse=True):
            percent_transactions = (stats["transactions"] / total_transactions * 100) if total_transactions > 0 else 0
            percent_quantity = (stats["quantity"] / total_quantity * 100) if total_quantity > 0 else 0
            percent_price = (stats["total_price"] / total_price * 100) if total_price > 0 else 0
            data.append([item, stats["transactions"], f"{percent_transactions:.1f}%", stats["quantity"], f"{percent_quantity:.1f}%", f"${stats['total_price']:,}", f"{percent_price:.1f}%"])

        self.show_table_gui(columns, data, f"Все дни: Транзакций {total_transactions}, шт. {total_quantity}, сумма ${total_price:,}", None, self.handle_purchase_menu_gui)

    def show_purchase_time_filter_gui(self):
        days = sorted(self.purchase_stats.keys())
        columns = ["№", "Дата"]
        data = [[i+1, str(day)] for i, day in enumerate(days)]
        
        def on_select(index):
            day = days[index]
            self.handle_time_filter_gui(day)
        
        self.show_table_gui(columns, data, "Выберите день для фильтра по времени", on_select, self.handle_purchase_menu_gui)

    def handle_time_filter_gui(self, day):
        self.clear_main_frame()
        self.push_navigation(self.show_purchase_time_filter_gui)
        
        ttk.Label(self.main_frame, text="Укажите промежуток времени (HH:MM):").pack(pady=10)

        start_entry = ttk.Entry(self.main_frame)
        start_entry.pack(pady=5)
        start_entry.insert(0, "05:30")

        end_entry = ttk.Entry(self.main_frame)
        end_entry.pack(pady=5)
        end_entry.insert(0, "15:45")

        ttk.Button(self.main_frame, text="Применить", command=lambda: self.apply_time_filter_gui(day, start_entry.get(), end_entry.get())).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", command=self.show_purchase_time_filter_gui).pack(pady=5)

    def apply_time_filter_gui(self, day, start_str, end_str):
        start_time = parse_time_extended(start_str)
        end_time = parse_time_extended(end_str)
        if not start_time or not end_time or start_time >= end_time:
            messagebox.showwarning("Ошибка", "Неверный формат или начало > конца")
            return

        day_logs = self.purchase_logs[day]
        filtered_stats = defaultdict(lambda: {"quantity": 0, "total_price": 0, "transactions": 0})
        for log in day_logs:
            log_time = parse_time_extended(log["time"])
            if log_time and start_time <= log_time < end_time:
                item = log["item"]
                filtered_stats[item]["quantity"] += log["quantity"]
                filtered_stats[item]["total_price"] += log["price"]
                filtered_stats[item]["transactions"] += 1

        self.show_purchase_stats_for_day_gui_with_stats(filtered_stats, day, start_time, end_time)

    def show_purchase_stats_for_day_gui_with_stats(self, filtered_stats, day, start_time, end_time):
        total_quantity = sum(stats["quantity"] for stats in filtered_stats.values())
        total_price = sum(stats["total_price"] for stats in filtered_stats.values())
        total_transactions = sum(stats["transactions"] for stats in filtered_stats.values())

        time_info = f" (с {start_time.strftime('%H:%M')} до {end_time.strftime('%H:%M')})"

        columns = ["Предмет", "Транзакций", "% транз.", "Кол-во", "% кол-ва", "Сумма", "% суммы"]
        data = []
        for item, stats in sorted(filtered_stats.items(), key=lambda x: x[1]["total_price"], reverse=True):
            percent_transactions = (stats["transactions"] / total_transactions * 100) if total_transactions > 0 else 0
            percent_quantity = (stats["quantity"] / total_quantity * 100) if total_quantity > 0 else 0
            percent_price = (stats["total_price"] / total_price * 100) if total_price > 0 else 0
            data.append([item, stats["transactions"], f"{percent_transactions:.1f}%", stats["quantity"], f"{percent_quantity:.1f}%", f"${stats['total_price']:,}", f"{percent_price:.1f}%"])

        self.show_table_gui(columns, data, f"{day}{time_info}: Транзакций {total_transactions}, шт. {total_quantity}, сумма ${total_price:,}", None, self.show_purchase_time_filter_gui)

    def handle_purchase_charts_menu_gui(self):
        days = sorted(self.purchase_stats.keys())
        columns = ["№", "Дата"]
        data = [[i+1, str(day)] for i, day in enumerate(days)]
        
        def on_select(index):
            day = days[index]
            self.ask_chart_type_gui(day)
        
        self.show_table_gui(columns, data, "Выберите день для графиков", on_select, self.handle_purchase_menu_gui)

    def ask_chart_type_gui(self, day):
        self.clear_main_frame()
        self.push_navigation(self.handle_purchase_charts_menu_gui)
        
        ttk.Label(self.main_frame, text=f"Тип графика для {day}").pack(pady=10)

        ttk.Button(self.main_frame, text="Все графики", command=lambda: self.show_purchase_charts_gui(day, "all")).pack(pady=5)
        ttk.Button(self.main_frame, text="Транзакции", command=lambda: self.show_purchase_charts_gui(day, "transactions")).pack(pady=5)
        ttk.Button(self.main_frame, text="Количество", command=lambda: self.show_purchase_charts_gui(day, "quantity")).pack(pady=5)
        ttk.Button(self.main_frame, text="Стоимость", command=lambda: self.show_purchase_charts_gui(day, "price")).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=self.handle_purchase_charts_menu_gui).pack(pady=5)

    def show_purchase_charts_gui(self, day, chart_type):
        day_stats = self.purchase_stats[day]
        items = list(day_stats.keys())
        transactions = [day_stats[item]["transactions"] for item in items]
        quantities = [day_stats[item]["quantity"] for item in items]
        prices = [day_stats[item]["total_price"] for item in items]

        if chart_type == "all":
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Анализ скупки за {day}', fontsize=16, fontweight='bold')

            ax1.barh(items, transactions, color='skyblue')
            ax1.set_xlabel('Количество транзакций')
            ax1.set_title('Транзакции по предметам')
            ax1.grid(axis='x', alpha=0.3)

            ax2.barh(items, quantities, color='lightgreen')
            ax2.set_xlabel('Количество штук')
            ax2.set_title('Количество купленных предметов')
            ax2.grid(axis='x', alpha=0.3)

            ax3.barh(items, prices, color='salmon')
            ax3.set_xlabel('Общая стоимость ($)')
            ax3.set_title('Общая стоимость покупок')
            ax3.grid(axis='x', alpha=0.3)

            total_price = sum(prices)
            if total_price > 0:
                ax4.pie(prices, labels=items, autopct='%1.1f%%', startangle=90)
                ax4.set_title('Распределение стоимости')

            plt.tight_layout()
            self.show_graph_gui(fig, f'Графики за {day}', lambda: self.ask_chart_type_gui(day))

        elif chart_type == "transactions":
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(items, transactions, color='skyblue')
            ax.set_xlabel('Количество транзакций')
            ax.set_title(f'Транзакции по предметам за {day}')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            self.show_graph_gui(fig, f'Транзакции за {day}', lambda: self.ask_chart_type_gui(day))

        elif chart_type == "quantity":
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(items, quantities, color='lightgreen')
            ax.set_xlabel('Количество штук')
            ax.set_title(f'Количество купленных предметов за {day}')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            self.show_graph_gui(fig, f'Количество за {day}', lambda: self.ask_chart_type_gui(day))

        elif chart_type == "price":
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(items, prices, color='salmon')
            ax.set_xlabel('Общая стоимость ($)')
            ax.set_title(f'Общая стоимость покупок за {day}')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            self.show_graph_gui(fig, f'Стоимость за {day}', lambda: self.ask_chart_type_gui(day))

    def show_purchase_hourly_trend_gui(self):
        days = sorted(self.purchase_stats.keys())
        if not days:
            messagebox.showinfo("Инфо", "Нет данных о скупке")
            return

        columns = ["№", "Дата"]
        data = [[i+1, str(day)] for i, day in enumerate(days)]
        
        def on_select(index):
            day = days[index]
            self.ask_hourly_chart_type_gui(day)
        
        self.show_table_gui(columns, data, "Выберите день для анализа по часам", on_select, self.handle_purchase_menu_gui)

    def ask_hourly_chart_type_gui(self, day):
        self.clear_main_frame()
        self.push_navigation(self.show_purchase_hourly_trend_gui)
        
        ttk.Label(self.main_frame, text=f"Выберите тип графика для {day}", font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Button(self.main_frame, text="Все графики", command=lambda: self.show_hourly_trend_for_day(day, "all")).pack(pady=5)
        ttk.Button(self.main_frame, text="Транзакции по часам", command=lambda: self.show_hourly_trend_for_day(day, "transactions")).pack(pady=5)
        ttk.Button(self.main_frame, text="Сумма по часам", command=lambda: self.show_hourly_trend_for_day(day, "price")).pack(pady=5)
        ttk.Button(self.main_frame, text="Количество по часам", command=lambda: self.show_hourly_trend_for_day(day, "quantity")).pack(pady=5)
        ttk.Button(self.main_frame, text="Назад", command=self.show_purchase_hourly_trend_gui).pack(pady=5)

    def show_hourly_trend_for_day(self, day, chart_type="all"):
        day_logs = self.purchase_logs[day]
        
        hourly_stats = defaultdict(lambda: {"transactions": 0, "total_price": 0, "quantity": 0})
        
        for log in day_logs:
            try:
                log_time = parse_time_extended(log["time"])
                if log_time:
                    hour = log_time.hour
                    hourly_stats[hour]["transactions"] += 1
                    hourly_stats[hour]["total_price"] += log["price"]
                    hourly_stats[hour]["quantity"] += log["quantity"]
            except:
                continue
        
        if not hourly_stats:
            messagebox.showinfo("Инфо", f"Нет данных за {day}")
            return
        
        hours = sorted(hourly_stats.keys())
        transactions = [hourly_stats[hour]["transactions"] for hour in hours]
        total_prices = [hourly_stats[hour]["total_price"] for hour in hours]
        quantities = [hourly_stats[hour]["quantity"] for hour in hours]
        
        if chart_type == "all":
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
            fig.suptitle(f'Тенденция скупки по часам за {day}', fontsize=16, fontweight='bold')
            
            bars1 = ax1.bar([f"{hour:02d}:00" for hour in hours], transactions, color='skyblue', alpha=0.7)
            ax1.set_title('Количество транзакций по часам')
            ax1.set_xlabel('Час')
            ax1.set_ylabel('Транзакций')
            ax1.grid(axis='y', alpha=0.3)
            
            for bar, value in zip(bars1, transactions):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(value), ha='center', va='bottom', fontsize=9)
            
            bars2 = ax2.bar([f"{hour:02d}:00" for hour in hours], total_prices, color='lightgreen', alpha=0.7)
            ax2.set_title('Сумма покупок по часам')
            ax2.set_xlabel('Час')
            ax2.set_ylabel('Сумма ($)')
            ax2.grid(axis='y', alpha=0.3)
            
            for bar, value in zip(bars2, total_prices):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        f"${value:,}", ha='center', va='bottom', fontsize=9)
            
            bars3 = ax3.bar([f"{hour:02d}:00" for hour in hours], quantities, color='salmon', alpha=0.7)
            ax3.set_title('Количество предметов по часам')
            ax3.set_xlabel('Час')
            ax3.set_ylabel('Количество')
            ax3.grid(axis='y', alpha=0.3)
            
            for bar, value in zip(bars3, quantities):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(value), ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            self.show_graph_gui(fig, f'Тенденция скупки по часам за {day}', lambda: self.ask_hourly_chart_type_gui(day))
        
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if chart_type == "transactions":
                bars = ax.bar([f"{hour:02d}:00" for hour in hours], transactions, color='skyblue', alpha=0.7)
                ax.set_title(f'Количество транзакций по часам за {day}')
                ax.set_ylabel('Транзакций')
                values = transactions
            elif chart_type == "price":
                bars = ax.bar([f"{hour:02d}:00" for hour in hours], total_prices, color='lightgreen', alpha=0.7)
                ax.set_title(f'Сумма покупок по часам за {day}')
                ax.set_ylabel('Сумма ($)')
                values = total_prices
            elif chart_type == "quantity":
                bars = ax.bar([f"{hour:02d}:00" for hour in hours], quantities, color='salmon', alpha=0.7)
                ax.set_title(f'Количество предметов по часам за {day}')
                ax.set_ylabel('Количество')
                values = quantities
            
            ax.set_xlabel('Час')
            ax.grid(axis='y', alpha=0.3)
            
            for bar, value in zip(bars, values):
                if chart_type == "price":
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                            f"${value:,}", ha='center', va='bottom', fontsize=9)
                else:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                            str(value), ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            self.show_graph_gui(fig, f'Тенденция скупки по часам за {day}', lambda: self.ask_hourly_chart_type_gui(day))

    def handle_roulette_menu_gui(self):
        self.clear_main_frame()
        self.push_navigation(self.display_main_menu)
        
        ttk.Label(self.main_frame, text="АНАЛИЗ ЛУТА С РУЛЕТОК", font=('Arial', 14, 'bold')).pack(pady=20)

        buttons = [
            ("1. Общая статистика за все время", self.show_roulette_stats_all_time),
            ("2. Статистика по дням", self.show_roulette_stats_by_day),
            ("3. Статистика по часам", self.show_roulette_stats_by_hour),
            ("4. Подсчет стоимости за AZ", self.show_az_calculator),
            ("5. Графики выпадений", self.show_roulette_charts_menu),
            ("6. Назад", self.display_main_menu)
        ]

        for text, command in buttons:
            btn = ttk.Button(self.main_frame, text=text, command=command, width=40)
            btn.pack(pady=5)

    def show_roulette_stats_all_time(self):
        total_stats = defaultdict(lambda: defaultdict(int))
        total_attempts = 0
        
        for day_data in self.roulette_stats.values():
            for roulette_type, items in day_data.items():
                for item, quantity in items.items():
                    total_stats[roulette_type][item] += quantity
                total_attempts += sum(items.values())
        
        if not total_stats:
            messagebox.showinfo("Инфо", "Нет данных о выпадениях из рулеток")
            return
        
        columns = ["Тип рулетки", "Предмет", "Количество", "Процент"]
        data = []
        
        for roulette_type in sorted(total_stats.keys()):
            type_total = sum(total_stats[roulette_type].values())
            for item, quantity in sorted(total_stats[roulette_type].items(), key=lambda x: x[1], reverse=True):
                percentage = (quantity / type_total * 100) if type_total > 0 else 0
                data.append([roulette_type, item, quantity, f"{percentage:.1f}%"])
        
        self.show_table_gui(columns, data, f"Общая статистика рулеток (всего попыток: {total_attempts})", 
                           None, self.handle_roulette_menu_gui)

    def show_roulette_stats_by_day(self):
        days = sorted(self.roulette_stats.keys())
        if not days:
            messagebox.showinfo("Инфо", "Нет данных о выпадениях из рулеток")
            return
        
        columns = ["№", "Дата", "Попыток", "Предметов"]
        data = []
        
        for i, day in enumerate(days):
            day_attempts = 0
            day_items = 0
            for roulette_type, items in self.roulette_stats[day].items():
                day_attempts += sum(items.values())
                day_items += len(items)
            data.append([i+1, str(day), day_attempts, day_items])
        
        def on_select(index):
            day = days[index]
            self.show_roulette_day_details(day)
        
        self.show_table_gui(columns, data, "Статистика по дням", on_select, self.handle_roulette_menu_gui)

    def show_roulette_day_details(self, day):
        day_stats = self.roulette_stats[day]
        if not day_stats:
            messagebox.showinfo("Инфо", f"Нет данных за {day}")
            return
        
        total_attempts = 0
        columns = ["Тип рулетки", "Предмет", "Количество", "Процент"]
        data = []
        
        for roulette_type in sorted(day_stats.keys()):
            type_total = sum(day_stats[roulette_type].values())
            total_attempts += type_total
            for item, quantity in sorted(day_stats[roulette_type].items(), key=lambda x: x[1], reverse=True):
                percentage = (quantity / type_total * 100) if type_total > 0 else 0
                data.append([roulette_type, item, quantity, f"{percentage:.1f}%"])
        
        self.show_table_gui(columns, data, f"Статистика за {day} (попыток: {total_attempts})", 
                           None, self.show_roulette_stats_by_day)

    def show_roulette_stats_by_hour(self):
        days = sorted(self.roulette_stats.keys())
        if not days:
            messagebox.showinfo("Инфо", "Нет данных о выпадениях из рулеток")
            return
        
        self.clear_main_frame()
        self.push_navigation(self.handle_roulette_menu_gui)
        
        ttk.Label(self.main_frame, text="Выберите день для анализа по часам", font=('Arial', 12, 'bold')).pack(pady=10)
        
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(self.main_frame, textvariable=day_var, values=[str(day) for day in days], state="readonly")
        day_combo.pack(pady=10)
        
        def show_hourly_stats():
            selected_day = day_var.get()
            if not selected_day:
                messagebox.showwarning("Ошибка", "Выберите день")
                return
                
            hourly_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            day_logs = self.roulette_logs.get(selected_day, [])
            
            for log in day_logs:
                try:
                    log_time = parse_time_extended(log['time'])
                    if log_time:
                        hour = log_time.hour
                        hourly_stats[hour][log['type']][log['item']] += log['quantity']
                except:
                    continue
            
            if not hourly_stats:
                messagebox.showinfo("Инфо", f"Нет данных за {selected_day}")
                return
            
            columns = ["Час", "Тип рулетки", "Предмет", "Количество"]
            data = []
            
            for hour in sorted(hourly_stats.keys()):
                for roulette_type in sorted(hourly_stats[hour].keys()):
                    for item, quantity in sorted(hourly_stats[hour][roulette_type].items(), key=lambda x: x[1], reverse=True):
                        data.append([f"{hour:02d}:00", roulette_type, item, quantity])
            
            self.show_table_gui(columns, data, f"Статистика по часам за {selected_day}", 
                               None, self.show_roulette_stats_by_hour)
        
        ttk.Button(self.main_frame, text="Показать статистику", command=show_hourly_stats).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", command=self.handle_roulette_menu_gui).pack(pady=5)

    def show_az_calculator(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_roulette_menu_gui)
        
        ttk.Label(self.main_frame, text="ПОДСЧЕТ СТОИМОСТИ ЗА AZ", font=('Arial', 14, 'bold')).pack(pady=10)
        
        if not self.roulette_price_manager.current_config:
            ttk.Label(self.main_frame, text="⚠ Цены не загружены. Сначала настройте цены в разделе 'Настройка цен предметов'", 
                     foreground='red').pack(pady=10)
        
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10, fill='x')
        
        ttk.Label(input_frame, text="Тип рулетки:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        roulette_var = tk.StringVar(value="Платиновая")
        roulette_combo = ttk.Combobox(input_frame, textvariable=roulette_var, 
                                     values=["Платиновая", "Золотая", "Серебряная", "Бронзовая"], state="readonly")
        roulette_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(input_frame, text="Цена рулетки ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        price_entry = ttk.Entry(input_frame)
        price_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        price_entry.insert(0, "800000")
        
        ttk.Label(input_frame, text="Количество попыток:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        attempts_entry = ttk.Entry(input_frame)
        attempts_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        attempts_entry.insert(0, "100")
        
        input_frame.columnconfigure(1, weight=1)
        
        config_frame = ttk.Frame(self.main_frame)
        config_frame.pack(pady=10, fill='x')
        
        ttk.Button(config_frame, text="Импортировать конфиг", command=self.load_roulette_price_config).pack(side='left', padx=5)
        ttk.Button(config_frame, text="Сохранить конфиг", command=self.save_roulette_price_config).pack(side='left', padx=5)
        
        ttk.Button(self.main_frame, text="Рассчитать стоимость за AZ", 
                  command=lambda: self.calculate_az_price(roulette_var.get(), price_entry.get(), attempts_entry.get())).pack(pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self.main_frame, height=15, wrap='word')
        self.result_text.pack(pady=10, fill='both', expand=True)
        
        ttk.Button(self.main_frame, text="Назад", command=self.handle_roulette_menu_gui).pack(pady=5)

    def calculate_az_price(self, roulette_type, price_str, attempts_str):
        try:
            roulette_price = int(price_str.replace(",", ""))
            attempts = int(attempts_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные числовые значения")
            return
        
        if not self.roulette_price_manager.current_config:
            messagebox.showerror("Ошибка", "Сначала загрузите цены на предметы")
            return
        
        total_stats = defaultdict(int)
        total_attempts = 0
        
        for day_data in self.roulette_stats.values():
            if roulette_type in day_data:
                for item, quantity in day_data[roulette_type].items():
                    total_stats[item] += quantity
                    total_attempts += quantity
        
        if total_attempts == 0:
            messagebox.showinfo("Инфо", f"Нет данных для рулетки: {roulette_type}")
            return
        
        total_investment = attempts * roulette_price
        total_loot_value = 0
        az_count = 0
        
        results = []
        results.append(f"РАСЧЕТ СТОИМОСТИ ЗА AZ")
        results.append(f"Тип рулетки: {roulette_type}")
        results.append(f"Цена рулетки: ${roulette_price:,}")
        results.append(f"Количество попыток: {attempts}")
        results.append(f"Общие инвестиции: ${total_investment:,}")
        results.append("")
        results.append("ДЕТАЛИ РАСЧЕТА:")
        results.append("-" * 50)
        
        for item, quantity in sorted(total_stats.items(), key=lambda x: x[1], reverse=True):
            item_price = self.roulette_price_manager.get_price(item)
            probability = quantity / total_attempts
            expected_quantity = probability * attempts
            item_value = expected_quantity * item_price
            total_loot_value += item_value
            
            if "AZ" in item.upper():
                az_count += expected_quantity
            
            results.append(f"{item}: {expected_quantity:.1f} шт. × ${item_price:,} = ${item_value:,.0f} ({probability:.1%})")
        
        results.append("-" * 50)
        results.append(f"Общая стоимость лута: ${total_loot_value:,.0f}")
        results.append(f"Количество AZ: {az_count:.1f}")
        
        if az_count > 0:
            az_price = (total_investment - total_loot_value) / az_count
            results.append(f"Стоимость за AZ: ${az_price:,.0f}")
            results.append(f"Эффективность: {total_loot_value/total_investment*100:.1f}%")
        else:
            results.append("AZ не выпадали")
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "\n".join(results))

    def show_roulette_charts_menu(self):
        self.clear_main_frame()
        self.push_navigation(self.handle_roulette_menu_gui)
        
        ttk.Label(self.main_frame, text="ГРАФИКИ ВЫПАДЕНИЙ ИЗ РУЛЕТОК", font=('Arial', 14, 'bold')).pack(pady=10)
        
        buttons = [
            ("1. Распределение по типам рулеток", self.show_roulette_type_chart),
            ("2. Топ предметов по выпадениям", self.show_roulette_top_items_chart),
            ("3. Динамика по дням", self.show_roulette_daily_chart),
            ("4. Динамика по часам", self.show_roulette_hourly_chart),
            ("5. Назад", self.handle_roulette_menu_gui)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(self.main_frame, text=text, command=command, width=30)
            btn.pack(pady=5)

    def show_roulette_type_chart(self):
        type_totals = defaultdict(int)
        for day_data in self.roulette_stats.values():
            for roulette_type, items in day_data.items():
                type_totals[roulette_type] += sum(items.values())
        
        if not type_totals:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return
        
        types = list(type_totals.keys())
        counts = list(type_totals.values())
        
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.bar(types, counts, color=['gold', 'silver', 'peru', 'sandybrown'])
        
        ax.set_title('Распределение выпадений по типам рулеток', fontsize=14, fontweight='bold')
        ax.set_ylabel('Количество выпадений')
        
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   str(count), ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        def on_click(event):
            if event.inaxes == ax:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        self.show_roulette_type_details(types[i])
                        break
        
        self.show_graph_gui(fig, "Распределение по типам рулеток", 
                           self.show_roulette_charts_menu, on_click)

    def show_roulette_type_details(self, roulette_type):
        type_items = defaultdict(int)
        for day_data in self.roulette_stats.values():
            if roulette_type in day_data:
                for item, quantity in day_data[roulette_type].items():
                    type_items[item] += quantity
        
        top_items = dict(sorted(type_items.items(), key=lambda x: x[1], reverse=True)[:10])
        
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(list(top_items.keys()), list(top_items.values()), color='lightblue')
        
        ax.set_title(f'Топ предметов из {roulette_type} рулетки', fontsize=14, fontweight='bold')
        ax.set_xlabel('Количество выпадений')
        
        plt.tight_layout()
        self.show_graph_gui(fig, f"Топ предметов - {roulette_type}", self.show_roulette_charts_menu)

    def show_roulette_top_items_chart(self):
        all_items = defaultdict(int)
        for day_data in self.roulette_stats.values():
            for roulette_type, items in day_data.items():
                for item, quantity in items.items():
                    all_items[item] += quantity
        
        if not all_items:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return
        
        top_items = dict(sorted(all_items.items(), key=lambda x: x[1], reverse=True)[:15])
        
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(list(top_items.keys()), list(top_items.values()), color='lightgreen')
        
        ax.set_title('Топ предметов по выпадениям из всех рулеток', fontsize=14, fontweight='bold')
        ax.set_xlabel('Количество выпадений')
        
        plt.tight_layout()
        self.show_graph_gui(fig, "Топ предметов по выпадениям", self.show_roulette_charts_menu)

    def show_roulette_daily_chart(self):
        daily_totals = defaultdict(int)
        for day, day_data in self.roulette_stats.items():
            for roulette_type, items in day_data.items():
                daily_totals[day] += sum(items.values())
        
        if not daily_totals:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return
        
        days = sorted(daily_totals.keys())
        counts = [daily_totals[day] for day in days]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(days, counts, marker='o', linewidth=2, markersize=6, color='blue')
        
        ax.set_title('Динамика выпадений из рулеток по дням', fontsize=14, fontweight='bold')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Количество выпадений')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self.show_graph_gui(fig, "Динамика по дням", self.show_roulette_charts_menu)

    def show_roulette_hourly_chart(self):
        days = sorted(self.roulette_stats.keys())
        if not days:
            messagebox.showinfo("Инфо", "Нет данных для построения графика")
            return
        
        self.clear_main_frame()
        self.push_navigation(self.show_roulette_charts_menu)
        
        ttk.Label(self.main_frame, text="Выберите день для анализа по часам", font=('Arial', 12, 'bold')).pack(pady=10)
        
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(self.main_frame, textvariable=day_var, values=[str(day) for day in days], state="readonly")
        day_combo.pack(pady=10)
        
        def show_chart():
            selected_day = day_var.get()
            if not selected_day:
                messagebox.showwarning("Ошибка", "Выберите день")
                return
                
            hourly_totals = defaultdict(int)
            day_logs = self.roulette_logs.get(selected_day, [])
            
            for log in day_logs:
                try:
                    log_time = parse_time_extended(log['time'])
                    if log_time:
                        hour = log_time.hour
                        hourly_totals[hour] += log['quantity']
                except:
                    continue
            
            if not hourly_totals:
                messagebox.showinfo("Инфо", f"Нет данных за {selected_day}")
                return
            
            hours = sorted(hourly_totals.keys())
            counts = [hourly_totals[hour] for hour in hours]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.bar([f"{hour:02d}:00" for hour in hours], counts, color='lightcoral', alpha=0.7)
            
            ax.set_title(f'Выпадения из рулеток по часам за {selected_day}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Час')
            ax.set_ylabel('Количество выпадений')
            ax.grid(axis='y', alpha=0.3)
            
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                       str(count), ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            self.show_graph_gui(fig, f"Динамика по часам за {selected_day}", self.show_roulette_charts_menu)
        
        ttk.Button(self.main_frame, text="Показать график", command=show_chart).pack(pady=10)
        ttk.Button(self.main_frame, text="Назад", command=self.show_roulette_charts_menu).pack(pady=5)

# ЗАПУСК ПРОГРАММЫ
def setup_plot_font():
    try:
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
    except:
        plt.rcParams['font.family'] = 'sans-serif'

if __name__ == "__main__":
    setup_plot_font()
    app = LogAnalyzerApp()
    app.mainloop()