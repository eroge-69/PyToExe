import sys
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QScrollArea, QSizePolicy, QLineEdit, QTextEdit,
    QDialog, QFormLayout, QComboBox, QDateEdit, QFileDialog, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPainter, QPen, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QDate, QRectF, QPointF, QEvent

# === إعداد قاعدة البيانات (لا تغيير) ===
DB_NAME = "clinic_data.db"
LOGO_PATH_FILE = "clinic_logo_path.txt" # ملف لحفظ مسار الشعار

def setup_database():
    """
    يقوم بإعداد قاعدة البيانات وإنشاء الجداول اللازمة إذا لم تكن موجودة.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS animals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        species TEXT,
        birth_date TEXT, -- تاريخ الميلاد
        age TEXT,
        weight TEXT,
        temperature TEXT,
        medical_history TEXT,
        diagnosis TEXT,
        vaccine_viruses TEXT,
        vaccine_insects TEXT,
        vaccine_fungi TEXT,
        vaccine_rabies TEXT,
        vaccine_worms TEXT,
        vaccine_other TEXT,
        photo_path TEXT,
        client_id INTEGER,
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
    )''')
    conn.commit()
    conn.close()

# === كلاس جديد: QLabel مخصص للقص ===
class CroppableLabel(QLabel):
    """
    QLabel مخصص لعرض الصورة والسماح للمستخدم بتحديد منطقة للقص عليها.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0; border-radius: 8px;")
        
        self.crop_rect = QRectF() # المستطيل الذي يحدده المستخدم للقص (إحداثيات داخل الصورة المعروضة)
        self.start_point = QPointF() # نقطة بداية السحب
        self.end_point = QPointF()   # نقطة نهاية السحب
        self.is_dragging = False     # هل المستخدم يقوم بالسحب حالياً
        self.image_display_rect = QRectF() # المستطيل الفعلي الذي تشغله الصورة داخل الـ QLabel بعد التحجيم

    def setPixmap(self, pixmap):
        """
        يضبط الصورة المعروضة في الـ QLabel ويعيد حساب منطقة عرض الصورة.
        """
        super().setPixmap(pixmap)
        # إعادة حساب image_display_rect عند تغيير الصورة
        if not pixmap.isNull() and not self.size().isEmpty():
            # حساب الحجم الفعلي للصورة بعد التحجيم للحفاظ على الأبعاد
            scaled_size = pixmap.size().scaled(self.size(), Qt.KeepAspectRatio)
            x_offset = (self.width() - scaled_size.width()) / 2
            y_offset = (self.height() - scaled_size.height()) / 2
            self.image_display_rect = QRectF(x_offset, y_offset, scaled_size.width(), scaled_size.height())
        else:
            self.image_display_rect = QRectF()
        self.update() # إعادة رسم لتحديث مربع القص القديم

    def resizeEvent(self, event):
        """
        يتم استدعاؤه عند تغيير حجم الـ QLabel.
        """
        super().resizeEvent(event)
        # إعادة حساب image_display_rect ومسح مربع القص عند تغيير حجم الـ QLabel
        if not self.pixmap().isNull():
            self.setPixmap(self.pixmap()) # يعيد ضبط الصورة ومربع العرض
        self.update() # إعادة رسم

    def mousePressEvent(self, event):
        """
        يتم استدعاؤه عند الضغط على زر الماوس.
        """
        if event.button() == Qt.LeftButton:
            if self.image_display_rect.contains(event.pos()): # التأكد من أن النقر داخل الصورة المعروضة
                self.is_dragging = True
                # إحداثيات بداية السحب تكون نسبةً لبداية الصورة المعروضة داخل الـ QLabel
                self.start_point = event.pos() - self.image_display_rect.topLeft()
                self.end_point = self.start_point
                self.update() # إعادة رسم الـ QLabel لتحديث مربع التحديد
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        يتم استدعاؤه عند تحريك الماوس أثناء الضغط.
        """
        if self.is_dragging:
            # إحداثيات نهاية السحب تكون نسبةً لبداية الصورة المعروضة داخل الـ QLabel
            self.end_point = event.pos() - self.image_display_rect.topLeft()
            self.update() # إعادة رسم الـ QLabel لتحديث مربع التحديد
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        يتم استدعاؤه عند تحرير زر الماوس.
        """
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.update() # إعادة رسم الـ QLabel لتحديث مربع التحديد
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """
        يتم استدعاؤه لرسم محتوى الـ QLabel، بما في ذلك مربع القص.
        """
        super().paintEvent(event) # يرسم الصورة الأساسية أولاً

        if self.is_dragging or not self.crop_rect.isEmpty():
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0, 180)) # لون أحمر شفاف
            pen.setWidth(2)
            painter.setPen(pen)
            
            # حساب المستطيل الذي سيتم رسمه على الـ QLabel
            # الإحداثيات هنا هي إحداثيات الـ QLabel
            rect_x = min(self.start_point.x(), self.end_point.x()) + self.image_display_rect.x()
            rect_y = min(self.start_point.y(), self.end_point.y()) + self.image_display_rect.y()
            rect_width = abs(self.start_point.x() - self.end_point.x())
            rect_height = abs(self.start_point.y() - self.end_point.y())
            
            # التأكد من أن مربع القص لا يخرج عن حدود الصورة المعروضة داخل الـ QLabel
            self.crop_rect = QRectF(rect_x, rect_y, rect_width, rect_height).intersected(self.image_display_rect)
            
            painter.drawRect(self.crop_rect)
            painter.end()

    def get_crop_rect_relative_to_displayed_image(self):
        """
        يعيد مستطيل القص بإحداثيات نسبية للصورة المعروضة فعلياً (scaled_pixmap).
        هذه الإحداثيات هي التي تستخدمها ImageCropperDialog للتحويل إلى الصورة الأصلية.
        """
        if self.crop_rect.isEmpty() or self.image_display_rect.isEmpty():
            return QRectF()
        
        # تحويل crop_rect من إحداثيات الـ QLabel إلى إحداثيات نسبية للصورة المعروضة
        return QRectF(
            self.crop_rect.x() - self.image_display_rect.x(),
            self.crop_rect.y() - self.image_display_rect.y(),
            self.crop_rect.width(),
            self.crop_rect.height()
        )

