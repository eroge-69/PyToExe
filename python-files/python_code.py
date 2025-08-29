import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QProgressBar, QHBoxLayout)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import requests
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Döviz kuru çekme ---
def get_exchange_rates():
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD")
        data = res.json()
        return {"USD": 1, "EUR": data["rates"]["EUR"], "TL": data["rates"]["TRY"]}
    except:
        return {"USD": 1, "EUR": 0.95, "TL": 28.0}  # fallback

    # --- Ana Uygulama ---
    class OexeTechApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("OexeTech")
            self.setGeometry(100, 100, 1200, 800)
            self.exchange_rates = get_exchange_rates()
            self.initUI()

            def initUI(self):
                font = QFont("Poppins", 12)
                self.setFont(font)

                # Ana widget
                main_widget = QWidget()
                main_layout = QVBoxLayout()

                # Başlık
                title = QLabel("OexeTech Dashboard")
                title.setFont(QFont("Poppins", 24))
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                main_layout.addWidget(title)

                # Para birimi seçimi
                currency_layout = QHBoxLayout()
                currency_label = QLabel("Tedarik Para Birimi:")
                self.currency_combo = QComboBox()
                self.currency_combo.addItems(["USD", "EUR", "TL"])
                currency_layout.addWidget(currency_label)
                currency_layout.addWidget(self.currency_combo)
                main_layout.addLayout(currency_layout)

                # Maliyetleri Güncelle Butonu
                update_button = QPushButton("Maliyetleri Güncelle")
                update_button.clicked.connect(self.update_costs)
                main_layout.addWidget(update_button)

                # --- Dashboard Tablosu ---
                self.table = QTableWidget()
                self.table.setColumnCount(4)
                self.table.setHorizontalHeaderLabels(["Proje Adı", "İlerleme (%)", "Maliyet (USD)", "Maliyet Seçilen Para"])
                main_layout.addWidget(self.table)

                # Örnek projeler
                self.projects = [
                    {"name": "Proje A", "progress": 25, "cost_usd": 10000},
                    {"name": "Proje B", "progress": 50, "cost_usd": 20000},
                    {"name": "Proje C", "progress": 75, "cost_usd": 15000},
                ]

                self.load_projects()

                # --- Grafik ---
                self.figure = Figure(figsize=(5, 3))
                self.canvas = FigureCanvas(self.figure)
                main_layout.addWidget(self.canvas)
                self.plot_progress()

                # Tema Renkleri
                palette = QPalette()
                palette.setColor(QPalette.ColorRole.Window, QColor("#373643"))
                palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
                self.setPalette(palette)

                main_widget.setLayout(main_layout)
                self.setCentralWidget(main_widget)

                def load_projects(self):
                    self.table.setRowCount(len(self.projects))
                    for row, project in enumerate(self.projects):
                        self.table.setItem(row, 0, QTableWidgetItem(project["name"]))
                        progress = QProgressBar()
                        progress.setValue(project["progress"])
                        self.table.setCellWidget(row, 1, progress)
                        self.table.setItem(row, 2, QTableWidgetItem(f'{project["cost_usd"]:.2f}'))
                        # Maliyet Seçilen Para
                        selected_currency = self.currency_combo.currentText()
                        converted = project["cost_usd"] * self.exchange_rates[selected_currency]
                        self.table.setItem(row, 3, QTableWidgetItem(f'{converted:.2f} {selected_currency}'))

                        def update_costs(self):
                            # Döviz güncelle
                            self.exchange_rates = get_exchange_rates()
                            # Örnek: rastgele ilerleme artır
                            for p in self.projects:
                                p["progress"] = min(100, p["progress"] + random.randint(0, 10))
                                self.load_projects()
                                self.plot_progress()

                                def plot_progress(self):
                                    self.figure.clear()
                                    ax = self.figure.add_subplot(111)
                                    names = [p["name"] for p in self.projects]
                                    progresses = [p["progress"] for p in self.projects]
                                    ax.bar(names, progresses, color="#ffcc00")
                                    ax.set_ylabel("İlerleme (%)")
                                    ax.set_ylim(0, 100)
                                    self.canvas.draw()

                                    if __name__ == "__main__":
                                        app = QApplication(sys.argv)
                                        window = OexeTechApp()
                                        window.show()
                                        sys.exit(app.exec())
