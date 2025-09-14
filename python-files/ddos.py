import requests
import threading

def send_requests(url, count):
    for _ in range(count):
        try:
            response = requests.get(url)
            print(f"Request sent, status code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Введите URL сайта: ")
    total_requests = int(input("Введите количество запросов: "))
    threads = []

    # Можно запускать запросы в нескольких потоках для ускорения
    for _ in range(10):  # например, 10 потоков
        t = threading.Thread(target=send_requests, args=(url, total_requests // 10))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Все запросы отправлены.")
