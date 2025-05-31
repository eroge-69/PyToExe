import time
import requests
import re


def process_credentials(mail, password):
    # Здесь вы можете выполнять любые действия с данными
    print(f"Обработка данных:\nПочта: {mail}\nПароль: {password}\n")
    
    url = f"https://api.firstmail.ltd/v1/market/get/message?username={mail}&password={password}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "884acd1f-38a4-45d3-b810-7399217594bb"
    }
    
    max_attempts = 5
    attempts = 0
    verification_code = None

    time.sleep(10)

    while attempts < max_attempts:
        response = requests.get(url, headers=headers)
        response_json = response.json()  # Парсим ответ в JSON

        if response_json.get("has_message", False):
            # Если сообщение есть, ищем код верификации
            pattern = r'<[^>]+>(?:[^0-9]+)?(\d{6})(?:[^0-9]+)?</[^>]+>'
            matches = re.findall(pattern, response_json['message'])
            verification_code = matches[0] if matches else None
            
            if verification_code:
                print(f"Код верификации: {verification_code}")
                return verification_code
        else:
            attempts += 1
            if attempts < max_attempts:
                print(f"Сообщение не найдено. Попытка {attempts}")
                time.sleep(10)  # Ждем 5 секунд перед следующей попыткой
            else:
                print(f"Error: Сообщение не найдено после {max_attempts} попыток.")


def main():
    while True:
        try:
            user_input = input("Введите данные в формате mail:password (или 'exit' для выхода): ").strip()
            if user_input.lower() == 'exit':
                print("Выход из программы.")
                break

            if ':' not in user_input:
                print("Неверный формат. Используйте mail:password")
                continue

            mail, password = user_input.split(':', 1)  # Разделить только по первому ':'
            process_credentials(mail, password)

        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break


if __name__ == "__main__":
    main()
