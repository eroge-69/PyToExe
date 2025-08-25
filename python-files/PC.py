import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import subprocess
import os
import pyautogui
import psutil
import socket
import datetime
import time

# Настройка подробного логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Изменили на DEBUG для подробных логов
)
logger = logging.getLogger(__name__)

# Замените на ваш реальный токен
TOKEN = "7765911491:AAFNgXpr8NQcrIolh96E1xxJnWQc2XYyrHU"
ALLOWED_USERS = [1937084129]  # Замените на ваш реальный Telegram ID

def is_allowed(update: Update) -> bool:
    """Проверка прав доступа пользователя"""
    if update.effective_user.id in ALLOWED_USERS:
        return True
    logger.warning(f"Доступ запрещен для пользователя: {update.effective_user.id}")
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда начала работы с ботом"""
    if not is_allowed(update):
        await update.message.reply_text("🚫 Доступ запрещен!")
        return
    
    keyboard = [
        ["📊 Статус системы", "📸 Скриншот"],
        ["🔒 Заблокировать", "⏹️ Выключить"],
        ["🔄 Перезагрузить", "🗒️ Процессы"],
        ["🌐 Сеть", "📂 Файлы"],
        ["🎵 Громкость", "❓ Помощь"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 Бот управления ПК активирован!\n"
        "Выберите действие из меню ниже:",
        reply_markup=reply_markup
    )
    logger.info(f"Пользователь {update.effective_user.id} начал работу с ботом")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по командам"""
    if not is_allowed(update):
        return
    
    help_text = """
📋 Доступные команды:

📊 Статус системы - информация о CPU, RAM, диске
📸 Скриншот - сделать снимок экрана
🔒 Заблокировать - заблокировать компьютер
⏹️ Выключить - выключить компьютер
🔄 Перезагрузить - перезагрузить компьютер
🗒️ Процессы - список запущенных процессов
🌐 Сеть - информация о сетевых подключениях
📂 Файлы - работа с файлами
🎵 Громкость - управление громкостью

⚙️ Команды:
/start - начать работу
/help - эта справка
/ip - IP адрес компьютера
/uptime - время работы системы
/cmd <команда> - выполнить команду
"""
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус системы"""
    if not is_allowed(update):
        return
    
    try:
        # Получаем информацию о системе
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        
        status_text = f"""
📊 Статус системы:

