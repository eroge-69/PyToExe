import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTextEdit
from PyQt5.QtCore import Qt
from playwright.sync_api import sync_playwright
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import time
import random
import os
import threading

class TikTokAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TikTok Trends Analyzer")
        self.setGeometry(100, 100, 600, 400)

        # Основной виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Поле для ввода ключевого слова
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Введите ключевое слово (например, 'dance')")
        layout.addWidget(QLabel("Ключевое слово для поиска:"))
        layout.addWidget(self.keyword_input)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.trend_btn = QPushButton("Анализировать тренды")
        self.trend_btn.clicked.connect(self.analyze_trends)
        btn_layout.addWidget(self.trend_btn)

        self.keyword_btn = QPushButton("Анализировать по ключевому слову")
        self.keyword_btn.clicked.connect(self.analyze_keyword)
        btn_layout.addWidget(self.keyword_btn)

        layout.addLayout(btn_layout)

        # Текстовое поле для вывода результатов
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.result_text)

        # Статус
        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)

    def log(self, message):
        self.result_text.append(message)
        QApplication.processEvents()

    def analyze_trends(self):
        self.status_label.setText("Анализ трендов...")
        self.trend_btn.setEnabled(False)
        threading.Thread(target=self.run_trend_analysis, daemon=True).start()

    def analyze_keyword(self):
        keyword = self.keyword_input.text().strip()
        if not keyword:
            self.log("Ошибка: введите ключевое слово")
            return
        self.status_label.setText(f"Анализ по ключевому слову '{keyword}'...")
        self.keyword_btn.setEnabled(False)
        threading.Thread(target=lambda: self.run_keyword_analysis(keyword), daemon=True).start()

    def get_trending_videos(self, page, count=30):
        try:
            page.goto("https://www.tiktok.com/trending", timeout=60000)
            time.sleep(2)

            videos = []
            for _ in range(count // 10):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(random.uniform(1, 3))

            video_elements = page.query_selector_all('div[data-e2e="recommend-list-item-container"]')
            for i, video in enumerate(video_elements[:count]):
                try:
                    description = video.query_selector('h3') or video.query_selector('h4')
                    description = description.inner_text() if description else ""
                    hashtags = [tag.inner_text().replace("#", "") for tag in video.query_selector_all('a[href*="/tag/"]')]
                    sound = video.query_selector('a[href*="/music/"]')
                    sound = sound.inner_text() if sound else "No sound"
                    stats = video.query_selector_all('strong[data-e2e="video-views"], strong[data-e2e="video-likes"]')
                    views = int(stats[0].inner_text().replace("K", "000").replace("M", "000000").replace(".", "")) if stats else 0
                    likes = int(stats[1].inner_text().replace("K", "000").replace("M", "000000").replace(".", "")) if len(stats) > 1 else 0

                    videos.append({
                        "video_id": f"video_{i}",
                        "description": description,
                        "hashtags": hashtags,
                        "sound": sound,
                        "views": views,
                        "likes": likes,
                        "comments": 0,
                        "shares": 0,
                        "created_at": int(time.time())
                    })
                except Exception as e:
                    self.log(f"Ошибка при парсинге видео {i}: {e}")
                time.sleep(random.uniform(0.5, 2))
            
            return videos
        except Exception as e:
            self.log(f"Ошибка при получении трендовых видео: {e}")
            return []

    def get_videos_by_keyword(self, page, keyword, count=20):
        try:
            page.goto(f"https://www.tiktok.com/search?q={keyword}", timeout=60000)
            time.sleep(2)

            videos = []
            for _ in range(count // 10):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(random.uniform(1, 3))

            video_elements = page.query_selector_all('div[data-e2e="search_video-item"]')
            for i, video in enumerate(video_elements[:count]):
                try:
                    description = video.query_selector('h3') or video.query_selector('h4')
                    description = description.inner_text() if description else ""
                    hashtags = [tag.inner_text().replace("#", "") for tag in video.query_selector_all('a[href*="/tag/"]')]
                    sound = video.query_selector('a[href*="/music/"]')
                    sound = sound.inner_text() if sound else "No sound"
                    stats = video.query_selector_all('strong[data-e2e="video-views"], strong[data-e2e="video-likes"]')
                    views = int(stats[0].inner_text().replace("K", "000").replace("M", "000000").replace(".", "")) if stats else 0
                    likes = int(stats[1].inner_text().replace("K", "000").replace("M", "000000").replace(".", "")) if len(stats) > 1 else 0

                    videos.append({
                        "video_id": f"video_{i}",
                        "description": description,
                        "hashtags": hashtags,
                        "sound": sound,
                        "views": views,
                        "likes": likes,
                        "comments": 0,
                        "shares": 0,
                        "created_at": int(time.time())
                    })
                except Exception as e:
                    self.log(f"Ошибка при парсинге видео {i}: {e}")
                time.sleep(random.uniform(0.5, 2))
            
            return videos
        except Exception as e:
            self.log(f"Ошибка при поиске видео по ключевому слову {keyword}: {e}")
            return []

    def get_top_sounds(self, video_data, top_n=5):
        sounds = [video["sound"] for video in video_data]
        return Counter(sounds).most_common(top_n)

    def get_top_hashtags(self, video_data, top_n=5):
        hashtags = [tag for video in video_data for tag in video["hashtags"]]
        return Counter(hashtags).most_common(top_n)

    def get_themes(self, video_data, theme_keywords=None):
        if theme_keywords is None:
            theme_keywords = {
                "dance": ["dance", "dancing", "dancechallenge"],
                "comedy": ["funny", "comedy", "meme", "joke"],
                "lifestyle": ["lifestyle", "dailyvlog", "routine", "aesthetic"],
                "fitness": ["fitness", "workout", "gym", "health"],
                "beauty": ["makeup", "skincare", "beauty", "fashion"]
            }
        
        theme_counts = {theme: 0 for theme in theme_keywords}
        for video in video_data:
            for theme, keywords in theme_keywords.items():
                if any(keyword.lower() in [tag.lower() for tag in video["hashtags"]] or 
                       keyword.lower() in video["description"].lower() for keyword in keywords):
                    theme_counts[theme] += 1
        return theme_counts

    def plot_data(self, data, title, x_label, y_label, filename):
        labels, values = zip(*data)
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color="#1f77b4")
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

    def run_trend_analysis(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            videos = self.get_trending_videos(page)
            browser.close()

            if not videos:
                self.log("Не удалось получить трендовые видео.")
                self.status_label.setText("Готов к работе")
                self.trend_btn.setEnabled(True)
                return

            df = pd.DataFrame(videos)
            df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
            df.to_csv("trending_videos.csv", index=False)
            self.log("Трендовые видео сохранены в trending_videos.csv")

            top_sounds = self.get_top_sounds(videos)
            self.log("\nТоп-5 звуков за неделю:")
            for sound, count in top_sounds:
                self.log(f"{sound}: {count} видео")
            self.plot_data(top_sounds, "Топ звуков на TikTok за неделю", "Звук", "Количество видео", "top_sounds.png")
            self.log("График топ звуков сохранен в top_sounds.png")

            top_hashtags = self.get_top_hashtags(videos)
            self.log("\nТоп-5 хэштегов за неделю:")
            for hashtag, count in top_hashtags:
                self.log(f"#{hashtag}: {count} упоминаний")
            self.plot_data(top_hashtags, "Топ хэштегов на TikTok за неделю", "Хэштег", "Количество упоминаний", "top_hashtags.png")
            self.log("График топ хэштегов сохранен в top_hashtags.png")

            theme_counts = self.get_themes(videos)
            self.log("\nСтатистика по тематикам:")
            for theme, count in theme_counts.items():
                self.log(f"{theme}: {count} видео")
            self.plot_data(theme_counts.items(), "Популярные тематики на TikTok", "Тематика", "Количество видео", "themes.png")
            self.log("График тематик сохранен в themes.png")

            self.status_label.setText("Готов к работе")
            self.trend_btn.setEnabled(True)

    def run_keyword_analysis(self, keyword):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            videos = self.get_videos_by_keyword(page, keyword)
            browser.close()

            if not videos:
                self.log(f"Не удалось получить видео по ключевому слову '{keyword}'.")
                self.status_label.setText("Готов к работе")
                self.keyword_btn.setEnabled(True)
                return

            df = pd.DataFrame(videos)
            df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
            df.to_csv(f"{keyword}_videos.csv", index=False)
            self.log(f"Видео по ключевому слову сохранены в {keyword}_videos.csv")

            top_sounds = self.get_top_sounds(videos)
            self.log(f"\nТоп-5 звуков для '{keyword}':")
            for sound, count in top_sounds:
                self.log(f"{sound}: {count} видео")

            self.status_label.setText("Готов к работе")
            self.keyword_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TikTokAnalyzer()
    window.show()
    sys.exit(app.exec_())