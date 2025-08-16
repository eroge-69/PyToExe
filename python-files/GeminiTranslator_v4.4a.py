# -*- coding: utf-8 -*-

import sys
import os
import glob
import argparse
import traceback
import time
import math
import re
import json
import zipfile
import subprocess
import uuid
import threading # <<< НОВИНКА: для ApiKeyManager
import shutil # <<< НОВИНКА: для TranslatedChaptersManagerDialog
import requests
from functools import partial
from xml.etree import ElementTree as ET # <<< НОВИНКА: для EpubCreator

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QDialogButtonBox, QLabel,
    QTextEdit, QFileDialog, QDoubleSpinBox, QListWidgetItem, QCheckBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout # <<< НОВИНКА: для нового диалога
)

from google.api_core import exceptions as google_exceptions
from google import generativeai as genai
import google.generativeai.types as genai_types
from concurrent.futures import (
    ThreadPoolExecutor, as_completed, Future, CancelledError
)

# --- Try importing optional libraries ---

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print(
        "WARNING: beautifulsoup4 library not found. EPUB/HTML processing will be disabled."
    )
    print("Install it using: pip install beautifulsoup4")
# ------------------------------------


# --- Конфигурация ---
MODELS = {
    "Gemini 2.0 Flash": {
        "id": "models/gemini-2.0-flash",
        "rpm": 15,  # As per user request, for concurrency suggestion
        "needs_chunking": True,
        "post_request_delay": 60,
    },
    "Gemini 2.5 Flash Preview": {
        "id": "models/gemini-2.5-flash",
        "rpm": 10,
        "needs_chunking": True,
        "post_request_delay": 60,
    },
    "Gemini 2.5 Flash-Lite": {
        "id": "models/gemini-2.5-flash-lite-preview-06-17",
        "rpm": 10,
        "needs_chunking": True,
        "post_request_delay": 60,
    },
    "Gemini 2.5 Pro": {
        "id": "models/gemini-2.5-pro",
        "rpm": 5,
        "needs_chunking": True,
        "post_request_delay": 60,
    },
}

# Конфигурация моделей OpenRouter
OPENROUTER_MODELS = {
    "DeepSeek V3 Chat (бесплатно)": {
        "id": "deepseek/deepseek-chat-v3-0324:free",
        "rpm": 20,  # Фиксированный RPM для OpenRouter
        "rpd": 50,  # Requests Per Day
        "needs_chunking": True,
        "post_request_delay": 3,  # Меньше задержка чем у Gemini
        "provider": "openrouter"
    },
    "Dolphin Mistral 24B Venice (бесплатно)": {
        "id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "rpm": 20,
        "rpd": 50,
        "needs_chunking": True,
        "post_request_delay": 3,
        "provider": "openrouter"
    },
    "GLM-4.5 Air (бесплатно)": {
        "id": "z-ai/glm-4.5-air:free",
        "rpm": 20,
        "rpd": 50,
        "needs_chunking": True,
        "post_request_delay": 3,
        "provider": "openrouter"
    },
    "Qwen 2.5 72B (бесплатно)": {
        "id": "qwen/qwen-2.5-72b-instruct:free",
        "rpm": 20,
        "rpd": 50,
        "needs_chunking": True,
        "post_request_delay": 3,
        "provider": "openrouter"
    },
    "Llama 3.1 8B (бесплатно)": {
        "id": "meta-llama/llama-3.1-8b-instruct:free",
        "rpm": 20,
        "rpd": 50,
        "needs_chunking": True,
        "post_request_delay": 3,
        "provider": "openrouter"
    },
    "Gemma 2 9B (бесплатно)": {
        "id": "google/gemma-2-9b-it:free",
        "rpm": 20,
        "rpd": 50,
        "needs_chunking": True,
        "post_request_delay": 3,
        "provider": "openrouter"
    }
}

# Объединенный словарь всех моделей
ALL_MODELS = {**MODELS, **OPENROUTER_MODELS}

DEFAULT_MODEL_NAME = (
    "Gemini 2.5 Flash Preview"
    if "Gemini 2.5 Flash Preview" in MODELS
    else list(MODELS.keys())[0]
)

MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 25
RATE_LIMIT_DELAY_SECONDS = 60
API_TIMEOUT_SECONDS = 600

CHARACTER_LIMIT_FOR_CHUNK = 900_000
CHUNK_SEARCH_WINDOW = 500
CHUNK_TARGET_SIZE = CHARACTER_LIMIT_FOR_CHUNK - 5000
MIN_CHUNK_SIZE = 500
CHUNK_HTML_SOURCE = True
# ---------------------


# --- Вспомогательные функции ---
def format_size(size_bytes):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
    i = min(i, len(size_name) - 1)  # Ensure index is valid
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def split_text_into_chunks(text, target_size, search_window, min_chunk_size):
    """Splits text into chunks, respecting paragraphs and sentences where possible."""
    chunks = []
    start_index = 0
    text_len = len(text)
    while start_index < text_len:
        if text_len - start_index <= target_size + search_window:
            chunks.append(text[start_index:])
            break

        end_index = min(start_index + target_size, text_len)
        split_index = -1
        search_start = max(start_index + min_chunk_size, end_index - search_window)

        best_split = text.rfind("\n\n", search_start, end_index)
        if best_split != -1:
            split_index = best_split + 2
        else:
            sentence_ends = list(re.finditer(r"[.!?]\s+", text[search_start:end_index]))
            if sentence_ends:
                split_index = search_start + sentence_ends[-1].end()
            else:
                best_split = text.rfind("\n", search_start, end_index)
                if best_split != -1:
                    split_index = best_split + 1
                else:
                    best_split = text.rfind(" ", search_start, end_index)
                    if best_split != -1:
                        split_index = best_split + 1

        if split_index == -1 or split_index <= start_index + min_chunk_size:
            split_index = end_index
        chunks.append(text[start_index:split_index])
        start_index = split_index
    return [chunk for chunk in chunks if chunk.strip()]

def extract_number_from_path(path):
    filename = os.path.basename(path)
    match = re.search(
        r"(?:chapter|part|section|page|item|file|ch|pt|pg|_)(\d+)",
        filename,
        re.IGNORECASE,
    )
    if not match:
        match = re.search(r"(\d+)", filename)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            return float("inf")
    return float("inf")

class ApiKeyManager:
    """Управляет пулом API ключей с отслеживанием использования и ротацией."""
    def __init__(self, api_keys):
        if not api_keys:
            raise ValueError("Список API ключей не может быть пустым.")
        self.api_keys = list(set(api_keys))  # Убираем дубликаты
        self.current_index = 0
        self.usage_counts = {key: 0 for key in self.api_keys}
        self.usage_limits = {key: 1000 for key in self.api_keys}
        self.exhausted_keys = set()  # Ключи с исчерпанной квотой
        self.lock = threading.Lock()

    def get_next_available_key(self):
        """Возвращает следующий доступный ключ с учетом лимитов."""
        with self.lock:
            # Пробуем найти рабочий ключ
            attempts = 0
            while attempts < len(self.api_keys):
                key = self.api_keys[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.api_keys)
                attempts += 1
                
                # Пропускаем исчерпанные ключи
                if key in self.exhausted_keys:
                    continue
                    
                if self.usage_counts[key] < self.usage_limits[key]:
                    self.usage_counts[key] += 1
                    return key
                    
            # Все ключи исчерпаны или достигли лимита
            return None
            
    def mark_key_exhausted(self, key):
        """Помечает ключ как исчерпанный"""
        with self.lock:
            if key in self.api_keys:
                self.exhausted_keys.add(key)
                print(f"[API KEY] Ключ ...{key[-4:]} помечен как исчерпанный")
                
    def has_available_keys(self):
        """Проверяет, есть ли доступные ключи"""
        with self.lock:
            return len(self.exhausted_keys) < len(self.api_keys)

    def reset_usage(self):
        """Сбрасывает счетчики использования."""
        with self.lock:
            for key in self.api_keys:
                self.usage_counts[key] = 0
            # НЕ сбрасываем exhausted_keys - они остаются исчерпанными

    def get_usage_report(self):
        """Возвращает отчет об использовании ключей."""
        with self.lock:
            reports = []
            for key in self.api_keys:
                key_short = f"...{key[-4:]}"
                status = "ИСЧЕРПАН" if key in self.exhausted_keys else f"{self.usage_counts[key]}/{self.usage_limits[key]}"
                reports.append(f"{key_short}: {status}")
            return ", ".join(reports)

class RateLimitTracker:
    """Отслеживает лимиты API на основе заголовков ответа"""
    def __init__(self):
        self.limits = {}  # {api_key: {'limit': X, 'remaining': Y, 'reset': Z}}
        self.lock = threading.Lock()
        
    def update_from_headers(self, api_key, headers):
        """Обновляет информацию о лимитах из заголовков ответа"""
        with self.lock:
            if api_key not in self.limits:
                self.limits[api_key] = {}
                
            # Пробуем разные варианты названий заголовков
            rate_limit_headers = {
                'limit': ['x-ratelimit-limit', 'ratelimit-limit', 'x-rate-limit-limit'],
                'remaining': ['x-ratelimit-remaining', 'ratelimit-remaining', 'x-rate-limit-remaining'],
                'reset': ['x-ratelimit-reset', 'ratelimit-reset', 'x-rate-limit-reset']
            }
            
            for key, possible_names in rate_limit_headers.items():
                for header_name in possible_names:
                    if header_name in headers:
                        try:
                            if key == 'reset':
                                self.limits[api_key][key] = int(headers[header_name])
                            else:
                                self.limits[api_key][key] = int(headers[header_name])
                        except (ValueError, TypeError):
                            pass
                        break
                        
    def get_remaining_requests(self, api_key):
        """Возвращает количество оставшихся запросов"""
        with self.lock:
            return self.limits.get(api_key, {}).get('remaining', None)
            
    def should_wait(self, api_key, threshold=2):
        """Определяет, нужно ли ждать перед следующим запросом"""
        remaining = self.get_remaining_requests(api_key)
        if remaining is not None and remaining <= threshold:
            reset_time = self.limits.get(api_key, {}).get('reset', 0)
            if reset_time:
                wait_time = max(0, reset_time - time.time())
                return True, wait_time
        return False, 0
        
    def get_status(self, api_key):
        """Возвращает строку со статусом лимитов"""
        with self.lock:
            if api_key not in self.limits:
                return "Нет данных о лимитах"
            
            info = self.limits[api_key]
            if 'remaining' in info and 'limit' in info:
                return f"{info['remaining']}/{info['limit']} запросов осталось"
            return "Частичные данные о лимитах"

class InitialSetupDialog(QDialog):
    """Начальный диалог для ввода всех настроек перед запуском переводчика с автоматической ротацией"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка переводчика с автоматической ротацией")
        self.setMinimumSize(700, 800)  # Увеличиваем высоту
        self.selected_file = None
        self.selected_html_files = []  # Добавляем список выбранных глав
        self.output_folder = None
        self.api_keys = []
        self.glossary_dict = {}
        self.selected_model = DEFAULT_MODEL_NAME
        self.concurrent_requests = 10
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
    
        # Информация о режиме
        info_label = QLabel(
            "🔄 Режим автоматической ротации ключей\n"
            "При достижении лимита программа автоматически переключится на следующий ключ"
        )
        info_label.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
    
        # 1. Выбор файла для перевода
        file_group = QGroupBox("1. Файл для перевода")
        file_layout = QVBoxLayout(file_group)
        file_btn_layout = QtWidgets.QHBoxLayout()
        self.file_btn = QPushButton("Выбрать файл...")
        self.file_btn.clicked.connect(self.select_file)
        self.file_label = QLabel("Файл не выбран")
        file_btn_layout.addWidget(self.file_btn)
        file_btn_layout.addWidget(self.file_label, 1)
        file_layout.addLayout(file_btn_layout)
        layout.addWidget(file_group)
    
        # 2. Путь сохранения
        output_group = QGroupBox("2. Папка для сохранения перевода")
        output_layout = QVBoxLayout(output_group)
        output_btn_layout = QtWidgets.QHBoxLayout()
        self.output_btn = QPushButton("Выбрать папку...")
        self.output_btn.clicked.connect(self.select_output_folder)
        self.output_label = QLabel("Папка не выбрана")
        output_btn_layout.addWidget(self.output_btn)
        output_btn_layout.addWidget(self.output_label, 1)
        output_layout.addLayout(output_btn_layout)
        layout.addWidget(output_group)
    
        # 3. API ключи
        keys_group = QGroupBox("3. API ключи Gemini")
        keys_layout = QVBoxLayout(keys_group)
        keys_layout.addWidget(QLabel("Введите ключи (по одному на строку):"))
        self.keys_edit = QTextEdit()
        self.keys_edit.setMaximumHeight(100)
        self.keys_edit.setPlaceholderText("Ключ1\nКлюч2\nКлюч3...")
        self.keys_edit.textChanged.connect(self.update_keys_count)
        keys_layout.addWidget(self.keys_edit)
    
        # Счетчик ключей
        self.keys_count_label = QLabel("Ключей: 0")
        self.keys_count_label.setStyleSheet("color: blue; font-size: 10px;")
        keys_layout.addWidget(self.keys_count_label)
    
        keys_btn_layout = QtWidgets.QHBoxLayout()
        load_keys_btn = QPushButton("📁 Загрузить из файла")
        load_keys_btn.clicked.connect(self.load_keys_from_file)
        keys_btn_layout.addWidget(load_keys_btn)
        keys_btn_layout.addStretch()
        keys_layout.addLayout(keys_btn_layout)
        layout.addWidget(keys_group)
    
        # 4. Глоссарий (с поддержкой JSON)
        glossary_group = QGroupBox("4. Глоссарий (опционально)")
        glossary_layout = QVBoxLayout(glossary_group)
    
        # Инструкция
        glossary_info = QLabel(
            "Введите термины в формате:\n"
            "• Обычный: Оригинал = Перевод\n"
            "• JSON: {\"term\": \"перевод\", ...}"
        )
        glossary_info.setStyleSheet("color: #666; font-size: 10px;")
        glossary_layout.addWidget(glossary_info)
    
        # Текстовое поле для глоссария
        self.glossary_text_edit = QtWidgets.QPlainTextEdit()
        self.glossary_text_edit.setMaximumHeight(120)
        self.glossary_text_edit.setPlaceholderText(
            "Son Goku = Сон Гоку\n"
            "Kamehameha = Камехамеха\n"
            "ИЛИ JSON:\n"
            '{\"Lin An\": \"Линь Ань\", \"Makima\": \"Макима\"}'
        )
        self.glossary_text_edit.setFont(QtGui.QFont("Consolas", 9))
        self.glossary_text_edit.textChanged.connect(self.update_glossary_count)
        glossary_layout.addWidget(self.glossary_text_edit)
    
        # Счетчик терминов
        self.glossary_count_label = QLabel("Терминов: 0")
        self.glossary_count_label.setStyleSheet("color: blue; font-size: 10px;")
        glossary_layout.addWidget(self.glossary_count_label)
    
        # Кнопки для работы с глоссарием
        glossary_buttons_layout = QtWidgets.QHBoxLayout()
    
        load_glossary_btn = QPushButton("📁 Загрузить")
        load_glossary_btn.clicked.connect(self.load_glossary_from_file)
        load_glossary_btn.setToolTip("Загрузить глоссарий из файла (JSON или TXT)")
        glossary_buttons_layout.addWidget(load_glossary_btn)
    
        save_glossary_btn = QPushButton("💾 Сохранить")
        save_glossary_btn.clicked.connect(self.save_glossary_to_file)
        save_glossary_btn.setToolTip("Сохранить текущий глоссарий в файл")
        glossary_buttons_layout.addWidget(save_glossary_btn)
    
        clear_glossary_btn = QPushButton("🗑️ Очистить")
        clear_glossary_btn.clicked.connect(lambda: self.glossary_text_edit.clear())
        clear_glossary_btn.setToolTip("Очистить глоссарий")
        glossary_buttons_layout.addWidget(clear_glossary_btn)
    
        # Предустановленные глоссарии
        preset_combo = QtWidgets.QComboBox()
        preset_combo.addItems([
            "Выбрать пресет...",
            "Аниме/Манга",
            "Китайские новеллы", 
            "Корейские новеллы",
            "Фэнтези",
            "Научная фантастика"
        ])
        preset_combo.currentTextChanged.connect(self.load_preset_glossary)
        glossary_buttons_layout.addWidget(preset_combo)
    
        glossary_buttons_layout.addStretch()
        glossary_layout.addLayout(glossary_buttons_layout)
    
        layout.addWidget(glossary_group)
    
        # Опции глоссария
        glossary_options_layout = QtWidgets.QHBoxLayout()

        self.dynamic_glossary_checkbox = QCheckBox("Динамический глоссарий")
        self.dynamic_glossary_checkbox.setToolTip(
            "Автоматически фильтрует глоссарий для каждой главы,\n"
            "оставляя только релевантные термины"
        )
        self.dynamic_glossary_checkbox.setChecked(True)
        glossary_options_layout.addWidget(self.dynamic_glossary_checkbox)

        glossary_options_layout.addStretch()
        glossary_layout.addLayout(glossary_options_layout)
    
        # 5. Модель и потоки
        model_group = QGroupBox("5. Настройки модели")
        model_layout = QFormLayout(model_group)
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(MODELS.keys())
        self.model_combo.setCurrentText(self.selected_model)
        self.concurrency_spin = QtWidgets.QSpinBox()
        self.concurrency_spin.setMinimum(1)
        self.concurrency_spin.setMaximum(100)
        self.concurrency_spin.setValue(self.concurrent_requests)
        # Обновляем значение при смене модели
        self.model_combo.currentTextChanged.connect(self.update_concurrency_for_model)
        model_layout.addRow("Модель:", self.model_combo)
        model_layout.addRow("Параллельные запросы:", self.concurrency_spin)
        layout.addWidget(model_group)
    
        # 1.5 Выбор провайдера API
        provider_group = QGroupBox("1.5. Выбор сервиса перевода")
        provider_layout = QVBoxLayout(provider_group)

        self.provider_combo = QtWidgets.QComboBox()
        self.provider_combo.addItems(["Google Gemini", "OpenRouter (бесплатные модели)"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)

        self.provider_info = QLabel(
            "Google Gemini - быстрый и качественный перевод\n"
            "Требуются API ключи Google"
        )
        self.provider_info.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        provider_layout.addWidget(self.provider_info)

        layout.addWidget(provider_group)

        # Скрываем/показываем поля в зависимости от провайдера
        self.on_provider_changed("Google Gemini")
    
        # 6. Кастомный промпт (НОВОЕ!)
        prompt_group = QGroupBox("6. Промпт (опционально)")
        prompt_layout = QVBoxLayout(prompt_group)
        prompt_layout.addWidget(QLabel("Оставьте пустым для стандартного промпта:"))
        self.custom_prompt_edit = QtWidgets.QPlainTextEdit()
        self.custom_prompt_edit.setMaximumHeight(150)
        self.custom_prompt_edit.setPlaceholderText(
            "Введите свой промпт с плейсхолдером {text}\n"
            "Пример: Переведи на русский язык: {text}"
        )
        prompt_layout.addWidget(self.custom_prompt_edit)
    
        # Кнопка загрузки стандартного промпта
        load_default_btn = QPushButton("📋 Загрузить стандартный промпт")
        load_default_btn.clicked.connect(self.load_default_prompt)
        prompt_layout.addWidget(load_default_btn)
    
        layout.addWidget(prompt_group)
    
        # Кнопки
        button_box = QDialogButtonBox()
        self.start_btn = QPushButton("🚀 Старт")
        self.start_btn.clicked.connect(self.validate_and_start)
        button_box.addButton(self.start_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_provider_changed(self, provider):
        """Обработчик изменения провайдера"""
        if provider == "OpenRouter (бесплатные модели)":
            # Для OpenRouter
            self.provider_info.setText(
                "OpenRouter - бесплатные модели AI\n"
                "RPM: 20 запросов/мин, RPD: 50 запросов/день\n"
                "Требуется один API ключ OpenRouter"
            )
        
            # Обновляем список моделей
            self.model_combo.clear()
            self.model_combo.addItems(OPENROUTER_MODELS.keys())
        
            # Обновляем подсказку для ключей
            self.keys_edit.setPlaceholderText("sk-or-v1-...")
        
            # Устанавливаем параметры для OpenRouter
            self.concurrency_spin.setValue(20)  # RPM 20
            self.concurrency_spin.setEnabled(False)  # Фиксированное значение
        
        else:
            # Для Gemini
            self.provider_info.setText(
                "Google Gemini - быстрый и качественный перевод\n"
                "Требуются API ключи Google"
            )
        
            # Обновляем список моделей
            self.model_combo.clear()
            self.model_combo.addItems(MODELS.keys())
        
            # Обновляем подсказку для ключей
            self.keys_edit.setPlaceholderText("Ключ1\nКлюч2\nКлюч3...")
        
            # Восстанавливаем настройки для Gemini
            self.concurrency_spin.setEnabled(True)
            default_model = self.model_combo.currentText()
            if default_model in MODELS:
                self.concurrency_spin.setValue(MODELS[default_model].get("rpm", 10))

    def update_concurrency_for_model(self, model_name):
        """Обновляет количество параллельных запросов при смене модели"""
        if model_name in MODELS:
            rpm = MODELS[model_name].get("rpm", 10)
            self.concurrency_spin.setValue(rpm)
            self.concurrent_requests = rpm

    def load_default_prompt(self):
        """Загружает улучшенный стандартный промпт с правилами диалогов"""
        default_prompt = """--- PROMPT START ---

**I. КОНТЕКСТ И ЗАДАЧА**

**Ваша Роль:** Вы — элитный переводчик и редактор, **мастер художественной адаптации**, специализирующийся на **литературном переводе содержимого EPUB-книг** (веб-новелл, ранобэ, романов и т.д.) с языка оригинала на русский язык. Вы обладаете глубоким пониманием языка оригинала, **его культурных кодов**, речевых оборотов, **литературных приемов, а также** технических аспектов форматирования XHTML. **Ваша цель – создать текст, который читается так, будто изначально был написан на русском языке для русскоязычного читателя, полностью заменяя оригинал и сохраняя при этом всю его суть, дух и уникальность.**

**Ваша Задача:** Перед вами фрагмент оригинального текста из файла EPUB (предоставленный как `{text}` в формате XHTML/HTML). Ваша цель — выполнить **высококлассную, глубокую литературную адаптацию** на русский язык, **виртуозно** сохраняя смысл, стиль, **эмоциональный накал, динамику повествования** и исходное XHTML-форматирование. **Критически важно, чтобы в итоговом результате НЕ ОСТАЛОСЬ НИ ОДНОГО СЛОВА или ФРАГМЕНТА текста на языке оригинала (за исключением неизменяемых частей XHTML, указанных ниже).**

**II. ОБЩИЕ ПРИНЦИПЫ АДАПТАЦИИ**

1.  **Естественность и Художественность Русского Языка:** Перевод должен звучать абсолютно органично и **литературно** по-русски. Избегайте буквального следования грамматике или идиомам оригинала, если они создают неестественные или косноязычные конструкции. Находите эквивалентные русские выражения, **идиомы и речевые обороты, которые точно передают замысел автора.** **Стремитесь к богатству, образности и выразительности русского языка.**
2.  **Сохранение Смысла, Тона и Атмосферы:** Точно передавайте основной смысл, атмосферу (юмор, саспенс, драму, романтику и т.д.) и авторский стиль оригинала. **Уделяйте особое внимание передаче эмоций персонажей, их внутренних переживаний, мотиваций и характера через их речь и мысли.**
3.  **Культурная и Стилистическая Адаптация:**
    *   **Хонорифики (-сан, -кун, -ним, гэгэ, шисюн, сэмпай и т.д.):** Как правило, **опускайте** или заменяйте естественными русскими формами обращения (по имени, "господин/госпожа", "братец/сестрица", "учитель", "старший" – в зависимости от контекста и отношений между персонажами).
    *   **Реалии:** Адаптируйте непонятные для русского читателя культурные или бытовые реалии: найдите русский эквивалент, дайте краткое, **органично вплетенное в повествование пояснение** (например, "он достал цзянь – прямой китайский меч"), или замените на близкую по смыслу понятную деталь. *Избегайте сносок и комментариев переводчика в тексте.*
    *   **Ономатопея (звукоподражания):** Заменяйте русскими звукоподражаниями или **яркими, образными описаниями звука/действия** (например, вместо "бах" можно написать "раздался глухой удар").
    *   **Имена собственные и Названия:** При отсутствии глоссария, стремитесь к благозвучной и понятной адаптации. Если возможен осмысленный перевод названия (например, техники или артефакта), отдавайте ему предпочтение перед транслитерацией. **Избегайте нагромождения труднопроизносимых транслитераций.**
    *   **Стилистика речи персонажей:** Если оригинал предполагает различия в манере речи разных персонажей (просторечия, высокий стиль, архаизмы, жаргон, детская речь), **старайтесь передать эти различия средствами русского языка.**

**III. ТЕХНИЧЕСКИЕ И СТИЛИСТИЧЕСКИЕ ТРЕБОВАНИЯ**

**1. Работа с XHTML/HTML-структурой EPUB:**
*   **ВАШ ГЛАВНЫЙ ПРИОРИТЕТ — ПОЛНОЕ СОХРАНЕНИЕ ИСХОДНОЙ XHTML/HTML-СТРУКТУРЫ.** Помните, что EPUB-книга состоит из XHTML-файлов. Ваша задача — работать с кодом этих файлов, переводя только текстовое наполнение.
*   **СОХРАНЯЙТЕ ВСЕ HTML-ТЕГИ!** Переводите **ТОЛЬКО видимый пользователю текст** внутри тегов (например, текст внутри `<p>`, `<h1>`, `<li>`, `<td>`, `<span>`, `<a>` и т.д., а также значения атрибутов `title` и `alt`, если они содержат осмысленный текст).
*   **НЕ МЕНЯЙТЕ, НЕ УДАЛЯЙТЕ и НЕ ДОБАВЛЯЙТЕ** никакие HTML-теги (`<p>`, `<div>`, `<img>`, `<a>` и т.д.), атрибуты (`class`, `id`, `href`, `src` и т.д.) или структуру документа.
*   **Комментарии HTML (`<!-- ... -->`), скрипты (`<script>...</script>`) и стили (`<style>...</style>`) должны оставаться БЕЗ ИЗМЕНЕНИЙ.** Содержимое этих тегов **НЕ ПЕРЕВОДИТСЯ**.
*   **Цель:** Выходной код должен быть валидным XHTML/HTML с той же структурой и тегами, что и входной, но с **полностью переведенным текстовым содержимым** (кроме указанных исключений).

**2. Стилистические Требования к Тексту (Правила Адаптации):**
*   **2.1. (Оформление прямой речи и цитат):**
    *   Квадратные скобки `[]`, обозначающие **прямую речь персонажей**, заменяйте на стандартное оформление прямой речи в русском языке с помощью тире: `— Реплика.`
    *   Конструкции вида `『Цитата/Реплика』` или `「Цитата/Реплика」` заменяйте на русские кавычки-«ёлочки» (`«Цитата/Реплика»`), если это выделенная мысль, название, цитата. Если это полноценная прямая речь, оформляйте её с тире: `— Реплика.`
*   **2.2. (Оформление мыслей):** Все **мысли героев** оформляйте русскими кавычками-«ёлочками»: `«Мысль персонажа.»`
*   **2.3. (Плавность и читаемость):** Уделите особое внимание **плавности и ритму текста**. Он должен читаться естественно и увлекательно. При необходимости, делите слишком длинные предложения на более короткие для лучшей читаемости, не теряя связи и смысла.
*   **2.4. (Передача протяжных звуков/заикания):** Для передачи протяжных звуков или заикания ограничивайтесь **тремя-четырьмя повторениями буквы**, разделенными дефисом: `А-а-ах...`, `Н-н-нет...`.
*   **2.5. (Знаки препинания в конце фразы):** Если фраза оканчивается на `...!` или `...?`, **сохраняйте этот порядок**. Для сочетания вопросительного и восклицательного знаков используйте `?!` или `!?`.
*   **2.6. (Оформление мыслей без тире):** Мысли в кавычках должны быть самостоятельными конструкциями. Не ставьте перед ними тире, как перед прямой речью.
    *   Корректно: `Он подумал: «Это интересно».` или `«Это интересно», — мелькнуло у него в голове.`
    *   Некорректно: `— «Мысль...»`
*   **2.7. (Количество знаков препинания):** Чрезмерное количество одинаковых знаков (`!!!!`, `????`) заменяйте **одним, двумя (`!!`, `??`) или сочетанием `?!` / `!?`**.
*   **2.8. (Передача заикания/раздельного произношения):** Сохраняйте разделение букв дефисом для передачи заикания или протяжного произнесения: `П-п-привет...`, `Чт-т-то-о?!`

    1. **КАЖДАЯ РЕПЛИКА ДИАЛОГА НАЧИНАЕТСЯ С НОВОЙ СТРОКИ (НОВОГО АБЗАЦА)**
    2. **Правильное оформление диалогов:**
       - Простая реплика: `— Текст реплики.`
       - Реплика с авторской ремаркой ПОСЛЕ: `— Текст реплики, — сказал персонаж.`
       - Реплика с авторской ремаркой ДО: `Персонаж сказал:` (новая строка) `— Текст реплики.`
       - НЕ разрывайте реплику и её авторскую ремарку на разные абзацы!

    3. **ЗАПРЕЩЕНО:**
       ❌ Неправильно:
       ```
       — Реплика.
   
       — Следующая реплика.
   
       сказал он.
       ```
   
       ✅ Правильно:
       ```
       — Реплика.
   
       — Следующая реплика, — сказал он.
       ```

    4. **Мысли персонажей:** оформляйте в кавычках-«ёлочках»: «Мысль персонажа»

**3. ОБЯЗАТЕЛЬНО ОФОРМЛЯТЬ НАЗВАНИЯ ГЛАВ В ВИДЕ: Глава X. Название главы**
Если ЕСТЬ глава, но нет названия, то просто: Глава X
А если нет главы, но есть название, то просто название надо с переводом

**IV. ГЛОССАРИЙ (Если применимо)**

*   Если предоставлен глоссарий имен, терминов, названий техник и т.д. — **строго придерживайтесь его**. Последовательность и единообразие критичны.

**V. ИТОГОВЫЙ РЕЗУЛЬТАТ**

*   Предоставьте **ИСКЛЮЧИТЕЛЬНО переведенный и адаптированный XHTML/HTML-код.**
*   **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО включать в вывод оригинальный текст или любые его фрагменты.**
*   **НЕ добавляйте никаких вводных фраз** типа "Вот перевод:", "Адаптация:", **а также никаких заключительных фраз или комментариев** (кроме неизмененных комментариев HTML).

**VI. ФИНАЛЬНАЯ ПРОВЕРКА (Мысленно перед выводом):**
*   Текст внутри HTML-кода звучит **естественно, художественно и увлекательно** по-русски?
*   Смысл, тон, **эмоции и атмосфера** оригинала переданы точно?
*   **XHTML-теги и структура документа** сохранены в точности?
*   Только видимый пользователю текст переведен, а теги, атрибуты, скрипты, стили и комментарии не тронуты?
*   **Все стилистические и культурные требования (разделы II и III.2) учтены?**
*   В итоговом коде **ПОЛНОСТЬЮ ОТСУТСТВУЕТ текст на языке оригинала** (за исключением разрешенных неизменяемых элементов)? **ПРОВЕРЕНО?**

