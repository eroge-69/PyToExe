def calculator():
    print("مرحباً بك في الآلة الحاسبة البسيطة!")
    print("العمليات المتاحة:")
    print("1. جمع (+)")
    print("2. طرح (-)")
    print("3. ضرب (*)")
    print("4. قسمة (/)")

    operation = input("اختر رقم العملية (1/2/3/4): ")

    if operation in ('1', '2', '3', '4'):
        try:
            num1 = float(input("أدخل الرقم الأول: "))
            num2 = float(input("أدخل الرقم الثاني: "))

            if operation == '1':
                result = num1 + num2
                print(f"النتيجة: {num1} + {num2} = {result}")

            elif operation == '2':
                result = num1 - num2
                print(f"النتيجة: {num1} - {num2} = {result}")

            elif operation == '3':
                result = num1 * num2
                print(f"النتيجة: {num1} * {num2} = {result}")

            elif operation == '4':
                if num2 != 0:
                    result = num1 / num2
                    print(f"النتيجة: {num1} / {num2} = {result}")
                else:
                    print("خطأ: لا يمكن القسمة على صفر.")
        except ValueError:
            print("خطأ: يرجى إدخال أرقام فقط.")
    else:
        print("خطأ: اختيار غير صحيح.")

# تشغيل الآلة الحاسبة
calculator()