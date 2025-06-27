from itertools import permutations
from datetime import datetime

def is_valid_date(day, month, year):
    """التحقق مما إذا كان التاريخ صحيحًا"""
    try:
        datetime(year=year, month=month, day=day)
        return True
    except ValueError:
        return False

def extract_digits(date_str):
    """استخراج الأرقام من التاريخ مع الحفاظ على التكرار"""
    digits = []
    for ch in date_str:
        if ch.isdigit():
            digits.append(ch)
    return digits

def find_valid_dates(digits):
    valid_dates = []

    # تحديد عدد الأرقام (7 أو 8)
    length = len(digits)
    if length not in [7, 8]:
        print("⚠️ الخطأ: يجب أن يحتوي التاريخ على 7 أو 8 أرقام.")
        return []

    for perm in set(permutations(digits)):  # جميع التوليفات الممكنة
        combined = ''.join(perm)

        # نحاول عدة أنماط بناءً على طول السلسلة
        if length == 7:
            # بصيغة 2+1+4 = 7
            day_str = combined[0:2]
            month_str = combined[2:3]
            year_str = combined[3:7]
            if day_str.isdigit() and month_str.isdigit() and year_str.isdigit():
                day = int(day_str)
                month = int(month_str)
                year = int(year_str)
                if 1 <= day <= 31 and 1 <= month <= 12 and 1976 <= year <= 2045:
                    if is_valid_date(day, month, year):
                        valid_dates.append(f"{day}/{month}/{year}")

            # بصيغة 1+2+4 = 7
            day_str = combined[0:1]
            month_str = combined[1:3]
            year_str = combined[3:7]
            if day_str.isdigit() and month_str.isdigit() and year_str.isdigit():
                day = int(day_str)
                month = int(month_str)
                year = int(year_str)
                if 1 <= day <= 31 and 1 <= month <= 12 and 1976 <= year <= 2045:
                    if is_valid_date(day, month, year):
                        valid_dates.append(f"{day}/{month}/{year}")

        elif length == 8:
            # بصيغة 2+2+4 = 8
            day_str = combined[0:2]
            month_str = combined[2:4]
            year_str = combined[4:8]
            if day_str.isdigit() and month_str.isdigit() and year_str.isdigit():
                day = int(day_str)
                month = int(month_str)
                year = int(year_str)
                if 1 <= day <= 31 and 1 <= month <= 12 and 1976 <= year <= 2045:
                    if is_valid_date(day, month, year):
                        valid_dates.append(f"{day}/{month}/{year}")

    # حذف التكرارات وفرز القائمة
    valid_dates = sorted(set(valid_dates), key=lambda x: (int(x.split('/')[2]), int(x.split('/')[1]), int(x.split('/')[0])))
    return valid_dates

# 📥 إدخال التاريخ من المستخدم
input_date = input("📅 أدخل تاريخًا (مثال: 26/1/2015 أو 26/01/2015): ")

# استخراج الأرقام
digits = extract_digits(input_date)

# البحث عن التواريخ الممكنة
results = find_valid_dates(digits)

# عرض النتائج
if results:
    print(f"\n✅ التواريخ الممكنة بين 1976 و2045 باستخدام نفس الأرقام ({len(results)} نتيجة):")
    for date in results:
        print(date)
else:
    print("\n❌ لم يتم العثور على تواريخ مطابقة باستخدام نفس الأرقام.")
