import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QPushButton,
    QHBoxLayout, QLabel
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class ErrorCorrectionPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Анализ помехоустойчивости кодов')
        self.setGeometry(200, 200, 1200, 700)

        # Layouts
        main_layout = QHBoxLayout()
        control_layout = QVBoxLayout()
        graph_layout = QVBoxLayout()

        # Graph
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # Checkboxes for codes
        self.bch_checkbox = QCheckBox('Код БЧХ')
        self.rs_checkbox = QCheckBox('Код Рида-Соломона')
        self.golay_checkbox = QCheckBox('Троичный код Голея')
        self.hamming_checkbox = QCheckBox('Код Рида-Соломона')
        self.ldpc_checkbox = QCheckBox('Код Рида-Соломона')
        self.conv_checkbox = QCheckBox('Троичный код Голея')  # Новый чекбокс
        self.turbo_checkbox = QCheckBox('Код БЧХ')         # Новый чекбокс
        self.msk_checkbox = QCheckBox('КИМ-ЧМ-ФМ')

        # Button
        self.calc_button = QPushButton('Построить график')
        self.calc_button.clicked.connect(self.plot_graph)

        # Add widgets
        control_layout.addWidget(QLabel('Выберите коды:'))
        control_layout.addWidget(self.rs_checkbox)
        control_layout.addWidget(self.hamming_checkbox)
        control_layout.addWidget(self.ldpc_checkbox)
        control_layout.addWidget(self.golay_checkbox)
        control_layout.addWidget(self.conv_checkbox)  # Новый чекбокс между Голея и БЧХ
        control_layout.addWidget(self.bch_checkbox)
        control_layout.addWidget(self.turbo_checkbox)  # Новый чекбокс после БЧХ
        control_layout.addWidget(self.msk_checkbox)
        control_layout.addWidget(self.calc_button)
        control_layout.addStretch()

        graph_layout.addWidget(self.canvas)
        main_layout.addLayout(control_layout, 1)
        main_layout.addLayout(graph_layout, 3)
        self.setLayout(main_layout)

    def calculate_curve(self, target_snr, snr_db, msk=False):
        """Рассчитывает кривую, проходящую через 10^-9 при target_snr"""
        snr_linear = 10 ** (snr_db / 10)
        
        # Базовый BER для MSK или обычной модуляции
        if msk:
            ber = 0.5 * erfc(np.sqrt(snr_linear))
        else:
            ber = 0.5 * erfc(np.sqrt(0.5 * snr_linear))
        
        # Находим коэффициент смещения для достижения 10^-9 при target_snr
        target_ber = 1e-9
        target_snr_linear = 10 ** (target_snr / 10)
        if msk:
            required_ber = 0.5 * erfc(np.sqrt(target_snr_linear))
        else:
            required_ber = 0.5 * erfc(np.sqrt(0.5 * target_snr_linear))
        
        # Коэффициент коррекции
        correction = np.log10(target_ber) / np.log10(required_ber)
        
        # Применяем коррекцию
        corrected_ber = np.power(ber, correction)
        
        return corrected_ber

    def plot_graph(self):
        self.ax.clear()
        snr_db = np.linspace(0, 20, 200)
        
        # Базовая кривая без кодирования (сдвинута дальше всех)
        base_curve = self.calculate_curve(22.0, snr_db, self.msk_checkbox.isChecked())
        self.ax.plot(snr_db, base_curve, 'k--', label='Без кодирования')

        # Кривые с кодированием
        if self.rs_checkbox.isChecked():
            rs_curve = self.calculate_curve(8, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, rs_curve, 'b-', label='Рида-Соломона (24,8)')
            self.ax.axvline(x=8, color='b', linestyle=':', alpha=0.3)

        if self.hamming_checkbox.isChecked():
            hamming_curve = self.calculate_curve(10, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, hamming_curve, 'b-', label='Рида-Соломона (32,26)')
            self.ax.axvline(x=10, color='b', linestyle=':', alpha=0.3)

        if self.ldpc_checkbox.isChecked():
            ldpc_curve = self.calculate_curve(11.5, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, ldpc_curve, 'b-', label='Рида-Соломона (64,48)')
            self.ax.axvline(x=11.5, color='b', linestyle=':', alpha=0.3)

        if self.golay_checkbox.isChecked():
            golay_curve = self.calculate_curve(13, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, golay_curve, 'g-', label='Троичный код Голея (24,12,8)')
            self.ax.axvline(x=13, color='g', linestyle=':', alpha=0.3)

        if self.conv_checkbox.isChecked():  # Новая кривая между Голея и БЧХ
            conv_curve = self.calculate_curve(14, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, conv_curve, 'g-', label='Троичный код Голея (24,13,7)')  # Жёлтая линия
            self.ax.axvline(x=14, color='g', linestyle=':', alpha=0.3)

        if self.bch_checkbox.isChecked():
            bch_curve = self.calculate_curve(15, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, bch_curve, 'r-', label='БЧХ (7,4,1)')
            self.ax.axvline(x=15, color='r', linestyle=':', alpha=0.3)

        if self.turbo_checkbox.isChecked():  # Новая кривая после БЧХ
            turbo_curve = self.calculate_curve(16, snr_db, self.msk_checkbox.isChecked())
            self.ax.plot(snr_db, turbo_curve, 'r-', label='БЧХ (15,4,1)')  # Оранжевая линия
            self.ax.axvline(x=16, color='r', linestyle=':', alpha=0.3)

        # Настройки графика
        self.ax.set_title('Зависимость вероятности ошибки на бит от отношения \n энергии сигнала к спектральной мощности шума')
        self.ax.set_xlabel('Отношение сигнал/шум (дБ)')
        self.ax.set_ylabel('Вероятность ошибки на бит')
        self.ax.set_yscale('log')
        self.ax.set_ylim(1e-12, 1)
        self.ax.set_xlim(0, 20)
        self.ax.grid(True, which='both', linestyle='--')
        
        # Линия 10^-9
        self.ax.axhline(y=1e-9, color='gray', linestyle='--', alpha=0.5)
        self.ax.text(1, 1.5e-9, '10^-9', color='gray')
        
        # Перенос легенды в правый верхний угол
        self.ax.legend(loc='upper right')
        
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ErrorCorrectionPlot()
    ex.show()
    sys.exit(app.exec())