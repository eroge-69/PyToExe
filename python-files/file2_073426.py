import os
import shutil


def find_and_save_stl_files_to_desktop(source_directory):
    """
    فایل‌های STL را از مسیر مبدأ پیدا کرده و آن‌ها را به پوشه‌ای در دسکتاپ کپی می‌کند.

    ورودی:
        source_directory (str): مسیر پوشه منبع (مبدأ).

    خروجی:
        int: تعداد فایل‌های کپی‌شده.
    """
    # بررسی می‌کند که آیا مسیر مبدأ معتبر است یا خیر
    if not os.path.isdir(source_directory):
        print(f"خطا: مسیر مبدأ '{source_directory}' وجود ندارد یا معتبر نیست.")
        return 0

    # پیدا کردن مسیر دسکتاپ
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    # تعیین مسیر پوشه مقصد در دسکتاپ
    destination_directory = os.path.join(desktop_path, "STL_Files_Found")

    # اگر پوشه مقصد وجود ندارد، آن را ایجاد می‌کند
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        print(f"پوشه مقصد '{destination_directory}' در دسکتاپ ایجاد شد.")

    copied_count = 0
    # پیمایش تمام فایل‌ها در مسیر مبدأ و زیرشاخه‌های آن
    for root, _, files in os.walk(source_directory):
        for file in files:
            # بررسی پسوند فایل، بدون حساسیت به حروف بزرگ و کوچک
            if file.lower().endswith('.stl'):
                source_file_path = os.path.join(root, file)
                destination_file_path = os.path.join(destination_directory, file)

                # کپی کردن فایل با استفاده از shutil.copy2
                try:
                    shutil.copy2(source_file_path, destination_file_path)
                    copied_count += 1
                    print(f"فایل '{file}' با موفقیت کپی شد.")
                except Exception as e:
                    print(f"خطا در کپی کردن فایل '{file}': {e}")

    return copied_count


# --- نحوه استفاده از تابع ---
if __name__ == "__main__":
    # مسیر مبدأ (پوشه‌ای که فایل‌های STL در آن قرار دارند)
    # مثلاً: my_folder_path = "C:\\Users\\YourName\\Documents\\3DModels"
    my_folder_path = r"C:\Users\user\Desktop\my assembly"

    total_copied = find_and_save_stl_files_to_desktop(my_folder_path)

    if total_copied > 0:
        print(f"\n✅ عملیات کپی به پایان رسید. تعداد {total_copied} فایل با موفقیت در دسکتاپ شما ذخیره شدند.")
    else:
        print("\n❌ هیچ فایل STL برای کپی کردن پیدا نشد.")
