import requests

# URL файла на GitHub (raw версия)
url = 'https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/TV'

try:
    # Загружаем содержимое файла
    response = requests.get(url)
    response.raise_for_status()  # Проверка успешности запроса

    # Разбиваем содержимое на строки
    lines = response.text.splitlines()

    # Начинаем с 5285-й строки (учитываем, что индексы с 0)
    start_index = 5284  # так как строка 5285 — это индекс 5284

    # Обрабатываем все строки с этого индекса
    for line in lines[start_index:]:
        if 'rutube' in line:
            print(line)

except requests.RequestException as e:
    print(f"Ошибка при скачивании файла: {e}")