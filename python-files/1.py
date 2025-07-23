import pandas as pd
from collections import defaultdict

# Пример данных (в реальной программе нужно заменить на чтение из файла)
data = [
    # Пример строки: дата, номер Э/к, фамилия, литры, тип топлива, и т.д.
    ("05-01", "652122351", "Мазаник", 37.33, "ДТ-Л-К5"),
    ("05-01", "652122351", "Мазаник", 75.00, "ДТ-Л-К5"),
    # ... остальные данные
]

# Создаем словарь для хранения данных: {фамилия: {дата: литры}}
fuel_data = defaultdict(lambda: defaultdict(float))

# Обработка данных (заполнение словаря)
for entry in data:
    date, _, surname, liters, _ = entry
    fuel_data[surname][date] += liters

# Преобразование в DataFrame для удобства
df = pd.DataFrame.from_dict(fuel_data, orient='index').fillna(0)

# Вывод таблицы
print(df)