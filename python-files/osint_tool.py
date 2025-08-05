```python
import requests
import socket
import whois
import json
import sys

def check_email_breach(email):
    print(f"\n[+] فحص تسريبات البريد الإلكتروني: {email}")
    print("[!] ملاحظة: هذا فحص تجريبي (واجهة وهمية)")
    print("[i] يُنصح باستخدام HaveIBeenPwned API بمفتاح رسمي.")  # تتطلب API مدفوعة

def check_phone_number(phone):
    print(f"\n[+] فحص الهاتف: {phone}")
    print("[!] يستخدم هذا السكربت مكتبة holehe، تأكد من تثبيتها.")
    try:
        import subprocess
        result = subprocess.check_output(['holehe', phone])
        print(result.decode())
    except Exception as e:
        print("[-] فشل تنفيذ holehe:", e)

def check_ip(ip):
    print(f"\n[+] تحليل عنوان IP: {ip}")
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        for k, v in data.items():
            print(f"{k}: {v}")
    except:
        print("[-] تعذر جلب بيانات IP.")

def check_domain(domain):
    print(f"\n[+] تحليل النطاق: {domain}")
    try:
        w = whois.whois(domain)
[4:31 م، 2025/8/5] ChatGPT: print(json.dumps(w, indent=2, default=str))
    except:
        print("[-] فشل فحص النطاق.")

def main():
    print("== أداة OSINT للتحقيق الرقمي ==")
    print("1. فحص بريد إلكتروني")
    print("2. فحص رقم هاتف")
    print("3. تحليل عنوان IP")
    print("4. تحليل نطاق (Domain)")
    choice = input("اختر من 1 إلى 4: ").strip()

    if choice == '1':
        email = input("أدخل البريد الإلكتروني: ").strip()
        check_email_breach(email)
    elif choice == '2':
        phone = input("أدخل رقم الهاتف مع رمز الدولة: ").strip()
        check_phone_number(phone)
    elif choice == '3':
        ip = input("أدخل عنوان IP: ").strip()
        check_ip(ip)
    elif choice == '4':
        domain = input("أدخل اسم النطاق (domain.com): ").strip()
        check_domain(domain)
    else:
        print("[-] خيار غير صالح.")

if name == "main":
    main()


---
