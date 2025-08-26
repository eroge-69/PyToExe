import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from dosyaadi import *
from PyQt5 import QtCore, QtGui, QtWidgets
from diger import *



# Veritabanı bağlantısı
conn = sqlite3.connect("veritabani.db")
curs = conn.cursor()

# Tablo oluşturma
curs.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        SporcuTcNo TEXT NOT NULL,
        SporcuAdi TEXT NOT NULL,
        SporcuSoyadi TEXT NOT NULL,
        KulupAdi TEXT NOT NULL,
        Brans TEXT NOT NULL,
        Cinsiyet TEXT NOT NULL,
        DTarihi TEXT NOT NULL,
        MHal TEXT NOT NULL,
        Kilo TEXT NOT NULL
    )
""")
conn.commit()


def ekle():
    try:
        print("Kayıt işlemi başladı...")
        _txttc = ui.txttc.text()
        _txtad = ui.txtad.text()
        _txtsoyad = ui.txtsoyad.text()
        _cbxkulup = ui.cbxkulup.currentText()
        _lstbrans = ui.lstbrans.currentItem().text() if ui.lstbrans.currentItem() else ""
        _cbxcinsiyet = ui.cbxcinsiyet.currentText()
        _clddogum = ui.clddogum.selectedDate().toString("dd.MM.yyyy")
        _spnkilo = str(ui.spnkilo.value())
        medenihal = "EVLİ" if ui.chkmedenihal.isChecked() else "BEKAR"

        print(
            f"Girilen bilgiler: TC={_txttc}, Ad={_txtad}, Soyad={_txtsoyad}, Kulüp={_cbxkulup}, Brans={_lstbrans}, Cinsiyet={_cbxcinsiyet}, Doğum={_clddogum}, Kilo={_spnkilo}, MHal={medenihal}")

        if not (_txttc and _txtad and _txtsoyad and _lstbrans):
            QMessageBox.warning(MainWindow, "Uyarı", "Lütfen tüm gerekli alanları doldurunuz!")
            return

        curs.execute("""
            INSERT INTO kullanicilar 
            (SporcuTcNo, SporcuAdi, SporcuSoyadi, KulupAdi, Brans, Cinsiyet, DTarihi, MHal, Kilo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (_txttc, _txtad, _txtsoyad, _cbxkulup, _lstbrans, _cbxcinsiyet, _clddogum, medenihal, _spnkilo))

        conn.commit()
        print("Kayıt başarılı.")
        QMessageBox.information(MainWindow, "Başarılı", "Kayıt başarıyla eklendi.")

    except Exception as e:
        print("HATA:", str(e))
        QMessageBox.critical(MainWindow, "Hata", f"Kayıt eklenemedi.\n{str(e)}")
    listele()
    formu_temizle()


def cikisYap():
    cevap = QMessageBox.question(MainWindow, "Çıkış Uyarısı Dikkat!!!", "Çıkmak İstediğinize Emin Misiniz?",
                                 QMessageBox.Yes | QMessageBox.No)

    if cevap == QMessageBox.Yes:
        print("Kullanıcı çıkış yaptı.")
        QtWidgets.qApp.quit()
    else:
        print("Çıkış iptal edildi.")


def sil():
    secili_satir = ui.tablo.currentRow()
    if secili_satir == -1:
        QMessageBox.warning(MainWindow, "Uyarı", "Lütfen silmek için bir satır seçin!")
        return

    cevap = QMessageBox.question(
        MainWindow,
        "Silme Onayı",
        "Seçili kaydı silmek istediğinize emin misiniz?",
        QMessageBox.Yes | QMessageBox.No
    )

    if cevap == QMessageBox.No:
        return

    # ID bilgisi 0. sütunda, veritabanındaki birincil anahtar
    silinecek_id = ui.tablo.item(secili_satir, 0).text()

    try:
        curs.execute("DELETE FROM kullanicilar WHERE ID = ?", (silinecek_id,))
        conn.commit()
        QMessageBox.information(MainWindow, "Başarılı", "Kayıt başarıyla silindi.")
        listele()
    except Exception as e:
        QMessageBox.critical(MainWindow, "Hata", f"Kayıt silinemedi.\n{str(e)}")
    listele()


def formu_temizle():
    ui.txttc.clear()
    ui.txtad.clear()
    ui.txtsoyad.clear()
    ui.cbxkulup.setCurrentIndex(0)
    ui.lstbrans.clearSelection()
    ui.cbxcinsiyet.setCurrentIndex(0)
    ui.clddogum.setSelectedDate(QtCore.QDate.currentDate())
    ui.spnkilo.setValue(50)
    ui.chkmedenihal.setChecked(False)


def listele():
    try:
        ui.tablo.setRowCount(0)
        ui.tablo.setHorizontalHeaderLabels(
            ("NO", "Tc No", "Adı", "Soyadı", "Kulüp", "Brans", "Cinsiyet", "Doğum Tarihi", "Medeni Hal",
             "Kilo"))  # Tablodaki eski verileri temizle
        curs.execute("SELECT * FROM kullanicilar")
        veriler = curs.fetchall()

        for row_index, row_data in enumerate(veriler):
            ui.tablo.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                ui.tablo.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(col_data)))

    except Exception as e:
        print("Listeleme hatası:", e)
        QMessageBox.critical(MainWindow, "Hata", f"Listeleme sırasında hata oluştu:\n{str(e)}")


def ara():
    ad = ui.txtaramaad.text().strip()
    soyad = ui.txtaramasoyad.text().strip()

    try:
        # Eğer her iki alan da boşsa tüm listeyi getir
        if ad == "" and soyad == "":
            listele()
            return

        # Tabloyu temizle
        ui.tablo.setRowCount(0)

        # SQL sorgusu ve parametreler dinamik hazırlanacak
        sql = "SELECT * FROM kullanicilar WHERE  "
        kriterler = []
        parametreler = []

        if ad:
            kriterler.append(" SporcuAdi LIKE ?")
            parametreler.append('%' + ad + '%')

        if soyad:
            kriterler.append(" SporcuSoyadi LIKE ?")
            parametreler.append('%' + soyad + '%')

        # Kriterleri birleştir
        sql += " AND".join(kriterler)

        curs.execute(sql, parametreler)
        veriler = curs.fetchall()

        for row_index, row_data in enumerate(veriler):
            ui.tablo.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                ui.tablo.setItem(row_index, col_index, item)

        # Hiç veri bulunamadıysa kullanıcıya bilgi ver
        if not veriler:
            QtWidgets.QMessageBox.information(ui.MainWindow, "Sonuç Yok", "Aradığınız kriterlere uygun sporcu bulunamadı.")

    except Exception as e:
        QtWidgets.QMessageBox.critical(ui.MainWindow, "Hata", f"Arama sırasında hata oluştu:\n{str(e)}")







uygulama=QApplication(sys.argv)
MainWindow=QMainWindow()
ui=Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
listele()
ui.btnkayit.clicked.connect(ekle)
ui.btnsil.clicked.connect(sil)
ui.txtaramaad.textChanged.connect(ara)
ui.txtaramasoyad.textChanged.connect(ara)


sys.exit(uygulama.exec_())