--- PROMPT END ---"""
    
        self.custom_prompt_edit.setPlainText(default_prompt)
        QtWidgets.QMessageBox.information(
            self,
            "Промпт загружен",
            "Загружен улучшенный стандартный промпт с правилами форматирования диалогов"
        )
        
    def update_keys_count(self):
        """Обновляет счетчик API ключей"""
        keys_text = self.keys_edit.toPlainText()
        keys = [k.strip() for k in keys_text.splitlines() if k.strip()]
        unique_keys = list(set(keys))
        
        if len(keys) != len(unique_keys):
            self.keys_count_label.setText(f"Ключей: {len(unique_keys)} (уникальных из {len(keys)})")
            self.keys_count_label.setStyleSheet("color: orange; font-size: 10px;")
        else:
            self.keys_count_label.setText(f"Ключей: {len(keys)}")
            self.keys_count_label.setStyleSheet("color: blue; font-size: 10px;")
          
    def update_glossary_count(self):
        """Обновляет счетчик терминов в глоссарии"""
        glossary_dict = self.parse_glossary_text()
        self.glossary_count_label.setText(f"Терминов: {len(glossary_dict)}")
        
    def parse_glossary_text(self):
        """Парсит текст глоссария в словарь (поддерживает JSON и обычный формат)"""
        glossary_dict = {}
        text = self.glossary_text_edit.toPlainText().strip()
    
        if not text:
            return glossary_dict
    
        # Проверяем, является ли это JSON
        if text.startswith('{') and text.endswith('}'):
            try:
                glossary_dict = json.loads(text)
                return glossary_dict
            except json.JSONDecodeError:
                # Не JSON, обрабатываем как обычный текст
                pass
    
        # Обычный формат: Term = Translation
        for line in text.splitlines():
            line = line.strip()
            if not line or '=' not in line:
                continue
            
            parts = line.split('=', 1)
            if len(parts) == 2:
                original = parts[0].strip()
                translation = parts[1].strip()
            
                if original and translation:
                    glossary_dict[original] = translation
                
        return glossary_dict
        
    def load_preset_glossary(self, preset_name):
        """Загружает предустановленный глоссарий"""
        presets = {
            "Аниме/Манга": {
                "San": "сан",
                "Chan": "чан", 
                "Kun": "кун",
                "Sama": "сама",
                "Senpai": "сэмпай",
                "Kouhai": "кохай",
                "Sensei": "сэнсэй",
                "Onii-chan": "братик",
                "Onee-chan": "сестричка",
                "Baka": "дурак",
                "Kawaii": "милый",
                "Sugoi": "потрясающе"
            },
            "Китайские новеллы": {
                "Cultivator": "культиватор",
                "Dao": "Дао",
                "Qi": "ци",
                "Immortal": "бессмертный",
                "Sect": "секта",
                "Elder": "старейшина",
                "Junior": "младший",
                "Senior": "старший",
                "Young Master": "молодой господин",
                "Jade Beauty": "нефритовая красавица"
            },
            "Корейские новеллы": {
                "Oppa": "оппа",
                "Hyung": "хён",
                "Noona": "нуна",
                "Unnie": "онни",
                "Sunbae": "сонбэ",
                "Hoobae": "хубэ",
                "Ahjussi": "аджосси",
                "Ahjumma": "аджумма"
            },
            "Фэнтези": {
                "Mage": "маг",
                "Knight": "рыцарь",
                "Dragon": "дракон",
                "Elf": "эльф",
                "Dwarf": "гном",
                "Orc": "орк",
                "Spell": "заклинание",
                "Sword": "меч",
                "Shield": "щит",
                "Armor": "доспехи"
            },
            "Научная фантастика": {
                "AI": "ИИ",
                "Cyborg": "киборг",
                "Android": "андроид",
                "Spaceship": "космический корабль",
                "Laser": "лазер",
                "Quantum": "квантовый",
                "Warp": "варп",
                "Hyperspace": "гиперпространство"
            }
        }
        
        if preset_name in presets:
            # Добавляем к существующему глоссарию
            current_text = self.glossary_text_edit.toPlainText()
            if current_text and not current_text.endswith('\n'):
                current_text += '\n'
                
            new_lines = []
            for original, translation in presets[preset_name].items():
                new_lines.append(f"{original} = {translation}")
                
            self.glossary_text_edit.setPlainText(current_text + '\n'.join(new_lines))
            
    def load_glossary_from_file(self):
        """Загружает глоссарий из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл глоссария",
            "",
            "All supported (*.json *.txt);;JSON files (*.json);;Text files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    glossary_data = json.load(f)
                    
                lines = []
                for key, value in glossary_data.items():
                    lines.append(f"{key} = {value}")
                    
                self.glossary_text_edit.setPlainText('\n'.join(lines))
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    f"Загружено {len(glossary_data)} терминов из JSON"
                )
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.glossary_text_edit.setPlainText(content)
                
                lines = [line.strip() for line in content.splitlines() if '=' in line.strip()]
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех", 
                    f"Загружено {len(lines)} терминов из текстового файла"
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
            
    def save_glossary_to_file(self):
        """Сохраняет глоссарий в файл"""
        glossary_dict = self.parse_glossary_text()
        
        if not glossary_dict:
            QtWidgets.QMessageBox.warning(
                self,
                "Предупреждение",
                "Глоссарий пуст или неправильно отформатирован"
            )
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить глоссарий",
            "glossary.json",
            "JSON files (*.json);;Text files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(glossary_dict, f, ensure_ascii=False, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.glossary_text_edit.toPlainText())
                    
            QtWidgets.QMessageBox.information(
                self,
                "Успех",
                f"Глоссарий сохранен ({len(glossary_dict)} терминов)"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
            
    def select_file(self):
        """Выбор EPUB файла и анализ глав"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите EPUB файл для перевода",
            "",
            "EPUB файлы (*.epub);;All files (*)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
        
            # Анализируем EPUB и показываем диалог выбора глав
            try:
                with zipfile.ZipFile(file_path, 'r') as epub_zip:
                    html_files = [
                        name for name in epub_zip.namelist()
                        if name.lower().endswith(('.html', '.xhtml', '.htm'))
                        and not name.startswith('__MACOSX')
                    ]
                    html_files = sorted(html_files, key=extract_number_from_path)
                
                    if not html_files:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Ошибка",
                            "В EPUB файле не найдены HTML/XHTML главы"
                        )
                        self.selected_file = None
                        self.file_label.setText("Файл не выбран")
                        return
                
                    # Показываем диалог выбора глав
                    selector = EpubHtmlSelectorDialog(file_path, html_files, self)
                    if selector.exec():
                        selected = selector.get_selected_files()
                        if selected:
                            self.selected_html_files = selected
                            self.file_label.setText(
                                f"{os.path.basename(file_path)} ({len(selected)} глав выбрано)"
                            )
                        
                            # Проверяем уже переведенные главы если выбрана папка
                            if self.output_folder:
                                self.check_already_translated()
                        else:
                            self.selected_html_files = []
                            self.selected_file = None
                            self.file_label.setText("Главы не выбраны")
                    else:
                        self.selected_file = None
                        self.file_label.setText("Выбор отменен")
                    
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось прочитать EPUB: {e}"
                )
                self.selected_file = None
                self.file_label.setText("Ошибка чтения файла")
            
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения перевода"
        )
        if folder:
            self.output_folder = folder
            self.output_label.setText(folder)
        
            # Проверяем уже переведенные главы если выбран файл
            if self.selected_file and self.selected_html_files:
                self.check_already_translated()
            
    def load_keys_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл с ключами",
            "",
            "Text files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    keys = [line.strip() for line in f if line.strip()]
                self.keys_edit.setPlainText('\n'.join(keys))
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл: {e}")
                
    def validate_and_start(self):
        # Проверка обязательных полей
        if not self.selected_file:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите файл для перевода")
            return
    
        if not self.selected_html_files:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите главы для перевода")
            return
        
        if not self.output_folder:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите папку для сохранения")
            return
        
        keys_text = self.keys_edit.toPlainText()
        self.api_keys = [k.strip() for k in keys_text.splitlines() if k.strip()]
    
        if not self.api_keys:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите хотя бы один API ключ")
            return
        
        # Парсим глоссарий
        self.glossary_dict = self.parse_glossary_text()
    
        self.selected_model = self.model_combo.currentText()
        self.concurrent_requests = self.concurrency_spin.value()
    
        self.accept()
    
    def check_already_translated(self):
        """Проверяет какие главы уже переведены и предлагает их исключить"""
        if not self.output_folder or not self.selected_html_files:
            return
    
        already_translated = []
        not_translated = []
    
        epub_base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
    
        for html_file in self.selected_html_files:
            html_file_name = os.path.splitext(os.path.basename(html_file))[0]
            safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
            expected_output = os.path.join(
                self.output_folder,
                f"{epub_base_name}_{safe_html_name}_translated.html"
            )
        
            if os.path.exists(expected_output):
                already_translated.append(html_file)
            else:
                not_translated.append(html_file)
    
        if already_translated:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Обнаружены переведенные главы")
            msg.setText(f"Найдено переведенных глав: {len(already_translated)}")
            msg.setInformativeText(
                f"Всего выбрано: {len(self.selected_html_files)}\n"
                f"Уже переведено: {len(already_translated)}\n"
                f"Осталось перевести: {len(not_translated)}\n\n"
                "Что делать с уже переведенными главами?"
            )
        
            skip_btn = msg.addButton("Пропустить переведенные", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
            retranslate_btn = msg.addButton("Перевести заново", QtWidgets.QMessageBox.ButtonRole.RejectRole)
            cancel_btn = msg.addButton("Отмена", QtWidgets.QMessageBox.ButtonRole.RejectRole)
        
            msg.exec()
        
            if msg.clickedButton() == skip_btn:
                self.selected_html_files = not_translated
                self.file_label.setText(
                    f"{os.path.basename(self.selected_file)} "
                    f"({len(not_translated)} новых глав для перевода)"
                )
            
                # Показываем детали
                QtWidgets.QMessageBox.information(
                    self,
                    "Главы отфильтрованы",
                    f"Пропущено переведенных: {len(already_translated)}\n"
                    f"Будет переведено: {len(not_translated)}"
                )
            elif msg.clickedButton() == retranslate_btn:
                # Оставляем все главы для повторного перевода
                pass
            else:
                # Отмена - сбрасываем выбор
                self.selected_html_files = []
                self.selected_file = None
                self.file_label.setText("Выбор отменен")
    
    def get_settings(self):
        """Возвращает настройки в виде словаря"""
        # Определяем провайдера
        provider = 'gemini'  # По умолчанию
        if hasattr(self, 'provider_combo'):
            provider_text = self.provider_combo.currentText()
            provider = 'openrouter' if 'OpenRouter' in provider_text else 'gemini'
    
        return {
            'provider': provider,
            'file_path': self.selected_file,
            'selected_chapters': getattr(self, 'selected_html_files', []),
            'output_folder': self.output_folder,
            'api_keys': self.api_keys,
            'glossary_dict': self.glossary_dict,
            'model': self.model_combo.currentText(),
            'dynamic_glossary': self.dynamic_glossary_checkbox.isChecked(),
            'custom_prompt': self.custom_prompt_edit.toPlainText().strip() if hasattr(self, 'custom_prompt_edit') else None,
            'concurrent_requests': self.concurrent_requests
        }

class TranslationSessionManager:
    """Менеджер сессии перевода для отслеживания прогресса между перезапусками."""
    def __init__(self, session_file_path):
        self.session_file_path = session_file_path
        self.session_data = {
            'original_file': None,
            'output_folder': None,
            'total_files': 0,
            'completed_files': [],
            'failed_files': [],
            'content_filtered_files': [],  # Отдельный список для заблокированных фильтрами
            'current_key_index': 0,
            'api_keys': [],
            'model': DEFAULT_MODEL_NAME,
            'concurrent_requests': 10,
            'glossary_dict': {},
            'glossary_path': None,  # Для обратной совместимости
            'file_type': None,
            'epub_html_files': []
        }
        
    def init_new_session(self, settings):
        """Инициализирует новую сессию с начальными настройками"""
        self.session_data['original_file'] = settings['file_path']
        self.session_data['output_folder'] = settings['output_folder']
        self.session_data['api_keys'] = settings['api_keys']
        self.session_data['current_key_index'] = 0
        self.session_data['model'] = settings['model']
        self.session_data['concurrent_requests'] = settings['concurrent_requests']
        self.session_data['provider'] = settings.get('provider', 'gemini')
    
        # Сохраняем настройки глоссария и промпта
        if 'glossary_dict' in settings:
            self.session_data['glossary_dict'] = settings['glossary_dict']
        if 'dynamic_glossary' in settings:
            self.session_data['dynamic_glossary'] = settings['dynamic_glossary']
        if 'custom_prompt' in settings:
            self.session_data['custom_prompt'] = settings['custom_prompt']
        
        self.session_data['completed_files'] = []
        self.session_data['failed_files'] = []
        self.session_data['content_filtered_files'] = []
    
        # Определяем тип файла и список для обработки
        file_ext = os.path.splitext(settings['file_path'])[1].lower()
        self.session_data['file_type'] = file_ext[1:]
    
        if file_ext == '.epub':
            # Используем выбранные главы если они указаны
            if 'selected_chapters' in settings and settings['selected_chapters']:
                self.session_data['epub_html_files'] = settings['selected_chapters']
            else:
                # Иначе берем все HTML файлы из EPUB
                html_files = self._get_epub_html_files(settings['file_path'])
                self.session_data['epub_html_files'] = html_files
        
            self.session_data['total_files'] = len(self.session_data['epub_html_files'])
        
            # Сохраняем информацию о прогрессе
            print(f"Инициализация сессии: {self.session_data['total_files']} глав для перевода")
        else:
            self.session_data['total_files'] = 1
        
        self.save_session()
        
    def _get_epub_html_files(self, epub_path):
        """Извлекает список HTML файлов из EPUB."""
        html_files = []
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub_zip:
                for name in epub_zip.namelist():
                    if name.lower().endswith(('.html', '.xhtml', '.htm')) and not name.startswith('__MACOSX'):
                        html_files.append(name)
            return sorted(html_files, key=extract_number_from_path)
        except Exception as e:
            print(f"Ошибка чтения EPUB: {e}")
            return []
            
    def save_session(self):
        """Сохраняет текущее состояние сессии."""
        try:
            with open(self.session_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")
            return False
            
    def load_session(self):
        """Загружает сохраненную сессию."""
        try:
            if os.path.exists(self.session_file_path):
                with open(self.session_file_path, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")
            return False
        
    def mark_file_completed(self, file_tuple):
        """Отмечает файл как успешно обработанный."""
        if file_tuple not in self.session_data['completed_files']:
            self.session_data['completed_files'].append(file_tuple)
            self.save_session()
            
    def mark_file_failed(self, file_tuple, error_msg):
        """Отмечает файл как неудачно обработанный."""
        self.session_data['failed_files'].append({
            'file': file_tuple,
            'error': error_msg,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_session()
        
    def mark_file_content_filtered(self, file_tuple, error_msg):
        """Отмечает файл как заблокированный фильтрами контента"""
        # Проверяем, не добавлен ли уже
        if not any(f['file'] == file_tuple for f in self.session_data['content_filtered_files']):
            self.session_data['content_filtered_files'].append({
                'file': file_tuple,
                'error': error_msg,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            self.save_session()
            
    def is_content_filtered(self, file_tuple):
        """Проверяет, была ли глава заблокирована фильтрами"""
        return any(f['file'] == file_tuple for f in self.session_data['content_filtered_files'])
        
    def get_pending_files(self):
        """Возвращает список файлов для обработки (еще не завершенных и не заблокированных)"""
        if self.session_data['file_type'] == 'epub':
            pending = []
            for html_file in self.session_data['epub_html_files']:
                file_tuple = ('epub', self.session_data['original_file'], html_file)
            
                # Пропускаем уже успешно обработанные
                if file_tuple in self.session_data['completed_files']:
                    continue
                
                # Пропускаем заблокированные фильтрами
                if self.is_content_filtered(file_tuple):
                    continue
                
                # === НОВОЕ: Пропускаем главы с техническими ошибками (500/503) ===
                # Они НЕ должны повторяться при смене ключа
                is_technical_error = False
                for failed_entry in self.session_data['failed_files']:
                    if failed_entry.get('file') == file_tuple:
                        error_msg = str(failed_entry.get('error', '')).lower()
                        if any(err in error_msg for err in ['500', '503', '504', 'internal error', 'service unavailable']):
                            is_technical_error = True
                            break
                        
                if is_technical_error:
                    continue
                
                # Добавляем в список для обработки
                pending.append(file_tuple)
            
            return pending
        else:
            file_type = self.session_data['file_type']
            file_tuple = (file_type, self.session_data['original_file'], None)
        
            if file_tuple in self.session_data['completed_files']:
                return []
            if self.is_content_filtered(file_tuple):
                return []
            
            # Проверяем на технические ошибки
            for failed_entry in self.session_data['failed_files']:
                if failed_entry.get('file') == file_tuple:
                    error_msg = str(failed_entry.get('error', '')).lower()
                    if any(err in error_msg for err in ['500', '503', '504', 'internal error', 'service unavailable']):
                        return []
                    
            return [file_tuple]
            
    def is_rate_limited(self, error_msg):
        """Проверяет, является ли ошибка превышением лимита запросов."""
        rate_limit_indicators = [
            '429',
            'rate limit',
            'ResourceExhausted',
            'too many requests'
        ]
        # НЕ включаем 'quota exceeded' и 'exceeded your current quota' сюда
        # так как это отдельный случай - полное исчерпание квоты
        error_lower = str(error_msg).lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators) and \
               'exceeded your current quota' not in error_lower and \
               'quota exceeded' not in error_lower

    def is_quota_exceeded(self, error_msg):
        """Проверяет, превышена ли квота API ключа полностью"""
        quota_indicators = [
            'exceeded your current quota',
            'quota exceeded',
            'out of quota'
        ]
        error_lower = str(error_msg).lower()
        return any(indicator in error_lower for indicator in quota_indicators)
        
    def is_content_filter_error(self, error_msg):
        """Проверяет, является ли ошибка блокировкой контента"""
        content_filter_indicators = [
            'PROHIBITED_CONTENT',
            'block_reason',
            'content filter',
            'blocked prompt',
            'safety',
            'harmful',
            'inappropriate',
            'BlockedPromptException',
            'StopCandidateException'
        ]
        error_lower = str(error_msg).lower()
        return any(indicator.lower() in error_lower for indicator in content_filter_indicators)
        
    def get_progress(self):
        """Возвращает текущий прогресс."""
        completed = len(self.session_data['completed_files'])
        filtered = len(self.session_data['content_filtered_files'])
        total = self.session_data['total_files']
        return completed, filtered, total

class TranslationProgressLog:
    """Ведет постоянный лог переведенных глав между сессиями"""
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.log_file = os.path.join(output_folder, "translation_progress.json")
        self.progress_data = self.load_progress()
        
    def load_progress(self):
        """Загружает историю прогресса"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'completed_chapters': [],
            'total_processed': 0,
            'sessions': []
        }
    
    def save_progress(self):
        """Сохраняет прогресс"""
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения прогресса: {e}")
    
    def add_completed_chapter(self, epub_file, chapter_name):
        """Добавляет главу в список завершенных"""
        chapter_key = f"{epub_file}::{chapter_name}"
        if chapter_key not in self.progress_data['completed_chapters']:
            self.progress_data['completed_chapters'].append(chapter_key)
            self.progress_data['total_processed'] += 1
            self.save_progress()
    
    def is_chapter_completed(self, epub_file, chapter_name):
        """Проверяет, была ли глава уже переведена"""
        chapter_key = f"{epub_file}::{chapter_name}"
        return chapter_key in self.progress_data['completed_chapters']
    
    def get_pending_chapters(self, epub_file, all_chapters):
        """Возвращает список глав, которые еще не переведены"""
        pending = []
        for chapter in all_chapters:
            if not self.is_chapter_completed(epub_file, chapter):
                pending.append(chapter)
        return pending
    
    def add_session_info(self, info):
        """Добавляет информацию о сессии"""
        session_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'chapters_processed': info.get('chapters_processed', 0),
            'model': info.get('model', 'unknown'),
            'duration': info.get('duration', 0)
        }
        self.progress_data['sessions'].append(session_data)
        self.save_progress()

def run_translation_with_auto_restart(initial_settings=None):
    """Главная функция для запуска перевода с автоматическим перезапуском при rate limit."""
    
    # Определяем путь к файлу сессии
    session_file = os.path.join(
        initial_settings['output_folder'] if initial_settings else os.getcwd(),
        'translation_session.json'
    )
    
    # Создаем менеджер сессии
    session_manager = TranslationSessionManager(session_file)
    
    # Создаем лог прогресса
    progress_log = TranslationProgressLog(
        initial_settings['output_folder'] if initial_settings else session_manager.session_data['output_folder']
    )

    # Если есть начальные настройки, проверяем уже переведенные главы
    if initial_settings and 'selected_chapters' in initial_settings:
        epub_file = initial_settings['file_path']
        selected_chapters = initial_settings['selected_chapters']
    
        # Фильтруем уже переведенные
        pending_chapters = progress_log.get_pending_chapters(epub_file, selected_chapters)
    
        if len(pending_chapters) < len(selected_chapters):
            already_done = len(selected_chapters) - len(pending_chapters)
            print(f"Пропущено уже переведенных глав: {already_done}")
            print(f"Осталось перевести: {len(pending_chapters)}")
        
            # Обновляем список для перевода
            initial_settings['selected_chapters'] = pending_chapters
    
    # Если есть начальные настройки, инициализируем новую сессию
    if initial_settings:
        session_manager.init_new_session(initial_settings)
        print(f"Инициализирована новая сессия перевода")
    else:
        # Пытаемся загрузить существующую сессию
        if not session_manager.load_session():
            print("Не удалось загрузить сессию")
            return False
    
    # Создаем единый ApiKeyManager со всеми ключами
    all_api_keys = session_manager.session_data['api_keys']
    shared_api_key_manager = ApiKeyManager(all_api_keys)
    print(f"Инициализирован менеджер с {len(all_api_keys)} ключами")
    
    # === ДОБАВЬТЕ ЭТУ СТРОКУ ===
    translator_window = None  # Объявляем переменную заранее
    
    # Основной цикл с автоматическим перезапуском
    continue_translation = True
    while continue_translation:
        # Получаем список файлов для обработки (исключая заблокированные фильтрами)
        pending_files = session_manager.get_pending_files()
        
        if not pending_files:
            print("Все файлы обработаны!")
            
            # Показываем финальную статистику
            completed = len(session_manager.session_data['completed_files'])
            filtered = len(session_manager.session_data['content_filtered_files'])
            failed = len(session_manager.session_data['failed_files'])
            
            message = f"Перевод завершен!\n\n"
            message += f"✅ Успешно переведено: {completed}\n"
            
            if filtered > 0:
                message += f"🚫 Заблокировано фильтрами: {filtered}\n"
                message += "(Используйте основное окно программы для обработки через OpenRouter)\n"
                
            if failed > 0:
                message += f"❌ Ошибки: {failed}\n"
                
            QtWidgets.QMessageBox.information(
                None,
                "Перевод завершен",
                message
            )
            
            # НЕ удаляем файл сессии если есть заблокированные главы
            if filtered == 0:
                try:
                    os.remove(session_file)
                except:
                    pass
            else:
                print(f"Сессия сохранена для обработки {filtered} заблокированных глав")
                
            return True
        
        # Проверяем, есть ли доступные ключи
        if not shared_api_key_manager.has_available_keys():
            print("Все API ключи исчерпаны!")
            completed, filtered, total = session_manager.get_progress()
            QtWidgets.QMessageBox.critical(
                None,
                "Ключи исчерпаны",
                f"Все доступные API ключи были использованы.\n\n"
                f"Обработано: {completed}/{total} файлов\n"
                f"Заблокировано фильтрами: {filtered}\n\n"
                f"Добавьте новые ключи и перезапустите программу."
            )
            return False
        
        print(f"Осталось обработать файлов: {len(pending_files)}")
        print(f"Статус ключей: {shared_api_key_manager.get_usage_report()}")
        
        # Создаем приложение Qt
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(sys.argv)
            
        try:
            # === НОВОЕ: Флаг для отслеживания необходимости продолжения ===
            need_restart = False
            
            # Создаем кастомный класс с переопределенным методом
            class AutoRestartTranslatorApp(TranslatorApp):
                def __init__(self, api_key_manager, session_mgr):
                    super().__init__(api_key_manager)
                    self.session_manager = session_mgr
                    self.rate_limit_detected = False
                    self.quota_exceeded = False
                    self.auto_mode = True  # Флаг автоматического режима

                @QtCore.pyqtSlot(int, int, list, bool, object)
                def on_translation_finished(self, success_count, error_count, errors_data, quota_exceeded=False, failed_file=None):
                    nonlocal need_restart  # Используем внешнюю переменную
                    nonlocal translator_window  # Используем внешнюю переменную окна

                    content_filtered_count = 0
                    rate_limit_count = 0
                    quota_count = 0
                    other_errors_count = 0
                    technical_errors_count = 0  # Для ошибок 500/503
        
                    # === НОВОЕ: Собираем все файлы для повторной обработки ===
                    files_for_new_key = []

                    # Обрабатываем каждую ошибку
                    for file_info, error_msg in errors_data:
                        error_str = str(error_msg)

                        # Проверяем тип ошибки
                        if self.session_manager.is_content_filter_error(error_str):
                            # Глава заблокирована фильтрами - сохраняем отдельно
                            self.session_manager.mark_file_content_filtered(file_info, error_msg)
                            content_filtered_count += 1
                            self.append_log(f"[FILTERED] Глава заблокирована фильтрами и сохранена для альтернативной обработки")

                        elif "Требуется новый API ключ" in error_str:
                            # Главы которые нужно обработать новым ключом
                            quota_count += 1
                            self.quota_exceeded = True
                            files_for_new_key.append(file_info)  # Сохраняем для следующего ключа

                        elif self.session_manager.is_quota_exceeded(error_str) or quota_exceeded:
                            # Превышение квоты
                            quota_count += 1
                            self.quota_exceeded = True
                            files_for_new_key.append(file_info)  # Сохраняем для следующего ключа

                        elif self.session_manager.is_rate_limited(error_str):
                            # Временный rate limit RPM - НЕ требует смены ключа
                            rate_limit_count += 1
                            # НЕ устанавливаем self.rate_limit_detected = True
                            # Эти главы будут повторены с тем же ключом после задержки
                            self.session_manager.mark_file_failed(file_info, error_msg)

                        elif any(err_code in error_str for err_code in ['500', '503', '504', 'internal error', 'service unavailable']):
                            # Технические ошибки - НЕ требуют смены ключа и НЕ повторяются
                            technical_errors_count += 1
                            self.session_manager.mark_file_failed(file_info, error_msg)

                        else:
                            # Другие ошибки - отмечаем как неудачные
                            self.session_manager.mark_file_failed(file_info, error_msg)
                            other_errors_count += 1

                    # Отмечаем успешно обработанные файлы
                    for file_info in self.selected_files_data:
                        if not any(err_file == file_info for err_file, _ in errors_data):
                            self.session_manager.mark_file_completed(file_info)

                    # Выводим статистику
                    if content_filtered_count > 0:
                        self.append_log(f"[INFO] Заблокировано фильтрами: {content_filtered_count} глав (будут обработаны через OpenRouter)")
                    if quota_count > 0:
                        self.append_log(f"[INFO] Требуется новый ключ для {quota_count} глав")
                    if rate_limit_count > 0:
                        self.append_log(f"[INFO] RPM Rate limit: {rate_limit_count} глав (будут повторены после задержки)")
                    if technical_errors_count > 0:
                        self.append_log(f"[INFO] Технические ошибки (500/503): {technical_errors_count} глав (НЕ будут повторены)")
                    if other_errors_count > 0:
                        self.append_log(f"[INFO] Другие ошибки: {other_errors_count} глав")

                    # === НОВОЕ: Если есть главы для нового ключа, обновляем список для обработки ===
                    if files_for_new_key and (self.quota_exceeded or quota_exceeded):
                        self.append_log(f"[INFO] Подготовка {len(files_for_new_key)} глав для обработки новым ключом...")
                        # Устанавливаем новый список файлов для обработки
                        if translator_window:  # Проверяем что translator_window существует
                            translator_window.selected_files_data = files_for_new_key
                            translator_window.update_file_list_widget()

                    # Обрабатываем автоматический режим
                    if self.auto_mode and (self.quota_exceeded or quota_exceeded):
                        self.append_log("[AUTO] Требуется смена ключа, перезапуск через 3 секунды...")
                        need_restart = True

                        # НЕ вызываем родительский метод, чтобы не блокировать UI диалогом
                        # Просто обновляем UI элементы
                        self.set_controls_enabled(True)

                        # Скрываем кнопки для ручного режима
                        self.retry_failed_btn.setVisible(False)
                        self.export_failed_html_btn.setVisible(False)

                        # Закрываем окно через 3 секунды
                        QtCore.QTimer.singleShot(3000, self.close)
                        return  # ВАЖНО: выходим здесь, не вызывая super()
        
                    elif self.auto_mode and self.rate_limit_detected:
                        self.append_log("[AUTO] Rate limit обнаружен, перезапуск через 30 секунд...")
                        need_restart = True

                        # Обновляем UI
                        self.set_controls_enabled(True)

                        # Закрываем окно через 30 секунд
                        QtCore.QTimer.singleShot(30000, self.close)
                        return  # ВАЖНО: выходим здесь

                    # Если не автоматический режим или нет необходимости в перезапуске,
                    # вызываем родительский метод
                    # Передаем только реальные ошибки (не фильтры и не rate limit для повтора)
                    real_errors = [(f, e) for f, e in errors_data 
                                   if not self.session_manager.is_content_filter_error(str(e))
                                   and "Требуется новый API ключ" not in str(e)]

                    super().on_translation_finished(success_count, len(real_errors), real_errors, False, None)

                def set_controls_enabled(self, enabled):
                    """Переопределяем для автоматического режима"""
                    # В автоматическом режиме не разблокируем контролы при завершении
                    if not self.auto_mode or not enabled:
                        super().set_controls_enabled(enabled)
                
                def on_translation_finished(self, success_count, error_count, errors_data, quota_exceeded=False, failed_file=None):
                    nonlocal need_restart  # Используем внешнюю переменную
    
                    content_filtered_count = 0
                    rate_limit_count = 0
                    quota_count = 0
                    other_errors_count = 0

                    # Обрабатываем каждую ошибку
                    for file_info, error_msg in errors_data:
                        error_str = str(error_msg)

                        # Проверяем тип ошибки
                        if self.session_manager.is_content_filter_error(error_str):
                            # Глава заблокирована фильтрами - сохраняем отдельно
                            self.session_manager.mark_file_content_filtered(file_info, error_msg)
                            content_filtered_count += 1
                            self.append_log(f"[FILTERED] Глава заблокирована фильтрами и сохранена для альтернативной обработки")
    
                        elif "Требуется новый API ключ" in error_str:
                            # Главы которые нужно обработать новым ключом
                            quota_count += 1
                            self.quota_exceeded = True
            
                        elif self.session_manager.is_quota_exceeded(error_str) or quota_exceeded:
                            # Превышение квоты
                            quota_count += 1
                            self.quota_exceeded = True

                        elif self.session_manager.is_rate_limited(error_str):
                            # Временный rate limit
                            rate_limit_count += 1
                            self.rate_limit_detected = True

                        else:
                            # Другие ошибки - отмечаем как неудачные
                            self.session_manager.mark_file_failed(file_info, error_msg)
                            other_errors_count += 1

                    # Отмечаем успешно обработанные файлы
                    for file_info in self.selected_files_data:
                        if not any(err_file == file_info for err_file, _ in errors_data):
                            self.session_manager.mark_file_completed(file_info)

                    # Выводим статистику
                    if content_filtered_count > 0:
                        self.append_log(f"[INFO] Заблокировано фильтрами: {content_filtered_count} глав (будут обработаны через OpenRouter)")
                    if quota_count > 0:
                        self.append_log(f"[INFO] Требуется новый ключ для {quota_count} глав")
                    if rate_limit_count > 0:
                        self.append_log(f"[INFO] Rate limit: {rate_limit_count} глав")
                    if other_errors_count > 0:
                        self.append_log(f"[INFO] Другие ошибки: {other_errors_count} глав")

                    # === ВАЖНО: Сначала обрабатываем автоматический режим ===
                    if self.auto_mode and (self.quota_exceeded or quota_exceeded):
                        self.append_log("[AUTO] Требуется смена ключа, перезапуск через 3 секунды...")
                        need_restart = True
        
                        # НЕ вызываем родительский метод, чтобы не блокировать UI диалогом
                        # Просто обновляем UI элементы
                        self.set_controls_enabled(True)
        
                        # Скрываем кнопки для ручного режима
                        self.retry_failed_btn.setVisible(False)
                        self.export_failed_html_btn.setVisible(False)
        
                        # Закрываем окно через 3 секунды
                        QtCore.QTimer.singleShot(3000, self.close)
                        return  # ВАЖНО: выходим здесь, не вызывая super()
        
                    elif self.auto_mode and self.rate_limit_detected:
                        self.append_log("[AUTO] Rate limit обнаружен, перезапуск через 30 секунд...")
                        need_restart = True
        
                        # Обновляем UI
                        self.set_controls_enabled(True)
        
                        # Закрываем окно через 30 секунд
                        QtCore.QTimer.singleShot(30000, self.close)
                        return  # ВАЖНО: выходим здесь
    
                    # Если не автоматический режим или нет необходимости в перезапуске,
                    # вызываем родительский метод
                    # Передаем только реальные ошибки (не фильтры и не rate limit для повтора)
                    real_errors = [(f, e) for f, e in errors_data 
                                   if not self.session_manager.is_content_filter_error(str(e))
                                   and "Требуется новый API ключ" not in str(e)]

                    super().on_translation_finished(success_count, len(real_errors), real_errors, False, None)
        
                    # Если нужна смена ключа - устанавливаем флаг и закрываем окно
                    if self.quota_exceeded and self.auto_mode:
                        self.append_log("[AUTO] Требуется смена ключа, перезапуск через 3 секунды...")
                        need_restart = True
                        # Закрываем окно через 3 секунды
                        QtCore.QTimer.singleShot(3000, self.close)
                    elif self.rate_limit_detected and self.auto_mode:
                        self.append_log("[AUTO] Rate limit обнаружен, перезапуск через 30 секунд...")
                        need_restart = True
                        QtCore.QTimer.singleShot(30000, self.close)
            
            # Проверяем провайдера из настроек
            is_openrouter = False
            if initial_settings and initial_settings.get('provider') == 'openrouter':
                is_openrouter = True
            elif session_manager.session_data.get('provider') == 'openrouter':
                is_openrouter = True

            # Создаем и настраиваем главное окно
            translator_window = AutoRestartTranslatorApp(shared_api_key_manager, session_manager)

            # Устанавливаем провайдера
            if is_openrouter:
                if hasattr(translator_window, 'provider_combo'):
                    translator_window.provider_combo.setCurrentText("OpenRouter")
                    # Вызываем обработчик для обновления интерфейса
                    translator_window.on_provider_changed("OpenRouter")
            
            # Загружаем настройки из сессии
            translator_window.out_folder = session_manager.session_data['output_folder']
            translator_window.out_lbl.setText(translator_window.out_folder)
            
            # Обновляем контекст менеджер
            translator_window.context_manager = ContextManager(translator_window.out_folder)
            
            # Настраиваем динамический глоссарий если указано в настройках
            # Используем данные из initial_settings или session_manager
            dynamic_glossary_enabled = True  # По умолчанию включен
            if initial_settings and 'dynamic_glossary' in initial_settings:
                dynamic_glossary_enabled = initial_settings.get('dynamic_glossary', True)
            elif session_manager.session_data and 'dynamic_glossary' in session_manager.session_data:
                dynamic_glossary_enabled = session_manager.session_data.get('dynamic_glossary', True)

            if dynamic_glossary_enabled:
                translator_window.context_manager.use_dynamic_glossary = True
            
            # Загружаем кастомный промпт если есть
            if initial_settings and 'custom_prompt' in initial_settings and initial_settings['custom_prompt']:
                translator_window.prompt_edit.setPlainText(initial_settings['custom_prompt'])
            elif session_manager.session_data.get('custom_prompt'):
                translator_window.prompt_edit.setPlainText(session_manager.session_data['custom_prompt'])
            
            # Загружаем глоссарий если есть
            if session_manager.session_data.get('glossary_dict'):
                translator_window.context_manager.global_glossary = session_manager.session_data['glossary_dict']
                translator_window.context_manager.save_glossary()
                print(f"Загружен глоссарий: {len(session_manager.session_data['glossary_dict'])} терминов")
                    
            # Устанавливаем модель и параметры
            translator_window.model_combo.setCurrentText(session_manager.session_data['model'])
            translator_window.concurrency_spin.setValue(session_manager.session_data['concurrent_requests'])
            
            # Загружаем файлы для обработки
            translator_window.selected_files_data = pending_files
            translator_window.update_file_list_widget()
            
            # Показываем окно
            translator_window.show()
            
            # Автоматически запускаем перевод через небольшую задержку
            def auto_start_translation():
                if translator_window.isVisible():
                    translator_window.start_translation()
                    
            QtCore.QTimer.singleShot(1000, auto_start_translation)
            
            # Запускаем event loop
            app.exec()
            
            # После закрытия окна проверяем, нужен ли перезапуск
            if need_restart:
                print("Перезапуск с новым ключом...")
                # Небольшая дополнительная задержка
                time.sleep(2)
                continue  # Продолжаем главный цикл
            else:
                # Перевод завершен успешно
                continue_translation = False
                
        except Exception as e:
            print(f"Ошибка в процессе перевода: {e}")
            traceback.print_exc()
            return False
            
    return True

