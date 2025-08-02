import pandas as pd
import shutil
import os

# مسیرها (تطبیق با فایل واقعی شما)
csv_path = r"C:\Users\Administrator\Downloads\pic2(1).csv"
source_folder = r"C:\Users\Administrator\Downloads\thumbs"
destination_folder = r"C:\Users\Administrator\Downloads\thumbs-new"

# ایجاد پوشه مقصد
os.makedirs(destination_folder, exist_ok=True)

# خواندن CSV
df = pd.read_csv(csv_path)

# ستون‌های تصویر
image_columns = ['Picture1', 'Picture2', 'Picture3']
copied = 0
missing = []

# استخراج لیست تصاویر
image_files = set()
for col in image_columns:
    image_files.update(df[col].dropna().astype(str).tolist())

# کپی فایل‌ها
for image_name in image_files:
    src_path = os.path.join(source_folder, image_name)
    dest_path = os.path.join(destination_folder, image_name)

    if os.path.isfile(src_path):
        shutil.copy2(src_path, dest_path)
        copied += 1
    else:
        missing.append(image_name)

# نمایش نتیجه
print(f"\n✅ {copied} فایل با موفقیت کپی شدند.")
if missing:
    print(f"\n⚠️ {len(missing)} فایل یافت نشد. نمونه:")
    for name in missing[:10]:
        print(f" - {name}")
