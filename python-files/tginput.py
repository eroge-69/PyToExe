import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from threading import Thread
from datetime import datetime
import time
import threading

class TelegramBotExecutor:
    def __init__(self):
        self.root = None
        self.current_operation = "⌚Ожидание команды"
        self.config = self.load_config()
        self.is_running = False
        
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = "telegram_config.json"
        default_config = {
            "api_id": "your_api_id",
            "api_hash": "your_api_hash",
            "session_string": "",
            "target_bot_username": "@Distance_raksamp_bot",
            "bot_paths": {
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\showlow.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\suncity.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\surprise.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\tucson.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\wensday.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\winslow.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\yava.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\Yuma.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\BrainBurg.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\bumblebee.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\CasaGrande.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\chandler.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\christmas.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\drake.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\faraway.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\gilbert.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\glendale.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\holiday.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\kingsman.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\kvinkreek.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\love.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\mesa.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\Mirage.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\page.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\payson.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\Phoenix.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\Presscot.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\saintrose.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\scottdale.bat"
                "C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\sedona.bat"
            },
            "special_commands": {
                "all_servers": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\! запустить по 1 боту на каждый сервер.bat",
                "stop_all": r"C:\Users\User\OneDrive\Рабочий стол\боты\PREMIUM QUEST BOT — 3.1 — копия\бот\! закрыть все окна raksamp.bat"
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                return default_config
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки конфигурации: {e}")
            return default_config

    def create_gui(self):
        """Создание графического интерфейса"""
        self.root = tk.Tk()
        self.root.title("Executo - Управление ботами")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")
        
        # Стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = tk.Label(main_frame, text="Executo", font=("Arial", 16, "bold"), 
                              fg="#ecf0f1", bg="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Статус
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="5")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text=self.current_operation, 
                                    fg="#bdc3c7", bg="#34495e", font=("Arial", 10))
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = tk.Button(button_frame, text="Запуск", command=self.start_client,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  width=10)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = tk.Button(button_frame, text="Стоп", command=self.stop_client,
                                 bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"),
                                 width=10, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                 bg="#1e272e", fg="#00ff00", 
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open("telegram_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.log_message("✅ Конфигурация сохранена")
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        
        # Ограничение размера лога
        if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.log_text.delete(1.0, 100)
    
    def update_status(self, status):
        """Обновление статуса"""
        self.current_operation = status
        self.status_label.config(text=status)
    
    def execute_command(self, command_type, bot_name=None):
        """Выполнение команды"""
        try:
            if command_type == "launch_bot" and bot_name:
                if bot_name in self.config["bot_paths"]:
                    bot_path = self.config["bot_paths"][bot_name]
                    self.update_status(f"🚀 Запуск {bot_name}")
                    self.log_message(f"Запускаю {bot_name}: {bot_path}")
                    
                    # Запуск bat файла
                    subprocess.Popen([bot_path], shell=True)
                    self.log_message(f"✅ {bot_name} запущен")
                    
                else:
                    self.log_message(f"❌ Бот {bot_name} не найден в конфигурации")
            
            elif command_type == "all_servers":
                self.update_status("🌐 Запуск всех серверов")
                self.log_message("Запускаю все серверы...")
                
                all_servers_path = self.config["special_commands"]["all_servers"]
                subprocess.Popen([all_servers_path], shell=True)
                self.log_message("✅ Все серверы запущены")
            
            elif command_type == "stop_all":
                self.update_status("⏹ Остановка всех ботов")
                self.log_message("Останавливаю все боты...")
                
                stop_all_path = self.config["special_commands"]["stop_all"]
                subprocess.Popen([stop_all_path], shell=True)
                self.log_message("✅ Все боты остановлены")
            
            self.update_status("⌚Ожидание команды")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка выполнения команды: {e}")
            self.update_status("❌ Ошибка выполнения")

    def run_file_monitor(self):
        """Мониторинг файла commands.json вместо Telegram"""
        commands_file = "commands.json"
        
        while self.is_running:
            try:
                if os.path.exists(commands_file):
                    with open(commands_file, 'r', encoding='utf-8') as f:
                        commands = json.load(f)
                    
                    if commands:
                        command = commands[0]
                        # Удаляем файл после чтения
                        os.remove(commands_file)
                        
                        if command.get("type") == "launch_bot":
                            self.execute_command("launch_bot", command.get("bot_name"))
                        elif command.get("type") == "all_servers":
                            self.execute_command("all_servers")
                        elif command.get("type") == "stop_all":
                            self.execute_command("stop_all")
                
                time.sleep(2)  # Проверяем каждые 2 секунды
                
            except Exception as e:
                self.log_message(f"❌ File monitor error: {e}")
                time.sleep(5)

    def start_client(self):
        """Запуск клиента"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, bg="#7f8c8d")
        self.stop_btn.config(state=tk.NORMAL, bg="#e74c3c")
        
        # Запускаем мониторинг файла
        Thread(target=self.run_file_monitor, daemon=True).start()
        self.log_message("📁 File monitor started")

    def stop_client(self):
        """Остановка клиента"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL, bg="#27ae60")
        self.stop_btn.config(state=tk.DISABLED, bg="#7f8c8d")
        self.log_message("⏹ File monitor stopped")

    def run(self):
        """Запуск приложения"""
        self.create_gui()
        self.log_message("🚀 Executo started")
        self.log_message("📁 Monitoring commands.json file")
        self.root.mainloop()

def main():
    app = TelegramBotExecutor()
    app.run()

if __name__ == "__main__":
    main()