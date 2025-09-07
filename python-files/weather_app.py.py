import webview
import requests
import datetime
import random
import time
from threading import Timer

class WeatherApp:
    def __init__(self):
        self.API_KEY = '482adb12c18eaf2ee9c6a2dac8e6c7b3'
        self.BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
        self.FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'
        
        self.request_count = 0
        self.last_request_time = 0
        self.is_rate_limited = False
        self.failed_attempts = 0
        self.captcha_verified = False
        self.suspicious_activity_detected = False
        
        self.ukrainian_cities = [
            'киев', 'kyiv', 'одесса', 'odessa', 'харьков', 'kharkiv', 'львов', 'lviv', 
            'днепр', 'dnipro', 'донецк', 'donetsk', 'запорожье', 'zaporizhzhia'
        ]
        
        self.current_unit = 'metric'
        self.current_weather_data = None
        
    def get_html(self):
        return '''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Прогноз Погоды от Vitastanka</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Segoe UI", sans-serif; }
                body { background: linear-gradient(135deg, #1a2980, #26d0ce); color: #333; min-height: 100vh; padding: 20px; display: flex; justify-content: center; align-items: center; }
                .container { width: 100%; max-width: 450px; background: rgba(255, 255, 255, 0.9); border-radius: 20px; padding: 25px; box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3); position: relative; }
                .security-badge { position: absolute; top: 10px; right: 10px; background: #4CAF50; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; display: flex; align-items: center; gap: 5px; }
                .search-box { display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; }
                .search-box input { flex: 1; height: 50px; border: none; outline: none; background: #ebfffc; border-radius: 25px; padding: 0 20px; font-size: 16px; margin-right: 15px; }
                .search-box button { width: 50px; height: 50px; border: none; outline: none; background: #ebfffc; border-radius: 50%; cursor: pointer; transition: all 0.3s ease; }
                .search-box button:hover { background: #c8faf4; transform: scale(1.05); }
                .weather-info { text-align: center; }
                .city-name { font-size: 28px; font-weight: 600; margin-bottom: 10px; color: #1a2980; }
                .date { font-size: 16px; color: #555; margin-bottom: 25px; }
                .temperature { font-size: 70px; font-weight: 700; margin: 20px 0; color: #1a2980; }
                .weather-icon { font-size: 80px; margin: 20px 0; color: #FFA726; }
                .weather-type { font-size: 24px; margin-bottom: 25px; color: #555; }
                .details { display: flex; justify-content: space-between; margin-top: 30px; padding: 0 20px; }
                .col { display: flex; align-items: center; text-align: left; }
                .col i { font-size: 28px; color: #1a2980; margin-right: 15px; }
                .humidity, .wind, .pressure { font-size: 18px; margin-bottom: 5px; }
                .error, .loading { text-align: center; margin-top: 20px; font-size: 16px; display: none; }
                .error { color: #ff6b6b; }
                .loading { color: #1a2980; }
                .forecast { margin-top: 30px; display: flex; justify-content: space-between; overflow-x: auto; padding: 10px 0; }
                .forecast-day { min-width: 80px; text-align: center; padding: 10px; background: rgba(255, 255, 255, 0.5); border-radius: 15px; margin: 0 5px; }
                .forecast-date { font-weight: 600; margin-bottom: 5px; font-size: 14px; }
                .forecast-temp { font-size: 18px; font-weight: 600; }
                .unit-toggle { text-align: right; margin-bottom: 10px; }
                .unit-btn { background: #ebfffc; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 14px; margin-left: 5px; }
                .unit-btn.active { background: #1a2980; color: white; }
                footer { text-align: center; margin-top: 30px; color: rgba(255, 255, 255, 0.7); font-size: 14px; }
                .country-error { text-align: center; margin-top: 20px; padding: 15px; background: #fff0f0; border-radius: 10px; border-left: 4px solid #ff6b6b; display: none; }
                .country-error i { color: #ff6b6b; font-size: 24px; margin-bottom: 10px; }
                .captcha-container { display: none; margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 10px; text-align: center; }
                .captcha-text { font-size: 24px; font-weight: bold; letter-spacing: 5px; background: #e0e0e0; padding: 10px; border-radius: 5px; margin: 10px 0; user-select: none; }
                .captcha-input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; text-align: center; font-size: 16px; }
                .rate-limit { text-align: center; margin-top: 20px; padding: 15px; background: #fff8e1; border-radius: 10px; border-left: 4px solid #ffc107; display: none; }
                .rate-limit i { color: #ff9800; font-size: 24px; margin-bottom: 10px; }
                .security-log { position: fixed; bottom: 10px; right: 10px; background: rgba(0, 0, 0, 0.7); color: white; padding: 10px; border-radius: 5px; font-size: 12px; max-width: 300px; display: none; z-index: 1000; }
                @media (max-width: 500px) {
                    .container { padding: 15px; }
                    .temperature { font-size: 60px; }
                    .details { flex-direction: column; gap: 15px; }
                    .forecast { flex-direction: column; gap: 10px; }
                    .forecast-day { min-width: auto; display: flex; justify-content: space-between; align-items: center; padding: 15px; }
                    .security-log { bottom: 5px; right: 5px; left: 5px; max-width: none; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="security-badge"><i class="fas fa-shield-alt"></i> Защищено</div>
                <div class="unit-toggle">
                    <button class="unit-btn active" id="celsius-btn">°C</button>
                    <button class="unit-btn" id="fahrenheit-btn">°F</button>
                </div>
                <div class="search-box">
                    <input type="text" placeholder="Введите город" id="city-input">
                    <button id="search-btn"><i class="fas fa-search"></i></button>
                </div>
                <div class="captcha-container" id="captcha-container">
                    <p>Подтвердите, что вы не робот:</p>
                    <div class="captcha-text" id="captcha-text">ABCD</div>
                    <input type="text" class="captcha-input" id="captcha-input" placeholder="Введите текст">
                    <button class="unit-btn" id="captcha-submit">Подтвердить</button>
                </div>
                <div class="loading" id="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка...</div>
                <div class="error" id="error-message">Город не найден. Попробуйте еще раз.</div>
                <div class="rate-limit" id="rate-limit">
                    <i class="fas fa-hourglass-half"></i>
                    <h3>Слишком много запросов</h3>
                    <p>Пожалуйста, подождите <span id="countdown">30</span> секунд</p>
                </div>
                <div class="country-error" id="country-error">
                    <i class="fas fa-ban"></i>
                    <h3>Данный город не поддерживается</h3>
                    <p>Error Code: 471</p>
                </div>
                <div class="weather-info" id="weather-info">
                    <h2 class="city-name" id="city-name">Хабаровск</h2>
                    <p class="date" id="date">Загрузка...</p>
                    <div class="weather-icon"><i class="fas fa-sun" id="weather-icon"></i></div>
                    <h1 class="temperature" id="temperature">25°C</h1>
                    <h3 class="weather-type" id="weather-type">Солнечно</h3>
                    <div class="details">
                        <div class="col"><i class="fas fa-tint"></i><div><p class="humidity" id="humidity">50%</p><p>Влажность</p></div></div>
                        <div class="col"><i class="fas fa-wind"></i><div><p class="wind" id="wind">5 м/с</p><p>Ветер</p></div></div>
                        <div class="col"><i class="fas fa-compress-alt"></i><div><p class="pressure" id="pressure">1013 гПа</p><p>Давление</p></div></div>
                    </div>
                    <div class="forecast" id="forecast"></div>
                </div>
            </div>
            <footer><p>© 2025 Прогноз Погоды от Vitastanka. Данные предоставлены OpenWeatherMap</p></footer>

            <script>
                const api = {
                    getWeather: (city) => pywebview.api.get_weather(city),
                    toggleUnit: (unit) => pywebview.api.toggle_unit(unit),
                    generateCaptcha: () => pywebview.api.generate_captcha(),
                    verifyCaptcha: (input) => pywebview.api.verify_captcha(input),
                    updateDate: () => pywebview.api.update_date()
                };

                const cityInput = document.getElementById('city-input');
                const searchBtn = document.getElementById('search-btn');
                const cityName = document.getElementById('city-name');
                const dateElement = document.getElementById('date');
                const weatherIcon = document.getElementById('weather-icon');
                const temperature = document.getElementById('temperature');
                const weatherType = document.getElementById('weather-type');
                const humidity = document.getElementById('humidity');
                const wind = document.getElementById('wind');
                const pressure = document.getElementById('pressure');
                const errorMessage = document.getElementById('error-message');
                const countryErrorMessage = document.getElementById('country-error');
                const loadingIndicator = document.getElementById('loading');
                const forecastContainer = document.getElementById('forecast');
                const weatherInfo = document.getElementById('weather-info');
                const celsiusBtn = document.getElementById('celsius-btn');
                const fahrenheitBtn = document.getElementById('fahrenheit-btn');
                const captchaContainer = document.getElementById('captcha-container');
                const captchaText = document.getElementById('captcha-text');
                const captchaInput = document.getElementById('captcha-input');
                const captchaSubmit = document.getElementById('captcha-submit');
                const rateLimit = document.getElementById('rate-limit');

                searchBtn.addEventListener('click', () => {
                    const city = cityInput.value.trim();
                    if (city) api.getWeather(city);
                });

                cityInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const city = cityInput.value.trim();
                        if (city) api.getWeather(city);
                    }
                });

                captchaSubmit.addEventListener('click', () => {
                    const userInput = captchaInput.value.trim();
                    api.verifyCaptcha(userInput);
                });

                captchaInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const userInput = captchaInput.value.trim();
                        api.verifyCaptcha(userInput);
                    }
                });

                celsiusBtn.addEventListener('click', () => api.toggleUnit('metric'));
                fahrenheitBtn.addEventListener('click', () => api.toggleUnit('imperial'));

                // Инициализация
                api.updateDate().then(date => {
                    document.getElementById('date').textContent = date;
                });
                api.getWeather('Хабаровск');
            </script>
        </body>
        </html>
        '''
    
    def get_weather(self, city):
        if not self.is_request_allowed():
            if self.suspicious_activity_detected:
                self.enable_rate_limit()
                self.suspicious_activity_detected = False
            return
        
        if self.is_ukrainian_city(city):
            self.show_country_error()
            return
        
        try:
            self.update_ui({'type': 'loading', 'show': True})
            
            response = requests.get(f"{self.BASE_URL}?q={city}&units={self.current_unit}&appid={self.API_KEY}&lang=ru")
            
            if response.status_code != 200:
                self.failed_attempts += 1
                raise Exception("Город не найден")
            
            data = response.json()
            
            if data.get('sys', {}).get('country') == 'UA':
                self.failed_attempts += 1
                raise Exception("UkraineNotSupported")
            
            self.failed_attempts = 0
            self.captcha_verified = False
            self.current_weather_data = data
            
            self.update_weather_ui(data)
            
            lat = data['coord']['lat']
            lon = data['coord']['lon']
            self.get_forecast(lat, lon)
            
        except Exception as e:
            if str(e) == "UkraineNotSupported":
                self.show_country_error()
            else:
                self.update_ui({'type': 'error', 'message': str(e)})
        finally:
            self.update_ui({'type': 'loading', 'show': False})
    
    def get_forecast(self, lat, lon):
        try:
            response = requests.get(f"{self.FORECAST_URL}?lat={lat}&lon={lon}&units={self.current_unit}&appid={self.API_KEY}&lang=ru")
            if response.status_code == 200:
                data = response.json()
                self.display_forecast(data)
        except:
            pass
    
    def update_weather_ui(self, data):
        weather_data = {
            'type': 'weather',
            'city': data['name'],
            'temp': f"{round(data['main']['temp'])}°{'C' if self.current_unit == 'metric' else 'F'}",
            'humidity': f"{data['main']['humidity']}%",
            'wind': f"{round(data['wind']['speed'])} м/с",
            'pressure': f"{data['main']['pressure']} гПа",
            'weather_type': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon']
        }
        self.update_ui(weather_data)
    
    def display_forecast(self, data):
        daily_forecasts = data['list'][:5]
        forecast_data = []
        
        for forecast in daily_forecasts:
            date = datetime.datetime.fromtimestamp(forecast['dt'])
            forecast_data.append({
                'date': date.strftime('%a'),
                'temp': f"{round(forecast['main']['temp'])}°{'C' if self.current_unit == 'metric' else 'F'}",
                'icon': forecast['weather'][0]['icon']
            })
        
        self.update_ui({'type': 'forecast', 'data': forecast_data})
    
    def toggle_unit(self, unit):
        self.current_unit = unit
        if self.current_weather_data:
            city = self.current_weather_data['name']
            self.get_weather(city)
        return 'ok'
    
    def generate_captcha(self):
        characters = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        captcha = ''.join(random.choice(characters) for _ in range(5))
        self.update_ui({'type': 'captcha', 'show': True, 'text': captcha})
        return captcha
    
    def verify_captcha(self, user_input):
        self.captcha_verified = True
        self.update_ui({'type': 'captcha', 'show': False})
        
        city = window.evaluate_js("document.getElementById('city-input').value")
        if city:
            self.get_weather(city)
        return True
    
    def is_ukrainian_city(self, city):
        return city.lower() in self.ukrainian_cities
    
    def is_request_allowed(self):
        now = time.time()
        time_diff = now - self.last_request_time
        
        if time_diff < 1.0:
            self.request_count += 1
            if self.request_count > 3:
                self.suspicious_activity_detected = True
                return False
        else:
            self.request_count = 1
        
        self.last_request_time = now
        
        if self.is_rate_limited:
            return False
        
        if self.failed_attempts > 5 and not self.captcha_verified:
            self.generate_captcha()
            return False
        
        return True
    
    def enable_rate_limit(self):
        self.is_rate_limited = True
        self.update_ui({'type': 'rate_limit', 'show': True})
        
        def disable_rate_limit():
            self.is_rate_limited = False
            self.failed_attempts = 0
            self.update_ui({'type': 'rate_limit', 'show': False})
        
        Timer(30.0, disable_rate_limit).start()
    
    def update_date(self):
        now = datetime.datetime.now()
        return now.strftime('%A, %d %B %Y')
    
    def show_country_error(self):
        self.update_ui({'type': 'country_error', 'show': True})
    
    def update_ui(self, data):
        js_code = ""
        
        if data['type'] == 'weather':
            js_code = f"""
                document.getElementById('city-name').textContent = '{data['city']}';
                document.getElementById('temperature').textContent = '{data['temp']}';
                document.getElementById('humidity').textContent = '{data['humidity']}';
                document.getElementById('wind').textContent = '{data['wind']}';
                document.getElementById('pressure').textContent = '{data['pressure']}';
                document.getElementById('weather-type').textContent = '{data['weather_type']}';
                document.getElementById('weather-icon').innerHTML = '<img src="https://openweathermap.org/img/wn/{data['icon']}@2x.png" width="80" height="80">';
                document.getElementById('weather-info').style.opacity = '1';
                document.getElementById('error-message').style.display = 'none';
                document.getElementById('country-error').style.display = 'none';
            """
        elif data['type'] == 'forecast':
            forecast_html = ''.join([f"""
                <div class="forecast-day">
                    <div class="forecast-date">{day['date']}</div>
                    <div class="forecast-icon"><img src="https://openweathermap.org/img/wn/{day['icon']}.png"></div>
                    <div class="forecast-temp">{day['temp']}</div>
                </div>
            """ for day in data['data']])
            js_code = f"document.getElementById('forecast').innerHTML = `{forecast_html}`;"
        elif data['type'] == 'loading':
            js_code = f"document.getElementById('loading').style.display = '{'block' if data['show'] else 'none'}';"
        elif data['type'] == 'error':
            js_code = f"""
                document.getElementById('error-message').style.display = 'block';
                document.getElementById('error-message').textContent = '{data['message']}';
            """
        elif data['type'] == 'country_error':
            js_code = f"document.getElementById('country-error').style.display = '{'block' if data['show'] else 'none'}';"
        elif data['type'] == 'captcha':
            if 'text' in data:
                js_code = f"""
                    document.getElementById('captcha-container').style.display = 'block';
                    document.getElementById('captcha-text').textContent = '{data['text']}';
                """
            else:
                js_code = f"document.getElementById('captcha-container').style.display = '{'block' if data['show'] else 'none'}';"
        elif data['type'] == 'rate_limit':
            js_code = f"document.getElementById('rate-limit').style.display = '{'block' if data['show'] else 'none'}';"
        
        try:
            window.evaluate_js(js_code)
        except:
            pass

# Глобальная переменная для окна
window = None

if __name__ == '__main__':
    app = WeatherApp()
    window = webview.create_window(
        'Прогноз Погоды от Vitastanka',
        html=app.get_html(),
        js_api=app,
        width=500,
        height=800,
        resizable=True
    )
    webview.start()