import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, 
                              QWidget, QLabel, QProgressBar, QFileDialog, QMessageBox)
from PySide6.QtCore import QThread, Signal

import os
import re
import abc
import time
# import torch
import pickle
import argparse
import numpy as np
import pandas as pd

from typing import Dict, List,  Union

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# device

regions = {
    "Акмолинская": 11,
    "Актюбинская": 15,
    "Алматинская": 19,
    "Атырауская": 23,
    "Восточно-Казахстанская": 63,
    "г. Астана": 71,
    "г. Алматы": 75,
    "г. Шымкент": 79,
    "Жамбылская": 31,
    "Западно-Казахстанская": 27,
    "Карагандинская": 35,
    "Костанайская": 39,
    "Кызылординская": 43,
    "Мангинстауская": 47,
    "Абай": 10,
    "Жетісу": 33,
    "Улытау": 62,
    "Павлодарская": 55,
    "Северо-Казахстанская": 59,
    "Туркестанская": 61
}

def find_kato(df):
    for col in df.columns:
        # print(df.columns)
        if 'ӘАОЖ / KATO' in col or 'ӘАОЖ / \nKATO' in col:
            return col
    raise ValueError("Не найден столбец с КАТО")

def process_region(region_name, region_folder, output_folder):
    base_data = {}
    file_path = f"1- қосымша (сельские округа) — 25022025.xlsx"
    filename = os.path.join(region_folder, file_path)
    if os.path.exists(filename):
        try:
            df = pd.read_excel(filename, header=1)
            # print("Столбцы в файле:", df.columns.tolist())

            for _, row in df.iterrows():
                kato = row["КАТО"]
                cnt = row['Unnamed: 63']

                try:
                    kato = int(row['КАТО']) if not pd.isna(row['КАТО']) else None

                    if kato is None  or kato // (10 ** 7) != regions[region_name]:
                        continue

                    # cnt = int(cnt) if not pd.isna(row['Unnamed: 63']) else 0
                    cnt = row['Unnamed: 63'] if 'Unnamed: 63' in row else 0

                    if pd.isna(cnt):
                        cnt = 0    
                
                    base_data[kato] = {
                        "КАТО": kato,
                        "Наименование населенного пункта": row["Елді мекендер атауы / Наименование населенного пункта"],
                        "БИН": row["БСН / БИН"],
                        "приложение-1": int(cnt)
                    }
                except (ValueError, TypeError):
                    continue
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {str(e)}")

    
    

    for i in range(2, 15):
        file_path = f"{i}-қосымша - {region_name}.xlsx"
        filename = os.path.join(region_folder,  file_path)
        if not os.path.exists(filename):
            file_path = f"10-қосымша (ликвидир ИП КФХ).xlsx"
            filename = os.path.join(region_folder,  file_path)
            if not os.path.exists(filename):
                continue
            
        try:
            df = pd.read_excel(filename, header=3)
            kato_col = find_kato(df)
        
            tmp_cnt = {}
            for _, row in df.iterrows():
                try:
                    kato = int(row[kato_col]) if not pd.isna(row[kato_col]) else None

                    if kato is None:
                        continue

                    rounded_kato = (kato // 1000) * 1000
                    tmp_cnt[rounded_kato] = tmp_cnt.get(rounded_kato, 0) + 1
                except (ValueError, TypeError):
                    continue
        
            for kato, cnt in tmp_cnt.items():
                if kato in base_data:
                    base_data[kato][f"приложение-{i}"] = cnt
                else:
                    # Если КАТО нет в приложении-1, но есть в других, добавляем с пустыми значениями
                    # print(base_data[kato][])
                    base_data[kato] = {
                        'КАТО': kato,
                        'Наименование населенного пункта': '',
                        'БИН': '',
                        **{f'приложение-{j}': 0 for j in range(1, i)},
                        f'приложение-{i}': cnt
                    }

            for kato in base_data:
                if f"приложение-{i}" not in base_data[kato]:
                    base_data[kato][f"приложение-{i}"] = 0

        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {str(e)}")



    if base_data:
        rows = []
        for kato in base_data.keys():
            row = base_data[kato]

            present_apps = [k for k in row.keys() if k.startswith('приложение-')]
            max_app = max([int(a.split('-')[1]) for a in present_apps]) if present_apps else 0

            for i in range(1, max_app + 1):
                col = f"приложение-{i}"
                if col not in row:
                    row[col] = 0

            row["Всего"] = sum(row.get(f"приложение-{i}", 0) for i in range(1, max_app + 1))
            rows.append(row)

            columns = ['КАТО', 'Наименование населенного пункта', 'БИН']
            columns.extend([f'приложение-{i}' for i in range(1, max_app + 1)])
            columns.append('Всего')

            result_df = pd.DataFrame(rows, columns=columns)

            output_path = f"Итог - {region_name}.xlsx"
            output_file = os.path.join(output_folder, output_path)
            result_df.to_excel(output_file, index=False)
        print(f"Результат сохранен в файл: {output_path}")

    print("Finish!!!")
    return base_data

def create_table(regions_data, output_folder):
    output_path = "Итог.xlsx"
    sum_rows = []
    total_cnts = {}

    max_app = 0
    for region_name, region_data in regions_data.items():
        if not region_data:
            continue

        for kato_data in region_data.values():
            for k in kato_data.keys():
                if k.startswith('приложение-'):
                    app_num = int(k.split('-')[1])
                    if app_num > max_app:
                        max_app = app_num

    for region_name in regions:
        region_data = regions_data.get(region_name, {})
        if not region_data:
            continue
    
        app_cnts = {i: 0 for i in range(1, max_app + 1)}

        
        for kato_data in region_data.values():
            for k, v in kato_data.items():
                if k.startswith('приложение-'):
                    app_num = int(k.split('-')[1])
                    app_cnts[app_num] += v

        row = {'Регион': region_name}
        for i in range(1, max_app + 1):
            row[f"приложение-{i}"] = app_cnts[i]
            total_cnts[i] = total_cnts.get(i, 0) + app_cnts[i]

        row["Всего"] = sum(app_cnts.values())
        sum_rows.append(row)

    if total_cnts:
        Z_row = {'Регион': 'Казахстан'}
        for i in range(1, max_app + 1):
            Z_row[f"приложение-{i}"] = total_cnts.get(i, 0)
        Z_row["Всего"] = sum(total_cnts.values())
        sum_rows.append(Z_row)

    if sum_rows:
        cols = ['Регион'] + [f"приложение-{i}" for i in range(1, max_app + 1)] + ["Всего"]
        sum_df = pd.DataFrame(sum_rows, columns=cols)

        output_file = os.path.join(output_folder, output_path)
        sum_df.to_excel(output_file, index=False)

def process_all_regions(output_folder, progress_callback=None):
    """Обрабатывает все регионы с возможностью отслеживания прогресса"""
    regions_data = {}
    total_regions = len(regions)
    
    # Создаем папку для результатов, если ее нет
    os.makedirs(output_folder, exist_ok=True)
    
    for i, region_name in enumerate(regions.keys(), 1):
        region_folder = os.path.join(os.getcwd(), region_name)
        if not os.path.exists(region_folder):
            continue
        
        # Обрабатываем регион
        region_result = process_region(region_name, region_folder, output_folder)
        regions_data[region_name] = region_result
        
        # Обновляем прогресс
        if progress_callback:
            progress = int((i / total_regions) * 100)
            progress_callback.emit(progress)
    
    # Создаем сводную таблицу
    create_table(regions_data, output_folder)
    
    if progress_callback:
        progress_callback.emit(100)

class ProcessingThread(QThread):
    """Поток для выполнения обработки данных"""
    progress_updated = Signal(int)
    processing_finished = Signal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.output_folder = "Итог Z"
        
    def set_output_folder(self, folder):
        self.output_folder = folder
        
    def run(self):
        try:
            # Вызываем вашу функцию обработки
            process_all_regions(self.output_folder, self.progress_updated)
            self.processing_finished.emit(True, "Обработка успешно завершена!")
        except Exception as e:
            self.processing_finished.emit(False, f"Ошибка: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обработка данных регионов Казахстана")
        self.setGeometry(100, 100, 400, 300)
        
        self.thread = None
        self.init_ui()
        
    def init_ui(self):
        # Основной виджет
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        self.title_label = QLabel("Обработка данных по регионам Казахстана")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Описание
        self.desc_label = QLabel(
            "Программа обрабатывает Excel-файлы с данными по регионам "
            "и создает итоговые отчеты."
        )
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # Кнопка выбора папки
        self.folder_btn = QPushButton("Выбрать папку для сохранения результатов")
        self.folder_btn.clicked.connect(self.select_output_folder)
        layout.addWidget(self.folder_btn)
        
        # Индикатор выбранной папки
        self.folder_label = QLabel("Папка не выбрана")
        self.folder_label.setWordWrap(True)
        layout.addWidget(self.folder_label)
        
        # Кнопка запуска обработки
        self.process_btn = QPushButton("Начать обработку")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        layout.addWidget(self.process_btn)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def select_output_folder(self):
        """Выбор папки для сохранения результатов"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения результатов",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.folder_label.setText(folder)
            self.process_btn.setEnabled(True)
            self.status_label.setText("Папка выбрана. Готов к обработке.")
            
    def start_processing(self):
        """Запуск обработки данных"""
        if self.thread and self.thread.isRunning():
            return
            
        # Создаем и настраиваем поток
        self.thread = ProcessingThread()
        self.thread.set_output_folder(self.folder_label.text())
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.processing_finished.connect(self.processing_done)
        
        # Блокируем кнопки на время обработки
        self.folder_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
        self.status_label.setText("Идет обработка...")
        
        # Запускаем поток
        self.thread.start()
        
    def update_progress(self, value):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        
    def processing_done(self, success, message):
        """Завершение обработки"""
        # Разблокируем кнопки
        self.folder_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        
        # Показываем сообщение
        if success:
            QMessageBox.information(self, "Успех", message)
            self.status_label.setText("Обработка завершена успешно!")
        else:
            QMessageBox.critical(self, "Ошибка", message)
            self.status_label.setText("Ошибка при обработке.")
        
        # Сбрасываем прогресс
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()