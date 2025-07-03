import sys
import math
from PyQt5.QtGui import QFont
import numpy as np
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QFormLayout, QGroupBox, QHeaderView, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
def f1(t, intensity):
    return 0.0043*(1.482**4)*1.282*t**3 - 0.0146*7.2603*t**2 + \
                0.0354*1.139*(1.482**4)*1.282*t - 0.0002*21.659
def f2(t, intensity):
    if intensity < 25:
        return 0.0193*t**3-0.4421*t**2+3.6172*t-7.5828
    if intensity >= 25 and intensity < 43:
        return 0.0102*t**3-0.3338*t**2+3.3889*t-7.4836
    if intensity >=43 and intensity < 45:
        return -0.0132*t**3+0.1082*t**2+0.572*t-2.3451
    if intensity >= 45 and intensity <= 65:
        return abs(-0.0472*t**3+0.6602*t**2-2.3713*t+2.8744)
def thickness_from_h0(t, h0, intensity, winter_start=6.0, winter_end=10.0):
    if t <= winter_start:
        if t < winter_end:
            loss = f1(t, intensity)
        else:
            loss = f2(winter_end, intensity) + f1(t - winter_end, intensity)
    else:
        if t < winter_end:
            loss = f1(winter_start, intensity) + f2(t - winter_start, intensity)
        else:
            loss = f1(winter_end, intensity) + f2(winter_start - winter_end, intensity) + f1(t - winter_start, intensity)
    return max(h0 - loss, 0.0)
def get_post_restore_loss(t_rest, t_end, intensity, winter_start=6.0, winter_end=10.0):
    total = 0.0
    warm_end = winter_start
    if t_rest < warm_end:
        rem_warm = min(warm_end, t_end) - t_rest
        total += f1(rem_warm, intensity)
    if t_end > winter_start:
        start = max(winter_start, t_rest)
        end = min(winter_end, t_end)
        if end > start:
            total += f2(end, intensity) - f2(start, intensity)
    spring_start = winter_end
    if t_end > spring_start:
        rem_spring = t_end - max(spring_start, t_rest)
        if rem_spring > 0:
            total += f1(rem_spring, intensity)
    return total
def generate_xticklabels(start_date):
    roman_months = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
    labels = []
    labels.append(start_date.strftime('%d.%m'))
    for i in range(1, 13):
        month = (start_date.month - 1 + i) % 12 
        labels.append(roman_months[month])
    return labels
from datetime import timedelta
def generate_xtick_positions_and_roman_labels(start_date):
    roman_months = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
    positions = []
    labels = []
    for i in range(13):
        current_date = start_date + timedelta(days=30*i)
        delta_days = (current_date - start_date).days
        pos = delta_days / 30
        positions.append(pos)
        if i == 0:
            labels.append(current_date.strftime('%d.%m'))
        else:
            month_index = (start_date.month - 1 + i) % 12
            labels.append(roman_months[month_index])
    return positions, labels
def check_season_crossings(temp_list, dates, threshold):
    crossings = []
    for i in range(len(temp_list)-1):
        t1 = temp_list[i]
        t2 = temp_list[i+1]
        if t1 is None or t2 is None:
            continue
        if ((t1 <= threshold and t2 >= threshold) or (t1 >= threshold and t2 <= threshold)) and t1 != t2:
            d1 = dates[i]
            d2 = dates[i+1]
            delta_days = abs((d2 - d1).days)
            delta_t = abs(t1 - t2)
            t_per_day = delta_t / delta_days
            delta_days_cross = abs(threshold - t1) / t_per_day
            cross_date = d1 + timedelta(days=int(delta_days_cross))
            crossings.append(cross_date)
    return crossings
def format_dates(dates):
            return ', '.join(d.strftime('%d.%m') for d in dates) if dates else 'нет данных'
def months_from_start(date, start_date):
    delta_days = (date - start_date).days % 365
    return delta_days / 30
def get_next_t_thresh(t_start, h0, intensity, zero_start, zero_end, h_thresh):
    t_thresh = next((t for t in np.arange(t_start,12.01,0.01)
                         if thickness_from_h0(t, h0, intensity, zero_start, zero_end) <= h_thresh), None)
    return t_thresh
def thickness_with_rests(t, h0, intensity, rests, winter_start, winter_end):
    if not rests:
        return thickness_from_h0(t, h0, intensity, winter_start, winter_end)
    rests = sorted(rests, key=lambda x: x[0])
    if t < rests[0][0]:
        return thickness_from_h0(t, h0, intensity, winter_start, winter_end)
    for i in range(len(rests)):
        if t < rests[i][0]:
            t_rest, x_rest = rests[i-1]
            return max(x_rest - get_post_restore_loss(t_rest, t, intensity, winter_start, winter_end), 0.0)
    t_rest, x_rest = rests[-1]
    return max(x_rest - get_post_restore_loss(t_rest, t, intensity, winter_start, winter_end), 0.0)
