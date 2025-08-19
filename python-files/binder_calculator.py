def calculate_f_and_eq_isocyanate(MW_isocyanate, NCO_content):
    """
    محاسبه درجه عاملیت (f) و وزن معادل NCO برای ایزوسیانات.
    
    ورودی‌ها:
    - MW_isocyanate: وزن مولکولی ایزوسیانات (g/mol)
    - NCO_content: محتوای NCO (%)
    
    خروجی:
    - وزن معادل NCO (g/eq)
    """
    f_isocyanate = (NCO_content / 100) * MW_isocyanate / 42
    eq_weight_NCO = MW_isocyanate / f_isocyanate
    print(f"درجه عاملیت ایزوسیانات (f): {f_isocyanate:.4f}")
    return eq_weight_NCO

def calculate_f_and_eq_oh(MW, OH_value, name):
    """
    محاسبه درجه عاملیت (f) و وزن معادل OH برای پلی‌ال یا DHE.
    
    ورودی‌ها:
    - MW: وزن مولکولی (g/mol)
    - OH_value: مقدار OH (mg KOH/g)
    - name: نام ماده (polyol یا dhe)
    
    خروجی:
    - وزن معادل OH (g/eq)
    """
    f = (OH_value * MW) / 56100
    eq_weight_OH = MW / f
    print(f"درجه عاملیت {name} (f): {f:.4f}")
    return eq_weight_OH

def main():
    print("محاسبه‌گر بایندر PBXN-109")
    print("1. محاسبه R")
    print("2. محاسبه مقدار ایزوسیانات موردنیاز")
    choice = input("گزینه را انتخاب کنید (1 یا 2): ")

    if choice == '1':
        # محاسبه R
        try:
            isocyanate_weight = float(input("وزن ایزوسیانات (گرم): "))
            MW_isocyanate = float(input("وزن مولکولی ایزوسیانات (g/mol): "))
            NCO_content = float(input("محتوای NCO (%): "))
            eq_weight_NCO = calculate_f_and_eq_isocyanate(MW_isocyanate, NCO_content)
            
            polyol_weight = float(input("وزن پلی‌ال (گرم): "))
            MW_polyol = float(input("وزن مولکولی پلی‌ال (g/mol): "))
            OH_value_polyol = float(input("OH value پلی‌ال (mg KOH/g): "))
            eq_weight_OH_polyol = calculate_f_and_eq_oh(MW_polyol, OH_value_polyol, "polyol")
            
            dhe_weight = float(input("وزن DHE (گرم): "))
            MW_dhe = float(input("وزن مولکولی DHE (g/mol): "))
            OH_value_dhe = float(input("OH value DHE (mg KOH/g): "))
            eq_weight_OH_dhe = calculate_f_and_eq_oh(MW_dhe, OH_value_dhe, "dhe")
            
            R = (isocyanate_weight / eq_weight_NCO) / ((polyol_weight / eq_weight_OH_polyol) + (dhe_weight / eq_weight_OH_dhe))
            print(f"\nنتیجه: R = {R:.4f}")
        except ValueError:
            print("خطا: لطفاً مقادیر عددی معتبر وارد کنید.")
        except ZeroDivisionError:
            print("خطا: وزن معادل صفر است. مقادیر ورودی را بررسی کنید.")

    elif choice == '2':
        # محاسبه مقدار ایزوسیانات
        try:
            desired_R = float(input("R موردنظر: "))
            
            polyol_weight = float(input("وزن پلی‌ال (گرم): "))
            MW_polyol = float(input("وزن مولکولی پلی‌ال (g/mol): "))
            OH_value_polyol = float(input("OH value پلی‌ال (mg KOH/g): "))
            eq_weight_OH_polyol = calculate_f_and_eq_oh(MW_polyol, OH_value_polyol, "polyol")
            
            dhe_weight = float(input("وزن DHE (گرم): "))
            MW_dhe = float(input("وزن مولکولی DHE (g/mol): "))
            OH_value_dhe = float(input("OH value DHE (mg KOH/g): "))
            eq_weight_OH_dhe = calculate_f_and_eq_oh(MW_dhe, OH_value_dhe, "dhe")
            
            MW_isocyanate = float(input("وزن مولکولی ایزوسیانات (g/mol): "))
            NCO_content = float(input("محتوای NCO (%): "))
            eq_weight_NCO = calculate_f_and_eq_isocyanate(MW_isocyanate, NCO_content)
            
            required_isocyanate = desired_R * ((polyol_weight / eq_weight_OH_polyol) + (dhe_weight / eq_weight_OH_dhe)) * eq_weight_NCO
            print(f"\nنتیجه: مقدار ایزوسیانات موردنیاز = {required_isocyanate:.4f} گرم")
        except ValueError:
            print("خطا: لطفاً مقادیر عددی معتبر وارد کنید.")
        except ZeroDivisionError:
            print("خطا: وزن معادل صفر است. مقادیر ورودی را بررسی کنید.")

    else:
        print("گزینه نامعتبر است. لطفاً 1 یا 2 را انتخاب کنید.")

if __name__ == "__main__":
    while True:
        main()
        again = input("\nآیا می‌خواهید دوباره محاسبه کنید؟ (بله/خیر): ")
        if again.lower() not in ['بله', 'yes']:
            break
    print("برنامه پایان یافت.")