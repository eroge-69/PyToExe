import os
import sys
import subprocess
import importlib

# Список необходимых библиотек
required_libraries = [
    'psutil',
    'python-dotenv',
    'PIL'
]

# Проверяем и устанавливаем отсутствующие библиотеки
def install_missing_libraries():
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Установка отсутствующей библиотеки: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Устанавливаем недостающие библиотеки
install_missing_libraries()

# Теперь импортируем все библиотеки
import time
import threading
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import psutil
import shutil
import logging
from typing import Optional, Dict, List, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GameTracker")

load_dotenv()

class GameDatabase:
    def __init__(self, db_name="game_sessions.db"):
        self.db_name = db_name
        self.backup_db_name = f"backup_{db_name}"
        self.init_database()
        self.create_backup()
    
    def create_backup(self):
        """Создает резервную копию базы данных"""
        try:
            if os.path.exists(self.db_name):
                shutil.copy2(self.db_name, self.backup_db_name)
                logger.info("Создана резервная копия базы данных")
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии: {e}")
    
    def restore_backup(self):
        """Восстанавливает базу данных из резервной копии"""
        try:
            if os.path.exists(self.backup_db_name):
                shutil.copy2(self.backup_db_name, self.db_name)
                logger.info("База данных восстановлена из резервной копии")
                return True
        except Exception as e:
            logger.error(f"Ошибка при восстановлении из резервной копии: {e}")
        return False
    
    def init_database(self):
        """Инициализирует базу данных и создает таблицы, если они не существуют"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Включаем WAL mode для лучшей производительности и надежности
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # Таблица игровых сессий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration INTEGER,
                    process_name TEXT
                )
            ''')
            
            # Таблица для настройки сопоставления процессов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_mapping (
                    process_name TEXT PRIMARY KEY,
                    game_name TEXT NOT NULL,
                    platform TEXT NOT NULL
                )
            ''')
            
            # Таблица статистики по играм
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats (
                    game_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    total_sessions INTEGER DEFAULT 0,
                    total_playtime INTEGER DEFAULT 0,
                    last_played DATETIME,
                    first_played DATETIME,
                    PRIMARY KEY (game_name, platform)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            # Пытаемся восстановить из резервной копии
            if self.restore_backup():
                self.init_database()
    
    def save_session(self, game_name: str, platform: str, start_time: str, 
                    end_time: Optional[str], duration: int, process_name: Optional[str] = None):
        """Сохраняет игровую сессию в базу данных и обновляет статистику"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Сохраняем сессию
            cursor.execute('''
                INSERT INTO game_sessions (game_name, platform, start_time, end_time, duration, process_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (game_name, platform, start_time, end_time, duration, process_name))
            
            # Обновляем статистику игры
            cursor.execute('''
                INSERT OR REPLACE INTO game_stats (game_name, platform, total_sessions, total_playtime, last_played, first_played)
                VALUES (
                    ?, 
                    ?, 
                    COALESCE((SELECT total_sessions FROM game_stats WHERE game_name = ? AND platform = ?), 0) + 1,
                    COALESCE((SELECT total_playtime FROM game_stats WHERE game_name = ? AND platform = ?), 0) + ?,
                    ?,
                    COALESCE((SELECT first_played FROM game_stats WHERE game_name = ? AND platform = ?), ?)
                )
            ''', (game_name, platform, game_name, platform, game_name, platform, duration, 
                 end_time, game_name, platform, start_time))
            
            conn.commit()
            conn.close()
            logger.info(f"Сохранена сессия: {game_name} ({platform}) - {duration} минут")
        except Exception as e:
            logger.error(f"Ошибка при сохранении сессии: {e}")
            # Пытаемся восстановить из резервной копии и повторить
            if self.restore_backup():
                self.save_session(game_name, platform, start_time, end_time, duration, process_name)
    
    def get_game_stats(self, game_name: str, platform: str):
        """Получает статистику по игре"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT total_sessions, total_playtime, last_played, first_played 
                FROM game_stats 
                WHERE game_name = ? AND platform = ?
            ''', (game_name, platform))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_sessions': result[0],
                    'total_playtime': result[1],
                    'last_played': result[2],
                    'first_played': result[3]
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики игры: {e}")
        return {
            'total_sessions': 0,
            'total_playtime': 0,
            'last_played': None,
            'first_played': None
        }
    
    def get_session_history(self, limit: int = 50):
        """Получает историю игровых сессий"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT game_name, platform, start_time, end_time, duration 
                FROM game_sessions 
                ORDER BY start_time DESC 
                LIMIT ?
            ''', (limit,))
            
            sessions = cursor.fetchall()
            conn.close()
            return sessions
        except Exception as e:
            logger.error(f"Ошибка при получении истории сессий: {e}")
            return []
    
    def get_process_mappings(self):
        """Получает все сопоставления процессов"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT process_name, game_name, platform FROM process_mapping')
            mappings = cursor.fetchall()
            conn.close()
            
            return {row[0]: {'game_name': row[1], 'platform': row[2]} for row in mappings}
        except Exception as e:
            logger.error(f"Ошибка при получении сопоставлений процессов: {e}")
            return {}
    
    def add_process_mapping(self, process_name: str, game_name: str, platform: str):
        """Добавляет новое сопоставление процесса"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO process_mapping (process_name, game_name, platform)
                VALUES (?, ?, ?)
            ''', (process_name, game_name, platform))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении сопоставления процесса: {e}")
            return False
    
    def delete_process_mapping(self, process_name: str):
        """Удаляет сопоставление процесса"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM process_mapping WHERE process_name = ?', (process_name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении сопоставления процесса: {e}")
            return False
    
    def update_process_mapping(self, old_process_name: str, new_process_name: str, game_name: str, platform: str):
        """Обновляет существующее сопоставление процесса"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Сначала удаляем старую запись
            cursor.execute('DELETE FROM process_mapping WHERE process_name = ?', (old_process_name,))
            
            # Затем добавляем новую
            cursor.execute('''
                INSERT INTO process_mapping (process_name, game_name, platform)
                VALUES (?, ?, ?)
            ''', (new_process_name, game_name, platform))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении сопоставления процесса: {e}")
            return False

class GameTracker:
    def __init__(self, db: GameDatabase):
        self.db = db
        self.process_mappings = self.db.get_process_mappings()
        self.last_detected_game = None
        self.last_detected_platform = None
        self.current_session_start = None
    
    def detect_game(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Обнаруживает текущую игру по запущенным процессам"""
        try:
            for proc in psutil.process_iter(['name']):
                process_name = proc.info['name'].lower()
                
                # Проверяем сопоставления процессов
                for mapped_process, game_info in self.process_mappings.items():
                    if mapped_process in process_name:
                        return game_info['game_name'], game_info['platform'], mapped_process
                    
        except Exception as e:
            logger.error(f"Ошибка при обнаружении процессов: {e}")
        
        return None, None, None
    
    def update(self):
        """Обновляет статус текущей игры"""
        game_name, platform, process_name = self.detect_game()
        
        # Если игра изменилась
        if game_name != self.last_detected_game or platform != self.last_detected_platform:
            # Завершаем предыдущую сессию
            if self.last_detected_game and self.current_session_start:
                end_time = datetime.now()
                duration = int((end_time - self.current_session_start).total_seconds() / 60)  # в минутах
                
                # Сохраняем сессию в базу данных
                self.db.save_session(
                    self.last_detected_game, 
                    self.last_detected_platform,
                    self.current_session_start.strftime("%Y-%m-%d %H:%M:%S"),
                    end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    duration,
                    None
                )
            
            # Начинаем новую сессию
            if game_name:
                self.current_session_start = datetime.now()
                logger.info(f"Начата новая сессия: {game_name} ({platform})")
            else:
                self.current_session_start = None
            
            # Обновляем последнюю обнаруженную игру
            self.last_detected_game = game_name
            self.last_detected_platform = platform
            
            return game_name, platform
        
        return None, None

class GameTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Tracker")
        self.root.geometry("1200x500")
        self.root.resizable(True, True)
        
        # Инициализация базы данных
        self.db = GameDatabase()
        self.game_tracker = GameTracker(self.db)
        
        # Переменные для хранения данных
        self.is_tracking = False
        self.tracking_thread = None
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Запускаем отслеживание при старте
        self.toggle_tracking()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Game Tracker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Область для отображения текущей игры
        self.game_frame = ttk.LabelFrame(main_frame, text="Текущая игра", padding="10")
        self.game_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        self.game_frame.columnconfigure(1, weight=1)
        
        # Платформа игры
        self.platform_var = tk.StringVar(value="Платформа: -")
        platform_label = ttk.Label(self.game_frame, textvariable=self.platform_var, font=("Arial", 10))
        platform_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Название игры
        self.game_name_var = tk.StringVar(value="Не играете")
        game_name_label = ttk.Label(self.game_frame, textvariable=self.game_name_var, font=("Arial", 12, "bold"))
        game_name_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # Статистика игры
        self.stats_var = tk.StringVar(value="Статистика: загрузка...")
        stats_label = ttk.Label(self.game_frame, textvariable=self.stats_var)
        stats_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Текущая сессия
        self.session_var = tk.StringVar(value="Текущая сессия: -")
        session_label = ttk.Label(self.game_frame, textvariable=self.session_var)
        session_label.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        # Статус отслеживания
        self.status_var = tk.StringVar(value="Статус: Не активно")
        status_label = ttk.Label(self.game_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.toggle_button = ttk.Button(buttons_frame, text="Остановить отслеживание", command=self.toggle_tracking)
        self.toggle_button.grid(row=0, column=0, padx=(0, 10))
        
        refresh_button = ttk.Button(buttons_frame, text="Обновить сейчас", command=self.manual_update)
        refresh_button.grid(row=0, column=1, padx=(0, 10))
        
        history_btn = ttk.Button(buttons_frame, text="История сессий", command=self.show_history)
        history_btn.grid(row=0, column=2, padx=(0, 10))
        
        stats_btn = ttk.Button(buttons_frame, text="Статистика игр", command=self.show_game_stats)
        stats_btn.grid(row=0, column=3, padx=(0, 10))
        
        process_btn = ttk.Button(buttons_frame, text="Управление процессами", command=self.show_process_manager)
        process_btn.grid(row=0, column=4, padx=(0, 10))
        
        backup_btn = ttk.Button(buttons_frame, text="Создать бэкап", command=self.create_backup)
        backup_btn.grid(row=0, column=5, padx=(0, 10))
        
        exit_button = ttk.Button(buttons_frame, text="Выход", command=self.exit_app)
        exit_button.grid(row=0, column=6)
        
        # История игровых сессий
        history_frame = ttk.LabelFrame(main_frame, text="Последние сессии", padding="10")
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Таблица истории
        columns = ("time", "platform", "game", "duration")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("platform", text="Платформа")
        self.history_tree.heading("game", text="Игра")
        self.history_tree.heading("duration", text="Длительность")
        
        self.history_tree.column("time", width=120)
        self.history_tree.column("platform", width=100)
        self.history_tree.column("game", width=200)
        self.history_tree.column("duration", width=80)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Настройка расширения колонок
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def update_game_info(self):
        game_name, platform = self.game_tracker.update()
        
        # Если игра изменилась
        if game_name:
            self.game_name_var.set(game_name)
            self.platform_var.set(f"Платформа: {platform}")
            
            # Получаем статистику по игре
            stats = self.db.get_game_stats(game_name, platform)
            total_hours = stats['total_playtime'] // 60
            total_minutes = stats['total_playtime'] % 60
            self.stats_var.set(f"Запусков: {stats['total_sessions']}, Всего времени: {total_hours}ч {total_minutes}м")
            
            # Добавляем запись в историю
            current_time = datetime.now().strftime("%H:%M:%S")
            self.history_tree.insert("", 0, values=(current_time, platform, game_name, "в процессе"))
            
            # Ограничиваем историю последними 10 записями
            if len(self.history_tree.get_children()) > 10:
                self.history_tree.delete(self.history_tree.get_children()[-1])
        elif self.game_tracker.last_detected_game is None:
            # Если игра завершилась
            self.game_name_var.set("Не играете")
            self.platform_var.set("Платформа: -")
            self.stats_var.set("Статистика: -")
            self.session_var.set("Текущая сессия: -")
        
        # Обновляем информацию о текущей сессии
        if self.game_tracker.current_session_start:
            current_time = datetime.now()
            duration = current_time - self.game_tracker.current_session_start
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.session_var.set(f"Текущая сессия: {hours}ч {minutes}м {seconds}с")
        else:
            self.session_var.set("Текущая сессия: -")
    
    def tracking_loop(self):
        while self.is_tracking:
            try:
                self.update_game_info()
                self.status_var.set(f"Статус: Активно (последняя проверка: {time.strftime('%H:%M:%S')})")
                time.sleep(5)  # Проверка каждые 5 секунд
            except Exception as e:
                logger.error(f"Ошибка в цикле отслеживания: {e}")
                time.sleep(10)  # При ошибке ждем дольше
    
    def toggle_tracking(self):
        if self.is_tracking:
            # Останавливаем отслеживание
            self.is_tracking = False
            self.toggle_button.config(text="Запустить отслеживание")
            self.status_var.set("Статус: Не активно")
        else:
            # Запускаем отслеживание
            self.is_tracking = True
            self.toggle_button.config(text="Остановить отслеживание")
            self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
            self.tracking_thread.start()
    
    def manual_update(self):
        try:
            self.update_game_info()
            self.status_var.set(f"Статус: Обновлено вручную ({time.strftime('%H:%M:%S')})")
        except Exception as e:
            logger.error(f"Ошибка при ручном обновлении: {e}")
            self.status_var.set("Ошибка при обновлении")
    
    def show_history(self):
        """Показывает окно с историю сессий"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История игровых сессий")
        history_window.geometry("900x500")
        
        # Создаем таблицу для отображения истории
        columns = ("start_time", "end_time", "platform", "game_name", "duration")
        tree = ttk.Treeview(history_window, columns=columns, show="headings", height=20)
        
        tree.heading("start_time", text="Начало")
        tree.heading("end_time", text="Конец")
        tree.heading("platform", text="Платформа")
        tree.heading("game_name", text="Игра")
        tree.heading("duration", text="Длительность (мин)")
        
        tree.column("start_time", width=150)
        tree.column("end_time", width=150)
        tree.column("platform", width=100)
        tree.column("game_name", width=300)
        tree.column("duration", width=100)
        
        # Получаем историю из базы данных
        sessions = self.db.get_session_history(100)
        for session in sessions:
            game_name, platform, start_time, end_time, duration = session
            tree.insert("", "end", values=(start_time, end_time, platform, game_name, duration))
        
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        history_window.columnconfigure(0, weight=1)
        history_window.rowconfigure(0, weight=1)
    
    def show_game_stats(self):
        """Показывает окно со статистикой по играм"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика игр")
        stats_window.geometry("800x500")
        
        # Заголовок
        title_label = ttk.Label(stats_window, text="Статистика по играм", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=5, pady=(10, 10))
        
        # Таблица статистики
        columns = ("game", "platform", "sessions", "playtime", "last_played")
        tree = ttk.Treeview(stats_window, columns=columns, show="headings", height=20)
        
        tree.heading("game", text="Игра")
        tree.heading("platform", text="Платформа")
        tree.heading("sessions", text="Запусков")
        tree.heading("playtime", text="Общее время (ч)")
        tree.heading("last_played", text="Последний запуск")
        
        tree.column("game", width=250)
        tree.column("platform", width=100)
        tree.column("sessions", width=80)
        tree.column("playtime", width=120)
        tree.column("last_played", width=150)
        
        # Заполняем таблицу данными
        try:
            conn = sqlite3.connect(self.db.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_name, platform, total_sessions, total_playtime, last_played 
                FROM game_stats 
                ORDER BY total_playtime DESC
            ''')
            
            for row in cursor.fetchall():
                game_name, platform, sessions, playtime, last_played = row
                hours = playtime // 60
                tree.insert("", "end", values=(game_name, platform, sessions, f"{hours}ч", last_played))
            
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка при загрузке статистики: {e}")
        
        scrollbar = ttk.Scrollbar(stats_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S), pady=(0, 10))
        
        stats_window.columnconfigure(0, weight=1)
        stats_window.rowconfigure(1, weight=1)
    
    def show_process_manager(self):
        """Показывает окно управления процессами"""
        process_window = tk.Toplevel(self.root)
        process_window.title("Управление процессами")
        process_window.geometry("700x500")
        
        # Заголовок
        title_label = ttk.Label(process_window, text="Сопоставление процессов с играми", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(10, 10))
        
        # Таблица процессов
        columns = ("process", "game", "platform")
        tree = ttk.Treeview(process_window, columns=columns, show="headings", height=15)
        
        tree.heading("process", text="Процесс")
        tree.heading("game", text="Игра")
        tree.heading("platform", text="Платформа")
        
        tree.column("process", width=150)
        tree.column("game", width=250)
        tree.column("platform", width=100)
        
        # Функция для обновления таблицы
        def refresh_table():
            tree.delete(*tree.get_children())
            mappings = self.db.get_process_mappings()
            for process, info in mappings.items():
                tree.insert("", "end", values=(process, info['game_name'], info['platform']))
        
        # Заполняем таблицу
        refresh_table()
        
        scrollbar = ttk.Scrollbar(process_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S), pady=(0, 10))
        
        # Функция для редактирования выбранного элемента
        def edit_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите элемент для редактирования")
                return
            
            item = tree.item(selected[0])
            process, game, platform = item['values']
            
            # Создаем окно редактирования
            edit_window = tk.Toplevel(process_window)
            edit_window.title("Редактирование сопоставления")
            edit_window.geometry("400x200")
            
            ttk.Label(edit_window, text="Процесс:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
            process_entry = ttk.Entry(edit_window, width=30)
            process_entry.insert(0, process)
            process_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(edit_window, text="Игра:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
            game_entry = ttk.Entry(edit_window, width=30)
            game_entry.insert(0, game)
            game_entry.grid(row=1, column=1, padx=5, pady=5)
            
            ttk.Label(edit_window, text="Платформа:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
            platform_entry = ttk.Entry(edit_window, width=30)
            platform_entry.insert(0, platform)
            platform_entry.grid(row=2, column=1, padx=5, pady=5)
            
            def save_changes():
                new_process = process_entry.get().strip().lower()
                new_game = game_entry.get().strip()
                new_platform = platform_entry.get().strip()
                
                if new_process and new_game and new_platform:
                    if self.db.update_process_mapping(process, new_process, new_game, new_platform):
                        # Обновляем кэш
                        self.game_tracker.process_mappings = self.db.get_process_mappings()
                        # Обновляем таблицу
                        refresh_table()
                        edit_window.destroy()
                        messagebox.showinfo("Успех", "Сопоставление обновлено")
                    else:
                        messagebox.showerror("Ошибка", "Не удалось обновить сопоставление")
                else:
                    messagebox.showwarning("Предупреждение", "Заполните все поля")
            
            save_button = ttk.Button(edit_window, text="Сохранить", command=save_changes)
            save_button.grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
            
            cancel_button = ttk.Button(edit_window, text="Отмена", command=edit_window.destroy)
            cancel_button.grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)
        
        # Функция для удаления выбранного элемента
        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите элемент для удаления")
                return
            
            item = tree.item(selected[0])
            process, game, platform = item['values']
            
            if messagebox.askyesno("Подтверждение", f"Удалить сопоставление для процесса '{process}'?"):
                if self.db.delete_process_mapping(process):
                    # Обновляем кэш
                    self.game_tracker.process_mappings = self.db.get_process_mappings()
                    # Удаляем из таблицы
                    tree.delete(selected[0])
                    messagebox.showinfo("Успех", "Сопоставление удалено")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить сопоставление")
        
        # Поля для добавления нового сопоставления
        ttk.Label(process_window, text="Процесс:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        process_entry = ttk.Entry(process_window, width=20)
        process_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(process_window, text="Игра:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        game_entry = ttk.Entry(process_window, width=20)
        game_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(process_window, text="Платформа:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        platform_entry = ttk.Entry(process_window, width=20)
        platform_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        def add_mapping():
            process = process_entry.get().strip().lower()
            game = game_entry.get().strip()
            platform = platform_entry.get().strip()
            
            if process and game and platform:
                if self.db.add_process_mapping(process, game, platform):
                    # Обновляем кэш
                    self.game_tracker.process_mappings = self.db.get_process_mappings()
                    # Обновляем таблицу
                    refresh_table()
                    # Очищаем поля
                    process_entry.delete(0, tk.END)
                    game_entry.delete(0, tk.END)
                    platform_entry.delete(0, tk.END)
                    messagebox.showinfo("Успех", "Сопоставление добавлено")
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить сопоставление")
            else:
                messagebox.showwarning("Предупреждение", "Заполните все поля")
        
        # Кнопки управления
        add_button = ttk.Button(process_window, text="Добавить", command=add_mapping)
        add_button.grid(row=5, column=1, padx=5, pady=10, sticky=tk.W)
        
        edit_button = ttk.Button(process_window, text="Редактировать", command=edit_selected)
        edit_button.grid(row=5, column=2, padx=5, pady=10)
        
        delete_button = ttk.Button(process_window, text="Удалить", command=delete_selected)
        delete_button.grid(row=5, column=3, padx=5, pady=10)
        
        refresh_button = ttk.Button(process_window, text="Обновить", command=refresh_table)
        refresh_button.grid(row=5, column=0, padx=5, pady=10)
        
        process_window.columnconfigure(0, weight=1)
        process_window.columnconfigure(1, weight=1)
        process_window.columnconfigure(2, weight=1)
        process_window.columnconfigure(3, weight=1)
        process_window.rowconfigure(1, weight=1)
    
    def create_backup(self):
        """Создает резервную копию базы данных"""
        if self.db.create_backup():
            messagebox.showinfo("Успех", "Резервная копия создана")
        else:
            messagebox.showerror("Ошибка", "Не удалось создать резервную копию")
    
    def exit_app(self):
        # Сохраняем текущую сессию при выходе, если игра активна
        if self.game_tracker.last_detected_game and self.game_tracker.current_session_start:
            end_time = datetime.now()
            duration = int((end_time - self.game_tracker.current_session_start).total_seconds() / 60)
            
            # Сохраняем сессию в базу данных
            self.db.save_session(
                self.game_tracker.last_detected_game, 
                self.game_tracker.last_detected_platform,
                self.game_tracker.current_session_start.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration,
                None
            )
        
        self.is_tracking = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = GameTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()