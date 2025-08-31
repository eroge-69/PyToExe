import sys
import os
from PyQt5.QtWidgets import QWidget, QApplication, QTextEdit, QLabel, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout, QMainWindow, QAction, qApp, QInputDialog, QMessageBox
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

# Notepad sınıfı, uygulamanın ana penceresini oluşturuyor ve bir QWidget'ten türetiliyor
class Notepad(QWidget):
    def __init__(self):
        # Üst sınıfın (QWidget) yapıcı metodunu çağırıyoruz
        super().__init__()
        # Arayüzü oluşturmak için init_ui metodunu çağırıyoruz
        self.init_ui()

    def init_ui(self):
        # QTextEdit widget'ı, metin düzenleme alanı olarak kullanılacak
        self.yazi_alani = QTextEdit()

        self.temizle = QPushButton("Temizle")
        self.ac = QPushButton("Aç")
        self.kaydet = QPushButton("Kaydet")

        h_box = QHBoxLayout()
        h_box.addWidget(self.temizle)
        h_box.addWidget(self.ac)
        h_box.addWidget(self.kaydet)

        # Dikey bir düzen (QVBoxLayout) oluşturuyoruz, metin alanı ve butonları üst üste yerleştirmek için
        v_box = QVBoxLayout()
        v_box.addWidget(self.yazi_alani)
        v_box.addLayout(h_box)

        self.setLayout(v_box)

        self.setWindowTitle("NotePad")

        # Butonlara tıklama olaylarını bağlıyoruz
        self.temizle.clicked.connect(self.yaziyi_temizle)
        self.ac.clicked.connect(self.dosya_ac)
        self.kaydet.clicked.connect(self.dosya_kaydet)

    # Metin alanını temizleyen fonksiyon
    def yaziyi_temizle(self):
        self.yazi_alani.clear()

    # Dosya açma
    def dosya_ac(self):
        # QFileDialog ile kullanıcının bir dosya seçmesini sağlıyoruz
        # İlk parametre: dialog başlığı, ikinci parametre: başlangıç dizini (kullanıcının ev dizini)
        # Yeni: os.getenv("HOME") None dönerse, geçerli dizini kullan
        baslangic_dizini = os.getenv("HOME") or os.getcwd()
        try:
            dosya_ismi = QFileDialog.getOpenFileName(self, "Dosya Aç", baslangic_dizini)
            # Yeni: Dosya seçilip seçilmediğini kontrol et
            if dosya_ismi[0]:
                with open(dosya_ismi[0], "r") as file:
                    self.yazi_alani.setText(file.read())
                print(f"Dosya açıldı: {dosya_ismi[0]}")  # Hata ayıklama için konsol çıktısı
            else:
                print("Dosya seçilmedi.")  # Hata ayıklama
        except Exception as e:
            print(f"Dosya açma hatası: {e}")  # Hata ayıklama
            QMessageBox.critical(self, "Hata", f"Dosya açma hatası: {e}")

    # Dosya kaydetme
    def dosya_kaydet(self):
        # QFileDialog ile kullanıcının dosya kaydetme konumu ve adını seçmesini sağlıyoruz
        baslangic_dizini = os.getenv("HOME") or os.getcwd()
        try:
            dosya_ismi = QFileDialog.getSaveFileName(self, "Dosya Kaydet", baslangic_dizini)
            if dosya_ismi[0]:
                with open(dosya_ismi[0], "w") as file:
                    file.write(self.yazi_alani.toPlainText())
                print(f"Dosya kaydedildi: {dosya_ismi[0]}")  # Hata ayıklama
            else:
                print("Dosya kaydetme iptal edildi.")  # Hata ayıklama
        except Exception as e:
            print(f"Dosya kaydetme hatası: {e}")  # Hata ayıklama
            QMessageBox.critical(self, "Hata", f"Dosya kaydetme hatası: {e}")

    # Metin arama fonksiyonu
    def metin_ara(self):
        try:
            # QInputDialog ile kullanıcıdan aranacak metni alıyoruz
            aranacak_metin, ok = QInputDialog.getText(self, "Metin Ara", "Aranacak metni girin:")
            if not ok or not aranacak_metin:
                print("Arama iptal edildi veya boş metin.")  # Hata ayıklama
                return

            print(f"Aranıyor: {aranacak_metin}")  # Hata ayıklama
            # İmleci metnin başına getiriyoruz
            self.yazi_alani.moveCursor(QTextCursor.Start)
            # Arka plan rengini ayarlayarak bulunan metni vurguluyoruz
            format = QTextCharFormat()
            format.setBackground(QColor("yellow"))

            bulundu = False
            while self.yazi_alani.find(aranacak_metin):
                self.yazi_alani.textCursor().mergeCharFormat(format)
                bulundu = True

            if not bulundu:
                QMessageBox.information(self, "Arama", "Metin bulunamadı!")
                print("Metin bulunamadı.")  # Hata ayıklama
            else:
                print("Metin bulundu ve vurgulandı.")  # Hata ayıklama
        except Exception as e:
            print(f"Arama hatası: {e}")  # Hata ayıklama
            QMessageBox.critical(self, "Hata", f"Arama hatası: {e}")

    # Metin değiştirme fonksiyonu
    def metin_degistir(self):
        try:
            # QInputDialog ile kullanıcıdan aranacak ve değiştirilecek metni alıyoruz
            aranacak_metin, ok1 = QInputDialog.getText(self, "Metin Değiştir", "Aranacak metni girin:")
            if not ok1 or not aranacak_metin:
                print("Değiştirme iptal edildi veya aranacak metin boş.")  # Hata ayıklama
                return

            degistirilecek_metin, ok2 = QInputDialog.getText(self, "Metin Değiştir", "Değiştirilecek metni girin:")
            if not ok2:
                print("Değiştirme iptal edildi.")  # Hata ayıklama
                return

            print(f"Değiştiriliyor: '{aranacak_metin}' -> '{degistirilecek_metin}'")  # Hata ayıklama
            # Metin alanındaki içeriği alıyoruz
            metin = self.yazi_alani.toPlainText()
            # Aranan metni değiştiriyoruz
            yeni_metin = metin.replace(aranacak_metin, degistirilecek_metin)
            # Yeni metni metin alanına yazıyoruz
            self.yazi_alani.setText(yeni_metin)
            QMessageBox.information(self, "Değiştir", "Metin değiştirildi!")
            print("Metin değiştirildi.")  # Hata ayıklama
        except Exception as e:
            print(f"Değiştirme hatası: {e}")  # Hata ayıklama
            QMessageBox.critical(self, "Hata", f"Değiştirme hatası: {e}")

