import psutil
import shutil
import time
import os
import jdatetime

today = jdatetime.date.today()
SOURCE_FILE = r"C:\01\{Red_Apple}.JPG"  # مسیر فایل منبع
FOLDER_NAME = "{Red_Apple}"+f"{today.year}_{today.month}_{today.day}"  # نام فولدری که می‌خواهید در فلش ایجاد شود

def get_usb_drives():
    usb_drives = []
    for partition in psutil.disk_partitions():
        # بررسی درایوهای قابل جدا شدن (مانند فلش)
        if 'removable' in partition.opts.lower() or 'usb' in partition.device.lower():
            usb_drives.append(partition.mountpoint)
    return usb_drives

def create_folder_and_copy_file(usb_path):
    try:
        destination_folder = os.path.join(usb_path, FOLDER_NAME)
        os.makedirs(destination_folder, exist_ok=True) 

        if os.path.exists(SOURCE_FILE):
            new_path = str(usb_path) + FOLDER_NAME
            file_name = os.path.basename(SOURCE_FILE)
            destination_file = os.path.join(new_path, file_name)
            shutil.copy2(SOURCE_FILE, destination_file)
        else:
            print("can not find file!")

    except Exception as e:
        print(f"error: {e}")

def monitor_usb():
    known_drives = set(get_usb_drives())
    if len(known_drives):
        print("Port list:\n\t")
        for j in known_drives:
            print(j, end=" | ")
    else:
        print("List is empty!")
    print("\n------------------------")
    while True:
        current_drives = set(get_usb_drives())
        new_drives = current_drives - known_drives
        
        if new_drives:
            for usb in new_drives:
                print(f"new flash: {usb}")
                create_folder_and_copy_file(usb)
        
        known_drives = current_drives
        time.sleep(2) 

if __name__ == "__main__":
    print("searching for new flash...")
    monitor_usb()
print(__name__)