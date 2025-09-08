import re
from collections import defaultdict

def analyze_door_logs(log_file_path, target_month):
    """
    Анализирует лог-файл открытий дверей и систематизирует данные по картам доступа за указанный месяц.

    Args:
        log_file_path (str): Путь к текстовому файлу с логами. Формат логов: "No., card type, card No., date, time".
                                 Например: "1,master,567713,25-09-08,11:59"
        target_month (int):  Номер месяца (1-12) для анализа.

    Returns:
        dict: Словарь, где ключи - ID карт доступа, а значения - список дат и времени
              открытий дверей этой картой в течение месяца. Возвращает пустой словарь, если
              файл не найден или возникла ошибка при чтении.
    """

    door_access_data = defaultdict(list)

    try:
        with open(log_file_path, 'r') as log_file:
            # Пропускаем первые две строки (заголовок)
            next(log_file)
            next(log_file)

            for line in log_file:
                # Регулярное выражение адаптировано под формат лога:  "No., card type, card No., date, time"
                match = re.match(r"\s*\d+,(.+?),(\d+),(\d{2}-\d{2}-\d{2}),(\d{2}:\d{2})", line)
                if match:
                    card_type = match.group(1).strip() # Тип карты (master, guest и т.д.)
                    card_id = match.group(2)
                    date_str = match.group(3)
                    time_str = match.group(4)

                    # Преобразуем дату из DD-MM-YY в YYYY-MM-DD для удобства сравнения
                    day, month, year = date_str.split('-')
                    year = "20" + year  # Предполагаем, что год начинается с 20 (2008, 2009 и т.д.)
                    date = f"{year}-{month}-{day}"
                    time = time_str + ":00" #Добавляем секунды , чтобы формат соответствовал исходному.


                    # Проверяем месяц
                    if int(month) == target_month:
                        door_access_data[card_id].append(f"{date} {time}")
                else:
                    print(f"Некорректный формат строки лога: {line.strip()}")

    except FileNotFoundError:
        print(f"Ошибка: Файл логов не найден по пути: {log_file_path}")
        return {}
    except Exception as e:
        print(f"Ошибка при чтении файла логов: {e}")
        return {}

    return dict(door_access_data)



def main():
    log_file = "door_logs.txt"  # Замените на имя вашего файла логов
    target_month = 8   # Месяц для анализа (август)
    access_data = analyze_door_logs(log_file, target_month)

    if access_data:
        print("Систематизированные данные об открытии дверей:")
        for card_id, access_times in access_data.items():
            print(f"  Карта доступа: {card_id}")
            for time in access_times:
                print(f"    - {time}")
    else:
        print("Не удалось получить данные об открытии дверей.")

if __name__ == "__main__":
    main()
