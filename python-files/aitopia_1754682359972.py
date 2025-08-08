import os
import re

def sort_files_by_number(folder_path):
    """ترتيب الملفات حسب الأرقام الموجودة في أسمائها"""

    # التحقق من وجود المجلد
    if not os.path.exists(folder_path):
        print(f"المجلد غير موجود: {folder_path}")
        return

    try:
        # الحصول على الملفات فقط (ليس المجلدات)
        files = [f for f in os.listdir(folder_path) 
                 if os.path.isfile(os.path.join(folder_path, f))]

        # ترتيب الملفات حسب الأرقام
        def extract_number(filename):
            # البحث عن أي مجموعة من الأرقام في اسم الملف
            numbers = re.findall(r'\d+', filename)
            # إرجاع أول رقم أو صفر إذا لم يوجد رقم
            return int(numbers[0]) if numbers else 0

        # فرز الملفات باستخدام دالة الاستخراج
        sorted_files = sorted(files, key=extract_number)

        return sorted_files

    except Exception as e:
        print(f"حدث خطأ:{e}")
        return []

# مثال على الاستخدام
folder = '/path/to/your/folder'
sorted_files = sort_files_by_number(folder)
print(sorted_files)
