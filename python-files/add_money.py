import struct
import os

def add_money_to_save(file_path, amount=50000):
    backup_path = file_path + ".bak"
    
    # اعمل نسخة احتياطية قبل التعديل
    if not os.path.exists(backup_path):
        os.rename(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print("Backup already exists.")
    
    # اقرأ البيانات من الملف
    with open(backup_path, "rb") as f:
        data = f.read()
    
    # هنبحث عن رقم كبير يمثل الفلوس (مثلاً فوق 1000)
    money_candidates = []
    for i in range(len(data) - 4):
        val = struct.unpack("<I", data[i:i+4])[0]
        if 1000 < val < 100000000:
            money_candidates.append((i, val))
    
    if not money_candidates:
        print("لم يتم العثور على قيمة الفلوس!")
        return
    
    # افترض إن أول قيمة كبيرة هي الفلوس
    offset, old_money = money_candidates[0]
    new_money = old_money + amount
    
    print(f"الفلوس القديمة: {old_money} -> الجديدة: {new_money}")
    
    # عدل الفلوس
    new_data = bytearray(data)
    new_data[offset:offset+4] = struct.pack("<I", new_money)
    
    # احفظ الملف الجديد
    with open(file_path, "wb") as f:
        f.write(new_data)
    
    print(f"تم تعديل الملف وإضافة {amount} فلوس بنجاح!")

# تعديل الملف
file_path = input("أدخل مسار ملف gamesaves.cfs23: ").strip()
add_money_to_save(file_path)
