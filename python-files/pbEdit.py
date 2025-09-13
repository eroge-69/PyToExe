# -*- coding: utf-8 -*-
import os
import sys

def remove_stars_from_second_field(input_filename):
    try:
        # بررسی وجود فایل
        if not os.path.exists(input_filename):
            print("❌ خطا: فایل مورد نظر یافت نشد!")
            print(f"فایل '{input_filename}' در مسیر جاری وجود ندارد.")
            input("برای خروج، کلید Enter را فشار دهید...")
            return False
        
        # ذخیره فایل اصلی با نام جدید
        base_name = os.path.splitext(input_filename)[0]
        original_backup = f"{base_name}_0.txt"
        
        # کپی فایل اصلی به فایل پشتیبان
        try:
            with open(input_filename, 'r', encoding='utf-8') as original_file:
                content = original_file.read()
            with open(original_backup, 'w', encoding='utf-8') as backup_file:
                backup_file.write(content)
        except Exception as e:
            print(f"❌ خطا در ایجاد نسخه پشتیبان: {e}")
            return False
        
        print("✅ نسخه پشتیبان با موفقیت ایجاد شد.")
        
        # پردازش خطوط و حذف ستاره‌ها از فیلد دوم
        processed_lines = []
        line_count = 0
        
        try:
            with open(input_filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line_count += 1
                    fields = line.strip().split(',')
                    if len(fields) >= 3:
                        # حذف ستاره‌ها از فیلد دوم (ایندکس 2)
                        original_value = fields[2]
                        fields[2] = fields[2].replace('*', '')
                        
                        # اگر تغییری ایجاد شده بود، نمایش دهید
                        if original_value != fields[2]:
                            print(f"📝 خط {line_count}: '{original_value}' → '{fields[2]}'")
                    
                    processed_line = ','.join(fields)
                    processed_lines.append(processed_line)
        except Exception as e:
            print(f"❌ خطا در پردازش فایل: {e}")
            return False
        
        # ذخیره فایل پردازش شده با نام اصلی
        try:
            with open(input_filename, 'w', encoding='utf-8') as file:
                for line in processed_lines:
                    file.write(line + '\n')
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل پردازش شده: {e}")
            return False
        
        print("\n✅ عملیات با موفقیت completed شد!")
        print(f"📁 فایل اصلی: '{original_backup}' (نسخه پشتیبان)")
        print(f"📁 فایل پردازش شده: '{input_filename}'")
        print(f"📊 تعداد خطوط پردازش شده: {line_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        return False

def main():
    print("=" * 50)
    print("🌟 برنامه پردازش فایل pasokhbarg.txt")
    print("🌟 حذف ستاره‌ها از فیلد دوم")
    print("=" * 50)
    
    input_filename = "pasokhbarg.txt"
    
    success = remove_stars_from_second_field(input_filename)
    
    if success:
        print("\n🎉 پردازش با موفقیت انجام شد!")
    else:
        print("\n❌ پردازش با خطا مواجه شد!")
    
    # منتظر ماندن برای فشار دادن کلید
    input("\nبرای خروج، کلید Enter را فشار دهید...")

if __name__ == "__main__":
    main()