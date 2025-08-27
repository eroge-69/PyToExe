import sys
import json
import time
from datetime import datetime, timedelta
from threading import Thread
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget,QTableWidgetItem, QHBoxLayout, 
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QLabel, QTimeEdit, QTabWidget,QSlider
)
from PyQt5.QtCore import QTimer, Qt
import pygame
pygame.mixer.init()
import locale

from PyQt5.QtWidgets import QMainWindow
class BellApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEKSİNN - SES KONTROL SİSTEMİ")
        self.setGeometry(300, 200, 900, 600)
        self.schedule = []
        self.running = True
        self.current_music = None

        from PyQt5.QtWidgets import QMenuBar, QAction
        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")
        about_menu = menubar.addMenu("Hakkında")
        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        about_action = QAction("Yazılım Hakkında", self)
        about_action.triggered.connect(lambda: QMessageBox.information(self, "Hakkında", "TEKSİNN - SES KONTROL SİSTEMİ"))
        about_menu.addAction(about_action)
        self.setMenuBar(menubar)
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(180, 180)
        self.logo_label.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc; margin: 10px; border-radius: 5px;")
        self.logo_label.setScaledContents(True)
        logo_path = "icerik/tksorjlogo.jpg"
        from PyQt5.QtGui import QPixmap
        import os
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(self.logo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        from PyQt5.QtWidgets import QFrame
        logo_info_frame = QFrame()
        logo_info_frame.setStyleSheet("background: #f9f9f9; border-radius: 8px; margin: 10px; padding: 10px;")
        logo_info_layout = QHBoxLayout(logo_info_frame)
        logo_info_layout.addWidget(self.logo_label)

        self.company_info = QLabel()
        self.company_info.setText(
            "<b>TEKSİNN</b><br>"
            "İthalat & İhracat A.Ş.<br>"
            "Adres: 1369.Sk N:9, Bandırma<br>"
            "Tel: <a href='tel:+904448995'>+90 444 89 95</a><br>"
            "E-posta: <a href='mailto:info@teksinn.com.tr'>info@teksinn.com.tr</a><br>"
            "Web: <a href='https://www.teksinn.com.tr'>www.teksinn.com.tr</a>"
        )
        self.company_info.setOpenExternalLinks(True)
        self.company_info.setStyleSheet("font-size: 13px; margin: 10px; color: #333; background: transparent; border-radius: 6px; padding: 10px;")
        logo_info_layout.addWidget(self.company_info)
        left_layout.addWidget(logo_info_frame)
        self.next_alarm_label = QLabel("SIRADAKİ ALARM: HESAPLANIYOR...")
        self.next_alarm_label.setStyleSheet("font-size: 14px; margin: 10px;")
        left_layout.addWidget(self.next_alarm_label)
        left_layout.addStretch()
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        right_layout.addWidget(self.datetime_label)
        self.update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.timeout.connect(self.update_next_alarm)
        self.timer.start(1000)
        self.tabs = QTabWidget()
        self.day_tables = {}
        self.days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for i, day in enumerate(self.days_en):
            table = QTableWidget(0, 2)
            table.setHorizontalHeaderLabels(["Zaman (HH:MM)", "Ses Dosyası"])
            self.day_tables[day] = table
            self.day_tables[self.days_tr[i]] = table
            self.tabs.addTab(table, f"{day} / {self.days_tr[i]}")

        today_index = datetime.now().weekday()
        self.tabs.setCurrentIndex(today_index)
        right_layout.addWidget(self.tabs)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Alarm Ekle")
        self.btn_add.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.btn_edit = QPushButton("Alarm Düzenle")
        self.btn_edit.setStyleSheet("padding: 8px; background-color: #FFC107; color: black; border-radius: 5px;")
        self.btn_delete = QPushButton("Alarm Sil")
        self.btn_delete.setStyleSheet("padding: 8px; background-color: #F44336; color: white; border-radius: 5px;")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        right_layout.addLayout(btn_layout)
        self.btn_add.clicked.connect(self.add_event_tab)
        self.btn_edit.clicked.connect(self.edit_event_tab)
        self.btn_delete.clicked.connect(self.delete_event_tab)
        self.weather_label = QLabel("Hava Durumu:")
        self.weather_label.setStyleSheet("font-size: 14px; margin: 10px;")
        right_layout.addWidget(self.weather_label)
        self.player_label = QLabel("Şuan Oynatılıyor:")
        self.player_label.setStyleSheet("font-size: 14px; margin: 10px;")
        left_layout.addWidget(self.player_label)
        self.player_controls = QHBoxLayout()
        self.btn_play = QPushButton("Oynat")
        self.btn_pause = QPushButton("Duraklat")
        self.btn_stop = QPushButton("Durdur")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.setFixedWidth(100)
        self.slider.sliderMoved.connect(self.seek_music)
        self.slider_timer = QTimer()
        self.slider_timer.timeout.connect(self.update_slider)
        self.btn_play.clicked.connect(self.player_play)
        self.btn_pause.clicked.connect(self.player_pause)
        self.btn_stop.clicked.connect(self.player_stop)
        self.player_controls.addWidget(self.btn_play)
        self.player_controls.addWidget(self.btn_pause)
        self.player_controls.addWidget(self.btn_stop)
        self.player_controls.addWidget(self.slider)
        left_layout.addLayout(self.player_controls)

        file_btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Kaydet")
        self.btn_import = QPushButton("İçe Aktar")
        self.btn_export = QPushButton("Dışa Aktar")
        file_btn_layout.addWidget(self.btn_save)
        file_btn_layout.addWidget(self.btn_import)
        file_btn_layout.addWidget(self.btn_export)
        right_layout.addLayout(file_btn_layout)

        self.btn_save.clicked.connect(self.save_schedules)
        self.btn_import.clicked.connect(self.import_schedules)
        self.btn_export.clicked.connect(self.export_schedules)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        self.update_next_alarm()

        self.thread = Thread(target=self.scheduler_loop, daemon=True)
        self.thread.start()

        from PyQt5.QtGui import QIcon
        icon_path = "tks.ico"  
        import os
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)

        kayit_folder = os.path.join(os.path.dirname(__file__), 'kayit')
        json_path = os.path.join(kayit_folder, '1.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.set_all_schedules(data)
                print(f"Zaman Listesi Yüklendi: {json_path}")
            except Exception as e:
                print(f"Zaman Listesi Yükleme Hatası: {e}")

    def add_event_tab(self):
        tab_index = self.tabs.currentIndex()
        current_day = self.days_en[tab_index]
        table = self.day_tables[current_day]
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QTimeEdit
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Yeni Ekle {self.tabs.tabText(tab_index)}")
        layout = QVBoxLayout(dialog)
        label = QLabel("Zaman Belirt:")
        layout.addWidget(label)
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(datetime.now().time())
        layout.addWidget(time_edit)
        file_label = QLabel("Ses dosyası seçin:")
        layout.addWidget(file_label)
        file_btn = QPushButton("Dosya Seç")
        file_path = [""]
        def choose_file():
            path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seç", "", "Ses Dosyaları (*.mp3 *.wav)")
            if path:
                file_path[0] = path
                file_btn.setText(path.split("/")[-1])
        file_btn.clicked.connect(choose_file)
        layout.addWidget(file_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted and file_path[0]:
            row = table.rowCount()
            table.insertRow(row)
            time_item = QTableWidgetItem(time_edit.time().toString("HH:mm"))
            file_item = QTableWidgetItem(file_path[0])
            table.setItem(row, 0, time_item)
            table.setItem(row, 1, file_item)

    def edit_event_tab(self):
        tab_index = self.tabs.currentIndex()
        current_day = self.days_en[tab_index]
        table = self.day_tables[current_day]
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Alarm Düzenle", "Lütfen düzenlemek için bir etkinlik seçin.")
            return
        time_item = table.item(row, 0)
        file_item = table.item(row, 1)
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QTimeEdit
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Etkinliği Düzenle {self.tabs.tabText(tab_index)}")
        layout = QVBoxLayout(dialog)
        label = QLabel("Yeni zamanı seçin:")
        layout.addWidget(label)
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(datetime.strptime(time_item.text(), "%H:%M").time())
        layout.addWidget(time_edit)
        file_label = QLabel("Yeni ses dosyasını seçin:")
        layout.addWidget(file_label)
        file_btn = QPushButton("Dosya Seç")
        file_path = [file_item.text()]
        file_btn.setText(file_item.text().split("/")[-1])
        def choose_file():
            path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seç", "", "Ses Dosyaları (*.mp3 *.wav)")
            if path:
                file_path[0] = path
                file_btn.setText(path.split("/")[-1])
        file_btn.clicked.connect(choose_file)
        layout.addWidget(file_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted and file_path[0]:
            time_item.setText(time_edit.time().toString("HH:mm"))
            file_item.setText(file_path[0])

    def delete_event_tab(self):
        tab_index = self.tabs.currentIndex()
        current_day = self.days_en[tab_index]
        table = self.day_tables[current_day]
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Etkinliği Sil", "Lütfen silmek için bir etkinlik seçin.")
            return
        table.removeRow(row)

    def add_event(self):
        from PyQt5.QtWidgets import QComboBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Alarm Ekle")
        layout = QVBoxLayout(dialog)
        day_label = QLabel("Günü Seçin:")
        layout.addWidget(day_label)
        day_combo = QComboBox()
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        day_combo.addItems(days)
        today_index = datetime.now().weekday()
        day_combo.setCurrentIndex(today_index)
        layout.addWidget(day_combo)
        label = QLabel("Saat Seçin:")
        layout.addWidget(label)
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(datetime.now().time())
        layout.addWidget(time_edit)
        file_label = QLabel("Ses Dosyası Seçin:")
        layout.addWidget(file_label)
        file_btn = QPushButton("Dosya Seç")
        file_path = [""]
        def choose_file():
            path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seçin", "", "Ses Dosyaları (*.mp3 *.wav)")
            if path:
                file_path[0] = path
                file_btn.setText(path.split("/")[-1])
        file_btn.clicked.connect(choose_file)
        layout.addWidget(file_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted and file_path[0]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            day_item = QTableWidgetItem(day_combo.currentText())
            time_item = QTableWidgetItem(time_edit.time().toString("HH:mm"))
            file_item = QTableWidgetItem(file_path[0])
            self.table.setItem(row, 0, day_item)
            self.table.setItem(row, 1, time_item)
            self.table.setItem(row, 2, file_item)

            action_layout = QHBoxLayout()
            btn_edit = QPushButton("Düzenle")
            btn_edit.setStyleSheet("padding: 4px; background-color: #FFC107; border-radius: 4px;")
            btn_edit.clicked.connect(lambda _, r=row: self.edit_event(r))
            btn_delete = QPushButton("Sil")
            btn_delete.setStyleSheet("padding: 4px; background-color: #F44336; color: white; border-radius: 4px;")
            btn_delete.clicked.connect(lambda _, r=row: self.delete_event(r))
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 3, action_widget)

    def edit_event(self, row):
        from PyQt5.QtWidgets import QComboBox
        day_item = self.table.item(row, 0)
        time_item = self.table.item(row, 1)
        file_item = self.table.item(row, 2)
        dialog = QDialog(self)
        dialog.setWindowTitle("Alarm Düzenle")
        layout = QVBoxLayout(dialog)
        day_label = QLabel("Yeni Günü Seçin:")
        layout.addWidget(day_label)
        day_combo = QComboBox()
        day_combo.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        day_combo.setCurrentText(day_item.text())
        layout.addWidget(day_combo)
        label = QLabel("Yeni Saati Seçin:")
        layout.addWidget(label)
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        h, m = map(int, time_item.text().split(":"))
        time_edit.setTime(datetime.strptime(time_item.text(), "%H:%M").time())
        layout.addWidget(time_edit)
        file_label = QLabel("Yeni Ses Dosyası Seçin:")
        layout.addWidget(file_label)
        file_btn = QPushButton("Dosya Seç")
        file_path = [file_item.text()]
        file_btn.setText(file_item.text().split("/")[-1])
        def choose_file():
            path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seçin", "", "Ses Dosyaları (*.mp3 *.wav)")
            if path:
                file_path[0] = path
                file_btn.setText(path.split("/")[-1])
        file_btn.clicked.connect(choose_file)
        layout.addWidget(file_btn)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted and file_path[0]:
            day_item.setText(day_combo.currentText())
            time_item.setText(time_edit.time().toString("HH:mm"))
            file_item.setText(file_path[0])

    def delete_event(self, row):
        self.table.removeRow(row)

    def load_schedule(self):
        path, _ = QFileDialog.getOpenFileName(self, "Zaman Düzeni Yükle", "", "JSON Dosyası (*.json)")
        if path:
            with open(path, "r") as f:
                self.schedule = json.load(f)
            self.table.setRowCount(0)
            for event in self.schedule:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(event.get("day", "Pazartesi")))
                self.table.setItem(row, 1, QTableWidgetItem(event["time"]))
                self.table.setItem(row, 2, QTableWidgetItem(event["file"]))
                action_layout = QHBoxLayout()
                btn_edit = QPushButton("Düzenle")
                btn_edit.setStyleSheet("padding: 4px; background-color: #FFC107; border-radius: 4px;")
                btn_edit.clicked.connect(lambda _, r=row: self.edit_event(r))
                btn_delete = QPushButton("Sil")
                btn_delete.setStyleSheet("padding: 4px; background-color: #F44336; color: white; border-radius: 4px;")
                btn_delete.clicked.connect(lambda _, r=row: self.delete_event(r))
                action_layout.addWidget(btn_edit)
                action_layout.addWidget(btn_delete)
                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.table.setCellWidget(row, 3, action_widget)

    def save_schedule(self):
        schedule = []
        for row in range(self.table.rowCount()):
            day_item = self.table.item(row, 0)
            time_item = self.table.item(row, 1)
            file_item = self.table.item(row, 2)
            if day_item and time_item and file_item:
                schedule.append({"day": day_item.text(), "time": time_item.text(), "file": file_item.text()})
        path, _ = QFileDialog.getSaveFileName(self, "Zaman Düzeni Kaydet", "", "JSON Dosyası (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(schedule, f, indent=2)
            QMessageBox.information(self, "Kaydedildi", "Zaman düzeni başarıyla kaydedildi!")

    def ring_now(self, file_path=None):
        try:
            if not file_path:
                current_day = self.get_current_day()[0]
                table = self.day_tables.get(current_day)
                if table:
                    row = table.currentRow()
                    if row >= 0:
                        file_path = table.item(row, 1).text()
                    elif table.rowCount() > 0:
                        file_path = table.item(0, 1).text()
            if not file_path or not isinstance(file_path, str) or not file_path.strip():
                QMessageBox.warning(self, "Hata", "Geçersiz ses dosyası yolu.!")
                self.player_label.setText("Oynatılan Dosya: Belirli Değil.")
                return
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.current_music = file_path
            if file_path:
                self.player_label.setText(f"Oynatılan Dosya: {file_path.split('/')[-1]}")
            else:
                self.player_label.setText("Oynatılan Dosya: Belirli Değil")
            self.slider.setValue(0)
            self.slider_timer.start(500)
        except Exception as e:
            QMessageBox.critical(self, "Oynatma Hatası", f"Dosya oynatılamadı:\n{e}")
            self.player_label.setText("Oynatılan Dosya: Belirli Değil")
            self.slider.setValue(0)
            self.slider_timer.stop()

    def get_current_day(self):
        try:
            locale.setlocale(locale.LC_TIME, 'C')
        except:
            pass
        day_en = datetime.now().strftime('%A')
        day_tr = self.days_tr[datetime.now().weekday()]
        return day_en, day_tr

    def scheduler_loop(self):
        while self.running:
            now = datetime.now()
            day_en, day_tr = self.get_current_day()
            current_day = day_en if day_en in self.day_tables else day_tr
            if current_day not in self.day_tables:
                today_index = now.weekday()
                current_day = self.days_en[today_index]
            table = self.day_tables.get(current_day)
            if not table:
                time.sleep(1)
                continue
            current_time = now.strftime("%H:%M")
            for row in range(table.rowCount()):
                time_item = table.item(row, 0)
                file_item = table.item(row, 1)
                if not time_item or not file_item:
                    continue
                time_str = time_item.text()
                file_path = file_item.text()

                if now.strftime('%H:%M') == time_str:
                    self.ring_now(file_path)
                    time.sleep(60)
            time.sleep(1)

    def update_datetime(self):
        now = datetime.now()
        self.datetime_label.setText(f"Şimdi: {now.strftime('%A, %d %B %Y %H:%M:%S')}")

    def update_next_alarm(self):
        now = datetime.now()
        next_alarm = None
        for i, (day_en, day_tr) in enumerate(zip(self.days_en, self.days_tr)):
            table = self.day_tables.get(day_en) or self.day_tables.get(day_tr)
            if not table:
                continue
            for row in range(table.rowCount()):
                time_item = table.item(row, 0)
                if not time_item:
                    continue
                time_str = time_item.text()
                alarm_day = i
                alarm_time = datetime.strptime(time_str, "%H:%M").time()
                days_ahead = (alarm_day - now.weekday() + 7) % 7
                alarm_date = now.date() if days_ahead == 0 and alarm_time > now.time() else now.date() + timedelta(days=days_ahead)
                alarm_dt = datetime.combine(alarm_date, alarm_time)
                if alarm_dt > now and (next_alarm is None or alarm_dt < next_alarm):
                    next_alarm = alarm_dt
        if next_alarm:
            self.next_alarm_label.setText(f"Sonraki Alarm: {next_alarm.strftime('%A, %d %B %Y %H:%M')}")
        else:
            self.next_alarm_label.setText("Sıradaki Alarm: Yok")

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def player_play(self):
        try:
            now = datetime.now()
            next_alarm = None
            next_file = None
            for i, (day_en, day_tr) in enumerate(zip(self.days_en, self.days_tr)):
                table = self.day_tables.get(day_en) or self.day_tables.get(day_tr)
                if not table:
                    continue
                for row in range(table.rowCount()):
                    time_item = table.item(row, 0)
                    file_item = table.item(row, 1)
                    if not time_item or not file_item:
                        continue
                    time_str = time_item.text()
                    alarm_day = i
                    alarm_time = datetime.strptime(time_str, "%H:%M").time()
                    days_ahead = (alarm_day - now.weekday() + 7) % 7
                    alarm_date = now.date() if days_ahead == 0 and alarm_time > now.time() else now.date() + timedelta(days=days_ahead)
                    alarm_dt = datetime.combine(alarm_date, alarm_time)
                    if alarm_dt > now and (next_alarm is None or alarm_dt < next_alarm):
                        next_alarm = alarm_dt
                        next_file = file_item.text()
            if next_file:
                self.current_music = next_file
                pygame.mixer.music.load(self.current_music)
                pygame.mixer.music.play()
                import os
                self.player_label.setText(f"Oynatılan Dosya: {os.path.basename(self.current_music)}")
                self.slider.setValue(0)
                self.slider_timer.start(500)
            elif self.current_music:
                pygame.mixer.music.load(self.current_music)
                pygame.mixer.music.play()
                import os
                self.player_label.setText(f"Oynatılan Dosya: {os.path.basename(self.current_music)}")
                self.slider.setValue(0)
                self.slider_timer.start(500)
            else:

                import os
                muzik_folder = os.path.join(os.path.dirname(__file__), 'muzik')
                files = [f for f in os.listdir(muzik_folder) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
                if files:
                    file_path = os.path.join(muzik_folder, files[0])
                    self.current_music = file_path
                    pygame.mixer.music.load(self.current_music)
                    pygame.mixer.music.play()
                    import os
                    self.player_label.setText(f"Oynatılan Dosya: {os.path.basename(self.current_music)}")
                    self.slider.setValue(0)
                    self.slider_timer.start(500)
                else:
                    QMessageBox.warning(self, "Oynatıcı", "Müzik 'muzik' klasöründe bulunamadı.")
        except Exception as e:
            QMessageBox.critical(self, "Oynatıcı Hatası", f"Oynatma başarısız oldu:\n{e}")

    def player_pause(self):
        try:
            pygame.mixer.music.pause()
            if self.current_music:
                import os
                self.player_label.setText(f"Duraklatıldı: {os.path.basename(self.current_music)}")
            else:
                self.player_label.setText("Duraklatıldı: Belirli Değil")
            self.slider_timer.stop()
        except Exception as e:
            QMessageBox.critical(self, "Oynatıcı Hatası", f"Duraklatma başarısız oldu:\n{e}")

    def player_stop(self):
        try:
            pygame.mixer.music.stop()
            self.player_label.setText("Oynatılan Dosya: Belirli Değil")
            self.slider.setValue(0)
            self.slider_timer.stop()
        except Exception as e:
            QMessageBox.critical(self, "Oynatıcı Hatası", f"Duraklatma başarısız oldu:\n{e}")

    def update_slider(self):
        if self.current_music:
            try:
                pos = pygame.mixer.music.get_pos() // 1000
                self.slider.setValue(min(pos, 100))
            except Exception as e:
                pass

    def seek_music(self, value):
        if self.current_music:
            try:
                pygame.mixer.music.rewind()
                pygame.mixer.music.set_pos(value)
            except Exception as e:
                pass

    def get_all_schedules(self):
        data = {}
        for day in self.days_en:
            table = self.day_tables[day]
            events = []
            for row in range(table.rowCount()):
                time_item = table.item(row, 0)
                file_item = table.item(row, 1)
                if time_item and file_item:
                    events.append({
                        "time": time_item.text(),
                        "file": file_item.text()
                    })
            data[day] = events
        return data

    def set_all_schedules(self, data):
        for day, events in data.items():
            table = self.day_tables.get(day)
            if not table:
                continue
            table.setRowCount(0)
            for i, event in enumerate(events):
                table.insertRow(i)
                time_item = QTableWidgetItem(event["time"])
                file_item = QTableWidgetItem(event["file"])
                table.setItem(i, 0, time_item)
                table.setItem(i, 1, file_item)

    def save_schedules(self):
        import os
        kayit_folder = os.path.join(os.path.dirname(__file__), 'kayit')
        if not os.path.exists(kayit_folder):
            os.makedirs(kayit_folder)
        path = os.path.join(kayit_folder, '1.json')
        data = self.get_all_schedules()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Kaydet", f"Zaman çizelgesi kaydedildi: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Kaydet", f"Kaydedilemedi: {e}")

    def import_schedules(self):
        import os
        kayit_folder = os.path.join(os.path.dirname(__file__), 'kayit')
        if not os.path.exists(kayit_folder):
            os.makedirs(kayit_folder)
        path, _ = QFileDialog.getOpenFileName(self, "İçe Aktar", kayit_folder, "JSON Dosyası (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.set_all_schedules(data)
            QMessageBox.information(self, "İçe Aktar", "Zaman çizelgesi yüklendi.")
            self.update_next_alarm()

    def export_schedules(self):
        path, _ = QFileDialog.getSaveFileName(self, "Dışa Aktar", "", "JSON Dosyası (*.json)")
        print(f"Dışa Aktarma Yolu: {path}")
        if path:
            if not path.lower().endswith('.json'):
                path += '.json'
            print(f"Son Dışa Aktarma Yolu: {path}")
            data = self.get_all_schedules()
            print(f"Dışarı Aktarılacak veri: {data}")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("JSON dosyası başarıyla dışa aktarıldı.")
                QMessageBox.information(self, "Dışa Aktar", f"Zaman çizelgesi dışa aktarıldı: {path}")
            except Exception as e:
                print(f"JSON dışa aktarma hatası: {e}")
                QMessageBox.critical(self, "Dışa Aktar", f"Dışa aktarılamadı: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BellApp()
    window.show()
    sys.exit(app.exec_())
