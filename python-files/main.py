import sys
import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtCore import QDate, QDateTime
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Основной класс нашего приложения
class GanttApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Интерактивный построитель диаграмм Ганта')
        self.setGeometry(100, 100, 1400, 800) # x, y, ширина, высота окна

        # --- Создание интерфейса ---
        # Основной макет, разделенный на левую (ввод) и правую (график) части
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # --- Левая панель (ввод данных) ---
        input_form_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText('Название задачи')
        self.start_date_input = QLineEdit(QDate.currentDate().toString('yyyy-MM-dd'))
        self.end_date_input = QLineEdit(QDate.currentDate().addDays(7).toString('yyyy-MM-dd'))
        
        # Добавляем подсказки
        input_form_layout.addWidget(QLabel('Задача:'))
        input_form_layout.addWidget(self.task_input)
        input_form_layout.addWidget(QLabel('Начало (ГГГГ-ММ-ДД):'))
        input_form_layout.addWidget(self.start_date_input)
        input_form_layout.addWidget(QLabel('Конец (ГГГГ-ММ-ДД):'))
        input_form_layout.addWidget(self.end_date_input)

        add_button = QPushButton('Добавить задачу')
        add_button.clicked.connect(self.add_task)

        # Таблица для отображения введенных задач
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Задача', 'Начало', 'Окончание'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Кнопка для генерации диаграммы
        generate_button = QPushButton('Построить диаграмму')
        generate_button.clicked.connect(self.generate_chart)
        
        left_panel.addLayout(input_form_layout)
        left_panel.addWidget(add_button)
        left_panel.addWidget(self.table)
        left_panel.addWidget(generate_button)

        # --- Правая панель (отображение диаграммы) ---
        self.browser = QWebEngineView()
        self.browser.setHtml("<h2 style='font-family: sans-serif; text-align: center; color: #888;'>Здесь будет ваша диаграмма Ганта</h2>")
        right_panel.addWidget(self.browser)

        # Сборка главного окна
        main_layout.addLayout(left_panel, stretch=40) # Левая панель занимает 40% ширины
        main_layout.addLayout(right_panel, stretch=60) # Правая панель - 60%

    def add_task(self):
        """Добавляет введенные данные в таблицу"""
        task_name = self.task_input.text()
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()

        if not task_name or not start_date or not end_date:
            # Можно добавить всплывающее окно с ошибкой
            print("Ошибка: Заполните все поля!")
            return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(task_name))
        self.table.setItem(row_position, 1, QTableWidgetItem(start_date))
        self.table.setItem(row_position, 2, QTableWidgetItem(end_date))
        
        # Очистка полей ввода
        self.task_input.clear()
        self.start_date_input.setText(end_date) # Устанавливаем дату начала новой задачи равной дате конца предыдущей
        self.end_date_input.setText(QDateTime.fromString(end_date, 'yyyy-MM-dd').addDays(7).toString('yyyy-MM-dd'))


    def generate_chart(self):
        """Собирает данные из таблицы и строит диаграмму"""
        tasks_data = []
        for row in range(self.table.rowCount()):
            tasks_data.append({
                'Task': self.table.item(row, 0).text(),
                'Start': self.table.item(row, 1).text(),
                'Finish': self.table.item(row, 2).text(),
            })
        
        if not tasks_data:
            print("Нет данных для построения диаграммы")
            return

        df = pd.DataFrame(tasks_data)
        
        # Важно: преобразуем строки в даты
        df['Start'] = pd.to_datetime(df['Start'])
        df['Finish'] = pd.to_datetime(df['Finish'])

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", title="Интерактивная диаграмма Ганта")
        fig.update_yaxes(autorange="reversed") # Чтобы первая задача была наверху
        
        # Преобразуем график в HTML и загружаем его в наш веб-компонент
        # `include_plotlyjs='cdn'` позволяет не встраивать всю библиотеку Plotly.js в HTML, 
        # а подгружать ее из интернета, что делает HTML-код намного меньше.
        html_content = fig.to_html(include_plotlyjs='cdn')
        self.browser.setHtml(html_content)

# Точка входа в программу
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GanttApp()
    window.show()
    sys.exit(app.exec())