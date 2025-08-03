import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from datetime import datetime
import time
import os

API_KEY = "0f85fa6c48522fb7deab23923b844d94"

CITIES = {
    "Auto (My Location)": None,
    "New York": ("40.7128", "-74.0060"),
    "Los Angeles": ("34.0522", "-118.2437"),
    "London": ("51.5074", "-0.1278"),
}

def get_day_name(unix_time):
    return time.strftime('%A', time.localtime(unix_time))

def update_forecast_time():
    now = datetime.now()
    current_time_label.config(text="🕒 Forecast (as of " + now.strftime("%I:%M %p") + ")")

def set_background(weather_description):
    desc = weather_description.lower()
    image_map = {
        "clear": "sunny.jpg",
        "clouds": "cloudy.jpg",
        "few clouds": "partly_cloudy.jpg",
        "scattered clouds": "partly_cloudy.jpg",
        "broken clouds": "broken_clouds.jpg",
        "rain": "rain.jpg",
        "drizzle": "drizzle.jpg",
        "thunderstorm": "storm.jpg",
        "snow": "snow.jpg",
        "mist": "fog.jpg",
        "fog": "fog.jpg",
        "haze": "fog.jpg",
        "smoke": "smoke.jpg",
        "dust": "dust.jpg",
        "sand": "dust.jpg",
        "ash": "ash.jpg",
        "squall": "wind.jpg",
        "tornado": "tornado.jpg"
    }

    # Match the most specific condition
    filename = None
    for key in image_map:
        if key in desc:
            filename = image_map[key]
            break

    if not filename:
        filename = "cloudy.jpg"  # fallback

    if os.path.exists(filename):
        bg_image = Image.open(filename).resize((root.winfo_screenwidth(), root.winfo_screenheight()))
        bg_photo = ImageTk.PhotoImage(bg_image)
        background_label.config(image=bg_photo)
        background_label.image = bg_photo


def get_weather_tip(condition, temp, humidity):
    condition = condition.lower()
    tips = []

    if "rain" in condition or "drizzle" in condition:
        tips.append("☔ Rain expected — bring an umbrella and wear waterproof shoes.")
    if "snow" in condition:
        tips.append("❄️ Snowfall likely — dress warmly and watch for icy roads.")
    if "thunderstorm" in condition:
        tips.append("⚡ Thunderstorms today — best to stay indoors if possible.")
    if "fog" in condition:
        tips.append("🌫️ Foggy conditions — use headlights and drive carefully.")
    if "wind" in condition:
        tips.append("🌬️ Windy outside — secure loose objects and avoid cycling.")
    if "clear" in condition:
        tips.append("☀️ Clear skies — great day to be outside!")
    if "cloud" in condition:
        tips.append("☁️ Cloudy skies — might feel cooler than the actual temp.")

    if temp >= 95:
        tips.append("🔥 Extremely hot — avoid being outdoors during peak hours.")
    elif temp >= 85:
        tips.append("🥵 Stay hydrated and wear sunscreen.")
    elif temp >= 70:
        tips.append("🌼 Comfortable weather — enjoy your day!")
    elif temp >= 50:
        tips.append("🧥 A bit chilly — consider a light jacket.")
    elif temp >= 32:
        tips.append("🥶 Cold weather — bundle up, especially in the morning.")
    else:
        tips.append("🧊 Freezing — limit time outdoors and dress in layers.")

    if humidity >= 80 and temp > 75:
        tips.append("💦 High humidity — it might feel hotter than it is.")

    return "\n".join(tips)

def draw_temp_bar(temp):
    bar_canvas.delete("all")
    min_temp = 0
    max_temp = 120
    bar_height = 150
    bar_width = 30
    margin = 10

    fill_height = int((temp - min_temp) / (max_temp - min_temp) * bar_height)
    fill_height = max(0, min(bar_height, fill_height))

    if temp <= 50:
        color = "#3A7BD5"
    elif temp >= 85:
        color = "#D52B1E"
    else:
        color = "#FDB813"

    bar_canvas.create_rectangle(margin, margin, bar_width + margin, bar_height + margin, outline="black")
    bar_canvas.create_rectangle(
        margin, bar_height + margin - fill_height,
        bar_width + margin, bar_height + margin,
        fill=color
    )