class EpubCreator:
    """Создает EPUB файл версии 2 из HTML глав."""
    def __init__(self, title, author="Unknown", language="ru"):
        self.title = title
        self.author = author
        self.language = language
        self.chapters = []
        self.uuid = str(uuid.uuid4())

    def add_chapter(self, filename, content, title):
        """Добавляет главу в книгу."""
        self.chapters.append({
            'filename': filename,
            'content': content,
            'title': title,
            'id': f'chapter{len(self.chapters) + 1}'
        })

    def create_epub(self, output_path):
        """Создает EPUB файл."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            epub.writestr('META-INF/container.xml', self._create_container())
            epub.writestr('OEBPS/content.opf', self._create_opf())
            epub.writestr('OEBPS/toc.ncx', self._create_ncx())
            epub.writestr('OEBPS/styles.css', self._create_styles())

            for chapter in self.chapters:
                epub.writestr(f'OEBPS/{chapter["filename"]}', chapter['content'])

    def _create_container(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''

    def _create_opf(self):
        opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{self.title}</dc:title>
        <dc:creator>{self.author}</dc:creator>
        <dc:language>{self.language}</dc:language>
        <dc:identifier id="BookID">urn:uuid:{self.uuid}</dc:identifier>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="styles" href="styles.css" media-type="text/css"/>'''
        for chapter in self.chapters:
            opf += f'\n        <item id="{chapter["id"]}" href="{chapter["filename"]}" media-type="application/xhtml+xml"/>'
        opf += '\n    </manifest>\n    <spine toc="ncx">'
        for chapter in self.chapters:
            opf += f'\n        <itemref idref="{chapter["id"]}"/>'
        opf += '\n    </spine>\n</package>'
        return opf

    def _create_ncx(self):
        ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{self.uuid}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{self.title}</text></docTitle>
    <navMap>'''
        for i, chapter in enumerate(self.chapters):
            ncx += f'''
        <navPoint id="navPoint-{i+1}" playOrder="{i+1}">
            <navLabel><text>{chapter["title"]}</text></navLabel>
            <content src="{chapter["filename"]}"/>
        </navPoint>'''
        ncx += '\n    </navMap>\n</ncx>'
        return ncx

    def _create_styles(self):
        return '''body { font-family: Georgia, serif; } p { text-indent: 1.5em; margin: 0; }'''

class TranslatedChaptersManagerDialog(QDialog):
    """Диалог для управления переведенными главами и создания EPUB."""
    def __init__(self, translated_folder, parent=None):
        super().__init__(parent)
        self.translated_folder = translated_folder
        self.chapters_data = []
        self.setWindowTitle("Менеджер EPUB")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_chapters()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Управление переведенными главами для сборки EPUB:"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Порядок", "Имя файла", "Действия"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(btn("Добавить файл...", self.add_external_file))
        buttons_layout.addWidget(btn("Заменить выбранный...", self.replace_selected_file))
        buttons_layout.addWidget(btn("Удалить выбранный", self.delete_selected_file))
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        metadata_group = QGroupBox("Метаданные книги")
        metadata_layout = QFormLayout()
        self.title_edit = QtWidgets.QLineEdit(os.path.basename(self.translated_folder))
        self.author_edit = QtWidgets.QLineEdit("Unknown")
        metadata_layout.addRow("Название книги:", self.title_edit)
        metadata_layout.addRow("Автор:", self.author_edit)
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        self.create_epub_btn = QPushButton("🚀 Собрать EPUB")
        self.create_epub_btn.setStyleSheet("background-color: #ccffcc;")
        self.create_epub_btn.clicked.connect(self.create_epub)
        layout.addWidget(self.create_epub_btn)

    def load_chapters(self):
        """Загружает и отображает список переведенных глав."""
        try:
            html_files = glob.glob(os.path.join(self.translated_folder, "*_translated.html"))
            self.chapters_data = sorted([{'filepath': f} for f in html_files], key=lambda x: extract_number_from_path(x['filepath']))
            self.table.setRowCount(len(self.chapters_data))
            for i, data in enumerate(self.chapters_data):
                self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.table.setItem(i, 1, QTableWidgetItem(os.path.basename(data['filepath'])))
                view_btn = QPushButton("Просмотр")
                view_btn.clicked.connect(partial(self.view_chapter, i))
                self.table.setCellWidget(i, 2, view_btn)
        except Exception as e:
            # <<< ИСПРАВЛЕНО: Добавлен префикс QtWidgets.
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить главы: {e}")

    def add_external_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выберите HTML файл", self.translated_folder, "HTML files (*.html *.htm)")
        if filepath:
            new_name = f"manual_{len(self.chapters_data) + 1}_translated.html"
            shutil.copy2(filepath, os.path.join(self.translated_folder, new_name))
            self.load_chapters()

    def replace_selected_file(self):
        current_row = self.table.currentRow()
        if current_row < 0: return
        filepath, _ = QFileDialog.getOpenFileName(self, "Выберите HTML файл для замены", self.translated_folder, "HTML files (*.html *.htm)")
        if filepath:
            shutil.copy2(filepath, self.chapters_data[current_row]['filepath'])
            self.load_chapters()
            self.table.selectRow(current_row)

    def delete_selected_file(self):
        current_row = self.table.currentRow()
        if current_row < 0: return
        # <<< ИСПРАВЛЕНО: Добавлен префикс QtWidgets.
        reply = QtWidgets.QMessageBox.question(self, "Подтверждение", "Удалить этот файл главы?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.chapters_data[current_row]['filepath'])
                self.load_chapters()
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка удаления", f"Не удалось удалить файл: {e}")


    def view_chapter(self, index):
        filepath = self.chapters_data[index]['filepath']
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Просмотр: {os.path.basename(filepath)}")
        dialog.setMinimumSize(800, 700)
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text_edit.setHtml(f.read())
        except Exception as e:
            text_edit.setPlainText(f"Ошибка чтения файла: {e}")
        layout.addWidget(text_edit)
        dialog.exec()

    def create_epub(self):
        title = self.title_edit.text() or "Переведенная книга"
        author = self.author_edit.text() or "Неизвестный автор"
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        output_path, _ = QFileDialog.getSaveFileName(self, "Сохранить EPUB", f"{safe_title}.epub", "EPUB files (*.epub)")
        if not output_path: return

        if not BS4_AVAILABLE:
            # <<< ИСПРАВЛЕНО: Добавлен префикс QtWidgets.
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Для создания EPUB необходима библиотека BeautifulSoup4.")
            return

        try:
            creator = EpubCreator(title, author)
            for i, chapter_data in enumerate(self.chapters_data):
                with open(chapter_data['filepath'], 'r', encoding='utf-8') as f:
                    content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                h_tags = soup.find(['h1', 'h2', 'h3'])
                chapter_title = h_tags.get_text().strip() if h_tags else f"Глава {i + 1}"
                creator.add_chapter(f"c{i+1}.xhtml", content, chapter_title)
            
            creator.create_epub(output_path)
            # <<< ИСПРАВЛЕНО: Добавлен префикс QtWidgets.
            QtWidgets.QMessageBox.information(self, "Успех", f"EPUB успешно создан: {output_path}")
        except Exception as e:
            # <<< ИСПРАВЛЕНО: Добавлен префикс QtWidgets.
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось создать EPUB: {e}\n{traceback.format_exc()}")
def btn(text, func):
    b = QPushButton(text)
    b.clicked.connect(func)
    return b

class GlossaryEditorDialog(QDialog):
    """Простой диалог для редактирования глоссария в формате JSON."""
    def __init__(self, glossary_json_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор Глоссария")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(
            "Отредактируйте глоссарий. Формат: JSON (ключ: значение).\n"
            "Ключ - термин на языке оригинала, значение - его перевод.\n"
            'Пример: {"Son Goku": "Сон Гоку", "Kamehameha": "Камехамеха"}'
        )
        layout.addWidget(info_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QtGui.QFont("Consolas", 10))
        self.text_edit.setPlainText(glossary_json_str)
        layout.addWidget(self.text_edit)
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def validate_and_accept(self):
        try:
            # Проверяем, что текст является валидным JSON
            json.loads(self.text_edit.toPlainText())
            self.accept()
        except json.JSONDecodeError as e:
            self.status_label.setText(f"Ошибка в формате JSON: {e}")
            self.status_label.setStyleSheet("color: red;")

    def get_glossary_text(self):
        return self.text_edit.toPlainText()

class ContextManager:
    """Управляет долгосрочным контекстом: глоссарием, резюме и т.д."""
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.glossary_path = os.path.join(self.output_folder, "context_glossary.json")
        self.global_glossary = {}
        self.use_dynamic_glossary = False  # Флаг для включения динамического глоссария
        self.min_term_length = 3  # Минимальная длина термина для динамического поиска
        self.load_glossary()

    def load_glossary(self):
        """Загружает глоссарий из файла."""
        try:
            if os.path.exists(self.glossary_path):
                with open(self.glossary_path, 'r', encoding='utf-8') as f:
                    self.global_glossary = json.load(f)
                return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки глоссария: {e}")
            self.global_glossary = {}
        return False

    def save_glossary(self):
        """Сохраняет глоссарий в файл."""
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            with open(self.glossary_path, 'w', encoding='utf-8') as f:
                json.dump(self.global_glossary, f, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            print(f"Ошибка сохранения глоссария: {e}")
            return False

    def get_glossary_as_json_str(self):
        """Возвращает глоссарий как отформатированную JSON строку."""
        return json.dumps(self.global_glossary, ensure_ascii=False, indent=4)
        
    def set_glossary_from_json_str(self, json_str):
        """Обновляет глоссарий из JSON строки."""
        try:
            self.global_glossary = json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def format_glossary_for_prompt(self, text_content=None):
        """Форматирует глоссарий для вставки в промпт с опциональной фильтрацией"""
        glossary_to_use = self.global_glossary
        
        # Если включен динамический глоссарий и передан текст, фильтруем
        if text_content and self.use_dynamic_glossary and self.global_glossary:
            original_size = len(self.global_glossary)
            glossary_to_use = DynamicGlossaryFilter.filter_glossary_for_text(
                self.global_glossary, 
                text_content,
                self.min_term_length
            )
            filtered_size = len(glossary_to_use)
            
            # Логируем статистику фильтрации (опционально)
            if original_size > 0:
                reduction_percent = (1 - filtered_size / original_size) * 100
                print(f"[DYNAMIC GLOSSARY] Из {original_size} терминов отобрано {filtered_size} " +
                      f"(сокращение на {reduction_percent:.1f}%)")
        
        if not glossary_to_use:
            return "Глоссарий пуст или не содержит релевантных терминов."
        
        lines = ["Строго следуй этому глоссарию:"]
        for key, value in glossary_to_use.items():
            lines.append(f'- "{key}" всегда переводить как "{value}"')
        
        # Добавляем информацию о фильтрации в конец
        if text_content and self.use_dynamic_glossary and glossary_to_use != self.global_glossary:
            lines.append(f"\n(Примечание: из полного глоссария в {len(self.global_glossary)} терминов " +
                        f"отобрано {len(glossary_to_use)} релевантных для данного текста)")
            
        return "\n".join(lines)

class GlossaryMerger:
    """Инструмент для слияния и управления глоссариями"""
    
    @staticmethod
    def merge_glossaries(glossaries_list):
        """
        Объединяет несколько глоссариев с обработкой конфликтов
        
        Args:
            glossaries_list: список словарей-глоссариев
            
        Returns:
            merged_glossary: объединенный глоссарий
            conflicts: словарь конфликтов {термин: [вариант1, вариант2, ...]}
        """
        merged = {}
        conflicts = {}
        
        for glossary in glossaries_list:
            for term, translation in glossary.items():
                if term in merged:
                    if merged[term] != translation:
                        # Конфликт - разные переводы одного термина
                        if term not in conflicts:
                            conflicts[term] = [merged[term]]
                        if translation not in conflicts[term]:
                            conflicts[term].append(translation)
                else:
                    merged[term] = translation
                    
        return merged, conflicts
    
    @staticmethod
    def find_reverse_conflicts(glossary):
        """
        Находит случаи, когда разные термины переводятся одинаково
        
        Returns:
            dict: {перевод: [термин1, термин2, ...]}
        """
        reverse_map = {}
        for term, translation in glossary.items():
            if translation not in reverse_map:
                reverse_map[translation] = []
            reverse_map[translation].append(term)
            
        # Оставляем только конфликты (где больше 1 термина)
        conflicts = {trans: terms for trans, terms in reverse_map.items() if len(terms) > 1}
        return conflicts

class GlossaryConflictResolver(QDialog):
    """Диалог для разрешения конфликтов при слиянии глоссариев"""
    
    def __init__(self, conflicts, reverse_conflicts=None, parent=None):
        super().__init__(parent)
        self.conflicts = conflicts
        self.reverse_conflicts = reverse_conflicts or {}
        self.resolved = {}
        self.setWindowTitle("Разрешение конфликтов глоссария")
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Информация
        info_label = QLabel(f"Найдено конфликтов: {len(self.conflicts)}")
        layout.addWidget(info_label)
        
        # Таблица конфликтов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Термин", "Варианты перевода", "Выбор", "Свой вариант"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        
        # Заполняем таблицу
        self.table.setRowCount(len(self.conflicts))
        self.combo_boxes = {}
        self.custom_edits = {}
        
        for i, (term, translations) in enumerate(self.conflicts.items()):
            # Термин
            self.table.setItem(i, 0, QTableWidgetItem(term))
            
            # Варианты
            variants_text = " | ".join(translations)
            self.table.setItem(i, 1, QTableWidgetItem(variants_text))
            
            # ComboBox для выбора
            combo = QtWidgets.QComboBox()
            combo.addItems(translations)
            combo.addItem("[Свой вариант]")
            combo.currentIndexChanged.connect(lambda idx, t=term: self.on_combo_changed(t, idx))
            self.table.setCellWidget(i, 2, combo)
            self.combo_boxes[term] = combo
            
            # Поле для своего варианта
            edit = QtWidgets.QLineEdit()
            edit.setEnabled(False)
            self.table.setCellWidget(i, 3, edit)
            self.custom_edits[term] = edit
            
        layout.addWidget(self.table)
        
        # Обратные конфликты
        if self.reverse_conflicts:
            reverse_label = QLabel(f"\nВнимание! Найдены одинаковые переводы для разных терминов:")
            reverse_label.setStyleSheet("color: orange;")
            layout.addWidget(reverse_label)
            
            reverse_text = QTextEdit()
            reverse_text.setReadOnly(True)
            reverse_text.setMaximumHeight(100)
            
            text = ""
            for translation, terms in self.reverse_conflicts.items():
                text += f"'{translation}' используется для: {', '.join(terms)}\n"
            reverse_text.setPlainText(text)
            layout.addWidget(reverse_text)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def on_combo_changed(self, term, index):
        """Обработка изменения выбора"""
        combo = self.combo_boxes[term]
        edit = self.custom_edits[term]
        
        # Если выбран "Свой вариант"
        if combo.currentText() == "[Свой вариант]":
            edit.setEnabled(True)
            edit.setFocus()
        else:
            edit.setEnabled(False)
            edit.clear()
            
    def get_resolved_glossary(self):
        """Возвращает глоссарий с разрешенными конфликтами"""
        for term, combo in self.combo_boxes.items():
            if combo.currentText() == "[Свой вариант]":
                custom_value = self.custom_edits[term].text().strip()
                if custom_value:
                    self.resolved[term] = custom_value
                else:
                    self.resolved[term] = self.conflicts[term][0]  # По умолчанию первый вариант
            else:
                self.resolved[term] = combo.currentText()
                
        return self.resolved

class DynamicGlossaryFilter:
    """Фильтрует глоссарий, оставляя только термины, встречающиеся в тексте"""
    
    @staticmethod
    def filter_glossary_for_text(full_glossary, text, min_word_length=3):
        """
        Возвращает только те термины из глоссария, которые встречаются в тексте
        
        Args:
            full_glossary: полный словарь глоссария {оригинал: перевод}
            text: текст главы для анализа
            min_word_length: минимальная длина термина для поиска
        """
        if not full_glossary or not text:
            return {}
            
        filtered_glossary = {}
        text_lower = text.lower()
        
        for original, translation in full_glossary.items():
            # Пропускаем слишком короткие термины
            if len(original) < min_word_length:
                continue
                
            # Быстрая проверка наличия в тексте
            if original.lower() in text_lower:
                # Дополнительная проверка на границы слов для точности
                import re
                # Создаем паттерн для поиска целого слова
                pattern = r'\b' + re.escape(original) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    filtered_glossary[original] = translation
                    
        return filtered_glossary
    
    @staticmethod
    def count_term_occurrences(glossary, text_files):
        """
        Подсчитывает, в скольких файлах встречается каждый термин
        
        Args:
            glossary: словарь глоссария
            text_files: список текстов для анализа
            
        Returns:
            dict: {термин: количество_файлов}
        """
        term_counts = {term: 0 for term in glossary.keys()}
        
        for text in text_files:
            text_lower = text.lower()
            for term in glossary.keys():
                if term.lower() in text_lower:
                    import re
                    pattern = r'\b' + re.escape(term) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        term_counts[term] += 1
                        
        return term_counts
    
    @staticmethod
    def remove_rare_terms(glossary, term_counts, min_occurrences=2):
        """Удаляет термины, встречающиеся менее min_occurrences раз"""
        filtered_glossary = {}
        removed_count = 0
        
        for term, translation in glossary.items():
            if term_counts.get(term, 0) >= min_occurrences:
                filtered_glossary[term] = translation
            else:
                removed_count += 1
                
        return filtered_glossary, removed_count

class EpubHtmlSelectorDialog(QDialog):
    def __init__(self, epub_filename, html_files, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"Выберите HTML/XHTML файлы из '{os.path.basename(epub_filename)}'"
        )
        self.setMinimumWidth(600)  # Increased width for char count
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        self.info_label = QLabel(
            f"Найденные HTML/XHTML файлы в:\n{epub_filename}\n\nВыберите файлы для перевода (используйте Ctrl+Click или Shift+Click):"
        )
        layout.addWidget(self.info_label)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )

        try:
            sorted_html_files = sorted(html_files, key=extract_number_from_path)
        except Exception as sort_err:
            print(
                f"Warning: Could not numerically sort HTML files, using default order. Error: {sort_err}"
            )
            sorted_html_files = sorted(html_files)

        try:
            with zipfile.ZipFile(epub_filename, "r") as epub_zip:
                for i, file_path_in_epub in enumerate(sorted_html_files):
                    char_count_str = "N/A"
                    try:
                        html_bytes = epub_zip.read(file_path_in_epub)
                        html_content_str = ""
                        try:
                            html_content_str = html_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            try:
                                html_content_str = html_bytes.decode("cp1251")
                            except UnicodeDecodeError:
                                html_content_str = html_bytes.decode(
                                    "latin-1", errors="ignore"
                                )
                        char_count_str = str(len(html_content_str))
                    except Exception as e_read:
                        # This print is for dev/debug, won't be visible to most users
                        print(
                            f"Warning: Could not read/decode '{file_path_in_epub}' from EPUB to get char count: {e_read}"
                        )

                    display_text = (
                        f"{i+1}. {file_path_in_epub} ({char_count_str} симв.)"
                    )
                    item = QListWidgetItem(display_text)
                    item.setData(
                        QtCore.Qt.ItemDataRole.UserRole, file_path_in_epub
                    )  # Store clean path
                    self.list_widget.addItem(item)
        except (zipfile.BadZipFile, FileNotFoundError, Exception) as e_zip:
            self.info_label.setText(
                f"Ошибка чтения EPUB файла '{os.path.basename(epub_filename)}': {e_zip}\nФайлы будут показаны без информации о размере."
            )
            for i, file_path_in_epub in enumerate(
                sorted_html_files
            ):  # Fallback: add items without char count
                display_text = f"{i+1}. {file_path_in_epub} (N/A симв.)"
                item = QListWidgetItem(display_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path_in_epub)
                self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        common_content_indicators = [
            "chapter",
            "part",
            "section",
            "content",
            "text",
            "page",
        ]
        skip_indicators = [
            "toc",
            "nav",
            "cover",
            "title",
            "index",
            "opf",
            "ncx",
            "css",
            "stylesheet",
        ]

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            file_path_in_epub = item.data(
                QtCore.Qt.ItemDataRole.UserRole
            )  # Get clean path

            if not file_path_in_epub:  # Fallback if UserRole data is missing
                item_text_display = item.text()
                # Try to extract path from display text (less reliable)
                match = re.match(r"^\d+\.\s*([^ (]+)", item_text_display)
                if match:
                    file_path_in_epub = match.group(1).strip()
                else:  # If still no path, skip auto-selection for this item
                    continue

            item_text_lower = file_path_in_epub.lower()
            file_base_name = os.path.basename(item_text_lower)

            contains_number = bool(re.search(r"\d", file_base_name))
            contains_content_word = any(
                indicator in file_base_name for indicator in common_content_indicators
            )
            contains_skip_word = any(
                skip_indicator in file_base_name for skip_indicator in skip_indicators
            )

            if (contains_number or contains_content_word) and not contains_skip_word:
                item.setSelected(True)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_selected_files(self):
        selected_items = self.list_widget.selectedItems()
        # Return clean paths stored in UserRole
        return [
            item.data(QtCore.Qt.ItemDataRole.UserRole)
            for item in selected_items
            if item.data(QtCore.Qt.ItemDataRole.UserRole)
        ]


class OperationCancelledError(Exception):
    """Custom exception for handling user cancellation."""

    pass

class RateLimitExceededError(Exception):
    """Исключение для обработки превышения лимита API"""
    def __init__(self, message, file_info=None):
        super().__init__(message)
        self.file_info = file_info

class Worker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)
    log_message = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(int, int, list, bool, object)

    # <<< ИЗМЕНЕНО: Обновлен конструктор для приема нового флага
    def __init__(
        self,
        api_key_manager,
        out_folder,
        prompt_template,
        files_to_process,
        model_config,
        max_concurrent_requests,
        chunking_enabled_override,
        temperature,
        post_delay_enabled,
        use_system_instruction,
        context_manager
    ):
        super().__init__()
        self.api_key_manager = api_key_manager
        self.out_folder = out_folder
        self.prompt_template = prompt_template
        self.files_to_process = files_to_process
        self.model_config = model_config
        self.max_concurrent_requests = max_concurrent_requests
        self.chunking_enabled_override = chunking_enabled_override
        self.temperature = temperature
        self.post_delay_enabled = post_delay_enabled
        self.use_system_instruction = use_system_instruction
        self.context_manager = context_manager
        self.is_cancelled = False
        self.model = None
        self.executor = None
        self.error_analyzer = ErrorAnalyzer()
        self.content_filter_handler = ContentFilterHandler(api_key_manager, context_manager)
        self.progress_monitor = TranslationProgressMonitor(out_folder)
    
        # === НОВОЕ: Отслеживание времени последнего запроса для контроля RPM ===
        self.last_request_time = 0
        self.request_count_in_minute = 0
        self.minute_start_time = time.time()

    # <<< ИЗМЕНЕНО: Полностью переработанный метод для поддержки двух режимов
    def clean_html_response(self, html_content, is_html=False): # <<< ИЗМЕНЕНО: Добавлен аргумент is_html
        """
        Очищает HTML контент от markdown code blocks обозначений и других артефактов.
        Удаляет ```html, ```xml, ```xhtml, ``` в начале и конце, а также другие паттерны.
        Эта версия нечувствительна к регистру и работает в цикле для удаления вложенных/повторяющихся маркеров.
        """
        if not html_content or not isinstance(html_content, str):
            return ""  # Возвращаем пустую строку для безопасности

        cleaned = html_content.strip()

        # Список возможных начальных маркеров (для проверки в нижнем регистре)
        start_markers = [
            "```html",
            "```xml",

            "```xhtml",
            "```"
        ]
        
        # Используем цикл, чтобы удалять маркеры, пока они находятся
        something_was_cleaned = True
        while something_was_cleaned:
            something_was_cleaned = False
            
            # Проверяем и удаляем начальные маркеры
            for marker in start_markers:
                if cleaned.lower().startswith(marker):
                    # Нашли маркер, отрезаем его
                    cleaned = cleaned[len(marker):].strip()
                    something_was_cleaned = True
                    break # Начинаем проверку заново с начала списка маркеров
            
            if something_was_cleaned:
                continue # Если что-то удалили, повторяем главный цикл

            # Проверяем и удаляем конечные маркеры (только если в начале ничего не нашли)
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
                something_was_cleaned = True

        # Полезная проверка для отладки: если после очистки не осталось HTML-тегов, сообщим об этом
        # <<< ИСПРАВЛЕНО: Теперь 'is_html' является известной переменной
        if cleaned and is_html and not ("<" in cleaned and ">" in cleaned):
            self.log_message.emit(f"ВНИМАНИЕ: Очищенный контент, похоже, не содержит HTML тегов. Результат может быть некорректным.")

        return cleaned
   
    def _enforce_rpm_limit(self):
        """Обеспечивает соблюдение лимита RPM с адаптивными задержками"""
        rpm_limit = self.model_config.get("rpm")
        if not rpm_limit:
            return
    
        current_time = time.time()
    
        # Используем информацию из трекера если доступна
        if hasattr(self, 'rate_limit_tracker') and hasattr(self, 'current_api_key'):
            should_wait, wait_time = self.rate_limit_tracker.should_wait(self.current_api_key)
            if should_wait:
                self.log_message.emit(f"[SMART RPM] Ожидание {wait_time:.1f} сек на основе заголовков API")
                time.sleep(wait_time)
                return
    
        # Стандартная логика RPM контроля
        # Сбрасываем счетчик если прошла минута
        if current_time - self.minute_start_time >= 60:
            self.request_count_in_minute = 0
            self.minute_start_time = current_time
    
        # Проверяем, не превысили ли мы лимит
        if self.request_count_in_minute >= rpm_limit:
            wait_time = 60 - (current_time - self.minute_start_time) + 1
            if wait_time > 0:
                self.log_message.emit(f"[RPM LIMIT] Достигнут лимит {rpm_limit} запросов/мин. Ожидание {wait_time:.1f} сек...")
                time.sleep(wait_time)
                self.request_count_in_minute = 0
                self.minute_start_time = time.time()
    
        # Добавляем минимальную задержку между запросами
        min_delay = 60.0 / rpm_limit
        time_since_last = time.time() - self.last_request_time
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            if sleep_time > 0:
                time.sleep(sleep_time)
    
        self.request_count_in_minute += 1
        self.last_request_time = time.time()
   
    def setup_client(self):
        """Настраивает API-клиент и модель"""
        try:
            # Получаем доступный API ключ
            current_key = self.api_key_manager.get_next_available_key()
            if not current_key:
                self.log_message.emit("[ERROR] Все API ключи исчерпаны или достигли лимита")
                return False
    
            self.current_api_key = current_key  # Сохраняем для пометки как исчерпанного

            self.log_message.emit(f"Используется ключ: ...{current_key[-4:]}")
            self.log_message.emit(f"Статус ключей: {self.api_key_manager.get_usage_report()}")
    
            # Конфигурируем библиотеку genai с полученным ключом
            genai.configure(api_key=current_key)

            # === НОВОЕ: Проверяем настройки динамического глоссария ===
            if hasattr(self.context_manager, 'use_dynamic_glossary') and self.context_manager.use_dynamic_glossary:
                self.log_message.emit("[INFO] Динамический глоссарий: ВКЛЮЧЕН")
                self.log_message.emit(f"[INFO] Минимальная длина термина: {self.context_manager.min_term_length} символов")
            else:
                self.log_message.emit("[INFO] Динамический глоссарий: ВЫКЛЮЧЕН (используется полный)")

            # Формирование базовой инструкции
            base_instruction_template = self.prompt_template

            # Настройка модели в зависимости от выбранного режима
            if self.use_system_instruction:
                # РЕЖИМ: СИСТЕМНЫЕ ИНСТРУКЦИИ
                base_instruction = base_instruction_template.replace("{text}", "").strip()
            
                # Для динамического глоссария НЕ включаем глоссарий в системную инструкцию
                if self.context_manager.use_dynamic_glossary:
                    # Системная инструкция без глоссария
                    final_system_instruction = base_instruction
                    self.log_message.emit("Режим: Системные инструкции с динамическим глоссарием (экономия токенов)")
                else:
                    # Включаем полный глоссарий в системную инструкцию
                    glossary_prompt_part = self.context_manager.format_glossary_for_prompt()
                    final_system_instruction = f"""{base_instruction}

    ---
    ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ (ОБЯЗАТЕЛЕН К ИСПОЛНЕНИЮ):
    {glossary_prompt_part}
    ---
    """
                    self.log_message.emit("Режим: Системные инструкции со статическим глоссарием")
            
                # Инициализируем модель
                self.model = genai.GenerativeModel(
                    self.model_config["id"],
                    system_instruction=final_system_instruction
                )
                self.log_message.emit(f"Длина системной инструкции: {len(final_system_instruction)} симв.")

            else:
                # РЕЖИМ: КЛАССИЧЕСКИЙ (промпт в каждом запросе)
                # Сохраняем базовый шаблон для последующего использования
                self.base_prompt_template = base_instruction_template
            
                if not self.context_manager.use_dynamic_glossary:
                    # Статический глоссарий - добавляем его один раз к шаблону
                    glossary_prompt_part = self.context_manager.format_glossary_for_prompt()
                    self.full_prompt_template_with_context = f"""{base_instruction_template}

    ---
    ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ (ОБЯЗАТЕЛЕН К ИСПОЛНЕНИЮ):
    {glossary_prompt_part}
    ---
    """
                # Для динамического глоссария будем формировать промпт для каждого чанка отдельно
            
                # Инициализируем модель без системной инструкции
                self.model = genai.GenerativeModel(self.model_config["id"])
                self.log_message.emit("Режим: Классический (промпт в каждом запросе)")

            # Логирование остальных параметров сессии
            self.log_message.emit(f"Используется модель: {self.model_config['id']}")
            self.log_message.emit(f"Температура: {self.temperature}")
            self.log_message.emit(f"Параллельные запросы (макс): {self.max_concurrent_requests}")
            self.log_message.emit(f"Таймаут API: {API_TIMEOUT_SECONDS} сек.")
            self.log_message.emit(f"Макс. ретраев при 429/503/504: {MAX_RETRIES}")
    
            if self.model_config.get("post_request_delay", 0) > 0:
                delay_status = "ВКЛЮЧЕНА" if self.post_delay_enabled else "ОТКЛЮЧЕНА (GUI)"
                self.log_message.emit(
                    f"Доп. задержка после запроса: {self.model_config['post_request_delay']} сек. ({delay_status})"
                )

            model_needs_chunking = self.model_config.get("needs_chunking", False)
            actual_chunking_behavior = "ВКЛЮЧЕН" if self.chunking_enabled_override else "ОТКЛЮЧЕН (GUI)"
            self.log_message.emit(f"Чанкинг: {actual_chunking_behavior}")

            self.log_message.emit("Клиент Gemini API успешно настроен.")
            return True

        except Exception as e:
            self.log_message.emit(f"[ERROR] Ошибка настройки клиента Gemini API: {e}")
            self.log_message.emit(f"Traceback:\n{traceback.format_exc()}")
            return False

    def _generate_content_with_retry(self, prompt_for_api, context_log_prefix="API Call"):
        """Генерирует контент с повторными попытками при ошибках"""
        retries = 0
        last_error = None

        safety_settings = [
            {"category": c, "threshold": "BLOCK_NONE"}
            for c in [
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_HATE_SPEECH", 
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "HARM_CATEGORY_DANGEROUS_CONTENT",
            ]
        ]
        request_options = {"timeout": API_TIMEOUT_SECONDS}
        generation_config = genai_types.GenerationConfig(temperature=self.temperature)

        while retries <= MAX_RETRIES:
            if self.is_cancelled:
                raise OperationCancelledError(f"Отменено ({context_log_prefix})")

            try:
                response = self.model.generate_content(
                    contents=prompt_for_api,
                    safety_settings=safety_settings,
                    generation_config=generation_config,
                    request_options=request_options,
                )
                
                # Пытаемся получить заголовки ответа (если доступны)
                if hasattr(response, '_response') and hasattr(response._response, 'headers'):
                    headers = response._response.headers
    
                    # Создаем трекер если его нет
                    if not hasattr(self, 'rate_limit_tracker'):
                        self.rate_limit_tracker = RateLimitTracker()
    
                    # Обновляем информацию о лимитах
                    if hasattr(self, 'current_api_key'):
                        self.rate_limit_tracker.update_from_headers(self.current_api_key, headers)
        
                        # Логируем статус
                        status = self.rate_limit_tracker.get_status(self.current_api_key)
                        self.log_message.emit(f"[RATE LIMIT STATUS] {status}")
        
                        # Проверяем, нужно ли ждать
                        should_wait, wait_time = self.rate_limit_tracker.should_wait(self.current_api_key)
                        if should_wait and wait_time > 0:
                            self.log_message.emit(f"[RATE LIMIT] Осталось мало запросов, ожидание {wait_time:.1f} сек до сброса лимита")
                            time.sleep(wait_time)
            
                # === НОВОЕ: Проверяем finish_reason перед доступом к тексту ===
                if response.candidates:
                    candidate = response.candidates[0]
                
                    # Проверяем finish_reason
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = candidate.finish_reason
                    
                        # finish_reason = 3 (SAFETY) - контент заблокирован
                        if finish_reason == 3:
                            error_msg = "Content blocked by safety filters (SAFETY finish_reason)"
                            self.log_message.emit(f"[SAFETY BLOCK] {context_log_prefix}: {error_msg}")
                        
                            # Применяем задержку
                            delay = self.model_config.get("post_request_delay", 60)
                            if self.model_config.get("rpm", 0) <= 5:
                                delay = max(delay, 60)
                            
                            self.log_message.emit(f"[INFO] {context_log_prefix}: Задержка {delay} сек после блокировки безопасности")
                            time.sleep(delay)
                        
                            raise genai_types.BlockedPromptException(error_msg)
                    
                        # finish_reason = 4 (RECITATION) - обнаружен плагиат
                        elif finish_reason == 4:
                            error_msg = "Content blocked due to recitation (copyright)"
                            self.log_message.emit(f"[RECITATION BLOCK] {context_log_prefix}: {error_msg}")
                        
                            delay = self.model_config.get("post_request_delay", 60)
                            if self.model_config.get("rpm", 0) <= 5:
                                delay = max(delay, 60)
                            
                            time.sleep(delay)
                            raise genai_types.BlockedPromptException(error_msg)
                        
                        # finish_reason = 5 (LANGUAGE) - неподдерживаемый язык
                        elif finish_reason == 5:
                            error_msg = "Unsupported language detected"
                            self.log_message.emit(f"[LANGUAGE BLOCK] {context_log_prefix}: {error_msg}")
                        
                            delay = 30
                            time.sleep(delay)
                            raise genai_types.BlockedPromptException(error_msg)
            
                # Пытаемся получить текст
                try:
                    translated_text = response.text
                except Exception as text_error:
                    # === ОБРАБОТКА ОШИБКИ "response.text requires valid Part" ===
                    error_str = str(text_error).lower()

                    if "finish_reason" in error_str and "is 1" in error_str:
                        # finish_reason = 1 (STOP) но нет текста - это блокировка
                        self.log_message.emit(f"[CONTENT BLOCK] {context_log_prefix}: Модель остановилась без генерации (возможная блокировка)")
    
                        # Применяем уменьшенную задержку
                        delay = 60  # Уменьшаем задержку до 30 секунд
                        self.log_message.emit(f"[INFO] {context_log_prefix}: Задержка {delay} сек после пустого ответа")
                        time.sleep(delay)
    
                        raise genai_types.StopCandidateException(f"Model stopped without content (likely blocked)")
    
                    elif "response.parts" in error_str or "response.text" in error_str:
                        # Другие проблемы с частями ответа
                        self.log_message.emit(f"[INVALID RESPONSE] {context_log_prefix}: Некорректный ответ от модели")
    
                        delay = 30  # Уменьшаем задержку
                        self.log_message.emit(f"[INFO] {context_log_prefix}: Задержка {delay} сек после некорректного ответа")
                        time.sleep(delay)
    
                        raise genai_types.StopCandidateException(f"Invalid response structure: {text_error}")
                    else:
                        # Неизвестная ошибка при получении текста
                        raise text_error

                # Применяем стандартную задержку после успешного запроса
                delay_needed = self.model_config.get("post_request_delay", 0)
                if delay_needed > 0 and self.post_delay_enabled:
                    self.log_message.emit(
                        f"[INFO] {context_log_prefix}: Применяем задержку {delay_needed} сек..."
                    )
                    time.sleep(delay_needed)

                return translated_text

            except (
                genai_types.BlockedPromptException,
                genai_types.StopCandidateException,
            ) as content_error:
                # Эти исключения уже обработаны выше с задержками
                raise content_error

            except google_exceptions.ResourceExhausted as e:
                error_msg = str(e).lower()
            
                # Различаем превышение квоты и RPM limit
                if "exceeded your current quota" in error_msg or "check your plan and billing" in error_msg:
                    # Это превышение дневной квоты - нужно менять ключ
                    self.log_message.emit(f"[QUOTA EXCEEDED] {context_log_prefix}: Превышена дневная квота текущего ключа.")
                
                    # Помечаем ключ как исчерпанный
                    if hasattr(self, 'current_api_key') and self.current_api_key:
                        self.api_key_manager.mark_key_exhausted(self.current_api_key)
                
                    # Бросаем специальное исключение для смены ключа
                    raise RateLimitExceededError(f"Quota exceeded: {e}", None)
            
                else:
                    # Это обычный RPM limit - ждем и повторяем с тем же ключом
                    last_error = e
                    current_retry_attempt = retries + 1
                
                    if current_retry_attempt > MAX_RETRIES:
                        self.log_message.emit(
                            f"[FAIL] {context_log_prefix}: Rate limit RPM, исчерпаны попытки ({MAX_RETRIES}). {e}"
                        )
                        raise e
                    else:
                        # Для RPM limit используем большую задержку
                        delay = 65  # Чуть больше минуты для гарантии сброса счетчика RPM
                        self.log_message.emit(
                            f"[WARN] {context_log_prefix}: Rate limit RPM (НЕ квота). Задержка {delay} сек. Попытка {current_retry_attempt}/{MAX_RETRIES}..."
                        )
                        time.sleep(delay)
                        retries += 1
                        continue
                
            except (
                google_exceptions.DeadlineExceeded,
                google_exceptions.ServiceUnavailable,
                google_exceptions.InternalServerError,
            ) as e:
                # Обработка ошибок 500/503/504 с обязательной задержкой
                error_code = (
                    "503 Unavailable"
                    if isinstance(e, google_exceptions.ServiceUnavailable)
                    else (
                        "500 Internal"
                        if isinstance(e, google_exceptions.InternalServerError)
                        else "504 Timeout"
                    )
                )
            
                # ОБЯЗАТЕЛЬНАЯ задержка после ошибок 500/503/504 для защиты RPM
                error_delay = 60  # Стандартная задержка 60 секунд
            
                if self.model_config.get("rpm", 0) <= 5:
                    error_delay = 60  # Минимум минута для Gemini 2.5 Pro (5 RPM)
                elif self.model_config.get("rpm", 0) <= 10:
                    error_delay = 30  # 30 секунд для моделей с RPM <= 10
                else:
                    error_delay = 15  # 15 секунд для быстрых моделей
            
                self.log_message.emit(
                    f"[ERROR] {context_log_prefix}: Ошибка {error_code}. Применяем задержку {error_delay} сек для защиты RPM..."
                )
                time.sleep(error_delay)
            
                # Для моделей с низким RPM НЕ делаем повтор
                if self.model_config.get("rpm", 0) <= 5:
                    self.log_message.emit(
                        f"[FAIL] {context_log_prefix}: Ошибка {error_code}. Повтор отключен для моделей с низким RPM."
                    )
                    raise e  # Бросаем исключение после задержки
            
                # Для других моделей - логика с повторами (если разрешено)
                last_error = e
                current_retry_attempt = retries + 1
            
                if current_retry_attempt > MAX_RETRIES:
                    self.log_message.emit(
                        f"[FAIL] {context_log_prefix}: Ошибка {error_code}, исчерпаны попытки ({MAX_RETRIES}). {e}"
                    )
                    raise e
                else:
                    # Дополнительная задержка перед повтором
                    additional_delay = 30
                    self.log_message.emit(
                        f"[WARN] {context_log_prefix}: Попытка {current_retry_attempt}/{MAX_RETRIES} через {additional_delay} сек..."
                    )
                    time.sleep(additional_delay)
                    retries += 1
                    continue
                
            except Exception as e:
                # Обработка всех остальных ошибок
                error_str = str(e).lower()
            
                # === ОБРАБОТКА СПЕЦИФИЧНОЙ ОШИБКИ "response.text requires valid Part" ===
                if ("response.text" in error_str or "response.parts" in error_str) and ("finish_reason" in error_str or "candidate" in error_str):
                    self.log_message.emit(f"[RESPONSE ERROR] {context_log_prefix}: Проблема со структурой ответа модели")
                
                    # Применяем задержку
                    delay = self.model_config.get("post_request_delay", 60)
                    if self.model_config.get("rpm", 0) <= 5:
                        delay = max(delay, 60)
                    
                    self.log_message.emit(f"[INFO] {context_log_prefix}: Задержка {delay} сек после ошибки ответа")
                    time.sleep(delay)
                
                    # Обрабатываем как блокировку контента
                    raise genai_types.StopCandidateException(f"Response structure error: {e}")
                
                # Для любых других ошибок при низком RPM - защитная задержка
                elif self.model_config.get("rpm", 0) <= 5:
                    safety_delay = 30  # Уменьшаем с 60 до 30 секунд
                    self.log_message.emit(
                        f"[INFO] {context_log_prefix}: Применяем защитную задержку {safety_delay} сек после ошибки (низкий RPM)"
                    )
                    time.sleep(safety_delay)
            
                self.log_message.emit(f"[CALL ERROR] {context_log_prefix}: Неожиданная ошибка: {e}")
                raise e
        
        raise last_error if last_error else RuntimeError("Неизвестная ошибка API после ретраев.")

    # <<< ИЗМЕНЕНО: Добавлена логика для выбора данных для API на основе флага
    def process_single_chunk(self, chunk_text, base_filename, chunk_index, total_chunks, is_html=False):
        """Обрабатывает один чанк текста"""
        if self.is_cancelled:
            raise OperationCancelledError(f"Отменено перед обработкой чанка {chunk_index+1}/{total_chunks}")

        chunk_log_prefix = f"{base_filename} [Chunk {chunk_index+1}/{total_chunks}]"
    
        # Упрощенный лог
        self.log_message.emit(f"[PROCESSING] {chunk_log_prefix}")

        prompt_for_api = ""
    
        if self.use_system_instruction:
            # Режим системных инструкций
            if self.context_manager.use_dynamic_glossary:
                # Динамический глоссарий - добавляем его к каждому чанку
                dynamic_glossary_text = self.context_manager.format_glossary_for_prompt(chunk_text)
                # Формируем промпт: сначала динамический глоссарий, потом текст
                prompt_for_api = f"""{dynamic_glossary_text}

    ТЕКСТ ДЛЯ ПЕРЕВОДА:
    {chunk_text}"""
            else:
                # Статический глоссарий уже в системной инструкции
                prompt_for_api = chunk_text
            
        else:
            # Классический режим
            if self.context_manager.use_dynamic_glossary:
                # Формируем промпт с динамическим глоссарием для этого чанка
                dynamic_glossary_text = self.context_manager.format_glossary_for_prompt(chunk_text)
                # Вставляем текст в базовый шаблон
                prompt_with_text = self.base_prompt_template.replace("{text}", chunk_text)
                # Добавляем динамический глоссарий
                prompt_for_api = f"""{prompt_with_text}

    ---
    ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ (ОБЯЗАТЕЛЕН К ИСПОЛНЕНИЮ):
    {dynamic_glossary_text}
    ---
    """
            else:
                # Используем заранее подготовленный полный промпт со статическим глоссарием
                prompt_for_api = self.full_prompt_template_with_context.replace("{text}", chunk_text)

        try:
            # === НОВОЕ: Контроль RPM перед запросом ===
            self._enforce_rpm_limit()
    
            raw_translated_chunk = self._generate_content_with_retry(prompt_for_api, chunk_log_prefix)

            if is_html:
                cleaned_chunk = self.clean_html_response(raw_translated_chunk, is_html=True)
                if len(cleaned_chunk) < len(raw_translated_chunk):
                    self.log_message.emit(f"[INFO] {chunk_log_prefix}: Ответ API был очищен от артефактов.")
            else:
                cleaned_chunk = raw_translated_chunk.strip()

            self.log_message.emit(f"[INFO] {chunk_log_prefix}: Чанк успешно переведен и обработан.")
            return chunk_index, cleaned_chunk

        except RateLimitExceededError as rle:
            # Пробрасываем наверх для обработки
            self.log_message.emit(f"[QUOTA] {chunk_log_prefix}: Превышена квота, требуется смена ключа.")
            raise rle
        except OperationCancelledError as oce:
            self.log_message.emit(f"[CANCELLED] {chunk_log_prefix}: Отменен во время API вызова.")
            raise oce
        except Exception as e:
            self.log_message.emit(f"[FAIL] {chunk_log_prefix}: Ошибка API вызова чанка: {e}")
            raise RuntimeError(f"Ошибка обработки чанка {chunk_index+1}: {e}") from e


    def process_single_file(self, file_info_tuple):
        """Обрабатывает только EPUB/HTML файлы"""
        file_type, path1, path2 = file_info_tuple
    
        # Проверяем, что это EPUB (единственный поддерживаемый тип)
        if file_type != "epub":
            return file_info_tuple, False, f"Неподдерживаемый тип файла: {file_type}"
    
        is_html_from_epub = True
        epub_base_name = os.path.splitext(os.path.basename(path1))[0]
        html_file_name = os.path.splitext(os.path.basename(path2))[0]
        safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
        src_display_path = f"{os.path.basename(path1)} -> {path2}"
        base_name_for_log = src_display_path
        out_path = os.path.join(
            self.out_folder, f"{epub_base_name}_{safe_html_name}_translated.html"
        )

        if self.is_cancelled:
            return (
                file_info_tuple,
                False,
                f"Отменено пользователем перед началом обработки файла: {base_name_for_log}",
            )

        log_prefix = base_name_for_log
        file_size_bytes = 0
        original_content = ""

        try:
            # Обработка EPUB/HTML
            if not BS4_AVAILABLE:
                return (
                    file_info_tuple,
                    False,
                    "Пропущено: EPUB/HTML обработка недоступна (нет beautifulsoup4)",
                )
            
            try:
                self.log_message.emit(f"Обработка EPUB/HTML: {log_prefix}")
                #self.log_message.emit(f"[INFO] {log_prefix}: Чтение HTML из EPUB...")
            
                # Анализ ошибок с помощью ErrorAnalyzer
                if hasattr(self, 'error_analyzer'):
                    self.progress_monitor.update_progress(chars_processed=0)
            
                with zipfile.ZipFile(path1, "r") as epub_zip:
                    try:
                        html_bytes = epub_zip.read(path2)
                        file_size_bytes = len(html_bytes)
                        original_content = html_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        self.log_message.emit(
                            f"[WARN] {log_prefix}: Ошибка UTF-8 декодирования, пробую cp1251..."
                        )
                        try:
                            original_content = html_bytes.decode("cp1251")
                        except UnicodeDecodeError:
                            self.log_message.emit(
                                f"[WARN] {log_prefix}: Ошибка cp1251 декодирования, пробую latin-1 с игнорированием ошибок..."
                            )
                            original_content = html_bytes.decode(
                                "latin-1", errors="ignore"
                            )
                    except Exception as zip_read_err:
                        raise RuntimeError(
                            f"Ошибка чтения файла '{path2}' из EPUB: {zip_read_err}"
                        ) from zip_read_err
                    
                #self.log_message.emit(
                #    f"[INFO] {log_prefix}: HTML прочитан (размер: {format_size(file_size_bytes)}, {len(original_content)} симв.)."
                #)
            
                # Обновляем прогресс
                if hasattr(self, 'progress_monitor'):
                    self.progress_monitor.update_progress(chars_processed=len(original_content))
            
                if not (
                    "<html" in original_content.lower()
                    and "</html>" in original_content.lower()
                ):
                    self.log_message.emit(
                        f"[WARN] {log_prefix}: Файл не выглядит как полный HTML документ."
                    )
                
            except zipfile.BadZipFile:
                error_msg = f"Ошибка: Некорректный EPUB (ZIP) файл: {os.path.basename(path1)}"
                if hasattr(self, 'error_analyzer'):
                    error_analysis = self.error_analyzer.analyze_error(None, error_msg)
                    self.progress_monitor.log_error(error_analysis['type'], error_msg)
                return file_info_tuple, False, error_msg
            
            except KeyError:
                error_msg = f"Ошибка: HTML файл '{path2}' не найден в EPUB '{os.path.basename(path1)}'"
                if hasattr(self, 'error_analyzer'):
                    error_analysis = self.error_analyzer.analyze_error(None, error_msg)
                    self.progress_monitor.log_error(error_analysis['type'], error_msg)
                return file_info_tuple, False, error_msg
            
            except Exception as read_err:
                error_msg = f"Ошибка чтения EPUB/HTML: {read_err}"
                if hasattr(self, 'error_analyzer'):
                    error_analysis = self.error_analyzer.analyze_error(read_err, error_msg)
                    self.progress_monitor.log_error(error_analysis['type'], error_msg)
                return file_info_tuple, False, error_msg

            if not original_content.strip():
                self.log_message.emit(f"[INFO] {log_prefix}: Пропущен (пустой контент).")
                open(out_path, "w").close()
                return file_info_tuple, True, "Пропущен (пустой контент)"

            # Чанкинг
            chunks = []
            content_length = len(original_content)
            needs_chunking_check = self.model_config.get("needs_chunking", False)
            should_attempt_chunking = self.chunking_enabled_override and (
                needs_chunking_check or content_length > CHARACTER_LIMIT_FOR_CHUNK
            )
            is_html_type = True
            apply_chunking = False

            if should_attempt_chunking:
                if not CHUNK_HTML_SOURCE:
                    # Закомментировано для уменьшения логов
                    # self.log_message.emit(f"[INFO] {log_prefix}: Чанкинг HTML отключен (CHUNK_HTML_SOURCE=False). Отправка целиком.")
                    chunks.append(original_content)
                elif content_length > CHARACTER_LIMIT_FOR_CHUNK:
                    self.log_message.emit(f"[INFO] {log_prefix}: Контент превышает лимит, разделяем на чанки...")
                    chunks = split_text_into_chunks(
                        original_content,
                        CHUNK_TARGET_SIZE,
                        CHUNK_SEARCH_WINDOW,
                        MIN_CHUNK_SIZE,
                    )
                    self.log_message.emit(f"[INFO] {log_prefix}: Разделено на {len(chunks)} чанков.")
                    if not chunks:
                        return file_info_tuple, False, "Ошибка разделения на чанки"
                    apply_chunking = True
                else:
                    # Закомментировано для уменьшения логов
                    # self.log_message.emit(
                    #     f"[INFO] {log_prefix}: Чанкинг включен, но контент ({content_length} симв.) в пределах лимита. Отправка целиком."
                    # )
                    chunks.append(original_content)
            else:
                chunks.append(original_content)
                if content_length > CHARACTER_LIMIT_FOR_CHUNK:
                    reason = (
                        "отключен в GUI"
                        if not self.chunking_enabled_override
                        else "модель не требует и лимит не превышен"
                    )
                    if not CHUNK_HTML_SOURCE and self.chunking_enabled_override:
                        reason = "отключен для HTML"
                    # Закомментировано для уменьшения логов
                    # self.log_message.emit(
                    #     f"[WARN] {log_prefix}: Контент ({content_length} симв.) большой, но чанкинг не применяется ({reason}). Отправка целиком..."
                    # )
                # else:
                    # self.log_message.emit(f"[INFO] {log_prefix}: Чанкинг не требуется.")

            translated_chunks_map = {}
            total_chunks = len(chunks)
            chunk_futures = {}

            if total_chunks == 0:
                self.log_message.emit(
                    f"[ERROR] {log_prefix}: Нет чанков для обработки после разделения."
                )
                return (
                    file_info_tuple,
                    False,
                    "Ошибка: не найдено контента для обработки после разделения.",
                )

            # Обработка чанков
            if total_chunks == 1:
                try:
                    chunk_index, translated_text = self.process_single_chunk(
                        chunks[0], log_prefix, 0, 1, is_html_type
                    )
                    translated_chunks_map[chunk_index] = translated_text
                except RateLimitExceededError as rle:
                    # Пробрасываем наверх с информацией о файле
                    rle.file_info = file_info_tuple
                    raise rle
                except OperationCancelledError as oce:
                    raise oce
                except Exception as e:
                    error_msg = f"Ошибка обработки единственного чанка: {e}"
                    self.log_message.emit(f"[FAIL] {log_prefix}: {error_msg}")
    
                    # Проверяем тип ошибки
                    error_str = str(e)
    
                    # 1. Проверка на превышение квоты (требует смены ключа)
                    if "exceeded your current quota" in error_str.lower():
                        raise RateLimitExceededError(error_str, file_info_tuple)
    
                    # 2. Проверка на блокировку контента (НЕ требует смены ключа)
                    content_filter_indicators = [
                        'PROHIBITED_CONTENT',
                        'block_reason',
                        'blocked prompt',
                        'BlockedPromptException',
                        'StopCandidateException'
                    ]
    
                    is_content_filtered = any(indicator.lower() in error_str.lower() 
                                              for indicator in content_filter_indicators)
    
                    if is_content_filtered:
                        self.log_message.emit(f"[CONTENT FILTER] {log_prefix}: Контент заблокирован фильтрами безопасности")
        
                        # Сохраняем главу для обработки через OpenRouter
                        if hasattr(self, 'content_filter_handler') and self.content_filter_handler:
                            self.content_filter_handler.add_filtered_chapter(file_info_tuple, chunks[0])
                            self.log_message.emit(f"[INFO] {log_prefix}: Глава сохранена для обработки через OpenRouter")
        
                        # Возвращаем с пометкой о фильтре
                        return file_info_tuple, False, f"CONTENT_FILTER: {error_msg}"
    
                    # 3. Другие ошибки
                    if hasattr(self, 'error_analyzer'):
                        error_analysis = self.error_analyzer.analyze_error(e, str(e))
                        self.progress_monitor.log_error(error_analysis['type'], error_msg)
    
                    return file_info_tuple, False, error_msg
            else:
                self.log_message.emit(
                    f"[INFO] {log_prefix}: Отправка {total_chunks} чанков на обработку (параллельно до {self.max_concurrent_requests})..."
                )
                for i, chunk_text in enumerate(chunks):
                    if self.is_cancelled:
                        raise OperationCancelledError(
                            f"Отменено перед отправкой чанка {i+1}/{total_chunks}"
                        )
                    future = self.executor.submit(
                        self.process_single_chunk,
                        chunk_text,
                        log_prefix,
                        i,
                        total_chunks,
                        is_html_type,
                    )
                    chunk_futures[future] = i

                chunks_processed_count = 0
                for future in as_completed(chunk_futures):
                    if self.is_cancelled:
                        for f_cancel in chunk_futures:
                            if not f_cancel.done():
                                try:
                                    f_cancel.cancel()
                                except Exception:
                                    pass
                        raise OperationCancelledError(
                            f"Отменено во время ожидания завершения чанков для {log_prefix}"
                        )

                    chunk_index = chunk_futures[future]
                    try:
                        _, translated_text = future.result()
                        translated_chunks_map[chunk_index] = translated_text
                        chunks_processed_count += 1
                    except (OperationCancelledError, CancelledError) as cancel_err:
                        self.log_message.emit(
                            f"[CANCELLED] {log_prefix} [Chunk {chunk_index+1}/{total_chunks}]: Обработка чанка отменена ({type(cancel_err).__name__})."
                        )
                        raise OperationCancelledError(
                            f"Отменен чанк {chunk_index+1}"
                        ) from cancel_err
                    except Exception as e:
                        error_msg = f"Критическая ошибка при получении результата чанка {chunk_index+1}: {e}"
                        self.log_message.emit(f"[FAIL] {log_prefix}: {error_msg}")
                    
                        # Анализируем ошибку
                        if hasattr(self, 'error_analyzer'):
                            error_analysis = self.error_analyzer.analyze_error(e, str(e))
                            self.progress_monitor.log_error(error_analysis['type'], error_msg)
                        
                            # Если контент заблокирован фильтрами
                            if error_analysis['type'] == 'CONTENT_FILTER' and hasattr(self, 'content_filter_handler'):
                                if chunk_index < len(chunks):
                                    self.content_filter_handler.add_filtered_chapter(
                                        file_info_tuple, chunks[chunk_index]
                                    )
                                
                        raise RuntimeError(error_msg) from e
                    
                self.log_message.emit(
                    f"[INFO] {log_prefix}: Все {total_chunks} чанков обработаны."
                )

            if self.is_cancelled:
                raise OperationCancelledError(
                    f"Отменено после обработки чанков для {log_prefix}"
                )

            if len(translated_chunks_map) != total_chunks:
                missing_chunks = total_chunks - len(translated_chunks_map)
                self.log_message.emit(
                    f"[ERROR] {log_prefix}: Не все чанки ({missing_chunks} из {total_chunks}) успешно обработаны. Файл не будет собран."
                )
                return (
                    file_info_tuple,
                    False,
                    f"Не все чанки обработаны ({missing_chunks} пропущено/ошибка)",
                )

            # Объединяем переведенные чанки
            final_translated_content = "".join(
                translated_chunks_map[i] for i in range(total_chunks)
            ).strip()

            self.log_message.emit(
                f"[INFO] {log_prefix}: Запись результата в: {out_path}"
            )
        
            try:
                if not (
                    "<html" in final_translated_content.lower()
                    and "</html>" in final_translated_content.lower()
                ):
                    self.log_message.emit(
                        f"[WARN] {log_prefix}: Результат перевода не похож на полный HTML. Записываю как есть."
                    )
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(final_translated_content)
                self.log_message.emit(
                    f"[SUCCESS] {log_prefix}: Файл HTML (из EPUB) сохранен."
                )
            
                # Обновляем статистику успеха
                if hasattr(self, 'progress_monitor'):
                    self.progress_monitor.update_progress(completed=1)
                
                return file_info_tuple, True, None
            
            except Exception as write_err:
                error_msg = f"Ошибка записи HTML: {write_err}"
                self.log_message.emit(f"[FAIL] {log_prefix}: {error_msg}")
                self.log_message.emit(f"Traceback (Write Error):\n{traceback.format_exc()}")
            
                if hasattr(self, 'error_analyzer'):
                    error_analysis = self.error_analyzer.analyze_error(write_err, error_msg)
                    self.progress_monitor.log_error(error_analysis['type'], error_msg)
                
                return file_info_tuple, False, error_msg
            
        except FileNotFoundError:
            error_msg = f"Исходный файл не найден: {src_display_path}"
            if hasattr(self, 'progress_monitor'):
                self.progress_monitor.update_progress(failed=1)
            return file_info_tuple, False, error_msg
        
        except IOError as e:
            error_msg = f"Ошибка I/O при обработке {src_display_path}: {e}"
            if hasattr(self, 'progress_monitor'):
                self.progress_monitor.update_progress(failed=1)
            return file_info_tuple, False, error_msg
        
        except OperationCancelledError as oce:
            self.log_message.emit(
                f"[CANCELLED] {log_prefix}: Обработка файла прервана ({oce})"
            )
            if hasattr(self, 'progress_monitor'):
                self.progress_monitor.update_progress(failed=1)
            return file_info_tuple, False, str(oce)
        
        except Exception as e:
            error_msg = f"Неожиданная ошибка файла: {e}"
            self.log_message.emit(f"[CRITICAL] {log_prefix}: {error_msg}")
            self.log_message.emit(f"Traceback:\n{traceback.format_exc()}")
        
            if hasattr(self, 'error_analyzer'):
                error_analysis = self.error_analyzer.analyze_error(e, error_msg)
                self.progress_monitor.log_error(error_analysis['type'], error_msg)
            
            if hasattr(self, 'progress_monitor'):
                self.progress_monitor.update_progress(failed=1)
            
            return file_info_tuple, False, error_msg

    @QtCore.pyqtSlot()
    def run(self):
        """Основной метод выполнения перевода"""
        if not self.setup_client():
            initial_errors = [(f_info, "Критическая ошибка: Не удалось инициализировать Gemini API клиент.")
                for f_info in self.files_to_process]
            self.finished.emit(0, len(self.files_to_process) if self.files_to_process else 0, initial_errors, False, None)
            return

        total_files = len(self.files_to_process)
        if total_files == 0:
            self.log_message.emit("Нет файлов для обработки.")
            self.finished.emit(0, 0, [], False, None)
            return

        processed_count = 0
        success_count = 0
        error_count = 0
        errors = []
        quota_exceeded = False
        quota_exceeded_file = None
    
        # === НОВОЕ: Отслеживаем успешно обработанные файлы ===
        successfully_processed = set()

        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests, thread_name_prefix="TranslateWorker") as self.executor:
            futures = {}
            quota_detected = False  # Флаг обнаружения превышения квоты
            futures_started = set()  # Отслеживаем какие файлы были запущены
    
            for file_info in self.files_to_process:
                if self.is_cancelled:
                    break
            
                # === НОВОЕ: Если обнаружена квота, НЕ запускаем новые задачи ===
                if quota_detected:
                    # Добавляем незапущенные файлы в список для следующего ключа
                    errors.append((file_info, "Требуется новый API ключ"))
                    error_count += 1
                    continue
            
                future = self.executor.submit(self.process_single_file, file_info)
                futures[future] = file_info
                futures_started.add(file_info)  # Отмечаем что файл был запущен

            # === НОВОЕ: Отслеживаем активные задачи ===
            completed_futures = set()
    
            for future in as_completed(futures):
                if self.is_cancelled and not quota_detected:
                    self.log_message.emit("[INFO] Отмена всех активных задач...")
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    for f, file_info in futures.items():
                        if not f.done():
                            errors.append((file_info, "Отменено пользователем"))
                            error_count += 1
                    break

                original_file_info = futures[future]
                completed_futures.add(future)
                file_type, path1, path2 = original_file_info
        
                if file_type == "epub":
                    base_src_path = f"{os.path.basename(path1)} -> {path2}"
                else:
                    base_src_path = os.path.basename(path1)

                processed_count += 1
        
                try:
                    returned_file_info, success, error_message = future.result(timeout=1)
            
                    if success:
                        success_count += 1
                        successfully_processed.add(original_file_info)  # Отмечаем успешную обработку
                    else:
                        # === ВАЖНО: Проверяем на превышение квоты ===
                        if error_message and "exceeded your current quota" in str(error_message).lower():
                            self.log_message.emit(f"[QUOTA EXCEEDED] {base_src_path}: Обнаружено превышение дневной квоты!")
                            quota_exceeded = True
                            quota_exceeded_file = original_file_info
                            quota_detected = True  # Устанавливаем флаг
                    
                            # === ИСПРАВЛЕНИЕ: Отменяем активные задачи вместо ожидания ===
                            self.log_message.emit("[INFO] Превышение квоты обнаружено. Отмена активных задач...")
                        
                            # Устанавливаем флаг отмены
                            self.is_cancelled = True
                        
                            # Отменяем все незавершенные задачи
                            cancelled_count = 0
                            for f in futures:
                                if not f.done():
                                    try:
                                        f.cancel()
                                        cancelled_count += 1
                                    except:
                                        pass
                        
                            if cancelled_count > 0:
                                self.log_message.emit(f"[INFO] Отменено {cancelled_count} активных задач для смены ключа")
                        
                            # Даем небольшую задержку для завершения отмены
                            time.sleep(2)
                        
                            # Добавляем текущий файл в ошибки для повтора с новым ключом
                            errors.append((original_file_info, "Требуется новый API ключ"))
                            error_count += 1
                        else:
                            error_count += 1
                            errors.append((original_file_info, error_message or "Неизвестная ошибка"))
                    
                except RateLimitExceededError as rle:
                    # === Обработка исключения превышения квоты ===
                    self.log_message.emit(f"[QUOTA EXCEEDED] Превышена дневная квота для {base_src_path}")
                    quota_exceeded = True
                    quota_exceeded_file = original_file_info
                    quota_detected = True
            
                    # Устанавливаем флаг отмены и отменяем задачи
                    self.is_cancelled = True
                    cancelled_count = 0
                    for f in futures:
                        if not f.done():
                            try:
                                f.cancel()
                                cancelled_count += 1
                            except:
                                pass
                
                    if cancelled_count > 0:
                        self.log_message.emit(f"[INFO] Отменено {cancelled_count} активных задач")
            
                    # Добавляем в ошибки для повтора
                    errors.append((original_file_info, "Требуется новый API ключ"))
                    error_count += 1
            
                except Exception as e:
                    error_count += 1
                    errors.append((original_file_info, f"Ошибка обработки: {e}"))
                    self.log_message.emit(f"[ERROR] {base_src_path}: {e}")

                self.progress.emit(processed_count)
        
                # === НОВОЕ: Если обнаружена квота, выходим из цикла ===
                if quota_detected:
                    # Обрабатываем результаты оставшихся завершенных задач
                    for f in futures:
                        if f not in completed_futures and f.done():
                            try:
                                file_info = futures[f]
                                _, success, err_msg = f.result(timeout=0.1)
                                if success:
                                    success_count += 1
                                    successfully_processed.add(file_info)
                                else:
                                    errors.append((file_info, "Требуется новый API ключ"))
                                    error_count += 1
                                processed_count += 1
                                self.progress.emit(processed_count)
                            except:
                                errors.append((futures[f], "Требуется новый API ключ"))
                                error_count += 1
                    break

        self.executor = None

        # === ФИНАЛЬНАЯ ОБРАБОТКА ===
        # Если была обнаружена квота, добавляем ВСЕ необработанные файлы
        if quota_detected:
            # === НОВОЕ: Более точный подсчет необработанных файлов ===
            self.log_message.emit(f"[INFO] Подсчет необработанных файлов...")
            self.log_message.emit(f"[INFO] Всего файлов: {total_files}")
            self.log_message.emit(f"[INFO] Успешно обработано: {len(successfully_processed)}")
        
            # Добавляем ВСЕ файлы, которые не были успешно обработаны
            unprocessed_count = 0
            for file_info in self.files_to_process:
                if file_info not in successfully_processed:
                    # Проверяем, не добавлен ли уже этот файл в ошибки
                    already_in_errors = any(err[0] == file_info for err in errors)
                    if not already_in_errors:
                        errors.append((file_info, "Требуется новый API ключ"))
                        error_count += 1
                        unprocessed_count += 1
        
            self.log_message.emit(f"[INFO] Добавлено необработанных файлов для нового ключа: {unprocessed_count}")

        # Передаем результаты
        if quota_exceeded:
            self.log_message.emit(f"\n--- ПРЕВЫШЕНА ДНЕВНАЯ КВОТА API КЛЮЧА ---")
            self.log_message.emit(f"Все активные задачи завершены.")
            self.log_message.emit(f"Успешно обработано: {success_count}")
            self.log_message.emit(f"Требуют обработки новым ключом: {error_count}")
            self.log_message.emit(f"Готово к переключению на следующий ключ.")
            # Передаем специальный сигнал о превышении квоты
            self.finished.emit(success_count, error_count, errors, quota_exceeded, quota_exceeded_file)
        elif self.is_cancelled:
            self.log_message.emit(f"\n--- Процесс отменен пользователем (обработано: {processed_count}/{total_files}) ---")
            self.finished.emit(success_count, error_count, errors, False, None)
        else:
            self.log_message.emit("\n--- Обработка всех файлов завершена ---")
            self.finished.emit(success_count, error_count, errors, False, None)

    def cancel(self):
        """Отменяет выполнение"""
        self.is_cancelled = True
        if self.executor:
            # НЕ делаем shutdown сразу, даем задачам завершиться
            self.log_message.emit("[INFO] Запрос на отмену получен. Ожидание завершения активных задач...")

class OpenRouterMainWorker(QtCore.QObject):
    """Worker для основного перевода через OpenRouter"""
    progress = QtCore.pyqtSignal(int)
    log_message = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(int, int, list, bool, object)

    def __init__(
        self,
        api_key,
        out_folder,
        prompt_template,
        files_to_process,
        model_config,
        max_concurrent_requests,
        chunking_enabled_override,
        temperature,
        context_manager
    ):
        super().__init__()
        self.api_key = api_key
        self.out_folder = out_folder
        self.prompt_template = prompt_template
        self.files_to_process = files_to_process
        self.model_config = model_config
        self.max_concurrent_requests = min(max_concurrent_requests, 20)  # Ограничиваем 20 RPM
        self.chunking_enabled_override = chunking_enabled_override
        self.temperature = temperature
        self.context_manager = context_manager
        self.is_cancelled = False
        self.executor = None
        
        # Счетчики для RPM и RPD
        self.request_count_minute = 0
        self.request_count_day = 0
        self.minute_start = time.time()
        self.day_start = time.time()
        self.last_request_time = 0
        
        # Настройки OpenRouter
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_id = model_config.get("id", "deepseek/deepseek-chat-v3-0324:free")
        
    def enforce_rate_limits(self):
        """Контроль лимитов RPM (20) и RPD (50) для OpenRouter"""
        current_time = time.time()
        
        # Проверяем RPD (50 запросов в день)
        if current_time - self.day_start >= 86400:  # Прошел день
            self.request_count_day = 0
            self.day_start = current_time
            
        if self.request_count_day >= 50:
            wait_time = 86400 - (current_time - self.day_start)
            self.log_message.emit(f"[RPD LIMIT] Достигнут дневной лимит (50). Ожидание {wait_time/3600:.1f} часов")
            return False  # Не можем продолжать
            
        # Проверяем RPM (20 запросов в минуту)
        if current_time - self.minute_start >= 60:
            self.request_count_minute = 0
            self.minute_start = current_time
            
        if self.request_count_minute >= 20:
            wait_time = 60 - (current_time - self.minute_start)
            if wait_time > 0:
                self.log_message.emit(f"[RPM LIMIT] Достигнут минутный лимит (20). Ожидание {wait_time:.1f} сек")
                time.sleep(wait_time)
            self.request_count_minute = 0
            self.minute_start = time.time()
            
        # Минимальная задержка между запросами (3 секунды для надежности)
        min_delay = 3.0
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            if time_since_last < min_delay:
                time.sleep(min_delay - time_since_last)
                
        return True
        
    def translate_with_openrouter(self, text, context_log_prefix=""):
        """Отправляет запрос на перевод в OpenRouter"""
        if not self.enforce_rate_limits():
            raise Exception("Превышен дневной лимит OpenRouter (50 запросов)")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://epub-translator.app", # Рекомендуемый заголовок
            "X-Title": "EPUB Translator Main" # Рекомендуемый заголовок
        }
        
        # Формируем промпт с учетом глоссария
        full_prompt = self.prompt_template
        
        if self.context_manager.use_dynamic_glossary and self.context_manager.global_glossary:
            glossary_text = self.context_manager.format_glossary_for_prompt(text)
            full_prompt = f"{self.prompt_template}\n\n{glossary_text}"
            
        # Заменяем {text} на реальный текст
        full_prompt = full_prompt.replace("{text}", text)

        # <<< ИСПРАВЛЕНО: Убран `max_tokens` и улучшен системный промпт
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an elite literary translator specializing in adapting EPUB content into natural-sounding Russian. Your task is to translate the user's text, meticulously preserving the original XHTML/HTML structure and all tags. The final output must be only the translated XHTML code without any extra explanations."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": self.temperature
        }
        
        try:
            self.log_message.emit(f"[OPENROUTER] {context_log_prefix}: Отправка запроса...")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=180 # <<< Увеличено время ожидания для больших глав
            )
            
            # Обновляем счетчики
            self.request_count_minute += 1
            self.request_count_day += 1
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    translated_text = result['choices'][0]['message']['content']
                    self.log_message.emit(f"[SUCCESS] {context_log_prefix}: Получен перевод")
                    return translated_text
                else:
                    raise Exception(f"Пустой или некорректный ответ от OpenRouter: {result}")
            else:
                error_msg = f"OpenRouter error {response.status_code}: {response.text[:200]}"
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Таймаут запроса к OpenRouter (120 сек)")
        except Exception as e:
            raise Exception(f"Ошибка OpenRouter: {e}")

    # Остальная часть класса OpenRouterMainWorker остается без изменений...
    def process_single_file(self, file_info_tuple):
        """Обрабатывает один файл через OpenRouter"""
        file_type, path1, path2 = file_info_tuple
        
        if file_type != "epub":
            return file_info_tuple, False, f"Неподдерживаемый тип файла: {file_type}"
            
        epub_base_name = os.path.splitext(os.path.basename(path1))[0]
        html_file_name = os.path.splitext(os.path.basename(path2))[0]
        safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
        out_path = os.path.join(
            self.out_folder, 
            f"{epub_base_name}_{safe_html_name}_translated.html"
        )
        
        log_prefix = f"{os.path.basename(path1)} -> {path2}"
        
        try:
            # Читаем HTML из EPUB
            with zipfile.ZipFile(path1, "r") as epub_zip:
                html_bytes = epub_zip.read(path2)
                try:
                    original_content = html_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    original_content = html_bytes.decode("cp1251", errors="ignore")
                    
            if not original_content.strip():
                open(out_path, "w").close() # Создаем пустой файл
                return file_info_tuple, True, "Пустой файл"
                
            # Чанкинг если нужно
            content_length = len(original_content)
            
            if self.chunking_enabled_override and content_length > CHARACTER_LIMIT_FOR_CHUNK:
                self.log_message.emit(f"[INFO] {log_prefix}: Разделение на чанки...")
                chunks = split_text_into_chunks(
                    original_content,
                    CHUNK_TARGET_SIZE,
                    CHUNK_SEARCH_WINDOW,
                    MIN_CHUNK_SIZE
                )
                
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    if self.is_cancelled:
                        return file_info_tuple, False, "Отменено пользователем"
                        
                    chunk_prefix = f"{log_prefix} [Chunk {i+1}/{len(chunks)}]"
                    translated = self.translate_with_openrouter(chunk, chunk_prefix)
                    
                    # Очистка от артефактов
                    if "```" in translated:
                        translated = self.clean_response(translated)
                        
                    translated_chunks.append(translated)
                    
                final_translated = "".join(translated_chunks)
            else:
                # Перевод целиком
                final_translated = self.translate_with_openrouter(original_content, log_prefix)
                
                if "```" in final_translated:
                    final_translated = self.clean_response(final_translated)
                    
            # Сохраняем результат
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(final_translated)
                
            self.log_message.emit(f"[SUCCESS] {log_prefix}: Сохранено")
            return file_info_tuple, True, None
            
        except Exception as e:
            self.log_message.emit(f"[ERROR] {log_prefix}: {e}")
            return file_info_tuple, False, str(e)
            
    def clean_response(self, text):
        """Очищает ответ от markdown артефактов"""
        cleaned = text.strip()
        markers = ["```html", "```xml", "```xhtml", "```"]
        
        for marker in markers:
            if cleaned.lower().startswith(marker):
                cleaned = cleaned[len(marker):].strip()
                break
                
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
            
        return cleaned
        
    @QtCore.pyqtSlot()
    def run(self):
        """Основной метод выполнения перевода через OpenRouter"""
        self.log_message.emit("=" * 40)
        self.log_message.emit(f"НАЧАЛО ПЕРЕВОДА ЧЕРЕЗ OPENROUTER")
        self.log_message.emit(f"Модель: {self.model_id}")
        self.log_message.emit(f"Файлов для обработки: {len(self.files_to_process)}")
        self.log_message.emit(f"RPM лимит: 20, RPD лимит: 50")
        self.log_message.emit("=" * 40)
        
        total_files = len(self.files_to_process)
        success_count = 0
        error_count = 0
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as self.executor:
            futures = {}
            
            for file_info in self.files_to_process:
                if self.is_cancelled:
                    break
                    
                future = self.executor.submit(self.process_single_file, file_info)
                futures[future] = file_info
                
            processed_count = 0
            for future in as_completed(futures):
                if self.is_cancelled:
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break
                    
                file_info = futures[future]
                processed_count += 1
                
                try:
                    returned_file_info, success, error_message = future.result()
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append((file_info, error_message))
                        
                except Exception as e:
                    error_count += 1
                    errors.append((file_info, str(e)))
                    
                self.progress.emit(processed_count)
                
        self.log_message.emit("=" * 40)
        self.log_message.emit(f"ЗАВЕРШЕНО: Успешно {success_count}, Ошибок {error_count}")
        self.log_message.emit(f"Использовано запросов: {self.request_count_day}/50 (дневной лимит)")
        self.log_message.emit("=" * 40)
        
        self.finished.emit(success_count, error_count, errors, False, None)
        
    def cancel(self):
        """Отменяет выполнение"""
        self.is_cancelled = True

class TranslationProgressMonitor:
    """Мониторинг и анализ прогресса перевода"""
    
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.stats_file = os.path.join(output_folder, 'translation_stats.json')
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_chapters': 0,
            'completed_chapters': 0,
            'failed_chapters': 0,
            'rate_limit_switches': 0,
            'content_filter_blocks': 0,
            'api_calls': 0,
            'total_chars_processed': 0,
            'average_speed': 0,
            'errors_by_type': {}
        }
        
    def start_session(self, total_chapters):
        """Начинает новую сессию мониторинга"""
        self.stats['start_time'] = time.time()
        self.stats['total_chapters'] = total_chapters
        self.save_stats()
        
    def update_progress(self, completed=0, failed=0, chars_processed=0):
        """Обновляет статистику прогресса"""
        self.stats['completed_chapters'] += completed
        self.stats['failed_chapters'] += failed
        self.stats['total_chars_processed'] += chars_processed
        
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                self.stats['average_speed'] = self.stats['total_chars_processed'] / elapsed
                
        self.save_stats()
        
    def log_error(self, error_type, error_msg):
        """Логирует ошибку по типу"""
        if error_type not in self.stats['errors_by_type']:
            self.stats['errors_by_type'][error_type] = []
        self.stats['errors_by_type'][error_type].append({
            'message': str(error_msg)[:200],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Специальные счетчики
        if error_type == 'RATE_LIMIT':
            self.stats['rate_limit_switches'] += 1
        elif error_type == 'CONTENT_FILTER':
            self.stats['content_filter_blocks'] += 1
            
        self.save_stats()
        
    def get_eta(self):
        """Рассчитывает примерное время завершения"""
        if not self.stats['start_time'] or self.stats['completed_chapters'] == 0:
            return None
            
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['completed_chapters'] / elapsed
        
        if rate > 0:
            remaining = self.stats['total_chapters'] - self.stats['completed_chapters']
            eta_seconds = remaining / rate
            return eta_seconds
            
        return None
        
    def save_stats(self):
        """Сохраняет статистику в файл"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения статистики: {e}")
            
    def generate_report(self):
        """Генерирует отчет о переводе"""
        if self.stats['start_time']:
            self.stats['end_time'] = time.time()
            elapsed = self.stats['end_time'] - self.stats['start_time']
            
            report = f"""
═══════════════════════════════════════════
           ОТЧЕТ О ПЕРЕВОДЕ
═══════════════════════════════════════════

📊 ОБЩАЯ СТАТИСТИКА:
• Всего глав: {self.stats['total_chapters']}
• Успешно переведено: {self.stats['completed_chapters']}
• С ошибками: {self.stats['failed_chapters']}
• Успешность: {(self.stats['completed_chapters'] / max(1, self.stats['total_chapters']) * 100):.1f}%

⏱️ ВРЕМЯ:
• Общее время: {elapsed/60:.1f} минут
• Средняя скорость: {self.stats['average_speed']:.0f} символов/сек
• Глав в час: {(self.stats['completed_chapters'] / max(1, elapsed/3600)):.1f}

🔄 API СТАТИСТИКА:
• Переключений ключей (rate limit): {self.stats['rate_limit_switches']}
• Блокировок контента: {self.stats['content_filter_blocks']}
• Всего API вызовов: {self.stats['api_calls']}

📝 ОБРАБОТАНО ДАННЫХ:
• Всего символов: {self.stats['total_chars_processed']:,}
• Среднее на главу: {(self.stats['total_chars_processed'] / max(1, self.stats['completed_chapters'])):.0f}

❌ ОШИБКИ ПО ТИПАМ:
"""
            for error_type, errors in self.stats['errors_by_type'].items():
                report += f"• {error_type}: {len(errors)} случаев\n"
                
            report += "\n═══════════════════════════════════════════"
            
            return report
        return "Нет данных для отчета"

