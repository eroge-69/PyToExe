import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox,
                             QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QLinearGradient, QColor


class AnswerWidget(QFrame):
    def __init__(self, label, color, value, main_window):
        super().__init__()
        self.value = value
        self.is_selected = False
        self.color = color
        self.main_window = main_window

        self.setMinimumSize(100, 80)
        self.setMaximumSize(120, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(6, 6, 6, 6)

        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setWordWrap(True)
        label_widget.setStyleSheet("color: #2C3E50; font-size: 16px; font-weight: bold; background: transparent;")
        layout.addWidget(label_widget)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)

        self.update_style()

    def update_style(self):
        border = "3px solid #FFD700" if self.is_selected else "3px solid transparent"
        bg_color = self.color if not self.is_selected else f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.color}, stop:1 #FFD700)"

        self.setStyleSheet(f"""
            AnswerWidget {{
                background: {bg_color};
                border-radius: 12px;
                border: {border};
            }}
            AnswerWidget:hover {{
                border: 3px solid white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.color}, stop:1 rgba(255,255,255,0.3));
            }}
        """)

    def mousePressEvent(self, event):
        self.set_selected(True)
        self.main_window.on_answer_clicked(self)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()


class InnovationRiskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FINANCIAL UNIVERSITY")
        self.setMinimumSize(1000, 750)

        self.questions = [
            "Может ли предлагаемая услуга, как охраняемый результат интеллектуальной деятельности защищена патентом или другим способом в рамках российского законодательства в области интеллектуальной собственности?",
            "Предлагаемая услуга не может быстро и легко скопирована основными конкурентами в отрасли?",
            "Предлагаемая услуга дает потребителю новые возможности?",
            "Услуга может быстро окупиться (срок окупаемости менее 1 года)?",
            "Реализация данной услуги не требует от компании дополнительного финансирования?",
            "Технология оказания данной услуги является стандартной?",
            "Для реализации предлагаемой услуги сотрудникам компании не нужны особые, новые знания?",
            "Предлагаемая услуга не противоречит бизнес-модели компании?",
            "Новая услуга имеет значительные перспективы в своей отрасли?",
            "Можно ли предложить данную услугу клиентам, компаниям из других отраслей?",
            "Предлагаемая услуга не может быть заменена системой искусственного интеллекта в настоящее время?",
            "Предлагаемая услуга не сможет быть заменена технологиями искусственного интеллекта в ближайшем будущем?"
        ]

        self.answers = [0] * len(self.questions)
        self.current_question = 0
        self.answer_widgets = []

        self.init_ui()

    def init_ui(self):
        self.set_modern_theme()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        layout.addWidget(self.create_header())
        layout.addWidget(self.create_content_area(), 1)
        layout.addWidget(self.create_footer())

        self.update_navigation()

    def set_modern_theme(self):
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor(64, 124, 189))
        gradient.setColorAt(0.5, QColor(96, 184, 211))
        gradient.setColorAt(1.0, QColor(155, 226, 245))

        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

    def create_glass_frame(self):
        frame = QFrame()
        frame.setStyleSheet("background: rgba(255, 255, 255, 0.15); border-radius: 20px;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)

        return frame

    def create_header(self):
        frame = self.create_glass_frame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("FINANCIAL UNIVERSITY \n 🚀 Экспресс-оценка инновационного риска")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold; background: transparent; padding: 10px;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()

        return frame

    def create_content_area(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.create_progress_section())
        layout.addWidget(self.create_question_section(), 3)
        layout.addWidget(self.create_answers_section(), 1)

        return container

    def create_progress_section(self):
        frame = self.create_glass_frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)

        self.progress_label = QLabel(f"Вопрос {self.current_question + 1} из {len(self.questions)}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.progress_label)

        progress_bg = QFrame()
        progress_bg.setStyleSheet("background-color: rgba(255, 255, 255, 0.25); border-radius: 10px;")
        progress_bg.setFixedHeight(12)

        self.progress_bar = QFrame(progress_bg)
        self.progress_bar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:1 #4ECDC4); border-radius: 10px;")
        self.progress_bar.setFixedHeight(12)

        layout.addWidget(progress_bg)
        return frame

    def create_question_section(self):
        frame = self.create_glass_frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(30, 5, 30, 40)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setStyleSheet(
            "color: white; font-size: 26px; font-weight: bold; line-height: 1.6; background: transparent; padding: 20px;")
        self.question_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.question_label.setMinimumHeight(180)

        layout.addWidget(self.question_label)
        return frame

    def create_answers_section(self):
        frame = self.create_glass_frame()
        layout = QHBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        answer_data = [
            ("Точно нет", "#FF6B6B", -2),
            ("Нет", "#FFA8A8", -1),
            ("Не знаю", "#E9ECEF", 0),
            ("Да", "#A5D8FF", 1),
            ("Точно да", "#4ECDC4", 2)
        ]

        self.answer_widgets.clear()
        for label, color, value in answer_data:
            widget = AnswerWidget(label, color, value, self)
            layout.addWidget(widget)
            self.answer_widgets.append(widget)

        return frame

    def create_footer(self):
        frame = self.create_glass_frame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)

        reset_btn = QPushButton("🔄 Начать заново")
        reset_btn.setMinimumSize(160, 55)
        reset_btn.setStyleSheet(self.get_button_style("#E9ECEF"))
        reset_btn.clicked.connect(self.reset_answers)

        layout.addStretch()
        layout.addWidget(reset_btn)
        layout.addStretch()

        return frame

    def get_button_style(self, base_color):
        text_color = "#000000" if base_color == "#E9ECEF" else "white"

        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {base_color}, stop:1 {QColor(base_color).darker(120).name()});
                color: {text_color}; font-size: 16px; font-weight: bold; padding: 15px 25px;
                border: none; border-radius: 12px; min-width: 120px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {QColor(base_color).lighter(120).name()}, stop:1 {base_color});
            }}
            QPushButton:pressed {{
                background: {QColor(base_color).darker(120).name()};
            }}
        """

    def on_answer_clicked(self, clicked_widget):
        for widget in self.answer_widgets:
            widget.set_selected(False)

        clicked_widget.set_selected(True)
        self.answers[self.current_question] = clicked_widget.value

        if self.current_question == len(self.questions) - 1:
            QTimer.singleShot(300, self.show_results)
        else:
            QTimer.singleShot(300, self.next_question_auto)

    def next_question_auto(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_navigation()

    def update_navigation(self):
        self.progress_label.setText(f"Вопрос {self.current_question + 1} из {len(self.questions)}")
        self.question_label.setText(self.questions[self.current_question])

        for widget in self.answer_widgets:
            widget.set_selected(False)

        current_answer = self.answers[self.current_question]
        if current_answer != 0:
            for widget in self.answer_widgets:
                if widget.value == current_answer:
                    widget.set_selected(True)
                    break

        self.update_progress_bar()

    def update_progress_bar(self):
        progress = (self.current_question + 1) / len(self.questions)
        if hasattr(self, 'progress_bar') and self.progress_bar.parent().width() > 0:
            bar_width = int(self.progress_bar.parent().width() * progress)
            self.progress_bar.setFixedWidth(bar_width)

    def reset_answers(self):
        reply = QMessageBox.question(self, "Подтверждение сброса",
                                     "Вы уверены, что хотите начать тестирование заново?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.answers = [0] * len(self.questions)
            self.current_question = 0
            self.update_navigation()

    def show_results(self):
        total_score = sum(self.answers)

        if total_score >= 12:
            risk_data = ("Безопасный уровень 🟢", "#28A745", "🎉",
                         "Низкий уровень инновационного риска. Услуга имеет высокие шансы на успех.")
        elif total_score >= 0:
            risk_data = ("Допустимый инновационный риск 🟡", "#FFC107", "⚠️",
                         "Умеренный уровень риска. Требуется дополнительный анализ и планирование.")
        elif total_score >= -11:
            risk_data = ("Критический инновационный риск 🟠", "#FD7E14", "🔥",
                         "Высокий уровень риска. Необходимы серьезные доработки и оценка целесообразности.")
        else:
            risk_data = ("Недопустимый инновационный риск 🔴", "#DC3545", "🚨",
                         "Очень высокий уровень риска. Рекомендуется пересмотреть концепцию услуги.")

        risk_level, color, icon, description = risk_data

        result_text = f"""
        <div style='text-align: center;'>
            <h1 style='color: #2C3E50; margin-bottom: 30px; font-size: 32px;'>{icon} Результаты оценки</h1>
            <p style='font-size: 20px; color: #2C3E50; margin: 15px;'>Итоговая сумма баллов:</p>
            <p style='font-size: 64px; color: {color}; font-weight: bold; margin: 25px;'>{total_score}</p>
            <p style='font-size: 28px; color: {color}; font-weight: bold; margin: 20px;'>{risk_level}</p>
            <p style='font-size: 18px; color: #5A6C7D; margin-top: 25px; line-height: 1.6; padding: 0 20px;'>{description}</p>
        </div>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("🎯 FINANCIAL UNIVERSITY")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(result_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background: white;
                border: 3px solid #E9ECEF;
                border-radius: 20px; 
                min-width: 680px;
                min-height: 480px;
            }
            QMessageBox QLabel { 
                color: #495057; 
                background: transparent; 
                font-family: "Segoe UI";
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6C757D, 
                    stop:1 #495057);
                color: white; 
                font-size: 16px; 
                font-weight: bold; 
                padding: 14px 32px;
                border: none;
                border-radius: 10px; 
                min-width: 130px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5A6268, 
                    stop:1 #3D4348);
            }
            QPushButton:pressed {
                background: #3D4348;
            }
        """)

        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    window = InnovationRiskApp()
    window.show()

    sys.exit(app.exec())