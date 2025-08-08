import os
import subprocess

def execute_command(cmd):
    cmd = cmd.lower()

    if "افتح المتصفح" in cmd:
        # افتح جوجل كروم (تأكد إنه متثبت ومساره صحيح)
        subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        print("فتح المتصفح")
    elif "اقفل الجهاز" in cmd:
        # أمر إيقاف تشغيل الويندوز بعد 1 دقيقة (يمكن تعديله)
        os.system("shutdown /s /t 60")
        print("جاري إغلاق الجهاز بعد 60 ثانية")
    elif "شغل المفكرة" in cmd:
        os.system("notepad")
        print("فتح المفكرة")
    elif "اكتب ملف" in cmd:
        with open("myfile.txt", "w", encoding="utf-8") as f:
            f.write("هذا ملف تم إنشاؤه بواسطة السكريبت.")
        print("تم إنشاء ملف")
    else:
        print("الأمر غير معروف")

def main():
    while True:
        cmd = input("اكتب الأمر: ")
        if cmd.lower() in ["خروج", "exit", "quit"]:
            print("خروج من البرنامج")
            break
        execute_command(cmd)

if __name__ == "__main__":
    main()