def get_weather():
    update_forecast_time()
    try:
        selection = selected_city.get()
        if CITIES.get(selection) is None:
            location_resp = requests.get("https://ipinfo.io")
            location_data = location_resp.json()
            loc = location_data.get("loc")
            city = location_data.get("city")
            if not loc:
                forecast_label.config(text="Could not get location.")
                return
            lat, lon = loc.split(",")
        else:
            lat, lon = CITIES[selection]
            city = selection

        current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
        current = requests.get(current_url).json()

        if "main" not in current or "weather" not in current:
            forecast_label.config(text="Error loading current data.")
            return

        weather_main = current["weather"][0]["main"]
        set_background(weather_main)

        desc = current["weather"][0]["description"].title()
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        temp_min = current["main"]["temp_min"]
        temp_max = current["main"]["temp_max"]
        humidity = current["main"]["humidity"]
        wind_speed = current["wind"]["speed"]
        pressure = current["main"]["pressure"]
        sunrise = datetime.fromtimestamp(current["sys"]["sunrise"]).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(current["sys"]["sunset"]).strftime("%I:%M %p")

        forecast_label.config(text=(
            f"{city}\n{desc}\n\n"
            f"🔼 High: {temp_max}°F   🔽 Low: {temp_min}°F\n"
            f"💧 Humidity: {humidity}%   🌬 Wind: {wind_speed} mph\n"
            f"📈 Pressure: {pressure} hPa\n"
            f"🌅 Sunrise: {sunrise}   🌇 Sunset: {sunset}"
        ))

        temp_label.config(text=f"🌡 Temp: {temp}°F\n🤒 Feels like: {feels_like}°F")
        draw_temp_bar(temp)

        tip = get_weather_tip(weather_main, temp, humidity)
        tip_label.config(text=tip)

        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
        forecast_data = requests.get(forecast_url).json()

        daily = {}
        for item in forecast_data["list"]:
            date_txt = item["dt_txt"]
            if "12:00:00" in date_txt:
                day = date_txt.split(" ")[0]
                if day not in daily and len(daily) < 5:
                    daily[day] = item

        for i, (day, entry) in enumerate(daily.items()):
            date = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
            day_name = date.strftime("%A")
            temp_max = int(entry["main"]["temp_max"])
            temp_min = int(entry["main"]["temp_min"])
            desc = entry["weather"][0]["main"]
            icon_code = entry["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
            icon_img = Image.open(BytesIO(requests.get(icon_url).content)).resize((50, 50))
            photo = ImageTk.PhotoImage(icon_img)

            day_icons[i].config(image=photo)
            day_icons[i].image = photo
            day_labels[i].config(text=f"{day_name}\n{temp_max}° / {temp_min}°\n{desc}")

    except Exception as e:
        forecast_label.config(text=f"Error: {str(e)}")

    root.after(60000, get_weather)

def add_city():
    city_name = add_entry.get().strip()
    if not city_name or city_name in CITIES:
        return
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    resp = requests.get(geo_url).json()
    if not resp:
        forecast_label.config(text="❌ City not found.")
        return
    lat = str(resp[0]["lat"])
    lon = str(resp[0]["lon"])
    CITIES[city_name] = (lat, lon)
    city_menu['menu'].add_command(label=city_name, command=tk._setit(selected_city, city_name, get_weather))
    selected_city.set(city_name)
    get_weather()
    add_entry.delete(0, tk.END)

def remove_city():
    city = selected_city.get()
    if city == "Auto (My Location)":
        return
    if city in CITIES:
        del CITIES[city]
        selected_city.set("Auto (My Location)")
        get_weather()
        city_menu['menu'].delete(0, 'end')
        for name in CITIES:
            city_menu['menu'].add_command(label=name, command=tk._setit(selected_city, name, get_weather))

def toggle_city_panel():
    if city_panel.winfo_ismapped():
        city_panel.pack_forget()
    else:
        city_panel.pack(pady=5)

# GUI Setup
root = tk.Tk()
root.attributes("-fullscreen", True)

selected_city = tk.StringVar()
selected_city.set("Auto (My Location)")

bg_image = Image.new("RGB", (1920, 1080), color="lightblue")
bg_photo = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Toggle Button
toggle_btn = tk.Button(root, text="☰ Cities", font=("Arial", 12), command=toggle_city_panel)
toggle_btn.pack(pady=(5, 0))

# Collapsible City Panel
city_panel = tk.Frame(root, bg="#ffffff")

city_menu = tk.OptionMenu(city_panel, selected_city, *CITIES.keys(), command=lambda _: get_weather())
city_menu.config(font=("Arial", 12))
city_menu.pack(side=tk.LEFT, padx=5)

add_entry = tk.Entry(city_panel, font=("Arial", 12), width=20)
add_entry.pack(side=tk.LEFT, padx=5)

add_btn = tk.Button(city_panel, text="Add City", font=("Arial", 10), command=add_city)
add_btn.pack(side=tk.LEFT, padx=5)

remove_btn = tk.Button(city_panel, text="Remove City", font=("Arial", 10), command=remove_city)
remove_btn.pack(side=tk.LEFT, padx=5)

# Header and Temperature
header = tk.Label(root, text="Weather", font=("Arial", 28), fg="#000000", bg="#ffffff")
header.pack(pady=10)

temp_frame = tk.Frame(root, bg="#ffffff")
temp_frame.pack()
temp_label = tk.Label(temp_frame, text="", font=("Arial", 20), fg="#000000", bg="#ffffff")
temp_label.pack(padx=20, pady=5)
bar_canvas = tk.Canvas(temp_frame, width=50, height=170, bg="#ffffff", highlightthickness=0)
bar_canvas.pack(pady=5)

forecast_label = tk.Label(root, text="", font=("Arial", 16), fg="#000000", justify="left", wraplength=1000, bg="#ffffff")
forecast_label.pack(pady=10)
current_time_label = tk.Label(root, text="", font=("Arial", 14), fg="#000000", bg="#ffffff")
current_time_label.pack(pady=(10, 5))
tip_label = tk.Label(root, text="", font=("Arial", 14), fg="#003366", bg="#ffffff", wraplength=900, justify="center")
tip_label.pack(pady=(10, 10))

forecast_frame = tk.Frame(root)
forecast_frame.pack(pady=20)

day_labels = []
day_icons = []

for _ in range(5):
    canvas = tk.Canvas(forecast_frame, width=120, height=120, highlightthickness=0, bg="white")
    canvas.pack(side=tk.LEFT, padx=10)
    canvas.create_rectangle(0, 0, 120, 120, fill='#FFFFFF', stipple='gray50', outline='')

    icon_label = tk.Label(canvas, bg="#ffffff", bd=0)
    canvas.create_window(60, 30, window=icon_label)

    text_label = tk.Label(canvas, text="", font=("Arial", 12), fg="#000000", bg="#ffffff", bd=0, wraplength=110, justify="center")
    canvas.create_window(60, 90, window=text_label)

    day_icons.append(icon_label)
    day_labels.append(text_label)

get_weather()
root.mainloop()
