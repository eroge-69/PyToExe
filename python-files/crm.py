import sys
import os
import sqlite3
import re
import json
import logging # Для замены print на logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                             QLineEdit, QTextEdit, QDateEdit, QFileDialog, QMessageBox,
                             QHeaderView, QGroupBox, QFormLayout, QComboBox, QScrollArea,
                             QAbstractItemView, QDialog, QDialogButtonBox, QToolBar, QAction,
                             QToolTip, QStyleOptionViewItem, QStyledItemDelegate, QSizePolicy,
                             QSplitter)
from PyQt5.QtCore import Qt, QDate, QSize, QSettings, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QColor
# <-- Обернуто в try-except для обработки отсутствия QtWebEngine
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("Внимание: Модуль PyQt5.QtWebEngineWidgets не найден. Вкладка отчетов будет недоступна.")
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import openpyxl.utils # Импортируем для get_column_letter
# Настройка логирования (простой пример)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class NumericDelegate(QStyledItemDelegate):
    """Делегат для форматирования чисел с разделителями тысяч"""
    def displayText(self, value, locale):
        try:
            if isinstance(value, str) and value.replace(',', '').replace('.', '').isdigit():
                # Если это строка, содержащая число
                num = float(value.replace(',', ''))
                return f"{num:,.2f}".replace(',', ' ')
            elif isinstance(value, (int, float)):
                return f"{value:,.2f}".replace(',', ' ')
        except Exception: # <-- ИСПРАВЛЕНО: Заменено широкое except: на except Exception:
            pass
        return super().displayText(value, locale)
