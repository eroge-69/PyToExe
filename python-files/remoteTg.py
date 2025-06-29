import os
import subprocess
import platform
import psutil
import pyautogui
import time
import logging
from threading import Thread
from telegram import Update, Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import wakeonlan
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from win10toast import ToastNotifier
import sys

# Настройки бота
MAC_ADDRESS = "74-56-3C-30-D9-E3"  # Замените на реальный MAC-адрес вашего ПК
TOKEN = '7802473532:AAHkCO0zrFHrEAnq53x6zGvAjNkcmvQYqxE'
ALLOWED_USERS = [1624260908]  # Ваш Telegram user ID (можно получить у @userinfobot)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверка авторизации пользователя
def auth_required(func):
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            await update.message.reply_text('🚫 Доступ запрещен!')
            return
        return await func(update, context)
    return wrapper

# Команда /start
@auth_required
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("📊 Системная информация"), KeyboardButton("📷 Скриншот экрана")],
        [KeyboardButton("🔌 Выключить компьютер"), KeyboardButton("🔄 Перезагрузить компьютер")],
        [KeyboardButton("💤 Режим сна"), KeyboardButton("🎵 Громкость +10%")],
        [KeyboardButton("🔇 Громкость -10%"), KeyboardButton("⌨️ Отправить команду")],
        [KeyboardButton("📂 Список файлов"), KeyboardButton("🚀 Открыть приложение")],
        [KeyboardButton("⚡️ Включить ПК"), KeyboardButton("⚡️ Список процессов")],
        [KeyboardButton("❌ Закрыть процесс"), KeyboardButton("💬 Отправить сообщение")],
        [KeyboardButton("🔄 Обновить меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        '🖥️ Добро пожаловать в систему удаленного управления компьютером!\n'
        'Выберите действие:',
        reply_markup=reply_markup
    )

# Функция для включения ПК через Wake-on-LAN
async def wake_up_pc(chat_id: int, bot: Bot):
    try:
        wakeonlan.send_magic_packet(MAC_ADDRESS)
        await bot.send_message(chat_id, '⚡️ Команда на включение ПК отправлена!')
    except Exception as e:
        await bot.send_message(chat_id, f'❌ Ошибка при отправке Wake-on-LAN пакета: {e}')

# Функция для поиска и запуска приложения
async def open_application(update: Update, context: CallbackContext):
    app_name = update.message.text.strip()
    try:
        if platform.system() == 'Windows':
            if ':\\' in app_name or ':/' in app_name or app_name.startswith('\\') or app_name.startswith('/'):
                if os.path.exists(app_name):
                    if app_name.lower().endswith(('.exe', '.bat', '.cmd')):
                        subprocess.Popen(app_name, shell=True)
                    else:
                        os.startfile(app_name)
                    await update.message.reply_text(f'✅ Файл {app_name} успешно запущен!')
                else:
                    await update.message.reply_text(f'❌ Файл {app_name} не найден!')
            else:
                paths = [
                    os.path.join(os.environ['ProgramFiles'], app_name),
                    os.path.join(os.environ['ProgramFiles'], 'Google', 'Chrome', 'Application', app_name),
                    os.path.join(os.environ['ProgramFiles(x86)'], app_name),
                    os.path.join(os.environ['SystemRoot'], 'System32', app_name),
                    os.path.join(os.environ['SystemRoot'], app_name),
                    os.path.join(os.environ['APPDATA'], app_name),
                    os.path.join(os.environ['LOCALAPPDATA'], app_name)
                ]
                
                for path in os.environ['PATH'].split(';'):
                    if path:
                        paths.append(os.path.join(path, app_name))
                
                found = False
                for path in paths:
                    if os.path.exists(path):
                        os.startfile(path)
                        found = True
                        break
                
                if not found:
                    try:
                        where_result = subprocess.run(f"where {app_name}", shell=True, capture_output=True, text=True)
                        if where_result.returncode == 0:
                            app_path = where_result.stdout.splitlines()[0].strip()
                            os.startfile(app_path)
                            found = True
                    except:
                        pass
                
                if found:
                    await update.message.reply_text(f'✅ Приложение {app_name} успешно запущено!')
                else:
                    await update.message.reply_text(f'❌ Приложение {app_name} не найдено. Проверьте название и попробуйте снова.')
        
        else:  # Для Linux/Mac
            try:
                if '/' in app_name:
                    if os.path.exists(app_name):
                        os.chmod(app_name, 0o755)
                        subprocess.Popen([os.path.abspath(app_name)], shell=True)
                        await update.message.reply_text(f'✅ Файл {app_name} успешно запущен!')
                    else:
                        await update.message.reply_text(f'❌ Файл {app_name} не найден!')
                else:
                    subprocess.Popen(app_name, shell=True)
                    await update.message.reply_text(f'✅ Команда для запуска {app_name} выполнена!')
            except Exception as e:
                await update.message.reply_text(f'❌ Ошибка при запуске приложения: {e}')
        
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка при поиске/запуске приложения: {e}')
    finally:
        context.user_data.pop('waiting_for_app', None)

# Отправка информации о системе
async def send_system_info(chat_id: int, bot: Bot):
    try:
        uname = platform.uname()
        system_info = f"""
🖥️ *Информация о системе*:
- *Система*: {uname.system}
- *Имя компьютера*: {uname.node}
- *Версия*: {uname.version}
- *Релиз*: {uname.release}
- *Процессор*: {uname.processor}
- *Архитектура*: {platform.architecture()[0]}

📊 *Использование ресурсов*:
- *CPU*: {psutil.cpu_percent()}%
- *Память*: {psutil.virtual_memory().percent}% использовано
- *Диск*: {psutil.disk_usage('/').percent}% использовано

🌐 *Сеть*:
- *IP-адреса*: {', '.join([addr.address for addr in psutil.net_if_addrs().get('Wi-Fi', []) if addr.family == 2])}
        """
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                system_info += f"\n🔋 *Батарея*: {battery.percent}% ({'заряжается' if battery.power_plugged else 'не заряжается'})"
        except:
            pass
        
        await bot.send_message(chat_id, system_info, parse_mode='Markdown')
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при получении информации о системе: {e}')

# Отправка скриншота
async def send_screenshot(chat_id: int, bot: Bot):
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = 'screenshot.png'
        screenshot.save(screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            await bot.send_photo(chat_id, photo)
        os.remove(screenshot_path)
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при создании скриншота: {e}')

def show_message_on_screen_thread(message):
    try:
        if platform.system() == 'Windows':
            toaster = ToastNotifier()
            toaster.show_toast(
                "Управление ПК",
                message,
                duration=10,
                icon_path=None,
                threaded=True
            )
    except Exception as e:
        logger.error(f"Ошибка при отображении сообщения: {e}")

# Выключение компьютера
async def shutdown_computer(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, '🔄 Выключаю компьютер...')
        if platform.system() == 'Windows':
            os.system('shutdown /s /t 1')
        else:
            os.system('shutdown -h now')
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при выключении: {e}')

# Перезагрузка компьютера
async def reboot_computer(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, '🔄 Перезагружаю компьютер...')
        if platform.system() == 'Windows':
            os.system('shutdown /r /t 1')
        else:
            os.system('shutdown -r now')
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при перезагрузке: {e}')

# Режим сна
async def sleep_computer(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, '💤 Перевожу компьютер в режим сна...')
        if platform.system() == 'Windows':
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        elif platform.system() == 'Darwin':
            os.system('pmset sleepnow')
        else:
            os.system('systemctl suspend')
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при переводе в режим сна: {e}')

# Изменение громкости
async def change_volume(chat_id: int, bot: Bot, delta: int):
    try:
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0) if delta < 0 else ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0) if delta < 0 else ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        elif platform.system() == 'Darwin':
            os.system(f"osascript -e 'set volume output volume ((output volume of (get volume settings)) + {delta})'")
        else:
            os.system(f"amixer set Master {abs(delta)}%{'+' if delta > 0 else '-'} unmute")
        
        await bot.send_message(chat_id, f'🔊 Громкость изменена на {delta}%')
    except Exception as e:
        await bot.send_message(chat_id, f'Ошибка при изменении громкости: {e}')

