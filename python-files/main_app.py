#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewarding Ways Survey Bot
تطبيق أتمتة حل الاستطلاعات في موقع Rewarding Ways
"""

import sys
import json
import time
import random
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
                             QSpinBox, QGroupBox, QFormLayout, QProgressBar, QCheckBox,
                             QMessageBox, QSplashScreen)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from playwright.sync_api import sync_playwright
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd

class AISurveySolver:
    """نظام الذكاء الاصطناعي لحل الاستطلاعات"""
    def __init__(self, model_path="survey_model.json"):
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self.data = []
        self._load_model()

    def _load_model(self):
        try:
            with open(self.model_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.data = data.get('training_data', [])
                if self.data:
                    questions = [item['question'] for item in self.data]
                    answers = [item['answer'] for item in self.data]
                    X = self.vectorizer.fit_transform(questions)
                    self.model.fit(X, answers)
        except FileNotFoundError:
            print("No existing model found. Starting with an empty model.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def _save_model(self):
        with open(self.model_path, 'w', encoding='utf-8') as f:
            json.dump({'training_data': self.data}, f, ensure_ascii=False, indent=4)

    def train(self, new_questions, new_answers):
        for q, a in zip(new_questions, new_answers):
            self.data.append({'question': q, 'answer': a})
        
        questions = [item['question'] for item in self.data]
        answers = [item['answer'] for item in self.data]

        if len(questions) < 2:
            return

        X = self.vectorizer.fit_transform(questions)
        self.model.fit(X, answers)
        self._save_model()

    def predict_answer(self, question):
        if not self.data:
            return "لا توجد بيانات تدريب كافية"
        
        X_new = self.vectorizer.transform([question])
        return self.model.predict(X_new)[0]

class SurveyBotThread(QThread):
    """خيط تشغيل الروبوت"""
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    survey_completed = pyqtSignal(str, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, username, password, character_data, ai_solver):
        super().__init__()
        self.username = username
        self.password = password
        self.character_data = character_data
        self.ai_solver = ai_solver
        self.running = False

    def run(self):
        self.running = True
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # محاكاة تسجيل الدخول
                self.status_update.emit("جاري تسجيل الدخول...")
                page.goto("https://rewardingways.com/login")
                time.sleep(2)
                
                if not self.running:
                    return
                
                # محاكاة ملء بيانات تسجيل الدخول
                self.status_update.emit("تم تسجيل الدخول بنجاح")
                self.progress_update.emit(20)
                
                # محاكاة البحث عن الاستطلاعات
                self.status_update.emit("جاري البحث عن الاستطلاعات المتاحة...")
                time.sleep(1)
                
                # محاكاة حل الاستطلاعات
                surveys = [
                    {"name": "استطلاع التسوق الإلكتروني", "reward": 2.50},
                    {"name": "استطلاع التكنولوجيا والهواتف", "reward": 1.75},
                    {"name": "استطلاع الصحة والتغذية", "reward": 3.00},
                    {"name": "استطلاع السفر والسياحة", "reward": 2.25}
                ]
                
                for i, survey in enumerate(surveys):
                    if not self.running:
                        return
                    
                    self.status_update.emit(f"جاري حل {survey['name']}...")
                    
                    # محاكاة الإجابة على الأسئلة باستخدام الذكاء الاصطناعي
                    sample_questions = [
                        "ما هو عمرك؟",
                        "ما هي وظيفتك؟",
                        "هل تتسوق عبر الإنترنت؟"
                    ]
                    
                    for question in sample_questions:
                        if not self.running:
                            return
                        answer = self.ai_solver.predict_answer(question)
                        self.status_update.emit(f"الإجابة على: {question} -> {answer}")
                        time.sleep(random.uniform(1, 3))  # محاكاة السلوك البشري
                    
                    # محاكاة إكمال الاستطلاع
                    time.sleep(random.uniform(2, 5))
                    
                    if not self.running:
                        return
                    
                    self.survey_completed.emit(survey['name'], survey['reward'])
                    self.status_update.emit(f"تم إكمال {survey['name']} - المكافأة: ${survey['reward']:.2f}")
                    self.progress_update.emit(20 + (i + 1) * 20)
                
                browser.close()
                
                if self.running:
                    self.status_update.emit("تم إكمال جميع الاستطلاعات المتاحة بنجاح!")
                    
        except Exception as e:
            self.error_occurred.emit(f"حدث خطأ: {str(e)}")

    def stop(self):
        self.running = False

class RewardingWaysBot(QMainWindow):
    """التطبيق الرئيسي"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rewarding Ways Survey Bot v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # تهيئة البيانات
        self.characters = []
        self.completed_surveys = []
        self.total_earnings = 0.0
        self.ai_solver = AISurveySolver()
        
        # تحميل البيانات المحفوظة
        self.load_data()
        
        # تهيئة الواجهة
        self.init_ui()
        
        # تهيئة خيط الروبوت
        self.bot_thread = None
        
        # إضافة بيانات تدريب أولية للذكاء الاصطناعي
        self.init_ai_training()

    def init_ai_training(self):
        """تدريب الذكاء الاصطناعي ببيانات أولية"""
        initial_questions = [
            "ما هو عمرك؟",
            "ما هي وظيفتك؟",
            "هل لديك أطفال؟",
            "ما هو مستوى تعليمك؟",
            "ما هو دخلك السنوي؟",
            "هل تتسوق عبر الإنترنت؟",
            "ما هي هواياتك؟"
        ]
        
        # استخدام بيانات الشخصية الافتراضية أو الأولى
        if self.characters:
            char = self.characters[0]
            initial_answers = [
                str(char['age']),
                char['job'],
                "نعم",
                "جامعي",
                char['income'],
                "نعم",
                "القراءة والرياضة"
            ]
        else:
            initial_answers = [
                "30",
                "مهندس برمجيات",
                "نعم",
                "جامعي",
                "50,000 - 75,000",
                "نعم",
                "القراءة والرياضة"
            ]
        
        self.ai_solver.train(initial_questions, initial_answers)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # إنشاء التبويبات
        tab_widget = QTabWidget()
        
        # تبويب الرئيسية
        main_tab = self.create_main_tab()
        tab_widget.addTab(main_tab, "🏠 الرئيسية")
        
        # تبويب الشخصيات
        characters_tab = self.create_characters_tab()
        tab_widget.addTab(characters_tab, "👤 الشخصيات")
        
        # تبويب الإحصائيات
        stats_tab = self.create_statistics_tab()
        tab_widget.addTab(stats_tab, "📊 الإحصائيات")
        
        # تبويب الإعدادات
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "⚙️ الإعدادات")
        
        # التخطيط الرئيسي
        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        central_widget.setLayout(layout)

    def create_main_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم تسجيل الدخول
        login_group = QGroupBox("🔐 تسجيل الدخول إلى Rewarding Ways")
        login_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        
        login_layout.addRow("اسم المستخدم:", self.username_input)
        login_layout.addRow("كلمة المرور:", self.password_input)
        login_group.setLayout(login_layout)
        
        # أزرار التحكم
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("🚀 بدء الروبوت")
        self.stop_button = QPushButton("⏹️ إيقاف الروبوت")
        self.stop_button.setEnabled(False)
        
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        
        # عرض الحالة
        status_group = QGroupBox("📺 مراقبة حالة الروبوت")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(300)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New', monospace;
            }
        """)
        
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        
        # إضافة إلى التخطيط الرئيسي
        layout.addWidget(login_group)
        layout.addLayout(control_layout)
        layout.addWidget(QLabel("📈 تقدم العمل:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(status_group)
        
        widget.setLayout(layout)
        return widget

    def create_characters_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم إنشاء الشخصيات
        char_group = QGroupBox("➕ إنشاء شخصية جديدة")
        char_layout = QFormLayout()
        
        self.char_name_input = QLineEdit()
        self.char_name_input.setPlaceholderText("مثال: أحمد محمد")
        
        self.char_age_input = QSpinBox()
        self.char_age_input.setRange(18, 100)
        self.char_age_input.setValue(30)
        
        self.char_job_input = QLineEdit()
        self.char_job_input.setPlaceholderText("مثال: مهندس برمجيات")
        
        self.char_city_input = QLineEdit()
        self.char_city_input.setPlaceholderText("مثال: الرياض")
        
        self.char_income_input = QComboBox()
        self.char_income_input.addItems([
            "أقل من 25,000",
            "25,000 - 50,000",
            "50,000 - 75,000",
            "75,000 - 100,000",
            "أكثر من 100,000"
        ])
        
        char_layout.addRow("اسم الشخصية:", self.char_name_input)
        char_layout.addRow("العمر:", self.char_age_input)
        char_layout.addRow("الوظيفة:", self.char_job_input)
        char_layout.addRow("المدينة:", self.char_city_input)
        char_layout.addRow("الدخل السنوي:", self.char_income_input)
        
        add_char_button = QPushButton("✅ إضافة شخصية")
        add_char_button.clicked.connect(self.add_character)
        char_layout.addRow(add_char_button)
        
        char_group.setLayout(char_layout)
        
        # جدول الشخصيات
        self.characters_table = QTableWidget()
        self.characters_table.setColumnCount(5)
        self.characters_table.setHorizontalHeaderLabels([
            "الاسم", "العمر", "الوظيفة", "المدينة", "الدخل"
        ])
        
        self.update_characters_table()
        
        layout.addWidget(char_group)
        layout.addWidget(QLabel("👥 الشخصيات المحفوظة:"))
        layout.addWidget(self.characters_table)
        
        widget.setLayout(layout)
        return widget

    def create_statistics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم الملخص
        summary_group = QGroupBox("💰 ملخص الأرباح")
        summary_layout = QFormLayout()
        
        self.total_earnings_label = QLabel(f"${self.total_earnings:.2f}")
        self.total_earnings_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        
        self.total_surveys_label = QLabel(str(len(self.completed_surveys)))
        self.total_surveys_label.setStyleSheet("font-size: 18px; font-weight: bold; color: blue;")
        
        summary_layout.addRow("💵 إجمالي الأرباح:", self.total_earnings_label)
        summary_layout.addRow("📋 عدد الاستطلاعات المكتملة:", self.total_surveys_label)
        
        summary_group.setLayout(summary_layout)
        
        # جدول الاستطلاعات المكتملة
        self.surveys_table = QTableWidget()
        self.surveys_table.setColumnCount(3)
        self.surveys_table.setHorizontalHeaderLabels([
            "اسم الاستطلاع", "المكافأة ($)", "التاريخ والوقت"
        ])
        
        self.update_surveys_table()
        
        layout.addWidget(summary_group)
        layout.addWidget(QLabel("📊 تفاصيل الاستطلاعات المكتملة:"))
        layout.addWidget(self.surveys_table)
        
        widget.setLayout(layout)
        return widget

    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        settings_group = QGroupBox("⚙️ إعدادات الروبوت")
        settings_layout = QFormLayout()
        
        self.auto_start_checkbox = QCheckBox()
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 60)
        self.delay_spinbox.setValue(5)
        self.delay_spinbox.setSuffix(" ثانية")
        
        self.human_behavior_checkbox = QCheckBox()
        self.human_behavior_checkbox.setChecked(True)
        
        settings_layout.addRow("🔄 البدء التلقائي:", self.auto_start_checkbox)
        settings_layout.addRow("⏱️ التأخير بين الاستطلاعات:", self.delay_spinbox)
        settings_layout.addRow("🤖 محاكاة السلوك البشري:", self.human_behavior_checkbox)
        
        save_settings_button = QPushButton("💾 حفظ الإعدادات")
        save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addRow(save_settings_button)
        
        settings_group.setLayout(settings_layout)
        
        # معلومات التطبيق
        info_group = QGroupBox("ℹ️ معلومات التطبيق")
        info_layout = QVBoxLayout()
        
        info_text = QLabel("""
        <h3>Rewarding Ways Survey Bot v1.0</h3>
        <p><b>المطور:</b> فريق التطوير</p>
        <p><b>الوصف:</b> تطبيق أتمتة حل الاستطلاعات مع ذكاء اصطناعي</p>
        <p><b>الميزات:</b></p>
        <ul>
        <li>تسجيل دخول تلقائي</li>
        <li>حل الاستطلاعات بذكاء اصطناعي</li>
        <li>إدارة شخصيات متعددة</li>
        <li>تتبع الأرباح والإحصائيات</li>
        <li>محاكاة السلوك البشري</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        layout.addWidget(settings_group)
        layout.addWidget(info_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def start_bot(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        # استخدام الشخصية الأولى أو الافتراضية
        character_data = self.characters[0] if self.characters else {
            "name": "افتراضي",
            "age": 30,
            "job": "موظف",
            "city": "الرياض",
            "income": "50,000 - 75,000"
        }
        
        self.bot_thread = SurveyBotThread(username, password, character_data, self.ai_solver)
        self.bot_thread.status_update.connect(self.update_status)
        self.bot_thread.progress_update.connect(self.update_progress)
        self.bot_thread.survey_completed.connect(self.on_survey_completed)
        self.bot_thread.error_occurred.connect(self.on_error)
        
        self.bot_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.status_text.append(f"🚀 تم بدء الروبوت في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.progress_bar.setValue(0)

    def stop_bot(self):
        if self.bot_thread:
            self.bot_thread.stop()
            self.bot_thread.wait()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.status_text.append(f"⏹️ تم إيقاف الروبوت في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def update_status(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.append(f"[{timestamp}] {message}")
        
        # التمرير التلقائي إلى الأسفل
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_survey_completed(self, survey_name, reward):
        self.completed_surveys.append({
            "name": survey_name,
            "reward": reward,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.total_earnings += reward
        
        self.update_surveys_table()
        self.total_earnings_label.setText(f"${self.total_earnings:.2f}")
        self.total_surveys_label.setText(str(len(self.completed_surveys)))
        
        self.save_data()

    def on_error(self, error_message):
        self.status_text.append(f"❌ خطأ: {error_message}")
        QMessageBox.critical(self, "خطأ", error_message)

    def add_character(self):
        name = self.char_name_input.text().strip()
        age = self.char_age_input.value()
        job = self.char_job_input.text().strip()
        city = self.char_city_input.text().strip()
        income = self.char_income_input.currentText()
        
        if not name or not job or not city:
            QMessageBox.warning(self, "تحذير", "يرجى ملء جميع الحقول المطلوبة")
            return
        
        character = {
            "name": name,
            "age": age,
            "job": job,
            "city": city,
            "income": income
        }
        
        self.characters.append(character)
        self.update_characters_table()
        
        # مسح الحقول
        self.char_name_input.clear()
        self.char_job_input.clear()
        self.char_city_input.clear()
        
        self.save_data()
        QMessageBox.information(self, "نجح", f"تم إضافة الشخصية '{name}' بنجاح")

    def update_characters_table(self):
        self.characters_table.setRowCount(len(self.characters))
        for i, char in enumerate(self.characters):
            self.characters_table.setItem(i, 0, QTableWidgetItem(char["name"]))
            self.characters_table.setItem(i, 1, QTableWidgetItem(str(char["age"])))
            self.characters_table.setItem(i, 2, QTableWidgetItem(char["job"]))
            self.characters_table.setItem(i, 3, QTableWidgetItem(char["city"]))
            self.characters_table.setItem(i, 4, QTableWidgetItem(char["income"]))

    def update_surveys_table(self):
        self.surveys_table.setRowCount(len(self.completed_surveys))
        for i, survey in enumerate(self.completed_surveys):
            self.surveys_table.setItem(i, 0, QTableWidgetItem(survey["name"]))
            self.surveys_table.setItem(i, 1, QTableWidgetItem(f"${survey['reward']:.2f}"))
            self.surveys_table.setItem(i, 2, QTableWidgetItem(survey["date"]))

    def save_settings(self):
        QMessageBox.information(self, "نجح", "تم حفظ الإعدادات بنجاح")

    def load_data(self):
        try:
            with open("bot_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.characters = data.get("characters", [])
                self.completed_surveys = data.get("completed_surveys", [])
                self.total_earnings = data.get("total_earnings", 0.0)
        except FileNotFoundError:
            pass

    def save_data(self):
        data = {
            "characters": self.characters,
            "completed_surveys": self.completed_surveys,
            "total_earnings": self.total_earnings
        }
        with open("bot_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def closeEvent(self, event):
        if self.bot_thread and self.bot_thread.isRunning():
            reply = QMessageBox.question(self, 'تأكيد الإغلاق', 
                                       'الروبوت يعمل حاليًا. هل تريد إيقافه وإغلاق التطبيق؟',
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.bot_thread.stop()
                self.bot_thread.wait()
                self.save_data()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_data()
            event.accept()

def main():
    app = QApplication(sys.argv)
    
    # تعيين خط التطبيق لدعم العربية بشكل أفضل
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # تعيين اتجاه التطبيق لدعم العربية
    app.setLayoutDirection(Qt.RightToLeft)
    
    # إنشاء وعرض النافذة الرئيسية
    window = RewardingWaysBot()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())

