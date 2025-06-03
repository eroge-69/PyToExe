import sys
import csv
import json
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QFileDialog, QLabel, QMessageBox, QStatusBar, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QFont, QPalette, QColor
from PySide6.QtCore import Qt, Slot, QSize

# --- دالة لتحميل الأيقونات بشكل آمن (اختياري، لكن جيد) ---
def get_icon(standard_pixmap_name, fallback_path=None):
    """
    يحاول تحميل أيقونة قياسية، وإذا فشل، يحاول تحميلها من مسار احتياطي.
    """
    try:
        # جرب استخدام أيقونات Qt القياسية أولاً
        icon = QApplication.style().standardIcon(getattr(QStyle, standard_pixmap_name))
        if not icon.isNull():
            return icon
    except AttributeError:
        print(f"الأيقونة القياسية {standard_pixmap_name} غير موجودة.")
    except Exception as e:
        print(f"خطأ أثناء تحميل الأيقونة القياسية: {e}")

    # إذا فشل تحميل الأيقونة القياسية أو لم تكن متوفرة، جرب مسار احتياطي
    # يمكنك وضع ملف أيقونة (مثلاً folder_open.png) في نفس مجلد السكربت
    if fallback_path and os.path.exists(fallback_path):
        return QIcon(fallback_path)
    
    # إذا لم يتم العثور على أي أيقونة، أرجع أيقونة فارغة
    return QIcon()


