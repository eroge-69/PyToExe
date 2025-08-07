import sys
import os
import time
import json
import uuid
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QFileDialog, QListWidget, 
                             QSpinBox, QProgressBar, QTabWidget, QMessageBox, QLineEdit,
                             QGroupBox, QFormLayout, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QDir, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap
from urllib.parse import quote
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from PySide6.QtWidgets import QInputDialog
from GUI_RELEASE import Ui_MainWindow
import csv
import re
import random

# Sabit MAC adresi ve son kullanım tarihi
ALLOWED_MAC_ADDRESS = "123861697537263"  # Cihazınızın MAC adresini buraya girin
EXPIRY_DATE = "2025-12-31"  # Format: YYYY-MM-DD

def check_license():
    """Lisans kontrolü yapar: MAC adresi ve son kullanım tarihi."""
    try:
        current_mac = str(uuid.getnode())
        if current_mac != ALLOWED_MAC_ADDRESS:
            return False, 0, "Lisans bu cihaz için geçerli değil!"

        try:
            expiry_date = datetime.fromisoformat(EXPIRY_DATE)
        except ValueError:
            return False, 0, "Geçersiz son kullanım tarihi formatı!"

        remaining_days = (expiry_date - datetime.now()).days

        if remaining_days < 0:
            return False, 0, "Lisans süresi doldu!"
        
        return True, remaining_days, None
    except Exception as e:
        return False, 0, f"Lisans kontrolü başarısız: {str(e)}"

def load_numbers_from_csv(csv_path):
    numbers = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for cell in row:
                cell = cell.strip().replace(" ", "")
                if cell.startswith("+"):
                    cell = cell[1:]
                if re.fullmatch(r"\d{8,15}", cell):
                    numbers.append(cell)
    return numbers

