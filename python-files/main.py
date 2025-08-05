import sys
import math
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDialog, QTabWidget, QListWidget, QGridLayout, QLineEdit)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QBrush
from datetime import datetime, timedelta
import pytz


class Drone:
    def __init__(self, name, lat, lon, speed_kmh, start_time):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.speed_kmh = speed_kmh
        self.start_time = start_time

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon}) {self.speed_kmh} км/ч {self.start_time.strftime('%H:%M')}"


class Target:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon})"


class DroneFlightGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drones = []
        self.targets = []
        self.sort_by_time = False

        self.initUI()
        self.loadData()
        self.updateTable()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTable)
        self.timer.start(1000)

    def getDroneColors(self):
        colors = [

            QColor(96, 205, 230),  # первой
        ]
        while len(colors) < len(self.drones):
            colors.append(QColor.fromHsv(len(colors) * 70 % 188, 77, 146))
        return colors

    def initUI(self):
        self.setWindowTitle('Расчет подлета БПЛА')
        self.resize(1200, 600)

        layout = QVBoxLayout()

        timeLayout = QHBoxLayout()
        self.moscowTimeLabel = QLabel()
        self.ekbTimeLabel = QLabel()
        timeLayout.addWidget(self.moscowTimeLabel)
        timeLayout.addWidget(self.ekbTimeLabel)
        layout.addLayout(timeLayout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        btnLayout = QHBoxLayout()
        editButton = QPushButton('Редактировать')
        editButton.clicked.connect(self.openEditDialog)

        self.armyButton = QPushButton('Расчет взлета армейской авиации')
        self.armyButton.setEnabled(False)

        self.sortButton = QPushButton('Сортировать по остатку времени')
        self.sortButton.clicked.connect(self.sortTargets)

        btnLayout.addWidget(editButton)
        btnLayout.addWidget(self.armyButton)
        btnLayout.addWidget(self.sortButton)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_size = max(8, self.width() // 100)
        font = self.table.font()
        font.setPointSize(new_size)
        self.table.setFont(font)
        self.moscowTimeLabel.setFont(font)
        self.ekbTimeLabel.setFont(font)

    def updateTable(self):
        now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
        now_ekb = datetime.now(pytz.timezone('Asia/Yekaterinburg'))

        self.moscowTimeLabel.setText(f"МСК: {now_moscow.strftime('%H:%M:%S')}")
        self.ekbTimeLabel.setText(f"ЕКБ: {now_ekb.strftime('%H:%M:%S')}")

        targets = self.targets.copy()
        if self.sort_by_time:
            targets.sort(key=lambda t: self.getMinRemainingTime(t, now_moscow))

        columns = ['Объект']
        for drone in self.drones:
            columns += [f"{drone.name}\nРасстояние", f"обнаружен  {drone.start_time.strftime('%H:%M')}\nРасчетное время", f"\nОстаток времени"]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        drone_colors = self.getDroneColors()

        # Окрашиваем заголовки БПЛА
        for idx, drone in enumerate(self.drones):
            base_col = 1 + idx * 3
            color = drone_colors[idx]
            for i in range(3):
                item = self.table.horizontalHeaderItem(base_col + i)
                if item:
                    item.setBackground(QBrush(color))

        self.table.setRowCount(len(targets))

        for i, target in enumerate(targets):
            self.table.setItem(i, 0, QTableWidgetItem(target.name))
            for j, drone in enumerate(self.drones):
                dist = self.haversine(drone.lat, drone.lon, target.lat, target.lon)
                hours = dist / drone.speed_kmh
                seconds = int(hours * 3600)

                today_start = now_moscow.replace(hour=drone.start_time.hour, minute=drone.start_time.minute,
                                                 second=0, microsecond=0)
                if today_start > now_moscow:
                    today_start -= timedelta(days=1)  # Keep this if drone spotted "yesterday"

                arrival = today_start + timedelta(seconds=seconds)

                remain = arrival - now_moscow
                remain_seconds = int(remain.total_seconds())
                if remain_seconds < 0:
                    remain_seconds = 0

                h, remainder = divmod(remain_seconds, 3600)
                m, s = divmod(remainder, 60)
                remain_str = f"{h:02}:{m:02}:{s:02}"

                dist_item = QTableWidgetItem(f"{dist:.1f}")
                dist_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                time_item = QTableWidgetItem(arrival.strftime('%H:%M:%S'))
                time_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                remain_item = QTableWidgetItem(remain_str)
                remain_item.setBackground(QBrush(drone_colors[j].lighter(140)))

                if remain_seconds <= 0:
                    remain_item.setForeground(Qt.white)
                    remain_item.setText("00:00:00")
                elif remain_seconds < 600:
                    remain_item.setForeground(Qt.red)

                self.table.setItem(i, 1 + j * 3, dist_item)
                self.table.setItem(i, 1 + j * 3 + 1, time_item)
                self.table.setItem(i, 1 + j * 3 + 2, remain_item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def sortTargets(self):
        self.sort_by_time = not self.sort_by_time
        self.sortButton.setText("Отключить сортировку" if self.sort_by_time else "Сортировать по остатку времени")
        self.updateTable()

    def getMinRemainingTime(self, target, now_moscow):
        min_remain = timedelta.max
        for drone in self.drones:
            dist = self.haversine(drone.lat, drone.lon, target.lat, target.lon)
            hours = dist / drone.speed_kmh
            seconds = int(hours * 3600)

            today_start = now_moscow.replace(hour=drone.start_time.hour, minute=drone.start_time.minute,
                                             second=0, microsecond=0)
            if today_start > now_moscow:
                today_start -= timedelta(days=1)

            arrival = today_start + timedelta(seconds=seconds)
            remain = arrival - now_moscow

            if remain.total_seconds() < 0:
                remain = timedelta(seconds=0)

            if remain < min_remain:
                min_remain = remain

        return min_remain

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def loadData(self):
        if os.path.exists('drones.txt'):
            with open('drones.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(';')
                    if len(parts) == 5:
                        self.drones.append(Drone(parts[0], float(parts[1]), float(parts[2]), float(parts[3]),
                                                 datetime.strptime(parts[4], '%H:%M').time()))
        if os.path.exists('targets.txt'):
            with open('targets.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(';')
                    if len(parts) == 3:
                        self.targets.append(Target(parts[0], float(parts[1]), float(parts[2])))

        if not self.targets:
            self.addDefaultTargets()

    def saveData(self):
        with open('drones.txt', 'w', encoding='utf-8') as f:
            for drone in self.drones:
                f.write(f"{drone.name};{drone.lat};{drone.lon};{drone.speed_kmh};{drone.start_time.strftime('%H:%M')}\n")

        with open('targets.txt', 'w', encoding='utf-8') as f:
            for target in self.targets:
                f.write(f"{target.name};{target.lat};{target.lon}\n")

    def addDefaultTargets(self):
        defaults = [
            ("Нижний Новгород", 56.2965, 44.0010),
            ("Самара", 53.1959, 50.1008),
            ("Саратов", 51.5331, 46.0342),
            ("Волгоград", 48.7071, 44.5169),
            ("Ульяновск", 54.3142, 48.4031),
            ("Пенза", 53.1950, 45.0183),
            ("Челябинск", 55.1644, 61.4368),
            ("Пермь", 58.0105, 56.2502),
            ("Тюмень", 57.1522, 65.5272),
            ("Оренбург", 51.7875, 55.1010),
            ("Уфа", 54.7388, 55.9721),
        ]
        for name, lat, lon in defaults:
            self.targets.append(Target(name, lat, lon))

    def openEditDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование")
        dialog.resize(700, 400)

        tabs = QTabWidget()

        # Drone Tab
        droneList = QListWidget()
        for drone in self.drones:
            droneList.addItem(str(drone))

        droneBtns = QHBoxLayout()
        addDroneBtn = QPushButton("Добавить")
        editDroneBtn = QPushButton("Редактировать")
        removeDroneBtn = QPushButton("Удалить")
        droneBtns.addWidget(addDroneBtn)
        droneBtns.addWidget(editDroneBtn)
        droneBtns.addWidget(removeDroneBtn)

        droneTab = QVBoxLayout()
        droneTab.addWidget(droneList)
        droneTab.addLayout(droneBtns)

        droneWidget = QWidget()
        droneWidget.setLayout(droneTab)

        # Target Tab
        targetList = QListWidget()
        for target in self.targets:
            targetList.addItem(str(target))

        targetBtns = QHBoxLayout()
        addTargetBtn = QPushButton("Добавить")
        editTargetBtn = QPushButton("Редактировать")
        removeTargetBtn = QPushButton("Удалить")
        targetBtns.addWidget(addTargetBtn)
        targetBtns.addWidget(editTargetBtn)
        targetBtns.addWidget(removeTargetBtn)

        targetTab = QVBoxLayout()
        targetTab.addWidget(targetList)
        targetTab.addLayout(targetBtns)

        targetWidget = QWidget()
        targetWidget.setLayout(targetTab)

        tabs.addTab(droneWidget, "БПЛА")
        tabs.addTab(targetWidget, "Цели")

        # Functions for editing lists:
        def addDrone():
            dialog2 = self.createDroneDialog()
            if dialog2.exec_():
                self.drones.append(dialog2.result)
                droneList.addItem(str(dialog2.result))
                self.saveData()
                self.updateTable()

        def editDrone():
            idx = droneList.currentRow()
            if idx >= 0:
                dialog2 = self.createDroneDialog(self.drones[idx])
                if dialog2.exec_():
                    self.drones[idx] = dialog2.result
                    droneList.item(idx).setText(str(dialog2.result))
                    self.saveData()
                    self.updateTable()

        def removeDrone():
            idx = droneList.currentRow()
            if idx >= 0:
                droneList.takeItem(idx)
                del self.drones[idx]
                self.saveData()
                self.updateTable()

        addDroneBtn.clicked.connect(addDrone)
        editDroneBtn.clicked.connect(editDrone)
        removeDroneBtn.clicked.connect(removeDrone)

        def addTarget():
            dialog2 = self.createTargetDialog()
            if dialog2.exec_():
                self.targets.append(dialog2.result)
                targetList.addItem(str(dialog2.result))
                self.saveData()
                self.updateTable()

        def editTarget():
            idx = targetList.currentRow()
            if idx >= 0:
                dialog2 = self.createTargetDialog(self.targets[idx])
                if dialog2.exec_():
                    self.targets[idx] = dialog2.result
                    targetList.item(idx).setText(str(dialog2.result))
                    self.saveData()
                    self.updateTable()

        def removeTarget():
            idx = targetList.currentRow()
            if idx >= 0:
                targetList.takeItem(idx)
                del self.targets[idx]
                self.saveData()
                self.updateTable()

        addTargetBtn.clicked.connect(addTarget)
        editTargetBtn.clicked.connect(editTarget)
        removeTargetBtn.clicked.connect(removeTarget)

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        dialog.setLayout(layout)
        dialog.exec_()

    def createDroneDialog(self, drone=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать БПЛА" if drone else "Добавить БПЛА")

        layout = QGridLayout()
        nameEdit = QLineEdit(drone.name if drone else "")
        latEdit = QLineEdit(str(drone.lat) if drone else "")
        lonEdit = QLineEdit(str(drone.lon) if drone else "")
        speedEdit = QLineEdit(str(drone.speed_kmh) if drone else "")
        startTimeEdit = QLineEdit(drone.start_time.strftime('%H:%M') if drone else "")

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

        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            try:
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
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать Цель" if target else "Добавить Цель")

        layout = QGridLayout()
        nameEdit = QLineEdit(target.name if target else "")
        latEdit = QLineEdit(str(target.lat) if target else "")
        lonEdit = QLineEdit(str(target.lon) if target else "")

        layout.addWidget(QLabel("Название:"), 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(QLabel("Широта:"), 1, 0)
        layout.addWidget(latEdit, 1, 1)
        layout.addWidget(QLabel("Долгота:"), 2, 0)
        layout.addWidget(lonEdit, 2, 1)

        btns = QHBoxLayout()
        okBtn = QPushButton("OK")
        cancelBtn = QPushButton("Отмена")
        btns.addWidget(okBtn)
        btns.addWidget(cancelBtn)

        def accept():
            try:
                result = Target(
                    nameEdit.text(),
                    float(latEdit.text()),
                    float(lonEdit.text())
                )
                dialog.result = result
                dialog.accept()
            except Exception:
                QMessageBox.critical(dialog, "Ошибка", "Некорректный ввод!")

        okBtn.clicked.connect(accept)
        cancelBtn.clicked.connect(dialog.reject)

        layout.addLayout(btns, 3, 0, 1, 2)
        dialog.setLayout(layout)
        return dialog


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DroneFlightGUI()
    window.show()
    sys.exit(app.exec_())


