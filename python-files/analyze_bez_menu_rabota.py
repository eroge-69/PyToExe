import sys
import numpy as np
import adi
import time
from scipy.signal import (firwin, lfilter, kaiserord)
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

##############################################################################
# Функция проектирования КИХ-фильтра
##############################################################################
def design_filter(sample_rate, cutoff_hz=400e3):
    """
    Проектирует КИХ-фильтр низких частот с использованием окна Кайзера.
    - sample_rate: частота дискретизации в Гц
    - cutoff_hz: частота среза в Гц
    """
    nyq_rate = sample_rate / 2.0
    width = 10e3 / nyq_rate
    ripple_db = 180
    N_filt, beta_filt = kaiserord(ripple_db, width)
    b_filt = firwin(N_filt, cutoff_hz / nyq_rate, window=('kaiser', beta_filt))
    return b_filt

##############################################################################
# Главное окно для GUI
##############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDR Frequency Sweep (400-6000 МГц)")
        self.setGeometry(100, 100, 1200, 600)

        # Параметры SDR
        self.sample_rate = 1.0e6
        self.rf_bw = 1.0e6
        self.cutoff_hz = 400e3

        # Параметры сканирования (400-6000 МГц)
        self.sweep_start = 400e6
        self.sweep_stop = 6000e6
        self.sweep_steps = 2000

        # Создание и настройка SDR
        self.sdr = adi.Pluto(uri='ip:192.168.2.1')#ad9361
        self.sdr.sample_rate = int(self.sample_rate)
        self.sdr.rx_lo = int(2.25e9)
        self.sdr.rx_rf_bandwidth = int(self.rf_bw)
        self.sdr.rx_buffer_size = 4192 * 8
        self.sdr.gain_control_mode_chan0 = 'manual'
        self.sdr.rx_hardwaregain_chan0 = 60

        # Фильтр
        self.b_filt = design_filter(self.sample_rate, self.cutoff_hz)

        # Частоты для сканирования
        self.frequencies = np.linspace(self.sweep_start, self.sweep_stop, self.sweep_steps)

        # Хранение данных
        self.num_samples = self.sdr.rx_buffer_size
        self.num_reads = 1
        self.buffer_clear_reads = 1
        self.delay_time = 0.01

        self.freq_list = []
        self.amp_list = []
        self.sweep_index = 0
        self.sweep_complete = False

        # Построение GUI
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # График: Амплитуда vs Частота
        self.amplitude_plot = pg.PlotWidget(title="Амплитуда vs Частота (400-6000 МГц)")
        self.amplitude_plot.setBackground('w')
        self.amplitude_plot.setLabel('left', "Амплитуда", units='дБ')
        self.amplitude_plot.setLabel('bottom', "Частота", units='ГГц')
        self.amplitude_plot.getAxis('left').setPen(pg.mkPen('k'))
        self.amplitude_plot.getAxis('bottom').setPen(pg.mkPen('k'))
        self.amplitude_plot.showGrid(x=True, y=True)
        main_layout.addWidget(self.amplitude_plot)

        # Кривая
        self.amplitude_curve = self.amplitude_plot.plot(pen=pg.mkPen('b', width=2))

        # Таймер для непрерывного обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

    ##########################################################################
    # Функция извлечения амплитуды с использованием текущего КИХ-фильтра
    ##########################################################################
    def extract_amplitude(self, rx_signal):
        filtered_signal = lfilter(self.b_filt, 1.0, rx_signal)
        amplitude = np.abs(filtered_signal)
        return np.mean(amplitude)

    ##########################################################################
    # Основной цикл обновления
    ##########################################################################
    def update_plot(self):
        # Сканирование в процессе
        if not self.sweep_complete and self.sweep_index < len(self.frequencies):
            freq = self.frequencies[self.sweep_index]
            self.sdr.rx_lo = int(freq)
            time.sleep(self.delay_time)

            # Очищаем буфер приемника
            for _ in range(self.buffer_clear_reads):
                self.sdr.rx()

            # Накопление сигналов
            accumulated_signal = np.zeros(self.num_samples * self.num_reads, dtype=np.complex64)
            for j in range(self.num_reads):
                rx_signal = self.sdr.rx()[0]
                accumulated_signal[j*self.num_samples:(j+1)*self.num_samples] = (rx_signal / 2**12) * 5.5

            # Вычисляем амплитуду (дБ)
            amp_lin = self.extract_amplitude(accumulated_signal)
            amp_db = 20 * np.log10(amp_lin)
            freq_ghz = freq / 1e9

            self.freq_list.append(freq_ghz)
            self.amp_list.append(amp_db)

            # Обновляем кривую амплитуды
            self.amplitude_curve.setData(self.freq_list, self.amp_list)

            self.sweep_index += 1
            self.setWindowTitle(f"SDR Frequency Sweep: {freq_ghz:.2f} ГГц, Амплитуда: {amp_db:.1f} дБ")

        # Сканирование только что завершено
        elif not self.sweep_complete:
            self.sweep_complete = True

        # Перезапуск сканирования
        else:
            # Сброс для нового сканирования
            self.freq_list.clear()
            self.amp_list.clear()
            self.sweep_index = 0
            self.sweep_complete = False

##############################################################################
# Точка входа
##############################################################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    try:
        sys.exit(app.exec())
    finally:
        # Очищаем буфер SDR
        main_window.sdr.rx_destroy_buffer()
