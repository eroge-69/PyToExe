import sys
import math
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDialog, QTabWidget, QListWidget, QGridLayout, QLineEdit, QGroupBox,
                             QComboBox, QSpinBox, QInputDialog, QFileDialog, QDialogButtonBox, QMenu, QAction)
from PyQt5.QtCore import QTimer, Qt, QSettings
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator, QIntValidator, QPalette
from datetime import datetime, timedelta
import pytz


class Location:
    """Базовый класс для всех географических объектов"""

    def __init__(self, name, lat, lon):
        self.name = name  # Название объекта
        self.lat = lat  # Широта
        self.lon = lon  # Долгота

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon})"

    def to_string(self):
        return f"{self.name}|{self.lat}|{self.lon}"


class Drone(Location):
    """Класс для БПЛА с дополнительными параметрами"""

    def __init__(self, name, lat, lon, speed_kmh, start_time):
        super().__init__(name, lat, lon)
        self.speed_kmh = speed_kmh  # Скорость в км/ч
        self.start_time = start_time  # Время обнаружения

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon}) {self.speed_kmh} км/ч {self.start_time.strftime('%H:%M')}"

    def to_string(self):
        return f"{super().to_string()}|{self.speed_kmh}|{self.start_time.strftime('%H:%M')}"


class Helicopter(Location):
    """Класс для вертолетов"""

    def __init__(self, name, lat, lon, speed_kmh, prep_time_min):
        super().__init__(name, lat, lon)
        self.speed_kmh = speed_kmh  # Скорость в км/ч
        self.prep_time_min = prep_time_min  # Время подготовки к вылету в минутах

    def __str__(self):
        return f"{self.name} ({self.speed_kmh} км/ч, подготовка: {self.prep_time_min} мин)"

    def to_string(self):
        return f"{super().to_string()}|{self.speed_kmh}|{self.prep_time_min}"


class Target(Location):
    """Класс для объекта (объектов наблюдения)"""
    pass


class AirfieldWithZones(Location):
    """Класс для аэродромов с зонами дежурства"""

    def __init__(self, name, lat, lon):
        super().__init__(name, lat, lon)
        self.zones = []  # Список зон дежурства с временем патрулирования

    def add_zone(self, name, lat, lon, patrol_duration):
        """Добавление зоны дежурства"""
        self.zones.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'patrol_duration': patrol_duration
        })

    def __str__(self):
        zones_info = ", ".join([f"{z['name']} ({z['patrol_duration']} мин)" for z in self.zones])
        return f"{self.name} ({self.lat}, {self.lon}) [Зоны: {zones_info if self.zones else 'нет'}]"

    def to_string(self):
        zones_str = ";".join([f"{z['name']}|{z['lat']}|{z['lon']}|{z['patrol_duration']}" for z in self.zones])
        return f"{super().to_string()}|{zones_str}"