class TranslationModeDialog(QDialog):
    """Диалог выбора режима работы программы"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор режима работы")
        self.setMinimumSize(600, 400)
        self.selected_mode = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Выберите режим работы переводчика:")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Режим 1: Автоматическая ротация
        mode1_group = QGroupBox("🔄 Режим автоматической ротации ключей")
        mode1_layout = QVBoxLayout(mode1_group)
        mode1_desc = QLabel(
            "• Один экземпляр программы\n"
            "• Автоматическая смена ключей при rate limit\n"
            "• Последовательная обработка\n"
            "• Подходит для: небольших книг, экономии ресурсов"
        )
        mode1_desc.setWordWrap(True)
        mode1_layout.addWidget(mode1_desc)
        self.mode1_btn = QPushButton("Выбрать автоматическую ротацию")
        self.mode1_btn.clicked.connect(lambda: self.select_mode('auto_rotation'))
        mode1_layout.addWidget(self.mode1_btn)
        layout.addWidget(mode1_group)
        
        # Режим 2: Параллельные окна
        mode2_group = QGroupBox("⚡ Режим параллельной обработки")
        mode2_layout = QVBoxLayout(mode2_group)
        mode2_desc = QLabel(
            "• Несколько окон программы (по числу ключей)\n"
            "• Каждое окно работает со своим ключом\n"
            "• Параллельная обработка разных глав\n"
            "• Подходит для: больших книг, быстрой обработки"
        )
        mode2_desc.setWordWrap(True)
        mode2_layout.addWidget(mode2_desc)
        self.mode2_btn = QPushButton("Выбрать параллельную обработку")
        self.mode2_btn.clicked.connect(lambda: self.select_mode('parallel'))
        mode2_layout.addWidget(self.mode2_btn)
        layout.addWidget(mode2_group)
        
        # Режим 3: Гибридный
        mode3_group = QGroupBox("🎯 Гибридный режим")
        mode3_layout = QVBoxLayout(mode3_group)
        mode3_desc = QLabel(
            "• Несколько окон с пулами ключей\n"
            "• Автоматическая ротация внутри каждого окна\n"
            "• Балансировка нагрузки\n"
            "• Подходит для: очень больших проектов"
        )
        mode3_desc.setWordWrap(True)
        mode3_layout.addWidget(mode3_desc)
        self.mode3_btn = QPushButton("Выбрать гибридный режим")
        self.mode3_btn.clicked.connect(lambda: self.select_mode('hybrid'))
        mode3_layout.addWidget(self.mode3_btn)
        layout.addWidget(mode3_group)
        
        layout.addStretch()
        
    def select_mode(self, mode):
        self.selected_mode = mode
        self.accept()

class ParallelModeSetupDialog(QDialog):
    """Диалог для настройки параллельного режима с автоматическим распределением глав"""
    
    def __init__(self, api_keys, parent=None):
        super().__init__(parent)
        self.api_keys = api_keys
        self.setWindowTitle("Настройка параллельного режима")
        self.setMinimumSize(600, 650)  # УМЕНЬШЕНО с 800, 750
        self.setMaximumWidth(900)      # ДОБАВЛЕНО ограничение по ширине
        self.settings = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
    
        # Заголовок
        title = QLabel("Автоматическая настройка параллельного перевода")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
    
        info = QLabel(f"У вас {len(self.api_keys)} API ключей. Программа откроет столько же окон и распределит главы.")
        info.setWordWrap(True)
        layout.addWidget(info)
    
        # 1. Выбор EPUB файла (компактно)
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(QLabel("1. EPUB:"))
        self.file_btn = QPushButton("Выбрать...")
        self.file_btn.setMaximumWidth(100)
        self.file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_btn)
    
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("color: gray; font-size: 10px;")
        file_layout.addWidget(self.file_label, 1)
        layout.addLayout(file_layout)
    
        # Информация о главах
        self.chapters_info_label = QLabel("")
        self.chapters_info_label.setStyleSheet("color: blue; font-size: 10px;")
        layout.addWidget(self.chapters_info_label)
    
        # 2. Папка для сохранения (компактно)
        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(QLabel("2. Папка:"))
        self.output_btn = QPushButton("Выбрать...")
        self.output_btn.setMaximumWidth(100)
        self.output_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_btn)
    
        self.output_label = QLabel("Папка не выбрана")
        self.output_label.setStyleSheet("color: gray; font-size: 10px;")
        output_layout.addWidget(self.output_label, 1)
        layout.addLayout(output_layout)
    
        # 3. Распределение глав (компактно)
        distribution_group = QGroupBox("3. Распределение")
        distribution_layout = QVBoxLayout(distribution_group)
    
        # Метод распределения в одну строку
        method_layout = QtWidgets.QHBoxLayout()
        method_layout.addWidget(QLabel("Метод:"))
        self.distribution_combo = QtWidgets.QComboBox()
        self.distribution_combo.addItems([
            "Равномерно (рекомендуется)",
            "По порядку блоками",
            "Вручную указать количество"
        ])
        self.distribution_combo.currentTextChanged.connect(self.on_distribution_method_changed)
        method_layout.addWidget(self.distribution_combo)
    
        # Ручной ввод
        method_layout.addWidget(QLabel("Глав на окно:"))
        self.chapters_per_window_spin = QtWidgets.QSpinBox()
        self.chapters_per_window_spin.setMinimum(1)
        self.chapters_per_window_spin.setMaximum(1000)
        self.chapters_per_window_spin.setValue(100)
        self.chapters_per_window_spin.setMaximumWidth(80)
        self.chapters_per_window_spin.setVisible(False)
        method_layout.addWidget(self.chapters_per_window_spin)
    
        method_layout.addStretch()
        distribution_layout.addLayout(method_layout)
    
        # Таблица распределения (компактная)
        self.distribution_table = QTableWidget()
        self.distribution_table.setColumnCount(3)
        self.distribution_table.setHorizontalHeaderLabels(["Окно", "Ключ", "Главы"])
        self.distribution_table.setMaximumHeight(120)
    
        # Фиксированные размеры колонок
        header = self.distribution_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.distribution_table.setColumnWidth(0, 60)
        self.distribution_table.setColumnWidth(1, 80)
    
        distribution_layout.addWidget(self.distribution_table)
        layout.addWidget(distribution_group)
    
        # 4. Настройки (компактная сетка)
        settings_group = QGroupBox("4. Настройки")
        settings_layout = QtWidgets.QGridLayout(settings_group)
    
        # Строка 1
        settings_layout.addWidget(QLabel("Модель:"), 0, 0)
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(MODELS.keys())
        self.model_combo.setCurrentText(DEFAULT_MODEL_NAME)
        settings_layout.addWidget(self.model_combo, 0, 1)

        # Обновляем concurrency при смене модели
        self.model_combo.currentTextChanged.connect(
            lambda model: self.concurrency_spin.setValue(
                MODELS.get(model, {}).get("rpm", 10)
            )
        )

        settings_layout.addWidget(QLabel("Потоки:"), 0, 2)
        self.concurrency_spin = QtWidgets.QSpinBox()
        self.concurrency_spin.setMinimum(1)
        self.concurrency_spin.setMaximum(100)
        # Устанавливаем значение на основе выбранной модели
        default_rpm = MODELS.get(self.model_combo.currentText(), {}).get("rpm", 10)
        self.concurrency_spin.setValue(default_rpm)
        self.concurrency_spin.setMaximumWidth(60)
        settings_layout.addWidget(self.concurrency_spin, 0, 3)
    
        # Строка 2
        settings_layout.addWidget(QLabel("Температура:"), 1, 0)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(1.0)
        self.temperature_spin.setMaximumWidth(80)
        settings_layout.addWidget(self.temperature_spin, 1, 1)
    
        # Чекбоксы
        self.auto_start_checkbox = QCheckBox("Автостарт")
        self.auto_start_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_start_checkbox, 1, 2)
    
        self.chunking_checkbox = QCheckBox("Чанкинг")
        self.chunking_checkbox.setChecked(True)
        settings_layout.addWidget(self.chunking_checkbox, 1, 3)
    
        layout.addWidget(settings_group)
    
        # 5. Глоссарий (очень компактно)
        glossary_group = QGroupBox("5. Глоссарий")
        glossary_layout = QVBoxLayout(glossary_group)
    
        # Глоссарий в одну строку
        glossary_input_layout = QtWidgets.QHBoxLayout()
    
        self.glossary_text_edit = QtWidgets.QPlainTextEdit()
        self.glossary_text_edit.setMaximumHeight(60)
        self.glossary_text_edit.setPlaceholderText("Son Goku = Сон Гоку\nKamehameha = Камехамеха")
        self.glossary_text_edit.textChanged.connect(self.update_glossary_count)
        glossary_input_layout.addWidget(self.glossary_text_edit)
    
        # Кнопки справа
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
    
        load_btn = QPushButton("📁")
        load_btn.setMaximumSize(30, 25)
        load_btn.clicked.connect(self.load_glossary_from_file)
        load_btn.setToolTip("Загрузить")
        buttons_layout.addWidget(load_btn)
    
        save_btn = QPushButton("💾")
        save_btn.setMaximumSize(30, 25)
        save_btn.clicked.connect(self.save_glossary_to_file)
        save_btn.setToolTip("Сохранить")
        buttons_layout.addWidget(save_btn)
    
        glossary_input_layout.addWidget(buttons_widget)
        glossary_layout.addLayout(glossary_input_layout)
    
        # Опции в одну строку
        glossary_options_layout = QtWidgets.QHBoxLayout()
    
        self.dynamic_glossary_checkbox = QCheckBox("Динамический глоссарий")
        self.dynamic_glossary_checkbox.setChecked(True)
        glossary_options_layout.addWidget(self.dynamic_glossary_checkbox)
    
        self.glossary_count_label = QLabel("Терминов: 0")
        self.glossary_count_label.setStyleSheet("color: blue; font-size: 10px;")
        glossary_options_layout.addWidget(self.glossary_count_label)
    
        glossary_options_layout.addStretch()
        glossary_layout.addLayout(glossary_options_layout)
    
        layout.addWidget(glossary_group)
    
        # 6. Промпт (компактно)
        prompt_group = QGroupBox("6. Промпт")
        prompt_layout = QtWidgets.QHBoxLayout(prompt_group)
    
        self.custom_prompt_edit = QtWidgets.QPlainTextEdit()
        self.custom_prompt_edit.setMaximumHeight(60)
        self.custom_prompt_edit.setPlaceholderText("Оставьте пустым для стандартного")
        prompt_layout.addWidget(self.custom_prompt_edit)
    
        load_prompt_btn = QPushButton("📋\nСтандартный")
        load_prompt_btn.setMaximumWidth(80)
        load_prompt_btn.clicked.connect(self.load_default_prompt)
        prompt_layout.addWidget(load_prompt_btn)
    
        layout.addWidget(prompt_group)
    
        # Кнопки
        button_box = QDialogButtonBox()
        self.start_btn = QPushButton("🚀 Запустить")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.validate_and_accept)
        button_box.addButton(self.start_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
        # Инициализация
        self.selected_file = None
        self.output_folder = None
        self.html_files = []
        self.distributions = []
        
    def load_glossary_from_file(self):
        """Загружает глоссарий из файла (поддержка JSON и текстового формата)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл глоссария",
            "",
            "All supported (*.json *.txt);;JSON files (*.json);;Text files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.lower().endswith('.json'):
                # Загрузка JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    glossary_data = json.load(f)
                    
                # Конвертируем в текстовый формат
                lines = []
                for key, value in glossary_data.items():
                    lines.append(f"{key} = {value}")
                    
                self.glossary_text_edit.setPlainText('\n'.join(lines))
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    f"Загружено {len(glossary_data)} терминов из JSON"
                )
                
            else:
                # Загрузка текстового файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.glossary_text_edit.setPlainText(content)
                
                # Подсчитываем термины
                lines = [line.strip() for line in content.splitlines() if '=' in line.strip()]
                QtWidgets.QMessageBox.information(
                    self,
                    "Успех",
                    f"Загружено {len(lines)} терминов из текстового файла"
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить файл: {e}"
            )
            
    def save_glossary_to_file(self):
        """Сохраняет глоссарий в файл"""
        glossary_dict = self.parse_glossary_text()
        
        if not glossary_dict:
            QtWidgets.QMessageBox.warning(
                self,
                "Предупреждение",
                "Глоссарий пуст или неправильно отформатирован"
            )
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить глоссарий",
            "glossary.json",
            "JSON files (*.json);;Text files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.lower().endswith('.json'):
                # Сохранение в JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(glossary_dict, f, ensure_ascii=False, indent=2)
            else:
                # Сохранение в текстовый файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.glossary_text_edit.toPlainText())
                    
            QtWidgets.QMessageBox.information(
                self,
                "Успех",
                f"Глоссарий сохранен ({len(glossary_dict)} терминов)"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить файл: {e}"
            )
            
    def update_glossary_count(self):
        """Обновляет счетчик терминов в глоссарии"""
        glossary_dict = self.parse_glossary_text()
        self.glossary_count_label.setText(f"Терминов: {len(glossary_dict)}")
        
    def parse_glossary_text(self):
        """Парсит текст глоссария в словарь"""
        glossary_dict = {}
        text = self.glossary_text_edit.toPlainText()
        
        for line in text.splitlines():
            line = line.strip()
            if not line or not '=' in line:
                continue
                
            # Разделяем по первому знаку =
            parts = line.split('=', 1)
            if len(parts) == 2:
                original = parts[0].strip()
                translation = parts[1].strip()
                
                if original and translation:
                    glossary_dict[original] = translation
                    
        return glossary_dict
        
    def load_default_prompt(self):  # ← ДОБАВИТЬ ЭТОТ МЕТОД ЗДЕСЬ
        """Загружает стандартный промпт"""
        default_prompt = """--- PROMPT START ---

**I. КОНТЕКСТ И ЗАДАЧА**

**Ваша Роль:** Вы — элитный переводчик и редактор, **мастер художественной адаптации**, специализирующийся на **литературном переводе содержимого EPUB-книг** (веб-новелл, ранобэ, романов и т.д.) с языка оригинала на русский язык. Вы обладаете глубоким пониманием языка оригинала, **его культурных кодов**, речевых оборотов, **литературных приемов, а также** технических аспектов форматирования XHTML. **Ваша цель – создать текст, который читается так, будто изначально был написан на русском языке для русскоязычного читателя, полностью заменяя оригинал и сохраняя при этом всю его суть, дух и уникальность.**

**Ваша Задача:** Перед вами фрагмент оригинального текста из файла EPUB (предоставленный как `{text}` в формате XHTML/HTML). Ваша цель — выполнить **высококлассную, глубокую литературную адаптацию** на русский язык, **виртуозно** сохраняя смысл, стиль, **эмоциональный накал, динамику повествования** и исходное XHTML-форматирование. **Критически важно, чтобы в итоговом результате НЕ ОСТАЛОСЬ НИ ОДНОГО СЛОВА или ФРАГМЕНТА текста на языке оригинала (за исключением неизменяемых частей XHTML, указанных ниже).**

**II. ОБЩИЕ ПРИНЦИПЫ АДАПТАЦИИ**

1.  **Естественность и Художественность Русского Языка:** Перевод должен звучать абсолютно органично и **литературно** по-русски. Избегайте буквального следования грамматике или идиомам оригинала, если они создают неестественные или косноязычные конструкции. Находите эквивалентные русские выражения, **идиомы и речевые обороты, которые точно передают замысел автора.** **Стремитесь к богатству, образности и выразительности русского языка.**
2.  **Сохранение Смысла, Тона и Атмосферы:** Точно передавайте основной смысл, атмосферу (юмор, саспенс, драму, романтику и т.д.) и авторский стиль оригинала. **Уделяйте особое внимание передаче эмоций персонажей, их внутренних переживаний, мотиваций и характера через их речь и мысли.**
3.  **Культурная и Стилистическая Адаптация:**
    *   **Хонорифики (-сан, -кун, -ним, гэгэ, шисюн, сэмпай и т.д.):** Как правило, **опускайте** или заменяйте естественными русскими формами обращения (по имени, "господин/госпожа", "братец/сестрица", "учитель", "старший" – в зависимости от контекста и отношений между персонажами).
    *   **Реалии:** Адаптируйте непонятные для русского читателя культурные или бытовые реалии: найдите русский эквивалент, дайте краткое, **органично вплетенное в повествование пояснение** (например, "он достал цзянь – прямой китайский меч"), или замените на близкую по смыслу понятную деталь. *Избегайте сносок и комментариев переводчика в тексте.*
    *   **Ономатопея (звукоподражания):** Заменяйте русскими звукоподражаниями или **яркими, образными описаниями звука/действия** (например, вместо "бах" можно написать "раздался глухой удар").
    *   **Имена собственные и Названия:** При отсутствии глоссария, стремитесь к благозвучной и понятной адаптации. Если возможен осмысленный перевод названия (например, техники или артефакта), отдавайте ему предпочтение перед транслитерацией. **Избегайте нагромождения труднопроизносимых транслитераций.**
    *   **Стилистика речи персонажей:** Если оригинал предполагает различия в манере речи разных персонажей (просторечия, высокий стиль, архаизмы, жаргон, детская речь), **старайтесь передать эти различия средствами русского языка.**

**III. ТЕХНИЧЕСКИЕ И СТИЛИСТИЧЕСКИЕ ТРЕБОВАНИЯ**

**1. Работа с XHTML/HTML-структурой EPUB:**
*   **ВАШ ГЛАВНЫЙ ПРИОРИТЕТ — ПОЛНОЕ СОХРАНЕНИЕ ИСХОДНОЙ XHTML/HTML-СТРУКТУРЫ.** Помните, что EPUB-книга состоит из XHTML-файлов. Ваша задача — работать с кодом этих файлов, переводя только текстовое наполнение.
*   **СОХРАНЯЙТЕ ВСЕ HTML-ТЕГИ!** Переводите **ТОЛЬКО видимый пользователю текст** внутри тегов (например, текст внутри `<p>`, `<h1>`, `<li>`, `<td>`, `<span>`, `<a>` и т.д., а также значения атрибутов `title` и `alt`, если они содержат осмысленный текст).
*   **НЕ МЕНЯЙТЕ, НЕ УДАЛЯЙТЕ и НЕ ДОБАВЛЯЙТЕ** никакие HTML-теги (`<p>`, `<div>`, `<img>`, `<a>` и т.д.), атрибуты (`class`, `id`, `href`, `src` и т.д.) или структуру документа.
*   **Комментарии HTML (`<!-- ... -->`), скрипты (`<script>...</script>`) и стили (`<style>...</style>`) должны оставаться БЕЗ ИЗМЕНЕНИЙ.** Содержимое этих тегов **НЕ ПЕРЕВОДИТСЯ**.
*   **Цель:** Выходной код должен быть валидным XHTML/HTML с той же структурой и тегами, что и входной, но с **полностью переведенным текстовым содержимым** (кроме указанных исключений).

**2. Стилистические Требования к Тексту (Правила Адаптации):**
*   **2.1. (Оформление прямой речи и цитат):**
    *   Квадратные скобки `[]`, обозначающие **прямую речь персонажей**, заменяйте на стандартное оформление прямой речи в русском языке с помощью тире: `— Реплика.`
    *   Конструкции вида `『Цитата/Реплика』` или `「Цитата/Реплика」` заменяйте на русские кавычки-«ёлочки» (`«Цитата/Реплика»`), если это выделенная мысль, название, цитата. Если это полноценная прямая речь, оформляйте её с тире: `— Реплика.`
*   **2.2. (Оформление мыслей):** Все **мысли героев** оформляйте русскими кавычками-«ёлочками»: `«Мысль персонажа.»`
*   **2.3. (Плавность и читаемость):** Уделите особое внимание **плавности и ритму текста**. Он должен читаться естественно и увлекательно. При необходимости, делите слишком длинные предложения на более короткие для лучшей читаемости, не теряя связи и смысла.
*   **2.4. (Передача протяжных звуков/заикания):** Для передачи протяжных звуков или заикания ограничивайтесь **тремя-четырьмя повторениями буквы**, разделенными дефисом: `А-а-ах...`, `Н-н-нет...`.
*   **2.5. (Знаки препинания в конце фразы):** Если фраза оканчивается на `...!` или `...?`, **сохраняйте этот порядок**. Для сочетания вопросительного и восклицательного знаков используйте `?!` или `!?`.
*   **2.6. (Оформление мыслей без тире):** Мысли в кавычках должны быть самостоятельными конструкциями. Не ставьте перед ними тире, как перед прямой речью.
    *   Корректно: `Он подумал: «Это интересно».` или `«Это интересно», — мелькнуло у него в голове.`
    *   Некорректно: `— «Мысль...»`
*   **2.7. (Количество знаков препинания):** Чрезмерное количество одинаковых знаков (`!!!!`, `????`) заменяйте **одним, двумя (`!!`, `??`) или сочетанием `?!` / `!?`**.
*   **2.8. (Передача заикания/раздельного произношения):** Сохраняйте разделение букв дефисом для передачи заикания или протяжного произнесения: `П-п-привет...`, `Чт-т-то-о?!`

    1. **КАЖДАЯ РЕПЛИКА ДИАЛОГА НАЧИНАЕТСЯ С НОВОЙ СТРОКИ (НОВОГО АБЗАЦА)**
    2. **Правильное оформление диалогов:**
       - Простая реплика: `— Текст реплики.`
       - Реплика с авторской ремаркой ПОСЛЕ: `— Текст реплики, — сказал персонаж.`
       - Реплика с авторской ремаркой ДО: `Персонаж сказал:` (новая строка) `— Текст реплики.`
       - НЕ разрывайте реплику и её авторскую ремарку на разные абзацы!

    3. **ЗАПРЕЩЕНО:**
       ❌ Неправильно:
       ```
       — Реплика.
   
       — Следующая реплика.
   
       сказал он.
       ```
   
       ✅ Правильно:
       ```
       — Реплика.
   
       — Следующая реплика, — сказал он.
       ```

    4. **Мысли персонажей:** оформляйте в кавычках-«ёлочках»: «Мысль персонажа»

**3. ОБЯЗАТЕЛЬНО ОФОРМЛЯТЬ НАЗВАНИЯ ГЛАВ В ВИДЕ: Глава X. Название главы**
Если ЕСТЬ глава, но нет названия, то просто: Глава X
А если нет главы, но есть название, то просто название надо с переводом

**IV. ГЛОССАРИЙ (Если применимо)**

*   Если предоставлен глоссарий имен, терминов, названий техник и т.д. — **строго придерживайтесь его**. Последовательность и единообразие критичны.

**V. ИТОГОВЫЙ РЕЗУЛЬТАТ**

*   Предоставьте **ИСКЛЮЧИТЕЛЬНО переведенный и адаптированный XHTML/HTML-код.**
*   **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО включать в вывод оригинальный текст или любые его фрагменты.**
*   **НЕ добавляйте никаких вводных фраз** типа "Вот перевод:", "Адаптация:", **а также никаких заключительных фраз или комментариев** (кроме неизмененных комментариев HTML).

**VI. ФИНАЛЬНАЯ ПРОВЕРКА (Мысленно перед выводом):**
*   Текст внутри HTML-кода звучит **естественно, художественно и увлекательно** по-русски?
*   Смысл, тон, **эмоции и атмосфера** оригинала переданы точно?
*   **XHTML-теги и структура документа** сохранены в точности?
*   Только видимый пользователю текст переведен, а теги, атрибуты, скрипты, стили и комментарии не тронуты?
*   **Все стилистические и культурные требования (разделы II и III.2) учтены?**
*   В итоговом коде **ПОЛНОСТЬЮ ОТСУТСТВУЕТ текст на языке оригинала** (за исключением разрешенных неизменяемых элементов)? **ПРОВЕРЕНО?**

--- PROMPT END ---"""
        
        self.custom_prompt_edit.setPlainText(default_prompt)
        QtWidgets.QMessageBox.information(
            self,
            "Промпт загружен",
            "Загружен стандартный промпт для перевода"
        )
        
    def select_file(self):
        """Выбор EPUB файла и анализ глав"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите EPUB файл",
            "",
            "EPUB files (*.epub)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            
            # Анализируем EPUB
            try:
                with zipfile.ZipFile(file_path, 'r') as epub_zip:
                    self.html_files = [
                        name for name in epub_zip.namelist()
                        if name.lower().endswith(('.html', '.xhtml', '.htm'))
                        and not name.startswith('__MACOSX')
                    ]
                    self.html_files = sorted(self.html_files, key=extract_number_from_path)
                    
                    # Показываем диалог выбора глав
                    selector = EpubHtmlSelectorDialog(file_path, self.html_files, self)
                    if selector.exec():
                        selected = selector.get_selected_files()
                        if selected:
                            self.html_files = selected
                            self.chapters_info_label.setText(
                                f"Выбрано глав: {len(self.html_files)}"
                            )
                            self.update_distribution_preview()
                            self.check_ready()
                        else:
                            self.html_files = []
                            self.chapters_info_label.setText("Главы не выбраны")
                    else:
                        self.html_files = []
                        self.chapters_info_label.setText("Выбор отменен")
                        
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось прочитать EPUB: {e}"
                )
                self.html_files = []
                
    def select_output_folder(self):
        """Выбор папки для сохранения"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения перевода"
        )
        if folder:
            self.output_folder = folder
            self.output_label.setText(folder)
            self.check_ready()
            
    def on_distribution_method_changed(self, method):
        """Обработка изменения метода распределения"""
        self.chapters_per_window_spin.setVisible(method == "Вручную указать количество")
        self.update_distribution_preview()
        
    def update_distribution_preview(self):
        """Обновляет предпросмотр распределения глав с учетом RPM модели"""
        if not self.html_files:
            return
        
        method = self.distribution_combo.currentText()
        total_chapters = len(self.html_files)
        num_windows = len(self.api_keys)
    
        # Учитываем RPM модели для оптимального распределения
        model_name = self.model_combo.currentText()
        model_rpm = MODELS.get(model_name, {}).get('rpm', 10)
    
        # Для моделей с низким RPM ограничиваем количество активных окон
        if model_rpm <= 5:
            # Для Gemini 2.5 Pro рекомендуем не более 5 активных окон одновременно
            recommended_windows = min(5, num_windows)
            if num_windows > recommended_windows:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Предупреждение о лимитах",
                    f"Модель {model_name} имеет лимит {model_rpm} RPM.\n"
                    f"Рекомендуется использовать не более {recommended_windows} окон одновременно.\n\n"
                    f"Остальные {num_windows - recommended_windows} окон можно запустить позже."
                )
    
        self.distributions = []
        
        if method == "Равномерно (рекомендуется)":
            # Равномерное распределение
            chapters_per_window = total_chapters // num_windows
            remainder = total_chapters % num_windows
            
            start_idx = 0
            for i in range(num_windows):
                count = chapters_per_window + (1 if i < remainder else 0)
                end_idx = start_idx + count
                self.distributions.append({
                    'window_id': i + 1,
                    'api_key': self.api_keys[i],
                    'chapters': self.html_files[start_idx:end_idx],
                    'start': start_idx,
                    'end': end_idx
                })
                start_idx = end_idx
                
        elif method == "По порядку блоками":
            # Блоками по 100 глав (или сколько есть)
            block_size = min(100, (total_chapters + num_windows - 1) // num_windows)
            
            start_idx = 0
            for i in range(num_windows):
                if start_idx >= total_chapters:
                    break
                end_idx = min(start_idx + block_size, total_chapters)
                self.distributions.append({
                    'window_id': i + 1,
                    'api_key': self.api_keys[i],
                    'chapters': self.html_files[start_idx:end_idx],
                    'start': start_idx,
                    'end': end_idx
                })
                start_idx = end_idx
                
        else:  # Вручную указать количество
            chapters_per_window = self.chapters_per_window_spin.value()
            
            start_idx = 0
            for i in range(num_windows):
                if start_idx >= total_chapters:
                    break
                end_idx = min(start_idx + chapters_per_window, total_chapters)
                self.distributions.append({
                    'window_id': i + 1,
                    'api_key': self.api_keys[i],
                    'chapters': self.html_files[start_idx:end_idx],
                    'start': start_idx,
                    'end': end_idx
                })
                start_idx = end_idx
                
        # Обновляем таблицу
        self.distribution_table.setRowCount(len(self.distributions))
        for i, dist in enumerate(self.distributions):
            self.distribution_table.setItem(i, 0, QTableWidgetItem(f"Окно #{dist['window_id']}"))
            self.distribution_table.setItem(i, 1, QTableWidgetItem(f"...{dist['api_key'][-4:]}"))
            chapters_range = f"Главы {dist['start']+1}-{dist['end']} ({len(dist['chapters'])} шт.)"
            self.distribution_table.setItem(i, 2, QTableWidgetItem(chapters_range))
            
    def check_ready(self):
        """Проверяет готовность к запуску"""
        ready = (
            self.selected_file is not None and
            self.output_folder is not None and
            len(self.html_files) > 0
        )
        self.start_btn.setEnabled(ready)
        
    def validate_and_accept(self):
        """Проверка и сохранение настроек"""
        if not self.selected_file or not self.output_folder or not self.html_files:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                "Заполните все обязательные поля"
            )
            return
            
        # Парсим глоссарий из текста
        glossary_dict = self.parse_glossary_text()
        
        self.settings = {
            'file_path': self.selected_file,
            'output_folder': self.output_folder,
            'glossary_dict': glossary_dict,  # Передаем словарь вместо пути к файлу
            'model': self.model_combo.currentText(),
            'concurrent_requests': self.concurrency_spin.value(),
            'temperature': self.temperature_spin.value(),
            'auto_start': self.auto_start_checkbox.isChecked(),
            'chunking': self.chunking_checkbox.isChecked(),
            'distributions': self.distributions
        }
        
        self.accept()
        
    def get_settings(self):
        """Возвращает настройки"""
        return {
            'file_path': self.selected_file,
            'output_folder': self.output_folder,
            'glossary_dict': self.parse_glossary_text(),  # Передаем словарь вместо пути к файлу
            'model': self.model_combo.currentText(),
            'concurrent_requests': self.concurrency_spin.value(),
            'temperature': self.temperature_spin.value(),
            'auto_start': self.auto_start_checkbox.isChecked(),
            'chunking': self.chunking_checkbox.isChecked(),
            'dynamic_glossary': self.dynamic_glossary_checkbox.isChecked(),
            'custom_prompt': self.custom_prompt_edit.toPlainText().strip() or None,  # === ДОБАВЛЕНА ЭТА СТРОКА ===
            'distributions': self.distributions
        }

