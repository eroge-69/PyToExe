# MyApp_fixed.py
# -*- coding: utf-8 -*-

import ifcopenshell
import ifcopenshell.geom
import pyvista as pv
from pyvistaqt import QtInteractor  # <-- исправленный импорт
import numpy as np
import csv
import os
import time
import random
import threading
import sys
from PyQt5 import QtWidgets, QtCore

SENSOR_DATA_FILE = 'sensor_data.csv'

# ----------------------------
# 1. DATA SIMULATOR
# ----------------------------
def simulate_iot_sensor(stop_event):
    print("Запуск симулятора данных IoT...")
    with open(SENSOR_DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'pressure', 'vibration'])
    while not stop_event.is_set():
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        temperature = round(random.uniform(18.0, 30.0), 2)
        pressure = round(random.uniform(1.0, 5.0), 2)
        vibration = round(random.uniform(0.0, 1.0), 2)
        try:
            with open(SENSOR_DATA_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([current_time, temperature, pressure, vibration])
        except (IOError, PermissionError):
            pass
        time.sleep(2)
    print("Симулятор остановлен.")


# ----------------------------
# 2. IFC VIEWER APP
# ----------------------------
class IFCViewerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("РИФ-200 Digital Twin 0.0.1")

        # PyVista QtInteractor
        self.plotter = QtInteractor(self)
        self.setCentralWidget(self.plotter)

        self.ifc_mesh = None
        self.sensors = {}
        self.sensor_id_counter = 0
        self.add_sensor_mode = False

        # QTimer для обновления датчиков
        self.timer = QtCore.QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start()

        # Меню
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")
        load_action = QtWidgets.QAction("Загрузить IFC", self)
        load_action.triggered.connect(self.get_ifc_file)
        file_menu.addAction(load_action)

        sensor_menu = menu_bar.addMenu("Датчики")
        add_sensor_action = QtWidgets.QAction("Добавить датчик", self)
        add_sensor_action.triggered.connect(self.activate_add_sensor_mode)
        sensor_menu.addAction(add_sensor_action)

    def get_ifc_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите IFC файл", "", "IFC Files (*.ifc)"
        )
        if file_path:
            self.load_ifc_model(file_path)
            self.setup_interaction()

    def load_ifc_model(self, path):
        try:
            ifc_file = ifcopenshell.open(path)
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            iterator = ifcopenshell.geom.iterator(settings, ifc_file, 4)

            all_vertices, all_faces, v_offset = [], [], 0
            print("Загрузка геометрии IFC...")
            for shape in iterator:
                if shape.geometry.verts:
                    verts = np.array(shape.geometry.verts).reshape(-1, 3)
                    faces = np.array(shape.geometry.faces).reshape(-1, 3)
                    faces_with_count = np.hstack((np.full((faces.shape[0], 1), 3), faces + v_offset))
                    all_vertices.append(verts)
                    all_faces.append(faces_with_count)
                    v_offset += len(verts)
            if not all_vertices:
                print("Геометрия в IFC не найдена.")
                return
            self.ifc_mesh = pv.PolyData(np.vstack(all_vertices), np.vstack(all_faces))
            self.plotter.add_mesh(self.ifc_mesh, color='lightgrey', specular=0.6, specular_power=10)
            self.plotter.camera_position = 'iso'
            print("Геометрия успешно загружена.")
        except Exception as e:
            print(f"Ошибка загрузки IFC: {e}")

    def setup_interaction(self):
        def pick_callback(point):
            if self.add_sensor_mode and point is not None:
                self.add_sensor_at_point(point)
                self.add_sensor_mode = False

        self.plotter.enable_point_picking(callback=pick_callback, key='p', show_message=True)

    def activate_add_sensor_mode(self):
        print("Режим добавления датчика: кликните по модели")
        self.add_sensor_mode = True

    def add_sensor_at_point(self, point):
        sid = self.sensor_id_counter
        self.sensor_id_counter += 1
        sphere = pv.Sphere(radius=0.3, center=point)
        actor = self.plotter.add_mesh(sphere, color='red', name=f"sensor_{sid}")
        label = self.plotter.add_point_labels(
            [point], [f"Датчик {sid}\nНет данных"],
            point_size=0, font_size=12, text_color='white',
            shape_opacity=0.5, always_visible=True
        )
        self.sensors[sid] = {'actor': actor, 'label': label, 'position': point}
        print(f"✅ Датчик {sid} добавлен в {point}")

    def get_latest_data(self):
        if not os.path.exists(SENSOR_DATA_FILE):
            return "Нет данных"
        try:
            with open(SENSOR_DATA_FILE, 'r') as f:
                lines = f.readlines()
            if len(lines) <= 1:
                return "Нет данных"
            last = lines[-1].strip().split(',')
            return f"T: {last[1]}°C\nP: {last[2]} bar\nVib: {last[3]}\nВремя: {last[0].split(' ')[1]}"
        except Exception:
            return "Ошибка чтения данных"

    def update_sensor_data(self):
        latest = self.get_latest_data()
        for sid, info in self.sensors.items():
            self.plotter.remove_actor(info['label'])
            label_actor = self.plotter.add_point_labels(
                [info['position']], [f"Датчик {sid}\n{latest}"],
                point_size=0, font_size=12, text_color='yellow',
                shape_opacity=0.7, always_visible=True
            )
            info['label'] = label_actor
            info['actor'].prop.color = 'yellow'
        self.plotter.render()


# ----------------------------
# 3. MAIN
# ----------------------------
if __name__ == "__main__":
    stop_event = threading.Event()
    simulator_thread = threading.Thread(target=simulate_iot_sensor, args=(stop_event,), daemon=True)
    simulator_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    window = IFCViewerApp()
    window.show()
    app.exec_()

    stop_event.set()
    simulator_thread.join(timeout=2)
    print("Приложение завершено.")
