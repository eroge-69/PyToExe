import platform
import psutil
import os
import socket
from datetime import datetime
import telebot
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Настройки Telegram
BOT_TOKEN = '8494173543:AAFfFqb-x6GrxmHlBCU9HKYFgLBAiWsmHp0'  # Замените на ваш токен
CHAT_ID = '7221793923'      # Замените на ваш chat_id

bot = telebot.TeleBot(BOT_TOKEN)

# Функция для получения chat_id (для отладки)
@bot.message_handler(commands=['start', 'getid'])
def send_welcome(message):
    chat_id = message.chat.id
    print(f"Chat ID: {chat_id}")
    bot.reply_to(message, f"Your Chat ID is {chat_id}. Use this in the script.")

def get_system_info():
    """
    Собирает информацию о системе, включая видеокарту и сетевые параметры.
    """
    info = {}
    
    # Информация об операционной системе
    info['OS'] = platform.system()
    info['OS Version'] = platform.release()
    info['OS Details'] = platform.version()
    
    # Информация о процессоре
    info['Processor'] = platform.processor()
    info['CPU Cores (Physical)'] = psutil.cpu_count(logical=False)
    info['CPU Cores (Logical)'] = psutil.cpu_count(logical=True)
    info['CPU Frequency (MHz)'] = round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else "N/A"
    
    # Информация о памяти
    memory = psutil.virtual_memory()
    info['Total RAM (GB)'] = round(memory.total / (1024 ** 3), 2)
    info['Used RAM (GB)'] = round(memory.used / (1024 ** 3), 2)
    info['Free RAM (GB)'] = round(memory.free / (1024 ** 3), 2)
    
    # Информация о диске
    disk = psutil.disk_usage('/')
    info['Total Disk Space (GB)'] = round(disk.total / (1024 ** 3), 2)
    info['Used Disk Space (GB)'] = round(disk.used / (1024 ** 3), 2)
    info['Free Disk Space (GB)'] = round(disk.free / (1024 ** 3), 2)
    
    # Информация о видеокарте
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                info['GPU'] = gpus[0].name
                info['GPU Memory Total (GB)'] = round(gpus[0].memoryTotal / 1024, 2)
                info['GPU Memory Used (GB)'] = round(gpus[0].memoryUsed / 1024, 2)
                info['GPU Memory Free (GB)'] = round(gpus[0].memoryFree / 1024, 2)
                info['GPU Driver'] = gpus[0].driver
            else:
                info['GPU'] = "No GPU detected"
        except Exception:
            info['GPU'] = "Unable to retrieve GPU info"
    else:
        info['GPU'] = "GPUtil not installed"
    
    # Информация о сети
    try:
        info['Hostname'] = socket.gethostname()
        info['Local IP Address'] = socket.gethostbyname(socket.gethostname())
        # Получение информации о сетевых интерфейсах
        net_info = psutil.net_if_addrs()
        for interface, addrs in net_info.items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    info[f'Network Interface ({interface}) IP'] = addr.address
                    info[f'Network Interface ({interface}) Netmask'] = addr.netmask
    except Exception as e:
        info['Network Info'] = f"Unable to retrieve network info: {e}"
    
    # Информация о Python
    info['Python Version'] = platform.python_version()
    
    # Время запуска системы
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    info['System Boot Time'] = boot_time.strftime('%Y-%m-%d %H:%M:%S')
    
    return info

def format_system_info(info):
    """
    Форматирует информацию для отправки в Telegram.
    """
    message = "Анализ системной информации:\n\n"
    for key, value in info.items():
        message += f"{key}: {value}\n"
    return message

def send_to_telegram(message):
    """
    Отправляет сообщение в Telegram.
    """
    try:
        bot.send_message(CHAT_ID, message)
        print("Данные успешно отправлены в Telegram!")
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Ошибка при отправке в Telegram: {e}")
        if e.error_code == 403:
            print("Возможные причины ошибки 403:")
            print("- Неверный CHAT_ID. Убедитесь, что вы используете правильный ID чата.")
            print("- Бот не добавлен в чат или пользователь не начал диалог (/start).")
            print("- Попробуйте отправить /start или /getid вашему боту для получения chat_id.")

if __name__ == "__main__":
    try:
        # Собираем и отправляем системную информацию
        system_info = get_system_info()
        formatted_message = format_system_info(system_info)
        send_to_telegram(formatted_message)
        
        # Запускаем бота для обработки команд
        bot.polling(none_stop=False, interval=0, timeout=20)
    except Exception as e:
        print(f"Произошла ошибка: {e}")