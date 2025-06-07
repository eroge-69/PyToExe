import sys
import time
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QListWidget, QLabel, QSpinBox, 
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from plyer import notification

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akıllı Görev Yöneticisi")
        self.setGeometry(100, 100, 600, 600)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Görev ekleme bölümü
        task_layout = QHBoxLayout()
        self.task_entry = QLineEdit()
        self.task_entry.setPlaceholderText("Yeni görev ekle...")
        self.task_entry.returnPressed.connect(self.add_task)
        task_layout.addWidget(self.task_entry)
        
        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.add_task)
        task_layout.addWidget(self.add_button)
        main_layout.addLayout(task_layout)
        
        # Görev listesi
        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)
        
        # Kontrol butonları
        control_layout = QHBoxLayout()
        self.delete_button = QPushButton("Sil")
        self.delete_button.clicked.connect(self.delete_task)
        control_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Tümünü Temizle")
        self.clear_button.clicked.connect(self.clear_tasks)
        control_layout.addWidget(self.clear_button)
        main_layout.addLayout(control_layout)
        
        # Zamanlayıcı bölümü
        timer_group = QGroupBox("Zamanlayıcı")
        timer_layout = QVBoxLayout()
        
        # Süre seçimi
        time_input_layout = QHBoxLayout()
        time_input_layout.addWidget(QLabel("Saat:"))
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        time_input_layout.addWidget(self.hour_spin)
        
        time_input_layout.addWidget(QLabel("Dakika:"))
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 59)
        time_input_layout.addWidget(self.min_spin)
        
        time_input_layout.addWidget(QLabel("Saniye:"))
        self.sec_spin = QSpinBox()
        self.sec_spin.setRange(0, 59)
        time_input_layout.addWidget(self.sec_spin)
        timer_layout.addLayout(time_input_layout)
        
        # Kontrol butonları
        timer_btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Başlat")
        self.start_btn.clicked.connect(self.start_timer)
        timer_btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.setEnabled(False)
        timer_btn_layout.addWidget(self.stop_btn)
        timer_layout.addLayout(timer_btn_layout)
        
        # Geri sayım gösterge
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4f6df5;")
        timer_layout.addWidget(self.time_label)
        
        timer_group.setLayout(timer_layout)
        main_layout.addWidget(timer_group)
        
        # Durum çubuğu
        self.status_bar = self.statusBar()
        
        # Değişkenler
        self.tasks = []
        self.timer_running = False
        self.remaining_time = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.load_tasks()
    
    def add_task(self):
        task = self.task_entry.text().strip()
        if task:
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
            task_with_time = f"{task} (Eklendi: {timestamp})"
            self.tasks.append(task_with_time)
            self.task_list.addItem(task_with_time)
            self.task_entry.clear()
            self.save_tasks()
            self.status_bar.showMessage(f"Görev eklendi: {task}")
        else:
            QMessageBox.warning(self, "Uyarı", "Görev alanı boş olamaz!")
    
    def delete_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            task = self.task_list.takeItem(selected).text()
            self.tasks.pop(selected)
            self.save_tasks()
            self.status_bar.showMessage(f"Görev silindi: {task.split(' (')[0]}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir görev seçin!")
    
    def clear_tasks(self):
        if QMessageBox.question(self, "Onay", "Tüm görevler silinsin mi?") == QMessageBox.Yes:
            self.task_list.clear()
            self.tasks = []
            self.save_tasks()
            self.status_bar.showMessage("Tüm görevler temizlendi")
    
    def save_tasks(self):
        with open("tasks.txt", "w") as f:
            for task in self.tasks:
                f.write(f"{task}\n")
    
    def load_tasks(self):
        try:
            with open("tasks.txt", "r") as f:
                self.tasks = [line.strip() for line in f.readlines()]
                self.task_list.addItems(self.tasks)
        except FileNotFoundError:
            pass
    
    def start_timer(self):
        if self.timer_running:
            return
            
        hours = self.hour_spin.value()
        minutes = self.min_spin.value()
        seconds = self.sec_spin.value()
        self.remaining_time = hours * 3600 + minutes * 60 + seconds
        
        if self.remaining_time <= 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir süre girin!")
            return
            
        self.timer_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.showMessage("Zamanlayıcı başladı...")
        
        self.update_timer_display()
        self.timer.start(1000)  # 1 saniyede bir güncelle
    
    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_display()
        else:
            self.timer_complete()
    
    def update_timer_display(self):
        hours, remainder = divmod(self.remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def timer_complete(self):
        self.timer.stop()
        self.timer_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Bildirim gönder
        notification.notify(
            title="Zaman Doldu!",
            message="Zamanlayıcınız sona erdi",
            app_name="Görev Yöneticisi",
            timeout=10
        )
        
        self.status_bar.showMessage("Zamanlayıcı tamamlandı!")
        QMessageBox.information(self, "Tamamlandı", "Zamanlayıcı sona erdi!")
    
    def stop_timer(self):
        self.timer.stop()
        self.timer_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_bar.showMessage("Zamanlayıcı durduruldu")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())