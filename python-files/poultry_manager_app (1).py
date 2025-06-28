# Poultry Management System (Windows 11 Compatible - PyQt6 Version)
# Modules: Flock, Feed, Egg Production (UI using PyQt6)

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                             QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
                             QMessageBox)
import csv

class FlockTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.flock_name = QLineEdit()
        self.breed = QLineEdit()
        self.arrival_date = QLineEdit()

        layout.addRow("Flock Name", self.flock_name)
        layout.addRow("Breed", self.breed)
        layout.addRow("Arrival Date", self.arrival_date)

        save_button = QPushButton("Save Flock")
        save_button.clicked.connect(self.save_flock)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_flock(self):
        data = [self.flock_name.text(), self.breed.text(), self.arrival_date.text()]
        with open("flocks.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        QMessageBox.information(self, "Saved", "Flock saved successfully")

class FeedTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.feed_date = QLineEdit()
        self.feed_qty = QLineEdit()

        layout.addRow("Date", self.feed_date)
        layout.addRow("Feed Quantity (kg)", self.feed_qty)

        save_button = QPushButton("Save Feed Entry")
        save_button.clicked.connect(self.save_feed)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_feed(self):
        data = [self.feed_date.text(), self.feed_qty.text()]
        with open("feed.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        QMessageBox.information(self, "Saved", "Feed record saved successfully")

class EggTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.egg_date = QLineEdit()
        self.egg_count = QLineEdit()

        layout.addRow("Date", self.egg_date)
        layout.addRow("Eggs Collected", self.egg_count)

        save_button = QPushButton("Save Egg Entry")
        save_button.clicked.connect(self.save_eggs)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_eggs(self):
        data = [self.egg_date.text(), self.egg_count.text()]
        with open("eggs.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        QMessageBox.information(self, "Saved", "Egg record saved successfully")

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poultry Management System")
        self.setGeometry(100, 100, 600, 400)

        tabs = QTabWidget()
        tabs.addTab(FlockTab(), "Flock Management")
        tabs.addTab(FeedTab(), "Feed Tracking")
        tabs.addTab(EggTab(), "Egg Production")

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