class GOZManagementApp(QMainWindow):
    # <-- Добавлены константы для номеров столбцов таблицы контрактов
    COL_ID = 0
    COL_ORG = 1
    COL_STATE_CUST = 2
    COL_EXECUTOR = 3
    COL_CONTRACT_NUM = 4
    COL_PRICE = 5
    COL_DEADLINE = 6
    COL_STATUS = 7
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления государственными оборонными заказами")
        self.setGeometry(100, 100, 1200, 800)
        # Инициализация настроек
        self.settings = QSettings("ShechikovSA", "GOZManagementApp")
        # Инициализация базы данных
        self.init_database()
        # Создание основного виджета и компоновки
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        # Создание вкладок
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        # Создание вкладок
        self.create_contracts_tab()
        self.create_add_edit_tab()
        # <-- Создание вкладки отчетов только если модуль доступен
        if WEBENGINE_AVAILABLE:
            self.create_reports_tab()
        else:
            self.create_reports_unavailable_tab()
        self.create_about_tab()
        # Переменные для хранения текущего контракта
        self.current_contract_id = None
        self.unsaved_changes = False  # Флаг несохраненных изменений
        # Загрузка данных
        self.load_contracts_data()
        # Подключаем обработчик изменения размера окна
        self.resizeEvent = self.on_resize_event
    def init_database(self):
        """Инициализация базы данных SQLite"""
        self.db_conn = sqlite3.connect('goz_database.db')
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_name TEXT,
                state_customer_name TEXT,
                state_customer_inn TEXT,
                state_customer_address TEXT,
                head_executor_name TEXT,
                head_executor_inn TEXT,
                head_executor_address TEXT,
                contractor_name TEXT,
                contractor_inn TEXT,
                contractor_address TEXT,
                contract_date TEXT,
                contract_number TEXT,
                contract_subject TEXT,
                contract_price REAL,
                vat_rate REAL,
                advance_terms TEXT,
                advance_size TEXT,
                final_payment_terms TEXT,
                execution_deadline TEXT,
                acceptance_date TEXT,
                execution_status TEXT CHECK(execution_status IN ('Выполнен', 'В работе', 'Просрочен', 'Отменен')),
                violations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS contract_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                payment_date TEXT,
                payment_amount REAL,
                FOREIGN KEY(contract_id) REFERENCES contracts(id)
            )
        ''')
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS attached_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                file_path TEXT,
                file_name TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contract_id) REFERENCES contracts(id)
            )
        ''')
        self.db_conn.commit()
    def create_contracts_tab(self):
        """Создание вкладки со списком контрактов"""
        self.contracts_tab = QWidget()
        layout = QVBoxLayout(self.contracts_tab)
        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите номер, ИНН, название организации или ключевые слова...")
        self.search_input.textChanged.connect(self.search_contracts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        # Панель управления
        control_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_contracts_data)
        control_layout.addWidget(self.refresh_btn)
        self.add_contract_btn = QPushButton("Добавить контракт")
        self.add_contract_btn.clicked.connect(self.add_new_contract)
        control_layout.addWidget(self.add_contract_btn)
        self.edit_contract_btn = QPushButton("Редактировать")
        self.edit_contract_btn.clicked.connect(self.edit_selected_contract)
        control_layout.addWidget(self.edit_contract_btn)
        self.delete_contract_btn = QPushButton("Удалить")
        self.delete_contract_btn.clicked.connect(self.delete_selected_contract)
        control_layout.addWidget(self.delete_contract_btn)
        self.attach_file_btn = QPushButton("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file_to_contract)
        control_layout.addWidget(self.attach_file_btn)
        control_layout.addStretch()
        self.import_excel_btn = QPushButton("Импорт из Excel")
        self.import_excel_btn.clicked.connect(self.import_from_excel)
        control_layout.addWidget(self.import_excel_btn)
        self.export_excel_btn = QPushButton("Экспорт в Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        control_layout.addWidget(self.export_excel_btn)
        layout.addLayout(control_layout)
        # Таблица контрактов
        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(8)
        self.contracts_table.setHorizontalHeaderLabels([
            "ID", "Организация", "Госзаказчик", "Исполнитель",
            "Номер контракта", "Цена", "Срок исполнения", "Статус"
        ])
        self.contracts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.contracts_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Настраиваем заголовки столбцов для растягивания
        header = self.contracts_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Растягиваем все столбцы
        # Устанавливаем делегат для форматирования чисел в столбце "Цена"
        price_delegate = NumericDelegate()
        self.contracts_table.setItemDelegateForColumn(self.COL_PRICE, price_delegate)
        # Подключаем обработчик двойного клика
        self.contracts_table.cellDoubleClicked.connect(self.edit_selected_contract)
        layout.addWidget(self.contracts_table)
        self.tabs.addTab(self.contracts_tab, "Список контрактов")
    def on_resize_event(self, event):
        """Обработчик изменения размера окна"""
        QMainWindow.resizeEvent(self, event)
        # Автоматически подгоняем столбцы при изменении размера окна
        self.adjust_columns_to_content()
    def adjust_columns_to_content(self):
        """Автоматическая подгонка столбцов под содержимое (с растяжением всех столбцов)"""
        if not hasattr(self, 'contracts_table'):
            return
        header = self.contracts_table.horizontalHeader()
        # Растягиваем все столбцы
        header.setSectionResizeMode(QHeaderView.Stretch)
    def search_contracts(self):
        """Поиск контрактов по различным критериям"""
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            self.load_contracts_data()
            return
        # Полностью пересоздаем таблицу для избежания смещения данных
        self.contracts_table.clear()
        self.contracts_table.setRowCount(0)
        self.contracts_table.setColumnCount(8)
        self.contracts_table.setHorizontalHeaderLabels([
            "ID", "Организация", "Госзаказчик", "Исполнитель",
            "Номер контракта", "Цена", "Срок исполнения", "Статус"
        ])
        self.contracts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.contracts_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Настраиваем заголовки столбцов
        header = self.contracts_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Растягиваем все столбцы
        # Устанавливаем делегат для форматирования чисел в столбце "Цена"
        price_delegate = NumericDelegate()
        self.contracts_table.setItemDelegateForColumn(self.COL_PRICE, price_delegate)
        # Подключаем обработчик двойного клика
        self.contracts_table.cellDoubleClicked.connect(self.edit_selected_contract)
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, organization_name, state_customer_name, head_executor_name,
                   contract_number, contract_price, execution_deadline, execution_status
            FROM contracts
            WHERE LOWER(organization_name) LIKE ?
               OR LOWER(state_customer_name) LIKE ?
               OR LOWER(head_executor_name) LIKE ?
               OR LOWER(contract_number) LIKE ?
               OR LOWER(state_customer_inn) LIKE ?
               OR LOWER(head_executor_inn) LIKE ?
               OR LOWER(contractor_inn) LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ))
        for row_num, row_data in enumerate(cursor.fetchall()):
            self.contracts_table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data) if data is not None else "") # <-- ИСПРАВЛЕНО: Явная проверка на None
                # Центрируем текст в определенных столбцах
                if col_num in [self.COL_ID, self.COL_ORG, self.COL_PRICE, self.COL_DEADLINE, self.COL_STATUS]:  # ID, Организация, Цена, Срок исполнения, Статус
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # Цветовая индикация для статуса (последний столбец)
                if col_num == self.COL_STATUS:  # Статус
                    status = str(data) if data else "В работе"
                    if status == "Выполнен":
                        item.setBackground(QColor(216, 237, 216))  # Светло-зеленый
                        item.setForeground(QColor(0, 97, 0))
                    elif status == "В работе":
                        item.setBackground(QColor(255, 242, 204))  # Светло-желтый
                        item.setForeground(QColor(156, 87, 0))
                    elif status == "Просрочен":
                        item.setBackground(QColor(248, 203, 173))  # Светло-оранжевый
                        item.setForeground(QColor(156, 0, 6))
                    elif status == "Отменен":
                        item.setBackground(QColor(217, 217, 217))  # Серый
                        item.setForeground(QColor(128, 128, 128))
                self.contracts_table.setItem(row_num, col_num, item)
        # Автоматически подгоняем столбцы под содержимое
        self.adjust_columns_to_content()
    def load_contracts_data(self):
        """Загрузка данных контрактов в таблицу с цветовой индикацией статуса"""
        # Полностью пересоздаем таблицу для избежания смещения данных
        self.contracts_table.clear()
        self.contracts_table.setRowCount(0)
        self.contracts_table.setColumnCount(8)
        self.contracts_table.setHorizontalHeaderLabels([
            "ID", "Организация", "Госзаказчик", "Исполнитель",
            "Номер контракта", "Цена", "Срок исполнения", "Статус"
        ])
        self.contracts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.contracts_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # Настраиваем заголовки столбцов
        header = self.contracts_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Растягиваем все столбцы
        # Устанавливаем делегат для форматирования чисел в столбце "Цена"
        price_delegate = NumericDelegate()
        self.contracts_table.setItemDelegateForColumn(self.COL_PRICE, price_delegate)
        # Подключаем обработчик двойного клика
        self.contracts_table.cellDoubleClicked.connect(self.edit_selected_contract)
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, organization_name, state_customer_name, head_executor_name,
                   contract_number, contract_price, execution_deadline, execution_status
            FROM contracts
            ORDER BY id DESC
        """)
        for row_num, row_data in enumerate(cursor.fetchall()):
            self.contracts_table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data) if data is not None else "") # <-- ИСПРАВЛЕНО: Явная проверка на None
                # Центрируем текст в определенных столбцах
                if col_num in [self.COL_ID, self.COL_ORG, self.COL_PRICE, self.COL_DEADLINE, self.COL_STATUS]:  # ID, Организация, Цена, Срок исполнения, Статус
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                # Цветовая индикация для статуса (последний столбец)
                if col_num == self.COL_STATUS:  # Статус
                    status = str(data) if data else "В работе"
                    if status == "Выполнен":
                        item.setBackground(QColor(216, 237, 216))  # Светло-зеленый
                        item.setForeground(QColor(0, 97, 0))
                    elif status == "В работе":
                        item.setBackground(QColor(255, 242, 204))  # Светло-желтый
                        item.setForeground(QColor(156, 87, 0))
                    elif status == "Просрочен":
                        item.setBackground(QColor(248, 203, 173))  # Светло-оранжевый
                        item.setForeground(QColor(156, 0, 6))
                    elif status == "Отменен":
                        item.setBackground(QColor(217, 217, 217))  # Серый
                        item.setForeground(QColor(128, 128, 128))
                self.contracts_table.setItem(row_num, col_num, item)
        # Автоматически подгоняем столбцы под содержимое
        self.adjust_columns_to_content()
    def create_add_edit_tab(self):
        """Создание вкладки для добавления/редактирования контракта"""
        self.add_edit_tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout(scroll_content)
        # --- Верхний ряд: Основная информация + Финансы ---
        top_row_layout = QHBoxLayout()
        # Левая колонка: Основная информация
        contract_group = QGroupBox("Основная информация о контракте")
        contract_layout = QFormLayout()
        self.org_name_input = QLineEdit()
        self.org_name_input.setToolTip("Пример: АО \"БРТ\"")
        contract_layout.addRow("Наименование организации:", self.org_name_input)
        self.state_customer_name_input = QLineEdit()
        self.state_customer_name_input.setToolTip("Пример: МО РФ, ФСБ, ООО ВПК")
        contract_layout.addRow("Наименование госзаказчика:", self.state_customer_name_input)
        self.state_customer_inn_input = QLineEdit()
        self.state_customer_inn_input.setToolTip("Пример: 7701234567")
        contract_layout.addRow("ИНН госзаказчика:", self.state_customer_inn_input)
        self.state_customer_address_input = QLineEdit()
        self.state_customer_address_input.setToolTip("Пример: г. Москва, ул. Ленина, д.1")
        contract_layout.addRow("Адрес госзаказчика:", self.state_customer_address_input)
        self.head_executor_name_input = QLineEdit()
        contract_layout.addRow("Наименование исполнителя:", self.head_executor_name_input)
        self.head_executor_inn_input = QLineEdit()
        contract_layout.addRow("ИНН исполнителя:", self.head_executor_inn_input)
        self.head_executor_address_input = QLineEdit()
        contract_layout.addRow("Адрес исполнителя:", self.head_executor_address_input)
        self.contractor_name_input = QLineEdit()
        contract_layout.addRow("Наименование контрагента:", self.contractor_name_input)
        self.contractor_inn_input = QLineEdit()
        contract_layout.addRow("ИНН контрагента:", self.contractor_inn_input)
        self.contractor_address_input = QLineEdit()
        contract_layout.addRow("Адрес контрагента:", self.contractor_address_input)
        self.contract_date_input = QDateEdit()
        self.contract_date_input.setCalendarPopup(True)
        self.contract_date_input.setDate(QDate.currentDate())
        self.contract_date_input.setToolTip("Формат: ДД.ММ.ГГГГ (например, 22.12.2023)")
        contract_layout.addRow("Дата заключения контракта:", self.contract_date_input)
        self.contract_number_input = QLineEdit()
        self.contract_number_input.setToolTip("Пример: №2224187312382442241007711/920-00/4662")
        contract_layout.addRow("Номер контракта:", self.contract_number_input)
        self.contract_subject_input = QTextEdit()
        self.contract_subject_input.setMaximumHeight(70)
        contract_layout.addRow("Предмет контракта:", self.contract_subject_input)
        self.contract_price_input = QLineEdit()
        self.contract_price_input.setToolTip("Пример: 3264784.85 (без текста 'руб')")
        self.contract_price_input.textChanged.connect(self.calculate_vat)  # <-- Подключаем пересчет НДС
        contract_layout.addRow("Цена контракта (руб):", self.contract_price_input)
        self.vat_rate_input = QComboBox()
        self.vat_rate_input.addItems(["0", "10", "20"])
        self.vat_rate_input.setCurrentText("20")
        self.vat_rate_input.currentTextChanged.connect(self.calculate_vat)  # <-- Подключаем пересчет НДС
        contract_layout.addRow("Ставка НДС (%):", self.vat_rate_input)
        # НОВОЕ ПОЛЕ: Сумма НДС
        self.vat_amount_input = QLineEdit()
        self.vat_amount_input.setReadOnly(True)
        self.vat_amount_input.setStyleSheet("background-color: #f0f0f0; color: #555;")
        contract_layout.addRow("Сумма НДС (руб):", self.vat_amount_input)
        contract_group.setLayout(contract_layout)
        top_row_layout.addWidget(contract_group)
        # Правая колонка: Финансовые условия (ОПТИМИЗИРОВАНО)
        finance_group = QGroupBox("Финансовые условия")
        finance_layout = QFormLayout()
        # Используем вертикальные компоновки для симметрии
        # Сроки и размер авансирования
        self.advance_terms_input = QTextEdit()
        self.advance_terms_input.setMaximumHeight(60)
        self.advance_terms_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.advance_terms_input.setToolTip("Укажите сроки авансирования")
        finance_layout.addRow("Сроки авансирования:", self.advance_terms_input)
        self.advance_size_input = QLineEdit()
        self.advance_size_input.setMaximumWidth(100)  # Ограничиваем ширину поля ввода процента
        self.advance_size_input.setToolTip("Укажите размер аванса в процентах")
        finance_layout.addRow("Размер аванса (%):", self.advance_size_input)
        # Сроки окончательного расчета
        self.final_payment_terms_input = QTextEdit()
        self.final_payment_terms_input.setMaximumHeight(60)
        self.final_payment_terms_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.final_payment_terms_input.setToolTip("Укажите сроки окончательного расчета")
        finance_layout.addRow("Сроки окончательного расчета:", self.final_payment_terms_input)
        finance_group.setLayout(finance_layout)
        top_row_layout.addWidget(finance_group)
        main_layout.addLayout(top_row_layout)
        # --- Средний ряд: Сроки исполнения ---
        execution_group = QGroupBox("Сроки исполнения")
        execution_layout = QFormLayout()
        self.execution_deadline_input = QLineEdit()
        self.execution_deadline_input.setToolTip("Пример: по 31.03.2025 или 4 кв.2025")
        execution_layout.addRow("Срок исполнения обязательств:", self.execution_deadline_input)
        self.acceptance_date_input = QDateEdit()
        self.acceptance_date_input.setCalendarPopup(True)
        execution_layout.addRow("Дата приемки работ:", self.acceptance_date_input)
        self.execution_status_input = QComboBox()
        self.execution_status_input.addItems(["Выполнен", "В работе", "Просрочен", "Отменен"])  # С большой буквы
        execution_layout.addRow("Сведения об исполнении:", self.execution_status_input)
        self.violations_input = QTextEdit()
        self.violations_input.setMaximumHeight(70)
        execution_layout.addRow("Выявленные нарушения и меры реагирования:", self.violations_input)
        execution_group.setLayout(execution_layout)
        main_layout.addWidget(execution_group)
        # --- Нижний ряд: Платежи и Файлы ---
        # Используем QSplitter для возможности изменения размеров
        splitter = QSplitter(Qt.Horizontal)
        # Платежи
        payments_group = QGroupBox("Платежи по контракту")
        payments_layout = QVBoxLayout()
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(3)
        self.payments_table.setHorizontalHeaderLabels(["Дата (ДД.ММ.ГГГГ)", "Сумма", "Действия"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        payments_layout.addWidget(self.payments_table)
        # Кнопки для управления платежами
        payments_buttons_layout = QHBoxLayout()
        add_payment_btn = QPushButton("Добавить платеж")
        add_payment_btn.clicked.connect(self.add_payment)
        payments_buttons_layout.addWidget(add_payment_btn)
        payments_layout.addLayout(payments_buttons_layout)
        payments_group.setLayout(payments_layout)
        splitter.addWidget(payments_group)
        # Прикрепленные файлы
        files_group = QGroupBox("Прикрепленные файлы")
        files_layout = QVBoxLayout()
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["Имя файла", "Дата загрузки", "Действия"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        files_layout.addWidget(self.files_table)
        attach_file_btn = QPushButton("Прикрепить файл")
        attach_file_btn.clicked.connect(self.attach_file_to_current_contract)
        files_layout.addWidget(attach_file_btn)
        files_group.setLayout(files_layout)
        splitter.addWidget(files_group)
        # Устанавливаем начальные размеры сплиттера
        splitter.setSizes([400, 400])  # Можно настроить по усмотрению
        main_layout.addWidget(splitter)
        # --- Кнопки сохранения ---
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.save_contract_btn = QPushButton("Сохранить контракт")
        self.save_contract_btn.clicked.connect(self.save_contract)
        buttons_layout.addWidget(self.save_contract_btn)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        buttons_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(buttons_layout)
        # Добавляем scroll в вкладку
        tab_layout = QVBoxLayout(self.add_edit_tab)
        tab_layout.addWidget(scroll)
        self.tabs.addTab(self.add_edit_tab, "Добавить/Редактировать контракт")
    @pyqtSlot()
    def calculate_vat(self):
        """Автоматический расчет суммы НДС при изменении цены или ставки"""
        try:
            price_text = self.contract_price_input.text().strip()
            rate_text = self.vat_rate_input.currentText()
            if not price_text:
                self.vat_amount_input.setText("")
                return
            price = float(price_text)
            rate = float(rate_text)
            vat_amount = price * rate / 100.0
            self.vat_amount_input.setText(f"{vat_amount:,.2f}".replace(',', ' '))
        except (ValueError, TypeError): # <-- ИСПРАВЛЕНО: Добавлен перехват TypeError
            self.vat_amount_input.setText("Ошибка")
    def create_reports_tab(self):
        """Создание вкладки отчетов и статистики с встроенным браузером"""
        self.reports_tab = QWidget()
        layout = QVBoxLayout(self.reports_tab)
        # Заголовок
        title_label = QLabel("Отчеты и статистика")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        # Кнопки отчетов - теперь вертикально
        reports_layout = QVBoxLayout()  # Изменено на QVBoxLayout для вертикального расположения кнопок
        btn1 = QPushButton("Сводный отчет по исполнителям")
        btn1.clicked.connect(lambda: self.generate_and_show_report(self.generate_executors_report, "Сводный отчет по исполнителям"))
        reports_layout.addWidget(btn1)
        btn2 = QPushButton("Отчет по срокам исполнения")
        btn2.clicked.connect(lambda: self.generate_and_show_report(self.generate_deadlines_report, "Отчет по срокам исполнения"))
        reports_layout.addWidget(btn2)
        btn3 = QPushButton("Финансовый отчет")
        btn3.clicked.connect(lambda: self.generate_and_show_report(self.generate_financial_report, "Финансовый отчет"))
        reports_layout.addWidget(btn3)
        btn4 = QPushButton("Отчет по нарушениям")
        btn4.clicked.connect(lambda: self.generate_and_show_report(self.generate_violations_report, "Отчет по нарушениям"))
        reports_layout.addWidget(btn4)
        layout.addLayout(reports_layout)
        # Встроенный веб-браузер для отображения отчетов
        self.report_browser = QWebEngineView()
        self.report_browser.setHtml("<h2>Выберите отчет для просмотра</h2>")
        layout.addWidget(self.report_browser)
        self.tabs.addTab(self.reports_tab, "Отчеты и статистика")
    def create_reports_unavailable_tab(self):
        """Создание вкладки, информирующей о недоступности отчетов"""
        self.reports_tab = QWidget()
        layout = QVBoxLayout(self.reports_tab)
        # Заголовок
        title_label = QLabel("Отчеты и статистика")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        # Информационное сообщение
        info_label = QLabel(
            "Вкладка отчетов недоступна, так как в системе не установлен модуль QtWebEngine.\n"
            "Пожалуйста, установите пакет `PyQtWebEngine` для использования этой функции."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(info_label)
        layout.addStretch()
        self.tabs.addTab(self.reports_tab, "Отчеты и статистика")
    def generate_and_show_report(self, report_generator, title):
        """Генерирует отчет и отображает его в браузере"""
        try:
            # Генерируем текст отчета
            report_text = report_generator(generate_text_only=True)
            # Конвертируем текст в HTML
            html_content = self.text_to_html(report_text, title)
            # Отображаем в браузере
            self.report_browser.setHtml(html_content)
        except Exception as e:
            error_html = f"<h2>Ошибка</h2><p>Не удалось сгенерировать отчет: {str(e)}</p>"
            self.report_browser.setHtml(error_html)
    def text_to_html(self, text, title):
        """Конвертирует текстовый отчет в HTML"""
        # Экранируем HTML символы
        html_safe_text = text.replace('&', '&amp;').replace('<', '<').replace('>', '>') # <-- ИСПРАВЛЕНО: Правильное экранирование '<'
        # Заменяем переносы строк на <br>
        html_safe_text = html_safe_text.replace('\n', '<br>')
        # Заменяем множественные пробелы на &nbsp;
        html_safe_text = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group()), html_safe_text)
        # Оборачиваем в HTML структуру
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: 'Courier New', monospace; font-size: 14px; margin: 20px; }}
                h1 {{ color: #2E5984; border-bottom: 2px solid #2E5984; padding-bottom: 10px; }}
                pre {{ background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <pre>{html_safe_text}</pre>
        </body>
        </html>
        """
        return html
    def create_about_tab(self):
        """Создание вкладки 'О программе'"""
        self.about_tab = QWidget()
        layout = QVBoxLayout(self.about_tab)
        # Заголовок
        title_label = QLabel("Система управления государственными оборонными заказами")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        # Информация о программе (без описания)
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
            <h2>О программе</h2>
            <p><b>Название:</b> Система управления государственными оборонными заказами</p>
            <p><b>Версия:</b> 1.0</p>
            <p><b>Автор:</b> Шешиков С.А.</p>
            <p><b>Год создания:</b> 2025</p>
            <h3>Основные функции:</h3>
            <ul>
                <li>Ввод и редактирование данных о контрактах ГОЗ</li>
                <li>Прикрепление файлов к каждому контракту</li>
                <li>Импорт данных из Excel-файлов</li>
                <li>Экспорт данных в Excel-файлы</li>
                <li>Формирование отчетов и статистики</li>
                <li>Удобный и интуитивно понятный интерфейс</li>
            </ul>
            <h3>Инструкция по использованию:</h3>
            <ol>
                <li>Перейдите на вкладку "Список контрактов"</li>
                <li>Нажмите "Добавить контракт" для создания новой записи</li>
                <li>Заполните все необходимые поля</li>
                <li>Сохраните контракт</li>
                <li>Для прикрепления файлов выберите контракт и нажмите "Прикрепить файл"</li>
                <li>Для экспорта данных нажмите "Экспорт в Excel"</li>
            </ol>
            <h3>Техническая поддержка:</h3>
            <p>По всем вопросам обращайтесь к автору программы: Шешиков С.А.</p>
        """)
        layout.addWidget(info_text)
        self.tabs.addTab(self.about_tab, "О программе")
    def add_new_contract(self):
        """Добавление нового контракта"""
        self.current_contract_id = None
        self.clear_contract_form()
        self.tabs.setCurrentIndex(1)  # Переключаемся на вкладку добавления/редактирования
    def edit_selected_contract(self):
        """Редактирование выбранного контракта"""
        selected_items = self.contracts_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите контракт для редактирования.")
            return
        row = selected_items[0].row()
        contract_id = int(self.contracts_table.item(row, 0).text())
        self.load_contract_data(contract_id)
        self.tabs.setCurrentIndex(1)
    def load_contract_data(self, contract_id):
        """Загрузка данных контракта в форму редактирования"""
        self.current_contract_id = contract_id
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
        contract_data = cursor.fetchone()
        if contract_data: # <-- ИСПРАВЛЕНО: Явная проверка на существование данных
            # Заполняем основные поля
            self.org_name_input.setText(contract_data[1] or "")
            self.state_customer_name_input.setText(contract_data[2] or "")
            self.state_customer_inn_input.setText(contract_data[3] or "")
            self.state_customer_address_input.setText(contract_data[4] or "")
            self.head_executor_name_input.setText(contract_data[5] or "")
            self.head_executor_inn_input.setText(contract_data[6] or "")
            self.head_executor_address_input.setText(contract_data[7] or "")
            self.contractor_name_input.setText(contract_data[8] or "")
            self.contractor_inn_input.setText(contract_data[9] or "")
            self.contractor_address_input.setText(contract_data[10] or "")
            if contract_data[11]:
                # Обработка разных форматов даты из Excel
                date_str = contract_data[11]
                try:
                    if '.' in date_str:
                        # Формат ДД.ММ.ГГГГ
                        day, month, year = date_str.split('.')
                        if len(year) == 2:
                            year = '20' + year
                        date = QDate(int(year), int(month), int(day))
                    else:
                        # Формат ГГГГ-ММ-ДД
                        date = QDate.fromString(date_str, "yyyy-MM-dd")
                    self.contract_date_input.setDate(date)
                except Exception: # <-- ИСПРАВЛЕНО: Заменено широкое except: на except Exception:
                    self.contract_date_input.setDate(QDate.currentDate())
            self.contract_number_input.setText(contract_data[12] or "")
            self.contract_subject_input.setText(contract_data[13] or "")
            self.contract_price_input.setText(str(contract_data[14]) if contract_data[14] is not None else "") # <-- ИСПРАВЛЕНО: Явная проверка на None
            self.vat_rate_input.setCurrentText(str(contract_data[15]) if contract_data[15] is not None else "20") # <-- ИСПРАВЛЕНО: Явная проверка на None
            # Рассчитываем и заполняем поле НДС
            if contract_data[14] is not None and contract_data[15] is not None: # <-- ИСПРАВЛЕНО: Явная проверка на None
                try:
                    vat_amount = float(contract_data[14]) * float(contract_data[15]) / 100.0
                    self.vat_amount_input.setText(f"{vat_amount:,.2f}".replace(',', ' '))
                except (ValueError, TypeError): # <-- ИСПРАВЛЕНО: Добавлен перехват TypeError
                    self.vat_amount_input.setText("")
            else:
                self.vat_amount_input.setText("")
            self.advance_terms_input.setText(contract_data[16] or "")
            self.advance_size_input.setText(contract_data[17] or "")
            self.final_payment_terms_input.setText(contract_data[18] or "")
            self.execution_deadline_input.setText(contract_data[19] or "")
            if contract_data[20]:
                # Обработка даты приемки
                date_str = contract_data[20]
                try:
                    if '.' in date_str:
                        day, month, year = date_str.split('.')
                        if len(year) == 2:
                            year = '20' + year
                        date = QDate(int(year), int(month), int(day))
                    else:
                        date = QDate.fromString(date_str, "yyyy-MM-dd")
                    self.acceptance_date_input.setDate(date)
                except Exception: # <-- ИСПРАВЛЕНО: Заменено широкое except: на except Exception:
                    self.acceptance_date_input.setDate(QDate.currentDate())
            # Устанавливаем статус с большой буквы
            status = contract_data[21] or "В работе"
            # Упрощенная и надежная установка статуса
            index = self.execution_status_input.findText(status, Qt.MatchFixedString)
            if index < 0:
                # Если точное совпадение не найдено, ищем нечувствительно к регистру
                index = self.execution_status_input.findText(status, Qt.MatchContains)
                if index < 0:
                    # Если все еще не найдено, устанавливаем значение по умолчанию
                    index = self.execution_status_input.findText("В работе", Qt.MatchFixedString)
            self.execution_status_input.setCurrentIndex(index if index >= 0 else 0)
            self.violations_input.setText(contract_data[22] or "")
            # Загружаем платежи
            self.load_payments(contract_id)
            # Загружаем прикрепленные файлы
            self.load_attached_files(contract_id)
    def clear_contract_form(self):
        """Очистка формы контракта"""
        self.org_name_input.clear()
        self.state_customer_name_input.clear()
        self.state_customer_inn_input.clear()
        self.state_customer_address_input.clear()
        self.head_executor_name_input.clear()
        self.head_executor_inn_input.clear()
        self.head_executor_address_input.clear()
        self.contractor_name_input.clear()
        self.contractor_inn_input.clear()
        self.contractor_address_input.clear()
        self.contract_date_input.setDate(QDate.currentDate())
        self.contract_number_input.clear()
        self.contract_subject_input.clear()
        self.contract_price_input.clear()
        self.vat_rate_input.setCurrentText("20")
        self.vat_amount_input.clear()  # Очищаем поле НДС
        self.advance_terms_input.clear()
        self.advance_size_input.clear()
        self.final_payment_terms_input.clear()
        self.execution_deadline_input.clear()
        self.acceptance_date_input.setDate(QDate.currentDate())
        self.execution_status_input.setCurrentText("В работе")  # С большой буквы
        self.violations_input.clear()
        # Очищаем таблицы
        self.payments_table.setRowCount(0)
        self.files_table.setRowCount(0)
        # Сбрасываем флаг несохраненных изменений
        self.unsaved_changes = False
    def load_payments(self, contract_id):
        """Загрузка платежей для контракта"""
        self.payments_table.setRowCount(0)
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, payment_date, payment_amount FROM contract_payments WHERE contract_id = ? ORDER BY payment_date", (contract_id,))
        for row_num, row_data in enumerate(cursor.fetchall()):
            self.payments_table.insertRow(row_num)
            self.payments_table.setItem(row_num, 0, QTableWidgetItem(row_data[1] if row_data[1] is not None else "")) # <-- ИСПРАВЛЕНО: Явная проверка на None
            self.payments_table.setItem(row_num, 1, QTableWidgetItem(str(row_data[2]) if row_data[2] is not None else "")) # <-- ИСПРАВЛЕНО: Явная проверка на None
            # Добавляем кнопку удаления
            # ВАЖНО: Использование lambda в цикле может быть неочевидным. Здесь оно работает,
            # потому что значение row_data[0] захватывается по значению на момент создания lambda.
            # Однако, это потенциальный источник ошибок в других сценариях.
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda _, payment_id=row_data[0]: self.delete_payment(payment_id))
            self.payments_table.setCellWidget(row_num, 2, delete_btn)
    def add_payment(self):
        """Добавление платежа через диалоговое окно"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить платеж")
        dialog.setModal(True)
        dialog.resize(400, 200)
        layout = QVBoxLayout(dialog)
        # Ввод даты
        date_layout = QHBoxLayout()
        date_label = QLabel("Дата платежа (ДД.ММ.ГГГГ):")
        self.payment_date_input = QLineEdit()
        self.payment_date_input.setPlaceholderText("например, 01.01.2025")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.payment_date_input)
        layout.addLayout(date_layout)
        # Ввод суммы
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Сумма платежа (руб):")
        self.payment_amount_input = QLineEdit()
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.payment_amount_input)
        layout.addLayout(amount_layout)
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        if dialog.exec_() == QDialog.Accepted:
            payment_date = self.payment_date_input.text().strip()
            payment_amount_text = self.payment_amount_input.text().strip()
            if not payment_date:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите дату платежа.")
                return
            if not payment_amount_text:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите сумму платежа.")
                return
            try:
                payment_amount = float(payment_amount_text)
                if not self.current_contract_id:
                    QMessageBox.warning(self, "Ошибка", "Сначала сохраните контракт.")
                    return
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO contract_payments (contract_id, payment_date, payment_amount)
                    VALUES (?, ?, ?)
                """, (self.current_contract_id, payment_date, payment_amount))
                self.db_conn.commit()
                self.load_payments(self.current_contract_id)
                QMessageBox.information(self, "Успех", "Платеж успешно добавлен.")
                self.unsaved_changes = True  # <-- ИСПРАВЛЕНО: Было False, стало True
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Неверный формат суммы платежа.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при добавлении платежа: {str(e)}")
    def delete_payment(self, payment_id):
        """Удаление платежа"""
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот платеж?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM contract_payments WHERE id = ?", (payment_id,))
            self.db_conn.commit()
            self.load_payments(self.current_contract_id)
            self.unsaved_changes = True
    def load_attached_files(self, contract_id):
        """Загрузка прикрепленных файлов для контракта"""
        self.files_table.setRowCount(0)
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, file_name, upload_date
            FROM attached_files
            WHERE contract_id = ?
            ORDER BY upload_date DESC
        """, (contract_id,))
        for row_num, row_data in enumerate(cursor.fetchall()):
            self.files_table.insertRow(row_num)
            self.files_table.setItem(row_num, 0, QTableWidgetItem(row_data[1] if row_data[1] is not None else "")) # <-- ИСПРАВЛЕНО: Явная проверка на None
            self.files_table.setItem(row_num, 1, QTableWidgetItem(row_data[2] if row_data[2] is not None else "")) # <-- ИСПРАВЛЕНО: Явная проверка на None
            # Добавляем кнопки действий
            # ВАЖНО: Использование lambda в цикле может быть неочевидным. Здесь оно работает,
            # потому что значение row_data[0] захватывается по значению на момент создания lambda.
            # Однако, это потенциальный источник ошибок в других сценариях.
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            open_btn = QPushButton("Открыть")
            open_btn.clicked.connect(lambda _, file_id=row_data[0]: self.open_attached_file(file_id))
            actions_layout.addWidget(open_btn)
            delete_btn = QPushButton("Удалить")
            delete_btn.clicked.connect(lambda _, file_id=row_data[0]: self.delete_attached_file(file_id))
            actions_layout.addWidget(delete_btn)
            self.files_table.setCellWidget(row_num, 2, actions_widget)
    def attach_file_to_contract(self):
        """Прикрепление файла к выбранному контракту"""
        selected_items = self.contracts_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите контракт для прикрепления файла.")
            return
        row = selected_items[0].row()
        contract_id = int(self.contracts_table.item(row, 0).text())
        self.attach_file(contract_id)
    def attach_file_to_current_contract(self):
        """Прикрепление файла к текущему контракту"""
        if not self.current_contract_id:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните контракт.")
            return
        self.attach_file(self.current_contract_id)
    def attach_file(self, contract_id):
        """Прикрепление файла к контракту"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл для прикрепления")
        if not file_path:
            return
        file_name = os.path.basename(file_path)
        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Создаем директорию для хранения файлов, если она не существует
        files_dir = "attached_files"
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
        # Генерируем уникальное имя файла
        file_ext = os.path.splitext(file_name)[1]
        unique_file_name = f"{contract_id}_{int(datetime.now().timestamp())}{file_ext}"
        destination_path = os.path.join(files_dir, unique_file_name)
        # Копируем файл
        try:
            with open(file_path, 'rb') as src_file:
                with open(destination_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            # Сохраняем информацию о файле в базе данных
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO attached_files (contract_id, file_path, file_name, upload_date)
                VALUES (?, ?, ?, ?)
            """, (contract_id, destination_path, file_name, upload_date))
            self.db_conn.commit()
            # Обновляем таблицу файлов, если редактируем текущий контракт
            if self.current_contract_id == contract_id:
                self.load_attached_files(contract_id)
            QMessageBox.information(self, "Успех", "Файл успешно прикреплен к контракту.")
            self.unsaved_changes = True
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при прикреплении файла: {str(e)}")
    def open_attached_file(self, file_id):
        """Открытие прикрепленного файла"""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT file_path FROM attached_files WHERE id = ?", (file_id,))
        result = cursor.fetchone()
        if result and result[0]:
            file_path = result[0]
            if os.path.exists(file_path):
                try:
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    elif sys.platform == "darwin":  # macOS
                        os.system(f"open '{file_path}'")
                    else:  # Linux
                        os.system(f"xdg-open '{file_path}'")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не найден на диске.")
        else:
            QMessageBox.warning(self, "Ошибка", "Файл не найден в базе данных.")
    def delete_attached_file(self, file_id):
        """Удаление прикрепленного файла"""
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот файл?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT file_path FROM attached_files WHERE id = ?", (file_id,))
            result = cursor.fetchone()
            if result and result[0]:
                file_path = result[0]
                # Удаляем файл с диска
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        QMessageBox.warning(self, "Предупреждение", f"Не удалось удалить файл с диска: {str(e)}")
            # Удаляем запись из базы данных
            cursor.execute("DELETE FROM attached_files WHERE id = ?", (file_id,))
            self.db_conn.commit()
            # Обновляем таблицу файлов, если редактируем текущий контракт
            if self.current_contract_id:
                self.load_attached_files(self.current_contract_id)
            QMessageBox.information(self, "Успех", "Файл успешно удален.")
            self.unsaved_changes = True
    def save_contract(self):
        """Сохранение контракта"""
        try:
            # Валидация обязательных полей
            if not self.org_name_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите наименование организации.")
                return
            if not self.contract_number_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите номер контракта.")
                return
            contract_price = 0.0
            if self.contract_price_input.text().strip():
                try:
                    contract_price = float(self.contract_price_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Неверный формат цены контракта.")
                    return
            vat_rate = float(self.vat_rate_input.currentText())
            contract_date = self.contract_date_input.date().toString("yyyy-MM-dd")
            acceptance_date = self.acceptance_date_input.date().toString("yyyy-MM-dd")
            # Получаем статус с большой буквы
            execution_status = self.execution_status_input.currentText()
            cursor = self.db_conn.cursor()
            if self.current_contract_id:
                # Обновляем существующий контракт
                cursor.execute("""
                    UPDATE contracts SET
                        organization_name = ?, state_customer_name = ?, state_customer_inn = ?,
                        state_customer_address = ?, head_executor_name = ?, head_executor_inn = ?,
                        head_executor_address = ?, contractor_name = ?, contractor_inn = ?,
                        contractor_address = ?, contract_date = ?, contract_number = ?,
                        contract_subject = ?, contract_price = ?, vat_rate = ?,
                        advance_terms = ?, advance_size = ?, final_payment_terms = ?,
                        execution_deadline = ?, acceptance_date = ?, execution_status = ?,
                        violations = ?
                    WHERE id = ?
                """, (
                    self.org_name_input.text().strip(),
                    self.state_customer_name_input.text().strip(),
                    self.state_customer_inn_input.text().strip(),
                    self.state_customer_address_input.text().strip(),
                    self.head_executor_name_input.text().strip(),
                    self.head_executor_inn_input.text().strip(),
                    self.head_executor_address_input.text().strip(),
                    self.contractor_name_input.text().strip(),
                    self.contractor_inn_input.text().strip(),
                    self.contractor_address_input.text().strip(),
                    contract_date,
                    self.contract_number_input.text().strip(),
                    self.contract_subject_input.toPlainText().strip(),
                    contract_price,
                    vat_rate,
                    self.advance_terms_input.toPlainText().strip(),
                    self.advance_size_input.text().strip(),
                    self.final_payment_terms_input.toPlainText().strip(),
                    self.execution_deadline_input.text().strip(),
                    acceptance_date,
                    execution_status,  # С большой буквы
                    self.violations_input.toPlainText().strip(),
                    self.current_contract_id
                ))
            else:
                # Создаем новый контракт
                cursor.execute("""
                    INSERT INTO contracts (
                        organization_name, state_customer_name, state_customer_inn,
                        state_customer_address, head_executor_name, head_executor_inn,
                        head_executor_address, contractor_name, contractor_inn,
                        contractor_address, contract_date, contract_number,
                        contract_subject, contract_price, vat_rate,
                        advance_terms, advance_size, final_payment_terms,
                        execution_deadline, acceptance_date, execution_status,
                        violations
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.org_name_input.text().strip(),
                    self.state_customer_name_input.text().strip(),
                    self.state_customer_inn_input.text().strip(),
                    self.state_customer_address_input.text().strip(),
                    self.head_executor_name_input.text().strip(),
                    self.head_executor_inn_input.text().strip(),
                    self.head_executor_address_input.text().strip(),
                    self.contractor_name_input.text().strip(),
                    self.contractor_inn_input.text().strip(),
                    self.contractor_address_input.text().strip(),
                    contract_date,
                    self.contract_number_input.text().strip(),
                    self.contract_subject_input.toPlainText().strip(),
                    contract_price,
                    vat_rate,
                    self.advance_terms_input.toPlainText().strip(),
                    self.advance_size_input.text().strip(),
                    self.final_payment_terms_input.toPlainText().strip(),
                    self.execution_deadline_input.text().strip(),
                    acceptance_date,
                    execution_status,  # С большой буквы
                    self.violations_input.toPlainText().strip()
                ))
                self.current_contract_id = cursor.lastrowid
            self.db_conn.commit()
            QMessageBox.information(self, "Успех", "Контракт успешно сохранен.")
            self.unsaved_changes = False
            # Обновляем список контрактов
            self.load_contracts_data()
            # Переключаемся на вкладку списка контрактов
            self.tabs.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении контракта: {str(e)}")
    def cancel_edit(self):
        """Отмена редактирования"""
        self.clear_contract_form()
        self.current_contract_id = None
        self.tabs.setCurrentIndex(0)
    def delete_selected_contract(self):
        """Удаление выбранного контракта"""
        selected_items = self.contracts_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите контракт для удаления.")
            return
        row = selected_items[0].row()
        contract_id = int(self.contracts_table.item(row, 0).text())
        contract_number = self.contracts_table.item(row, 4).text()
        # ИСПРАВЛЕНО: Незакрытая f-строка - теперь используем двойные кавычки для внешней строки
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить контракт №{contract_number}?\n"
            "Все связанные данные (платежи, файлы) также будут удалены.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_conn.cursor()
                # Удаляем прикрепленные файлы и сами файлы с диска
                cursor.execute("SELECT file_path FROM attached_files WHERE contract_id = ?", (contract_id,))
                files = cursor.fetchall()
                for file in files:
                    if file[0] and os.path.exists(file[0]):
                        try:
                            os.remove(file[0])
                        except Exception as e:
                            # ИСПРАВЛЕНО: Заменено print на logging.warning
                            logging.warning(f"Ошибка при удалении файла {file[0]}: {str(e)}")
                # Удаляем все связанные данные
                cursor.execute("DELETE FROM attached_files WHERE contract_id = ?", (contract_id,))
                cursor.execute("DELETE FROM contract_payments WHERE contract_id = ?", (contract_id,))
                cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
                self.db_conn.commit()
                QMessageBox.information(self, "Успех", "Контракт успешно удален.")
                self.load_contracts_data()
                self.unsaved_changes = False
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при удалении контракта: {str(e)}")
    def parse_date_from_excel(self, date_str):
        """Улучшенный парсинг дат из Excel файла"""
        if not date_str or not isinstance(date_str, str):
            return None
        date_str = date_str.strip()
        # Обработка формата ДД.ММ.ГГГГ
        if re.match(r'\d{1,2}\.\d{1,2}\.\d{4}', date_str):
            parts = date_str.split('.')
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        # Обработка формата ММ.ГГ (например, Aug.24)
        elif re.match(r'[A-Za-z]{3,}\.\d{2}', date_str):
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            parts = date_str.split('.')
            month_abbr = parts[0][:3].title()
            # Явная проверка наличия сокращенного названия месяца # <-- ИСПРАВЛЕНО: Добавлена явная проверка
            if month_abbr not in month_map:
                 return None # <-- ИСПРАВЛЕНО: Возвращаем None, если месяц не найден
            year_short = parts[1]
            month = month_map.get(month_abbr, '01')
            year = f"20{year_short}" if len(year_short) == 2 else year_short
            # Устанавливаем первое число месяца как дату
            return f"{year}-{month}-01"
        # Обработка формата "квартал.год" (например, 4 кв.2025)
        elif 'кв.' in date_str:
            parts = date_str.split('кв.')
            try:
                quarter = int(parts[0].strip())
                year = parts[1].strip()
                # Устанавливаем первый день квартала
                quarter_start = {1: '01-01', 2: '04-01', 3: '07-01', 4: '10-01'}
                return f"{year}-{quarter_start.get(quarter, '01-01')}"
            except (ValueError, IndexError):
                return None
        # Обработка формата только год (например, 2025)
        elif re.match(r'^\d{4}$', date_str):
            return f"{date_str}-01-01"
        return None  # Если формат не распознан
    def parse_price_from_excel(self, price_str):
        """Извлечение числовой цены из строки Excel"""
        if not price_str or not isinstance(price_str, str):
            return 0.0
        # Извлекаем первое число из строки
        match = re.search(r'[\d\s,\.]+', price_str)
        if match:
            num_str = match.group(0).replace(' ', '').replace(',', '.')
            try:
                return float(num_str)
            except ValueError:
                return 0.0
        return 0.0
    def parse_contractor_info(self, contractor_str):
        """Парсинг информации о контрагенте из строки"""
        if not contractor_str or not isinstance(contractor_str, str):
            return "", "", ""
        name = ""
        inn = ""
        address = ""
        # Поиск ИНН
        # ИСПРАВЛЕНО: Уточнено регулярное выражение для поиска ИНН в начале строки или после пробела
        inn_match = re.search(r'\bИНН\s*(\d+)', contractor_str)
        if inn_match:
            inn = inn_match.group(1)
            # Название - всё до ИНН
            name_part = contractor_str[:inn_match.start()].strip()
            name = name_part
            # Адрес - всё после ИНН и цифр ИНН
            address_part = contractor_str[inn_match.end():].strip()
            # Удаляем сам ИНН из адреса, если он там остался
            address = re.sub(r'^\d+\s*', '', address_part).strip()
        else:
            # Если ИНН не найден, считаем всю строку названием
            name = contractor_str.strip()
        return name, inn, address
    def import_from_excel(self):
        """Импорт данных из Excel файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите Excel файл для импорта", "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path, header=None)
            # Пропускаем первые строки с заголовками
            start_row = 0
            for i, row in df.iterrows():
                # ИСПРАВЛЕНО: Комментарий о необходимости более надежного способа определения начала данных
                # Например, наличие нескольких ключевых заголовков в строке.
                if "Наименование организации" in str(row[0]) or "АО" in str(row[0]):
                    start_row = i
                    break
            imported_count = 0
            cursor = self.db_conn.cursor()
            # Обрабатываем строки
            i = start_row
            while i < len(df):
                row = df.iloc[i]
                if pd.isna(row[0]) or str(row[0]).strip() == "":
                    i += 1
                    continue
                # Проверяем, что это строка с данными организации
                if "АО" in str(row[0]) or "ООО" in str(row[0]):
                    try:
                        # Извлекаем данные
                        organization_name = str(row[0]).strip()
                        state_customer_name = str(row[1]).strip() if not pd.isna(row[1]) else ""
                        head_executor_name = str(row[2]).strip() if not pd.isna(row[2]) else ""
                        # Для контрагента используем данные из строки или следующей
                        contractor_info = ""
                        if len(row) > 3 and not pd.isna(row[3]):
                            contractor_info = str(row[3]).strip()
                        elif i+1 < len(df) and not pd.isna(df.iloc[i+1][0]):
                            contractor_info = str(df.iloc[i+1][0]).strip()
                        # Парсим информацию о контрагенте
                        contractor_name, contractor_inn, contractor_address = self.parse_contractor_info(contractor_info)
                        # Дата заключения контракта
                        contract_date = ""
                        if len(row) > 4 and not pd.isna(row[4]):
                            contract_date = self.parse_date_from_excel(str(row[4]).strip()) or ""
                        # Номер и предмет контракта
                        contract_number = ""
                        contract_subject = ""
                        if len(row) > 5 and not pd.isna(row[5]):
                            contract_text = str(row[5]).strip()
                            if "№" in contract_text:
                                parts = contract_text.split("№", 1)
                                contract_subject = parts[0].strip()
                                contract_number = "№" + parts[1].strip()
                            else:
                                contract_subject = contract_text
                        # Цена контракта
                        contract_price = 0.0
                        if len(row) > 6 and not pd.isna(row[6]):
                            contract_price = self.parse_price_from_excel(str(row[6]).strip())
                        # Сроки авансирования
                        advance_terms = ""
                        if len(row) > 7 and not pd.isna(row[7]):
                            advance_terms = str(row[7]).strip()
                        # Размер авансирования
                        advance_size = ""
                        if len(row) > 8 and not pd.isna(row[8]):
                            advance_size = str(row[8]).strip()
                        # Сроки окончательного расчета
                        final_payment_terms = ""
                        if len(row) > 9 and not pd.isna(row[9]):
                            final_payment_terms = str(row[9]).strip()
                        # Срок исполнения
                        execution_deadline = ""
                        if len(row) > 12 and not pd.isna(row[12]):
                            execution_deadline = str(row[12]).strip()
                        # Дата приемки
                        acceptance_date = ""
                        # ИСПРАВЛЕНО: Добавлена явная проверка pd.isna(row[13])
                        if len(row) > 13 and not pd.isna(row[13]):
                            acceptance_date = self.parse_date_from_excel(str(row[13]).strip()) or ""
                        # Статус исполнения
                        execution_status = "В работе"
                        if len(row) > 14 and not pd.isna(row[14]):
                            status = str(row[14]).strip()
                            if "выполнен" in status.lower():
                                execution_status = "Выполнен"
                            elif "в работе" in status.lower():
                                execution_status = "В работе"
                            elif "просрочен" in status.lower():
                                execution_status = "Просрочен"
                            elif "отменен" in status.lower():
                                execution_status = "Отменен"
                        elif acceptance_date:
                            # Если указана дата приемки, но не указан статус
                            execution_status = "Выполнен"
                        # Вставляем данные в базу
                        cursor.execute("""
                            INSERT INTO contracts (
                                organization_name, state_customer_name, head_executor_name,
                                contractor_name, contractor_inn, contractor_address,
                                contract_date, contract_number, contract_subject,
                                contract_price, vat_rate, advance_terms,
                                advance_size, final_payment_terms, execution_deadline,
                                acceptance_date, execution_status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            organization_name,
                            state_customer_name,
                            head_executor_name,
                            contractor_name,
                            contractor_inn,
                            contractor_address,
                            contract_date,
                            contract_number,
                            contract_subject,
                            contract_price,
                            20.0,  # По умолчанию ставка НДС 20%
                            advance_terms,
                            advance_size,
                            final_payment_terms,
                            execution_deadline,
                            acceptance_date,
                            execution_status  # С большой буквы
                        ))
                        imported_count += 1
                    except Exception as e:
                        print(f"Ошибка при импорте строки {i}: {str(e)}")
                        continue
                i += 1
            self.db_conn.commit()
            QMessageBox.information(self, "Успех", f"Успешно импортировано {imported_count} контрактов.")
            self.load_contracts_data()
            self.unsaved_changes = False
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при импорте из Excel: {str(e)}")
    def export_to_excel(self):
        """Экспорт данных в Excel файл с улучшенным форматированием"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить Excel файл", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT
                    c.id,
                    c.organization_name,
                    c.state_customer_name,
                    c.state_customer_inn,
                    c.head_executor_name,
                    c.head_executor_inn,
                    c.contract_number,
                    c.contract_subject,
                    c.contract_price,
                    c.vat_rate,
                    c.execution_status,
                    c.execution_deadline,
                    c.acceptance_date,
                    c.advance_terms,
                    c.advance_size,
                    c.final_payment_terms,
                    c.violations
                FROM contracts c
                ORDER BY c.id DESC
            """)
            rows = cursor.fetchall()
            columns = [
                "ID",
                "Наименование организации",
                "Наименование госзаказчика",
                "ИНН госзаказчика",
                "Наименование исполнителя",
                "ИНН исполнителя",
                "Номер контракта",
                "Предмет контракта",
                "Цена контракта (руб)",
                "Ставка НДС (%)",
                "Статус исполнения",
                "Срок исполнения",
                "Дата приемки",
                "Сроки авансирования",
                "Размер авансирования (%)",
                "Сроки окончательного расчета",
                "Нарушения и меры реагирования"
            ]
            df = pd.DataFrame(rows, columns=columns)
            # Создаем рабочую книгу и лист
            wb = Workbook()
            ws = wb.active
            ws.title = "Реестр контрактов ГОЗ"
            # Заголовок отчета
            ws.merge_cells('A1:Q1')
            title_cell = ws['A1']
            title_cell.value = "РЕЕСТР ГОСУДАРСТВЕННЫХ КОНТРАКТОВ ГОЗ"
            title_cell.font = Font(name='Arial', size=16, bold=True, color='FFFFFF')
            title_cell.fill = PatternFill(start_color='2E5984', end_color='2E5984', fill_type='solid')
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            # Добавляем текущую дату
            ws.merge_cells('A2:Q2')
            date_cell = ws['A2']
            date_cell.value = f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            date_cell.font = Font(name='Arial', size=10, italic=True)
            date_cell.alignment = Alignment(horizontal='right')
            # Создаем заголовки столбцов
            for col_num, column_title in enumerate(columns, 1):
                cell = ws.cell(row=4, column=col_num, value=column_title)
                cell.font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
                cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
            # Добавляем данные
            for row_num, row_data in enumerate(rows, 5):
                for col_num, cell_value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=cell_value)
                    cell.font = Font(name='Arial', size=10)
                    cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                    cell.border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )
                    # Особое форматирование для цены
                    if col_num == 9:  # Цена контракта
                        if isinstance(cell_value, (int, float)):
                            cell.number_format = '#,##0.00 ₽'
                        cell.alignment = Alignment(horizontal='right', vertical='center')
                    # Особое форматирование для статуса
                    if col_num == 11:  # Статус исполнения
                        if cell_value == "Выполнен":
                            cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
                            cell.font = Font(name='Arial', size=10, color='006100')
                        elif cell_value == "В работе":
                            cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
                            cell.font = Font(name='Arial', size=10, color='9C5700')
                        elif cell_value == "Просрочен":
                            cell.fill = PatternFill(start_color='F8CBAD', end_color='F8CBAD', fill_type='solid')
                            cell.font = Font(name='Arial', size=10, color='9C0006')
                        elif cell_value == "Отменен":
                            cell.fill = PatternFill(start_color='D9D9D9', end_color='D9D9D9', fill_type='solid')
                            cell.font = Font(name='Arial', size=10, color='808080')
            # Автоматически подгоняем ширину столбцов
            for col_num, column_title in enumerate(columns, 1):
                max_length = len(str(column_title))
                for row_data in rows:
                    cell_value = str(row_data[col_num-1]) if row_data[col_num-1] is not None else "" # <-- ИСПРАВЛЕНО: Явная проверка на None
                    max_length = max(max_length, len(cell_value))
                adjusted_width = min(max_length + 2, 50)
                # ИСПРАВЛЕНО: Заменено chr(64 + col_num) на openpyxl.utils.get_column_letter(col_num) # <-- ИСПРАВЛЕНО: Использование get_column_letter
                col_letter = openpyxl.utils.get_column_letter(col_num)
                ws.column_dimensions[col_letter].width = adjusted_width
            # Устанавливаем высоту строк с заголовками
            ws.row_dimensions[4].height = 30
            # Закрепляем заголовки
            ws.freeze_panes = 'A5'
            # Добавляем автофильтр
            ws.auto_filter.ref = f"A4:Q{len(rows) + 4}"
            # Сохраняем файл
            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"Данные успешно экспортированы в файл:\n{file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при экспорте в Excel: {str(e)}")
    def generate_executors_report(self, generate_text_only=False):
        """Генерация отчета по исполнителям"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT
                    head_executor_name,
                    COUNT(*) as total_contracts,
                    SUM(contract_price) as total_amount,
                    SUM(CASE WHEN execution_status = 'Выполнен' THEN 1 ELSE 0 END) as completed_contracts,
                    SUM(CASE WHEN execution_status = 'В работе' THEN 1 ELSE 0 END) as in_progress_contracts,
                    SUM(CASE WHEN execution_status = 'Просрочен' THEN 1 ELSE 0 END) as overdue_contracts
                FROM contracts
                WHERE head_executor_name IS NOT NULL AND head_executor_name != ''
                GROUP BY head_executor_name
                ORDER BY total_amount DESC
            """)
            rows = cursor.fetchall()
            report_text = "СВОДНЫЙ ОТЧЕТ ПО ИСПОЛНИТЕЛЯМ\n"
            report_text += "{:<30} {:<15} {:<20} {:<12} {:<12} {:<12}\n".format(
                "Наименование исполнителя", "Всего контрактов", "Общая сумма", "Выполнено", "В работе", "Просрочено"
            )
            report_text += "-" * 120 + "\n"
            for row in rows:
                report_text += "{:<30} {:<15} {:<20,.2f} {:<12} {:<12} {:<12}\n".format(
                    row[0] if row[0] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[1] if row[1] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[2] if row[2] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[3] if row[3] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[4] if row[4] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[5] if row[5] is not None else 0 # <-- ИСПРАВЛЕНО: Явная проверка на None
                )
            return report_text
        except Exception as e:
            error_msg = f"Ошибка при генерации отчета: {str(e)}"
            if generate_text_only:
                return error_msg
            else:
                QMessageBox.warning(self, "Ошибка", error_msg)
    def generate_deadlines_report(self, generate_text_only=False):
        """Генерация отчета по срокам исполнения"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT
                    contract_number,
                    organization_name,
                    head_executor_name,
                    execution_deadline,
                    acceptance_date,
                    execution_status,
                    contract_price,
                    CASE
                        WHEN execution_status = 'Выполнен' THEN 'Выполнен в срок'
                        WHEN execution_status = 'В работе' AND execution_deadline < DATE('now') THEN 'Просрочен'
                        WHEN execution_status = 'В работе' THEN 'В срок'
                        WHEN execution_status = 'Просрочен' THEN 'Просрочен'
                        ELSE 'Не определено'
                    END as deadline_status
                FROM contracts
                ORDER BY
                    CASE WHEN execution_status = 'В работе' THEN 1 ELSE 2 END,
                    execution_deadline
            """)
            rows = cursor.fetchall()
            report_text = "ОТЧЕТ ПО СРОКАМ ИСПОЛНЕНИЯ КОНТРАКТОВ\n"
            report_text += "{:<20} {:<25} {:<25} {:<15} {:<12} {:<15} {:<20}\n".format(
                "Номер контракта", "Организация", "Исполнитель", "Срок исполнения", "Статус", "Сумма", "Соблюдение сроков"
            )
            report_text += "-" * 150 + "\n"
            for row in rows:
                report_text += "{:<20} {:<25} {:<25} {:<15} {:<12} {:<15,.2f} {:<20}\n".format(
                    row[0] if row[0] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[1] if row[1] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[2] if row[2] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[3] if row[3] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[5] if row[5] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[6] if row[6] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[7] if row[7] is not None else "" # <-- ИСПРАВЛЕНО: Явная проверка на None
                )
            return report_text
        except Exception as e:
            error_msg = f"Ошибка при генерации отчета: {str(e)}"
            if generate_text_only:
                return error_msg
            else:
                QMessageBox.warning(self, "Ошибка", error_msg)
    def generate_financial_report(self, generate_text_only=False):
        """Генерация финансового отчета - ИСПРАВЛЕНА ОШИБКА"""
        try:
            cursor = self.db_conn.cursor()
            # Общая статистика
            cursor.execute("SELECT COALESCE(SUM(contract_price), 0), COUNT(*) FROM contracts")
            result = cursor.fetchone()
            total_sum = result[0] if result[0] is not None else 0
            total_count = result[1]
            cursor.execute("SELECT COALESCE(SUM(contract_price), 0) FROM contracts WHERE execution_status = 'Выполнен'")
            result = cursor.fetchone()
            completed_sum = result[0] if result[0] is not None else 0
            cursor.execute("SELECT COALESCE(SUM(contract_price), 0) FROM contracts WHERE execution_status = 'В работе'")
            result = cursor.fetchone()
            in_progress_sum = result[0] if result[0] is not None else 0
            cursor.execute("SELECT COALESCE(SUM(contract_price), 0) FROM contracts WHERE execution_status = 'Просрочен'")
            result = cursor.fetchone()
            overdue_sum = result[0] if result[0] is not None else 0
            # Подробный отчет по платежам
            cursor.execute("""
                SELECT
                    c.contract_number,
                    c.organization_name,
                    c.head_executor_name,
                    c.contract_price,
                    COALESCE(SUM(p.payment_amount), 0) as paid_amount,
                    c.contract_price - COALESCE(SUM(p.payment_amount), 0) as remaining_amount,
                    c.execution_status
                FROM contracts c
                LEFT JOIN contract_payments p ON c.id = p.contract_id
                GROUP BY c.id, c.contract_number, c.organization_name, c.head_executor_name, c.contract_price, c.execution_status
                ORDER BY c.contract_price DESC
            """)
            payment_rows = cursor.fetchall()
            report_text = "ФИНАНСОВЫЙ ОТЧЕТ ПО ГОСУДАРСТВЕННЫМ ОБОРОННЫМ ЗАКАЗАМ\n"
            report_text += "=" * 80 + "\n"
            report_text += "ОБЩАЯ СТАТИСТИКА\n"
            report_text += "=" * 80 + "\n"
            report_text += f"Общее количество контрактов: {total_count}\n"
            report_text += f"Общая сумма контрактов: {total_sum:,.2f} руб.\n"
            report_text += f"Сумма выполненных контрактов: {completed_sum:,.2f} руб.\n"
            report_text += f"Сумма контрактов в работе: {in_progress_sum:,.2f} руб.\n"
            report_text += f"Сумма просроченных контрактов: {overdue_sum:,.2f} руб.\n"
            report_text += "=" * 80 + "\n"
            report_text += "ДЕТАЛИЗАЦИЯ ПО КОНТРАКТАМ\n"
            report_text += "=" * 80 + "\n"
            report_text += "{:<20} {:<25} {:<25} {:<15} {:<15} {:<15} {:<15}\n".format(
                "Номер контракта", "Организация", "Исполнитель", "Общая сумма", "Оплачено", "Остаток", "Статус"
            )
            report_text += "-" * 120 + "\n"
            for row in payment_rows:
                # Обработка NULL значений
                contract_number = row[0] if row[0] is not None else "" # <-- ИСПРАВЛЕНО: Явная проверка на None
                organization_name = row[1] if row[1] is not None else "" # <-- ИСПРАВЛЕНО: Явная проверка на None
                head_executor_name = row[2] if row[2] is not None else "" # <-- ИСПРАВЛЕНО: Явная проверка на None
                contract_price = row[3] if row[3] is not None else 0 # <-- ИСПРАВЛЕНО: Явная проверка на None
                paid_amount = row[4] if row[4] is not None else 0 # <-- ИСПРАВЛЕНО: Явная проверка на None
                remaining_amount = row[5] if row[5] is not None else 0 # <-- ИСПРАВЛЕНО: Явная проверка на None
                execution_status = row[6] if row[6] is not None else "Не определен" # <-- ИСПРАВЛЕНО: Явная проверка на None
                report_text += "{:<20} {:<25} {:<25} {:<15,.2f} {:<15,.2f} {:<15,.2f} {:<15}\n".format(
                    contract_number,
                    organization_name,
                    head_executor_name,
                    contract_price,
                    paid_amount,
                    remaining_amount,
                    execution_status
                )
            return report_text
        except Exception as e:
            error_msg = f"Ошибка при генерации отчета: {str(e)}"
            if generate_text_only:
                return error_msg
            else:
                QMessageBox.warning(self, "Ошибка", error_msg)
    def generate_violations_report(self, generate_text_only=False):
        """Генерация отчета по нарушениям"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT
                    contract_number,
                    organization_name,
                    head_executor_name,
                    contractor_name,
                    execution_status,
                    violations,
                    contract_price
                FROM contracts
                WHERE violations IS NOT NULL AND violations != ''
                ORDER BY contract_price DESC
            """)
            rows = cursor.fetchall()
            report_text = "ОТЧЕТ ПО ВЫЯВЛЕННЫМ НАРУШЕНИЯМ\n"
            report_text += "{:<20} {:<25} {:<25} {:<25} {:<15} {:<15} {:<50}\n".format(
                "Номер контракта", "Организация", "Исполнитель", "Контрагент", "Статус", "Сумма", "Описание нарушений"
            )
            report_text += "-" * 150 + "\n"
            for row in rows:
                violations_text = (row[5] if row[5] is not None else "").replace('\n', ' ').replace('\r', ' ') if row[5] else "" # <-- ИСПРАВЛЕНО: Явная проверка на None и обработка возможного None
                report_text += "{:<20} {:<25} {:<25} {:<25} {:<15} {:<15,.2f} {:<50}\n".format(
                    row[0] if row[0] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[1] if row[1] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[2] if row[2] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[3] if row[3] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[4] if row[4] is not None else "", # <-- ИСПРАВЛЕНО: Явная проверка на None
                    row[6] if row[6] is not None else 0, # <-- ИСПРАВЛЕНО: Явная проверка на None
                    violations_text[:47] + "..." if len(violations_text) > 50 else violations_text
                )
            if len(rows) == 0:
                report_text += "Нарушений не выявлено.\n"
            return report_text
        except Exception as e:
            error_msg = f"Ошибка при генерации отчета: {str(e)}"
            if generate_text_only:
                return error_msg
            else:
                QMessageBox.warning(self, "Ошибка", error_msg)
    def closeEvent(self, event):
        """Обработка закрытия приложения с подтверждением"""
        if self.unsaved_changes:
            # ИСПРАВЛЕНО: Использование многострочной строки без f-строки для большей надежности
            reply = QMessageBox.question(
                self,
                "Подтверждение закрытия",
                "Есть несохраненные изменения. Вы уверены, что хотите выйти?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.db_conn:
                    self.db_conn.close()
                event.accept()
            else:
                event.ignore()
        else:
            if self.db_conn:
                self.db_conn.close()
            event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Устанавливаем современный стиль
    window = GOZManagementApp()
    window.show()
    sys.exit(app.exec_())
