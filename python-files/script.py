# برنامج دمج نص مع توقيع ثابت
# Developed by abdalah_hr
# All rights reserved to abdalah_hr

def main():
    print("مرحبًا! هذا البرنامج مصمم بواسطة abdalah_hr.")
    text = input("أدخل النص الذي تريد دمجه: ")
    signature = "\n-- abdalah_hr"  # التوقيع الثابت (يمكنك تعديله هنا)
    result = text + signature
    print("\nالنتيجة:")
    print(result)
    
    # خيار حفظ النتيجة في ملف
    save = input("هل تريد حفظ النتيجة في ملف نصي؟ (نعم/لا): ")
    if save.lower() == "نعم":
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write(result)
        print("تم حفظ النتيجة في ملف output.txt")

if __name__ == "__main__":
    main()