# Список процессов
async def list_processes(chat_id: int, bot: Bot):
    try:
        processes = []
        for proc in psutil.process_iter(['name']):
            try:
                processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        unique_processes = sorted(list(set(processes)))
        
        message = "📊 *Список всех процессов*:\n\n"
        message += "\n".join(unique_processes)
        
        max_length = 4000
        if len(message) > max_length:
            parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
            for part in parts:
                await bot.send_message(chat_id, part, parse_mode='Markdown')
        else:
            await bot.send_message(chat_id, message, parse_mode='Markdown')
        
    except Exception as e:
        await bot.send_message(chat_id, f'❌ Ошибка при получении списка процессов: {e}')

# Обработчик сообщений
@auth_required
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == "🔄 Обновить меню":
        await start(update, context)
        return
    
    chat_id = update.message.chat_id
    
    if text == "📊 Системная информация":
        await send_system_info(chat_id, context.bot)
    elif text == "📷 Скриншот экрана":
        await send_screenshot(chat_id, context.bot)
    elif text == "🔌 Выключить компьютер":
        await shutdown_computer(chat_id, context.bot)
    elif text == "🔄 Перезагрузить компьютер":
        await reboot_computer(chat_id, context.bot)
    elif text == "💤 Режим сна":
        await sleep_computer(chat_id, context.bot)
    elif text == "🎵 Громкость +10%":
        await change_volume(chat_id, context.bot, 10)
    elif text == "🔇 Громкость -10%":
        await change_volume(chat_id, context.bot, -10)
    elif text == "⌨️ Отправить команду":
        await context.bot.send_message(chat_id, 'Введите команду для выполнения:')
        context.user_data['waiting_for_cmd'] = True
    elif text == "📂 Список файлов":
        await context.bot.send_message(chat_id, 'Введите путь к папке (или оставьте пустым для текущей директории):')
        context.user_data['waiting_for_path'] = True
    elif text == "🚀 Открыть приложение":
        await context.bot.send_message(chat_id, 'Введите название приложения для запуска (например: notepad.exe или chrome.exe), \nИли используйте путь к файлу: (например: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe)')
        context.user_data['waiting_for_app'] = True
    elif text == "⚡️ Включить ПК":
        await wake_up_pc(chat_id, context.bot)
    elif text == "⚡️ Список процессов":
        await list_processes(chat_id, context.bot)
    elif text == "❌ Закрыть процесс":
        await context.bot.send_message(chat_id, 'Введите название процесса для закрытия (например: chrome или chrome.exe):')
        context.user_data['waiting_for_kill'] = True
    elif text == "💬 Отправить сообщение":
        await context.bot.send_message(chat_id, 'Введите сообщение, которое появится на экране:')
        context.user_data['waiting_for_msg'] = True
    elif 'waiting_for_cmd' in context.user_data:
        command = update.message.text
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            if len(output) > 4000:
                output = output[:4000] + "\n\n... (сообщение обрезано)"
            await update.message.reply_text(f'✅ Результат выполнения команды:\n```\n{output}\n```', parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f'❌ Ошибка при выполнении команды: {e}')
        finally:
            context.user_data.pop('waiting_for_cmd', None)
    elif 'waiting_for_path' in context.user_data:
        path = update.message.text if update.message.text else '.'
        try:
            files = os.listdir(path)
            files_str = "\n".join(files)
            if len(files_str) > 4000:
                files_str = files_str[:4000] + "\n\n... (список обрезан)"
            await update.message.reply_text(f'📂 Содержимое папки {path}:\n```\n{files_str}\n```', parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f'❌ Ошибка при получении списка файлов: {e}')
        finally:
            context.user_data.pop('waiting_for_path', None)
    elif 'waiting_for_app' in context.user_data:
        await open_application(update, context)
    elif 'waiting_for_kill' in context.user_data:
        process_name = update.message.text.strip()
        try:
            if process_name.lower().endswith('.exe'):
                process_name = process_name[:-4]
            
            killed = False
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name']
                    if proc_name.lower().endswith('.exe'):
                        proc_name = proc_name[:-4]
                    
                    if proc_name.lower() == process_name.lower():
                        proc.kill()
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if killed:
                await update.message.reply_text(f'✅ Процесс {process_name} успешно закрыт!')
            else:
                await update.message.reply_text(f'❌ Процесс {process_name} не найден или не может быть закрыт')
        
        except Exception as e:
            await update.message.reply_text(f'❌ Ошибка при закрытии процесса: {e}')
        finally:
            context.user_data.pop('waiting_for_kill', None)
    elif 'waiting_for_msg' in context.user_data:
        message = update.message.text
        try:
            Thread(target=show_message_on_screen_thread, args=(message,), daemon=True).start()
            await update.message.reply_text('✅ Сообщение отправлено в виде уведомления!')
        except Exception as e:
            await update.message.reply_text(f'❌ Ошибка при отображении сообщения: {e}')
        finally:
            context.user_data.pop('waiting_for_msg', None)

# Обработка ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f'Ошибка: {context.error}', exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text('⚠️ Произошла ошибка при обработке запроса.')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()