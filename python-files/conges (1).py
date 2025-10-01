import sqlite3
from datetime import datetime

# إنشاء قاعدة البيانات والجداول
conn = sqlite3.connect("conges.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT,
    position TEXT,
    salary REAL,
    hire_date TEXT,
    annual_balance INTEGER DEFAULT 30,
    sick_balance INTEGER DEFAULT 15,
    maternity_balance INTEGER DEFAULT 90,
    unpaid_balance INTEGER DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    leave_type TEXT,
    start_date TEXT,
    end_date TEXT,
    reason TEXT,
    days INTEGER,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)""")

conn.commit()

# ---------------------------- #
# وظائف البرنامج
# ---------------------------- #

def add_employee(name, department, position, salary, hire_date):
    c.execute("INSERT INTO employees (name, department, position, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
              (name, department, position, salary, hire_date))
    conn.commit()
    print(f"✅ تمت إضافة الموظف: {name}")

def add_leave(employee_id, leave_type, start_date, end_date, reason):
    # حساب عدد الأيام
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1

    # التحقق من الرصيد حسب نوع العطلة
    column = None
    if leave_type == "سنوية":
        column = "annual_balance"
    elif leave_type == "مرضية":
        column = "sick_balance"
    elif leave_type == "أمومة":
        column = "maternity_balance"
    elif leave_type == "بدون أجر":
        column = "unpaid_balance"
    else:
        print("❌ نوع العطلة غير معروف")
        return

    c.execute(f"SELECT {column} FROM employees WHERE id=?", (employee_id,))
    balance = c.fetchone()
    if not balance:
        print("❌ الموظف غير موجود")
        return
    balance = balance[0]

    if column != "unpaid_balance" and days > balance:
        print("❌ لا يوجد رصيد كافٍ للعطلة")
        return

    # تسجيل العطلة
    c.execute("INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason, days) VALUES (?, ?, ?, ?, ?, ?)",
              (employee_id, leave_type, start_date, end_date, reason, days))

    # تحديث الرصيد (إلا العطلة بدون أجر)
    if column != "unpaid_balance":
        c.execute(f"UPDATE employees SET {column} = {column} - ? WHERE id=?",
                  (days, employee_id))
    
    conn.commit()
    print(f"✅ تم تسجيل عطلة {leave_type} ({days} يوم)")

def list_employees():
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    print("\n📋 قائمة الموظفين:")
    for emp in employees:
        print(f"ID:{emp[0]} | {emp[1]} | قسم: {emp[2]} | منصب: {emp[3]} | راتب: {emp[4]} | "
              f"رصيد سنوي: {emp[6]} | مرضي: {emp[7]} | أمومة: {emp[8]} | بدون أجر: غير محدود")
    return employees

def list_leaves():
    c.execute("""SELECT l.id, e.name, l.leave_type, l.start_date, l.end_date, l.reason, l.days
                 FROM leaves l
                 JOIN employees e ON l.employee_id = e.id""")
    leaves = c.fetchall()
    print("\n📋 قائمة العطل:")
    for lv in leaves:
        print(f"ID:{lv[0]} | موظف: {lv[1]} | نوع: {lv[2]} | من {lv[3]} إلى {lv[4]} | {lv[6]} يوم | سبب: {lv[5]}")
    return leaves

# ---------------------------- #
# القائمة الرئيسية
# ---------------------------- #
while True:
    print("\n===== نظام تسيير العطل =====")
    print("1️⃣ إضافة موظف")
    print("2️⃣ تسجيل عطلة")
    print("3️⃣ عرض الموظفين")
    print("4️⃣ عرض العطل")
    print("5️⃣ خروج")
    
    choice = input("👉 اختر: ")
    
    if choice == "1":
        name = input("اسم الموظف: ")
        dep = input("القسم: ")
        pos = input("المنصب: ")
        sal = float(input("الراتب: "))
        hire = input("تاريخ التوظيف (YYYY-MM-DD): ")
        add_employee(name, dep, pos, sal, hire)
    elif choice == "2":
        list_employees()
        emp_id = int(input("ادخل رقم الموظف: "))
        print("📌 اختر نوع العطلة: (سنوية / مرضية / أمومة / بدون أجر)")
        leave_type = input("نوع العطلة: ")
        start = input("تاريخ البداية (YYYY-MM-DD): ")
        end = input("تاريخ النهاية (YYYY-MM-DD): ")
        reason = input("سبب العطلة: ")
        add_leave(emp_id, leave_type, start, end, reason)
    elif choice == "3":
        list_employees()
    elif choice == "4":
        list_leaves()
    elif choice == "5":
        print("👋 خروج...")
        break
    else:
        print("❌ اختيار غير صحيح")