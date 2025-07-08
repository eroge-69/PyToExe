import sys
from ruamel.yaml import YAML
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                            QPushButton, QVBoxLayout, QWidget, QHBoxLayout, 
                            QFileDialog, QHeaderView, QLabel)
from PyQt5.QtCore import Qt

class HexEditTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, event):
        # Разрешаем только hex-символы: 0-9, A-F, a-f и управляющие клавиши
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, 
                          Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Tab):
            super().keyPressEvent(event)
            return
            
        if event.text().upper() not in '0123456789ABCDEF':
            event.ignore()
            return
            
        super().keyPressEvent(event)
        
        # Автоматически переводим в верхний регистр
        current_item = self.currentItem()
        if current_item:
            current_item.setText(current_item.text().upper())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register Editor for2.2.0")
        self.setMinimumSize(1200, 700)
        
        # Центральный виджет и основной лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель статуса
        self.status_label = QLabel("Файл не загружен")
        main_layout.addWidget(self.status_label)
        
        # Таблица для отображения регистров
        self.table = HexEditTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Регистр", "Имя", 
            "HEX", "INT32 (чтение)", 
            "Описание"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        main_layout.addWidget(self.table)
        
        # Панель кнопок
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Загрузить файл")
        self.load_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("Сохранить файл")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Инициализация переменных
        self.file_path = None
        self.yaml_data = None
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=4, sequence=4, offset=2)
        
        # Обработчик изменений в таблице
        self.table.cellChanged.connect(self.handle_cell_changed)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите YAML файл", 
            "", 
            "YAML Files (*.yaml *.yml)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.yaml_data = self.yaml.load(f)
                
            self.file_path = file_path
            self.status_label.setText(f"Загружен файл: {file_path}")
            self.save_button.setEnabled(True)
            self.populate_table()
            
        except Exception as e:
            self.status_label.setText(f"Ошибка загрузки: {str(e)}")

    def populate_table(self):
        if not self.yaml_data or 'registers' not in self.yaml_data:
            self.status_label.setText("Некорректный формат файла")
            return
            
        # Отключаем сигналы во время заполнения таблицы
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        # Поиск нужного блока регистров
        sense_block = None
        for reg_block in self.yaml_data['registers']:
            if reg_block.get('name') == 'TSens1wUid':  # Исправлено имя блока
                sense_block = reg_block
                break
                
        if not sense_block:
            self.status_label.setText("Блок TSens1wUid не найден")
            return
            
        # Заполнение таблицы
        fields = sense_block.get('fields', [])
        self.table.setRowCount(len(fields))
        
        for row, field in enumerate(fields):
            # Колонка 0: Номер регистра
            reg_item = QTableWidgetItem(str(field['reg']))
            reg_item.setFlags(reg_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, reg_item)
            
            # Колонка 1: Имя регистра
            name_item = QTableWidgetItem(field['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)
            
            # Колонка 2: HEX значение (редактируемое)
            hex_value = f"{field['value']:08X}"  # Форматирование в 8-значный HEX
            hex_item = QTableWidgetItem(hex_value)
            self.table.setItem(row, 2, hex_item)
                     
            # Колонка 3: DEC значение (только чтение)
            dec_item = QTableWidgetItem(str(field['value']))
            dec_item.setFlags(dec_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, dec_item)
            
            # Колонка 4: Описание
            info_item = QTableWidgetItem(field.get('info', ''))
            info_item.setFlags(info_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, info_item)
            
        # Включаем сигналы обратно
        self.table.blockSignals(False)

    def handle_cell_changed(self, row, column):
        """Обработчик изменений ячеек"""
        if column == 2:  # Изменения в HEX-колонке
            self.update_dec_from_hex(row)
            
    def update_dec_from_hex(self, row):
        """Обновление DEC значения на основе HEX"""
        hex_item = self.table.item(row, 2)
        if not hex_item:
            return
            
        hex_text = hex_item.text().strip()
        if not hex_text:
            return
            
        try:
            # Преобразуем HEX в DEC
            dec_value = int(hex_text, 16)
            
            # Обновляем DEC-колонку
            dec_item = self.table.item(row, 3)
            if dec_item:
                # Временно блокируем сигналы чтобы избежать рекурсии
                self.table.blockSignals(True)
                dec_item.setText(str(dec_value))
                self.table.blockSignals(False)
                
        except ValueError:
            # Оставляем старое значение при ошибке преобразования
            pass

    def save_file(self):
        if not self.file_path or not self.yaml_data:
            self.status_label.setText("Нет данных для сохранения")
            return
            
        # Обновляем данные в yaml_data из таблицы
        sense_block = None
        for reg_block in self.yaml_data['registers']:
            if reg_block.get('name') == 'TSens1wUid':  # Исправлено имя блока
                sense_block = reg_block
                break
                
        if not sense_block:
            self.status_label.setText("Блок TSens1wUid не найден в данных")
            return
            
        fields = sense_block.get('fields', [])
        
        # Временно блокируем сигналы
        self.table.blockSignals(True)
        
        for row in range(self.table.rowCount()):
            if row >= len(fields):
                break
                
            hex_item = self.table.item(row, 2)  # Берем данные из HEX-колонки
            if not hex_item:
                continue
                
            hex_text = hex_item.text().strip()
            if not hex_text:
                continue
                
            try:
                # Преобразуем HEX в целое число
                new_value = int(hex_text, 16)
                fields[row]['value'] = new_value
            except ValueError:
                # Пропускаем поле при ошибке преобразования
                continue
        
        # Включаем сигналы обратно
        self.table.blockSignals(False)
        
        # Сохраняем файл
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            self.file_path,
            "YAML Files (*.yaml *.yml)"
        )
        
        if not save_path:
            return
            
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(self.yaml_data, f)
            self.status_label.setText(f"Файл успешно сохранён: {save_path}")
        except Exception as e:
            self.status_label.setText(f"Ошибка сохранения: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
