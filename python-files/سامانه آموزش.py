import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
    QStackedWidget, QCheckBox, QComboBox, QSpinBox, QAbstractItemView
)
from PyQt6.QtCore import Qt

DB_NAME = "university.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fields (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            total_units INTEGER NOT NULL,
            max_semesters INTEGER NOT NULL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        personnel_code TEXT PRIMARY KEY,
        national_code TEXT NOT NULL,
        fullname TEXT NOT NULL,
        academic_rank TEXT NOT NULL
       )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
       student_id TEXT,
        term_code TEXT,
       offering_id INTEGER,
       PRIMARY KEY(student_id, term_code, offering_id)
       )

    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS course_offerings (
        offering_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT NOT NULL,
        field_code TEXT NOT NULL,
        term_code TEXT NOT NULL,
        professor_code TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,  -- 0 تا 5 (شنبه تا پنجشنبه)
        start_time TEXT NOT NULL,      -- 4 رقمی مثل 0800
        FOREIGN KEY(course_code) REFERENCES courses(course_code),
        FOREIGN KEY(field_code) REFERENCES fields(field_code),
        FOREIGN KEY(term_code) REFERENCES terms(term_code),
        FOREIGN KEY(professor_code) REFERENCES professors(professor_code)
    )

    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_code TEXT PRIMARY KEY,
        field_code TEXT NOT NULL,
        course_name TEXT NOT NULL,
        units INTEGER NOT NULL,
        passing_grade INTEGER NOT NULL,
        FOREIGN KEY (field_code) REFERENCES fields(code)
      )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS terms (
         term_code TEXT PRIMARY KEY,
         term_name TEXT NOT NULL,
         is_current INTEGER NOT NULL DEFAULT 0

      )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grades (
         student_id TEXT,
         offering_id INTEGER,
         term_code TEXT,
         grade REAL,
         PRIMARY KEY (student_id, offering_id, term_code),
         FOREIGN KEY (student_id) REFERENCES students(student_id),
         FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
         FOREIGN KEY (term_code) REFERENCES terms(term_code)
      )
    """)




    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            national_code TEXT NOT NULL,
            fullname TEXT NOT NULL,
            field_code TEXT NOT NULL,
            entry_year INTEGER NOT NULL,
            entry_semester INTEGER NOT NULL,
            FOREIGN KEY (field_code) REFERENCES fields(code)
        )
    """)
    conn.commit()
    conn.close()



class StudentRecordViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مشاهده و ویرایش سوابق تحصیلی")
        self.resize(1000, 700)

        self.student_id = None

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ورودی کد دانشجو
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("کد دانشجو:"))
        self.student_id_input = QLineEdit()
        search_layout.addWidget(self.student_id_input)

        # دکمه جستجو (می‌تونیم حذف کنیم برای اتومات)
        self.search_btn = QPushButton("جستجو")
        self.search_btn.clicked.connect(self.search_student)
        search_layout.addWidget(self.search_btn)

        main_layout.addLayout(search_layout)

        # نمایش اطلاعات دانشجو
        self.student_info_label = QLabel("اطلاعات دانشجو: -")
        main_layout.addWidget(self.student_info_label)

        # انتخاب نیمسال
        term_layout = QHBoxLayout()
        term_layout.addWidget(QLabel("انتخاب نیمسال:"))
        self.term_combo = QComboBox()
        self.term_combo.currentIndexChanged.connect(self.term_changed)
        term_layout.addWidget(self.term_combo)
        main_layout.addLayout(term_layout)

        # جدول دروس و نمرات
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["کد درس", "شماره گروه", "نام درس", "نمره", "حذف"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        main_layout.addWidget(self.table)

        # خلاصه وضعیت
        self.summary_label = QLabel()
        main_layout.addWidget(self.summary_label)

        # اتوماتیک بارگذاری وقتی کد دانشجو وارد شد (بدون نیاز به دکمه)
        self.student_id_input.textChanged.connect(self.auto_load_student)

    def auto_load_student(self):
        # اگر رشته ورودی به حداقل 5 حرف رسید (یا شرایط دیگه)
        sid = self.student_id_input.text().strip()
        if len(sid) >= 11:
            self.search_student()
        else:
            self.clear_all()

    def clear_all(self):
        self.student_info_label.setText("اطلاعات دانشجو: -")
        self.term_combo.clear()
        self.table.setRowCount(0)
        self.summary_label.clear()
        self.student_id = None

    def search_student(self):
      try:
        sid = self.student_id_input.text().strip()
        if not sid:
            self.clear_all()
            return

        rows = self.fetch_db("""
            SELECT s.fullname, f.name
            FROM students s
            JOIN fields f ON s.field_code = f.code
            WHERE s.student_id=?
        """, (sid,))

        if not rows:
            QMessageBox.warning(self, "خطا", "دانشجویی با این کد یافت نشد.")
            self.clear_all()
            return

        fullname, field_name = rows[0]
        self.student_info_label.setText(f"<b>نام:</b> {fullname} &nbsp;&nbsp; <b>رشته:</b> {field_name}")
        self.student_id = sid

        self.load_terms()

      except sqlite3.OperationalError as e:
        QMessageBox.critical(self, "خطای پایگاه داده", f"خطای دیتابیس: {e}")
      except Exception as e:
        QMessageBox.critical(self, "خطای داخلی", f"خطا: {e}")

    def load_terms(self):
        if not self.student_id:
            self.term_combo.clear()
            return
        # نیمسال‌هایی که دانشجو در آن‌ها ثبت‌نام کرده یا نمره گرفته
        terms = self.fetch_db("""
            SELECT DISTINCT term_code, term_name FROM terms
            WHERE term_code IN (
                SELECT term_code FROM enrollments WHERE student_id=?
                UNION
                SELECT term_code FROM grades WHERE student_id=?
            )
            ORDER BY term_code DESC
        """, (self.student_id, self.student_id))

        self.term_combo.clear()
        for code, name in terms:
            self.term_combo.addItem(f"{name} ({code})", code)

        if terms:
            self.term_combo.setCurrentIndex(0)
        else:
            self.table.setRowCount(0)
            self.summary_label.setText("هیچ نیمسالی برای این دانشجو وجود ندارد.")

    def term_changed(self):
        term_code = self.term_combo.currentData()
        if term_code:
            self.load_courses(term_code)

    def load_courses(self, term_code):
        if not self.student_id:
            return

        # دریافت لیست دروس با نمرات و مشخصات
        courses = self.fetch_db("""
            SELECT g.course_code, co.offering_id, c.course_name, g.grade, c.units
            FROM grades g
            JOIN course_offerings co ON g.offering_id = co.offering_id AND g.term_code = co.term_code
            JOIN courses c ON co.course_code = c.course_code
            WHERE g.student_id = ? AND g.term_code = ?
            ORDER BY c.course_code
        """, (self.student_id, term_code))

        # پاک کردن جدول و درج مجدد
        self.table.setRowCount(0)

        # پر کردن جدول
        for row_idx, (course_code, offering_id, course_name, grade, units) in enumerate(courses):
            self.table.insertRow(row_idx)

            # کد درس (قابل ویرایش)
            code_item = QTableWidgetItem(course_code)
            code_item.setFlags(code_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, code_item)

            # شماره گروه (offering_id) (قابل ویرایش)
            group_item = QTableWidgetItem(str(offering_id))
            group_item.setFlags(group_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 1, group_item)

            # نام درس (غیرقابل ویرایش، فقط نمایش)
            name_item = QTableWidgetItem(course_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 2, name_item)

            # نمره (قابل ویرایش)
            grade_item = QTableWidgetItem("" if grade is None else str(grade))
            grade_item.setFlags(grade_item.flags() | Qt.ItemFlag.ItemIsEditable)
            grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, grade_item)

            # ستون حذف (دکمه یا علامت)
            del_item = QTableWidgetItem("❌")
            del_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            del_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row_idx, 4, del_item)

        # اضافه کردن یک ردیف خالی برای افزودن درس جدید
        self.add_empty_row()

        # به‌روزرسانی خلاصه
        self.update_summary(term_code)

    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(5):
            item = QTableWidgetItem("")
            if col == 4:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
            else:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)

    def show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        col = index.column()

        menu = QMenu()
        if col == 4 and row < self.table.rowCount() - 1:
            action_delete = menu.addAction("حذف این درس")
            action = menu.exec(self.table.viewport().mapToGlobal(pos))
            if action == action_delete:
                self.delete_course(row)

    def delete_course(self, row):
        course_code = self.table.item(row, 0).text().strip()
        offering_id = self.table.item(row, 1).text().strip()
        term_code = self.term_combo.currentData()

        if not course_code or not offering_id:
            QMessageBox.warning(self, "خطا", "کد درس یا شماره گروه معتبر نیست.")
            return

        try:
            offering_id_int = int(offering_id)
        except:
            QMessageBox.warning(self, "خطا", "شماره گروه باید عدد باشد.")
            return

        # حذف رکورد از grades
        self.execute_db("""
            DELETE FROM grades WHERE student_id=? AND course_code=? AND offering_id=? AND term_code=?
        """, (self.student_id, course_code, offering_id_int, term_code))

        # حذف ردیف از جدول
        self.table.removeRow(row)

        QMessageBox.information(self, "حذف", "درس با موفقیت حذف شد.")
        self.update_summary(term_code)

    def update_summary(self, term_code):
        # محاسبه خلاصه وضعیت دروس (پاس، مردود، مانده، واحد و معدل)
        rows = self.fetch_db("""
            SELECT c.units, g.grade, c.course_code, c.course_name
            FROM grades g
            JOIN course_offerings co ON g.offering_id = co.offering_id AND g.term_code = co.term_code
            JOIN courses c ON co.course_code = c.course_code
            WHERE g.student_id=? AND g.term_code=?
        """, (self.student_id, term_code))

        passed_units = 0
        failed_units = 0
        total_units = 0
        weighted_sum = 0
        weighted_count = 0
        passed_courses = []
        failed_courses = []
        remaining_courses = []

        for units, grade, course_code, course_name in rows:
            if grade is not None:
                total_units += units
                if grade >= 10:
                    passed_units += units
                    passed_courses.append(f"{course_code} - {course_name}")
                    weighted_sum += grade * units
                    weighted_count += units
                else:
                    failed_units += units
                    failed_courses.append(f"{course_code} - {course_name}")
            else:
                remaining_courses.append(f"{course_code} - {course_name}")

        avg_gpa = weighted_sum / weighted_count if weighted_count > 0 else 0

        summary_text = (
            f"<b>نمرات پاس شده:</b> {', '.join(passed_courses) if passed_courses else 'ندارد'}<br>"
            f"<b>نمرات مردود:</b> {', '.join(failed_courses) if failed_courses else 'ندارد'}<br>"
            f"<b>دروس مانده (اخذ نشده یا بدون نمره):</b> {', '.join(remaining_courses) if remaining_courses else 'ندارد'}<br>"
            f"<b>مجموع واحد پاس شده:</b> {passed_units}<br>"
            f"<b>مجموع واحد مردود:</b> {failed_units}<br>"
            f"<b>معدل ترم:</b> {avg_gpa:.2f}"
        )
        self.summary_label.setText(summary_text)

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def save_changes(self):
        term_code = self.term_combo.currentData()
        if not self.student_id or not term_code:
            return

        for row in range(self.table.rowCount()):
            course_code = self.table.item(row, 0).text().strip()
            offering_id = self.table.item(row, 1).text().strip()
            grade_item = self.table.item(row, 3)
            grade_text = grade_item.text().strip() if grade_item else ""

            if course_code == "" and offering_id == "" and grade_text == "":
                continue  # ردیف خالی برای افزودن

            # اعتبارسنجی
            if not course_code or not offering_id:
                continue  # نادیده گرفتن ردیف ناقص

            try:
                offering_id_int = int(offering_id)
            except:
                QMessageBox.warning(self, "خطا", f"شماره گروه باید عدد باشد (ردیف {row+1}).")
                return

            if grade_text == "":
                grade = None
            else:
                try:
                    grade = float(grade_text)
                    if grade < 0 or grade > 20:
                        QMessageBox.warning(self, "خطا", f"نمره باید بین 0 تا 20 باشد (ردیف {row+1}).")
                        return
                except:
                    QMessageBox.warning(self, "خطا", f"نمره نامعتبر است (ردیف {row+1}).")
                    return

            # چک وجود درس در دوره ارائه
            co = self.fetch_db("""
                SELECT 1 FROM course_offerings
                WHERE offering_id=? AND term_code=? AND course_code=?
            """, (offering_id_int, term_code, course_code))
            if not co:
                QMessageBox.warning(self, "خطا", f"درس یا گروه ارائه معتبر نیست (ردیف {row+1}).")
                return

            # درج یا آپدیت
            self.execute_db("""
                INSERT INTO grades (student_id, offering_id, term_code, grade)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id, offering_id, term_code) DO UPDATE SET grade=excluded.grade
            """, (self.student_id, offering_id_int, term_code, grade))

        QMessageBox.information(self, "ثبت تغییرات", "تغییرات با موفقیت ذخیره شد.")
        # بارگذاری مجدد برای تازه‌سازی نام درس
        self.load_courses(term_code)

    def closeEvent(self, event):
        # هنگام بسته شدن پنجره تغییرات رو ذخیره کن (می‌تونی حذف کنی اگر دوست نداری)
        self.save_changes()
        event.accept()



