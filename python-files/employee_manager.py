import pandas as pd
import os
from datetime import datetime

# اسم ملف الإكسل
EXCEL_FILE = "employees_data.xlsx"

# التحقق من وجود الملف أو إنشاؤه
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["الاسم", "الوظيفة", "القسم", "رقم الهاتف", "الراتب", "تاريخ التعيين"])
        df.to_excel(EXCEL_FILE, index=False)
        print(f"تم إنشاء ملف جديد: {EXCEL_FILE}")

# قراءة البيانات من الإكسل
def load_data():
    return pd.read_excel(EXCEL_FILE)

# حفظ موظف جديد
def save_employee(emp_data):
    df = load_data()
    new_df = pd.DataFrame([emp_data])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"✅ تم حفظ الموظف '{emp_data['الاسم']}' بنجاح!")

# إدخال بيانات موظف جديد
def add_employee():
    print("\n➕ إدخال موظف جديد:")
    name = input("الاسم الكامل: ").strip()
    job = input("الوظيفة: ").strip()
    department = input("القسم: ").strip()
    phone = input("رقم الهاتف: ").strip()

    while True:
        try:
            salary = float(input("الراتب الشهري: "))
            break
        except ValueError:
            print("❌ الرجاء إدخال رقم صحيح للراتب.")

    while True:
        date_input = input("تاريخ التعيين (يوم/شهر/سنة) مثال 15/4/2025: ")
        try:
            hire_date = datetime.strptime(date_input, "%d/%m/%Y").date()
            break
        except ValueError:
            print("❌ التنسيق غير صحيح. استخدم: يوم/شهر/سنة")

    # تجهيز البيانات
    emp_data = {
        "الاسم": name,
        "الوظيفة": job,
        "القسم": department,
        "رقم الهاتف": phone,
        "الراتب": salary,
        "تاريخ التعيين": hire_date.strftime("%Y-%m-%d")
    }

    save_employee(emp_data)

# عرض جميع الموظفين
def view_employees():
    df = load_data()
    if df.empty:
        print("\n📄 لا توجد بيانات موظفين بعد.")
    else:
        print("\n📋 قائمة الموظفين:")
        print("="*90)
        print(df.to_string(index=False))
        print("="*90)

# القائمة الرئيسية
def main():
    init_excel()
    print("👥 برنامج إدارة بيانات الموظفين")

    while True:
        print("\nاختر عملية:")
        print("1. إدخال موظف جديد")
        print("2. عرض جميع الموظفين")
        print("3. الخروج")

        choice = input("أدخل رقم الخيار (1-3): ").strip()

        if choice == '1':
            add_employee()
        elif choice == '2':
            view_employees()
        elif choice == '3':
            print("👋 تم الخروج من البرنامج. مع السلامة!")
            break
        else:
            print("❌ اختيار غير صحيح، حاول مجددًا.")

if __name__ == "__main__":
    main()