💻 CPU: {cpu}%
🧠 RAM: {ram.percent}% ({ram.used//1024//1024}MB/{ram.total//1024//1024}MB)
💾 Диск: {disk.percent}% ({disk.used//1024//1024}MB/{disk.total//1024//1024}MB)
⏰ Время работы: {str(uptime).split('.')[0]}
"""
        await update.message.reply_text(status_text)
        
    except Exception as e:
        error_msg = f"❌ Ошибка при получении статуса: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скриншот экрана"""
    if not is_allowed(update):
        return
    
    try:
        # Делаем скриншот
        screenshot_path = 'telegram_bot_screenshot.png'
        img = pyautogui.screenshot()
        img.save(screenshot_path)
        
        # Отправляем скриншот
        with open(screenshot_path, 'rb') as photo:
            await update.message.reply_photo(
                photo, 
                caption="🖥️ Текущий экран"
            )
        
        # Удаляем временный файл
        os.remove(screenshot_path)
        logger.info("Скриншот успешно отправлен")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при создании скриншота: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выключение компьютера"""
    if not is_allowed(update):
        return
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['shutdown', '/s', '/t', '60'], check=True)
            msg = "⏹️ Выключение через 60 секунд"
        else:  # Linux/Mac
            subprocess.run(['shutdown', '-h', '+1'], check=True)
            msg = "⏹️ Выключение через 1 минуту"
        
        await update.message.reply_text(msg)
        logger.info("Команда выключения отправлена")
        
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Ошибка при выключении: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"❌ Неизвестная ошибка: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезагрузка компьютера"""
    if not is_allowed(update):
        return
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['shutdown', '/r', '/t', '60'], check=True)
            msg = "🔄 Перезагрузка через 60 секунд"
        else:  # Linux/Mac
            subprocess.run(['shutdown', '-r', '+1'], check=True)
            msg = "🔄 Перезагрузка через 1 минуту"
        
        await update.message.reply_text(msg)
        logger.info("Команда перезагрузки отправлена")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при перезагрузке: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Блокировка компьютера"""
    if not is_allowed(update):
        return
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
        else:  # Linux
            # Попробуем разные команды для блокировки
            try:
                subprocess.run(['gnome-screensaver-command', '-l'], check=True)
            except:
                subprocess.run(['xdg-screensaver', 'lock'], check=True)
        
        await update.message.reply_text("🔒 Компьютер заблокирован")
        logger.info("Компьютер заблокирован")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при блокировке: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать запущенные процессы"""
    if not is_allowed(update):
        return
    
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Сортируем по использованию CPU
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        result = "🗒️ Топ-10 процессов по использованию CPU:\n\n"
        for i, proc in enumerate(processes[:10]):
            cpu = proc['cpu_percent'] or 0
            memory = proc['memory_percent'] or 0
            result += f"{i+1}. {proc['name']} (PID: {proc['pid']})\n"
            result += f"   CPU: {cpu:.1f}% | RAM: {memory:.1f}%\n\n"
        
        await update.message.reply_text(result)
        logger.info("Информация о процессах отправлена")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при получении процессов: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def network_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о сети"""
    if not is_allowed(update):
        return
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Получаем внешний IP
        external_ip = "Не удалось получить"
        try:
            external_ip = subprocess.run(
                ['curl', '-s', 'ifconfig.me'],
                capture_output=True, text=True, timeout=10
            ).stdout.strip()
        except:
            try:
                external_ip = subprocess.run(
                    ['curl', '-s', 'icanhazip.com'],
                    capture_output=True, text=True, timeout=10
                ).stdout.strip()
            except:
                pass
        
        # Информация о сетевых интерфейсах
        interfaces = psutil.net_if_addrs()
        net_info = f"🌐 Сетевая информация:\n\n"
        net_info += f"🖥️ Хостнейм: {hostname}\n"
        net_info += f"📡 Локальный IP: {local_ip}\n"
        net_info += f"🌍 Внешний IP: {external_ip}\n\n"
        
        net_info += "📶 Сетевые интерфейсы:\n"
        for interface, addrs in list(interfaces.items())[:5]:  # Ограничиваем количество
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    net_info += f"• {interface}: {addr.address}\n"
        
        await update.message.reply_text(net_info)
        logger.info("Информация о сети отправлена")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при получении сетевой информации: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def file_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Менеджер файлов"""
    if not is_allowed(update):
        return
    
    try:
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        
        file_list = f"📂 Файлы в директории:\n{current_dir}\n\n"
        
        # Показываем только первые 15 файлов/папок
        for i, file in enumerate(files[:15]):
            full_path = os.path.join(current_dir, file)
            if os.path.isdir(full_path):
                file_list += f"📁 {file}/\n"
            else:
                try:
                    size = os.path.getsize(full_path)
                    file_list += f"📄 {file} ({size} байт)\n"
                except:
                    file_list += f"📄 {file} (недоступен)\n"
        
        if len(files) > 15:
            file_list += f"\n... и еще {len(files) - 15} файлов/папок"
        
        await update.message.reply_text(file_list)
        logger.info("Информация о файлах отправлена")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при получении списка файлов: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def volume_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление громкостью"""
    if not is_allowed(update):
        return
    
    try:
        if os.name == 'nt':  # Windows
            # Для Windows можно использовать nircmd или другие утилиты
            volume_info = "🎵 Управление громкостью\n\n"
            volume_info += "Для Windows рекомендуется:\n"
            volume_info += "• Использовать nircmd\n"
            volume_info += "• Или системные средства\n"
            volume_info += "• Или сторонние утилиты"
        else:  # Linux
            # Для Linux
            volume_info = "🎵 Управление громкостью\n\n"
            volume_info += "Для Linux:\n"
            volume_info += "• amixer set Master 10%+\n"
            volume_info += "• amixer set Master 10%-\n"
            volume_info += "• amixer set Master toggle\n"
        
        await update.message.reply_text(volume_info)
        
    except Exception as e:
        error_msg = f"❌ Ошибка управления громкостью: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def ip_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить IP адрес"""
    if not is_allowed(update):
        return
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Получаем внешний IP
        external_ip = "Не удалось получить"
        try:
            external_ip = subprocess.run(
                ['curl', '-s', 'ifconfig.me'],
                capture_output=True, text=True, timeout=10
            ).stdout.strip()
        except:
            pass
        
        ip_info = f"🌐 IP адреса:\n\n"
        ip_info += f"🖥️ Локальный IP: {local_ip}\n"
        ip_info += f"🌍 Внешний IP: {external_ip}\n"
        ip_info += f"📡 Хостнейм: {hostname}"
        
        await update.message.reply_text(ip_info)
        logger.info("IP информация отправлена")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при получении IP: {e}"
        await update.message.reply_text(error_msg)
        logger.error(error_msg)

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполнение команды"""
    if not is_allowed(update):
        return
    
    if not context.args:
        await update.message.reply_text("ℹ️ Используйте: /cmd <команда>")
        return
    
    command = ' '.join(context.args)
    try:
        logger.info(f"Выполнение команды: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        output = result.stdout or result.stderr
        if not output:
            output = "Команда выполнена успешно (нет вывода)"
        
        # Ограничиваем длину сообщения
        if len(output) > 3000:
            output = output[:3000] + "\n... (вывод обрезан)"
        
        await update.message.reply_text(f"💻 Результат:\n```\n{output}\n```")
        logger.info(f"Команда выполнена: {command}")
        
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏰ Команда выполнена с таймаутом (30 секунд)")
        logger.warning(f"Таймаут команды: {command}")
    except Exception as e:
        error_msg = f"❌ Ошибка выполнения команды: {e}"
        await update.message.reply_text(error_msg)
        logger.error(f"Ошибка команды {command}: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (кнопок)"""
    if not is_allowed(update):
        return
    
    text = update.message.text
    logger.info(f"Получено сообщение: {text}")
    
    # Обработка кнопок
    if text == "📊 Статус системы":
        await status(update, context)
    elif text == "📸 Скриншот":
        await screenshot(update, context)
    elif text == "🔒 Заблокировать":
        await lock(update, context)
    elif text == "⏹️ Выключить":
        await shutdown(update, context)
    elif text == "🔄 Перезагрузить":
        await restart(update, context)
    elif text == "🗒️ Процессы":
        await processes(update, context)
    elif text == "🌐 Сеть":
        await network_info(update, context)
    elif text == "📂 Файлы":
        await file_manager(update, context)
    elif text == "🎵 Громкость":
        await volume_control(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "🤔 Неизвестная команда. Используйте кнопки меню или /help"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)

def main():
    """Основная функция запуска бота"""
    try:
        logger.info("Запуск бота управления ПК...")
        
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики команд
        handlers = [
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("status", status),
            CommandHandler("screenshot", screenshot),
            CommandHandler("shutdown", shutdown),
            CommandHandler("restart", restart),
            CommandHandler("lock", lock),
            CommandHandler("cmd", run_cmd),
            CommandHandler("ip", ip_address),
            CommandHandler("processes", processes),
            CommandHandler("network", network_info),
            CommandHandler("files", file_manager),
        ]
        
        for handler in handlers:
            application.add_handler(handler)
        
        # Обработчик текстовых сообщений
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        logger.info("Бот запущен. Ожидание сообщений...")
        print("Бот запущен! Проверьте Telegram...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}")
        print(f"Ошибка запуска: {e}")
        print("Проверьте:")
        print("1. Правильность токена бота")
        print("2. Интернет-соединение")
        print("3. Бот должен быть активирован в Telegram")

if __name__ == "__main__":
    main()