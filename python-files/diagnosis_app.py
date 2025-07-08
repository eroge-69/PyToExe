
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QComboBox, QPushButton, QDateTimeEdit, QMessageBox, QHBoxLayout, QTextEdit
)
from PyQt6.QtCore import QDateTime

class DiagnosisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ранняя диагностика ОКН")
        self.resize(700, 700)
        self.total_score = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Раздел 1
        layout.addWidget(QLabel("Ф.И.О. больного"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("№ И/Б больного"))
        self.id_input = QLineEdit()
        layout.addWidget(self.id_input)

        layout.addWidget(QLabel("Дата обследования"))
        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_input.setDisplayFormat("dd.MM.yyyy г., HH:mm")
        self.datetime_input.setCalendarPopup(True)
        layout.addWidget(self.datetime_input)

        # Объективные данные (пример одного поля)
        layout.addWidget(QLabel("Период до поступления (час)"))
        self.period_input = QComboBox()
        self.period_options = {
            "0-6 часов": 4, "6-12 часов": 5, "12-24 часов": 7,
            "24-48 часов": 9, "48 ≤ часов": 11
        }
        self.period_input.addItems(self.period_options.keys())
        layout.addWidget(self.period_input)

        # Добавьте аналогично другие поля...
        self.sections = []

        self.sections.append(self.add_criterion_block(
            layout, "Общее состояние", {
                "удовлетворительное": 1,
                "средней тяжести": 3,
                "тяжелое": 5,
                "крайне тяжелое": 7
            }))

        self.sections.append(self.add_criterion_block(
            layout, "Характер боли", {
                "схваткообразные": 9,
                "приступообразные": 5,
                "тупые боли (не сильные)": 3,
                "безболезненные": 2
            }))

        self.sections.append(self.add_criterion_block(
            layout, "Задержка стула и газов", {
                "в норме (была вчера/сегодня)": 2,
                "небольшой жидкий стул": 4,
                "частичная (до 1,5 суток)": 5,
                "отсутствует более 2-х дней": 7
            }))

        self.sections.append(self.add_criterion_block(
            layout, "Характер рвотных масс", {
                "желчная (желудочная)": 4,
                "в виде кофейной гущи": 6,
                "каловая рвота (с запахом)": 9,
                "рвоты не отмечалось": 2
            }))

        # Кнопка расчета
        self.result_btn = QPushButton("Рассчитать результат")
        self.result_btn.clicked.connect(self.calculate_result)
        layout.addWidget(self.result_btn)

        # Вывод результата
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.setLayout(layout)

    def add_criterion_block(self, layout, title, options):
        layout.addWidget(QLabel(title))
        combo = QComboBox()
        combo.addItems(options.keys())
        layout.addWidget(combo)
        return (combo, options)

    def calculate_result(self):
        score = self.period_options[self.period_input.currentText()]
        for combo, options in self.sections:
            score += options[combo.currentText()]

        result_text = f"Общий балл: {score}\n"

        if score <= 30:
            conclusion = "Показаний к операции нет. Признаков деструктивных осложнений нет."
            recommendation = "Динамическое наблюдение, продолжить консервативное лечение."
        elif 31 <= score <= 54:
            conclusion = "Показания к операции нечеткие. Риска деструктивных осложнений нет."
            recommendation = "Повторное клиническое обследование, уточнение сомнительных признаков."
        elif 55 <= score <= 80:
            conclusion = "Показание к операции. Имеется риск возникновения деструктивных осложнений."
            recommendation = "Подготовка к операции в короткие сроки (в течение 2-3 часов)."
        else:
            conclusion = "Показание к экстренной операции. Имеются признаки деструктивной осложненности."
            recommendation = "Перевод в операционную для экстренной операции (в течение часа)."

        result_text += f"\nКлиническое заключение: {conclusion}\nРекомендации: {recommendation}"
        self.result_output.setText(result_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiagnosisApp()
    window.show()
    sys.exit(app.exec())