# === كلاس جديد: نافذة قص الصور ===
class ImageCropperDialog(QDialog):
    """
    نافذة منبثقة تسمح للمستخدم بقص صورة محددة.
    """
    def __init__(self, parent=None, image_path=None):
        super().__init__(parent)
        self.setWindowTitle("قص الصورة")
        self.setGeometry(100, 100, 800, 600)
        
        self.original_pixmap = QPixmap(image_path)
        if self.original_pixmap.isNull():
            QMessageBox.critical(self, "خطأ", "فشل تحميل الصورة.")
            self.reject()
            return
        
        self.init_ui()
        self.image_label.setPixmap(self.original_pixmap) # عرض الصورة الأصلية في CroppableLabel

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.image_label = CroppableLabel(self) # استخدام الـ QLabel المخصص للقص
        # ضبط حجم مبدئي للـ CroppableLabel، سيتم تعديله في resizeEvent
        self.image_label.setFixedSize(780, 500) 
        main_layout.addWidget(self.image_label)
        
        buttons_layout = QHBoxLayout()
        self.crop_button = QPushButton("قص وحفظ")
        self.crop_button.clicked.connect(self.accept_crop)
        self.crop_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);")
        
        cancel_button = QPushButton("إلغاء")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("background-color: #F44336; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);")
        
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.crop_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch(1)
        
        main_layout.addLayout(buttons_layout)

    def resizeEvent(self, event):
        """
        يتم استدعاؤه عند تغيير حجم نافذة القص.
        """
        super().resizeEvent(event)
        # ضبط حجم الـ CroppableLabel ليتناسب مع حجم النافذة الجديدة
        # مع ترك مساحة للأزرار والهوامش
        new_label_width = self.width() - 40 # 20px margin on each side
        new_label_height = self.height() - 100 # Approx. space for buttons and top/bottom margins
        self.image_label.setFixedSize(new_label_width, new_label_height)
        self.image_label.setPixmap(self.original_pixmap) # إعادة تحجيم الصورة داخل الـ QLabel

    def accept_crop(self):
        """
        يقوم بقص الصورة بناءً على التحديد ويحفظها.
        """
        crop_rect_on_scaled_image = self.image_label.get_crop_rect_relative_to_displayed_image()

        if crop_rect_on_scaled_image.isEmpty() or crop_rect_on_scaled_image.width() <= 1 or crop_rect_on_scaled_image.height() <= 1:
            QMessageBox.warning(self, "تحذير", "برجاء تحديد منطقة صالحة للقص أولاً (أكبر من 1x1 بكسل).")
            return

        original_width = self.original_pixmap.width()
        original_height = self.original_pixmap.height()
        
        # حساب نسبة القياس من أبعاد الصورة المعروضة إلى أبعاد الصورة الأصلية
        if self.image_label.image_display_rect.width() == 0 or self.image_label.image_display_rect.height() == 0:
             QMessageBox.critical(self, "خطأ", "أبعاد الصورة المعروضة غير صالحة للقص.")
             self.reject()
             return

        scale_x = original_width / self.image_label.image_display_rect.width()
        scale_y = original_height / self.image_label.image_display_rect.height()

        # تحويل إحداثيات القص من الصورة المعروضة إلى الصورة الأصلية
        final_x = int(crop_rect_on_scaled_image.x() * scale_x)
        final_y = int(crop_rect_on_scaled_image.y() * scale_y)
        final_width = int(crop_rect_on_scaled_image.width() * scale_x)
        final_height = int(crop_rect_on_scaled_image.height() * scale_y)

        # التأكد من أن الإحداثيات ضمن حدود الصورة الأصلية
        final_x = max(0, final_x)
        final_y = max(0, final_y)
        final_width = min(final_width, original_width - final_x)
        final_height = min(final_height, original_height - final_y)
        
        # التأكد من الحد الأدنى للأبعاد لتجنب الأخطاء مع QPixmap.copy
        final_width = max(1, final_width)
        final_height = max(1, final_height)

        try:
            cropped_pixmap = self.original_pixmap.copy(final_x, final_y, final_width, final_height)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في القص", f"حدث خطأ أثناء عملية القص: {e}")
            self.reject()
            return

        if cropped_pixmap.isNull():
            QMessageBox.critical(self, "خطأ", "الصورة المقصوصة فارغة أو غير صالحة. قد تكون منطقة التحديد صغيرة جداً.")
            self.reject()
            return
        
        temp_dir = "temp_cropped_images"
        os.makedirs(temp_dir, exist_ok=True)
        # استخدام اسم فريد لتجنب التضارب
        # يجب أن يكون self.parent() موجوداً وله current_animal_id
        animal_id_str = str(self.parent().current_animal_id) if hasattr(self.parent(), 'current_animal_id') and self.parent().current_animal_id is not None else "unknown_animal"
        temp_file_path = os.path.join(temp_dir, f"cropped_{animal_id_str}_{os.urandom(4).hex()}.png")
        
        pil_image = Image.fromqpixmap(cropped_pixmap)
        image_format = temp_file_path.split('.')[-1].lower()
        if image_format == 'jpg':
            image_format = 'jpeg'
        try:
            pil_image.save(temp_file_path, format=image_format)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في حفظ الصورة", f"حدث خطأ أثناء حفظ الصورة المقصوصة: {e}")
            self.reject()
            return
        
        self.cropped_image_path = temp_file_path
        self.accept()

