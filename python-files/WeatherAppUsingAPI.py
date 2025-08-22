from PyQt5.QtWidgets import (QApplication , QWidget , QLabel , QLineEdit , QPushButton , QVBoxLayout)
                             
from PyQt5.QtCore import Qt
import sys
import requests

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather app")
        self.setGeometry(700 , 300 , 50 , 50)
        
        self.city_label = QLabel("Enter the name of a city" , self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get weather" , self)
        self.temperataure_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.init_UI()

    def init_UI(self):
        
        
        
        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperataure_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperataure_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperataure_label.setObjectName("temperataure_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel , QPushButton{
                
                font-family : consolas;
                                    
            }
            
            QLabel#city_label{
                           
                font-size : 40px;
                font-style : italic;
                font-weight : bold;
            }
                           
            QLineEdit#city_input{
                           
                font-family : consolas;
                font-size : 40px;
                font-style : bold;
            }
                           
            QPushButton#get_weather_button{
                           
                font-size : 30px;
                font-style : italic;
            }
                           
            QLabel#temperataure_label{
                           
                font-size : 35px;
                font-style : italic;
                font-weight : bold;            
            }
                           
            QLabel#emoji_label{
                           
                font-size : 150px;
                font-family : Segoe UI emoji;
            }
                           
            QLabel#description_label{
                           
                font-size : 30px;
                font-style : italic;               
            }
            
        """)

        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        
        api_key = "3291ce72ba37521455e6d006181af467"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_errors("Bad request\nCheck your input\nHTTP status code 400")

                case 401:
                    self.display_errors("Unauthorised\nInvalid API key\nHTTP status code 401")

                case 403:
                    self.display_errors("Forbidden\nAccsess is denied\nHTTP status code 403")

                case 404:
                    self.display_errors("Not found\nCity not found\nHTTP status code 404")

                case 500:
                    self.display_errors("Internal server error\nTry again later\nHTTP status code 500")

                case 502:
                    self.display_errors("Bad gateway\nInvalid response from the server\nHTTP status code 502")

                case 503:
                    self.display_errors("Service unavailable\nServer is down\nHTTP status code 503")

                case 504:
                    self.display_errors("Gateway timeout\nNo response from the server\nHTTP status code 504")

                case _:
                    self.display_errors(f"An unexpected HTTP error occured {http_error}")

        except requests.exceptions.RequestException:
            pass
            
    def display_errors(self , message):
        self.temperataure_label.setText(message)

    def display_weather(self , data):
        self.temperataure_label.setStyleSheet("font-size : 35px;")
        temperature_kelvin = data["main"]["temp"]
        temperature_celcius = temperature_kelvin - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        
        self.temperataure_label.setText(f"{temperature_celcius:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)

    @staticmethod

    def get_weather_emoji(weather_id):
        
        if 200 <= weather_id <= 232:
            return "⛈️"
        
        elif 300 <= weather_id <= 321:
            return "🌦️"
        
        elif 500 <= weather_id <= 531:
            return "🌧️"
        
        elif 600 <= weather_id <= 622:
            return "❄️"
        
        elif 701 <= weather_id <= 741:
            return "🌫️"
        
        elif weather_id == 762:
            return "🌋"
        
        elif weather_id == 771:
            return "💨"
        
        elif weather_id == 781:
            return "🌪️"
        
        elif weather_id == 800:
            return "🌞"
        
        elif 801 <= weather_id <= 804:
            return "☁️"
        
        else:
            return ""
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())