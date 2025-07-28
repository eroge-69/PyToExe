import sys
import pandas as pd
import re
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QMessageBox
)

STALE_KONTO = "28109027050000000153215794"

miesiace = {
    "styczeń": 1, "luty": 2, "marzec": 3, "kwiecień": 4,
    "maj": 5, "czerwiec": 6, "lipiec": 7, "sierpień": 8,
    "wrzesień": 9, "październik": 10, "listopad": 11, "grudzień": 12
}

class ExcelToTxt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generator przelewów")
        self.setGeometry(300, 300, 500, 200)

        self.layout = QVBoxLayout()

        self.label1 = QLabel("1. Wybierz plik Excel (.xlsx):")
        self.layout.addWidget(self.label1)

        self.button_file = QPushButton("Wybierz plik")
        self.button_file.clicked.connect(self.wybierz_plik)
        self.layout.addWidget(self.button_file)

        self.label2 = QLabel("2. Wybierz arkusz:")
        self.layout.addWidget(self.label2)

        self.combo_sheets = QComboBox()
        self.layout.addWidget(self.combo_sheets)

        self.button_generate = QPushButton("3. Generuj plik przelewów TXT")
        self.button_generate.clicked.connect(self.generuj_plik)
        self.layout.addWidget(self.button_generate)

        self.setLayout(self.layout)
        self.plik_xlsx = None

    def wybierz_plik(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Wybierz plik Excel", "", "Excel Files (*.xlsx)")
        if fname:
            self.plik_xlsx = fname
            xls = pd.ExcelFile(fname)
            self.combo_sheets.clear()
            self.combo_sheets.addItems(xls.sheet_names)

    def generuj_plik(self):
        if not self.plik_xlsx:
            QMessageBox.warning(self, "Brak pliku", "Najpierw wybierz plik Excel.")
            return

        arkusz = self.combo_sheets.currentText()

        # Wyciągnięcie nazwy miesiąca i roku z arkusza np. "czerwiec'24"
        dopasowanie = re.search(r"(\w+)[\u2019'](\d{2})", arkusz.lower())
        if not dopasowanie:
            QMessageBox.warning(self, "Błąd", "Nie udało się odczytać miesiąca i roku z nazwy arkusza")
            return

        miesiac_nazwa = dopasowanie.group(1)
        rok_suffix = int(dopasowanie.group(2))
        rok = 2000 + rok_suffix

        if miesiac_nazwa not in miesiace:
            QMessageBox.warning(self, "Błąd", f"Nieznana nazwa miesiąca: {miesiac_nazwa}")
            return

        miesiac_num = miesiace[miesiac_nazwa]

        # Data wypłaty = 20. kolejnego miesiąca
        miesiac_wyplaty = miesiac_num + 1
        rok_wyplaty = rok
        if miesiac_wyplaty == 13:
            miesiac_wyplaty = 1
            rok_wyplaty += 1
        data_wyplaty = f"20-{miesiac_wyplaty:02d}-{rok_wyplaty}"

        try:
            df = pd.read_excel(self.plik_xlsx, sheet_name=arkusz)
            df.columns = df.columns.str.strip()

            wynik = ["4120414|1"]  # pierwsza linia nagłówkowa

            for _, row in df.iterrows():
                if pd.isna(row.get('LP')) or pd.isna(row.get('DANE KUPUJĄCEGO')):
                    continue

                kupujacy = str(row['DANE KUPUJĄCEGO']).strip()
                lokal = str(row.get('NR LOKALU')).strip() if not pd.isna(row.get('NR LOKALU')) else "brak"
                konto = str(row.get('Kolumna2')).strip() if not pd.isna(row.get('Kolumna2')) else "BRAK_KONTA"

                kwota = row.get('do wypłaty')

                liczby = re.sub(r'[^\d,.-]', '', str(kwota)).replace(',', '.')
                try:
                    float_kwota = float(liczby)
                    sformatowana_kwota = f"{float_kwota:.2f}".replace('.', ',').replace(' ', '')
                except:
                    continue

                opis = f"Czynsz za miesiąc {miesiac_nazwa} za lokal {lokal}"

                linia = f"1|{STALE_KONTO}|{konto}|{kupujacy}|brak danych|{sformatowana_kwota}|1|{opis}|{data_wyplaty}|"
                wynik.append(linia)

            if len(wynik) > 1:
                nazwa_pliku = f"przelew_{miesiac_nazwa}.txt"
                folder = os.path.dirname(self.plik_xlsx)
                sciezka = os.path.join(folder, nazwa_pliku)
                with open(sciezka, "w", encoding="utf-8") as f:
                    f.write("\n".join(wynik))
                QMessageBox.information(self, "Sukces", f"Plik zapisany jako:\n{sciezka}")
            else:
                QMessageBox.information(self, "Brak danych", "Nie znaleziono danych do zapisania.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = ExcelToTxt()
    okno.show()
    sys.exit(app.exec_())
