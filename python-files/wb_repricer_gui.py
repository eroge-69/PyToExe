Python 3.8.8rc1 (tags/v3.8.8rc1:dfd7d68, Feb 17 2021, 10:45:44) [MSC v.1928 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> python
import sys
import os
import csv
import time
import json
import random
import threading
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar, 
                             QFileDialog, QGroupBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTabWidget, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import requests

class RepricerWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wildberries Репрайсер")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4a9cff;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a8cec;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                background-color: #4a9cff;
                width: 10px;
            }
        """)
        
        # Конфигурация
        self.api_key = ""
        self.total_cost_percent = 50
        self.min_profit_percent = 10
        self.is_running = False
        self.current_status = "Ожидание запуска"
        self.products = []
        self.report_data = []
        
        self.init_ui()
        self.load_last_config()
        
    def init_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной лейаут
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Сплиттер для разделения на левую и правую панели
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель (управление)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Группа настроек
        settings_group = QGroupBox("Настройки репрайсера")
        settings_layout = QVBoxLayout(settings_group)
        
        # API ключ
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API Ключ Wildberries:"))
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Введите ваш API ключ")
        self.api_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_input)
        settings_layout.addLayout(api_layout)
        
        # Процент издержек
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Общие издержки (%):"))
        self.cost_input = QLineEdit(str(self.total_cost_percent))
        self.cost_input.setFixedWidth(60)
        cost_layout.addWidget(self.cost_input)
        settings_layout.addLayout(cost_layout)
        
        # Минимальная прибыль
        profit_layout = QHBoxLayout()
        profit_layout.addWidget(QLabel("Минимальная прибыль (%):"))
        self.profit_input = QLineEdit(str(self.min_profit_percent))
        self.profit_input.setFixedWidth(60)
        profit_layout.addWidget(self.profit_input)
        settings_layout.addLayout(profit_layout)
        
        left_layout.addWidget(settings_group)
        
        # Группа управления
        control_group = QGroupBox("Управление процессом")
        control_layout = QVBoxLayout(control_group)
        
        # Кнопка загрузки файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_label)
        self.browse_btn = QPushButton("Выбрать файл")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        control_layout.addLayout(file_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        control_layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel(f"Статус: {self.current_status}")
        self.status_label.setStyleSheet("font-weight: bold; color: #555;")
        control_layout.addWidget(self.status_label)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Запустить репрайсер")
        self.start_btn.clicked.connect(self.start_repricer)
        self.start_btn.setStyleSheet("background-color: #28a745;")
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_repricer)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #dc3545;")
        btn_layout.addWidget(self.stop_btn)
        control_layout.addLayout(btn_layout)
        
        left_layout.addWidget(control_group)
        
        # Лог
        log_group = QGroupBox("Лог выполнения")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        left_layout.addWidget(log_group)
        
        # Правая панель (результаты)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Таблица результатов
        results_group = QGroupBox("Результаты репрайсинга")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "nmID", "Артикул", "Себестоимость", 
            "Текущая цена", "Цена конкурента", 
            "Новая цена", "Прибыль", "Маржа %", "Стратегия"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        
        # Кнопка экспорта
        self.export_btn = QPushButton("Экспортировать отчет")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        results_layout.addWidget(self.export_btn)
        
        right_layout.addWidget(results_group)
        
        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
        
        # Таймер для обновления интерфейса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл товаров", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.file_path = file_path
            self.log(f"Выбран файл: {file_path}")
            
            # Предварительная загрузка данных
            try:
                df = pd.read_csv(file_path, delimiter=';')
                self.log(f"Загружено товаров: {len(df)}")
            except Exception as e:
                self.log(f"Ошибка чтения файла: {str(e)}", "error")
    
    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "error":
            formatted = f'<font color="red">[{timestamp}] {message}</font>'
        elif level == "success":
            formatted = f'<font color="green">[{timestamp}] {message}</font>'
        elif level == "warning":
            formatted = f'<font color="orange">[{timestamp}] {message}</font>'
        else:
            formatted = f'<font color="black">[{timestamp}] {message}</font>'
        
        self.log_text.append(formatted)
        self.log_text.ensureCursorVisible()
        
        # Обновляем статус бар
        self.statusBar().showMessage(message)
    
    def start_repricer(self):
        # Проверка настроек
        self.api_key = self.api_input.text().strip()
        if not self.api_key:
            self.log("Ошибка: Не указан API ключ", "error")
            return
            
        try:
            self.total_cost_percent = float(self.cost_input.text())
            self.min_profit_percent = float(self.profit_input.text())
        except ValueError:
            self.log("Ошибка: Некорректные значения процентов", "error")
            return
            
        if not hasattr(self, 'file_path'):
            self.log("Ошибка: Не выбран файл товаров", "error")
            return
            
        # Сохраняем настройки
        self.save_config()
        
        # Блокируем интерфейс
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.current_status = "Запуск процесса..."
        
        # Запускаем в отдельном потоке
        self.repricer_thread = threading.Thread(target=self.run_repricer)
        self.repricer_thread.daemon = True
        self.repricer_thread.start()
    
    def stop_repricer(self):
        self.is_running = False
        self.current_status = "Остановка процесса..."
        self.log("Процесс остановлен по запросу пользователя", "warning")
        
    def run_repricer(self):
        try:
            # 1. Загрузка данных
            self.update_status("Загрузка информации о товарах...")
            products = self.load_products()
            if not products:
                return
                
            # 2. Получение текущих цен
            self.update_status("Получение ваших текущих цен...")
            my_prices = self.get_current_prices()
            
            # 3. Парсинг цен конкурентов
            self.update_status("Анализ цен конкурентов...")
            nm_ids = [p['nmId'] for p in products]
            comp_prices = self.get_competitor_prices(nm_ids)
            
            # 4. Расчет новых цен
            self.update_status("Расчет оптимальных цен...")
            updates = self.apply_price_strategy(products, my_prices, comp_prices)
            
            # 5. Обновление цен на WB
            self.update_status("Обновление цен на Wildberries...")
            updated_count = self.update_prices_on_wb(updates)
            
            # 6. Сохранение отчета
            self.update_status("Формирование отчета...")
            self.report_data = updates
            self.update_results_table()
            
            # Завершение
            self.log(f"✅ Процесс завершен успешно! Обновлено товаров: {updated_count}", "success")
            self.current_status = "Готово"
            
        except Exception as e:
            self.log(f"❌ Критическая ошибка: {str(e)}", "error")
            self.current_status = "Ошибка выполнения"
        finally:
            # Разблокируем интерфейс
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.browse_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
    
    def update_status(self, message):
        self.current_status = message
        self.log(message)
    
    def load_products(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                products = []
                for row in reader:
                    try:
                        row['nmId'] = int(row['nmId'])
                        row['cost_price'] = float(row['cost_price'])
                        products.append(row)
                    except ValueError as e:
                        self.log(f"Ошибка обработки строки: {row} - {str(e)}", "warning")
                self.log(f"✅ Загружено товаров: {len(products)}")
                return products
        except Exception as e:
            self.log(f"❌ Ошибка чтения файла: {str(e)}", "error")
            return []
    
    def get_current_prices(self):
        try:
            response = requests.get(
                "https://suppliers-api.wildberries.ru/public/api/v1/info",
                headers={"Authorization": self.api_key},
                params={"quantity": 0},
                timeout=30
            )
            if response.status_code == 200:
                return {item['nmId']: item['price'] for item in response.json()}
            self.log(f"❌ Ошибка API: {response.status_code} - {response.text}", "error")
            return {}
        except Exception as e:
            self.log(f"❌ Ошибка получения цен: {str(e)}", "error")
            return {}
    
    def get_competitor_prices(self, nm_ids):
        # Для упрощения в виджете будем использовать случайные цены
        # В реальном приложении здесь должен быть парсинг
        return {nm_id: random.randint(500, 5000) for nm_id in nm_ids}
    
    def calculate_min_price(self, cost_price):
        """Расчет минимальной цены с гарантией прибыли"""
        return (cost_price * (1 + self.min_profit_percent/100)) / (1 - self.total_cost_percent/100)
    
    def apply_price_strategy(self, products, my_prices, comp_prices):
        updates = []
        
        for i, product in enumerate(products):
            if not self.is_running:
                break
                
            nm_id = product['nmId']
            cost = product['cost_price']
            
            # Обновляем прогресс
            progress = int((i + 1) / len(products) * 100)
            self.progress_bar.setValue(progress)
            
            min_price = self.calculate_min_price(cost)
            current_price = my_prices.get(nm_id, min_price)
            comp_price = comp_prices.get(nm_id, min_price * 1.2)
            
            # Стратегия ценообразования
            if comp_price < min_price * 0.95:
                new_price = min_price
                strategy = "Демпинг-защита"
            elif current_price > comp_price * 1.1:
                new_price = max(min_price, comp_price * 0.98)
                strategy = "Атака рынка"
            else:
                new_price = max(min_price, current_price * 0.99)
                strategy = "Оптимизация"
            
            # Расчет прибыли
            revenue = new_price * (1 - self.total_cost_percent/100)
            profit = revenue - cost
            margin = (profit / cost) * 100 if cost > 0 else 0
            
            # Гарантия минимальной прибыли
            if margin < self.min_profit_percent:
                new_price = min_price
                strategy = "Защита маржи"
                revenue = new_price * (1 - self.total_cost_percent/100)
                profit = revenue - cost
                margin = (profit / cost) * 100
            
            updates.append({
                "nmId": nm_id,
                "Артикул": product.get('vendorCode', ''),
                "Себестоимость": cost,
                "Текущая цена": current_price,
                "Цена конкурента": comp_price,
                "Новая цена": round(new_price),
                "Прибыль": round(profit, 2),
                "Маржа %": round(margin, 1),
                "Стратегия": strategy
            })
        
        return updates
    
    def update_prices_on_wb(self, updates):
        # В демо-режиме не отправляем реальные запросы
        self.log("Демо-режим: реальное обновление цен отключено", "warning")
        return len(updates)
    
    def update_results_table(self):
        if not self.report_data:
            return
            
        self.results_table.setRowCount(len(self.report_data))
        
        for row, item in enumerate(self.report_data):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(item["nmId"])))
            self.results_table.setItem(row, 1, QTableWidgetItem(item["Артикул"]))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(item["Себестоимость"])))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(item["Текущая цена"])))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(item["Цена конкурента"])))
            
            # Новая цена с цветовым оформлением
            new_price_item = QTableWidgetItem(str(item["Новая цена"]))
            if item["Новая цена"] < item["Текущая цена"]:
                new_price_item.setForeground(QColor(220, 53, 69))  # Красный
            elif item["Новая цена"] > item["Текущая цена"]:
                new_price_item.setForeground(QColor(40, 167, 69))   # Зеленый
            self.results_table.setItem(row, 5, new_price_item)
            
            # Прибыль с цветовым оформлением
            profit_item = QTableWidgetItem(str(item["Прибыль"]))
            if item["Прибыль"] < 0:
                profit_item.setForeground(QColor(220, 53, 69))  # Красный
            else:
                profit_item.setForeground(QColor(40, 167, 69))   # Зеленый
            self.results_table.setItem(row, 6, profit_item)
            
            # Маржа с цветовым оформлением
            margin_item = QTableWidgetItem(f"{item['Маржа %']}%")
            if item["Маржа %"] < self.min_profit_percent:
                margin_item.setForeground(QColor(220, 53, 69))  # Красный
            else:
                margin_item.setForeground(QColor(40, 167, 69))   # Зеленый
            self.results_table.setItem(row, 7, margin_item)
            
            # Стратегия
            strategy_item = QTableWidgetItem(item["Стратегия"])
            if "Демпинг" in item["Стратегия"]:
                strategy_item.setForeground(QColor(220, 53, 69))  # Красный
            elif "Защита" in item["Стратегия"]:
                strategy_item.setForeground(QColor(255, 193, 7))  # Желтый
            elif "Атака" in item["Стратегия"]:
                strategy_item.setForeground(QColor(23, 162, 184)) # Голубой
            else:
                strategy_item.setForeground(QColor(40, 167, 69)) # Зеленый
            self.results_table.setItem(row, 8, strategy_item)
    
    def export_report(self):
        if not self.report_data:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.report_data[0].keys(), delimiter=';')
                    writer.writeheader()
                    writer.writerows(self.report_data)
                self.log(f"✅ Отчет сохранен: {file_path}", "success")
            except Exception as e:
                self.log(f"❌ Ошибка сохранения отчета: {str(e)}", "error")
    
    def update_ui(self):
        self.status_label.setText(f"Статус: {self.current_status}")
        self.progress_bar.setValue(self.progress_bar.value())
        
    def save_config(self):
        config = {
            "api_key": self.api_key,
            "total_cost_percent": self.total_cost_percent,
            "min_profit_percent": self.min_profit_percent
        }
        try:
            with open("repricer_config.json", "w") as f:
                json.dump(config, f)
        except:
            pass
    
    def load_last_config(self):
        try:
            if os.path.exists("repricer_config.json"):
                with open("repricer_config.json", "r") as f:
                    config = json.load(f)
                    self.api_input.setText(config.get("api_key", ""))
                    self.cost_input.setText(str(config.get("total_cost_percent", 35)))
                    self.profit_input.setText(str(config.get("min_profit_percent", 10)))
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Настройка шрифта
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = RepricerWidget()
    window.show()
    sys.exit(app.exec_())