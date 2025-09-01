import os

folder_path = '/storage/emulated/0/DCIM/Facebook'

# التحقق من وجود المجلد
if os.path.exists(folder_path):
    print("المجلد موجود")
    os.rmdir("/storage/emulated/0/DCIM/Facebook")