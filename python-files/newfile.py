def calculate_service_duration():
    # إدخال تاريخ التسريح
    print("أدخل تاريخ التسريح:")
    discharge_day = int(input("اليوم: "))
    discharge_month = int(input("الشهر: "))
    discharge_year = int(input("السنة: "))

    # إدخال تاريخ التجنيد
    print("\nأدخل تاريخ التجنيد:")
    enlistment_day = int(input("اليوم: "))
    enlistment_month = int(input("الشهر: "))
    enlistment_year = int(input("السنة: "))

    # تعديل التاريخ إذا كان يوم التجنيد أكبر من يوم التسريح
    if enlistment_day > discharge_day:
        discharge_month -= 1
        discharge_day += 30

    # حساب الفرق في الأيام والأشهر والسنوات
    days_remaining = discharge_day - enlistment_day
    months_remaining = discharge_month - enlistment_month
    years_remaining = discharge_year - enlistment_year

    # تعديل القيم السالبة للأشهر
    if months_remaining < 0:
        years_remaining -= 1
        months_remaining += 12

    # عرض النتيجة
    print(f"\nالمدة المتبقية: {years_remaining} سنة/ {months_remaining} شهر/شهر، {days_remaining} يوم/م")

# تشغيل البرنامج
calculate_service_duration()