class ContentFilterHandler:
    """Обработчик глав, заблокированных фильтрами контента"""
    
    def __init__(self, api_key_manager, context_manager):
        self.api_key_manager = api_key_manager
        self.context_manager = context_manager
        self.filtered_chapters = []
        self.openrouter_key = None
        self.openrouter_model = None
        self.openrouter_translator = None
        # Добавляем отслеживание результатов OpenRouter
        self.openrouter_results = []
        self.openrouter_failed_chapters = []
        
    def set_openrouter_settings(self, api_key, model):
        """Устанавливает настройки для OpenRouter"""
        self.openrouter_key = api_key
        self.openrouter_model = model
        self.openrouter_translator = OpenRouterTranslator(api_key, model)
        
    def add_filtered_chapter(self, file_info, chunk_text):
        """Добавляет главу в список для повторной обработки"""
        self.filtered_chapters.append({
            'file_info': file_info,
            'content': chunk_text,
            'original_error': 'Content Filter Block'
        })
        
    def add_openrouter_failed_chapter(self, chapter_data):
        """Добавляет главу, которую не удалось перевести через OpenRouter"""
        if chapter_data not in self.openrouter_failed_chapters:
            self.openrouter_failed_chapters.append(chapter_data)
            
    def get_openrouter_failed_chapters(self):
        """Возвращает список глав, не переведенных через OpenRouter"""
        return self.openrouter_failed_chapters
        
    def clear_openrouter_results(self):
        """Очищает результаты OpenRouter для новой попытки"""
        self.openrouter_results = []
        self.openrouter_failed_chapters = []
        
    def process_filtered_chapters_with_openrouter(self, prompt_template, output_folder, log_callback=None):
        """Обрабатывает заблокированные главы через OpenRouter API"""
        if not self.filtered_chapters:
            return []
            
        if not self.openrouter_translator:
            if log_callback:
                log_callback("[ERROR] OpenRouter не настроен. Установите API ключ.")
            return []
            
        if log_callback:
            log_callback(f"[INFO] Обработка {len(self.filtered_chapters)} заблокированных глав через OpenRouter...")
            
        results = []
        self.clear_openrouter_results()
        
        for i, chapter_data in enumerate(self.filtered_chapters):
            try:
                if log_callback:
                    log_callback(f"[INFO] Обработка главы {i+1}/{len(self.filtered_chapters)}...")
                    
                # Переводим через OpenRouter
                translated_text = self.openrouter_translator.translate_text(
                    chapter_data['content'],
                    prompt_template,
                    log_callback
                )
                
                if translated_text and len(translated_text.strip()) > 0:
                    # Сохраняем результат
                    file_info = chapter_data['file_info']
                    file_type, epub_path, html_path = file_info
                    
                    if file_type == 'epub':
                        epub_base_name = os.path.splitext(os.path.basename(epub_path))[0]
                        html_file_name = os.path.splitext(os.path.basename(html_path))[0]
                        safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
                        output_path = os.path.join(
                            output_folder,
                            f"{epub_base_name}_{safe_html_name}_translated_openrouter.html"
                        )
                        
                        # Очищаем от возможных артефактов
                        if "```" in translated_text:
                            translated_text = self._clean_response(translated_text)
                            
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(translated_text)
                            
                        results.append({
                            'file_info': file_info,
                            'output_path': output_path,
                            'success': True
                        })
                        
                        if log_callback:
                            log_callback(f"[SUCCESS] Глава сохранена: {output_path}")
                    else:
                        results.append({
                            'file_info': file_info,
                            'success': False,
                            'error': 'Неподдерживаемый тип файла'
                        })
                else:
                    # Пустой или отсутствующий ответ
                    self.add_openrouter_failed_chapter(chapter_data)
                    results.append({
                        'file_info': chapter_data['file_info'],
                        'success': False,
                        'error': 'Пустой ответ от OpenRouter'
                    })
                    if log_callback:
                        log_callback(f"[ERROR] Не удалось перевести главу {i+1}")
                    
            except Exception as e:
                self.add_openrouter_failed_chapter(chapter_data)
                results.append({
                    'file_info': chapter_data['file_info'],
                    'success': False,
                    'error': str(e)
                })
                if log_callback:
                    log_callback(f"[ERROR] Ошибка обработки главы: {e}")
                    
        self.openrouter_results = results
        return results
        
    def _clean_response(self, text):
        """Очищает ответ от markdown артефактов"""
        cleaned = text.strip()
        markers = ["```html", "```xml", "```xhtml", "```"]
        
        for marker in markers:
            if cleaned.lower().startswith(marker):
                cleaned = cleaned[len(marker):].strip()
                break
                
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
            
        return cleaned

