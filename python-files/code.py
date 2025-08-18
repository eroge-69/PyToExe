import sys
import csv
import os
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

# قائمة أيام الأسبوع بالترتيب
days_order = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']

class StudentScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("جدول الطالب")
        self.setGeometry(100, 100, 900, 700)
        
        # تحديد مسار الملف الحالي للبرنامج
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # إنشاء الخطوط
        self.title_font = QFont("Arial", 18, QFont.Bold)
        self.header_font = QFont("Arial", 12, QFont.Bold)
        self.normal_font = QFont("Arial", 11)
        
        # إنشاء الواجهة الرئيسية
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # إضافة عنوان
        self.title_label = QLabel("جدول الطالب")
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title_label)
        
        # إنشاء إطار الإدخال
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; padding: 15px;")
        input_layout = QHBoxLayout(input_frame)
        
        # حقل إدخال اسم الطالب
        self.student_label = QLabel("اسم الطالب:")
        self.student_label.setFont(self.header_font)
        input_layout.addWidget(self.student_label)
        
        self.student_input = QLineEdit()
        self.student_input.setFont(self.normal_font)
        self.student_input.setMinimumHeight(40)
        self.student_input.setPlaceholderText("أدخل اسم الطالب بالكامل")
        self.student_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2980b9;
            }
        """)
        input_layout.addWidget(self.student_input)
        
        # زر البحث
        self.search_button = QPushButton("عرض الجدول")
        self.search_button.setFont(self.header_font)
        self.search_button.setMinimumHeight(40)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.search_button.clicked.connect(self.display_schedule)
        input_layout.addWidget(self.search_button)
        
        self.main_layout.addWidget(input_frame)
        
        # إضافة مساحة
        self.main_layout.addSpacing(20)
        
        # إنشاء جدول النتائج
        self.result_frame = QFrame()
        self.result_frame.setFrameShape(QFrame.StyledPanel)
        self.result_frame.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
        """)
        result_layout = QVBoxLayout(self.result_frame)
        
        # عنوان النتائج
        self.result_title = QLabel("")
        self.result_title.setFont(self.header_font)
        self.result_title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        self.result_title.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_title)
        
        # جدول عرض النتائج
        self.table_widget = QTableWidget()
        self.table_widget.setFont(self.normal_font)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["اليوم", "الفترة", "المادة", "المعلم"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setFont(self.header_font)
        self.table_widget.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #ecf0f1;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        self.table_widget.setAlternatingRowColors(True)
        
        result_layout.addWidget(self.table_widget)
        
        self.main_layout.addWidget(self.result_frame, 1)
        
        # إضافة تذييل
        footer = QLabel("© 2023 جدول الطالب - جميع الحقوق محفوظة الاستاذ عبدالرحمن خلف")
        footer.setFont(QFont("Arial", 9))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; margin-top: 20px;")
        self.main_layout.addWidget(footer)
        
        # تعيين لون الخلفية
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(236, 240, 241))
        self.setPalette(palette)
    
    def get_student_schedule(self, student_name):
        # قراءة ملف CSV وتجميع الجدول
        schedule = defaultdict(lambda: defaultdict(list))
        try:
            # تحديد المسار الكامل لملف CSV
            csv_path = os.path.join(self.base_dir, 'schedule.csv')
            
            # التحقق من وجود الملف
            if not os.path.exists(csv_path):
                QMessageBox.critical(self, "خطأ", 
                    f"ملف schedule.csv غير موجود في المجلد:\n{self.base_dir}\n"
                    "الرجاء التأكد من وجود الملف في نفس مجلد البرنامج.")
                return None
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # تخطي رأس الجدول
                
                for row in reader:
                    if len(row) < 6:  # تأكيد وجود جميع الأعمدة
                        continue
                        
                    day, period, subject, section, teacher, students = row
                    student_list = [s.strip() for s in students.split(',')]
                    
                    if student_name in student_list:
                        try:
                            period = int(period)
                        except ValueError:
                            continue
                        
                        schedule[day][period].append({
                            'subject': subject,
                            'teacher': teacher,
                            'section': section
                        })
        except Exception as e:
            QMessageBox.critical(self, "خطأ", 
                f"حدث خطأ أثناء قراءة الملف:\n{str(e)}\n"
                f"مسار الملف: {csv_path}")
            return None
        
        # ترتيب الجدول حسب الأيام والفترات
        ordered_schedule = []
        for day in days_order:
            if day in schedule:
                periods = sorted(schedule[day].keys())
                daily_schedule = []
                for period in periods:
                    for class_info in schedule[day][period]:
                        daily_schedule.append({
                            'day': day,
                            'period': period,
                            'subject': class_info['subject'],
                            'teacher': class_info['teacher'],
                            'section': class_info['section']
                        })
                ordered_schedule.extend(daily_schedule)
        
        return ordered_schedule
    
    def display_schedule(self):
        student_name = self.student_input.text().strip()
        if not student_name:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال اسم الطالب")
            return
        
        # الحصول على جدول الطالب
        schedule = self.get_student_schedule(student_name)
        
        if schedule is None:
            return
        
        if not schedule:
            self.result_title.setText(f"لم يتم العثور على جدول للطالب: {student_name}")
            self.table_widget.setRowCount(0)
            return
        
        # تحديث عنوان النتائج
        self.result_title.setText(f"جدول الطالب: {student_name}")
        
        # تعبئة الجدول بالنتائج
        self.table_widget.setRowCount(len(schedule))
        
        for row_idx, class_info in enumerate(schedule):
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(class_info['day']))
            self.table_widget.setItem(row_idx, 1, QTableWidgetItem(str(class_info['period'])))  # تم تصحيح السطر هنا
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(class_info['subject']))
            self.table_widget.setItem(row_idx, 3, QTableWidgetItem(class_info['teacher']))
            
            # تلوين الصفوف حسب اليوم
            day_color = {
                'الأحد': QColor(231, 76, 60, 50),
                'الاثنين': QColor(155, 89, 182, 50),
                'الثلاثاء': QColor(52, 152, 219, 50),
                'الأربعاء': QColor(46, 204, 113, 50),
                'الخميس': QColor(241, 196, 15, 50)
            }
            
            if class_info['day'] in day_color:
                for col in range(4):
                    self.table_widget.item(row_idx, col).setBackground(day_color[class_info['day']])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # حل مشكلة اللغة العربية
    app.setFont(QFont("Arial", 11))
    
    window = StudentScheduleApp()
    window.show()
    sys.exit(app.exec_())