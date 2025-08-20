import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
from datetime import datetime


def parse_guilty_data():
    url = "https://milgram.jp/judge/result/season_3"  # Вставьте нужный URL

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Используем CSS селектор который вы скопировали
        target_div = soup.select_one(
            'body > main > article > section > section.sub-judge-contents > section > div > ul > li.character-3 > div:nth-child(2) > div > div')

        if target_div:
            # Извлекаем данные из data-атрибутов
            guilty_percent = target_div.get('data-guilty')  # "48.29"
            not_guilty_percent = target_div.get('data-not-guilty')  # "51.71"

            # Преобразуем в числа
            guilty = float(guilty_percent) if guilty_percent else None
            not_guilty = float(not_guilty_percent) if not_guilty_percent else None

            # Сохраняем результат
            result = {
                'timestamp': datetime.now().isoformat(),
                'guilty_percent': guilty,
                'not_guilty_percent': not_guilty,
            }

            # Записываем в файл
            with open('milgram_data.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

            print(f"[{datetime.now()}] Данные: Виновен {guilty}%, Не виновен {not_guilty}%")

        else:
            print(f"[{datetime.now()}] Элемент не найден")

    except Exception as e:
        print(f"[{datetime.now()}] Ошибка: {e}")



# Для тестирования
if __name__ == "__main__":

    # Или для периодического сбора
    schedule.every(5).minutes.do(parse_guilty_data)
    parse_guilty_data()  # Первый запуск
