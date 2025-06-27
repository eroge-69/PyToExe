import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QMessageBox
)
from yt_dlp import YoutubeDL
import threading

class MusicDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Zeneletöltő")
        self.setGeometry(300, 300, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Keresősáv + gomb
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Írd be a YouTube keresési kulcsszavad vagy linket")
        self.download_btn = QPushButton("Letöltés")
        self.download_btn.clicked.connect(self.download_song)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.download_btn)

        # Letöltött zenék listája
        self.download_list = QListWidget()

        layout.addLayout(search_layout)
        layout.addWidget(self.download_list)

        self.setLayout(layout)

    def download_song(self):
        url = self.search_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Hiba", "Adj meg egy YouTube linket vagy keresőkifejezést!")
            return

        self.download_btn.setEnabled(False)
        self.download_btn.setText("Letöltés folyamatban...")

        # Letöltés külön szálon, hogy ne fagyjon a GUI
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

    def run_download(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Nincs cím')
            self.download_list.addItem(f"Letöltve: {title}")
        except Exception as e:
            self.download_list.addItem(f"Hiba: {e}")

        # GUI frissítés az eredmény után
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Letöltés")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MusicDownloader()
    win.show()
    sys.exit(app.exec())