class CSVtoJSONConverter(QMainWindow): # تغيير إلى QMainWindow
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_stylesheet()

    def init_ui(self):
        self.setWindowTitle("محول CSV إلى JSON الاحترافي")
        self.setGeometry(200, 200, 550, 250) # x, y, width, height

        # --- الودجت المركزي والتخطيط الرئيسي ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20) # هوامش حول التخطيط الرئيسي
        main_layout.setSpacing(15) # مسافة بين العناصر

        # --- تسمية المعلومات ---
        self.info_label = QLabel("قم باختيار ملف CSV لتحويله إلى JSON بسهولة.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setObjectName("InfoLabel") # لسهولة التخصيص بالـ QSS
        main_layout.addWidget(self.info_label)

        # --- زر اختيار الملف ---
        # تخطيط أفقي لوضع الأيقونة بجانب النص في الزر (أكثر تعقيدًا قليلاً مما هو مطلوب عادة)
        # عادةً ما يتم تعيين أيقونة للزر مباشرةً
        self.process_button = QPushButton("اختر ملف CSV وابدأ المعالجة")
        self.process_button.setObjectName("ProcessButton")
        self.process_button.setIconSize(QSize(24,24)) # حجم الأيقونة
        
        # محاولة تحميل أيقونة فتح مجلد قياسية
        # إذا لم تكن لديك أيقونات مخصصة، يمكن لـ Qt توفير بعض الأيقونات القياسية
        # QStyle.SP_DirOpenIcon هي أيقونة قياسية لفتح مجلد
        try:
            folder_icon = self.style().standardIcon(getattr(QStyle, 'SP_DirOpenIcon'))
            if not folder_icon.isNull():
                 self.process_button.setIcon(folder_icon)
        except AttributeError:
            print("لم يتم العثور على QStyle.SP_DirOpenIcon, قد يختلف اسم الأيقونة بين إصدارات Qt أو الأنظمة.")
        except Exception as e:
            print(f"خطأ في تحميل الأيقونة: {e}")


        self.process_button.clicked.connect(self.process_csv_file)
        main_layout.addWidget(self.process_button)
        
        # إضافة مسافة مرنة لدفع شريط الحالة للأسفل إذا لزم الأمر (أقل أهمية مع QMainWindow)
        # spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # main_layout.addSpacerItem(spacer)

        # --- شريط الحالة ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar) # إضافة شريط الحالة إلى QMainWindow
        self.status_bar.showMessage("جاهز لاستقبال الأوامر...")

    def apply_stylesheet(self):
        # يمكنك تجربة ألوان وخطوط مختلفة هنا
        # هذا مثال لنمط حديث وبسيط
        stylesheet = """
            QMainWindow {
                background-color: #f4f6f8; /* لون خلفية فاتح للنافذة */
            }
            QWidget#CentralWidget { /* لتطبيقها على الودجت المركزي إن أردت */
                 background-color: #f4f6f8;
            }
            QLabel#InfoLabel {
                font-size: 15px; /* حجم خط أكبر للتسمية */
                color: #2c3e50; /* لون نص داكن قليلاً */
                padding-bottom: 10px; /* مسافة سفلية */
            }
            QPushButton#ProcessButton {
                background-color: #3498db; /* لون أزرق جذاب للزر */
                color: white; /* لون نص أبيض */
                font-size: 14px;
                font-weight: bold; /* خط عريض */
                padding: 12px 20px; /* حشوة داخلية للزر */
                border-radius: 8px; /* حواف دائرية للزر */
                border: none; /* إزالة الحدود الافتراضية */
                min-height: 30px; /* أقل ارتفاع للزر */
            }
            QPushButton#ProcessButton:hover {
                background-color: #2980b9; /* لون أغمق عند مرور الفأرة */
            }
            QPushButton#ProcessButton:pressed {
                background-color: #1f618d; /* لون أغمق عند الضغط */
            }
            QStatusBar {
                background-color: #e9ecef; /* لون خلفية لشريط الحالة */
                color: #495057; /* لون نص لشريط الحالة */
                font-size: 12px;
            }
            QMessageBox {
                font-size: 13px;
            }
            QMessageBox QLabel { /* لتخصيص نص الرسائل داخل QMessageBox */
                color: #333;
            }
            QMessageBox QPushButton { /* لتخصيص أزرار QMessageBox */
                background-color: #007bff;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
        """
        self.setStyleSheet(stylesheet)
        # يمكنك استخدام central_widget.setObjectName("CentralWidget") إذا أردت تخصيصها بشكل منفصل

    @Slot()
    def process_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف CSV",
            "",
            "ملفات CSV (*.csv);;جميع الملفات (*.*)"
        )

        if not file_path:
            self.status_bar.showMessage("تم إلغاء اختيار الملف.")
            return

        self.status_bar.showMessage(f"جاري معالجة: {os.path.basename(file_path)}...")
        QApplication.processEvents()

        results = []
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                try:
                    header = next(reader)
                    if not header:
                        self.status_bar.showMessage("ملف CSV فارغ أو لا يحتوي على بيانات بعد الرأس.")
                        QMessageBox.warning(self, "تحذير", "ملف CSV فارغ أو لا يحتوي على بيانات بعد الرأس.")
                        return
                except StopIteration:
                    self.status_bar.showMessage("ملف CSV فارغ أو يحتوي على رأس فقط.")
                    QMessageBox.warning(self, "تحذير", "ملف CSV فارغ أو يحتوي على رأس فقط.")
                    return

                for row_number, row in enumerate(reader, start=2): # start=2 لأننا تجاوزنا الرأس
                    if len(row) >= 9:
                        code = row[0].strip()
                        number = row[1].strip().zfill(3)
                        distinctive_mark = row[8].strip()
                        if code and code.strip(): # تحقق أن الكود ليس فارغًا أو مسافات فقط
                            results.append({
                                "code": code,
                                "number": number,
                                "distinctiveMark": distinctive_mark
                            })
                    # else:
                        # يمكنك إضافة تنبيه هنا إذا كان عدد الأعمدة في صف ما غير كافٍ
                        # print(f"تحذير: الصف رقم {row_number} لا يحتوي على 9 أعمدة على الأقل.")


            if not results:
                self.status_bar.showMessage("لم يتم العثور على بيانات صالحة للمعالجة.")
                QMessageBox.information(self, "معلومات", "لم يتم العثور على بيانات صالحة للمعالجة في ملف CSV.")
                return

            directory, filename = os.path.split(file_path)
            base_filename, _ = os.path.splitext(filename)
            output_json_path = os.path.join(directory, f"{base_filename}.json")

            json_output = json.dumps(results, ensure_ascii=False, indent=4) # indent=4 لزيادة الوضوح

            with open(output_json_path, 'w', encoding='utf-8') as f:
                f.write(json_output)

            self.status_bar.showMessage(f"تم الحفظ بنجاح: {output_json_path}")
            QMessageBox.information(self, "نجاح", f"تم حفظ ملف JSON بنجاح في:\n{output_json_path}")

        except FileNotFoundError:
            self.status_bar.showMessage(f"خطأ: لم يتم العثور على الملف {file_path}")
            QMessageBox.critical(self, "خطأ في الملف", f"لم يتم العثور على الملف:\n{file_path}")
        except Exception as e:
            self.status_bar.showMessage(f"حدث خطأ: {e}")
            QMessageBox.critical(self, "خطأ في المعالجة", f"حدث خطأ أثناء معالجة الملف:\n{e}")

def main():
    app = QApplication(sys.argv)
    
    # --- تطبيق خط عام (اختياري) ---
    # font = QFont("Segoe UI", 10) # يمكنك اختيار خط مختلف إذا أردت
    # app.setFont(font)

    converter_app = CSVtoJSONConverter()
    converter_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()