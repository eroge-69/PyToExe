import subprocess
import requests
import platform
import os

def get_gpu_info():
    try:
        # Для Windows
        if platform.system() == "Windows":
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name'
            ], capture_output=True, text=True)
            
            gpus = [line.strip() for line in result.stdout.split('\n') 
                   if line.strip() and line.strip() != 'Name']
            return gpus
        
        # Для Linux
        elif platform.system() == "Linux":
            result = subprocess.run([
                'lspci', '|', 'grep', '-i', 'vga'
            ], capture_output=True, text=True, shell=True)
            return result.stdout.split('\n')
        
        # Для macOS
        elif platform.system() == "Darwin":
            result = subprocess.run([
                'system_profiler', 'SPDisplaysDataType'
            ], capture_output=True, text=True)
            return result.stdout
        
    except Exception as e:
        return f"Ошибка: {e}"

def send_to_telegram(message, bot_token, chat_id):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False

def main():
    # Настройки бота (замените на свои)
    BOT_TOKEN = "7541342578:AAG8nWD6Ko32WtYX-sGpo0UyzW3GH8GcVw0"
    CHAT_ID = "7656693126"
    
    # Получаем информацию о системе
    system_info = f"""
🖥️ <b>Информация о системе:</b>
ОС: {platform.system()} {platform.release()}
Процессор: {platform.processor()}
Версия Python: {platform.python_version()}
    """
    
    # Получаем информацию о видеокарте
    gpu_info = get_gpu_info()
    gpu_message = f"🎮 <b>Видеокарта:</b> {gpu_info}"
    
    # Формируем полное сообщение
    full_message = system_info + "\n" + gpu_message
    
    # Отправляем в Telegram
    if send_to_telegram(full_message, BOT_TOKEN, CHAT_ID):
        print("Информация успешно отправлена!")
    else:
        print("Не удалось отправить информацию.")

if __name__ == "__main__":
    main()