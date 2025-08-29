import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction,
                             QFileDialog, QMessageBox, QVBoxLayout,
                             QWidget, QLabel, QTableWidget, QTableWidgetItem,
                             QSplitter, QStatusBar)
from PyQt5.QtCore import Qt
import html
import re

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Предупреждение: BeautifulSoup4 не установлен. Установите: pip install beautifulsoup4")


class HTMLtoExcelConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_data = None

    def initUI(self):
        self.setWindowTitle('Конвертер HTML в Excel с сортировкой')
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Сплиттер для разделения интерфейса
        splitter = QSplitter(Qt.Vertical)

        # Верхняя часть - информация
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        self.info_label = QLabel('Выберите файл HTML для конвертации')
        top_layout.addWidget(self.info_label)

        # Нижняя часть - таблица для предпросмотра
        self.table_widget = QTableWidget()

        splitter.addWidget(top_widget)
        splitter.addWidget(self.table_widget)
        splitter.setSizes([100, 700])

        layout.addWidget(splitter)

        # Статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Меню
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')

        html_action = QAction('Собрать данные из HTML X-ways', self)
        html_action.triggered.connect(self.convert_html_to_excel)
        file_menu.addAction(html_action)

    def convert_html_to_excel(self):
        if not BS4_AVAILABLE:
            QMessageBox.critical(self, 'Ошибка',
                                 'BeautifulSoup4 не установлен.\n\n'
                                 'Установите: pip install beautifulsoup4')
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите HTML файл', '', 'HTML files (*.html *.htm);;All files (*.*)')

        if file_path:
            try:
                self.statusBar.showMessage('Чтение HTML файла...')
                df = self.read_html_to_dataframe(file_path)

                if df is not None:
                    self.current_data = df
                    self.show_data_in_table(df)
                    self.save_to_excel_with_sheets(df, file_path)

            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при конвертации: {str(e)}')
            finally:
                self.statusBar.clearMessage()

    def read_html_to_dataframe(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                html_content = file.read()

            if not BS4_AVAILABLE:
                # Альтернативный метод без BeautifulSoup
                return self.simple_html_parse(html_content)

            # Используем BeautifulSoup для парсинга
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')

            if not table:
                raise Exception('В HTML файле не найдена таблица')

            # Извлекаем заголовки
            headers = []
            header_row = table.find('tr')
            if header_row:
                for cell in header_row.find_all(['th', 'td']):
                    headers.append(self.decode_html_entities(cell.get_text().strip()))

            # Извлекаем данные
            data = []
            rows = table.find_all('tr')[1:]  # Пропускаем заголовок

            for row in rows:
                row_data = []
                for cell in row.find_all('td'):
                    row_data.append(self.decode_html_entities(cell.get_text().strip()))
                if row_data:  # Добавляем только непустые строки
                    data.append(row_data)

            # Создаем DataFrame
            df = pd.DataFrame(data, columns=headers)
            return df

        except Exception as e:
            raise Exception(f'Ошибка чтения HTML: {str(e)}')

    def simple_html_parse(self, html_content):
        """Простой парсер HTML таблиц без BeautifulSoup"""
        # Ищем таблицу
        table_match = re.search(r'<table.*?>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
        if not table_match:
            raise Exception('В HTML файле не найдена таблица')

        table_content = table_match.group(1)

        # Ищем строки
        rows = re.findall(r'<tr.*?>(.*?)</tr>', table_content, re.DOTALL | re.IGNORECASE)

        if not rows:
            raise Exception('В таблице не найдены строки')

        # Заголовки из первой строки
        headers = []
        header_cells = re.findall(r'<(th|td).*?>(.*?)</\1>', rows[0], re.DOTALL | re.IGNORECASE)
        for _, cell_content in header_cells:
            headers.append(self.decode_html_entities(self.clean_html(cell_content)))

        # Данные из остальных строк
        data = []
        for row in rows[1:]:
            row_data = []
            cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            for cell_content in cells:
                row_data.append(self.decode_html_entities(self.clean_html(cell_content)))
            if row_data:
                data.append(row_data)

        df = pd.DataFrame(data, columns=headers)
        return df

    def clean_html(self, text):
        """Очистка HTML тегов из текста"""
        return re.sub(r'<.*?>', '', text).strip()

    def decode_html_entities(self, text):
        if not text:
            return text
        return html.unescape(text)

    def show_data_in_table(self, df):
        """Показ данных в таблице для предпросмотра"""
        self.table_widget.clear()
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                self.table_widget.setItem(row, col, item)

        self.table_widget.resizeColumnsToContents()

    def save_to_excel_with_sheets(self, df, original_file_path):
        """Сохранение в Excel с созданием листов по столбцу 'Таблицы автоотчетов'"""

        # Проверяем наличие столбца для сортировки
        sort_column = 'Таблицы автоотчетов'
        if sort_column not in df.columns:
            QMessageBox.warning(self, 'Внимание',
                                f'Столбец "{sort_column}" не найден в данных. Будет создан один лист.')
            self.save_simple_excel(df, original_file_path)
            return

        # Получаем уникальные значения для создания листов
        unique_values = df[sort_column].dropna().unique()

        if len(unique_values) == 0:
            QMessageBox.warning(self, 'Внимание',
                                'Не найдено значений для сортировки. Будет создан один лист.')
            self.save_simple_excel(df, original_file_path)
            return

        # Диалог для выбора места сохранения
        save_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить Excel файл',
            os.path.splitext(original_file_path)[0] + '_sorted.xlsx',
            'Excel files (*.xlsx)')

        if not save_path:
            return

        try:
            # Создаем Excel файл только с листами для каждого уникального значения
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # Создаем листы для каждого уникального значения
                for value in unique_values:
                    if pd.notna(value):  # Пропускаем NaN значения
                        # Фильтруем данные
                        filtered_df = df[df[sort_column] == value].copy()
                        # Удаляем столбец сортировки
                        filtered_df.drop(columns=[sort_column], inplace=True)

                        # Создаем валидное имя листа
                        sheet_name = self.create_valid_sheet_name(str(value))
                        filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)

            QMessageBox.information(self, 'Успех',
                                    f'Файл успешно сохранен:\n{save_path}\n\n'
                                    f'Создано листов: {len(unique_values)}\n'
                                    f'Столбец "{sort_column}" удален из всех листов')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении Excel: {str(e)}')

    def create_valid_sheet_name(self, name):
        """Создает валидное имя для листа Excel"""
        # Убираем запрещенные символы
        invalid_chars = r'[\\/*?\[\]:]'
        valid_name = re.sub(invalid_chars, '_', name)

        # Ограничиваем длину (максимум 31 символ для Excel)
        if len(valid_name) > 31:
            valid_name = valid_name[:31]

        # Убеждаемся, что имя не пустое
        if not valid_name.strip():
            valid_name = 'Лист'

        return valid_name

    def save_simple_excel(self, df, original_file_path):
        """Простое сохранение без сортировки"""
        save_path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить Excel файл',
            os.path.splitext(original_file_path)[0] + '.xlsx',
            'Excel files (*.xlsx)')

        if not save_path:
            return

        try:
            df.to_excel(save_path, index=False)
            QMessageBox.information(self, 'Успех', f'Файл успешно сохранен:\n{save_path}')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении Excel: {str(e)}')


def main():
    app = QApplication(sys.argv)
    converter = HTMLtoExcelConverter()
    converter.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()