# Menu sınıfı, menü çubuğunu ve ana pencereyi oluşturuyor, QMainWindow'dan türetiliyor
class Menu(QMainWindow):
    def __init__(self):
        # Üst sınıfın (QMainWindow) yapıcı metodunu çağırıyoruz
        super().__init__()

        # Notepad sınıfından bir pencere oluşturuyoruz
        self.pencere = Notepad()
        # Notepad widget'ını ana pencerenin merkezi widget'ı olarak ayarlıyoruz
        self.setCentralWidget(self.pencere)
        # Menüleri oluşturmak için metodu çağırıyoruz
        self.menuleri_olustur()

    def menuleri_olustur(self):
        # Menü çubuğunu oluşturuyoruz
        menubar = self.menuBar()

        # "Dosya" adında bir menü ekliyoruz
        dosya = menubar.addMenu("Dosya")
        duzenle = menubar.addMenu("Düzenle")

        # Menü için eylemler (QAction) oluşturuyoruz
        dosya_ac = QAction("Dosya Aç", self)
        dosya_ac.setShortcut("Ctrl+O")  # Kısayol tuşu: Ctrl+O

        dosya_kaydet = QAction("Dosya Kaydet", self)
        dosya_kaydet.setShortcut("Ctrl+S")  # Kısayol tuşu: Ctrl+S

        cikis = QAction("Çıkış", self)
        cikis.setShortcut("Ctrl+Q")  # Kısayol tuşu: Ctrl+Q

        # Düzenle menüsüne menü ekliyoruz
        ara_ve_degistir = duzenle.addMenu("Ara ve Değiştir")

        temizle = QAction("Temizle", self)
        temizle.setShortcut("Ctrl+D")  # Kısayol tuşu: Ctrl+D

        ara = QAction("Ara", self)  # Kısayol tuşu: Ctrl+F
        ara.setShortcut("Ctrl+F")

        degistir = QAction("Değiştir", self)  # Kısayol tuşu: Ctrl+H
        degistir.setShortcut("Ctrl+H")

        # Eylemleri menüye ekliyoruz
        dosya.addAction(dosya_ac)
        dosya.addAction(dosya_kaydet)
        dosya.addAction(temizle)
        dosya.addAction(cikis)

        ara_ve_degistir.addAction(ara)
        ara_ve_degistir.addAction(degistir)

        duzenle.addAction(temizle)

        # Menüdeki bir eylemin tetiklenmesi durumunda response fonksiyonunu çağırıyoruz
        dosya.triggered.connect(self.response)
        duzenle.triggered.connect(self.response)
        ara_ve_degistir.triggered.connect(self.response)

        # Yeni: Menü oluşturulduğunu konsola yaz
        print("Menü çubuğu oluşturuldu.")  # Hata ayıklama
        self.setWindowTitle("Metin Editörü")
        self.show()

    # Menü eylemlerine yanıt veren fonksiyon
    def response(self, action):
        # Hangi eylemin tetiklendiğini kontrol ediyoruz
        print(f"Eylem tetiklendi: {action.text()}")  # Hata ayıklama
        if action.text() == "Dosya Aç":
            self.pencere.dosya_ac()  # Dosya açma fonksiyonunu çağır
        elif action.text() == "Dosya Kaydet":
            self.pencere.dosya_kaydet()  # Dosya kaydetme fonksiyonunu çağır
        elif action.text() == "Temizle":  # Menüde "Temizle" olarak tanımlı
            self.pencere.yaziyi_temizle()  # Metin temizleme fonksiyonunu çağır
        elif action.text() == "Çıkış":
            qApp.quit()  # Uygulamayı kapat
        elif action.text() == "Ara":
            self.pencere.metin_ara()  # Arama fonksiyonunu çağır
        elif action.text() == "Değiştir":
            self.pencere.metin_degistir()  # Değiştirme fonksiyonunu çağır

# QApplication nesnesi oluşturuyoruz, bu PyQt uygulamasının ana döngüsünü yönetir
app = QApplication(sys.argv)
# Menu sınıfından bir nesne oluşturuyoruz
menu = Menu()
# Yeni: Uygulama başlatıldığını konsola yaz
print("Uygulama başlatıldı.")  # Hata ayıklama
# Uygulamayı başlatıyoruz ve sistemden çıkış yapıldığında uygulamayı kapatıyoruz
sys.exit(app.exec_())