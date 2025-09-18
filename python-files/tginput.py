import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import subprocess
import os
import sys
import json
from pathlib import Path

class PCCommandExecutor:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Command Executor")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Переменная для отслеживания текущей операции
        self.current_operation = "⌚Ожидание команды"
        
        # Загрузка конфигурации
        self.config = self.load_config()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск мониторинга команд
        self.monitor_commands()
        
    def load_config(self):
        """Загрузка конфигурации из файла"""
        config_path = "bot_config.json"
        default_config = {
            "BOT_PATHS": {
                "Phoenix": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\phoenix.bat",
                "Tucson": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\tucson.bat",
                "Scottdale": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\scottdale.bat",
                "Winslow": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\winslow.bat",
                "Brainburg": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\brainburg.bat",
                "BumbleBee": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\bumblebee.bat",
                "CasaGrande": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\casagrande.bat",
                "Chandler": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\chandler.bat",
                "Christmas": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\christmas.bat",
                "Faraway": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\faraway.bat",
                "Gilbert": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\gilbert.bat",
                "Glendale": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\glendale.bat",
                "Holiday": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\holiday.bat",
                "Kingman": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\kingman.bat",
                "Mesa": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\mesa.bat",
                "Page": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\page.bat",
                "Payson": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\payson.bat",
                "Prescott": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\prescott.bat",
                "QueenCreek": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\queencreek.bat",
                "RedRock": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\redrock.bat",
                "SaintRose": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\saintrose.bat",
                "Sedona": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\sedona.bat",
                "ShowLow": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\showlow.bat",
                "SunCity": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\suncity.bat",
                "Surprise": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\surprise.bat",
                "Wednesday": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\wednesday.bat",
                "Yava": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\yava.bat",
                "Yuma": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\yuma.bat",
                "Love": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\love.bat",
                "Mirage": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\mirage.bat",
                "Drake": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\drake.bat"
            },
            "SPECIAL_COMMANDS": {
                "all_servers": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\! запустить по 1 боту на каждый сервер.bat",
                "stop_all": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\! закрыть все окна raksamp.bat"
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем файл конфигурации
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                return default_config
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки конфигурации: {e}")
            return default_config
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = tk.Label(main_frame, text="🤖 PC Command Executor", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Статус
        self.status_label = tk.Label(main_frame, text=self.current_operation,
                                    font=("Arial", 12), fg="blue")
        self.status_label.pack(pady=5)
        
        # Лог действий
        log_label = tk.Label(main_frame, text="📋 Лог действий:", 
                            font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15,
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Кнопка очистки лога
        clear_btn = tk.Button(main_frame, text="🧹 Очистить лог", 
                             command=self.clear_log)
        clear_btn.pack(pady=5)
        
        # Информация о программе
        info_text = ("🔸 Программа ожидает команды от Telegram бота\n"
                    "🔸 Запускает ботов на указанных серверах\n"
                    "🔸 Управление через файл commands.json")
        info_label = tk.Label(main_frame, text=info_text, justify=tk.LEFT,
                             font=("Arial", 9), fg="gray")
        info_label.pack(pady=5)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Лог очищен")
    
    def update_status(self, status):
        """Обновление статуса программы"""
        self.current_operation = status
        self.status_label.config(text=status)
        
        if "⭐Выполняется запуск" in status:
            self.status_label.config(fg="green")
        elif "⌚Ожидание команды" in status:
            self.status_label.config(fg="blue")
        else:
            self.status_label.config(fg="black")
    
    def execute_command(self, command_type, bot_name=None):
        """Выполнение команды на компьютере"""
        try:
            if command_type == "launch_bot" and bot_name:
                if bot_name in self.config["BOT_PATHS"]:
                    bot_path = self.config["BOT_PATHS"][bot_name]
                    if os.path.exists(bot_path):
                        self.update_status(f"⭐Выполняется запуск бота {bot_name}")
                        self.log_message(f"🚀 Запускаю бота: {bot_name}")
                        
                        # Запускаем .bat файл
                        subprocess.Popen(bot_path, shell=True)
                        
                        self.log_message(f"✅ Бот {bot_name} запущен успешно")
                        return True
                    else:
                        self.log_message(f"❌ Файл не найден: {bot_path}")
                        return False
                else:
                    self.log_message(f"❌ Бот {bot_name} не найден в конфигурации")
                    return False
            
            elif command_type == "all_servers":
                if "all_servers" in self.config["SPECIAL_COMMANDS"]:
                    bat_path = self.config["SPECIAL_COMMANDS"]["all_servers"]
                    if os.path.exists(bat_path):
                        self.update_status("⭐Выполняется запуск по 1 боту на все сервера")
                        self.log_message("🚀 Запускаю по 1 боту на все сервера")
                        
                        subprocess.Popen(bat_path, shell=True)
                        
                        self.log_message("✅ Запуск по 1 боту на все сервера выполнен")
                        return True
                    else:
                        self.log_message(f"❌ Файл не найден: {bat_path}")
                        return False
                else:
                    self.log_message("❌ Команда 'all_servers' не настроена")
                    return False
            
            elif command_type == "stop_all":
                if "stop_all" in self.config["SPECIAL_COMMANDS"]:
                    bat_path = self.config["SPECIAL_COMMANDS"]["stop_all"]
                    if os.path.exists(bat_path):
                        self.update_status("⭐Выполняется остановка всех ботов")
                        self.log_message("🛑 Останавливаю всех ботов")
                        
                        subprocess.Popen(bat_path, shell=True)
                        
                        self.log_message("✅ Все боты остановлены")
                        return True
                    else:
                        self.log_message(f"❌ Файл не найден: {bat_path}")
                        return False
                else:
                    self.log_message("❌ Команда 'stop_all' не настроена")
                    return False
            
            else:
                self.log_message(f"❌ Неизвестная команда: {command_type}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Ошибка выполнения команды: {str(e)}")
            return False
        finally:
            # Через 3 секунды возвращаем статус ожидания
            self.root.after(3000, lambda: self.update_status("⌚Ожидание команды"))
    
    def check_commands_file(self):
        """Проверка файла команд"""
        commands_file = "commands.json"
        
        try:
            if os.path.exists(commands_file):
                with open(commands_file, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
                
                # Если есть команды для выполнения
                if commands:
                    command = commands.pop(0)  # Берем первую команду
                    
                    # Удаляем файл после чтения
                    os.remove(commands_file)
                    
                    return command
            return None
            
        except Exception as e:
            self.log_message(f"❌ Ошибка чтения файла команд: {e}")
            return None
    
    def monitor_commands(self):
        """Мониторинг команд в фоновом режиме"""
        command = self.check_commands_file()
        
        if command:
            if command.get("type") == "launch_bot":
                self.execute_command("launch_bot", command.get("bot_name"))
            elif command.get("type") == "all_servers":
                self.execute_command("all_servers")
            elif command.get("type") == "stop_all":
                self.execute_command("stop_all")
        
        # Проверяем каждые 2 секунды
        self.root.after(2000, self.monitor_commands)

def main():
    """Основная функция"""
    root = tk.Tk()
    app = PCCommandExecutor(root)
    
    # Центрирование окна
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()