# === نموذج إضافة/تعديل عميل ===
class ClientFormDialog(QDialog):
    """
    نافذة لإضافة أو تعديل بيانات العميل.
    """
    def __init__(self, parent=None, client_id=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة عميل جديد" if client_id is None else "تعديل بيانات العميل")
        self.setFixedSize(450, 250)
        self.client_id = client_id
        self.parent_window = parent

        self.init_ui()
        if self.client_id is not None:
            self.load_client_data()

    def init_ui(self):
        form_layout = QFormLayout(self)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight) # محاذاة تسميات الحقول لليمين
        form_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop) # محاذاة النموذج لليمين

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ادخل اسم العميل")
        self.name_input.setFont(QFont("Arial", 11))
        self.name_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.name_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("اسم العميل:"), self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("ادخل رقم الهاتف")
        self.phone_input.setFont(QFont("Arial", 11))
        self.phone_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.phone_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("رقم الهاتف:"), self.phone_input)

        save_btn = QPushButton("حفظ")
        save_btn.setFont(QFont("Arial", 12, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 10px;
                margin-top: 15px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        save_btn.clicked.connect(self.save_client)
        form_layout.addRow(save_btn)

    def load_client_data(self):
        """
        يقوم بتحميل بيانات العميل الحالي من قاعدة البيانات.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone FROM clients WHERE id = ?", (self.client_id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            self.name_input.setText(data[0])
            self.phone_input.setText(data[1])

    def save_client(self):
        """
        يقوم بحفظ بيانات العميل (إضافة جديد أو تعديل موجود).
        """
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name:
            QMessageBox.warning(self, "بيانات ناقصة", "برجاء إدخال اسم العميل.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if self.client_id is None:
                cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
                QMessageBox.information(self, "تم الحفظ", "تم إضافة العميل بنجاح.")
            else:
                cursor.execute("UPDATE clients SET name = ?, phone = ? WHERE id = ?", (name, phone, self.client_id))
                QMessageBox.information(self, "تم التعديل", "تم تعديل بيانات العميل بنجاح.")
            conn.commit()
            self.parent_window.load_clients()
            if self.client_id is not None:
                current_item = self.parent_window.client_list_widget.currentItem()
                if current_item and current_item.data(Qt.UserRole) == self.client_id:
                    self.parent_window.display_client_details(current_item)
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في الحفظ", f"حدث خطأ أثناء حفظ البيانات: {e}")
        finally:
            conn.close()

# === نموذج إضافة/تعديل حيوان ===
class AnimalFormDialog(QDialog):
    """
    نافذة لإضافة أو تعديل بيانات الحيوان.
    """
    def __init__(self, parent=None, client_id=None, animal_id=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة حيوان جديد" if animal_id is None else "تعديل بيانات الحيوان")
        self.setGeometry(200, 200, 650, 800)
        self.client_id = client_id
        self.animal_id = animal_id
        self.parent_window = parent
        self.current_photo_path = "" # لتخزين مسار الصورة (سواء الأصلية أو المقصوصة)

        self.init_ui()
        if self.animal_id is not None:
            self.load_animal_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(12)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight) # محاذاة تسميات الحقول لليمين
        form_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop) # محاذاة النموذج لليمين

        # عناوين الأقسام
        form_layout.addRow(QLabel("<h3 style='color:#3F51B5; margin-bottom: 10px;'>بيانات الحيوان الأساسية:</h3>"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم الحيوان")
        self.name_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.name_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الاسم:"), self.name_input)

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("مثال: كلب، قطة، طائر")
        self.type_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.type_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("النوع:"), self.type_input)

        self.species_input = QLineEdit()
        self.species_input.setPlaceholderText("مثال: بلدي، شيرازي، سيامي")
        self.species_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.species_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الفصيلة:"), self.species_input)

        self.birth_date_input = QDateEdit(calendarPopup=True)
        self.birth_date_input.setDate(QDate.currentDate())
        self.birth_date_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("تاريخ الميلاد:"), self.birth_date_input)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("العمر (اختياري)")
        self.age_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.age_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("العمر:"), self.age_input)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("الوزن (كجم)")
        self.weight_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.weight_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الوزن:", self.weight_input))

        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("درجة الحرارة (مئوية)")
        self.temp_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.temp_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("درجة الحرارة:"), self.temp_input)

        self.medical_history_input = QTextEdit()
        self.medical_history_input.setPlaceholderText("التاريخ الطبي (الأمراض السابقة، الجراحات..)")
        self.medical_history_input.setFixedHeight(120)
        self.medical_history_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.medical_history_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("التاريخ الطبي:"), self.medical_history_input)

        self.diagnosis_input = QTextEdit()
        self.diagnosis_input.setPlaceholderText("التشخيص الحالي")
        self.diagnosis_input.setFixedHeight(120)
        self.diagnosis_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.diagnosis_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("التشخيص:"), self.diagnosis_input)

        form_layout.addRow(QLabel("<h3 style='color:#3F51B5; margin-top: 20px; margin-bottom: 10px;'>بيانات التطعيمات (تاريخ آخر تطعيم):</h3>"))
        
        self.vaccine_viruses_input = QLineEdit()
        self.vaccine_viruses_input.setPlaceholderText("الفيروسات")
        self.vaccine_viruses_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_viruses_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الفيروسات:"), self.vaccine_viruses_input)

        self.vaccine_insects_input = QLineEdit()
        self.vaccine_insects_input.setPlaceholderText("الحشرات")
        self.vaccine_insects_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_insects_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الحشرات:"), self.vaccine_insects_input)

        self.vaccine_fungi_input = QLineEdit()
        self.vaccine_fungi_input.setPlaceholderText("الفطريات")
        self.vaccine_fungi_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_fungi_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الفطريات:"), self.vaccine_fungi_input)

        self.vaccine_rabies_input = QLineEdit()
        self.vaccine_rabies_input.setPlaceholderText("السعار")
        self.vaccine_rabies_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_rabies_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("السعار:"), self.vaccine_rabies_input)

        self.vaccine_worms_input = QLineEdit()
        self.vaccine_worms_input.setPlaceholderText("الديدان")
        self.vaccine_worms_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_worms_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("الديدان:"), self.vaccine_worms_input)

        self.vaccine_other_input = QLineEdit()
        self.vaccine_other_input.setPlaceholderText("تطعيمات أخرى")
        self.vaccine_other_input.setAlignment(Qt.AlignRight) # محاذاة لليمين
        self.vaccine_other_input.setStyleSheet("padding: 8px; border: 1px solid #B0BEC5; border-radius: 5px;")
        form_layout.addRow(QLabel("أخرى:"), self.vaccine_other_input)

        # === صورة الحيوان مع زر القص ===
        form_layout.addRow(QLabel("<h3 style='color:#3F51B5; margin-top: 20px; margin-bottom: 10px;'>صورة الحيوان:</h3>"))
        
        photo_actions_layout = QHBoxLayout()
        self.photo_path_label = QLabel("لا توجد صورة مختارة.")
        self.photo_path_label.setFixedWidth(250)
        self.photo_path_label.setWordWrap(True)
        self.photo_path_label.setStyleSheet("border: 1px dashed #ccc; padding: 5px; background-color: #f9f9f9; border-radius: 5px;")
        
        select_photo_btn = QPushButton("اختيار صورة")
        select_photo_btn.clicked.connect(self.select_photo)
        select_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0; /* بنفسجي */
                color: white;
                border-radius: 5px;
                padding: 8px;
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #AB47BC;
            }
        """)

        self.crop_photo_btn = QPushButton("قص الصورة")
        self.crop_photo_btn.clicked.connect(self.open_image_cropper)
        self.crop_photo_btn.setEnabled(False) # تعطيل الزر حتى يتم اختيار صورة
        self.crop_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; /* برتقالي */
                color: white;
                border-radius: 5px;
                padding: 8px;
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #FFB74D;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #616161;
            }
        """)
        
        photo_actions_layout.addWidget(self.photo_path_label)
        photo_actions_layout.addWidget(select_photo_btn)
        photo_actions_layout.addWidget(self.crop_photo_btn)
        form_layout.addRow(QLabel("الصورة:"), photo_actions_layout)

        self.photo_preview_label = QLabel()
        self.photo_preview_label.setAlignment(Qt.AlignCenter)
        self.photo_preview_label.setFixedSize(200, 200)
        self.photo_preview_label.setStyleSheet("border: 1px solid #ddd; background-color: #f5f5f5; border-radius: 10px;")
        form_layout.addRow("", self.photo_preview_label)

        save_btn = QPushButton("حفظ بيانات الحيوان")
        save_btn.setFont(QFont("Arial", 13, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-top: 25px;
                box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_animal)
        form_layout.addRow(save_btn)

        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

    def select_photo(self):
        """
        يفتح نافذة اختيار ملف الصورة للحيوان.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "اختيار صورة الحيوان", "", 
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.current_photo_path = file_path
            self.photo_path_label.setText(os.path.basename(file_path))
            self.load_photo_preview(file_path)
            self.crop_photo_btn.setEnabled(True) # تفعيل زر القص

    def open_image_cropper(self):
        """
        يفتح نافذة قص الصورة للحيوان الحالي.
        """
        if not self.current_photo_path or not os.path.exists(self.current_photo_path):
            QMessageBox.warning(self, "خطأ", "لا توجد صورة محددة لقصها.")
            return

        cropper_dialog = ImageCropperDialog(self, self.current_photo_path)
        if cropper_dialog.exec_() == QDialog.Accepted:
            cropped_path = cropper_dialog.cropped_image_path
            if cropped_path:
                self.current_photo_path = cropped_path # تحديث المسار للملف المقصوص
                self.photo_path_label.setText(os.path.basename(cropped_path))
                self.load_photo_preview(cropped_path)
                QMessageBox.information(self, "تم القص", "تم قص الصورة بنجاح.")

    def load_photo_preview(self, path):
        """
        يعرض معاينة للصورة المختارة.
        """
        if os.path.exists(path):
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(self.photo_preview_label.size(), 
                                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_preview_label.setPixmap(scaled_pixmap)
        else:
            self.photo_preview_label.clear()
            self.photo_preview_label.setText("خطأ في تحميل الصورة")

    def load_animal_data(self):
        """
        يقوم بتحميل بيانات الحيوان الحالي من قاعدة البيانات.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animals WHERE id = ?", (self.animal_id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            self.name_input.setText(data[1])
            self.type_input.setText(data[2])
            self.species_input.setText(data[3])
            
            if data[4]:
                self.birth_date_input.setDate(QDate.fromString(data[4], "yyyy-MM-dd"))

            self.age_input.setText(data[5])
            self.weight_input.setText(data[6])
            self.temp_input.setText(data[7])
            self.medical_history_input.setText(data[8])
            self.diagnosis_input.setText(data[9])
            
            self.vaccine_viruses_input.setText(data[10])
            self.vaccine_insects_input.setText(data[11])
            self.vaccine_fungi_input.setText(data[12])
            self.vaccine_rabies_input.setText(data[13])
            self.vaccine_worms_input.setText(data[14])
            self.vaccine_other_input.setText(data[15])
            
            self.current_photo_path = data[16] if data[16] else ""
            if self.current_photo_path:
                self.photo_path_label.setText(os.path.basename(self.current_photo_path))
                self.load_photo_preview(self.current_photo_path)
                self.crop_photo_btn.setEnabled(True)
            else:
                self.photo_path_label.setText("لا توجد صورة مختارة.")
                self.photo_preview_label.clear()
                self.crop_photo_btn.setEnabled(False)

    def save_animal(self):
        """
        يقوم بحفظ بيانات الحيوان (إضافة جديد أو تعديل موجود).
        """
        name = self.name_input.text().strip()
        animal_type = self.type_input.text().strip()
        species = self.species_input.text().strip()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        age = self.age_input.text().strip()
        weight = self.weight_input.text().strip()
        temperature = self.temp_input.text().strip()
        medical_history = self.medical_history_input.toPlainText().strip()
        diagnosis = self.diagnosis_input.toPlainText().strip()
        
        vaccine_viruses = self.vaccine_viruses_input.text().strip()
        vaccine_insects = self.vaccine_insects_input.text().strip()
        vaccine_fungi = self.vaccine_fungi_input.text().strip()
        vaccine_rabies = self.vaccine_rabies_input.text().strip()
        vaccine_worms = self.vaccine_worms_input.text().strip()
        vaccine_other = self.vaccine_other_input.text().strip()
        
        photo_path = self.current_photo_path

        if not name or not animal_type:
            QMessageBox.warning(self, "بيانات ناقصة", "برجاء إدخال اسم الحيوان ونوعه على الأقل.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if self.animal_id is None:
                cursor.execute("""
                    INSERT INTO animals (
                        name, type, species, birth_date, age, weight, temperature,
                        medical_history, diagnosis, vaccine_viruses, vaccine_insects,
                        vaccine_fungi, vaccine_rabies, vaccine_worms, vaccine_other,
                        photo_path, client_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, animal_type, species, birth_date, age, weight, temperature,
                      medical_history, diagnosis, vaccine_viruses, vaccine_insects,
                      vaccine_fungi, vaccine_rabies, vaccine_worms, vaccine_other,
                      photo_path, self.client_id))
                QMessageBox.information(self, "تم الحفظ", "تم إضافة الحيوان بنجاح.")
            else:
                cursor.execute("""
                    UPDATE animals SET
                        name = ?, type = ?, species = ?, birth_date = ?, age = ?,
                        weight = ?, temperature = ?, medical_history = ?, diagnosis = ?,
                        vaccine_viruses = ?, vaccine_insects = ?, vaccine_fungi = ?,
                        vaccine_rabies = ?, vaccine_worms = ?, vaccine_other = ?,
                        photo_path = ?
                    WHERE id = ?
                """, (name, animal_type, species, birth_date, age, weight, temperature,
                      medical_history, diagnosis, vaccine_viruses, vaccine_insects,
                      vaccine_fungi, vaccine_rabies, vaccine_worms, vaccine_other,
                      photo_path, self.animal_id))
                QMessageBox.information(self, "تم التعديل", "تم تعديل بيانات الحيوان بنجاح.")
            conn.commit()
            
            # بعد الحفظ أو التعديل، يجب العودة لصفحة تفاصيل العميل وتحديث قائمة الحيوانات
            if self.parent_window and self.client_id:
                for i in range(self.parent_window.client_list_widget.count()):
                    item = self.parent_window.client_list_widget.item(i)
                    if item.data(Qt.UserRole) == self.client_id:
                        self.parent_window.display_client_details(item) # إعادة عرض تفاصيل العميل لتحديث قائمة الحيوانات
                        break
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في الحفظ", f"حدث خطأ أثناء حفظ البيانات: {e}")
        finally:
            conn.close()

