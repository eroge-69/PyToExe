import folium
from folium.plugins import MiniMap, Fullscreen, MeasureControl, MarkerCluster
import requests
import time
from branca.element import Template, MacroElement

# Налаштування
API_KEY = "692664742c614623b3d124540250606"
MAP_CENTER = [48.3794, 31.1656]  # Географічний центр України
MAP_ZOOM = 6  # Оптимальний масштаб для всієї України

# Координати обласних центрів
oblasts = {
    "Київ": (50.450100, 30.523400),
    "Львів": (49.839683, 24.029717),
    "Харків": (49.993500, 36.230383),
    "Одеса": (46.482526, 30.723310),
    "Дніпро": (48.464717, 35.046183),
    "Запоріжжя": (47.838800, 35.139567),
    "Чернігів": (51.505510, 31.284870),
    "Суми": (50.907700, 34.798100),
    "Полтава": (49.588266, 34.551417),
    "Черкаси": (49.444433, 32.059767),
    "Житомир": (50.254650, 28.658667),
    "Вінниця": (49.232780, 28.468217),
    "Хмельницький": (49.422983, 26.987133),
    "Тернопіль": (49.553517, 25.594767),
    "Івано-Франківськ": (48.922633, 24.711117),
    "Ужгород": (48.620800, 22.287883),
    "Чернівці": (48.291500, 25.940300),
    "Рівне": (50.619900, 26.251617),
    "Луцьк": (50.747600, 25.325383),
    "Кропивницький": (48.507933, 32.262317),
    "Миколаїв": (46.975033, 31.994583),
    "Херсон": (46.635417, 32.616867),
}

def get_warning_level(wind_kph, rain_mm, condition):
    """
    Система класифікації небезпек на основі погодних умов
    """
    if wind_kph > 70 or ("Thunderstorm" in condition and wind_kph > 50):
        return ("red", "Висока небезпека", "⚠️")
    elif wind_kph > 50 or rain_mm > 20:
        return ("orange", "Помірна небезпека", "❗")
    elif wind_kph > 30 or rain_mm > 5:
        return ("lightorange", "Підвищена увага", "🔍")
    else:
        return ("green", "Безпечно", "✅")

# Створюємо деталізовану карту України
ukraine_map = folium.Map(
    location=MAP_CENTER,
    zoom_start=MAP_ZOOM,
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    control_scale=True,
    prefer_canvas=True
)

# Додаємо шар супутникових знімків
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Imagery',
    name='Супутникові знімки',
    overlay=False,
    control=True
).add_to(ukraine_map)

# Додаємо мінімап
MiniMap(toggle_display=True, position='bottomleft').add_to(ukraine_map)

# Додаємо кнопки повного екрану
Fullscreen(position='topright', title='Розгорнути', title_cancel='Згорнути').add_to(ukraine_map)

for name, (lat, lon) in oblasts.items():
    print(f"Отримую дані для: {name}...")
    
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        current = data['current']
        wind_kph = current['wind_kph']
        rain_mm = current['precip_mm']
        condition = current['condition']['text']
        humidity = current['humidity']
        temp_c = current['temp_c']
        pressure_mb = current['pressure_mb']
        
        # Визначення рівня небезпеки
        color, warning_level, icon = get_warning_level(wind_kph, rain_mm, condition)
        
        # Деталізований popup
        popup_html = f"""
        <div style="width:250px; font-family: Arial;">
            <h4 style="color:{color}; margin-bottom:5px;">{name}</h4>
            <div style="background-color:#f8f9fa; padding:10px; border-radius:5px;">
                <p style="margin:3px 0;"><b>Стан:</b> {condition}</p>
                <p style="margin:3px 0;"><b>Вітер:</b> {wind_kph} км/год</p>
                <p style="margin:3px 0;"><b>Опади:</b> {rain_mm} мм</p>
                <p style="margin:3px 0;"><b>Температура:</b> {temp_c}°C</p>
                <p style="margin:3px 0;"><b>Вологість:</b> {humidity}%</p>
                <p style="margin:3px 0;"><b>Тиск:</b> {pressure_mb} мбар</p>
                <p style="margin:3px 0; font-weight:bold; color:{color}">
                    {icon} {warning_level}
                </p>
            </div>
        </div>
        """
        
        # Додаємо маркер
        folium.Marker(
            location=(lat, lon),
            popup=popup_html,
            icon=folium.Icon(
                color=color,
                icon='info-sign',
                prefix='glyphicon'
            ),
            tooltip=f"{name}: {warning_level}"
        ).add_to(ukraine_map)
        
        time.sleep(1)  # Обмеження запитів до API

    except Exception as e:
        print(f"Помилка для {name}: {str(e)}")
        continue

# Додаємо деталізовану легенду
legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; 
    width: 220px; 
    border: 2px solid #2c3e50;
    border-radius: 5px;
    z-index: 9999; 
    font-size: 13px;
    background-color: white;
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
    padding: 10px;
    font-family: Arial, sans-serif;
    ">
    <h4 style="margin:0 0 10px 0; padding:0; color: #2c3e50; border-bottom:1px solid #eee; padding-bottom:5px;">Рівні небезпеки</h4>
    <p style="margin:5px 0;"><i class="fa fa-circle" style="color:red"></i> <b>Висока:</b> Вітер >70 км/год або гроза</p>
    <p style="margin:5px 0;"><i class="fa fa-circle" style="color:orange"></i> <b>Помірна:</b> Вітер >50 км/год або опади >20 мм</p>
    <p style="margin:5px 0;"><i class="fa fa-circle" style="color:lightorange"></i> <b>Підвищена увага:</b> Вітер >30 км/год або опади >5 мм</p>
    <p style="margin:5px 0;"><i class="fa fa-circle" style="color:green"></i> <b>Безпечно</b></p>
</div>
{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)
ukraine_map.get_root().add_child(legend)

# Додаємо інтерактивні елементи
MeasureControl(position='topright').add_to(ukraine_map)
MarkerCluster().add_to(ukraine_map)
folium.LayerControl().add_to(ukraine_map)

# Збереження карти
output_file = r"C:\Users\EGOR\Desktop\Tornado-boy\ukraine_weather_map.html"
ukraine_map.save(output_file)
print(f"Карта погоди збережена у файлі: {output_file}")