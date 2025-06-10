from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import fitz
import random
from docx2pdf import convert
import comtypes.client

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.dirname(os.path.dirname(os.__file__)) + '\\Lib\\site-packages\\PyQt5\\Qt5\\plugins'
prog_dir = os.path.dirname(os.path.abspath(__file__))
full_dir = os.path.abspath(os.path.normpath(os.path.join(prog_dir, "..")))



class log_in(QDialog):
    def __init__(self, main_window, action_in, action_redact_tema):
        super().__init__()

        self.main_window = main_window
        self.action_in = action_in
        self.action_redact_tema = action_redact_tema

        self.setWindowTitle("Вход")
        self.setFixedSize(200, 120)
        self.progicon = os.path.join(full_dir, 'data/icon/icon.png')
        self.setWindowIcon(QIcon(self.progicon))

        self.LE_login = QLineEdit(self)
        self.LE_login.setPlaceholderText("Введите логин")
        self.LE_password = QLineEdit(self)
        self.LE_password.setPlaceholderText("Введите пароль")
        self.LE_password.setEchoMode(QLineEdit.Password)
        self.pb_in = QPushButton(self)
        self.pb_in.setText("Вход")
        
        #Добавление виджетов авторизации
        self.LE_login.move(40, 10)
        self.LE_login.resize(120, 20)

        self.LE_password.move(40, 40)
        self.LE_password.resize(120, 20)

        self.pb_in.move(50, 70)
        self.pb_in.resize(100, 30)

        self.pb_in.clicked.connect(self.into_)

        
    def into_(self):
        username = self.LE_login.text()
        password = self.LE_password.text()
        file = os.path.join(full_dir, 'data/account/user.txt')

        try:
            with open(file, 'r', encoding = 'utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        user_in_file, pass_in_file = parts[0], parts[1]
                        if user_in_file == username and pass_in_file == password:
                            msg = QMessageBox()
                            msg.setWindowTitle("Успешно")
                            msg.setText("Вы авторизировались")
                            msg.setIcon(QMessageBox.Information)
                            msg.exec_()

                            self.action_in.setEnabled(False)
                            self.action_redact_tema.setVisible(True)
                            self.accept()

                            return True
                        
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Возможно отсутсвуют данные, либо неправильный логин и пароль")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return False
        except FileNotFoundError:
            print(f"Файл {file} не найден")
            return False

        

class redact_temwin(QDialog):
    def __init__(self, main_window, read_file_tree, tema_model):
        super().__init__()

        self.main_window = main_window
        self.read_file_tree = read_file_tree
        self.tema_model = tema_model

        self.setWindowTitle("Окно редактирование темы")
        self.setFixedSize(800, 320)
        self.progicon = os.path.join(full_dir, 'data/icon/icon.png')
        self.setWindowIcon(QIcon(self.progicon))

        #Строки кода на выполнение добавления темы
        self.LE_w_add = QLineEdit(self)
        self.LE_w_add.setPlaceholderText("Путь к файлу")
        self.LE_w_add.setReadOnly(True)
        self.pb_w_add = QPushButton(self)
        self.pb_w_add.setText("Обзор")

        self.LE_nameTem_add = QLineEdit(self)
        self.LE_nameTem_add.setPlaceholderText("Название темы")
        

        self.pb_input_add = QPushButton(self)
        self.pb_input_add.setText("Выполнить")

        self.lb_add = QLabel(self)
        self.lb_add.setText("Добавление")

        #Строки кода на выполнение удаление темы
        self.lb_delete = QLabel(self)
        self.lb_delete.setText("Удаление")

        self.lb_nameTema = QLabel(self)
        self.lb_nameTema.setText("Название темы")
        self.cb_temaName = QComboBox(self)

        self.pb_delete = QPushButton(self)
        self.pb_delete.setText("Удалить")

        #Строки кода на древо добавленных 
        # В методе init класса redact_temwin
        self.tree_add_tema = QTreeView(self)
        self.tree_add_tema.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Установка шрифта для содержимого
        font = QFont()
        font.setPointSize(16)
        self.tree_add_tema.setFont(font)


        self.model_tree_add = QStandardItemModel()
        self.model_tree_add.setHorizontalHeaderLabels(['Добавленные темы'])

        self.tree_add_tema.setModel(self.model_tree_add)

        self.tree_redact_tem()

        
        #Строки кода линий
        self.line1H = QFrame(self)
        self.line1H.setFrameShape(QFrame.HLine)
        self.line1H.setFrameShadow(QFrame.Sunken)

        self.line2H = QFrame(self)
        self.line2H.setFrameShape(QFrame.HLine)
        self.line2H.setFrameShadow(QFrame.Sunken)

        self.line3H = QFrame(self)
        self.line3H.setFrameShape(QFrame.HLine)
        self.line3H.setFrameShadow(QFrame.Sunken)

        self.line1V = QFrame(self)
        self.line1V.setFrameShape(QFrame.VLine)
        self.line1V.setFrameShadow(QFrame.Sunken)

        self.line2V = QFrame(self)
        self.line2V.setFrameShape(QFrame.VLine)
        self.line2V.setFrameShadow(QFrame.Sunken)
        
        
        #Строки кода на добавление виджетов в окно
        self.line1H.move(5, 5)
        self.line1H.resize(270, 5)

        self.line2H.move(5, 130)
        self.line2H.resize(270, 5)

        self.line3H.move(5, 290)
        self.line3H.resize(270, 5)

        self.line1V.move(5, 5)
        self.line1V.resize(5, 287)

        self.line2V.move(275, 5)
        self.line2V.resize(5, 287)

        
        #Виджеты для добавление темы
        
        
        self.lb_add.move(100, 10)
        self.lb_add.resize(200,20)

        self.LE_w_add.move(10, 40)
        self.LE_w_add.resize(200, 20)
        self.pb_w_add.move(220, 40)
        self.pb_w_add.resize(50, 20)

        self.LE_nameTem_add.move(10, 70)
        self.LE_nameTem_add.resize(200, 20)


        self.pb_input_add.move(90, 100)
        self.pb_input_add.resize(100, 20)
        
        #Виджеты на удаление темы

        self.lb_delete.move(105, 140)
        self.lb_delete.resize(100, 20)


        self.lb_nameTema.move(10, 160)
        self.lb_nameTema.resize(200, 20)
        self.cb_temaName.move(10, 180)
        self.cb_temaName.resize(200, 20)

        self.pb_delete.move(90, 210)
        self.pb_delete.resize(100,20)

        #Виджет отображение тем
        self.tree_add_tema.move(285, 10)
        self.tree_add_tema.resize(500, 280)

        self.populate_treeview()

        self.pb_w_add.clicked.connect(self.select_file)
        self.pb_input_add.clicked.connect(self.comp_add)
        self.pb_delete.clicked.connect(self.delete_selected_theme)

        self.fill_combobox_from_lib()

    def populate_treeview(self):
        # Очищаем текущую модель перед заполнением
        self.model_tree_add.clear()
        
        # Устанавливаем заголовки заново после очистки
        self.model_tree_add.setHorizontalHeaderLabels(['Добавленные темы'])
        
        root = self.model_tree_add.invisibleRootItem()

        # Получаем список имен из файла
        names = self.tree_redact_tem()

        for name in names:
            item = QStandardItem(name)
            root.appendRow(item)
    


    def tree_redact_tem(self):
        
        lib_dir = os.path.join(full_dir, "data/lib/lib.txt")
        
        names = []
        
        try:
            with open(lib_dir, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if parts:
                            names.append(parts[0])  # добавляем только название файла
                        
            return names
            
        except FileNotFoundError:
            print(f"Файл {lib_dir} не найден.")
            return []
        self.populate_treeview()
                    


    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите документ",
            "",
            "Word Documents (*.docx);;PDF Files (*.pdf);;Все файлы (*)",
            options=options
        )
        
        if not file_name:
            return
            
        try:
            # Получаем базовую директорию программы
            base_dir = os.path.join(full_dir, "data/lib")
            
            # Формируем путь в формате files\название_файла
            file_name_base = os.path.basename(file_name)
            new_path = os.path.join("files", file_name_base)
            
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext == ".pdf":
                self.LE_w_add.setText(new_path)
                only_name, _ = os.path.splitext(file_name_base)
                self.LE_nameTem_add.setText(only_name)
                
            elif file_ext == ".docx":
                reply = QMessageBox.information(
                    self,
                    "Оповещение",
                    "Данный файл будет конвертирован в PDF",
                    QMessageBox.Ok | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Ok:
                    pdf_name = os.path.splitext(file_name_base)[0] + ".pdf"
                    pdf_path = os.path.join(os.path.dirname(file_name), pdf_name)
                    success = self.convert_word_to_pdf(file_name, pdf_path)
                    if success:
                        self.LE_w_add.setText(os.path.join("files", pdf_name))
                        only_name, _ = os.path.splitext(pdf_name)
                        self.LE_nameTem_add.setText(only_name)
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Выберите файл с расширением .docx или .pdf"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Произошла ошибка: {str(e)}"
            )

    def convert_word_to_pdf(self, docx_path, pdf_path):
        try:
            if not os.path.exists(docx_path):
                raise FileNotFoundError(f"Файл {docx_path} не найден")

            # Для работы в .exe
            if getattr(sys, 'frozen', False):
                import tempfile
                temp_dir = tempfile.gettempdir()
                temp_pdf = os.path.join(temp_dir, os.path.basename(pdf_path))
                
                # Явное указание видимости COM-объекта
                import pythoncom
                pythoncom.CoInitialize()  # Инициализация COM для текущего потока
                
                try:
                    convert(docx_path, temp_pdf)
                finally:
                    pythoncom.CoUninitialize()  # Освобождение ресурсов
                
                if not os.path.exists(temp_pdf):
                    raise RuntimeError("Временный PDF не был создан")
                
                import shutil
                shutil.copy2(temp_pdf, pdf_path)
                
                try:
                    os.remove(temp_pdf)
                except:
                    pass
            else:
                convert(docx_path, pdf_path)
            
            if not os.path.exists(pdf_path):
                raise RuntimeError("PDF не был создан")
            
            return True
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка конвертации",
                f"Не удалось конвертировать файл:\n{str(e)}"
            )
            return False
            
    def comp_add(self):
        try:
            name = self.LE_nameTem_add.text()
            path = self.LE_w_add.text()
            file = os.path.join(full_dir, 'data/lib/lib.txt')

            if not name or not path:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Некорректные данные полей, выберите файл")
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

            found = False
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) >= 2:
                            name_tema, path_tema = parts[0], parts[1]
                            if name_tema == name and path_tema == path:
                                found = True
                                break
            except FileNotFoundError:
                self.tree_redact_tem()
                self.read_file_tree()
                self.fill_combobox_from_lib()

            if found:
                msg = QMessageBox()
                msg.setWindowTitle("Ошибка")
                msg.setText("Данный файл уже добавлен в список")
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                return

            with open(file, 'a', encoding='utf-8') as f:
                f.write(f"{name} {path}\n")

            self.populate_treeview()
            self.tema_model()
            self.fill_combobox_from_lib()
            

            success_msg = QMessageBox()
            success_msg.setWindowTitle("Успех")
            success_msg.setText("Данные успешно добавлены")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.exec_()
            

        except Exception as e:
            error_msg = QMessageBox()
            error_msg.setWindowTitle("Ошибка")
            error_msg.setText(f"Произошла ошибка: {str(e)}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec_()


    def fill_combobox_from_lib(self):
        lib_dir = os.path.join(full_dir, "data/lib/lib.txt")
        self.cb_temaName.clear()
        try:
            with open(lib_dir, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if parts:
                            theme_name = parts[0]
                            self.cb_temaName.addItem(theme_name)
        except FileNotFoundError:
            print(f"Файл {lib_dir} не найден.")
    def delete_selected_theme(self):
        selected_theme = self.cb_temaName.currentText()
        if not selected_theme:
            QMessageBox.warning(self, "Предупреждение", "Выберите тему для удаления.")
            return

        lib_dir = os.path.join(full_dir, "data/lib/lib.txt")
        try:
            with open(lib_dir, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            with open(lib_dir, 'w', encoding='utf-8') as f:
                for line in lines:
                    line_strip = line.strip()
                    if not line_strip:
                        continue
                    parts = line_strip.split()
                    if parts and parts[0] == selected_theme:
                        continue 
                    f.write(line)

            self.fill_combobox_from_lib()
            self.populate_treeview()
            self.tema_model()
            

            QMessageBox.information(self, "Успех", f"Тема '{selected_theme}' удалена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить тему: {str(e)}")
        
class open_testwin(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Тест")
        self.setFixedSize(400, 100)
        self.progicon = os.path.join(full_dir, 'data/icon/icon.png')
        self.setWindowIcon(QIcon(self.progicon))

        self.LE_FIO = QLineEdit(self)
        self.LE_FIO.setPlaceholderText("Введите фамилию")
        name_regexp = QRegExp("^[А-Яа-яЁёA-Za-z]+$")
        validator_name = QRegExpValidator(name_regexp)
        self.LE_FIO.setValidator(validator_name)

        self.LE_num = QLineEdit(self)
        self.LE_num.setPlaceholderText("Введите номер группы")
        self.LE_num.setValidator(QIntValidator(1, 999))

        self.pb_input = QPushButton("Пройти тест", self)

        self.LE_FIO.move(10, 10)
        self.LE_FIO.resize(200, 30)
        self.LE_num.move(10, 55)
        self.LE_num.resize(200, 30)
        self.pb_input.move(250, 35)
        self.pb_input.resize(100, 30)

        self.pb_input.clicked.connect(self.run_test)

    def run_test(self):
        fio = self.LE_FIO.text().strip()
        group_num = self.LE_num.text().strip()
        if not fio or not group_num:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста заполните все поля")
            return

        test_dialog = TestWindow(surname=fio, group=group_num)
        result = test_dialog.exec_()
        self.close()

class TestWindow(QDialog):
    def __init__(self, surname=None, group=None):
        super().__init__()
        self.surname = surname
        self.group = group
        
        self.setWindowTitle("Тест по GIMP")
        self.setFixedSize(600, 300)
        self.progicon = os.path.join(full_dir, 'data/icon/icon.png')
        self.setWindowIcon(QIcon(self.progicon))

        self.layout = QVBoxLayout()

        self.label_question = QLabel(self)
        self.label_question.setWordWrap(True)
        self.layout.addWidget(self.label_question)

        self.checkboxes = []

        self.btn_next = QPushButton("Далее", self)
        self.btn_next.setEnabled(False) 
        self.layout.addWidget(self.btn_next)

        self.setLayout(self.layout)

        global QUESTIONS
        QUESTIONS = [
            {
                "question": "Что такое GIMP?",
                "answers": ["Бесплатный графический редактор", "Программа для 3D-моделирования", "Аналог Adobe Illustrator"],
                "correct": ["Бесплатный графический редактор"]
            },
            {
                "question": "Как открыть изображение в GIMP?",
                "answers": ["Через меню 'Файл → Открыть'", "Двойным щелчком по рабочей области", "Автоматически при запуске программы"],
                "correct": ["Через меню 'Файл → Открыть'"]
            },
            {
                "question": "Как добавить новый слой?",
                "answers": ["Комбинацией Shift+Ctrl+N", "Через контекстное меню правой кнопки", "Автоматически при вставке изображения"],
                "correct": ["Комбинацией Shift+Ctrl+N"]
            },
            {
                "question": "Как изменить размер изображения?",
                "answers": ["Через 'Изображение → Размер изображения'", "Растягиванием углов мышью", "Только при экспорте"],
                "correct": ["Через 'Изображение → Размер изображения'"]
            },
            {
                "question": "Как вырезать объект из фона?",
                "answers": ["Инструментами выделения (Лассо, Волшебная палочка)", "Заливкой фона белым цветом", "Фильтром 'Размытие'"],
                "correct": ["Инструментами выделения (Лассо, Волшебная палочка)"]
            },
            {
                "question": "Как сохранить изображение в PNG или JPG?",
                "answers": ["Через 'Файл → Экспортировать как'", "Автоматически в формате PSD", "Только через буфер обмена"],
                "correct": ["Через 'Файл → Экспортировать как'"]
            },
            {
                "question": "Как сделать прозрачный фон?",
                "answers": ["Удалить фон и сохранить в PNG", "Использовать фильтр 'Прозрачность'", "Залить слой белым цветом"],
                "correct": ["Удалить фон и сохранить в PNG"]
            },
            {
                "question": "Как размыть часть изображения?",
                "answers": ["Инструментом 'Размытие'", "Уменьшением резкости всего изображения", "Добавлением шума"],
                "correct": ["Инструментом 'Размытие'"]
            },
            {
                "question": "Как добавить текст в GIMP?",
                "answers": ["Инструментом 'Текст' (кнопка 'А')", "Вставкой из буфера обмена", "Через фильтр 'Текстовые эффекты'"],
                "correct": ["Инструментом 'Текст' (кнопка 'А')"]
            },
            {
                "question": "Как убрать красные глаза на фото?",
                "answers": ["Фильтром 'Удаление эффекта красных глаз'", "Заливкой глаз чёрным цветом", "Размытием области глаз"],
                "correct": ["Фильтром 'Удаление эффекта красных глаз'"]
            },
            {
                "question": "Как установить новые кисти или плагины в GIMP?",
                "answers": ["Скопировать файлы в папки 'Brushes' или 'Plug-ins'", "Через встроенный магазин дополнений", "Автоматически при обновлении программы"],
                "correct": ["Скопировать файлы в папки 'Brushes' или 'Plug-ins'"]
            },
            {
                "question": "Как изменить цвет объекта в GIMP?",
                "answers": ["Через 'Цвета → Цветовой тон/Насыщенность'", "Перекрашиванием кистью", "Изменением режима слоя на 'Перекрытие'"],
                "correct": ["Через 'Цвета → Цветовой тон/Насыщенность'"]
            },
            {
                "question": "Как сделать зеркальное отражение изображения?",
                "answers": ["Инструментом 'Отразить' (Shift+F)", "Вручную перерисовать изображение", "Фильтром 'Искажение'"],
                "correct": ["Инструментом 'Отразить' (Shift+F)"]
            },
            {
                "question": "Как выровнять горизонт на фото?",
                "answers": ["Инструментом 'Поворот' с последующим кадрированием", "Обрезкой по вертикали", "Автоматической коррекцией в 'Цветах'"],
                "correct": ["Инструментом 'Поворот' с последующим кадрированием"]
            },
            {
                "question": "Как создать анимацию в GIMP?",
                "answers": ["Экспортировать слои в GIF с задержками", "Использовать видео-редактор", "Сохранить каждый кадр отдельно"],
                "correct": ["Экспортировать слои в GIF с задержками"]
            },
            {
                "question": "Как убрать шум с фотографии?",
                "answers": ["Фильтром 'Уменьшить шум'", "Увеличением резкости", "Заменить фон полностью"],
                "correct": ["Фильтром 'Уменьшить шум'"]
            },
            {
                "question": "Как нарисовать плавную линию (кривую Безье)?",
                "answers": ["Инструментом 'Контуры' (Shift+B)", "От руки с помощью кисти", "Фильтром 'Сглаживание'"],
                "correct": ["Инструментом 'Контуры' (Shift+B)"]
            },
            {
                "question": "Как добавить тень к тексту или объекту?",
                "answers": ["Дублировать слой, размыть и сдвинуть", "Использовать градиент", "Наложить текстуру"],
                "correct": ["Дублировать слой, размыть и сдвинуть"]
            },
            {
                "question": "Как работать с масками слоя?",
                "answers": ["Добавить маску и рисовать чёрным/белым", "Использовать только прозрачность слоя", "Применять фильтры напрямую"],
                "correct": ["Добавить маску и рисовать чёрным/белым"]
            },
            {
                "question": "Как исправить пересвеченные участки на фото?",
                "answers": ["Слоем в режиме 'Перекрытие' и серой кистью", "Увеличением контраста", "Полной заменой цвета"],
                "correct": ["Слоем в режиме 'Перекрытие' и серой кистью"]
            }
        ]

        self.current_index = 0
        self.correct_answers_count = 0


        self.show_question()

        self.btn_next.clicked.connect(self.next_question)

        self.test_finished = False

    def show_question(self):
        # Очищаем предыдущие чекбоксы
        for cb in self.checkboxes:
            self.layout.removeWidget(cb)
            cb.deleteLater()
        self.checkboxes.clear()

        # Инициализируем список выбранных вопросов при первом вызове
        if not hasattr(self, 'selected_questions'):
            self.selected_questions = random.sample(QUESTIONS, min(10, len(QUESTIONS)))
            self.current_question_index = 0
            self.user_answers = []  # Для хранения ответов пользователя

        # Проверяем, остались ли вопросы
        if self.current_question_index < len(self.selected_questions):
            current_q = self.selected_questions[self.current_question_index]
            
            # Отображаем текст вопроса
            self.label_question.setText(
                f"Вопрос {self.current_question_index + 1}/{len(self.selected_questions)}: {current_q['question']}"
            )

            # Добавляем варианты ответов
            for answer in current_q['answers']:
                cb = QCheckBox(answer)
                cb.stateChanged.connect(self.update_button_state)
                self.layout.insertWidget(self.layout.count() - 1, cb)
                self.checkboxes.append(cb)

            # Настраиваем кнопку
            self.btn_next.setText("Завершить" if self.current_question_index == len(self.selected_questions) - 1 else "Далее")
            self.btn_next.setEnabled(False)

        else:
            # Все вопросы пройдены - показываем результаты
            self.show_results()

    def update_button_state(self):
        # Активируем кнопку, если выбран хотя бы один вариант
        self.btn_next.setEnabled(any(cb.isChecked() for cb in self.checkboxes))

    def next_question(self):
        # Сохраняем ответы пользователя
        selected_answers = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        self.user_answers.append({
            'question': self.selected_questions[self.current_question_index]['question'],
            'user_answers': selected_answers,
            'correct_answers': self.selected_questions[self.current_question_index]['correct']
        })
        
        # Переходим к следующему вопросу
        self.current_question_index += 1
        self.show_question()

    def show_results(self):
        # Вычисляем результат
        correct_count = sum(
            1 for i, q in enumerate(self.user_answers)
            if set(q['user_answers']) == set(q['correct_answers'])
        )
        
        # Рассчитываем процент правильных ответов
        percentage = correct_count / len(self.selected_questions) * 100
        
        # Определяем оценку
        if percentage >= 90:
            grade = "5"
        elif percentage >= 75:
            grade = "4"
        elif percentage >= 60:
            grade = "3"
        else:
            grade = "2"
        
        # Показываем результаты
        result_text = (f"Тест завершен!\n"
                      f"Правильных ответов: {correct_count}/{len(self.selected_questions)}\n"
                      f"Оценка:{grade}\n"
                       "Все результаты можно посмотреть в файле results.txt")
        
        QMessageBox.information(self, "Результаты теста", result_text)
        
        # Запись результатов в файл
        with open(os.path.join(full_dir, 'results.txt'), "a", encoding="utf-8") as file:
            file.write(
                f"Тест прошёл курсант {self.group} {self.surname} на оценку: {grade}\n"
            )
        
        self.close()

class UI_MainWindow(QMainWindow ,object):
    def setupUi(self, MainWindow):
        global action_In
        self.current_scale = 1.0 

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1200,1050)
        self.progicon = os.path.join(full_dir, 'data/icon/icon.png')
        MainWindow.setWindowIcon(QIcon(self.progicon))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        #Изображение фото
        self.photoGIMP = QLabel(self.centralwidget)
        self.menuIcon = os.path.join(full_dir, "data/icon/photo1.png")
        self.pixmap = QPixmap(self.menuIcon)
        self.photoGIMP.setPixmap(self.pixmap)
        self.photoGIMP.move(600, 200)

        #Виджет для отображения документов
        self.container_widget = QWidget()
        self.layout = QVBoxLayout(self.container_widget)
        self.scroll_area = QScrollArea(MainWindow)
        self.scroll_area.setGeometry(QRect(450, 40, 740, 950))
        self.scroll_area.setVisible(False)
        self.scroll_area.setWidget(self.container_widget)
        self.container_widget.setMinimumSize(700, 900)

        #Кнопки масштаба
        self.font_pb = QFont()
        self.font_pb.setBold(True)
        self.font_pb.setPointSize(10)
        
        self.pb_plus = QPushButton(self.centralwidget)
        self.pb_plus.setObjectName("pb_plus")
        self.pb_plus.setGeometry(QRect(1100, 965, 80, 30))
        self.pb_plus.setFont(self.font_pb)
        self.pb_plus.setVisible(False)

        self.pb_minus = QPushButton(self.centralwidget)
        self.pb_minus.setObjectName("pb_minus")
        self.pb_minus.setGeometry(QRect(1000, 965, 80, 30))
        self.pb_minus.setFont(self.font_pb)
        self.pb_minus.setVisible(False)

        
        
        #МенюБар
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")

        #Вкладка Меню
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)

        self.actionOpenTest = QAction(MainWindow)
        self.actionOpenTest.setObjectName("OpenTest")

        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("ExitAction")

        self.action_In = QAction(MainWindow)
        self.action_In.setObjectName("PrepodRedact")

        self.Action_redact_tema = QAction(MainWindow)
        self.Action_redact_tema.setObjectName("Redact_tema")


        
        #Вкладка Справка
        self.spravka = QMenu(self.menubar)
        self.spravka.setObjectName("spravka")
        MainWindow.setMenuBar(self.menubar)

        self.actionAboutProg = QAction(MainWindow)
        self.actionAboutProg.setObjectName("ActionAboutProg")

        self.actionAboutAuthor = QAction(MainWindow)
        self.actionAboutAuthor.setObjectName("ActionAboutAuthor")

        self.actionInst = QAction(MainWindow)
        self.actionInst.setObjectName("ActionInst")

        #Окно файлов тем
        # В методе setupUI класса UI_MainWindow
        self.tree_tema = QTreeView(MainWindow)
        self.tree_tema.setGeometry(QRect(20, 40, 400, 950))
        self.tree_tema.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Установка шрифта для содержимого
        font = QFont()
        font.setPointSize(16)
        self.tree_tema.setFont(font)

        self.model_tree = QStandardItemModel()
        self.model_tree.setHorizontalHeaderLabels(['Темы'])
        self.model_tree.setItemPrototype(None)

        self.tree_tema.setModel(self.model_tree)

        self.tema_model()        
        
        #Action в Меню
        self.menu.addAction(self.action_In)
        self.menu.addSeparator()
        self.menu.addAction(self.Action_redact_tema)
        self.menu.addSeparator()
        self.menu.addAction(self.actionOpenTest)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExit)
        self.menubar.addAction(self.menu.menuAction())

        
        #Action в Справке
        self.spravka.addAction(self.actionAboutProg)
        self.spravka.addAction(self.actionAboutAuthor)
        self.spravka.addAction(self.actionInst)
        self.menubar.addAction(self.spravka.menuAction())
        

        self.statusbar = QStatusBar(self.centralwidget)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        #Подключение def к кнопкам
        self.actionAboutProg.triggered.connect(self.about_prog)
        self.actionAboutAuthor.triggered.connect(self.about_auth)
        self.actionInst.triggered.connect(self.inst)
        self.Action_redact_tema.triggered.connect(self.redact_tem)
        self.action_In.triggered.connect(self.login_)
        self.actionOpenTest.triggered.connect(self.open_test)
        self.actionExit.triggered.connect(self.exit_)
        self.tree_tema.doubleClicked.connect(self.check_clicked_treeview)
        self.pb_plus.clicked.connect(self.zoom_in)
        self.pb_minus.clicked.connect(self.zoom_out)

        #спрятанный виджет
        self.Action_redact_tema.setVisible(False)
        
        

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Электронное учебное пособие: Компьютерная графика"))
        self.menu.setTitle(_translate("MainWindow", "Меню"))
        self.action_In.setText(_translate("MainWindow", "Войти"))
        self.Action_redact_tema.setText(_translate("MainWindow", "Редактирование темы"))
        self.actionOpenTest.setText(_translate("MainWIndow", "Открыть тест"))
        self.actionExit.setText(_translate("MainWindow", "Выход"))
        self.spravka.setTitle(_translate("MainWindow", "Справка"))
        self.actionAboutProg.setText(_translate("MainWindow", "О программе"))
        self.actionAboutAuthor.setText(_translate("MainWindow", "Об авторе"))
        self.actionInst.setText(_translate("MainWindow", "Инструкция"))
        self.pb_plus.setText(_translate("MainWindow", "Увеличить"))
        self.pb_minus.setText(_translate("MainWindow", "Уменьшить"))

    def check_clicked_treeview(self, index):
        # Сбрасываем масштаб при выборе нового документа
        self.current_scale = 1.0
        # Остальной код метода остается без изменений
        index = self.tree_tema.currentIndex()
        
        if not index.isValid():
            return

        item_name = self.model_tree.data(index, Qt.DisplayRole)

        lib_path = os.path.join(full_dir, "data/lib/lib.txt")
        file_path = None
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_strip = line.strip()
                    if not line_strip:
                        continue
                    parts = line_strip.split()
                    if parts and parts[0] == item_name:
                        if len(parts) >= 2:
                            file_path = parts[1]
                            break
            if file_path:
                self.perform_action_with_file(file_path)
            else:
                print("Путь к файлу не найден для выбранного предмета.")
        except Exception as e:
            error_msg = QMessageBox()
            error_msg.setWindowTitle("Ошибка")
            error_msg.setText(f"Ошибки чтения файла: {str(e)}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec_()

    def perform_action_with_file(self, path):
        pdf_path = os.path.join(full_dir, path)

        # Удаляем старые виджеты
        for i in reversed(range(self.layout.count())):
            widget_to_remove = self.layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

        # Открываем PDF и отображаем страницы
        doc = fitz.open(pdf_path)
        total_height = 0  # Для подсчета общего размера по высоте

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Используем текущий масштаб
            pix = page.get_pixmap(matrix=fitz.Matrix(self.current_scale, self.current_scale))
            img_data = pix.tobytes("png")

            qimage = QImage()
            qimage.loadFromData(img_data)

            qpixmap = QPixmap.fromImage(qimage)

            label = QLabel()
            label.setPixmap(qpixmap)
            label.setAlignment(Qt.AlignCenter)

            self.layout.addWidget(label)

            # Обновляем высоту для контейнера
            total_height += qpixmap.height()

        # Обновляем размер контейнера под содержимое (преобразуем в int)
        self.container_widget.setMinimumSize(int(700 * self.current_scale), int(total_height))
        self.scroll_area.setVisible(True)
        self.pb_plus.setVisible(True)
        self.pb_minus.setVisible(True)
                
                
                
        
        

    def zoom_in(self):
        """Увеличить масштаб (на 20%)"""
        self.current_scale *= 1.2
        self.reload_pdf_with_new_scale()  # Перезагружаем PDF с новым масштабом

    def zoom_out(self):
        """Уменьшить масштаб (на 20%, но не меньше 50%)"""
        self.current_scale = max(0.5, self.current_scale / 1.2)  # Минимальный масштаб = 0.5
        self.reload_pdf_with_new_scale()  # Перезагружаем PDF с новым масштабом

    def reload_pdf_with_new_scale(self):
        """Перезагружает текущий PDF с новым масштабом"""
        current_index = self.tree_tema.currentIndex()
        if current_index.isValid():
            item_name = self.model_tree.data(current_index, Qt.DisplayRole)
            lib_path = os.path.join(full_dir, "data/lib/lib.txt")
            try:
                with open(lib_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and line.split()[0] == item_name:
                            file_path = line.split()[1]
                            self.perform_action_with_file(file_path)  # Перерисовываем
                            break
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить масштаб: {e}")
    def tema_model(self):
        self.model_tree.clear()
        self.model_tree.setHorizontalHeaderLabels(['Темы'])
        
        root = self.model_tree.invisibleRootItem()
        names = self.read_file_tree()

        for name in names:
            item = QStandardItem(name)
            root.appendRow(item)

    def read_file_tree(self):
        lib_dir = os.path.join(full_dir, "data/lib/lib.txt")
        
        names = []
        
        try:
            with open(lib_dir, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if parts:
                            names.append(parts[0])
                        
            return names
            
        
            
        except FileNotFoundError:
            print(f"Файл {lib_dir} не найден.")
            return []
        

#Окна гл.меню
    def login_(self):
        self.login_window = log_in(self,self.action_In, self.Action_redact_tema)
        self.login_window.exec_()

    def redact_tem(self):
        self.redact_tem_win = redact_temwin(self, self.read_file_tree, self.tema_model)
        self.redact_tem_win.exec_()

    def open_test(self):
        self.open_test_win = open_testwin()
        self.open_test_win.exec_()



    def exit_(self, event):
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы действительно хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QApplication.instance().closeAllWindows()
            QApplication.instance().quit()
            sys.exit()
        
#Окна справки
    def about_prog(self):
        msg = QMessageBox()
        msg.setWindowTitle("О Программе")
        msg.setText('Программа "Электронное учебное пособие: Компьютерная Графика", помогает пользователям в \n'
                    "изучение различных тем по эксплуатации программы GIMP.\n"
                    "В данную программу вложены различные темы для изучения, такие как,\n"
                    'Создание водяного знака, работа со штампом и т.д;.')
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def about_auth(self):
        msg = QMessageBox()
        msg.setWindowTitle("Об Авторе")
        msg.setText('Дипломная работа "Электронное учебное пособие: Компьютерная графика"\n'
                    'Разработана курсантом Троицкого Авиационного Технического Колледжа филиал МГТУ ГА\n'
                    '431 группа Морозов Тимофей Алексеевич\n'
                    'Адрес: Троицк, Челябинская область, Ул.Гагарина, 1\n'
                    'Связь с разработчиком: timmorozov1995@gmail.com')
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def inst(self):
        msg = QMessageBox()
        msg.setWindowTitle("Инструкция")
        msg.setText("Влевом вверхном углу находится Меню приложения,\n"
                    "в ней находятся 3 функциональные кнопки.\n"
                    "Первая из них отвечает за авторизацию преподавателя для добавления новых тем,\n"
                    'после авторизации в контекстном меню появляется кнопка "Редактирование тем"\n'
                    'При нажатие на которую пользователя переносет на окно, где добавляются темы\n'
                    'и при соблюдения инструкий: 1. Выбрать файл с помощью кнопки "Обзор". 2. Ожидания процесса. 3. После нажать кнопку "Выполнить", когда пользователь удостовериться в правильном пути и название'
                    '\nТо затем в окне "Добавленные темы" пользователь увидет тот самый файл, ПРИМЕЧАНИЕ: Для корректной работы приложения нужно вводить файлы, у которых названия слитное или пробелы заменены на "_"'
                    '\nТакже существует действие удалить, нужно всего-лишь выбрать файл и нажать кнопку "Удалить".'
                    '\nДля учащихся доступны только 3 действия, двойным нажатием на названия темы - открывается сама тема, а при нажатие кнопки "Открыть тест" в контекстном меню'
                    )
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UI_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
