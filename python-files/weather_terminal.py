import os
import time
from threading import Thread
import requests
import ctypes

# === Настройки ===
API_KEY = '19be55c29e9c1c982227ee3cf166ed0b'
CITY = 'Moscow'
UNITS = 'metric'
WEATHER_UPDATE_INTERVAL = 10
TIME_UPDATE_INTERVAL = 3

FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# === Цвета для вывода в консоли ===
COLORS = {
    'утро': '\033[92m',   # зелёный
    'день': '\033[93m',   # жёлтый
    'вечер': '\033[94m',  # синий
    'reset': '\033[0m',
}

def set_console_size(lines=30, columns=80):
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleScreenBufferSize(kernel32.GetStdHandle(-11), (columns << 16) | lines)
        except:
            os.system(f'mode con: cols={columns} lines={lines}')


def get_weather_forecast():
    url = f"{FORECAST_URL}?q={CITY}&appid={API_KEY}&units={UNITS}&lang=ru"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def parse_forecast(data):
    forecasts = data['list']
    result = {'today': {}, 'tomorrow': {}}
    
    for entry in forecasts:
        dt_txt = entry['dt_txt']
        time_str = dt_txt.split()[1]
        date_str = dt_txt.split()[0]

        hour = int(time_str.split(':')[0])

        day_part = ''
        if 5 <= hour < 12:
            day_part = 'утро'
        elif 12 <= hour < 18:
            day_part = 'день'
        elif 18 <= hour < 23:
            day_part = 'вечер'

        if not day_part:
            continue

        temp = entry['main']['temp']
        desc = entry['weather'][0]['description']

        day_dict = result['tomorrow'] if date_str > forecasts[0]['dt_txt'].split()[0] else result['today']

        if day_part not in day_dict:
            day_dict[day_part] = {'temp': temp, 'desc': desc}

    return result

def draw_weather_box(title, data):
    lines = []
    max_len = len(f"== {title} ==")
    lines.append(f"== {title} ==")

    for period, info in data.items():
        color = COLORS.get(period, COLORS['reset'])
        line = f"{color}{period.capitalize()}: {info['temp']}°C, {info['desc']}{COLORS['reset']}"
        lines.append(line)

    lines.append("=" * max_len)
    return "\n".join(lines)

# === Вывод времени и даты ===
def display_time(clock_mode=False):
    while True:
        now = time.localtime()
        current_time = time.strftime("%H:%M:%S", now)
        current_date = time.strftime("%d.%m.%Y", now)
        clear_screen()
        print(f"Дата: {current_date}")
        print(f"Текущее время: {current_time}")
        if clock_mode:
            print("\n[Показываю время...]")
        else:
            print("\n[Обновление данных о погоде...]")

        print("-" * 40 + "\n")
        time.sleep(TIME_UPDATE_INTERVAL)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# === Основной цикл работы ===
def main():
    weather_data = {}
    current_day = {}
    tomorrow_day = {}

    while True:
        try:
            raw_data = get_weather_forecast()
            if raw_data:
                parsed = parse_forecast(raw_data)
                current_day = parsed['today']
                tomorrow_day = parsed['tomorrow']
                print("[✔️ Данные о погоде успешно загружены]")
            else:
                print("[❌ Ошибка загрузки погоды]")

            clear_screen()
            print(draw_weather_box("Погода сегодня", current_day))
            print("\nВведите 1 чтобы увидеть прогноз на завтра или Enter для продолжения...")
            user_input = input("Ввод: ").strip()

            if user_input == '1':
                clear_screen()
                print(draw_weather_box("Погода завтра", tomorrow_day))
                print("\nНажмите Enter чтобы вернуться...")
                input()

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(WEATHER_UPDATE_INTERVAL)

if __name__ == '__main__':
    set_console_size(30, 80)

    time_thread = Thread(target=display_time, args=(True,), daemon=True)
    time_thread.start()

    main()