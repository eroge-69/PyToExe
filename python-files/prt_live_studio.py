import sys
import subprocess
import requests
import json
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLineEdit, QListWidget, QListWidgetItem, QStackedWidget,
    QTextEdit, QCheckBox, QComboBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

# --- CONFIG ---
PEXELS_API_KEY = "your_pexels_api_key"
PIXABAY_API_KEY = "your_pixabay_api_key"
GOOGLE_CSE_ID = "84163c040cc404e75"
GOOGLE_API_KEY = "AIzaSyDDEMHgV_QtpkoAg295X_8yWYn4UZHk2As"
RSS_FEED_URL = "https://prtuudised.edgeone.app/"

WEATHER_CITIES = ["Tallinn", "Tartu", "Pärnu", "Narva", "Paris", "London", "Berlin", "New York"]

class PRTLiveStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PRT Live Studio")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setWindowIcon(QIcon("prt_icon.png"))

        # Layout
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        content_area = QVBoxLayout()

        # --- Left panel buttons ---
        self.subtitles_btn = QPushButton("Subtiitrid")
        self.videos_btn = QPushButton("Pildid / Videod")
        self.news_btn = QPushButton("Uudised")
        self.weather_btn = QPushButton("Ilmateade")
        self.microphone_btn = QPushButton("Mikrofon")
        self.text_btn = QPushButton("Tekst")
        for btn in [self.subtitles_btn, self.videos_btn, self.news_btn, self.weather_btn, self.microphone_btn, self.text_btn]:
            btn.setStyleSheet("background-color: #1f1f1f; color: #0facae; font-size: 16px;")
            btn.setFixedHeight(50)
            left_panel.addWidget(btn)

        # --- Content area ---
        self.stack = QStackedWidget()
        content_area.addWidget(self.stack)

        # Add panels
        self.stack.addWidget(self.create_subtitles_panel())
        self.stack.addWidget(self.create_videos_panel())
        self.stack.addWidget(self.create_news_panel())
        self.stack.addWidget(self.create_weather_panel())
        self.stack.addWidget(self.create_microphone_panel())
        self.stack.addWidget(self.create_text_panel())

        # Connect buttons
        self.subtitles_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.videos_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.news_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.weather_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.microphone_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.text_btn.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        # Add to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(content_area, 4)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Top right logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap("prt_logo.png").scaled(200, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.move(self.width() - 250, 10)
        self.logo.setStyleSheet("background-color: transparent;")

        # Start ticker
        self.start_news_ticker()

    def create_subtitles_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Subtiitrite haldamine:"))
        self.subtitle_editor = QTextEdit()
        layout.addWidget(self.subtitle_editor)
        send_btn = QPushButton("Lisa subtiitrid eetrisse")
        send_btn.setStyleSheet("background-color: #0facae;")
        layout.addWidget(send_btn)
        panel.setLayout(layout)
        return panel

    def create_videos_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        self.video_search = QLineEdit()
        self.video_search.setPlaceholderText("Otsi videot või pilti...")
        self.video_results = QListWidget()
        search_btn = QPushButton("Otsi")
        search_btn.setStyleSheet("background-color: #0facae;")
        search_btn.clicked.connect(self.search_media)
        layout.addWidget(self.video_search)
        layout.addWidget(search_btn)
        layout.addWidget(self.video_results)
        panel.setLayout(layout)
        return panel

    def create_news_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        self.news_label = QLabel("Uudised jooksvalt:")
        layout.addWidget(self.news_label)
        panel.setLayout(layout)
        return panel

    def create_weather_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        self.city_combo = QComboBox()
        self.city_combo.addItems(sorted(WEATHER_CITIES))
        self.weather_info = QLabel("Ilm: -")
        get_weather_btn = QPushButton("Näita ilmateadet")
        get_weather_btn.setStyleSheet("background-color: #0facae;")
        get_weather_btn.clicked.connect(self.get_weather)
        layout.addWidget(QLabel("Vali linn:"))
        layout.addWidget(self.city_combo)
        layout.addWidget(get_weather_btn)
        layout.addWidget(self.weather_info)
        panel.setLayout(layout)
        return panel

    def create_microphone_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        self.mic_status = QLabel("Mikrofon: Mitteaktiivne")
        toggle_btn = QPushButton("Lülita sisse/välja")
        toggle_btn.setStyleSheet("background-color: #0facae;")
        toggle_btn.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mic_status)
        layout.addWidget(toggle_btn)
        panel.setLayout(layout)
        return panel

    def create_text_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Teksti ja pildiallikate lisamine:"))
        add_name_btn = QPushButton("Lisa inimene (nimi, amet)")
        add_title_btn = QPushButton("Lisa pealkiri")
        add_source_btn = QPushButton("Lisa pildiallikas")
        for btn in [add_name_btn, add_title_btn, add_source_btn]:
            btn.setStyleSheet("background-color: #0facae;")
            layout.addWidget(btn)
        panel.setLayout(layout)
        return panel

    def toggle_mic(self):
        if "Mitteaktiivne" in self.mic_status.text():
            self.mic_status.setText("Mikrofon: Aktiivne")
        else:
            self.mic_status.setText("Mikrofon: Mitteaktiivne")

    def search_media(self):
        query = self.video_search.text()
        self.video_results.clear()

        # Pexels API näide
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3", headers=headers)
        data = r.json()
        for video in data.get("videos", []):
            item = QListWidgetItem(f"Pexels video: {video['url']}")
            self.video_results.addItem(item)

        # Google Images API
        r2 = requests.get(
            f"https://www.googleapis.com/customsearch/v1?q={query}&cx={GOOGLE_CSE_ID}&key={GOOGLE_API_KEY}&searchType=image"
        )
        img_data = r2.json()
        for img in img_data.get("items", []):
            item = QListWidgetItem(f"Pilt: {img['link']}")
            self.video_results.addItem(item)

    def get_weather(self):
        city = self.city_combo.currentText()
        # Simuleerime ilmateadet
        self.weather_info.setText(f"{city}: {datetime.datetime.now().strftime('%H:%M')} 🌦 17°C")

    def start_news_ticker(self):
        self.ticker_label = QLabel(self)
        self.ticker_label.setGeometry(0, self.height() - 40, self.width(), 30)
        self.ticker_label.setStyleSheet("background-color: #0facae; color: white; font-size: 18px;")
        self.ticker_label.setAlignment(Qt.AlignCenter)

        def update_ticker():
            try:
                r = requests.get(RSS_FEED_URL)
                headlines = r.json().get("headlines", ["PRT Uudised töötavad..."])
                self.ticker_label.setText("   ✦   ".join(headlines))
            except:
                self.ticker_label.setText("PRT Uudised: Viga RSS allalaadimisel")

        self.ticker_timer = QTimer()
        self.ticker_timer.timeout.connect(update_ticker)
        self.ticker_timer.start(10000)  # iga 10 sek uuendab
        update_ticker()

# --- RUN ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PRTLiveStudio()
    window.show()
    sys.exit(app.exec_())