class WhatsAppSenderThread(QThread):
    progress_update = Signal(int, str)
    status_update = Signal(str)
    finished_signal = Signal()

    def __init__(self, numbers, message, media_files, media_messages, wait, delay):
        super().__init__()
        self.numbers = numbers
        self.message = message
        self.media_files = media_files
        self.media_messages = media_messages
        self.delay = delay * 5
        self.wait = wait * 0.5
        self.is_running = True

    def log_status(self, message):
        current_time = time.strftime("%H:%M:%S")
        log_entry = f"[{current_time}] {message}"
        self.status_update.emit(log_entry)

    def insansi_yaz(self, element, text):
        for character in text:
            element.send_keys(character)
            time.sleep(random.uniform(0.05, 0.1))

    def send_multiline_message(self, message_box, message):
        lines = message.splitlines()
        for idx, line in enumerate(lines):
            self.insansi_yaz(message_box, line)
            if idx != len(lines) - 1:
                message_box.send_keys(Keys.SHIFT + Keys.ENTER)

    def run(self):
        try:
            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument("--profile-directory=Default")
            options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")
            options.add_argument('--start-maximized')
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")

            self.status_update.emit("Tarayıcı başlatılıyor...")

            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.get('https://web.whatsapp.com')
            
            self.status_update.emit("WhatsApp Web'e giriş yapın ve QR kodu okutun...")
            
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[role="grid"]'))
                )
                sleep(1)
            except:
                self.status_update.emit("Giriş yapılamadı. QR kodu okutulamadı.")
                self.driver.quit()
                self.finished_signal.emit()
                return
            
            try:
                first_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button"))
                )
                first_button.click()
                self.log_status("Açılışta çıkan butona tıklandı.")
            except:
                pass

            total_number = len(self.numbers)
            for idx, number in enumerate(self.numbers):
                if not self.is_running:
                    self.status_update.emit("İşlem durduruldu.")
                    break
                    
                number = number.strip()
                if number == "":
                    continue
                    
                self.progress_update.emit(idx + 1, number)
                self.status_update.emit(f"Mesaj gönderiliyor: {number}")
                
                try:
                    url = f'https://web.whatsapp.com/send?phone={number}'
                    self.driver.get(url)
                    
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='main']"))
                        )
                        
                        invalid_messages = [
                            "//div[text()='URL yoluyla paylaşılan telefon numarası geçersiz.']",
                            "//div[contains(text(), 'Telefon numarası geçersiz')]",
                            "//div[contains(text(), 'The phone number shared via url is invalid')]"
                        ]
                        
                        for xpath in invalid_messages:
                            try:
                                if self.driver.find_elements(By.XPATH, xpath):
                                    self.log_status(f"Geçersiz numara: {number}")
                                    break
                            except:
                                pass
                        else:
                            pass
                    except Exception as e:
                        self.log_status(f"Numara kontrolü sırasında hata: {str(e)}")

                    if self.media_files:
                        self.status_update.emit("Medya dosyaları yükleniyor...")
                        attach_button = WebDriverWait(self.driver, self.delay).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='plus-rounded']"))
                        )
                        attach_button.click()
                        
                        try:
                            image_box = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']"))
                            )
                        except:
                            try:
                                image_box = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//input[@accept='*']"))
                                )
                            except:
                                image_box = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                                )
                        
                        image_box.send_keys('\n'.join(self.media_files))
                        time.sleep(self.wait)
                        
                        combined_media_message = '\n'.join(
                            self.media_messages.get(media_file, '') for media_file in self.media_files if media_file in self.media_messages
                        )
                        if combined_media_message:
                            message_box = WebDriverWait(self.driver, self.delay).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
                            )
                            self.send_multiline_message(message_box, combined_media_message)
                            message_box.send_keys(Keys.ENTER)
                            time.sleep(self.wait)
                        
                        send_button = WebDriverWait(self.driver, self.delay).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='wds-ic-send-filled']"))
                        )
                        send_button.click()
                        time.sleep(self.wait)
                        
                        try:
                            target_div = self.driver.find_element(By.CSS_SELECTOR, "div[data-tab='8'].x3psx0u")
                            WebDriverWait(target_div, 30).until_not(
                                EC.presence_of_element_located((By.TAG_NAME, "circle"))
                            )
                        except:
                            self.log_status("Medya yükleme durumu kontrol edilemedi, devam ediliyor...")
                    
                    if self.message:
                        message_box = None
                        message_box_selectors = [
                            "//div[@role='textbox' and @data-tab='10']",
                            "//div[@role='textbox']",
                            "//p[@class='selectable-text copyable-text']"
                        ]
                        for selector in message_box_selectors:
                            try:
                                message_box = WebDriverWait(self.driver, self.delay).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                if message_box:
                                    break
                            except:
                                continue
                        if not message_box:
                            self.log_status("Mesaj kutusu bulunamadı, atlanıyor.")
                        else:
                            message_box.click()
                            message_box.clear()
                            safe_message = self.message
                            self.send_multiline_message(message_box, safe_message)
                            time.sleep(self.wait)
                            send_button = None
                            send_button_selectors = [
                                "//span[@data-icon='wds-ic-send-filled']",
                                "//button[@data-testid='compose-btn-send']",
                                "//span[@data-icon='send']"
                            ]
                            for selector in send_button_selectors:
                                try:
                                    send_button = WebDriverWait(self.driver, self.delay).until(
                                        EC.element_to_be_clickable((By.XPATH, selector))
                                    )
                                    if send_button:
                                        break
                                except:
                                    continue
                            if send_button:
                                send_button.click()
                                time.sleep(self.wait)
                            else:
                                try:
                                    message_box.click()
                                    message_box.send_keys(Keys.ENTER)
                                    time.sleep(self.wait)
                                    self.log_status("Gönder butonu bulunamadı, Enter ile gönderildi.")
                                except Exception as e:
                                    self.log_status(f"Gönder butonu ve Enter ile gönderme başarısız")
                    
                    if self.is_running:
                        self.log_status(f"Mesaj gönderildi: {number}")
                
                except Exception as e:
                    self.status_update.emit(f"Hata: {str(e)}")
                
                time.sleep(self.wait)
            
            self.driver.quit()
            self.finished_signal.emit()
            
        except Exception as e:
            self.status_update.emit(f"Kritik hata: {str(e)}")
            self.finished_signal.emit()
    
    def stop(self):
        self.is_running = False
        if hasattr(self, 'driver'):
            self.driver.quit()

