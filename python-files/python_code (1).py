import sys, sqlite3, random, requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QProgressBar, QHBoxLayout, QLineEdit, QMessageBox)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ---------- DÖVİZ KURU ÇEKME ----------
def get_exchange_rates():
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD")
        data = res.json()
        return {"USD": 1, "EUR": data["rates"]["EUR"], "TL": data["rates"]["TRY"]}
    except:
        return {"USD": 1, "EUR": 0.95, "TL": 28.0}  # fallback

    # ---------- VERİ TABANI ----------
    conn = sqlite3.connect("oexetech.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, progress INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, supplier_id INTEGER, unit_cost REAL, currency TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS project_materials (
                    project_id INTEGER, material_id INTEGER)""")
    conn.commit()

    # ---------- ANA UYGULAMA ----------
    class OexeTechApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("OexeTech ERP")
            self.setGeometry(100, 100, 1400, 900)
            self.exchange_rates = get_exchange_rates()
            self.initUI()

            def initUI(self):
                font = QFont("Poppins", 12)
                self.setFont(font)
                main_widget = QWidget()
                main_layout = QVBoxLayout()

                # Başlık
                title = QLabel("OexeTech ERP Dashboard")
                title.setFont(QFont("Poppins", 24))
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                main_layout.addWidget(title)

                # Para birimi seçimi
                currency_layout = QHBoxLayout()
                currency_label = QLabel("Para Birimi:")
                self.currency_combo = QComboBox()
                self.currency_combo.addItems(["USD", "EUR", "TL"])
                currency_layout.addWidget(currency_label)
                currency_layout.addWidget(self.currency_combo)
                main_layout.addLayout(currency_layout)

                # Dashboard Güncelle Butonu
                update_button = QPushButton("Güncelle & Rastgele İlerleme")
                update_button.clicked.connect(self.update_dashboard)
                main_layout.addWidget(update_button)

                # --- Projeler Tablosu ---
                self.table = QTableWidget()
                self.table.setColumnCount(3)
                self.table.setHorizontalHeaderLabels(["Proje Adı", "İlerleme (%)", "Toplam Maliyet"])
                main_layout.addWidget(self.table)

                # --- Proje Ekle ---
                add_layout = QHBoxLayout()
                self.project_input = QLineEdit()
                self.project_input.setPlaceholderText("Yeni Proje Adı")
                add_button = QPushButton("Proje Ekle")
                add_button.clicked.connect(self.add_project)
                add_layout.addWidget(self.project_input)
                add_layout.addWidget(add_button)
                main_layout.addLayout(add_layout)

                # --- Malzeme ve Tedarikçi Ekle ---
                material_layout = QHBoxLayout()
                self.material_input = QLineEdit()
                self.material_input.setPlaceholderText("Yeni Malzeme Adı")
                self.supplier_input = QLineEdit()
                self.supplier_input.setPlaceholderText("Tedarikçi Adı")
                self.cost_input = QLineEdit()
                self.cost_input.setPlaceholderText("Birim Maliyet")
                self.currency_input = QComboBox()
                self.currency_input.addItems(["USD","EUR","TL"])
                add_material_btn = QPushButton("Malzeme Ekle")
                add_material_btn.clicked.connect(self.add_material)
                material_layout.addWidget(self.material_input)
                material_layout.addWidget(self.supplier_input)
                material_layout.addWidget(self.cost_input)
                material_layout.addWidget(self.currency_input)
                material_layout.addWidget(add_material_btn)
                main_layout.addLayout(material_layout)

                # --- Grafik ---
                self.figure = Figure(figsize=(6,4))
                self.canvas = FigureCanvas(self.figure)
                main_layout.addWidget(self.canvas)

                # Tema Renkleri
                palette = QPalette()
                palette.setColor(QPalette.ColorRole.Window, QColor("#373643"))
                palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
                self.setPalette(palette)

                main_widget.setLayout(main_layout)
                self.setCentralWidget(main_widget)
                self.load_projects()
                self.plot_dashboard()

                # ---------- Projeleri Yükle ----------
                def load_projects(self):
                    cursor.execute("SELECT * FROM projects")
                    self.projects = [{"id": r[0], "name": r[1], "progress": r[2]} for r in cursor.fetchall()]
                    self.table.setRowCount(len(self.projects))
                    for row, p in enumerate(self.projects):
                        self.table.setItem(row, 0, QTableWidgetItem(p["name"]))
                        progress = QProgressBar()
                        progress.setValue(p["progress"])
                        self.table.setCellWidget(row, 1, progress)
                        # Toplam maliyet
                        cursor.execute("""SELECT SUM(m.unit_cost * ?) FROM project_materials pm
                              JOIN materials m ON pm.material_id = m.id
                              WHERE pm.project_id=?""", (self.exchange_rates[self.currency_combo.currentText()], p["id"]))
                        total = cursor.fetchone()[0]
                        total = total if total else 0
                        self.table.setItem(row, 2, QTableWidgetItem(f"{total:.2f} {self.currency_combo.currentText()}"))

                        # ---------- Proje Ekle ----------
                        def add_project(self):
                            name = self.project_input.text().strip()
                            if name=="":
                                QMessageBox.warning(self, "Hata","Proje adı boş olamaz!")
                                return
                            cursor.execute("INSERT INTO projects (name, progress) VALUES (?,?)",(name,0))
                            conn.commit()
                            self.project_input.clear()
                            self.load_projects()
                            self.plot_dashboard()

                            # ---------- Malzeme Ekle ----------
                            def add_material(self):
                                m_name = self.material_input.text().strip()
                                s_name = self.supplier_input.text().strip()
                                cost_text = self.cost_input.text().strip()
                                currency = self.currency_input.currentText()
                                if m_name=="" or s_name=="" or cost_text=="":
                                    QMessageBox.warning(self,"Hata","Tüm alanları doldurun!")
                                    return
                                try:
                                    cost = float(cost_text)
                                    except:
                                        QMessageBox.warning(self,"Hata","Birim maliyet sayı olmalı!")
                                        return
                                    # Tedarikçi ekle veya bul
                                    cursor.execute("SELECT id FROM suppliers WHERE name=?",(s_name,))
                                    res = cursor.fetchone()
                                    if res:
                                        supplier_id = res[0]
                                    else:
                                        cursor.execute("INSERT INTO suppliers (name) VALUES (?)",(s_name,))
                                        supplier_id = cursor.lastrowid
                                        cursor.execute("INSERT INTO materials (name,supplier_id,unit_cost,currency) VALUES (?,?,?,?)",
                                                       (m_name,supplier_id,cost,currency))
                                        conn.commit()
                                        self.material_input.clear()
                                        self.supplier_input.clear()
                                        self.cost_input.clear()
                                        self.load_projects()
                                        self.plot_dashboard()

                                        # ---------- Dashboard Güncelle ----------
                                        def update_dashboard(self):
                                            self.exchange_rates = get_exchange_rates()
                                            for p in self.projects:
                                                new_progress = min(100, p["progress"] + random.randint(0,10))
                                                cursor.execute("UPDATE projects SET progress=? WHERE id=?",(new_progress,p["id"]))
                                                conn.commit()
                                                self.load_projects()
                                                self.plot_dashboard()

                                                # ---------- Grafik Çiz ----------
                                                def plot_dashboard(self):
                                                    self.figure.clear()
                                                    ax = self.figure.add_subplot(111)
                                                    names = [p["name"] for p in self.projects]
                                                    progresses = [p["progress"] for p in self.projects]
                                                    ax.bar(names, progresses, color="#ffcc00")
                                                    ax.set_ylabel("İlerleme (%)")
                                                    ax.set_ylim(0,100)
                                                    self.canvas.draw()

                                                    # ---------- Uygulamayı Çalıştır ----------
                                                    if __name__=="__main__":
                                                        app = QApplication(sys.argv)
                                                        window = OexeTechApp()
                                                        window.show()
                                                        sys.exit(app.exec())
