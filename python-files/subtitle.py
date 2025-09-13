import os

# مسیر پوشه‌ای که زیرنویس‌ها در آن قرار دارند
subtitle_folder = "C:/Users/MehrDesign/Desktop/subtitle/"

# عبور از تمام فایل‌ها در پوشه
for filename in os.listdir(subtitle_folder):
    if filename.endswith(".srt"):
        file_path = os.path.join(subtitle_folder, filename)

        # باز کردن و خواندن محتوای فایل
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # جایگزینی کلمات
        content = content.replace("مای موویز", "نیوفیلم")
        content = content.replace("MyMoviz", "NewFilm")
        content = content.replace("قــقــنـوس", "نیـوفیلم")
        content = content.replace("@subforpersian", "NewFilm")

        # ذخیره مجدد فایل با محتوای ویرایش‌شده
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"{filename} ویرایش شد.")