# === النافذة الرئيسية للبرنامج ===
class ClinicMainWindow(QMainWindow):
    """
    النافذة الرئيسية لتطبيق إدارة عيادة هرة البيطرية.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("عيادة هرة البيطرية - Herh Vet Clinic")
        self.setGeometry(100, 100, 1200, 800)

        self.conn = None
        self.cursor = None
        self.current_animal_id = None # لتتبع الحيوان الحالي لعرض تفاصيله
        self.init_db_connection()

        self.init_ui()
        self.load_clients()
        self.load_logo() # تحميل الشعار عند بدء التشغيل

    def init_db_connection(self):
        """
        يقوم بإنشاء اتصال بقاعدة البيانات.
        """
        try:
            self.conn = sqlite3.connect(DB_NAME)
            self.cursor = self.conn.cursor()
            setup_database()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"فشل الاتصال بقاعدة البيانات: {e}")
            sys.exit(1)

    def init_ui(self):
        """
        يقوم بتهيئة واجهة المستخدم الرئيسية للبرنامج.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)

        # رأس البرنامج (Header)
        top_header_frame = QFrame()
        top_header_frame.setFixedHeight(350) # زيادة الارتفاع لاستيعاب اللوجو الأكبر
        top_header_frame.setStyleSheet("background-color: #E0F2F7; border-bottom: 3px solid #B2EBF2; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);")
        top_header_layout = QVBoxLayout(top_header_frame)
        top_header_layout.setAlignment(Qt.AlignCenter)
        top_header_layout.setSpacing(5) 

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        clinic_name_label = QLabel("عيادة هرة البيطرية")
        # محاولة استخدام خط Tajawal إذا كان متوفراً
        font_id = QFontDatabase.addApplicationFont(":/fonts/Tajawal-Bold.ttf") # افتراضي: ابحث عن الخط في مسار الموارد
        if font_id != -1:
            clinic_name_label.setFont(QFont("Tajawal", 48, QFont.Bold)) # حجم أكبر
        else:
            clinic_name_label.setFont(QFont("Arial", 48, QFont.Bold))
        clinic_name_label.setAlignment(Qt.AlignCenter)
        clinic_name_label.setStyleSheet("color: #2196F3; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);")

        clinic_slogan_label = QLabel("Herh Vet Clinic - بيتك الثاني لحيوانك الأليف")
        font_id = QFontDatabase.addApplicationFont(":/fonts/Tajawal-Regular.ttf")
        if font_id != -1:
            clinic_slogan_label.setFont(QFont("Tajawal", 24, QFont.StyleItalic)) # حجم أكبر
        else:
            clinic_slogan_label.setFont(QFont("Arial", 24, QFont.StyleItalic))
        clinic_slogan_label.setAlignment(Qt.AlignCenter)
        clinic_slogan_label.setStyleSheet("color: #757575;")

        self.change_logo_btn = QPushButton("تغيير الشعار")
        self.change_logo_btn.setFont(QFont("Arial", 11))
        self.change_logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #03A9F4;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                margin-top: 15px;
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #29B6F6;
            }
        """)
        self.change_logo_btn.clicked.connect(self.select_logo)

        top_header_layout.addWidget(self.logo_label)
        top_header_layout.addWidget(clinic_name_label)
        top_header_layout.addWidget(clinic_slogan_label)
        top_header_layout.addWidget(self.change_logo_btn) 

        main_v_layout.addWidget(top_header_frame)

        # الجزء السفلي (الشريط الجانبي ومنطقة التفاصيل)
        bottom_h_layout = QHBoxLayout()
        bottom_h_layout.setContentsMargins(15, 15, 15, 15) 

        # الشريط الجانبي (Sidebar)
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(320) # زيادة عرض الشريط الجانبي
        sidebar_frame.setFrameShape(QFrame.StyledPanel)
        sidebar_frame.setFrameShadow(QFrame.Raised)
        sidebar_frame.setStyleSheet("""
            background-color: #F8F8F8;
            border-radius: 15px; /* حواف مستديرة أكثر */
            border: 1px solid #E0E0E0;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
        """)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(15)

        sidebar_layout.addWidget(QLabel("<h3 style='color:#3F51B5;'>قائمة العملاء</h3>"))
        self.client_list_widget = QListWidget()
        self.client_list_widget.setFont(QFont("Arial", 14)) # خط أكبر
        self.client_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #B0BEC5;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
                selection-background-color: #BBDEFB;
                selection-color: #1A237E;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                background-color: #BBDEFB;
                color: #1A237E;
                font-weight: bold;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
        """)
        self.client_list_widget.itemClicked.connect(self.display_client_details) # تم التأكد من الربط الصحيح
        sidebar_layout.addWidget(self.client_list_widget)

        self.add_client_btn = QPushButton("⊕ إضافة عميل جديد")
        self.add_client_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.add_client_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 12px;
                padding: 15px;
                margin-top: 20px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.add_client_btn.clicked.connect(self.open_add_client_form)
        sidebar_layout.addWidget(self.add_client_btn)

        bottom_h_layout.addWidget(sidebar_frame)

        # منطقة عرض التفاصيل
        self.details_area = QScrollArea()
        self.details_area.setWidgetResizable(True)
        self.details_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 15px; /* حواف مستديرة أكثر */
                background-color: white;
                box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            }
        """)
        
        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)
        self.details_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.details_layout.setContentsMargins(30, 30, 30, 30) 

        self.details_area.setWidget(details_widget)
        
        self.welcome_label = QLabel("<html><body dir='rtl'><p align='center'><span style='font-size:24pt; font-weight:600; color:#3F51B5;'>مرحباً بك في عيادة هرة البيطرية</span></p>"
                                     "<p align='center'><span style='font-size:18pt;'>برجاء اختيار عميل من القائمة الجانبية</span></p>"
                                     "<p align='center'><span style='font-size:18pt;'>أو اضغط على زر <b>'إضافة عميل جديد'</b> للبدء.</span></p></body></html>")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.details_layout.addWidget(self.welcome_label)
        self.details_layout.addStretch(1)

        bottom_h_layout.addWidget(self.details_area)

        main_v_layout.addLayout(bottom_h_layout)

    def load_logo(self):
        """
        يقوم بتحميل شعار العيادة من المسار المحفوظ.
        """
        logo_path = ""
        if os.path.exists(LOGO_PATH_FILE):
            with open(LOGO_PATH_FILE, 'r') as f:
                logo_path = f.read().strip()

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # حجم أكبر للشعار
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("<h2>[لا يوجد شعار]</h2>")
            self.logo_label.setStyleSheet("color: #FF5722;")

    def select_logo(self):
        """
        يفتح نافذة اختيار ملف الصورة لتغيير شعار العيادة.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "اختيار شعار العيادة", "", 
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            with open(LOGO_PATH_FILE, 'w') as f:
                f.write(file_path)
            self.load_logo() # إعادة تحميل الشعار الجديد
            QMessageBox.information(self, "تم تحديث الشعار", "تم تغيير شعار العيادة بنجاح.")

    def load_clients(self):
        """
        يقوم بتحميل قائمة العملاء من قاعدة البيانات وعرضها في الشريط الجانبي.
        """
        self.client_list_widget.clear()
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone FROM clients ORDER BY name")
            clients = cursor.fetchall()
            conn.close()
            for client_id, name, phone in clients:
                item = QListWidgetItem(f"{name} ({phone if phone else 'لا يوجد هاتف'})")
                item.setData(Qt.UserRole, client_id)
                self.client_list_widget.addItem(item)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في تحميل العملاء", f"حدث خطأ أثناء تحميل بيانات العملاء: {e}")

    def open_add_client_form(self):
        """
        يفتح نافذة إضافة عميل جديد.
        """
        dialog = ClientFormDialog(self)
        dialog.exec_()

    def display_client_details(self, item):
        """
        يعرض تفاصيل العميل المحدد وقائمة حيواناته.
        """
        client_id = item.data(Qt.UserRole)
        self.clear_details_layout()

        # بيانات العميل
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone FROM clients WHERE id = ?", (client_id,))
        client_data = cursor.fetchone()
        
        client_name_label = QLabel(f"<h2>العميل: {client_data[0]}</h2>")
        client_name_label.setStyleSheet("color: #3F51B5;")
        client_name_label.setAlignment(Qt.AlignCenter)
        self.details_layout.addWidget(client_name_label)

        client_phone_label = QLabel(f"<p style='font-size:14pt;'>الهاتف: {client_data[1] if client_data[1] else 'لا يوجد'}</p>")
        client_phone_label.setAlignment(Qt.AlignCenter)
        self.details_layout.addWidget(client_phone_label)

        # أزرار تعديل وحذف العميل
        client_actions_layout = QHBoxLayout()
        edit_client_btn = QPushButton("تعديل العميل")
        edit_client_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107; /* أصفر */
                color: black;
                border-radius: 8px;
                padding: 10px 15px;
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #FFD54F;
            }
        """)
        edit_client_btn.clicked.connect(lambda: self.open_edit_client_form(client_id))
        
        delete_client_btn = QPushButton("حذف العميل")
        delete_client_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336; /* أحمر */
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #E57373;
            }
        """)
        delete_client_btn.clicked.connect(lambda: self.delete_client(client_id))

        client_actions_layout.addStretch(1)
        client_actions_layout.addWidget(edit_client_btn)
        client_actions_layout.addWidget(delete_client_btn)
        client_actions_layout.addStretch(1)
        self.details_layout.addLayout(client_actions_layout)

        self.details_layout.addSpacing(25)
        self.details_layout.addWidget(QLabel("<h3 style='color:#3F51B5;'>حيوانات العميل:</h3>"))

        # قائمة الحيوانات
        animals_list_widget = QListWidget()
        animals_list_widget.setFont(QFont("Arial", 12))
        animals_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #B0BEC5;
                border-radius: 8px;
                padding: 8px;
                background-color: #F5F5F5;
                selection-background-color: #E3F2FD;
                selection-color: #1A237E;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px dashed #D0D0D0;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1A237E;
                font-weight: bold;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #E0F2F7;
            }
        """)
        animals_list_widget.setFixedHeight(180) 
        animals_list_widget.itemClicked.connect(lambda animal_item: self.display_animal_details(animal_item, client_id))
        self.details_layout.addWidget(animals_list_widget)

        cursor.execute("SELECT id, name, type FROM animals WHERE client_id = ?", (client_id,))
        animals = cursor.fetchall()
        conn.close()

        if not animals:
            animals_list_widget.addItem("لا يوجد حيوانات مسجلة لهذا العميل.")
        else:
            for animal_id, animal_name, animal_type in animals:
                item = QListWidgetItem(f"{animal_name} ({animal_type})")
                item.setData(Qt.UserRole, animal_id)
                animals_list_widget.addItem(item)

        add_animal_btn = QPushButton("⊕ إضافة حيوان جديد")
        add_animal_btn.setFont(QFont("Arial", 12, QFont.Bold))
        add_animal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 10px;
                padding: 12px;
                margin-top: 15px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        add_animal_btn.clicked.connect(lambda: self.open_add_animal_form(client_id))
        self.details_layout.addWidget(add_animal_btn)

        self.details_layout.addSpacing(25)
        self.details_layout.addWidget(QLabel("<h3 style='color:#3F51B5;'>تفاصيل الحيوان المحدد:</h3>"))

        # منطقة عرض تفاصيل الحيوان
        self.animal_details_frame = QFrame()
        self.animal_details_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #CFD8DC;
                border-radius: 10px;
                background-color: #ECEFF1;
                padding: 20px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        self.animal_details_layout = QVBoxLayout(self.animal_details_frame)
        self.animal_details_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.animal_details_layout.addWidget(QLabel("برجاء اختيار حيوان من القائمة أعلاه لعرض تفاصيله."))
        self.details_layout.addWidget(self.animal_details_frame)
        self.details_layout.addStretch(1) 

    def clear_details_layout(self):
        """
        يمسح جميع العناصر من تخطيط التفاصيل.
        """
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        """
        دالة مساعدة لمسح تخطيط فرعي.
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def open_edit_client_form(self, client_id):
        """
        يفتح نافذة تعديل بيانات العميل.
        """
        dialog = ClientFormDialog(self, client_id)
        dialog.exec_()

    def delete_client(self, client_id):
        """
        يحذف العميل المحدد وجميع حيواناته.
        """
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                     "هل أنت متأكد من حذف هذا العميل وجميع حيواناته؟",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                conn.commit()
                QMessageBox.information(self, "تم الحذف", "تم حذف العميل بنجاح.")
                self.load_clients()
                self.clear_details_layout() 
                self.details_layout.addWidget(self.welcome_label) 
                self.details_layout.addStretch(1)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "خطأ في الحذف", f"حدث خطأ أثناء حذف العميل: {e}")
            finally:
                conn.close()

    def open_add_animal_form(self, client_id):
        """
        يفتح نافذة إضافة حيوان جديد لعميل محدد.
        """
        dialog = AnimalFormDialog(self, client_id=client_id)
        dialog.exec_()

    def display_animal_details(self, item, client_id):
        """
        يعرض تفاصيل الحيوان المحدد في منطقة التفاصيل.
        """
        animal_id = item.data(Qt.UserRole)
        self.current_animal_id = animal_id # حفظ الـ ID للوصول إليه من نافذة القص

        self.clear_layout(self.animal_details_layout)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animals WHERE id = ?", (animal_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            # === عرض الصورة (أكبر حجمًا وقابلة للنقر) ===
            photo_path = data[16]
            self.animal_photo_label = QLabel()
            self.animal_photo_label.setAlignment(Qt.AlignCenter)
            self.animal_photo_label.setFixedSize(280, 280) # حجم أكبر للصورة
            self.animal_photo_label.setStyleSheet("border: 2px solid #B0BEC5; border-radius: 15px; background-color: white; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);")
            self.animal_photo_label.setCursor(Qt.PointingHandCursor) # مؤشر اليد للإشارة إلى أنها قابلة للنقر
            self.animal_photo_label.mousePressEvent = self.on_animal_photo_clicked # ربط حدث النقر

            if photo_path and os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                scaled_pixmap = pixmap.scaled(self.animal_photo_label.size(), 
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.animal_photo_label.setPixmap(scaled_pixmap)
            else:
                self.animal_photo_label.setText("لا توجد صورة")
                self.animal_photo_label.setStyleSheet("border: 2px dashed #B0BEC5; border-radius: 15px; background-color: #ECEFF1; color: #757575; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);")
            self.animal_details_layout.addWidget(self.animal_photo_label)
            self.animal_details_layout.addSpacing(15)

            # === اسم الحيوان (خط أكبر) ===
            animal_name_label = QLabel(f"<h2 style='color:#3F51B5;'>{data[1]}</h2>") # حجم خط أكبر
            font_id = QFontDatabase.addApplicationFont(":/fonts/Tajawal-Bold.ttf")
            if font_id != -1:
                animal_name_label.setFont(QFont("Tajawal", 28, QFont.Bold))
            else:
                animal_name_label.setFont(QFont("Arial", 28, QFont.Bold))
            animal_name_label.setAlignment(Qt.AlignCenter)
            self.animal_details_layout.addWidget(animal_name_label)
            self.animal_details_layout.addSpacing(15)

            # تفاصيل الحيوان الأخرى
            details_grid_layout = QFormLayout()
            details_grid_layout.setContentsMargins(0, 0, 0, 0)
            details_grid_layout.setSpacing(10)
            details_grid_layout.setLabelAlignment(Qt.AlignRight) # محاذاة التسميات لليمين
            details_grid_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop) # محاذاة النموذج لليمين

            details_grid_layout.addRow(QLabel("النوع:"), QLabel(data[2]))
            details_grid_layout.addRow(QLabel("الفصيلة:"), QLabel(data[3]))
            details_grid_layout.addRow(QLabel("تاريخ الميلاد:"), QLabel(data[4]))
            details_grid_layout.addRow(QLabel("العمر:"), QLabel(data[5]))
            details_grid_layout.addRow(QLabel("الوزن:"), QLabel(data[6] + " كجم" if data[6] else ""))
            details_grid_layout.addRow(QLabel("درجة الحرارة:"), QLabel(data[7] + " مئوية" if data[7] else ""))
            
            # عرض التاريخ الطبي والتشخيص في QTextEdit للقراءة فقط
            medical_history_label = QLabel("التاريخ الطبي:")
            medical_history_text = QTextEdit()
            medical_history_text.setReadOnly(True)
            medical_history_text.setText(data[8])
            medical_history_text.setFixedHeight(80)
            medical_history_text.setAlignment(Qt.AlignRight) # محاذاة لليمين
            medical_history_text.setStyleSheet("background-color: white; border: 1px solid #D0D0D0; border-radius: 5px; padding: 5px;")
            details_grid_layout.addRow(medical_history_label, medical_history_text)

            diagnosis_label = QLabel("التشخيص:")
            diagnosis_text = QTextEdit()
            diagnosis_text.setReadOnly(True)
            diagnosis_text.setText(data[9])
            diagnosis_text.setFixedHeight(80)
            diagnosis_text.setAlignment(Qt.AlignRight) # محاذاة لليمين
            diagnosis_text.setStyleSheet("background-color: white; border: 1px solid #D0D0D0; border-radius: 5px; padding: 5px;")
            details_grid_layout.addRow(diagnosis_label, diagnosis_text)

            self.animal_details_layout.addLayout(details_grid_layout)
            self.animal_details_layout.addSpacing(20)

            self.animal_details_layout.addWidget(QLabel("<h4 style='color:#3F51B5;'>بيانات التطعيمات:</h4>"))
            vaccine_grid_layout = QFormLayout()
            vaccine_grid_layout.setContentsMargins(0, 0, 0, 0)
            vaccine_grid_layout.setSpacing(8)
            vaccine_grid_layout.setLabelAlignment(Qt.AlignRight) # محاذاة التسميات لليمين
            vaccine_grid_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop) # محاذاة النموذج لليمين

            vaccine_grid_layout.addRow(QLabel("الفيروسات:"), QLabel(data[10]))
            vaccine_grid_layout.addRow(QLabel("الحشرات:"), QLabel(data[11]))
            vaccine_grid_layout.addRow(QLabel("الفطريات:"), QLabel(data[12]))
            vaccine_grid_layout.addRow(QLabel("السعار:"), QLabel(data[13]))
            vaccine_grid_layout.addRow(QLabel("الديدان:"), QLabel(data[14]))
            vaccine_grid_layout.addRow(QLabel("أخرى:"), QLabel(data[15]))
            self.animal_details_layout.addLayout(vaccine_grid_layout)
            self.animal_details_layout.addSpacing(25)

            # أزرار تعديل وحذف الحيوان
            animal_actions_layout = QHBoxLayout()
            edit_animal_btn = QPushButton("تعديل بيانات الحيوان")
            edit_animal_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    color: black;
                    border-radius: 8px;
                    padding: 10px 15px;
                    box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
                }
                QPushButton:hover {
                    background-color: #FFD54F;
                }
            """)
            edit_animal_btn.clicked.connect(lambda: self.open_edit_animal_form(client_id, animal_id))
            
            delete_animal_btn = QPushButton("حذف الحيوان")
            delete_animal_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 15px;
                    box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
                }
                QPushButton:hover {
                    background-color: #E57373;
                }
            """)
            delete_animal_btn.clicked.connect(lambda: self.delete_animal(animal_id, client_id))

            animal_actions_layout.addStretch(1)
            animal_actions_layout.addWidget(edit_animal_btn)
            animal_actions_layout.addWidget(delete_animal_btn)
            animal_actions_layout.addStretch(1)
            self.animal_details_layout.addLayout(animal_actions_layout)
            self.animal_details_layout.addStretch(1) 

    def on_animal_photo_clicked(self, event):
        """
        يتم استدعاء هذه الدالة عند النقر على صورة الحيوان لعرض نافذة القص.
        """
        if self.current_animal_id is None:
            QMessageBox.warning(self, "خطأ", "لا يوجد حيوان محدد لقص صورته.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT photo_path FROM animals WHERE id = ?", (self.current_animal_id,))
        photo_path_tuple = cursor.fetchone()
        conn.close()

        photo_path = photo_path_tuple[0] if photo_path_tuple else None

        if not photo_path or not os.path.exists(photo_path):
            QMessageBox.warning(self, "خطأ", "لا توجد صورة لهذا الحيوان لقصها.")
            return

        cropper_dialog = ImageCropperDialog(self, photo_path)
        if cropper_dialog.exec_() == QDialog.Accepted:
            cropped_path = cropper_dialog.cropped_image_path
            if cropped_path:
                # تحديث مسار الصورة في قاعدة البيانات
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("UPDATE animals SET photo_path = ? WHERE id = ?", (cropped_path, self.current_animal_id))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "تم القص", "تم قص الصورة وتحديثها بنجاح.")
                
                # إعادة تحميل تفاصيل الحيوان لتحديث الصورة المعروضة
                current_client_id = None
                for i in range(self.client_list_widget.count()):
                    item = self.client_list_widget.item(i)
                    if item.isSelected():
                        current_client_id = item.data(Qt.UserRole)
                        break
                
                if current_client_id:
                    # إعادة عرض تفاصيل العميل لتحديث قائمة الحيوانات والتفاصيل
                    # هذا يضمن تحديث الصورة في الواجهة
                    for i in range(self.client_list_widget.count()):
                        item = self.client_list_widget.item(i)
                        if item.data(Qt.UserRole) == current_client_id:
                            self.display_client_details(item)
                            # بعد تحديث تفاصيل العميل، يجب التأكد من إعادة تحديد الحيوان ليعرض تفاصيله المحدثة
                            # هذا الجزء قد يتطلب إعادة بناء منطق التحديد إذا لم يتم تحديثه تلقائياً
                            # أبسط حل هو إعادة استدعاء display_animal_details مباشرة
                            # ولكن يجب التأكد من أن الـ item الخاص بالحيوان لا يزال صالحاً
                            conn_temp = sqlite3.connect(DB_NAME)
                            cursor_temp = conn_temp.cursor()
                            cursor_temp.execute("SELECT id, name, type FROM animals WHERE id = ?", (self.current_animal_id,))
                            animal_data_temp = cursor_temp.fetchone()
                            conn_temp.close()
                            if animal_data_temp:
                                temp_animal_item = QListWidgetItem(f"{animal_data_temp[1]} ({animal_data_temp[2]})")
                                temp_animal_item.setData(Qt.UserRole, animal_data_temp[0])
                                self.display_animal_details(temp_animal_item, current_client_id)
                            break


    def open_edit_animal_form(self, client_id, animal_id):
        """
        يفتح نافذة تعديل بيانات الحيوان.
        """
        dialog = AnimalFormDialog(self, client_id=client_id, animal_id=animal_id)
        dialog.exec_()

    def delete_animal(self, animal_id, client_id):
        """
        يحذف الحيوان المحدد.
        """
        reply = QMessageBox.question(self, "تأكيد الحذف",
                                     "هل أنت متأكد من حذف بيانات هذا الحيوان؟",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM animals WHERE id = ?", (animal_id,))
                conn.commit()
                QMessageBox.information(self, "تم الحذف", "تم حذف بيانات الحيوان بنجاح.")
                # بعد الحذف، أعد عرض تفاصيل العميل لتحديث قائمة الحيوانات
                for i in range(self.client_list_widget.count()):
                    item = self.client_list_widget.item(i)
                    if item.data(Qt.UserRole) == client_id:
                        self.display_client_details(item)
                        break
            except sqlite3.Error as e:
                QMessageBox.critical(self, "خطأ في الحذف", f"حدث خطأ أثناء حذف الحيوان: {e}")
            finally:
                conn.close()

    def closeEvent(self, event):
        """
        يتم استدعاؤه عند إغلاق النافذة الرئيسية لإغلاق اتصال قاعدة البيانات.
        """
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Herh Vet Clinic")
    # يمكنك استبدال "icon.png" بمسار أيقونة لبرنامجك
    if os.path.exists("icon.png"):
        app.setWindowIcon(QIcon("icon.png")) 
    else:
        # يمكنك إضافة أيقونة افتراضية أو رسالة تحذير
        pass

    # ضبط الخط الافتراضي للبرنامج
    # حاول تحميل خط Tajawal إذا كان متوفراً في نظام التشغيل
    # وإلا استخدم Arial
    font_loaded = False
    # يجب أن تكون ملفات الخطوط في مجلد 'fonts' بجانب ملف البرنامج
    # أو قم بتغيير المسار هنا
    if os.path.exists("fonts/Tajawal-Regular.ttf"):
        if QFontDatabase.addApplicationFont("fonts/Tajawal-Regular.ttf") != -1:
            font = QFont("Tajawal", 10)
            font_loaded = True
    if os.path.exists("fonts/Tajawal-Bold.ttf"):
        if QFontDatabase.addApplicationFont("fonts/Tajawal-Bold.ttf") != -1:
            # يمكن استخدام هذا الخط للخطوط العريضة
            pass # لا نغير الخط الافتراضي هنا، فقط نجعله متاحاً
    
    if not font_loaded:
        font = QFont("Arial", 10)
    
    app.setFont(font)

    main_window = ClinicMainWindow()
    main_window.showMaximized() # فتح النافذة بأقصى حجم
    sys.exit(app.exec_())
