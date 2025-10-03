import sys
import time
import os
import io
import ftplib
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QSpinBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, QTimer, QDateTime, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon
import fdb
import logging
import pandas as pd

# Naplózás beállítása
log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
log_handler = logging.FileHandler('debug_log.txt', mode='a', encoding='utf-8')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)

# Excel számára problémás karakterek tisztítása
def clean_excel_string(value):
    """
    Megtisztítja az Excel számára problémás karaktereket a cellákból
    """
    if isinstance(value, str):
        # Eltávolítjuk vagy lecseréljük az Excel által nem támogatott karaktereket
        # Excel nem támogatja ezeket a vezérlő karaktereket: \x00-\x1F (kivéve \t, \n, \r)
        invalid_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
                        '\x08', '\x0b', '\x0c', '\x0e', '\x0f', '\x10', '\x11', '\x12',
                        '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a',
                        '\x1b', '\x1c', '\x1d', '\x1e', '\x1f']
        for char in invalid_chars:
            value = value.replace(char, '')
        # Trim whitespace
        value = value.strip()
    return value

class QueryThread(QThread):
    query_finished = pyqtSignal(list, list)

    def __init__(self, dsn, user, password, fbclient_path, sql_file):
        super().__init__()
        self.dsn = dsn
        self.user = user
        self.password = password
        self.fbclient_path = fbclient_path
        self.sql_file = sql_file

    def run(self):
        results = []
        column_names = []
        try:
            logging.info("SQL lekérdezés végrehajtása.")
            con = fdb.connect(
                dsn=self.dsn, user=self.user, password=self.password,
                fb_library_name=self.fbclient_path, charset='WIN1250'
            )
            cur = con.cursor()
            with open(self.sql_file, 'r', encoding='ISO-8859-2') as file:
                sql_query = file.read()
            cur.execute(sql_query)
            results = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            con.close()
            logging.info("Lekérdezés sikeresen végrehajtva.")
        except Exception as e:
            logging.error(f"Hiba a lekérdezés végrehajtása közben: {e}")
        self.query_finished.emit(results, column_names)

class SKUSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_query)
        self.current_time_timer = QTimer(self)
        self.current_time_timer.timeout.connect(self.update_current_time)
        self.current_time_timer.start(1000)
        self.last_query_time = None
        self.ftp_host = 'pentacolor.hu'
        self.ftp_port = 21
        self.ftp_user = 'webfile@pentacolor.hu'
        self.ftp_password = 'NPnkSlGKiI8C'

    def initUI(self):
        self.setWindowTitle('InCash Lekérdezés Futattó')
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon('icon.png'))  # Itt állítjuk be az ikont

        layout = QVBoxLayout()

        self.dsn_input = QLineEdit(self)
        self.dsn_input.setPlaceholderText("DSN")
        self.dsn_input.setText("192.168.164.252/3048:F:\\incash\\database\\INCASH.FDB")
        self.dsn_input.setReadOnly(True)
        layout.addWidget(self.dsn_input)

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Felhasználó")
        self.user_input.setText("ICPUBLIC")
        self.user_input.setReadOnly(True)
        layout.addWidget(self.user_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Jelszó")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("ickey2004")
        self.password_input.setReadOnly(True)
        layout.addWidget(self.password_input)

        interval_layout = QHBoxLayout()
        self.interval_label = QLabel("Időzítő intervallum (perc):")
        interval_layout.addWidget(self.interval_label)

        self.interval_input = QSpinBox(self)
        self.interval_input.setRange(1, 1440)
        self.interval_input.setValue(60)
        interval_layout.addWidget(self.interval_input)

        self.interval_display_label = QLabel("Aktuális intervallum: 60 perc")
        interval_layout.addWidget(self.interval_display_label)

        layout.addLayout(interval_layout)

        self.interval_input.valueChanged.connect(self.update_interval_display)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Időzítő indítása", self)
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Időzítő leállítása", self)
        self.stop_button.clicked.connect(self.stop_timer)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel("Állapot: Kész", self)
        layout.addWidget(self.status_label)

        self.current_time_label = QLabel("Jelenlegi idő: --:--:--", self)
        layout.addWidget(self.current_time_label)

        self.last_query_label = QLabel("Utolsó lekérdezés: Soha", self)
        layout.addWidget(self.last_query_label)

        self.next_query_label = QLabel("Következő lekérdezés: Nincs ütemezve", self)
        layout.addWidget(self.next_query_label)

        self.log_button = QPushButton("Naplófájl megnyitása", self)
        self.log_button.clicked.connect(self.open_log_file)
        layout.addWidget(self.log_button)

        self.open_files_button = QPushButton("FTP Fájlok megnyitása", self)
        self.open_files_button.clicked.connect(self.open_ftp_files)
        layout.addWidget(self.open_files_button)

        self.setLayout(layout)

        # Alkalmazzuk a világos és színes modern stílusokat
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLineEdit, QSpinBox, QPushButton, QLabel {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 8px;
                border-radius: 5px;
                margin: 4px 0;
            }
            QLineEdit {
                border-left: 5px solid #0078d7;
            }
            QSpinBox {
                border-left: 5px solid #28a745;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #0078d7;
            }
            QLabel {
                font-size: 16px;
            }
        """)

    def update_interval_display(self):
        interval_minutes = self.interval_input.value()
        self.interval_display_label.setText(f"Aktuális intervallum: {interval_minutes} perc")

    def start_timer(self):
        interval_minutes = self.interval_input.value()
        interval_milliseconds = interval_minutes * 60 * 1000
        self.timer.start(interval_milliseconds)
        logging.info(f"Időzítő elindítva {interval_minutes} perces intervallummal")
        self.status_label.setText(f"Állapot: Időzítő elindítva, futtatás {interval_minutes} percenként")
        self.update_next_query_time()

    def stop_timer(self):
        self.timer.stop()
        logging.info("Időzítő leállítva")
        self.status_label.setText("Állapot: Időzítő leállítva")
        self.next_query_label.setText("Következő lekérdezés: Nincs ütemezve")

    def update_next_query_time(self):
        next_query_time = QDateTime.currentDateTime().addSecs(self.interval_input.value() * 60)
        self.next_query_label.setText(f"Következő lekérdezés: {next_query_time.toString('yyyy-MM-dd HH:mm:ss')}")

    def update_current_time(self):
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.current_time_label.setText(f"Jelenlegi idő: {current_time}")

    def is_host_reachable(self, host):
        try:
            subprocess.check_output(['ping', '-n', '1', host], stderr=subprocess.STDOUT, universal_newlines=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def execute_query(self):
        self.status_label.setText("Állapot: Lekérdezés futtatása")
        dsn = self.dsn_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        fbclient_path = os.path.abspath("fbclient.dll")
        sql_file = os.path.abspath("teszt.sql")

        if not all([dsn, user, password, fbclient_path, sql_file]):
            logging.error("Hiányzó adatbázis kapcsolat részletei vagy fájlok.")
            self.status_label.setText("Állapot: Hiányzó adatbázis kapcsolat részletei vagy fájlok")
            self.update_next_query_time()
            return

        self.query_thread = QueryThread(dsn, user, password, fbclient_path, sql_file)
        self.query_thread.query_finished.connect(self.process_query_results)
        self.query_thread.start()

        self.last_query_time = QDateTime.currentDateTime()
        self.last_query_label.setText(f"Utolsó lekérdezés: {self.last_query_time.toString('yyyy-MM-dd HH:mm:ss')}")
        self.start_time = time.time()
        self.update_next_query_time()

    def process_query_results(self, results, column_names):
        if not results or not column_names:
            logging.error("A lekérdezés nem adott vissza eredményt.")
            self.status_label.setText("Állapot: A lekérdezés nem adott vissza eredményt")
            return

        try:
            df = pd.DataFrame(results, columns=column_names)

            # Csak számokat tartalmazó oszlopok konvertálása egész számokra
            for column in df.columns:
                if pd.to_numeric(df[column], errors='coerce').notnull().all():
                    df[column] = df[column].astype(int)

            # Tisztítjuk az Excel számára problémás karaktereket
            df = df.map(clean_excel_string)

            # Lokális mentés helyett mentés az FTP szerverre
            self.upload_to_ftp(df, 'webshop.xlsx', 'webshop.csv', 'webshop.xml')

            elapsed_time = time.time() - self.start_time
            logging.info(f"Eredmények mentve az FTP szerverre.")
            logging.info(f"Folyamat befejeződött {elapsed_time:.2f} másodperc alatt.")

            self.status_label.setText("Állapot: Fájlok sikeresen mentve az FTP szerverre")
            self.last_query_label.setText(
                f"Utolsó lekérdezés: {self.last_query_time.toString('yyyy-MM-dd HH:mm:ss')} ({elapsed_time:.2f} másodperc)")

        except Exception as e:
            logging.error(f"Hiba a lekérdezési eredmények FTP-re való mentése közben: {e}")
            self.status_label.setText("Állapot: Hiba a fájlok FTP-re való mentése közben")

    def upload_to_ftp(self, dataframe, excel_filename, csv_filename, xml_filename):
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(self.ftp_host, self.ftp_port)
                ftp.login(self.ftp_user, self.ftp_password)

                # Excel fájl feltöltése
                with io.BytesIO() as excel_buffer:
                    # Az engine='openpyxl' használata stabilabb Excel generáláshoz
                    dataframe.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    ftp.storbinary(f'STOR {excel_filename}', excel_buffer)

                # CSV fájl feltöltése
                with io.BytesIO() as csv_buffer:
                    dataframe.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
                    csv_buffer.seek(0)
                    ftp.storbinary(f'STOR {csv_filename}', csv_buffer)

                # XML fájl feltöltése
                with io.BytesIO() as xml_buffer:
                    dataframe.to_xml(xml_buffer, index=False)
                    xml_buffer.seek(0)
                    ftp.storbinary(f'STOR {xml_filename}', xml_buffer)

            logging.info("Fájlok sikeresen feltöltve az FTP szerverre.")

        except Exception as e:
            logging.error(f"Hiba az FTP feltöltés során: {e}")
            raise

    def open_log_file(self):
        try:
            log_file_path = os.path.abspath('debug_log.txt')
            if sys.platform == "win32":
                os.startfile(log_file_path)
            elif sys.platform == "darwin":
                subprocess.call(('open', log_file_path))
            else:
                subprocess.call(('xdg-open', log_file_path))
        except Exception as e:
            logging.error(f"Hiba a naplófájl megnyitása közben: {e}")
            self.status_label.setText("Állapot: Hiba a naplófájl megnyitása közben")

    def open_ftp_files(self):
        try:
            ftp_url = f'ftp://{self.ftp_host}'

            if sys.platform == "win32":
                subprocess.call(['explorer', ftp_url])
            elif sys.platform == "darwin":
                subprocess.call(['open', ftp_url])
            else:
                subprocess.call(['xdg-open', ftp_url])

        except Exception as e:
            logging.error(f"Hiba az FTP fájlok megnyitása közben: {e}")
            QMessageBox.critical(self, "Hiba", f"Hiba az FTP fájlok megnyitása közben: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.png'))
    main_win = SKUSelector()
    main_win.show()
    sys.exit(app.exec_())