class OpenRouterTranslator:
    """Переводчик через OpenRouter API для обработки заблокированных глав"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model or "deepseek/deepseek-chat-v3-0324:free"
        
    def set_model(self, model):
        """Устанавливает модель для использования"""
        self.model = model
        
    def translate_text(self, text, prompt_template, log_callback=None):
        """Переводит текст через OpenRouter API"""
        if not self.api_key:
            if log_callback:
                log_callback("[ERROR] OpenRouter API ключ не установлен")
            return None
            
        # Упрощенный промпт для OpenRouter
        system_message = "You are a professional translator. Translate the following text to Russian, preserving ALL HTML tags EXACTLY as they are. Do not modify, add or remove any HTML tags."
        
        # Используем только текст без полного промпта для экономии токенов
        user_message = f"Translate to Russian (keep all HTML tags):\n\n{text}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://epub-translator.app",
            "X-Title": "EPUB Translator"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 50000
        }
        
        try:
            if log_callback:
                log_callback(f"[INFO] Отправка запроса к OpenRouter (модель: {self.model})...")
                log_callback(f"[DEBUG] Размер текста: {len(text)} символов")
                
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=90
            )
            
            if log_callback:
                log_callback(f"[DEBUG] Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    translated_text = result['choices'][0]['message']['content']
                    if log_callback:
                        log_callback(f"[SUCCESS] Получен ответ от OpenRouter ({len(translated_text)} символов)")
                    return translated_text
                else:
                    if log_callback:
                        log_callback(f"[ERROR] Пустой ответ от OpenRouter: {result}")
                    return None
            else:
                error_msg = f"OpenRouter API error: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', response.text[:200])}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                if log_callback:
                    log_callback(f"[ERROR] {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            if log_callback:
                log_callback("[ERROR] Таймаут при обращении к OpenRouter API (90 сек)")
            return None
        except requests.exceptions.ConnectionError as e:
            if log_callback:
                log_callback(f"[ERROR] Ошибка соединения с OpenRouter: {e}")
            return None
        except Exception as e:
            if log_callback:
                log_callback(f"[ERROR] Неожиданная ошибка при обращении к OpenRouter: {e}")
                import traceback
                log_callback(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return None

class OpenRouterWorker(QtCore.QObject):
    """Воркер для асинхронной обработки через OpenRouter с поддержкой параллельных запросов"""
    progress = QtCore.pyqtSignal(int)
    log_message = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(list)
    
    def __init__(self, filtered_chapters, openrouter_translator, prompt_template, output_folder, max_rpm=10):
        super().__init__()
        self.filtered_chapters = filtered_chapters
        self.openrouter_translator = openrouter_translator
        self.prompt_template = prompt_template
        self.output_folder = output_folder
        self.is_cancelled = False
        self.max_rpm = max_rpm  # Максимум запросов в минуту
        self.max_concurrent = min(5, max_rpm)  # Максимум одновременных запросов
        
    @QtCore.pyqtSlot()
    def run(self):
        """Обрабатывает заблокированные главы с параллельными запросами"""
        results = []
        total = len(self.filtered_chapters)
        
        self.log_message.emit(f"[INFO] Начало обработки {total} заблокированных глав через OpenRouter...")
        self.log_message.emit(f"[INFO] Параллельные запросы: до {self.max_concurrent}, RPM: до {self.max_rpm}")
        
        # Для контроля RPM
        request_times = []
        processed_count = 0
        
        # Используем ThreadPoolExecutor для параллельной обработки
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Словарь для отслеживания фьючерсов
            future_to_chapter = {}
            
            # Запускаем первую партию задач
            for i, chapter_data in enumerate(self.filtered_chapters[:self.max_concurrent]):
                if self.is_cancelled:
                    break
                    
                # Контроль RPM
                self._wait_for_rpm_limit(request_times)
                
                future = executor.submit(self._process_single_chapter, i, chapter_data)
                future_to_chapter[future] = (i, chapter_data)
                request_times.append(time.time())
            
            # Индекс следующей главы для обработки
            next_chapter_idx = self.max_concurrent
            
            # Обрабатываем результаты по мере готовности
            while future_to_chapter:
                if self.is_cancelled:
                    # Отменяем все незавершенные задачи
                    for future in future_to_chapter:
                        future.cancel()
                    self.log_message.emit("[INFO] Обработка отменена пользователем")
                    break
                
                # Ждем завершения любой задачи
                done, pending = as_completed(future_to_chapter, timeout=1).__next__(), None
                
                for future in as_completed(future_to_chapter):
                    if self.is_cancelled:
                        break
                        
                    idx, chapter_data = future_to_chapter[future]
                    
                    try:
                        result = future.result(timeout=1)
                        results.append(result)
                        processed_count += 1
                        
                        if result['success']:
                            self.log_message.emit(f"[SUCCESS] Глава {idx + 1}/{total} обработана")
                        else:
                            self.log_message.emit(f"[ERROR] Глава {idx + 1}/{total} не обработана: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        self.log_message.emit(f"[ERROR] Ошибка обработки главы {idx + 1}: {e}")
                        results.append({
                            'file_info': chapter_data['file_info'],
                            'success': False,
                            'error': str(e)
                        })
                        processed_count += 1
                    
                    # Удаляем обработанный фьючерс
                    del future_to_chapter[future]
                    
                    # Обновляем прогресс
                    self.progress.emit(processed_count)
                    
                    # Запускаем следующую задачу если есть
                    if next_chapter_idx < total and not self.is_cancelled:
                        # Контроль RPM
                        self._wait_for_rpm_limit(request_times)
                        
                        next_chapter = self.filtered_chapters[next_chapter_idx]
                        future = executor.submit(self._process_single_chapter, next_chapter_idx, next_chapter)
                        future_to_chapter[future] = (next_chapter_idx, next_chapter)
                        request_times.append(time.time())
                        next_chapter_idx += 1
                        
                    # Выходим из цикла для проверки отмены
                    break
                    
        self.log_message.emit(f"[INFO] Обработка завершена. Успешно: {sum(1 for r in results if r['success'])}/{total}")
        self.finished.emit(results)
        
    def _wait_for_rpm_limit(self, request_times):
        """Ожидает если необходимо для соблюдения RPM лимита"""
        if len(request_times) >= self.max_rpm:
            # Удаляем старые записи (старше минуты)
            current_time = time.time()
            request_times[:] = [t for t in request_times if current_time - t < 60]
            
            # Если все еще превышаем лимит, ждем
            if len(request_times) >= self.max_rpm:
                oldest_request = min(request_times)
                wait_time = 60 - (current_time - oldest_request) + 0.1  # +0.1 для безопасности
                if wait_time > 0:
                    self.log_message.emit(f"[RPM] Достигнут лимит {self.max_rpm} запросов/мин, ожидание {wait_time:.1f} сек...")
                    time.sleep(wait_time)
                    
    def _process_single_chapter(self, index, chapter_data):
        """Обрабатывает одну главу (выполняется в отдельном потоке)"""
        try:
            # Переводим через OpenRouter
            translated_text = self.openrouter_translator.translate_text(
                chapter_data['content'],
                self.prompt_template,
                None  # log_callback не используем в потоке
            )
            
            if translated_text:
                # Сохраняем результат
                file_info = chapter_data['file_info']
                file_type, epub_path, html_path = file_info
                
                if file_type == 'epub':
                    epub_base_name = os.path.splitext(os.path.basename(epub_path))[0]
                    html_file_name = os.path.splitext(os.path.basename(html_path))[0]
                    safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
                    output_path = os.path.join(
                        self.output_folder,
                        f"{epub_base_name}_{safe_html_name}_translated_openrouter.html"
                    )
                    
                    # Очищаем от возможных артефактов
                    cleaned_text = self._clean_response(translated_text)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_text)
                    
                    return {
                        'file_info': file_info,
                        'output_path': output_path,
                        'success': True
                    }
                else:
                    return {
                        'file_info': file_info,
                        'success': False,
                        'error': 'Неподдерживаемый тип файла'
                    }
            else:
                return {
                    'file_info': chapter_data['file_info'],
                    'success': False,
                    'error': 'Не удалось получить перевод от OpenRouter'
                }
                
        except Exception as e:
            return {
                'file_info': chapter_data['file_info'],
                'success': False,
                'error': str(e)
            }
            
    def _clean_response(self, text):
        """Очищает ответ от markdown артефактов"""
        cleaned = text.strip()
        markers = ["```html", "```xml", "```xhtml", "```"]
        
        for marker in markers:
            if cleaned.lower().startswith(marker):
                cleaned = cleaned[len(marker):].strip()
                break
                
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
            
        return cleaned
        
    def cancel(self):
        """Отменяет обработку"""
        self.is_cancelled = True

class ErrorAnalyzer:
    """Анализатор ошибок API для определения типа и возможности повтора"""
    
    @staticmethod
    def analyze_error(error_obj, error_msg=None):
        """Анализирует ошибку и возвращает тип и рекомендации"""
        error_str = str(error_obj).lower() if error_obj else ""
        msg_str = str(error_msg).lower() if error_msg else ""
        combined = f"{error_str} {msg_str}"
        
        # Rate limit проверки
        if any(x in combined for x in ['429', 'rate limit', 'resourceexhausted', 'quota exceeded', 'too many requests']):
            return {
                'type': 'RATE_LIMIT',
                'retryable': True,
                'switch_key': True,
                'message': 'Превышен лимит запросов (Rate Limit 429)'
            }
        
        # Content filter проверки
        if any(x in combined for x in ['blocked', 'content filter', 'safety', 'harmful', 'inappropriate']):
            return {
                'type': 'CONTENT_FILTER',
                'retryable': True,
                'switch_model': True,
                'message': 'Контент заблокирован фильтрами безопасности'
            }
        
        # Timeout
        if any(x in combined for x in ['timeout', 'deadline exceeded', '504']):
            return {
                'type': 'TIMEOUT',
                'retryable': True,
                'switch_key': False,
                'message': 'Превышено время ожидания ответа'
            }
        
        # Server errors
        if any(x in combined for x in ['500', '503', 'internal server', 'service unavailable']):
            return {
                'type': 'SERVER_ERROR',
                'retryable': True,
                'switch_key': False,
                'message': 'Ошибка сервера Google'
            }
        
        # API/Auth errors
        if any(x in combined for x in ['401', '403', 'unauthorized', 'forbidden', 'api key']):
            return {
                'type': 'AUTH_ERROR',
                'retryable': False,
                'switch_key': True,
                'message': 'Ошибка авторизации или недействительный ключ'
            }
        
        return {
            'type': 'UNKNOWN',
            'retryable': False,
            'switch_key': False,
            'message': f'Неизвестная ошибка: {error_str[:200]}'
        }


class TranslatorApp(QtWidgets.QWidget):
    def __init__(self, api_key_manager):
        super().__init__()
        self.api_key_manager = api_key_manager
        self.out_folder = None
        self.selected_files_data = []
        self.worker = None
        self.thread = None
        self.worker_ref = None
        self.thread_ref = None
        self.last_failed_items = []
        self.context_manager = ContextManager(os.path.join(os.getcwd(), "temp_context"))
        # Новые атрибуты
        self.progress_monitor = None
        self.content_filter_handler = None
        self.init_ui()

    def init_ui(self):
        num_keys = len(self.api_key_manager.api_keys) if self.api_key_manager and self.api_key_manager.api_keys else 0
        self.setWindowTitle(f"EPUB Translator v3.0 ({num_keys} keys loaded)")
        self.setGeometry(100, 100, 900, 900)

        # Изменен текст кнопки - только EPUB
        self.file_select_btn = QtWidgets.QPushButton(
            "1. Выбрать файлы EPUB"
        )
        self.file_select_btn.clicked.connect(self.select_files)
        
        self.file_list_widget = QtWidgets.QListWidget()
        self.file_list_widget.setToolTip(
            "Список HTML/XHTML файлов из EPUB для перевода."
        )
        self.file_list_widget.setFixedHeight(150)
        self.file_list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )

        self.clear_list_btn = QtWidgets.QPushButton("Очистить список")
        self.clear_list_btn.clicked.connect(self.clear_file_list)

        self.remove_selected_btn = QtWidgets.QPushButton("Удалить выбранное из списка")
        self.remove_selected_btn.setToolTip(
            "Удаляет выделенные элементы из списка файлов для перевода."
        )
        self.remove_selected_btn.clicked.connect(self.remove_selected_files_from_list)

        self.filter_untranslated_btn = QtWidgets.QPushButton("Скрыть переведенные")
        self.filter_untranslated_btn.setToolTip(
            "Удаляет из списка главы, которые уже переведены\n"
            "(проверяет наличие файлов в папке вывода)"
        )
        self.filter_untranslated_btn.clicked.connect(self.filter_untranslated_files)

        self.retry_failed_btn = QtWidgets.QPushButton("Выбрать только ошибочные")
        self.retry_failed_btn.setToolTip(
            "Очищает текущий список и добавляет только те главы,\nкоторые не удалось обработать в последнем запуске."
        )
        self.retry_failed_btn.clicked.connect(self.select_failed_items)
        self.retry_failed_btn.setVisible(False)

        self.export_failed_html_btn = QtWidgets.QPushButton("Сохранить HTML с ошибками")
        self.export_failed_html_btn.setToolTip(
            "Сохраняет исходные (непереведенные) HTML-файлы из EPUB,\nкоторые не удалось обработать, в указанную папку."
        )
        self.export_failed_html_btn.clicked.connect(self.export_failed_html_files)
        self.export_failed_html_btn.setVisible(False)

        # Новая кнопка для обработки заблокированных глав
        self.process_filtered_btn = QtWidgets.QPushButton("Обработать заблокированные главы")
        self.process_filtered_btn.setToolTip(
            "Попытаться перевести главы, заблокированные фильтрами контента,\nиспользуя альтернативную модель и настройки."
        )
        self.process_filtered_btn.clicked.connect(self.process_filtered_chapters)
        self.process_filtered_btn.setVisible(False)

        # Новые кнопки для OpenRouter
        self.retry_openrouter_btn = QtWidgets.QPushButton("🔄 Повторить OpenRouter для неудачных")
        self.retry_openrouter_btn.setToolTip(
            "Повторно попытаться перевести главы, которые не удалось\nперевести через OpenRouter в прошлый раз."
        )
        self.retry_openrouter_btn.clicked.connect(self.retry_openrouter_failed)
        self.retry_openrouter_btn.setVisible(False)

        self.select_openrouter_failed_btn = QtWidgets.QPushButton("📋 Выбрать неудачные OpenRouter")
        self.select_openrouter_failed_btn.setToolTip(
            "Добавить в список главы, которые не удалось перевести через OpenRouter."
        )
        self.select_openrouter_failed_btn.clicked.connect(self.select_openrouter_failed)
        self.select_openrouter_failed_btn.setVisible(False)

        self.export_openrouter_failed_btn = QtWidgets.QPushButton("💾 Экспорт неудачных OpenRouter")
        self.export_openrouter_failed_btn.setToolTip(
            "Сохранить исходные тексты глав, которые не удалось перевести через OpenRouter."
        )
        self.export_openrouter_failed_btn.clicked.connect(self.export_openrouter_failed)
        self.export_openrouter_failed_btn.setVisible(False)

        self.out_btn = QtWidgets.QPushButton("2. Папка для перевода")
        self.out_lbl = QtWidgets.QLineEdit("<не выбрано>")
        self.out_lbl.setReadOnly(True)
        self.out_lbl.setCursorPosition(0)
        self.out_btn.clicked.connect(self.select_output_folder)

        self.manage_glossary_btn = QtWidgets.QPushButton("📖 Управление Глоссарием")
        self.manage_glossary_btn.setToolTip("Открыть редактор глоссария (имена, термины).")
        self.manage_glossary_btn.clicked.connect(self.open_glossary_editor)

        self.manage_epub_btn = QtWidgets.QPushButton("📚 Создать EPUB из переводов")
        self.manage_epub_btn.setToolTip("Собрать переведенные главы в единый EPUB файл")
        self.manage_epub_btn.clicked.connect(self.open_epub_manager)
        
        # Новая кнопка для просмотра статистики
        self.view_stats_btn = QtWidgets.QPushButton("📊 Статистика")
        self.view_stats_btn.setToolTip("Просмотр статистики текущей сессии перевода")
        self.view_stats_btn.clicked.connect(self.view_statistics)
    
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(MODELS.keys())
        try:
            if DEFAULT_MODEL_NAME in MODELS:
                self.model_combo.setCurrentText(DEFAULT_MODEL_NAME)
            elif MODELS:
                self.model_combo.setCurrentIndex(0)
        except Exception:
            pass
        self.model_combo.setToolTip("Выберите модель Gemini.")
        
        self.concurrency_spin = QtWidgets.QSpinBox()
        self.concurrency_spin.setMinimum(1)
        self.concurrency_spin.setMaximum(1000)
        self.concurrency_spin.setToolTip(
            "Макс. одновременных запросов к API (для чанков)."
        )
        self.model_combo.currentTextChanged.connect(self.update_concurrency_suggestion)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(1.0)
        self.temperature_spin.setToolTip(
            "Температура генерации (0.0-2.0).\nВысокие значения = более креативно, низкие = более детерминированно.\nОбычно рекомендуется 0.7-1.0."
        )

        self.update_concurrency_suggestion(self.model_combo.currentText())

        self.chunking_checkbox = QtWidgets.QCheckBox(
            "Включить Чанкинг (для очень больших глав)"
        )
        self.chunking_checkbox.setToolTip(
            f"Разделять главы, превышающие ~{CHARACTER_LIMIT_FOR_CHUNK // 1000}k символов.\nВНИМАНИЕ: Чанкинг HTML может повредить теги!"
        )
        default_model_needs_chunking = MODELS.get(
            self.model_combo.currentText(), {}
        ).get("needs_chunking", False)
        self.chunking_checkbox.setChecked(default_model_needs_chunking)
        self.model_combo.currentTextChanged.connect(
            self.update_chunking_checkbox_suggestion
        )
        self.update_chunking_checkbox_suggestion(self.model_combo.currentText())

        self.post_delay_checkbox = QtWidgets.QCheckBox(
            "Включить пост-задержку API (рекомендуется)"
        )
        self.post_delay_checkbox.setToolTip(
            "Включает дополнительную задержку после каждого успешного запроса.\n"
            "Это помогает избежать ошибок лимита (429)."
        )
        self.post_delay_checkbox.setChecked(True)

        self.system_instruction_checkbox = QCheckBox(
            "Использовать системные инструкции (экономия токенов)"
        )
        self.system_instruction_checkbox.setToolTip(
            "Промпт будет установлен как системная инструкция один раз при инициализации модели.\n"
            "Это экономит токены при обработке множества глав."
        )
        self.system_instruction_checkbox.setChecked(True)

        self.dynamic_glossary_checkbox = QCheckBox(
            "Использовать динамический глоссарий (фильтрация по содержимому)"
        )
        self.dynamic_glossary_checkbox.setToolTip(
            "Автоматически выбирает из глоссария только те термины,\n"
            "которые встречаются в переводимом тексте.\n"
            "Это значительно экономит токены и ускоряет перевод."
        )
        self.dynamic_glossary_checkbox.setChecked(True)  # Включено по умолчанию

        self.prompt_lbl = QtWidgets.QLabel(
            "Промпт (инструкция для API, `{text}` будет заменен):"
        )
        self.prompt_edit = QtWidgets.QPlainTextEdit()
        self.prompt_edit.setPlaceholderText("Загрузка промпта по умолчанию...")
        # Здесь оставляем существующий промпт
        self.prompt_edit.setPlainText(
            """--- PROMPT START ---

**I. КОНТЕКСТ И ЗАДАЧА**

**Ваша Роль:** Вы — элитный переводчик и редактор, **мастер художественной адаптации**, специализирующийся на **литературном переводе содержимого EPUB-книг** (веб-новелл, ранобэ, романов и т.д.) с языка оригинала на русский язык. Вы обладаете глубоким пониманием языка оригинала, **его культурных кодов**, речевых оборотов, **литературных приемов, а также** технических аспектов форматирования XHTML. **Ваша цель – создать текст, который читается так, будто изначально был написан на русском языке для русскоязычного читателя, полностью заменяя оригинал и сохраняя при этом всю его суть, дух и уникальность.**

**Ваша Задача:** Перед вами фрагмент оригинального текста из файла EPUB (предоставленный как `{text}` в формате XHTML/HTML). Ваша цель — выполнить **высококлассную, глубокую литературную адаптацию** на русский язык, **виртуозно** сохраняя смысл, стиль, **эмоциональный накал, динамику повествования** и исходное XHTML-форматирование. **Критически важно, чтобы в итоговом результате НЕ ОСТАЛОСЬ НИ ОДНОГО СЛОВА или ФРАГМЕНТА текста на языке оригинала (за исключением неизменяемых частей XHTML, указанных ниже).**

**II. ОБЩИЕ ПРИНЦИПЫ АДАПТАЦИИ**

1.  **Естественность и Художественность Русского Языка:** Перевод должен звучать абсолютно органично и **литературно** по-русски. Избегайте буквального следования грамматике или идиомам оригинала, если они создают неестественные или косноязычные конструкции. Находите эквивалентные русские выражения, **идиомы и речевые обороты, которые точно передают замысел автора.** **Стремитесь к богатству, образности и выразительности русского языка.**
2.  **Сохранение Смысла, Тона и Атмосферы:** Точно передавайте основной смысл, атмосферу (юмор, саспенс, драму, романтику и т.д.) и авторский стиль оригинала. **Уделяйте особое внимание передаче эмоций персонажей, их внутренних переживаний, мотиваций и характера через их речь и мысли.**
3.  **Культурная и Стилистическая Адаптация:**
    *   **Хонорифики (-сан, -кун, -ним, гэгэ, шисюн, сэмпай и т.д.):** Как правило, **опускайте** или заменяйте естественными русскими формами обращения (по имени, "господин/госпожа", "братец/сестрица", "учитель", "старший" – в зависимости от контекста и отношений между персонажами).
    *   **Реалии:** Адаптируйте непонятные для русского читателя культурные или бытовые реалии: найдите русский эквивалент, дайте краткое, **органично вплетенное в повествование пояснение** (например, "он достал цзянь – прямой китайский меч"), или замените на близкую по смыслу понятную деталь. *Избегайте сносок и комментариев переводчика в тексте.*
    *   **Ономатопея (звукоподражания):** Заменяйте русскими звукоподражаниями или **яркими, образными описаниями звука/действия** (например, вместо "бах" можно написать "раздался глухой удар").
    *   **Имена собственные и Названия:** При отсутствии глоссария, стремитесь к благозвучной и понятной адаптации. Если возможен осмысленный перевод названия (например, техники или артефакта), отдавайте ему предпочтение перед транслитерацией. **Избегайте нагромождения труднопроизносимых транслитераций.**
    *   **Стилистика речи персонажей:** Если оригинал предполагает различия в манере речи разных персонажей (просторечия, высокий стиль, архаизмы, жаргон, детская речь), **старайтесь передать эти различия средствами русского языка.**

**III. ТЕХНИЧЕСКИЕ И СТИЛИСТИЧЕСКИЕ ТРЕБОВАНИЯ**

**1. Работа с XHTML/HTML-структурой EPUB:**
*   **ВАШ ГЛАВНЫЙ ПРИОРИТЕТ — ПОЛНОЕ СОХРАНЕНИЕ ИСХОДНОЙ XHTML/HTML-СТРУКТУРЫ.** Помните, что EPUB-книга состоит из XHTML-файлов. Ваша задача — работать с кодом этих файлов, переводя только текстовое наполнение.
*   **СОХРАНЯЙТЕ ВСЕ HTML-ТЕГИ!** Переводите **ТОЛЬКО видимый пользователю текст** внутри тегов (например, текст внутри `<p>`, `<h1>`, `<li>`, `<td>`, `<span>`, `<a>` и т.д., а также значения атрибутов `title` и `alt`, если они содержат осмысленный текст).
*   **НЕ МЕНЯЙТЕ, НЕ УДАЛЯЙТЕ и НЕ ДОБАВЛЯЙТЕ** никакие HTML-теги (`<p>`, `<div>`, `<img>`, `<a>` и т.д.), атрибуты (`class`, `id`, `href`, `src` и т.д.) или структуру документа.
*   **Комментарии HTML (`<!-- ... -->`), скрипты (`<script>...</script>`) и стили (`<style>...</style>`) должны оставаться БЕЗ ИЗМЕНЕНИЙ.** Содержимое этих тегов **НЕ ПЕРЕВОДИТСЯ**.
*   **Цель:** Выходной код должен быть валидным XHTML/HTML с той же структурой и тегами, что и входной, но с **полностью переведенным текстовым содержимым** (кроме указанных исключений).

**2. Стилистические Требования к Тексту (Правила Адаптации):**
*   **2.1. (Оформление прямой речи и цитат):**
    *   Квадратные скобки `[]`, обозначающие **прямую речь персонажей**, заменяйте на стандартное оформление прямой речи в русском языке с помощью тире: `— Реплика.`
    *   Конструкции вида `『Цитата/Реплика』` или `「Цитата/Реплика」` заменяйте на русские кавычки-«ёлочки» (`«Цитата/Реплика»`), если это выделенная мысль, название, цитата. Если это полноценная прямая речь, оформляйте её с тире: `— Реплика.`
*   **2.2. (Оформление мыслей):** Все **мысли героев** оформляйте русскими кавычками-«ёлочками»: `«Мысль персонажа.»`
*   **2.3. (Плавность и читаемость):** Уделите особое внимание **плавности и ритму текста**. Он должен читаться естественно и увлекательно. При необходимости, делите слишком длинные предложения на более короткие для лучшей читаемости, не теряя связи и смысла.
*   **2.4. (Передача протяжных звуков/заикания):** Для передачи протяжных звуков или заикания ограничивайтесь **тремя-четырьмя повторениями буквы**, разделенными дефисом: `А-а-ах...`, `Н-н-нет...`.
*   **2.5. (Знаки препинания в конце фразы):** Если фраза оканчивается на `...!` или `...?`, **сохраняйте этот порядок**. Для сочетания вопросительного и восклицательного знаков используйте `?!` или `!?`.
*   **2.6. (Оформление мыслей без тире):** Мысли в кавычках должны быть самостоятельными конструкциями. Не ставьте перед ними тире, как перед прямой речью.
    *   Корректно: `Он подумал: «Это интересно».` или `«Это интересно», — мелькнуло у него в голове.`
    *   Некорректно: `— «Мысль...»`
*   **2.7. (Количество знаков препинания):** Чрезмерное количество одинаковых знаков (`!!!!`, `????`) заменяйте **одним, двумя (`!!`, `??`) или сочетанием `?!` / `!?`**.
*   **2.8. (Передача заикания/раздельного произношения):** Сохраняйте разделение букв дефисом для передачи заикания или протяжного произнесения: `П-п-привет...`, `Чт-т-то-о?!`

    1. **КАЖДАЯ РЕПЛИКА ДИАЛОГА НАЧИНАЕТСЯ С НОВОЙ СТРОКИ (НОВОГО АБЗАЦА)**
    2. **Правильное оформление диалогов:**
       - Простая реплика: `— Текст реплики.`
       - Реплика с авторской ремаркой ПОСЛЕ: `— Текст реплики, — сказал персонаж.`
       - Реплика с авторской ремаркой ДО: `Персонаж сказал:` (новая строка) `— Текст реплики.`
       - НЕ разрывайте реплику и её авторскую ремарку на разные абзацы!

    3. **ЗАПРЕЩЕНО:**
       ❌ Неправильно:
       ```
       — Реплика.
   
       — Следующая реплика.
   
       сказал он.
       ```
   
       ✅ Правильно:
       ```
       — Реплика.
   
       — Следующая реплика, — сказал он.
       ```

    4. **Мысли персонажей:** оформляйте в кавычках-«ёлочках»: «Мысль персонажа»

**3. ОБЯЗАТЕЛЬНО ОФОРМЛЯТЬ НАЗВАНИЯ ГЛАВ В ВИДЕ: Глава X. Название главы**
Если ЕСТЬ глава, но нет названия, то просто: Глава X
А если нет главы, но есть название, то просто название надо с переводом

**IV. ГЛОССАРИЙ (Если применимо)**

*   Если предоставлен глоссарий имен, терминов, названий техник и т.д. — **строго придерживайтесь его**. Последовательность и единообразие критичны.

**V. ИТОГОВЫЙ РЕЗУЛЬТАТ**

*   Предоставьте **ИСКЛЮЧИТЕЛЬНО переведенный и адаптированный XHTML/HTML-код.**
*   **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО включать в вывод оригинальный текст или любые его фрагменты.**
*   **НЕ добавляйте никаких вводных фраз** типа "Вот перевод:", "Адаптация:", **а также никаких заключительных фраз или комментариев** (кроме неизмененных комментариев HTML).

**VI. ФИНАЛЬНАЯ ПРОВЕРКА (Мысленно перед выводом):**
*   Текст внутри HTML-кода звучит **естественно, художественно и увлекательно** по-русски?
*   Смысл, тон, **эмоции и атмосфера** оригинала переданы точно?
*   **XHTML-теги и структура документа** сохранены в точности?
*   Только видимый пользователю текст переведен, а теги, атрибуты, скрипты, стили и комментарии не тронуты?
*   **Все стилистические и культурные требования (разделы II и III.2) учтены?**
*   В итоговом коде **ПОЛНОСТЬЮ ОТСУТСТВУЕТ текст на языке оригинала** (за исключением разрешенных неизменяемых элементов)? **ПРОВЕРЕНО?**

