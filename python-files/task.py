import requests
import os

API_URL = "https://sunrisetelegram.ru/api/task/create"
API_FILE = "Api.txt"

def load_or_request_api_key():
    """Загружает API-ключ из файла или запрашивает у пользователя"""
    if os.path.exists(API_FILE):
        with open(API_FILE, 'r') as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
    
    api_key = input("Введите ваш API ключ: ").strip()
    with open(API_FILE, 'w') as f:
        f.write(api_key)
    return api_key

def get_task_data(api_key):
    """Запрашивает у пользователя данные для создания задачи"""
    print("\n" + "="*40)
    print("Введите данные для создания новой задачи")
    print("="*40)
    
    service_id = input("Введите ID услуги для заказа: ").strip()
    url_task = input("Введите ссылку на ресурс для подписки: ").strip()
    quantity = input("Введите количество для подписки: ").strip()
    title = input("Введите название заказа: ").strip()
    
    return {
        "user_api": api_key,
        "id": service_id,
        "url_task": url_task,
        "quantity": quantity,
        "title": title
    }

def send_request(params, data):
    """Отправляет запрос к API и обрабатывает ответ"""
    try:
        response = requests.post(
            API_URL,
            params={"user_api": params["user_api"]},
            data={
                "id": data["id"],
                "url_task": data["url_task"],
                "quantity": data["quantity"],
                "title": data["title"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("\n✅ Задача успешно создана!")
                print(f"ID задачи: {result.get('task_id')}")
                print(f"Слотов: {result.get('slots')}")
                print(f"Стоимость: {result.get('total_cost')}")
                print(f"Порт: {result.get('port')}")
                print(f"Количество строк в listwork: {result.get('listwork_lines')}")
            else:
                print("\n❌ Ошибка при создании задачи:")
                print(response.text)
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка при выполнении запроса: {e}")
    except ValueError as e:
        print(f"\n❌ Ошибка при обработке JSON ответа: {e}")

def main():
    print("Скрипт для создания задач через API SunriseTelegram")
    print("Для выхода введите 'exit' в любое время\n")
    
    # Загружаем или запрашиваем API ключ
    api_key = load_or_request_api_key()
    
    while True:
        try:
            # Получаем данные задачи от пользователя
            task_data = get_task_data(api_key)
            
            # Проверяем на команду выхода
            if any(value.lower() == 'exit' for value in task_data.values() if isinstance(value, str)):
                print("\nЗавершение работы...")
                break
                
            # Отправляем запрос
            print("\nОтправляем запрос к API...")
            send_request(
                params={"user_api": api_key},
                data={
                    "id": task_data["id"],
                    "url_task": task_data["url_task"],
                    "quantity": task_data["quantity"],
                    "title": task_data["title"]
                }
            )
            
            # Предлагаем создать еще одну задачу
            choice = input("\nХотите создать еще одну задачу? (y/n): ").strip().lower()
            if choice != 'y':
                print("\nЗавершение работы...")
                break
                
        except KeyboardInterrupt:
            print("\n\nЗавершение работы...")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            print("Попробуйте еще раз\n")

if __name__ == "__main__":
    main()