class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("app_icon.ico"))
        
        # Lisans kontrolü
        is_valid, remaining_days, error_message = check_license()
        if not is_valid:
            msg = QMessageBox()
            msg.setWindowTitle("Lisans Hatası")
            msg.setText(error_message)
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()
            sys.exit(1)
        
        # Kalan gün sayısını versionLabel'da göster
        self.ui.versionLabel.setText(f"v2.0 (Kalan: {remaining_days} gün)")
        
        self.sender_thread = None
        self.media_files = []
        self.media_messages = {}
        self.numbers = []
        
        self.load_settings()
        self.setup_connections()
        
        self.ui.mediaList.itemSelectionChanged.connect(self.on_media_selection_changed)
        self.ui.mediaMessageEdit.textChanged.connect(self.on_media_message_changed)

    def setup_connections(self):
        self.ui.addNumberBtn.clicked.connect(self.add_number)
        self.ui.startBtn.clicked.connect(self.start_sending)
        self.ui.stopBtn.clicked.connect(self.stop_sending)
        self.ui.removeNumberBtn.clicked.connect(self.remove_number)
        self.ui.importNumbersBtn.clicked.connect(self.import_numbers)
        self.ui.addMediaBtn.clicked.connect(self.add_media)
        self.ui.removeMediaBtn.clicked.connect(self.remove_media)
        self.ui.clearMediaBtn.clicked.connect(self.clear_media)
        
        self.ui.delaySpin.valueChanged.connect(self.save_settings)
        self.ui.waitSpin.valueChanged.connect(self.save_settings)

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.media_messages = settings.get('media_messages', {})
                    delay = settings.get('delay', 3)
                    wait = settings.get('wait', 3)
                    self.ui.delaySpin.setValue(delay)
                    self.ui.waitSpin.setValue(wait)
                    self.update_media_list()
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText(f"Ayarlar yüklenirken hata: {str(e)}")
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()

    def save_settings(self):
        try:
            settings = {
                'media_messages': self.media_messages,
                'delay': self.ui.delaySpin.value(),
                'wait': self.ui.waitSpin.value()
            }
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText(f"Ayarlar kaydedilirken hata: {str(e)}")
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()

    def update_media_list(self):
        self.ui.mediaList.clear()
        for file_path in self.media_files:
            item = QListWidgetItem(os.path.basename(file_path))
            if file_path in self.media_messages:
                item.setText(f"★ {os.path.basename(file_path)}")
            self.ui.mediaList.addItem(item)

    def on_media_selection_changed(self):
        selected_items = self.ui.mediaList.selectedItems()
        if selected_items:
            file_name = selected_items[0].text().replace('★ ', '')
            file_path = next((path for path in self.media_files if os.path.basename(path) == file_name), None)
            if file_path:
                self.ui.mediaMessageEdit.setText(self.media_messages.get(file_path, ''))
        else:
            self.ui.mediaMessageEdit.clear()

    def on_media_message_changed(self):
        selected_items = self.ui.mediaList.selectedItems()
        if selected_items:
            file_name = selected_items[0].text().replace('★ ', '')
            file_path = next((path for path in self.media_files if os.path.basename(path) == file_name), None)
            if file_path:
                message = self.ui.mediaMessageEdit.toPlainText()
                if message:
                    self.media_messages[file_path] = message
                    selected_items[0].setText(f"★ {file_name}")
                else:
                    self.media_messages.pop(file_path, None)
                    selected_items[0].setText(file_name)
                self.save_settings()

    def add_media(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Medya Dosyaları Ekle", "", 
                                                  "Medya Dosyaları (*.jpg *.jpeg *.png *.pdf *.mp4)")
        if not file_paths:
            return
            
        for path in file_paths:
            self.media_files.append(path)
            item = QListWidgetItem(os.path.basename(path))
            if path in self.media_messages:
                item.setText(f"★ {os.path.basename(path)}")
            self.ui.mediaList.addItem(item)
        self.save_settings()

    def remove_media(self):
        selected_items = self.ui.mediaList.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            file_name = item.text().replace('★ ', '')
            file_path = next((path for path in self.media_files if os.path.basename(path) == file_name), None)
            if file_path:
                self.media_files.remove(file_path)
                self.media_messages.pop(file_path, None)
                self.ui.mediaList.takeItem(self.ui.mediaList.row(item))
        self.save_settings()

    def clear_media(self):
        self.media_files.clear()
        self.media_messages.clear()
        self.ui.mediaList.clear()
        self.ui.mediaMessageEdit.clear()
        self.save_settings()

    def start_sending(self):
        # Lisans kontrolü
        is_valid, remaining_days, error_message = check_license()
        if not is_valid:
            msg = QMessageBox()
            msg.setWindowTitle("Lisans Hatası")
            msg.setText(error_message)
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()
            return
        
        if self.sender_thread and self.sender_thread.isRunning():
            return
        
        self.ui.progressBar.setValue(0)
        message = self.ui.messageEdit.toPlainText()
        delay = self.ui.delaySpin.value()
        wait = self.ui.waitSpin.value()

        if not self.numbers:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText("Lütfen en az bir numara ekleyin!")
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()
            return
        
        self.sender_thread = WhatsAppSenderThread(self.numbers, message, self.media_files, self.media_messages, wait, delay)
        self.sender_thread.progress_update.connect(self.update_progress)
        self.sender_thread.status_update.connect(self.update_status)
        self.sender_thread.finished_signal.connect(self.sending_finished)
        
        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        self.sender_thread.start()
        
    def stop_sending(self):
        if self.sender_thread:
            self.sender_thread.stop()
            self.ui.startBtn.setEnabled(True)
            self.ui.stopBtn.setEnabled(False)
            self.sender_thread.is_running = False
            self.ui.statusText.append("İşlemler durduruluyor...")
        
    def update_progress(self, current, number):
        self.ui.progressBar.setValue(int((current / len(self.numbers)) * 100))
        self.ui.statusText.append(f"İşleniyor: {number} ({current}/{len(self.numbers)})")
        
    def update_status(self, message):
        self.ui.statusText.append(message)
        
    def sending_finished(self):
        self.ui.startBtn.setEnabled(True)
        self.ui.stopBtn.setEnabled(False)
        self.ui.statusText.append("İşlem tamamlandı!")

    def add_number(self):
        number, ok = QInputDialog.getText(self, "Numara Ekle", 
                                      "Telefon numarasını ülke koduyla birlikte girin (örn: 905551234567):")
        if ok and number:
            self.ui.numbersList.addItem(number)
            self.numbers.append(number)
            self.log_status(f"Numara eklendi: {number}")

    def remove_number(self):
        selected_items = self.ui.numbersList.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            self.numbers.remove(item.text())
            self.ui.numbersList.takeItem(self.ui.numbersList.row(item))
            self.log_status(f"Numara silindi: {item.text()}")
    
    def import_numbers(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Numara Listesi İçe Aktar", "", "CSV Dosyaları (*.csv);;Metin Dosyaları (*.txt)")
        if not file_path:
            return
        try:
            if file_path.endswith('.csv'):
                new_numbers = load_numbers_from_csv(file_path)
            else:
                with open(file_path, "r") as f:
                    new_numbers = [line.strip() for line in f.readlines() if line.strip()]
            self.numbers.extend(new_numbers)
            self.ui.numbersList.clear()
            self.ui.numbersList.addItems(new_numbers)
            self.log_status(f"{len(new_numbers)} numara içe aktarıldı.")
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText(f"Dosya içe aktarılırken hata oluştu: {str(e)}")
            msg.setStyleSheet("QLabel { color: black; }")
            msg.exec()

    def log_status(self, message):
        current_time = time.strftime("%H:%M:%S")
        log_entry = f"[{current_time}] {message}"
        self.ui.statusText.append(log_entry)
        self.ui.statusText.verticalScrollBar().setValue(self.ui.statusText.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("windows")
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())