def get_next_t_thresh_with_rests(t_start, h0, intensity, rests, zero_start, zero_end, h_thresh):
    for t in np.arange(t_start, 12.01, 0.01):
        thickness = thickness_with_rests(t, h0, intensity, rests, zero_start, zero_end)
        if thickness <= h_thresh:
            return t
    return None
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Оптимизация годовой программы нанесения дорожной разметки')
        self.setMinimumSize(1000, 800)
        self._init_ui()
    def _init_ui(self):
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(5, 5, 5, 5)
        params_group = QGroupBox()
        params_layout = QFormLayout()
        label_style = "QLabel { font-weight: bold; }"
        self.intensity_input = QLineEdit()
        self.h0_input = QLineEdit()
        self.cost_input = QLineEdit()
        self.step_input = QLineEdit("1.0")
        self.date_edit = QDateEdit(QDate(QDate.currentDate().year(), 5, 1))
        self.date_edit.setCalendarPopup(True)
        params_layout.addRow(QLabel("Интенсивность (тыс.авт/сут):"), self.intensity_input)
        params_layout.addRow(QLabel("Изначальная толщина (мм):"), self.h0_input)
        params_layout.addRow(QLabel("Стоимость 1 мм/м² (руб):"), self.cost_input)
        params_layout.addRow(QLabel("Шаг увеличения толщины (мм):"), self.step_input)
        params_layout.addRow(QLabel("Дата 1-го нанесения:"), self.date_edit)
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        climate_group = QGroupBox("Средние месячные температуры")
        climate_layout = QVBoxLayout()
        self.climate_table = QTableWidget(12, 2)
        self.climate_table.setHorizontalHeaderLabels(['Месяц', 'Температура (°C)'])
        self.climate_table.verticalHeader().setVisible(False)
        roman_months = ['I', 'II', 'III', 'IV', 'V', 'VI', 
                       'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        for row, month in enumerate(roman_months):
            month_item = QTableWidgetItem(month)
            month_item.setFlags(month_item.flags() & ~Qt.ItemIsEditable)
            month_item.setTextAlignment(Qt.AlignCenter)
            self.climate_table.setItem(row, 0, month_item)
            temp_item = QTableWidgetItem('0.0')
            temp_item.setTextAlignment(Qt.AlignCenter)
            self.climate_table.setItem(row, 1, temp_item)
        self.climate_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.climate_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.climate_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        climate_layout.addWidget(self.climate_table)
        self.info_label = QLabel()
        self.info_label.setStyleSheet(label_style)
        self.info_label.setWordWrap(True)
        climate_layout.addWidget(self.info_label)
        climate_group.setLayout(climate_layout)
        left_panel.addWidget(climate_group)
        self.btn = QPushButton('Рассчитать и построить')
        self.btn.setStyleSheet("QPushButton { font-weight: bold; padding: 5px; }")
        self.btn.clicked.connect(self.on_calculate)
        left_panel.addWidget(self.btn)
        main_layout.addLayout(left_panel, stretch=1)
        right_panel = QVBoxLayout()
        results_group = QGroupBox("Результаты расчета")
        results_layout = QVBoxLayout()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            'Стратегия', 'Восстановления',
            '1-е (мм)', 'Дата',
            '2-е (мм)', 'Дата',
            'Стоимость, руб'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.on_table_cell_clicked)
        results_layout.addWidget(self.table)
        results_group.setLayout(results_layout)
        right_panel.addWidget(results_group, stretch=1)
        fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(fig)
        self.canvas.setMinimumHeight(300)
        right_panel.addWidget(self.canvas, stretch=2)
        main_layout.addLayout(right_panel, stretch=2)
        self.setLayout(main_layout)
        self._setup_plot()
    def _setup_plot(self):
        self.ax.clear()
        labels = generate_xticklabels(datetime(QDate.currentDate().year(), 5, 1))
        self.ax.set_xticks(range(len(labels)))
        self.ax.set_xticklabels(labels)
        self.ax.set_xlabel('Срок службы разметки, мес.')
        self.ax.set_ylabel('Толщина разметки, мм')
        self.ax.set_ylim(0, 6.0)
        self.ax.set_yticks(np.arange(0, 6.1, 0.5))
        self.ax.grid(alpha=0.3)
        self.canvas.draw()
    def on_calculate(self):
        try:
            h0 = float(self.h0_input.text())
            cost_per_mm = float(self.cost_input.text())
            step = float(self.step_input.text())
            intensity = float(self.intensity_input.text())
            if h0 <= 0 or cost_per_mm <= 0 or step <= 0 or intensity <= 0: raise ValueError
        except:
            QMessageBox.warning(self, 'Ошибка', 'Введите значения.')
            return
        if not self.validate_climate_table():
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля температур корректными числами.')
            return
        start_date = self.date_edit.date()
        start_date = datetime(start_date.year(), start_date.month(), start_date.day())
        zero_crossings, five_crossings = self.find_transition_dates()
        info_text = f"<b>Переходы через 0°C:</b> {format_dates(zero_crossings)}<br>" \
                    f"<b>Переходы через +5°C:</b> {format_dates(five_crossings)}"
        self.info_label.setText(info_text)
        if zero_crossings:
            zero_crossings.sort()
            zero_start = months_from_start(zero_crossings[-1], start_date)
            zero_end = months_from_start(zero_crossings[0], start_date)
        else:
            temps = [float(self.climate_table.item(1, col).text()) for col in range(12)]
            avg_temp = sum(temps) / len(temps)
            if avg_temp > 0:
                zero_start = 13.0
                zero_end = 13.0
            else:
                zero_start = 0.0
                zero_end = 12.0
        if five_crossings:
            five_crossings.sort()
            if start_date < five_crossings[0] or start_date > five_crossings[-1]:
                QMessageBox.warning(self, 'Ошибка', 'Дата 1-го нанесения должна удовлетворять условиям нанесения.')
                return
            five_start = months_from_start(five_crossings[0], start_date)
            five_end = months_from_start(five_crossings[-1], start_date)
        else:
            temps = [float(self.climate_table.item(1, col).text()) for col in range(12)]
            avg_temp = sum(temps) / len(temps)
            if avg_temp > 5:
                five_start = 0.0
                five_end = 12.0
            else:
                QMessageBox.warning(self, 'Ошибка', 'Температура ниже +5°C весь год, период нанесения отсутствует.')
                return
        self.zero_start = zero_start
        self.zero_end = zero_end
        self.start_date = start_date
        self.table.clearContents()
        self.table.setRowCount(0)
        self.ax.clear()
        self.canvas.draw()
        h_thresh = 0.75 * h0
        self.variants = self.find_all_strategies(h0, intensity, zero_start, zero_end, five_start, five_end, h_thresh, step, cost_per_mm)
        self.table.setRowCount(len(self.variants))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            '№ стратегии', 'Кол-во восстановлений',
            'Восст. №1 (мм)', 'Дата №1',
            'Восст. №2 (мм)', 'Дата №2',
            'Стоимость, руб.'
        ])
        for i, var in enumerate(self.variants):
            self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.table.setItem(i, 1, QTableWidgetItem(str(var['rest_count'])))
            if var['rest_count'] > 0:
                self.table.setItem(i, 2, QTableWidgetItem(f"{var['rests'][0][1]:.1f}"))
                date1 = (start_date + timedelta(days=int(var['rests'][0][0]*30))).strftime('%d.%m')
                self.table.setItem(i, 3, QTableWidgetItem(date1))
            else:
                self.table.setItem(i, 2, QTableWidgetItem('-'))
                self.table.setItem(i, 3, QTableWidgetItem('-'))
            if var['rest_count'] > 1:
                self.table.setItem(i, 4, QTableWidgetItem(f"{var['rests'][1][1]:.1f}"))
                date2 = (start_date + timedelta(days=int(var['rests'][1][0]*30))).strftime('%d.%m')
                self.table.setItem(i, 5, QTableWidgetItem(date2))
            else:
                self.table.setItem(i, 4, QTableWidgetItem('-'))
                self.table.setItem(i, 5, QTableWidgetItem('-'))
            self.table.setItem(i, 6, QTableWidgetItem(f"{var['cost']:.2f}"))
    def plot_strategy(self, variant, h0, intensity, zero_start, zero_end, start_date, h_thresh):
        rests = sorted(variant['rests'], key=lambda r: r[0])
        t_pts = np.linspace(0, 12, 500)
        vals = []
        for t in t_pts:
            vals.append(thickness_with_rests(t, h0, intensity, rests, zero_start, zero_end))
    
        self.ax.clear()
        rest_times = [0] + [r[0] for r in rests] + [12]
    
        for i in range(len(rest_times) - 1):
            start_t = rest_times[i]
            end_t = rest_times[i+1]
            segment_vals = []
            segment_t = []
        
        # Разделяем на зимние и летние периоды
            winter_segments = []
            summer_segments = []
        
        # Определяем зимние периоды
            if zero_start < zero_end:
            # Зима в одном году (например, ноябрь-март)
                winter_ranges = [(zero_start, zero_end)]
            else:
            # Зима разбита на два периода (например, декабрь-февраль и ноябрь-январь следующего года)
                winter_ranges = [(zero_start, 12), (0, zero_end)]
        
        # Разбиваем текущий сегмент на подсегменты
            current_segments = []
            for w_start, w_end in winter_ranges:
                seg_start = max(start_t, w_start)
                seg_end = min(end_t, w_end)
                if seg_start < seg_end:
                    current_segments.append(('winter', seg_start, seg_end))
        
        # Добавляем летние периоды
            if zero_start < zero_end:
            # Лето до и после зимы
                if start_t < zero_start:
                    current_segments.append(('summer', start_t, min(end_t, zero_start)))
                if end_t > zero_end:
                    current_segments.append(('summer', max(start_t, zero_end), end_t))
            else:
            # Лето между двумя зимними периодами
                if end_t > zero_end and start_t < zero_start:
                    current_segments.append(('summer', zero_end, zero_start))
        
        # Сортируем сегменты по времени
            current_segments.sort(key=lambda x: x[1])
        
        # Отрисовываем каждый подсегмент
            for seg_type, seg_start, seg_end in current_segments:
                seg_t = []
                seg_v = []
                for t, v in zip(t_pts, vals):
                    if seg_start <= t <= seg_end:
                        seg_t.append(t)
                        seg_v.append(v)
                    elif t > seg_end:
                        break
            
                if seg_type == 'winter':
                # Для зимнего периода рисуем прямую линию между начальной и конечной точками
                    if seg_t:
                        self.ax.plot([seg_t[0], seg_t[-1]], [seg_v[0], seg_v[-1]], 'r-', lw=2)
                else:
                # Для летнего периода рисуем как обычно
                    if seg_t:
                        self.ax.plot(seg_t, seg_v, 'r-', lw=2)
    
        # Отрисовываем восстановления
        for t_restore, x_restore in rests:
            th_before = thickness_with_rests(t_restore, h0, intensity,
                                        [r for r in rests if r[0] < t_restore],
                                        zero_start, zero_end)
            self.ax.vlines(t_restore, th_before, x_restore, colors='g', linestyles='--', lw=2)
    
        self.ax.hlines(h_thresh, 0, 12, colors='b', linestyles='--')
        self.ax.hlines(h0, 0, 12, colors='k', linestyles=':')
    
        positions, labels = generate_xtick_positions_and_roman_labels(start_date)
        self.ax.set_xticks(positions)
        self.ax.set_xticklabels(labels)
        self.ax.set_xlabel('Срок службы разметки, мес.')
        self.ax.set_ylabel('Толщина разметки, мм')
        self.ax.set_ylim(0, 6.0)
        self.ax.set_yticks(np.arange(0, 6.1, 0.5))
        self.ax.grid(alpha=0.3)
        self.canvas.draw()
    def find_all_strategies(self, h0, intensity, zero_start, zero_end, five_start, five_end, h_thresh, step, cost_per_mm):
        print(f"params: h0={h0}, intensity={intensity}, zero_start={zero_start}, zero_end={zero_end}, five_start={five_start}, five_end={five_end}, h_thresh={h_thresh}, step={step}, cost_per_mm={cost_per_mm}")
        variants = []
        if self.check_no_restoration_needed(h0, intensity, zero_start, zero_end, h_thresh):
            variants.append({'rest_count': 0, 'rests': [], 'cost': round(h0 * cost_per_mm, 2)})
        else:
            variants.extend(self.generate_one_restoration_variants(h0, intensity, zero_start, zero_end, five_start, five_end, h_thresh, step, cost_per_mm))
            variants.extend(self.generate_two_restoration_variants(h0, intensity, zero_start, zero_end, five_start, five_end, h_thresh, step, cost_per_mm))
        if not variants:
            QMessageBox.warning(self, 'Невозможно', 'Нет подходящих вариантов.')
        return sorted(variants, key=lambda v: v['cost'])
    def check_no_restoration_needed(self, h0, intensity, zero_start, zero_end, h_thresh):
        t_thresh = get_next_t_thresh(0, h0, intensity, zero_start, zero_end, h_thresh)
        if not t_thresh is None and t_thresh < 12.0:
            return False
        return True
    def generate_one_restoration_variants(self, h0, intensity, zero_start, zero_end, five_start, five_end, h_thresh, step, cost_per_mm):
        t_thresh = get_next_t_thresh(0, h0, intensity, zero_start, zero_end, h_thresh)    
        if t_thresh is None:
            return []
        t_restore = min(t_thresh, five_end)
        th_before = thickness_from_h0(t_restore, h0, intensity, zero_start, zero_end)
        total_loss = get_post_restore_loss(t_restore, 12.0, intensity, zero_start, zero_end)
        x_req = h_thresh + total_loss
        x_min = math.ceil(x_req / step) * step
        options = np.arange(x_min, 6.001, step)
        variants = []
        for x in options:
            final_th = x - total_loss
            if final_th > h_thresh:
                price = round((h0 + x - th_before) * cost_per_mm, 2)
                variants.append({
                    'rest_count': 1,
                    'rests': [(t_restore, x)],
                    'cost': price
                })
        return variants
    def generate_two_restoration_variants(self, h0, intensity, zero_start, zero_end,
                                           five_start, five_end, h_thresh, step, cost_per_mm):
        t_thresh = get_next_t_thresh(0, h0, intensity, zero_start, zero_end, h_thresh)    
        if t_thresh is None:
            return []
        if t_thresh > five_end:
            return []
        t_restore = min(t_thresh, five_end)
        th_before = thickness_from_h0(t_restore, h0, intensity, zero_start, zero_end)
        x1_min = math.ceil(h_thresh / step) * step
        options = np.arange(x1_min, 6.001, step)
        variants = []
        for x1 in options:
            if x1 <= th_before:
                continue
            th_at_restore = thickness_with_rests(t_restore, h0, intensity, [(t_restore, x1)], zero_start, zero_end)
            if th_at_restore <= h_thresh + 1e-6:
                continue
            t1_thresh = get_next_t_thresh_with_rests(t_thresh, x1, intensity, [(t_restore, x1)], zero_start, zero_end, h_thresh)
            if t1_thresh is None or t1_thresh <= t_restore + 1e-6:
                continue
            t1_restore = min(t1_thresh, five_end)
            total_loss_1_to_2 = get_post_restore_loss(t_thresh, t1_restore, intensity, zero_start, zero_end)
            th_before1 = x1 - total_loss_1_to_2
            for x2 in options:
                if x2 <= th_before1:
                    continue
                total_loss_2_to_end = get_post_restore_loss(t1_restore, 12.0, intensity, zero_start, zero_end)
                final_th = x2 - total_loss_2_to_end
                if final_th > h_thresh:
                    price = round((h0 + x1 - th_before + x2 - th_before1) * cost_per_mm, 2)
                    variants.append({
                        'rest_count': 2,
                        'rests': [(t_restore, x1), (t1_restore, x2)],
                        'cost': price
                    })
        return variants
    def on_table_cell_clicked(self, row, column):
        if not hasattr(self, 'variants'):
            return
        if row >= len(self.variants):
            return
        variant = self.variants[row]
        try:
            h0 = float(self.h0_input.text())
            intensity = float(self.intensity_input.text())
            step = float(self.step_input.text())
        except:
            return
        self.plot_strategy(
            variant, h0, intensity,
            self.zero_start, self.zero_end,
            self.start_date, 0.75 * h0
        )
    def find_transition_dates(self):
        temps = []
        for col in range(12):
            try:
                val = float(self.climate_table.item(1, col).text())
            except:
                val = None
            temps.append(val)
        year = datetime.now().year
        dates = [datetime(year, month+1, 15) for month in range(12)]
        zero_crossings = check_season_crossings(temps, dates, 0)
        five_crossings = check_season_crossings(temps, dates, 5)
        return zero_crossings, five_crossings
    def validate_climate_table(self):
        for col in range(12):
            item = self.climate_table.item(1, col)
            if item is None or item.text().strip() == '':
                return False
            try:
                float(item.text())
            except ValueError:
                return False
        return True
    def validate_climate_table(self):
        for row in range(12):
            item = self.climate_table.item(row, 1)
            if item is None or item.text().strip() == '':
                return False
            try:
                float(item.text())
            except ValueError:
                return False
        return True
    def find_transition_dates(self):
        temps = []
        for row in range(12):
            try:
                val = float(self.climate_table.item(row, 1).text())
            except:
                val = None
            temps.append(val)
        year = datetime.now().year
        dates = [datetime(year, month+1, 15) for month in range(12)]
        zero_crossings = check_season_crossings(temps, dates, 0)
        five_crossings = check_season_crossings(temps, dates, 5)
        return zero_crossings, five_crossings
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())