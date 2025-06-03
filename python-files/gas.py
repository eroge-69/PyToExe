import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class GasWellApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Производительность горизонтальной газовой скважины")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.param_selector = QComboBox()
        self.param_selector.addItems(["Толщина пласта H", "Длина ствола Lгс", "Радиус скважины Rc", "Радиус контура Rк", "Анизотропия ν"])
        self.param_selector.currentIndexChanged.connect(self.update_values)
        layout.addWidget(QLabel("Выберите параметр:"))
        layout.addWidget(self.param_selector)

        self.value_selector = QComboBox()
        layout.addWidget(QLabel("Выберите значение:"))
        layout.addWidget(self.value_selector)

        self.calc_button = QPushButton("Рассчитать Qг и построить график")
        self.calc_button.clicked.connect(self.plot_graph)
        layout.addWidget(self.calc_button)

        self.result_label = QLabel("Результат: Qг = ? тыс м³/сутки")
        self.result_label.setFont(QFont('Arial', 14))
        layout.addWidget(self.result_label)

        self.canvas = FigureCanvas(plt.Figure())
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.update_values()

    def update_values(self):
        param = self.param_selector.currentText()
        self.value_selector.clear()
        if param == "Толщина пласта H":
            self.value_selector.addItems(["10", "20", "30", "40", "100"])
        elif param == "Длина ствола Lгс":
            self.value_selector.addItems(["600", "700", "2000"])
        elif param == "Радиус скважины Rc":
            self.value_selector.addItems(["0.1", "0.15", "0.2"])
        elif param == "Радиус контура Rк":
            self.value_selector.addItems(["500", "800", "1800"])
        elif param == "Анизотропия ν":
            self.value_selector.addItems(["0.3", "0.5", "1"])

    def calculate_Q(self, H, Lgs, Rc, Rk, v):
        delta_P = 0.1
        hj = (H / 2) - Rc
        a_vert = 0.0157
        b_vert = 0.00024
        a_star = (a_vert * H * 3.1415926) / (np.log(Rk / Rc))
        b_star = (b_vert * 2 * 3.1415926 * 3.1415926 * H * H) / ((1/Rc)-(1/Rk))
        a_g = (a_star / (Lgs * 2))*((2/(v*hj))*((v*hj)+Rc*(np.log((Rc)/(Rc+(v*hj)))))+((Rk-(v*hj))/(Rk+(v*hj))))
        b_g = (b_star / (8*Lgs*Lgs))*((2/(v*hj))*((np.log((Rc+(v*hj))/Rc))-((v*hj)/(Rc+(v*hj))))+((Rk-(v*hj))/((Rc+(v*hj))**2)))
        Qg = ((-a_g)+((a_g**2)+4*b_g*(delta_P**2))**0.5)/(2*b_g)
        return Qg

    def plot_graph(self):
        param = self.param_selector.currentText()
        value = float(self.value_selector.currentText())

        fixed = {
            'H': 10,
            'Lgs': 600,
            'Rc': 0.1,
            'Rk': 500,
            'v': 0.3
        }

        if param == "Толщина пласта H":
            values = [10, 20, 30, 40, 100]
            fixed['H'] = value
        elif param == "Длина ствола Lгс":
            values = [600, 700, 2000]
            fixed['Lgs'] = value
        elif param == "Радиус скважины Rc":
            values = [0.1, 0.15, 0.2]
            fixed['Rc'] = value
        elif param == "Радиус контура Rк":
            values = [500, 800, 1800]
            fixed['Rk'] = value
        elif param == "Анизотропия ν":
            values = [0.3, 0.5, 1]
            fixed['v'] = value

        Qg_list = []
        for val in values:
            args = dict(fixed)
            key_map = {
                "Толщина пласта H": "H",
                "Длина ствола Lгс": "Lgs",
                "Радиус скважины Rc": "Rc",
                "Радиус контура Rк": "Rk",
                "Анизотропия ν": "v"
            }
            key = key_map[param]
            args[key] = val
            Qg_list.append(self.calculate_Q(**args))

        self.result_label.setText(f"Результат: Qг = {self.calculate_Q(**fixed):.3f} тыс м³/сутки")

        # Очистка холста
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        ax.plot(values, Qg_list, marker='o', color='green')
        ax.set_title(f"Зависимость Qг от {param}")
        ax.set_xlabel(param)
        ax.set_ylabel("Qг, тыс м³/сутки")
        ax.grid(True)
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = GasWellApp()
    mainWin.show()
    sys.exit(app.exec_())
