import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTextEdit, QLabel, QFileDialog, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import requests
import os
from collections import Counter
import re

# xAI API için placeholder
API_KEY = "senin_api_anahtarin"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

class AssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Öğrenen Meslek Lisesi Asistanı")
        self.setGeometry(100, 100, 800, 600)
        self.history = []  # Geçmiş sorgular
        self.init_ui()
        self.load_history()  # Başlangıçta geçmişi yükle

    def init_ui(self):
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Stil: Şık görünüm
        self.setStyleSheet("""
            QWidget { font-family: Arial; font-size: 14px; }
            QPushButton { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; }
            QPushButton:hover { background-color: #45a049; }
            QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; }
            QLabel { font-weight: bold; }
        """)

        # Ödev giriş alanı
        self.label = QLabel("Ödev Sorunu veya Kod Talebini Gir:")
        layout.addWidget(self.label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Örnek: 'LED devresi için Proteus şeması' veya 'Python'da döngü örneği'")
        layout.addWidget(self.input_text)

        # Butonlar için yatay layout
        button_layout = QHBoxLayout()
        self.process_btn = QPushButton("Özetle ve Çöz")
        self.process_btn.clicked.connect(self.process_homework)
        button_layout.addWidget(self.process_btn)

        self.image_btn = QPushButton("Proteus Şeması Ekle")
        self.image_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.image_btn)

        self.suggest_btn = QPushButton("Öneri Ver")
        self.suggest_btn.clicked.connect(self.make_suggestion)
        button_layout.addWidget(self.suggest_btn)
        layout.addLayout(button_layout)

        # Çıktı alanı
        self.output_label = QLabel("Sonuç:")
        layout.addWidget(self.output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Resim gösterme alanı (Proteus şemaları için)
        self.image_label = QLabel("Şema Görüntüsü:")
        layout.addWidget(self.image_label)
        self.image_display = QLabel()
        self.image_display.setAlignment(Qt.AlignCenter)
        scroll = QScrollArea()
        scroll.setWidget(self.image_display)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

    def load_history(self):
        # Geçmiş sorguları yükle
        if os.path.exists("history.txt"):
            with open("history.txt", "r", encoding="utf-8") as f:
                self.history = [line.strip() for line in f if line.strip()]

    def save_history(self, query):
        # Sorguyu kaydet
        self.history.append(query)
        with open("history.txt", "a", encoding="utf-8") as f:
            f.write(f"{query}\n")

    def analyze_history(self):
        # Geçmiş sorguları analiz et
        if not self.history:
            return "Henüz sorgu yok."
        
        # Basit kelime analizi (örneğin, ders kategorileri)
        keywords = ["python", "proteus", "proton basic", "matematik", "elektronik"]
        counts = Counter()
        for query in self.history:
            query = query.lower()
            for keyword in keywords:
                if keyword in query:
                    counts[keyword] += 1
        
        if not counts:
            return "Geçmişte tanınan bir ders bulunamadı."
        
        most_common = counts.most_common(1)[0]
        return f"En çok sorulan: {most_common[0]} ({most_common[1]} kez). Örnek mi istersin?"

    def make_suggestion(self):
        # Öneri ver (öğrenme mekanizması)
        suggestion = self.analyze_history()
        QMessageBox.information(self, "Öneri", suggestion)
        if "örnek mi istersin?" in suggestion.lower():
            # Örnek öneri (basit)
            most_common = re.findall(r"En çok sorulan: (\w+)", suggestion)[0]
            example = {
                "python": "Örnek Python Kodu:\nfor i in range(5):\n    print(i)",
                "proteus": "Proteus için: 5V, 220 ohm direnç, LED bağla.",
                "proton basic": "Proton Basic Örneği:\nFOR X = 1 TO 10\n    PRINT X\nNEXT X",
                "matematik": "Matematik örneği: x^2 + 2x + 1 = (x+1)^2",
                "elektronik": "Elektronik önerisi: Seri devre için Ohm Kanunu: V=IR"
            }.get(most_common, "Genel öneri: Daha fazla detay ver!")
            self.output_text.setText(example)

    def process_homework(self):
        query = self.input_text.toPlainText().strip()
        if not query:
            self.output_text.setText("Hata: Ödev sorusu girin!")
            return

        # xAI API ile sorgu
        if API_KEY != "senin_api_anahtarin":
            try:
                response = requests.post(
                    GROK_API_URL,
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={
                        "model": "grok-4",
                        "messages": [{"role": "user", "content": f"Bu ödevi özetle ve adım adım açıkla: {query}. Python, Proteus veya Proton Basic ilgiliyse kod örneği ver."}]
                    }
                )
                result = response.json()['choices'][0]['message']['content']
            except Exception as e:
                result = f"API Hatası: {e}. Anahtarı kontrol et."
        else:
            result = f"Örnek çıktı: '{query}' için özet hazırlıyorum...\n"
            if "python" in query.lower():
                result += "Örnek Python Kodu:\nfor i in range(5):\n    print(i)"
            elif "proteus" in query.lower():
                result += "Proteus için: LED devresi önerisi - 5V, 220 ohm direnç, LED bağla."
            elif "proton basic" in query.lower():
                result += "Proton Basic Örneği:\nFOR X = 1 TO 10\n    PRINT X\nNEXT X"
            else:
                result += "Genel özet: Sorunuzu adım adım çözüyorum..."

        self.output_text.setText(result)
        self.save_history(query)

        # Sunum için Markdown
        with open("sunum_ozet.md", "w", encoding="utf-8") as f:
            f.write(f"# Ödev Özeti\n\n{result}\n\nSunum için PowerPoint'e kopyala.")
        
        self.output_text.setText(self.output_text.toPlainText() + "\nSunum özeti 'sunum_ozet.md' dosyasına kaydedildi.")

    def load_image(self):
        # Resim seç (Proteus şeması)
        file_name, _ = QFileDialog.getOpenFileName(self, "Proteus Şeması Seç", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            if pixmap.isNull():
                self.output_text.setText("Hata: Resim yüklenemedi!")
                return
            pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio)
            self.image_display.setPixmap(pixmap)
            self.output_text.setText(self.output_text.toPlainText() + f"\nŞema yüklendi: {os.path.basename(file_name)}")
            self.save_history(f"Resim yüklendi: {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec_())