--- PROMPT END ---"""
        )

        self.start_btn = QtWidgets.QPushButton("🚀 Начать перевод")
        self.start_btn.setStyleSheet("background-color: #ccffcc; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_translation)
        
        self.cancel_btn = QtWidgets.QPushButton("❌ Отмена")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet("background-color: #ffcccc;")
        self.cancel_btn.clicked.connect(self.cancel_translation)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m глав (%p%)")
        
        self.log_lbl = QtWidgets.QLabel("Лог выполнения:")
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QtGui.QFont("Consolas", 9))
        self.log_output.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        # === НОВОЕ: Настройка для отображения HTML ===
        self.log_output.setAcceptRichText(True)
        # === КОНЕЦ НОВОГО ===
        
        # Опционально: добавьте чекбокс для включения/выключения цветов
        self.color_logs_checkbox = QCheckBox("Цветные логи")
        self.color_logs_checkbox.setChecked(True)
        self.color_logs_checkbox.setToolTip("Включить/выключить цветную подсветку сообщений в логе")

        # Компоновка интерфейса
        main_layout = QtWidgets.QVBoxLayout(self)
        
        file_box = QtWidgets.QGroupBox("1. Исходный EPUB файл")
        file_layout = QtWidgets.QVBoxLayout(file_box)
        file_btn_layout = QtWidgets.QHBoxLayout()
        file_btn_layout.addWidget(self.file_select_btn)
        file_btn_layout.addWidget(self.clear_list_btn)
        file_btn_layout.addWidget(self.remove_selected_btn)
        file_btn_layout.addWidget(self.filter_untranslated_btn)
        file_btn_layout.addWidget(self.retry_failed_btn)
        file_btn_layout.addWidget(self.export_failed_html_btn)
        file_btn_layout.addWidget(self.process_filtered_btn)
        file_btn_layout.addWidget(self.retry_openrouter_btn)
        file_btn_layout.addWidget(self.select_openrouter_failed_btn)
        file_btn_layout.addWidget(self.export_openrouter_failed_btn)
        file_btn_layout.addWidget(self.filter_untranslated_btn)
        file_btn_layout.addStretch(1)
        file_layout.addLayout(file_btn_layout)
        file_layout.addWidget(self.file_list_widget)
        main_layout.addWidget(file_box)

        out_box = QtWidgets.QGroupBox("2. Папка для перевода и Управление")
        out_layout = QtWidgets.QHBoxLayout(out_box)
        out_layout.addWidget(self.out_btn)
        out_layout.addWidget(self.out_lbl, 1)
        out_layout.addWidget(self.manage_glossary_btn)
        out_layout.addWidget(self.manage_epub_btn)
        out_layout.addWidget(self.view_stats_btn)
        main_layout.addWidget(out_box)

        settings_prompt_box = QtWidgets.QGroupBox("3. Настройки API и Промпт")
        settings_prompt_layout = QtWidgets.QVBoxLayout(settings_prompt_box)
        api_grid_layout = QtWidgets.QGridLayout()
        # Добавляем выбор провайдера
        provider_layout = QtWidgets.QHBoxLayout()
        provider_layout.addWidget(QtWidgets.QLabel("Сервис:"))

        self.provider_combo = QtWidgets.QComboBox()
        self.provider_combo.addItems(["Google Gemini", "OpenRouter"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)

        # Теперь можно безопасно добавить в api_grid_layout
        api_grid_layout.addLayout(provider_layout, 0, 0, 1, 2)

        # Остальные элементы сетки
        api_grid_layout.addWidget(QtWidgets.QLabel("Модель API:"), 1, 0)  # Изменили строку с 0 на 1
        api_grid_layout.addWidget(self.model_combo, 1, 1)                 # Изменили строку с 0 на 1
        api_grid_layout.addWidget(QtWidgets.QLabel("Паралл. запросы:"), 2, 0)  # Изменили строку с 1 на 2
        api_grid_layout.addWidget(self.concurrency_spin, 2, 1)                 # Изменили строку с 1 на 2
        api_grid_layout.addWidget(QtWidgets.QLabel("Температура:"), 3, 0)      # Изменили строку с 2 на 3
        api_grid_layout.addWidget(self.temperature_spin, 3, 1)                 # Изменили строку с 2 на 3
        # ... и так далее, увеличьте номера строк для остальных элементов

        # Вызываем после создания всех виджетов
        self.on_provider_changed("Google Gemini")
        api_grid_layout.addWidget(QtWidgets.QLabel("Модель API:"), 0, 0)
        api_grid_layout.addWidget(self.model_combo, 0, 1)
        api_grid_layout.addWidget(QtWidgets.QLabel("Паралл. запросы:"), 1, 0)
        api_grid_layout.addWidget(self.concurrency_spin, 1, 1)
        api_grid_layout.addWidget(QtWidgets.QLabel("Температура:"), 2, 0)
        api_grid_layout.addWidget(self.dynamic_glossary_checkbox, 6, 0, 1, 2)
        api_grid_layout.addWidget(self.temperature_spin, 2, 1)
        api_grid_layout.addWidget(self.chunking_checkbox, 3, 0, 1, 2)
        api_grid_layout.addWidget(self.post_delay_checkbox, 4, 0, 1, 2)
        api_grid_layout.addWidget(self.system_instruction_checkbox, 5, 0, 1, 2)
        api_grid_layout.setColumnStretch(1, 1)
        settings_prompt_layout.addLayout(api_grid_layout)
        settings_prompt_layout.addWidget(self.prompt_lbl)
        settings_prompt_layout.addWidget(self.prompt_edit, 1)
        main_layout.addWidget(settings_prompt_box, 1)

        hbox_controls = QtWidgets.QHBoxLayout()
        hbox_controls.addWidget(self.start_btn, 1)
        hbox_controls.addWidget(self.cancel_btn)
        main_layout.addLayout(hbox_controls)
        main_layout.addWidget(self.progress_bar)
        log_controls_layout = QtWidgets.QHBoxLayout()
        log_controls_layout.addWidget(self.log_lbl)
        log_controls_layout.addStretch()
        log_controls_layout.addWidget(self.color_logs_checkbox)
        main_layout.addLayout(log_controls_layout)
        # main_layout.addWidget(self.log_lbl)
        main_layout.addWidget(self.log_output, 2)
        self.setLayout(main_layout)

    @QtCore.pyqtSlot(list)
    def on_openrouter_finished(self, results):
        """Обработка завершения перевода через OpenRouter"""
        # Очищаем воркер и поток
        if hasattr(self, 'openrouter_thread'):
            self.openrouter_thread.quit()
            self.openrouter_thread.wait()
            self.openrouter_thread.deleteLater()
            self.openrouter_worker.deleteLater()
    
        # Разблокируем интерфейс
        self.set_controls_enabled(True)

        # Считаем результаты
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count

        self.append_log("=" * 40)
        self.append_log(f"OPENROUTER ЗАВЕРШЕН: {success_count} успешно, {fail_count} с ошибками")
        self.append_log("=" * 40)

        # Обновляем видимость кнопок
        if fail_count > 0:
            self.retry_openrouter_btn.setVisible(True)
            self.select_openrouter_failed_btn.setVisible(True)
            self.export_openrouter_failed_btn.setVisible(True)
            self.append_log(f"[INFO] Доступны кнопки для работы с {fail_count} неудачными главами OpenRouter")
        else:
            self.retry_openrouter_btn.setVisible(False)
            self.select_openrouter_failed_btn.setVisible(False)
            self.export_openrouter_failed_btn.setVisible(False)

        # Очищаем список заблокированных глав только если все успешно
        if success_count > 0 and fail_count == 0:
            self.content_filter_handler.filtered_chapters = []
            self.process_filtered_btn.setVisible(False)

        # Показываем диалог с результатами
        QtWidgets.QMessageBox.information(
            self,
            "OpenRouter завершен",
            f"Обработка через OpenRouter завершена:\n\n"
            f"Успешно переведено: {success_count}\n"
            f"С ошибками: {fail_count}\n\n"
            f"Файлы сохранены с суффиксом '_openrouter'"
        )

    def retry_openrouter_failed(self):
        """Повторная попытка перевести неудачные главы через OpenRouter"""
        if not self.content_filter_handler or not self.content_filter_handler.openrouter_failed_chapters:
            QtWidgets.QMessageBox.information(
                self,
                "Нет неудачных глав",
                "Нет глав, которые не удалось перевести через OpenRouter."
            )
            return
        
        failed_count = len(self.content_filter_handler.openrouter_failed_chapters)
    
        reply = QtWidgets.QMessageBox.question(
            self,
            "Повторная попытка",
            f"Найдено {failed_count} глав, не переведенных через OpenRouter.\n\n"
            "Попробовать перевести их снова?",
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
    
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Перемещаем неудачные главы обратно в filtered_chapters
            self.content_filter_handler.filtered_chapters = self.content_filter_handler.openrouter_failed_chapters.copy()
            self.content_filter_handler.clear_openrouter_results()
        
            # Запускаем обработку
            self.process_filtered_chapters()
     
    def on_provider_changed(self, provider):
        """Обработчик смены провайдера API"""
        self.model_combo.clear()
    
        if provider == "OpenRouter":
            self.model_combo.addItems(OPENROUTER_MODELS.keys())
            # Фиксированные значения для OpenRouter
            self.concurrency_spin.setValue(20)
            self.concurrency_spin.setEnabled(False)
            self.append_log("[INFO] Переключено на OpenRouter (RPM: 20, RPD: 50)")
        else:
            self.model_combo.addItems(MODELS.keys())
            self.concurrency_spin.setEnabled(True)
            # Восстанавливаем значение для Gemini
            if self.model_combo.currentText() in MODELS:
                self.concurrency_spin.setValue(MODELS[self.model_combo.currentText()].get("rpm", 10))
     
    def filter_untranslated_files(self):
        """Фильтрует список файлов, оставляя только непереведенные"""
        if not self.selected_files_data or not self.out_folder:
            return
    
        untranslated = []
        translated_count = 0
    
        for file_info in self.selected_files_data:
            file_type, path1, path2 = file_info
        
            # Определяем имя выходного файла
            if file_type == "epub":
                epub_base_name = os.path.splitext(os.path.basename(path1))[0]
                html_file_name = os.path.splitext(os.path.basename(path2))[0]
                safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_file_name)
                out_filename = f"{epub_base_name}_{safe_html_name}_translated.html"
            else:
                # Для других типов файлов (если будут добавлены)
                base_name = os.path.splitext(os.path.basename(path1))[0]
                out_filename = f"{base_name}_translated.{file_type}"
            
            out_path = os.path.join(self.out_folder, out_filename)
        
            # Проверяем существование файла
            if os.path.exists(out_path):
                translated_count += 1
            else:
                untranslated.append(file_info)
    
        # Обновляем список
        self.selected_files_data = untranslated
        self.update_file_list_widget()
    
        # Информируем пользователя
        self.append_log(f"[INFO] Скрыто переведенных глав: {translated_count}")
        self.append_log(f"[INFO] Осталось для перевода: {len(untranslated)}")
    
        if translated_count > 0:
            QtWidgets.QMessageBox.information(
                self,
                "Фильтрация завершена",
                f"Скрыто переведенных глав: {translated_count}\n"
                f"Осталось для перевода: {len(untranslated)}"
            )
     
    def select_openrouter_failed(self):
        """Добавляет неудачные OpenRouter главы в список для обработки"""
        if not self.content_filter_handler or not self.content_filter_handler.openrouter_failed_chapters:
            QtWidgets.QMessageBox.information(
                self,
                "Нет неудачных глав",
                "Нет глав, которые не удалось перевести через OpenRouter."
            )
            return
        
        # Очищаем текущий список
        self.selected_files_data = []
    
        # Добавляем неудачные главы
        for chapter_data in self.content_filter_handler.openrouter_failed_chapters:
            file_info = chapter_data['file_info']
            if file_info not in self.selected_files_data:
                self.selected_files_data.append(file_info)
            
        self.update_file_list_widget()
    
        self.append_log(f"[INFO] Выбрано {len(self.selected_files_data)} глав, не переведенных через OpenRouter")
    
    def export_openrouter_failed(self):
        """Экспортирует исходные тексты глав, не переведенных через OpenRouter"""
        if not self.content_filter_handler or not self.content_filter_handler.openrouter_failed_chapters:
            QtWidgets.QMessageBox.information(
                self,
                "Нет неудачных глав",
                "Нет глав, которые не удалось перевести через OpenRouter."
            )
            return
        
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения неудачных глав OpenRouter",
            self.out_folder or ""
        )
    
        if not save_dir:
            return
        
        saved_count = 0
        failed_count = 0
    
        self.append_log(f"[INFO] Экспорт {len(self.content_filter_handler.openrouter_failed_chapters)} неудачных глав OpenRouter...")
    
        for chapter_data in self.content_filter_handler.openrouter_failed_chapters:
            try:
                file_info = chapter_data['file_info']
                content = chapter_data['content']
            
                if file_info[0] == 'epub':
                    epub_base = os.path.splitext(os.path.basename(file_info[1]))[0]
                    html_name = os.path.splitext(os.path.basename(file_info[2]))[0]
                    safe_name = re.sub(r'[\\/*?:"<>|]', "_", html_name)
                    filename = f"{epub_base}_{safe_name}_openrouter_failed.html"
                else:
                    filename = f"openrouter_failed_{saved_count}.html"
                
                filepath = os.path.join(save_dir, filename)
            
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.append_log(f"[SUCCESS] Сохранено: {filename}")
                saved_count += 1
            
            except Exception as e:
                self.append_log(f"[ERROR] Ошибка сохранения: {e}")
                failed_count += 1
            
        QtWidgets.QMessageBox.information(
            self,
            "Экспорт завершен",
            f"Сохранено: {saved_count} файлов\n"
            f"Ошибок: {failed_count}"
        )



    def show_content_filtered_summary(self):
        """Показывает сводку по заблокированным главам после завершения всех ключей"""
        if not hasattr(self, 'content_filter_handler') or not self.content_filter_handler:
            return
        
        filtered_count = len(self.content_filter_handler.filtered_chapters)
        if filtered_count == 0:
            return
        
        self.append_log("=" * 50)
        self.append_log("📋 СВОДКА ПО ЗАБЛОКИРОВАННЫМ ГЛАВАМ")
        self.append_log("=" * 50)
        self.append_log(f"Всего заблокировано фильтрами: {filtered_count} глав")
        self.append_log("Эти главы НЕ будут повторно обрабатываться при смене ключей")
        self.append_log("Используйте кнопку 'Обработать заблокированные главы' для перевода через OpenRouter")
    
        # Показываем список
        for i, chapter in enumerate(self.content_filter_handler.filtered_chapters[:10]):
            file_info = chapter['file_info']
            if file_info[0] == 'epub':
                chapter_name = f"{os.path.basename(file_info[1])} -> {file_info[2]}"
            else:
                chapter_name = os.path.basename(file_info[1])
            self.append_log(f"  {i+1}. {chapter_name}")
        
        if filtered_count > 10:
            self.append_log(f"  ... и еще {filtered_count - 10} глав")
        
        self.append_log("=" * 50)
    
        # Делаем кнопку видимой
        self.process_filtered_btn.setVisible(True)

    def restart_with_failed_items(self, quota_exceeded=False):
        """Перезапускает перевод с необработанными элементами"""
        if not self.last_failed_items and quota_exceeded:
            # При превышении квоты берем все необработанные из текущего списка
            failed_items = []
            for file_info in self.selected_files_data:
                # Проверяем, была ли глава успешно обработана
                if hasattr(self, 'worker') and self.worker:
                    # Здесь нужна логика проверки успешности
                    pass
                failed_items.append(file_info)
        
            if failed_items:
                self.selected_files_data = failed_items
                self.update_file_list_widget()
                self.append_colored_log(f"🔄 Перезапуск с {len(failed_items)} необработанными главами", "#0088cc", True)
                QtCore.QTimer.singleShot(1000, self.start_translation)
            else:
                self.append_log("[WARN] Нет глав для повторной обработки")
        elif self.last_failed_items:
            self.selected_files_data = list(self.last_failed_items)
            self.update_file_list_widget()
            self.append_colored_log(f"🔄 Перезапуск с {len(self.last_failed_items)} ошибочными главами", "#0088cc", True)
            QtCore.QTimer.singleShot(1000, self.start_translation)
        
    def show_add_keys_dialog(self):
        """Показывает диалог для добавления новых API ключей"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Добавить API ключи")
        dialog.setMinimumSize(500, 400)
    
        layout = QVBoxLayout(dialog)
    
        # Информация
        info_label = QLabel(
            "Все текущие API ключи исчерпали свою квоту.\n"
            "Добавьте новые ключи для продолжения перевода.\n\n"
            "Введите ключи (по одному на строку):"
        )
        layout.addWidget(info_label)
    
        # Текстовое поле для ключей
        keys_edit = QTextEdit()
        keys_edit.setPlaceholderText(
            "AIza...\n"
            "AIza...\n"
            "..."
        )
        layout.addWidget(keys_edit)
    
        # Статистика
        stats_label = QLabel()
        if hasattr(self, 'api_key_manager'):
            stats_label.setText(f"Текущие ключи: {self.api_key_manager.get_usage_report()}")
            stats_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(stats_label)
    
        # Кнопки
        buttons_layout = QtWidgets.QHBoxLayout()
    
        add_btn = QPushButton("➕ Добавить ключи")
        add_btn.clicked.connect(lambda: self.add_new_keys(keys_edit.toPlainText(), dialog))
        buttons_layout.addWidget(add_btn)
    
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
    
        layout.addLayout(buttons_layout)
    
        dialog.exec()
    
    def add_new_keys(self, keys_text, dialog):
        """Добавляет новые ключи в менеджер"""
        new_keys = [k.strip() for k in keys_text.splitlines() if k.strip()]
    
        if not new_keys:
            QtWidgets.QMessageBox.warning(dialog, "Ошибка", "Введите хотя бы один ключ")
            return
        
        # Добавляем ключи в менеджер
        added_count = 0
        for key in new_keys:
            if key not in self.api_key_manager.api_keys:
                self.api_key_manager.api_keys.append(key)
                self.api_key_manager.usage_counts[key] = 0
                self.api_key_manager.usage_limits[key] = 1000
                added_count += 1
            
        if added_count > 0:
            self.append_colored_log(f"✅ Добавлено {added_count} новых ключей", "#008800", True)
            dialog.accept()
        
            # Перезапускаем перевод
            self.restart_with_failed_items(quota_exceeded=True)
        else:
            QtWidgets.QMessageBox.information(dialog, "Информация", "Все введенные ключи уже есть в списке")

    def process_filtered_chapters(self):
        """Обрабатывает главы, заблокированные фильтрами контента"""
        if not self.content_filter_handler or not self.content_filter_handler.filtered_chapters:
            QtWidgets.QMessageBox.information(
                self,
                "Нет заблокированных глав",
                "Нет глав, заблокированных фильтрами контента."
            )
            return
        
        # Спрашиваем, какой метод использовать
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Выбор метода обработки")
        msg_box.setText(f"Найдено {len(self.content_filter_handler.filtered_chapters)} заблокированных глав.")
        msg_box.setInformativeText("Выберите метод обработки:")
    
        openrouter_btn = msg_box.addButton("OpenRouter (бесплатные модели)", QtWidgets.QMessageBox.ButtonRole.ActionRole)
        gemini_btn = msg_box.addButton("Gemini (альтернативные настройки)", QtWidgets.QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg_box.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
    
        msg_box.exec()
    
        if msg_box.clickedButton() == cancel_btn:
            return
        elif msg_box.clickedButton() == openrouter_btn:
            # Используем OpenRouter
        
            # Показываем диалог настройки
            settings_dialog = OpenRouterSettingsDialog(self)
            if settings_dialog.exec():
                settings = settings_dialog.get_settings()
                if settings['api_key']:
                    self.content_filter_handler.set_openrouter_settings(
                        settings['api_key'],
                        settings['model']
                    )
                    self.append_log(f"[INFO] OpenRouter настроен с моделью: {settings['model']}")
                else:
                    return
            else:
                return
        
            # Запускаем асинхронную обработку
            self.append_log("=" * 40)
            self.append_log(f"ОБРАБОТКА ЧЕРЕЗ OPENROUTER (модель: {settings['model']})")
            self.append_log("=" * 40)
        
            # Блокируем интерфейс
            self.set_controls_enabled(False)
        
            # Настраиваем прогресс-бар
            total_chapters = len(self.content_filter_handler.filtered_chapters)
            self.progress_bar.setRange(0, total_chapters)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%v / %m глав OpenRouter (%p%)")
        
            # Создаем воркер и поток
            self.openrouter_thread = QtCore.QThread()
            self.openrouter_worker = OpenRouterWorker(
                self.content_filter_handler.filtered_chapters,
                self.content_filter_handler.openrouter_translator,
                self.prompt_edit.toPlainText().strip(),
                self.out_folder,
                max_rpm=10  # Устанавливаем RPM лимит для OpenRouter
            )
        
            # Подключаем сигналы
            self.openrouter_worker.moveToThread(self.openrouter_thread)
            self.openrouter_worker.progress.connect(self.progress_bar.setValue)
            self.openrouter_worker.log_message.connect(self.append_log)
            self.openrouter_worker.finished.connect(self.on_openrouter_finished)
            self.openrouter_thread.started.connect(self.openrouter_worker.run)
        
            # Запускаем
            self.openrouter_thread.start()
        
        else:
            # Используем Gemini с альтернативными настройками (старый код)
            self.append_log("=" * 40)
            self.append_log("ОБРАБОТКА ЗАБЛОКИРОВАННЫХ ГЛАВ (GEMINI)")
            self.append_log("=" * 40)
        
            results = self.content_filter_handler.process_filtered_chapters(self.append_log)
        
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
        
            self.append_log("=" * 40)
            self.append_log(f"Результат: {success_count} успешно, {fail_count} с ошибками")
            self.append_log("=" * 40)
        
            QtWidgets.QMessageBox.information(
                self,
                "Результат",
                f"Обработка завершена:\n\n"
                f"Успешно: {success_count}\n"
                f"С ошибками: {fail_count}"
            )

    def append_colored_log(self, message, color=None, bold=False, icon=None):
        """Добавляет сообщение с заданным цветом и форматированием"""
        current_time = time.strftime("%H:%M:%S", time.localtime())
    
        # Добавляем иконку если указана
        if icon:
            message = f"{icon} {message}"
    
        formatted_line = f"[{current_time}] {message}"
    
        cursor = self.log_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
    
        if color or bold:
            html_line = "<span style='"
            if color:
                html_line += f"color: {color};"
            if bold:
                html_line += "font-weight: bold;"
            html_line += f"'>{formatted_line.replace('<', '&lt;').replace('>', '&gt;')}</span>"
        else:
            html_line = formatted_line.replace('<', '&lt;').replace('>', '&gt;')
    
        cursor.insertHtml(html_line + "<br>")
    
        # Прокручиваем к последней строке
        scrollbar = self.log_output.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def view_statistics(self):
        """Показывает статистику текущей сессии"""
        if not self.progress_monitor:
            if self.out_folder:
                self.progress_monitor = TranslationProgressMonitor(self.out_folder)
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Нет данных",
                    "Сначала выберите папку для перевода."
                )
                return
                
        report = self.progress_monitor.generate_report()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Статистика перевода")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QtGui.QFont("Consolas", 10))
        text_edit.setPlainText(report)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def open_epub_manager(self):
        """Открывает диалог управления сборкой EPUB."""
        if not self.out_folder:
            QMessageBox.warning(self, "Папка не выбрана", "Сначала выберите папку для перевода, где лежат готовые HTML-главы.")
            return
        try:
            dialog = TranslatedChaptersManagerDialog(self.out_folder, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть менеджер EPUB: {e}\n{traceback.format_exc()}")
    
    @QtCore.pyqtSlot(str)
    def update_concurrency_suggestion(self, model_display_name):
        """Обновляет рекомендуемое количество параллельных запросов на основе RPM модели"""
        default_value = 1
        tooltip_base = "Макс. одновременных запросов к API (для файлов и чанков)."
        tooltip_suffix = ""

        if model_display_name in MODELS:
            model_config = MODELS[model_display_name]
            model_rpm = model_config.get("rpm", 1)
        
            # Используем RPM напрямую без искусственных ограничений
            default_value = model_rpm
        
            tooltip_suffix = f"\nМодель: {model_display_name}\nЗаявленный RPM: {model_rpm}\nУстановлен лимит: {default_value}"
        else:
            tooltip_suffix = "\nНеизвестная модель."

        # Устанавливаем значение
        self.concurrency_spin.setValue(
            min(default_value, self.concurrency_spin.maximum())
        )
        self.concurrency_spin.setToolTip(tooltip_base + tooltip_suffix)

    @QtCore.pyqtSlot(str)
    def update_chunking_checkbox_suggestion(self, model_display_name):
        needs_chunking = False
        tooltip_text = f"Разделять файлы, превышающие ~{CHARACTER_LIMIT_FOR_CHUNK // 1000}k символов."
        if model_display_name in MODELS:
            needs_chunking = MODELS[model_display_name].get("needs_chunking", False)
            if needs_chunking:
                tooltip_text += "\nРЕКОМЕНДУЕТСЯ ВКЛЮЧИТЬ: Эта модель может иметь ограничение на длину ввода."
            else:
                tooltip_text += "\nМОЖНО ОСТАВИТЬ ВЫКЛЮЧЕННЫМ: Эта модель поддерживает длинный контекст."
        else:
            needs_chunking = True
            tooltip_text += "\nНеизвестная модель, чанкинг включен по умолчанию."
        if not CHUNK_HTML_SOURCE:
            tooltip_text += "\nЧанкинг HTML отключен (может повредить теги)."
        self.chunking_checkbox.setChecked(needs_chunking)
        self.chunking_checkbox.setToolTip(tooltip_text)

    def select_files(self):
        """Упрощенная версия - работает только с EPUB файлами"""
        last_dir = self.out_folder or QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.DocumentsLocation
        )
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы EPUB",
            last_dir,
            "EPUB files (*.epub);;All files (*)",
        )
        if not files:
            return

        if not BS4_AVAILABLE:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                "Для работы с EPUB необходима библиотека beautifulsoup4.\n"
                "Установите: pip install beautifulsoup4"
            )
            return

        new_files_data = []
        added_count = 0
        skipped_count = 0
        current_files_set = {(ft, p1, p2) for ft, p1, p2 in self.selected_files_data}

        for file_path in files:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != ".epub":
                self.append_log(
                    f"[WARN] Пропуск файла: {os.path.basename(file_path)} (только EPUB поддерживается)"
                )
                skipped_count += 1
                continue
            
            try:
                self.append_log(f"Анализ EPUB: {os.path.basename(file_path)}...")
                with zipfile.ZipFile(file_path, "r") as epub_zip:
                    html_files_in_epub = [
                        name
                        for name in epub_zip.namelist()
                        if name.lower().endswith((".html", ".xhtml", ".htm"))
                        and not name.startswith("__MACOSX")
                    ]
                    if not html_files_in_epub:
                        self.append_log(
                            f"[WARN] В EPUB '{os.path.basename(file_path)}' не найдено HTML/XHTML файлов."
                        )
                        skipped_count += 1
                        continue
                    
                    dialog = EpubHtmlSelectorDialog(
                        file_path, html_files_in_epub, self
                    )
                    if dialog.exec():
                        selected_html = dialog.get_selected_files()
                        if selected_html:
                            self.append_log(
                                f"Выбрано {len(selected_html)} HTML файлов из {os.path.basename(file_path)}:"
                            )
                            for html_path in selected_html:
                                file_tuple = ("epub", file_path, html_path)
                                if (
                                    file_tuple not in current_files_set
                                    and file_tuple not in new_files_data
                                ):
                                    new_files_data.append(file_tuple)
                                    self.append_log(f"  + {html_path}")
                                    added_count += 1
                                else:
                                    self.append_log(
                                        f"  - {html_path} (дубликат, пропущен)"
                                    )
                                    skipped_count += 1
                        else:
                            self.append_log(
                                f"HTML файлы не выбраны из {os.path.basename(file_path)}."
                            )
                            skipped_count += 1
                    else:
                        self.append_log(
                            f"Выбор HTML из {os.path.basename(file_path)} отменен."
                        )
                        skipped_count += 1
            except zipfile.BadZipFile:
                self.append_log(
                    f"[ERROR] Не удалось открыть EPUB: {os.path.basename(file_path)}. Файл поврежден или не является ZIP-архивом."
                )
                skipped_count += 1
            except Exception as e:
                self.append_log(
                    f"[ERROR] Ошибка обработки EPUB {os.path.basename(file_path)}: {e}"
                )
                skipped_count += 1

        if new_files_data:
            self.selected_files_data.extend(new_files_data)
            self.update_file_list_widget()
            log_message = f"Добавлено {added_count} файлов/частей."
            if skipped_count > 0:
                log_message += f" Пропущено {skipped_count} (дубликаты/ошибки)."
            self.append_log(log_message)
            self.retry_failed_btn.setVisible(False)
            self.export_failed_html_btn.setVisible(False)
            self.last_failed_items = []
        elif skipped_count > 0:
            self.append_log(
                f"Новые файлы не добавлены. Пропущено {skipped_count} (дубликаты/ошибки)."
            )
        else:
            self.append_log("Новые файлы не добавлены.")

    def update_file_list_widget(self):
        self.file_list_widget.clear()
        display_items = []

        def sort_key(item_tuple):
            file_type, path1, path2 = item_tuple
            if file_type == "epub":
                return (path1, extract_number_from_path(path2), path2)
            else:
                return (path1, 0, path1)

        sorted_data = sorted(self.selected_files_data, key=sort_key)
        self.selected_files_data = sorted_data

        for file_type, path1, path2 in self.selected_files_data:
            if file_type == "epub":
                display_items.append(f"{os.path.basename(path1)}  ->  {path2}")
            else:
                display_items.append(os.path.basename(path1))
        self.file_list_widget.addItems(display_items)
        self.file_list_widget.scrollToBottom()

    def clear_file_list(self):
        self.selected_files_data = []
        self.file_list_widget.clear()
        self.last_failed_items = []
        self.retry_failed_btn.setVisible(False)
        self.export_failed_html_btn.setVisible(False)
        self.append_log("Список файлов очищен.")

    def remove_selected_files_from_list(self):
        selected_qlist_items = self.file_list_widget.selectedItems()
        if not selected_qlist_items:
            self.append_log("Не выбрано элементов для удаления.")
            return
        selected_indices = sorted(
            [self.file_list_widget.row(item) for item in selected_qlist_items],
            reverse=True,
        )
        removed_count = 0
        for index in selected_indices:
            if 0 <= index < len(self.selected_files_data):
                self.selected_files_data.pop(index)
                removed_count += 1
        self.update_file_list_widget()
        self.append_log(f"Удалено {removed_count} элементов из списка.")
        if not self.selected_files_data:
            self.last_failed_items = []
            self.retry_failed_btn.setVisible(False)
            self.export_failed_html_btn.setVisible(False)

    def select_failed_items(self):
        if not self.last_failed_items:
            self.append_log("[WARN] Нет информации об ошибочных файлах для выбора.")
            return
        self.append_log(
            f"Очистка списка и выбор {len(self.last_failed_items)} ошибочных элементов из предыдущего запуска..."
        )
        self.selected_files_data = list(self.last_failed_items)
        self.update_file_list_widget()
        self.retry_failed_btn.setVisible(False)
        self.export_failed_html_btn.setVisible(False)
        self.append_log(
            "Ошибочные элементы выбраны. Нажмите 'Начать перевод' для повторной попытки."
        )

    def export_failed_html_files(self):
        failed_html_files = [
            item for item in self.last_failed_items if item[0] == "epub"
        ]

        if not failed_html_files:
            self.append_log("[INFO] Нет ошибочных HTML-файлов для экспорта.")
            QtWidgets.QMessageBox.information(
                self,
                "Нет файлов",
                "В последнем запуске не было ошибок, связанных с файлами HTML из EPUB.",
                QtWidgets.QMessageBox.StandardButton.Ok,
            )
            return

        save_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения исходных HTML с ошибками",
            self.out_folder or "",
        )
        if not save_dir:
            self.append_log("Экспорт отменен пользователем.")
            return

        self.append_log(
            f"--- Начало экспорта {len(failed_html_files)} исходных HTML с ошибками в папку: {save_dir} ---"
        )
        saved_count = 0
        failed_count = 0
        for file_type, epub_path, html_path_in_epub in failed_html_files:
            try:
                if not os.path.exists(epub_path):
                    self.append_log(
                        f"[ERROR] Не удалось найти исходный EPUB: {epub_path}"
                    )
                    failed_count += 1
                    continue

                epub_base_name = os.path.splitext(os.path.basename(epub_path))[0]
                html_filename_only = os.path.basename(html_path_in_epub)
                safe_html_name = re.sub(r'[\\/*?:"<>|]', "_", html_filename_only)
                output_filename = f"{epub_base_name}_{safe_html_name}"
                output_filepath = os.path.join(save_dir, output_filename)

                with zipfile.ZipFile(epub_path, "r") as epub_zip:
                    html_content_bytes = epub_zip.read(html_path_in_epub)

                with open(output_filepath, "wb") as out_f:
                    out_f.write(html_content_bytes)

                self.append_log(f"[SUCCESS] Сохранен исходный файл: {output_filename}")
                saved_count += 1

            except KeyError:
                self.append_log(
                    f"[ERROR] Файл '{html_path_in_epub}' не найден внутри EPUB '{epub_path}'."
                )
                failed_count += 1
            except Exception as e:
                self.append_log(
                    f"[ERROR] Не удалось сохранить '{html_path_in_epub}' из '{epub_path}': {e}"
                )
                failed_count += 1

        summary_message = f"Экспорт завершен. Успешно сохранено: {saved_count}. Ошибок: {failed_count}."
        self.append_log(f"--- {summary_message} ---")
        QtWidgets.QMessageBox.information(
            self,
            "Экспорт завершен",
            summary_message,
            QtWidgets.QMessageBox.StandardButton.Ok,
        )

    def open_glossary_editor(self):
        if not self.out_folder:
            QtWidgets.QMessageBox.warning(self, "Папка не выбрана", "Сначала выберите папку для перевода. Глоссарий будет сохранен там.")
            return

        # Убедимся, что менеджер контекста использует правильную папку
        if self.context_manager.output_folder != self.out_folder:
            self.context_manager = ContextManager(self.out_folder)
            self.append_log(f"Менеджер контекста переключен на папку: {self.out_folder}")
        
        self.context_manager.load_glossary()
        
        dialog = GlossaryEditorDialog(self.context_manager.get_glossary_as_json_str(), self)
        if dialog.exec():
            new_glossary_str = dialog.get_glossary_text()
            if self.context_manager.set_glossary_from_json_str(new_glossary_str):
                self.context_manager.save_glossary()
                self.append_log(f"Глоссарий успешно обновлен и сохранен в {self.context_manager.glossary_path}")
            else:
                self.append_log("[ERROR] Не удалось обновить глоссарий из-за ошибки в формате.")

    def select_output_folder(self):
        last_dir = self.out_folder or QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.DocumentsLocation
        )
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения переводов", last_dir
        )
        if path:
            self.out_folder = path
            self.out_lbl.setText(path)
            self.out_lbl.setCursorPosition(0)
            self.append_log(f"Папка вывода: {path}")
            # <<< КОНТЕКСТ: Обновляем путь в менеджере контекста
            self.context_manager = ContextManager(self.out_folder)
            self.append_log(f"Менеджер контекста настроен на папку: {self.out_folder}")
            if self.context_manager.load_glossary():
                self.append_log(f"Загружен существующий глоссарий: {self.context_manager.glossary_path}")

    @QtCore.pyqtSlot(str)

    def handle_log_message(self, message):
        self.append_log(message)

    def append_log(self, message):
        """Добавляет сообщение в лог с опциональной цветной подсветкой"""
        current_time = time.strftime("%H:%M:%S", time.localtime())
        message_str = str(message).strip()
    
        # Проверяем, включены ли цвета
        use_colors = hasattr(self, 'color_logs_checkbox') and self.color_logs_checkbox.isChecked()
    
        cursor = self.log_output.textCursor()
    
        for line in message_str.splitlines():
            color = None
            bold = False
        
            if use_colors:
                # Определяем цвет на основе типа сообщения
                line_upper = line.upper()
            
                if any(tag in line_upper for tag in ['[ERROR]', '[FAIL]', '[CRITICAL]', 'ОШИБКА', 'КРИТИЧЕСКАЯ']):
                    color = "#cc0000"  # Красный
                    bold = True
                elif any(tag in line_upper for tag in ['[WARN]', '[WARNING]', 'ПРЕДУПРЕЖДЕНИЕ', 'ВНИМАНИЕ']):
                    color = "#ff8800"  # Оранжевый  
                elif any(tag in line_upper for tag in ['[INFO]', '[DEBUG]', 'ИНФОРМАЦИЯ']):
                    color = "#666666"  # Серый
                elif any(tag in line_upper for tag in ['[SUCCESS]', 'УСПЕШНО', 'ГОТОВО', '✅']):
                    color = "#008800"  # Зелёный
                    bold = True
                elif any(tag in line_upper for tag in ['[CANCELLED]', '[SKIP]', 'ОТМЕНЕНО', 'ПРОПУЩЕНО']):
                    color = "#0088cc"  # Синий
                elif any(tag in line_upper for tag in ['[API BLOCK]', '[API STOP]', 'BLOCK_REASON', 'PROHIBITED_CONTENT']):
                    color = "#cc00cc"  # Фиолетовый
                    bold = True
                elif any(tag in line_upper for tag in ['[RATE LIMIT]', '429', 'QUOTA EXCEEDED', 'EXCEEDED YOUR CURRENT QUOTA']):
                    color = "#ff0066"  # Розовый
                    bold = True
                elif line.startswith("===") or line.startswith("---"):
                    color = "#0000cc"  # Синий для разделителей
                    bold = True
                elif "ИТОГ" in line or "НАЧАЛО ПЕРЕВОДА" in line or "ЗАВЕРШЕНО" in line:
                    color = "#000088"  # Тёмно-синий для важных заголовков
                    bold = True
        
            formatted_line = f"[{current_time}] {line}"
        
            if color or bold:
                html_line = "<span style='"
                if color:
                    html_line += f"color: {color};"
                if bold:
                    html_line += "font-weight: bold;"
                html_line += f"'>{formatted_line.replace('<', '&lt;').replace('>', '&gt;')}</span>"
            else:
                html_line = formatted_line.replace('<', '&lt;').replace('>', '&gt;')
        
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
            cursor.insertHtml(html_line + "<br>")
    
        scrollbar = self.log_output.verticalScrollBar()
        if scrollbar and scrollbar.value() >= scrollbar.maximum() - 30:
            scrollbar.setValue(scrollbar.maximum())

    # <<< ИЗМЕНЕНО: Метод теперь считывает новый чекбокс и передает его в Worker
    def start_translation(self):
        prompt_template = self.prompt_edit.toPlainText().strip()
        selected_model_name = self.model_combo.currentText()
        max_concurrency = self.concurrency_spin.value()
        temperature = self.temperature_spin.value()
        files_to_process = list(self.selected_files_data)
        chunking_enabled = self.chunking_checkbox.isChecked()
        post_delay_enabled = self.post_delay_checkbox.isChecked()
        use_system_instruction = self.system_instruction_checkbox.isChecked()

        # === ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===
        self.append_log(f"[DEBUG] Выбранная модель: {selected_model_name}")
        if hasattr(self, 'provider_combo'):
            self.append_log(f"[DEBUG] Выбранный провайдер: {self.provider_combo.currentText()}")

        # Проверка файлов
        if not files_to_process:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не выбраны файлы для перевода.")
            return
        if not self.out_folder:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не выбрана папка вывода.")
            return

        # Настройка контекст менеджера
        if self.context_manager.output_folder != self.out_folder:
            self.context_manager = ContextManager(self.out_folder)
    
        # Настройка динамического глоссария
        self.context_manager.use_dynamic_glossary = self.dynamic_glossary_checkbox.isChecked()
        if self.context_manager.use_dynamic_glossary:
            self.append_log("[INFO] Динамический глоссарий ВКЛЮЧЕН")
        else:
            self.append_log("[INFO] Динамический глоссарий ВЫКЛЮЧЕН")

        # Проверка папки вывода
        if not os.path.isdir(self.out_folder):
            reply = QtWidgets.QMessageBox.question(
                self,
                "Папка не существует",
                f"Папка '{self.out_folder}' не найдена или не является директорией. Создать?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.Yes,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    os.makedirs(self.out_folder, exist_ok=True)
                    self.append_log(f"Папка '{self.out_folder}' создана.")
                except OSError as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось создать папку: {e}")
                    return
            else:
                return

        # === ОПРЕДЕЛЕНИЕ ПРОВАЙДЕРА ===
        is_openrouter = False
        if hasattr(self, 'provider_combo'):
            is_openrouter = self.provider_combo.currentText() == "OpenRouter"
    
        # === ОПРЕДЕЛЕНИЕ КОНФИГУРАЦИИ МОДЕЛИ ===
        model_config = None
    
        if is_openrouter:
            # Для OpenRouter
            if 'OPENROUTER_MODELS' in globals() and selected_model_name in OPENROUTER_MODELS:
                model_config = OPENROUTER_MODELS[selected_model_name]
                self.append_log(f"[INFO] Используется OpenRouter модель: {model_config['id']}")
            else:
                # Если словарь не найден, используем захардкоженную конфигурацию
                self.append_log("[WARN] OPENROUTER_MODELS не найден, используем стандартную конфигурацию")
            
                # Определяем ID модели по названию
                model_id_map = {
                    "Dolphin Mistral 24B Venice (бесплатно)": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
                    "DeepSeek V3 Chat (бесплатно)": "deepseek/deepseek-chat-v3-0324:free",
                    "Qwen 2.5 72B (бесплатно)": "qwen/qwen-2.5-72b-instruct:free",
                    "Llama 3.1 8B (бесплатно)": "meta-llama/llama-3.1-8b-instruct:free",
                    "Gemma 2 9B (бесплатно)": "google/gemma-2-9b-it:free"
                }
            
                model_id = model_id_map.get(selected_model_name, "deepseek/deepseek-chat-v3-0324:free")
            
                model_config = {
                    "id": model_id,
                    "rpm": 20,
                    "rpd": 50,
                    "needs_chunking": True,
                    "post_request_delay": 3,
                    "provider": "openrouter"
                }
                self.append_log(f"[INFO] Используется OpenRouter модель: {model_config['id']}")
        else:
            # Для Gemini
            if selected_model_name not in MODELS:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    f"Некорректная модель выбрана: {selected_model_name}"
                )
                return
            model_config = MODELS[selected_model_name]

        # Проверка BeautifulSoup для EPUB
        needs_epub_html = any(ft == "epub" for ft, _, _ in files_to_process)
        if needs_epub_html and not BS4_AVAILABLE:
            QtWidgets.QMessageBox.critical(
                self, 
                "Ошибка", 
                "Выбраны EPUB файлы, но библиотека 'beautifulsoup4' не установлена.\n"
                "Установите: pip install beautifulsoup4"
            )
            return

        # Проверка промпта
        if "{text}" not in prompt_template:
            QtWidgets.QMessageBox.warning(
                self, 
                "Ошибка", 
                "Промпт должен содержать плейсхолдер `{text}` для вставки контента."
            )
            return

        # Проверка API ключей
        if not self.api_key_manager or not self.api_key_manager.api_keys:
            QtWidgets.QMessageBox.critical(
                self, 
                "Ошибка", 
                "Менеджер API ключей пуст. Пожалуйста, перезапустите программу и предоставьте хотя бы один ключ."
            )
            return

        # Проверка активного потока
        if self.thread_ref and self.thread_ref.isRunning():
            QtWidgets.QMessageBox.warning(
                self, 
                "Внимание", 
                "Процесс перевода уже запущен. Дождитесь завершения или отмените его."
            )
            return

        # Инициализация обработчика заблокированных глав
        if not hasattr(self, 'content_filter_handler') or not self.content_filter_handler:
            self.content_filter_handler = ContentFilterHandler(self.api_key_manager, self.context_manager)

        # Очистка интерфейса
        self.retry_failed_btn.setVisible(False)
        self.export_failed_html_btn.setVisible(False)
        self.log_output.clear()
    
        # Настройка прогресс-бара
        total_files = len(files_to_process)
        self.progress_bar.setRange(0, total_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v / %m заданий (%p%)")

        # Логирование начала
        self.append_log("=" * 40)
        self.append_log(f"НАЧАЛО ПЕРЕВОДА ({total_files} заданий)")
        self.append_log(f"Провайдер: {'OpenRouter' if is_openrouter else 'Google Gemini'}")
        self.append_log(f"Модель: {selected_model_name} ({model_config['id']})")
        self.append_log(f"Температура: {temperature}")
        self.append_log(f"Параллельных запросов: {max_concurrency}")
        self.append_log(f"Чанкинг включен в GUI: {'Да' if chunking_enabled else 'Нет'}")
    
        if not is_openrouter:
            self.append_log(f"Пост-задержка API: {'Включена' if post_delay_enabled else 'ОТКЛЮЧЕНА'}")
            self.append_log(f"Системные инструкции: {'Включены (экономия токенов)' if use_system_instruction else 'Выключены (классический режим)'}")
    
        self.append_log(f"Чанкинг HTML: {'Включен' if CHUNK_HTML_SOURCE else 'ОТКЛЮЧЕН'}")
        self.append_log(f"Папка вывода: {self.out_folder}")
        self.append_log(f"Поддержка EPUB/HTML: {'ДА' if BS4_AVAILABLE else 'НЕТ (библиотека не найдена)'}")
        self.append_log("=" * 40)
    
        # Блокировка интерфейса
        self.set_controls_enabled(False)

        # === СОЗДАНИЕ WORKER ===
        self.thread = QtCore.QThread()
    
        if is_openrouter:
            # === ИСПОЛЬЗУЕМ OpenRouterMainWorker ===
            self.append_log("[INFO] Используется OpenRouter Worker")
        
            # Проверяем класс OpenRouterMainWorker
            if 'OpenRouterMainWorker' not in globals():
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Класс OpenRouterMainWorker не найден. Проверьте, что он добавлен в код."
                )
                self.set_controls_enabled(True)
                return
        
            self.worker = OpenRouterMainWorker(
                api_key=self.api_key_manager.api_keys[0],  # Используем первый ключ
                out_folder=self.out_folder,
                prompt_template=prompt_template,
                files_to_process=files_to_process,
                model_config=model_config,
                max_concurrent_requests=20,  # Фиксированное для OpenRouter
                chunking_enabled_override=chunking_enabled,
                temperature=temperature,
                context_manager=self.context_manager
            )
        else:
            # === ИСПОЛЬЗУЕМ обычный Worker для Gemini ===
            self.append_log("[INFO] Используется Gemini Worker")
        
            self.worker = Worker(
                api_key_manager=self.api_key_manager,
                out_folder=self.out_folder,
                prompt_template=prompt_template,
                files_to_process=files_to_process,
                model_config=model_config,
                max_concurrent_requests=max_concurrency,
                chunking_enabled_override=chunking_enabled,
                temperature=temperature,
                post_delay_enabled=post_delay_enabled,
                use_system_instruction=use_system_instruction,
                context_manager=self.context_manager
            )

        # Настройка Worker
        self.worker.moveToThread(self.thread)
        self.worker_ref = self.worker
        self.thread_ref = self.thread
    
        # Подключение сигналов
        self.worker.progress.connect(self.update_progress)
        self.worker.log_message.connect(self.handle_log_message)
        self.worker.finished.connect(self.on_translation_finished)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
    
        # Установка content_filter_handler
        if hasattr(self.worker, 'content_filter_handler'):
            self.worker.content_filter_handler = self.content_filter_handler
    
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_worker_refs)
    
        # Запуск потока
        self.thread.start()
        self.append_log("Рабочий поток запущен...")

    @QtCore.pyqtSlot(int)
    def update_progress(self, processed_count):
        self.progress_bar.setValue(processed_count)

    def cancel_translation(self):
        """Отменяет текущий процесс перевода"""
        if self.worker_ref and self.thread_ref and self.thread_ref.isRunning():
            self.append_log("Отправка сигнала отмены...")
            self.worker_ref.cancel()
            self.cancel_btn.setEnabled(False)
            self.append_log("Ожидание завершения активных задач (может занять время)...")
        
            # Ждём завершения потока с таймаутом
            if not self.thread_ref.wait(5000):  # 5 секунд таймаут
                self.append_log("[WARN] Поток не завершился за 5 секунд, принудительное завершение...")
                self.thread_ref.terminate()
                self.thread_ref.wait()
            
            # Очищаем ссылки
            self.clear_worker_refs()
        else:
            self.append_log("[WARN] Нет активного процесса для отмены.")

    @QtCore.pyqtSlot(int, int, list, bool, object)
    def on_translation_finished(self, success_count, error_count, errors_data, quota_exceeded=False, failed_file=None):
        """Обработчик завершения перевода с поддержкой превышения квоты"""
        self.last_failed_items = []
        self.append_log("=" * 40)
        self.append_log(f"ИТОГ")
        self.append_log(f"Успешно: {success_count}")
        self.append_log(f"Ошибок/Отменено/Пропущено: {error_count}")
    
        if quota_exceeded:
            self.append_colored_log("⚠️ ПРЕВЫШЕНА КВОТА ТЕКУЩЕГО API КЛЮЧА", "#ff0066", True)
        
            # Проверяем, есть ли еще ключи для ротации
            if hasattr(self, 'api_key_manager') and hasattr(self.api_key_manager, 'api_keys'):
                current_usage = self.api_key_manager.get_usage_report()
                self.append_log(f"Статус ключей: {current_usage}")
            
                # Пытаемся получить следующий ключ
                try:
                    next_key = self.api_key_manager.get_next_available_key()
                    if next_key:
                        self.append_colored_log(f"🔄 Автоматическое переключение на следующий ключ: ...{next_key[-4:]}", "#0088cc", True)
                    
                        # НЕ закрываем окно, а перезапускаем с новым ключом
                        QtCore.QTimer.singleShot(2000, lambda: self.restart_with_failed_items(quota_exceeded=True))
                        return
                    else:
                        # Все ключи исчерпаны - предлагаем добавить новые
                        self.append_colored_log("❌ Все API ключи исчерпаны!", "#cc0000", True)
                        self.show_add_keys_dialog()
                        return
                except Exception as e:
                    self.append_log(f"[ERROR] Ошибка при переключении ключа: {e}")
                
        self.append_log("=" * 40)
    
        # Обработка ошибок
        has_failed_html = False
        content_filtered_count = 0
    
        if errors_data:
            self.append_log("Детали ошибок/отмен/пропусков:")
            max_err_display = 30
        
            for i, (file_info, error_message) in enumerate(errors_data):
                error_str = str(error_message)
            
                # Проверяем тип ошибки
                if any(indicator in error_str for indicator in ['PROHIBITED_CONTENT', 'block_reason', 'CONTENT_FILTER']):
                    content_filtered_count += 1
                    # НЕ добавляем в last_failed_items - они обрабатываются отдельно
                    continue
            
                # Добавляем в список для повторной попытки (кроме заблокированных)
                if "Требуется новый API ключ" not in error_str:
                    self.last_failed_items.append(file_info)
                
                file_type, path1, path2 = file_info
                if file_type == "epub":
                    has_failed_html = True

                base_src_path = ""
                if file_type == "epub":
                    base_src_path = f"{os.path.basename(path1)} -> {path2}"
                else:
                    base_src_path = os.path.basename(path1)
                
                if i < max_err_display:
                    log_entry = f"- {base_src_path}: {error_str[:300]}{'...' if len(error_str) > 300 else ''}"
                    self.append_log(log_entry)
                elif i == max_err_display:
                    self.append_log(f"- ... ({len(errors_data) - max_err_display} еще)")
                
            self.append_log("-" * 40)
        
            if content_filtered_count > 0:
                self.append_colored_log(
                    f"🚫 Заблокировано фильтрами: {content_filtered_count} глав (используйте OpenRouter)",
                    "#cc00cc", True
                )

            if self.last_failed_items:
                self.retry_failed_btn.setVisible(True)
                self.append_log("Доступна кнопка 'Выбрать только ошибочные' для повторной попытки.")
            
            if has_failed_html:
                self.export_failed_html_btn.setVisible(True)
                self.append_log("Доступна кнопка 'Сохранить HTML с ошибками' для анализа.")

        else:
            self.retry_failed_btn.setVisible(False)
            self.export_failed_html_btn.setVisible(False)

        # Проверяем наличие заблокированных глав
        if (hasattr(self, 'content_filter_handler') and 
            self.content_filter_handler and 
            self.content_filter_handler.filtered_chapters):
            self.process_filtered_btn.setVisible(True)
            self.append_log(f"Доступна кнопка 'Обработать заблокированные главы' ({len(self.content_filter_handler.filtered_chapters)} глав).")

        # Финальное сообщение
        final_message = ""
        msg_type = QtWidgets.QMessageBox.Icon.Information
        title = "Завершено"
        was_cancelled = self.worker_ref and self.worker_ref.is_cancelled
        total_tasks = self.progress_bar.maximum()

        if was_cancelled:
            title = "Отменено"
            msg_type = QtWidgets.QMessageBox.Icon.Warning
            final_message = f"Процесс перевода был отменен пользователем.\n\nУспешно до отмены: {success_count}\nОшибок/Пропущено/Отменено: {error_count}"
            if error_count > 0:
                final_message += "\n\nНажмите 'Выбрать только ошибочные' для повтора."
        elif error_count == 0 and success_count > 0:
            title = "Готово!"
            final_message = f"Перевод {success_count} заданий успешно завершен!"
        elif success_count > 0 and error_count > 0:
            title = "Завершено с ошибками/пропусками"
            msg_type = QtWidgets.QMessageBox.Icon.Warning
            final_message = f"Перевод завершен.\n\nУспешно: {success_count}\nОшибок/Отменено/Пропущено: {error_count}\n\nНажмите 'Выбрать только ошибочные' для повтора неудавшихся.\nСм. лог для деталей."
        elif success_count == 0 and error_count > 0:
            title = "Завершено с ошибками"
            msg_type = QtWidgets.QMessageBox.Icon.Critical
            final_message = f"Не переведено ни одного файла.\nОшибок/Отменено/Пропущено: {error_count}\n\nНажмите 'Выбрать только ошибочные' для повтора.\nСм. лог для деталей."
        elif success_count == 0 and error_count == 0 and total_tasks > 0:
            title = "Завершено"
            final_message = "Обработка завершена. Нет успешно переведенных файлов (все пропущены или отменены?)."
        elif total_tasks == 0:
            title = "Завершено"
            final_message = "Обработка завершена. Файлы не были выбраны для перевода."
        else:
            final_message = "Обработка завершена."
        
        if self.isVisible() and not quota_exceeded:
            QtWidgets.QMessageBox(msg_type, title, final_message, QtWidgets.QMessageBox.StandardButton.Ok, self).exec()

    def auto_retry_failed(self, max_retries=3):
        """Автоматически повторяет перевод неудачных глав"""
        if not self.last_failed_items or self.retry_count >= max_retries:
            return
        
        self.retry_count = getattr(self, 'retry_count', 0) + 1
        self.append_colored_log(
            f"🔄 Автоповтор #{self.retry_count} для {len(self.last_failed_items)} глав",
            "#0088cc", True
        )
    
        self.selected_files_data = list(self.last_failed_items)
        self.update_file_list_widget()
    
        # Запускаем перевод через 3 секунды
        QtCore.QTimer.singleShot(3000, self.start_translation)

    @QtCore.pyqtSlot()
    def clear_worker_refs(self):
        self.append_log("Фоновый поток завершен. Очистка ссылок...")
        self.worker = None
        self.thread = None
        self.worker_ref = None
        self.thread_ref = None
        self.set_controls_enabled(True)
        self.append_log("Интерфейс разблокирован.")

    def set_controls_enabled(self, enabled):
        widgets_to_toggle = [
            self.file_select_btn,
            self.clear_list_btn,
            self.remove_selected_btn,
            self.out_btn,
            self.out_lbl,
            self.model_combo,
            self.concurrency_spin,
            self.temperature_spin,
            self.chunking_checkbox,
            self.post_delay_checkbox,
            self.system_instruction_checkbox,
            self.manage_glossary_btn,
            self.prompt_edit,
            self.start_btn,
        ]
        for widget in widgets_to_toggle:
            if not isinstance(widget, QtWidgets.QLineEdit):
                widget.setEnabled(enabled)
            elif widget == self.out_lbl:
                self.out_btn.setEnabled(enabled)
        self.cancel_btn.setEnabled(not enabled)

        if not enabled:
            self.retry_failed_btn.setEnabled(False)
            self.export_failed_html_btn.setEnabled(False)
            self.process_filtered_btn.setEnabled(False)
            # Добавьте новые кнопки
            self.retry_openrouter_btn.setEnabled(False)
            self.select_openrouter_failed_btn.setEnabled(False)
            self.export_openrouter_failed_btn.setEnabled(False)
        else:
            self.retry_failed_btn.setEnabled(self.retry_failed_btn.isVisible())
            self.export_failed_html_btn.setEnabled(self.export_failed_html_btn.isVisible())
            self.process_filtered_btn.setEnabled(self.process_filtered_btn.isVisible())
            # Добавьте новые кнопки
            self.retry_openrouter_btn.setEnabled(self.retry_openrouter_btn.isVisible())
            self.select_openrouter_failed_btn.setEnabled(self.select_openrouter_failed_btn.isVisible())
            self.export_openrouter_failed_btn.setEnabled(self.export_openrouter_failed_btn.isVisible())

    def closeEvent(self, event: QtGui.QCloseEvent):
        is_running = self.thread_ref is not None and self.thread_ref.isRunning()
        if is_running:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Процесс выполняется",
                "Перевод все еще выполняется. Вы уверены, что хотите прервать процесс и выйти?",
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.append_log("Отмена перевода из-за закрытия окна...")
                self.cancel_translation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class ApiKeysDialog(QDialog):
    """Диалог для ввода API ключей"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите API ключи Gemini")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.keys = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Информация
        info_label = QLabel(
            "Введите один или несколько API ключей Google Gemini.\n"
            "Каждый ключ на новой строке.\n\n"
            "В параллельном режиме: каждый ключ = отдельное окно\n"
            "В гибридном режиме: ключи будут распределены между окнами"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Поле ввода ключей
        self.keys_edit = QTextEdit()
        self.keys_edit.setPlaceholderText(
            "Ключ1\n"
            "Ключ2\n"
            "Ключ3\n"
            "..."
        )
        self.keys_edit.setAcceptRichText(False)
        layout.addWidget(self.keys_edit)
        
        # Кнопка загрузки из файла
        load_button = QPushButton("📁 Загрузить ключи из файла .txt")
        load_button.clicked.connect(self.load_from_file)
        layout.addWidget(load_button)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        # Кнопки OK/Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_from_file(self):
        """Загружает ключи из текстового файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл с API ключами", 
            "", 
            "Text files (*.txt);;All files (*)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Разделяем по переносам строк и фильтруем пустые
                    keys_from_file = [
                        line.strip() 
                        for line in content.splitlines() 
                        if line.strip()
                    ]
                if keys_from_file:
                    self.keys_edit.setPlainText("\n".join(keys_from_file))
                    self.status_label.setText(
                        f"✅ Загружено {len(keys_from_file)} ключей из файла"
                    )
                    self.status_label.setStyleSheet("color: green;")
                else:
                    self.status_label.setText("⚠️ Файл пуст или не содержит ключей")
                    self.status_label.setStyleSheet("color: orange;")
            except Exception as e:
                self.status_label.setText(f"❌ Ошибка чтения файла: {e}")
                self.status_label.setStyleSheet("color: red;")
                
    def validate_and_accept(self):
        """Проверяет введенные ключи и закрывает диалог"""
        plain_text = self.keys_edit.toPlainText()
        self.keys = [
            key.strip() 
            for key in plain_text.splitlines() 
            if key.strip()
        ]
        
        if not self.keys:
            self.status_label.setText("❌ Ошибка: Не введено ни одного API ключа")
            self.status_label.setStyleSheet("color: red;")
            QtWidgets.QMessageBox.warning(
                self,
                "Нет ключей",
                "Пожалуйста, введите хотя бы один API ключ."
            )
            return
            
        # Проверяем на дубликаты
        unique_keys = list(set(self.keys))
        if len(unique_keys) < len(self.keys):
            duplicates = len(self.keys) - len(unique_keys)
            reply = QtWidgets.QMessageBox.question(
                self,
                "Обнаружены дубликаты",
                f"Обнаружено {duplicates} дублирующихся ключей.\n"
                "Использовать только уникальные ключи?",
                QtWidgets.QMessageBox.StandardButton.Yes |
                QtWidgets.QMessageBox.StandardButton.No
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.keys = unique_keys
                
        self.accept()
        
    def get_keys(self):
        """Возвращает список введенных ключей"""
        return self.keys

class OpenRouterSettingsDialog(QDialog):
    """Диалог для настройки OpenRouter API"""
    
    # Список бесплатных моделей OpenRouter с их характеристиками
    FREE_MODELS = {
        "DeepSeek V3 (рекомендуется, RPM: 10)": "deepseek/deepseek-chat-v3-0324:free",
        "Dolphin Mistral 24B Venice (новая, RPM: 10)": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "GLM-4.5-Air (Zhipu AI, RPM: 10)": "z-ai/glm-4.5-air:free",
        "Qwen 2.5 72B (RPM: 10)": "qwen/qwen-2.5-72b-instruct:free",
        "Llama 3.1 8B (RPM: 10)": "meta-llama/llama-3.1-8b-instruct:free",
        "Llama 3.2 3B (RPM: 10)": "meta-llama/llama-3.2-3b-instruct:free",
        "Llama 3.2 1B (RPM: 10)": "meta-llama/llama-3.2-1b-instruct:free",
        "Gemma 2 9B (RPM: 10)": "google/gemma-2-9b-it:free",
        "Phi-3 Mini (RPM: 10)": "microsoft/phi-3-mini-128k-instruct:free",
        "Phi-3 Medium (RPM: 10)": "microsoft/phi-3-medium-128k-instruct:free",
        "Mythomist 7B (RPM: 10)": "gryphe/mythomist-7b:free",
        "Другая модель (ввести вручную)": "custom"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка OpenRouter API")
        self.setMinimumSize(600, 450)
        self.api_key = None
        self.selected_model = "deepseek/deepseek-chat-v3-0324:free"
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Информация
        info_label = QLabel(
            "OpenRouter предоставляет доступ к бесплатным моделям AI\n"
            "для перевода глав, заблокированных фильтрами Gemini.\n\n"
            "Получите бесплатный API ключ на: https://openrouter.ai/keys\n"
            "(требуется регистрация)"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Поле ввода ключа
        key_layout = QtWidgets.QHBoxLayout()
        key_layout.addWidget(QLabel("API ключ:"))
        self.key_edit = QtWidgets.QLineEdit()
        self.key_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("sk-or-v1-...")
        key_layout.addWidget(self.key_edit)
        layout.addLayout(key_layout)
        
        # Выбор модели
        model_group = QGroupBox("Выбор модели")
        model_layout = QVBoxLayout(model_group)
        
        model_label = QLabel("Выберите бесплатную модель:")
        model_layout.addWidget(model_label)
        
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(self.FREE_MODELS.keys())
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        # Поле для ввода кастомной модели
        self.custom_model_edit = QtWidgets.QLineEdit()
        self.custom_model_edit.setPlaceholderText("Например: openai/gpt-3.5-turbo")
        self.custom_model_edit.setVisible(False)
        model_layout.addWidget(self.custom_model_edit)
        
        # Информация о выбранной модели
        self.model_info_label = QLabel("Модель: deepseek/deepseek-chat-v3-0324:free")
        self.model_info_label.setStyleSheet("color: blue; font-size: 10px;")
        model_layout.addWidget(self.model_info_label)
        
        layout.addWidget(model_group)
        
        # Чекбокс для сохранения
        self.save_checkbox = QCheckBox("Сохранить настройки для будущих сессий")
        self.save_checkbox.setChecked(True)
        layout.addWidget(self.save_checkbox)
        
        # Статус
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Попробуем загрузить сохраненные настройки
        self.load_saved_settings()
        
    def on_model_changed(self, text):
        """Обработка изменения выбранной модели"""
        model_id = self.FREE_MODELS.get(text, "custom")
    
        if model_id == "custom":
            self.custom_model_edit.setVisible(True)
            self.model_info_label.setText("Введите ID модели выше")
        else:
            self.custom_model_edit.setVisible(False)
            self.model_info_label.setText(f"Модель: {model_id}")
            self.selected_model = model_id
        
            # Добавляем специальную информацию для новой модели
            if "dolphin-mistral-24b-venice" in model_id:
                self.model_info_label.setText(
                    f"Модель: {model_id}\n"
                    "Venice Edition - улучшенная версия для литературных переводов"
                )
                self.model_info_label.setStyleSheet("color: green; font-size: 10px;")
            
    def load_saved_settings(self):
        """Загружает сохраненные настройки из файла"""
        config_file = os.path.join(os.path.expanduser("~"), ".epub_translator_openrouter.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    if 'api_key' in data:
                        self.key_edit.setText(data['api_key'])
                    if 'model' in data:
                        # Найти модель в комбобоксе
                        for name, model_id in self.FREE_MODELS.items():
                            if model_id == data['model']:
                                self.model_combo.setCurrentText(name)
                                break
                        else:
                            # Если модель не найдена в списке, установить кастомную
                            self.model_combo.setCurrentText("Другая модель (ввести вручную)")
                            self.custom_model_edit.setText(data['model'])
                            self.custom_model_edit.setVisible(True)
                    self.status_label.setText("✅ Загружены сохраненные настройки")
                    self.status_label.setStyleSheet("color: green;")
            except:
                pass
                
    def save_settings(self):
        """Сохраняет настройки в файл"""
        if self.save_checkbox.isChecked():
            config_file = os.path.join(os.path.expanduser("~"), ".epub_translator_openrouter.json")
            try:
                with open(config_file, 'w') as f:
                    json.dump({
                        'api_key': self.api_key,
                        'model': self.selected_model
                    }, f)
            except:
                pass
                
    def validate_and_accept(self):
        """Проверяет введенные данные"""
        key = self.key_edit.text().strip()
        if not key:
            self.status_label.setText("❌ Введите API ключ")
            self.status_label.setStyleSheet("color: red;")
            return
            
        # Определяем выбранную модель
        current_text = self.model_combo.currentText()
        model_id = self.FREE_MODELS.get(current_text, "custom")
        
        if model_id == "custom":
            custom_model = self.custom_model_edit.text().strip()
            if not custom_model:
                self.status_label.setText("❌ Введите ID модели")
                self.status_label.setStyleSheet("color: red;")
                return
            self.selected_model = custom_model
        else:
            self.selected_model = model_id
            
        self.api_key = key
        self.save_settings()
        self.accept()
        
    def get_settings(self):
        """Возвращает настройки"""
        return {
            'api_key': self.api_key,
            'model': self.selected_model
        }

def main():
    """Точка входа с выбором режима работы"""
    parser = argparse.ArgumentParser(
        description="EPUB Translator with Multiple Modes"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Возобновить прерванную сессию перевода"
    )
    parser.add_argument(
        "--session-file",
        help="Путь к файлу сессии для возобновления"
    )
    parser.add_argument(
        "--mode",
        choices=['auto', 'parallel', 'hybrid'],
        default=None,
        help="Режим работы: auto (автоматическая ротация), parallel (параллельные окна), hybrid (гибридный)"
    )
    args = parser.parse_args()
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Проверка обязательной библиотеки
    if not BS4_AVAILABLE:
        QtWidgets.QMessageBox.critical(
            None,
            "Отсутствует обязательная библиотека",
            "Для работы программы необходима библиотека beautifulsoup4.\n"
            "Установите её командой: pip install beautifulsoup4"
        )
        sys.exit(1)
    
    # Если указан флаг возобновления
    if args.resume:
        session_file = args.session_file or 'translation_session.json'
        if os.path.exists(session_file):
            print(f"Возобновление сессии из: {session_file}")
            run_translation_with_auto_restart()
        else:
            QtWidgets.QMessageBox.critical(
                None,
                "Ошибка",
                f"Файл сессии не найден: {session_file}"
            )
            sys.exit(1)
    else:
        # Выбор режима работы
        selected_mode = args.mode
        
        if not selected_mode:
            # Показываем диалог выбора режима
            mode_dialog = TranslationModeDialog()
            if not mode_dialog.exec():
                print("Выбор режима отменен пользователем")
                sys.exit(0)
            selected_mode = mode_dialog.selected_mode
        
        print(f"Выбран режим: {selected_mode}")
        
        if selected_mode == 'auto_rotation' or selected_mode == 'auto':
            # Режим с автоматической ротацией ключей
            setup_dialog = InitialSetupDialog()
            if setup_dialog.exec():
                settings = setup_dialog.get_settings()
                
                # Проверяем, что выбран EPUB файл
                if not settings['file_path'].lower().endswith('.epub'):
                    QtWidgets.QMessageBox.critical(
                        None,
                        "Ошибка",
                        "Программа поддерживает только EPUB файлы.\n"
                        "Выберите файл с расширением .epub"
                    )
                    sys.exit(1)
                
                print(f"Запуск перевода с автоматической ротацией:")
                print(f"  EPUB файл: {settings['file_path']}")
                print(f"  Папка вывода: {settings['output_folder']}")
                print(f"  Количество ключей: {len(settings['api_keys'])}")
                print(f"  Модель: {settings['model']}")
                
                # Запускаем процесс перевода с автоматической ротацией
                run_translation_with_auto_restart(settings)
            else:
                print("Настройка отменена пользователем")
                sys.exit(0)
               
        elif selected_mode == 'hybrid':
            # Гибридный режим
            QtWidgets.QMessageBox.information(
                None,
                "Гибридный режим",
                "Гибридный режим находится в разработке.\n"
                "Используйте параллельный режим с автоматическим распределением глав."
            )
    
            # Переключаемся на параллельный режим
            selected_mode = 'parallel'
               
        elif selected_mode == 'parallel':
            # Параллельный режим
    
            # Диалог для ввода ключей
            keys_dialog = ApiKeysDialog()
            if not keys_dialog.exec():
                print("Ввод ключей отменен")
                sys.exit(0)
    
            api_keys = keys_dialog.get_keys()
            if not api_keys:
                QtWidgets.QMessageBox.critical(
                    None,
                    "Ошибка",
                    "Не введены API ключи"
                )
                sys.exit(1)
    
            print(f"Получено {len(api_keys)} ключей")
    
            # Спрашиваем, какой вариант параллельного режима
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Выбор варианта параллельного режима")
            msg_box.setText("Выберите вариант работы:")
    
            auto_btn = msg_box.addButton(
                "Автоматическая настройка (рекомендуется)",
                QtWidgets.QMessageBox.ButtonRole.ActionRole
            )
            manual_btn = msg_box.addButton(
                "Ручная настройка каждого окна",
                QtWidgets.QMessageBox.ButtonRole.ActionRole
            )
            cancel_btn = msg_box.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
    
            msg_box.exec()
    
            if msg_box.clickedButton() == cancel_btn:
                print("Выбор отменен")
                sys.exit(0)
        
            elif msg_box.clickedButton() == auto_btn:
                # АВТОМАТИЧЕСКАЯ НАСТРОЙКА
                print("Выбран режим автоматической настройки")
        
                # Показываем диалог настройки
                setup_dialog = ParallelModeSetupDialog(api_keys)
                if not setup_dialog.exec():
                    print("Настройка отменена")
                    sys.exit(0)
            
                settings = setup_dialog.get_settings()
                if not settings:
                    print("Настройки не получены")
                    sys.exit(1)
            
                print(f"Запуск {len(settings['distributions'])} окон с автоматическим распределением глав")
        
                # Создаем окна с предустановленными настройками
                windows = []

                for i, distribution in enumerate(settings['distributions']):
                    # Создаем менеджер с одним ключом
                    key_manager = ApiKeyManager([distribution['api_key']])

                    # Создаем окно переводчика
                    translator_window = TranslatorApp(key_manager)

                    # Настраиваем заголовок
                    translator_window.setWindowTitle(
                        f"EPUB Translator - Окно #{distribution['window_id']} "
                        f"(Главы {distribution['start']+1}-{distribution['end']})"
                    )

                    # Применяем настройки
                    translator_window.out_folder = settings['output_folder']
                    translator_window.out_lbl.setText(settings['output_folder'])

                    # Обновляем контекст менеджер
                    translator_window.context_manager = ContextManager(settings['output_folder'])
    
                    # === НОВОЕ: Настраиваем динамический глоссарий ===
                    if settings.get('dynamic_glossary', True):
                        translator_window.context_manager.use_dynamic_glossary = True
                        translator_window.dynamic_glossary_checkbox.setChecked(True)  # Обновляем UI
                        print(f"Окно #{distribution['window_id']}: Динамический глоссарий ВКЛЮЧЕН")

                    # Загружаем глоссарий из словаря (вместо файла)
                    if settings.get('glossary_dict'):
                        translator_window.context_manager.global_glossary = settings['glossary_dict']
                        translator_window.context_manager.save_glossary()
                        print(f"Загружен глоссарий: {len(settings['glossary_dict'])} терминов")
    
                    # Устанавливаем настройки перевода
                    translator_window.model_combo.setCurrentText(settings['model'])
                    translator_window.concurrency_spin.setValue(settings['concurrent_requests'])
                    translator_window.temperature_spin.setValue(settings['temperature'])
                    translator_window.chunking_checkbox.setChecked(settings['chunking'])
                    
                    # Устанавливаем кастомный промпт если указан
                    if settings.get('custom_prompt'):
                        translator_window.prompt_edit.setPlainText(settings['custom_prompt'])
                        print(f"Окно #{distribution['window_id']}: Установлен кастомный промпт")

                    # Загружаем назначенные главы
                    translator_window.selected_files_data = [
                        ('epub', settings['file_path'], chapter)
                        for chapter in distribution['chapters']
                    ]
                    translator_window.update_file_list_widget()

                    # Позиционируем окна каскадом
                    base_x = 50
                    base_y = 50
                    offset = 30
                    translator_window.move(base_x + (i * offset), base_y + (i * offset))

                    # Показываем окно
                    translator_window.show()
                    windows.append(translator_window)

                    print(f"Окно #{distribution['window_id']}: "
                          f"{len(distribution['chapters'])} глав, "
                          f"ключ ...{distribution['api_key'][-4:]}")

                    # Автозапуск если включен
                    if settings['auto_start']:
                        # Определяем задержку между запусками на основе модели
                        model_rpm = MODELS.get(settings['model'], {}).get('rpm', 10)
    
                        # Вычисляем безопасную задержку между запусками окон
                        if model_rpm <= 5:  # Gemini 2.5 Pro
                            delay_between_windows = 15000  # 15 секунд между окнами
                            initial_delay = 2000  # 2 секунды до первого окна
                        elif model_rpm <= 10:  # Gemini 2.5 Flash
                            delay_between_windows = 6000  # 6 секунд между окнами
                            initial_delay = 1500
                        else:  # Gemini 2.0 Flash (15 RPM)
                            delay_between_windows = 4000  # 4 секунды между окнами
                            initial_delay = 1000
    
                        # Запускаем окна с задержками
                        for i, window in enumerate(windows):
                            start_delay = initial_delay + (i * delay_between_windows)
                            QtCore.QTimer.singleShot(start_delay, window.start_translation)
        
                            # Логируем план запуска
                            print(f"Окно #{i+1} запустится через {start_delay/1000:.1f} секунд")
    
                        # Показываем информационное сообщение
                        total_time = (initial_delay + (len(windows) - 1) * delay_between_windows) / 1000
                        QtWidgets.QMessageBox.information(
                            None,
                            "Параллельный режим запущен",
                            f"Открыто {len(windows)} окон.\n\n"
                            f"Модель: {settings['model']} (RPM: {model_rpm})\n"
                            f"Окна будут запускаться последовательно\n"
                            f"с интервалом {delay_between_windows/1000} секунд.\n\n"
                            f"Общее время запуска: ~{total_time:.1f} секунд\n"
                            f"Это предотвратит превышение лимитов API."
                        )
                
                # Информационное сообщение
                if settings['auto_start']:
                    QtWidgets.QMessageBox.information(
                        None,
                        "Параллельный режим запущен",
                        f"Открыто {len(windows)} окон.\n\n"
                        f"Перевод запущен автоматически.\n"
                        f"Каждое окно обрабатывает свою часть глав.\n\n"
                        f"Общее количество глав: {sum(len(d['chapters']) for d in settings['distributions'])}"
                    )
                else:
                    QtWidgets.QMessageBox.information(
                        None,
                        "Параллельный режим готов",
                        f"Открыто {len(windows)} окон.\n\n"
                        f"Главы распределены между окнами.\n"
                        f"Запустите перевод в каждом окне вручную.\n\n"
                        f"Общее количество глав: {sum(len(d['chapters']) for d in settings['distributions'])}"
                    )
            
            else:
                # РУЧНАЯ НАСТРОЙКА (старый код)
                print("Выбран режим ручной настройки")
                print("Открываем окна для каждого ключа...")
        
                # Создаем список окон
                windows = []
        
                for i, api_key in enumerate(api_keys):
                    # Создаем менеджер с одним ключом
                    key_manager = ApiKeyManager([api_key])
            
                    # Создаем окно переводчика
                    translator_window = TranslatorApp(key_manager)
            
                    # Настраиваем заголовок окна
                    translator_window.setWindowTitle(
                        f"EPUB Translator - Окно #{i+1} (Ключ ...{api_key[-4:]})"
                    )
            
                    # Позиционируем окна каскадом
                    base_x = 100
                    base_y = 100
                    offset = 30
                    translator_window.move(base_x + (i * offset), base_y + (i * offset))
            
                    # Показываем окно
                    translator_window.show()
                    windows.append(translator_window)
            
                    print(f"Окно #{i+1} открыто с ключом ...{api_key[-4:]}")
        
                # Информационное сообщение
                QtWidgets.QMessageBox.information(
                    None,
                    "Параллельный режим (ручная настройка)",
                    f"Открыто {len(windows)} окон.\n\n"
                    "Каждое окно работает независимо со своим API ключом.\n"
                    "Вы можете:\n"
                    "• Загрузить один и тот же EPUB в каждое окно\n"
                    "• Выбрать разные главы для перевода в каждом окне\n"
                    "• Запустить перевод независимо в каждом окне\n\n"
                    "Это позволит переводить разные части книги параллельно."
                )
        
            # Запускаем главный цикл приложения
            sys.exit(app.exec())


def run_worker_instance(settings):
    """Запускает отдельный экземпляр воркера для параллельного режима"""
    try:
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(sys.argv)
        
        # Создаем менеджер ключей с одним ключом
        api_key_manager = ApiKeyManager(settings['api_keys'])
        
        # Создаем окно переводчика
        translator = TranslatorApp(api_key_manager)
        translator.setWindowTitle(
            f"EPUB Translator - Worker #{settings.get('worker_id', 1)}"
        )
        
        # Устанавливаем настройки
        translator.out_folder = settings['output_folder']
        translator.out_lbl.setText(settings['output_folder'])
        
        # Загружаем только назначенные главы
        if 'chapters' in settings:
            translator.selected_files_data = [
                ('epub', settings['file_path'], chapter)
                for chapter in settings['chapters']
            ]
            translator.update_file_list_widget()
        
        # Автоматически запускаем перевод
        QtCore.QTimer.singleShot(1000, translator.start_translation)
        
        translator.show()
        app.exec()
        
    except Exception as e:
        print(f"Ошибка в воркере: {e}")
        traceback.print_exc()


if __name__ == "__main__":

    def excepthook(exc_type, exc_value, exc_tb):
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        error_message = f"Неперехваченная глобальная ошибка:\n\n{exc_type.__name__}: {exc_value}\n\nTraceback:\n{tb_str}"
        print(f"КРИТИЧЕСКАЯ ОШИБКА (Unhandled Exception):\n{error_message}")
        try:
            if QtWidgets.QApplication.instance():
                QtWidgets.QMessageBox.critical(
                    None, "Критическая Ошибка Приложения", error_message
                )
            else:
                print(
                    "QApplication not running, cannot show MessageBox for critical error."
                )
        except Exception as mb_error:
            print(f"Не удалось показать MessageBox для критической ошибки: {mb_error}")
        sys.exit(1)

    sys.excepthook = excepthook
    try:
        main()
    except SystemExit:
        pass
    except Exception as e:
        error_message = f"Критическая ошибка во время запуска:\n\n{type(e).__name__}: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"КРИТИЧЕСКАЯ ОШИБКА ЗАПУСКА:\n{error_message}")
        try:
            app_launch_error = (
                QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            )
            QtWidgets.QMessageBox.critical(
                None, "Критическая Ошибка Запуска", error_message
            )
        except Exception as mb_error:
            print(f"Не удалось показать MessageBox для ошибки запуска: {mb_error}")
        sys.exit(1)