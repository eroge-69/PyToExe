import sys
import math
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDialog, QTabWidget, QListWidget, QGridLayout, QLineEdit, QGroupBox,
                             QComboBox, QSpinBox, QInputDialog, QFileDialog)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator, QIntValidator
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

    def to_dict(self):
        return {
            'name': self.name,
            'lat': self.lat,
            'lon': self.lon
        }


class Drone(Location):
    """Класс для БПЛА с дополнительными параметрами"""

    def __init__(self, name, lat, lon, speed_kmh, start_time):
        super().__init__(name, lat, lon)
        self.speed_kmh = speed_kmh  # Скорость в км/ч
        self.start_time = start_time  # Время обнаружения

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon}) {self.speed_kmh} км/ч {self.start_time.strftime('%H:%M')}"

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'speed_kmh': self.speed_kmh,
            'start_time': self.start_time.strftime('%H:%M')
        })
        return data


class Helicopter:
    """Класс для вертолетов"""

    def __init__(self, name, speed_kmh, prep_time_min):
        self.name = name  # Название вертолета
        self.speed_kmh = speed_kmh  # Скорость в км/ч
        self.prep_time_min = prep_time_min  # Время подготовки к вылету в минутах

    def __str__(self):
        return f"{self.name} ({self.speed_kmh} км/ч, подготовка: {self.prep_time_min} мин)"

    def to_dict(self):
        return {
            'name': self.name,
            'speed_kmh': self.speed_kmh,
            'prep_time_min': self.prep_time_min
        }


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

    def to_dict(self):
        data = super().to_dict()
        data['zones'] = self.zones
        return data


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
        self.resultTable.setColumnCount(6)
        self.resultTable.setHorizontalHeaderLabels([
            "Аэродром",
            "Зона дежурства",
            "Время взлета вертолета",
            "Время входа БПЛА в зону",
            "Время дежурства в зоне",
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

            # Добавление строки в таблицу
            row = self.resultTable.rowCount()
            self.resultTable.insertRow(row)

            # Заполнение таблицы
            items = [
                QTableWidgetItem(airfield.name),
                QTableWidgetItem(zone['name']),
                QTableWidgetItem(takeoff_time.strftime('%H:%M:%S')),
                QTableWidgetItem(drone_time.strftime('%H:%M:%S')),
                QTableWidgetItem(f"{arrival_time.strftime('%H:%M:%S')} - {patrol_end_time.strftime('%H:%M:%S')}"),
                QTableWidgetItem(status)
            ]

            # Установка цветов в зависимости от статуса
            if status == "Истекло":
                color = QColor(255, 200, 200)  # Светло-красный
            elif status == "Дежурство":
                color = QColor(200, 255, 200)  # Светло-зеленый
            else:
                color = QColor(240, 240, 240)  # Светло-серый

            for i, item in enumerate(items):
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
                "Аэродром", "Зона дежурства", "Время взлета",
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

        self.initUI()  # Инициализация интерфейса
        self.loadData()  # Загрузка данных
        self.updateTable()  # Обновление таблицы

        # Настройка таймера для обновления времени каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTable)
        self.timer.start(1000)

    def getDroneColors(self):
        """Генерация цветов для отображения БПЛА"""
        colors = [
            QColor(96, 205, 230),  # Первый цвет (голубой)
        ]
        # Генерация дополнительных цветов при необходимости
        while len(colors) < len(self.drones):
            colors.append(QColor.fromHsv(len(colors) * 70 % 188, 77, 146))
        return colors

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

        # Layout для кнопок управления
        btnLayout = QHBoxLayout()
        editButton = QPushButton('Редактировать')
        editButton.clicked.connect(self.openEditDialog)

        self.armyButton = QPushButton('Расчет взлета армейской авиации')
        self.armyButton.clicked.connect(self.openArmAviaDialog)

        self.sortButton = QPushButton('Сортировать по остатку времени')
        self.sortButton.clicked.connect(self.sortTargets)

        btnLayout.addWidget(editButton)
        btnLayout.addWidget(self.armyButton)
        btnLayout.addWidget(self.sortButton)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

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
                f"Расчетное\nвремя",
                f"Остаток\nвремени"
            ]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        drone_colors = self.getDroneColors()

        # Окрашивание заголовков столбцов для каждого БПЛА
        for idx, drone in enumerate(self.drones):
            base_col = 1 + idx * 3
            color = drone_colors[idx]
            for i in range(3):
                item = self.table.horizontalHeaderItem(base_col + i)
                if item:
                    item.setBackground(QBrush(color))

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

    def openEditDialog(self):
        """Окно редактирования всех объектов"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование объектов")
        dialog.resize(1000, 600)

        # Создание вкладок
        tabs = QTabWidget()

        # Создание вкладок для каждого типа объектов
        droneTab = self.createListTab("Цель", self.drones, self.createDroneDialog)
        targetTab = self.createListTab("объекты", self.targets, self.createTargetDialog)
        heliTab = self.createListTab("Вертолеты", self.helicopters, self.createHelicopterDialog)
        airfieldTab = self.createAirfieldTab()

        # Добавление вкладок
        tabs.addTab(droneTab, "БПЛА")
        tabs.addTab(targetTab, "Объект")
        tabs.addTab(heliTab, "Вертолеты")
        tabs.addTab(airfieldTab, "Аэродромы")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        dialog.setLayout(layout)
        dialog.exec_()

    def createAirfieldTab(self):
        """Создание вкладки для аэродромов"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Список аэродромов
        self.airfieldList = QListWidget()
        for airfield in self.airfields:
            self.airfieldList.addItem(str(airfield))
        layout.addWidget(self.airfieldList)

        # Кнопки управления аэродромами
        airfieldBtnLayout = QHBoxLayout()
        addAirfieldBtn = QPushButton("Добавить аэродром")
        editAirfieldBtn = QPushButton("Редактировать аэродром")
        removeAirfieldBtn = QPushButton("Удалить аэродром")

        addAirfieldBtn.clicked.connect(self.addAirfield)
        editAirfieldBtn.clicked.connect(self.editAirfield)
        removeAirfieldBtn.clicked.connect(self.removeAirfield)

        airfieldBtnLayout.addWidget(addAirfieldBtn)
        airfieldBtnLayout.addWidget(editAirfieldBtn)
        airfieldBtnLayout.addWidget(removeAirfieldBtn)
        layout.addLayout(airfieldBtnLayout)

        # Кнопки управления зонами
        zoneBtnLayout = QHBoxLayout()
        addZoneBtn = QPushButton("Добавить зону")
        editZoneBtn = QPushButton("Редактировать зону")
        removeZoneBtn = QPushButton("Удалить зону")

        addZoneBtn.clicked.connect(self.addZone)
        editZoneBtn.clicked.connect(self.editZone)
        removeZoneBtn.clicked.connect(self.removeZone)

        zoneBtnLayout.addWidget(addZoneBtn)
        zoneBtnLayout.addWidget(editZoneBtn)
        zoneBtnLayout.addWidget(removeZoneBtn)
        layout.addLayout(zoneBtnLayout)

        widget.setLayout(layout)
        return widget

    def createHelicopterDialog(self, helicopter=None):
        """Диалог для редактирования вертолетов"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать вертолет" if helicopter else "Добавить вертолет")

        layout = QGridLayout()
        # Поля ввода
        nameEdit = QLineEdit(helicopter.name if helicopter else "")
        speedEdit = QLineEdit(str(helicopter.speed_kmh) if helicopter else "250")
        prepTimeEdit = QLineEdit(str(helicopter.prep_time_min) if helicopter else "15")

        # Валидаторы
        speedEdit.setValidator(QDoubleValidator(100, 500, 0))
        prepTimeEdit.setValidator(QIntValidator(0, 120))

        # Добавление полей в layout
        layout.addWidget(QLabel("Название:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Скорость (км/ч):"), 1, 0)
        layout.addWidget(speedEdit, 1, 1)
        layout.addWidget(QLabel("Время подготовки (мин):"), 2, 0)
        layout.addWidget(prepTimeEdit, 2, 1)

        # Кнопки
        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            """Обработчик нажатия OK"""
            try:
                # Проверка данных
                speed = float(speedEdit.text())
                prep_time = int(prepTimeEdit.text())

                # Создание объекта
                dialog.result = Helicopter(
                    nameEdit.text(),
                    speed,
                    prep_time
                )
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", str(e))

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 3, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog

    def addAirfield(self):
        """Добавление нового аэродрома"""
        dialog = self.createAirfieldDialog()
        if dialog.exec_():
            self.airfields.append(dialog.result)
            self.airfieldList.addItem(str(dialog.result))
            self.saveData()

    def editAirfield(self):
        """Редактирование существующего аэродрома"""
        idx = self.airfieldList.currentRow()
        if idx >= 0:
            dialog = self.createAirfieldDialog(self.airfields[idx])
            if dialog.exec_():
                self.airfields[idx] = dialog.result
                self.airfieldList.item(idx).setText(str(dialog.result))
                self.saveData()

    def removeAirfield(self):
        """Удаление аэродрома"""
        idx = self.airfieldList.currentRow()
        if idx >= 0:
            self.airfieldList.takeItem(idx)
            del self.airfields[idx]
            self.saveData()

    def addZone(self):
        """Добавление новой зоны"""
        idx = self.airfieldList.currentRow()
        if idx >= 0:
            dialog = self.createZoneDialog()
            if dialog.exec_():
                airfield = self.airfields[idx]
                airfield.add_zone(
                    dialog.result['name'],
                    dialog.result['lat'],
                    dialog.result['lon'],
                    dialog.result['duration']
                )
                self.airfieldList.item(idx).setText(str(airfield))
                self.saveData()

    def editZone(self):
        """Редактирование зоны"""
        airfield_idx = self.airfieldList.currentRow()
        if airfield_idx >= 0:
            airfield = self.airfields[airfield_idx]
            if not airfield.zones:
                QMessageBox.information(self, "Информация", "У этого аэродрома нет зон")
                return

            # Диалог выбора зоны для редактирования
            zone_names = [z['name'] for z in airfield.zones]
            zone_name, ok = QInputDialog.getItem(
                self, "Выбор зоны", "Выберите зону для редактирования:", zone_names, 0, False
            )

            if ok and zone_name:
                zone_idx = next(i for i, z in enumerate(airfield.zones) if z['name'] == zone_name)
                zone = airfield.zones[zone_idx]

                dialog = self.createZoneDialog(zone)
                if dialog.exec_():
                    # Обновляем данные зоны
                    airfield.zones[zone_idx] = {
                        'name': dialog.result['name'],
                        'lat': dialog.result['lat'],
                        'lon': dialog.result['lon'],
                        'patrol_duration': dialog.result['duration']
                    }
                    self.airfieldList.item(airfield_idx).setText(str(airfield))
                    self.saveData()

    def removeZone(self):
        """Удаление зоны"""
        airfield_idx = self.airfieldList.currentRow()
        if airfield_idx >= 0:
            airfield = self.airfields[airfield_idx]
            if not airfield.zones:
                QMessageBox.information(self, "Информация", "У этого аэродрома нет зон")
                return

            # Диалог выбора зоны для удаления
            zone_names = [z['name'] for z in airfield.zones]
            zone_name, ok = QInputDialog.getItem(
                self, "Выбор зоны", "Выберите зону для удаления:", zone_names, 0, False
            )

            if ok and zone_name:
                zone_idx = next(i for i, z in enumerate(airfield.zones) if z['name'] == zone_name)
                airfield.zones.pop(zone_idx)
                self.airfieldList.item(airfield_idx).setText(str(airfield))
                self.saveData()

    def createAirfieldDialog(self, airfield=None):
        """Диалог для редактирования аэродрома"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать аэродром" if airfield else "Добавить аэродром")

        layout = QGridLayout()
        # Поля ввода
        nameEdit = QLineEdit(airfield.name if airfield else "")
        latEdit = QLineEdit(str(airfield.lat) if airfield else "")
        lonEdit = QLineEdit(str(airfield.lon) if airfield else "")

        # Добавление полей в layout
        layout.addWidget(QLabel("Название:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Широта:"), 1, 0)
        layout.addWidget(latEdit, 1, 1)
        layout.addWidget(QLabel("Долгота:"), 2, 0)
        layout.addWidget(lonEdit, 2, 1)

        # Кнопки
        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            """Обработчик нажатия OK"""
            try:
                # Проверка координат
                lat = float(latEdit.text())
                lon = float(lonEdit.text())
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Некорректные координаты")

                # Создание объекта
                dialog.result = AirfieldWithZones(nameEdit.text(), lat, lon)
                # Копируем зоны из старого объекта, если он был
                if airfield:
                    for zone in airfield.zones:
                        dialog.result.add_zone(zone['name'], zone['lat'], zone['lon'], zone['patrol_duration'])

                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", str(e))

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 3, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog

    def createZoneDialog(self, zone=None):
        """Диалог для редактирования зоны дежурства"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать зону" if zone else "Добавить зону")

        layout = QGridLayout()
        # Поля ввода
        nameEdit = QLineEdit(zone['name'] if zone else "")
        latEdit = QLineEdit(str(zone['lat']) if zone else "")
        lonEdit = QLineEdit(str(zone['lon']) if zone else "")
        durationEdit = QSpinBox()
        durationEdit.setRange(1, 1000)
        durationEdit.setValue(zone['patrol_duration'] if zone else 60)

        # Добавление полей в layout
        layout.addWidget(QLabel("Название:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Широта:"), 1, 0)
        layout.addWidget(latEdit, 1, 1)
        layout.addWidget(QLabel("Долгота:"), 2, 0)
        layout.addWidget(lonEdit, 2, 1)
        layout.addWidget(QLabel("Время дежурства (мин):"), 3, 0)
        layout.addWidget(durationEdit, 3, 1)

        # Кнопки
        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            """Обработчик нажатия OK"""
            try:
                # Проверка координат
                lat = float(latEdit.text())
                lon = float(lonEdit.text())
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Некорректные координаты")

                # Создание объекта
                dialog.result = {
                    'name': nameEdit.text(),
                    'lat': lat,
                    'lon': lon,
                    'duration': durationEdit.value()
                }
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", str(e))

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 4, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog

    def createListTab(self, title, items, createDialogFunc):
        """Создание вкладки со списком объектов"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Список объектов
        listWidget = QListWidget()
        for item in items:
            listWidget.addItem(str(item))

        # Кнопки управления
        btnLayout = QHBoxLayout()
        addBtn = QPushButton("Добавить")
        editBtn = QPushButton("Редактировать")
        removeBtn = QPushButton("Удалить")

        # Подключение обработчиков
        addBtn.clicked.connect(lambda: self.addItem(listWidget, items, createDialogFunc))
        editBtn.clicked.connect(lambda: self.editItem(listWidget, items, createDialogFunc))
        removeBtn.clicked.connect(lambda: self.removeItem(listWidget, items))

        btnLayout.addWidget(addBtn)
        btnLayout.addWidget(editBtn)
        btnLayout.addWidget(removeBtn)

        # Компоновка элементов
        layout.addWidget(listWidget)
        layout.addLayout(btnLayout)
        widget.setLayout(layout)
        return widget

    def addItem(self, listWidget, items, createDialogFunc):
        """Добавление нового объекта"""
        dialog = createDialogFunc()
        if dialog.exec_():
            items.append(dialog.result)
            listWidget.addItem(str(dialog.result))
            self.saveData()

    def editItem(self, listWidget, items, createDialogFunc):
        """Редактирование существующего объекта"""
        idx = listWidget.currentRow()
        if idx >= 0:
            dialog = createDialogFunc(items[idx])
            if dialog.exec_():
                items[idx] = dialog.result
                listWidget.item(idx).setText(str(dialog.result))
                self.saveData()

    def removeItem(self, listWidget, items):
        """Удаление объекта"""
        idx = listWidget.currentRow()
        if idx >= 0:
            listWidget.takeItem(idx)
            del items[idx]
            self.saveData()

    def createDroneDialog(self, drone=None):
        """Диалог для редактирования БПЛА"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать БПЛА" if drone else "Добавить БПЛА")

        layout = QGridLayout()
        # Поля ввода
        nameEdit = QLineEdit(drone.name if drone else "")
        latEdit = QLineEdit(str(drone.lat) if drone else "")
        lonEdit = QLineEdit(str(drone.lon) if drone else "")
        speedEdit = QLineEdit(str(drone.speed_kmh) if drone else "")
        startTimeEdit = QLineEdit(drone.start_time.strftime('%H:%M') if drone else "")

        # Добавление полей в layout
        layout.addWidget(QLabel("Имя:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Широта:"), 1, 0)
        layout.addWidget(latEdit, 1, 1)
        layout.addWidget(QLabel("Долгота:"), 2, 0)
        layout.addWidget(lonEdit, 2, 1)
        layout.addWidget(QLabel("Скорость (км/ч):"), 3, 0)
        layout.addWidget(speedEdit, 3, 1)
        layout.addWidget(QLabel("Время обнаружения (HH:MM):"), 4, 0)
        layout.addWidget(startTimeEdit, 4, 1)

        # Кнопки
        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            """Обработчик нажатия OK"""
            try:
                # Проверка и сохранение данных
                result = Drone(
                    nameEdit.text(),
                    float(latEdit.text()),
                    float(lonEdit.text()),
                    float(speedEdit.text()),
                    datetime.strptime(startTimeEdit.text(), "%H:%M").time()
                )
                dialog.result = result
                dialog.accept()
            except Exception:
                QMessageBox.critical(dialog, "Ошибка", "Некорректный ввод!")

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 5, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog

    def createTargetDialog(self, target=None):
        """Диалог для редактирования целей"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактировать объект" if target else "Добавить объект")

        layout = QGridLayout()
        # Поля ввода
        nameEdit = QLineEdit(target.name if target else "")
        latEdit = QLineEdit(str(target.lat) if target else "")
        lonEdit = QLineEdit(str(target.lon) if target else "")

        # Добавление полей в layout
        layout.addWidget(QLabel("Название:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Широта:"), 1, 0)
        layout.addWidget(latEdit, 1, 1)
        layout.addWidget(QLabel("Долгота:"), 2, 0)
        layout.addWidget(lonEdit, 2, 1)

        # Кнопки
        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            """Обработчик нажатия OK"""
            try:
                # Проверка координат
                lat = float(latEdit.text())
                lon = float(lonEdit.text())
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Некорректные координаты")

                # Создание объекта
                dialog.result = Target(
                    nameEdit.text(),
                    lat,
                    lon
                )
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", str(e))

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 3, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog

    def haversine(self, lat1, lon1, lat2, lon2):
        """Расчет расстояния между двумя точками на сфере (в км)"""
        # Конвертация градусов в радианы
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Формула гаверсинусов
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Радиус Земли в километрах
        r = 6371
        return c * r

    def getMinRemainingTime(self, target, now):
        """Получение минимального оставшегося времени для цели"""
        min_time = float('inf')
        for drone in self.drones:
            dist = self.haversine(drone.lat, drone.lon, target.lat, target.lon)
            hours = dist / drone.speed_kmh
            seconds = int(hours * 3600)

            today_start = now.replace(hour=drone.start_time.hour, minute=drone.start_time.minute,
                                      second=0, microsecond=0)
            if today_start > now:
                today_start -= timedelta(days=1)

            arrival = today_start + timedelta(seconds=seconds)
            remain = (arrival - now).total_seconds()

            if remain < min_time:
                min_time = remain

        return min_time if min_time != float('inf') else 0

    def sortTargets(self):
        """Переключение режима сортировки целей"""
        self.sort_by_time = not self.sort_by_time
        if self.sort_by_time:
            self.sortButton.setText("Сортировать по имени")
        else:
            self.sortButton.setText("Сортировать по остатку времени")
        self.updateTable()

    def loadData(self):
        """Загрузка данных из файлов"""
        try:
            # Создаем папку для данных, если ее нет
            if not os.path.exists('data'):
                os.makedirs('data')

            # Загрузка БПЛА
            if os.path.exists('data/drones.txt'):
                with open('data/drones.txt', 'r', encoding='utf-8') as f:
                    drones_data = json.loads(f.read())
                    self.drones = [
                        Drone(
                            item['name'],
                            item['lat'],
                            item['lon'],
                            item['speed_kmh'],
                            datetime.strptime(item['start_time'], '%H:%M').time()
                        ) for item in drones_data
                    ]

            # Загрузка целей
            if os.path.exists('data/targets.txt'):
                with open('data/targets.txt', 'r', encoding='utf-8') as f:
                    targets_data = json.loads(f.read())
                    self.targets = [
                        Target(item['name'], item['lat'], item['lon'])
                        for item in targets_data
                    ]

            # Загрузка вертолетов
            if os.path.exists('data/helicopters.txt'):
                with open('data/helicopters.txt', 'r', encoding='utf-8') as f:
                    helicopters_data = json.loads(f.read())
                    self.helicopters = [
                        Helicopter(
                            item['name'],
                            item['speed_kmh'],
                            item['prep_time_min']
                        ) for item in helicopters_data
                    ]

            # Загрузка аэродромов
            if os.path.exists('data/airfields.txt'):
                with open('data/airfields.txt', 'r', encoding='utf-8') as f:
                    airfields_data = json.loads(f.read())
                    self.airfields = []
                    for item in airfields_data:
                        airfield = AirfieldWithZones(item['name'], item['lat'], item['lon'])
                        for zone in item.get('zones', []):
                            airfield.add_zone(
                                zone['name'],
                                zone['lat'],
                                zone['lon'],
                                zone['patrol_duration']
                            )
                        self.airfields.append(airfield)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))
            # Загрузка тестовых данных при ошибке
            self.loadTestData()

    def loadTestData(self):
        """Загрузка тестовых данных"""
        try:
            # Тестовые БПЛА
            self.drones = [
                Drone("БПЛА-1", 56.5, 60.5, 100, datetime.strptime("10:00", "%H:%M").time()),
                Drone("БПЛА-2", 57.0, 61.0, 120, datetime.strptime("09:30", "%H:%M").time())
            ]

            # Тестовые цели
            self.targets = [
                Target("Саратов", 56.8, 60.8),
                Target("Екатеринбург", 57.2, 61.2),
                Target("Балашов", 51.554601, 43.146478),
                Target("Ртищево", 52.257455, 43.785657),
            ]

            # Тестовые вертолеты
            self.helicopters = [
                Helicopter("Ми-28", 250, 15),
                Helicopter("Ка-52", 300, 10)
            ]

            # Тестовые аэродромы с зонами
            airfield = AirfieldWithZones("Аэродром 1", 56.6, 60.6)
            airfield.add_zone("Зона 1", 56.7, 60.7, 60)
            airfield.add_zone("Зона 2", 56.9, 60.9, 90)
            self.airfields = [airfield]

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки тестовых данных", str(e))

    def saveData(self):
        """Сохранение данных в файлы"""
        try:
            # Создаем папку для данных, если ее нет
            if not os.path.exists('data'):
                os.makedirs('data')

            # Сохранение БПЛА
            with open('data/drones.txt', 'w', encoding='utf-8') as f:
                f.write(json.dumps([drone.to_dict() for drone in self.drones], ensure_ascii=False, indent=4))

            # Сохранение объектов
            with open('data/targets.txt', 'w', encoding='utf-8') as f:
                f.write(json.dumps([target.to_dict() for target in self.targets], ensure_ascii=False, indent=4))

            # Сохранение вертолетов
            with open('data/helicopters.txt', 'w', encoding='utf-8') as f:
                f.write(json.dumps([heli.to_dict() for heli in self.helicopters], ensure_ascii=False, indent=4))

            # Сохранение аэродромов
            with open('data/airfields.txt', 'w', encoding='utf-8') as f:
                f.write(json.dumps([airfield.to_dict() for airfield in self.airfields], ensure_ascii=False, indent=4))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения данных", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DroneFlightGUI()
    ex.show()
    sys.exit(app.exec_())