class CourseGradeEntry(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود نمرات")
        self.resize(900, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # کادر انتخاب نیمسال
        term_layout = QHBoxLayout()
        term_layout.addWidget(QLabel("انتخاب نیمسال:"))
        self.term_combo = QComboBox()
        term_layout.addWidget(self.term_combo)
        layout.addLayout(term_layout)

        self.load_terms()

        # ورودی کد درس و شماره گروه ارائه
        form_layout = QFormLayout()
        self.course_code_input = QLineEdit()
        self.offering_id_input = QLineEdit()
        form_layout.addRow("کد درس:", self.course_code_input)
        form_layout.addRow("شماره گروه ارائه:", self.offering_id_input)
        layout.addLayout(form_layout)

        self.load_course_btn = QPushButton("بارگذاری اطلاعات درس")
        self.load_course_btn.clicked.connect(self.load_course_info)
        layout.addWidget(self.load_course_btn)

        self.course_info_label = QLabel("اطلاعات درس: -")
        layout.addWidget(self.course_info_label)

        # جدول دانشجویان و نمرات
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["شماره دانشجویی", "نام دانشجو", "نمره"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        layout.addWidget(self.table)

        # دکمه ثبت نهایی نمرات
        self.finalize_btn = QPushButton("ثبت نهایی")
        self.finalize_btn.clicked.connect(self.finalize_grades)
        layout.addWidget(self.finalize_btn)

        self.offering_id = None
        self.current_course_info = None
        self.term_code = None

    def load_terms(self):
        terms = self.fetch_db("SELECT term_code, term_name FROM terms ORDER BY term_code DESC")
        self.term_combo.clear()
        for term_code, term_name in terms:
            self.term_combo.addItem(f"{term_name} ({term_code})", term_code)

    def get_selected_term(self):
        return self.term_combo.currentData()

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_course_info(self):
        self.term_code = self.get_selected_term()
        if not self.term_code:
            QMessageBox.warning(self, "خطا", "لطفاً نیمسال را انتخاب کنید.")
            return

        course_code = self.course_code_input.text().strip()
        offering_id_str = self.offering_id_input.text().strip()

        if not course_code or not offering_id_str.isdigit():
            QMessageBox.warning(self, "خطا", "کد درس و شماره گروه ارائه معتبر نیست.")
            return

        offering_id = int(offering_id_str)

        rows = self.fetch_db("""
            SELECT co.offering_id, c.course_name, t.fullname, c.passing_grade
            FROM course_offerings co
            JOIN courses c ON co.course_code = c.course_code
            JOIN teachers t ON co.professor_code = t.personnel_code
            WHERE co.offering_id = ? AND co.term_code = ?
        """, (offering_id, self.term_code))

        if not rows:
            QMessageBox.warning(self, "خطا", "گروه ارائه یا نیمسال انتخاب شده یافت نشد.")
            self.course_info_label.setText("اطلاعات درس: -")
            self.table.setRowCount(0)
            self.current_course_info = None
            return

        self.offering_id = rows[0][0]
        course_name = rows[0][1]
        professor_name = rows[0][2]
        passing_grade = rows[0][3]

        self.course_info_label.setText(
            f"<b>درس:</b> {course_name} &nbsp;&nbsp; <b>استاد:</b> {professor_name} &nbsp;&nbsp; <b>حداقل قبولی:</b> {passing_grade}"
        )

        students = self.fetch_db("""
            SELECT s.student_id, s.fullname
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            WHERE e.offering_id = ? AND e.term_code = ?
        """, (self.offering_id, self.term_code))

        self.table.setRowCount(len(students))

        for row_idx, (student_id, fullname) in enumerate(students):
            self.table.setItem(row_idx, 0, QTableWidgetItem(student_id))
            self.table.setItem(row_idx, 1, QTableWidgetItem(fullname))

            grade_rows = self.fetch_db("""
                SELECT grade FROM grades
                WHERE student_id=? AND offering_id=? AND term_code=?
            """, (student_id, self.offering_id, self.term_code))

            grade_text = str(grade_rows[0][0]) if grade_rows and grade_rows[0][0] is not None else ""
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setFlags(grade_item.flags() | Qt.ItemFlag.ItemIsEditable)
            grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, grade_item)

    def finalize_grades(self):
        if not self.offering_id:
            QMessageBox.warning(self, "خطا", "ابتدا درس را بارگذاری کنید.")
            return

        passing_grade_rows = self.fetch_db("""
            SELECT c.passing_grade FROM course_offerings co
            JOIN courses c ON co.course_code = c.course_code
            WHERE co.offering_id = ?
        """, (self.offering_id,))

        if not passing_grade_rows:
            QMessageBox.warning(self, "خطا", "امکان دریافت حداقل قبولی نیست.")
            return

        passing_grade = passing_grade_rows[0][0]

        for row_idx in range(self.table.rowCount()):
            student_id = self.table.item(row_idx, 0).text()
            grade_item = self.table.item(row_idx, 2)
            grade_text = grade_item.text().strip() if grade_item else ""
            if grade_text == "":
                grade = None
            else:
                try:
                    grade = float(grade_text)
                except ValueError:
                    QMessageBox.warning(self, "خطا", f"نمره وارد شده برای دانشجو {student_id} معتبر نیست.")
                    return

            self.execute_db("""
                INSERT INTO grades (student_id, offering_id, term_code, grade)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id, offering_id, term_code) DO UPDATE SET grade=excluded.grade
            """, (student_id, self.offering_id, self.term_code, grade))

        QMessageBox.information(self, "ثبت نمرات", "نمرات با موفقیت ثبت شدند.")

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.finalize_btn.setEnabled(False)



class CourseSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("انتخاب واحد دانشجو")
        self.resize(900, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- نیمسال جاری ---
        self.current_term_code = self.get_current_term()
        if not self.current_term_code:
            QMessageBox.critical(self, "خطا", "نیمسال جاری در سیستم تعریف نشده است.")
            sys.exit()

        # --- بخش دانشجو ---
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel("شماره دانشجویی:"))
        self.student_id_input = QLineEdit()
        student_layout.addWidget(self.student_id_input)
        self.student_name_label = QLabel("نام دانشجو: - ")
        student_layout.addWidget(self.student_name_label)
        layout.addLayout(student_layout)

        self.student_id_input.editingFinished.connect(self.load_student_info)

        # --- تیک باکس ها برای تنظیمات ---
        checks_layout = QHBoxLayout()
        self.chk_max_14 = QCheckBox("مجاز به انتخاب حداکثر 14 واحد")
        self.chk_max_24 = QCheckBox("مجاز به انتخاب 24 واحد")
        self.chk_check_conflict = QCheckBox("چک تداخل")
        self.chk_check_capacity = QCheckBox("چک ظرفیت")
        checks_layout.addWidget(self.chk_max_14)
        checks_layout.addWidget(self.chk_max_24)
        checks_layout.addWidget(self.chk_check_conflict)
        checks_layout.addWidget(self.chk_check_capacity)
        layout.addLayout(checks_layout)

        # --- ورودی درس و گروه ارائه ---
        form_layout = QFormLayout()
        self.course_code_input = QLineEdit()
        self.offering_id_input = QLineEdit()
        form_layout.addRow("کد درس:", self.course_code_input)
        form_layout.addRow("شماره گروه ارائه:", self.offering_id_input)
        layout.addLayout(form_layout)

        # دکمه گرفتن اطلاعات درس
        self.load_course_btn = QPushButton("بارگذاری اطلاعات درس")
        layout.addWidget(self.load_course_btn)
        self.load_course_btn.clicked.connect(self.load_course_info)

        # نمایش اطلاعات درس بارگذاری شده
        self.course_info_label = QLabel("اطلاعات درس: -")
        layout.addWidget(self.course_info_label)

        # --- جدول دروس انتخاب شده ---

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "کد درس", "نام درس", "نام استاد", "ظرفیت باقیمانده",
            "روز برگزاری", "ساعت شروع", "تعداد واحد", "حذف"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    

        # دکمه اخذ درس
        self.add_course_btn = QPushButton("اخذ درس")
        layout.addWidget(self.add_course_btn)
        self.add_course_btn.clicked.connect(self.add_course_to_selection)

        # نگه داشتن دروس انتخاب شده در حافظه (لیست دیکشنری)
        self.selected_courses = []

        # نگه داشتن آخرین اطلاعات درس بارگذاری شده برای اخذ
        self.current_course_info = None

    def get_current_term(self):
        rows = self.fetch_db("SELECT term_code FROM terms WHERE is_current=1")
        return rows[0][0] if rows else None

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_student_info(self):
        student_id = self.student_id_input.text().strip()
        if not student_id:
            self.student_name_label.setText("نام دانشجو: -")
            self.selected_courses.clear()
            self.table.setRowCount(0)
            self.current_course_info = None
            return

        rows = self.fetch_db("SELECT fullname FROM students WHERE student_id=?", (student_id,))
        if rows:
            self.student_name_label.setText(f"نام دانشجو: {rows[0][0]}")
            self.load_student_enrollments(student_id)
        else:
            self.student_name_label.setText("نام دانشجو: یافت نشد")
            self.selected_courses.clear()
            self.table.setRowCount(0)
            self.current_course_info = None

    def load_student_enrollments(self, student_id):
        # بارگذاری دروس اخذ شده برای این دانشجو و نیمسال جاری
        query = """
        SELECT co.course_code, c.course_name, p.fullname, co.capacity,
               co.day_of_week, co.start_time, c.units, co.offering_id
        FROM enrollments e
        JOIN course_offerings co ON e.offering_id = co.offering_id
        JOIN courses c ON co.course_code = c.course_code
        JOIN teachers p ON co.professor_code = p.personnel_code
        WHERE e.student_id = ? AND e.term_code = ?
        """
        rows = self.fetch_db(query, (student_id, self.current_term_code))
        self.selected_courses.clear()
        self.table.setRowCount(0)
        for row in rows:
            course_code, course_name, professor_name, capacity, day, start_time, units, offering_id = row
            # محاسبه ظرفیت باقیمانده
            enrolled = self.get_enrollment_count(offering_id)
            remaining = capacity - enrolled
            course = {
                "offering_id": offering_id,
                "course_code": course_code,
                "course_name": course_name,
                "professor": professor_name,
                "capacity": capacity,
                "remaining": remaining,
                "day": day,
                "start_time": start_time,
                "units": units,
            }
            self.selected_courses.append(course)
            self.add_course_row(course)

    def load_course_info(self):
        course_code = self.course_code_input.text().strip()
        try:
            offering_id = int(self.offering_id_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "خطا", "شماره گروه ارائه باید عدد باشد.")
            return

        query = """
        SELECT co.course_code, c.course_name, p.fullname, co.capacity, co.day_of_week, co.start_time, c.units
        FROM course_offerings co
        JOIN courses c ON co.course_code = c.course_code
        JOIN teachers p ON co.professor_code = p.personnel_code
        WHERE co.offering_id = ? AND co.course_code = ?
        """
        rows = self.fetch_db(query, (offering_id, course_code))
        if rows:
            course_code, course_name, professor_name, capacity, day, start_time, units = rows[0]
            enrolled = self.get_enrollment_count(offering_id)
            remaining = capacity - enrolled
            self.current_course_info = {
                "offering_id": offering_id,
                "course_code": course_code,
                "course_name": course_name,
                "professor": professor_name,
                "capacity": capacity,
                "remaining": remaining,
                "day": day,
                "start_time": start_time,
                "units": units,
            }
            self.course_info_label.setText(
                f"{course_code} - {course_name} | استاد: {professor_name} | ظرفیت باقیمانده: {remaining} | "
                f"روز: {['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه'][day]} | ساعت شروع: {start_time} | واحد: {units}"
            )
        else:
            QMessageBox.warning(self, "خطا", "ارائه‌ی درس یافت نشد.")
            self.course_info_label.setText("اطلاعات درس: -")
            self.current_course_info = None

    def get_enrollment_count(self, offering_id):
        rows = self.fetch_db("SELECT COUNT(*) FROM enrollments WHERE offering_id=?", (offering_id,))
        return rows[0][0] if rows else 0

    def add_course_to_selection(self):
        if not self.current_course_info:
            QMessageBox.warning(self, "خطا", "ابتدا اطلاعات درس را بارگذاری کنید.")
            return

        if not self.student_id_input.text().strip():
            QMessageBox.warning(self, "خطا", "ابتدا شماره دانشجویی را وارد کنید.")
            return

        # چک ظرفیت
        if self.chk_check_capacity.isChecked():
            if self.current_course_info["remaining"] <= 0:
                QMessageBox.warning(self, "خطا", "ظرفیت این درس تکمیل شده است.")
                return

        # چک تعداد واحد
        max_units = 20
        if self.chk_max_14.isChecked():
            max_units = 14
        elif self.chk_max_24.isChecked():
            max_units = 24

        current_units = sum(c['units'] for c in self.selected_courses)
        if current_units + self.current_course_info["units"] > max_units:
            QMessageBox.warning(self, "خطا", f"حداکثر تعداد واحد مجاز ({max_units}) عبور شده است.")
            return

        # چک تداخل زمانی
        if self.chk_check_conflict.isChecked():
            for c in self.selected_courses:
                if c["day"] == self.current_course_info["day"]:
                    if c["start_time"] == self.current_course_info["start_time"]:
                        QMessageBox.warning(self, "خطا", "تداخل زمانی وجود دارد.")
                        return

        # چک اینکه این درس قبلا اخذ نشده باشه
        for c in self.selected_courses:
            if c["offering_id"] == self.current_course_info["offering_id"]:
                QMessageBox.warning(self, "خطا", "این درس قبلا اخذ شده است.")
                return

        # ثبت انتخاب واحد در دیتابیس
        try:
            self.execute_db(
                "INSERT INTO enrollments (student_id, term_code, offering_id) VALUES (?, ?, ?)",
                (self.student_id_input.text().strip(), self.current_term_code, self.current_course_info["offering_id"])
            )
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطا", "این انتخاب واحد قبلا ثبت شده است.")
            return

        # افزودن به لیست داخلی و جدول
        self.selected_courses.append(self.current_course_info)
        self.add_course_row(self.current_course_info)

        # پاک کردن ورودی‌ها
        self.course_code_input.clear()
        self.offering_id_input.clear()
        self.course_info_label.setText("اطلاعات درس: -")
        self.current_course_info = None

    def add_course_row(self, course):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(course["course_code"]))
        self.table.setItem(row, 1, QTableWidgetItem(course["course_name"]))
        self.table.setItem(row, 2, QTableWidgetItem(course["professor"]))
        self.table.setItem(row, 3, QTableWidgetItem(str(course["remaining"])))
        self.table.setItem(row, 4, QTableWidgetItem(['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه'][course["day"]]))
        self.table.setItem(row, 5, QTableWidgetItem(course["start_time"]))
        self.table.setItem(row, 6, QTableWidgetItem(str(course["units"])))

        # دکمه حذف
        btn_remove = QPushButton("حذف")
        self.table.setCellWidget(row, 7, btn_remove)
        btn_remove.clicked.connect(lambda _, r=row: self.remove_course(r))

    def remove_course(self, row):
        if row < 0 or row >= len(self.selected_courses):
            return
        course = self.selected_courses[row]

        student_id = self.student_id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "خطا", "ابتدا شماره دانشجویی را وارد کنید.")
            return

        # حذف از دیتابیس
        self.execute_db(
            "DELETE FROM enrollments WHERE student_id=? AND term_code=? AND offering_id=?",
            (student_id, self.current_term_code, course["offering_id"])
        )

        # حذف از لیست داخلی و جدول
        self.selected_courses.pop(row)
        self.table.removeRow(row)

        # چون ردیف‌ها جابجا میشن، باید سیگنال حذف هر دکمه رو دوباره به ردیف درست متصل کنیم
        for i in range(self.table.rowCount()):
            btn = self.table.cellWidget(i, 7)
            btn.clicked.disconnect()
            btn.clicked.connect(lambda _, r=i: self.remove_course(r))


class CourseOfferingManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تعریف ارائه دروس")
        self.resize(700, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "کد ارائه", "کد درس", "نام درس", "کد رشته", "نام رشته", "کد ترم", "نام ترم",
            "کد استاد", "نام استاد", "ظرفیت", "روز برگزاری", "ساعت شروع"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.course_combo = QComboBox()
        self.field_combo = QComboBox()
        self.term_combo = QComboBox()
        self.professor_combo = QComboBox()
        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 500)
        self.day_combo = QComboBox()
        self.day_combo.addItems(["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه"])
        self.start_time_input = QLineEdit()
        self.start_time_input.setMaxLength(4)
        self.start_time_input.setPlaceholderText("مثلاً 0800")

        form_layout.addRow("درس:", self.course_combo)
        form_layout.addRow("رشته:", self.field_combo)
        form_layout.addRow("نیمسال:", self.term_combo)
        form_layout.addRow("استاد:", self.professor_combo)
        form_layout.addRow("ظرفیت:", self.capacity_input)
        form_layout.addRow("روز برگزاری:", self.day_combo)
        form_layout.addRow("ساعت شروع:", self.start_time_input)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن ارائه")
        self.edit_btn = QPushButton("ویرایش ارائه")
        self.delete_btn = QPushButton("حذف ارائه")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_offering)
        self.edit_btn.clicked.connect(self.edit_offering)
        self.delete_btn.clicked.connect(self.delete_offering)
        self.table.cellClicked.connect(self.load_selected_offering)

        self.load_combos()
        self.load_offerings()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def load_combos(self):
        self.course_combo.clear()
        courses = self.fetch_db("SELECT course_code, course_name FROM courses")
        for code, name in courses:
            self.course_combo.addItem(f"{code} - {name}", code)

        self.field_combo.clear()
        fields = self.fetch_db("SELECT code, name FROM fields")
        for code, name in fields:
            self.field_combo.addItem(f"{code} - {name}", code)

        self.term_combo.clear()
        terms = self.fetch_db("SELECT term_code, term_name FROM terms")
        for code, name in terms:
            self.term_combo.addItem(f"{code} - {name}", code)

        self.professor_combo.clear()
        professors = self.fetch_db("SELECT personnel_code, fullname FROM teachers")
        for code, name in professors:
            self.professor_combo.addItem(f"{code} - {name}", code)

    def load_offerings(self):
        query = """
        SELECT co.offering_id, co.course_code, c.course_name, co.field_code, f.name,
               co.term_code, t.term_name, co.professor_code, p.fullname,
               co.capacity, co.day_of_week, co.start_time
        FROM course_offerings co
        JOIN courses c ON co.course_code = c.course_code
        JOIN fields f ON co.field_code = f.code
        JOIN terms t ON co.term_code = t.term_code
        JOIN teachers p ON co.professor_code = p.personnel_code
        ORDER BY co.offering_id
        """
        rows = self.fetch_db(query)

        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.clear_inputs()

    def clear_inputs(self):
        self.course_combo.setCurrentIndex(-1)
        self.field_combo.setCurrentIndex(-1)
        self.term_combo.setCurrentIndex(-1)
        self.professor_combo.setCurrentIndex(-1)
        self.capacity_input.setValue(1)
        self.day_combo.setCurrentIndex(0)
        self.start_time_input.clear()
        if hasattr(self, 'current_id'):
            del self.current_id

    def load_selected_offering(self, row, _):
        self.current_id = int(self.table.item(row, 0).text())

        course_code = self.table.item(row, 1).text()
        field_code = self.table.item(row, 3).text()
        term_code = self.table.item(row, 5).text()
        professor_code = self.table.item(row, 7).text()

        self.set_combobox_by_data(self.course_combo, course_code)
        self.set_combobox_by_data(self.field_combo, field_code)
        self.set_combobox_by_data(self.term_combo, term_code)
        self.set_combobox_by_data(self.professor_combo, professor_code)

        self.capacity_input.setValue(int(self.table.item(row, 9).text()))
        self.day_combo.setCurrentIndex(int(self.table.item(row, 10).text()))
        self.start_time_input.setText(self.table.item(row, 11).text())

    def set_combobox_by_data(self, combo, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return

    def add_offering(self):
        course_code = self.course_combo.currentData()
        field_code = self.field_combo.currentData()
        term_code = self.term_combo.currentData()
        professor_code = self.professor_combo.currentData()
        capacity = self.capacity_input.value()
        day_of_week = self.day_combo.currentIndex()
        start_time = self.start_time_input.text().strip()

        if not all([course_code, field_code, term_code, professor_code]) or len(start_time) != 4 or not start_time.isdigit():
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را به درستی پر کنید و ساعت شروع را به صورت 4 رقم وارد کنید.")
            return

        query = """
        INSERT INTO course_offerings
        (course_code, field_code, term_code, professor_code, capacity, day_of_week, start_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_db(query, (course_code, field_code, term_code, professor_code, capacity, day_of_week, start_time))
        QMessageBox.information(self, "موفقیت", "ارائه درس با موفقیت اضافه شد.")
        self.load_offerings()

    def edit_offering(self):
        if not hasattr(self, "current_id"):
            QMessageBox.warning(self, "خطا", "لطفاً یک ارائه را از جدول انتخاب کنید.")
            return

        course_code = self.course_combo.currentData()
        field_code = self.field_combo.currentData()
        term_code = self.term_combo.currentData()
        professor_code = self.professor_combo.currentData()
        capacity = self.capacity_input.value()
        day_of_week = self.day_combo.currentIndex()
        start_time = self.start_time_input.text().strip()

        if not all([course_code, field_code, term_code, professor_code]) or len(start_time) != 4 or not start_time.isdigit():
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را به درستی پر کنید و ساعت شروع را به صورت 4 رقم وارد کنید.")
            return

        query = """
        UPDATE course_offerings
        SET course_code=?, field_code=?, term_code=?, professor_code=?, capacity=?, day_of_week=?, start_time=?
        WHERE offering_id=?
        """
        self.execute_db(query, (course_code, field_code, term_code, professor_code, capacity, day_of_week, start_time, self.current_id))
        QMessageBox.information(self, "موفقیت", "ارائه درس با موفقیت ویرایش شد.")
        self.load_offerings()

    def delete_offering(self):
        if not hasattr(self, "current_id"):
            QMessageBox.warning(self, "خطا", "لطفاً یک ارائه را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف ارائه",
            "آیا از حذف این ارائه مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM course_offerings WHERE offering_id=?"
            self.execute_db(query, (self.current_id,))
            QMessageBox.information(self, "موفقیت", "ارائه درس با موفقیت حذف شد.")
            self.load_offerings()




class TermsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تعریف ترم‌ها")
        self.resize(600, 350)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["کد ترم", "نام ترم", "ترم جاری"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.term_code_input = QLineEdit()
        self.term_name_input = QLineEdit()
        self.is_current_checkbox = QCheckBox("ترم جاری")

        form_layout.addRow("کد ترم:", self.term_code_input)
        form_layout.addRow("نام ترم:", self.term_name_input)
        form_layout.addRow("", self.is_current_checkbox)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن ترم")
        self.edit_btn = QPushButton("ویرایش ترم")
        self.delete_btn = QPushButton("حذف ترم")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_term)
        self.edit_btn.clicked.connect(self.edit_term)
        self.delete_btn.clicked.connect(self.delete_term)
        self.table.cellClicked.connect(self.load_selected_term)

        self.load_terms()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_terms(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT term_code, term_name, is_current FROM terms ORDER BY term_code")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            term_code, term_name, is_current = row_data
            self.table.setItem(row_idx, 0, QTableWidgetItem(term_code))
            self.table.setItem(row_idx, 1, QTableWidgetItem(term_name))

            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_state = Qt.CheckState.Checked if is_current else Qt.CheckState.Unchecked
            chk_item.setCheckState(chk_state)
            self.table.setItem(row_idx, 2, chk_item)

        self.clear_inputs()

    def clear_inputs(self):
        self.term_code_input.setEnabled(True)
        self.term_code_input.clear()
        self.term_name_input.clear()
        self.is_current_checkbox.setChecked(False)

    def load_selected_term(self, row, _column):
        self.term_code_input.setText(self.table.item(row, 0).text())
        self.term_name_input.setText(self.table.item(row, 1).text())
        is_current = self.table.item(row, 2).checkState() == Qt.CheckState.Checked
        self.is_current_checkbox.setChecked(is_current)
        self.term_code_input.setEnabled(False)

    def add_term(self):
        term_code = self.term_code_input.text().strip()
        term_name = self.term_name_input.text().strip()
        is_current = 1 if self.is_current_checkbox.isChecked() else 0

        if not term_code or not term_name:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM terms WHERE term_code=?", (term_code,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "خطا", "کد ترم تکراری است.")
            conn.close()
            return

        if is_current:
            # اگر تیک ترم جاری زده شده، اول همه رو صفر کن
            cursor.execute("UPDATE terms SET is_current=0")

        cursor.execute("INSERT INTO terms (term_code, term_name, is_current) VALUES (?, ?, ?)",
                       (term_code, term_name, is_current))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "موفقیت", "ترم با موفقیت اضافه شد.")
        self.load_terms()

    def edit_term(self):
        term_code = self.term_code_input.text().strip()
        term_name = self.term_name_input.text().strip()
        is_current = 1 if self.is_current_checkbox.isChecked() else 0

        if not term_code or not term_name:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if is_current:
            cursor.execute("UPDATE terms SET is_current=0")

        cursor.execute("""
            UPDATE terms SET term_name=?, is_current=?
            WHERE term_code=?
        """, (term_name, is_current, term_code))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "موفقیت", "ترم با موفقیت ویرایش شد.")
        self.load_terms()

    def delete_term(self):
        term_code = self.term_code_input.text().strip()
        if not term_code:
            QMessageBox.warning(self, "خطا", "لطفاً یک ترم را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف ترم",
            f"آیا از حذف ترم با کد '{term_code}' مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM terms WHERE term_code=?", (term_code,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "موفقیت", "ترم با موفقیت حذف شد.")
            self.load_terms()



class CoursesManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تعریف دروس")
        self.resize(750, 420)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "کد درس", "کد رشته", "نام رشته", "نام درس", "واحد", "حداقل نمره قبولی"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.course_code_input = QLineEdit()
        self.field_code_input = QLineEdit()
        self.field_name_label = QLabel("-")
        self.course_name_input = QLineEdit()
        self.units_input = QLineEdit()
        self.passing_grade_input = QLineEdit()

        form_layout.addRow("کد درس:", self.course_code_input)

        field_code_hbox = QHBoxLayout()
        field_code_hbox.addWidget(self.field_code_input)
        field_code_hbox.addWidget(QLabel("نام رشته:"))
        field_code_hbox.addWidget(self.field_name_label)
        form_layout.addRow("کد رشته:", field_code_hbox)

        form_layout.addRow("نام درس:", self.course_name_input)
        form_layout.addRow("واحد:", self.units_input)
        form_layout.addRow("حداقل نمره قبولی:", self.passing_grade_input)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن درس")
        self.edit_btn = QPushButton("ویرایش درس")
        self.delete_btn = QPushButton("حذف درس")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_course)
        self.edit_btn.clicked.connect(self.edit_course)
        self.delete_btn.clicked.connect(self.delete_course)
        self.table.cellClicked.connect(self.load_selected_course)
        self.field_code_input.textChanged.connect(self.update_field_name)

        self.load_courses()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_courses(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_code, c.field_code, f.name, c.course_name, c.units, c.passing_grade
            FROM courses c LEFT JOIN fields f ON c.field_code = f.code
            ORDER BY c.course_code
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.clear_inputs()

    def clear_inputs(self):
        self.course_code_input.setEnabled(True)
        self.course_code_input.clear()
        self.field_code_input.clear()
        self.field_name_label.setText("-")
        self.course_name_input.clear()
        self.units_input.clear()
        self.passing_grade_input.clear()

    def load_selected_course(self, row, _column):
        self.course_code_input.setText(self.table.item(row, 0).text())
        self.field_code_input.setText(self.table.item(row, 1).text())
        self.course_name_input.setText(self.table.item(row, 3).text())
        self.units_input.setText(self.table.item(row, 4).text())
        self.passing_grade_input.setText(self.table.item(row, 5).text())
        self.course_code_input.setEnabled(False)
        self.update_field_name()

    def update_field_name(self):
        code = self.field_code_input.text().strip()
        if not code:
            self.field_name_label.setText("-")
            return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM fields WHERE code=?", (code,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.field_name_label.setText(row[0])
        else:
            self.field_name_label.setText("کد رشته نامعتبر است")

    def add_course(self):
        course_code = self.course_code_input.text().strip()
        field_code = self.field_code_input.text().strip()
        course_name = self.course_name_input.text().strip()
        units = self.units_input.text().strip()
        passing_grade = self.passing_grade_input.text().strip()

        if not (course_code and field_code and course_name and units.isdigit() and passing_grade.isdigit()):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        # بررسی وجود رشته
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fields WHERE code=?", (field_code,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "خطا", "کد رشته وارد شده معتبر نیست.")
            conn.close()
            return
        conn.close()

        try:
            self.execute_db("""
                INSERT INTO courses (course_code, field_code, course_name, units, passing_grade)
                VALUES (?, ?, ?, ?, ?)
            """, (course_code, field_code, course_name, int(units), int(passing_grade)))
            QMessageBox.information(self, "موفقیت", "درس با موفقیت اضافه شد.")
            self.load_courses()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطا", "کد درس تکراری است.")

    def edit_course(self):
        course_code = self.course_code_input.text().strip()
        field_code = self.field_code_input.text().strip()
        course_name = self.course_name_input.text().strip()
        units = self.units_input.text().strip()
        passing_grade = self.passing_grade_input.text().strip()

        if not (course_code and field_code and course_name and units.isdigit() and passing_grade.isdigit()):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        # بررسی وجود رشته
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fields WHERE code=?", (field_code,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "خطا", "کد رشته وارد شده معتبر نیست.")
            conn.close()
            return
        conn.close()

        self.execute_db("""
            UPDATE courses SET field_code=?, course_name=?, units=?, passing_grade=?
            WHERE course_code=?
        """, (field_code, course_name, int(units), int(passing_grade), course_code))
        QMessageBox.information(self, "موفقیت", "درس با موفقیت ویرایش شد.")
        self.load_courses()

    def delete_course(self):
        course_code = self.course_code_input.text().strip()
        if not course_code:
            QMessageBox.warning(self, "خطا", "لطفاً یک درس را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف درس",
            f"آیا از حذف درس با کد '{course_code}' مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.execute_db("DELETE FROM courses WHERE course_code=?", (course_code,))
            QMessageBox.information(self, "موفقیت", "درس با موفقیت حذف شد.")
            self.load_courses()


class TeachersManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدیریت اساتید")
        self.resize(700, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "کد پرسنلی", "کد ملی", "نام و نام خانوادگی", "مرتبه علمی"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.personnel_code_input = QLineEdit()
        self.national_code_input = QLineEdit()
        self.fullname_input = QLineEdit()
        self.academic_rank_input = QLineEdit()

        form_layout.addRow("کد پرسنلی:", self.personnel_code_input)
        form_layout.addRow("کد ملی:", self.national_code_input)
        form_layout.addRow("نام و نام خانوادگی:", self.fullname_input)
        form_layout.addRow("مرتبه علمی:", self.academic_rank_input)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن استاد")
        self.edit_btn = QPushButton("ویرایش استاد")
        self.delete_btn = QPushButton("حذف استاد")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_teacher)
        self.edit_btn.clicked.connect(self.edit_teacher)
        self.delete_btn.clicked.connect(self.delete_teacher)
        self.table.cellClicked.connect(self.load_selected_teacher)

        self.load_teachers()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_teachers(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT personnel_code, national_code, fullname, academic_rank FROM teachers ORDER BY personnel_code")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.clear_inputs()

    def clear_inputs(self):
        self.personnel_code_input.setEnabled(True)
        self.personnel_code_input.clear()
        self.national_code_input.clear()
        self.fullname_input.clear()
        self.academic_rank_input.clear()

    def load_selected_teacher(self, row, _column):
        self.personnel_code_input.setText(self.table.item(row, 0).text())
        self.national_code_input.setText(self.table.item(row, 1).text())
        self.fullname_input.setText(self.table.item(row, 2).text())
        self.academic_rank_input.setText(self.table.item(row, 3).text())
        self.personnel_code_input.setEnabled(False)

    def add_teacher(self):
        personnel_code = self.personnel_code_input.text().strip()
        national_code = self.national_code_input.text().strip()
        fullname = self.fullname_input.text().strip()
        academic_rank = self.academic_rank_input.text().strip()

        if not (personnel_code and national_code and fullname and academic_rank):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        try:
            self.execute_db("""
                INSERT INTO teachers (personnel_code, national_code, fullname, academic_rank)
                VALUES (?, ?, ?, ?)
            """, (personnel_code, national_code, fullname, academic_rank))
            QMessageBox.information(self, "موفقیت", "استاد با موفقیت اضافه شد.")
            self.load_teachers()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطا", "کد پرسنلی تکراری است.")

    def edit_teacher(self):
        personnel_code = self.personnel_code_input.text().strip()
        national_code = self.national_code_input.text().strip()
        fullname = self.fullname_input.text().strip()
        academic_rank = self.academic_rank_input.text().strip()

        if not (personnel_code and national_code and fullname and academic_rank):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        self.execute_db("""
            UPDATE teachers SET national_code=?, fullname=?, academic_rank=?
            WHERE personnel_code=?
        """, (national_code, fullname, academic_rank, personnel_code))
        QMessageBox.information(self, "موفقیت", "استاد با موفقیت ویرایش شد.")
        self.load_teachers()

    def delete_teacher(self):
        personnel_code = self.personnel_code_input.text().strip()
        if not personnel_code:
            QMessageBox.warning(self, "خطا", "لطفاً یک استاد را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف استاد",
            f"آیا از حذف استاد با کد پرسنلی '{personnel_code}' مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.execute_db("DELETE FROM teachers WHERE personnel_code=?", (personnel_code,))
            QMessageBox.information(self, "موفقیت", "استاد با موفقیت حذف شد.")
            self.load_teachers()



class StudentsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدیریت دانشجویان")
        self.resize(800, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "شماره دانشجویی", "کد ملی", "نام و نام خانوادگی", 
            "کد رشته تحصیلی", "نام رشته", "سال ورودی", "نیم‌سال ورودی"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.student_id_input = QLineEdit()
        self.national_code_input = QLineEdit()
        self.fullname_input = QLineEdit()
        self.field_code_input = QLineEdit()
        self.field_name_label = QLabel("-")
        self.year_input = QLineEdit()
        self.semester_input = QLineEdit()
        self.semester_text_label = QLabel("-")

        form_layout.addRow("شماره دانشجویی:", self.student_id_input)
        form_layout.addRow("کد ملی:", self.national_code_input)
        form_layout.addRow("نام و نام خانوادگی:", self.fullname_input)

        field_code_hbox = QHBoxLayout()
        field_code_hbox.addWidget(self.field_code_input)
        field_code_hbox.addWidget(QLabel("نام رشته:"))
        field_code_hbox.addWidget(self.field_name_label)
        form_layout.addRow("کد رشته تحصیلی:", field_code_hbox)

        form_layout.addRow("سال ورودی:", self.year_input)

        semester_hbox = QHBoxLayout()
        semester_hbox.addWidget(self.semester_input)
        semester_hbox.addWidget(QLabel("توضیح:"))
        semester_hbox.addWidget(self.semester_text_label)
        form_layout.addRow("نیم‌سال ورودی:", semester_hbox)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن دانشجو")
        self.edit_btn = QPushButton("ویرایش دانشجو")
        self.delete_btn = QPushButton("حذف دانشجو")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_student)
        self.edit_btn.clicked.connect(self.edit_student)
        self.delete_btn.clicked.connect(self.delete_student)
        self.table.cellClicked.connect(self.load_selected_student)
        self.field_code_input.textChanged.connect(self.update_field_name)
        self.semester_input.textChanged.connect(self.update_semester_text)

        self.load_students()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_students(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.national_code, s.fullname, s.field_code, f.name, s.entry_year, s.entry_semester 
            FROM students s LEFT JOIN fields f ON s.field_code = f.code
            ORDER BY s.student_id
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                if col_idx == 6:  # entry_semester
                    value = "نیمسال اول" if value == 1 else ("نیمسال دوم" if value == 2 else "-")
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.clear_inputs()

    def clear_inputs(self):
        self.student_id_input.setEnabled(True)
        self.student_id_input.clear()
        self.national_code_input.clear()
        self.fullname_input.clear()
        self.field_code_input.clear()
        self.field_name_label.setText("-")
        self.year_input.clear()
        self.semester_input.clear()
        self.semester_text_label.setText("-")

    def load_selected_student(self, row, _column):
        self.student_id_input.setText(self.table.item(row, 0).text())
        self.national_code_input.setText(self.table.item(row, 1).text())
        self.fullname_input.setText(self.table.item(row, 2).text())
        self.field_code_input.setText(self.table.item(row, 3).text())
        self.year_input.setText(self.table.item(row, 5).text())

        semester_text = self.table.item(row, 6).text()
        semester_num = 1 if semester_text == "نیمسال اول" else 2 if semester_text == "نیمسال دوم" else ""
        self.semester_input.setText(str(semester_num))
        self.semester_text_label.setText(semester_text)

        self.student_id_input.setEnabled(False)
        self.update_field_name()

    def update_field_name(self):
        code = self.field_code_input.text().strip()
        if not code:
            self.field_name_label.setText("-")
            return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM fields WHERE code=?", (code,))
        row = cursor.fetchone()
        conn.close()
        if row:
            self.field_name_label.setText(row[0])
        else:
            self.field_name_label.setText("کد رشته نامعتبر است")

    def update_semester_text(self):
        val = self.semester_input.text().strip()
        if val == "1":
            self.semester_text_label.setText("نیمسال اول")
        elif val == "2":
            self.semester_text_label.setText("نیمسال دوم")
        else:
            self.semester_text_label.setText("-")

    def add_student(self):
        student_id = self.student_id_input.text().strip()
        national_code = self.national_code_input.text().strip()
        fullname = self.fullname_input.text().strip()
        field_code = self.field_code_input.text().strip()
        year = self.year_input.text().strip()
        semester = self.semester_input.text().strip()

        if not (student_id and national_code and fullname and field_code and year.isdigit() and semester in ("1","2")):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        # بررسی وجود رشته
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fields WHERE code=?", (field_code,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "خطا", "کد رشته وارد شده معتبر نیست.")
            conn.close()
            return
        conn.close()

        try:
            self.execute_db("""
                INSERT INTO students (student_id, national_code, fullname, field_code, entry_year, entry_semester)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, national_code, fullname, field_code, int(year), int(semester)))
            QMessageBox.information(self, "موفقیت", "دانشجو با موفقیت اضافه شد.")
            self.load_students()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطا", "شماره دانشجویی تکراری است.")

    def edit_student(self):
        student_id = self.student_id_input.text().strip()
        national_code = self.national_code_input.text().strip()
        fullname = self.fullname_input.text().strip()
        field_code = self.field_code_input.text().strip()
        year = self.year_input.text().strip()
        semester = self.semester_input.text().strip()

        if not (student_id and national_code and fullname and field_code and year.isdigit() and semester in ("1","2")):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        # بررسی وجود رشته
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fields WHERE code=?", (field_code,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "خطا", "کد رشته وارد شده معتبر نیست.")
            conn.close()
            return
        conn.close()

        self.execute_db("""
            UPDATE students SET national_code=?, fullname=?, field_code=?, entry_year=?, entry_semester=?
            WHERE student_id=?
        """, (national_code, fullname, field_code, int(year), int(semester), student_id))
        QMessageBox.information(self, "موفقیت", "دانشجو با موفقیت ویرایش شد.")
        self.load_students()

    def delete_student(self):
        student_id = self.student_id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک دانشجو را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف دانشجو",
            f"آیا از حذف دانشجو با شماره '{student_id}' مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.execute_db("DELETE FROM students WHERE student_id=?", (student_id,))
            QMessageBox.information(self, "موفقیت", "دانشجو با موفقیت حذف شد.")
            self.load_students()



class FieldsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مدیریت رشته‌های تحصیلی")
        self.resize(700, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["کد رشته", "نام رشته", "تعداد واحد کل", "تعداد ترم مجاز"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        form_layout = QFormLayout()

        self.code_input = QLineEdit()
        self.name_input = QLineEdit()
        self.units_input = QLineEdit()
        self.semesters_input = QLineEdit()

        form_layout.addRow("کد رشته:", self.code_input)
        form_layout.addRow("نام رشته:", self.name_input)
        form_layout.addRow("تعداد واحد کل:", self.units_input)
        form_layout.addRow("تعداد ترم مجاز:", self.semesters_input)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("افزودن رشته")
        self.edit_btn = QPushButton("ویرایش رشته")
        self.delete_btn = QPushButton("حذف رشته")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_field)
        self.edit_btn.clicked.connect(self.edit_field)
        self.delete_btn.clicked.connect(self.delete_field)
        self.table.cellClicked.connect(self.load_selected_field)

        self.load_fields()

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def load_fields(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fields ORDER BY code")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.clear_inputs()

    def clear_inputs(self):
        self.code_input.setEnabled(True)
        self.code_input.clear()
        self.name_input.clear()
        self.units_input.clear()
        self.semesters_input.clear()

    def load_selected_field(self, row, _column):
        self.code_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.units_input.setText(self.table.item(row, 2).text())
        self.semesters_input.setText(self.table.item(row, 3).text())
        self.code_input.setEnabled(False)

    def add_field(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        units = self.units_input.text().strip()
        semesters = self.semesters_input.text().strip()

        if not (code and name and units.isdigit() and semesters.isdigit()):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        try:
            self.execute_db(
                "INSERT INTO fields (code, name, total_units, max_semesters) VALUES (?, ?, ?, ?)",
                (code, name, int(units), int(semesters))
            )
            QMessageBox.information(self, "موفقیت", "رشته با موفقیت اضافه شد.")
            self.load_fields()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "خطا", "کد رشته تکراری است. لطفاً کد دیگری وارد کنید.")

    def edit_field(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        units = self.units_input.text().strip()
        semesters = self.semesters_input.text().strip()

        if not (code and name and units.isdigit() and semesters.isdigit()):
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را به درستی پر کنید.")
            return

        self.execute_db(
            "UPDATE fields SET name=?, total_units=?, max_semesters=? WHERE code=?",
            (name, int(units), int(semesters), code)
        )
        QMessageBox.information(self, "موفقیت", "رشته با موفقیت ویرایش شد.")
        self.load_fields()

    def delete_field(self):
        code = self.code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "خطا", "لطفاً یک رشته را از جدول انتخاب کنید.")
            return

        ret = QMessageBox.question(
            self, "حذف رشته",
            f"آیا از حذف رشته با کد '{code}' مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.execute_db("DELETE FROM fields WHERE code=?", (code,))
            QMessageBox.information(self, "موفقیت", "رشته با موفقیت حذف شد.")
            self.load_fields()

VALID_USERNAME = "0150521308"
VALID_PASSWORD = "88116040"
USER_FULLNAME = "محمدنیما گنج خانی"

class LoginWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("صفحه ورود")

        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("نام کاربری:", self.username_input)
        layout.addRow("رمز عبور:", self.password_input)

        self.login_btn = QPushButton("ورود")
        self.login_btn.clicked.connect(self.check_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            self.username_input.clear()
            self.password_input.clear()
            self.stacked_widget.setCurrentIndex(1)  # رفتن به داشبورد
        else:
            QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("داشبورد مسئول آموزش")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(f"سلام {USER_FULLNAME}")
        layout.addWidget(self.label)

        self.fields_manager = FieldsManager()
        self.students_manager = StudentsManager()
        self.teachers_manager = TeachersManager()
        self.courses_manager = CoursesManager()
        self.terms_manager = TermsManager()
        self.course_offering_manager = CourseOfferingManager()
        self.course_selection = CourseSelection()
        self.course_grade_entry = CourseGradeEntry()
        self.Student_Record_Viewer = StudentRecordViewer()





        buttons = {
            "رشته‌های تحصیلی": self.open_fields_manager,
            "دانشجویان": self.open_students_manager,
            "اساتید": self.open_teachers_manager,
            "تعریف دروس": self.open_courses_manager,
            "تعریف ترم": self.open_terms_manager,
            "تعریف ارائه دروس در ترم": self.open_course_offering_manager,
            "ورود نمرات": self.open_course_grade_entry,
            "مشاهده و ویرایش سوابق تحصیلی": self.open_Student_Record_Viewer,
            "انتخاب واحد دانشجو": self.open_course_selection,
            "چاپ لیست حضورغیاب": self.not_implemented,
      }

        for text, handler in buttons.items():
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text, h=handler: h(t))
            layout.addWidget(btn)


    def open_Student_Record_Viewer(self, _):
        self.Student_Record_Viewer.show()
        self.Student_Record_Viewer.raise_()
        self.Student_Record_Viewer.activateWindow()

    def open_fields_manager(self, _):
        self.fields_manager.show()
        self.fields_manager.raise_()
        self.fields_manager.activateWindow()

    def open_course_grade_entry(self, _):
        self.course_grade_entry.show()
        self.course_grade_entry.raise_()
        self.course_grade_entry.activateWindow()

    def open_students_manager(self, _):
       self.students_manager.show()
       self.students_manager.raise_()
       self.students_manager.activateWindow()

    def open_teachers_manager(self, _):
       self.teachers_manager.show()
       self.teachers_manager.raise_()
       self.teachers_manager.activateWindow()

    def open_courses_manager(self, _):
       self.courses_manager.show()
       self.courses_manager.raise_()
       self.courses_manager.activateWindow()

    def open_terms_manager(self, _):
       self.terms_manager.show()
       self.terms_manager.raise_()
       self.terms_manager.activateWindow()

    def open_course_offering_manager(self, _):
       self.course_offering_manager.show()
       self.course_offering_manager.raise_()
       self.course_offering_manager.activateWindow()

    def open_course_selection(self, name):
       self.course_selection.show()
       self.course_selection.raise_()
       self.course_selection.activateWindow()
    
    def not_implemented(self, name):
        QMessageBox.information(self, "در دست ساخت", f"قابلیت '{name}' هنوز پیاده‌سازی نشده است.")

if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    login = LoginWindow(stacked_widget)
    dashboard = Dashboard()

    stacked_widget.addWidget(login)
    stacked_widget.addWidget(dashboard)
    stacked_widget.setFixedSize(600, 550)
    stacked_widget.show()

    sys.exit(app.exec())
