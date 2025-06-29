import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem,
                             QTextEdit, QVBoxLayout, QWidget, QPushButton, QLineEdit, 
                             QInputDialog, QMessageBox, QFileDialog, QAction, QMenu, QLabel)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QKeySequence, QTextCursor
from docx import Document

class KnowledgeBaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("База знаний СТР")
        self.setGeometry(100, 100, 1200, 800)
        self.dark_mode = True
        self.current_item = None
        self.clipboard = ""
        
        # Инициализация UI
        self.init_ui()
        self.load_data()
        self.apply_dark_theme()
        
    def init_ui(self):
        # Главный сплиттер
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель (дерево)
        self.left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск...")
        self.search_box.textChanged.connect(self.search_content)
        left_layout.addWidget(self.search_box)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Структура")
        self.tree.itemClicked.connect(self.item_selected)
        left_layout.addWidget(self.tree)
        
        # Кнопки для разделов
        self.btn_add_section = QPushButton("Добавить раздел")
        self.btn_add_section.clicked.connect(self.add_section)
        left_layout.addWidget(self.btn_add_section)
        
        self.btn_add_subsection = QPushButton("Добавить подраздел")
        self.btn_add_subsection.clicked.connect(self.add_subsection)
        left_layout.addWidget(self.btn_add_subsection)
        
        self.btn_remove = QPushButton("Удалить")
        self.btn_remove.clicked.connect(self.remove_item)
        left_layout.addWidget(self.btn_remove)
        
        self.left_panel.setLayout(left_layout)
        
        # Правая панель (контент)
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        self.content_label = QLabel("Содержимое:")
        self.content_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(self.content_label)
        
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        right_layout.addWidget(self.content_display)
        
        self.btn_edit = QPushButton("Редактировать")
        self.btn_edit.clicked.connect(self.toggle_edit_mode)
        right_layout.addWidget(self.btn_edit)
        
        self.btn_import = QPushButton("Импорт из DOCX")
        self.btn_import.clicked.connect(self.import_docx)
        right_layout.addWidget(self.btn_import)
        
        self.right_panel.setLayout(right_layout)
        
        # Добавление панелей в сплиттер
        main_splitter.addWidget(self.left_panel)
        main_splitter.addWidget(self.right_panel)
        main_splitter.setSizes([300, 900])
        
        self.setCentralWidget(main_splitter)
        
        # Контекстное меню
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Горячие клавиши
        self.setup_shortcuts()
        
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QTreeWidget, QTextEdit, QLineEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #5A5A5A;
                color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6A6A6A;
            }
            QLabel {
                color: #AAAAFF;
            }
        """)
        
    def setup_shortcuts(self):
        # Копирование
        copy_action = QAction("Копировать", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_content)
        self.addAction(copy_action)
        
        # Вставка
        paste_action = QAction("Вставить", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_content)
        self.addAction(paste_action)
        
    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        
        context_menu = QMenu()
        
        copy_action = context_menu.addAction("Копировать")
        copy_action.triggered.connect(self.copy_content)
        
        paste_action = context_menu.addAction("Вставить")
        paste_action.triggered.connect(self.paste_content)
        
        context_menu.exec_(self.tree.mapToGlobal(pos))
        
    def copy_content(self):
        if self.content_display.hasFocus():
            self.clipboard = self.content_display.textCursor().selectedText()
        elif self.tree.hasFocus():
            item = self.tree.currentItem()
            if item and item.parent():
                self.clipboard = item.text(0) + "\n" + item.data(0, Qt.UserRole)
                
    def paste_content(self):
        if self.content_display.hasFocus() and self.content_display.isEnabled():
            cursor = self.content_display.textCursor()
            cursor.insertText(self.clipboard)
            
    def load_data(self):
        try:
            if os.path.exists("knowledge_base.json"):
                with open("knowledge_base.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.populate_tree(data)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
    
    def save_data(self):
        root = self.tree.invisibleRootItem()
        data = []
        
        for i in range(root.childCount()):
            section = root.child(i)
            section_data = {
                "title": section.text(0),
                "subsections": []
            }
            
            for j in range(section.childCount()):
                subsection = section.child(j)
                section_data["subsections"].append({
                    "title": subsection.text(0),
                    "content": subsection.data(0, Qt.UserRole)
                })
            
            data.append(section_data)
        
        try:
            with open("knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения данных: {str(e)}")
    
    def populate_tree(self, data):
        self.tree.clear()
        for section in data:
            section_item = QTreeWidgetItem([section["title"]])
            self.tree.addTopLevelItem(section_item)
            
            for subsection in section["subsections"]:
                subsection_item = QTreeWidgetItem([subsection["title"]])
                subsection_item.setData(0, Qt.UserRole, subsection["content"])
                section_item.addChild(subsection_item)
    
    def item_selected(self, item):
        self.current_item = item
        
        # Показываем контент только для подразделов
        if item.parent():
            self.content_display.setPlainText(item.data(0, Qt.UserRole))
            self.content_label.setText(f"Содержимое: {item.text(0)}")
        else:
            self.content_display.clear()
            self.content_label.setText("Содержимое: [выберите подраздел]")
        
        self.content_display.setReadOnly(True)
        self.btn_edit.setText("Редактировать")
    
    def add_section(self):
        title, ok = QInputDialog.getText(
            self, "Новый раздел", "Название раздела:"
        )
        if ok and title:
            section_item = QTreeWidgetItem([title])
            self.tree.addTopLevelItem(section_item)
            self.save_data()
    
    def add_subsection(self):
        if not self.current_item or not self.current_item.parent() is None:
            QMessageBox.warning(self, "Ошибка", "Выберите раздел для добавления подраздела")
            return
        
        title, ok = QInputDialog.getText(
            self, "Новый подраздел", "Название подраздела:"
        )
        if not ok or not title:
            return
        
        content, ok = QInputDialog.getMultiLineText(
            self, "Содержимое", "Введите содержимое:", ""
        )
        if ok:
            subsection_item = QTreeWidgetItem([title])
            subsection_item.setData(0, Qt.UserRole, content)
            self.current_item.addChild(subsection_item)
            self.save_data()
    
    def remove_item(self):
        if not self.current_item:
            return
            
        if self.current_item.parent() is None:
            msg = "Удалить раздел и все подразделы?"
        else:
            msg = "Удалить подраздел?"
            
        reply = QMessageBox.question(
            self, "Подтверждение", msg, 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            parent = self.current_item.parent()
            if parent:
                parent.removeChild(self.current_item)
            else:
                self.tree.invisibleRootItem().removeChild(self.current_item)
            self.current_item = None
            self.content_display.clear()
            self.save_data()
    
    def toggle_edit_mode(self):
        if not self.current_item or not self.current_item.parent():
            return
            
        if self.content_display.isReadOnly():
            self.content_display.setReadOnly(False)
            self.btn_edit.setText("Сохранить")
        else:
            self.current_item.setData(0, Qt.UserRole, self.content_display.toPlainText())
            self.content_display.setReadOnly(True)
            self.btn_edit.setText("Редактировать")
            self.save_data()
    
    def search_content(self):
        keyword = self.search_box.text().lower()
        if not keyword:
            self.reset_highlight()
            return
            
        # Сброс предыдущего выделения
        self.reset_highlight()
        
        # Поиск и подсветка
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            section = root.child(i)
            section_matched = False
            
            for j in range(section.childCount()):
                subsection = section.child(j)
                content = subsection.data(0, Qt.UserRole).lower()
                
                if keyword in content or keyword in subsection.text(0).lower():
                    # Подсветка элемента
                    subsection.setBackground(0, QColor(255, 255, 0))
                    section_matched = True
                    section.setExpanded(True)
            
            if section_matched:
                section.setBackground(0, QColor(255, 200, 100))
                section.setExpanded(True)
            else:
                section.setHidden(True)
    
    def reset_highlight(self):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            section = root.child(i)
            section.setBackground(0, QColor(0, 0, 0, 0))
            section.setHidden(False)
            
            for j in range(section.childCount()):
                subsection = section.child(j)
                subsection.setBackground(0, QColor(0, 0, 0, 0))
    
    def import_docx(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите DOCX файл", "", "Word Documents (*.docx)"
        )
        if not file_path:
            return
            
        try:
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
            
            if self.current_item and self.current_item.parent():
                # Добавляем в текущий подраздел
                self.content_display.setPlainText(
                    self.content_display.toPlainText() + "\n" + content
                )
                self.current_item.setData(0, Qt.UserRole, self.content_display.toPlainText())
            else:
                # Создаем новый подраздел
                title = os.path.basename(file_path).replace(".docx", "")
                if not self.current_item:
                    section_item = QTreeWidgetItem([title[:30] + "..."])
                    self.tree.addTopLevelItem(section_item)
                    self.current_item = section_item
                
                subsection_item = QTreeWidgetItem([title])
                subsection_item.setData(0, Qt.UserRole, content)
                self.current_item.addChild(subsection_item)
            
            self.save_data()
            QMessageBox.information(self, "Успех", "Документ успешно импортирован!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка импорта: {str(e)}")
    
    def closeEvent(self, event):
        self.save_data()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KnowledgeBaseApp()
    window.show()
    sys.exit(app.exec_())