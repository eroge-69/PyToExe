import pandas as pd
import math
import sys
import os

def load_shipping_data():
    """تحميل بيانات التسعيرة من ملف Excel في نفس مجلد الـ exe"""
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(script_dir, "aramex.xlsx")
    
    try:
        df = pd.read_excel(file_path, header=0)
        # تعيين أسماء الأعمدة بشكل صحيح
        df.columns = ['Country_EN', 'Country_AR', 'FirstHalfKg', 'Addtional0_5To10', 'Addtional10To15', 'AddtionalOver15']
        
        for col in ['FirstHalfKg', 'Addtional0_5To10', 'Addtional10To15', 'AddtionalOver15']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        print(f"❌ لم يتم العثور على ملف التسعيرة: {file_path}")
        print("⚠️ تأكد من وضع ملف 'aramex.xlsx' في نفس مجلد البرنامج.")
        input("اضغط Enter لإغلاق...")
        exit()
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        input("اضغط Enter لإغلاق...")
        exit()

def calculate_aramex_cost(df, country, weight_kg):
    """حساب تكلفة الشحن حسب تسعيرة أرامكس"""
    try:
        weight = float(weight_kg)
        if weight < 0:
            return "❌ الوزن لا يمكن أن يكون سالبًا."
    except ValueError:
        return "❌ الوزن يجب أن يكون رقمًا."

    # البحث عن الدولة (بالإنجليزي أو العربي)
    country_clean = country.strip()
    country_match = df[
        (df['Country_EN'].str.strip().str.upper() == country_clean.upper()) |
        (df['Country_AR'].str.strip().str.contains(country_clean, case=False, na=False))
    ]
    
    if country_match.empty:
        return f"❌ لا توجد تسعيرة للدولة: {country}"

    row = country_match.iloc[0]
    first = row['FirstHalfKg']
    add_05_10 = row['Addtional0_5To10']
    add_10_15 = row['Addtional10To15']
    add_over_15 = row['AddtionalOver15']

    # التحقق من وجود N/A
    if pd.isna(first) or pd.isna(add_05_10):
        return f"❌ لا توجد خدمة شحن حاليًا إلى {row['Country_EN']} ({row['Country_AR']}) (بيانات غير متوفرة)."

    half_kg_units = math.ceil(weight * 2)  # عدد وحدات نصف الكيلو (مقرب لأعلى)

    if weight <= 0.5:
        total = first
    elif weight <= 10:
        extra_halves = half_kg_units - 1
        total = first + (extra_halves * add_05_10)
    elif weight <= 15:
        extra_05_10 = 19  # من 0.5 إلى 10 كغ = 19 وحدة إضافية
        extra_10_15 = half_kg_units - 20
        total = first + (extra_05_10 * add_05_10) + (extra_10_15 * add_10_15)
    else:
        extra_05_10 = 19
        extra_10_15 = 10  # من 10 إلى 15 كغ = 10 وحدات
        extra_over_15 = half_kg_units - 30
        total = first + (extra_05_10 * add_05_10) + (extra_10_15 * add_10_15) + (extra_over_15 * add_over_15)

    return f"✅ سعر الشحن لـ {row['Country_EN']} ({row['Country_AR']}) بوزن {weight} كغ هو: {total:.2f} دولار"

def main():
    print("📦 برنامج حساب تكلفة الشحن - أرامكس (نسخة محمولة)")
    print("=" * 60)
    
    df = load_shipping_data()
    
    while True:
        print("\nأدخل 'quit' أو 'exit' للخروج.")
        country = input("أدخل اسم الدولة (بالإنجليزي أو العربي): ").strip()
        if country.lower() in ['quit', 'exit']:
            print("👋 وداعًا!")
            break
        
        weight = input("أدخل الوزن (كغ): ").strip()
        
        result = calculate_aramex_cost(df, country, weight)
        print(result)
        print("-" * 60)

if __name__ == "__main__":
    main()