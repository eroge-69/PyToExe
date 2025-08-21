import sys
import os
import sys
from pathlib import Path

# Указываем правильный путь к плагинам Qt вручную
python_dir = Path(sys.executable).parent
qt_plugins_path = python_dir / "Lib" / "site-packages" / "PyQt5" / "Qt5" / "plugins"

if qt_plugins_path.exists():
    os.environ['QT_PLUGIN_PATH'] = str(qt_plugins_path)
else:
    # Альтернативный путь поиска
    for path in sys.path:
        if "site-packages" in path:
            alt_path = Path(path) / "PyQt5" / "Qt5" / "plugins"
            if alt_path.exists():
                os.environ['QT_PLUGIN_PATH'] = str(alt_path)
                break

# Теперь импортируем PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Словарь с кодами и значениями резисторов
resistor_codes = {
    # Омы
    "R10": 0.1, "1R0": 1.0, "100": 10.0, "101": 100.0,
    "R11": 0.11, "1R1": 1.1, "110": 11.0, "111": 110.0,
    "R12": 0.12, "1R2": 1.2, "120": 12.0, "121": 120.0,
    "R13": 0.13, "1R3": 1.3, "130": 13.0, "131": 130.0,
    "R15": 0.15, "1R5": 1.5, "150": 15.0, "151": 150.0,
    "R16": 0.16, "1R6": 1.6, "160": 16.0, "161": 160.0,
    "R18": 0.18, "1R8": 1.8, "180": 18.0, "181": 180.0,
    "R20": 0.2, "2R0": 2.0, "200": 20.0, "201": 200.0,
    "R22": 0.22, "2R2": 2.2, "220": 22.0, "221": 220.0,
    "R24": 0.24, "2R4": 2.4, "240": 24.0, "241": 240.0,
    "R27": 0.27, "2R7": 2.7, "270": 27.0, "271": 270.0,
    "R30": 0.3, "3R0": 3.0, "300": 30.0, "301": 300.0,
    "R33": 0.33, "3R3": 3.3, "330": 33.0, "331": 330.0,
    "R36": 0.36, "3R6": 3.6, "360": 36.0, "361": 360.0,
    "R39": 0.39, "3R9": 3.9, "390": 39.0, "391": 390.0,
    "R43": 0.43, "4R3": 4.3, "430": 43.0, "431": 430.0,
    "R47": 0.47, "4R7": 4.7, "470": 47.0, "471": 470.0,
    "R51": 0.51, "5R1": 5.1, "510": 51.0, "511": 510.0,
    "R56": 0.56, "5R6": 5.6, "560": 56.0, "561": 560.0,
    "R62": 0.62, "6R2": 6.2, "620": 62.0, "621": 620.0,
    "R68": 0.68, "6R8": 6.8, "680": 68.0, "681": 680.0,
    "R75": 0.75, "7R5": 7.5, "750": 75.0, "751": 750.0,
    "R82": 0.82, "8R2": 8.2, "820": 82.0, "821": 820.0,
    "R91": 0.91, "9R1": 9.1, "910": 91.0, "911": 910.0,
    
    # Килоомы и Мегаомы
    "102": 1000.0, "103": 10000.0, "104": 100000.0, "105": 1000000.0,
    "112": 1100.0, "113": 11000.0, "114": 110000.0, "115": 1100000.0,
    "122": 1200.0, "123": 12000.0, "124": 120000.0, "125": 1200000.0,
    "132": 1300.0, "133": 13000.0, "134": 130000.0, "135": 1300000.0,
    "152": 1500.0, "153": 15000.0, "154": 150000.0, "155": 1500000.0,
    "162": 1600.0, "163": 16000.0, "164": 160000.0, "165": 1600000.0,
    "182": 1800.0, "183": 18000.0, "184": 180000.0, "185": 1800000.0,
    "202": 2000.0, "203": 20000.0, "204": 200000.0, "205": 2000000.0,
    "222": 2200.0, "223": 22000.0, "224": 220000.0, "225": 2200000.0,
    "242": 2400.0, "243": 24000.0, "244": 240000.0, "245": 2400000.0,
    "272": 2700.0, "273": 27000.0, "274": 270000.0, "275": 2700000.0,
    "302": 3000.0, "303": 30000.0, "304": 300000.0, "305": 3000000.0,
    "332": 3300.0, "333": 33000.0, "334": 330000.0, "335": 3300000.0,
    "362": 3600.0, "363": 36000.0, "364": 360000.0, "365": 3600000.0,
    "392": 3900.0, "393": 39000.0, "394": 390000.0, "395": 3900000.0,
    "432": 4300.0, "433": 43000.0, "434": 430000.0, "435": 4300000.0,
    "472": 4700.0, "473": 47000.0, "474": 470000.0, "475": 4700000.0,
    "512": 5100.0, "513": 51000.0, "514": 510000.0, "515": 5100000.0,
    "562": 5600.0, "563": 56000.0, "564": 560000.0, "565": 5600000.0,
    "622": 6200.0, "623": 62000.0, "624": 620000.0, "625": 6200000.0,
    "682": 6800.0, "683": 68000.0, "684": 680000.0, "685": 6800000.0,
    "752": 7500.0, "753": 75000.0, "754": 750000.0, "755": 7500000.0,
    "822": 8200.0, "823": 82000.0, "824": 820000.0, "815": 8200000.0,
    "912": 9100.0, "913": 91000.0, "914": 910000.0, "915": 9100000.0
}

class ResistorCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Калькулятор АЦМщика. Автор Ильин")
        self.setFixedSize(400, 350)
        
        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Поля ввода
        self.create_input_fields(main_layout)
        
        # Кнопка расчета
        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.calculate_button.setFixedHeight(35)
        self.calculate_button.clicked.connect(self.calculate)
        main_layout.addWidget(self.calculate_button)
        
        # Результат
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 9))
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        main_layout.addWidget(self.result_label)
        
    def create_input_fields(self, layout):
        # Размеры для выравнивания
        label_width = 100
        field_width = 200
        field_height = 30
        
        # Паспортное значение
        pas_layout = QHBoxLayout()
        pas_label = QLabel("Паспорт:")
        pas_label.setFixedWidth(label_width)
        pas_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pas_entry = QLineEdit()
        self.pas_entry.setFixedSize(field_width, field_height)
        pas_layout.addWidget(pas_label)
        pas_layout.addWidget(self.pas_entry)
        layout.addLayout(pas_layout)
        
        # Датчик
        dat_layout = QHBoxLayout()
        dat_label = QLabel("Датчик:")
        dat_label.setFixedWidth(label_width)
        dat_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.dat_combobox = QComboBox()
        self.dat_combobox.setFixedSize(field_width, field_height)
        self.dat_combobox.addItems(["200", "250", "400", "600", "800", "1000", "1500", "2000"])
        dat_layout.addWidget(dat_label)
        dat_layout.addWidget(self.dat_combobox)
        layout.addLayout(dat_layout)
        
        # Прибор
        pr_layout = QHBoxLayout()
        pr_label = QLabel("Прибор:")
        pr_label.setFixedWidth(label_width)
        pr_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.pr_combobox = QComboBox()
        self.pr_combobox.setFixedSize(field_width, field_height)
        self.pr_combobox.addItems(["200", "250", "400", "600", "800", "1000", "1500", "2000"])
        pr_layout.addWidget(pr_label)
        pr_layout.addWidget(self.pr_combobox)
        layout.addLayout(pr_layout)
        
        # Тип АЦМ
        acm_layout = QHBoxLayout()
        acm_label = QLabel("Тип АЦМ:")
        acm_label.setFixedWidth(label_width)
        acm_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.acm_combobox = QComboBox()
        self.acm_combobox.setFixedSize(field_width, field_height)
        acm_types = [
            "АЦМ-6", "АЦМ-7", "АЦМ-6/20", "АЦМ-7/20", "АЦМ-6УИТ",
            "АЦМ-10(204-304)", "АЦМ-10(154-274)", "АЦМ-8.3", "АЦМ-9.3",
            "АЦМ-8.2", "АЦМ-8У", "АЦМ-9.2", "АЦМ-8РТ", "АЦМ-8М(МС)", "АЦМ-8М(К)"
        ]
        self.acm_combobox.addItems(acm_types)
        acm_layout.addWidget(acm_label)
        acm_layout.addWidget(self.acm_combobox)
        layout.addLayout(acm_layout)
    
    def calculate_x(self, pas, dat, pr):
        return pr * (pas / dat)
    
    def calculate_r_acm(self, acm_type, x, pas):
        formulas = {
            "АЦМ-6": lambda x: (x / 331) * 3.9*1000,
            "АЦМ-7": lambda x: (x / 175) * 3.3*1000,
            "АЦМ-6/20": lambda x: (x / 148) * 2*1000,
            "АЦМ-7/20": lambda x: (x / 200) * 3.6*1000,
            "АЦМ-6УИТ": lambda x: (x / 364) * 4.7*1000,
            "АЦМ-10(204-304)": lambda x: (x / 162) * 9.1*1000,
            "АЦМ-10(154-274)": lambda x: (x / 162) * 7.5*1000,
            "АЦМ-8.3": lambda x: (x / 146) * 15*1000,
            "АЦМ-9.3": lambda x: (x / 241) * 36*1000,
            "АЦМ-8.2": lambda x: (x / 136) * 9.1*1000,
            "АЦМ-8У": lambda x: (x / 325) * 25*1000,
            "АЦМ-9.2": lambda x: (x / 211) * 22*1000,
            "АЦМ-8РТ": lambda x: (x / 148) * 9.1*1000,
            "АЦМ-8М(МС)": lambda pas: pas * 0.022*1000,
            "АЦМ-8М(К)": lambda pas: pas * 0.064*1000
        }
        
        if acm_type in ["АЦМ-8М(МС)", "АЦМ-8М(К)"]:
            return formulas[acm_type](pas)
        else:
            return formulas[acm_type](x)
    
    def find_nearest_resistor(self, target_r):
        nearest_code = None
        nearest_value = float('inf')
        
        for code, value in resistor_codes.items():
            if value >= target_r and value < nearest_value:
                nearest_value = value
                nearest_code = code
        
        return nearest_code, nearest_value
    
    def format_resistance(self, value):
        if value >= 1000000:
            return f"{value/1000000:.4f} МОм"
        elif value >= 1000:
            return f"{value/1000:.4f} кОм"
        else:
            return f"{value:.4f} Ом"
    
    def calculate(self):
        try:
            # Получаем значения из полей ввода
            pas = float(self.pas_entry.text())
            dat = int(self.dat_combobox.currentText())
            pr = int(self.pr_combobox.currentText())
            acm_type = self.acm_combobox.currentText()
            
            # Расчет
            x = self.calculate_x(pas, dat, pr)
            r_calculated = self.calculate_r_acm(acm_type, x, pas)
            
            # Находим ближайший резистор
            resistor_code, resistor_value = self.find_nearest_resistor(r_calculated)
            
            # Форматируем результат
            result_text = f"<b>Расчетное сопротивление:</b> {self.format_resistance(r_calculated)}<br>"
            result_text += f"<b>Ближайший резистор:</b> {resistor_code} ({self.format_resistance(resistor_value)})"
            
            self.result_label.setText(result_text)
            
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, введите корректные числовые значения")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    calculator = ResistorCalculator()
    calculator.show()
    sys.exit(app.exec_())
