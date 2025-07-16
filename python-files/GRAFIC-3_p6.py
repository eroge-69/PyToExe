import sys
import sqlite3
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QCalendarWidget, QVBoxLayout, QWidget, QTabWidget, QComboBox,
    QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QLabel,
    QGroupBox, QFormLayout, QMenu, QHeaderView, QAbstractItemView,
    QDialog, QTextEdit, QDialogButtonBox, QToolTip
)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QColor, QBrush, QCursor, QIcon, QPixmap


class MessageDialog(QDialog):
    """Dialog for editing the message before sending to Telegram."""
    def __init__(self, initial_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование сообщения")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_message(self):
        return self.text_edit.toPlainText()


class GrafikApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("График выездов")
        self.setGeometry(100, 100, 1400, 800)
        
        # Telegram API
        self.TELEGRAM_TOKEN = "5735833748:AAGkAuwB8fXs9BIJyhhhdBKhFufQmnYI-bI"
        self.DEFAULT_CHAT_ID = "1644869032"
        
        # Подключение к БД с обработкой ошибок
        try:
            self.conn = sqlite3.connect("DATA_Grafik.db")
            self.cursor = self.conn.cursor()
            self.init_db()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка подключения к базе данных: {str(e)}")
            sys.exit(1)
        
        # Текущая выбранная дата
        self.current_date = QDate.currentDate().toString("yyyyMMdd")
        
        # Создание вкладок
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка 1: График выездов
        self.tab_grafik = QWidget()
        self.tabs.addTab(self.tab_grafik, "График выездов")
        
        # Вкладка 2: Списки данных
        self.tab_lists = QWidget()
        self.tabs.addTab(self.tab_lists, "Редактирование справочников")
        
        self.init_grafik_tab()
        self.init_lists_tab()
        
        # Загружаем данные для текущей даты
        self.load_trips()
    
    def init_db(self):
        """Инициализация таблиц в БД, если их нет."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            date TEXT,        -- Формат ГГГГММДД (20240101)
            number INTEGER,   -- № (уникальный в рамках даты)
            star TEXT,       -- *
            topic TEXT,      -- ТЕМА
            kor TEXT,         -- КОР
            oper TEXT,        -- ОПЕР
            driver TEXT,     -- ВОДИТЕЛЬ
            address TEXT,    -- АДРЕС
            departure TEXT,   -- Выезд (время)
            start TEXT,       -- Начало (время)
            arrival TEXT,     -- Приезд (время)
            comment TEXT,     -- Коммент
            color TEXT,       -- Цвет ячейки
            PRIMARY KEY (date, number)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionaries (
            category TEXT,   -- Например, "ТЕМА", "КОР", "время"
            value TEXT,       -- Значение (например, "Ремонт", "Иванов")
            PRIMARY KEY (category, value)
        )
        """)
        
        # Заполняем справочники примерами (если они пустые)
        default_data = {
            "*": ["★", "☆"],
            "ТЕМА": ["Агротуризм", "Ремонт", "Обслуживание"],
            "КОР": ["Иванов", "Петров", "Сидоров"],
            "ОПЕР": ["Смирнов", "Кузнецов", "Попов"],
            "ВОДИТЕЛЬ": ["Алексей", "Дмитрий", "Михаил"],
            "АДРЕС": ["ул. Ленина, 1", "ул. Пушкина, 10", "пр. Мира, 25"],
            "время": ["08:00", "09:00", "10:00", "11:00", "12:00"]
        }
        
        for category, values in default_data.items():
            for value in values:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO dictionaries VALUES (?, ?)",
                    (category, value)
                )
        self.conn.commit()
    
    def init_grafik_tab(self):
        """Инициализация вкладки с графиком выездов."""
        layout = QVBoxLayout()
        
        # Верхняя панель с календарем и кнопками
        top_panel = QHBoxLayout()
        
        # Календарь для выбора даты
        self.calendar = QCalendarWidget()
        self.calendar.setFixedSize(330, 190)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        top_panel.addWidget(self.calendar)
        
        # Кнопки
        buttons_layout = QVBoxLayout()

        self.btn_add_row = QPushButton("Добавить строку")
        self.btn_add_row.setFixedSize(150, 30)
        self.btn_add_row.setStyleSheet("""
            font-size: 12px; 
            background-color: #4CAF50; 
            color: white;
            border-radius: 3px;
        """)
        self.btn_add_row.clicked.connect(self.add_new_row)
        buttons_layout.addWidget(self.btn_add_row)

        self.btn_delete_row = QPushButton("Удалить строку")
        self.btn_delete_row.setFixedSize(150, 30)
        self.btn_delete_row.setStyleSheet("""
            font-size: 12px; 
            background-color: #f44336; 
            color: white;
            border-radius: 3px;
        """)
        self.btn_delete_row.clicked.connect(self.delete_current_row)
        buttons_layout.addWidget(self.btn_delete_row)

        self.btn_send_all = QPushButton("Отправить график в чат")
        self.btn_send_all.setFixedSize(150, 30)
        self.btn_send_all.setStyleSheet("""
            font-size: 12px; 
            background-color: #2196F3; 
            color: white;
            border-radius: 3px;
        """)
        self.btn_send_all.clicked.connect(self.send_all_to_telegram)
        buttons_layout.addWidget(self.btn_send_all)

        self.btn_show_operators = QPushButton("Операторы")
        self.btn_show_operators.setFixedSize(150, 30)
        self.btn_show_operators.setStyleSheet("""
            font-size: 12px; 
            background-color: #FF9800; 
            color: white;
            border-radius: 3px;
        """)
        self.btn_show_operators.clicked.connect(self.show_operators_info)
        buttons_layout.addWidget(self.btn_show_operators)

        top_panel.addLayout(buttons_layout)

        # Информационное окно операторов
        self.operators_info = QTextEdit()
        self.operators_info.setReadOnly(True)
        self.operators_info.setFixedSize(300, 190)
        self.operators_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                font-size: 12px;
            }
        """)
        top_panel.addWidget(self.operators_info)

        top_panel.addStretch()
        layout.addLayout(top_panel)
        
        # Таблица выездов
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "№", "*", "ТЕМА", "КОР", "ОПЕР", "ВОДИТЕЛЬ", "АДРЕС", 
            "Выезд", "Начало", "Приезд", "Коммент", "Карточка", "Отправить"
        ])
        
        # Настройка размеров столбцов
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 35)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 200)
        self.table.setColumnWidth(7, 70)
        self.table.setColumnWidth(8, 70)
        self.table.setColumnWidth(9, 70)
        self.table.setColumnWidth(10, 200)
        self.table.setColumnWidth(11, 300)
        self.table.setColumnWidth(12, 100)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(11, QHeaderView.Stretch)
        
        # Настройка сортировки
        self.table.setSortingEnabled(True)
        
        # Контекстное меню
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Tooltip для отображения полного текста
        self.table.setMouseTracking(True)
        self.table.itemEntered.connect(self.show_tooltip)
        
        # Убрали чередование цветов строк
        self.table.setStyleSheet("""
            QTableView {
                background-color: white;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #d0d0d0;
            }
        """)
        
        self.table.cellChanged.connect(self.save_trip_data)
        layout.addWidget(self.table)
        
        self.tab_grafik.setLayout(layout)
    
    def init_lists_tab(self):
        """Инициализация вкладки для редактирования справочников."""
        layout = QVBoxLayout()
        
        # Группа "Редактирование справочников"
        group_box = QGroupBox("Редактирование справочников")
        form_layout = QFormLayout()
        
        # Выбор категории справочника
        self.combo_category = QComboBox()
        self.combo_category.addItems([
            "*", "ТЕМА", "КОР", "ОПЕР", "ВОДИТЕЛЬ", "АДРЕС", "время"
        ])
        self.combo_category.currentTextChanged.connect(self.load_dictionary)
        form_layout.addRow("Категория:", self.combo_category)
        
        # Поле для добавления нового значения
        self.edit_new_value = QLineEdit()
        self.edit_new_value.setPlaceholderText("Введите новое значение")
        form_layout.addRow("Новое значение:", self.edit_new_value)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.btn_add_value = QPushButton("Добавить")
        self.btn_add_value.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_add_value.clicked.connect(self.add_dictionary_value)
        buttons_layout.addWidget(self.btn_add_value)
        
        self.btn_delete_value = QPushButton("Удалить выбранное")
        self.btn_delete_value.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete_value.clicked.connect(self.delete_dictionary_value)
        buttons_layout.addWidget(self.btn_delete_value)
        
        form_layout.addRow(buttons_layout)
        
        # Таблица значений справочника
        self.table_dict = QTableWidget()
        self.table_dict.setColumnCount(1)
        self.table_dict.setHorizontalHeaderLabels(["Значения"])
        self.table_dict.cellChanged.connect(self.update_dictionary_value)
        
        form_layout.addRow(self.table_dict)
        
        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        
        self.tab_lists.setLayout(layout)
        self.load_dictionary()
    
    def show_operators_info(self):
        """Показывает информацию о свободном времени операторов."""
        self.calculate_operators_time()

    def calculate_operators_time(self):
        """Рассчитывает свободное время операторов."""
        try:
            # Получаем все поездки на выбранную дату
            self.cursor.execute(
                "SELECT oper, departure, arrival FROM trips "
                "WHERE date = ? ORDER BY departure",
                (self.current_date,)
            )
            trips = self.cursor.fetchall()
            
            # Собираем данные по операторам
            operators = {}
            for oper, departure, arrival in trips:
                if not oper:
                    continue
                    
                if oper not in operators:
                    operators[oper] = {
                        'count': 0,
                        'time_slots': []
                    }
                
                operators[oper]['count'] += 1
                if departure and arrival:
                    operators[oper]['time_slots'].append((departure, arrival))
            
            # Рассчитываем свободное время для каждого оператора
            result = []
            for oper, data in operators.items():
                time_slots = sorted(data['time_slots'], key=lambda x: x[0])
                free_time = []
                
                # Начало рабочего дня (может быть раньше 9:00)
                work_start = "09:00"
                if time_slots and time_slots[0][0] < work_start:
                    work_start = time_slots[0][0]
                
                # Конец рабочего дня (фиксированный)
                work_end = "17:30"
                
                # Предыдущее время окончания задачи
                prev_end = work_start
                
                for departure, arrival in time_slots:
                    # Добавляем свободное окно перед текущей задачей
                    if departure > prev_end:
                        free_time.append(f"{prev_end}-{departure}")
                    
                    # Обновляем предыдущее время окончания (добавляем 30 минут перерыва)
                    prev_end = self.add_minutes(arrival, 30)
                
                # Добавляем свободное время после последней задачи
                if prev_end < work_end:
                    free_time.append(f"{prev_end}-{work_end}")
                
                # Формируем строку результата
                free_slots = " ".join(free_time) if free_time else "нет свободного времени"
                result.append(f"{oper} - {data['count']} свободен {free_slots}")
            
            # Обновляем информационное окно
            if result:
                self.operators_info.setPlainText("\n".join(result))
            else:
                self.operators_info.setPlainText("Нет данных об операторах")
        
        except Exception as e:
            self.operators_info.setPlainText(f"Ошибка расчета: {str(e)}")

    def add_minutes(self, time_str, minutes):
        """Добавляет минуты к времени в формате HH:MM."""
        if not time_str:
            return "00:00"
        
        try:
            hours, mins = map(int, time_str.split(':'))
            total_mins = hours * 60 + mins + minutes
            new_hours = total_mins // 60
            new_mins = total_mins % 60
            return f"{new_hours:02d}:{new_mins:02d}"
        except:
            return time_str
    
    def send_all_to_telegram(self):
        """Отправляет все карточки выбранной даты в Telegram чат."""
        try:
            if self.table.rowCount() == 0:
                QMessageBox.warning(self, "Ошибка", "Нет данных для отправки!")
                return
            
            # Собираем все карточки
            cards = []
            for row in range(self.table.rowCount()):
                if self.table.item(row, 11):
                    card_text = self.table.item(row, 11).text()
                    cards.append(card_text)
            
            if not cards:
                QMessageBox.warning(self, "Ошибка", "Нет карточек для отправки!")
                return
            
            # Соединяем карточки с пустой строкой между ними
            final_message = "\n\n".join(cards)
            
            dialog = MessageDialog(final_message, self)
            dialog.setWindowTitle("Редактирование сообщения перед отправкой")
            if dialog.exec_() == QDialog.Accepted:
                message_to_send = dialog.get_message()
                
                if not message_to_send.strip():
                    QMessageBox.warning(self, "Ошибка", "Сообщение не может быть пустым!")
                    return
                
                url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
                params = {
                    "chat_id": self.DEFAULT_CHAT_ID,
                    "text": message_to_send,
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(url, params=params)
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "График отправлен в Telegram!")
                else:
                    QMessageBox.warning(self, "Ошибка", 
                        f"Не удалось отправить сообщение. Код ошибки: {response.status_code}")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при отправке: {str(e)}")
    
    def show_tooltip(self, item):
        """Показывает tooltip с полным текстом, если он не помещается в ячейке."""
        if item is None:
            return
            
        text = item.text()
        if text and len(text) > 20:
            QToolTip.showText(QCursor.pos(), text, self.table)
    
    def show_context_menu(self, pos):
        """Показывает контекстное меню для выбора значений из справочника."""
        try:
            item = self.table.itemAt(pos)
            row = self.table.rowAt(pos.y())
            col = self.table.columnAt(pos.x())
            
            if row == -1 or col == -1:
                return
                
            # Для столбца "Карточка" - особое меню
            if col == 11:
                self.show_card_context_menu(pos, row)
                return
                
            # Определяем категорию для выпадающего списка
            categories = {
                1: "*", 2: "ТЕМА", 3: "КОР", 4: "ОПЕР", 
                5: "ВОДИТЕЛЬ", 6: "АДРЕС", 7: "время", 8: "время", 9: "время"
            }
            category = categories.get(col)
            
            if category:
                menu = QMenu()
                
                # Добавляем значения из справочника
                values = self.get_dict_values(category)
                for value in values:
                    action = menu.addAction(value)
                    action.triggered.connect(
                        lambda checked, v=value, r=row, c=col: self.set_table_item_value(r, c, v)
                    )
                
                # Добавляем разделитель
                menu.addSeparator()
                
                # Добавляем меню выбора цвета
                color_menu = menu.addMenu("Цвет ячейки")
                
                colors = {
                    "Без цвета": None,
                    "Красный": QColor(255, 200, 200),
                    "Зеленый": QColor(200, 255, 200),
                    "Синий": QColor(200, 200, 255),
                    "Желтый": QColor(255, 255, 200)
                }
                
                for color_name, color in colors.items():
                    action = color_menu.addAction(color_name)
                    if color:
                        action.setIcon(self.create_color_icon(color))
                    action.triggered.connect(
                        lambda checked, c=color, r=row, column=col: self.set_cell_color(r, column, c)
                    )
                
                menu.exec_(self.table.viewport().mapToGlobal(pos))
        except Exception as e:
            print(f"Ошибка при показе контекстного меню: {str(e)}")
    
    def set_table_item_value(self, row, col, value):
        """Устанавливает значение в таблицу с проверкой на существование элемента"""
        if not self.table.item(row, col):
            self.table.setItem(row, col, QTableWidgetItem(value))
        else:
            self.table.item(row, col).setText(value)
    
    def show_card_context_menu(self, pos, row):
        """Показывает контекстное меню для столбца 'Карточка'."""
        try:
            menu = QMenu()
            
            # Получаем текст карточки
            card_item = self.table.item(row, 11)
            
            # Добавляем действие "Копировать"
            copy_action = menu.addAction("Копировать карточку")
            copy_action.triggered.connect(lambda: self.copy_card_to_clipboard(row))
            
            # Добавляем меню выбора цвета
            color_menu = menu.addMenu("Цвет ячейки")
            
            colors = {
                "Без цвета": None,
                "Красный": QColor(255, 200, 200),
                "Зеленый": QColor(200, 255, 200),
                "Синий": QColor(200, 200, 255),
                "Желтый": QColor(255, 255, 200)
            }
            
            for color_name, color in colors.items():
                action = color_menu.addAction(color_name)
                if color:
                    action.setIcon(self.create_color_icon(color))
                action.triggered.connect(
                    lambda checked, c=color, r=row, column=11: self.set_cell_color(r, column, c)
                )
            
            menu.exec_(self.table.viewport().mapToGlobal(pos))
        except Exception as e:
            print(f"Ошибка при показе контекстного меню карточки: {str(e)}")
    
    def copy_card_to_clipboard(self, row):
        """Копирует текст карточки в буфер обмена."""
        card_text = self.table.item(row, 11).text() if self.table.item(row, 11) else ""
        clipboard = QApplication.clipboard()
        clipboard.setText(card_text)
        QToolTip.showText(QCursor.pos(), "Карточка скопирована!", self.table)
    
    def create_color_icon(self, color):
        """Создает иконку с указанным цветом."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        return QIcon(pixmap)
    
    def set_cell_color(self, row, col, color):
        """Устанавливает цвет фона для указанной ячейки."""
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
        
        if color:
            item.setBackground(QBrush(color))
        else:
            item.setBackground(QBrush(QColor(255, 255, 255)))
        
        # Сохраняем цвет в БД
        if col != 11:
            column_name = self.table.horizontalHeaderItem(col).text()
            column_mapping = {
                "*": "star",
                "ТЕМА": "topic",
                "КОР": "kor",
                "ОПЕР": "oper",
                "ВОДИТЕЛЬ": "driver",
                "АДРЕС": "address",
                "Выезд": "departure",
                "Начало": "start",
                "Приезд": "arrival",
                "Коммент": "comment"
            }
            
            db_column = column_mapping.get(column_name)
            if db_column:
                number = self.table.item(row, 0).text()
                color_str = color.name() if color else ""
                
                self.cursor.execute(
                    f"UPDATE trips SET color = ? WHERE date = ? AND number = ?",
                    (color_str, self.current_date, number)
                )
                self.conn.commit()
    
    def on_date_selected(self, date):
        """Обработчик выбора даты в календаре."""
        self.current_date = date.toString("yyyyMMdd")
        self.load_trips()
    
    def load_trips(self):
        """Загружает поездки для выбранной даты."""
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        self.cursor.execute(
            "SELECT number, star, topic, kor, oper, driver, address, "
            "departure, start, arrival, comment, color FROM trips "
            "WHERE date = ? ORDER BY number",
            (self.current_date,)
        )
        
        trips = self.cursor.fetchall()
        
        for row_idx, trip in enumerate(trips):
            self.table.insertRow(row_idx)
            
            for col_idx, value in enumerate(trip[:11]):
                item = QTableWidgetItem(str(value) if value is not None else "")
                
                if col_idx == 0 or col_idx == 1:
                    item.setTextAlignment(Qt.AlignCenter)
                
                if col_idx in (7, 8, 9):
                    item.setTextAlignment(Qt.AlignCenter)
                
                self.table.setItem(row_idx, col_idx, item)
            
            # Устанавливаем цвет ячейки
            color_str = trip[11] if len(trip) > 11 else None
            if color_str:
                color = QColor(color_str)
                for col in range(self.table.columnCount() - 2):
                    if self.table.item(row_idx, col):
                        self.table.item(row_idx, col).setBackground(QBrush(color))
            
            # Кнопка "Отправить в чат"
            btn_send = QPushButton("Отправить")
            btn_send.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 3px;
                    padding: 3px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
            """)
            btn_send.clicked.connect(lambda checked, r=row_idx: self.send_to_telegram(r))
            self.table.setCellWidget(row_idx, 12, btn_send)
            
            # Обновляем карточку
            self.update_card(row_idx)
        
        if len(trips) == 0:
            self.add_new_row()
        
        self.table.blockSignals(False)
    
    def update_card(self, row):
        """Обновляет содержимое карточки для указанной строки."""
        required_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for col in required_columns:
            if not self.table.item(row, col):
                return
        
        number = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        star = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        topic = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        kor = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        oper = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        driver = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
        address = self.table.item(row, 6).text() if self.table.item(row, 6) else ""
        departure = self.table.item(row, 7).text() if self.table.item(row, 7) else ""
        start = self.table.item(row, 8).text() if self.table.item(row, 8) else ""
        arrival = self.table.item(row, 9).text() if self.table.item(row, 9) else ""
        comment = self.table.item(row, 10).text() if self.table.item(row, 10) else ""
        
        card_text = f"№{number} {star} {topic}\n"
        card_text += f"#{kor}  #{oper}\n"
        card_text += f"Водитель: #{driver}\n"
        card_text += f"Адрес: {address}\n"
        card_text += f"Выезд: {departure}  К: {start}\n"
        card_text += f"Приезд: {arrival}\n"
        card_text += f"Комментарий: {comment}"
        
        item = QTableWidgetItem(card_text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 11, item)
    
    def send_to_telegram(self, row):
        """Отправляет данные строки в Telegram чат."""
        try:
            if not self.table.item(row, 11):
                return
                
            card_text = self.table.item(row, 11).text()
            
            dialog = MessageDialog("", self)
            dialog.setWindowTitle("Дополнительный текст")
            if dialog.exec_() == QDialog.Accepted:
                additional_text = dialog.get_message()
                
                final_message = ""
                if additional_text.strip():
                    final_message = f"{additional_text}\n\n"
                final_message += card_text
                
                if not final_message.strip():
                    QMessageBox.warning(self, "Ошибка", "Сообщение не может быть пустым!")
                    return
                
                url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
                params = {
                    "chat_id": self.DEFAULT_CHAT_ID,
                    "text": final_message,
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(url, params=params)
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Сообщение отправлено в Telegram!")
                else:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось отправить сообщение. Код ошибки: {response.status_code}")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при отправке: {str(e)}")
    
    def save_trip_data(self, row, column):
        """Сохраняет изменения в ячейке таблицы в БД."""
        if column == 0:
            return
            
        number_item = self.table.item(row, 0)
        if not number_item:
            return
            
        number = number_item.text()
        column_name = self.table.horizontalHeaderItem(column).text()
        
        column_mapping = {
            "*": "star",
            "ТЕМА": "topic",
            "КОР": "kor",
            "ОПЕР": "oper",
            "ВОДИТЕЛЬ": "driver",
            "АДРЕС": "address",
            "Выезд": "departure",
            "Начало": "start",
            "Приезд": "arrival",
            "Коммент": "comment"
        }
        
        db_column = column_mapping.get(column_name)
        if not db_column:
            return
            
        value = self.table.item(row, column).text() if self.table.item(row, column) else ""
        
        self.cursor.execute(
            "SELECT 1 FROM trips WHERE date = ? AND number = ?",
            (self.current_date, number)
        )
        exists = self.cursor.fetchone()
        
        if exists:
            self.cursor.execute(
                f"UPDATE trips SET {db_column} = ? WHERE date = ? AND number = ?",
                (value, self.current_date, number))
        else:
            self.cursor.execute(
                f"INSERT INTO trips (date, number, {db_column}) VALUES (?, ?, ?)",
                (self.current_date, number, value))
        
        self.conn.commit()
        
        if column != 11:
            self.update_card(row)
    
    def load_dictionary(self):
        """Загружает значения выбранного справочника."""
        category = self.combo_category.currentText()
        values = self.get_dict_values(category)
        
        self.table_dict.blockSignals(True)
        self.table_dict.setRowCount(0)
        
        for row, value in enumerate(values):
            self.table_dict.insertRow(row)
            item = QTableWidgetItem(value)
            self.table_dict.setItem(row, 0, item)
        
        self.table_dict.blockSignals(False)
    
    def get_dict_values(self, category):
        """Возвращает список значений для указанной категории справочника."""
        self.cursor.execute(
            "SELECT value FROM dictionaries WHERE category = ?",
            (category,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_dictionary_value(self):
        """Добавляет новое значение в справочник."""
        category = self.combo_category.currentText()
        value = self.edit_new_value.text().strip()
        
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение!")
            return
            
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO dictionaries VALUES (?, ?)",
                (category, value))
            self.conn.commit()
            self.edit_new_value.clear()
            self.load_dictionary()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такое значение уже существует!")
    
    def update_dictionary_value(self, row, column):
        """Обновляет значение в справочнике."""
        if column != 0:
            return
            
        category = self.combo_category.currentText()
        values = self.get_dict_values(category)
        if row >= len(values):
            return
            
        old_value = values[row]
        new_value = self.table_dict.item(row, column).text()
        
        if not new_value:
            QMessageBox.warning(self, "Ошибка", "Значение не может быть пустым!")
            self.load_dictionary()
            return
            
        try:
            self.cursor.execute(
                "UPDATE dictionaries SET value = ? WHERE category = ? AND value = ?",
                (new_value, category, old_value))
            
            column_mapping = {
                "*": "star",
                "ТЕМА": "topic",
                "КОР": "kor",
                "ОПЕР": "oper",
                "ВОДИТЕЛЬ": "driver",
                "АДРЕС": "address",
                "время": None
            }
            
            db_column = column_mapping.get(category)
            
            if db_column:
                self.cursor.execute(
                    f"UPDATE trips SET {db_column} = ? WHERE {db_column} = ?",
                    (new_value, old_value))
            
            self.conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такое значение уже существует!")
            self.load_dictionary()
    
    def delete_dictionary_value(self):
        """Удаляет выбранное значение из справочника."""
        current_row = self.table_dict.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите значение для удаления!")
            return
            
        category = self.combo_category.currentText()
        value = self.table_dict.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Удалить значение '{value}' из справочника '{category}'?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.cursor.execute(
                "DELETE FROM dictionaries WHERE category = ? AND value = ?",
                (category, value))
            self.conn.commit()
            self.load_dictionary()
    
    def add_new_row(self):
        """Добавляет новую строку в таблицу."""
        self.table.blockSignals(True)
        
        self.cursor.execute(
            "SELECT MAX(number) FROM trips WHERE date = ?",
            (self.current_date,))
        max_number = self.cursor.fetchone()[0] or 0
        new_number = max_number + 1
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        item = QTableWidgetItem(str(new_number))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item)
        
        btn_send = QPushButton("Отправить")
        btn_send.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 3px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        btn_send.clicked.connect(lambda _, r=row: self.send_to_telegram(r))
        self.table.setCellWidget(row, 12, btn_send)
        
        self.cursor.execute(
            "INSERT INTO trips (date, number) VALUES (?, ?)",
            (self.current_date, new_number))
        self.conn.commit()
        
        self.table.blockSignals(False)
    
    def delete_current_row(self):
        """Удаляет текущую выбранную строку."""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления!")
            return
            
        number = self.table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Удалить строку №{number}?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.cursor.execute(
                "DELETE FROM trips WHERE date = ? AND number = ?",
                (self.current_date, number))
            self.conn.commit()
            self.table.removeRow(current_row)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrafikApp()
    window.show()
    sys.exit(app.exec_())