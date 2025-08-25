import sys
import random
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import Qt

class ParolaOlusturucu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sallama Parola Oluşturucu")
        self.setFixedSize(400, 320)

        # Arayüz düzeni
        layout = QVBoxLayout()

        # Ad etiketi ve girişi
        self.ad_label = QLabel("Ad:")
        layout.addWidget(self.ad_label)
        self.ad_girisi = QLineEdit()
        self.ad_girisi.setPlaceholderText("Adınızı girin (zorunlu değil)")
        layout.addWidget(self.ad_girisi)

        # Soyad etiketi ve girişi
        self.soyad_label = QLabel("Soyad:")
        layout.addWidget(self.soyad_label)
        self.soyad_girisi = QLineEdit()
        self.soyad_girisi.setPlaceholderText("Soyadınızı girin (zorunlu değil)")
        layout.addWidget(self.soyad_girisi)

        # Parola uzunluğu etiketi ve seçimi
        self.uzunluk_label = QLabel("Parola Uzunluğu:")
        layout.addWidget(self.uzunluk_label)
        self.uzunluk_secimi = QComboBox()
        self.uzunluk_secimi.addItems(["8", "12", "16", "20", "24", "28", "32"])
        self.uzunluk_secimi.setCurrentText("12")  # Varsayılan 12 karakter
        layout.addWidget(self.uzunluk_secimi)

        # Oluştur butonu
        self.olustur_butonu = QPushButton("Parola Oluştur")
        self.olustur_butonu.clicked.connect(self.parola_olustur)
        layout.addWidget(self.olustur_butonu)

        # Parola gösterim alanı
        self.parola_label = QLabel("Oluşturulan parola burada görünecek")
        self.parola_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.parola_label)

        # Karıştır butonu
        self.karistir_butonu = QPushButton("Parolayı Karıştır")
        self.karistir_butonu.clicked.connect(self.parolayi_karistir)
        self.karistir_butonu.setEnabled(False)  # Parola oluşmadan devre dışı
        layout.addWidget(self.karistir_butonu)

        # Kaydet butonu
        self.kaydet_butonu = QPushButton("Parolayı Masaüstüne Kaydet")
        self.kaydet_butonu.clicked.connect(self.parolayi_kaydet)
        self.kaydet_butonu.setEnabled(False)  # Parola oluşmadan devre dışı
        layout.addWidget(self.kaydet_butonu)

        # Ana widget ve layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.son_parola = ""  # Oluşturulan parolayı saklamak için
        self.hedef_uzunluk = 12  # Varsayılan uzunluk

        # Stil şablonu (renkli tema)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: black;
            }
            QLabel#Ad {
                color: #FFFF00; /* Sarı */
                font-size: 14px;
            }
            QLabel#Soyad {
                color: #FF0000; /* Kırmızı */
                font-size: 14px;
            }
            QLabel#ParolaUzunlugu {
                color: #00FF00; /* Yeşil */
                font-size: 14px;
            }
            QLabel#ParolaSonuc {
                color: #00FFFF; /* Camgöbeği */
                font-size: 14px;
            }
            QLineEdit {
                background-color: #222222;
                color: #FFA500; /* Turuncu */
                border: 1px solid #FF69B4; /* Pembe kenarlık */
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #FFC1CC; /* Açık pembe */
            }
            QPushButton#OlusturButonu {
                background-color: #FF0000; /* Kırmızı */
                color: white;
                border: 1px solid #FFFFFF;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton#OlusturButonu:hover {
                background-color: #CC0000; /* Koyu kırmızı */
            }
            QPushButton#KaristirButonu {
                background-color: #00FF00; /* Yeşil */
                color: white;
                border: 1px solid #FFFFFF;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton#KaristirButonu:hover {
                background-color: #00CC00; /* Koyu yeşil */
            }
            QPushButton#KaristirButonu:disabled {
                background-color: #222222;
                color: #666666;
            }
            QPushButton#KaydetButonu {
                background-color: #800080; /* Mor */
                color: white;
                border: 1px solid #FFFFFF;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton#KaydetButonu:hover {
                background-color: #660066; /* Koyu mor */
            }
            QPushButton#KaydetButonu:disabled {
                background-color: #222222;
                color: #666666;
            }
            QComboBox {
                background-color: #222222;
                color: #FFA500; /* Turuncu */
                border: 1px solid #FF69B4; /* Pembe kenarlık */
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #00FFFF; /* Camgöbeği */
                selection-background-color: #444444;
                selection-color: white;
            }
        """)

        # Etiketlere obje adları ver (stil için)
        self.ad_label.setObjectName("Ad")
        self.soyad_label.setObjectName("Soyad")
        self.uzunluk_label.setObjectName("ParolaUzunlugu")
        self.parola_label.setObjectName("ParolaSonuc")
        self.olustur_butonu.setObjectName("OlusturButonu")
        self.karistir_butonu.setObjectName("KaristirButonu")
        self.kaydet_butonu.setObjectName("KaydetButonu")

    def parola_olustur(self):
        ad = self.ad_girisi.text().strip()
        soyad = self.soyad_girisi.text().strip()
        self.hedef_uzunluk = int(self.uzunluk_secimi.currentText())  # Seçilen uzunluk

        # Ad ve soyad boşsa varsayılan harfler
        if not ad and not soyad:
            harfler = list("abcdefghijklmnopqrstuvwxyz")
            random.shuffle(harfler)
            harfler = harfler[:min(10, self.hedef_uzunluk)]  # Uzunluğa göre harf al
        else:
            tam_isim = (ad + soyad).replace(" ", "").lower()
            harfler = list(tam_isim)
            # Eğer harf sayısı hedef uzunluktan fazlaysa, rastgele seç
            if len(harfler) > self.hedef_uzunluk:
                harfler = random.sample(harfler, self.hedef_uzunluk // 2)

        # Harfleri karıştır
        random.shuffle(harfler)

        # Parola oluştur
        parola = ""
        for i, harf in enumerate(harfler):
            parola += harf
            # Her 2 harften sonra rastgele sayı ekle, ama uzunluğu aşmamak için kontrol et
            if i % 2 == 1 and len(parola) < self.hedef_uzunluk - 1:
                parola += str(random.randint(0, 9))

        # Hedef uzunluğa ulaşana kadar rastgele sayı veya harf ekle
        while len(parola) < self.hedef_uzunluk:
            if random.choice([True, False]):  # Rastgele harf veya sayı ekle
                parola += random.choice("abcdefghijklmnopqrstuvwxyz")
            else:
                parola += str(random.randint(0, 9))

        # Eğer parola hedef uzunluğu aştıysa, kırp
        parola = parola[:self.hedef_uzunluk]

        # Parolayı göster
        self.parola_label.setText(f"Parola: {parola}")
        self.son_parola = parola
        self.karistir_butonu.setEnabled(True)
        self.kaydet_butonu.setEnabled(True)

    def parolayi_karistir(self):
        if not self.son_parola:
            return

        # Mevcut parolayı al ve karakterlerine ayır
        karakterler = list(self.son_parola)
        random.shuffle(karakterler)  # Karakterleri rastgele karıştır

        # Ekstra sağlamlık için rastgele 1-2 karakter ekle (harf veya sayı)
        for _ in range(random.randint(1, 2)):
            if len(karakterler) < self.hedef_uzunluk:
                if random.choice([True, False]):
                    karakterler.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
                else:
                    karakterler.append(str(random.randint(0, 9)))

        # Yeni parolayı oluştur
        yeni_parola = "".join(karakterler)

        # Hedef uzunluğa uyması için kırp veya tamamla
        while len(yeni_parola) < self.hedef_uzunluk:
            if random.choice([True, False]):
                yeni_parola += random.choice("abcdefghijklmnopqrstuvwxyz")
            else:
                yeni_parola += str(random.randint(0, 9))
        yeni_parola = yeni_parola[:self.hedef_uzunluk]

        # Yeni parolayı göster
        self.parola_label.setText(f"Parola: {yeni_parola}")
        self.son_parola = yeni_parola
        self.karistir_butonu.setEnabled(True)
        self.kaydet_butonu.setEnabled(True)

    def parolayi_kaydet(self):
        if self.son_parola:
            masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop", "sallama_parola.txt")
            with open(masaustu_yolu, "w") as dosya:
                dosya.write(self.son_parola)
            self.parola_label.setText(f"Parola kaydedildi: {masaustu_yolu}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = ParolaOlusturucu()
    pencere.show()
    sys.exit(app.exec())