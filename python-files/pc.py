import os
import webbrowser
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import threading
import time
from PIL import Image, ImageTk
import winsound

# Попробуем импортировать голосовые библиотеки
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class ModernVoiceAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌟 Современный голосовой помощник")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a0a2a')
        self.root.resizable(True, True)
        
        # Центрирование окна
        self.center_window()
        
        # Имя помощника
        self.assistant_name = ""
        
        # Инициализация голосовых компонентов
        self.engine = None
        self.recognizer = None
        if VOICE_AVAILABLE:
            self.init_voice_components()
        
        # Загрузка команд и настроек
        self.commands = self.load_commands()
        self.settings = self.load_settings()
        
        # Переменные интерфейса
        self.is_listening = False
        self.learning_mode = False
        self.current_learning_command = ""
        
        # Создание современного интерфейса
        self.setup_modern_interface()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def init_voice_components(self):
        """Инициализация голосовых компонентов"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.8)
        except:
            self.engine = None
            
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.pause_threshold = 1.0
        except:
            self.recognizer = None
    
    def load_commands(self):
        """Загрузка команд из файла"""
        try:
            with open("commands.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            default_commands = {
                "открой яндекс": {"action": "https://yandex.ru", "type": "website"},
                "открой ютуб": {"action": "https://youtube.com", "type": "website"},
                "открой вк": {"action": "https://vk.com", "type": "website"},
                "запусти калькулятор": {"action": "calc", "type": "app"},
                "открой блокнот": {"action": "notepad", "type": "app"}
            }
            self.save_commands(default_commands)
            return default_commands
    
    def load_settings(self):
        """Загрузка настроек"""
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"assistant_name": "Ассистент"}
    
    def save_commands(self, commands=None):
        """Сохранение команд"""
        if commands is None:
            commands = self.commands
        with open("commands.json", "w", encoding="utf-8") as f:
            json.dump(commands, f, ensure_ascii=False, indent=4)
    
    def save_settings(self):
        """Сохранение настроек"""
        self.settings["assistant_name"] = self.assistant_name
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
    
    def create_gradient_bg(self, width, height, color1, color2):
        """Создание градиентного фона"""
        try:
            from PIL import Image, ImageDraw
            image = Image.new('RGB', (width, height), color1)
            draw = ImageDraw.Draw(image)
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            return ImageTk.PhotoImage(image)
        except:
            return None
    
    def setup_modern_interface(self):
        """Создание ультра-современного интерфейса"""
        # Стиль для ttk виджетов
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        bg_color = '#0a0a2a'
        accent1 = '#9370db'  # Фиолетовый
        accent2 = '#00ffff'  # Голубой
        accent3 = '#6a5acd'  # Сланцевый
        text_color = '#e6e6fa'
        
        # Настройка стилей
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=accent2)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12, 'bold'), foreground=accent1)
        
        # Стили для кнопок
        style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'), 
                       background=accent1, foreground='white', borderwidth=0, 
                       focuscolor='none', padding=(20, 10))
        style.map('Primary.TButton', 
                 background=[('active', accent3), ('pressed', '#483d8b')])
        
        style.configure('Secondary.TButton', font=('Segoe UI', 10), 
                       background=accent3, foreground='white', borderwidth=0,
                       padding=(15, 8))
        style.map('Secondary.TButton', 
                 background=[('active', accent1), ('pressed', '#483d8b')])
        
        style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'), 
                       background='#32cd32', foreground='white', borderwidth=0,
                       padding=(15, 8))
        style.map('Success.TButton', 
                 background=[('active', '#228b22'), ('pressed', '#006400')])
        
        style.configure('Danger.TButton', font=('Segoe UI', 10), 
                       background='#ff6b6b', foreground='white', borderwidth=0,
                       padding=(15, 8))
        style.map('Danger.TButton', 
                 background=[('active', '#ff4757'), ('pressed', '#ff3838')])
        
        # Главный контейнер с градиентом
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Верхняя панель с градиентом
        header_frame = tk.Frame(main_container, bg=bg_color, height=120)
        header_frame.pack(fill=tk.X, pady=(0, 0))
        header_frame.pack_propagate(False)
        
        # Заголовок и имя
        title_container = ttk.Frame(header_frame)
        title_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.title_label = ttk.Label(title_container, 
                                   text="🌟 СОВРЕМЕННЫЙ ГОЛОСОВОЙ ПОМОЩНИК", 
                                   style='Title.TLabel')
        self.title_label.pack(side=tk.LEFT)
        
        self.name_label = ttk.Label(title_container, 
                                  text=f"👤 Имя: {self.assistant_name}", 
                                  font=('Segoe UI', 12, 'italic'), 
                                  foreground='#98fb98')
        self.name_label.pack(side=tk.RIGHT)
        
        # Основное содержимое
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Левая панель - управление
        left_panel = ttk.Frame(content_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # Правая панель - лог и информация
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === ЛЕВАЯ ПАНЕЛЬ ===
        
        # Статусная панель
        status_frame = ttk.LabelFrame(left_panel, text="📊 Статус системы", 
                                    padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="✅ Система готова", 
                                    foreground='#32cd32', font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        ttk.Label(status_frame, text=f"Команд в базе: {len(self.commands)}", 
                 font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Панель голосового управления
        voice_frame = ttk.LabelFrame(left_panel, text="🎤 Голосовое управление", 
                                   padding=15)
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.voice_button = ttk.Button(voice_frame, text="🎤 Нажми и говори", 
                                      command=self.toggle_listening, 
                                      style='Primary.TButton')
        self.voice_button.pack(fill=tk.X, pady=5)
        
        ttk.Label(voice_frame, text="Произнесите команду с именем помощника", 
                 font=('Segoe UI', 9), foreground='#aaa').pack()
        
        # Панель быстрых команд
        quick_frame = ttk.LabelFrame(left_panel, text="⚡ Быстрые команды", 
                                   padding=15)
        quick_frame.pack(fill=tk.X, pady=(0, 15))
        
        quick_commands = [
            ("🌐 Яндекс", "открой яндекс"),
            ("🎥 YouTube", "открой ютуб"),
            ("👥 ВКонтакте", "открой вк"),
            ("🧮 Калькулятор", "запусти калькулятор"),
            ("📝 Блокнот", "открой блокнот")
        ]
        
        for text, cmd in quick_commands:
            ttk.Button(quick_frame, text=text, 
                      command=lambda c=cmd: self.quick_command(c),
                      style='Secondary.TButton').pack(fill=tk.X, pady=2)
        
        # Панель управления
        control_frame = ttk.LabelFrame(left_panel, text="⚙️ Управление", 
                                     padding=15)
        control_frame.pack(fill=tk.X)
        
        ttk.Button(control_frame, text="📚 Обучить новой команде", 
                  command=self.start_learning_gui, style='Success.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="📋 Управление командами", 
                  command=self.show_commands_manager, style='Secondary.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="✏️ Сменить имя", 
                  command=self.change_name, style='Secondary.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="❌ Выход", 
                  command=self.root.quit, style='Danger.TButton').pack(fill=tk.X, pady=(10, 2))
        
        # === ПРАВАЯ ПАНЕЛЬ ===
        
        # Лог действий
        log_frame = ttk.LabelFrame(right_panel, text="📝 Лог действий", padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, 
                                                bg='#1a1a3a', fg=text_color, 
                                                insertbackground=accent2,
                                                font=('Consolas', 10),
                                                relief='flat', borderwidth=0,
                                                padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Статистика внизу
        stats_frame = ttk.Frame(right_panel)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, 
                                   text=f"🔊 Голосовой ввод: {'✅ Доступен' if self.recognizer else '❌ Недоступен'} | "
                                       f"🗣️ Синтез речи: {'✅ Доступен' if self.engine else '❌ Недоступен'}",
                                   font=('Segoe UI', 9))
        self.stats_label.pack(side=tk.LEFT)
        
        ttk.Button(stats_frame, text="🔄 Обновить", 
                  command=self.refresh_status).pack(side=tk.RIGHT)
        
        # Запрос имени при первом запуске
        if not self.assistant_name:
            self.root.after(500, self.request_name)
        else:
            self.log("🚀 Помощник успешно запущен!", "success")
    
    def request_name(self):
        """Запрос имени помощника при запуске"""
        name = simpledialog.askstring("👤 Имя помощника", 
                                     "Как вы хотите назвать вашего помощника?\n\n"
                                     "Это имя будет использоваться для активации голосовых команд.",
                                     initialvalue="Ассистент")
        if name and name.strip():
            self.assistant_name = name.strip()
            self.name_label.config(text=f"👤 Имя: {self.assistant_name}")
            self.save_settings()
            self.log(f"✅ Установлено имя помощника: {self.assistant_name}", "success")
            self.speak(f"Привет! Я ваш помощник {self.assistant_name}. Готов к работе!")
        else:
            self.assistant_name = "Ассистент"
            self.name_label.config(text=f"👤 Имя: {self.assistant_name}")
            self.log("⚠️ Установлено имя по умолчанию: Ассистент", "warning")
    
    def change_name(self):
        """Смена имени помощника"""
        name = simpledialog.askstring("✏️ Смена имени", 
                                     "Введите новое имя помощника:",
                                     initialvalue=self.assistant_name)
        if name and name.strip():
            self.assistant_name = name.strip()
            self.name_label.config(text=f"👤 Имя: {self.assistant_name}")
            self.save_settings()
            self.log(f"✏️ Имя изменено на: {self.assistant_name}", "success")
            self.speak(f"Теперь я {self.assistant_name}")
    
    def log(self, message, msg_type="info"):
        """Добавление сообщения в лог с цветовым кодированием"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Цвета для разных типов сообщений
        colors = {
            "success": "#32cd32",
            "error": "#ff6b6b", 
            "warning": "#ffa500",
            "info": "#00bfff",
            "command": "#9370db"
        }
        
        color = colors.get(msg_type, "#e6e6fa")
        
        self.log_text.tag_configure(msg_type, foreground=color)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "info")
        self.log_text.insert(tk.END, f"{message}\n", msg_type)
        self.log_text.see(tk.END)
        self.root.update()
    
    def speak(self, text):
        """Озвучивание текста"""
        self.log(f"🔊 Ассистент: {text}", "info")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                self.log(f"❌ Ошибка синтеза речи: {e}", "error")
    
    def listen(self):
        """Прослушивание команды"""
        if not self.recognizer:
            self.log("❌ Голосовое распознавание недоступно", "error")
            return ""
        
        try:
            with sr.Microphone() as source:
                self.status_label.config(text="🎤 Слушаю...", foreground='#ffa500')
                self.log("🎤 Слушаю... Произнесите команду", "info")
                
                # Звуковой сигнал начала записи
                winsound.Beep(1000, 200)
                
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=6)
            
            self.status_label.config(text="🔍 Обрабатываю...", foreground='#ffd700')
            text = self.recognizer.recognize_google(audio, language="ru-RU").lower()
            
            self.status_label.config(text="✅ Система готова", foreground='#32cd32')
            self.log(f"🎤 Распознано: {text}", "command")
            
            # Звуковой сигнал успешного распознавания
            winsound.Beep(800, 100)
            
            return text
            
        except sr.WaitTimeoutError:
            self.status_label.config(text="✅ Система готова", foreground='#32cd32')
            return ""
        except Exception as e:
            self.status_label.config(text="❌ Ошибка", foreground='#ff6b6b')
            self.log(f"❌ Ошибка распознавания: {e}", "error")
            return ""
    
    def process_command(self, command_text):
        """Обработка команды с учетом имени"""
        if not command_text:
            return "no_command"
        
        # Проверяем, содержит ли команда имя помощника
        contains_name = self.assistant_name.lower() in command_text.lower()
        
        # Удаляем имя из команды если оно есть
        if contains_name:
            clean_command = command_text.lower().replace(self.assistant_name.lower(), "").strip()
        else:
            clean_command = command_text.lower()
        
        self.log(f"🔍 Обрабатываю команду: '{clean_command}'", "info")
        
        # Специальные команды (работают только с именем)
        if contains_name:
            if any(word in clean_command for word in ["стоп", "выход", "пока"]):
                return "exit"
            
            if any(word in clean_command for word in ["научись", "обучись", "запомни"]):
                return "learn"
            
            if "список команд" in clean_command:
                self.show_commands_manager()
                return "show_commands"
        
        # Поиск команды в базе (работают с именем или без)
        for cmd, data in self.commands.items():
            if cmd in clean_command or clean_command in cmd:
                return self.execute_action(data["action"], cmd)
        
        # Если команда не найдена и было упомянуто имя
        if contains_name:
            return "not_found"
        
        return "no_name"
    
    def execute_action(self, action, command_name):
        """Выполнение действия"""
        try:
            if action.startswith(("http://", "https://", "www.")):
                webbrowser.open(action)
                return f"🌐 Открываю {command_name}"
            
            elif action in ["calc", "notepad", "explorer"]:
                os.system(f'start {action}')
                return f"🚀 Запускаю {command_name}"
            
            elif os.path.exists(action):
                os.startfile(action)
                return f"🚀 Запускаю {command_name}"
            
            else:
                os.system(f'start {action}')
                return f"⚡ Выполняю: {action}"
                
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def toggle_listening(self):
        """Включение/выключение прослушивания"""
        if not self.is_listening:
            self.is_listening = True
            self.voice_button.config(text="🔴 Слушаю...")
            threading.Thread(target=self.voice_listen_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.voice_button.config(text="🎤 Нажми и говори")
    
    def voice_listen_loop(self):
        """Цикл прослушивания голоса"""
        while self.is_listening:
            command = self.listen()
            if command:
                result = self.process_command(command)
                self.handle_command_result(result, command)
            
            time.sleep(0.5)
    
    def handle_command_result(self, result, original_command):
        """Обработка результата команды"""
        if result == "exit":
            self.speak("До свидания! Удачи!")
            self.root.after(1000, self.root.quit)
        
        elif result == "learn":
            self.start_learning_voice(original_command)
        
        elif result == "not_found":
            self.speak("Команда не найдена. Скажите 'научись' чтобы добавить её.")
        
        elif result == "no_name":
            # Игнорируем команды без имени
            pass
        
        elif result == "no_command":
            # Пустая команда
            pass
        
        elif result == "show_commands":
            self.speak("Открываю список команд")
        
        else:
            self.speak(result)
    
    def start_learning_voice(self, original_command):
        """Начало обучения через голос"""
        self.learning_mode = True
        self.speak("Какую команду вы хотите добавить?")
        
        time.sleep(1)
        new_command = self.listen()
        
        if new_command:
            self.current_learning_command = new_command
            self.speak("Открываю окно для ввода действия")
            self.root.after(100, self.open_learning_dialog)
        else:
            self.speak("Не удалось распознать команду")
            self.learning_mode = False
    
    def start_learning_gui(self):
        """Начало обучения через GUI"""
        self.open_learning_dialog()
    
    def open_learning_dialog(self):
        """Открытие диалога обучения"""
        learn_window = tk.Toplevel(self.root)
        learn_window.title("🎓 Обучение новой команде")
        learn_window.geometry("600x500")
        learn_window.configure(bg='#1a1a3a')
        learn_window.resizable(False, False)
        learn_window.transient(self.root)
        learn_window.grab_set()
        
        # Центрирование
        learn_window.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (600 // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (500 // 2)
        learn_window.geometry(f"+{x}+{y}")
        
        ttk.Label(learn_window, text="🎓 Обучение новой команде", 
                 style='Title.TLabel').pack(pady=20)
        
        # Поле для команды
        ttk.Label(learn_window, text="📝 Команда (что говорить):", 
                 style='Subtitle.TLabel').pack(pady=5)
        cmd_entry = ttk.Entry(learn_window, width=60, font=('Segoe UI', 11))
        cmd_entry.pack(pady=10, padx=20)
        
        if self.current_learning_command:
            cmd_entry.insert(0, self.current_learning_command)
        
        # Поле для действия
        ttk.Label(learn_window, text="⚡ Действие (что выполнять):", 
                 style='Subtitle.TLabel').pack(pady=5)
        action_entry = scrolledtext.ScrolledText(learn_window, height=6, width=60,
                                               font=('Segoe UI', 10))
        action_entry.pack(pady=10, padx=20)
        
        # Подсказки
        tips_frame = ttk.LabelFrame(learn_window, text="💡 Подсказки", padding=10)
        tips_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tips_text = """• URL сайта: https://example.com
• Путь к программе: C:\\Program Files\\app.exe  
• Системная команда: calc, notepad, explorer
• Протокол: minecraft://, steam://
• Папка: C:\\Users\\Name\\Folder"""
        
        ttk.Label(tips_frame, text=tips_text, font=('Segoe UI', 9), 
                 foreground='#aaa').pack()
        
        # Кнопки
        btn_frame = ttk.Frame(learn_window)
        btn_frame.pack(pady=20)
        
        def save_command():
            command = cmd_entry.get().strip()
            action = action_entry.get("1.0", tk.END).strip()
            
            if not command:
                messagebox.showerror("Ошибка", "Введите команду!")
                return
            
            if not action:
                messagebox.showerror("Ошибка", "Введите действие!")
                return
            
            # Определяем тип команды
            cmd_type = "other"
            if action.startswith("http"):
                cmd_type = "website"
            elif action in ["calc", "notepad", "explorer"] or action.endswith(".exe"):
                cmd_type = "app"
            elif os.path.isdir(action):
                cmd_type = "folder"
            
            self.commands[command] = {"action": action, "type": cmd_type}
            self.save_commands()
            
            self.log(f"✅ Изучена новая команда: '{command}' -> '{action}'", "success")
            self.speak(f"Команда '{command}' успешно добавлена!")
            
            learn_window.destroy()
            self.learning_mode = False
            self.current_learning_command = ""
        
        ttk.Button(btn_frame, text="💾 Сохранить команду", 
                  command=save_command, style='Success.TButton', width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🧪 Тестировать", 
                  command=lambda: self.test_command(action_entry.get("1.0", tk.END).strip()),
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=learn_window.destroy, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        cmd_entry.focus()
    
    def test_command(self, action):
        """Тестирование команды перед сохранением"""
        if not action:
            messagebox.showwarning("Предупреждение", "Введите действие для тестирования!")
            return
        
        try:
            if action.startswith(("http://", "https://", "www.")):
                webbrowser.open(action)
                self.log("🌐 Тестирование: открыт сайт", "success")
            elif os.path.exists(action):
                os.startfile(action)
                self.log("🚀 Тестирование: запущена программа", "success")
            else:
                os.system(f'start {action}')
                self.log("⚡ Тестирование: выполнена команда", "success")
        except Exception as e:
            self.log(f"❌ Ошибка тестирования: {e}", "error")
    
    def show_commands_manager(self):
        """Показать менеджер команд с возможностью редактирования"""
        manager_window = tk.Toplevel(self.root)
        manager_window.title("📋 Менеджер команд")
        manager_window.geometry("800x600")
        manager_window.configure(bg='#1a1a3a')
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        # Центрирование
        manager_window.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (800 // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (600 // 2)
        manager_window.geometry(f"+{x}+{y}")
        
        ttk.Label(manager_window, text="📋 Менеджер команд", 
                 style='Title.TLabel').pack(pady=20)
        
        # Панель поиска и фильтрации
        search_frame = ttk.Frame(manager_window)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=10)
        search_entry.bind('<KeyRelease>', lambda e: self.filter_commands(tree, search_var.get()))
        
        # Таблица команд
        tree_frame = ttk.Frame(manager_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("command", "action", "type"), show="headings", height=15)
        
        tree.heading("command", text="Команда")
        tree.heading("action", text="Действие") 
        tree.heading("type", text="Тип")
        
        tree.column("command", width=200)
        tree.column("action", width=400)
        tree.column("type", width=100)
        
        # Заполнение данными
        for cmd, data in self.commands.items():
            tree.insert("", tk.END, values=(cmd, data["action"], data.get("type", "other")))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель действий
        action_frame = ttk.Frame(manager_window)
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def edit_command():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите команду для редактирования!")
                return
            
            item = tree.item(selection[0])
            command, action, _ = item["values"]
            self.edit_command_dialog(command, action, manager_window)
        
        def delete_command():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите команду для удаления!")
                return
            
            item = tree.item(selection[0])
            command = item["values"][0]
            
            if messagebox.askyesno("Подтверждение", f"Удалить команду '{command}'?"):
                del self.commands[command]
                self.save_commands()
                tree.delete(selection[0])
                self.log(f"🗑️ Удалена команда: {command}", "warning")
        
        def execute_command():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите команду для выполнения!")
                return
            
            item = tree.item(selection[0])
            command, action, _ = item["values"]
            result = self.execute_action(action, command)
            self.speak(result)
        
        ttk.Button(action_frame, text="✏️ Редактировать", 
                  command=edit_command, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text("🚀 Выполнить"), 
                  command=execute_command, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="🗑️ Удалить", 
                  command=delete_command, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="❌ Закрыть", 
                  command=manager_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def filter_commands(self, tree, search_text):
        """Фильтрация команд в дереве"""
        for item in tree.get_children():
            tree.delete(item)
        
        search_text = search_text.lower()
        for cmd, data in self.commands.items():
            if search_text in cmd.lower() or search_text in data["action"].lower():
                tree.insert("", tk.END, values=(cmd, data["action"], data.get("type", "other")))
    
    def edit_command_dialog(self, command, action, parent_window):
        """Диалог редактирования команды"""
        edit_window = tk.Toplevel(parent_window)
        edit_window.title("✏️ Редактирование команды")
        edit_window.geometry("500x400")
        edit_window.transient(parent_window)
        edit_window.grab_set()
        
        ttk.Label(edit_window, text="✏️ Редактирование команды", 
                 style='Title.TLabel').pack(pady=20)
        
        ttk.Label(edit_window, text="Команда:").pack(pady=5)
        cmd_entry = ttk.Entry(edit_window, width=50)
        cmd_entry.insert(0, command)
        cmd_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Действие:").pack(pady=5)
        action_entry = scrolledtext.ScrolledText(edit_window, height=8, width=50)
        action_entry.insert("1.0", action)
        action_entry.pack(pady=5)
        
        def save_changes():
            new_command = cmd_entry.get().strip()
            new_action = action_entry.get("1.0", tk.END).strip()
            
            if not new_command or not new_action:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            
            # Удаляем старую команду если имя изменилось
            if new_command != command:
                del self.commands[command]
            
            # Сохраняем новую команду
            cmd_type = "other"
            if new_action.startswith("http"):
                cmd_type = "website"
            elif new_action in ["calc", "notepad", "explorer"] or new_action.endswith(".exe"):
                cmd_type = "app"
            
            self.commands[new_command] = {"action": new_action, "type": cmd_type}
            self.save_commands()
            
            self.log(f"✏️ Обновлена команда: '{new_command}'", "success")
            edit_window.destroy()
            parent_window.destroy()
            self.show_commands_manager()
        
        ttk.Button(edit_window, text="💾 Сохранить изменения", 
                  command=save_changes, style='Success.TButton').pack(pady=10)
    
    def quick_command(self, command):
        """Быстрое выполнение команды"""
        self.log(f"⚡ Быстрая команда: {command}", "command")
        if command in self.commands:
            result = self.execute_action(self.commands[command]["action"], command)
            self.speak(result)
        else:
            self.log(f"❌ Команда не найдена: {command}", "error")
    
    def refresh_status(self):
        """Обновление статуса системы"""
        self.stats_label.config(
            text=f"🔊 Голосовой ввод: {'✅ Доступен' if self.recognizer else '❌ Недоступен'} | "
                f"🗣️ Синтез речи: {'✅ Доступен' if self.engine else '❌ Недоступен'}"
        )
        self.log("🔄 Статус системы обновлен", "info")
    
    def run(self):
        """Запуск приложения"""
        # Загружаем имя из настроек
        if "assistant_name" in self.settings:
            self.assistant_name = self.settings["assistant_name"]
            self.name_label.config(text=f"👤 Имя: {self.assistant_name}")
        
        self.log("🚀 Помощник успешно запущен!", "success")
        self.root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    try:
        app = ModernVoiceAssistant()
        app.run()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...")