class EditDialog(QDialog):
    """Диалог для редактирования объектов"""

    def __init__(self, parent=None, obj_type=None, obj=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"Редактирование {'БПЛА' if obj_type == 'drone' else 'цели' if obj_type == 'target' else 'аэродрома' if obj_type == 'airfield' else 'вертолета'}")
        self.obj_type = obj_type
        self.obj = obj
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        grid = QGridLayout()
        row = 0

        # Название
        grid.addWidget(QLabel("Название:"), row, 0)
        self.name_edit = QLineEdit()
        grid.addWidget(self.name_edit, row, 1)
        row += 1

        # Широта
        grid.addWidget(QLabel("Широта:"), row, 0)
        self.lat_edit = QLineEdit()
        self.lat_edit.setValidator(QDoubleValidator(-90, 90, 6))
        grid.addWidget(self.lat_edit, row, 1)
        row += 1

        # Долгота
        grid.addWidget(QLabel("Долгота:"), row, 0)
        self.lon_edit = QLineEdit()
        self.lon_edit.setValidator(QDoubleValidator(-180, 180, 6))
        grid.addWidget(self.lon_edit, row, 1)
        row += 1

        # Дополнительные параметры в зависимости от типа объекта
        if self.obj_type == 'drone':
            # Скорость
            grid.addWidget(QLabel("Скорость (км/ч):"), row, 0)
            self.speed_edit = QLineEdit()
            self.speed_edit.setValidator(QDoubleValidator(0, 1000, 2))
            grid.addWidget(self.speed_edit, row, 1)
            row += 1

            # Время обнаружения
            grid.addWidget(QLabel("Время обнаружения (ЧЧ:ММ):"), row, 0)
            self.time_edit = QLineEdit()
            grid.addWidget(self.time_edit, row, 1)
            row += 1

        elif self.obj_type == 'helicopter':
            # Скорость
            grid.addWidget(QLabel("Скорость (км/ч):"), row, 0)
            self.speed_edit = QLineEdit()
            self.speed_edit.setValidator(QDoubleValidator(0, 1000, 2))
            grid.addWidget(self.speed_edit, row, 1)
            row += 1

            # Время подготовки
            grid.addWidget(QLabel("Время подготовки (мин):"), row, 0)
            self.prep_edit = QLineEdit()
            self.prep_edit.setValidator(QIntValidator(0, 120))
            grid.addWidget(self.prep_edit, row, 1)
            row += 1

        elif self.obj_type == 'airfield':
            # Кнопка добавления зоны
            self.add_zone_btn = QPushButton("Добавить зону")
            self.add_zone_btn.clicked.connect(self.add_zone)
            grid.addWidget(self.add_zone_btn, row, 0, 1, 2)
            row += 1

            # Список зон
            self.zones_list = QListWidget()
            grid.addWidget(self.zones_list, row, 0, 1, 2)
            row += 1

            # Кнопка удаления зоны
            self.del_zone_btn = QPushButton("Удалить зону")
            self.del_zone_btn.clicked.connect(self.del_zone)
            grid.addWidget(self.del_zone_btn, row, 0, 1, 2)
            row += 1

        layout.addLayout(grid)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Заполняем поля, если редактируем существующий объект
        if self.obj:
            self.name_edit.setText(self.obj.name)
            self.lat_edit.setText(str(self.obj.lat))
            self.lon_edit.setText(str(self.obj.lon))

            if self.obj_type == 'drone':
                self.speed_edit.setText(str(self.obj.speed_kmh))
                self.time_edit.setText(self.obj.start_time.strftime("%H:%M"))
            elif self.obj_type == 'helicopter':
                self.speed_edit.setText(str(self.obj.speed_kmh))
                self.prep_edit.setText(str(self.obj.prep_time_min))
            elif self.obj_type == 'airfield':
                for zone in self.obj.zones:
                    self.zones_list.addItem(
                        f"{zone['name']} ({zone['lat']}, {zone['lon']}) - {zone['patrol_duration']} мин")

    def add_zone(self):
        """Добавление новой зоны"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление зоны")
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(QLabel("Название:"), 0, 0)
        name_edit = QLineEdit()
        grid.addWidget(name_edit, 0, 1)

        grid.addWidget(QLabel("Широта:"), 1, 0)
        lat_edit = QLineEdit()
        lat_edit.setValidator(QDoubleValidator(-90, 90, 6))
        grid.addWidget(lat_edit, 1, 1)

        grid.addWidget(QLabel("Долгота:"), 2, 0)
        lon_edit = QLineEdit()
        lon_edit.setValidator(QDoubleValidator(-180, 180, 6))
        grid.addWidget(lon_edit, 2, 1)

        grid.addWidget(QLabel("Время патрулирования (мин):"), 3, 0)
        duration_edit = QLineEdit()
        duration_edit.setValidator(QIntValidator(0, 1000))
        grid.addWidget(duration_edit, 3, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(grid)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text()
            lat = float(lat_edit.text())
            lon = float(lon_edit.text())
            duration = int(duration_edit.text())

            self.zones_list.addItem(f"{name} ({lat}, {lon}) - {duration} мин")

    def del_zone(self):
        """Удаление выбранной зоны"""
        current = self.zones_list.currentRow()
        if current >= 0:
            self.zones_list.takeItem(current)

    def get_data(self):
        """Получение данных из формы"""
        name = self.name_edit.text()
        lat = float(self.lat_edit.text())
        lon = float(self.lon_edit.text())

        if self.obj_type == 'drone':
            speed = float(self.speed_edit.text())
            time_str = self.time_edit.text()
            hours, minutes = map(int, time_str.split(':'))
            time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            return Drone(name, lat, lon, speed, time)

        elif self.obj_type == 'helicopter':
            speed = float(self.speed_edit.text())
            prep = int(self.prep_edit.text())
            return Helicopter(name, lat, lon, speed, prep)

        elif self.obj_type == 'airfield':
            airfield = AirfieldWithZones(name, lat, lon)
            for i in range(self.zones_list.count()):
                text = self.zones_list.item(i).text()
                parts = text.split(' - ')
                name_coords = parts[0].split(' (')
                zone_name = name_coords[0]
                coords = name_coords[1].rstrip(')').split(', ')
                lat = float(coords[0])
                lon = float(coords[1])
                duration = int(parts[1].split(' ')[0])
                airfield.add_zone(zone_name, lat, lon, duration)
            return airfield

        else:  # target
            return Target(name, lat, lon)


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle('Настройки')
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Настройки темы
        theme_group = QGroupBox("Тема оформления")
        theme_layout = QVBoxLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая тема", "light")
        self.theme_combo.addItem("Темная тема", "dark")
        self.theme_combo.setCurrentIndex(1 if self.parent.dark_theme else 0)

        theme_layout.addWidget(QLabel("Выберите тему:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_settings(self):
        """Сохранение настроек"""
        self.parent.dark_theme = self.theme_combo.currentData() == "dark"
        self.parent.save_settings()
        self.parent.apply_theme()
        self.accept()


class ArmyAviationDialog(QDialog):
    """Диалоговое окно расчета армейской авиации"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Расчет взлета армейской авиации')
        self.resize(1200, 600)
        self.parent = parent

        self.initUI()
        self.calculateAll()  # Автоматический расчет при открытии

    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Время (как в главном окне)
        timeLayout = QHBoxLayout()
        self.moscowTimeLabel = QLabel()
        self.ekbTimeLabel = QLabel()
        timeLayout.addWidget(self.moscowTimeLabel)
        timeLayout.addWidget(self.ekbTimeLabel)
        layout.addLayout(timeLayout)

        # Выбор вертолета и БПЛА
        paramsGroup = QGroupBox("Параметры расчета")
        paramsLayout = QGridLayout()

        # Выбор вертолета
        paramsLayout.addWidget(QLabel("Вертолет:"), 0, 0)
        self.heliCombo = QComboBox()
        for heli in self.parent.helicopters:
            self.heliCombo.addItem(heli.name, heli)
        paramsLayout.addWidget(self.heliCombo, 0, 1)

        # Выбор БПЛА
        paramsLayout.addWidget(QLabel("БПЛА:"), 1, 0)
        self.droneCombo = QComboBox()
        for drone in self.parent.drones:
            self.droneCombo.addItem(drone.name, drone)
        paramsLayout.addWidget(self.droneCombo, 1, 1)

        paramsGroup.setLayout(paramsLayout)
        layout.addWidget(paramsGroup)

        # Таблица результатов
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(7)
        self.resultTable.setHorizontalHeaderLabels([
            "Аэродром",
            "Зона дежурства",
            "Вертолет",
            "Время взлета",
            "Время входа БПЛА",
            "Время дежурства",
            "Статус"
        ])
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.resultTable)

        # Кнопки
        btnLayout = QHBoxLayout()
        recalcBtn = QPushButton('Пересчитать')
        recalcBtn.clicked.connect(self.calculateAll)

        exportBtn = QPushButton('Экспорт в справку')
        exportBtn.clicked.connect(self.exportReport)

        closeBtn = QPushButton('Закрыть')
        closeBtn.clicked.connect(self.close)

        btnLayout.addWidget(recalcBtn)
        btnLayout.addWidget(exportBtn)
        btnLayout.addWidget(closeBtn)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

        # Таймер для обновления времени
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.updateTime()

    def updateTime(self):
        """Обновление времени в заголовке"""
        now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
        now_ekb = datetime.now(pytz.timezone('Asia/Yekaterinburg'))

        self.moscowTimeLabel.setText(f"МСК: {now_moscow.strftime('%H:%M:%S')}")
        self.ekbTimeLabel.setText(f"ЕКБ: {now_ekb.strftime('%H:%M:%S')}")

    def calculateAll(self):
        """Расчет времени для всех аэродромов и зон"""
        try:
            helicopter = self.heliCombo.currentData()
            drone = self.droneCombo.currentData()

            if not helicopter:
                raise ValueError("Не выбран вертолет")
            if not drone:
                raise ValueError("Не выбран БПЛА")

            # Очистка таблицы
            self.resultTable.setRowCount(0)

            # Для каждого аэродрома и его зон выполняем расчет
            for airfield in self.parent.airfields:
                for zone in airfield.zones:
                    self.calculateZone(airfield, zone, helicopter, drone)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def calculateZone(self, airfield, zone, helicopter, drone):
        """Расчет времени для одной зоны с учетом времени подлета БПЛА"""
        try:
            # Расчет расстояния и времени полета вертолета
            distance = self.parent.haversine(airfield.lat, airfield.lon, zone['lat'], zone['lon'])
            travel_time = distance / helicopter.speed_kmh * 60  # Время полета в минутах

            # Расчет времени подлета БПЛА к этой зоне
            drone_time = self.calculateDroneTime(zone, drone)

            if drone_time is None:
                return

            # Расчет времени прибытия вертолета (за 10 минут до подлета БПЛА)
            arrival_time = drone_time - timedelta(minutes=10)

            # Время взлета вертолета (с учетом подготовки)
            takeoff_time = arrival_time - timedelta(minutes=travel_time + helicopter.prep_time_min)

            # Время окончания дежурства
            patrol_end_time = arrival_time + timedelta(minutes=zone['patrol_duration'])

            # Текущее время
            now = datetime.now(pytz.timezone('Europe/Moscow'))

            # Статус зоны
            status = "Активна"
            if patrol_end_time < now:
                status = "Истекло"
            elif arrival_time < now:
                status = "Дежурство"

            # Определяем оптимальный вертолет
            optimal_heli = self.parent.calculateOptimalHelicopter(drone, zone)
            is_optimal = optimal_heli and optimal_heli.name == helicopter.name

            # Добавление строки в таблицу
            row = self.resultTable.rowCount()
            self.resultTable.insertRow(row)

            # Заполнение таблицы
            items = [
                QTableWidgetItem(airfield.name),
                QTableWidgetItem(zone['name']),
                QTableWidgetItem(helicopter.name),
                QTableWidgetItem(takeoff_time.strftime('%H:%M:%S')),
                QTableWidgetItem(drone_time.strftime('%H:%M:%S')),
                QTableWidgetItem(f"{arrival_time.strftime('%H:%M:%S')} - {patrol_end_time.strftime('%H:%M:%S')}"),
                QTableWidgetItem(status)
            ]

            # Установка цветов в зависимости от статуса и оптимальности
            if is_optimal:
                color = QColor(255, 255, 200)  # Светло-желтый для оптимального
                for item in items:
                    item.setBackground(QBrush(color))
                    item.setToolTip("Оптимальный вертолет для перехвата")
            elif status == "Истекло":
                color = QColor(255, 200, 200)  # Светло-красный
            elif status == "Дежурство":
                color = QColor(200, 255, 200)  # Светло-зеленый
            else:
                color = QColor(240, 240, 240)  # Светло-серый

            for i, item in enumerate(items):
                if not is_optimal:
                    item.setBackground(QBrush(color))
                self.resultTable.setItem(row, i, item)

        except Exception as e:
            print(f"Ошибка расчета для зоны {zone['name']}: {str(e)}")

    def calculateDroneTime(self, zone, drone):
        """Расчет времени подлета БПЛА к зоне"""
        # Расчет расстояния между БПЛА и зоной
        dist = self.parent.haversine(drone.lat, drone.lon, zone['lat'], zone['lon'])
        hours = dist / drone.speed_kmh
        seconds = int(hours * 3600)

        # Расчет времени обнаружения
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        today_start = now.replace(hour=drone.start_time.hour, minute=drone.start_time.minute,
                                  second=0, microsecond=0)
        if today_start > now:
            today_start -= timedelta(days=1)

        arrival = today_start + timedelta(seconds=seconds)

        return arrival

    def exportReport(self):
        """Экспорт данных в текстовый файл"""
        try:
            # Получаем текущую дату и время для имени файла
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"справка_{now}.txt"

            # Диалог выбора файла для сохранения
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить справку", default_filename, "Текстовые файлы (*.txt)"
            )

            if not filename:
                return  # Пользователь отменил сохранение

            # Добавляем расширение .txt, если его нет
            if not filename.lower().endswith('.txt'):
                filename += '.txt'

            # Собираем данные для экспорта
            helicopter = self.heliCombo.currentData()
            drone = self.droneCombo.currentData()

            if not helicopter or not drone:
                raise ValueError("Не выбран вертолет или БПЛА")

            # Формируем содержимое файла
            content = []
            content.append(f"СПРАВКА по расчету взлета армейской авиации")
            content.append(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            content.append(f"\nПараметры расчета:")
            content.append(f"Вертолет: {helicopter.name}")
            content.append(f"БПЛА: {drone.name}")
            content.append("\nРезультаты расчета:")

            # Добавляем заголовки таблицы
            headers = [
                "Аэродром", "Зона дежурства", "Вертолет", "Время взлета",
                "Время входа БПЛА", "Время дежурства", "Статус"
            ]
            content.append("\t".join(headers))

            # Добавляем данные из таблицы
            for row in range(self.resultTable.rowCount()):
                row_data = []
                for col in range(self.resultTable.columnCount()):
                    item = self.resultTable.item(row, col)
                    row_data.append(item.text() if item else "")
                content.append("\t".join(row_data))

            # Записываем в файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))

            QMessageBox.information(self, "Успех", f"Справка успешно сохранена в файл:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить справку:\n{str(e)}")


class DroneFlightGUI(QWidget):
    """Основной класс графического интерфейса"""

    def __init__(self):
        super().__init__()
        # Инициализация списков объектов
        self.drones = []  # Список БПЛА
        self.targets = []  # Список объектов
        self.airfields = []  # Список аэродромов с зонами
        self.helicopters = []  # Список вертолетов
        self.sort_by_time = False  # Флаг сортировки по времени

        # Настройки темы
        self.dark_theme = False
        self.load_settings()  # Загрузка настроек
        self.load_data()  # Загрузка данных

        self.initUI()  # Инициализация интерфейса
        self.updateTable()  # Обновление таблицы
        self.apply_theme()  # Применение темы

        # Настройка таймера для обновления времени каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTable)
        self.timer.start(1000)

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists('settings.txt'):
                with open('settings.txt', 'r') as f:
                    for line in f:
                        if line.startswith('dark_theme='):
                            self.dark_theme = line.split('=')[1].strip() == 'True'
                            break
        except Exception as e:
            print(f"Ошибка загрузки настроек: {str(e)}")

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open('settings.txt', 'w') as f:
                f.write(f"dark_theme={self.dark_theme}\n")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists('data.txt'):
                with open('data.txt', 'r') as f:
                    section = None
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        if line == "[drones]":
                            section = "drones"
                            continue
                        elif line == "[targets]":
                            section = "targets"
                            continue
                        elif line == "[airfields]":
                            section = "airfields"
                            continue
                        elif line == "[helicopters]":
                            section = "helicopters"
                            continue

                        if section == "drones":
                            parts = line.split('|')
                            if len(parts) >= 5:
                                name = parts[0]
                                lat = float(parts[1])
                                lon = float(parts[2])
                                speed = float(parts[3])
                                time_str = parts[4]
                                hours, minutes = map(int, time_str.split(':'))
                                time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
                                self.drones.append(Drone(name, lat, lon, speed, time))

                        elif section == "targets":
                            parts = line.split('|')
                            if len(parts) >= 3:
                                name = parts[0]
                                lat = float(parts[1])
                                lon = float(parts[2])
                                self.targets.append(Target(name, lat, lon))

                        elif section == "airfields":
                            parts = line.split('|')
                            if len(parts) >= 3:
                                name = parts[0]
                                lat = float(parts[1])
                                lon = float(parts[2])
                                airfield = AirfieldWithZones(name, lat, lon)

                                if len(parts) > 3 and parts[3]:
                                    zones = parts[3].split(';')
                                    for zone in zones:
                                        z_parts = zone.split('|')
                                        if len(z_parts) >= 4:
                                            z_name = z_parts[0]
                                            z_lat = float(z_parts[1])
                                            z_lon = float(z_parts[2])
                                            z_duration = int(z_parts[3])
                                            airfield.add_zone(z_name, z_lat, z_lon, z_duration)

                                self.airfields.append(airfield)

                        elif section == "helicopters":
                            parts = line.split('|')
                            if len(parts) >= 5:
                                name = parts[0]
                                lat = float(parts[1])
                                lon = float(parts[2])
                                speed = float(parts[3])
                                prep = int(parts[4])
                                self.helicopters.append(Helicopter(name, lat, lon, speed, prep))

        except Exception as e:
            print(f"Ошибка загрузки данных: {str(e)}")
            self.load_sample_data()

    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open('data.txt', 'w') as f:
                # Сохраняем БПЛА
                f.write("[drones]\n")
                for drone in self.drones:
                    f.write(drone.to_string() + "\n")

                # Сохраняем цели
                f.write("\n[targets]\n")
                for target in self.targets:
                    f.write(target.to_string() + "\n")

                # Сохраняем аэродромы
                f.write("\n[airfields]\n")
                for airfield in self.airfields:
                    f.write(airfield.to_string() + "\n")

                # Сохраняем вертолеты
                f.write("\n[helicopters]\n")
                for heli in self.helicopters:
                    f.write(heli.to_string() + "\n")

        except Exception as e:
            print(f"Ошибка сохранения данных: {str(e)}")

    def load_sample_data(self):
        """Загрузка тестовых данных"""
        # Тестовые БПЛА
        self.drones = [
            Drone("Orlan-10", 56.5, 60.5, 150, datetime.strptime("08:00", "%H:%M")),
            Drone("Zala", 57.0, 59.5, 120, datetime.strptime("10:30", "%H:%M"))
        ]

        # Тестовые цели
        self.targets = [
            Target("Завод", 56.8, 60.6),
            Target("Мост", 56.9, 60.8)
        ]

        # Тестовые аэродромы
        airfield = AirfieldWithZones("Аэродром1", 56.7, 60.7)
        airfield.add_zone("Зона1", 56.75, 60.75, 30)
        airfield.add_zone("Зона2", 56.8, 60.8, 45)
        self.airfields = [airfield]

        # Тестовые вертолеты
        self.helicopters = [
            Helicopter("Ми-8", 56.7, 60.7, 250, 15),
            Helicopter("Ка-52", 56.7, 60.7, 300, 10)
        ]

    def getDroneColors(self):
        """Генерация цветов для отображения БПЛА"""
        if self.dark_theme:
            base_colors = [
                QColor(70, 130, 180),  # Голубой для темной темы
                QColor(152, 251, 152),  # Светло-зеленый
                QColor(255, 165, 0),  # Оранжевый
            ]
        else:
            base_colors = [
                QColor(96, 205, 230),  # Голубой для светлой темы
                QColor(50, 205, 50),  # Лаймовый
                QColor(255, 99, 71),  # Томатный
            ]

        # Генерация дополнительных цветов при необходимости
        while len(base_colors) < len(self.drones):
            hue = (len(base_colors) * 70) % 360
            if self.dark_theme:
                base_colors.append(QColor.fromHsv(hue, 150, 200))
            else:
                base_colors.append(QColor.fromHsv(hue, 200, 230))

        return base_colors

    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Расчет подлета БПЛА и вертолетов')
        self.resize(1200, 600)

        # Основной вертикальный layout
        layout = QVBoxLayout()

        # Layout для отображения времени
        timeLayout = QHBoxLayout()
        self.moscowTimeLabel = QLabel()
        self.ekbTimeLabel = QLabel()
        timeLayout.addWidget(self.moscowTimeLabel)
        timeLayout.addWidget(self.ekbTimeLabel)
        layout.addLayout(timeLayout)

        # Таблица для отображения данных
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Кнопка меню редактирования
        self.editMenuButton = QPushButton('Редактирование')
        self.editMenu = QMenu()

        # Подменю "БПЛА"
        drone_menu = self.editMenu.addMenu('БПЛА')
        add_drone_action = QAction('Добавить БПЛА', self)
        add_drone_action.triggered.connect(lambda: self.edit_object('drone'))
        drone_menu.addAction(add_drone_action)

        edit_drone_action = QAction('Редактировать БПЛА', self)
        edit_drone_action.triggered.connect(lambda: self.edit_object('drone', edit=True))
        drone_menu.addAction(edit_drone_action)

        del_drone_action = QAction('Удалить БПЛА', self)
        del_drone_action.triggered.connect(lambda: self.delete_object('drone'))
        drone_menu.addAction(del_drone_action)

        # Подменю "Цели"
        target_menu = self.editMenu.addMenu('Цели')
        add_target_action = QAction('Добавить цель', self)
        add_target_action.triggered.connect(lambda: self.edit_object('target'))
        target_menu.addAction(add_target_action)

        edit_target_action = QAction('Редактировать цель', self)
        edit_target_action.triggered.connect(lambda: self.edit_object('target', edit=True))
        target_menu.addAction(edit_target_action)

        del_target_action = QAction('Удалить цель', self)
        del_target_action.triggered.connect(lambda: self.delete_object('target'))
        target_menu.addAction(del_target_action)

        # Подменю "Аэродромы"
        airfield_menu = self.editMenu.addMenu('Аэродромы')
        add_airfield_action = QAction('Добавить аэродром', self)
        add_airfield_action.triggered.connect(lambda: self.edit_object('airfield'))
        airfield_menu.addAction(add_airfield_action)

        edit_airfield_action = QAction('Редактировать аэродром', self)
        edit_airfield_action.triggered.connect(lambda: self.edit_object('airfield', edit=True))
        airfield_menu.addAction(edit_airfield_action)

        del_airfield_action = QAction('Удалить аэродром', self)
        del_airfield_action.triggered.connect(lambda: self.delete_object('airfield'))
        airfield_menu.addAction(del_airfield_action)

        # Подменю "Вертолеты"
        heli_menu = self.editMenu.addMenu('Вертолеты')
        add_heli_action = QAction('Добавить вертолет', self)
        add_heli_action.triggered.connect(lambda: self.edit_object('helicopter'))
        heli_menu.addAction(add_heli_action)

        edit_heli_action = QAction('Редактировать вертолет', self)
        edit_heli_action.triggered.connect(lambda: self.edit_object('helicopter', edit=True))
        heli_menu.addAction(edit_heli_action)

        del_heli_action = QAction('Удалить вертолет', self)
        del_heli_action.triggered.connect(lambda: self.delete_object('helicopter'))
        heli_menu.addAction(del_heli_action)

        self.editMenuButton.setMenu(self.editMenu)

        # Layout для кнопок управления
        btnLayout = QHBoxLayout()

        self.settingsButton = QPushButton('Настройки')
        self.settingsButton.clicked.connect(self.openSettingsDialog)

        self.armyButton = QPushButton('Расчет взлета армейской авиации')
        self.armyButton.clicked.connect(self.openArmAviaDialog)

        self.sortButton = QPushButton('Сортировать по остатку времени')
        self.sortButton.clicked.connect(self.sortTargets)

        btnLayout.addWidget(self.editMenuButton)
        btnLayout.addWidget(self.settingsButton)
        btnLayout.addWidget(self.armyButton)
        btnLayout.addWidget(self.sortButton)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def edit_object(self, obj_type, edit=False):
        """Редактирование или добавление объекта"""
        try:
            if edit:
                # Получаем список объектов для выбора
                if obj_type == 'drone':
                    objects = self.drones
                    title = "Выберите БПЛА для редактирования"
                elif obj_type == 'target':
                    objects = self.targets
                    title = "Выберите цель для редактирования"
                elif obj_type == 'airfield':
                    objects = self.airfields
                    title = "Выберите аэродром для редактирования"
                elif obj_type == 'helicopter':
                    objects = self.helicopters
                    title = "Выберите вертолет для редактирования"
                else:
                    return

                if not objects:
                    QMessageBox.information(self, "Информация", "Нет объектов для редактирования")
                    return

                # Диалог выбора объекта
                item, ok = QInputDialog.getItem(
                    self, title, "Объект:", [str(obj) for obj in objects], 0, False
                )

                if ok and item:
                    index = [str(obj) for obj in objects].index(item)
                    obj = objects[index]
                else:
                    return
            else:
                obj = None

            # Открываем диалог редактирования
            dialog = EditDialog(self, obj_type, obj)
            if dialog.exec_() == QDialog.Accepted:
                new_obj = dialog.get_data()

                if edit:
                    # Обновляем существующий объект
                    if obj_type == 'drone':
                        self.drones[index] = new_obj
                    elif obj_type == 'target':
                        self.targets[index] = new_obj
                    elif obj_type == 'airfield':
                        self.airfields[index] = new_obj
                    elif obj_type == 'helicopter':
                        self.helicopters[index] = new_obj
                else:
                    # Добавляем новый объект
                    if obj_type == 'drone':
                        self.drones.append(new_obj)
                    elif obj_type == 'target':
                        self.targets.append(new_obj)
                    elif obj_type == 'airfield':
                        self.airfields.append(new_obj)
                    elif obj_type == 'helicopter':
                        self.helicopters.append(new_obj)

                self.save_data()
                self.updateTable()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить объект:\n{str(e)}")

    def delete_object(self, obj_type):
        """Удаление объекта"""
        try:
            # Получаем список объектов для выбора
            if obj_type == 'drone':
                objects = self.drones
                title = "Выберите БПЛА для удаления"
            elif obj_type == 'target':
                objects = self.targets
                title = "Выберите цель для удаления"
            elif obj_type == 'airfield':
                objects = self.airfields
                title = "Выберите аэродром для удаления"
            elif obj_type == 'helicopter':
                objects = self.helicopters
                title = "Выберите вертолет для удаления"
            else:
                return

            if not objects:
                QMessageBox.information(self, "Информация", "Нет объектов для удаления")
                return

            # Диалог выбора объекта
            item, ok = QInputDialog.getItem(
                self, title, "Объект:", [str(obj) for obj in objects], 0, False
            )

            if ok and item:
                index = [str(obj) for obj in objects].index(item)

                # Подтверждение удаления
                reply = QMessageBox.question(
                    self, 'Подтверждение',
                    f'Вы действительно хотите удалить этот объект?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    if obj_type == 'drone':
                        del self.drones[index]
                    elif obj_type == 'target':
                        del self.targets[index]
                    elif obj_type == 'airfield':
                        del self.airfields[index]
                    elif obj_type == 'helicopter':
                        del self.helicopters[index]

                    self.save_data()
                    self.updateTable()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить объект:\n{str(e)}")

    def openSettingsDialog(self):
        """Открытие диалога настроек"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def apply_theme(self):
        """Применение выбранной темы"""
        palette = QPalette()

        if self.dark_theme:
            # Темная тема
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            # Светлая тема (стандартная)
            palette = QApplication.style().standardPalette()

        QApplication.setPalette(palette)
        self.updateTable()

    def calculateOptimalHelicopter(self, drone, zone):
        """Определение оптимального вертолета для перехвата"""
        if not self.helicopters:
            return None

        # Рассчитываем время, за которое БПЛА достигнет зоны
        drone_dist = self.haversine(drone.lat, drone.lon, zone['lat'], zone['lon'])
        drone_time = drone_dist / drone.speed_kmh  # в часах

        optimal_heli = None
        min_diff = float('inf')

        for heli in self.helicopters:
            # Рассчитываем время, за которое вертолет достигнет зоны
            heli_dist = self.haversine(heli.lat, heli.lon, zone['lat'], zone['lon'])
            heli_time = heli_dist / heli.speed_kmh + heli.prep_time_min / 60  # в часах

            # Разница во времени (должна быть отрицательной - вертолет должен прибыть раньше)
            time_diff = heli_time - drone_time

            # Ищем вертолет с минимальной разницей (но который успевает)
            if time_diff < -0.1 and abs(time_diff) < min_diff:  # минимум 6 минут запаса
                min_diff = abs(time_diff)
                optimal_heli = heli

        return optimal_heli

    def haversine(self, lat1, lon1, lat2, lon2):
        """Расчет расстояния между двумя точками на Земле в километрах"""
        R = 6371  # Радиус Земли в км
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) * math.sin(dLon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def getMinRemainingTime(self, target, current_time):
        """Получение минимального оставшегося времени для цели"""
        min_time = float('inf')
        for drone in self.drones:
            dist = self.haversine(drone.lat, drone.lon, target.lat, target.lon)
            hours = dist / drone.speed_kmh
            arrival = (drone.start_time.replace(year=current_time.year,
                                                month=current_time.month,
                                                day=current_time.day) +
                       timedelta(hours=hours))
            if arrival < drone.start_time:
                arrival += timedelta(days=1)
            remain = (arrival - current_time).total_seconds()
            if remain < min_time:
                min_time = remain
        return min_time if min_time != float('inf') else 0

    def sortTargets(self):
        """Переключение сортировки по времени"""
        self.sort_by_time = not self.sort_by_time
        self.updateTable()
        self.sortButton.setText("Сортировать по имени" if self.sort_by_time else
                                "Сортировать по остатку времени")

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        # Автоматическая настройка размера шрифта
        new_size = max(8, self.width() // 100)
        font = self.table.font()
        font.setPointSize(new_size)
        self.table.setFont(font)
        self.moscowTimeLabel.setFont(font)
        self.ekbTimeLabel.setFont(font)

    def updateTable(self):
        """Обновление данных в таблице"""
        # Получение текущего времени для разных часовых поясов
        now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
        now_ekb = datetime.now(pytz.timezone('Asia/Yekaterinburg'))

        # Обновление меток времени
        self.moscowTimeLabel.setText(f"МСК: {now_moscow.strftime('%H:%M:%S')}")
        self.ekbTimeLabel.setText(f"ЕКБ: {now_ekb.strftime('%H:%M:%S')}")

        # Создание копии списка целей для сортировки
        targets = self.targets.copy()
        if self.sort_by_time:
            targets.sort(key=lambda t: self.getMinRemainingTime(t, now_moscow))

        # Настройка столбцов таблицы
        columns = ['Объект']
        for drone in self.drones:
            columns += [
                f"{drone.name}\nРасстояние",
                f"t обнаружения  {drone.start_time.strftime('%H:%M')}\nРасчетное время",
                f"\nОстаток времени"
            ]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        drone_colors = self.getDroneColors()

        # Окрашивание заголовков столбцов для каждого БПЛА
        for idx, drone in enumerate(self.drones):
            base_col = 1 + idx * 3
            color = drone_colors[idx]
            for i in range(3):
                item = QTableWidgetItem(self.table.horizontalHeaderItem(base_col + i).text())
                item.setBackground(QBrush(color))
                if self.dark_theme:
                    item.setForeground(QBrush(Qt.black))
                self.table.setHorizontalHeaderItem(base_col + i, item)

        self.table.setRowCount(len(targets))

        # Заполнение таблицы данными
        for i, target in enumerate(targets):
            self.table.setItem(i, 0, QTableWidgetItem(target.name))

            for j, drone in enumerate(self.drones):
                # Расчет расстояния между БПЛА и объектом
                dist = self.haversine(drone.lat, drone.lon, target.lat, target.lon)
                hours = dist / drone.speed_kmh
                seconds = int(hours * 3600)

                # Расчет времени обнаружения
                today_start = now_moscow.replace(hour=drone.start_time.hour, minute=drone.start_time.minute,
                                                 second=0, microsecond=0)
                if today_start > now_moscow:
                    today_start -= timedelta(days=1)

                # Расчет времени прибытия
                arrival = today_start + timedelta(seconds=seconds)

                # Расчет оставшегося времени
                remain = arrival - now_moscow
                remain_seconds = int(remain.total_seconds())
                if remain_seconds < 0:
                    remain_seconds = 0

                # Форматирование времени
                h, remainder = divmod(remain_seconds, 3600)
                m, s = divmod(remainder, 60)
                remain_str = f"{h:02}:{m:02}:{s:02}"

                # Создание элементов таблицы с цветами
                dist_item = QTableWidgetItem(f"{dist:.1f}")
                dist_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                time_item = QTableWidgetItem(arrival.strftime('%H:%M:%S'))
                time_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                remain_item = QTableWidgetItem(remain_str)
                remain_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                # Подсветка срочных целей
                if remain_seconds <= 0:
                    remain_item.setForeground(Qt.white)
                    remain_item.setText("00:00:00")
                elif remain_seconds < 600:  # 10 минут
                    remain_item.setForeground(Qt.red)

                # Добавление элементов в таблицу
                self.table.setItem(i, 1 + j * 3, dist_item)
                self.table.setItem(i, 1 + j * 3 + 1, time_item)
                self.table.setItem(i, 1 + j * 3 + 2, remain_item)

        # Настройка отображения таблицы
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def openArmAviaDialog(self):
        """Открытие диалога расчета армейской авиации"""
        if not self.helicopters:
            QMessageBox.warning(self, "Ошибка", "Не добавлены вертолеты!")
            return

        if not self.airfields:
            QMessageBox.warning(self, "Ошибка", "Не добавлены аэродромы!")
            return

        if not self.drones:
            QMessageBox.warning(self, "Ошибка", "Не добавлены БПЛА!")
            return

        dialog = ArmyAviationDialog(self)
        dialog.exec_()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.save_data()
        self.save_settings()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DroneFlightGUI()
    ex.show()
    sys.exit(app.exec_())