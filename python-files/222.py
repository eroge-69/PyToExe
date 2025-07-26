import serial
import psutil
import time
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import requests
import json
from datetime import datetime, timedelta
from mcstatus import JavaServer

# Глобальные переменные для кэширования данных о погоде
weather_data = None
last_weather_update = None

def send_to_display(text1, text2='', port='COM1', baudrate=9600):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(b'\x0C')  # Clear display
            time.sleep(0.1)
            ser.write(text1[:20].encode('cp866').ljust(20))
            if text2:
                ser.write(b'\x0D')  # Переход на новую строку
                ser.write(text2[:20].encode('cp866').ljust(20))
    except serial.SerialException:
        print(f"Error: Could not open port {port}")



def get_cpu_usage():
    return f"CPU: {psutil.cpu_percent()}%"

def get_ram_usage():
    ram = psutil.virtual_memory()
    used_gb = ram.used / (1024 ** 3)
    total_gb = ram.total / (1024 ** 3)
    return f"RAM: {used_gb:.1f}/{total_gb:.1f}GB"

def get_network_usage():
    net_io_1 = psutil.net_io_counters()
    time.sleep(1)
    net_io_2 = psutil.net_io_counters()
    total_mb = (net_io_2.bytes_sent - net_io_1.bytes_sent + net_io_2.bytes_recv - net_io_1.bytes_recv) * 8 / (1024 ** 2)
    return f"Net: {total_mb:.2f}Mb/s"

def get_current_time_and_date():
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%d.%m")
    return f"{time_str} {date_str}"

def create_image():
    # Create a simple image for the tray icon
    image = Image.new('RGB', (64, 64), color = (73, 109, 137))
    d = ImageDraw.Draw(image)
    d.text((10,10), "Info", fill=(255,255,0))
    return image

def exit_action(icon):
    icon.stop()

def get_wind_direction(degrees):
    directions = ['С', 'С-В', 'В', 'Ю-В', 'Ю', 'Ю-З', 'З', 'С-З']
    index = round(degrees / 45) % 8
    return directions[index]

def get_weather_data():
    global weather_data, last_weather_update
    current_time = datetime.now()

    if weather_data is None or last_weather_update is None or (current_time - last_weather_update) > timedelta(minutes=30):
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=20.01&longitude=20.35&current=temperature_2m,relative_humidity_2m,rain,snowfall,surface_pressure,wind_speed_10m,wind_direction_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow"
            response = requests.get(url)
            weather_data = json.loads(response.text)['current']
            last_weather_update = current_time
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    return weather_data

def display_info():
    while True:
        cpu_usage = get_cpu_usage()
        ram_usage = get_ram_usage()
        send_to_display(cpu_usage, ram_usage)
        time.sleep(2)

        net_usage = get_network_usage()
        current_time_and_date = get_current_time_and_date()
        send_to_display(net_usage, current_time_and_date)
        time.sleep(2)
        
        # Отображение данных о погоде
        weather = get_weather_data()
        if weather:
            precipitation = "Ясно"
            if weather['rain'] > 0 or weather['snowfall'] > 0:
                precipitation = "Осадки"
            
            weather_info1 = f"T:{weather['temperature_2m']}C В:{weather['relative_humidity_2m']}% {precipitation}"
            
            pressure_mmhg = weather['surface_pressure'] * 0.75  # Конвертация гПа в мм рт.ст.
            wind_direction = get_wind_direction(weather['wind_direction_10m'])
            weather_info2 = f"Д:{pressure_mmhg:.0f} В:{weather['wind_speed_10m']}м/с {wind_direction}"
            
            send_to_display(weather_info1, weather_info2)
            time.sleep(2)
        minecraft_status = get_minecraft_status("192.168.1.199")
        send_to_display(minecraft_status)
        time.sleep(1)

def run():
    info_thread = threading.Thread(target=display_info, daemon=True)
    info_thread.start()
    menu = Menu(MenuItem('Exit', exit_action))
    icon = Icon("name", create_image(), "System Info Display", menu)
    icon.run()

if __name__ == "__main__":
    run()