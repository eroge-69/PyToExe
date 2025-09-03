import requests
import datetime

# Словарь с координатами (широта и долгота) основных районов Санкт-Петербурга
districts = {
    'Адмиралтейский': {'lat': 59.9311, 'lon': 30.3009},
    'Василеостровский': {'lat': 59.9414, 'lon': 30.2620},
    'Выборгский': {'lat': 60.0393, 'lon': 30.3550},
    'Калининский': {'lat': 60.0014, 'lon': 30.3944},
    'Кировский': {'lat': 59.8796, 'lon': 30.2616},
    'Колпинский': {'lat': 59.7410, 'lon': 30.6016},
    'Красногвардейский': {'lat': 59.9731, 'lon': 30.4768},
    'Красносельский': {'lat': 59.8293, 'lon': 30.1413},
    'Кронштадтский': {'lat': 59.9884, 'lon': 29.7734},
    'Курортный (Сестрорецк)': {'lat': 60.1633, 'lon': 29.8556},
    'Московский': {'lat': 59.8516, 'lon': 30.3210},
    'Невский': {'lat': 59.8565, 'lon': 30.4636},
    'Петроградский': {'lat': 59.9664, 'lon': 30.3115},
    'Петродворцовый (Петергоф)': {'lat': 59.8845, 'lon': 29.9086},
    'Приморский': {'lat': 60.0138, 'lon': 30.2568},
    'Пушкинский (Царское Село)': {'lat': 59.7212, 'lon': 30.4040},
    'Фрунзенский': {'lat': 59.8930, 'lon': 30.3638},
    'Центральный': {'lat': 59.9311, 'lon': 30.3609}
}

def get_weather_openmeteo(lat, lon):
    """
    Функция для получения данных о погоде с Open-Meteo API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,pressure_msl',
        'timezone': 'Europe/Moscow',
        'forecast_days': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

def weather_code_to_text(code):
    """
    Преобразование кода погоды в текстовое описание
    Коды погоды WMO: https://open-meteo.com/en/docs
    """
    weather_codes = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        48: 'Инейный туман',
        51: 'Лекая морось',
        53: 'Умеренная морось',
        55: 'Сильная морось',
        61: 'Небольшой дождь',
        63: 'Умеренный дождь',
        65: 'Сильный дождь',
        80: 'Небольшой ливень',
        81: 'Умеренный ливень',
        82: 'Сильный ливень',
        95: 'Гроза'
    }
    return weather_codes.get(code, 'Неизвестно')

def display_weather(data, district_name):
    """
    Функция для отображения данных о погоде
    """
    if data is None or 'current' not in data:
        print(f"Не удалось получить данные для {district_name}.")
        return

    current = data['current']
    
    temp = current['temperature_2m']
    feels_like = current['apparent_temperature']
    humidity = current['relative_humidity_2m']
    pressure = current['pressure_msl']  # давление в гПа
    wind_speed = current['wind_speed_10m']
    weather_desc = weather_code_to_text(current['weather_code'])

    # Конвертируем давление в мм рт. ст.
    pressure_mmhg = pressure * 0.750062

    print(f"\n📍 {district_name}")
    print(f"   Погода: {weather_desc}")
    print(f"   Температура: {temp}°C (ощущается как {feels_like}°C)")
    print(f"   Влажность: {humidity}%")
    print(f"   Давление: {pressure_mmhg:.1f} мм рт. ст.")
    print(f"   Ветер: {wind_speed} м/с")
    print("-" * 40)

def main():
    print("🌤️  Погода в Санкт-Петербурге по районам")
    print("=" * 50)
    print(f"Актуально на: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 50)

    # Запрос погоды для каждого района
    for district, coords in districts.items():
        weather_data = get_weather_openmeteo(coords['lat'], coords['lon'])
        display_weather(weather_data, district)
def get_single_district_weather(district_name):
    """
    Функция для получения погоды только для одного района
    """
    if district_name in districts:
        coords = districts[district_name]
        weather_data = get_weather_openmeteo(coords['lat'], coords['lon'])
        display_weather(weather_data, district_name)
    else:
        print(f"Район '{district_name}' не найден в списке.")
        print("Доступные районы:", ', '.join(districts.keys()))

# Дополнительная функция для сравнения погоды во всех районах
def compare_districts():
    """
    Функция для сравнения температуры во всех районах
    """
    print("\n🌡️  Сравнение температуры по районам:")
    print("=" * 35)
    
    temperatures = {}
    for district, coords in districts.items():
        weather_data = get_weather_openmeteo(coords['lat'], coords['lon'])
        if weather_data and 'current' in weather_data:
            temp = weather_data['current']['temperature_2m']
            temperatures[district] = temp
    
    # Сортируем районы по температуре
    sorted_temps = sorted(temperatures.items(), key=lambda x: x[1], reverse=True)
    
    for district, temp in sorted_temps:
        print(f"{district:<25}: {temp:>5}°C")

if __name__ == "__main__":
    # Основной режим работы - показать погоду во всех районах
    main()
    
    # Дополнительно: можно раскомментировать для других режимов
    # compare_districts()  # Сравнение температуры
    
    # Для получения погоды только в одном районе:
    # get_single_district_weather("Василеостровский")