import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен вашего бота (получите у @BotFather)
BOT_TOKEN = "7742035954:AAE2EnOW_NXcCkmz7LCIgqx5MqI6ouAir4A"

# ID вашего Telegram аккаунта (для безопасности)
ADMIN_USER_ID = 7476936312  # Замените на ваш ID

# Команды которые разрешено выполнять
ALLOWED_COMMANDS = {
    'status': 'получить статус системы',
    'screenshot': 'сделать скриншот',
    'shutdown': 'выключить компьютер через 60 сек',
    'cancel_shutdown': 'отменить выключение',
    'restart': 'перезагрузить компьютер через 60 сек',
    'ip': 'получить IP адрес',
    'processes': 'показать запущенные процессы',
    'disk': 'показать использование диска'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен!")
        return
    
    commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in ALLOWED_COMMANDS.items()])
    await update.message.reply_text(
        f"🤖 Бот для управления компьютером\n\n"
        f"Доступные команды:\n{commands_list}"
    )

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд"""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Доступ запрещен!")
        return

    command = update.message.text.split()[0][1:]  # Убираем / из команды

    try:
        if command == 'status':
            await system_status(update, context)
        elif command == 'screenshot':
            await take_screenshot(update, context)
        elif command == 'shutdown':
            await shutdown_computer(update, context)
        elif command == 'cancel_shutdown':
            await cancel_shutdown(update, context)
        elif command == 'restart':
            await restart_computer(update, context)
        elif command == 'ip':
            await get_ip_address(update, context)
        elif command == 'processes':
            await get_processes(update, context)
        elif command == 'disk':
            await get_disk_usage(update, context)
        else:
            await update.message.reply_text("❌ Неизвестная команда")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить статус системы"""
    try:
        # Для Windows
        if os.name == 'nt':
            uptime = subprocess.check_output('powershell "Get-WmiObject -Class Win32_OperatingSystem | Select-Object -Property LastBootUpTime"', shell=True)
            memory = subprocess.check_output('systeminfo | find "Available Physical Memory"', shell=True)
            await update.message.reply_text(f"🖥️ Статус системы:\nВремя работы: {uptime.decode()}\nПамять: {memory.decode()}")
        # Для Linux/Mac
        else:
            uptime = subprocess.check_output(['uptime']).decode()
            memory = subprocess.check_output(['free', '-h']).decode()
            await update.message.reply_text(f"🖥️ Статус системы:\n{uptime}\nПамять:\n{memory}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения статуса: {str(e)}")

async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сделать скриншот"""
    try:
        # Установите библиотеку для скриншотов: pip install pyautogui pillow
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        
        with open('screenshot.png', 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="📸 Скриншот экрана")
        
        os.remove('screenshot.png')
    except ImportError:
        await update.message.reply_text("❌ Библиотека pyautogui не установлена")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка создания скриншота: {str(e)}")

async def shutdown_computer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выключить компьютер"""
    try:
        if os.name == 'nt':  # Windows
            os.system("shutdown /s /t 60")
            await update.message.reply_text("🔄 Компьютер выключится через 60 секунд")
        else:  # Linux/Mac
            os.system("shutdown -h +1")
            await update.message.reply_text("🔄 Компьютер выключится через 60 секунд")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка выключения: {str(e)}")

async def cancel_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить выключение"""
    try:
        if os.name == 'nt':  # Windows
            os.system("shutdown /a")
            await update.message.reply_text("✅ Выключение отменено")
        else:  # Linux/Mac
            os.system("shutdown -c")
            await update.message.reply_text("✅ Выключение отменено")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отмены выключения: {str(e)}")

async def restart_computer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезагрузить компьютер"""
    try:
        if os.name == 'nt':  # Windows
            os.system("shutdown /r /t 60")
            await update.message.reply_text("🔄 Компьютер перезагрузится через 60 секунд")
        else:  # Linux/Mac
            os.system("shutdown -r +1")
            await update.message.reply_text("🔄 Компьютер перезагрузится через 60 секунд")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка перезагрузки: {str(e)}")

async def get_ip_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить IP адрес"""
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Получение внешнего IP
        import requests
        external_ip = requests.get('https://api.ipify.org').text
        
        await update.message.reply_text(f"🌐 IP адреса:\nЛокальный: {local_ip}\nВнешний: {external_ip}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения IP: {str(e)}")

async def get_processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить список процессов"""
    try:
        if os.name == 'nt':  # Windows
            processes = subprocess.check_output(['tasklist']).decode()[:4000]  # Ограничение длины
        else:  # Linux/Mac
            processes = subprocess.check_output(['ps', 'aux']).decode()[:4000]
        
        await update.message.reply_text(f"📊 Процессы:\n```\n{processes}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения процессов: {str(e)}")

async def get_disk_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить информацию о дисках"""
    try:
        if os.name == 'nt':  # Windows
            disk_info = subprocess.check_output(['wmic', 'logicaldisk', 'get', 'size,freespace,caption']).decode()
        else:  # Linux/Mac
            disk_info = subprocess.check_output(['df', '-h']).decode()
        
        await update.message.reply_text(f"💾 Использование диска:\n```\n{disk_info}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения информации о дисках: {str(e)}")

def main():
    """Основная функция"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик для всех команд
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/'), handle_command))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()